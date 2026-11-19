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
    SourceResult,
)
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.reporting.html_report import render_html_report
from antennadesk.ui.i18n import Language, Translator


def make_result(project: Project) -> SimulationResult:
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_100_000.0, 2),
        segmentation=SegmentationPolicy(segments_per_wire=21),
        far_field=FarFieldRequest(),
    )
    far_field = (
        FarFieldPoint(0.0, 0.0, 2.14, None, 2.14, 0.0, 0.0, "LINEAR", None, None, None, None),
        FarFieldPoint(0.0, 90.0, 1.8, None, 1.8, 0.0, 0.0, "LINEAR", None, None, None, None),
        FarFieldPoint(90.0, 0.0, -4.0, None, -4.0, 0.0, 0.0, None, None, None, None, None),
        FarFieldPoint(90.0, 90.0, -6.0, None, -6.0, 0.0, 0.0, None, None, None, None, None),
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
            directivity_db=2.20,
            realized_gain_db=1.85,
            mismatch_loss_db=0.20,
            feed_line_loss_db=0.10,
            network_loss_db=0.05,
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
    assert "Gain and efficiency" in report
    assert "Max realized gain" in report
    assert "1.85 dBi" in report


def test_html_report_includes_geometry_and_both_pattern_cuts(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    geometry_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<line x1="0" y1="0" x2="10" y2="10"/></svg>'
    )
    report = render_html_report(
        sample_project,
        design,
        make_result(sample_project),
        geometry_svg=geometry_svg,
    )

    assert "Geometry" in report
    assert geometry_svg in report
    assert "Azimuth cut at" in report
    assert "Elevation cut at" in report
    assert "No azimuth cut available." not in report
    assert "No elevation cut available." not in report
    assert report.count('class="chart pattern-lobe"') == 1
    assert "3D far-field pattern" in report


def test_html_report_explains_missing_geometry_and_patterns(
    sample_project: Project,
) -> None:
    result = make_result(sample_project)
    frequencies = tuple(replace(frequency, far_field=()) for frequency in result.frequencies)
    report = render_html_report(
        sample_project,
        sample_project.designs[0],
        replace(result, frequencies=frequencies),
    )

    assert "No geometry figure available." in report
    assert "No far-field pattern available." in report


def test_html_report_explains_a_single_cut_3d_pattern(sample_project: Project) -> None:
    result = make_result(sample_project)
    single_cut = (
        FarFieldPoint(0.0, 0.0, 2.14, None, 2.14, 0.0, 0.0, None, None, None, None, None),
        FarFieldPoint(90.0, 0.0, -4.0, None, -4.0, 0.0, 0.0, None, None, None, None, None),
    )
    frequencies = tuple(
        replace(frequency, far_field=single_cut) for frequency in result.frequencies
    )

    report = render_html_report(
        sample_project,
        sample_project.designs[0],
        replace(result, frequencies=frequencies),
    )

    assert 'class="chart pattern-lobe"' not in report
    assert (
        "3D pattern unavailable: the far-field data does not contain a 2D angular grid." in report
    )


def test_html_report_lists_driven_sources(sample_project: Project) -> None:
    result = make_result(sample_project)
    sources = (
        SourceResult(
            wire_id="first",
            offset_m=0.0,
            tag=1,
            segment=11,
            amplitude=1.0,
            phase_deg=0.0,
            voltage_v=complex(1.0, 0.0),
            current_a=complex(0.01, -0.02),
            impedance_ohm=complex(60.0, -10.0),
            power_w=0.001,
        ),
        SourceResult(
            wire_id="second",
            offset_m=0.0,
            tag=2,
            segment=22,
            amplitude=0.5,
            phase_deg=90.0,
            voltage_v=complex(0.0, 0.5),
            current_a=complex(0.005, 0.001),
            impedance_ohm=complex(40.0, 20.0),
            power_w=-0.0002,
        ),
    )
    frequencies = tuple(
        replace(frequency, source_results=sources) for frequency in result.frequencies
    )
    report = render_html_report(
        sample_project,
        sample_project.designs[0],
        replace(result, frequencies=frequencies),
    )

    assert "Driven sources" in report
    assert "S2" in report
    assert "second" in report
    assert "-0.000200" in report
    assert "absorbs power" in report


def test_html_report_escapes_user_text(sample_project: Project) -> None:
    project = replace(sample_project, name="<script>alert(1)</script>")
    report = render_html_report(project, project.designs[0], make_result(project))

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in report
    assert "<script>alert(1)</script>" not in report


def test_html_report_supports_new_geometry_summaries(sample_project: Project) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
    from antennadesk.domain.antennas.loop import LoopParameters

    design = sample_project.designs[0]
    folded = design.with_parameters(
        FoldedDipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
            spacing_m=0.2,
        )
    )
    folded_report = render_html_report(sample_project, folded, make_result(sample_project))
    assert "folded dipole" in folded_report
    assert "Element length" in folded_report
    assert "Feed transformer" in folded_report
    assert "4:1" in folded_report

    loop = design.with_parameters(
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=8,
        )
    )
    loop_report = render_html_report(sample_project, loop, make_result(sample_project))
    assert "loop" in loop_report
    assert "Circumference" in loop_report
    assert "Feed transformer" in loop_report
    assert "2:1" in loop_report


