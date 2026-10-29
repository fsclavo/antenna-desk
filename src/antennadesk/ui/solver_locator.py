# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Locate a nec2c executable for development and packaged runs."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _executable_name() -> str:
    return "nec2c.exe" if os.name == "nt" else "nec2c"


def find_nec2c() -> Path | None:
    configured = os.environ.get("NEC2C")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return candidate.resolve()

    on_path = shutil.which("nec2c") or shutil.which("nec2c.exe")
    if on_path:
        candidate = Path(on_path)
        if candidate.is_file():
            return candidate.resolve()

    name = _executable_name()
    repo_root = Path(__file__).resolve().parents[3]
    candidates = [
        repo_root / "spikes" / "phase0" / "build" / name,
        Path.cwd() / "spikes" / "phase0" / "build" / name,
        Path(sys.executable).resolve().parent / name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None
