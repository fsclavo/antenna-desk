# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reusable task-progress bar for long-running UI operations."""

from __future__ import annotations

from enum import StrEnum

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QWidget,
)

from ..i18n import Translator


class TaskProgressState(StrEnum):
    """Lifecycle of one background task."""

    IDLE = "idle"
    RUNNING = "running"
    CANCELLING = "cancelling"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class TaskProgressBar(QWidget):
    """A compact progress bar with a translated status label.

    The widget owns presentation only. Callers decide whether a task has a
    meaningful determinate unit or is indeterminate, and provide translated
    text keys or already-translated text.
    """

    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._state = TaskProgressState.IDLE
        self._text_key = "progress.working"
        self._text_args: dict[str, object] = {}
        self._plain_text: str | None = None
        self._elapsed_seconds: int | None = None

        self._label = QLabel(self)
        self._label.setMinimumWidth(120)
        self._label.setWordWrap(False)
        self._label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )

        self._bar = QProgressBar(self)
        self._bar.setRange(0, 1)
        self._bar.setValue(0)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(14)
        self._bar.setMinimumWidth(160)
        self._bar.setMaximumWidth(240)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self._label, 1)
        layout.addWidget(self._bar)

        self.setVisible(False)
        self.retranslate()

    @property
    def state(self) -> TaskProgressState:
        return self._state

    @property
    def text(self) -> str:
        return self._label.text()

    @property
    def progress_value(self) -> int:
        return self._bar.value()

    @property
    def progress_maximum(self) -> int:
        return self._bar.maximum()

    @property
    def elapsed_seconds(self) -> int | None:
        return self._elapsed_seconds

    @property
    def is_indeterminate(self) -> bool:
        return self._bar.minimum() == 0 and self._bar.maximum() == 0

    def begin_indeterminate(
        self,
        text_key: str = "progress.working",
        **text_args: object,
    ) -> None:
        """Start a task whose total work is unknown."""

        self._state = TaskProgressState.RUNNING
        self._elapsed_seconds = None
        self._bar.setRange(0, 0)
        self._set_text_key(text_key, text_args)
        self.show()

    def begin_determinate(
        self,
        maximum: int,
        text_key: str = "progress.working",
        **text_args: object,
    ) -> None:
        """Start a task with a known unit count."""

        self._state = TaskProgressState.RUNNING
        self._elapsed_seconds = None
        self._bar.setRange(0, max(1, int(maximum)))
        self._bar.setValue(0)
        self._set_text_key(text_key, text_args)
        self.show()

    def set_progress(
        self,
        value: int,
        text_key: str | None = None,
        **text_args: object,
    ) -> None:
        """Update the current unit count and, optionally, the label."""

        if text_key is not None:
            self._set_text_key(text_key, text_args)
        if not self.is_indeterminate:
            self._bar.setValue(min(max(int(value), 0), self._bar.maximum()))

    def set_text_key(self, text_key: str, **text_args: object) -> None:
        self._set_text_key(text_key, text_args)

    def set_text(self, text: str) -> None:
        """Set already-translated text, for callers with preformatted values."""

        self._plain_text = text
        self._refresh_text()

    def set_elapsed(self, seconds: int | None) -> None:
        self._elapsed_seconds = None if seconds is None else max(0, int(seconds))
        self._refresh_text()

    def mark_cancelling(
        self,
        text_key: str = "status.cancelling",
        **text_args: object,
    ) -> None:
        self._state = TaskProgressState.CANCELLING
        self._elapsed_seconds = None
        self._set_text_key(text_key, text_args)
        self.show()

    def complete(
        self,
        text_key: str = "progress.completed",
        **text_args: object,
    ) -> None:
        self._state = TaskProgressState.COMPLETED
        self._elapsed_seconds = None
        self._bar.setRange(0, 1)
        self._bar.setValue(1)
        self._set_text_key(text_key, text_args)
        self.show()

    def cancel(
        self,
        text_key: str = "progress.cancelled",
        **text_args: object,
    ) -> None:
        self._state = TaskProgressState.CANCELLED
        self._elapsed_seconds = None
        self._bar.setRange(0, 1)
        self._bar.setValue(0)
        self._set_text_key(text_key, text_args)
        self.show()

    def fail(
        self,
        text_key: str = "progress.failed",
        **text_args: object,
    ) -> None:
        self._state = TaskProgressState.ERROR
        self._elapsed_seconds = None
        self._bar.setRange(0, 1)
        self._bar.setValue(0)
        self._set_text_key(text_key, text_args)
        self.show()

    def reset(self) -> None:
        self._state = TaskProgressState.IDLE
        self._text_key = "progress.working"
        self._text_args = {}
        self._plain_text = None
        self._elapsed_seconds = None
        self._bar.setRange(0, 1)
        self._bar.setValue(0)
        self._label.clear()
        self._label.setToolTip("")
        self.hide()

    def retranslate(self) -> None:
        self._bar.setAccessibleName(self._translator.t("progress.accessible_name"))
        if self._state is not TaskProgressState.IDLE:
            self._refresh_text()

    def _set_text_key(self, text_key: str, text_args: dict[str, object]) -> None:
        self._text_key = text_key
        self._text_args = dict(text_args)
        self._plain_text = None
        self._refresh_text()

    def _refresh_text(self) -> None:
        if self._plain_text is not None:
            text = self._plain_text
        else:
            text = self._translator.t(self._text_key, **self._text_args)
        if self._elapsed_seconds is not None:
            text = self._translator.t(
                "progress.with_elapsed",
                text=text,
                seconds=self._elapsed_seconds,
            )
        self._label.setText(text)
        self._label.setToolTip(text)
        self._label.setWhatsThis(text)
        self._label.setAccessibleDescription(text)
        self._bar.setAccessibleDescription(text)
