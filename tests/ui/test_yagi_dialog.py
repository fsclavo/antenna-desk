# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.ui.dialogs.yagi_dialog import YagiDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def test_yagi_dialog_loads_the_nbs_preset(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert dialog._table.rowCount() == 5
    assert dialog._driven.currentData() == 1
    assert dialog._ground.currentText() == "Free space"
    assert dialog._material.currentText() == "Copper"
    assert dialog._form._polarization.currentText() == "Horizontal"
    assert dialog._form._polarization.itemText(1) == "Vertical"
    parameters = dialog.parameters()
    assert len(parameters.elements) == 5
    assert parameters.driven_index == 1


def test_yagi_dialog_can_add_and_remove_elements(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._add_element()
    assert dialog._table.rowCount() == 6
    parameters = dialog.parameters()
    assert len(parameters.elements) == 6

    dialog._table.selectRow(5)
    dialog._remove_element()
    assert dialog._table.rowCount() == 5


def test_yagi_dialog_rebuilds_geometry_from_edited_lengths(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._table.item(1, 2).setText("10.000")

    parameters = dialog.parameters()

    assert parameters.elements[1].length_m == pytest.approx(10.0, abs=0.001)


def test_yagi_dialog_driven_element_mapping_survives_reordering(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog._table.item(0, 1).setText("2.000")

    parameters = dialog.parameters()
    yagi = YagiParameters(
        frequency_hz=parameters.frequency_hz,
        elements=tuple(
            YagiElement(
                position_m=float(dialog._table.item(row, 1).text()),
                length_m=float(dialog._table.item(row, 2).text()),
                radius_m=float(dialog._table.item(row, 3).text()) / 1_000.0,
            )
            for row in range(dialog._table.rowCount())
        ),
        height_m=12.0,
        driven_index=1,
    )

    assert yagi.elements[0].position_m == pytest.approx(2.0)
    assert parameters.driven_index == 1


def test_yagi_dialog_restores_existing_geometry(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.yagi import nbs_five_element

    original = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=8.0,
        azimuth_deg=20.0,
    )
    dialog = YagiDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog._table.rowCount() == 5
    restored = dialog.parameters()
    assert restored.frequency_hz == pytest.approx(original.frequency_hz)
    assert restored.azimuth_deg == pytest.approx(original.azimuth_deg)
    assert restored.driven_index == original.driven_index


def test_yagi_dialog_restores_vertical_polarization(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.polarization import Polarization
    from antennadesk.domain.antennas.yagi import nbs_five_element

    original = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=8.0,
        polarization=Polarization.VERTICAL,
    )
    dialog = YagiDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    restored = dialog.parameters()
    assert restored.polarization is Polarization.VERTICAL
    assert restored.height_m == pytest.approx(original.height_m)
    assert restored.azimuth_deg == pytest.approx(original.azimuth_deg)
    assert restored.driven_index == original.driven_index
    assert dialog._form._polarization.currentData() == "vertical"


def test_yagi_dialog_supports_a_folded_driven_element(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    dialog._driven_folded.setChecked(True)
    dialog._driven_fold_spacing.setValue(0.08)
    parameters = dialog.parameters()

    assert parameters.driven_folded is True
    assert parameters.driven_fold_spacing_m == pytest.approx(0.08, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 8


def test_yagi_dialog_supports_a_beta_hairpin_match(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.yagi import YagiMatchType

    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    index = dialog._match_type.findData(YagiMatchType.BETA_HAIRPIN.value)
    dialog._match_type.setCurrentIndex(index)
    dialog._match_length.setValue(0.2)
    dialog._match_spacing.setValue(0.1)
    parameters = dialog.parameters()

    assert parameters.match_type is YagiMatchType.BETA_HAIRPIN
    assert parameters.match_length_m == pytest.approx(0.2, abs=1e-3)
    assert parameters.match_spacing_m == pytest.approx(0.1, abs=1e-3)
    assert len(parameters.to_antenna().wires) == 10


def test_yagi_dialog_disables_match_with_folded_driven(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.yagi import YagiMatchType

    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    index = dialog._match_type.findData(YagiMatchType.BETA_HAIRPIN.value)
    dialog._match_type.setCurrentIndex(index)
    dialog._driven_folded.setChecked(True)

    assert dialog._match_type.currentData() == YagiMatchType.NONE.value
    assert dialog._match_type.isEnabled() is False
    assert dialog.parameters().match_type is YagiMatchType.NONE


def test_yagi_dialog_restores_folded_driven_settings(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.yagi import nbs_five_element

    original = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=8.0,
        folded_driven=True,
        folded_spacing_m=0.12,
    )
    dialog = YagiDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        parameters=original,
    )
    qtbot.addWidget(dialog)

    assert dialog._driven_folded.isChecked() is True
    assert dialog.parameters().driven_fold_spacing_m == pytest.approx(0.12)


def test_yagi_dialog_warns_when_vertical_elements_reach_the_ground(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog._form._height.setValue(1.0)
    index = dialog._form._polarization.findData("vertical")
    dialog._form._polarization.setCurrentIndex(index)

    assert dialog._form._clearance_warning.isHidden() is False
    assert "greater than" in dialog._form._clearance_warning.text()
    with pytest.raises(ValueError, match="below ground"):
        dialog.parameters()


def test_yagi_dialog_scales_elements_when_frequency_changes(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    original_length = float(dialog._table.item(1, 2).text())
    original_position = float(dialog._table.item(1, 1).text())

    dialog._form._frequency.setValue(7.1)

    scaled_length = float(dialog._table.item(1, 2).text())
    scaled_position = float(dialog._table.item(1, 1).text())
    assert scaled_length == pytest.approx(original_length * 2.0, rel=0.02)
    assert scaled_position == pytest.approx(original_position * 2.0, rel=0.02)
    assert dialog._form._frequency_warning.isVisible() is False
    assert dialog.parameters().frequency_hz == pytest.approx(7_100_000.0)


def test_yagi_dialog_warns_about_a_frequency_mismatch(qtbot: QtBot) -> None:
    dialog = YagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog.show()
    dialog._table.item(1, 2).setText("5.000")

    assert dialog._form._frequency_warning.isHidden() is False
