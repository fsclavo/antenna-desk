# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project journal timeline, notes, photos, and snapshot comparison."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.projects.journal import JournalEntry
from ...domain.projects.project import Project
from ...reporting.journal_snapshot import journal_design_snapshot
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from .journal_comparison_dialog import JournalComparisonDialog, JournalSnapshotChoice
from .journal_entry_dialog import JournalEntryDialog


class JournalDialog(QDialog):
    """Show the journal newest-first and edit its entries."""

    def __init__(
        self,
        translator: Translator,
        project: Project,
        parent: QWidget | None = None,
        *,
        now: Callable[[], datetime] | None = None,
        default_design_id: UUID | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._now = now or (lambda: datetime.now(UTC))
        self._default_design_id = default_design_id
        self._entries: tuple[JournalEntry, ...] = ()
        self.setWindowTitle(translator.t("journal.title"))
        self.resize(*scaled_dialog_size(1_020, 720))

        self._summary = QLabel(
            translator.t("journal.timeline", count=0, snapshots=0),
            self,
        )
        self._summary.setWordWrap(True)
        apply_help(self._summary, translator, "journal.timeline")

        self._table = QTableWidget(0, 6, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.itemSelectionChanged.connect(self._selection_changed)
        self._table.itemDoubleClicked.connect(lambda _item: self._edit_entry())
        apply_help(self._table, translator, "journal.table")

        self._details = QLabel(self)
        self._details.setWordWrap(True)
        self._details.setTextFormat(Qt.TextFormat.PlainText)
        self._details.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        apply_help(self._details, translator, "journal.details")
        self._preview = QLabel(self)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setMinimumSize(260, 170)
        self._preview.setWordWrap(True)
        apply_help(self._preview, translator, "journal.preview")

        self._new = QPushButton(translator.t("journal.new"), self)
        self._edit = QPushButton(translator.t("journal.edit"), self)
        self._delete = QPushButton(translator.t("journal.delete"), self)
        self._compare = QPushButton(translator.t("journal.compare"), self)
        self._new.clicked.connect(self._new_entry)
        self._edit.clicked.connect(self._edit_entry)
        self._delete.clicked.connect(self._delete_entry)
        self._compare.clicked.connect(self._compare_versions)
        for button, key in (
            (self._new, "journal.new"),
            (self._edit, "journal.edit"),
            (self._delete, "journal.delete"),
            (self._compare, "journal.compare"),
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

        actions = QHBoxLayout()
        actions.addWidget(self._new)
        actions.addWidget(self._edit)
        actions.addWidget(self._delete)
        actions.addStretch(1)
        actions.addWidget(self._compare)

        details_row = QHBoxLayout()
        details_row.addWidget(self._details, 2)
        details_row.addWidget(self._preview, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(self._summary)
        layout.addWidget(self._table, 2)
        layout.addLayout(details_row, 2)
        layout.addLayout(actions)
        layout.addWidget(buttons)

        self._reload()

    def result_project(self) -> Project:
        return self._project

    def _reload(self, selected_id: UUID | None = None) -> None:
        self._entries = tuple(
            sorted(
                self._project.journal_entries,
                key=lambda entry: (entry.created_at, entry.title.lower()),
                reverse=True,
            )
        )
        self._table.blockSignals(True)
        try:
            self._table.setRowCount(len(self._entries))
            self._table.setHorizontalHeaderLabels(
                [
                    self._translator.t("journal.date"),
                    self._translator.t("journal.kind_column"),
                    self._translator.t("journal.title_column"),
                    self._translator.t("journal.design"),
                    self._translator.t("journal.images"),
                    self._translator.t("journal.snapshot"),
                ]
            )
            for row, entry in enumerate(self._entries):
                design = (
                    next(
                        (
                            design.name
                            for design in self._project.designs
                            if design.id == entry.design_id
                        ),
                        None,
                    )
                    if entry.design_id is not None
                    else None
                )
                values = (
                    entry.created_at.strftime("%Y-%m-%d %H:%M"),
                    self._translator.t(f"journal.kind.{entry.kind.value}"),
                    entry.title,
                    design or "—",
                    str(len(entry.image_references)) if entry.image_references else "—",
                    (
                        self._translator.t(
                            "journal.snapshot_available",
                            name=entry.snapshot.design_name,
                        )
                        if entry.snapshot is not None
                        else "—"
                    ),
                )
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if column == 0:
                        item.setData(Qt.ItemDataRole.UserRole, entry.id)
                    self._table.setItem(row, column, item)
        finally:
            self._table.blockSignals(False)
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setStretchLastSection(True)
        self._summary.setText(
            self._translator.t(
                "journal.timeline",
                count=len(self._entries),
                snapshots=sum(1 for entry in self._entries if entry.snapshot is not None),
            )
        )
        if self._entries:
            target = 0
            if selected_id is not None:
                target = next(
                    (row for row, entry in enumerate(self._entries) if entry.id == selected_id),
                    0,
                )
            self._table.selectRow(target)
        else:
            self._details.setText(self._translator.t("journal.empty"))
            self._preview.clear()
            self._preview.setText(self._translator.t("journal.preview_hint"))
        self._update_actions()

    def _selected_entry(self) -> JournalEntry | None:
        row = self._table.currentRow()
        if row < 0 or row >= len(self._entries):
            return None
        return self._entries[row]

    def _selection_changed(self) -> None:
        entry = self._selected_entry()
        if entry is None:
            self._details.setText(self._translator.t("journal.empty"))
            self._preview.clear()
            self._preview.setText(self._translator.t("journal.preview_hint"))
            self._update_actions()
            return
        design = (
            next(
                (design.name for design in self._project.designs if design.id == entry.design_id),
                None,
            )
            if entry.design_id is not None
            else None
        )
        lines = [
            entry.title,
            self._translator.t(
                "journal.details_meta",
                date=entry.created_at.strftime("%Y-%m-%d %H:%M"),
                kind=self._translator.t(f"journal.kind.{entry.kind.value}"),
                design=design or self._translator.t("journal.no_design"),
            ),
            "",
            entry.body or self._translator.t("journal.no_notes"),
        ]
        if entry.image_references:
            lines.extend(
                [
                    "",
                    self._translator.t("journal.field.images"),
                    *entry.image_references,
                ]
            )
        if entry.snapshot is not None:
            lines.extend(
                [
                    "",
                    self._translator.t(
                        "journal.snapshot_stored",
                        name=entry.snapshot.design_name,
                        rows=len(entry.snapshot.rows),
                    ),
                ]
            )
        self._details.setText("\n".join(lines))
        self._show_preview(entry)
        self._update_actions()

    def _show_preview(self, entry: JournalEntry) -> None:
        if not entry.image_references:
            self._preview.clear()
            self._preview.setText(self._translator.t("journal.preview_hint"))
            return
        path = entry.image_references[0]
        if not Path(path).is_file():
            self._preview.clear()
            self._preview.setText(self._translator.t("journal.preview_unavailable"))
            return
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._preview.clear()
            self._preview.setText(self._translator.t("journal.preview_unavailable"))
            return
        self._preview.setPixmap(
            pixmap.scaled(
                320,
                220,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _update_actions(self) -> None:
        has_selection = self._selected_entry() is not None
        self._edit.setEnabled(has_selection)
        self._delete.setEnabled(has_selection)
        self._compare.setEnabled(len(self._comparison_choices()) >= 2)

    def _new_entry(self) -> None:
        dialog = JournalEntryDialog(
            self._translator,
            self._project,
            self,
            default_design_id=self._default_design_id,
            now=self._now,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        entry = dialog.entry()
        if entry is None:
            return
        self._project = self._project.with_journal_entry(
            entry,
            updated_at=self._now(),
        )
        self._reload(entry.id)

    def _edit_entry(self) -> None:
        entry = self._selected_entry()
        if entry is None:
            return
        dialog = JournalEntryDialog(
            self._translator,
            self._project,
            self,
            entry=entry,
            now=self._now,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        updated = dialog.entry()
        if updated is None or updated == entry:
            return
        self._project = self._project.with_updated_journal_entry(
            updated,
            updated_at=self._now(),
        )
        self._reload(updated.id)

    def _delete_entry(self) -> None:
        entry = self._selected_entry()
        if entry is None:
            return
        answer = QMessageBox.question(
            self,
            self._translator.t("journal.delete_title"),
            self._translator.t("journal.delete_confirm", title=entry.title),
        )
        if answer is not QMessageBox.StandardButton.Yes:
            return
        self._project = self._project.without_journal_entry(
            entry.id,
            updated_at=self._now(),
        )
        self._reload()

    def _comparison_choices(self) -> tuple[JournalSnapshotChoice, ...]:
        stored = tuple(
            JournalSnapshotChoice(
                label=(
                    f"{entry.created_at.strftime('%Y-%m-%d %H:%M')} · "
                    f"{entry.title} · {entry.snapshot.design_name}"
                ),
                snapshot=entry.snapshot,
            )
            for entry in sorted(
                self._project.journal_entries,
                key=lambda entry: entry.created_at,
            )
            if entry.snapshot is not None
        )
        if not stored:
            return ()
        current = tuple(
            JournalSnapshotChoice(
                label=self._translator.t(
                    "journal.current_design",
                    name=design.name,
                ),
                snapshot=journal_design_snapshot(self._project, design),
            )
            for design in self._project.designs
        )
        return (*stored, *current)

    def _compare_versions(self) -> None:
        choices = self._comparison_choices()
        if len(choices) < 2:
            QMessageBox.information(
                self,
                self._translator.t("journal.comparison.title"),
                self._translator.t("journal.comparison.need_two"),
            )
            return
        dialog = JournalComparisonDialog(
            self._translator,
            choices,
            self,
            left_index=max(len(choices) - 2, 0),
            right_index=len(choices) - 1,
        )
        dialog.exec()
