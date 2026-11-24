# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Development scripts must import with the current package layout."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = sorted((ROOT / "scripts").glob("*.py"))


def test_development_scripts_import_without_stale_module_paths() -> None:
    assert SCRIPTS

    for path in SCRIPTS:
        # Use a non-main run name so the CLI entry point is not executed.
        runpy.run_path(str(path), run_name=f"antennadesk_script_{path.stem}")
