# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persistence errors."""

from __future__ import annotations


class PersistenceError(Exception):
    """Base class for persistence failures."""


class ProjectFormatError(PersistenceError):
    """The project file is malformed, unsupported, or fails validation."""


class ProjectTooLargeError(ProjectFormatError):
    """The project file exceeds the supported size."""


class UnsupportedSchemaVersion(ProjectFormatError):
    """The project uses a schema version newer than this build supports."""

    def __init__(self, *, found: int, supported: int) -> None:
        self.found = found
        self.supported = supported
        super().__init__(
            f"unsupported project schema version {found}; "
            f"this build supports up to version {supported}"
        )
