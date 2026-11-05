# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Empty-state page shown when no project is open."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from ..fonts import scaled_pixel_font
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
        self._apply_title_font()

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

        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.fontChanged.connect(self._on_application_font_changed)

        self.retranslate()

    def _apply_title_font(self) -> None:
        self._title.setFont(
            scaled_pixel_font(
                22,
                QFont.Weight.DemiBold,
                self.font().family(),
            )
        )

    def _on_application_font_changed(self, font: QFont) -> None:
        del font
        self._apply_title_font()

    def retranslate(self) -> None:
        self._title.setText(self._translator.t("start.title"))
        self._description.setText(self._translator.t("start.description"))
        self._new_button.setText(self._translator.t("action.new"))
        self._open_button.setText(self._translator.t("action.open"))
        self._flow.setText(self._translator.t("start.flow"))
