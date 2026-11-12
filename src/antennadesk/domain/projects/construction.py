# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""As-built construction record and checklist."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ..common.units import ensure_non_negative

MAX_CONSTRUCTION_LABEL_LENGTH = 200
MAX_CONSTRUCTION_NOTES_LENGTH = 4_000
MAX_DIMENSION_NOTES_LENGTH = 1_000

CONSTRUCTION_CHECKLIST_KEYS: tuple[str, ...] = (
    "prepare_drawings",
    "check_dimensions",
    "inspect_insulators",
    "check_feedpoint",
    "seal_connectors",
    "check_supports",
    "verify_grounding",
    "measure_swr",
    "record_measurement",
    "update_as_built",
)


@dataclass(frozen=True, slots=True)
class AsBuiltDimension:
    """One measured construction dimension and its design counterpart."""

    id: UUID
    label: str
    design_value_m: float | None = None
    actual_value_m: float | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        label = self.label.strip()
        if not label:
            raise ValueError("as-built dimension label must not be empty")
        if len(label) > MAX_CONSTRUCTION_LABEL_LENGTH:
            raise ValueError(
                "as-built dimension label must be at most "
                f"{MAX_CONSTRUCTION_LABEL_LENGTH} characters"
            )
        if self.design_value_m is not None:
            ensure_non_negative(self.design_value_m, name="design_value_m")
        if self.actual_value_m is not None:
            ensure_non_negative(self.actual_value_m, name="actual_value_m")
        if len(self.notes) > MAX_DIMENSION_NOTES_LENGTH:
            raise ValueError(
                f"as-built dimension notes must be at most {MAX_DIMENSION_NOTES_LENGTH} characters"
            )
        object.__setattr__(self, "label", label)


@dataclass(frozen=True, slots=True)
class ConstructionChecklistItem:
    """One construction checklist entry."""

    key: str
    checked: bool = False

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("construction checklist key must not be empty")
        object.__setattr__(self, "key", self.key.strip())


@dataclass(frozen=True, slots=True)
class ConstructionRecord:
    """As-built notes, measured dimensions, and checklist state."""

    as_built_notes: str = ""
    dimensions: tuple[AsBuiltDimension, ...] = ()
    checklist: tuple[ConstructionChecklistItem, ...] = ()

    def __post_init__(self) -> None:
        if len(self.as_built_notes) > MAX_CONSTRUCTION_NOTES_LENGTH:
            raise ValueError(
                f"as-built notes must be at most {MAX_CONSTRUCTION_NOTES_LENGTH} characters"
            )
        dimensions = tuple(self.dimensions)
        ids = [dimension.id for dimension in dimensions]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate as-built dimension id")
        checklist = tuple(self.checklist)
        keys = [item.key for item in checklist]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate construction checklist key")
        object.__setattr__(self, "dimensions", dimensions)
        object.__setattr__(self, "checklist", checklist)

    def checked_keys(self) -> frozenset[str]:
        return frozenset(item.key for item in self.checklist if item.checked)
