# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""ADR numbering consistency."""

from __future__ import annotations

from pathlib import Path

ADR_DIR = Path(__file__).resolve().parents[2] / "docs" / "ADR"


def _adr_files() -> list[Path]:
    return sorted(ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md"))


def test_adr_numbers_are_unique() -> None:
    numbers = [path.name[:4] for path in _adr_files()]
    duplicates = {number for number in numbers if numbers.count(number) > 1}

    assert not duplicates


def test_adr_numbers_are_contiguous() -> None:
    numbers = [int(path.name[:4]) for path in _adr_files()]

    assert numbers == list(range(1, len(numbers) + 1))


def test_adr_heading_matches_the_filename() -> None:
    for path in _adr_files():
        heading = path.read_text(encoding="utf-8").splitlines()[0]
        assert heading.startswith(f"# ADR-{path.name[:4]}"), path.name
