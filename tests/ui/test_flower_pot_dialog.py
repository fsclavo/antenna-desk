# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Flower Pot form and dialog behavior."""

from __future__ import annotations

from dataclasses import replace

import pytest
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QLabel
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.flower_pot import (
    FLOWER_POT_2M_BOTTOM_LENGTH_M,
    FLOWER_POT_2M_TOP_LENGTH_M,
    FLOWER_POT_6M_BOTTOM_LENGTH_M,
    FLOWER_POT_6M_TOP_LENGTH_M,
    FLOWER_POT_ELECTRICAL_LENGTH_SCALE,
    FlowerPotParameters,
    flower_pot_2m,
)
from antennadesk.ui.dialogs.flower_pot_dialog import FlowerPotDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.preferences import FontSize, FontSizeController
from antennadesk.ui.units import UnitSystem, radius_to_m
from antennadesk.ui.widgets.flower_pot_form import FlowerPotForm
from antennadesk.ui.widgets.form_dialog import FormDialogFrame


def _form(qtbot: QtBot) -> FlowerPotForm:
    form = FlowerPotForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    return form


def test_form_keeps_the_physical_cuts_and_the_electrical_model_separate(
    qtbot: QtBot,
) -> None:
    form = _form(qtbot)

    parameters = form.parameters()

    assert parameters.top_length_m == pytest.approx(FLOWER_POT_2M_TOP_LENGTH_M)
    assert parameters.bottom_length_m == pytest.approx(FLOWER_POT_2M_BOTTOM_LENGTH_M)
    assert parameters.choke_height_m == pytest.approx(0.045)
    assert parameters.base_height_m == pytest.approx(1.0)
    assert parameters.choke_height_m == pytest.approx(0.045)
    assert parameters.physical_total_length_m == pytest.approx(0.904)
    assert parameters.electrical_total_length_m == pytest.approx(
        0.904 * FLOWER_POT_ELECTRICAL_LENGTH_SCALE
    )
    summary = form._geometry.text().lower()
    assert "physical" in summary
    assert "electrical" in summary
    assert "choke" in summary


def test_form_loads_the_published_2m_and_6m_rows(qtbot: QtBot) -> None:
    form = _form(qtbot)

    form.load_6m_example()
    parameters = form.parameters()
    assert parameters.frequency_hz == pytest.approx(52_700_000.0)
    assert parameters.top_length_m == pytest.approx(FLOWER_POT_6M_TOP_LENGTH_M)
    assert parameters.bottom_length_m == pytest.approx(FLOWER_POT_6M_BOTTOM_LENGTH_M)
    assert parameters.base_height_m == pytest.approx(1.0)
    assert parameters.choke_height_m == pytest.approx(0.063)

    form.load_2m_example()
    parameters = form.parameters()
    assert parameters.frequency_hz == pytest.approx(146_000_000.0)
    assert parameters.top_length_m == pytest.approx(FLOWER_POT_2M_TOP_LENGTH_M)
    assert parameters.bottom_length_m == pytest.approx(FLOWER_POT_2M_BOTTOM_LENGTH_M)


def test_form_preserves_a_loaded_model_scale_and_construction_factor(
    qtbot: QtBot,
) -> None:
    form = _form(qtbot)
    loaded = replace(
        flower_pot_2m(),
        construction_shortening_factor=0.9,
        electrical_length_scale=1.05,
    )

    form.set_parameters(loaded)

    restored = form.parameters()
    assert restored == loaded


def test_form_switches_units_without_losing_both_radii(qtbot: QtBot) -> None:
    form = _form(qtbot)
    before = form.parameters()

    form.set_unit_system(UnitSystem.IMPERIAL)

    after = form.parameters()
    assert form._top_radius.suffix().strip() == "in"
    assert form._bottom_radius.suffix().strip() == "in"
    assert after.top_length_m == pytest.approx(before.top_length_m, rel=1e-3)
    assert after.bottom_length_m == pytest.approx(before.bottom_length_m, rel=1e-3)
    assert after.choke_height_m == pytest.approx(before.choke_height_m, abs=2e-4)
    assert radius_to_m(form._top_radius.value(), UnitSystem.IMPERIAL) == pytest.approx(
        before.top_radius_m,
        abs=2e-6,
    )
    assert radius_to_m(form._bottom_radius.value(), UnitSystem.IMPERIAL) == pytest.approx(
        before.bottom_radius_m,
        abs=2e-6,
    )


