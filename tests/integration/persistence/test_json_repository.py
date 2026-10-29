from __future__ import annotations

import json
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from antennadesk.domain.projects.project import Project
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
    document["project"]["designs"][0]["antenna_type"] = "yagi"
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
