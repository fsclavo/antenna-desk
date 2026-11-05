# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Structural checks for the hand-maintained changelog.

This cannot prove that every user-visible change was described, but it prevents
the common failure modes: an empty Unreleased section, malformed version
headings, invalid dates, unknown subsection names, and releases that are out of
chronological order.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[2] / "CHANGELOG.md"
RELEASE_HEADING = re.compile(r"^## \[([^\]]+)\] - (\d{4}-\d{2}-\d{2})$")
SUBSECTIONS = frozenset({"Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"})


def _lines() -> list[str]:
    return CHANGELOG.read_text(encoding="utf-8").splitlines()


def _sections() -> list[tuple[str, int, int]]:
    lines = _lines()
    starts = [index for index, line in enumerate(lines) if line.startswith("## [")]
    return [
        (
            lines[start],
            start,
            starts[position + 1] if position + 1 < len(starts) else len(lines),
        )
        for position, start in enumerate(starts)
    ]


def test_unreleased_section_exists_and_has_an_entry() -> None:
    lines = _lines()
    assert lines[0] == "# Changelog"
    sections = _sections()

    assert sections
    heading, start, end = sections[0]
    assert heading == "## [Unreleased]"

    body = lines[start + 1 : end]
    assert any(line.startswith("### ") for line in body)
    assert any(line.startswith("- ") for line in body)


def test_release_headings_have_valid_dates_and_are_ordered() -> None:
    release_dates: list[date] = []

    for heading, _start, _end in _sections():
        if heading == "## [Unreleased]":
            continue
        match = RELEASE_HEADING.match(heading)
        assert match is not None, f"malformed release heading: {heading!r}"
        release_dates.append(date.fromisoformat(match.group(2)))

    assert release_dates == sorted(release_dates, reverse=True)


def test_release_versions_are_unique() -> None:
    versions = [
        match.group(1)
        for heading, _start, _end in _sections()
        if (match := RELEASE_HEADING.match(heading)) is not None
    ]

    assert len(versions) == len(set(versions))


def test_subsections_use_keep_a_changelog_names() -> None:
    lines = _lines()

    for heading, start, end in _sections():
        for line in lines[start + 1 : end]:
            if line.startswith("### "):
                assert line[4:] in SUBSECTIONS, f"{heading}: unknown subsection {line!r}"
