# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.environment.ground import GroundKind
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.wizard.dipole_wizard import DipoleWizard


def test_wizard_builds_parameters(qtbot: QtBot) -> None:
    wizard = DipoleWizard(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        initial_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(wizard)
    wizard.project_page.set_project_name("Test dipole")
    wizard.geometry_page.initializePage()

    parameters = wizard.build_parameters()

    assert wizard.project_name() == "Test dipole"
    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert parameters.total_length_m > 19.0
    assert parameters.height_m == pytest.approx(8.0)
    assert parameters.wire_radius_m == pytest.approx(0.001)
    assert parameters.material.name == "copper"
    assert parameters.ground.kind is GroundKind.FINITE


def test_wizard_review_accepts_valid_design(qtbot: QtBot) -> None:
    wizard = DipoleWizard(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(wizard)
    wizard.geometry_page.initializePage()
    wizard.review_page.initializePage()

    assert wizard.review_page.isComplete() is True


def test_wizard_supports_spanish_and_imperial(qtbot: QtBot) -> None:
    wizard = DipoleWizard(
        Translator(Language.SPANISH),
        UnitSystem.IMPERIAL,
        initial_frequency_hz=14_100_000.0,
    )
    qtbot.addWidget(wizard)

    assert wizard.windowTitle() == "Nueva antena"
    assert wizard.build_parameters().total_length_m > 9.0


def test_wizard_builds_a_vertical_dipole(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.dipole import DipoleOrientation

    wizard = DipoleWizard(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        initial_frequency_hz=7_100_000.0,
    )
    qtbot.addWidget(wizard)
    wizard.geometry_page._orientation.setCurrentIndex(1)
    wizard.geometry_page.initializePage()

    parameters = wizard.build_parameters()

    assert parameters.orientation is DipoleOrientation.VERTICAL
    antenna = parameters.to_antenna()
    assert antenna.wires[0].start.z_m == pytest.approx(8.0)
    assert antenna.wires[0].end.z_m > 8.0


def test_wizard_builds_a_loop(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.loop import ANTENNA_TYPE_LOOP, LoopParameters

    wizard = DipoleWizard(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        initial_frequency_hz=7_100_000.0,
        initial_antenna_type=ANTENNA_TYPE_LOOP,
    )
    qtbot.addWidget(wizard)
    wizard.geometry_page.initializePage()

    parameters = wizard.build_parameters()

    assert wizard.project_page.antenna_type() == ANTENNA_TYPE_LOOP
    assert wizard.windowTitle() == "New Antenna"
    assert wizard.project_name() == "40 m loop"
    assert isinstance(parameters, LoopParameters)
    assert parameters.circumference_m > 35.0
    assert parameters.sides == 16
    assert len(parameters.to_antenna().wires) == 16


def test_wizard_builds_a_folded_dipole(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.folded_dipole import (
        ANTENNA_TYPE_FOLDED_DIPOLE,
        FoldedDipoleParameters,
    )

    wizard = DipoleWizard(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        initial_frequency_hz=7_100_000.0,
        initial_antenna_type=ANTENNA_TYPE_FOLDED_DIPOLE,
    )
    qtbot.addWidget(wizard)
    wizard.geometry_page.initializePage()

    parameters = wizard.build_parameters()

    assert wizard.project_page.antenna_type() == ANTENNA_TYPE_FOLDED_DIPOLE
    assert wizard.project_name() == "40 m folded dipole"
    assert isinstance(parameters, FoldedDipoleParameters)
    assert parameters.total_length_m > 19.0
    assert parameters.spacing_m == pytest.approx(0.1)
    assert len(parameters.to_antenna().wires) == 4


def test_wizard_antenna_type_list_is_populated(qtbot: QtBot) -> None:
    wizard = DipoleWizard(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(wizard)
    combo = wizard.project_page._type

    texts = [combo.itemText(index) for index in range(combo.count())]

    assert texts == ["Wire dipole", "Folded dipole", "Loop"]
    assert all(texts)


def test_wizard_antenna_type_list_is_translated(qtbot: QtBot) -> None:
    wizard = DipoleWizard(Translator(Language.SPANISH), UnitSystem.METRIC)
    qtbot.addWidget(wizard)
    combo = wizard.project_page._type

    texts = [combo.itemText(index) for index in range(combo.count())]

    assert texts == ["Dipolo de hilo", "Dipolo plegado", "Lazo"]


def test_wizard_accepts_an_initial_loop_side_count(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.loop import ANTENNA_TYPE_LOOP

    wizard = DipoleWizard(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        initial_antenna_type=ANTENNA_TYPE_LOOP,
        initial_sides=3,
    )
    qtbot.addWidget(wizard)
    wizard.geometry_page.initializePage()

    parameters = wizard.build_parameters()

    assert parameters.sides == 3
