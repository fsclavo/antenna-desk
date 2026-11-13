# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run project bundle export or import without blocking the Qt event loop."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from ...application.use_cases.project_bundle import (
    ExportProjectBundle,
    ImportProjectBundle,
)
from ...domain.projects.project import Project


class ProjectBundleExportWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        use_case: ExportProjectBundle,
        project: Project,
        bundle_path: Path,
        *,
        base_dir: Path | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._use_case = use_case
        self._project = project
        self._bundle_path = bundle_path
        self._base_dir = base_dir

    @Slot()
    def run(self) -> None:
        try:
            result = self._use_case.execute(
                self._project,
                self._bundle_path,
                base_dir=self._base_dir,
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)


class ProjectBundleImportWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        use_case: ImportProjectBundle,
        bundle_path: Path,
        destination_parent: Path,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._use_case = use_case
        self._bundle_path = bundle_path
        self._destination_parent = destination_parent

    @Slot()
    def run(self) -> None:
        try:
            result = self._use_case.execute(
                self._bundle_path,
                self._destination_parent,
            )
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
