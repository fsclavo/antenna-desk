# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project snapshot history and action decorator for undo/redo."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any
from uuid import UUID

from PySide6.QtGui import QUndoCommand

from ..domain.projects.project import Project


@dataclass(frozen=True, slots=True)
class ProjectSnapshot:
    project: Project | None
    design_id: UUID | None

    def signature(self) -> tuple[object, ...] | None:
        if self.project is None:
            return None
        return (
            self.project.name,
            self.project.description,
            self.project.designs,
            self.project.measurements,
            self.project.feed_line,
            self.project.matching_network,
        )


class SnapshotCommand(QUndoCommand):
    """Restore an editable project snapshot on undo/redo."""

    def __init__(
        self,
        restore: Callable[[ProjectSnapshot], None],
        before: ProjectSnapshot,
        after: ProjectSnapshot,
        text: str,
    ) -> None:
        super().__init__(text)
        self._restore = restore
        self._before = before
        self._after = after
        self._skip_first_redo = True

    def undo(self) -> None:
        self._restore(self._before)

    def redo(self) -> None:
        if self._skip_first_redo:
            self._skip_first_redo = False
            return
        self._restore(self._after)


def history_action(label_key: str):
    """Record a project change around a MainWindow method.

    Nested decorated actions share the outer transaction.
    """

    def decorator(method: Callable[..., Any]):
        @wraps(method)
        def wrapper(self, *args: object, **kwargs: object):
            if getattr(self, "_history_restoring", False) or getattr(self, "_history_depth", 0):
                return method(self, *args, **kwargs)
            before = self._history_snapshot()
            self._history_depth = 1
            try:
                result = method(self, *args, **kwargs)
            finally:
                self._history_depth = 0
            after = self._history_snapshot()
            self._record_history(label_key, before, after)
            return result

        return wrapper

    return decorator
