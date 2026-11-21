# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""A prepared, size-checked project container payload."""

from __future__ import annotations

from dataclasses import dataclass

from .project_limits import (
    MAX_CONTAINER_BYTES,
    MAX_ENTRIES,
    MAX_ENTRY_BYTES,
    MAX_MANIFEST_BYTES,
    MAX_PATH_BYTES,
    MAX_PROJECT_UNCOMPRESSED_BYTES,
)


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
class PreparedProject:
    """A validated container ready to be written.

    ``payload`` is the exact compressed file bytes. ``expanded_bytes`` is the
    sum of the uncompressed entry payloads, including the manifest. Keeping both
    sizes lets the UI report the honest storage contract without re-reading the
    container.
    """

    payload: bytes
    entry_count: int
    expanded_bytes: int
    limits: ProjectLimits = ProjectLimits()

    def __post_init__(self) -> None:
        if self.entry_count < 1:
            raise ValueError("a prepared project must contain at least one entry")
        if self.expanded_bytes < 0:
            raise ValueError("expanded_bytes must not be negative")
        if len(self.payload) > self.limits.container_bytes:
            raise ValueError("prepared project exceeds the container limit")
        if self.expanded_bytes > self.limits.expanded_bytes:
            raise ValueError("prepared project exceeds the expanded limit")
        if self.entry_count > self.limits.entries:
            raise ValueError("prepared project exceeds the entry-count limit")

    @property
    def compressed_bytes(self) -> int:
        return len(self.payload)
