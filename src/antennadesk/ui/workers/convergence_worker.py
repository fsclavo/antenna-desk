# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run a segmentation convergence study off the GUI thread."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ...application.use_cases.run_convergence_study import (
    RunConvergenceStudy,
    RunConvergenceStudyCommand,
)


class ConvergenceWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        study: RunConvergenceStudy,
        command: RunConvergenceStudyCommand,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._study = study
        self._command = command

    @Slot()
    def run(self) -> None:
        try:
            result = self._study.execute(self._command)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
