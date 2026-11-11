# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Self-contained HTML report for one design and simulation result."""

from __future__ import annotations

import html
import math
from pathlib import Path

from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.band_result import BandAnalysisResult
from ..domain.simulation.band_summary import summarize_band
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import SimulationResult
from .design_summary import (
    design_provenance_rows,
    design_summary_rows,
    feed_matching_rows,
    installation_profile_rows,
    load_summary_rows,
    optimization_summary_rows,
    transmission_line_summary_rows,
)
from .localization import (
    Labeler,
    identity_labeler,
    localize_diagnostic,
    localize_html_labels,
    localize_rows,
)
from .result_summary import gain_metric_rows
from .svg_chart import SvgSeries, line_chart_svg

CSS = """
body { font-family: system-ui, sans-serif; margin: 32px; color: #222; background: #fff; }
h1 { font-size: 22px; margin-bottom: 4px; }
h2 { font-size: 16px; margin-top: 28px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
p { line-height: 1.45; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }
th, td { border: 1px solid #ddd; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #f3f3f3; font-weight: 600; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
.muted { color: #666; font-size: 12px; }
.warning { color: #8a5a00; }
.error { color: #b00020; }
.notice { background: #f7f7f7; border-left: 4px solid #999; padding: 10px 14px; margin: 16px 0; }
.chart { margin: 16px 0; }
footer { margin-top: 32px; color: #777; font-size: 11px; }
"""


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _format_swr(value: float) -> str:
    return "∞" if math.isinf(value) else f"{value:.3f}"


def _format_impedance(value: complex) -> str:
    return f"{value.real:.3f} {value.imag:+.3f}j"


def _frequency_series(result: SimulationResult) -> tuple[SvgSeries, ...]:
    if not result.frequencies:
        return ()
    x = [frequency.frequency_hz / 1e6 for frequency in result.frequencies]
    resistance = [frequency.impedance_ohm.real for frequency in result.frequencies]
    reactance = [frequency.impedance_ohm.imag for frequency in result.frequencies]
    return (
        SvgSeries("R", "#1f5fa8", tuple(zip(x, resistance, strict=True))),
        SvgSeries("X", "#d07b1f", tuple(zip(x, reactance, strict=True))),
    )


def _swr_series(result: SimulationResult, tr: Labeler) -> tuple[SvgSeries, ...]:
    points = tuple(
        (frequency.frequency_hz / 1e6, frequency.swr)
        for frequency in result.frequencies
        if math.isfinite(frequency.swr)
    )
    return (SvgSeries(tr("SWR"), "#2e8b57", points),) if points else ()


def _pattern_series(
    result: SimulationResult,
    design: DesignVariant,
    tr: Labeler,
) -> tuple[tuple[SvgSeries, ...], float | None]:
    if not result.frequencies:
        return (), None
    target = design.parameters.frequency_hz
    candidates = [item for item in result.frequencies if item.far_field]
    if not candidates:
        return (), None
    frequency = min(
        candidates,
        key=lambda item: abs(item.frequency_hz - target),
    )
    points = tuple(
        (point.theta_deg, point.gain_total_db)
        for point in frequency.far_field
        if point.gain_total_db is not None
    )
    if not points:
        return (), frequency.frequency_hz
    return (SvgSeries(tr("Total gain"), "#7b4ea3", points),), frequency.frequency_hz


