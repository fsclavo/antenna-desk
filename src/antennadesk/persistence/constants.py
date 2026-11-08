# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Native project format constants."""

from __future__ import annotations

from typing import Final

PROJECT_FORMAT: Final = "antennadesk-project"
SCHEMA_VERSION: Final = 28
MAX_PROJECT_SIZE_BYTES: Final = 64 * 1024 * 1024
PROJECT_SIZE_WARNING_BYTES: Final = 32 * 1024 * 1024
