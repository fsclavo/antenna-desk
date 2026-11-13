# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Manual BOM unit costs and totals."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.projects.bom_costs import (
    MAX_BOM_CURRENCY_LENGTH,
    BomCostLine,
    BomCostRecord,
)
from ...domain.projects.project import DesignVariant, Project
from ...reporting.bom_costs import (
    BomCostEntry,
    bom_cost_entries,
    format_cost,
)
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator


class BomCostsDialog(QDialog):
    """Edit manual unit costs for the current design's BOM rows."""

    def __init__(
        self,
        translator: Translator,
        project: Project,
        design: DesignVariant,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._design = design
        self._existing = project.bom_costs
        self._record: BomCostRecord | None = self._existing
        self._entries = bom_cost_entries(project, design, translator.report)
        self._cost_spins: list[tuple[BomCostEntry, QDoubleSpinBox, QTableWidgetItem]] = []
        self.setWindowTitle(translator.t("bom_costs.title"))
        self.resize(*scaled_dialog_size(860, 560))

        self._currency = QLineEdit(self)
        self._currency.setMaxLength(MAX_BOM_CURRENCY_LENGTH)
        self._currency.setText(self._existing.currency if self._existing is not None else "")
        self._currency_label = QLabel(translator.t("bom_costs.currency"), self)
        currency_form = QFormLayout()
        currency_form.addRow(self._currency_label, self._currency)
        apply_row_help(currency_form, 0, translator, "bom_costs.currency")

        self._table = QTableWidget(0, 5, self)
        self._table.setHorizontalHeaderLabels(
            (
                translator.t("bom_costs.item"),
                translator.t("bom_costs.quantity"),
                translator.t("bom_costs.unit"),
                translator.t("bom_costs.unit_cost"),
                translator.t("bom_costs.line_total"),
            )
        )
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        apply_help(self._table, translator, "bom_costs.table")

        for entry in self._entries:
            row = self._table.rowCount()
            self._table.insertRow(row)
            label = QTableWidgetItem(entry.label)
            label.setToolTip(entry.note)
            quantity = QTableWidgetItem(f"{entry.quantity:g}")
            quantity.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            unit = QTableWidgetItem(entry.unit)
            unit_cost = QDoubleSpinBox(self._table)
            unit_cost.setRange(0.0, 1_000_000_000.0)
            unit_cost.setDecimals(2)
            unit_cost.setSingleStep(0.5)
            unit_cost.setSpecialValueText(translator.t("bom_costs.no_cost"))
            unit_cost.setValue(entry.unit_cost if entry.unit_cost is not None else 0.0)
            if entry.quantity <= 0.0:
                unit_cost.setEnabled(False)
            apply_help(unit_cost, translator, "bom_costs.unit_cost")
            line_total = QTableWidgetItem("—")
            line_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 0, label)
            self._table.setItem(row, 1, quantity)
            self._table.setItem(row, 2, unit)
            self._table.setCellWidget(row, 3, unit_cost)
            self._table.setItem(row, 4, line_total)
            unit_cost.valueChanged.connect(self._recalculate)
            self._cost_spins.append((entry, unit_cost, line_total))
        self._table.resizeColumnsToContents()
        self._table.setColumnWidth(3, 140)
        self._table.setColumnWidth(4, 140)
        self._table.horizontalHeader().setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Stretch,
        )

        self._total_label = QLabel(self)
        self._total_label.setTextFormat(Qt.TextFormat.PlainText)
        apply_help(self._total_label, translator, "bom_costs.total")
        hint = QLabel(translator.t("bom_costs.hint"), self)
        hint.setWordWrap(True)
        apply_help(hint, translator, "bom_costs.hint")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(currency_form)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._total_label)
        layout.addWidget(hint)
        layout.addWidget(buttons)

        self._currency.textChanged.connect(self._recalculate)
        self._recalculate()

    def _recalculate(self, *args: object) -> None:
        del args
        currency = self._currency.text().strip()
        total = 0.0
        has_cost = False
        for entry, spin, line_total in self._cost_spins:
            unit_cost = spin.value()
            if unit_cost > 0.0 and entry.quantity > 0.0:
                value = entry.quantity * unit_cost
                line_total.setText(format_cost(value, currency))
                total += value
                has_cost = True
            else:
                line_total.setText("—")
        value_text = (
            format_cost(total, currency) if has_cost else self._translator.t("bom_costs.no_cost")
        )
        self._total_label.setText(self._translator.t("bom_costs.total_value", total=value_text))

    def accept(self) -> None:
        current_keys = {entry.key for entry, _, _ in self._cost_spins}
        lines = [
            BomCostLine(entry.key, spin.value())
            for entry, spin, _ in self._cost_spins
            if spin.value() > 0.0
        ]
        if self._existing is not None:
            lines.extend(line for line in self._existing.lines if line.key not in current_keys)
        try:
            record = BomCostRecord(currency=self._currency.text(), lines=tuple(lines))
        except ValueError as exc:
            QMessageBox.critical(self, self._translator.t("bom_costs.title"), str(exc))
            return
        self._record = None if record.is_empty else record
        super().accept()

    def result_bom_costs(self) -> BomCostRecord | None:
        return self._record
