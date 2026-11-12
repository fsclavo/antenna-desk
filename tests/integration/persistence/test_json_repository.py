# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import gzip
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
    data = path.read_bytes()
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    value = json.loads(data.decode("utf-8"))
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


def test_round_trip_preserves_vertical_top_hat(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    from antennadesk.domain.antennas.vertical import VerticalParameters
    from antennadesk.domain.projects.project import DesignVariant

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=9.0,
        base_height_m=0.25,
        radial_count=14,
        radial_length_m=12.863,
        loading_coil_enabled=True,
        loading_coil_inductance_h=10e-6,
        top_hat_enabled=True,
        top_hat_radius_m=0.5,
        top_hat_wire_count=4,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Vertical",
        antenna_type="vertical",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )
    project = replace(sample_project, designs=(design,))
    path = tmp_path / "vertical.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded.designs[0].parameters == parameters
    assert loaded.designs[0].antenna == design.antenna


def test_round_trip_preserves_design_band_plan(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from antennadesk.domain.design.band_plan import BandPlan, BandSelection
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    bands = []
    for band_id in ("40m", "20m"):
        band = amateur_band_by_id(band_id)
        assert band is not None
        bands.append(BandSelection(band, points=21))
    plan = BandPlan(tuple(bands))
    design = sample_project.designs[0].with_band_plan(plan)
    project = sample_project.with_design(design, updated_at=sample_project.updated_at)
    path = tmp_path / "band-plan.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded.designs[0].band_plan == plan


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
    original_bytes = path.read_bytes()

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

    assert path.read_bytes() == original_bytes
    assert list(tmp_path.glob(".*.tmp")) == []


def test_saved_file_is_losslessly_compressed(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "compressed.antennadesk"

    repository.save(sample_project, path)

    assert path.read_bytes().startswith(b"\x1f\x8b")
    assert repository.serialized_size(sample_project) == path.stat().st_size
    assert repository.load(path) == sample_project


def test_plain_json_project_still_loads(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "legacy.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    _write_json(path, document)

    assert repository.load(path) == sample_project


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
        SourceResult,
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
        pattern_frequencies_hz=(6_900_000.0,),
        feed_line=FeedLine(
            characteristic_impedance_ohm=75.0,
            length_m=30.0,
            velocity_factor=0.8,
            matched_loss_db_per_100m=1.5,
        ),
        feed_transformer_ratio=4.0,
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
            source_results=(
                SourceResult(
                    wire_id="radiator",
                    offset_m=10.0,
                    tag=1,
                    segment=11,
                    amplitude=1.0,
                    phase_deg=0.0,
                    voltage_v=complex(1.0, 0.0),
                    current_a=complex(0.1, -0.05),
                    impedance_ohm=complex(60.0, -10.0),
                    power_w=0.001,
                ),
            ),
            power_budget=PowerBudget(0.001, 0.0009, 0.0001, 0.0, 90.0),
            directivity_db=2.20,
            realized_gain_db=1.85,
            mismatch_loss_db=0.20,
            feed_line_loss_db=0.45,
            network_loss_db=0.05,
            balun_loss_db=0.03,
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
    assert run.result.frequencies[0].directivity_db == pytest.approx(2.20)
    assert run.result.frequencies[0].realized_gain_db == pytest.approx(1.85)
    assert run.result.frequencies[0].mismatch_loss_db == pytest.approx(0.20)
    assert run.result.frequencies[0].feed_line_loss_db == pytest.approx(0.45)
    assert run.result.frequencies[0].network_loss_db == pytest.approx(0.05)
    assert run.result.frequencies[0].balun_loss_db == pytest.approx(0.03)
    assert run.result.frequencies[0].source_results[0].wire_id == "radiator"
    assert run.result.frequencies[0].source_results[0].impedance_ohm == complex(60.0, -10.0)
    assert run.result.frequencies[0].source_results[0].power_w == pytest.approx(0.001)
    assert math.isinf(run.result.frequencies[1].swr)
    assert run.result.spec.segmentation.wire_segments == (("radiator", 21),)
    assert run.result.spec.feed_line == FeedLine(
        characteristic_impedance_ohm=75.0,
        length_m=30.0,
        velocity_factor=0.8,
        matched_loss_db_per_100m=1.5,
    )
    assert run.result.spec.feed_transformer_ratio == 4.0
    assert run.result.spec.pattern_frequencies_hz == (6_900_000.0,)


def test_serialized_size_matches_written_file(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"

    repository.save(sample_project, path)

    assert repository.serialized_size(sample_project) == path.stat().st_size


def test_prepared_payload_can_be_written_without_recompression(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "prepared.antennadesk"

    payload = repository.prepare_payload(sample_project)
    repository.write_payload(path, payload)

    assert path.read_bytes() == payload
    assert repository.serialized_size(sample_project) == len(payload)


def test_round_trip_with_a_project_feed_line(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from antennadesk.domain.antennas.matching_network import MatchingNetworkPosition

    line = FeedLine(
        characteristic_impedance_ohm=75.0,
        length_m=30.0,
        velocity_factor=0.8,
        matched_loss_db_per_100m=1.5,
    )
    project = replace(
        sample_project,
        feed_line=line,
        matching_network_position=MatchingNetworkPosition.SHACK,
    )
    path = tmp_path / "feed-line.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded.feed_line == line
    assert loaded.matching_network_position is MatchingNetworkPosition.SHACK
    assert loaded == project


def test_round_trip_with_installation_profiles(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    from antennadesk.domain.environment.ground import FREE_SPACE
    from antennadesk.domain.projects.installation import (
        InstallationProfile,
        InstallationSupport,
    )

    home = InstallationProfile(
        id=uuid4(),
        name="Home",
        available_height_m=12.0,
        available_width_m=30.0,
        orientation_deg=90.0,
        ground=FREE_SPACE,
        support=InstallationSupport.MAST,
        notes="Back yard",
        image_reference="site.png",
    )
    portable = InstallationProfile(
        id=uuid4(),
        name="Portable",
        available_height_m=4.0,
        support=InstallationSupport.PORTABLE,
    )
    project = replace(
        sample_project,
        installation_profiles=(home, portable),
        active_installation_profile_id=portable.id,
    )
    path = tmp_path / "installation.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded == project
    assert loaded.active_installation_profile == portable


def test_round_trip_preserves_band_analysis_metadata(
    repository: JsonProjectRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )

    batch_id = uuid4()
    project = RecordSimulationRun().execute(
        RecordSimulationRunCommand(
            project=sample_project,
            design_id=sample_project.designs[0].id,
            result=_rich_result(),
            created_at=sample_project.updated_at,
            band_id="40m",
            batch_id=batch_id,
        )
    )
    path = tmp_path / "with-band-run.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded == project
    run = loaded.simulation_runs[0]
    assert run.band_id == "40m"
    assert run.batch_id == batch_id
    analysis = loaded.latest_band_analysis(sample_project.designs[0].id)
    assert analysis is not None
    assert analysis.bands[0].band.name == "40m"
