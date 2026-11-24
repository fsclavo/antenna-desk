# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validated, deterministic ZIP project container.

The container replaces the previous gzip JSON envelope. It keeps the project
metadata, each design, each simulation run, optional raw solver text, and each
optimization summary in separate entries so limits are enforceable per entry
and a future session can load runs lazily.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import tempfile
import zipfile
import zlib
from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Literal, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .. import __version__
from ..application.project_limits import (
    MAX_CONTAINER_BYTES,
    MAX_ENTRIES,
    MAX_ENTRY_BYTES,
    MAX_MANIFEST_BYTES,
    MAX_PATH_BYTES,
    MAX_PROJECT_UNCOMPRESSED_BYTES,
)
from ..application.project_payload import PreparedProject, ProjectLimits
from ..application.project_session import (
    ProjectSession,
)
from ..application.project_session import (
    RunIndexEntry as ApplicationRunIndexEntry,
)
from ..domain.projects.project import Project
from ..domain.simulation.run import SimulationRun
from .constants import (
    CONTAINER_FORMAT,
    CONTAINER_VERSION,
    PROJECT_FORMAT,
    SCHEMA_VERSION,
)
from .errors import ProjectFormatError, ProjectTooLargeError, UnsupportedSchemaVersion
from .schema import (
    DesignPayload,
    OptimizationSummaryPayload,
    ProjectDocument,
    ProjectMetadataDocument,
    ProjectMetadataPayload,
    ProjectPayload,
    SimulationRunPayload,
    document_from_project,
    project_from_document,
    simulation_run_from_payload,
)

MANIFEST_NAME = "manifest.json"
PROJECT_NAME = "project.json"
DESIGN_DIR = "designs"
RUN_DIR = "runs"
OPTIMIZATION_DIR = "optimizations"
RAW_INPUT_SUFFIX = ".raw-input.txt"
RAW_OUTPUT_SUFFIX = ".raw-output.txt"

DESIGN_FORMAT: Literal["antennadesk.design"] = "antennadesk.design"
RUN_FORMAT: Literal["antennadesk.run"] = "antennadesk.run"
OPTIMIZATION_FORMAT: Literal["antennadesk.optimization"] = "antennadesk.optimization"

_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

_ModelT = TypeVar("_ModelT", bound=BaseModel)
_ENTRY_NAME = re.compile(r"^[A-Za-z0-9._/-]+$")


class ContainerModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        allow_inf_nan=False,
    )


EntryKind = Literal[
    "metadata",
    "design",
    "run",
    "raw-input",
    "raw-output",
    "optimization",
]


class ManifestEntry(ContainerModel):
    path: str = Field(min_length=1)
    kind: EntryKind
    uncompressed_bytes: int = Field(ge=0)
    compressed_bytes: int = Field(ge=0)
    crc32: int = Field(ge=0, le=0xFFFFFFFF)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class RunIndexEntry(ContainerModel):
    id: UUID
    design_id: UUID
    created_at: datetime
    band_id: str | None = None
    batch_id: UUID | None = None

    @model_validator(mode="after")
    def _validate(self) -> RunIndexEntry:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("run created_at must be timezone-aware")
        if self.band_id is None and self.batch_id is not None:
            raise ValueError("a band-analysis run requires a band_id")
        if self.band_id is not None and self.batch_id is None:
            raise ValueError("a band run requires a batch_id")
        return self


class RetentionPayload(ContainerModel):
    retained_run_ids: list[UUID] = Field(default_factory=list)


class ProjectManifest(ContainerModel):
    format: Literal["antennadesk.project"]
    container_version: int = Field(ge=1)
    schema_version: int = Field(ge=1)
    project_id: UUID
    project_name: str = Field(min_length=1)
    application_version: str = Field(min_length=1)
    created_at: datetime
    updated_at: datetime
    design_ids: list[UUID] = Field(default_factory=list)
    runs: list[RunIndexEntry] = Field(default_factory=list)
    entries: list[ManifestEntry] = Field(default_factory=list)
    retention: RetentionPayload = Field(default_factory=RetentionPayload)

    @model_validator(mode="after")
    def _validate_entries(self) -> ProjectManifest:
        paths = [entry.path for entry in self.entries]
        if len(paths) != len(set(paths)):
            raise ValueError("duplicate manifest entry path")
        folded = [path.casefold() for path in paths]
        if len(folded) != len(set(folded)):
            raise ValueError("case-insensitive duplicate manifest entry path")
        if MANIFEST_NAME in paths:
            raise ValueError("manifest.json must not list itself")
        if PROJECT_NAME not in paths:
            raise ValueError("manifest is missing the project metadata entry")
        if len(self.design_ids) != len(set(self.design_ids)):
            raise ValueError("duplicate manifest design id")
        run_ids = [run.id for run in self.runs]
        if len(run_ids) != len(set(run_ids)):
            raise ValueError("duplicate manifest run id")
        known_designs = set(self.design_ids)
        for run in self.runs:
            if run.design_id not in known_designs:
                raise ValueError("manifest run references an unknown design")
        for name, value in (
            ("created_at", self.created_at),
            ("updated_at", self.updated_at),
        ):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be earlier than created_at")
        return self


