# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Native project format constants."""

from __future__ import annotations

from typing import Final

from ..application.project_limits import (
    MAX_CONTAINER_BYTES,
    MAX_ENTRIES,
    MAX_ENTRY_BYTES,
    MAX_MANIFEST_BYTES,
    MAX_PATH_BYTES,
    MAX_PROJECT_SIZE_BYTES,
    MAX_PROJECT_UNCOMPRESSED_BYTES,
    PROJECT_SIZE_WARNING_BYTES,
)

CONTAINER_FORMAT: Final = "antennadesk.project"
CONTAINER_VERSION: Final = 1
PROJECT_FORMAT: Final = "antennadesk-project"
SCHEMA_VERSION: Final = 70

__all__ = [
    "CONTAINER_FORMAT",
    "CONTAINER_VERSION",
    "MAX_CONTAINER_BYTES",
    "MAX_ENTRIES",
    "MAX_ENTRY_BYTES",
    "MAX_MANIFEST_BYTES",
    "MAX_PATH_BYTES",
    "MAX_PROJECT_SIZE_BYTES",
    "MAX_PROJECT_UNCOMPRESSED_BYTES",
    "PROJECT_FORMAT",
    "PROJECT_SIZE_WARNING_BYTES",
    "SCHEMA_VERSION",
]
