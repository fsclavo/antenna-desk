# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json
import math
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.result import SimulationResult
from antennadesk.persistence import json_repository
from antennadesk.persistence.constants import (
    MAX_PROJECT_SIZE_BYTES,
    PROJECT_FORMAT,
    SCHEMA_VERSION,
)
from antennadesk.persistence.errors import (
    ProjectFormatError,
    ProjectTooLargeError,
    UnsupportedSchemaVersion,
)
from antennadesk.persistence.json_repository import JsonProjectRepository


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(json.dumps(document), encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_round_trip(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)

    loaded = repository.load(path)

    assert loaded == sample_project


def test_saved_document_envelope(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)

    document = _load_json(path)

    assert document["format"] == PROJECT_FORMAT
    assert document["schema_version"] == SCHEMA_VERSION
    assert document["project"]["name"] == "40 m dipole"
    assert document["project"]["simulation_runs"] == []
    design = document["project"]["designs"][0]
    assert design["antenna_type"] == "wire_dipole"
    assert design["parameters"]["total_length_m"] == pytest.approx(20.0)
    assert design["antenna"]["wires"][0]["start"]["x_m"] == pytest.approx(-10.0)


def test_atomic_save_keeps_original_on_failure(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    original_text = path.read_text(encoding="utf-8")

    design = sample_project.designs[0]
    modified = sample_project.with_design(
        design.with_parameters(design.parameters.with_length(19.5)),
        updated_at=sample_project.updated_at + timedelta(hours=1),
    )

    def failing_replace(source: object, destination: object) -> None:
        raise OSError("simulated failure")

    monkeypatch.setattr(json_repository.os, "replace", failing_replace)

    with pytest.raises(ProjectFormatError, match="could not save"):
        repository.save(modified, path)

    assert path.read_text(encoding="utf-8") == original_text
    assert list(tmp_path.glob(".*.tmp")) == []


def test_unknown_format_is_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["format"] = "something-else"
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="format"):
        repository.load(path)


def test_future_schema_is_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["schema_version"] = SCHEMA_VERSION + 1
    _write_json(path, document)

    with pytest.raises(UnsupportedSchemaVersion):
        repository.load(path)


def test_missing_schema_version_is_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    del document["schema_version"]
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="schema_version"):
        repository.load(path)


def test_extra_fields_are_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["project"]["unexpected"] = True
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="invalid project file"):
        repository.load(path)


def test_invalid_geometry_is_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    wire = document["project"]["designs"][0]["antenna"]["wires"][0]
    wire["end"] = dict(wire["start"])
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="non-zero length"):
        repository.load(path)


def test_non_finite_coordinates_are_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["project"]["designs"][0]["antenna"]["wires"][0]["start"]["x_m"] = float("nan")
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="invalid project file"):
        repository.load(path)


