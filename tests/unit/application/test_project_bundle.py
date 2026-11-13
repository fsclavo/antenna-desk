# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable project bundle export and import."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

import pytest

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
    missing: bool = False,
) -> tuple[Project, Path, Path]:
    photo = tmp_path / "site photo.jpg"
    photo.write_bytes(b"site-photo")
    plan = tmp_path / "plan.png"
    plan.write_bytes(b"plan-image")
    profile = InstallationProfile(
        id=uuid4(),
        name="Portable site",
        image_reference=str(photo),
    )
    references = (str(plan), str(photo))
    if missing:
        references += (str(tmp_path / "missing.jpg"),)
    entry = JournalEntry(
        id=uuid4(),
        created_at=datetime(2026, 11, 12, tzinfo=UTC),
        title="As built",
        kind=JournalEntryKind.PHOTO,
        image_references=references,
    )
    project = sample_project.with_installation_profile(
        profile,
        updated_at=sample_project.updated_at,
    )
    project = project.with_journal_entry(entry, updated_at=sample_project.updated_at)
    return project, photo, plan


def _read_zip(path: Path) -> dict[str, bytes]:
    with ZipFile(path) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def _write_zip(path: Path, entries: dict[str, bytes]) -> None:
    with ZipFile(path, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)


def _bundle_project(entries: dict[str, bytes], tmp_path: Path) -> Project:
    project_path = tmp_path / "bundle-project.antennadesk"
    project_path.write_bytes(entries[PROJECT_NAME])
    return JsonProjectRepository().load(project_path)


def test_export_writes_a_manifest_project_and_assets(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project, photo, plan = _project_with_images(sample_project, tmp_path)
    bundle = tmp_path / "project.antennadesk-bundle"

    result = ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)

    assert result.bundle_path == bundle
    assert result.asset_count == 2
    assert result.missing_assets == ()
    entries = _read_zip(bundle)
    assert set(entries) >= {MANIFEST_NAME, PROJECT_NAME}
    manifest = json.loads(entries[MANIFEST_NAME])
    assert manifest["format"] == "antennadesk.project_bundle"
    assert manifest["format_version"] == 1
    assert manifest["project_file"] == PROJECT_NAME
    assert len(manifest["assets"]) == 2
    bundled = _bundle_project(entries, tmp_path)
    assert bundled.installation_profiles[0].image_reference.startswith("assets/")
    assert all(
        reference.startswith("assets/") for reference in bundled.journal_entries[0].image_references
    )
    assert project.installation_profiles[0].image_reference == str(photo)
    assert project.journal_entries[0].image_references[0] == str(plan)


def test_import_round_trip_rewrites_images_to_local_files(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project, _, _ = _project_with_images(sample_project, tmp_path)
    bundle = tmp_path / "project.antennadesk-bundle"
    ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)
    destination_parent = tmp_path / "imported"
    destination_parent.mkdir()

    result = ImportProjectBundle(JsonProjectRepository()).execute(
        bundle,
        destination_parent,
    )

    assert result.project_path.is_file()
    assert result.project_path.parent == result.destination
    assert result.asset_count == 2
    assert result.missing_assets == ()
    profile_image = result.project.installation_profiles[0].image_reference
    assert Path(profile_image).is_file()
    journal_images = result.project.journal_entries[0].image_references
    assert all(Path(reference).is_file() for reference in journal_images)
    loaded = JsonProjectRepository().load(result.project_path)
    assert loaded.installation_profiles[0].image_reference == profile_image
    assert loaded.journal_entries[0].image_references == journal_images


def test_missing_images_are_reported_but_do_not_block_export_or_import(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project, _, _ = _project_with_images(sample_project, tmp_path, missing=True)
    bundle = tmp_path / "project.antennadesk-bundle"

    exported = ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)

    assert exported.asset_count == 2
    assert exported.missing_assets == (str(tmp_path / "missing.jpg"),)
    destination_parent = tmp_path / "imported"
    destination_parent.mkdir()
    imported = ImportProjectBundle(JsonProjectRepository()).execute(bundle, destination_parent)
    assert imported.missing_assets == (str(tmp_path / "missing.jpg"),)
    assert str(tmp_path / "missing.jpg") in imported.project.journal_entries[0].image_references


