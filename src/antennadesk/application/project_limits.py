# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project storage limits shared by the repository and the UI budget."""

from __future__ import annotations

from typing import Final

MAX_PROJECT_SIZE_BYTES: Final = 64 * 1024 * 1024
MAX_PROJECT_UNCOMPRESSED_BYTES: Final = 256 * 1024 * 1024
PROJECT_SIZE_WARNING_BYTES: Final = 32 * 1024 * 1024
