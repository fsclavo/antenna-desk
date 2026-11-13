# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Export and import portable project bundles.

A bundle is a ZIP file with a manifest, the native project payload, and the
project's referenced images.  It contains no server state and no executable
content.  Import rewrites image references to the extracted local files.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import zipfile
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

from ... import __version__
from ...domain.common.time import utc_now
from ...domain.common.validation import raise_if_errors
from ...domain.projects.project import Project
from ..ports.project_repository import ProjectRepository

BUNDLE_FORMAT = "antennadesk.project_bundle"
BUNDLE_FORMAT_VERSION = 1
BUNDLE_EXTENSION = ".antennadesk-bundle"
MANIFEST_NAME = "manifest.json"
PROJECT_NAME = "project.antennadesk"
ASSET_DIR = "assets"

MAX_BUNDLE_BYTES = 256 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
MAX_ASSETS = 100
MAX_ASSET_BYTES = 25 * 1024 * 1024
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_PROJECT_PAYLOAD_BYTES = 64 * 1024 * 1024


class ProjectBundleError(ValueError):
    """A bundle is invalid, unsafe, or cannot be written."""


@dataclass(frozen=True, slots=True)
class BundleAsset:
    original_reference: str
    asset_path: str = ""
    size: int = 0
    sha256: str = ""
    missing: bool = False
    data: bytes = b""

    def manifest_dict(self) -> dict[str, object]:
        value: dict[str, object] = {
            "original_reference": self.original_reference,
            "missing": self.missing,
        }
        if not self.missing:
            value.update(
                asset_path=self.asset_path,
                size=self.size,
                sha256=self.sha256,
            )
        return value


@dataclass(frozen=True, slots=True)
class BundleExportResult:
    bundle_path: Path
    asset_count: int
    missing_assets: tuple[str, ...]
    bundle_size: int


@dataclass(frozen=True, slots=True)
class BundleImportResult:
    project: Project
    project_path: Path
    destination: Path
    asset_count: int
    missing_assets: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExportProjectBundle:
    """Write a project and its referenced images into a portable ZIP."""

    repository: ProjectRepository

    def execute(
        self,
        project: Project,
        bundle_path: Path,
        *,
        base_dir: Path | None = None,
    ) -> BundleExportResult:
        bundle_path = Path(bundle_path)
        if bundle_path.is_dir():
            raise ProjectBundleError(f"bundle path is a directory: {bundle_path}")
        if not bundle_path.parent.is_dir():
            raise ProjectBundleError(f"bundle directory does not exist: {bundle_path.parent}")

        assets: list[BundleAsset] = []
        mapping: dict[str, str] = {}
        seen_paths: dict[Path, str] = {}
        used_asset_paths: set[str] = set()
        total_asset_bytes = 0
        asset_index = 0

        for reference in _collect_image_references(project):
            path = _resolve_reference(reference, base_dir)
            if path in seen_paths:
                mapping[reference] = seen_paths[path]
                continue
            if not path.is_file():
                assets.append(BundleAsset(original_reference=reference, missing=True))
                continue
            if asset_index >= MAX_ASSETS:
                raise ProjectBundleError(f"bundle has more than {MAX_ASSETS} assets")
            try:
                size = path.stat().st_size
            except OSError as exc:
                raise ProjectBundleError(f"could not read bundle asset {reference}: {exc}") from exc
            if size > MAX_ASSET_BYTES:
                raise ProjectBundleError(
                    f"asset is too large: {reference} ({size} bytes; "
                    f"limit is {MAX_ASSET_BYTES} bytes)"
                )
            total_asset_bytes += size
            if total_asset_bytes > MAX_UNCOMPRESSED_BYTES:
                raise ProjectBundleError(
                    f"bundle assets exceed the {MAX_UNCOMPRESSED_BYTES}-byte limit"
                )
            try:
                data = path.read_bytes()
            except OSError as exc:
                raise ProjectBundleError(f"could not read bundle asset {reference}: {exc}") from exc
            asset_index += 1
            asset_path = _asset_name(asset_index, path)
            while asset_path in used_asset_paths:
                asset_index += 1
                asset_path = _asset_name(asset_index, path)
            used_asset_paths.add(asset_path)
            asset = BundleAsset(
                original_reference=reference,
                asset_path=asset_path,
                size=len(data),
                sha256=hashlib.sha256(data).hexdigest(),
                data=data,
            )
            assets.append(asset)
            mapping[reference] = asset_path
            seen_paths[path] = asset_path

        bundled_project = _project_with_references(project, mapping)
        raise_if_errors(bundled_project.validate())
        payload = self.repository.prepare_payload(bundled_project)
        if len(payload) > MAX_PROJECT_PAYLOAD_BYTES:
            raise ProjectBundleError(
                f"project payload is too large ({len(payload)} bytes; "
                f"limit is {MAX_PROJECT_PAYLOAD_BYTES} bytes)"
            )

        missing = tuple(asset.original_reference for asset in assets if asset.missing)
        manifest = {
            "format": BUNDLE_FORMAT,
            "format_version": BUNDLE_FORMAT_VERSION,
            "application_version": __version__,
            "created_at": utc_now().isoformat(),
            "project_file": PROJECT_NAME,
            "project_name": project.name,
            "assets": [asset.manifest_dict() for asset in assets],
        }
        manifest_bytes = json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        if len(manifest_bytes) > MAX_MANIFEST_BYTES:
            raise ProjectBundleError("bundle manifest is too large")
        if total_asset_bytes + len(payload) + len(manifest_bytes) > MAX_UNCOMPRESSED_BYTES:
            raise ProjectBundleError(
                f"bundle exceeds the {MAX_UNCOMPRESSED_BYTES}-byte uncompressed limit"
            )

        _write_bundle(bundle_path, manifest_bytes, payload, assets)
        return BundleExportResult(
            bundle_path=bundle_path,
            asset_count=len(assets) - len(missing),
            missing_assets=missing,
            bundle_size=bundle_path.stat().st_size,
        )


