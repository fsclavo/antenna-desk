# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared bounds for UI-exposed parallel solver work."""

from __future__ import annotations

import os

MAX_UI_PARALLEL_WORKERS = 4


def default_parallel_workers() -> int:
    """Return the default worker count: one less than the CPU count, capped."""

    return min(MAX_UI_PARALLEL_WORKERS, max(1, (os.cpu_count() or 1) - 1))
