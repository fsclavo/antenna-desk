# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Printable construction sheet for a dipole design."""

from __future__ import annotations

import html
import math
from pathlib import Path

from ..domain.antennas.dipole import DipoleParameters
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.loop import LoopParameters
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import FrequencyResult, SimulationResult
from .design_summary import design_summary_rows, load_summary_rows

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
    feed_ratio = feed_offset_m / feed_wire.length_m if feed_wire.length_m > 0 else 0.0
    feed_height_m = feed_wire.start.z_m + (feed_wire.end.z_m - feed_wire.start.z_m) * feed_ratio
    frequency = _nearest_frequency(result, parameters.frequency_hz) if result else None
    max_gain = _max_gain(result)
    efficiency = (
        frequency.power_budget.efficiency_percent
        if frequency is not None and frequency.power_budget is not None
        else None
    )

    dimension_rows = "".join(
        f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>"
        for label, value in (
            *design_summary_rows(parameters),
            *load_summary_rows(design.antenna.loads),
        )
    )
    if isinstance(parameters, DipoleParameters):
        other_leg_m = max(feed_wire.length_m - feed_offset_m, 0.0)
        feed_rows = f"""
<tr><th>First leg (from wire start)</th><td>{feed_offset_m:.4f} m</td></tr>
<tr><th>Second leg (from feed)</th><td>{other_leg_m:.4f} m</td></tr>
<tr><th>Wire height at start</th><td>{feed_wire.start.z_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut the two legs to the dimensions above, leaving a small feed gap at the
center. The feed point is {feed_offset_m:.4f} m from the start of the wire
and {other_leg_m:.4f} m from the end.</p>"""
    elif isinstance(parameters, FoldedDipoleParameters):
        feed_rows = f"""
<tr><th>Driven element length</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>End connector length</th><td>{parameters.spacing_m:.4f} m</td></tr>
<tr><th>Feed location</th><td>center of driven element</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut two equal driven elements of {parameters.total_length_m:.4f} m
and two end connectors of {parameters.spacing_m:.4f} m. Join them at both
ends and feed the center of one element. The total conductor length is
{parameters.total_conductor_length_m:.4f} m.</p>"""
    elif isinstance(parameters, FanDipoleParameters):
        lengths = ", ".join(f"{element.length_m:.4f} m" for element in parameters.elements)
        feed_rows = f"""
<tr><th>Pairs</th><td>{len(parameters.elements)}</td></tr>
<tr><th>Element lengths</th><td>{_escape(lengths)}</td></tr>
<tr><th>Apex height</th><td>{parameters.apex_height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut {len(parameters.elements)} dipole pairs with lengths
{_escape(lengths)}. Join all pairs at the common apex and feed there.</p>"""
    elif isinstance(parameters, MoxonParameters):
        feed_rows = f"""
<tr><th>Element width</th><td>{parameters.width_m:.4f} m</td></tr>
<tr><th>Element spacing</th><td>{parameters.depth_m:.4f} m</td></tr>
<tr><th>Reflector tip</th><td>{parameters.reflector_tip_m:.4f} m</td></tr>
<tr><th>Driven tip</th><td>{parameters.driven_tip_m:.4f} m</td></tr>
<tr><th>Tip gap</th><td>{parameters.gap_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Build a Moxon rectangle with {parameters.width_m:.4f} m elements,
{parameters.depth_m:.4f} m spacing, and bent tips leaving a
{parameters.gap_m:.4f} m gap.</p>"""
    elif isinstance(parameters, YagiParameters):
        positions = [element.position_m for element in parameters.elements]
        feed_rows = f"""
<tr><th>Elements</th><td>{len(parameters.elements)}</td></tr>
<tr><th>Boom length</th><td>{max(positions) - min(positions):.4f} m</td></tr>
<tr><th>Driven element</th><td>{parameters.driven_index + 1}</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Build {len(parameters.elements)} parallel elements on a
{max(positions) - min(positions):.4f} m boom. Feed the center of element
{parameters.driven_index + 1}.</p>"""
    elif isinstance(parameters, InvertedVParameters):
        feed_rows = f"""
<tr><th>Leg length</th><td>{parameters.leg_length_m:.4f} m</td></tr>
<tr><th>Apex height</th><td>{parameters.apex_height_m:.4f} m</td></tr>
<tr><th>End height</th><td>{parameters.end_height_m:.4f} m</td></tr>
<tr><th>Included angle</th><td>{parameters.included_angle_deg:.1f}°</td></tr>
"""
        construction_note = f"""<p>Cut two legs of {parameters.leg_length_m:.4f} m and join them at
the apex with an included angle of {parameters.included_angle_deg:.1f}°.
The apex is {parameters.apex_height_m:.4f} m above ground.</p>"""
    elif isinstance(parameters, VerticalParameters):
        feed_rows = f"""
<tr><th>Radiator height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Radials</th><td>{parameters.radial_count}</td></tr>
<tr><th>Radial length</th><td>{parameters.radial_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Install a {parameters.height_m:.4f} m vertical radiator with its base
{parameters.base_height_m:.4f} m above ground. Add {parameters.radial_count} radials of
{parameters.radial_length_m:.4f} m in the base plane.</p>"""
    elif isinstance(parameters, OCFDParameters):
        other_leg_m = max(feed_wire.length_m - feed_offset_m, 0.0)
        feed_rows = f"""
<tr><th>Feed offset from start</th><td>{feed_offset_m:.4f} m</td></tr>
<tr><th>Remaining leg</th><td>{other_leg_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut one conductor to {parameters.total_length_m:.4f} m.
Feed it {feed_offset_m:.4f} m from the start ({parameters.feed_ratio * 100:.1f}% of its length).</p>"""
    elif isinstance(parameters, LoopParameters):
        feed_rows = f"""
<tr><th>Side length</th><td>{parameters.side_length_m:.4f} m</td></tr>
<tr><th>Feed side</th><td>{_escape(antenna.feed.wire_id)}</td></tr>
<tr><th>Feed location</th><td>midpoint of the first side</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut one conductor to {parameters.circumference_m:.4f} m and
close it into {parameters.sides} equal sides of {parameters.side_length_m:.4f} m.
Feed the midpoint of the first side.</p>"""
    else:
        raise TypeError(f"unsupported antenna parameters: {type(parameters)!r}")

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
{dimension_rows}
{feed_rows}
</table>

<h2>Simulation</h2>
<table>
{simulation_rows}
</table>

<h2>Construction notes</h2>
<div class="notes">
{construction_note}
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