class DesignDocument(ContainerModel):
    format: Literal["antennadesk.design"]
    schema_version: int
    design: DesignPayload

    @model_validator(mode="after")
    def _validate(self) -> DesignDocument:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported design schema version")
        if self.design.optimization_summary is not None:
            raise ValueError("design entry must not embed an optimization summary")
        return self


class RunDocument(ContainerModel):
    format: Literal["antennadesk.run"]
    schema_version: int
    run: SimulationRunPayload

    @model_validator(mode="after")
    def _validate(self) -> RunDocument:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported run schema version")
        return self


class OptimizationDocument(ContainerModel):
    format: Literal["antennadesk.optimization"]
    schema_version: int
    design_id: UUID
    summary: OptimizationSummaryPayload

    @model_validator(mode="after")
    def _validate(self) -> OptimizationDocument:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported optimization schema version")
        return self


@dataclass(frozen=True, slots=True)
class _Entry:
    kind: EntryKind
    data: bytes


class ProjectContainerRepository:
    """Read and write versioned ZIP project containers.

    The reader accepts container version 1 and the current schema, plus the
    migration path for schema 59 and 60. Previous gzip/plain-JSON files are
    rejected deliberately; the project has not shipped to users yet.
    """

    # -- public repository API ------------------------------------------------

    def save(self, project: Project, path: Path) -> None:
        self.write_payload(path, self.prepare_payload(project))

    def prepare_payload(self, project: Project) -> PreparedProject:
        entries = self._build_entries(project)
        self._check_entry_limits(entries)
        payload, manifest_bytes = self._build_container(project, entries)
        return self._prepared(entries, payload, manifest_bytes)

    def prepare_session_payload(
        self,
        session: ProjectSession,
        project: Project,
        *,
        retained_only: bool = False,
    ) -> PreparedProject:
        """Prepare a save that copies unloaded runs instead of materializing them.

        Runs already present in ``project.simulation_runs`` are serialized
        normally. Unchanged runs are copied as validated container entries from
        the session's source container. If a custom store or a compaction with
        new in-memory runs makes that impossible, the call falls back to a full
        materialization.
        """

        store = session.run_store
        if not isinstance(store, ContainerRunStore) or (retained_only and project.simulation_runs):
            full = session.materialize()
            if project.simulation_runs:
                merged = {run.id: run for run in full.simulation_runs}
                merged.update({run.id: run for run in project.simulation_runs})
                full = replace(full, simulation_runs=tuple(merged.values()))
            if retained_only:
                full = full.with_latest_simulation_runs_only(updated_at=project.updated_at)
            return self.prepare_payload(full)

        entries = self._build_entries(project)
        design_ids = {design.id for design in project.designs}
        existing_ids = {run.id for run in project.simulation_runs}
        retained_ids = set(session.retained_run_ids())
        source_runs = [
            index
            for index in store.run_index
            if index.design_id in design_ids
            and index.id not in existing_ids
            and (not retained_only or index.id in retained_ids)
        ]
        copied = store.copy_entries([index.id for index in source_runs])
        for path, data in copied.items():
            kind = _kind_for_path(path)
            if kind is None:
                raise ProjectFormatError(f"unexpected copied run entry: {path}")
            entries[path] = _Entry(kind, data)
        runs = [
            RunIndexEntry(
                id=index.id,
                design_id=index.design_id,
                created_at=index.created_at,
                band_id=index.band_id,
                batch_id=index.batch_id,
            )
            for index in source_runs
        ] + [
            RunIndexEntry(
                id=run.id,
                design_id=run.design_id,
                created_at=run.created_at,
                band_id=run.band_id,
                batch_id=run.batch_id,
            )
            for run in project.simulation_runs
        ]
        retained = [index.id for index in source_runs if index.id in retained_ids] + [
            run.id for run in project.simulation_runs
        ]
        self._check_entry_limits(entries)
        payload, manifest_bytes = self._build_container(
            project,
            entries,
            runs=runs,
            retained_run_ids=retained,
        )
        return self._prepared(entries, payload, manifest_bytes)

    def _prepared(
        self,
        entries: dict[str, _Entry],
        payload: bytes,
        manifest_bytes: int,
    ) -> PreparedProject:
        expanded = sum(len(entry.data) for entry in entries.values()) + manifest_bytes
        if expanded > MAX_PROJECT_UNCOMPRESSED_BYTES:
            raise ProjectTooLargeError(
                "project entries are too large when expanded "
                f"({expanded} bytes; limit is {MAX_PROJECT_UNCOMPRESSED_BYTES} bytes)",
                size=expanded,
                limit=MAX_PROJECT_UNCOMPRESSED_BYTES,
                expanded=True,
            )
        if len(payload) > MAX_CONTAINER_BYTES:
            raise ProjectTooLargeError(
                "project container is too large "
                f"({len(payload)} bytes; limit is {MAX_CONTAINER_BYTES} bytes)",
                size=len(payload),
                limit=MAX_CONTAINER_BYTES,
                expanded=False,
            )
        return PreparedProject(
            payload=payload,
            entry_count=len(entries) + 1,
            expanded_bytes=expanded,
            limits=ProjectLimits(
                container_bytes=MAX_CONTAINER_BYTES,
                expanded_bytes=MAX_PROJECT_UNCOMPRESSED_BYTES,
                manifest_bytes=MAX_MANIFEST_BYTES,
                entry_bytes=MAX_ENTRY_BYTES,
                entries=MAX_ENTRIES,
                path_bytes=MAX_PATH_BYTES,
            ),
        )

    def write_payload(self, path: Path, payload: PreparedProject) -> None:
        if payload.compressed_bytes > MAX_CONTAINER_BYTES:
            raise ProjectTooLargeError(
                "project container is too large "
                f"({payload.compressed_bytes} bytes; limit is {MAX_CONTAINER_BYTES} bytes)",
                size=payload.compressed_bytes,
                limit=MAX_CONTAINER_BYTES,
                expanded=False,
            )
        if not zipfile.is_zipfile(io.BytesIO(payload.payload)):
            raise ProjectFormatError("prepared project payload is not a valid ZIP container")
        self._atomic_write(Path(path), payload.payload)

    def load(self, path: Path) -> Project:
        return self.open_session(path).materialize()

    def open_session(self, path: Path) -> ProjectSession:
        path = self._check_path(path)
        try:
            with zipfile.ZipFile(path) as archive:
                infos = archive.infolist()
                self._validate_archive_entries(infos)
                manifest = self._require_manifest(archive, infos)
                listed = {entry.path: entry for entry in manifest.entries}
                self._check_entry_set(infos, listed)
                metadata_entries = {
                    entry_path: entry
                    for entry_path, entry in listed.items()
                    if not _is_run_entry(entry_path)
                }
                data = self._read_entries(archive, infos, metadata_entries)
                metadata = self._parse_document(
                    ProjectMetadataDocument,
                    data[PROJECT_NAME],
                    PROJECT_NAME,
                )
                designs = self._read_designs(data)
                self._check_manifest_index(manifest, designs)
                project = self._project_from_parts(metadata, designs, [])
                return ProjectSession(project, ContainerRunStore(path, manifest, self))
        except zipfile.BadZipFile as exc:
            with path.open("rb") as handle:
                first = handle.read(1)
            if first in (b"{", b"\x1f"):
                raise ProjectFormatError(
                    "unsupported legacy project format; resave the project with this version"
                ) from exc
            raise ProjectFormatError(f"project container is not a valid ZIP file: {exc}") from exc
        except OSError as exc:
            raise ProjectFormatError(f"could not read project file: {exc}") from exc

    def open_design_only(self, path: Path) -> Project:
        """Recover the metadata and designs while ignoring every run entry."""

        path = self._check_path(path)
        try:
            with zipfile.ZipFile(path) as archive:
                infos = archive.infolist()
                self._validate_archive_entries(infos)
                manifest = self._require_manifest(archive, infos)
                listed = {entry.path: entry for entry in manifest.entries}
                actual = {info.filename for info in infos}
                metadata_entries = {
                    entry_path: entry
                    for entry_path, entry in listed.items()
                    if not _is_run_entry(entry_path) and entry_path in actual
                }
                if PROJECT_NAME not in metadata_entries:
                    raise ProjectFormatError(
                        "project container is missing the metadata entry for recovery"
                    )
                data = self._read_entries(archive, infos, metadata_entries)
                metadata = self._parse_document(
                    ProjectMetadataDocument,
                    data[PROJECT_NAME],
                    PROJECT_NAME,
                )
                designs = self._read_designs(data)
                return self._project_from_parts(metadata, designs, [])
        except zipfile.BadZipFile as exc:
            raise ProjectFormatError(f"project container is not a valid ZIP file: {exc}") from exc
        except OSError as exc:
            raise ProjectFormatError(f"could not read project file: {exc}") from exc

    def _check_path(self, path: Path) -> Path:
        path = Path(path)
        if not path.is_file():
            raise ProjectFormatError(f"project file not found: {path}")
        try:
            size = path.stat().st_size
        except OSError as exc:
            raise ProjectFormatError(f"could not read project file: {exc}") from exc
        if size > MAX_CONTAINER_BYTES:
            raise ProjectTooLargeError(
                "project container is too large "
                f"({size} bytes; limit is {MAX_CONTAINER_BYTES} bytes)",
                size=size,
                limit=MAX_CONTAINER_BYTES,
                expanded=False,
            )
        return path

    def _require_manifest(
        self,
        archive: zipfile.ZipFile,
        infos: list[zipfile.ZipInfo],
    ) -> ProjectManifest:
        manifest_info = next(
            (info for info in infos if info.filename == MANIFEST_NAME),
            None,
        )
        if manifest_info is None:
            raise ProjectFormatError("project container is missing manifest.json")
        manifest = self._read_manifest(archive, manifest_info)
        if manifest.container_version != CONTAINER_VERSION:
            raise ProjectFormatError(
                f"unsupported project container version {manifest.container_version}"
            )
        if manifest.schema_version not in (59, 60, SCHEMA_VERSION):
            raise UnsupportedSchemaVersion(
                found=manifest.schema_version,
                supported=SCHEMA_VERSION,
            )
        if manifest.schema_version != SCHEMA_VERSION:
            manifest = manifest.model_copy(update={"schema_version": SCHEMA_VERSION})
        return manifest

    @staticmethod
    def _check_entry_set(
        infos: list[zipfile.ZipInfo],
        listed: dict[str, ManifestEntry],
    ) -> None:
        actual = {info.filename for info in infos if info.filename != MANIFEST_NAME}
        if set(listed) != actual:
            missing = sorted(set(listed) - actual)
            extra = sorted(actual - set(listed))
            raise ProjectFormatError(
                f"manifest/ZIP entry mismatch (missing={missing}, extra={extra})"
            )

    def _check_manifest_index(
        self,
        manifest: ProjectManifest,
        designs: list[DesignPayload],
    ) -> None:
        design_ids = {design.id for design in designs}
        if set(manifest.design_ids) != design_ids:
            raise ProjectFormatError("manifest design index does not match the design entries")
        run_ids = {entry.id for entry in manifest.runs}
        zip_run_ids = {
            _uuid_from_path(entry.path, RUN_DIR, ".json")
            for entry in manifest.entries
            if entry.path.startswith(f"{RUN_DIR}/") and entry.path.endswith(".json")
        }
        if run_ids != zip_run_ids:
            raise ProjectFormatError("manifest run index does not match the run entries")

    def _project_from_parts(
        self,
        metadata: ProjectMetadataDocument,
        designs: list[DesignPayload],
        runs: list[SimulationRunPayload],
    ) -> Project:
        try:
            payload = ProjectPayload(
                **metadata.project.model_dump(mode="json"),
                designs=designs,
                simulation_runs=runs,
            )
            document = ProjectDocument(
                format=PROJECT_FORMAT,
                schema_version=SCHEMA_VERSION,
                project=payload,
            )
            return project_from_document(document)
        except ValidationError as exc:
            raise ProjectFormatError(f"invalid project data: {exc}") from exc
        except ValueError as exc:
            raise ProjectFormatError(f"invalid project data: {exc}") from exc

    def serialized_size(self, project: Project) -> int:
        return self.prepare_payload(project).compressed_bytes

    # -- write ----------------------------------------------------------------

    def _build_entries(self, project: Project) -> dict[str, _Entry]:
        document = document_from_project(project)
        payload = document.project
        project_data = payload.model_dump(mode="json")
        project_data.pop("designs", None)
        project_data.pop("simulation_runs", None)
        metadata = ProjectMetadataDocument(
            format=PROJECT_FORMAT,
            schema_version=SCHEMA_VERSION,
            project=ProjectMetadataPayload.model_validate(project_data),
        )
        entries: dict[str, _Entry] = {
            PROJECT_NAME: _Entry("metadata", _json_bytes(metadata)),
        }
        for design in payload.designs:
            design_data = design.model_dump(mode="json")
            summary = design_data.pop("optimization_summary", None)
            design_document = DesignDocument(
                format=DESIGN_FORMAT,
                schema_version=SCHEMA_VERSION,
                design=DesignPayload.model_validate(design_data),
            )
            entries[f"{DESIGN_DIR}/{design.id}.json"] = _Entry(
                "design",
                _json_bytes(design_document),
            )
            if summary is not None:
                optimization = OptimizationDocument(
                    format=OPTIMIZATION_FORMAT,
                    schema_version=SCHEMA_VERSION,
                    design_id=design.id,
                    summary=OptimizationSummaryPayload.model_validate(summary),
                )
                entries[f"{OPTIMIZATION_DIR}/{design.id}.json"] = _Entry(
                    "optimization",
                    _json_bytes(optimization),
                )
        for run in payload.simulation_runs:
            run_data = run.model_dump(mode="json")
            result = run_data["result"]
            raw_input = result.pop("raw_input", "")
            raw_output = result.pop("raw_output", "")
            run_document = RunDocument(
                format=RUN_FORMAT,
                schema_version=SCHEMA_VERSION,
                run=SimulationRunPayload.model_validate(run_data),
            )
            entries[f"{RUN_DIR}/{run.id}.json"] = _Entry("run", _json_bytes(run_document))
            if raw_input:
                entries[f"{RUN_DIR}/{run.id}{RAW_INPUT_SUFFIX}"] = _Entry(
                    "raw-input",
                    raw_input.encode("utf-8"),
                )
            if raw_output:
                entries[f"{RUN_DIR}/{run.id}{RAW_OUTPUT_SUFFIX}"] = _Entry(
                    "raw-output",
                    raw_output.encode("utf-8"),
                )
        return entries

    def _build_container(
        self,
        project: Project,
        entries: dict[str, _Entry],
        *,
        runs: list[RunIndexEntry] | None = None,
        retained_run_ids: list[UUID] | None = None,
    ) -> tuple[bytes, int]:
        preliminary = _zip_bytes(entries)
        with zipfile.ZipFile(io.BytesIO(preliminary)) as archive:
            compressed = {info.filename: info.compress_size for info in archive.infolist()}
        manifest_entries = []
        for path, entry in entries.items():
            manifest_entries.append(
                ManifestEntry(
                    path=path,
                    kind=entry.kind,
                    uncompressed_bytes=len(entry.data),
                    compressed_bytes=compressed[path],
                    crc32=zlib.crc32(entry.data) & 0xFFFFFFFF,
                    sha256=hashlib.sha256(entry.data).hexdigest(),
                )
            )
        if runs is None:
            runs = [
                RunIndexEntry(
                    id=run.id,
                    design_id=run.design_id,
                    created_at=run.created_at,
                    band_id=run.band_id,
                    batch_id=run.batch_id,
                )
                for run in project.simulation_runs
            ]
        if retained_run_ids is None:
            retained_run_ids = [run.id for run in project.retained_simulation_runs()]
        manifest = ProjectManifest(
            format=CONTAINER_FORMAT,
            container_version=CONTAINER_VERSION,
            schema_version=SCHEMA_VERSION,
            project_id=project.id,
            project_name=project.name,
            application_version=__version__,
            created_at=project.created_at,
            updated_at=project.updated_at,
            design_ids=[design.id for design in project.designs],
            runs=runs,
            entries=manifest_entries,
            retention=RetentionPayload(retained_run_ids=retained_run_ids),
        )
        manifest_bytes = _json_bytes(manifest)
        if len(manifest_bytes) > MAX_MANIFEST_BYTES:
            raise ProjectTooLargeError(
                "project manifest is too large "
                f"({len(manifest_bytes)} bytes; limit is {MAX_MANIFEST_BYTES} bytes)",
                size=len(manifest_bytes),
                limit=MAX_MANIFEST_BYTES,
                expanded=True,
            )
        return _zip_bytes(entries, manifest_bytes), len(manifest_bytes)

    def _check_entry_limits(self, entries: dict[str, _Entry]) -> None:
        if len(entries) + 1 > MAX_ENTRIES:
            raise ProjectTooLargeError(
                f"project container has too many entries ({len(entries) + 1}; "
                f"limit is {MAX_ENTRIES})",
                size=len(entries) + 1,
                limit=MAX_ENTRIES,
                expanded=False,
            )
        total = 0
        for path, entry in entries.items():
            if len(path.encode("utf-8")) > MAX_PATH_BYTES:
                raise ProjectTooLargeError(
                    f"project entry path is too long ({path!r})",
                    size=len(path),
                    limit=MAX_PATH_BYTES,
                    expanded=False,
                )
            if len(entry.data) > MAX_ENTRY_BYTES:
                raise ProjectTooLargeError(
                    f"project entry {path} is too large "
                    f"({len(entry.data)} bytes; limit is {MAX_ENTRY_BYTES} bytes)",
                    size=len(entry.data),
                    limit=MAX_ENTRY_BYTES,
                    expanded=True,
                )
            total += len(entry.data)
        if total > MAX_PROJECT_UNCOMPRESSED_BYTES:
            raise ProjectTooLargeError(
                "project entries are too large when expanded "
                f"({total} bytes; limit is {MAX_PROJECT_UNCOMPRESSED_BYTES} bytes)",
                size=total,
                limit=MAX_PROJECT_UNCOMPRESSED_BYTES,
                expanded=True,
            )

    # -- read -----------------------------------------------------------------

    def _validate_archive_entries(self, infos: list[zipfile.ZipInfo]) -> None:
        if len(infos) > MAX_ENTRIES:
            raise ProjectTooLargeError(
                f"project container has too many entries ({len(infos)}; limit is {MAX_ENTRIES})",
                size=len(infos),
                limit=MAX_ENTRIES,
                expanded=False,
            )
        names: list[str] = []
        for info in infos:
            name = info.filename
            if not name or name.endswith("/"):
                raise ProjectFormatError(f"invalid project entry name: {name!r}")
            self._validate_path(name)
            if info.flag_bits & 0x1:
                raise ProjectFormatError(f"encrypted project entries are not supported: {name}")
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise ProjectFormatError(f"symbolic links are not supported: {name}")
            if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                raise ProjectFormatError(
                    f"unsupported compression method for project entry: {name}"
                )
            names.append(name)
        if len(names) != len(set(names)):
            raise ProjectFormatError("duplicate project entry name")
        folded = [name.casefold() for name in names]
        if len(folded) != len(set(folded)):
            raise ProjectFormatError("case-insensitive duplicate project entry name")

    def _read_manifest(
        self,
        archive: zipfile.ZipFile,
        info: zipfile.ZipInfo,
    ) -> ProjectManifest:
        if info.file_size > MAX_MANIFEST_BYTES:
            raise ProjectTooLargeError(
                f"project manifest is too large ({info.file_size} bytes; "
                f"limit is {MAX_MANIFEST_BYTES} bytes)",
                size=info.file_size,
                limit=MAX_MANIFEST_BYTES,
                expanded=True,
            )
        data = self._read_bounded(archive, info, MAX_MANIFEST_BYTES)
        try:
            return ProjectManifest.model_validate_json(data)
        except ValidationError as exc:
            raise ProjectFormatError(f"invalid project manifest: {exc}") from exc
        except ValueError as exc:
            raise ProjectFormatError(f"invalid project manifest: {exc}") from exc

    def _read_entries(
        self,
        archive: zipfile.ZipFile,
        infos: list[zipfile.ZipInfo],
        listed: dict[str, ManifestEntry],
    ) -> dict[str, bytes]:
        data: dict[str, bytes] = {}
        total = 0
        by_name = {info.filename: info for info in infos}
        for path, entry in listed.items():
            info = by_name[path]
            if info.file_size > MAX_ENTRY_BYTES:
                raise ProjectTooLargeError(
                    f"project entry {path} is too large ({info.file_size} bytes; "
                    f"limit is {MAX_ENTRY_BYTES} bytes)",
                    size=info.file_size,
                    limit=MAX_ENTRY_BYTES,
                    expanded=True,
                )
            payload = self._read_bounded(archive, info, MAX_ENTRY_BYTES)
            total += len(payload)
            if total > MAX_PROJECT_UNCOMPRESSED_BYTES:
                raise ProjectTooLargeError(
                    "project entries are too large when expanded "
                    f"({total} bytes; limit is {MAX_PROJECT_UNCOMPRESSED_BYTES} bytes)",
                    size=total,
                    limit=MAX_PROJECT_UNCOMPRESSED_BYTES,
                    expanded=True,
                )
            if len(payload) != entry.uncompressed_bytes:
                raise ProjectFormatError(f"size mismatch for project entry {path}")
            if info.compress_size != entry.compressed_bytes:
                raise ProjectFormatError(f"compressed size mismatch for project entry {path}")
            if zlib.crc32(payload) & 0xFFFFFFFF != entry.crc32:
                raise ProjectFormatError(f"CRC mismatch for project entry {path}")
            if hashlib.sha256(payload).hexdigest() != entry.sha256:
                raise ProjectFormatError(f"SHA-256 mismatch for project entry {path}")
            if entry.kind != _kind_for_path(path):
                raise ProjectFormatError(f"manifest kind does not match entry path: {path}")
            data[path] = payload
        return data

    def _read_designs(self, data: dict[str, bytes]) -> list[DesignPayload]:
        summaries: dict[UUID, OptimizationSummaryPayload] = {}
        for path, payload in data.items():
            if not path.startswith(f"{OPTIMIZATION_DIR}/"):
                continue
            optimization_document = self._parse_document(OptimizationDocument, payload, path)
            design_id = _uuid_from_path(path, OPTIMIZATION_DIR, ".json")
            if optimization_document.design_id != design_id:
                raise ProjectFormatError(f"optimization design id does not match {path}")
            if design_id in summaries:
                raise ProjectFormatError(f"duplicate optimization entry for {design_id}")
            summaries[design_id] = optimization_document.summary
        designs: list[DesignPayload] = []
        design_ids: set[UUID] = set()
        for path, payload in data.items():
            if not path.startswith(f"{DESIGN_DIR}/"):
                continue
            design_document = self._parse_document(DesignDocument, payload, path)
            design_id = _uuid_from_path(path, DESIGN_DIR, ".json")
            if design_id != design_document.design.id:
                raise ProjectFormatError(f"design id does not match {path}")
            if design_id in design_ids:
                raise ProjectFormatError(f"duplicate design entry for {design_id}")
            design_ids.add(design_id)
            summary = summaries.pop(design_id, None)
            design_data = design_document.design.model_dump(mode="json")
            if summary is not None:
                design_data["optimization_summary"] = summary.model_dump(mode="json")
            designs.append(DesignPayload.model_validate(design_data))
        if summaries:
            raise ProjectFormatError(
                f"optimization entries reference unknown designs: {sorted(summaries)}"
            )
        return designs

    def _read_runs(self, data: dict[str, bytes]) -> list[SimulationRunPayload]:
        runs: dict[UUID, SimulationRunPayload] = {}
        for path, payload in data.items():
            if not path.startswith(f"{RUN_DIR}/") or not path.endswith(".json"):
                continue
            document = self._parse_document(RunDocument, payload, path)
            run_id = _uuid_from_path(path, RUN_DIR, ".json")
            if document.run.id != run_id:
                raise ProjectFormatError(f"run id does not match {path}")
            runs[run_id] = document.run
        for path, payload in data.items():
            if not path.startswith(f"{RUN_DIR}/") or not path.endswith(
                (RAW_INPUT_SUFFIX, RAW_OUTPUT_SUFFIX)
            ):
                continue
            suffix = RAW_INPUT_SUFFIX if path.endswith(RAW_INPUT_SUFFIX) else RAW_OUTPUT_SUFFIX
            run_id = _uuid_from_path(path, RUN_DIR, suffix)
            run = runs.get(run_id)
            if run is None:
                raise ProjectFormatError(f"raw solver text has no run entry: {path}")
            try:
                text = payload.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ProjectFormatError(f"raw solver text is not UTF-8: {path}") from exc
            run_data = run.model_dump(mode="json")
            if suffix == RAW_INPUT_SUFFIX:
                run_data["result"]["raw_input"] = text
            else:
                run_data["result"]["raw_output"] = text
            runs[run_id] = SimulationRunPayload.model_validate(run_data)
        return list(runs.values())

    @staticmethod
    def _migrate_payload(payload: bytes) -> bytes:
        try:
            data = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return payload
        if not isinstance(data, dict) or data.get("schema_version") not in (59, 60):
            return payload
        migrated_from = data["schema_version"]
        data["schema_version"] = SCHEMA_VERSION
        project = data.get("project")
        if migrated_from == 59 and isinstance(project, dict):
            # 59 -> 60 added the optional site_ground metadata field. The
            # 60 -> 61 radial droop field defaults to zero, so no rewrite is
            # needed for design entries.
            project.setdefault("site_ground", None)
        return json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

    def _parse_document(
        self,
        model: type[_ModelT],
        payload: bytes,
        path: str,
    ) -> _ModelT:
        payload = self._migrate_payload(payload)
        try:
            return model.model_validate_json(payload)
        except ValidationError as exc:
            raise ProjectFormatError(f"invalid project entry {path}: {exc}") from exc
        except ValueError as exc:
            raise ProjectFormatError(f"invalid project entry {path}: {exc}") from exc

    @staticmethod
    def _validate_path(name: str) -> None:
        if len(name.encode("utf-8")) > MAX_PATH_BYTES:
            raise ProjectTooLargeError(
                f"project entry path is too long ({name!r})",
                size=len(name),
                limit=MAX_PATH_BYTES,
                expanded=False,
            )
        if not _ENTRY_NAME.fullmatch(name):
            raise ProjectFormatError(f"invalid project entry name: {name!r}")
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts or "\\" in name or ":" in name:
            raise ProjectFormatError(f"unsafe project entry name: {name!r}")
        if name == MANIFEST_NAME:
            return
        if pure.parts[0] not in (
            PROJECT_NAME,
            DESIGN_DIR,
            RUN_DIR,
            OPTIMIZATION_DIR,
        ):
            raise ProjectFormatError(f"unknown project entry: {name!r}")
        if name == PROJECT_NAME:
            return
        expected = _kind_for_path(name)
        if expected is None:
            raise ProjectFormatError(f"unknown project entry: {name!r}")
        if (
            not name.endswith(".json")
            and not name.endswith(RAW_INPUT_SUFFIX)
            and not name.endswith(RAW_OUTPUT_SUFFIX)
        ):
            raise ProjectFormatError(f"unexpected project entry extension: {name!r}")

    @staticmethod
    def _read_bounded(
        archive: zipfile.ZipFile,
        info: zipfile.ZipInfo,
        limit: int,
    ) -> bytes:
        with archive.open(info) as handle:
            payload = handle.read(limit + 1)
        if len(payload) > limit:
            raise ProjectTooLargeError(
                f"project entry {info.filename} exceeds the {limit}-byte limit",
                size=len(payload),
                limit=limit,
                expanded=True,
            )
        return payload

    @staticmethod
    def _atomic_write(path: Path, payload: bytes) -> None:
        parent = path.parent
        if not parent.is_dir():
            raise ProjectFormatError(f"project directory does not exist: {parent}")
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except OSError as exc:
            temporary.unlink(missing_ok=True)
            raise ProjectFormatError(f"could not save project: {exc}") from exc
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise


