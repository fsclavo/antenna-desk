# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project journal editor, timeline, and version comparison dialogs."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.journal import (
    JournalDesignSnapshot,
    JournalEntry,
    JournalEntryKind,
    JournalRowChange,
)
from antennadesk.domain.projects.project import Project
from antennadesk.reporting.journal_snapshot import journal_design_snapshot
from antennadesk.ui.dialogs import journal_dialog as journal_dialog_module
from antennadesk.ui.dialogs.journal_comparison_dialog import (
    JournalComparisonDialog,
    JournalSnapshotChoice,
)
from antennadesk.ui.dialogs.journal_dialog import JournalDialog
from antennadesk.ui.dialogs.journal_entry_dialog import JournalEntryDialog
from antennadesk.ui.i18n import Language, Translator

NOW = datetime(2026, 11, 12, 20, 0, tzinfo=UTC)
DESIGN_ID = UUID("00000000-0000-0000-0000-000000000002")


def _snapshot(
    *,
    design_name: str = "Initial",
    rows: tuple[tuple[str, str], ...] | None = None,
) -> JournalDesignSnapshot:
    return JournalDesignSnapshot(
        design_id=DESIGN_ID,
        design_name=design_name,
        antenna_type="wire_dipole",
        frequency_hz=7_100_000.0,
        rows=rows
        or (
            ("Frequency", "7.100000 MHz"),
            ("Total wire length", "20.0000 m"),
            ("Model wires", "1"),
        ),
    )


def _entry(
    *,
    title: str,
    created_at: datetime = NOW,
    kind: JournalEntryKind = JournalEntryKind.NOTE,
    body: str = "",
    design_id: UUID | None = DESIGN_ID,
    snapshot: JournalDesignSnapshot | None = None,
    images: tuple[str, ...] = (),
) -> JournalEntry:
    return JournalEntry(
        id=uuid5(NAMESPACE_URL, f"{title}-{created_at.isoformat()}"),
        created_at=created_at,
        title=title,
        kind=kind,
        body=body,
        design_id=design_id,
        snapshot=snapshot,
        image_references=images,
    )


