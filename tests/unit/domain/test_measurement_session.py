# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measurement sessions and their project links."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from antennadesk.application.use_cases.delete_design_variant import (
    DeleteDesignVariant,
    DeleteDesignVariantCommand,
)
from antennadesk.domain.measurement import (
    MAX_MEASUREMENT_SESSION_NAME_LENGTH,
    Measurement,
    MeasurementPoint,
    MeasurementSession,
)
from antennadesk.domain.projects.project import Project


def _session(**overrides: object) -> MeasurementSession:
    values: dict[str, object] = {
        "id": uuid4(),
        "name": "Back yard",
        "created_at": datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
        "location": "Back yard",
        "conditions": "Dry ground, light wind",
        "notes": "Before trimming the radiator",
    }
    values.update(overrides)
    return MeasurementSession(**values)  # type: ignore[arg-type]


def _measurement(session_id: UUID | None = None) -> Measurement:
    return Measurement(
        id=uuid4(),
        name="Field sweep",
        created_at=datetime(2026, 11, 12, 15, 5, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),),
        session_id=session_id,
    )


def test_session_trims_its_name_and_requires_utc() -> None:
    session = _session(name="  Before tuning  ")

    assert session.name == "Before tuning"

    with pytest.raises(ValueError, match="name"):
        _session(name=" ")
    with pytest.raises(ValueError, match="at most"):
        _session(name="x" * (MAX_MEASUREMENT_SESSION_NAME_LENGTH + 1))
    with pytest.raises(ValueError, match="timezone-aware"):
        _session(created_at=datetime(2026, 11, 12, 15, 0))


def test_project_adds_updates_and_removes_a_session(sample_project: Project) -> None:
    session = _session(design_id=sample_project.designs[0].id)
    measurement = _measurement(session.id)
    project = sample_project.with_measurement_session(
        session,
        updated_at=sample_project.updated_at + timedelta(hours=1),
    ).with_measurement(
        measurement,
        updated_at=sample_project.updated_at + timedelta(hours=2),
    )

    assert project.measurement_session_by_id(session.id) == session
    assert project.measurements_for_session(session.id) == (measurement,)
    assert project.unassigned_measurements() == ()

    updated = replace(session, name="After tuning", notes="Trimmed")
    project = project.with_updated_measurement_session(
        updated,
        updated_at=sample_project.updated_at + timedelta(hours=3),
    )
    assert project.measurement_sessions == (updated,)

    project = project.without_measurement_session(
        session.id,
        updated_at=sample_project.updated_at + timedelta(hours=4),
    )
    assert project.measurement_sessions == ()
    assert project.measurements[0].session_id is None
    assert project.unassigned_measurements() == (project.measurements[0],)


def test_project_rejects_unknown_session_operations(sample_project: Project) -> None:
    session = _session()

    with pytest.raises(KeyError, match="unknown measurement session"):
        sample_project.with_updated_measurement_session(
            session,
            updated_at=sample_project.updated_at,
        )
    with pytest.raises(KeyError, match="unknown measurement session"):
        sample_project.without_measurement_session(
            session.id,
            updated_at=sample_project.updated_at,
        )
    with pytest.raises(KeyError, match="unknown measurement session"):
        sample_project.measurement_session_by_id(session.id)


def test_project_rejects_a_measurement_with_an_unknown_session(
    sample_project: Project,
) -> None:
    with pytest.raises(ValueError, match="unknown session"):
        sample_project.with_measurement(
            _measurement(uuid4()),
            updated_at=sample_project.updated_at,
        )


def test_project_rejects_a_session_with_an_unknown_design(
    sample_project: Project,
) -> None:
    with pytest.raises(ValueError, match="unknown design"):
        sample_project.with_measurement_session(
            _session(design_id=uuid4()),
            updated_at=sample_project.updated_at,
        )


def test_project_rejects_duplicate_session_ids(sample_project: Project) -> None:
    session = _session()
    project = sample_project.with_measurement_session(
        session,
        updated_at=sample_project.updated_at,
    )

    with pytest.raises(ValueError, match="duplicate measurement session id"):
        project.with_measurement_session(
            replace(session, name="Another session"),
            updated_at=sample_project.updated_at,
        )


def test_deleting_a_design_detaches_its_sessions(sample_project: Project) -> None:
    design = sample_project.designs[0]
    session = _session(design_id=design.id)
    project = sample_project.with_measurement_session(
        session,
        updated_at=sample_project.updated_at,
    )
    second = replace(
        design,
        id=uuid4(),
        name="Second",
    )
    project = project.with_design(second, updated_at=sample_project.updated_at)

    deleted = DeleteDesignVariant().execute(
        DeleteDesignVariantCommand(
            project=project,
            design_id=design.id,
            updated_at=sample_project.updated_at + timedelta(hours=1),
        )
    )

    assert deleted.measurement_sessions[0].design_id is None
    assert deleted.measurements == project.measurements
