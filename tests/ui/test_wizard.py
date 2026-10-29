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

    assert wizard.windowTitle() == "Nuevo dipolo"
    assert wizard.build_parameters().total_length_m > 9.0
