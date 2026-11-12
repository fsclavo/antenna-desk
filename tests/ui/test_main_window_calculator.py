# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Component calculator action in the main window."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.antennas.load import SeriesLoad
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.dialogs.component_calculator_dialog import CalculatorSeed
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


class _FakeCalculatorDialog:
    captured: CalculatorSeed | None = None

    def __init__(self, *args: object, **kwargs: object) -> None:
        seed = kwargs.get("seed")
        type(self).captured = seed if isinstance(seed, CalculatorSeed) else None

    def exec(self) -> QDialog.DialogCode:
        return QDialog.DialogCode.Rejected

    def calculator_result(self) -> None:
        return None


def test_calculator_action_is_in_tools_and_retranslates(window: MainWindow) -> None:
    assert window._calculator_action in window._tools_menu.actions()
    assert window._calculator_action.text() == "Component Calculators..."

    window._set_language(Language.SPANISH)

    assert window._calculator_action.text() == "Calculadoras de componentes..."
    window._set_language(Language.ENGLISH)


def test_calculator_action_seeds_from_the_current_load(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    assert window._design_id is not None
    design = window._project.design_by_id(window._design_id)
    design = design.with_loads((SeriesLoad("coil", "radiator", 5.0, inductance_h=12e-6),))
    window._project = window._project.with_design(
        design,
        updated_at=window._project.updated_at,
    )
    monkeypatch.setattr(
        main_window_module,
        "ComponentCalculatorDialog",
        _FakeCalculatorDialog,
    )

    window.show_component_calculators()

    assert _FakeCalculatorDialog.captured is not None
    assert _FakeCalculatorDialog.captured.tab == "coil"
    assert _FakeCalculatorDialog.captured.inductance_h == pytest.approx(12e-6)