@dataclass(frozen=True, slots=True)
class ImportProjectBundle:
    """Validate a bundle, extract it, and save a local project copy."""

    repository: ProjectRepository

    def execute(self, bundle_path: Path, destination_parent: Path) -> BundleImportResult:
        bundle_path = Path(bundle_path)
        destination_parent = Path(destination_parent)
        if not bundle_path.is_file():
            raise ProjectBundleError(f"bundle file not found: {bundle_path}")
        if not destination_parent.is_dir():
            raise ProjectBundleError(f"destination directory does not exist: {destination_parent}")
        try:
            if bundle_path.stat().st_size > MAX_BUNDLE_BYTES:
                raise ProjectBundleError(
                    f"bundle is too large ({bundle_path.stat().st_size} bytes; "
                    f"limit is {MAX_BUNDLE_BYTES} bytes)"
                )
            with zipfile.ZipFile(bundle_path) as archive:
                entries = _validate_entries(archive)
                manifest_assets, manifest_missing = _read_manifest(archive, entries)
                project = self._read_project(archive, entries)
                if not project.designs:
                    raise ProjectBundleError("bundle project has no designs")
                asset_data = _read_assets(archive, entries, manifest_assets)
        except zipfile.BadZipFile as exc:
            raise ProjectBundleError(f"bundle is not a valid ZIP file: {exc}") from exc
        except OSError as exc:
            raise ProjectBundleError(f"could not read bundle: {exc}") from exc

        destination = _unique_destination(destination_parent, project.name)
        try:
            (destination / ASSET_DIR).mkdir(parents=True, exist_ok=True)
            for asset_path, data in asset_data.items():
                target = destination.joinpath(*PurePosixPath(asset_path).parts)
                target.write_bytes(data)
            mapping: dict[str, str] = {}
            missing = list(manifest_missing)
            for reference in _collect_image_references(project):
                if reference.startswith(f"{ASSET_DIR}/"):
                    if reference in asset_data:
                        mapping[reference] = str(
                            destination.joinpath(*PurePosixPath(reference).parts).resolve()
                        )
                    else:
                        missing.append(reference)
                elif not Path(reference).expanduser().is_file():
                    missing.append(reference)
            imported = _project_with_references(project, mapping)
            project_path = destination / PROJECT_NAME
            self.repository.save(imported, project_path)
        except OSError as exc:
            shutil.rmtree(destination, ignore_errors=True)
            raise ProjectBundleError(f"could not write imported bundle: {exc}") from exc
        except Exception:
            shutil.rmtree(destination, ignore_errors=True)
            raise

        unique_missing = tuple(dict.fromkeys(missing))
        return BundleImportResult(
            project=imported,
            project_path=project_path,
            destination=destination,
            asset_count=len(asset_data),
            missing_assets=unique_missing,
        )

    def _read_project(
        self,
        archive: zipfile.ZipFile,
        entries: dict[str, zipfile.ZipInfo],
    ) -> Project:
        payload = _read_entry(archive, entries[PROJECT_NAME], MAX_PROJECT_PAYLOAD_BYTES)
        with tempfile.TemporaryDirectory(prefix="antennadesk-bundle-") as temporary:
            path = Path(temporary) / PROJECT_NAME
            path.write_bytes(payload)
            project = self.repository.load(path)
        raise_if_errors(project.validate())
        return project


def _collect_image_references(project: Project) -> tuple[str, ...]:
    references: list[str] = []
    for profile in project.installation_profiles:
        value = profile.image_reference.strip()
        if value:
            references.append(value)
    for entry in project.journal_entries:
        references.extend(value for value in entry.image_references if value.strip())
    return tuple(dict.fromkeys(references))


