# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Installation profile validation and project operations."""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from uuid import uuid4

import pytest

from antennadesk.domain.common.validation import DomainValidationError
from antennadesk.domain.environment.ground import FREE_SPACE, GroundModel
from antennadesk.domain.projects.installation import (
    InstallationProfile,
    InstallationSupport,
)
from antennadesk.domain.projects.project import Project


def _profile(name: str = "Home", **overrides: object) -> InstallationProfile:
    values: dict[str, object] = {
        "id": uuid4(),
        "name": name,
        "available_height_m": 12.0,
        "available_width_m": 30.0,
        "orientation_deg": 90.0,
        "ground": FREE_SPACE,
        "support": InstallationSupport.MAST,
        "notes": "Back yard",
    }
    values.update(overrides)
    return InstallationProfile(**values)  # type: ignore[arg-type]


def test_profile_normalizes_name_orientation_and_support() -> None:
    profile = _profile("  Home  ", orientation_deg=-10.0, support="tree")

    assert profile.name == "Home"
    assert profile.orientation_deg == pytest.approx(350.0)
    assert profile.support is InstallationSupport.TREE


@pytest.mark.parametrize("field", ["available_height_m", "available_width_m"])
def test_profile_rejects_non_positive_limits(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        _profile(**{field: 0.0})


def test_profile_rejects_an_empty_name_and_long_notes() -> None:
    with pytest.raises(ValueError, match="name"):
        _profile("   ")
    with pytest.raises(ValueError, match="notes"):
        _profile(notes="x" * 4_001)


def test_project_adds_replaces_activates_and_removes_profiles(
    sample_project: Project,
) -> None:
    first = _profile("Home")
    second = _profile("Portable", ground=GroundModel.perfect())

    project = sample_project.with_installation_profile(
        first,
        updated_at=sample_project.updated_at,
    )
    assert project.active_installation_profile == first

    project = project.with_installation_profile(
        second,
        make_active=False,
        updated_at=sample_project.updated_at + timedelta(seconds=1),
    )
    assert project.active_installation_profile == first
    assert project.installation_profile_by_id(second.id) == second

    project = project.with_active_installation_profile(
        second.id,
        updated_at=sample_project.updated_at + timedelta(seconds=2),
    )
    assert project.active_installation_profile == second

    renamed = replace(first, name="Home site")
    project = project.with_installation_profile(
        renamed,
        updated_at=sample_project.updated_at + timedelta(seconds=3),
    )
    assert project.installation_profile_by_id(first.id) == renamed
    assert len(project.installation_profiles) == 2

    project = project.without_installation_profile(
        second.id,
        updated_at=sample_project.updated_at + timedelta(seconds=4),
    )
    assert project.active_installation_profile == renamed
    assert len(project.installation_profiles) == 1

    project = project.without_installation_profile(
        first.id,
        updated_at=sample_project.updated_at + timedelta(seconds=5),
    )
    assert project.installation_profiles == ()
    assert project.active_installation_profile is None


def test_project_rejects_duplicate_profiles_and_unknown_active(
    sample_project: Project,
) -> None:
    profile = _profile()
    with pytest.raises(DomainValidationError):
        replace(
            sample_project,
            installation_profiles=(profile, profile),
            active_installation_profile_id=profile.id,
        )
    with pytest.raises(DomainValidationError):
        replace(
            sample_project,
            installation_profiles=(profile,),
            active_installation_profile_id=uuid4(),
        )
    with pytest.raises(DomainValidationError):
        replace(
            sample_project,
            installation_profiles=(profile, _profile("Home")),
            active_installation_profile_id=profile.id,
        )


def test_with_installation_state_replaces_the_whole_set(sample_project: Project) -> None:
    first = _profile("Home")
    second = _profile("Field day", support=InstallationSupport.PORTABLE)

    project = sample_project.with_installation_state(
        (first, second),
        second.id,
        updated_at=sample_project.updated_at,
    )

    assert project.installation_profiles == (first, second)
    assert project.active_installation_profile == second
