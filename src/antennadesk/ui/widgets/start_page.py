# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Empty-state page shown when no project is open."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ..i18n import Translator


class StartPage(QWidget):
    """Small start screen with the two project entry points."""

    new_requested = Signal()
    open_requested = Signal()

    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator

        self._title = QLabel(self)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setWordWrap(True)
        self._title.setStyleSheet("font-size: 22px; font-weight: 600;")

        self._description = QLabel(self)
        self._description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description.setWordWrap(True)

        self._new_button = QPushButton(self)
        self._new_button.setMinimumHeight(40)
        self._new_button.setMinimumWidth(220)
        self._new_button.clicked.connect(self.new_requested)

        self._open_button = QPushButton(self)
        self._open_button.setMinimumHeight(40)
        self._open_button.setMinimumWidth(220)
        self._open_button.clicked.connect(self.open_requested)

        self._flow = QLabel(self)
        self._flow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flow.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.addStretch(1)
        layout.addWidget(self._title)
        layout.addSpacing(8)
        layout.addWidget(self._description)
        layout.addSpacing(28)
        layout.addWidget(self._new_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._open_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(28)
        layout.addWidget(self._flow)
        layout.addStretch(2)

        self.retranslate()

    def retranslate(self) -> None:
        self._title.setText(self._translator.t("start.title"))
        self._description.setText(self._translator.t("start.description"))
        self._new_button.setText(self._translator.t("action.new"))
        self._open_button.setText(self._translator.t("action.open"))
        self._flow.setText(self._translator.t("start.flow"))
