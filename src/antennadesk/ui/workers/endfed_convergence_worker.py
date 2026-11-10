# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run the end-fed segmentation convergence check off the GUI thread."""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from ...application.use_cases.check_endfed_convergence import (
    CheckEndFedConvergence,
    CheckEndFedConvergenceCommand,
)


class EndFedConvergenceWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        check: CheckEndFedConvergence,
        command: CheckEndFedConvergenceCommand,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._check = check
        self._command = command

    @Slot()
    def run(self) -> None:
        try:
            result = self._check.execute(self._command)
        except Exception as exc:
            self.failed.emit(str(exc))
            return
        self.finished.emit(result)
