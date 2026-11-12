# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run a comparison batch off the GUI thread."""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import QObject, Signal, Slot

from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.compare_designs import (
    CompareDesigns,
    CompareDesignsCommand,
    ComparisonOutcome,
)


class ComparisonWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        solver: AntennaSolver,
        command: CompareDesignsCommand,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._solver = solver
        self._command = command

    @Slot()
    def run(self) -> None:
        command = replace(
            self._command,
            progress_callback=lambda index, total, name: self.progress.emit(
                index,
                total,
                name,
            ),
        )
        try:
            outcome: ComparisonOutcome = CompareDesigns(self._solver).execute(command)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(outcome)
