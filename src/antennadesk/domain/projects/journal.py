# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project journal entries and design snapshots for version comparison."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from ..common.time import ensure_utc
from ..common.units import ensure_positive

MAX_JOURNAL_TITLE_LENGTH = 200
MAX_JOURNAL_BODY_LENGTH = 8_000
MAX_JOURNAL_IMAGE_REFERENCES = 12
MAX_JOURNAL_IMAGE_REFERENCE_LENGTH = 1_000


class JournalEntryKind(StrEnum):
    NOTE = "note"
    DECISION = "decision"
    AS_BUILT = "as_built"
    MEASUREMENT = "measurement"
    TUNING = "tuning"
    PHOTO = "photo"
    OTHER = "other"


class JournalRowChange(StrEnum):
    SAME = "same"
    CHANGED = "changed"
    ADDED = "added"
    REMOVED = "removed"


@dataclass(frozen=True, slots=True)
class JournalDesignSnapshot:
    """A compact, comparable snapshot of a design's summary sheet."""

    design_id: UUID | None
    design_name: str
    antenna_type: str
    frequency_hz: float
    rows: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        design_name = self.design_name.strip()
        antenna_type = self.antenna_type.strip()
        if not design_name:
            raise ValueError("journal snapshot design name must not be empty")
        if not antenna_type:
            raise ValueError("journal snapshot antenna type must not be empty")
        ensure_positive(self.frequency_hz, name="journal snapshot frequency_hz")
        rows = tuple((str(label).strip(), str(value)) for label, value in self.rows)
        if any(not label for label, _ in rows):
            raise ValueError("journal snapshot row labels must not be empty")
        labels = [label for label, _ in rows]
        if len(labels) != len(set(labels)):
            raise ValueError("journal snapshot row labels must be unique")
        object.__setattr__(self, "design_name", design_name)
        object.__setattr__(self, "antenna_type", antenna_type)
        object.__setattr__(self, "rows", rows)


@dataclass(frozen=True, slots=True)
class JournalSnapshotComparisonRow:
    """One field compared between two historical design snapshots."""

    label: str
    left: str | None
    right: str | None
    change: JournalRowChange

    def __post_init__(self) -> None:
        object.__setattr__(self, "change", JournalRowChange(self.change))


def compare_journal_snapshots(
    left: JournalDesignSnapshot,
    right: JournalDesignSnapshot,
) -> tuple[JournalSnapshotComparisonRow, ...]:
    """Compare snapshots in row order without inferring numeric changes."""

    left_rows = dict(left.rows)
    right_rows = dict(right.rows)
    labels = [label for label, _ in left.rows]
    labels.extend(label for label, _ in right.rows if label not in left_rows)
    rows: list[JournalSnapshotComparisonRow] = []
    for label in labels:
        before = left_rows.get(label)
        after = right_rows.get(label)
        if before is None:
            change = JournalRowChange.ADDED
        elif after is None:
            change = JournalRowChange.REMOVED
        elif before == after:
            change = JournalRowChange.SAME
        else:
            change = JournalRowChange.CHANGED
        rows.append(JournalSnapshotComparisonRow(label, before, after, change))
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class JournalEntry:
    """One dated project journal record."""

    id: UUID
    created_at: datetime
    title: str
    kind: JournalEntryKind = JournalEntryKind.NOTE
    body: str = ""
    design_id: UUID | None = None
    snapshot: JournalDesignSnapshot | None = None
    image_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        title = self.title.strip()
        if not title:
            raise ValueError("journal title must not be empty")
        if len(title) > MAX_JOURNAL_TITLE_LENGTH:
            raise ValueError(f"journal title must be at most {MAX_JOURNAL_TITLE_LENGTH} characters")
        ensure_utc(self.created_at, name="journal created_at")
        if len(self.body) > MAX_JOURNAL_BODY_LENGTH:
            raise ValueError(f"journal body must be at most {MAX_JOURNAL_BODY_LENGTH} characters")
        references = tuple(str(reference).strip() for reference in self.image_references)
        if len(references) > MAX_JOURNAL_IMAGE_REFERENCES:
            raise ValueError(
                f"journal entries support at most {MAX_JOURNAL_IMAGE_REFERENCES} image references"
            )
        if any(not reference for reference in references):
            raise ValueError("journal image references must not be empty")
        if any(len(reference) > MAX_JOURNAL_IMAGE_REFERENCE_LENGTH for reference in references):
            raise ValueError(
                "journal image references must be at most "
                f"{MAX_JOURNAL_IMAGE_REFERENCE_LENGTH} characters"
            )
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "kind", JournalEntryKind(self.kind))
        object.__setattr__(self, "image_references", references)