def test_form_rejects_a_base_height_that_puts_the_scaled_tip_below_ground(
    qtbot: QtBot,
) -> None:
    form = _form(qtbot)
    form._base_height_field.configure(0.01)
    form._choke_height_field.configure(0.0)

    with pytest.raises(ValueError, match="scaled electrical lower tip"):
        form.parameters()


def test_form_applies_bilingual_help_to_physical_cut_fields(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    form = FlowerPotForm(translator, UnitSystem.METRIC)
    qtbot.addWidget(form)

    labels = {label.objectName(): label for label in form.findChildren(QLabel)}
    assert "Physical top coax cut" in labels["flower_pot.top_length"].toolTip()
    assert "Physical bottom coax cut" in labels["flower_pot.bottom_length"].toolTip()
    assert "not the 1.087 NEC electrical scale" in (
        labels["flower_pot.construction_factor"].toolTip()
    )
    assert "45 mm" in labels["flower_pot.choke_height"].toolTip()
    assert "physical feed connector" in labels["flower_pot.base_height"].toolTip()

    translator.set_language(Language.SPANISH)
    form.retranslate()

    assert "Corte físico superior" in labels["flower_pot.top_length"].toolTip()


def test_results_view_anchors_the_pattern_overlay_at_the_physical_feed(
    qtbot: QtBot,
) -> None:
    from antennadesk.application.use_cases.create_dipole_project import (
        CreateDipoleProject,
        CreateDipoleProjectCommand,
    )
    from antennadesk.ui.widgets.results_view import ResultsView

    parameters = flower_pot_2m()
    design = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="Flower Pot overlay",
            variant_name="Flower Pot",
            parameters=parameters,
        )
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_design(design.designs[0])

    overlay = view._pattern_3d._overlay
    assert overlay is not None
    assert overlay.feed == pytest.approx((0.0, 0.0, parameters.physical_feed_height_m))
    assert overlay.center == pytest.approx(overlay.feed)
    lowest = min(point[2] for wire in overlay.wires for point in (wire.start, wire.end))
    assert lowest >= parameters.physical_feed_height_m - 1e-9
    assert parameters.physical_junction_height_m > parameters.physical_feed_height_m


def test_dialog_keeps_actions_visible_with_large_spanish(
    qtbot: QtBot,
) -> None:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    controller = FontSizeController(QFont("Sans Serif", 10))
    controller.apply(FontSize.LARGE)
    try:
        dialog = FlowerPotDialog(Translator(Language.SPANISH), UnitSystem.METRIC)
        qtbot.addWidget(dialog)
        dialog.resize(600, 640)
        dialog.show()
        qtbot.wait(10)
        QApplication.processEvents()

        buttons = dialog.findChild(QDialogButtonBox)
        assert buttons is not None
        assert buttons.isVisible() is True
        assert buttons.geometry().bottom() <= dialog.rect().bottom()
        assert dialog._scroll is not None
        assert dialog._scroll.horizontalScrollBar().maximum() == 0
    finally:
        controller.apply(FontSize.MEDIUM)


def test_dialog_loads_a_preset_and_returns_a_first_class_design(
    qtbot: QtBot,
) -> None:
    dialog = FlowerPotDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert isinstance(dialog, FormDialogFrame)
    assert dialog.notes
    dialog._example_2m.click()
    parameters = dialog.parameters()

    assert isinstance(parameters, FlowerPotParameters)
    assert parameters.frequency_hz == pytest.approx(146_000_000.0)
    assert parameters.top_length_m == pytest.approx(FLOWER_POT_2M_TOP_LENGTH_M)
