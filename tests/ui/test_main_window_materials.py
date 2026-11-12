# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Materials reference action in the main window."""

from __future__ import annotations

from typing import ClassVar

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


class _FakeMaterialsDialog:
    captured: ClassVar[dict[str, object]] = {}
    decision = QDialog.DialogCode.Accepted
    feed_line: FeedLine | None = None

    def __init__(self, *args: object, **kwargs: object) -> None:
        type(self).captured = dict(kwargs)

    def exec(self) -> QDialog.DialogCode:
        return type(self).decision

    def result_feed_line(self) -> FeedLine | None:
        return type(self).feed_line


def test_materials_action_is_in_tools_and_retranslates(window: MainWindow) -> None:
    assert window._materials_action in window._tools_menu.actions()
    assert window._materials_action.text() == "Materials Reference..."

    window._set_language(Language.SPANISH)

    assert window._materials_action.text() == "Referencia de materiales..."
    window._set_language(Language.ENGLISH)


def test_materials_action_applies_a_feed_line_and_can_be_undone(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    previous = FeedLine(
        characteristic_impedance_ohm=75.0,
        length_m=15.0,
        velocity_factor=0.8,
        matched_loss_db_per_100m=1.5,
    )
    assert window._project is not None
    window._project = window._project.with_feed_line(
        previous,
        updated_at=window._project.updated_at,
    )
    window._feed_line = previous
    window._clean_signature = window._current_project_signature()
    window._dirty = False
    applied = FeedLine(
        characteristic_impedance_ohm=50.0,
        length_m=15.0,
        velocity_factor=0.66,
        matched_loss_db_per_100m=6.23,
    )
    _FakeMaterialsDialog.captured = {}
    _FakeMaterialsDialog.decision = QDialog.DialogCode.Accepted
    _FakeMaterialsDialog.feed_line = applied
    monkeypatch.setattr(
        main_window_module,
        "MaterialsReferenceDialog",
        _FakeMaterialsDialog,
    )
    before = window._undo_stack.count()

    window.show_materials_reference()

    assert _FakeMaterialsDialog.captured["feed_line"] == previous
    assert _FakeMaterialsDialog.captured["can_apply"] is True
    assert window._feed_line == applied
    assert window._project.feed_line == applied
    assert window._undo_stack.count() == before + 1

    window._undo_stack.undo()

    assert window._feed_line == previous
    assert window._project.feed_line == previous


def test_materials_action_cancel_does_not_change_the_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _FakeMaterialsDialog.decision = QDialog.DialogCode.Rejected
    _FakeMaterialsDialog.feed_line = FeedLine(length_m=10.0)
    monkeypatch.setattr(
        main_window_module,
        "MaterialsReferenceDialog",
        _FakeMaterialsDialog,
    )
    before = window._undo_stack.count()
    previous = window._feed_line

    window.show_materials_reference()

    assert window._feed_line == previous
    assert window._undo_stack.count() == before


def test_materials_action_disables_apply_without_a_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window._project = None
    window._design_id = None
    _FakeMaterialsDialog.captured = {}
    _FakeMaterialsDialog.decision = QDialog.DialogCode.Rejected
    monkeypatch.setattr(
        main_window_module,
        "MaterialsReferenceDialog",
        _FakeMaterialsDialog,
    )

    window.show_materials_reference()

    assert _FakeMaterialsDialog.captured["can_apply"] is False
