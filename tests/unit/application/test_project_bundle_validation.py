# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation branches for portable project bundle import/export."""

from __future__ import annotations

import json
import stat
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest

from antennadesk.application.use_cases import project_bundle as bundle_module
from antennadesk.application.use_cases.project_bundle import (
    MANIFEST_NAME,
    PROJECT_NAME,
    ExportProjectBundle,
    ImportProjectBundle,
    ProjectBundleError,
)
from antennadesk.domain.projects.installation import InstallationProfile
from antennadesk.domain.projects.journal import JournalEntry, JournalEntryKind
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.json_repository import JsonProjectRepository


def _project_with_images(
    sample_project: Project,
    tmp_path: Path,
    *,
    count: int = 1,
) -> tuple[Project, tuple[Path, ...]]:
    project = sample_project
    photos: list[Path] = []
    for index in range(count):
        photo = tmp_path / f"site-{index}.jpg"
        photo.write_bytes(f"photo-{index}".encode())
        photos.append(photo)
        project = project.with_installation_profile(
            InstallationProfile(
                id=uuid4(),
                name=f"Site {index}",
                image_reference=str(photo),
            ),
            updated_at=project.updated_at,
        )
    return project, tuple(photos)


def _read_zip(path: Path) -> dict[str, bytes]:
    with ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def _write_zip(
    path: Path,
    entries: dict[str, bytes] | list[tuple[str | ZipInfo, bytes]],
) -> None:
    items = entries.items() if isinstance(entries, dict) else entries
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for name, data in items:
            archive.writestr(name, data)


def _base_entries(sample_project: Project, tmp_path: Path) -> dict[str, bytes]:
    bundle = tmp_path / "base.antennadesk-bundle"
    ExportProjectBundle(JsonProjectRepository()).execute(sample_project, bundle)
    return _read_zip(bundle)


def _write_modified(
    path: Path,
    entries: dict[str, bytes],
    manifest: dict[str, object],
) -> None:
    entries = dict(entries)
    entries[MANIFEST_NAME] = json.dumps(manifest).encode("utf-8")
    _write_zip(path, entries)


def _manifest(entries: dict[str, bytes]) -> dict[str, object]:
    value = json.loads(entries[MANIFEST_NAME])
    assert isinstance(value, dict)
    return value


def _import(
    bundle: Path,
    destination: Path,
) -> object:
    return ImportProjectBundle(JsonProjectRepository()).execute(bundle, destination)


def test_export_rejects_a_directory_path(sample_project: Project, tmp_path: Path) -> None:
    with pytest.raises(ProjectBundleError, match="directory"):
        ExportProjectBundle(JsonProjectRepository()).execute(sample_project, tmp_path)


def test_export_rejects_a_missing_parent(sample_project: Project, tmp_path: Path) -> None:
    with pytest.raises(ProjectBundleError, match="does not exist"):
        ExportProjectBundle(JsonProjectRepository()).execute(
            sample_project,
            tmp_path / "missing" / "bundle",
        )


