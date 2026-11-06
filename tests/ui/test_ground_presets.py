# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox
from pytestqt.qtbot import QtBot

from antennadesk.domain.environment.ground import GroundKind, GroundModel
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.ground_presets import (
    CUSTOM_SOIL_KEY,
    GroundPresetController,
    matching_soil_key,
)
from antennadesk.ui.widgets.vertical_form import VerticalForm


def _editor(
    qtbot: QtBot,
    *,
    translator: Translator | None = None,
) -> tuple[QComboBox, QComboBox, QDoubleSpinBox, QDoubleSpinBox, GroundPresetController]:
    ground = QComboBox()
    soil = QComboBox()
    permittivity = QDoubleSpinBox()
    conductivity = QDoubleSpinBox()
    permittivity.setRange(1.0, 1_000.0)
    permittivity.setDecimals(2)
    conductivity.setRange(0.000001, 1_000.0)
    conductivity.setDecimals(6)
    permittivity.setValue(13.0)
    conductivity.setValue(0.005)
    for widget in (ground, soil, permittivity, conductivity):
        qtbot.addWidget(widget)
    ground.addItem("", GroundKind.FREE_SPACE.value)
    ground.addItem("", GroundKind.PERFECT.value)
    ground.addItem("", GroundKind.FINITE.value)
    ground.setCurrentIndex(2)
    controller = GroundPresetController(
        ground,
        soil,
        permittivity,
        conductivity,
        translator or Translator(Language.ENGLISH),
    )
    return ground, soil, permittivity, conductivity, controller


def test_average_values_select_the_average_preset(qtbot: QtBot) -> None:
    _, soil, _, _, _ = _editor(qtbot)

    assert soil.currentData() == "average"
    assert matching_soil_key(13.0, 0.005) == "average"


def test_selecting_a_preset_updates_the_numeric_values(qtbot: QtBot) -> None:
    _, soil, permittivity, conductivity, _ = _editor(qtbot)

    soil.setCurrentIndex(soil.findData("salt_water"))

    assert permittivity.value() == pytest.approx(81.0)
    assert conductivity.value() == pytest.approx(5.0)
    assert matching_soil_key(81.0, 5.0) == "salt_water"


def test_editing_a_value_switches_to_custom(qtbot: QtBot) -> None:
    _, soil, permittivity, _, _ = _editor(qtbot)

    permittivity.setValue(42.0)

    assert soil.currentData() == CUSTOM_SOIL_KEY
    assert matching_soil_key(42.0, 0.005) == CUSTOM_SOIL_KEY


def test_preset_selector_is_enabled_only_for_finite_ground(qtbot: QtBot) -> None:
    ground, soil, _, _, _ = _editor(qtbot)

    assert soil.isEnabled() is True
    ground.setCurrentIndex(ground.findData(GroundKind.FREE_SPACE.value))
    assert soil.isEnabled() is False
    ground.setCurrentIndex(ground.findData(GroundKind.FINITE.value))
    assert soil.isEnabled() is True


def test_preset_labels_are_translated(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    _, soil, _, _, controller = _editor(qtbot, translator=translator)
    index = soil.findData("salt_water")
    assert soil.itemText(index) == "Salt water"

    translator.set_language(Language.SPANISH)

    # The controller is retranslated by the host form, not by the translator.
    controller.retranslate()
    assert soil.itemText(soil.findData("salt_water")) == "Agua salada"


def test_all_ground_editors_install_the_preset_selector() -> None:
    ui_root = Path(__file__).resolve().parents[2] / "src" / "antennadesk" / "ui"
    ground_editors = [
        path
        for path in ui_root.rglob("*.py")
        if 'self._conductivity.setSuffix(" S/m")' in path.read_text(encoding="utf-8")
    ]

    assert ground_editors
    for path in ground_editors:
        text = path.read_text(encoding="utf-8")
        assert "GroundPresetController" in text, path
        assert "field.soil_preset" in text, path


def test_vertical_form_exposes_the_soil_preset(qtbot: QtBot) -> None:
    form = VerticalForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)

    assert form._soil.currentData() == "average"
    form._soil.setCurrentIndex(form._soil.findData("salt_water"))
    parameters = form.parameters()
    assert parameters.ground == GroundModel.finite(
        relative_permittivity=81.0,
        conductivity_s_per_m=5.0,
    )

    form._permittivity.setValue(42.0)
    assert form._soil.currentData() == CUSTOM_SOIL_KEY
    assert form.parameters().ground.relative_permittivity == pytest.approx(42.0)
