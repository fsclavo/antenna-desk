# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Self-contained HTML report for one design and simulation result."""

from __future__ import annotations

import html
import math
from pathlib import Path

from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import SimulationResult
from .design_summary import design_summary_rows, load_summary_rows
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


def _swr_series(result: SimulationResult) -> tuple[SvgSeries, ...]:
    points = tuple(
        (frequency.frequency_hz / 1e6, frequency.swr)
        for frequency in result.frequencies
        if math.isfinite(frequency.swr)
    )
    return (SvgSeries("SWR", "#2e8b57", points),) if points else ()


def _pattern_series(
    result: SimulationResult,
    design: DesignVariant,
) -> tuple[tuple[SvgSeries, ...], float | None]:
    if not result.frequencies:
        return (), None
    target = design.parameters.frequency_hz
    frequency = min(
        result.frequencies,
        key=lambda item: abs(item.frequency_hz - target),
    )
    points = tuple(
        (point.theta_deg, point.gain_total_db)
        for point in frequency.far_field
        if point.gain_total_db is not None
    )
    if not points:
        return (), frequency.frequency_hz
    return (SvgSeries("Total gain", "#7b4ea3", points),), frequency.frequency_hz


def _diagnostics_table(result: SimulationResult) -> str:
    if not result.diagnostics:
        return '<p class="muted">No diagnostics.</p>'
    rows = "".join(
        "<tr>"
        f"<td>{_escape(diagnostic.severity.value)}</td>"
        f"<td>{_escape(diagnostic.code)}</td>"
        f"<td>{_escape(diagnostic.message)}</td>"
        "</tr>"
        for diagnostic in result.diagnostics
    )
    return (
        "<table><thead><tr><th>Severity</th><th>Code</th><th>Message</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def render_html_report(
    project: Project,
    design: DesignVariant,
    result: SimulationResult,
) -> str:
    parameters = design.parameters
    design_rows = "".join(
        f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>"
        for label, value in (
            *design_summary_rows(parameters),
            *load_summary_rows(design.antenna.loads),
        )
    )
    spec = result.spec
    segmentation = spec.segmentation
    if segmentation.segments_per_wire is not None:
        segmentation_text = f"{segmentation.segments_per_wire} segments per wire"
    else:
        segmentation_text = (
            f"target λ/{1.0 / segmentation.target_segment_length_wavelengths:.0f} per segment"
        )

    frequency_plan = spec.frequency_plan
    if frequency_plan.is_single:
        frequency_text = f"{frequency_plan.start_hz / 1e6:g} MHz"
    else:
        frequency_text = (
            f"{frequency_plan.start_hz / 1e6:g}-{frequency_plan.stop_hz / 1e6:g} MHz, "
            f"{frequency_plan.count} points"
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
        else '<p class="muted">No resonance in the sweep.</p>'
    )

    impedance_chart = line_chart_svg(
        title="Impedance",
        x_label="Frequency (MHz)",
        y_label="Impedance (Ω)",
        series=_frequency_series(result),
    )
    swr_chart = line_chart_svg(
        title="SWR",
        x_label="Frequency (MHz)",
        y_label="SWR",
        series=_swr_series(result),
    )
    pattern_series, pattern_frequency = _pattern_series(result, design)
    pattern_chart = ""
    if pattern_series and pattern_frequency is not None:
        pattern_chart = line_chart_svg(
            title=f"Power gain pattern at {pattern_frequency / 1e6:g} MHz",
            x_label="Elevation θ (°)",
            y_label="Power gain (dBi)",
            series=pattern_series,
        )

    finished = (
        result.finished_at.isoformat(timespec="seconds")
        if result.finished_at is not None
        else "not recorded"
    )
    diagnostics = _diagnostics_table(result)
    pattern_section = (
        f'<div class="chart">{pattern_chart}</div>'
        if pattern_chart
        else '<p class="muted">No far-field pattern available.</p>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_escape(project.name)} — {_escape(design.name)} — AntennaDesk report</title>
<style>{CSS}</style>
</head>
<body>
<h1>{_escape(project.name)} — {_escape(design.name)}</h1>
<p class="muted">AntennaDesk simulation report · generated from an immutable result snapshot · {_escape(finished)}</p>

<div class="notice">
<strong>Reproducibility.</strong> Model/spec fingerprint
<code>{_escape(result.model_fingerprint)}</code> · solver
<strong>{_escape(result.solver.name)} {_escape(result.solver.version)}</strong> ·
status <strong>{_escape(result.status.value)}</strong>.
</div>

<h2>Design</h2>
<table>
{design_rows}
</table>

<h2>Simulation configuration</h2>
<table>
<tr><th>Frequency plan</th><td>{_escape(frequency_text)}</td></tr>
<tr><th>Segmentation</th><td>{_escape(segmentation_text)}</td></tr>
<tr><th>Reference impedance</th><td>{spec.reference_impedance_ohm:g} Ω</td></tr>
<tr><th>Conductor losses</th><td>{"enabled" if spec.include_conductor_losses else "disabled"}</td></tr>
<tr><th>Far field</th><td>{"enabled" if spec.far_field.enabled else "disabled"}</td></tr>
<tr><th>Solver executable</th><td>{_escape(result.solver.executable or "unknown")}</td></tr>
</table>

<h2>Impedance</h2>
<table>
<thead><tr><th>Frequency (MHz)</th><th>R (Ω)</th><th>X (Ω)</th><th>|Z| (Ω)</th><th>SWR</th><th>Input power (W)</th></tr></thead>
<tbody>{impedance_rows}</tbody>
</table>
<div class="chart">{impedance_chart}</div>

<h2>Resonance</h2>
{resonance_section}

<h2>SWR</h2>
<div class="chart">{swr_chart}</div>

<h2>Far field</h2>
{pattern_section}

<h2>Diagnostics</h2>
{diagnostics}

<footer>
AntennaDesk · GPL-3.0-or-later · This report reflects the model and conditions above.
Use the browser print dialog to save it as PDF.
</footer>
</body>
</html>
"""


def write_html_report(
    project: Project,
    design: DesignVariant,
    result: SimulationResult,
    path: Path,
) -> None:
    path.write_text(
        render_html_report(project, design, result),
        encoding="utf-8",
        newline="\n",
    )
