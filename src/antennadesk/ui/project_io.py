# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project open/save workers, progress dialogs, and file pickers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from PySide6.QtCore import QEventLoop, QObject, Qt, QThread
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QProgressDialog,
    QWidget,
)

from ..application.ports.project_repository import ProjectRepository
from ..application.use_cases.open_project import OpenProject
from ..application.use_cases.save_project import SaveProject
from ..domain.projects.project import Project
from .i18n import Translator
from .workers.open_project_worker import OpenProjectWorker
from .workers.save_project_worker import SaveProjectWorker


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

    def load(self, path: Path) -> Project:
        progress = self._progress_dialog("status.opening", "dialog.open_title")
        try:
            value = self._run_worker(
                OpenProjectWorker(OpenProject(self.repository), path),
                "finished",
            )
        finally:
            progress.close()
        if not isinstance(value, Project):
            raise RuntimeError("open worker produced no project")
        return value

    def prepare_payload(self, project: Project) -> bytes:
        progress = self._progress_dialog("status.preparing_save", "dialog.save_title")
        try:
            value = self._run_worker(
                SaveProjectWorker(SaveProject(self.repository), project),
                "prepared",
            )
        finally:
            progress.close()
        if not isinstance(value, bytes):
            raise RuntimeError("save worker produced no payload")
        return value

    def write(self, path: Path, payload: bytes) -> None:
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
        thread = QThread(self.parent)
        worker.moveToThread(thread)
        result: dict[str, object] = {}
        loop = QEventLoop()

        def finished(value: object) -> None:
            result["value"] = value
            loop.quit()

        def failed(message: str) -> None:
            result["error"] = message
            loop.quit()

        worker_object = cast(Any, worker)
        success = getattr(worker_object, success_signal)
        failure = worker_object.failed
        success.connect(finished)
        failure.connect(failed)
        success.connect(thread.quit)
        failure.connect(thread.quit)
        thread.started.connect(worker_object.run)
        thread.finished.connect(loop.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        try:
            loop.exec()
        finally:
            thread.quit()
            thread.wait()
        error = result.get("error")
        if isinstance(error, str):
            raise ValueError(error)
        return result.get("value")
