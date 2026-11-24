# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Autosave recovery store behavior."""

from __future__ import annotations

import os
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from antennadesk.application.project_payload import PreparedProject
from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.run import SimulationRun
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.persistence.container import ProjectContainerRepository
from antennadesk.persistence.errors import ProjectFormatError
from antennadesk.ui.recovery import (
    MAX_RECOVERY_PAYLOAD_BYTES,
    AutosaveRecovery,
    RecoveryTooLargeError,
)


def test_recovery_round_trip_and_clear(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", ProjectContainerRepository())

    recovery.save(
        sample_project,
        original_path=tmp_path / "source.antennadesk",
        dirty=True,
    )

    assert recovery.project_path.is_file()
    assert recovery.metadata_path.is_file()
    snapshot = recovery.load()
    assert snapshot is not None
    assert snapshot.project == sample_project
    assert snapshot.original_path == tmp_path / "source.antennadesk"
    assert snapshot.dirty is True
    assert snapshot.saved_at

    recovery.clear()
    assert recovery.load() is None
    assert not recovery.project_path.exists()
    assert not recovery.metadata_path.exists()


def _run(sample_project: Project) -> SimulationRun:
    result = SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="test"),
        frequencies=(
            FrequencyResult(
                frequency_hz=7_100_000.0,
                feed_tag=1,
                feed_segment=1,
                impedance_ohm=complex(50.0, 0.0),
                swr=1.0,
                input_power_w=1.0,
            ),
        ),
    )
    return SimulationRun(
        id=uuid4(),
        design_id=sample_project.designs[0].id,
        created_at=datetime(2026, 11, 19, tzinfo=UTC),
        result=result,
    )


def test_recovery_snapshot_excludes_simulation_runs(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project = replace(sample_project, simulation_runs=(_run(sample_project),))
    recovery = AutosaveRecovery(tmp_path / "recovery", ProjectContainerRepository())

    recovery.save(project, original_path=None, dirty=True)

    snapshot = recovery.load()
    assert snapshot is not None
    assert snapshot.project.simulation_runs == ()
    assert snapshot.project.designs == project.designs


def test_oversized_design_snapshot_is_rejected_without_writing(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    class OversizeRepository:
        def prepare_payload(self, project: Project) -> PreparedProject:
            del project
            return PreparedProject(
                b"x" * (MAX_RECOVERY_PAYLOAD_BYTES + 1),
                entry_count=1,
                expanded_bytes=MAX_RECOVERY_PAYLOAD_BYTES + 1,
            )

        def write_payload(self, path: Path, payload: PreparedProject) -> None:
            del path, payload
            raise AssertionError("oversized payload must not be written")

    recovery = AutosaveRecovery(tmp_path / "recovery", OversizeRepository())  # type: ignore[arg-type]

    with pytest.raises(RecoveryTooLargeError):
        recovery.save(sample_project, original_path=None, dirty=True)
    assert not recovery.project_path.exists()


def test_corrupt_metadata_falls_back_to_safe_defaults(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", ProjectContainerRepository())
    recovery.save(sample_project, original_path=None, dirty=True)
    recovery.metadata_path.write_text("{bad json", encoding="utf-8")

    snapshot = recovery.load()

    assert snapshot is not None
    assert snapshot.project == sample_project
    assert snapshot.original_path is None
    assert snapshot.dirty is True


def test_corrupt_project_payload_raises(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", ProjectContainerRepository())
    recovery.save(sample_project, original_path=None, dirty=True)
    recovery.project_path.write_bytes(b"not a project")

    with pytest.raises(ProjectFormatError):
        recovery.load()


@pytest.mark.skipif(
    os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
    reason="directory permissions are not enforced on Windows or as root",
)
def test_read_only_recovery_directory_is_reported(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    directory = tmp_path / "recovery"
    directory.mkdir()
    directory.chmod(0o500)
    recovery = AutosaveRecovery(directory, ProjectContainerRepository())
    try:
        with pytest.raises((OSError, ProjectFormatError)):
            recovery.save(sample_project, original_path=None, dirty=True)
    finally:
        directory.chmod(0o700)
