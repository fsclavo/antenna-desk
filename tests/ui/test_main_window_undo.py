# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Undo, redo, dirty-state, and history behavior."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import wait_for_condition
from PySide6.QtWidgets import QInputDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.ui.main_window import MainWindow


def test_apply_design_can_be_undone_and_redone(window: MainWindow) -> None:
    original = window._project.designs[0].parameters
    window._form._length.setValue(22.0)
    window.apply_design()
    changed = window._project.designs[0].parameters
    assert changed != original

    window._undo_stack.undo()
    assert window._project.designs[0].parameters == original
    assert window._undo_stack.canRedo() is True

    window._undo_stack.redo()
    assert window._project.designs[0].parameters == changed
    window._dirty = False


def test_new_variant_can_be_undone_and_redone(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Undoable", True))
    window.new_variant()
    assert len(window._project.designs) == 2

    window._undo_stack.undo()
    assert len(window._project.designs) == 1
    window._undo_stack.redo()
    assert len(window._project.designs) == 2
    window._dirty = False


def test_save_sets_clean_history_and_undo_marks_dirty(
    window: MainWindow,
    tmp_path: Path,
) -> None:
    path = tmp_path / "history.antennadesk"
    window._form._length.setValue(21.0)
    window.apply_design()
    assert window._dirty is True

    assert window._save_to(path) is True
    assert window._dirty is False

    window._undo_stack.undo()
    assert window._dirty is True
    window._dirty = False


def test_simulation_runs_survive_undo_of_a_design_edit(
    window: MainWindow,
) -> None:
    window._form._length.setValue(21.0)
    window.apply_design()
    window.simulate()
    wait_for_condition(lambda: not window._simulating and window._thread is None)
    assert window._project is not None
    runs_after_simulation = len(window._project.simulation_runs)
    assert runs_after_simulation >= 1

    window._form._length.setValue(22.0)
    window.apply_design()
    window._undo_stack.undo()

    assert window._project is not None
    assert len(window._project.simulation_runs) == runs_after_simulation
    assert window._dirty is True
    window._dirty = False


def test_undo_actions_are_enabled_after_an_edit(window: MainWindow) -> None:
    assert window._undo_action.isEnabled() is False
    assert window._redo_action.isEnabled() is False

    window._form._length.setValue(21.0)
    window.apply_design()

    assert window._undo_action.isEnabled() is True
    window._undo_stack.undo()
    assert window._redo_action.isEnabled() is True
    window._dirty = False


def test_ctrl_z_in_a_text_editor_does_not_undo_the_project(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    from PySide6.QtCore import Qt

    window._form._length.setValue(21.0)
    window.apply_design()
    undo_index = window._undo_stack.index()
    window._project_name.setFocus()
    window._project_name.selectAll()
    qtbot.keyClicks(window._project_name, "Renamed")
    qtbot.keyClick(window._project_name, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)

    assert window._undo_stack.index() == undo_index
    assert window._project_name.text() != "Renamed"
    window._dirty = False


def test_project_undo_prompts_for_unapplied_form_changes(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window._form._length.setValue(21.0)
    window.apply_design()
    index = window._undo_stack.index()
    window._form._length.setValue(22.0)
    assert window._form_dirty is True

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )
    window._undo_project()
    assert window._undo_stack.index() == index

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    window._undo_project()
    assert window._undo_stack.index() == index - 1
    window._dirty = False
