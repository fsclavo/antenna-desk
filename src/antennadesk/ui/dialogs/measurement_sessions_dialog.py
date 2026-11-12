# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measurement session timeline and record manager."""

from __future__ import annotations

from dataclasses import replace
from uuid import UUID, uuid4

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.common.time import utc_now
from ...domain.measurement import Measurement, MeasurementSession
from ...domain.projects.project import Project
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from .measurement_comparison_dialog import MeasurementComparisonDialog
from .measurement_details_dialog import MeasurementDetailsDialog
from .measurement_session_dialog import MeasurementSessionDialog


class MeasurementSessionsDialog(QDialog):
    """Show sessions on a timeline and manage their measurements."""

    def __init__(
        self,
        translator: Translator,
        project: Project,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._measurements: tuple[Measurement, ...] = ()
        self._unassigned_item: QTreeWidgetItem | None = None
        self.setWindowTitle(translator.t("measurement.sessions_title"))
        self.resize(*scaled_dialog_size(980, 680))

        self._timeline_label = QLabel(translator.t("measurement.sessions_timeline"), self)
        self._timeline_label.setWordWrap(True)
        self._tree = QTreeWidget(self)
        self._tree.setColumnCount(5)
        self._tree.setRootIsDecorated(False)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for column in (0, 2, 3, 4):
            self._tree.header().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        self._tree.itemSelectionChanged.connect(self._selection_changed)
        apply_help(self._tree, translator, "measurement.sessions.timeline")

        self._details = QLabel(self)
        self._details.setWordWrap(True)
        self._details.setTextFormat(Qt.TextFormat.PlainText)
        apply_help(self._details, translator, "measurement.sessions.details")

        self._measurements_label = QLabel(translator.t("measurement.sessions_measurements"), self)
        self._measurements_table = QTableWidget(0, 5, self)
        self._measurements_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._measurements_table.setAlternatingRowColors(True)
        self._measurements_table.verticalHeader().setVisible(False)
        self._measurements_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        for column in (1, 2, 3, 4):
            self._measurements_table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        self._measurements_table.itemSelectionChanged.connect(self._update_buttons)
        apply_help(self._measurements_table, translator, "measurement.sessions.table")

        self._new = QPushButton(translator.t("measurement.session_new"), self)
        self._edit = QPushButton(translator.t("measurement.session_edit"), self)
        self._delete = QPushButton(translator.t("measurement.session_delete"), self)
        self._edit_measurement = QPushButton(
            translator.t("measurement.sessions_edit_measurement"),
            self,
        )
        self._compare = QPushButton(translator.t("measurement.sessions_compare"), self)
        self._new.clicked.connect(self._new_session)
        self._edit.clicked.connect(self._edit_session)
        self._delete.clicked.connect(self._delete_session)
        self._edit_measurement.clicked.connect(self._edit_selected_measurement)
        self._compare.clicked.connect(self._compare_measurements)
        for button, key in (
            (self._new, "measurement.sessions.new"),
            (self._edit, "measurement.sessions.edit"),
            (self._delete, "measurement.sessions.delete"),
            (self._edit_measurement, "measurement.sessions.edit_measurement"),
            (self._compare, "measurement.sessions.compare"),
        ):
            apply_help(button, translator, key)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(translator.t("action.ok"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(
            translator.t("action.cancel")
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        session_buttons = QHBoxLayout()
        session_buttons.addWidget(self._new)
        session_buttons.addWidget(self._edit)
        session_buttons.addWidget(self._delete)
        session_buttons.addStretch(1)
        session_buttons.addWidget(self._edit_measurement)
        session_buttons.addWidget(self._compare)

        layout = QVBoxLayout(self)
        layout.addWidget(self._timeline_label)
        layout.addWidget(self._tree, 2)
        layout.addWidget(self._details)
        layout.addWidget(self._measurements_label)
        layout.addWidget(self._measurements_table, 2)
        layout.addLayout(session_buttons)
        layout.addWidget(buttons)

        self.retranslate()
        self._reload()

    def result_project(self) -> Project:
        return self._project

    def _selected_session(self) -> MeasurementSession | None:
        item = self._tree.currentItem()
        if item is None or item is self._unassigned_item:
            return None
        value = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(value, UUID):
            return None
        return next(
            (session for session in self._project.measurement_sessions if session.id == value),
            None,
        )

    def _selected_measurement(self) -> Measurement | None:
        row = self._measurements_table.currentRow()
        if row < 0 or row >= len(self._measurements):
            return None
        return self._measurements[row]

    def _session_design_name(self, session: MeasurementSession) -> str:
        if session.design_id is None:
            return self._translator.t("measurement.session_no_design")
        try:
            return self._project.design_by_id(session.design_id).name
        except KeyError:
            return "—"

    def _reload(self, *, select_session_id: UUID | str | None = None) -> None:
        previous = self._tree.currentItem()
        previous_data = previous.data(0, Qt.ItemDataRole.UserRole) if previous is not None else None
        self._tree.clear()
        self._unassigned_item = None
        sessions = sorted(
            self._project.measurement_sessions,
            key=lambda session: session.created_at,
            reverse=True,
        )
        for session in sessions:
            measurements = self._project.measurements_for_session(session.id)
            item = QTreeWidgetItem(
                [
                    f"{session.created_at:%Y-%m-%d %H:%M}",
                    session.name,
                    self._session_design_name(session),
                    str(len(measurements)),
                    session.location or "—",
                ]
            )
            item.setData(0, Qt.ItemDataRole.UserRole, session.id)
            self._tree.addTopLevelItem(item)
        unassigned = self._project.unassigned_measurements()
        if unassigned:
            item = QTreeWidgetItem(
                [
                    "—",
                    self._translator.t("measurement.sessions_unassigned"),
                    "—",
                    str(len(unassigned)),
                    "—",
                ]
            )
            item.setData(0, Qt.ItemDataRole.UserRole, "unassigned")
            self._unassigned_item = item
            self._tree.addTopLevelItem(item)

        target = select_session_id if select_session_id is not None else previous_data
        for index in range(self._tree.topLevelItemCount()):
            candidate = self._tree.topLevelItem(index)
            if candidate is None:
                continue
            data = candidate.data(0, Qt.ItemDataRole.UserRole)
            if target == data:
                self._tree.setCurrentItem(candidate)
                break
        else:
            first = self._tree.topLevelItem(0)
            if first is not None:
                self._tree.setCurrentItem(first)
        self._selection_changed()

    def _selection_changed(self) -> None:
        session = self._selected_session()
        item = self._tree.currentItem()
        if item is self._unassigned_item:
            self._measurements = self._project.unassigned_measurements()
            self._details.setText(self._translator.t("measurement.sessions_unassigned_hint"))
        elif session is not None:
            self._measurements = self._project.measurements_for_session(session.id)
            details = [
                f"{session.created_at:%Y-%m-%d %H:%M}",
                self._session_design_name(session),
            ]
            if session.location:
                details.append(session.location)
            if session.conditions:
                details.append(session.conditions)
            if session.notes:
                details.append(session.notes)
            self._details.setText(" · ".join(details))
        else:
            self._measurements = ()
            self._details.clear()
        self._measurements = tuple(sorted(self._measurements, key=lambda item: item.created_at))
        self._measurements_table.setRowCount(len(self._measurements))
        for row, measurement in enumerate(self._measurements):
            values = (
                measurement.name,
                f"{measurement.created_at:%Y-%m-%d %H:%M}",
                str(len(measurement.points)),
                f"{measurement.reference_impedance_ohm:g} Ω",
                measurement.source or "—",
            )
            for column, value in enumerate(values):
                self._measurements_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(value),
                )
        self._update_buttons()

    def _update_buttons(self) -> None:
        session = self._selected_session()
        self._edit.setEnabled(session is not None)
        self._delete.setEnabled(session is not None)
        self._edit_measurement.setEnabled(self._selected_measurement() is not None)
        self._compare.setEnabled(len(self._project.measurements) >= 2)

    def _new_session(self) -> None:
        dialog = MeasurementSessionDialog(self._translator, self._project, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            session = MeasurementSession(
                id=uuid4(),
                name=dialog.name(),
                created_at=dialog.created_at(),
                design_id=dialog.design_id(),
                location=dialog.location(),
                conditions=dialog.conditions(),
                notes=dialog.notes(),
            )
            self._project = self._project.with_measurement_session(
                session,
                updated_at=utc_now(),
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._translator.t("measurement.sessions_title"),
                str(exc),
            )
            return
        self._reload(select_session_id=session.id)

    def _edit_session(self) -> None:
        session = self._selected_session()
        if session is None:
            return
        dialog = MeasurementSessionDialog(
            self._translator,
            self._project,
            self,
            session=session,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            updated = replace(
                session,
                name=dialog.name() or session.name,
                created_at=dialog.created_at(),
                design_id=dialog.design_id(),
                location=dialog.location(),
                conditions=dialog.conditions(),
                notes=dialog.notes(),
            )
            self._project = self._project.with_updated_measurement_session(
                updated,
                updated_at=utc_now(),
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._translator.t("measurement.sessions_title"),
                str(exc),
            )
            return
        self._reload(select_session_id=session.id)

    def _delete_session(self) -> None:
        session = self._selected_session()
        if session is None:
            return
        answer = QMessageBox.question(
            self,
            self._translator.t("measurement.session_delete_title"),
            self._translator.t(
                "measurement.session_delete_confirm",
                name=session.name,
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self._project = self._project.without_measurement_session(
                session.id,
                updated_at=utc_now(),
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._translator.t("measurement.sessions_title"),
                str(exc),
            )
            return
        self._reload(select_session_id="unassigned")

    def _edit_selected_measurement(self) -> None:
        measurement = self._selected_measurement()
        if measurement is None:
            return
        dialog = MeasurementDetailsDialog(
            self._translator,
            measurement.name,
            self,
            measurement=measurement,
            sessions=self._project.measurement_sessions,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            updated = replace(
                measurement,
                name=dialog.name() or measurement.name,
                calibration=dialog.calibration(),
                reference_plane=dialog.reference_plane(),
                feed_line=dialog.feed_line(),
                notes=dialog.notes(),
                session_id=dialog.session_id(),
            )
            self._project = self._project.with_updated_measurement(
                updated,
                updated_at=utc_now(),
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._translator.t("measurement.sessions_title"),
                str(exc),
            )
            return
        self._reload()

    def _compare_measurements(self) -> None:
        if len(self._project.measurements) < 2:
            return
        measurements = tuple(sorted(self._project.measurements, key=lambda item: item.created_at))
        before_id = measurements[0].id
        after_id = measurements[-1].id
        selected = self._selected_measurement()
        if selected is not None:
            index = measurements.index(selected)
            if index == 0:
                before_id = measurements[0].id
                after_id = measurements[1].id
            else:
                before_id = measurements[index - 1].id
                after_id = selected.id
        dialog = MeasurementComparisonDialog(
            self._translator,
            measurements,
            self,
            session_names={
                session.id: session.name for session in self._project.measurement_sessions
            },
            initial_before_id=before_id,
            initial_after_id=after_id,
        )
        dialog.exec()

    def retranslate(self) -> None:
        t = self._translator.t
        self.setWindowTitle(t("measurement.sessions_title"))
        self._timeline_label.setText(t("measurement.sessions_timeline"))
        self._measurements_label.setText(t("measurement.sessions_measurements"))
        self._tree.setHeaderLabels(
            [
                t("measurement.session_date"),
                t("measurement.session_name"),
                t("measurement.session_design"),
                t("measurement.sessions_count"),
                t("measurement.session_location"),
            ]
        )
        self._measurements_table.setHorizontalHeaderLabels(
            [
                t("measurement.name"),
                t("measurement.session_date"),
                t("measurement.points"),
                t("measurement.reference"),
                t("measurement.source"),
            ]
        )
        self._new.setText(t("measurement.session_new"))
        self._edit.setText(t("measurement.session_edit"))
        self._delete.setText(t("measurement.session_delete"))
        self._edit_measurement.setText(t("measurement.sessions_edit_measurement"))
        self._compare.setText(t("measurement.sessions_compare"))
        apply_help(self._tree, self._translator, "measurement.sessions.timeline")
        apply_help(self._details, self._translator, "measurement.sessions.details")
        apply_help(self._measurements_table, self._translator, "measurement.sessions.table")