def test_oversized_file_is_rejected(
    repository: JsonProjectRepository,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    path.write_bytes(b" " * (MAX_PROJECT_SIZE_BYTES + 1))

    with pytest.raises(ProjectTooLargeError):
        repository.load(path)


def test_missing_file_is_rejected(
    repository: JsonProjectRepository,
    tmp_path: Path,
) -> None:
    with pytest.raises(ProjectFormatError, match="not found"):
        repository.load(tmp_path / "missing.antennadesk")


def test_save_to_missing_directory_is_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing" / "dipole.antennadesk"

    with pytest.raises(ProjectFormatError, match="directory"):
        repository.save(sample_project, path)


def test_saved_file_is_stable_across_dataclass_replacement(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)

    unchanged = replace(sample_project)
    loaded = repository.load(path)

    assert loaded == unchanged


def test_invalid_json_is_rejected(
    repository: JsonProjectRepository,
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid.antennadesk"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ProjectFormatError, match="invalid project JSON"):
        repository.load(path)


def test_non_object_root_is_rejected(
    repository: JsonProjectRepository,
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid.antennadesk"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ProjectFormatError, match="root must be a JSON object"):
        repository.load(path)


def test_invalid_utf8_is_rejected(
    repository: JsonProjectRepository,
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid.antennadesk"
    path.write_bytes(b"\xff\xfe\xfd")

    with pytest.raises(ProjectFormatError, match="UTF-8"):
        repository.load(path)


def test_unsupported_antenna_type_is_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["project"]["designs"][0]["antenna_type"] = "unsupported_type"
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="unsupported antenna type"):
        repository.load(path)


def test_naive_timestamp_is_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["project"]["created_at"] = "2026-10-29T12:00:00"
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="timezone-aware"):
        repository.load(path)


def test_invalid_ground_is_rejected(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["project"]["designs"][0]["parameters"]["ground"] = {"kind": "finite"}
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="invalid project file"):
        repository.load(path)


def _rich_result() -> SimulationResult:
    from datetime import UTC, datetime

    from antennadesk.domain.common.validation import Diagnostic, Severity
    from antennadesk.domain.simulation.far_field import FarFieldRequest
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.result import (
        CurrentSample,
        FarFieldPoint,
        FrequencyResult,
        PowerBudget,
        SimulationStatus,
    )
    from antennadesk.domain.simulation.segmentation import SegmentationPolicy
    from antennadesk.domain.simulation.solver import SolverMetadata
    from antennadesk.domain.simulation.spec import SimulationSpec

    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_100_000.0, 2),
        segmentation=SegmentationPolicy(
            wire_segments=(("radiator", 21),),
        ),
        far_field=FarFieldRequest(),
        feed_line=FeedLine(
            characteristic_impedance_ohm=75.0,
            length_m=30.0,
            velocity_factor=0.8,
            matched_loss_db_per_100m=1.5,
        ),
    )
    current = CurrentSample(
        segment=1,
        tag=1,
        x_m=-1.0,
        y_m=0.0,
        z_m=8.0,
        length_m=1.0,
        current_a=complex(0.1, -0.05),
        magnitude_a=0.1118,
        phase_deg=-26.565,
    )
    far_field = FarFieldPoint(
        theta_deg=0.0,
        phi_deg=0.0,
        gain_vertical_db=2.14,
        gain_horizontal_db=None,
        gain_total_db=2.14,
        axial_ratio=0.0,
        tilt_deg=0.0,
        polarization="LINEAR",
        e_theta_magnitude_v_per_m=0.67,
        e_theta_phase_deg=-122.0,
        e_phi_magnitude_v_per_m=0.0,
        e_phi_phase_deg=0.0,
    )
    frequencies = (
        FrequencyResult(
            frequency_hz=6_900_000.0,
            feed_tag=1,
            feed_segment=11,
            impedance_ohm=complex(60.0, -10.0),
            swr=2.0,
            input_power_w=0.001,
            currents=(current,),
            far_field=(far_field,),
            power_budget=PowerBudget(0.001, 0.0009, 0.0001, 0.0, 90.0),
        ),
        FrequencyResult(
            frequency_hz=7_100_000.0,
            feed_tag=1,
            feed_segment=11,
            impedance_ohm=complex(70.0, 0.0),
            swr=math.inf,
            input_power_w=0.002,
        ),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3", executable="nec2c"),
        frequencies=frequencies,
        diagnostics=(
            Diagnostic(
                code="test.warning",
                severity=Severity.WARNING,
                message="test warning",
                field="test",
            ),
        ),
        raw_input="GW 1 21 ...\n",
        raw_output="FREQUENCY ...\n",
        stderr="",
        duration_s=0.25,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def test_round_trip_with_a_simulation_run(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )

    project = RecordSimulationRun().execute(
        RecordSimulationRunCommand(
            project=sample_project,
            design_id=sample_project.designs[0].id,
            result=_rich_result(),
            created_at=sample_project.updated_at,
        )
    )
    path = tmp_path / "with-run.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded == project
    assert len(loaded.simulation_runs) == 1
    run = loaded.simulation_runs[0]
    assert run.design_id == sample_project.designs[0].id
    assert run.result.raw_output == "FREQUENCY ...\n"
    assert run.result.frequencies[0].impedance_ohm == complex(60.0, -10.0)
    assert math.isinf(run.result.frequencies[1].swr)
    assert run.result.spec.segmentation.wire_segments == (("radiator", 21),)
    assert run.result.spec.feed_line == FeedLine(
        characteristic_impedance_ohm=75.0,
        length_m=30.0,
        velocity_factor=0.8,
        matched_loss_db_per_100m=1.5,
    )


def test_serialized_size_matches_written_file(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"

    repository.save(sample_project, path)

    assert repository.serialized_size(sample_project) == path.stat().st_size


def test_round_trip_with_a_project_feed_line(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    line = FeedLine(
        characteristic_impedance_ohm=75.0,
        length_m=30.0,
        velocity_factor=0.8,
        matched_loss_db_per_100m=1.5,
    )
    project = replace(sample_project, feed_line=line)
    path = tmp_path / "feed-line.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded.feed_line == line
    assert loaded == project
