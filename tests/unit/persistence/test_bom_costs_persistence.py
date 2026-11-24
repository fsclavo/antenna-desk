# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""BOM cost persistence."""

from __future__ import annotations

from pathlib import Path

from antennadesk.domain.projects.bom_costs import BomCostLine, BomCostRecord
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.constants import SCHEMA_VERSION
from antennadesk.persistence.json_repository import JsonProjectRepository


def test_schema_version_is_current() -> None:
    assert SCHEMA_VERSION == 61


def test_bom_costs_round_trip(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    record = BomCostRecord(
        currency="EUR",
        lines=(
            BomCostLine("conductor:copper:2.000", 1.25),
            BomCostLine("hardware:coax_connector", 4.5),
        ),
    )
    project = sample_project.with_bom_costs(record, updated_at=sample_project.updated_at)
    path = tmp_path / "costs.antennadesk"
    repository = JsonProjectRepository()

    repository.save(project, path)
    loaded = repository.load(path)

    assert loaded.bom_costs == record
