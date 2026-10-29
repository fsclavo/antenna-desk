# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.reporting.html_report import render_html_report


def make_result(project: Project) -> SimulationResult:
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_100_000.0, 2),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        far_field=FarFieldRequest(),
    )
    far_field = (
        FarFieldPoint(0.0, 0.0, 2.14, None, 2.14, 0.0, 0.0, "LINEAR", None, None, None, None),
        FarFieldPoint(90.0, 0.0, -999.99, None, -999.99, 0.0, 0.0, None, None, None, None, None),
    )
    frequencies = (
        FrequencyResult(
            frequency_hz=6_900_000.0,
            feed_tag=1,
            feed_segment=11,
            impedance_ohm=complex(60.0, -10.0),
            swr=2.0,
            input_power_w=0.001,
            far_field=far_field,
        ),
        FrequencyResult(
            frequency_hz=7_100_000.0,
            feed_tag=1,
            feed_segment=11,
            impedance_ohm=complex(70.0, 0.0),
            swr=1.4,
            input_power_w=0.002,
            far_field=far_field,
        ),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3", executable="nec2c"),
        frequencies=frequencies,
        duration_s=0.1,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def test_html_report_contains_design_results_and_charts(sample_project: Project) -> None:
    design = sample_project.designs[0]
    report = render_html_report(sample_project, design, make_result(sample_project))

    assert report.startswith("<!DOCTYPE html>")
    assert "40 m dipole" in report
    assert "Impedance" in report
    assert "Resonance" in report
    assert "<svg" in report
    assert "7.100000" in report


def test_html_report_escapes_user_text(sample_project: Project) -> None:
    project = replace(sample_project, name="<script>alert(1)</script>")
    report = render_html_report(project, project.designs[0], make_result(project))

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in report
    assert "<script>alert(1)</script>" not in report
