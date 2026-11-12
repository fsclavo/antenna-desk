# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project journal entries, snapshots, and their project links."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from antennadesk.application.use_cases.delete_design_variant import (
    DeleteDesignVariant,
    DeleteDesignVariantCommand,
)
from antennadesk.domain.projects.journal import (
    MAX_JOURNAL_BODY_LENGTH,
    MAX_JOURNAL_IMAGE_REFERENCES,
    MAX_JOURNAL_TITLE_LENGTH,
    JournalDesignSnapshot,
    JournalEntry,
    JournalEntryKind,
    JournalRowChange,
    compare_journal_snapshots,
)
from antennadesk.domain.projects.project import Project


def _snapshot(**overrides: object) -> JournalDesignSnapshot:
    values: dict[str, object] = {
        "design_id": uuid4(),
        "design_name": "Initial",
        "antenna_type": "wire_dipole",
        "frequency_hz": 7_100_000.0,
        "rows": (
            ("Frequency", "7.100000 MHz"),
            ("Total wire length", "20.0000 m"),
        ),
    }
    values.update(overrides)
    return JournalDesignSnapshot(**values)  # type: ignore[arg-type]


def _entry(**overrides: object) -> JournalEntry:
    values: dict[str, object] = {
        "id": uuid4(),
        "created_at": datetime(2026, 11, 12, 18, 0, tzinfo=UTC),
        "title": "First contact",
        "kind": JournalEntryKind.NOTE,
        "body": "Worked Europe on 40 m.",
        "snapshot": _snapshot(),
        "image_references": ("/home/operator/photos/station.jpg",),
    }
    values.update(overrides)
    return JournalEntry(**values)  # type: ignore[arg-type]


def test_entry_trims_text_and_normalizes_its_kind() -> None:
    entry = _entry(
        title="  As built  ",
        kind="as_built",
        image_references=("  /home/operator/photo.jpg  ",),
    )

    assert entry.title == "As built"
    assert entry.kind is JournalEntryKind.AS_BUILT
    assert entry.image_references == ("/home/operator/photo.jpg",)


def test_entry_validates_title_time_body_and_images() -> None:
    with pytest.raises(ValueError, match="title"):
        _entry(title=" ")
    with pytest.raises(ValueError, match="at most"):
        _entry(title="x" * (MAX_JOURNAL_TITLE_LENGTH + 1))
    with pytest.raises(ValueError, match="timezone-aware"):
        _entry(created_at=datetime(2026, 11, 12, 18, 0))
    with pytest.raises(ValueError, match="body"):
        _entry(body="x" * (MAX_JOURNAL_BODY_LENGTH + 1))
    with pytest.raises(ValueError, match="at most"):
        _entry(
            image_references=tuple(
                f"/home/operator/photo-{index}.jpg"
                for index in range(MAX_JOURNAL_IMAGE_REFERENCES + 1)
            )
        )
    with pytest.raises(ValueError, match="must not be empty"):
        _entry(image_references=(" ",))


def test_snapshot_validates_its_identity_and_rows() -> None:
    snapshot = _snapshot(
        design_name="  Initial  ",
        rows=((" Frequency ", "7.100000 MHz"),),
    )

    assert snapshot.design_name == "Initial"
    assert snapshot.rows == (("Frequency", "7.100000 MHz"),)

    with pytest.raises(ValueError, match="design name"):
        _snapshot(design_name=" ")
    with pytest.raises(ValueError, match="antenna type"):
        _snapshot(antenna_type=" ")
    with pytest.raises(ValueError, match="frequency"):
        _snapshot(frequency_hz=0.0)
    with pytest.raises(ValueError, match="labels must not be empty"):
        _snapshot(rows=((" ", "value"),))
    with pytest.raises(ValueError, match="unique"):
        _snapshot(rows=(("Frequency", "7.1"), ("Frequency", "14.1")))


