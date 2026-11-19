# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main-window autosave, restore, discard, and save-as fallback."""

from __future__ import annotations

from pathlib import Path

import pytest
from main_window_support import FakeSolver
from PySide6.QtWidgets import QFileDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.recovery import AutosaveRecovery
from antennadesk.ui.units import UnitSystem


def _window(
    qtbot: QtBot,
    recovery: AutosaveRecovery | None = None,
) -> MainWindow:
    window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        recovery=recovery,
    )
    qtbot.addWidget(window)
    return window


def test_autosave_writes_a_recovery_and_restores_the_project(
    window: MainWindow,
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())
    window._recovery = recovery
    window._autosave_enabled = True
    window._dirty = True

    assert window._autosave_now() is True
    assert recovery.project_path.is_file()

    restored = _window(qtbot, recovery)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    restored._startup_recovery()

    assert restored._project == window._project
    assert restored._dirty is True
    assert restored._current_path is None
    restored._dirty = False
    restored.close()
    window._dirty = False


def test_autosave_is_cleared_by_a_normal_save(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())
    window._recovery = recovery
    window._autosave_enabled = True
    window._dirty = True
    assert window._autosave_now() is True
    target = tmp_path / "saved.antennadesk"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), ""),
    )

    assert window.save_project_as() is True

    assert not recovery.project_path.exists()
    assert not recovery.metadata_path.exists()
    window._dirty = False


def test_missing_original_path_falls_back_to_save_as(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())
    recovery.save(
        sample_project,
        original_path=tmp_path / "moved-away.antennadesk",
        dirty=True,
    )
    window = _window(qtbot, recovery)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    window._startup_recovery()

    assert window._project == sample_project
    assert window._current_path is None
    assert window._dirty is True

    target = tmp_path / "save-as.antennadesk"
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), ""),
    )
    assert window.save_project() is True
    assert target.is_file()
    assert not recovery.project_path.exists()
    window._dirty = False
    window.close()


def test_discard_recovery_removes_the_copy(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())
    recovery.save(sample_project, original_path=None, dirty=True)
    window = _window(qtbot, recovery)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.No,
    )

    window._startup_recovery()

    assert window._project is None
    assert recovery.load() is None
    window.close()


def test_corrupt_recovery_is_discarded(
    qtbot: QtBot,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())
    recovery.directory.mkdir(parents=True)
    recovery.project_path.write_bytes(b"not a project")
    window = _window(qtbot, recovery)
    warnings: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: warnings.append(str(args[2])),
    )

    window._startup_recovery()

    assert warnings
    assert recovery.load() is None
    assert window._project is None
    window.close()


def test_normal_close_clears_the_recovery(
    window: MainWindow,
    tmp_path: Path,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())
    window._recovery = recovery
    window._autosave_enabled = True
    window._dirty = True
    assert window._autosave_now() is True

    window._dirty = False
    window.close()

    assert recovery.load() is None
