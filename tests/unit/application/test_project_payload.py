# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""PreparedProject size and entry invariants."""

from __future__ import annotations

import io
from pathlib import Path

import pytest

from antennadesk.application.project_payload import (
    PreparedProject,
    PreparedSpool,
    ProjectLimits,
)


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


def test_prepared_project_requires_exactly_one_storage_source(tmp_path: Path) -> None:
    spool_path = tmp_path / "container.antennadesk"
    spool_path.write_bytes(b"PK")
    with pytest.raises(ValueError, match="exactly one payload or spool"):
        PreparedProject(entry_count=1, expanded_bytes=0)
    with pytest.raises(ValueError, match="exactly one payload or spool"):
        PreparedProject(
            b"PK",
            entry_count=1,
            expanded_bytes=0,
            spool=PreparedSpool(spool_path, 2),
        )


def test_prepared_project_copies_a_spool_to_a_target(tmp_path: Path) -> None:
    spool_path = tmp_path / "container.antennadesk"
    spool_path.write_bytes(b"PK\x03\x04prepared")
    prepared = PreparedProject(
        entry_count=1,
        expanded_bytes=12,
        spool=PreparedSpool(spool_path, spool_path.stat().st_size),
    )
    target = io.BytesIO()

    prepared.copy_to(target)

    assert prepared.payload is None
    assert prepared.compressed_bytes == spool_path.stat().st_size
    assert target.getvalue() == b"PK\x03\x04prepared"


def test_prepared_spool_rejects_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        PreparedSpool(tmp_path / "missing.antennadesk", 2)


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