@dataclass(frozen=True, slots=True)
class ContainerRunStore:
    """Load runs from one validated container without materializing the rest."""

    path: Path
    manifest: ProjectManifest
    repository: ProjectContainerRepository

    @property
    def run_index(self) -> tuple[ApplicationRunIndexEntry, ...]:
        return tuple(
            ApplicationRunIndexEntry(
                id=run.id,
                design_id=run.design_id,
                created_at=run.created_at,
                band_id=run.band_id,
                batch_id=run.batch_id,
            )
            for run in self.manifest.runs
        )

    def load_run(self, run_id: UUID) -> SimulationRun:
        index = next((run for run in self.manifest.runs if run.id == run_id), None)
        if index is None:
            raise ProjectFormatError(f"run is not indexed in the manifest: {run_id}")
        paths = {
            f"{RUN_DIR}/{run_id}.json",
            f"{RUN_DIR}/{run_id}{RAW_INPUT_SUFFIX}",
            f"{RUN_DIR}/{run_id}{RAW_OUTPUT_SUFFIX}",
        }
        listed = {entry.path: entry for entry in self.manifest.entries if entry.path in paths}
        if f"{RUN_DIR}/{run_id}.json" not in listed:
            raise ProjectFormatError(f"run entry is missing from the container: {run_id}")
        with zipfile.ZipFile(self.path) as archive:
            infos = archive.infolist()
            self.repository._validate_archive_entries(infos)
            data = self.repository._read_entries(archive, infos, listed)
        payloads = self.repository._read_runs(data)
        if len(payloads) != 1 or payloads[0].id != run_id:
            raise ProjectFormatError(f"run entry does not match its manifest id: {run_id}")
        if payloads[0].design_id != index.design_id:
            raise ProjectFormatError(f"run design id does not match the manifest: {run_id}")
        return simulation_run_from_payload(payloads[0])

    def copy_entries(self, run_ids: Iterable[UUID]) -> dict[str, bytes]:
        """Copy the serialized entries for these runs without parsing them."""

        paths: set[str] = set()
        for run_id in run_ids:
            paths.update(
                {
                    f"{RUN_DIR}/{run_id}.json",
                    f"{RUN_DIR}/{run_id}{RAW_INPUT_SUFFIX}",
                    f"{RUN_DIR}/{run_id}{RAW_OUTPUT_SUFFIX}",
                }
            )
        listed = {entry.path: entry for entry in self.manifest.entries if entry.path in paths}
        if not listed:
            return {}
        with zipfile.ZipFile(self.path) as archive:
            infos = archive.infolist()
            self.repository._validate_archive_entries(infos)
            return self.repository._read_entries(archive, infos, listed)

    def load_all_runs(self) -> tuple[SimulationRun, ...]:
        listed = {entry.path: entry for entry in self.manifest.entries if _is_run_entry(entry.path)}
        with zipfile.ZipFile(self.path) as archive:
            infos = archive.infolist()
            self.repository._validate_archive_entries(infos)
            data = self.repository._read_entries(archive, infos, listed)
        payloads = {payload.id: payload for payload in self.repository._read_runs(data)}
        runs: list[SimulationRun] = []
        for index in self.manifest.runs:
            payload = payloads.get(index.id)
            if payload is None:
                raise ProjectFormatError(f"indexed run is missing from the container: {index.id}")
            if payload.design_id != index.design_id:
                raise ProjectFormatError(f"run design id does not match the manifest: {index.id}")
            runs.append(simulation_run_from_payload(payload))
        return tuple(runs)


