# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import gzip
import hashlib
import io
import json
import math
import zipfile
import zlib
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from antennadesk.application.project_payload import PreparedProject
from antennadesk.domain.antennas.feed_line import FeedLine
from antennadesk.domain.environment.site_ground import EdgeShape, SiteGroundProfile
from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.result import SimulationResult
from antennadesk.persistence import container as container_module
from antennadesk.persistence.constants import (
    MAX_PROJECT_SIZE_BYTES,
    PROJECT_FORMAT,
    PROJECT_SIZE_WARNING_BYTES,
    SCHEMA_VERSION,
)
from antennadesk.persistence.container import ProjectContainerRepository
from antennadesk.persistence.errors import (
    ProjectFormatError,
    ProjectTooLargeError,
    UnsupportedSchemaVersion,
)


def _read_entries(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {info.filename: archive.read(info) for info in archive.infolist()}


def _write_entries(path: Path, entries: dict[str, bytes]) -> None:
    with zipfile.ZipFile(
        path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, entries[name])


def _write_container(path: Path, entries: dict[str, bytes]) -> None:
    manifest = json.loads(entries["manifest.json"])
    preliminary = io.BytesIO()
    with zipfile.ZipFile(
        preliminary,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:
        for name in sorted(entries):
            if name == "manifest.json":
                continue
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, entries[name])
    with zipfile.ZipFile(preliminary) as archive:
        compressed = {info.filename: info.compress_size for info in archive.infolist()}
    for entry in manifest["entries"]:
        data = entries[entry["path"]]
        entry["uncompressed_bytes"] = len(data)
        entry["compressed_bytes"] = compressed[entry["path"]]
        entry["crc32"] = zlib.crc32(data) & 0xFFFFFFFF
        entry["sha256"] = hashlib.sha256(data).hexdigest()
    entries["manifest.json"] = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    _write_entries(path, entries)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(_read_entries(path)["project.json"])
    assert isinstance(value, dict)
    return value


def _write_json(path: Path, document: dict[str, Any]) -> None:
    entries = _read_entries(path)
    entries["project.json"] = json.dumps(document, separators=(",", ":")).encode("utf-8")
    _write_container(path, entries)


def _load_design(path: Path, index: int = 0) -> dict[str, Any]:
    entries = _read_entries(path)
    names = sorted(name for name in entries if name.startswith("designs/"))
    value = json.loads(entries[names[index]])
    assert isinstance(value, dict)
    return value


def _write_design(path: Path, document: dict[str, Any], index: int = 0) -> None:
    entries = _read_entries(path)
    names = sorted(name for name in entries if name.startswith("designs/"))
    entries[names[index]] = json.dumps(document, separators=(",", ":")).encode("utf-8")
    _write_container(path, entries)


def test_round_trip(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)

    loaded = repository.load(path)

    assert loaded == sample_project


def test_round_trip_preserves_vertical_top_hat(
    repository: ProjectContainerRepository,
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
        radial_droop_deg=0.5,
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
    repository: ProjectContainerRepository,
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


def _manifest(path: Path) -> dict[str, Any]:
    value = json.loads(_read_entries(path)["manifest.json"])
    assert isinstance(value, dict)
    return value


def _write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    entries = _read_entries(path)
    entries["manifest.json"] = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    _write_entries(path, entries)


def test_saved_container_envelope(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)

    manifest = _manifest(path)
    document = _load_json(path)
    design = _load_design(path)

    assert manifest["format"] == "antennadesk.project"
    assert manifest["container_version"] == 1
    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["project_name"] == "40 m dipole"
    assert document["format"] == PROJECT_FORMAT
    assert document["schema_version"] == SCHEMA_VERSION
    assert "designs" not in document["project"]
    assert "simulation_runs" not in document["project"]
    assert design["design"]["antenna_type"] == "wire_dipole"
    assert design["design"]["parameters"]["total_length_m"] == pytest.approx(20.0)
    assert design["design"]["antenna"]["wires"][0]["start"]["x_m"] == pytest.approx(-10.0)


def test_atomic_save_keeps_original_on_failure(
    repository: ProjectContainerRepository,
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

    monkeypatch.setattr(container_module.os, "replace", failing_replace)

    with pytest.raises(ProjectFormatError, match="could not save"):
        repository.save(modified, path)

    assert path.read_bytes() == original_bytes
    assert list(tmp_path.glob(".*.tmp")) == []


def test_saved_container_is_a_deterministic_zip(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.antennadesk"
    second = tmp_path / "second.antennadesk"

    repository.save(sample_project, first)
    repository.save(sample_project, second)

    assert first.read_bytes().startswith(b"PK")
    assert first.read_bytes() == second.read_bytes()
    assert repository.serialized_size(sample_project) == first.stat().st_size
    assert repository.load(first) == sample_project


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(gzip.compress(b'{"format":"antennadesk-project"}'), id="gzip"),
        pytest.param(b'{"format":"antennadesk-project"}', id="plain-json"),
    ],
)
def test_legacy_project_formats_are_rejected(
    repository: ProjectContainerRepository,
    tmp_path: Path,
    payload: bytes,
) -> None:
    path = tmp_path / "legacy.antennadesk"
    path.write_bytes(payload)

    with pytest.raises(ProjectFormatError, match="legacy project format"):
        repository.load(path)


def test_prepare_rejects_total_expanded_over_limit(
    repository: ProjectContainerRepository,
    sample_project: Project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(container_module, "MAX_PROJECT_UNCOMPRESSED_BYTES", 256)

    with pytest.raises(ProjectTooLargeError, match="expanded") as error:
        repository.prepare_payload(sample_project)

    assert error.value.expanded is True
    assert error.value.size > 256


def test_prepare_rejects_container_over_limit(
    repository: ProjectContainerRepository,
    sample_project: Project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(container_module, "MAX_CONTAINER_BYTES", 16)

    with pytest.raises(ProjectTooLargeError, match="container is too large") as error:
        repository.prepare_payload(sample_project)

    assert error.value.expanded is False


def test_write_rejects_container_over_limit(
    repository: ProjectContainerRepository,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(container_module, "MAX_CONTAINER_BYTES", 16)
    path = tmp_path / "compressed.antennadesk"

    with pytest.raises(ProjectTooLargeError, match="container is too large"):
        repository.write_payload(path, PreparedProject(b"x" * 17, entry_count=1, expanded_bytes=17))

    assert not path.exists()


def test_write_rejects_a_non_container_payload(
    repository: ProjectContainerRepository,
    tmp_path: Path,
) -> None:
    path = tmp_path / "not-a-container.antennadesk"

    with pytest.raises(ProjectFormatError, match="not a valid ZIP"):
        repository.write_payload(
            path, PreparedProject(b"not a zip", entry_count=1, expanded_bytes=11)
        )

    assert not path.exists()


def test_save_never_writes_a_project_that_load_would_reject(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The save/load invariant: a successful save always reopens."""

    path = tmp_path / "invariant.antennadesk"
    monkeypatch.setattr(container_module, "MAX_PROJECT_UNCOMPRESSED_BYTES", 256)

    with pytest.raises(ProjectTooLargeError):
        repository.save(sample_project, path)
    assert not path.exists()

    monkeypatch.setattr(container_module, "MAX_PROJECT_UNCOMPRESSED_BYTES", 256 * 1024 * 1024)
    repository.save(sample_project, path)

    assert repository.load(path) == sample_project


def test_unknown_project_format_is_rejected(
    repository: ProjectContainerRepository,
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


def test_future_project_schema_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["schema_version"] = SCHEMA_VERSION + 1
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match="schema version"):
        repository.load(path)


def test_future_container_schema_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["schema_version"] = SCHEMA_VERSION + 1
    _write_manifest(path, manifest)

    with pytest.raises(UnsupportedSchemaVersion):
        repository.load(path)


def test_missing_schema_version_is_rejected(
    repository: ProjectContainerRepository,
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


def test_extra_project_fields_are_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    document = _load_json(path)
    document["project"]["unexpected"] = True
    _write_json(path, document)

    with pytest.raises(ProjectFormatError, match=r"invalid project entry project\.json"):
        repository.load(path)


def test_invalid_geometry_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    design = _load_design(path)
    wire = design["design"]["antenna"]["wires"][0]
    wire["end"] = dict(wire["start"])
    _write_design(path, design)

    with pytest.raises(ProjectFormatError, match="non-zero length"):
        repository.load(path)


def test_non_finite_coordinates_are_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    design = _load_design(path)
    design["design"]["antenna"]["wires"][0]["start"]["x_m"] = float("nan")
    _write_design(path, design)

    with pytest.raises(ProjectFormatError, match="invalid project entry designs/"):
        repository.load(path)


def test_oversized_file_is_rejected(
    repository: ProjectContainerRepository,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    path.write_bytes(b" " * (MAX_PROJECT_SIZE_BYTES + 1))

    with pytest.raises(ProjectTooLargeError):
        repository.load(path)


def test_missing_file_is_rejected(
    repository: ProjectContainerRepository,
    tmp_path: Path,
) -> None:
    with pytest.raises(ProjectFormatError, match="not found"):
        repository.load(tmp_path / "missing.antennadesk")


def test_save_to_missing_directory_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "missing" / "dipole.antennadesk"

    with pytest.raises(ProjectFormatError, match="directory"):
        repository.save(sample_project, path)


def test_saved_file_is_stable_across_dataclass_replacement(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)

    unchanged = replace(sample_project)
    loaded = repository.load(path)

    assert loaded == unchanged


def test_invalid_project_json_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    entries["project.json"] = b"{not json"
    _write_container(path, entries)

    with pytest.raises(ProjectFormatError, match=r"invalid project entry project\.json"):
        repository.load(path)


def test_non_object_project_root_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    entries["project.json"] = b"[]"
    _write_container(path, entries)

    with pytest.raises(ProjectFormatError, match=r"invalid project entry project\.json"):
        repository.load(path)


def test_invalid_project_utf8_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    entries["project.json"] = b"\xff\xfe\xfd"
    _write_container(path, entries)

    with pytest.raises(ProjectFormatError, match=r"invalid project entry project\.json"):
        repository.load(path)


def test_unsupported_antenna_type_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    design = _load_design(path)
    design["design"]["antenna_type"] = "unsupported_type"
    _write_design(path, design)

    with pytest.raises(ProjectFormatError, match="unsupported antenna type"):
        repository.load(path)


def test_naive_timestamp_is_rejected(
    repository: ProjectContainerRepository,
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
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    design = _load_design(path)
    design["design"]["parameters"]["ground"] = {"kind": "finite"}
    _write_design(path, design)

    with pytest.raises(ProjectFormatError, match="invalid project entry designs/"):
        repository.load(path)


def _rich_result() -> SimulationResult:
    from datetime import UTC, datetime

    from antennadesk.domain.antennas.balun import (
        SQUASH_PRACTICE_49_1_LOSS,
        LossPoint,
    )
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
            attenuation_points=(
                LossPoint(1_000_000.0, 1.0),
                LossPoint(100_000_000.0, 5.0),
            ),
            attenuation_source="test datasheet",
        ),
        transformer_loss=SQUASH_PRACTICE_49_1_LOSS,
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
            transformer_loss_db=0.30,
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


def test_round_trip_with_a_100_point_sweep(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )
    from antennadesk.domain.simulation.budget import estimate_compressed_project_bytes
    from antennadesk.domain.simulation.frequency import FrequencyPlan

    plan = FrequencyPlan.sweep(6_700_000.0, 7_500_000.0, 100)
    base = _rich_result()
    points = tuple(
        replace(
            base.frequencies[0],
            frequency_hz=frequency_hz,
            impedance_ohm=complex(60.0 + index * 0.1, -10.0 + index * 0.2),
            swr=1.0 + index * 0.01,
        )
        for index, frequency_hz in enumerate(plan.frequencies_hz)
    )
    result = replace(
        base,
        spec=replace(base.spec, frequency_plan=plan),
        frequencies=points,
    )
    project = RecordSimulationRun().execute(
        RecordSimulationRunCommand(
            project=sample_project,
            design_id=sample_project.designs[0].id,
            result=result,
            created_at=sample_project.updated_at,
        )
    )
    path = tmp_path / "with-100-points.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded == project
    assert len(loaded.simulation_runs[0].result.frequencies) == 100
    # About 4.4 MB compressed for 100 points at 725 segments, below the
    # 32 MB warning threshold.
    estimate = estimate_compressed_project_bytes(
        frequency_count=100,
        far_field_points_per_frequency=0,
        segment_count=725,
    )
    assert estimate < PROJECT_SIZE_WARNING_BYTES
    assert path.stat().st_size < PROJECT_SIZE_WARNING_BYTES


def test_round_trip_with_a_simulation_run(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )
    from antennadesk.domain.antennas.balun import (
        SQUASH_PRACTICE_49_1_LOSS,
        LossPoint,
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
    assert run.result.frequencies[0].transformer_loss_db == pytest.approx(0.30)
    assert run.result.spec.transformer_loss == SQUASH_PRACTICE_49_1_LOSS
    assert run.result.spec.feed_line is not None
    assert run.result.spec.feed_line.attenuation_points == (
        LossPoint(1_000_000.0, 1.0),
        LossPoint(100_000_000.0, 5.0),
    )
    assert run.result.spec.feed_line.attenuation_source == "test datasheet"
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
        attenuation_points=(
            LossPoint(1_000_000.0, 1.0),
            LossPoint(100_000_000.0, 5.0),
        ),
        attenuation_source="test datasheet",
    )
    assert run.result.spec.feed_transformer_ratio == 4.0
    assert run.result.spec.pattern_frequencies_hz == (6_900_000.0,)


def test_serialized_size_matches_written_file(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"

    repository.save(sample_project, path)

    assert repository.serialized_size(sample_project) == path.stat().st_size


def test_prepared_payload_can_be_written_without_recompression(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "prepared.antennadesk"

    payload = repository.prepare_payload(sample_project)
    repository.write_payload(path, payload)

    assert path.read_bytes() == payload.payload
    assert repository.serialized_size(sample_project) == payload.compressed_bytes


def test_round_trip_with_a_project_feed_line(
    repository: ProjectContainerRepository,
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


def test_round_trip_with_a_construction_record(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    from antennadesk.domain.projects.construction import (
        AsBuiltDimension,
        ConstructionChecklistItem,
        ConstructionRecord,
    )

    record = ConstructionRecord(
        as_built_notes="Built in the back yard",
        dimensions=(
            AsBuiltDimension(
                id=uuid4(),
                label="Radiator length",
                design_value_m=20.0,
                actual_value_m=19.9,
                notes="Cut slightly long",
            ),
        ),
        checklist=(
            ConstructionChecklistItem("check_dimensions", checked=True),
            ConstructionChecklistItem("measure_swr"),
        ),
    )
    project = replace(sample_project, construction_record=record)
    path = tmp_path / "construction.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded.construction_record == record
    assert loaded == project


def test_round_trip_with_installation_profiles(
    repository: ProjectContainerRepository,
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
    repository: ProjectContainerRepository,
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


def _write_raw_zip(
    path: Path,
    entries: list[tuple[zipfile.ZipInfo, bytes]],
) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for info, data in entries:
            archive.writestr(info, data)


def _zip_info(
    name: str,
    *,
    compression: int = zipfile.ZIP_DEFLATED,
    flag_bits: int = 0,
    external_attr: int = 0o644 << 16,
) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = compression
    info.flag_bits = flag_bits
    info.external_attr = external_attr
    return info


def test_missing_manifest_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    del entries["manifest.json"]
    _write_entries(path, entries)

    with pytest.raises(ProjectFormatError, match=r"manifest\.json"):
        repository.load(path)


def test_manifest_entry_missing_from_zip_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    entries.pop("project.json")
    _write_entries(path, entries)

    with pytest.raises(ProjectFormatError, match="mismatch"):
        repository.load(path)


def test_extra_zip_entry_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    entries["runs/00000000-0000-0000-0000-000000000099.json"] = b"{}"
    _write_entries(path, entries)

    with pytest.raises(ProjectFormatError, match="mismatch"):
        repository.load(path)


def test_crc_mismatch_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["entries"][0]["crc32"] = (manifest["entries"][0]["crc32"] + 1) & 0xFFFFFFFF
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="CRC mismatch"):
        repository.load(path)


def test_sha256_mismatch_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["entries"][0]["sha256"] = "0" * 64
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="SHA-256 mismatch"):
        repository.load(path)


def test_uncompressed_size_mismatch_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["entries"][0]["uncompressed_bytes"] += 1
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="size mismatch"):
        repository.load(path)


def test_compressed_size_mismatch_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["entries"][0]["compressed_bytes"] += 1
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="compressed size mismatch"):
        repository.load(path)


@pytest.mark.parametrize(
    "name",
    [
        "../evil.json",
        "/absolute.json",
        "runs\\evil.json",
        "designs/not-a-uuid.json",
        "unknown/entry.json",
    ],
)
def test_unsafe_or_unknown_entry_paths_are_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    name: str,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    entries[name] = b"{}"
    _write_entries(path, entries)

    with pytest.raises(ProjectFormatError):
        repository.load(path)


def test_duplicate_case_insensitive_entry_names_are_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    design_id = uuid4()
    lower = f"designs/{design_id}.json"
    upper = f"designs/{str(design_id).upper()}.json"
    entries = _read_entries(path)
    entries[lower] = b"{}"
    entries[upper] = b"{}"
    _write_entries(path, entries)

    with pytest.raises(ProjectFormatError, match="case-insensitive duplicate"):
        repository.load(path)


def test_symlink_entry_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    entries.pop("manifest.json")
    name = f"designs/{uuid4()}.json"
    _write_raw_zip(
        path,
        [(_zip_info(name, external_attr=0o120777 << 16), b"{}")],
    )

    with pytest.raises(ProjectFormatError, match="symbolic links"):
        repository.load(path)


def test_encrypted_entry_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:

    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    raw = bytearray(path.read_bytes())
    for signature, offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
        index = raw.find(signature)
        while index != -1:
            raw[index + offset] |= 0x1
            index = raw.find(signature, index + 4)
    path.write_bytes(raw)

    with pytest.raises(ProjectFormatError, match="encrypted"):
        repository.load(path)


def test_unsupported_compression_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    name = f"designs/{uuid4()}.json"
    _write_raw_zip(
        path,
        [(_zip_info(name, compression=zipfile.ZIP_BZIP2), b"{}")],
    )

    with pytest.raises(ProjectFormatError, match="compression"):
        repository.load(path)


def test_entry_limit_is_enforced_on_save_and_load(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    monkeypatch.setattr(container_module, "MAX_ENTRY_BYTES", 64)

    with pytest.raises(ProjectTooLargeError, match="too large"):
        repository.prepare_payload(sample_project)
    with pytest.raises(ProjectTooLargeError, match="too large"):
        repository.load(path)


def test_manifest_limit_is_enforced_on_load(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    monkeypatch.setattr(container_module, "MAX_MANIFEST_BYTES", 8)

    with pytest.raises(ProjectTooLargeError, match="manifest is too large"):
        repository.load(path)


def test_entry_count_limit_is_enforced_on_save_and_load(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    monkeypatch.setattr(container_module, "MAX_ENTRIES", 2)

    with pytest.raises(ProjectTooLargeError, match="too many entries"):
        repository.prepare_payload(sample_project)
    with pytest.raises(ProjectTooLargeError, match="too many entries"):
        repository.load(path)


def test_path_length_limit_is_enforced_on_save(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(container_module, "MAX_PATH_BYTES", 5)

    with pytest.raises(ProjectTooLargeError, match="path is too long"):
        repository.prepare_payload(sample_project)


def test_run_raw_text_is_stored_in_separate_entries(
    repository: ProjectContainerRepository,
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

    entries = _read_entries(path)
    run_path = next(name for name in entries if name.startswith("runs/") and name.endswith(".json"))
    run_document = json.loads(entries[run_path])
    assert run_document["run"]["result"]["raw_input"] == ""
    assert run_document["run"]["result"]["raw_output"] == ""
    assert f"{run_path[:-5]}.raw-input.txt" in entries
    assert f"{run_path[:-5]}.raw-output.txt" in entries
    assert b"FREQUENCY" in entries[f"{run_path[:-5]}.raw-output.txt"]
    assert repository.load(path) == project


def test_optimization_is_a_separate_entry(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from datetime import UTC, datetime

    from antennadesk.domain.optimization.summary import (
        OptimizationMode,
        OptimizationSummary,
    )

    summary = OptimizationSummary(
        mode=OptimizationMode.SINGLE,
        objective="swr",
        status="ok",
        budget_profile="quick",
        evaluations=10,
        seed=1,
        best_values={"length_m": 20.0},
        best_metrics={"swr": 1.1},
        completed_at=datetime(2026, 10, 29, tzinfo=UTC),
    )
    design = sample_project.designs[0].with_optimization_summary(summary)
    project = sample_project.with_design(design, updated_at=sample_project.updated_at)
    path = tmp_path / "with-optimization.antennadesk"
    repository.save(project, path)

    entries = _read_entries(path)
    optimization_path = f"optimizations/{design.id}.json"
    design_path = f"designs/{design.id}.json"
    assert optimization_path in entries
    assert json.loads(entries[design_path])["design"].get("optimization_summary") is None
    assert repository.load(path) == project


def test_optimization_for_an_unknown_design_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    manifest = json.loads(entries["manifest.json"])
    name = f"optimizations/{uuid4()}.json"
    entries[name] = b"{}"
    manifest["entries"].append(
        {
            "path": name,
            "kind": "optimization",
            "uncompressed_bytes": 2,
            "compressed_bytes": 4,
            "crc32": zlib.crc32(b"{}") & 0xFFFFFFFF,
            "sha256": hashlib.sha256(b"{}").hexdigest(),
        }
    )
    entries["manifest.json"] = json.dumps(manifest).encode("utf-8")
    _write_container(path, entries)

    with pytest.raises(ProjectFormatError, match="optimization"):
        repository.load(path)


def _replace_entry(path: Path, name: str, document: dict[str, Any]) -> None:
    entries = _read_entries(path)
    entries[name] = json.dumps(document, separators=(",", ":")).encode("utf-8")
    _write_container(path, entries)


def test_manifest_duplicate_path_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["entries"].append(dict(manifest["entries"][0]))
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="duplicate manifest entry path"):
        repository.load(path)


def test_manifest_self_entry_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["entries"].append(
        {
            "path": "manifest.json",
            "kind": "metadata",
            "uncompressed_bytes": 1,
            "compressed_bytes": 1,
            "crc32": 0,
            "sha256": "0" * 64,
        }
    )
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="must not list itself"):
        repository.load(path)


def test_manifest_missing_project_entry_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["entries"] = [
        entry for entry in manifest["entries"] if entry["path"] != "project.json"
    ]
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="missing the project metadata"):
        repository.load(path)


def test_manifest_naive_timestamp_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["created_at"] = "2026-10-29T12:00:00"
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="timezone-aware"):
        repository.load(path)


def test_container_version_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["container_version"] = 2
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="container version"):
        repository.load(path)


def test_invalid_manifest_json_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    entries["manifest.json"] = b"{not json"
    _write_entries(path, entries)

    with pytest.raises(ProjectFormatError, match="invalid project manifest"):
        repository.load(path)


def test_design_with_embedded_optimization_summary_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from datetime import UTC, datetime

    from antennadesk.domain.optimization.summary import (
        OptimizationMode,
        OptimizationSummary,
    )

    summary = OptimizationSummary(
        mode=OptimizationMode.SINGLE,
        objective="swr",
        status="ok",
        budget_profile="quick",
        evaluations=1,
        seed=1,
        best_values={},
        best_metrics={},
        completed_at=datetime(2026, 10, 29, tzinfo=UTC),
    )
    design = sample_project.designs[0].with_optimization_summary(summary)
    project = sample_project.with_design(design, updated_at=sample_project.updated_at)
    path = tmp_path / "dipole.antennadesk"
    repository.save(project, path)

    entries = _read_entries(path)
    design_name = f"designs/{design.id}.json"
    design_document = json.loads(entries[design_name])
    design_document["design"]["optimization_summary"] = json.loads(
        entries[f"optimizations/{design.id}.json"]
    )["summary"]
    _replace_entry(path, design_name, design_document)

    with pytest.raises(ProjectFormatError, match="must not embed"):
        repository.load(path)


def test_run_id_mismatch_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

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
    run_name = next(
        name for name in _read_entries(path) if name.startswith("runs/") and name.endswith(".json")
    )
    run_document = json.loads(_read_entries(path)[run_name])
    run_document["run"]["id"] = str(uuid4())
    _replace_entry(path, run_name, run_document)

    with pytest.raises(ProjectFormatError, match="run id does not match"):
        repository.load(path)


def test_raw_text_without_run_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    manifest = json.loads(entries["manifest.json"])
    name = f"runs/{uuid4()}.raw-input.txt"
    entries[name] = b"CE test"
    manifest["entries"].append(
        {
            "path": name,
            "kind": "raw-input",
            "uncompressed_bytes": len(entries[name]),
            "compressed_bytes": 0,
            "crc32": zlib.crc32(entries[name]) & 0xFFFFFFFF,
            "sha256": hashlib.sha256(entries[name]).hexdigest(),
        }
    )
    entries["manifest.json"] = json.dumps(manifest).encode("utf-8")
    _write_container(path, entries)

    with pytest.raises(ProjectFormatError, match="no run entry"):
        repository.load(path)


def test_raw_text_invalid_utf8_is_rejected(
    repository: ProjectContainerRepository,
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
    run_name = next(
        name for name in _read_entries(path) if name.startswith("runs/") and name.endswith(".json")
    )
    raw_name = f"{run_name[:-5]}.raw-input.txt"
    entries = _read_entries(path)
    entries[raw_name] = b"\xff\xfe"
    _write_container(path, entries)

    with pytest.raises(ProjectFormatError, match="not UTF-8"):
        repository.load(path)


def test_manifest_kind_mismatch_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    design_entry = next(
        entry for entry in manifest["entries"] if entry["path"].startswith("designs/")
    )
    design_entry["kind"] = "run"
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="kind does not match"):
        repository.load(path)


def test_invalid_uuid_entry_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    manifest = json.loads(entries["manifest.json"])
    existing = next((name, data) for name, data in entries.items() if name.startswith("designs/"))
    name = "designs/not-a-uuid.json"
    entries[name] = existing[1]
    manifest["entries"].append(
        {
            "path": name,
            "kind": "design",
            "uncompressed_bytes": len(existing[1]),
            "compressed_bytes": 0,
            "crc32": zlib.crc32(existing[1]) & 0xFFFFFFFF,
            "sha256": hashlib.sha256(existing[1]).hexdigest(),
        }
    )
    entries["manifest.json"] = json.dumps(manifest).encode("utf-8")
    _write_container(path, entries)

    with pytest.raises(ProjectFormatError, match="not a UUID"):
        repository.load(path)


@pytest.mark.filterwarnings("ignore:Duplicate name")
def test_duplicate_zip_entry_name_is_rejected(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "dipole.antennadesk"
    repository.save(sample_project, path)
    entries = _read_entries(path)
    name = "designs/00000000-0000-0000-0000-000000000077.json"
    _write_raw_zip(
        path,
        [
            (_zip_info("manifest.json"), entries["manifest.json"]),
            (_zip_info(name), b"{}"),
            (_zip_info(name), b"{}"),
        ],
    )

    with pytest.raises(ProjectFormatError, match="duplicate project entry name"):
        repository.load(path)


def _project_with_runs(
    sample_project: Project,
    count: int = 3,
) -> Project:
    from datetime import timedelta

    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )

    project = sample_project
    for index in range(count):
        project = RecordSimulationRun().execute(
            RecordSimulationRunCommand(
                project=project,
                design_id=sample_project.designs[0].id,
                result=_rich_result(),
                created_at=sample_project.updated_at + timedelta(minutes=index),
            )
        )
    return project


def test_open_session_keeps_runs_lazy(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _project_with_runs(sample_project)
    path = tmp_path / "lazy.antennadesk"
    repository.save(project, path)
    calls: list[dict[str, bytes]] = []

    def fail_if_run_payloads_are_read(data: dict[str, bytes]) -> object:
        calls.append(data)
        raise AssertionError("open_session must not read run payloads")

    monkeypatch.setattr(repository, "_read_runs", fail_if_run_payloads_are_read)

    session = repository.open_session(path)

    assert session.project.simulation_runs == ()
    assert session.run_count() == 3
    assert calls == []


def test_session_loads_only_the_requested_run(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _project_with_runs(sample_project)
    path = tmp_path / "lazy-one.antennadesk"
    repository.save(project, path)
    original = repository._read_runs
    calls: list[set[str]] = []

    def counted(data: dict[str, bytes]) -> object:
        calls.append(set(data))
        return original(data)

    monkeypatch.setattr(repository, "_read_runs", counted)
    session = repository.open_session(path)

    latest = session.latest_run(sample_project.designs[0].id)

    assert latest == project.simulation_runs[-1]
    assert len(calls) == 1
    run_id = latest.id if latest is not None else None
    assert f"runs/{run_id}.json" in calls[0]
    assert len(session.cached_runs()) == 1


def test_session_materializes_every_run_on_demand(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project = _project_with_runs(sample_project)
    path = tmp_path / "materialize.antennadesk"
    repository.save(project, path)

    session = repository.open_session(path)
    materialized = session.materialize()

    assert materialized == project
    assert len(materialized.simulation_runs) == 3


def test_session_latest_band_analysis_uses_the_manifest_index(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from datetime import timedelta
    from uuid import uuid4

    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )

    batch_id = uuid4()
    project = sample_project
    for index, band_id in enumerate(("40m", "20m")):
        project = RecordSimulationRun().execute(
            RecordSimulationRunCommand(
                project=project,
                design_id=sample_project.designs[0].id,
                result=_rich_result(),
                created_at=sample_project.updated_at + timedelta(minutes=index),
                band_id=band_id,
                batch_id=batch_id,
            )
        )
    path = tmp_path / "band-session.antennadesk"
    repository.save(project, path)

    session = repository.open_session(path)
    analysis = session.latest_band_analysis(sample_project.designs[0].id)

    assert analysis is not None
    assert analysis.batch_id == batch_id
    assert [band.band.name for band in analysis.bands] == ["40m", "20m"]
    assert analysis.bands[0].result == project.simulation_runs[0].result


def test_open_design_only_ignores_run_entries(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project = _project_with_runs(sample_project)
    path = tmp_path / "design-only.antennadesk"
    repository.save(project, path)
    entries = _read_entries(path)
    run_name = next(name for name in entries if name.startswith("runs/") and name.endswith(".json"))
    entries[run_name] = b"{not a run"
    _write_container(path, entries)

    recovered = repository.open_design_only(path)

    assert recovered.designs == project.designs
    assert recovered.simulation_runs == ()
    assert recovered.name == project.name


def test_manifest_run_index_must_match_the_entries(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project = _project_with_runs(sample_project, count=1)
    path = tmp_path / "bad-index.antennadesk"
    repository.save(project, path)
    manifest = _manifest(path)
    manifest["runs"] = []
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="run index"):
        repository.open_session(path)


def test_manifest_design_index_must_match_the_entries(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "bad-design-index.antennadesk"
    repository.save(sample_project, path)
    manifest = _manifest(path)
    manifest["design_ids"] = []
    _write_manifest(path, manifest)

    with pytest.raises(ProjectFormatError, match="design index"):
        repository.open_session(path)


def test_open_design_only_ignores_missing_run_entries(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project = _project_with_runs(sample_project, count=1)
    path = tmp_path / "missing-run.antennadesk"
    repository.save(project, path)
    entries = _read_entries(path)
    entries.pop(
        next(name for name in entries if name.startswith("runs/") and name.endswith(".json"))
    )
    _write_entries(path, entries)

    with pytest.raises(ProjectFormatError, match="mismatch"):
        repository.open_session(path)

    recovered = repository.open_design_only(path)

    assert recovered.designs == project.designs
    assert recovered.simulation_runs == ()


def test_session_surfaces_a_corrupt_run_only_when_requested(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project = _project_with_runs(sample_project, count=1)
    path = tmp_path / "corrupt-run.antennadesk"
    repository.save(project, path)
    entries = _read_entries(path)
    run_name = next(name for name in entries if name.startswith("runs/") and name.endswith(".json"))
    entries[run_name] = b"{not a run"
    _write_container(path, entries)

    session = repository.open_session(path)
    assert session.project.simulation_runs == ()

    with pytest.raises(ProjectFormatError, match="invalid project entry"):
        session.latest_run(sample_project.designs[0].id)


def test_prepared_project_reports_compressed_and_expanded_sizes(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    prepared = repository.prepare_payload(sample_project)
    path = tmp_path / "sizes.antennadesk"
    repository.write_payload(path, prepared)

    with zipfile.ZipFile(path) as archive:
        expanded = sum(info.file_size for info in archive.infolist())
        entries = len(archive.infolist())

    assert prepared.compressed_bytes == path.stat().st_size
    assert prepared.expanded_bytes == expanded
    assert prepared.entry_count == entries
    assert prepared.limits.container_bytes == MAX_PROJECT_SIZE_BYTES


def test_prepare_session_payload_copies_runs_without_materializing(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _project_with_runs(sample_project, count=3)
    source = tmp_path / "source.antennadesk"
    repository.save(project, source)
    session = repository.open_session(source)
    original = repository._read_runs

    def fail(data: dict[str, bytes]) -> object:
        del data
        raise AssertionError("lazy save must not parse run payloads")

    monkeypatch.setattr(repository, "_read_runs", fail)
    prepared = repository.prepare_session_payload(session, session.project)
    target = tmp_path / "lazy-saved.antennadesk"
    repository.write_payload(target, prepared)

    monkeypatch.setattr(repository, "_read_runs", original)
    assert repository.load(target) == project


def test_prepare_session_payload_adds_new_runs(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )

    source_project = _project_with_runs(sample_project, count=1)
    source = tmp_path / "source.antennadesk"
    repository.save(source_project, source)
    session = repository.open_session(source)
    updated = RecordSimulationRun().execute(
        RecordSimulationRunCommand(
            project=session.project,
            design_id=session.project.designs[0].id,
            result=_rich_result(),
            created_at=source_project.updated_at + timedelta(minutes=10),
        )
    )
    prepared = repository.prepare_session_payload(session, updated)
    target = tmp_path / "with-new-run.antennadesk"
    repository.write_payload(target, prepared)

    loaded = repository.load(target)
    assert len(loaded.simulation_runs) == 2
    assert {run.id for run in loaded.simulation_runs} == {
        *[run.id for run in source_project.simulation_runs],
        updated.simulation_runs[-1].id,
    }


def test_prepare_session_payload_can_keep_only_retained_runs(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project = _project_with_runs(sample_project, count=3)
    source = tmp_path / "source.antennadesk"
    repository.save(project, source)
    session = repository.open_session(source)
    compacted_project = replace(project, simulation_runs=(), updated_at=project.updated_at)
    prepared = repository.prepare_session_payload(
        session,
        compacted_project,
        retained_only=True,
    )
    target = tmp_path / "retained.antennadesk"
    repository.write_payload(target, prepared)

    loaded = repository.load(target)
    assert len(loaded.simulation_runs) == 1
    assert loaded.simulation_runs[0].id in {run.id for run in project.simulation_runs}


def test_prepare_session_payload_with_new_runs_and_retention_falls_back(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )

    source_project = _project_with_runs(sample_project, count=2)
    source = tmp_path / "source.antennadesk"
    repository.save(source_project, source)
    session = repository.open_session(source)
    updated = RecordSimulationRun().execute(
        RecordSimulationRunCommand(
            project=session.project,
            design_id=session.project.designs[0].id,
            result=_rich_result(),
            created_at=source_project.updated_at + timedelta(minutes=10),
        )
    )
    prepared = repository.prepare_session_payload(
        session,
        updated,
        retained_only=True,
    )
    target = tmp_path / "retained-with-new.antennadesk"
    repository.write_payload(target, prepared)

    loaded = repository.load(target)
    assert len(loaded.simulation_runs) == 1
    assert loaded.simulation_runs[0].id == updated.simulation_runs[-1].id


def test_round_trip_with_site_ground(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    profile = SiteGroundProfile(
        second_medium_relative_permittivity=81.0,
        second_medium_conductivity_s_per_m=5.0,
        edge_distance_m=50.0,
        edge_shape=EdgeShape.CIRCULAR,
        edge_height_m=0.0,
        label="Coastal cliff",
        notes="Far-field only.",
    )
    project = sample_project.with_site_ground(
        profile,
        updated_at=sample_project.updated_at,
    )
    path = tmp_path / "site-ground.antennadesk"
    repository.save(project, path)

    loaded = repository.load(path)

    assert loaded == project
    assert loaded.site_ground == profile
    document = _load_json(path)
    assert document["project"]["site_ground"]["edge_shape"] == "circular"


def test_schema_59_container_migrates_to_current(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    source = tmp_path / "schema-59.antennadesk"
    repository.save(sample_project, source)
    entries = _read_entries(source)
    manifest = json.loads(entries["manifest.json"])
    manifest["schema_version"] = 59
    project_document = json.loads(entries["project.json"])
    project_document["schema_version"] = 59
    project_document["project"].pop("site_ground", None)
    entries["project.json"] = json.dumps(project_document, separators=(",", ":")).encode("utf-8")
    for name in entries:
        if name.startswith(("designs/", "optimizations/", "runs/")) and name.endswith(".json"):
            document = json.loads(entries[name])
            document["schema_version"] = 59
            entries[name] = json.dumps(document, separators=(",", ":")).encode("utf-8")
    entries["manifest.json"] = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    _write_container(source, entries)

    loaded = repository.load(source)
    assert loaded.site_ground is None

    target = tmp_path / "schema-current.antennadesk"
    repository.save(loaded, target)
    assert _manifest(target)["schema_version"] == SCHEMA_VERSION


def test_schema_60_container_migrates_a_vertical_at_zero_droop(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from uuid import uuid4

    from antennadesk.domain.antennas.vertical import VerticalParameters
    from antennadesk.domain.projects.project import DesignVariant

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=2.0,
        radial_count=8,
        radial_length_m=5.0,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Vertical",
        antenna_type="vertical",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )
    source = tmp_path / "schema-60.antennadesk"
    repository.save(replace(sample_project, designs=(design,)), source)

    entries = _read_entries(source)
    manifest = json.loads(entries["manifest.json"])
    manifest["schema_version"] = 60
    entries["manifest.json"] = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    project_document = json.loads(entries["project.json"])
    project_document["schema_version"] = 60
    entries["project.json"] = json.dumps(project_document, separators=(",", ":")).encode("utf-8")
    design_entry = next(name for name in entries if name.startswith("designs/"))
    design_document = json.loads(entries[design_entry])
    design_document["schema_version"] = 60
    design_document["design"]["parameters"].pop("radial_droop_deg")
    entries[design_entry] = json.dumps(design_document, separators=(",", ":")).encode("utf-8")
    _write_container(source, entries)

    loaded = repository.load(source)

    assert loaded.designs[0].parameters.radial_droop_deg == 0.0
    target = tmp_path / "schema-current-vertical.antennadesk"
    repository.save(loaded, target)
    assert _manifest(target)["schema_version"] == SCHEMA_VERSION


def test_schema_61_container_migrates_to_current(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    source = tmp_path / "schema-61.antennadesk"
    repository.save(sample_project, source)
    entries = _read_entries(source)
    manifest = json.loads(entries["manifest.json"])
    manifest["schema_version"] = 61
    entries["manifest.json"] = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    for name, payload in tuple(entries.items()):
        if not name.endswith(".json"):
            continue
        document = json.loads(payload)
        if isinstance(document, dict) and document.get("schema_version") == SCHEMA_VERSION:
            document["schema_version"] = 61
            entries[name] = json.dumps(document, separators=(",", ":")).encode("utf-8")
    _write_container(source, entries)

    loaded = repository.load(source)

    assert loaded == sample_project
    target = tmp_path / "schema-current-61.antennadesk"
    repository.save(loaded, target)
    assert _manifest(target)["schema_version"] == SCHEMA_VERSION


def test_schema_62_container_migrates_to_current(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    source = tmp_path / "schema-62.antennadesk"
    repository.save(sample_project, source)
    entries = _read_entries(source)
    manifest = json.loads(entries["manifest.json"])
    manifest["schema_version"] = 62
    entries["manifest.json"] = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    for name, payload in tuple(entries.items()):
        if not name.endswith(".json"):
            continue
        document = json.loads(payload)
        if isinstance(document, dict) and document.get("schema_version") == SCHEMA_VERSION:
            document["schema_version"] = 62
            entries[name] = json.dumps(document, separators=(",", ":")).encode("utf-8")
    _write_container(source, entries)

    loaded = repository.load(source)

    assert loaded == sample_project
    target = tmp_path / "schema-current-62.antennadesk"
    repository.save(loaded, target)
    assert _manifest(target)["schema_version"] == SCHEMA_VERSION


def test_schema_64_container_migrates_to_current(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    source = tmp_path / "schema-64.antennadesk"
    repository.save(sample_project, source)
    entries = _read_entries(source)
    manifest = json.loads(entries["manifest.json"])
    manifest["schema_version"] = 64
    entries["manifest.json"] = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    for name, payload in tuple(entries.items()):
        if not name.endswith(".json"):
            continue
        document = json.loads(payload)
        if isinstance(document, dict) and document.get("schema_version") == SCHEMA_VERSION:
            document["schema_version"] = 64
            entries[name] = json.dumps(document, separators=(",", ":")).encode("utf-8")
    _write_container(source, entries)

    loaded = repository.load(source)

    assert loaded == sample_project
    target = tmp_path / "schema-current-64.antennadesk"
    repository.save(loaded, target)
    assert _manifest(target)["schema_version"] == SCHEMA_VERSION


def test_round_trip_preserves_run_site_ground(
    repository: ProjectContainerRepository,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from antennadesk.application.use_cases.record_simulation_run import (
        RecordSimulationRun,
        RecordSimulationRunCommand,
    )

    site = SiteGroundProfile(
        second_medium_relative_permittivity=81.0,
        second_medium_conductivity_s_per_m=5.0,
        edge_distance_m=25.0,
        edge_shape=EdgeShape.LINEAR,
    )
    base = _rich_result()
    result = replace(base, spec=replace(base.spec, site_ground=site))
    project = RecordSimulationRun().execute(
        RecordSimulationRunCommand(
            project=sample_project,
            design_id=sample_project.designs[0].id,
            result=result,
            created_at=sample_project.updated_at,
        )
    )
    path = tmp_path / "run-site.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded.simulation_runs[0].result.spec.site_ground == site