def test_snapshot_comparison_reports_changes_in_row_order() -> None:
    left = _snapshot(
        rows=(
            ("Frequency", "7.100000 MHz"),
            ("Total wire length", "20.0000 m"),
            ("Removed field", "legacy"),
        )
    )
    right = _snapshot(
        rows=(
            ("Total wire length", "20.0500 m"),
            ("Frequency", "7.100000 MHz"),
            ("Model wires", "1"),
        )
    )

    rows = compare_journal_snapshots(left, right)

    assert [row.label for row in rows] == [
        "Frequency",
        "Total wire length",
        "Removed field",
        "Model wires",
    ]
    assert [row.change for row in rows] == [
        JournalRowChange.SAME,
        JournalRowChange.CHANGED,
        JournalRowChange.REMOVED,
        JournalRowChange.ADDED,
    ]
    assert rows[1].left == "20.0000 m"
    assert rows[1].right == "20.0500 m"
    assert rows[2].right is None
    assert rows[3].left is None


def test_project_adds_updates_and_removes_an_entry(sample_project: Project) -> None:
    design = sample_project.designs[0]
    entry = _entry(design_id=design.id, snapshot=_snapshot(design_id=design.id))
    project = sample_project.with_journal_entry(
        entry,
        updated_at=sample_project.updated_at + timedelta(hours=1),
    )

    assert project.journal_entry_by_id(entry.id) == entry
    assert project.journal_entries == (entry,)

    updated = replace(entry, title="After tuning", body="Trimmed the radiator")
    project = project.with_updated_journal_entry(
        updated,
        updated_at=sample_project.updated_at + timedelta(hours=2),
    )
    assert project.journal_entries == (updated,)
    assert project.journal_entries[0].snapshot == entry.snapshot

    project = project.without_journal_entry(
        entry.id,
        updated_at=sample_project.updated_at + timedelta(hours=3),
    )
    assert project.journal_entries == ()


def test_project_rejects_unknown_journal_operations(sample_project: Project) -> None:
    entry = _entry()

    with pytest.raises(KeyError, match="unknown journal entry"):
        sample_project.with_updated_journal_entry(
            entry,
            updated_at=sample_project.updated_at,
        )
    with pytest.raises(KeyError, match="unknown journal entry"):
        sample_project.without_journal_entry(
            entry.id,
            updated_at=sample_project.updated_at,
        )
    with pytest.raises(KeyError, match="unknown journal entry"):
        sample_project.journal_entry_by_id(entry.id)


def test_project_rejects_duplicate_entry_ids(sample_project: Project) -> None:
    entry = _entry()
    project = sample_project.with_journal_entry(
        entry,
        updated_at=sample_project.updated_at,
    )

    with pytest.raises(ValueError, match="duplicate journal entry id"):
        project.with_journal_entry(
            replace(entry, title="Another entry"),
            updated_at=sample_project.updated_at,
        )


def test_project_rejects_an_entry_with_an_unknown_design(sample_project: Project) -> None:
    with pytest.raises(ValueError, match="unknown design"):
        sample_project.with_journal_entry(
            _entry(design_id=uuid4()),
            updated_at=sample_project.updated_at,
        )


def test_deleting_a_design_detaches_the_entry_and_keeps_its_snapshot(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    snapshot = _snapshot(design_id=design.id, design_name=design.name)
    entry = _entry(design_id=design.id, snapshot=snapshot)
    project = sample_project.with_journal_entry(
        entry,
        updated_at=sample_project.updated_at,
    )
    second = replace(design, id=uuid4(), name="Second")
    project = project.with_design(second, updated_at=sample_project.updated_at)

    deleted = DeleteDesignVariant().execute(
        DeleteDesignVariantCommand(
            project=project,
            design_id=design.id,
            updated_at=sample_project.updated_at + timedelta(hours=1),
        )
    )

    assert deleted.journal_entries[0].design_id is None
    assert deleted.journal_entries[0].snapshot == snapshot
    assert deleted.journal_entries[0].body == entry.body
