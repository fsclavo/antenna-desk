# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measurement session editor."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from PySide6.QtCore import QDateTime, QTimeZone
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...domain.measurement import MeasurementSession
from ...domain.projects.project import Project
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator


class MeasurementSessionDialog(QDialog):
    """Create or edit the conditions of one measurement session."""

    def __init__(
        self,
        translator: Translator,
        project: Project,
        parent: QWidget | None = None,
        *,
        session: MeasurementSession | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self.setWindowTitle(translator.t("measurement.session_title"))
        self.resize(*scaled_dialog_size(560, 520))

        self._name = QLineEdit(self)
        self._date = QDateTimeEdit(self)
        self._date.setCalendarPopup(True)
        self._date.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._date.setDateTime(
            QDateTime.fromSecsSinceEpoch(
                int((session.created_at if session else datetime.now(UTC)).timestamp()),
                QTimeZone.utc(),
            )
        )
        self._design = QComboBox(self)
        self._design.addItem(translator.t("measurement.session_no_design"), None)
        for design in project.designs:
            self._design.addItem(design.name, design.id)
        self._location = QLineEdit(self)
        self._conditions = QPlainTextEdit(self)
        self._conditions.setFixedHeight(70)
        self._notes = QPlainTextEdit(self)

        if session is not None:
            self._name.setText(session.name)
            self._location.setText(session.location)
            self._conditions.setPlainText(session.conditions)
            self._notes.setPlainText(session.notes)
            if session.design_id is not None:
                index = self._design.findData(session.design_id)
                if index >= 0:
                    self._design.setCurrentIndex(index)

        form = QFormLayout()
        form.addRow(translator.t("measurement.session_name"), self._name)
        form.addRow(translator.t("measurement.session_date"), self._date)
        form.addRow(translator.t("measurement.session_design"), self._design)
        form.addRow(translator.t("measurement.session_location"), self._location)
        for row, key in enumerate(
            (
                "measurement.session.name",
                "measurement.session.date",
                "measurement.session.design",
                "measurement.session.location",
            )
        ):
            apply_row_help(form, row, translator, key)
        self._conditions_label = QLabel(translator.t("measurement.session_conditions"), self)
        self._notes_label = QLabel(translator.t("measurement.session_notes"), self)
        apply_help(self._conditions, translator, "measurement.session.conditions")
        apply_help(self._conditions_label, translator, "measurement.session.conditions")
        apply_help(self._notes, translator, "measurement.session.notes")
        apply_help(self._notes_label, translator, "measurement.session.notes")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._conditions_label)
        layout.addWidget(self._conditions)
        layout.addWidget(self._notes_label)
        layout.addWidget(self._notes, 1)
        layout.addWidget(buttons)

    def accept(self) -> None:
        if not self.name():
            QMessageBox.warning(
                self,
                self.windowTitle(),
                self._translator.t("measurement.session_name_required"),
            )
            return
        super().accept()

    def name(self) -> str:
        return self._name.text().strip()

    def created_at(self) -> datetime:
        return datetime.fromtimestamp(self._date.dateTime().toSecsSinceEpoch(), UTC)

    def design_id(self) -> UUID | None:
        value = self._design.currentData()
        return value if isinstance(value, UUID) else None

    def location(self) -> str:
        return self._location.text().strip()

    def conditions(self) -> str:
        return self._conditions.toPlainText().strip()

    def notes(self) -> str:
        return self._notes.toPlainText().strip()