def test_export_rejects_too_many_assets(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project, _ = _project_with_images(sample_project, tmp_path)
    monkeypatch.setattr(bundle_module, "MAX_ASSETS", 0)

    with pytest.raises(ProjectBundleError, match="more than 0 assets"):
        ExportProjectBundle(JsonProjectRepository()).execute(
            project,
            tmp_path / "bundle.antennadesk-bundle",
        )


def test_export_rejects_a_total_asset_size_limit(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project, _ = _project_with_images(sample_project, tmp_path)
    monkeypatch.setattr(bundle_module, "MAX_UNCOMPRESSED_BYTES", 1)

    with pytest.raises(ProjectBundleError, match="assets exceed"):
        ExportProjectBundle(JsonProjectRepository()).execute(
            project,
            tmp_path / "bundle.antennadesk-bundle",
        )


def test_export_rejects_a_project_payload_limit(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bundle_module, "MAX_PROJECT_PAYLOAD_BYTES", 1)

    with pytest.raises(ProjectBundleError, match="project payload is too large"):
        ExportProjectBundle(JsonProjectRepository()).execute(
            sample_project,
            tmp_path / "bundle.antennadesk-bundle",
        )


def test_export_rejects_a_manifest_limit(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bundle_module, "MAX_MANIFEST_BYTES", 1)

    with pytest.raises(ProjectBundleError, match="manifest is too large"):
        ExportProjectBundle(JsonProjectRepository()).execute(
            sample_project,
            tmp_path / "bundle.antennadesk-bundle",
        )


def test_export_rejects_a_bundle_size_limit(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bundle_module, "MAX_BUNDLE_BYTES", 1)
    bundle = tmp_path / "bundle.antennadesk-bundle"

    with pytest.raises(ProjectBundleError, match="bundle is too large"):
        ExportProjectBundle(JsonProjectRepository()).execute(sample_project, bundle)

    assert not bundle.exists()


def test_import_rejects_a_missing_bundle(tmp_path: Path) -> None:
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="not found"):
        _import(tmp_path / "missing.antennadesk-bundle", destination)


def test_import_rejects_a_missing_destination(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)

    with pytest.raises(ProjectBundleError, match="destination directory does not exist"):
        _import(bundle, tmp_path / "missing")


def test_import_rejects_an_oversized_bundle(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()
    monkeypatch.setattr(bundle_module, "MAX_BUNDLE_BYTES", 1)

    with pytest.raises(ProjectBundleError, match="bundle is too large"):
        _import(bundle, destination)


def test_import_rejects_a_non_zip_file(tmp_path: Path) -> None:
    bundle = tmp_path / "bad.antennadesk-bundle"
    bundle.write_text("not a zip", encoding="utf-8")
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="not a valid ZIP"):
        _import(bundle, destination)


def test_import_rejects_an_unexpected_directory(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    entries["other/"] = b""
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="unexpected bundle directory"):
        _import(bundle, destination)


def test_import_rejects_an_unknown_entry(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    entries["notes.txt"] = b"notes"
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="unexpected bundle entry"):
        _import(bundle, destination)


def test_import_rejects_a_duplicate_entry(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    with pytest.warns(UserWarning, match="Duplicate name"):
        _write_zip(
            bundle,
            [*entries.items(), (MANIFEST_NAME, entries[MANIFEST_NAME])],
        )
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="duplicate bundle entry"):
        _import(bundle, destination)


def test_import_rejects_a_symlink_entry(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    info = ZipInfo("assets/link")
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, [(name, data) for name, data in entries.items()] + [(info, b"")])
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="symbolic links"):
        _import(bundle, destination)


def test_import_rejects_an_encrypted_entry(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    infos = [ZipInfo(name) for name in entries]
    info = ZipInfo("assets/encrypted")
    info.flag_bits |= 0x1
    infos.append(info)

    class _Archive:
        def infolist(self) -> list[ZipInfo]:
            return infos

    with pytest.raises(ProjectBundleError, match="encrypted bundle entry"):
        bundle_module._validate_entries(_Archive())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "name",
    [
        "../outside.txt",
        "/absolute.txt",
        "assets\\outside.txt",
        "C:outside.txt",
        "assets/sub/file.txt",
    ],
)
def test_import_rejects_unsafe_entry_names(
    sample_project: Project,
    tmp_path: Path,
    name: str,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    entries[name] = b"bad"
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError):
        _import(bundle, destination)


def test_import_rejects_invalid_manifest_json(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    entries[MANIFEST_NAME] = b"{"
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="invalid bundle manifest"):
        _import(bundle, destination)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("format", "other", "unsupported bundle format"),
        ("format_version", 99, "unsupported bundle format version"),
        ("project_file", "other.antennadesk", "unexpected project file"),
        ("assets", {}, "assets must be a list"),
    ],
)
def test_import_rejects_invalid_manifest_fields(
    sample_project: Project,
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    manifest = _manifest(entries)
    manifest[field] = value
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_modified(bundle, entries, manifest)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match=message):
        _import(bundle, destination)