def test_entry_dialog_captures_a_snapshot(qtbot: QtBot, sample_project: Project) -> None:
    dialog = JournalEntryDialog(
        Translator(Language.ENGLISH),
        sample_project,
        now=lambda: NOW,
        default_design_id=DESIGN_ID,
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Journal entry"
    assert sample_project.designs[0].id == DESIGN_ID
    assert dialog._design.itemData(1) == DESIGN_ID
    assert dialog._design.currentData() == DESIGN_ID
    assert dialog._capture.isChecked() is True
    dialog._title.setText("  As built  ")
    dialog._body.setPlainText("Trimmed the radiator to 20.05 m.")
    dialog.accept()

    entry = dialog.entry()
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert entry is not None
    assert entry.title == "As built"
    assert entry.created_at == NOW
    assert entry.design_id == DESIGN_ID
    assert entry.snapshot is not None
    assert dict(entry.snapshot.rows)["Frequency"] == "7.100000 MHz"
    assert dict(entry.snapshot.rows)["Model wires"] == "1"


def test_entry_dialog_requires_a_title(qtbot: QtBot, sample_project: Project) -> None:
    dialog = JournalEntryDialog(
        Translator(Language.ENGLISH),
        sample_project,
        now=lambda: NOW,
    )
    qtbot.addWidget(dialog)

    dialog.accept()

    assert dialog.result() != QDialog.DialogCode.Accepted
    assert dialog._validation.isHidden() is False
    assert "title" in dialog._validation.text().lower()


def test_entry_dialog_preserves_a_stored_snapshot(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    snapshot = _snapshot()
    entry = _entry(title="First build", body="Before", snapshot=snapshot)
    dialog = JournalEntryDialog(
        Translator(Language.ENGLISH),
        sample_project,
        entry=entry,
        now=lambda: NOW,
    )
    qtbot.addWidget(dialog)

    assert dialog._capture.isHidden() is True
    assert dialog._snapshot_info.isHidden() is False
    assert "does not recapture" in dialog._snapshot_info.text()
    dialog._title.setText("First build, revised")
    dialog._body.setPlainText("After")
    dialog._design.setCurrentIndex(0)
    dialog.accept()

    updated = dialog.entry()
    assert updated is not None
    assert updated.title == "First build, revised"
    assert updated.body == "After"
    assert updated.design_id is None
    assert updated.snapshot == snapshot


def test_entry_dialog_manages_image_references(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    from antennadesk.domain.projects.journal import MAX_JOURNAL_IMAGE_REFERENCES

    dialog = JournalEntryDialog(
        Translator(Language.ENGLISH),
        sample_project,
        now=lambda: NOW,
    )
    qtbot.addWidget(dialog)

    dialog._append_image_paths(("/home/operator/a.jpg", "/home/operator/b.jpg"))
    assert dialog._images.count() == 2
    assert dialog._image_references() == (
        "/home/operator/a.jpg",
        "/home/operator/b.jpg",
    )

    dialog._images.setCurrentRow(0)
    dialog._remove_selected_image()
    assert dialog._image_references() == ("/home/operator/b.jpg",)

    dialog._append_image_paths(tuple(f"/home/operator/photo-{index}.jpg" for index in range(20)))
    assert dialog._images.count() == MAX_JOURNAL_IMAGE_REFERENCES
    assert dialog._validation.isHidden() is False
    assert str(MAX_JOURNAL_IMAGE_REFERENCES) in dialog._validation.text()


def test_entry_dialog_retranslates(qtbot: QtBot, sample_project: Project) -> None:
    dialog = JournalEntryDialog(
        Translator(Language.SPANISH),
        sample_project,
        now=lambda: NOW,
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Entrada de la bitácora"
    assert dialog._kind.itemText(0) == "Nota"


def _journal_project(sample_project: Project) -> Project:
    design = sample_project.designs[0]
    first = _entry(
        title="Chosen layout",
        created_at=NOW - timedelta(days=2),
        kind=JournalEntryKind.DECISION,
        body="Use the north support.",
        snapshot=_snapshot(rows=(("Frequency", "7.100000 MHz"),)),
    )
    second = _entry(
        title="First build",
        created_at=NOW - timedelta(days=1),
        kind=JournalEntryKind.AS_BUILT,
        body="Trimmed to 20.05 m.",
        snapshot=_snapshot(
            design_name="First build",
            rows=(
                ("Frequency", "7.100000 MHz"),
                ("Total wire length", "20.0500 m"),
            ),
        ),
        images=("/home/operator/build.jpg",),
    )
    third = _entry(
        title="Site note",
        created_at=NOW,
        kind=JournalEntryKind.OTHER,
        body="Moved the mast.",
        design_id=None,
        snapshot=None,
    )
    assert design.id == DESIGN_ID
    return (
        sample_project.with_journal_entry(first, updated_at=NOW)
        .with_journal_entry(second, updated_at=NOW)
        .with_journal_entry(third, updated_at=NOW)
    )


def test_timeline_lists_entries_newest_first(qtbot: QtBot, sample_project: Project) -> None:
    project = _journal_project(sample_project)
    dialog = JournalDialog(Translator(Language.ENGLISH), project, now=lambda: NOW)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Project journal"
    assert dialog._table.rowCount() == 3
    assert dialog._table.item(0, 2).text() == "Site note"
    assert dialog._table.item(1, 2).text() == "First build"
    assert dialog._table.item(2, 2).text() == "Chosen layout"
    assert "3 entries" in dialog._summary.text()
    assert "2 with design snapshots" in dialog._summary.text()
    assert dialog._table.item(0, 3).text() == "—"
    assert dialog._table.item(1, 4).text() == "1"
    assert "Captured" in dialog._table.item(1, 5).text()
    assert dialog._edit.isEnabled() is True
    assert dialog._delete.isEnabled() is True
    assert dialog._compare.isEnabled() is True

    dialog._table.selectRow(1)

    assert "First build" in dialog._details.text()
    assert "Trimmed to 20.05 m." in dialog._details.text()
    assert "/home/operator/build.jpg" in dialog._details.text()
    assert "Stored snapshot" in dialog._details.text()


def test_timeline_new_edit_and_delete_update_the_project(
    qtbot: QtBot,
    sample_project: Project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _journal_project(sample_project)
    dialog = JournalDialog(Translator(Language.ENGLISH), project, now=lambda: NOW)
    qtbot.addWidget(dialog)

    created = _entry(title="New note", created_at=NOW, design_id=None, snapshot=None)

    class FakeEntryDialog:
        action = "new"

        def __init__(self, *args: object, entry: JournalEntry | None = None, **kwargs: object):
            self._entry = created if entry is None else replace(entry, body="Edited")

        def exec(self) -> int:
            return QDialog.DialogCode.Accepted

        def entry(self) -> JournalEntry:
            return self._entry

    monkeypatch.setattr(journal_dialog_module, "JournalEntryDialog", FakeEntryDialog)
    dialog._new_entry()
    assert dialog._table.rowCount() == 4
    assert dialog.result_project().journal_entries[-1].title == "New note"

    created_row = next(
        row
        for row in range(dialog._table.rowCount())
        if dialog._table.item(row, 0).data(Qt.ItemDataRole.UserRole) == created.id
    )
    dialog._table.selectRow(created_row)
    dialog._edit_entry()
    edited = next(
        entry for entry in dialog.result_project().journal_entries if entry.id == created.id
    )
    assert edited.body == "Edited"

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    dialog._table.selectRow(created_row)
    dialog._delete_entry()
    assert dialog._table.rowCount() == 3
    assert all(entry.title != "New note" for entry in dialog.result_project().journal_entries)


def test_comparison_reports_changed_added_and_removed_rows(qtbot: QtBot) -> None:
    left = _snapshot(
        rows=(
            ("Frequency", "7.100000 MHz"),
            ("Total wire length", "20.0000 m"),
            ("Legacy field", "old"),
        )
    )
    right = _snapshot(
        rows=(
            ("Frequency", "7.100000 MHz"),
            ("Total wire length", "20.0500 m"),
            ("Model wires", "1"),
        )
    )
    choices = (
        JournalSnapshotChoice("Initial", left),
        JournalSnapshotChoice("Current", right),
    )
    dialog = JournalComparisonDialog(Translator(Language.ENGLISH), choices)
    qtbot.addWidget(dialog)

    rows = dialog.rows()
    assert [row.change for row in rows] == [
        JournalRowChange.SAME,
        JournalRowChange.CHANGED,
        JournalRowChange.REMOVED,
        JournalRowChange.ADDED,
    ]
    assert dialog._table.rowCount() == 4
    assert dialog._table.item(1, 3).text() == "Changed"
    assert dialog._table.item(2, 3).text() == "Removed"
    assert dialog._table.item(3, 3).text() == "Added"
    assert "1 changed" in dialog._summary.text()
    assert "1 unchanged" in dialog._summary.text()


def test_comparison_dialog_retranslates(qtbot: QtBot) -> None:
    snapshot = _snapshot()
    dialog = JournalComparisonDialog(
        Translator(Language.SPANISH),
        (
            JournalSnapshotChoice("Inicial", snapshot),
            JournalSnapshotChoice("Actual", snapshot),
        ),
    )
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Comparar versiones de diseño"
    assert dialog.rows()
    assert all(row.change is JournalRowChange.SAME for row in dialog.rows())


def test_timeline_comparison_choices_include_the_current_design(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    project = _journal_project(sample_project)
    dialog = JournalDialog(Translator(Language.ENGLISH), project, now=lambda: NOW)
    qtbot.addWidget(dialog)

    choices = dialog._comparison_choices()

    assert len(choices) == 3
    assert choices[-1].label == "Current design — Initial"
    assert choices[-1].snapshot == journal_design_snapshot(
        project,
        project.designs[0],
    )


def test_journal_dialog_without_snapshots_cannot_compare(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    entry = _entry(title="Only a note", design_id=None, snapshot=None)
    project = sample_project.with_journal_entry(entry, updated_at=NOW)
    dialog = JournalDialog(Translator(Language.ENGLISH), project, now=lambda: NOW)
    qtbot.addWidget(dialog)

    assert dialog._compare.isEnabled() is False
    assert dialog._comparison_choices() == ()
