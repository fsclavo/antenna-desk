# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""PreparedProject size and entry invariants."""

from __future__ import annotations

import pytest

from antennadesk.application.project_payload import PreparedProject, ProjectLimits


def test_prepared_project_reports_both_sizes() -> None:
    prepared = PreparedProject(
        b"PK",
        entry_count=2,
        expanded_bytes=100,
        limits=ProjectLimits(container_bytes=10),
    )

    assert prepared.payload == b"PK"
    assert prepared.compressed_bytes == 2
    assert prepared.expanded_bytes == 100
    assert prepared.entry_count == 2


def test_prepared_project_rejects_an_empty_entry_set() -> None:
    with pytest.raises(ValueError, match="at least one entry"):
        PreparedProject(b"PK", entry_count=0, expanded_bytes=0)


def test_prepared_project_rejects_a_negative_expanded_size() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        PreparedProject(b"PK", entry_count=1, expanded_bytes=-1)


def test_prepared_project_rejects_a_container_over_the_limit() -> None:
    with pytest.raises(ValueError, match="container limit"):
        PreparedProject(
            b"x" * 11,
            entry_count=1,
            expanded_bytes=11,
            limits=ProjectLimits(container_bytes=10),
        )


def test_prepared_project_rejects_an_expanded_size_over_the_limit() -> None:
    with pytest.raises(ValueError, match="expanded limit"):
        PreparedProject(
            b"PK",
            entry_count=1,
            expanded_bytes=11,
            limits=ProjectLimits(expanded_bytes=10),
        )


def test_prepared_project_rejects_too_many_entries() -> None:
    with pytest.raises(ValueError, match="entry-count limit"):
        PreparedProject(
            b"PK",
            entry_count=2,
            expanded_bytes=2,
            limits=ProjectLimits(entries=1),
        )
