# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""External model importers."""

from __future__ import annotations

from pathlib import Path

MAX_IMPORT_FILE_BYTES = 16 * 1024 * 1024


def read_import_text(path: Path, *, errors: str = "strict") -> str:
    """Read a text import after rejecting an oversized file.

    The size check runs before decoding so an untrusted selection cannot
    allocate an unbounded string. The parser-specific limits still apply.
    """

    size = path.stat().st_size
    if size > MAX_IMPORT_FILE_BYTES:
        raise ValueError(
            f"{path.name} is too large ({size} bytes; limit is {MAX_IMPORT_FILE_BYTES} bytes)"
        )
    return path.read_text(encoding="utf-8", errors=errors)