def _resolve_reference(reference: str, base_dir: Path | None) -> Path:
    path = Path(reference).expanduser()
    if not path.is_absolute():
        path = (base_dir or Path.cwd()) / path
    try:
        return path.resolve()
    except OSError:
        return path


def _asset_name(index: int, path: Path) -> str:
    suffix = path.suffix.lower()
    if not re.fullmatch(r"\.[A-Za-z0-9]{1,10}", suffix):
        suffix = ""
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", path.stem).strip("._-")
    stem = stem[:60] or "asset"
    return f"{ASSET_DIR}/{index:04d}-{stem}{suffix}"


def _project_with_references(project: Project, mapping: dict[str, str]) -> Project:
    profiles = tuple(
        replace(
            profile,
            image_reference=mapping.get(
                profile.image_reference.strip(),
                profile.image_reference,
            ),
        )
        for profile in project.installation_profiles
    )
    entries = tuple(
        replace(
            entry,
            image_references=tuple(
                mapping.get(reference, reference) for reference in entry.image_references
            ),
        )
        for entry in project.journal_entries
    )
    return replace(
        project,
        installation_profiles=profiles,
        journal_entries=entries,
    )


def _write_bundle(
    path: Path,
    manifest_bytes: bytes,
    project_payload: bytes,
    assets: list[BundleAsset],
) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
        ) as archive:
            archive.writestr(MANIFEST_NAME, manifest_bytes)
            archive.writestr(PROJECT_NAME, project_payload)
            for asset in assets:
                if not asset.missing:
                    archive.writestr(asset.asset_path, asset.data)
        size = temporary.stat().st_size
        if size > MAX_BUNDLE_BYTES:
            raise ProjectBundleError(
                f"bundle is too large ({size} bytes; limit is {MAX_BUNDLE_BYTES} bytes)"
            )
        os.replace(temporary, path)
    except OSError as exc:
        raise ProjectBundleError(f"could not write bundle: {exc}") from exc
    finally:
        temporary.unlink(missing_ok=True)


