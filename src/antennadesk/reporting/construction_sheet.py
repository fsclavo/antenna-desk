# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Printable construction sheet for a dipole design."""

from __future__ import annotations

import html
import math
from pathlib import Path

from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import FrequencyResult, SimulationResult

CSS = """
body { font-family: system-ui, sans-serif; margin: 28px; color: #222; background: #fff; }
h1 { font-size: 22px; margin-bottom: 2px; }
h2 { font-size: 15px; margin-top: 24px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
p { line-height: 1.45; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }
th, td { border: 1px solid #ddd; padding: 6px 8px; text-align: left; }
th { background: #f3f3f3; width: 34%; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
.muted { color: #666; font-size: 12px; }
.notes { background: #f7f7f7; border-left: 4px solid #888; padding: 10px 14px; }
footer { margin-top: 28px; color: #777; font-size: 11px; }
"""


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _nearest_frequency(
    result: SimulationResult,
    target_hz: float,
) -> FrequencyResult | None:
    if not result.frequencies:
        return None
    return min(result.frequencies, key=lambda item: abs(item.frequency_hz - target_hz))


def _swr_text(frequency: FrequencyResult | None) -> str:
    if frequency is None:
        return "—"
    return "∞" if math.isinf(frequency.swr) else f"{frequency.swr:.3f}"


def _max_gain(result: SimulationResult | None) -> float | None:
    if result is None:
        return None
    gains = [
        point.gain_total_db
        for frequency in result.frequencies
        for point in frequency.far_field
        if point.gain_total_db is not None
    ]
    return max(gains) if gains else None


def _resonance_text(result: SimulationResult | None) -> str:
    if result is None or len(result.frequencies) < 2:
        return "—"
    resonances = find_resonances(
        [frequency.frequency_hz for frequency in result.frequencies],
        [frequency.impedance_ohm for frequency in result.frequencies],
    )
    if not resonances:
        return "No resonance in the sweep."
    return " · ".join(
        f"{point.frequency_hz / 1e6:.3f} MHz (R={point.impedance_ohm.real:.1f} Ω)"
        for point in resonances
    )


def render_construction_sheet(
    project: Project,
    design: DesignVariant,
    result: SimulationResult | None,
) -> str:
    parameters = design.parameters
    antenna = design.antenna
    feed_wire = antenna.feed_wire
    feed_offset_m = antenna.feed.offset_m
    other_leg_m = max(feed_wire.length_m - feed_offset_m, 0.0)
    feed_ratio = feed_offset_m / feed_wire.length_m if feed_wire.length_m > 0 else 0.0
    feed_height_m = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio
    azimuth_text = (
        f"{parameters.azimuth_deg:.1f}°" if parameters.orientation.value == "horizontal" else "—"
    )
    frequency = _nearest_frequency(result, parameters.frequency_hz) if result else None
    max_gain = _max_gain(result)
    efficiency = (
        frequency.power_budget.efficiency_percent
        if frequency is not None and frequency.power_budget is not None
        else None
    )
    ground = design.antenna.environment.ground
    ground_text = ground.kind.value
    if ground.relative_permittivity is not None and ground.conductivity_s_per_m is not None:
        ground_text = (
            f"{ground_text} (eps_r={ground.relative_permittivity:g}, "
            f"sigma={ground.conductivity_s_per_m:g} S/m)"
        )

    simulation_rows = ""
    if result is not None and frequency is not None:
        simulation_rows = f"""
<tr><th>Simulated frequency</th><td>{frequency.frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Impedance</th><td>{frequency.impedance_ohm.real:.3f} {frequency.impedance_ohm.imag:+.3f}j Ω</td></tr>
<tr><th>SWR ({result.spec.reference_impedance_ohm:g} Ω)</th><td>{_swr_text(frequency)}</td></tr>
<tr><th>Max power gain</th><td>{f"{max_gain:.2f} dBi" if max_gain is not None else "—"}</td></tr>
<tr><th>Efficiency</th><td>{f"{efficiency:.2f} %" if efficiency is not None else "—"}</td></tr>
<tr><th>Resonance</th><td>{_escape(_resonance_text(result))}</td></tr>
<tr><th>Solver</th><td>{_escape(result.solver.name)} {_escape(result.solver.version)}</td></tr>
<tr><th>Fingerprint</th><td><code>{_escape(result.model_fingerprint)}</code></td></tr>
"""
    else:
        simulation_rows = "<tr><th>Simulation</th><td>No result yet.</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_escape(project.name)} — {_escape(design.name)} — construction sheet</title>
<style>{CSS}</style>
</head>
<body>
<h1>{_escape(project.name)} — {_escape(design.name)}</h1>
<p class="muted">AntennaDesk construction sheet · SI units (m, MHz, Ω)</p>

<h2>Dimensions</h2>
<table>
<tr><th>Target frequency</th><td>{parameters.frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Orientation</th><td>{_escape(parameters.orientation.value)}</td></tr>
<tr><th>Total wire length</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>First leg (from wire start)</th><td>{feed_offset_m:.4f} m</td></tr>
<tr><th>Second leg (from feed)</th><td>{other_leg_m:.4f} m</td></tr>
<tr><th>Wire height at start</th><td>{feed_wire.start.z_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
<tr><th>Azimuth</th><td>{azimuth_text}</td></tr>
<tr><th>Wire diameter</th><td>{parameters.wire_radius_m * 2000.0:.3f} mm</td></tr>
<tr><th>Material</th><td>{_escape(parameters.material.name)} ({parameters.material.conductivity_s_per_m:.3g} S/m)</td></tr>
<tr><th>Ground</th><td>{_escape(ground_text)}</td></tr>
</table>

<h2>Simulation</h2>
<table>
{simulation_rows}
</table>

<h2>Construction notes</h2>
<div class="notes">
<p>Cut the two legs to the dimensions above, leaving a small feed gap at the
center. The feed point is {feed_offset_m:.4f} m from the start of the wire
and {other_leg_m:.4f} m from the end.</p>
<p>Trim and re-measure after installation. Real ground, supports, feed line,
and nearby objects can shift the result. A low SWR does not prove high
efficiency or a useful radiation pattern.</p>
</div>

<footer>AntennaDesk · GPL-3.0-or-later · Use the browser print dialog to save
this sheet as PDF.</footer>
</body>
</html>
"""


def write_construction_sheet(
    project: Project,
    design: DesignVariant,
    result: SimulationResult | None,
    path: Path,
) -> None:
    path.write_text(
        render_construction_sheet(project, design, result),
        encoding="utf-8",
        newline="\n",
    )
