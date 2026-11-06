# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Edit series RLC loads on antenna wires."""

from __future__ import annotations

import math
from collections.abc import Mapping

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.load import LoadKind, LumpedLoad, ParallelLoad, SeriesLoad
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key


class LoadsDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        wire_lengths_m: Mapping[str, float],
        loads: tuple[LumpedLoad, ...],
        parent: QWidget | None = None,
        *,
        protected_load_ids: frozenset[str] = frozenset(),
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._wire_lengths_m = dict(wire_lengths_m)
        self._loads = list(loads)
        self._protected_load_ids = protected_load_ids
        self.setWindowTitle(translator.t("loads.title"))
        self.resize(*scaled_dialog_size(720, 480))

        self._table = QTableWidget(0, 6, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)

        self._kind = QComboBox(self)
        self._kind.addItem("", LoadKind.SERIES.value)
        self._kind.addItem("", LoadKind.PARALLEL.value)

        self._wire = QComboBox(self)
        for wire_id in sorted(self._wire_lengths_m):
            self._wire.addItem(wire_id, wire_id)
        self._wire.currentIndexChanged.connect(self._update_offset_range)
        self._offset = QDoubleSpinBox(self)
        self._offset.setDecimals(3)
        self._offset.setRange(0.0, 1.0)
        self._resistance = QDoubleSpinBox(self)
        self._resistance.setRange(0.0, 1_000_000.0)
        self._resistance.setDecimals(3)
        self._resistance.setSuffix(" Ω")
        self._inductance = QDoubleSpinBox(self)
        self._inductance.setRange(0.0, 1_000_000.0)
        self._inductance.setDecimals(3)
        self._inductance.setSuffix(" µH")
        self._capacitance = QDoubleSpinBox(self)
        self._capacitance.setRange(0.0, 1_000_000.0)
        self._capacitance.setDecimals(3)
        self._capacitance.setSuffix(" pF")

        self._trap_frequency = QDoubleSpinBox(self)
        self._trap_frequency.setRange(0.1, 100_000.0)
        self._trap_frequency.setDecimals(6)
        self._trap_frequency.setSuffix(" MHz")
        self._trap_frequency.setValue(14.1)

        self._add = QPushButton(translator.t("loads.add"), self)
        self._add_trap = QPushButton(translator.t("loads.add_trap"), self)
        self._remove = QPushButton(translator.t("loads.remove"), self)
        self._add.clicked.connect(self._add_load)
        self._add_trap.clicked.connect(self._add_trap_load)
        self._remove.clicked.connect(self._remove_load)
        self._remove.setEnabled(False)
        self._table.itemSelectionChanged.connect(
            lambda: self._remove.setEnabled(bool(self._table.selectedItems()))
        )

        form = QFormLayout()
        form.addRow(translator.t("loads.kind"), self._kind)
        form.addRow(translator.t("loads.wire"), self._wire)
        form.addRow(translator.t("loads.offset"), self._offset)
        form.addRow(translator.t("loads.resistance"), self._resistance)
        form.addRow(translator.t("loads.inductance"), self._inductance)
        form.addRow(translator.t("loads.capacitance"), self._capacitance)
        form.addRow(translator.t("loads.trap_frequency"), self._trap_frequency)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        add_remove = QHBoxLayout()
        add_remove.addWidget(self._add)
        add_remove.addWidget(self._add_trap)
        add_remove.addWidget(self._remove)
        add_remove.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self._table, 1)
        layout.addLayout(form)
        layout.addLayout(add_remove)
        layout.addWidget(buttons)

        self._table.setHorizontalHeaderLabels(
            [
                translator.t("loads.kind"),
                translator.t("loads.wire"),
                translator.t("loads.offset"),
                translator.t("loads.resistance"),
                translator.t("loads.inductance"),
                translator.t("loads.capacitance"),
            ]
        )
        self._offset.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._update_offset_range()
        self._refresh()

    def _update_offset_range(self) -> None:
        wire_id = self._wire.currentData()
        if not isinstance(wire_id, str):
            return
        length_m = self._wire_lengths_m.get(wire_id, 0.0)
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._offset.setRange(0.0, length_from_m(length_m, self._unit_system))
        self._offset.setSuffix(f" {unit}")

    def _refresh(self) -> None:
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._table.setRowCount(len(self._loads))
        for row, load in enumerate(self._loads):
            values = [
                (
                    self._translator.t("loads.parallel")
                    if isinstance(load, ParallelLoad)
                    else self._translator.t("loads.series")
                ),
                load.wire_id,
                f"{length_from_m(load.offset_m, self._unit_system):.3f} {unit}",
                f"{load.resistance_ohm:.3f}",
                f"{load.inductance_h * 1e6:.3f}",
                f"{load.capacitance_f * 1e12:.3f}",
            ]
            for column, value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(value))
        self._table.resizeColumnsToContents()

    def _add_load(self) -> None:
        wire_id = self._wire.currentData()
        if not isinstance(wire_id, str):
            return
        load_class = (
            ParallelLoad if self._kind.currentData() == LoadKind.PARALLEL.value else SeriesLoad
        )
        try:
            load = load_class(
                id=self._next_id(),
                wire_id=wire_id,
                offset_m=length_to_m(self._offset.value(), self._unit_system),
                resistance_ohm=self._resistance.value(),
                inductance_h=self._inductance.value() * 1e-6,
                capacitance_f=self._capacitance.value() * 1e-12,
            )
        except ValueError as exc:
            QMessageBox.critical(self, self._translator.t("loads.title"), str(exc))
            return
        self._loads.append(load)
        self._refresh()

    def _add_trap_load(self) -> None:
        wire_id = self._wire.currentData()
        if not isinstance(wire_id, str):
            return
        inductance_h = self._inductance.value() * 1e-6
        if inductance_h <= 0.0:
            QMessageBox.critical(
                self,
                self._translator.t("loads.title"),
                self._translator.t("loads.trap_requires_l"),
            )
            return
        frequency_hz = self._trap_frequency.value() * 1_000_000.0
        capacitance_f = 1.0 / ((2.0 * math.pi * frequency_hz) ** 2 * inductance_h)
        try:
            load = ParallelLoad(
                id=self._next_id(),
                wire_id=wire_id,
                offset_m=length_to_m(self._offset.value(), self._unit_system),
                resistance_ohm=self._resistance.value(),
                inductance_h=inductance_h,
                capacitance_f=capacitance_f,
            )
        except ValueError as exc:
            QMessageBox.critical(self, self._translator.t("loads.title"), str(exc))
            return
        self._loads.append(load)
        self._refresh()

    def _remove_load(self) -> None:
        rows = sorted({index.row() for index in self._table.selectedIndexes()}, reverse=True)
        if any(self._loads[row].id in self._protected_load_ids for row in rows):
            QMessageBox.information(
                self,
                self._translator.t("loads.title"),
                self._translator.t("loads.protected_message"),
            )
            return
        for row in rows:
            if 0 <= row < len(self._loads):
                del self._loads[row]
        self._refresh()

    def _next_id(self) -> str:
        used = {load.id for load in self._loads}
        index = 1
        while f"load-{index}" in used:
            index += 1
        return f"load-{index}"

    def loads(self) -> tuple[LumpedLoad, ...]:
        return tuple(self._loads)
