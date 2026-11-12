# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Side-by-side comparison of two journal design snapshots."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.projects.journal import (
    JournalDesignSnapshot,
    JournalRowChange,
    JournalSnapshotComparisonRow,
    compare_journal_snapshots,
)
from ...reporting.journal_snapshot import journal_snapshot_rows
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator


@dataclass(frozen=True, slots=True)
class JournalSnapshotChoice:
    """One selectable historical or current design snapshot."""

    label: str
    snapshot: JournalDesignSnapshot


class JournalComparisonDialog(QDialog):
    """Compare two stored snapshots field by field."""

    def __init__(
        self,
        translator: Translator,
        choices: tuple[JournalSnapshotChoice, ...],
        parent: QWidget | None = None,
        *,
        left_index: int = 0,
        right_index: int = 1,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._choices = choices
        self._rows: tuple[JournalSnapshotComparisonRow, ...] = ()
        self.setWindowTitle(translator.t("journal.comparison.title"))
        self.resize(*scaled_dialog_size(900, 660))

        self._left = QComboBox(self)
        self._right = QComboBox(self)
        for index, choice in enumerate(choices):
            self._left.addItem(choice.label, index)
            self._right.addItem(choice.label, index)
        self._left.setCurrentIndex(min(max(left_index, 0), len(choices) - 1))
        self._right.setCurrentIndex(min(max(right_index, 0), len(choices) - 1))
        self._left.currentIndexChanged.connect(self._render)
        self._right.currentIndexChanged.connect(self._render)
        apply_help(self._left, translator, "journal.comparison.left")
        apply_help(self._right, translator, "journal.comparison.right")

        self._left_label = QLabel(translator.t("journal.comparison.before"), self)
        self._right_label = QLabel(translator.t("journal.comparison.after"), self)
        form = QFormLayout()
        form.addRow(self._left_label, self._left)
        form.addRow(self._right_label, self._right)

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        apply_help(self._summary, translator, "journal.comparison.table")

        self._table = QTableWidget(0, 4, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        apply_help(self._table, translator, "journal.comparison.table")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._summary)
        layout.addWidget(self._table, 1)
        layout.addWidget(buttons)

        self._render()

    def rows(self) -> tuple[JournalSnapshotComparisonRow, ...]:
        return self._rows

    def _render(self, *_args: object) -> None:
        left = self._choices[self._left.currentIndex()].snapshot
        right = self._choices[self._right.currentIndex()].snapshot
        self._rows = compare_journal_snapshots(left, right)
        left_rows = dict(journal_snapshot_rows(left, self._translate))
        right_rows = dict(journal_snapshot_rows(right, self._translate))
        changed = sum(1 for row in self._rows if row.change is JournalRowChange.CHANGED)
        same = sum(1 for row in self._rows if row.change is JournalRowChange.SAME)
        added = sum(1 for row in self._rows if row.change is JournalRowChange.ADDED)
        removed = sum(1 for row in self._rows if row.change is JournalRowChange.REMOVED)
        self._summary.setText(
            self._translator.t(
                "journal.comparison.summary",
                changed=changed,
                same=same,
                added=added,
                removed=removed,
            )
        )
        self._table.setHorizontalHeaderLabels(
            [
                self._translator.t("journal.comparison.field"),
                self._translator.t("journal.comparison.before"),
                self._translator.t("journal.comparison.after"),
                self._translator.t("journal.comparison.change"),
            ]
        )
        self._table.setRowCount(len(self._rows))
        self._table.blockSignals(True)
        try:
            for row_index, row in enumerate(self._rows):
                label = self._translate(row.label)
                values = (
                    label,
                    left_rows.get(label, "—"),
                    right_rows.get(label, "—"),
                    self._translator.t(f"journal.comparison.change.{row.change.value}"),
                )
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if row.change is not JournalRowChange.SAME:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    if column == 3:
                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                        )
                    if row.change is JournalRowChange.SAME:
                        item.setForeground(QBrush(QColor("#7a7a7a")))
                    self._table.setItem(row_index, column, item)
        finally:
            self._table.blockSignals(False)
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def _translate(self, text: str, /, **values: object) -> str:
        translated = self._translator.t(text, **values)
        return text if translated == text else translated