# -- helpers ------------------------------------------------------------------


def _json_bytes(value: BaseModel) -> bytes:
    data = value.model_dump(mode="json")
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return (text + "\n").encode("utf-8")


def _zip_bytes(entries: dict[str, _Entry], manifest: bytes | None = None) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:
        if manifest is not None:
            _writestr(archive, MANIFEST_NAME, manifest)
        for path in sorted(entries):
            _writestr(archive, path, entries[path].data)
    return buffer.getvalue()


def _writestr(archive: zipfile.ZipFile, path: str, data: bytes) -> None:
    info = zipfile.ZipInfo(path, date_time=_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def _is_run_entry(path: str) -> bool:
    return path.startswith(f"{RUN_DIR}/") and path.endswith(
        (".json", RAW_INPUT_SUFFIX, RAW_OUTPUT_SUFFIX)
    )


def _kind_for_path(path: str) -> EntryKind | None:
    if path == PROJECT_NAME:
        return "metadata"
    if path.startswith(f"{DESIGN_DIR}/") and path.endswith(".json"):
        return "design"
    if path.startswith(f"{RUN_DIR}/") and path.endswith(".json"):
        return "run"
    if path.startswith(f"{RUN_DIR}/") and path.endswith(RAW_INPUT_SUFFIX):
        return "raw-input"
    if path.startswith(f"{RUN_DIR}/") and path.endswith(RAW_OUTPUT_SUFFIX):
        return "raw-output"
    if path.startswith(f"{OPTIMIZATION_DIR}/") and path.endswith(".json"):
        return "optimization"
    return None


def _uuid_from_path(path: str, directory: str, suffix: str) -> UUID:
    prefix = f"{directory}/"
    if not path.startswith(prefix) or not path.endswith(suffix):
        raise ProjectFormatError(f"unexpected project entry path: {path}")
    value = path[len(prefix) : -len(suffix)]
    try:
        return UUID(value)
    except ValueError as exc:
        raise ProjectFormatError(f"project entry name is not a UUID: {path}") from exc
