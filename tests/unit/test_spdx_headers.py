# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every source-like file must carry the project SPDX header."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRECTORIES = ("src", "tests", "scripts", "packaging")
SUFFIXES = frozenset({".py", ".sh", ".ps1", ".spec", ".desktop"})
SKIP_PARTS = frozenset({"__pycache__", ".venv", "build", "dist", "mutants"})


def _source_files() -> list[Path]:
    files: list[Path] = []
    for directory in DIRECTORIES:
        for path in sorted((ROOT / directory).rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUFFIXES:
                continue
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            files.append(path)
    return files


def test_source_files_have_the_project_spdx_header() -> None:
    missing = []
    for path in _source_files():
        head = path.read_text(encoding="utf-8")[:800]
        if (
            "SPDX-FileCopyrightText:" not in head
            or "SPDX-License-Identifier: GPL-3.0-or-later" not in head
        ):
            missing.append(path.relative_to(ROOT))

    assert not missing, "\n".join(f"missing SPDX header: {path}" for path in missing)