def test_duplicate_image_references_share_one_asset(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    photo = tmp_path / "photo.jpg"
    photo.write_bytes(b"same-photo")
    profile = InstallationProfile(
        id=uuid4(),
        name="Portable",
        image_reference=str(photo),
    )
    entry = JournalEntry(
        id=uuid4(),
        created_at=datetime(2026, 11, 12, tzinfo=UTC),
        title="Photo",
        kind=JournalEntryKind.PHOTO,
        image_references=(str(photo),),
    )
    project = sample_project.with_installation_profile(
        profile,
        updated_at=sample_project.updated_at,
    )
    project = project.with_journal_entry(entry, updated_at=sample_project.updated_at)
    bundle = tmp_path / "bundle.antennadesk-bundle"

    result = ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)

    assert result.asset_count == 1
    manifest = json.loads(_read_zip(bundle)[MANIFEST_NAME])
    assert len(manifest["assets"]) == 1


def test_import_rejects_path_traversal(tmp_path: Path) -> None:
    bundle = tmp_path / "bad.antennadesk-bundle"
    _write_zip(
        bundle,
        {
            MANIFEST_NAME: b"{}",
            "../outside.txt": b"no",
            PROJECT_NAME: b"{}",
        },
    )
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="unsafe"):
        ImportProjectBundle(JsonProjectRepository()).execute(bundle, destination)


def test_import_rejects_unlisted_assets(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project, _, _ = _project_with_images(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)
    entries = _read_zip(bundle)
    entries["assets/extra.jpg"] = b"extra"
    bad_bundle = tmp_path / "bad.antennadesk-bundle"
    _write_zip(bad_bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="does not match"):
        ImportProjectBundle(JsonProjectRepository()).execute(bad_bundle, destination)


def test_import_rejects_a_corrupt_asset(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project, _, _ = _project_with_images(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)
    entries = _read_zip(bundle)
    manifest = json.loads(entries[MANIFEST_NAME])
    asset = next(item for item in manifest["assets"] if not item["missing"])
    original = entries[asset["asset_path"]]
    entries[asset["asset_path"]] = b"x" * len(original)
    bad_bundle = tmp_path / "bad.antennadesk-bundle"
    _write_zip(bad_bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="checksum mismatch"):
        ImportProjectBundle(JsonProjectRepository()).execute(bad_bundle, destination)


def test_import_rejects_an_unsupported_manifest(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project, _, _ = _project_with_images(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)
    entries = _read_zip(bundle)
    manifest = json.loads(entries[MANIFEST_NAME])
    manifest["format_version"] = 99
    entries[MANIFEST_NAME] = json.dumps(manifest).encode()
    bad_bundle = tmp_path / "bad.antennadesk-bundle"
    _write_zip(bad_bundle, entries)
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="version"):
        ImportProjectBundle(JsonProjectRepository()).execute(bad_bundle, destination)


def test_import_rejects_a_bundle_without_its_project(tmp_path: Path) -> None:
    bundle = tmp_path / "bad.antennadesk-bundle"
    _write_zip(bundle, {MANIFEST_NAME: b"{}"})
    destination = tmp_path / "destination"
    destination.mkdir()

    with pytest.raises(ProjectBundleError, match="missing"):
        ImportProjectBundle(JsonProjectRepository()).execute(bundle, destination)


def test_export_rejects_an_oversized_asset(
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.application.use_cases import project_bundle

    photo = tmp_path / "photo.jpg"
    photo.write_bytes(b"12345")
    project = sample_project.with_installation_profile(
        InstallationProfile(
            id=uuid4(),
            name="Portable",
            image_reference=str(photo),
        ),
        updated_at=sample_project.updated_at,
    )
    monkeypatch.setattr(project_bundle, "MAX_ASSET_BYTES", 4)
    bundle = tmp_path / "bundle.antennadesk-bundle"

    with pytest.raises(ProjectBundleError, match="too large"):
        ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)


def test_import_creates_a_unique_destination(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    project, _, _ = _project_with_images(sample_project, tmp_path)
    bundle = tmp_path / "bundle.antennadesk-bundle"
    ExportProjectBundle(JsonProjectRepository()).execute(project, bundle)
    destination = tmp_path / "destination"
    destination.mkdir()

    first = ImportProjectBundle(JsonProjectRepository()).execute(bundle, destination)
    second = ImportProjectBundle(JsonProjectRepository()).execute(bundle, destination)

    assert first.destination != second.destination
    assert first.destination.is_dir()
    assert second.destination.is_dir()
