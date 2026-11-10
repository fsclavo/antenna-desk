# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run antenna synthesis off the GUI thread."""

from __future__ import annotations

from dataclasses import is_dataclass, replace

from PySide6.QtCore import QObject, Signal, Slot

from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.synthesize_antenna import (
    SynthesizeAntenna,
    SynthesizeAntennaCommand,
)


class SynthesisWorker(QObject):
    progress = Signal(int)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        solver: AntennaSolver,
        command: SynthesizeAntennaCommand,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._solver = solver
        self._command = command
        self._external_progress = getattr(command, "progress", None)
        if is_dataclass(command) and hasattr(command, "progress"):
            self._command = replace(command, progress=self._emit_progress)

    def _emit_progress(self, completed: int) -> None:
        if callable(self._external_progress):
            self._external_progress(completed)
        self.progress.emit(completed)

    @Slot()
    def run(self) -> None:
        try:
            result = SynthesizeAntenna(self._solver).execute(self._command)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
