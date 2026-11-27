# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""A prepared, size-checked project container payload."""

from __future__ import annotations

import io
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Final

from .project_limits import (
    MAX_CONTAINER_BYTES,
    MAX_ENTRIES,
    MAX_ENTRY_BYTES,
    MAX_MANIFEST_BYTES,
    MAX_PATH_BYTES,
    MAX_PROJECT_UNCOMPRESSED_BYTES,
)

_COPY_CHUNK_BYTES: Final = 1024 * 1024


@dataclass(frozen=True, slots=True)
class ProjectLimits:
    """The limits that a prepared project payload was checked against."""

    container_bytes: int = MAX_CONTAINER_BYTES
    expanded_bytes: int = MAX_PROJECT_UNCOMPRESSED_BYTES
    manifest_bytes: int = MAX_MANIFEST_BYTES
    entry_bytes: int = MAX_ENTRY_BYTES
    entries: int = MAX_ENTRIES
    path_bytes: int = MAX_PATH_BYTES


@dataclass(frozen=True, slots=True)
class PreparedSpool:
    """A temporary file holding the exact container bytes.

    The spool owns the temporary directory that contains the file. Call
    :meth:`close` after the write completes; the owner also cleans up when the
    prepared project is garbage-collected.
    """

    path: Path
    compressed_bytes: int
    owner: tempfile.TemporaryDirectory[str] | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if self.compressed_bytes < 0:
            raise ValueError("compressed_bytes must not be negative")
        if not self.path.is_file():
            raise ValueError(f"prepared spool file does not exist: {self.path}")

    def open_binary(self) -> IO[bytes]:
        return self.path.open("rb")

    def close(self) -> None:
        if self.owner is not None:
            self.owner.cleanup()


@dataclass(frozen=True, slots=True)
class PreparedProject:
    """A validated container ready to be written.

    ``payload`` keeps the small in-memory compatibility path. Production saves
    use ``spool``, a temporary file with the exact compressed container bytes,
    so the repository can stream it to the atomic destination without holding
    the whole project in memory. ``expanded_bytes`` is the sum of the
    uncompressed entry payloads, including the manifest.
    """

    payload: bytes | None = None
    entry_count: int = 1
    expanded_bytes: int = 0
    limits: ProjectLimits = field(default_factory=ProjectLimits)
    spool: PreparedSpool | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if (self.payload is None) == (self.spool is None):
            raise ValueError("a prepared project requires exactly one payload or spool")
        if self.entry_count < 1:
            raise ValueError("a prepared project must contain at least one entry")
        if self.expanded_bytes < 0:
            raise ValueError("expanded_bytes must not be negative")
        if self.compressed_bytes > self.limits.container_bytes:
            raise ValueError("prepared project exceeds the container limit")
        if self.expanded_bytes > self.limits.expanded_bytes:
            raise ValueError("prepared project exceeds the expanded limit")
        if self.entry_count > self.limits.entries:
            raise ValueError("prepared project exceeds the entry-count limit")

    @property
    def compressed_bytes(self) -> int:
        if self.spool is not None:
            return self.spool.compressed_bytes
        if self.payload is None:
            raise RuntimeError("prepared project has no payload")
        return len(self.payload)

    def open_binary(self) -> IO[bytes]:
        """Open the exact container bytes for a bounded read."""

        if self.spool is not None:
            return self.spool.open_binary()
        if self.payload is None:
            raise RuntimeError("prepared project has no payload")
        return io.BytesIO(self.payload)

    def copy_to(self, target: IO[bytes]) -> None:
        """Stream the exact container bytes into an open binary file."""

        with self.open_binary() as source:
            shutil.copyfileobj(source, target, _COPY_CHUNK_BYTES)

    def close(self) -> None:
        """Release the temporary spool, when present; safe to call repeatedly."""

        if self.spool is not None:
            self.spool.close()
