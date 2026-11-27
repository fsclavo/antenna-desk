# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Two-phase deterministic ZIP writer with a bounded temporary spool.

The container manifest lists the compressed size, CRC32, and SHA-256 of every
entry and must be written first. Building that manifest without holding every
entry in memory requires two phases: stage each entry in a temporary ZIP while
recording its metadata, then write the final container by streaming the staged
entries after the manifest. Peak memory scales with the largest entry and the
I/O buffer, not with the whole project history.
"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
import zipfile
import zlib
from contextlib import suppress
from dataclasses import dataclass, replace
from pathlib import Path
from typing import IO, Final

from ..application.project_payload import ProjectLimits
from .errors import ProjectFormatError, ProjectTooLargeError

_ZIP_TIMESTAMP: Final = (1980, 1, 1, 0, 0, 0)
_COPY_CHUNK_BYTES: Final = 1024 * 1024
_STAGE_NAME: Final = "entries.zip"
CONTAINER_NAME: Final = "container.antennadesk"


@dataclass(frozen=True, slots=True)
class StagedEntry:
    """Metadata for one entry already compressed in the temporary stage."""

    path: str
    kind: str
    uncompressed_bytes: int
    compressed_bytes: int
    crc32: int
    sha256: str


class ContainerSpool:
    """Stage entries one at a time, then write a deterministic container.

    The spool owns a temporary directory. Call :meth:`release_directory` after
    :meth:`write_container` to transfer cleanup ownership to the prepared
    payload, or :meth:`cleanup` on every failure path.
    """

    def __init__(self, limits: ProjectLimits) -> None:
        self._limits = limits
        directory = tempfile.TemporaryDirectory(prefix="antennadesk-save-")
        self._directory: tempfile.TemporaryDirectory[str] | None = directory
        self._stage_path = Path(directory.name) / _STAGE_NAME
        self._stage = zipfile.ZipFile(
            self._stage_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=6,
        )
        self._entries: dict[str, StagedEntry] = {}
        self._expanded_bytes = 0
        self._stage_closed = False
        self._container_path: Path | None = None
        self._container_bytes = 0

    @property
    def container_path(self) -> Path:
        if self._container_path is None:
            raise RuntimeError("the container has not been written yet")
        return self._container_path

    @property
    def container_bytes(self) -> int:
        return self._container_bytes

    def add_bytes(self, path: str, kind: str, data: bytes) -> StagedEntry:
        """Add one in-memory entry, enforcing the path and entry limits."""

        self._check_new_entry(path)
        if len(data) > self._limits.entry_bytes:
            raise ProjectTooLargeError(
                f"project entry {path} is too large "
                f"({len(data)} bytes; limit is {self._limits.entry_bytes} bytes)",
                size=len(data),
                limit=self._limits.entry_bytes,
                expanded=True,
            )
        self._stage.writestr(_zip_info(path), data)
        entry = StagedEntry(
            path=path,
            kind=kind,
            uncompressed_bytes=len(data),
            compressed_bytes=0,
            crc32=zlib.crc32(data) & 0xFFFFFFFF,
            sha256=hashlib.sha256(data).hexdigest(),
        )
        self._record(entry)
        return entry

    def add_stream(
        self,
        path: str,
        kind: str,
        source: IO[bytes],
        *,
        expected_bytes: int | None = None,
    ) -> StagedEntry:
        """Add one entry from a bounded stream without materializing it."""

        self._check_new_entry(path)
        if expected_bytes is not None and expected_bytes > self._limits.entry_bytes:
            raise ProjectTooLargeError(
                f"project entry {path} is too large "
                f"({expected_bytes} bytes; limit is {self._limits.entry_bytes} bytes)",
                size=expected_bytes,
                limit=self._limits.entry_bytes,
                expanded=True,
            )
        digest = hashlib.sha256()
        crc = 0
        size = 0
        with self._stage.open(_zip_info(path), mode="w") as target:
            while chunk := source.read(_COPY_CHUNK_BYTES):
                size += len(chunk)
                if size > self._limits.entry_bytes:
                    raise ProjectTooLargeError(
                        f"project entry {path} is too large "
                        f"({size} bytes; limit is {self._limits.entry_bytes} bytes)",
                        size=size,
                        limit=self._limits.entry_bytes,
                        expanded=True,
                    )
                self._check_expanded(size)
                digest.update(chunk)
                crc = zlib.crc32(chunk, crc)
                target.write(chunk)
        if expected_bytes is not None and size != expected_bytes:
            raise ProjectFormatError(
                f"size mismatch for project entry {path} "
                f"(declared {expected_bytes} bytes, copied {size} bytes)"
            )
        entry = StagedEntry(
            path=path,
            kind=kind,
            uncompressed_bytes=size,
            compressed_bytes=0,
            crc32=crc & 0xFFFFFFFF,
            sha256=digest.hexdigest(),
        )
        self._record(entry)
        return entry

    def close_stage(self) -> tuple[StagedEntry, ...]:
        """Close the staging ZIP and fill in each deterministic compressed size."""

        if self._stage_closed:
            raise RuntimeError("the staging container is already closed")
        self._stage.close()
        self._stage_closed = True
        with zipfile.ZipFile(self._stage_path) as archive:
            infos = {info.filename: info for info in archive.infolist()}
        staged: list[StagedEntry] = []
        for path, entry in self._entries.items():
            info = infos.get(path)
            if info is None:
                raise ProjectFormatError(f"staged entry is missing from the spool: {path}")
            if info.file_size != entry.uncompressed_bytes:
                raise ProjectFormatError(f"staged size mismatch for project entry {path}")
            if entry.crc32 != info.CRC & 0xFFFFFFFF:
                raise ProjectFormatError(f"staged CRC mismatch for project entry {path}")
            staged.append(replace(entry, compressed_bytes=info.compress_size))
        if len(staged) + 1 > self._limits.entries:
            raise ProjectTooLargeError(
                f"project container has too many entries ({len(staged) + 1}; "
                f"limit is {self._limits.entries})",
                size=len(staged) + 1,
                limit=self._limits.entries,
                expanded=False,
            )
        self._entries = {entry.path: entry for entry in staged}
        return tuple(staged)

    def write_container(self, manifest: bytes, manifest_name: str) -> int:
        """Write the final deterministic container into the spool directory."""

        if not self._stage_closed:
            raise RuntimeError("close_stage() must run before write_container()")
        if len(manifest) > self._limits.manifest_bytes:
            raise ProjectTooLargeError(
                "project manifest is too large "
                f"({len(manifest)} bytes; limit is {self._limits.manifest_bytes} bytes)",
                size=len(manifest),
                limit=self._limits.manifest_bytes,
                expanded=True,
            )
        destination = Path(self._require_directory().name) / CONTAINER_NAME
        try:
            with zipfile.ZipFile(
                destination,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=6,
            ) as archive:
                archive.writestr(_zip_info(manifest_name), manifest)
                with zipfile.ZipFile(self._stage_path) as stage:
                    for path in sorted(self._entries):
                        with (
                            stage.open(path) as source,
                            archive.open(_zip_info(path), mode="w") as target,
                        ):
                            shutil.copyfileobj(source, target, _COPY_CHUNK_BYTES)
            size = destination.stat().st_size
        except OSError as exc:
            raise ProjectFormatError(f"could not prepare project: {exc}") from exc
        if size > self._limits.container_bytes:
            raise ProjectTooLargeError(
                "project container is too large "
                f"({size} bytes; limit is {self._limits.container_bytes} bytes)",
                size=size,
                limit=self._limits.container_bytes,
                expanded=False,
            )
        self._container_path = destination
        self._container_bytes = size
        return size

    def release_directory(self) -> tempfile.TemporaryDirectory[str]:
        """Transfer the temporary directory to the prepared payload owner."""

        directory = self._require_directory()
        self._directory = None
        return directory

    def cleanup(self) -> None:
        """Remove the staging and container files; safe to call more than once."""

        if not self._stage_closed:
            with suppress(Exception):
                self._stage.close()
            self._stage_closed = True
        if self._directory is not None:
            self._directory.cleanup()
            self._directory = None

    def _require_directory(self) -> tempfile.TemporaryDirectory[str]:
        if self._directory is None:
            raise RuntimeError("the spool directory was already released")
        return self._directory

    def _check_new_entry(self, path: str) -> None:
        if path in self._entries:
            raise ProjectFormatError(f"duplicate project entry path: {path}")
        if len(self._entries) + 2 > self._limits.entries:
            raise ProjectTooLargeError(
                f"project container has too many entries ({len(self._entries) + 2}; "
                f"limit is {self._limits.entries})",
                size=len(self._entries) + 2,
                limit=self._limits.entries,
                expanded=False,
            )
        path_bytes = len(path.encode("utf-8"))
        if path_bytes > self._limits.path_bytes:
            raise ProjectTooLargeError(
                f"project entry path is too long ({path!r})",
                size=path_bytes,
                limit=self._limits.path_bytes,
                expanded=False,
            )

    def _check_expanded(self, entry_size: int) -> None:
        total = self._expanded_bytes + entry_size
        if total > self._limits.expanded_bytes:
            raise ProjectTooLargeError(
                "project entries are too large when expanded "
                f"({total} bytes; limit is {self._limits.expanded_bytes} bytes)",
                size=total,
                limit=self._limits.expanded_bytes,
                expanded=True,
            )

    def _record(self, entry: StagedEntry) -> None:
        self._check_expanded(entry.uncompressed_bytes)
        self._expanded_bytes += entry.uncompressed_bytes
        self._entries[entry.path] = entry


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    return info
