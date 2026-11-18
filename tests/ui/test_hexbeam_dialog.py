# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.hexbeam_dialog import HexbeamDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> HexbeamDialog:
    return HexbeamDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_hexbeam_dialog_builds_the_published_reference(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Hexbeam Generator"
    assert parameters.driver_half_length_m == pytest.approx(5.5372, abs=1e-3)
    assert parameters.reflector_half_length_m == pytest.approx(5.2324, abs=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.302, abs=1e-3)
    assert parameters.tip_gap_m == pytest.approx(0.6096, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 10
    assert "driver 5.537 m half" in dialog._form._geometry.text()


def test_hexbeam_dialog_updates_the_wire_path(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._driver_half.setValue(5.84)
    dialog._form._reflector_half.setValue(5.52)
    dialog._form._turning_radius.setValue(3.47)
    dialog._form._tip_gap.setValue(0.64)

    parameters = dialog.parameters()

    assert parameters.driver_half_length_m == pytest.approx(5.84, abs=1e-3)
    assert parameters.reflector_half_length_m == pytest.approx(5.52, abs=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.47, abs=1e-3)
    assert parameters.tip_gap_m == pytest.approx(0.64, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 10


def test_hexbeam_dialog_seeds_the_reference_at_the_requested_frequency(
    qtbot: QtBot,
) -> None:
    dialog = HexbeamDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        frequency_hz=21_200_000.0,
    )
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()
    assert parameters.frequency_hz == pytest.approx(21_200_000.0)
    assert parameters.driver_half_length_m == pytest.approx(3.7047, abs=1e-3)
    assert parameters.reflector_half_length_m == pytest.approx(3.5008, abs=1e-3)


def test_hexbeam_form_load_starting_preserves_installation_fields(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form
    form._frequency.setValue(21.2)
    form._height.setValue(12.0)
    form._azimuth.setValue(30.0)
    form._driver_half.setValue(10.0)

    form._starting.click()

    parameters = form.parameters()
    assert parameters.driver_half_length_m == pytest.approx(3.7047, abs=1e-3)
    assert parameters.height_m == pytest.approx(12.0)
    assert parameters.azimuth_deg == pytest.approx(30.0)


def test_hexbeam_form_auto_resizes_pristine_geometry(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    form._frequency.setValue(21.2)

    assert form.parameters().driver_half_length_m == pytest.approx(3.7047, abs=1e-3)

    form._height.setValue(12.0)
    form._frequency.setValue(28.4)

    assert form.parameters().height_m == pytest.approx(12.0)
    assert form.parameters().driver_half_length_m < 3.0

    form._driver_half.setValue(2.82)
    form._frequency.setValue(30.0)

    assert form.parameters().driver_half_length_m == pytest.approx(2.82)
    assert "not resized" in form._starting_note.text().lower()


def test_hexbeam_form_preserves_lengths_when_switching_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._driver_half.setValue(5.5)
    dialog._form._turning_radius.setValue(3.3)

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)

    parameters = dialog.parameters()
    assert parameters.driver_half_length_m == pytest.approx(5.5, rel=1e-3)
    assert parameters.turning_radius_m == pytest.approx(3.3, rel=1e-3)
    assert dialog._form._driver_half.suffix().strip() == "ft"


def test_hexbeam_form_represents_uhf_tip_and_feed_gaps(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters

    dialog = _dialog()
    qtbot.addWidget(dialog)
    parameters = published_hexbeam_parameters(
        frequency_hz=435_000_000.0,
        height_m=10.0,
    )

    dialog._form.set_parameters(parameters)

    restored = dialog.parameters()
    assert restored.tip_gap_m == pytest.approx(parameters.tip_gap_m, abs=5e-4)
    assert restored.feed_gap_m == pytest.approx(parameters.feed_gap_m, abs=5e-4)
    assert restored.element_separation_m == pytest.approx(
        parameters.element_separation_m,
        abs=5e-4,
    )
    assert dialog._form._tip_gap.value() > 0.0
    assert dialog._form._feed_gap.value() > 0.0


def test_hexbeam_form_selects_the_five_band_preset(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for check in form._band_checks.values():
        check.setChecked(True)

    parameters = dialog.parameters()

    assert tuple(band.label for band in parameters.bands) == (
        "20m",
        "17m",
        "15m",
        "12m",
        "10m",
    )
    assert len(parameters.to_antenna().wires) == 50
    assert len(parameters.to_antenna().sources) == 0
    assert parameters.to_antenna(active_band="15m").feed.wire_id == "hexbeam-band3-feed"
    assert form._band_table.rowCount() == 5
    assert not form._band_table.isHidden()
    assert form._frequency.isEnabled()
    assert not form._driver_half.isEnabled()
    assert "5 bands" in form._geometry.text().lower()
    assert "m)" in form._band_table.horizontalHeaderItem(2).text()
    assert form._active_band_combo.count() == 5
    assert form.active_band() == "20m"
    form._active_band_combo.setCurrentIndex(2)
    assert form.active_band() == "15m"


def _band_length_text(form: object, value_m: float) -> str:
    return form._display_units.format_number(  # type: ignore[attr-defined]
        value_m,
        unit=form._band_table_unit,  # type: ignore[attr-defined]
        trim=False,
    )


def test_hexbeam_form_edits_one_band_without_touching_the_others(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for check in form._band_checks.values():
        check.setChecked(True)
    original = dialog.parameters()

    form._band_table.item(2, 2).setText(_band_length_text(form, 3.68))

    parameters = dialog.parameters()

    assert parameters.bands[0] == original.bands[0]
    assert parameters.bands[1] == original.bands[1]
    assert parameters.bands[3] == original.bands[3]
    assert parameters.bands[4] == original.bands[4]
    assert parameters.bands[2].driver_half_length_m == pytest.approx(3.68)
    assert "custom" in form._bands_note.text().lower()


def test_hexbeam_form_edits_custom_labels_and_frequencies(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for check in form._band_checks.values():
        check.setChecked(True)
    form._band_table.item(2, 0).setText("custom-15")
    form._band_table.item(2, 1).setText("21.250")

    parameters = dialog.parameters()

    assert parameters.bands[2].label == "custom-15"
    assert parameters.bands[2].frequency_hz == pytest.approx(21_250_000.0)
    assert form._band_checks["15m"].isChecked() is False
    texts = tuple(
        form._active_band_combo.itemText(index) for index in range(form._active_band_combo.count())
    )
    assert "custom-15" in texts
    assert "custom" in form._bands_note.text().lower()


def test_hexbeam_form_adds_and_removes_custom_band_rows(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for label in ("20m", "17m", "15m"):
        form._band_checks[label].setChecked(True)
    assert form._band_table.rowCount() == 3

    form._add_band.click()

    assert form._band_table.rowCount() == 4
    assert "complete" in form._bands_note.text().lower()

    row = 3
    values = (
        "custom-24",
        "24.000",
        _band_length_text(form, 3.24),
        _band_length_text(form, 3.08),
        _band_length_text(form, 0.359),
        _band_length_text(form, 0.028),
        _band_length_text(form, 0.0),
    )
    for column, value in enumerate(values):
        form._band_table.item(row, column).setText(value)

    parameters = dialog.parameters()
    assert tuple(band.label for band in parameters.bands) == (
        "20m",
        "17m",
        "15m",
        "custom-24",
    )
    assert parameters.bands[-1].frequency_hz == pytest.approx(24_000_000.0)

    form._band_table.setCurrentCell(3, 0)
    form._remove_band.click()

    assert form._band_table.rowCount() == 3
    assert tuple(band.label for band in dialog.parameters().bands) == (
        "20m",
        "17m",
        "15m",
    )


def test_hexbeam_form_removing_to_one_row_returns_to_single_band(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for label in ("20m", "17m"):
        form._band_checks[label].setChecked(True)
    form._band_table.setCurrentCell(1, 0)
    form._remove_band.click()

    parameters = dialog.parameters()
    assert parameters.bands == ()
    assert parameters.frequency_hz == pytest.approx(14_184_000.0)
    assert form._band_table.isHidden()
    assert form._driver_half.isEnabled()


def test_hexbeam_form_rejects_invalid_custom_rows(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for label in ("20m", "17m"):
        form._band_checks[label].setChecked(True)

    form._band_table.item(1, 0).setText("20m")

    with pytest.raises(ValueError, match="labels must be unique"):
        dialog.parameters()
    assert "complete" in form._bands_note.text().lower()


def test_hexbeam_form_confirms_before_replacing_custom_rows(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from PySide6.QtWidgets import QMessageBox

    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for label in ("20m", "17m"):
        form._band_checks[label].setChecked(True)
    form._band_table.item(1, 2).setText(_band_length_text(form, 4.0))
    custom_value = dialog.parameters().bands[1].driver_half_length_m

    monkeypatch.setattr(
        "antennadesk.ui.widgets.hexbeam_form.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )
    form._band_checks["15m"].setChecked(True)

    assert dialog.parameters().bands[1].driver_half_length_m == pytest.approx(custom_value)
    assert tuple(band.label for band in dialog.parameters().bands) == ("20m", "17m")

    monkeypatch.setattr(
        "antennadesk.ui.widgets.hexbeam_form.QMessageBox.question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    form._band_checks["15m"].setChecked(True)

    published = dialog.parameters()
    assert tuple(band.label for band in published.bands) == ("20m", "17m", "15m")
    assert published.bands[1].driver_half_length_m == pytest.approx(
        169.5 * 0.0254,
        abs=1e-3,
    )


def test_hexbeam_form_custom_rows_need_published_labels_for_starting_dimensions(
    qtbot: QtBot,
) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for label in ("20m", "17m"):
        form._band_checks[label].setChecked(True)
    form._band_table.item(1, 0).setText("custom-17")
    form._band_table.item(1, 2).setText(_band_length_text(form, 4.0))
    edited = dialog.parameters()

    form._starting.click()

    assert dialog.parameters() == edited
    assert "published band labels" in form._bands_note.text().lower()


def test_hexbeam_form_scales_the_band_stack_within_the_primary_band(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for check in form._band_checks.values():
        check.setChecked(True)

    form._frequency.setValue(14.1)
    parameters = dialog.parameters()

    assert len(parameters.bands) == 5
    assert parameters.frequency_hz == pytest.approx(14_100_000.0)
    assert parameters.bands[0].frequency_hz == pytest.approx(14_100_000.0)
    assert parameters.bands[1].frequency_hz == pytest.approx(18_010_702.0, abs=2.0)
    assert "reference-scaled" in form._bands_note.text().lower()
    assert form._band_table.rowCount() == 5

    form._height.setValue(12.0)
    preserved = dialog.parameters()
    assert preserved.height_m == pytest.approx(12.0)
    assert preserved.bands[0].frequency_hz == pytest.approx(14_100_000.0)

    form._frequency.setValue(10.0)
    assert form._frequency.value() == pytest.approx(14.1)
    assert "outside the primary band" in form._bands_note.text().lower()


def test_hexbeam_form_single_preset_and_custom_single_band(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    form._band_checks["15m"].setChecked(True)
    parameters = dialog.parameters()

    assert parameters.bands == ()
    assert parameters.driver_half_length_m == pytest.approx(144.5 * 0.0254, abs=1e-3)
    assert form._frequency.isEnabled()
    assert form._driver_half.isEnabled()
    assert form._band_table.isHidden()

    form._driver_half.setValue(form._driver_half.value() + 0.01)
    assert not any(check.isChecked() for check in form._band_checks.values())


def test_hexbeam_form_clearing_bands_returns_to_custom_single_band(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    form = dialog._form

    for check in form._band_checks.values():
        check.setChecked(True)
    form._band_checks["10m"].setChecked(False)

    parameters = dialog.parameters()

    assert tuple(band.label for band in parameters.bands) == ("20m", "17m", "15m", "12m")
    assert len(parameters.to_antenna().wires) == 40
    assert form._band_table.rowCount() == 4

    for check in form._band_checks.values():
        check.setChecked(False)

    custom = dialog.parameters()
    assert custom.bands == ()
    assert form._frequency.isEnabled()
    assert form._driver_half.isEnabled()
    assert form._band_table.isHidden()


def test_hexbeam_form_uses_per_field_units_when_auto(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
    from antennadesk.ui.units import DisplayUnits, LengthPolicy
    from antennadesk.ui.widgets.hexbeam_form import HexbeamForm

    form = HexbeamForm(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        display_units=DisplayUnits(UnitSystem.METRIC, LengthPolicy.AUTO),
    )
    qtbot.addWidget(form)
    form.set_parameters(published_hexbeam_parameters(frequency_hz=435_000_000.0))

    assert form._driver_half_field.unit == "cm"
    assert form._turning_radius_field.unit == "cm"
    assert form._tip_gap_field.unit == "cm"
    assert form._height_field.unit == "m"
