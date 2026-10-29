# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    PowerBudget,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.reporting.construction_sheet import render_construction_sheet


def _make_result() -> SimulationResult:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    frequency = FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=11,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=0.001,
        power_budget=PowerBudget(0.001, 0.0009, 0.0001, 0.0, 90.0),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(frequency,),
        duration_s=0.1,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def test_construction_sheet_contains_dimensions_and_result(sample_project: Project) -> None:
    design = sample_project.designs[0]
    sheet = render_construction_sheet(sample_project, design, _make_result())

    assert "construction sheet" in sheet
    assert "Total wire length" in sheet
    assert "10.0000 m" in sheet
    assert "Feed height above ground" in sheet
    assert "SWR" in sheet
    assert "1.000" in sheet
    assert "90.00 %" in sheet
    assert "a" * 64 in sheet
    assert "Construction notes" in sheet


def test_construction_sheet_works_without_a_result(sample_project: Project) -> None:
    sheet = render_construction_sheet(
        sample_project,
        sample_project.designs[0],
        None,
    )
    assert "No result yet." in sheet


def test_construction_sheet_escapes_user_text(sample_project: Project) -> None:
    project = replace(sample_project, name="<script>alert(1)</script>")
    sheet = render_construction_sheet(project, project.designs[0], None)

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in sheet
    assert "<script>alert(1)</script>" not in sheet


def test_vertical_construction_sheet_uses_feed_height(sample_project: Project) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.dipole import DipoleOrientation

    design = sample_project.designs[0]
    parameters = replace(
        design.parameters,
        orientation=DipoleOrientation.VERTICAL,
        total_length_m=5.0,
        height_m=2.0,
        wire_radius_m=0.3,
        frequency_hz=30_000_000.0,
    )
    vertical_design = design.with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, vertical_design, None)

    assert "<td>vertical</td>" in sheet
    assert "First leg (from wire start)" in sheet
    assert "2.5000 m" in sheet
    assert "Wire height at start" in sheet
    assert "Feed height above ground" in sheet
    assert "4.5000 m" in sheet
    assert "Azimuth" in sheet


def test_folded_dipole_construction_sheet(sample_project: Project) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    design = sample_project.designs[0]
    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    folded = design.with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, folded, None)

    assert "Element length" in sheet
    assert "Spacing" in sheet
    assert "Total conductor length" in sheet
    assert "End connector length" in sheet
    assert "40.4000 m" in sheet


def test_loop_construction_sheet(sample_project: Project) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    design = sample_project.designs[0]
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=8,
    )
    loop = design.with_parameters(parameters)
    sheet = render_construction_sheet(sample_project, loop, None)

    assert "Circumference" in sheet
    assert "Side length" in sheet
    assert "Feed side" in sheet
    assert "5.0000 m" in sheet
    assert "8 equal sides" in sheet
