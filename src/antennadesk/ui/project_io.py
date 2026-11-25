# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project open/save workers, progress dialogs, and file pickers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QProgressDialog,
    QWidget,
)

from ..application.ports.project_repository import ProjectRepository
from ..application.project_payload import PreparedProject
from ..application.project_session import ProjectSession
from ..application.use_cases.open_project import OpenProjectSession
from ..application.use_cases.save_project import SaveProject
from ..domain.projects.project import Project
from .i18n import Translator
from .workers.open_project_worker import OpenProjectWorker
from .workers.save_project_worker import SaveProjectWorker
from .workers.task_runner import run_worker_blocking


@dataclass(frozen=True, slots=True)
class ProjectIO:
    """Run project file work off the GUI thread with a modal progress dialog."""

    parent: QWidget
    translator: Translator
    repository: ProjectRepository

    def choose_open_path(self, start: Path) -> Path | None:
        filename, _ = QFileDialog.getOpenFileName(
            self.parent,
            self.translator.t("dialog.open_title"),
            str(start),
            self.translator.t("dialog.project_filter"),
        )
        return Path(filename) if filename else None

    def choose_save_path(self, project_name: str) -> Path | None:
        safe_name = project_name.replace("/", "-").replace("\\", "-")
        filename, _ = QFileDialog.getSaveFileName(
            self.parent,
            self.translator.t("dialog.save_title"),
            str(Path.home() / f"{safe_name}.antennadesk"),
            self.translator.t("dialog.project_filter"),
        )
        if not filename:
            return None
        path = Path(filename)
        if path.suffix.lower() != ".antennadesk":
            path = path.with_suffix(".antennadesk")
        return path

    def load_session(self, path: Path) -> ProjectSession:
        progress = self._progress_dialog("status.opening", "dialog.open_title")
        try:
            value = self._run_worker(
                OpenProjectWorker(OpenProjectSession(self.repository), path),
                "finished",
            )
        finally:
            progress.close()
        if not isinstance(value, ProjectSession):
            raise RuntimeError("open worker produced no project session")
        return value

    def open_design_only(self, path: Path) -> Project:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            return self.repository.open_design_only(path)
        finally:
            QApplication.restoreOverrideCursor()

    def prepare_payload(self, project: Project) -> PreparedProject:
        return self._prepare_worker(SaveProjectWorker(SaveProject(self.repository), project))

    def prepare_session_payload(
        self,
        session: ProjectSession,
        project: Project,
        *,
        retained_only: bool = False,
    ) -> PreparedProject:
        return self._prepare_worker(
            SaveProjectWorker(
                SaveProject(self.repository),
                project,
                session,
                retained_only=retained_only,
            )
        )

    def _prepare_worker(self, worker: SaveProjectWorker) -> PreparedProject:
        progress = self._progress_dialog("status.preparing_save", "dialog.save_title")
        try:
            value = self._run_worker(worker, "prepared")
        finally:
            progress.close()
        if not isinstance(value, PreparedProject):
            raise RuntimeError("save worker produced no payload")
        return value

    def write(self, path: Path, payload: PreparedProject) -> None:
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            SaveProject(self.repository).write(path, payload)
        finally:
            QApplication.restoreOverrideCursor()

    def run_bundle_worker(self, worker: QObject, text_key: str) -> object:
        progress = self._progress_dialog(text_key, "app.title")
        try:
            return self._run_worker(worker, "finished")
        finally:
            progress.close()

    def _progress_dialog(self, text_key: str, title_key: str) -> QProgressDialog:
        dialog = QProgressDialog(
            self.translator.t(text_key),
            "",
            0,
            0,
            self.parent,
        )
        dialog.setWindowTitle(self.translator.t(title_key))
        dialog.setWindowModality(Qt.WindowModality.WindowModal)
        dialog.setCancelButton(None)
        dialog.setMinimumDuration(250)
        dialog.setAutoClose(False)
        dialog.setAutoReset(False)
        dialog.setValue(0)
        return dialog

    def _run_worker(self, worker: QObject, success_signal: str) -> object:
        return run_worker_blocking(self.parent, worker, success_signal=success_signal)
