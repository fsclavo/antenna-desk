# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Edit lossless transmission-line two-ports between wire points."""

from __future__ import annotations

from collections.abc import Mapping

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.transmission_line import TransmissionLine
from ...domain.antennas.wire import Wire
from ..fonts import scaled_dialog_size
from ..help import apply_row_help
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key


class TransmissionLinesDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        wires: Mapping[str, Wire],
        transmission_lines: tuple[TransmissionLine, ...],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._wires = dict(wires)
        self._transmission_lines = list(transmission_lines)
        self.setWindowTitle(translator.t("transmission_lines.title"))
        self.resize(*scaled_dialog_size(900, 560))

        self._table = QTableWidget(0, 7, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)

        self._start_wire = QComboBox(self)
        self._end_wire = QComboBox(self)
        for wire_id in sorted(self._wires):
            self._start_wire.addItem(wire_id, wire_id)
            self._end_wire.addItem(wire_id, wire_id)

        self._start_offset = QDoubleSpinBox(self)
        self._end_offset = QDoubleSpinBox(self)
        for spin in (self._start_offset, self._end_offset):
            spin.setDecimals(3)
            spin.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._z0 = QDoubleSpinBox(self)
        self._z0.setRange(0.1, 100_000.0)
        self._z0.setDecimals(1)
        self._z0.setSuffix(" Ω")
        self._z0.setValue(50.0)

        self._length = QDoubleSpinBox(self)
        self._length.setRange(0.001, 100_000.0)
        self._length.setDecimals(3)
        self._length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._length.setValue(1.0)

        self._velocity = QDoubleSpinBox(self)
        self._velocity.setRange(0.01, 1.0)
        self._velocity.setDecimals(3)
        self._velocity.setValue(1.0)

        self._use_distance = QPushButton(translator.t("transmission_lines.use_distance"), self)
        self._add = QPushButton(translator.t("transmission_lines.add"), self)
        self._remove = QPushButton(translator.t("transmission_lines.remove"), self)
        self._remove.setEnabled(False)

        self._start_wire.currentIndexChanged.connect(self._update_offset_ranges)
        self._end_wire.currentIndexChanged.connect(self._update_offset_ranges)
        self._use_distance.clicked.connect(self._set_straight_line_distance)
        self._add.clicked.connect(self._add_line)
        self._remove.clicked.connect(self._remove_line)
        self._table.itemSelectionChanged.connect(
            lambda: self._remove.setEnabled(bool(self._table.selectedItems()))
        )

        form = QFormLayout()
        form.addRow(translator.t("transmission_lines.start_wire"), self._start_wire)
        form.addRow(translator.t("transmission_lines.start_offset"), self._start_offset)
        form.addRow(translator.t("transmission_lines.end_wire"), self._end_wire)
        form.addRow(translator.t("transmission_lines.end_offset"), self._end_offset)
        form.addRow(translator.t("transmission_lines.z0"), self._z0)
        length_row = QHBoxLayout()
        length_row.addWidget(self._length)
        length_row.addWidget(self._use_distance)
        form.addRow(translator.t("transmission_lines.length"), length_row)
        form.addRow(translator.t("transmission_lines.velocity_factor"), self._velocity)
        for row, key in enumerate(
            (
                "transmission_lines.start_wire",
                "transmission_lines.start_offset",
                "transmission_lines.end_wire",
                "transmission_lines.end_offset",
                "transmission_lines.z0",
                "transmission_lines.length",
                "transmission_lines.velocity_factor",
            )
        ):
            apply_row_help(form, row, translator, key)

        hint = QLabel(translator.t("transmission_lines.hint"), self)
        hint.setWordWrap(True)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        add_remove = QHBoxLayout()
        add_remove.addWidget(self._add)
        add_remove.addWidget(self._remove)
        add_remove.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self._table, 1)
        layout.addLayout(form)
        layout.addLayout(add_remove)
        layout.addWidget(hint)
        layout.addWidget(buttons)

        self._table.setHorizontalHeaderLabels(
            [
                translator.t("transmission_lines.start_wire"),
                translator.t("transmission_lines.start_offset"),
                translator.t("transmission_lines.end_wire"),
                translator.t("transmission_lines.end_offset"),
                translator.t("transmission_lines.z0"),
                translator.t("transmission_lines.length"),
                translator.t("transmission_lines.velocity_factor"),
            ]
        )
        self._update_offset_ranges()
        self._refresh()

    def _selected_wire(self, combo: QComboBox) -> Wire | None:
        wire_id = combo.currentData()
        if not isinstance(wire_id, str):
            return None
        return self._wires.get(wire_id)

    def _update_offset_ranges(self) -> None:
        unit = self._translator.t(length_unit_key(self._unit_system))
        for combo, spin in (
            (self._start_wire, self._start_offset),
            (self._end_wire, self._end_offset),
        ):
            wire = self._selected_wire(combo)
            maximum = length_from_m(wire.length_m, self._unit_system) if wire else 0.0
            spin.setRange(0.0, maximum)
            spin.setSuffix(f" {unit}")

    def _set_straight_line_distance(self) -> None:
        start_wire = self._selected_wire(self._start_wire)
        end_wire = self._selected_wire(self._end_wire)
        if start_wire is None or end_wire is None:
            return
        start = start_wire.point_at(
            min(length_to_m(self._start_offset.value(), self._unit_system), start_wire.length_m)
        )
        end = end_wire.point_at(
            min(length_to_m(self._end_offset.value(), self._unit_system), end_wire.length_m)
        )
        distance = max(start.distance_to(end), 0.001)
        self._length.setValue(length_from_m(distance, self._unit_system))

    def _refresh(self) -> None:
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._table.setRowCount(len(self._transmission_lines))
        for row, line in enumerate(self._transmission_lines):
            values = [
                line.start_wire_id,
                f"{length_from_m(line.start_offset_m, self._unit_system):.3f} {unit}",
                line.end_wire_id,
                f"{length_from_m(line.end_offset_m, self._unit_system):.3f} {unit}",
                f"{line.characteristic_impedance_ohm:.1f}",
                f"{length_from_m(line.length_m, self._unit_system):.3f} {unit}",
                f"{line.velocity_factor:.3f}",
            ]
            for column, value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(value))
        self._table.resizeColumnsToContents()

    def _next_id(self) -> str:
        used = {line.id for line in self._transmission_lines}
        index = 1
        while f"line-{index}" in used:
            index += 1
        return f"line-{index}"

    def _add_line(self) -> None:
        start_wire = self._selected_wire(self._start_wire)
        end_wire = self._selected_wire(self._end_wire)
        if start_wire is None or end_wire is None:
            return
        start_offset = min(
            length_to_m(self._start_offset.value(), self._unit_system),
            start_wire.length_m,
        )
        end_offset = min(
            length_to_m(self._end_offset.value(), self._unit_system),
            end_wire.length_m,
        )
        try:
            line = TransmissionLine(
                id=self._next_id(),
                start_wire_id=start_wire.id,
                start_offset_m=start_offset,
                end_wire_id=end_wire.id,
                end_offset_m=end_offset,
                characteristic_impedance_ohm=self._z0.value(),
                length_m=length_to_m(self._length.value(), self._unit_system),
                velocity_factor=self._velocity.value(),
            )
        except ValueError as exc:
            QMessageBox.critical(
                self,
                self._translator.t("transmission_lines.title"),
                str(exc),
            )
            return
        self._transmission_lines.append(line)
        self._refresh()

    def _remove_line(self) -> None:
        rows = sorted({index.row() for index in self._table.selectedIndexes()}, reverse=True)
        for row in rows:
            del self._transmission_lines[row]
        self._refresh()

    def transmission_lines(self) -> tuple[TransmissionLine, ...]:
        return tuple(self._transmission_lines)
