# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run generic element optimization off the GUI thread."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.optimize_elements import (
    OptimizeElements,
    OptimizeElementsCommand,
)


class ElementOptimizationWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        solver: AntennaSolver,
        command: OptimizeElementsCommand,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._solver = solver
        self._command = command

    @Slot()
    def run(self) -> None:
        try:
            result = OptimizeElements(self._solver).execute(self._command)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
