# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measurement condition editor shown before import."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..i18n import Translator


class MeasurementDetailsDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        default_name: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self.setWindowTitle(translator.t("measurement.details_title"))
        self.resize(520, 360)

        self._name = QLineEdit(default_name, self)
        self._calibration = QLineEdit(self)
        self._reference_plane = QLineEdit(self)
        self._feed_line = QLineEdit(self)
        self._notes = QPlainTextEdit(self)
        self._notes.setPlaceholderText(translator.t("measurement.notes_hint"))

        form = QFormLayout()
        form.addRow(translator.t("measurement.name"), self._name)
        form.addRow(translator.t("measurement.calibration"), self._calibration)
        form.addRow(translator.t("measurement.reference_plane"), self._reference_plane)
        form.addRow(translator.t("measurement.feed_line"), self._feed_line)
        self._notes_label = QLabel(translator.t("measurement.notes"), self)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._notes_label)
        layout.addWidget(self._notes, 1)
        layout.addWidget(buttons)

    def name(self) -> str:
        return self._name.text().strip()

    def calibration(self) -> str:
        return self._calibration.text().strip()

    def reference_plane(self) -> str:
        return self._reference_plane.text().strip()

    def feed_line(self) -> str:
        return self._feed_line.text().strip()

    def notes(self) -> str:
        return self._notes.toPlainText().strip()