def test_html_report_includes_the_current_balun_record(sample_project: Project) -> None:
    project = sample_project.with_current_balun(
        True,
        updated_at=sample_project.updated_at,
    )

    report = render_html_report(project, project.designs[0], make_result(project))

    assert "Current balun" in report
    assert "recorded; common-mode choking is not modeled" in report


def test_html_report_includes_estimator_provenance(sample_project: Project) -> None:
    from antennadesk.domain.projects.project import DesignProvenance

    design = replace(
        sample_project.designs[0],
        provenance=DesignProvenance(
            method_id="loop.resonant_circumference",
            confidence="empirical",
            tolerance_m=1.2,
            source_ids=("arrl.antenna_book.loop.resonant_circumference",),
        ),
    )
    report = render_html_report(sample_project, design, make_result(sample_project))

    assert "Dimension source" in report
    assert "loop.resonant_circumference" in report
    assert "Estimate confidence" in report


def test_html_report_includes_a_band_summary(sample_project: Project) -> None:
    from uuid import uuid4

    from antennadesk.domain.simulation.band_result import BandAnalysisResult, BandResult
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    design = sample_project.designs[0]
    band = amateur_band_by_id("40m")
    assert band is not None
    analysis = BandAnalysisResult(
        design_id=design.id,
        batch_id=uuid4(),
        created_at=datetime(2026, 11, 3, tzinfo=UTC),
        bands=(BandResult(band=band, result=make_result(sample_project)),),
    )

    report = render_html_report(
        sample_project,
        design,
        make_result(sample_project),
        band_analysis=analysis,
    )

    assert "Band summary" in report
    assert "Band patterns" in report
    assert "40m" in report
    assert "Azimuth cut at" in report
    assert "Elevation cut at" in report
    assert report.count('class="chart pattern-lobe"') == 1


def test_spanish_report_uses_roe_not_swr(sample_project: Project) -> None:
    report = render_html_report(
        sample_project,
        sample_project.designs[0],
        make_result(sample_project),
        labeler=Translator(Language.SPANISH).report,
        language="es",
    )

    assert "ROE" in report
    assert "SWR" not in report
    assert "Geometría" in report
    assert "No hay figura de geometría disponible." in report


def test_spanish_report_translates_geometry_and_pattern_headings(
    sample_project: Project,
) -> None:
    report = render_html_report(
        sample_project,
        sample_project.designs[0],
        make_result(sample_project),
        labeler=Translator(Language.SPANISH).report,
        language="es",
        geometry_svg='<svg xmlns="http://www.w3.org/2000/svg"></svg>',
    )

    assert "Geometría" in report
    assert "Corte de azimut" in report
    assert "Corte de elevación" in report
    assert "Patrón 3D de campo lejano" in report