def _validate_entries(archive: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    entries: dict[str, zipfile.ZipInfo] = {}
    total_size = 0
    for info in archive.infolist():
        name = info.filename
        if name == f"{ASSET_DIR}/":
            continue
        if not name or name.endswith("/"):
            raise ProjectBundleError(f"unexpected bundle directory: {name!r}")
        if name in entries:
            raise ProjectBundleError(f"duplicate bundle entry: {name}")
        _validate_entry_name(name)
        if info.flag_bits & 0x1:
            raise ProjectBundleError(f"encrypted bundle entry is not supported: {name}")
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise ProjectBundleError(f"symbolic links are not allowed in a bundle: {name}")
        if name == MANIFEST_NAME:
            limit = MAX_MANIFEST_BYTES
        elif name == PROJECT_NAME:
            limit = MAX_PROJECT_PAYLOAD_BYTES
        elif name.startswith(f"{ASSET_DIR}/"):
            limit = MAX_ASSET_BYTES
        else:
            raise ProjectBundleError(f"unexpected bundle entry: {name}")
        if info.file_size > limit:
            raise ProjectBundleError(
                f"bundle entry is too large: {name} ({info.file_size} bytes; "
                f"limit is {limit} bytes)"
            )
        total_size += info.file_size
        if total_size > MAX_UNCOMPRESSED_BYTES:
            raise ProjectBundleError(
                f"bundle exceeds the {MAX_UNCOMPRESSED_BYTES}-byte uncompressed limit"
            )
        entries[name] = info
    if MANIFEST_NAME not in entries or PROJECT_NAME not in entries:
        raise ProjectBundleError("bundle is missing its manifest or project file")
    if sum(1 for name in entries if name.startswith(f"{ASSET_DIR}/")) > MAX_ASSETS:
        raise ProjectBundleError(f"bundle has more than {MAX_ASSETS} assets")
    return entries


def _validate_entry_name(name: str) -> None:
    if "\\" in name or "\x00" in name or name.startswith("/"):
        raise ProjectBundleError(f"unsafe bundle entry: {name!r}")
    if name.startswith("./") or "/./" in name or "/../" in name or name == "..":
        raise ProjectBundleError(f"unsafe bundle entry: {name!r}")
    parts = PurePosixPath(name).parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise ProjectBundleError(f"unsafe bundle entry: {name!r}")
    if any(":" in part for part in parts):
        raise ProjectBundleError(f"unsafe bundle entry: {name!r}")
    if name in (MANIFEST_NAME, PROJECT_NAME):
        return
    if name.startswith(f"{ASSET_DIR}/"):
        if len(parts) != 2 or not parts[1]:
            raise ProjectBundleError(f"assets must be flat files: {name!r}")
        return
    raise ProjectBundleError(f"unexpected bundle entry: {name}")


def _read_manifest(
    archive: zipfile.ZipFile,
    entries: dict[str, zipfile.ZipInfo],
) -> tuple[tuple[BundleAsset, ...], tuple[str, ...]]:
    raw = _read_entry(archive, entries[MANIFEST_NAME], MAX_MANIFEST_BYTES)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProjectBundleError(f"invalid bundle manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise ProjectBundleError("bundle manifest root must be an object")
    if value.get("format") != BUNDLE_FORMAT:
        raise ProjectBundleError("unsupported bundle format")
    if value.get("format_version") != BUNDLE_FORMAT_VERSION:
        raise ProjectBundleError("unsupported bundle format version")
    if value.get("project_file") != PROJECT_NAME:
        raise ProjectBundleError("bundle manifest has an unexpected project file")
    raw_assets = value.get("assets")
    if not isinstance(raw_assets, list):
        raise ProjectBundleError("bundle manifest assets must be a list")
    assets: list[BundleAsset] = []
    missing: list[str] = []
    used_paths: set[str] = set()
    for item in raw_assets:
        if not isinstance(item, dict):
            raise ProjectBundleError("bundle manifest asset must be an object")
        reference = item.get("original_reference")
        if not isinstance(reference, str) or not reference.strip():
            raise ProjectBundleError("bundle asset reference must not be empty")
        is_missing = item.get("missing", False)
        if not isinstance(is_missing, bool):
            raise ProjectBundleError("bundle asset missing flag must be a boolean")
        if is_missing:
            assets.append(BundleAsset(original_reference=reference, missing=True))
            missing.append(reference)
            continue
        asset_path = item.get("asset_path")
        size = item.get("size")
        digest = item.get("sha256")
        if (
            not isinstance(asset_path, str)
            or not isinstance(size, int)
            or not isinstance(digest, str)
        ):
            raise ProjectBundleError("bundle asset is missing its path, size, or hash")
        _validate_entry_name(asset_path)
        if not asset_path.startswith(f"{ASSET_DIR}/"):
            raise ProjectBundleError("bundle asset path must be under assets/")
        if asset_path in used_paths:
            raise ProjectBundleError(f"duplicate bundle asset path: {asset_path}")
        if size < 0 or size > MAX_ASSET_BYTES:
            raise ProjectBundleError(f"bundle asset size is invalid: {asset_path}")
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ProjectBundleError(f"bundle asset hash is invalid: {asset_path}")
        used_paths.add(asset_path)
        assets.append(
            BundleAsset(
                original_reference=reference,
                asset_path=asset_path,
                size=size,
                sha256=digest,
            )
        )
    if len(assets) > MAX_ASSETS:
        raise ProjectBundleError(f"bundle has more than {MAX_ASSETS} assets")
    return tuple(assets), tuple(missing)


def _read_assets(
    archive: zipfile.ZipFile,
    entries: dict[str, zipfile.ZipInfo],
    manifest_assets: tuple[BundleAsset, ...],
) -> dict[str, bytes]:
    expected = {asset.asset_path for asset in manifest_assets if not asset.missing}
    actual = {name for name in entries if name.startswith(f"{ASSET_DIR}/")}
    if actual != expected:
        raise ProjectBundleError("bundle asset list does not match the archive contents")
    data: dict[str, bytes] = {}
    for asset in manifest_assets:
        if asset.missing:
            continue
        payload = _read_entry(archive, entries[asset.asset_path], MAX_ASSET_BYTES)
        if len(payload) != asset.size:
            raise ProjectBundleError(f"bundle asset size mismatch: {asset.asset_path}")
        if hashlib.sha256(payload).hexdigest() != asset.sha256:
            raise ProjectBundleError(f"bundle asset checksum mismatch: {asset.asset_path}")
        data[asset.asset_path] = payload
    return data


def _read_entry(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    limit: int,
) -> bytes:
    with archive.open(info) as handle:
        payload = handle.read(limit + 1)
    if len(payload) > limit:
        raise ProjectBundleError(f"bundle entry is too large: {info.filename}")
    return payload


def _unique_destination(parent: Path, project_name: str) -> Path:
    base = _safe_folder_name(project_name)
    candidate = parent / base
    counter = 2
    while candidate.exists():
        candidate = parent / f"{base} ({counter})"
        counter += 1
    try:
        candidate.mkdir()
    except FileExistsError as exc:
        raise ProjectBundleError(f"could not create bundle destination: {candidate}") from exc
    return candidate


def _safe_folder_name(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._ -]+", "-", name).strip(" .-")
    return value[:80] or "AntennaDesk project"
