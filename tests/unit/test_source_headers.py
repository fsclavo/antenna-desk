# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every maintained Python source starts with an SPDX header."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOTS = (
    ROOT / "src",
    ROOT / "tests",
    ROOT / "benchmarks",
    ROOT / "scripts",
)


def test_python_sources_have_an_spdx_license_header() -> None:
    missing: list[str] = []
    for root in SOURCE_ROOTS:
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:5])
            if "SPDX-License-Identifier: GPL-3.0-or-later" not in head:
                missing.append(str(path.relative_to(ROOT)))

    assert not missing, "Missing SPDX header:\n" + "\n".join(missing)
