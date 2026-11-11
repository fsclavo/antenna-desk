# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compact next-step panel for the progressive workflow."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..help import apply_help
from ..i18n import Translator
from ..workflow import NextStep


class NextStepPanel(QFrame):
    """Show one deterministic recommendation and its primary action."""

    action_requested = Signal(object)
    advanced_requested = Signal()

    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._step: NextStep | None = None
        self._guided = False

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setObjectName("workflowPanel")

        self._title = QLabel(self)
        self._title.setStyleSheet("font-weight: bold;")
        self._body = QLabel(self)
        self._body.setWordWrap(True)

        self._action = QPushButton(self)
        self._action.clicked.connect(self._emit_action)
        self._advanced = QPushButton(self)
        self._advanced.clicked.connect(self.advanced_requested)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.addWidget(self._action)
        actions.addWidget(self._advanced)
        actions.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        layout.addWidget(self._title)
        layout.addWidget(self._body)
        layout.addLayout(actions)

        self.retranslate()

    @property
    def step(self) -> NextStep | None:
        """The currently displayed recommendation, for tests and diagnostics."""

        return self._step

    def set_step(self, step: NextStep | None) -> None:
        self._step = step
        self.retranslate()

    def set_guided(self, guided: bool) -> None:
        self._guided = guided
        self.retranslate()

    def _emit_action(self) -> None:
        if self._step is not None:
            self.action_requested.emit(self._step.kind)

    def retranslate(self) -> None:
        t = self._translator.t
        self._title.setText(t("workflow.panel_title"))
        self._body.setText(t(self._step.body_key) if self._step is not None else "")
        action_key = self._step.action_key if self._step is not None else None
        self._action.setText(t(action_key) if action_key else "")
        self._action.setVisible(bool(action_key))
        self._advanced.setText(t("workflow.show_advanced"))
        self._advanced.setVisible(self._guided)
        self._body.setAccessibleName(t("workflow.panel_title"))
        apply_help(self, self._translator, "section.workflow")
        apply_help(self._action, self._translator, "action.next_step")
        apply_help(self._advanced, self._translator, "action.show_advanced")