@pytest.mark.parametrize(
    ("asset", "message"),
    [
        ({}, "reference must not be empty"),
        ({"original_reference": "photo.jpg", "missing": "yes"}, "missing flag"),
        ({"original_reference": "photo.jpg"}, "missing its path, size, or hash"),
        (
            {
                "original_reference": "photo.jpg",
                "asset_path": "manifest.json",
                "size": 1,
                "sha256": "0" * 64,
            },
            "must be under assets",
        ),
        (
            {
                "original_reference": "photo.jpg",
                "asset_path": "assets/photo.jpg",
                "size": -1,
                "sha256": "0" * 64,
            },
            "size is invalid",
        ),
        (
            {
                "original_reference": "photo.jpg",
                "asset_path": "assets/photo.jpg",
                "size": 1,
                "sha256": "bad",
            },
            "hash is invalid",
        ),
    ],
)
def test_import_rejects_malformed_assets(
    sample_project: Project,
    tmp_path: Path,
    asset: dict[str, object],
    message: str,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    manifest = _manifest(entries)
    manifest["assets"] = [asset]
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_modified(bundle, entries, manifest)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match=message):
        _import(bundle, destination)


def test_import_rejects_too_many_manifest_assets(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    manifest = _manifest(entries)
    manifest["assets"] = [{"original_reference": "missing.jpg", "missing": True}]
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_modified(bundle, entries, manifest)
    destination = tmp_path / "destination"
    destination.mkdir()
    monkeypatch.setattr(bundle_module, "MAX_ASSETS", 0)

    with pytest.raises(ProjectBundleError, match="more than 0 assets"):
        _import(bundle, destination)


def test_import_rejects_an_entry_above_its_limit(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()
    monkeypatch.setattr(bundle_module, "MAX_MANIFEST_BYTES", 1)

    with pytest.raises(ProjectBundleError, match="entry is too large"):
        _import(bundle, destination)


def test_import_rejects_the_total_uncompressed_limit(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()
    monkeypatch.setattr(bundle_module, "MAX_UNCOMPRESSED_BYTES", 1)

    with pytest.raises(ProjectBundleError, match="uncompressed limit"):
        _import(bundle, destination)


def test_import_rejects_a_project_without_designs(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project = replace(sample_project, designs=())
    payload = JsonProjectRepository().prepare_payload(project)
    manifest = {
        "format": "antennadesk.project_bundle",
        "format_version": 1,
        "application_version": "test",
        "created_at": datetime(2026, 11, 13, tzinfo=UTC).isoformat(),
        "project_file": PROJECT_NAME,
        "project_name": project.name,
        "assets": [],
    }
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(
        bundle,
        {
            MANIFEST_NAME: json.dumps(manifest).encode("utf-8"),
            PROJECT_NAME: payload,
        },
    )
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="no designs"):
        _import(bundle, destination)


def test_import_rejects_an_asset_size_mismatch(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project, _ = _project_with_images(sample_project, tmp_path)
    entries = _base_entries(project, tmp_path)
    manifest = _manifest(entries)
    asset = next(item for item in manifest["assets"] if not item["missing"])
    entries[asset["asset_path"]] = b"different length"
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_modified(bundle, entries, manifest)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="size mismatch"):
        _import(bundle, destination)


def test_import_removes_the_destination_on_save_error(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    def fail_save(self: object, project: object, path: Path) -> None:
        del self, project, path
        raise OSError("disk full")

    monkeypatch.setattr(JsonProjectRepository, "save", fail_save)

    with pytest.raises(ProjectBundleError, match="could not write imported bundle"):
        _import(bundle, destination)

    assert not (destination / sample_project.name).exists()


def test_import_removes_the_destination_on_unexpected_error(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entries = _base_entries(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    _write_zip(bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    def fail_save(self: object, project: object, path: Path) -> None:
        del self, project, path
        raise ValueError("invalid project")

    monkeypatch.setattr(JsonProjectRepository, "save", fail_save)

    with pytest.raises(ValueError, match="invalid project"):
        _import(bundle, destination)

    assert not (destination / sample_project.name).exists()


def test_import_handles_a_journal_reference_without_an_asset(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    photo = tmp_path / "journal.jpg"
    photo.write_bytes(b"journal")
    entry = JournalEntry(
        id=uuid4(),
        created_at=datetime(2026, 11, 13, tzinfo=UTC),
        title="Photo",
        kind=JournalEntryKind.PHOTO,
        image_references=(str(photo),),
    )
    project = sample_project.with_journal_entry(entry, updated_at=sample_project.updated_at)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)
    destination = tmp_path / "destination"
    destination.mkdir()

    result = _import(bundle, destination)

    assert result.asset_count == 1
    assert result.missing_assets == ()
