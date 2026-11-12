# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measurement condition editor shown before import."""

from __future__ import annotations

from uuid import UUID

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...domain.measurement import Measurement, MeasurementSession
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator


class MeasurementDetailsDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        default_name: str,
        parent: QWidget | None = None,
        *,
        measurement: Measurement | None = None,
        sessions: tuple[MeasurementSession, ...] = (),
        session_id: UUID | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self.setWindowTitle(translator.t("measurement.details_title"))
        self.resize(*scaled_dialog_size(540, 430))

        self._name = QLineEdit(default_name, self)
        self._calibration = QLineEdit(self)
        self._reference_plane = QLineEdit(self)
        self._feed_line = QLineEdit(self)
        self._session = QComboBox(self)
        self._session.addItem(translator.t("measurement.session_unassigned"), None)
        for session in sorted(sessions, key=lambda item: item.created_at, reverse=True):
            self._session.addItem(
                f"{session.name} · {session.created_at:%Y-%m-%d %H:%M}",
                session.id,
            )
        self._notes = QPlainTextEdit(self)
        self._notes.setPlaceholderText(translator.t("measurement.notes_hint"))

        if measurement is not None:
            self._name.setText(measurement.name)
            self._calibration.setText(measurement.calibration)
            self._reference_plane.setText(measurement.reference_plane)
            self._feed_line.setText(measurement.feed_line)
            self._notes.setPlainText(measurement.notes)
            target_session = session_id or measurement.session_id
            if target_session is not None:
                index = self._session.findData(target_session)
                if index >= 0:
                    self._session.setCurrentIndex(index)
        elif session_id is not None:
            index = self._session.findData(session_id)
            if index >= 0:
                self._session.setCurrentIndex(index)

        form = QFormLayout()
        form.addRow(translator.t("measurement.name"), self._name)
        form.addRow(translator.t("measurement.session"), self._session)
        form.addRow(translator.t("measurement.calibration"), self._calibration)
        form.addRow(translator.t("measurement.reference_plane"), self._reference_plane)
        form.addRow(translator.t("measurement.feed_line"), self._feed_line)
        self._notes_label = QLabel(translator.t("measurement.notes"), self)
        for row, key in enumerate(
            (
                "measurement.name",
                "measurement.session",
                "measurement.calibration",
                "measurement.reference_plane",
                "measurement.feed_line",
            )
        ):
            apply_row_help(form, row, translator, key)
        apply_help(self._notes_label, translator, "measurement.notes")
        apply_help(self._notes, translator, "measurement.notes")

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

    def session_id(self) -> UUID | None:
        value = self._session.currentData()
        return value if isinstance(value, UUID) else None

    def calibration(self) -> str:
        return self._calibration.text().strip()

    def reference_plane(self) -> str:
        return self._reference_plane.text().strip()

    def feed_line(self) -> str:
        return self._feed_line.text().strip()

    def notes(self) -> str:
        return self._notes.toPlainText().strip()
