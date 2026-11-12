# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""As-built construction record validation and project operations."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

import pytest

from antennadesk.domain.projects.construction import (
    AsBuiltDimension,
    ConstructionChecklistItem,
    ConstructionRecord,
)
from antennadesk.domain.projects.project import Project


def _dimension(label: str = "Radiator length", **overrides: object) -> AsBuiltDimension:
    values: dict[str, object] = {
        "id": uuid4(),
        "label": label,
        "design_value_m": 20.0,
        "actual_value_m": 19.9,
        "notes": "Cut slightly long",
    }
    values.update(overrides)
    return AsBuiltDimension(**values)  # type: ignore[arg-type]


def test_record_validates_labels_values_and_notes() -> None:
    with pytest.raises(ValueError, match="label"):
        _dimension("   ")
    with pytest.raises(ValueError, match="design_value"):
        _dimension(design_value_m=-1.0)
    with pytest.raises(ValueError, match="notes"):
        _dimension(notes="x" * 1_001)


def test_record_rejects_duplicate_ids_and_checklist_keys() -> None:
    dimension = _dimension()
    with pytest.raises(ValueError, match="duplicate"):
        ConstructionRecord(dimensions=(dimension, dimension))
    with pytest.raises(ValueError, match="duplicate"):
        ConstructionRecord(
            checklist=(
                ConstructionChecklistItem("check_dimensions"),
                ConstructionChecklistItem("check_dimensions", checked=True),
            )
        )


def test_record_reports_checked_keys() -> None:
    record = ConstructionRecord(
        checklist=(
            ConstructionChecklistItem("check_dimensions", checked=True),
            ConstructionChecklistItem("measure_swr"),
        )
    )

    assert record.checked_keys() == frozenset({"check_dimensions"})


def test_project_stores_and_clears_the_construction_record(
    sample_project: Project,
) -> None:
    record = ConstructionRecord(
        as_built_notes="Built in the back yard",
        dimensions=(_dimension(),),
        checklist=(ConstructionChecklistItem("measure_swr", checked=True),),
    )

    project = sample_project.with_construction_record(
        record,
        updated_at=sample_project.updated_at,
    )
    assert project.construction_record == record

    project = project.with_construction_record(
        None,
        updated_at=sample_project.updated_at,
    )
    assert project.construction_record is None


def test_dimension_replacement_keeps_the_record_immutable() -> None:
    dimension = _dimension()
    record = ConstructionRecord(dimensions=(dimension,))
    updated = replace(dimension, actual_value_m=20.1)

    assert record.dimensions[0].actual_value_m == 19.9
    assert updated.actual_value_m == 20.1
