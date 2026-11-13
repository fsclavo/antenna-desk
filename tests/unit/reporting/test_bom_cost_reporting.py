# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""BOM cost entries, CSV, and construction sheet output."""

from __future__ import annotations

import pytest

from antennadesk.domain.projects.bom_costs import BomCostLine, BomCostRecord
from antennadesk.domain.projects.project import Project
from antennadesk.reporting.bom_costs import (
    bom_cost_entries,
    bom_cost_total,
    format_cost,
    hardware_cost_key,
)
from antennadesk.reporting.construction_sheet import render_construction_sheet
from antennadesk.reporting.wire_schedule import bom_to_csv, conductor_bom_rows


def _project_with_costs(sample_project: Project) -> tuple[Project, BomCostRecord]:
    design = sample_project.designs[0]
    conductor = conductor_bom_rows(design.antenna)[0]
    record = BomCostRecord(
        currency="USD",
        lines=(
            BomCostLine(conductor.cost_key, 2.5),
            BomCostLine(hardware_cost_key("end_insulators"), 1.0),
        ),
    )
    return (
        sample_project.with_bom_costs(record, updated_at=sample_project.updated_at),
        record,
    )


def test_entries_join_conductor_and_hardware_costs(sample_project: Project) -> None:
    project, record = _project_with_costs(sample_project)
    design = project.designs[0]
    conductor = conductor_bom_rows(design.antenna)[0]

    entries = {entry.key: entry for entry in bom_cost_entries(project, design)}

    assert entries[conductor.cost_key].quantity == pytest.approx(conductor.total_length_m)
    assert entries[conductor.cost_key].unit == "m"
    assert entries[conductor.cost_key].unit_cost == pytest.approx(2.5)
    assert entries[conductor.cost_key].line_total == pytest.approx(conductor.total_length_m * 2.5)
    hardware = entries[hardware_cost_key("end_insulators")]
    assert hardware.quantity == pytest.approx(2.0)
    assert hardware.unit_cost == pytest.approx(1.0)
    assert hardware.line_total == pytest.approx(2.0)
    assert hardware_cost_key("antenna_conductor") not in entries
    assert bom_cost_total(tuple(entries.values())) == pytest.approx(
        conductor.total_length_m * 2.5 + 2.0
    )
    assert record.currency == "USD"


def test_cost_formatting() -> None:
    assert format_cost(12.5, "EUR") == "12.50 EUR"
    assert format_cost(12.5, "") == "12.50"
    assert format_cost(None, "USD") == "—"


def test_bom_csv_adds_cost_columns_only_when_requested(sample_project: Project) -> None:
    project, record = _project_with_costs(sample_project)
    design = project.designs[0]
    conductor = conductor_bom_rows(design.antenna)[0]

    plain = bom_to_csv(design)
    with_costs = bom_to_csv(design, costs=record)

    assert plain.splitlines()[0] == "material,diameter_mm,wire_count,total_length_m"
    header = with_costs.splitlines()[0]
    assert header == (
        "material,diameter_mm,wire_count,total_length_m,currency,unit_cost_per_m,line_total"
    )
    assert "USD" in with_costs
    assert f"{conductor.total_length_m * 2.5:.6f}" in with_costs


def test_construction_sheet_shows_cost_columns_and_total(sample_project: Project) -> None:
    project, _ = _project_with_costs(sample_project)
    design = project.designs[0]

    sheet = render_construction_sheet(project, design, None)

    assert "Unit cost" in sheet
    assert "Line total" in sheet
    assert "BOM total" in sheet
    assert "USD" in sheet
    plain = render_construction_sheet(sample_project, design, None)
    assert "Unit cost" not in plain
    assert "BOM total" not in plain


def test_zero_quantity_cost_is_not_counted(sample_project: Project) -> None:
    record = BomCostRecord(
        currency="USD",
        lines=(BomCostLine(hardware_cost_key("boom"), 100.0),),
    )
    project = sample_project.with_bom_costs(record, updated_at=sample_project.updated_at)

    entries = bom_cost_entries(project, project.designs[0])
    boom = next(entry for entry in entries if entry.key == hardware_cost_key("boom"))

    assert boom.quantity == pytest.approx(0.0)
    assert boom.unit_cost == pytest.approx(100.0)
    assert boom.line_total is None
    assert bom_cost_total(entries) is None
