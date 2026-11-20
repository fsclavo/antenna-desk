# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Autosave timers, recovery storage, and the startup recovery prompt."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox, QWidget

from ..domain.projects.project import Project
from .i18n import Translator
from .recovery import AutosaveRecovery, RecoverySnapshot, RecoveryTooLargeError


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    restore: bool
    path: Path | None


class RecoveryController:
    """Own the autosave cadence and the recovery-file prompts."""

    def __init__(
        self,
        parent: QWidget,
        translator: Translator,
        recovery: Callable[[], AutosaveRecovery | None],
        on_autosave: Callable[[], object],
    ) -> None:
        self._parent = parent
        self._translator = translator
        self._recovery_provider = recovery
        self._enabled = False
        self._timer = QTimer(parent)
        self._timer.setInterval(30_000)
        self._timer.timeout.connect(on_autosave)
        self._debounce = QTimer(parent)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(2_000)
        self._debounce.timeout.connect(on_autosave)

    def _recovery(self) -> AutosaveRecovery | None:
        return self._recovery_provider()

    @property
    def available(self) -> bool:
        return self._recovery() is not None

    def set_enabled(self, enabled: bool, *, pending: bool = False) -> None:
        self._enabled = enabled and self._recovery() is not None
        if self._enabled:
            self._timer.start()
            if pending:
                self._debounce.start()
        else:
            self.stop()

    def schedule(self) -> None:
        if self._enabled:
            self._debounce.start()

    def stop_debounce(self) -> None:
        self._debounce.stop()

    def stop(self) -> None:
        self._timer.stop()
        self._debounce.stop()

    def clear(self) -> bool:
        recovery = self._recovery()
        if recovery is None:
            return False
        try:
            recovery.clear()
        except OSError:
            return False
        return True

    def load(self) -> RecoverySnapshot | None:
        recovery = self._recovery()
        if recovery is None:
            return None
        try:
            return recovery.load()
        except Exception:
            self.clear()
            QMessageBox.warning(
                self._parent,
                self._translator.t("dialog.recovery_title"),
                self._translator.t("dialog.recovery_corrupt"),
            )
            return None

    def save(self, project: Project, path: Path | None) -> bool:
        recovery = self._recovery()
        if recovery is None:
            return False
        try:
            recovery.save(project, original_path=path, dirty=True)
        except RecoveryTooLargeError:
            return False
        except Exception:
            return False
        return True

    def offer(self, snapshot: RecoverySnapshot) -> RecoveryDecision:
        if not snapshot.project.designs:
            self.clear()
            return RecoveryDecision(restore=False, path=None)
        path = snapshot.original_path
        if path is not None and not path.is_file():
            path = None
        name = path.name if path is not None else self._translator.t("recovery.untitled")
        answer = QMessageBox.question(
            self._parent,
            self._translator.t("dialog.recovery_title"),
            self._translator.t("dialog.recovery_message", name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        self.clear()
        return RecoveryDecision(
            restore=answer == QMessageBox.StandardButton.Yes,
            path=path,
        )