def _diagnostics_table(result: SimulationResult, tr: Labeler) -> str:
    if not result.diagnostics:
        return f'<p class="muted">{_escape(tr("No diagnostics."))}</p>'
    rows = "".join(
        "<tr>"
        f"<td>{_escape(tr(diagnostic.severity.value))}</td>"
        f"<td>{_escape(diagnostic.code)}</td>"
        f"<td>{_escape(localize_diagnostic(diagnostic, tr))}</td>"
        "</tr>"
        for diagnostic in result.diagnostics
    )
    return (
        "<table><thead><tr><th>Severity</th><th>Code</th><th>Message</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def _band_summary_table(analysis: BandAnalysisResult, tr: Labeler) -> str:
    rows = []
    for band_result in analysis.bands:
        summary = summarize_band(band_result.band, band_result.result)
        best_swr = "" if summary.best_swr is None else f"{summary.best_swr:.3f}"
        best_hz = "" if summary.best_swr_hz is None else f"{summary.best_swr_hz / 1e6:.6f}"
        gain = "" if summary.max_gain_db is None else f"{summary.max_gain_db:.2f}"
        takeoff = "" if summary.takeoff_deg is None else f"{summary.takeoff_deg:.1f}"
        efficiency = (
            "" if summary.efficiency_percent is None else f"{summary.efficiency_percent:.1f}"
        )
        rows.append(
            "<tr>"
            f"<td>{_escape(band_result.band.name)}</td>"
            f'<td class="num">{best_swr}</td>'
            f'<td class="num">{best_hz}</td>'
            f'<td class="num">{gain}</td>'
            f'<td class="num">{takeoff}</td>'
            f'<td class="num">{efficiency}</td>'
            f"<td>{_escape(tr(summary.status.value))}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>Band</th><th>Best SWR</th><th>At (MHz)</th>"
        "<th>Gain (dBi)</th><th>Takeoff (°)</th><th>Efficiency (%)</th>"
        "<th>Status</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _band_patterns(
    analysis: BandAnalysisResult,
    design: DesignVariant,
    tr: Labeler,
) -> str:
    charts = []
    for band_result in analysis.bands:
        series, frequency = _pattern_series(band_result.result, design, tr)
        if not series or frequency is None:
            continue
        charts.append(
            '<div class="chart">'
            + line_chart_svg(
                title=tr(
                    "{band} power gain at {frequency:g} MHz",
                    band=band_result.band.name,
                    frequency=frequency / 1e6,
                ),
                x_label=tr("Elevation θ (°)"),
                y_label=tr("Power gain (dBi)"),
                series=series,
            )
            + "</div>"
        )
    return (
        "".join(charts)
        if charts
        else f'<p class="muted">{_escape(tr("No band patterns available."))}</p>'
    )


def render_html_report(
    project: Project,
    design: DesignVariant,
    result: SimulationResult,
    *,
    band_analysis: BandAnalysisResult | None = None,
    labeler: Labeler | None = None,
    language: str = "en",
) -> str:
    tr = labeler or identity_labeler
    parameters = design.parameters
    design_rows = "".join(
        f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>"
        for label, value in localize_rows(
            (
                *design_summary_rows(
                    parameters,
                    labeler=tr,
                    project_network=project.matching_network,
                ),
                *installation_profile_rows(project.active_installation_profile, labeler=tr),
                *feed_matching_rows(
                    project.matching_network,
                    project.feed_line,
                    project.balun_loss,
                    labeler=tr,
                ),
                *optimization_summary_rows(design),
                *design_provenance_rows(design),
                *load_summary_rows(design.antenna.loads, labeler=tr),
                *transmission_line_summary_rows(
                    design.antenna.transmission_lines,
                    labeler=tr,
                ),
            ),
            tr,
        )
    )
    gain_rows = "".join(
        f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>"
        for label, value in localize_rows(gain_metric_rows(result), tr)
    )
    spec = result.spec
    segmentation = spec.segmentation
    if segmentation.segments_per_wire is not None:
        segmentation_text = tr(
            "{count} segments per wire",
            count=segmentation.segments_per_wire,
        )
    else:
        segmentation_text = tr(
            "target λ/{ratio:.0f} per segment",
            ratio=1.0 / segmentation.target_segment_length_wavelengths,
        )

    frequency_plan = spec.frequency_plan
    if frequency_plan.is_single:
        frequency_text = f"{frequency_plan.start_hz / 1e6:g} MHz"
    else:
        frequency_text = tr(
            "{start:g}-{stop:g} MHz, {count} points",
            start=frequency_plan.start_hz / 1e6,
            stop=frequency_plan.stop_hz / 1e6,
            count=frequency_plan.count,
        )

    impedance_rows = "".join(
        "<tr>"
        f'<td class="num">{frequency.frequency_hz / 1e6:.6f}</td>'
        f'<td class="num">{frequency.impedance_ohm.real:.3f}</td>'
        f'<td class="num">{frequency.impedance_ohm.imag:+.3f}</td>'
        f'<td class="num">{abs(frequency.impedance_ohm):.3f}</td>'
        f'<td class="num">{_escape(_format_swr(frequency.swr))}</td>'
        f'<td class="num">{frequency.input_power_w:.6g}</td>'
        "</tr>"
        for frequency in result.frequencies
    )

    resonances = find_resonances(
        [frequency.frequency_hz for frequency in result.frequencies],
        [frequency.impedance_ohm for frequency in result.frequencies],
    )
    resonance_rows = "".join(
        "<tr>"
        f'<td class="num">{point.frequency_hz / 1e6:.6f}</td>'
        f'<td class="num">{point.impedance_ohm.real:.3f}</td>'
        "</tr>"
        for point in resonances
    )
    resonance_section = (
        "<table><thead><tr><th>Frequency (MHz)</th><th>R (Ω)</th></tr></thead>"
        f"<tbody>{resonance_rows}</tbody></table>"
        if resonance_rows
        else f'<p class="muted">{_escape(tr("No resonance in the sweep."))}</p>'
    )

    source_rows = "".join(
        "<tr>"
        f'<td class="num">{frequency.frequency_hz / 1e6:.6f}</td>'
        f'<td class="num">S{source_index}</td>'
        f"<td>{_escape(source.wire_id)}</td>"
        f'<td class="num">{source.amplitude:.3f}</td>'
        f'<td class="num">{source.phase_deg:.1f}°</td>'
        f'<td class="num">{source.impedance_ohm.real:.3f}</td>'
        f'<td class="num">{source.impedance_ohm.imag:+.3f}</td>'
        f'<td class="num">{source.power_w:+.6f}</td>'
        "</tr>"
        for frequency in result.frequencies
        for source_index, source in enumerate(frequency.source_results, start=1)
    )
    multi_source = any(len(frequency.source_results) > 1 for frequency in result.frequencies)
    source_section = (
        "<h2>Driven sources</h2>"
        f'<p class="muted">{_escape(tr("Ideal source inputs; negative power means that source absorbs power. The primary feed remains the impedance/SWR reference."))}</p>'
        "<table><thead><tr><th>Frequency (MHz)</th><th>Source</th><th>Wire</th>"
        "<th>Amplitude</th><th>Phase</th><th>R (Ω)</th><th>X (Ω)</th>"
        "<th>Power (W)</th></tr></thead>"
        f"<tbody>{source_rows}</tbody></table>"
        if multi_source
        else ""
    )

    impedance_chart = line_chart_svg(
        title=tr("Impedance"),
        x_label=tr("Frequency (MHz)"),
        y_label=tr("Impedance (Ω)"),
        series=_frequency_series(result),
    )
    swr_chart = line_chart_svg(
        title=tr("SWR"),
        x_label=tr("Frequency (MHz)"),
        y_label=tr("SWR"),
        series=_swr_series(result, tr),
    )
    pattern_series, pattern_frequency = _pattern_series(result, design, tr)
    pattern_chart = ""
    if pattern_series and pattern_frequency is not None:
        pattern_chart = line_chart_svg(
            title=tr(
                "Power gain pattern at {frequency:g} MHz",
                frequency=pattern_frequency / 1e6,
            ),
            x_label=tr("Elevation θ (°)"),
            y_label=tr("Power gain (dBi)"),
            series=pattern_series,
        )

    finished = (
        result.finished_at.isoformat(timespec="seconds")
        if result.finished_at is not None
        else tr("not recorded")
    )
    diagnostics = _diagnostics_table(result, tr)
    pattern_section = (
        f'<div class="chart">{pattern_chart}</div>'
        if pattern_chart
        else f'<p class="muted">{_escape(tr("No far-field pattern available."))}</p>'
    )
    band_section = ""
    if band_analysis is not None:
        band_section = (
            "<h2>Band summary</h2>"
            f"{_band_summary_table(band_analysis, tr)}"
            "<h2>Band patterns</h2>"
            f"{_band_patterns(band_analysis, design, tr)}"
        )

    status = tr(result.status.value)
    reproducibility = tr(
        "<strong>Reproducibility.</strong> Model/spec fingerprint "
        "<code>{fingerprint}</code> · solver <strong>{solver} {version}</strong> · "
        "status <strong>{status}</strong>.",
        fingerprint=_escape(result.model_fingerprint),
        solver=_escape(result.solver.name),
        version=_escape(result.solver.version),
        status=_escape(status),
    )
    document = f"""<!DOCTYPE html>
<html lang="{_escape(language)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_escape(project.name)} — {_escape(design.name)} — {_escape(tr("AntennaDesk report"))}</title>
<style>{CSS}</style>
</head>
<body>
<h1>{_escape(project.name)} — {_escape(design.name)}</h1>
<p class="muted">{_escape(tr("AntennaDesk simulation report · generated from an immutable result snapshot · {finished}", finished=finished))}</p>

<div class="notice">
{reproducibility}
</div>

<h2>Design</h2>
<table>
{design_rows}
</table>

{band_section}

<h2>Simulation configuration</h2>
<table>
<tr><th>Frequency plan</th><td>{_escape(frequency_text)}</td></tr>
<tr><th>Segmentation</th><td>{_escape(segmentation_text)}</td></tr>
<tr><th>Reference impedance</th><td>{spec.reference_impedance_ohm:g} Ω</td></tr>
<tr><th>Conductor losses</th><td>{_escape(tr("enabled" if spec.include_conductor_losses else "disabled"))}</td></tr>
<tr><th>Far field</th><td>{_escape(tr("enabled" if spec.far_field.enabled else "disabled"))}</td></tr>
<tr><th>Solver executable</th><td>{_escape(result.solver.executable or tr("unknown"))}</td></tr>
</table>

<h2>Impedance</h2>
<table>
<thead><tr><th>Frequency (MHz)</th><th>R (Ω)</th><th>X (Ω)</th><th>|Z| (Ω)</th><th>SWR</th><th>Input power (W)</th></tr></thead>
<tbody>{impedance_rows}</tbody>
</table>
<div class="chart">{impedance_chart}</div>

<h2>Resonance</h2>
{resonance_section}

{source_section}

<h2>SWR</h2>
<div class="chart">{swr_chart}</div>

<h2>Far field</h2>
{pattern_section}

<h2>Gain and efficiency</h2>
<table>
{gain_rows}
</table>

<h2>Diagnostics</h2>
{diagnostics}

<footer>
{_escape(tr("AntennaDesk · GPL-3.0-or-later · This report reflects the model and conditions above. Use the browser print dialog to save it as PDF."))}
</footer>
</body>
</html>
"""
    return localize_html_labels(document, tr)


def write_html_report(
    project: Project,
    design: DesignVariant,
    result: SimulationResult,
    path: Path,
    *,
    band_analysis: BandAnalysisResult | None = None,
    labeler: Labeler | None = None,
    language: str = "en",
) -> None:
    path.write_text(
        render_html_report(
            project,
            design,
            result,
            band_analysis=band_analysis,
            labeler=labeler,
            language=language,
        ),
        encoding="utf-8",
        newline="\n",
    )
