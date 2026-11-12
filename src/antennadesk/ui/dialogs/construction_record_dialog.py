# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""As-built dimensions, notes, and construction checklist editor."""

from __future__ import annotations

import contextlib
from uuid import UUID, uuid4

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.projects.construction import (
    CONSTRUCTION_CHECKLIST_KEYS,
    AsBuiltDimension,
    ConstructionChecklistItem,
    ConstructionRecord,
)
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key


class ConstructionRecordDialog(QDialog):
    """Edit the as-built record and checklist for the current project."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        record: ConstructionRecord | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._initial = record
        self.setWindowTitle(translator.t("construction_record.title"))
        self.resize(*scaled_dialog_size(760, 620))

        t = translator.t
        self._notes_label = QLabel(t("construction_record.notes"), self)
        self._notes = QPlainTextEdit(self)
        self._notes.setPlaceholderText(t("construction_record.notes_placeholder"))
        self._notes.setPlainText(record.as_built_notes if record is not None else "")
        apply_help(self._notes, translator, "construction_record.notes")

        self._dimensions_label = QLabel(t("construction_record.dimensions"), self)
        self._table = QTableWidget(0, 4, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setStretchLastSection(True)
        apply_help(self._table, translator, "construction_record.dimensions")

        self._add = QPushButton(t("construction_record.add"), self)
        self._add.clicked.connect(self._add_dimension)
        self._remove = QPushButton(t("construction_record.remove"), self)
        self._remove.clicked.connect(self._remove_dimension)
        apply_help(self._add, translator, "construction_record.add")
        apply_help(self._remove, translator, "construction_record.remove")
        dimension_buttons = QHBoxLayout()
        dimension_buttons.addWidget(self._add)
        dimension_buttons.addWidget(self._remove)
        dimension_buttons.addStretch(1)

        self._checklist_label = QLabel(t("construction_record.checklist"), self)
        self._checklist = QListWidget(self)
        for key in CONSTRUCTION_CHECKLIST_KEYS:
            item = QListWidgetItem(t(f"construction_record.checklist.{key}"))
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self._checklist.addItem(item)
        apply_help(self._checklist, translator, "construction_record.checklist")
        checked = record.checked_keys() if record is not None else frozenset()
        for row in range(self._checklist.count()):
            item = self._checklist.item(row)
            if item.data(Qt.ItemDataRole.UserRole) in checked:
                item.setCheckState(Qt.CheckState.Checked)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(t("action.ok"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(t("action.cancel"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._notes_label)
        layout.addWidget(self._notes)
        layout.addWidget(self._dimensions_label)
        layout.addWidget(self._table)
        layout.addLayout(dimension_buttons)
        layout.addWidget(self._checklist_label)
        layout.addWidget(self._checklist)
        layout.addWidget(buttons)
        self._load_dimensions()
        self.retranslate()

    def retranslate(self) -> None:
        t = self._translator.t
        unit = t(length_unit_key(self._unit_system))
        self._table.setHorizontalHeaderLabels(
            [
                t("construction_record.label"),
                t("construction_record.design_value", unit=unit),
                t("construction_record.actual_value", unit=unit),
                t("construction_record.notes_column"),
            ]
        )
        self._notes_label.setText(t("construction_record.notes"))
        self._dimensions_label.setText(t("construction_record.dimensions"))
        self._checklist_label.setText(t("construction_record.checklist"))
        self._add.setText(t("construction_record.add"))
        self._remove.setText(t("construction_record.remove"))
        for row in range(self._checklist.count()):
            item = self._checklist.item(row)
            key = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(key, str):
                item.setText(t(f"construction_record.checklist.{key}"))

    def _load_dimensions(self) -> None:
        record = self._initial
        if record is None:
            return
        for dimension in record.dimensions:
            self._append_dimension(dimension)

    def _append_dimension(self, dimension: AsBuiltDimension | None = None) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        values = (
            "",
            "",
            "",
            "",
        )
        if dimension is not None:
            values = (
                dimension.label,
                (
                    f"{length_from_m(dimension.design_value_m, self._unit_system):.3f}"
                    if dimension.design_value_m is not None
                    else ""
                ),
                (
                    f"{length_from_m(dimension.actual_value_m, self._unit_system):.3f}"
                    if dimension.actual_value_m is not None
                    else ""
                ),
                dimension.notes,
            )
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column == 0 and dimension is not None:
                item.setData(Qt.ItemDataRole.UserRole, str(dimension.id))
            self._table.setItem(row, column, item)

    def _add_dimension(self) -> None:
        self._append_dimension()
        self._table.setCurrentCell(self._table.rowCount() - 1, 0)

    def _remove_dimension(self) -> None:
        row = self._table.currentRow()
        if row >= 0:
            self._table.removeRow(row)

    def _dimension_value(self, row: int, column: int) -> float | None:
        item = self._table.item(row, column)
        if item is None or not item.text().strip():
            return None
        try:
            return length_to_m(float(item.text()), self._unit_system)
        except ValueError as exc:
            raise ValueError(
                self._translator.t(
                    "construction_record.invalid_value",
                    row=row + 1,
                    column=column,
                )
            ) from exc

    def record(self) -> ConstructionRecord | None:
        dimensions: list[AsBuiltDimension] = []
        for row in range(self._table.rowCount()):
            label_item = self._table.item(row, 0)
            label = label_item.text().strip() if label_item is not None else ""
            if not label:
                continue
            id_value = label_item.data(Qt.ItemDataRole.UserRole) if label_item else None
            dimension_id = uuid4()
            if isinstance(id_value, str):
                with contextlib.suppress(ValueError):
                    dimension_id = UUID(id_value)
            notes_item = self._table.item(row, 3)
            dimensions.append(
                AsBuiltDimension(
                    id=dimension_id,
                    label=label,
                    design_value_m=self._dimension_value(row, 1),
                    actual_value_m=self._dimension_value(row, 2),
                    notes=notes_item.text() if notes_item is not None else "",
                )
            )
        checklist = []
        for row in range(self._checklist.count()):
            item = self._checklist.item(row)
            key = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(key, str):
                checklist.append(
                    ConstructionChecklistItem(
                        key=key,
                        checked=item.checkState() is Qt.CheckState.Checked,
                    )
                )
        record = ConstructionRecord(
            as_built_notes=self._notes.toPlainText(),
            dimensions=tuple(dimensions),
            checklist=tuple(checklist),
        )
        if not record.as_built_notes and not record.dimensions and not record.checked_keys():
            return None
        return record

    def accept(self) -> None:
        try:
            self.record()
        except ValueError as exc:
            QMessageBox.critical(
                self,
                self._translator.t("construction_record.title"),
                str(exc),
            )
            return
        super().accept()
