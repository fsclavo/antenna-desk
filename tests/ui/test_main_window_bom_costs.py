# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""BOM cost action in the main window."""

from __future__ import annotations

from typing import ClassVar

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.projects.bom_costs import BomCostLine, BomCostRecord
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


class _FakeBomCostsDialog:
    captured: ClassVar[dict[str, object]] = {}
    record: ClassVar[BomCostRecord | None] = None
    decision = QDialog.DialogCode.Accepted

    def __init__(self, *args: object) -> None:
        type(self).captured = {"args": args}

    def exec(self) -> QDialog.DialogCode:
        return type(self).decision

    def result_bom_costs(self) -> BomCostRecord | None:
        return type(self).record


def test_bom_costs_action_is_in_the_design_menu_and_retranslates(
    window: MainWindow,
) -> None:
    assert window._bom_costs_action in window._design_menu.actions()
    assert window._bom_costs_action.text() == "BOM Costs..."
    assert window._bom_costs_action.toolTip()

    window._set_language(Language.SPANISH)

    assert window._bom_costs_action.text() == "Costos del BOM..."
    assert window._bom_costs_action.toolTip()
    window._set_language(Language.ENGLISH)


def test_bom_costs_action_applies_and_undoes(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    window._form_dirty = False
    window._dirty = False
    window._clean_signature = window._current_project_signature()
    record = BomCostRecord(
        currency="USD",
        lines=(BomCostLine("hardware:end_insulators", 1.0),),
    )
    _FakeBomCostsDialog.record = record
    _FakeBomCostsDialog.decision = QDialog.DialogCode.Accepted
    monkeypatch.setattr(
        main_window_module,
        "BomCostsDialog",
        _FakeBomCostsDialog,
    )
    before = window._undo_stack.count()

    window.edit_bom_costs()

    assert window._project.bom_costs == record
    assert window._last_status_key == "status.bom_costs_saved"
    assert window._undo_stack.count() == before + 1

    window._undo_stack.undo()

    assert window._project.bom_costs is None


def test_bom_costs_action_without_change_does_not_touch_history(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window._form_dirty = False
    window._dirty = False
    _FakeBomCostsDialog.record = None
    _FakeBomCostsDialog.decision = QDialog.DialogCode.Accepted
    monkeypatch.setattr(
        main_window_module,
        "BomCostsDialog",
        _FakeBomCostsDialog,
    )
    before = window._undo_stack.count()

    window.edit_bom_costs()

    assert window._project.bom_costs is None
    assert window._undo_stack.count() == before
