# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project-level site ground profile validation."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from antennadesk.domain.environment.site_ground import (
    MAX_SITE_LABEL_LENGTH,
    MAX_SITE_NOTES_LENGTH,
    EdgeShape,
    SiteGroundProfile,
)
from antennadesk.domain.projects.project import Project


def _profile(**overrides: object) -> SiteGroundProfile:
    values: dict[str, object] = {
        "second_medium_relative_permittivity": 81.0,
        "second_medium_conductivity_s_per_m": 5.0,
        "edge_distance_m": 50.0,
        "edge_shape": EdgeShape.CIRCULAR,
        "edge_height_m": 0.0,
        "label": "Coastal cliff",
        "notes": "Second medium is salt water.",
    }
    values.update(overrides)
    return SiteGroundProfile(**values)  # type: ignore[arg-type]


def test_site_ground_profile_accepts_the_bounded_fields() -> None:
    profile = _profile()

    assert profile.edge_shape is EdgeShape.CIRCULAR
    assert profile.is_far_field_only is True
    assert profile.label == "Coastal cliff"


def test_site_ground_profile_strips_label_and_notes() -> None:
    profile = _profile(label="  Cliff  ", notes="  note  ")

    assert profile.label == "Cliff"
    assert profile.notes == "note"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("second_medium_relative_permittivity", 0.9),
        ("second_medium_conductivity_s_per_m", 0.0),
        ("edge_distance_m", -1.0),
        ("edge_height_m", -1.0),
    ],
)
def test_site_ground_profile_rejects_invalid_numbers(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        _profile(**{field: value})


def test_site_ground_profile_rejects_overlong_text() -> None:
    with pytest.raises(ValueError, match="site label"):
        _profile(label="x" * (MAX_SITE_LABEL_LENGTH + 1))
    with pytest.raises(ValueError, match="site notes"):
        _profile(notes="x" * (MAX_SITE_NOTES_LENGTH + 1))


def test_project_with_site_ground_is_immutable(sample_project: Project) -> None:
    profile = _profile()
    updated = sample_project.with_site_ground(
        profile,
        updated_at=datetime(2026, 11, 24, tzinfo=UTC),
    )

    assert sample_project.site_ground is None
    assert updated.site_ground == profile
    assert updated is not sample_project
