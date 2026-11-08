# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Printable construction sheet for a design."""

from __future__ import annotations

import html
import math
from pathlib import Path

from ..domain.antennas.beverage import BeverageParameters
from ..domain.antennas.biquad import BiquadParameters
from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.dipole import DipoleParameters
from ..domain.antennas.endfed import EndFedParameters
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.inverted_l import InvertedLParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.loaded_dipole import LoadedDipoleParameters
from ..domain.antennas.loop import LoopOrientation, LoopParameters
from ..domain.antennas.magnetic_loop import MagneticLoopParameters
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.phased_vertical import PhasedVerticalParameters
from ..domain.antennas.quad_beam import QuadBeamParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvKind, ScvParameters
from ..domain.antennas.t2fd import T2FDParameters
from ..domain.antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zepp import (
    ZEPP_MATCHING_FEED_ID,
    ZEPP_MATCHING_OPEN_ID,
    ZEPP_RADIATOR_ID,
    ZeppParameters,
    parallel_wire_impedance_ohm,
)
from ..domain.optimization.length import measure_bandwidth_hz
from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import FrequencyResult, SimulationResult
from .design_summary import (
    design_provenance_rows,
    design_summary_rows,
    load_summary_rows,
    optimization_summary_rows,
    transmission_line_summary_rows,
)
from .result_summary import gain_metric_rows

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
    efficiency = (
        frequency.power_budget.efficiency_percent
        if frequency is not None and frequency.power_budget is not None
        else None
    )

    dimension_rows = "".join(
        f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>"
        for label, value in (
            *design_summary_rows(parameters),
            *optimization_summary_rows(design),
            *design_provenance_rows(design),
            *load_summary_rows(design.antenna.loads),
            *transmission_line_summary_rows(design.antenna.transmission_lines),
        )
    )
    if isinstance(parameters, DipoleParameters):
        if parameters.sag_m > 0.0:
            feed_rows = f"""
<tr><th>Span</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>Conductor length</th><td>{parameters.conductor_length_m:.4f} m</td></tr>
<tr><th>Wire height at supports</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Center sag</th><td>{parameters.sag_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
            construction_note = f"""<p>Cut one conductor to
{parameters.conductor_length_m:.4f} m. Support the ends at
{parameters.height_m:.4f} m and let the center sag by
{parameters.sag_m:.4f} m; the feed is at the lowest point,
{feed_height_m:.4f} m above ground. The sagged shape is approximated by
straight NEC segments between the sampled points.</p>"""
        else:
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
    elif isinstance(parameters, TrapDipoleParameters):
        left_position, right_position = parameters.trap_positions_m
        feed_rows = f"""
<tr><th>Total wire length</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>Center section</th><td>{parameters.inner_length_m:.4f} m</td></tr>
<tr><th>Outer sections</th><td>{parameters.outer_length_m:.4f} m each</td></tr>
<tr><th>Trap positions</th><td>{left_position:.4f} m, {right_position:.4f} m from wire start</td></tr>
<tr><th>Trap frequency</th><td>{parameters.trap_frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Trap inductance</th><td>{parameters.trap_inductance_h * 1e6:.4f} µH</td></tr>
<tr><th>Trap capacitance</th><td>{parameters.trap_capacitance_f * 1e12:.4f} pF</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut one conductor to {parameters.total_length_m:.4f} m.
Mark the trap positions at {left_position:.4f} m and {right_position:.4f} m from
the start, leaving a {parameters.inner_length_m:.4f} m center section. Install
 parallel LC traps tuned to {parameters.trap_frequency_hz / 1e6:.6f} MHz
({parameters.trap_inductance_h * 1e6:.4f} µH, {parameters.trap_capacitance_f * 1e12:.4f} pF).
Feed the center of the element.</p>"""
    elif isinstance(parameters, T2FDParameters):
        feed_rows = f"""
<tr><th>Element length</th><td>{parameters.length_m:.4f} m each</td></tr>
<tr><th>Conductor spacing</th><td>{parameters.spacing_m:.4f} m</td></tr>
<tr><th>Design band</th><td>{parameters.frequency_hz / 1e6:.6f} MHz to {parameters.highest_frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Termination resistor</th><td>{parameters.termination_resistance_ohm:g} Ω non-inductive</td></tr>
<tr><th>Feed transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut two equal conductors of {parameters.length_m:.4f} m
and two end connectors of {parameters.spacing_m:.4f} m. Join them at both ends
to form a folded loop. Feed the midpoint of one conductor through a
{parameters.transformer_ratio:g}:1 transformer. Install a
{parameters.termination_resistance_ohm:g} Ω non-inductive resistor at the
midpoint of the other conductor, opposite the feed point. The total conductor
length is {parameters.total_conductor_length_m:.4f} m.</p>"""
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
    elif isinstance(parameters, ScvParameters):
        if parameters.kind is ScvKind.HALF_SQUARE:
            feed_point = "the top corner of one outer vertical"
            wire_note = (
                f"Cut two vertical wires of {parameters.vertical_height_m:.4f} m and "
                f"one top wire of {parameters.horizontal_length_m:.4f} m."
            )
        else:
            feed_point = "the top junction of the center vertical and the top wires"
            wire_note = (
                f"Cut three vertical wires of {parameters.vertical_height_m:.4f} m and "
                f"two top wires of {parameters.horizontal_segment_m:.4f} m each."
            )
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Horizontal length</th><td>{parameters.horizontal_length_m:.4f} m</td></tr>
<tr><th>Horizontal segment</th><td>{parameters.horizontal_segment_m:.4f} m each</td></tr>
<tr><th>Vertical height</th><td>{parameters.vertical_height_m:.4f} m</td></tr>
<tr><th>Vertical elements</th><td>{parameters.vertical_count}</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Top height</th><td>{parameters.top_height_m:.4f} m</td></tr>
<tr><th>Feed offset below top</th><td>{parameters.feed_offset_m:.4f} m</td></tr>
<tr><th>Total conductor</th><td>{parameters.total_conductor_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Build a {parameters.template_name.lower()} with
{parameters.vertical_count} vertical elements joined at the top.
{wire_note} Keep the bottom ends insulated from ground and feed
{feed_point}. The feed is {parameters.feed_offset_m:.4f} m below the top
junction at {feed_height_m:.4f} m above ground.</p>"""
    elif isinstance(parameters, LoadedDipoleParameters):
        coil_note = (
            f"Fit two {parameters.loading_coil_inductance_h * 1e6:.3f} µH loading "
            f"coils at {parameters.link_offset_m:.4f} m either side of the feed; each "
            f"coil has {parameters.loading_coil_resistance_ohm:.3f} Ω series "
            "resistance."
            if parameters.coil_active
            else (
                "Leave the links open and use only the center section."
                if parameters.link_open
                else "No loading coils are fitted."
            )
        )
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Active length</th><td>{parameters.active_length_m:.4f} m</td></tr>
<tr><th>Full length</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>Link offset</th><td>{parameters.link_offset_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut the full {parameters.total_length_m:.4f} m
wire and mark the link positions at {parameters.link_offset_m:.4f} m either
side of the center. Feed the center. {coil_note} The coil model is an ideal
series R-L load; tune it for the installed height and ground.</p>"""
    elif isinstance(parameters, QuadBeamParameters):
        director_note = (
            f" The director loop is {parameters.director_side_m:.4f} m per side "
            f"at {parameters.director_spacing_m:.4f} m in front of the driven loop."
            if parameters.element_count == 3
            else ""
        )
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Loops</th><td>{parameters.element_count}</td></tr>
<tr><th>Driven loop side</th><td>{parameters.loop_side_m:.4f} m</td></tr>
<tr><th>Reflector side</th><td>{parameters.reflector_side_m:.4f} m</td></tr>
<tr><th>Reflector spacing</th><td>{parameters.reflector_spacing_m:.4f} m</td></tr>
<tr><th>Boom length</th><td>{parameters.boom_length_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{parameters.feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Build {parameters.element_count} square loops
with the driven loop at {parameters.loop_side_m:.4f} m per side and the
reflector at {parameters.reflector_side_m:.4f} m per side.
Set the reflector {parameters.reflector_spacing_m:.4f} m behind the driven
loop.{director_note} Feed the midpoint of the driven loop's left vertical
side and keep the loops square. The boom, spreaders, mast, and matching
network are not modeled; tune the match for the installed antenna.</p>"""
    elif isinstance(parameters, PhasedVerticalParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Verticals</th><td>{parameters.element_count}</td></tr>
<tr><th>Element spacing</th><td>{parameters.spacing_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Phase step</th><td>{parameters.phase_step_deg:.1f}°</td></tr>
<tr><th>Amplitude taper</th><td>{parameters.amplitude_taper * 100.0:.0f}%</td></tr>
<tr><th>Radials per element</th><td>{parameters.radial_count}</td></tr>
<tr><th>Radial length</th><td>{parameters.radial_length_m:.4f} m</td></tr>
<tr><th>Total conductor</th><td>{parameters.total_conductor_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Build {parameters.element_count} vertical
radiators of {parameters.height_m:.4f} m, spaced {parameters.spacing_m:.4f} m
along one line, with their bases at {parameters.base_height_m:.4f} m above
ground. Fit {parameters.radial_count} radials of
{parameters.radial_length_m:.4f} m to each base. Drive the first vertical as
the primary feed and the remaining verticals with the listed phase and
amplitude steps. The combining network is ideal and is not included; use an
explicit feed network and verify the match.</p>"""
    elif isinstance(parameters, BeverageParameters):
        termination_note = (
            f"Fit a {parameters.termination_resistance_ohm:.1f} Ω resistor from "
            "the far end to a ground rod."
            if parameters.termination_enabled
            else "Leave the far end open for a bidirectional receiving pattern."
        )
        termination_row = (
            f"{parameters.termination_resistance_ohm:.1f} Ω to ground"
            if parameters.termination_enabled
            else "disabled"
        )
        feed_rows = f"""
<tr><th>Type</th><td>Beverage</td></tr>
<tr><th>Length</th><td>{parameters.length_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Termination</th><td>{termination_row}</td></tr>
<tr><th>Total conductor</th><td>{parameters.total_conductor_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Run one horizontal wire of
{parameters.length_m:.4f} m at {parameters.height_m:.4f} m above ground.
Feed the near end directly and keep the wire straight. {termination_note}
The one-wavelength starting length and termination value are heuristics; the
pattern and receiving performance are not independently validated.</p>"""
    elif isinstance(parameters, BiquadParameters):
        reflector_note = (
            f"A wire reflector sits {parameters.reflector_spacing_m:.4f} m behind the driven plane."
            if parameters.reflector_enabled
            else "This variant has no reflector."
        )
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Loops</th><td>{parameters.loop_count}</td></tr>
<tr><th>Loop side</th><td>{parameters.loop_side_m:.4f} m</td></tr>
<tr><th>Stack height</th><td>{parameters.total_height_m:.4f} m</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Feed height</th><td>{parameters.feed_height_m:.4f} m</td></tr>
<tr><th>Reflector</th><td>{parameters.reflector_spacing_m:.4f} m behind</td></tr>
<tr><th>Total conductor</th><td>{parameters.total_conductor_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Build {parameters.loop_count} square loops with
{parameters.loop_side_m:.4f} m sides. Join them at the shared horizontal
rails, starting at {parameters.base_height_m:.4f} m above ground, and feed
the midpoint of the central rail at {feed_height_m:.4f} m. {reflector_note}
The quarter-wave side and eighth-wave reflector spacing are starting
dimensions; tune them for the installation.</p>"""
    elif isinstance(parameters, RingoParameters):
        feed_rows = f"""
<tr><th>Radiator height</th><td>{parameters.radiator_height_m:.4f} m</td></tr>
<tr><th>Ring diameter</th><td>{parameters.ring_diameter_m:.4f} m</td></tr>
<tr><th>Ring height</th><td>{parameters.ring_height_m:.4f} m</td></tr>
<tr><th>Ring sides</th><td>{parameters.ring_sides}</td></tr>
"""
        construction_note = f"""<p>Build a {parameters.radiator_height_m:.4f} m vertical radiator
with a {parameters.ring_diameter_m:.4f} m matching ring at
{parameters.ring_height_m:.4f} m above ground.</p>"""
    elif isinstance(parameters, JPoleParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Radiator height</th><td>{parameters.radiator_height_m:.4f} m</td></tr>
<tr><th>Stub length</th><td>{parameters.stub_length_m:.4f} m</td></tr>
<tr><th>Stub spacing</th><td>{parameters.spacing_m:.4f} m</td></tr>
<tr><th>Feed offset</th><td>{parameters.feed_offset_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Build a {parameters.template_name} with a
{parameters.radiator_height_m:.4f} m radiator and a {parameters.stub_length_m:.4f} m
stub spaced {parameters.spacing_m:.4f} m.</p>"""
    elif isinstance(parameters, EndFedParameters):
        counterpoise = (
            f"{parameters.counterpoise_length_m:.4f} m at {parameters.counterpoise_height_m:.4f} m"
            if parameters.counterpoise_length_m > 0.0
            else "none"
        )
        feed_rows = f"""
<tr><th>Wire length</th><td>{parameters.length_m:.4f} m</td></tr>
<tr><th>Feed height</th><td>{parameters.feed_height_m:.4f} m</td></tr>
<tr><th>End height</th><td>{parameters.end_height_m:.4f} m</td></tr>
<tr><th>Transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Counterpoise</th><td>{counterpoise}</td></tr>
"""
        construction_note = f"""<p>Cut one wire to {parameters.length_m:.4f} m and feed it at one end.
The feed is at {parameters.feed_height_m:.4f} m and the far end at
{parameters.end_height_m:.4f} m. Use a {parameters.transformer_ratio:g}:1
transformer; the counterpoise is {counterpoise}.</p>"""
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
        folded_row = ""
        folded_note = ""
        if parameters.driven_folded:
            folded_row = f"""
<tr><th>Folded driven element</th><td>yes</td></tr>
<tr><th>Fold spacing</th><td>{parameters.driven_fold_spacing_m:.4f} m</td></tr>
"""
            folded_note = f""" The driven element is folded with
{parameters.driven_fold_spacing_m:.4f} m spacing and two end connectors. Feed one
conductor at its center; the second conductor remains passive."""
        match_row = ""
        match_note = ""
        if parameters.match_type.value == "beta_hairpin":
            match_row = f"""
<tr><th>Feed match</th><td>beta / hairpin</td></tr>
<tr><th>Hairpin length</th><td>{parameters.match_length_m:.4f} m</td></tr>
<tr><th>Hairpin spacing</th><td>{parameters.match_spacing_m:.4f} m</td></tr>
"""
            match_note = f""" A beta/hairpin stub is connected across the
{parameters.match_spacing_m:.4f} m driven-element gap and shorted
{parameters.match_length_m:.4f} m along the boom."""
        feed_rows = f"""
<tr><th>Elements</th><td>{len(parameters.elements)}</td></tr>
<tr><th>Boom length</th><td>{max(positions) - min(positions):.4f} m</td></tr>
<tr><th>Driven element</th><td>{parameters.driven_index + 1}</td></tr>
{folded_row}
{match_row}
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Build {len(parameters.elements)} parallel elements on a
{max(positions) - min(positions):.4f} m boom. Feed the center of element
{parameters.driven_index + 1}.{folded_note}{match_note}</p>"""
    elif isinstance(parameters, InvertedLParameters):
        feed_rows = f"""
<tr><th>Vertical section</th><td>{parameters.vertical_height_m:.4f} m</td></tr>
<tr><th>Horizontal top run</th><td>{parameters.horizontal_length_m:.4f} m</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Top height</th><td>{parameters.top_height_m:.4f} m</td></tr>
<tr><th>Total wire length</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>Azimuth</th><td>{parameters.azimuth_deg:.1f}°</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut one conductor to {parameters.total_length_m:.4f} m.
Install {parameters.vertical_height_m:.4f} m vertically with the base
{parameters.base_height_m:.4f} m above ground, then run the remaining
{parameters.horizontal_length_m:.4f} m horizontally at
{parameters.top_height_m:.4f} m. Feed the base of the vertical section.</p>"""
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
        top_hat_rows = ""
        top_hat_note = ""
        if parameters.top_hat_enabled:
            top_hat_rows = f"""
<tr><th>Top hat wires</th><td>{parameters.top_hat_wire_count}</td></tr>
<tr><th>Top hat radius</th><td>{parameters.top_hat_radius_m:.4f} m</td></tr>
"""
            top_hat_note = f""" Add {parameters.top_hat_wire_count} horizontal
top-hat wires of {parameters.top_hat_radius_m:.4f} m at the radiator top."""
        feed_rows = f"""
<tr><th>Radiator height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Radials</th><td>{parameters.radial_count}</td></tr>
<tr><th>Radial length</th><td>{parameters.radial_length_m:.4f} m</td></tr>
{top_hat_rows}
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Install a {parameters.height_m:.4f} m vertical radiator with its base
{parameters.base_height_m:.4f} m above ground. Add {parameters.radial_count} radials of
{parameters.radial_length_m:.4f} m in the base plane.{top_hat_note}</p>"""
    elif isinstance(parameters, OCFDParameters):
        other_leg_m = max(feed_wire.length_m - feed_offset_m, 0.0)
        feed_rows = f"""
<tr><th>Feed offset from start</th><td>{feed_offset_m:.4f} m</td></tr>
<tr><th>Remaining leg</th><td>{other_leg_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut one conductor to {parameters.total_length_m:.4f} m.
Feed it {feed_offset_m:.4f} m from the start ({parameters.feed_ratio * 100:.1f}% of its length).</p>"""
    elif isinstance(parameters, MagneticLoopParameters):
        feed_rows = f"""
<tr><th>Loop diameter</th><td>{parameters.diameter_m:.4f} m</td></tr>
<tr><th>Loop circumference</th><td>{parameters.circumference_m:.4f} m</td></tr>
<tr><th>Metal conductor length</th><td>{parameters.loop_conductor_length_m:.4f} m</td></tr>
<tr><th>Polygon sides</th><td>{parameters.sides}</td></tr>
<tr><th>Tuning gap</th><td>{parameters.gap_length_m:.4f} m</td></tr>
<tr><th>Tuning capacitance</th><td>{parameters.tuning_capacitance_f * 1e12:.3f} pF</td></tr>
<tr><th>Capacitor ESR</th><td>{parameters.capacitor_esr_ohm:.3f} Ω</td></tr>
<tr><th>Bottom height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Top height</th><td>{parameters.top_height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Form a {parameters.diameter_m:.4f} m loop with
{parameters.sides} sides. Leave a {parameters.gap_length_m:.4f} m gap at the top
and install a {parameters.tuning_capacitance_f * 1e12:.3f} pF capacitor with
about {parameters.capacitor_esr_ohm:.3f} Ω ESR. Feed the midpoint of the bottom
side. Conductor loss comes from the selected material and wire radius; a
coupling loop and the capacitor voltage are not modeled.</p>"""
    elif isinstance(parameters, LoopParameters):
        horizontal = parameters.orientation is LoopOrientation.HORIZONTAL
        height_row = (
            f"<tr><th>Plane height</th><td>{parameters.height_m:.4f} m</td></tr>"
            if horizontal
            else f"<tr><th>Base height</th><td>{parameters.height_m:.4f} m</td></tr>"
        )
        feed_rows = f"""
<tr><th>Orientation</th><td>{parameters.orientation.value}</td></tr>
<tr><th>Side length</th><td>{parameters.side_length_m:.4f} m</td></tr>
{height_row}
<tr><th>Feed side</th><td>{_escape(antenna.feed.wire_id)}</td></tr>
<tr><th>Feed location</th><td>midpoint of the first side</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        plane = "horizontal" if horizontal else "vertical"
        construction_note = f"""<p>Cut one conductor to {parameters.circumference_m:.4f} m and
close it into {parameters.sides} equal sides of {parameters.side_length_m:.4f} m
in a {plane} plane. Feed the midpoint of the first side.</p>"""
    elif isinstance(parameters, TransmissionLineDoubletParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Dipole length</th><td>{parameters.dipole_total_length_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Matching line</th><td>{parameters.line_impedance_ohm:g} Ω, {parameters.line_length_m:.4f} m, vf={parameters.line_velocity_factor:.3f}</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut one dipole conductor to
{parameters.dipole_total_length_m:.4f} m and install it at
{parameters.height_m:.4f} m. Add a short source stub at the center and a
{parameters.line_length_m:.4f} m, {parameters.line_impedance_ohm:g} Ω matching line.
The line velocity factor is {parameters.line_velocity_factor:.3f}; the published
dimensions are starting points.</p>"""
    elif isinstance(parameters, ZeppParameters):
        impedance = parallel_wire_impedance_ohm(
            parameters.spacing_m,
            parameters.wire_radius_m,
        )
        feed_rows = f"""
<tr><th>Radiator length</th><td>{parameters.radiator_length_m:.4f} m</td></tr>
<tr><th>Matching section</th><td>{parameters.matching_section_length_m:.4f} m</td></tr>
<tr><th>Conductor spacing</th><td>{parameters.spacing_m:.4f} m</td></tr>
<tr><th>Estimated stub impedance</th><td>{impedance:.1f} Ω</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Radiator height</th><td>{parameters.base_height_m + parameters.matching_section_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = f"""<p>Cut the radiator to
{parameters.radiator_length_m:.4f} m and two matching-stub conductors to
{parameters.matching_section_length_m:.4f} m, spaced
{parameters.spacing_m:.4f} m. Join the stub conductors at the base and feed the
center of that connector; leave the antenna end of the second conductor open.
The estimated stub impedance is {impedance:.1f} Ω. The 1:1 common-mode choke is
a construction requirement and is not part of the NEC model.</p>"""
    elif isinstance(parameters, CustomAntennaParameters):
        radiator = next(
            (wire for wire in antenna.wires if wire.id == ZEPP_RADIATOR_ID),
            None,
        )
        matching_feed = next(
            (wire for wire in antenna.wires if wire.id == ZEPP_MATCHING_FEED_ID),
            None,
        )
        matching_open = next(
            (wire for wire in antenna.wires if wire.id == ZEPP_MATCHING_OPEN_ID),
            None,
        )
        if (
            parameters.generator_id == "zepp"
            and radiator is not None
            and matching_feed is not None
            and matching_open is not None
        ):
            spacing_m = math.hypot(
                matching_open.start.x_m - matching_feed.start.x_m,
                matching_open.start.y_m - matching_feed.start.y_m,
            )
            impedance_ohm = parallel_wire_impedance_ohm(spacing_m, matching_feed.radius_m)
            feed_rows = f"""
<tr><th>Radiator length</th><td>{radiator.length_m:.4f} m</td></tr>
<tr><th>Matching stub length</th><td>{matching_feed.length_m:.4f} m</td></tr>
<tr><th>Conductor spacing</th><td>{spacing_m:.4f} m</td></tr>
<tr><th>Estimated stub impedance</th><td>{impedance_ohm:.1f} Ω</td></tr>
<tr><th>Feed/base height</th><td>{feed_height_m:.4f} m</td></tr>
<tr><th>Radiator height</th><td>{radiator.start.z_m:.4f} m</td></tr>
"""
            construction_note = f"""<p>Cut the radiator to {radiator.length_m:.4f} m and
two matching-stub conductors to {matching_feed.length_m:.4f} m. Join one stub
conductor to the radiator, leave the second open at the antenna end, and join
both at the base connector. Feed the middle of the base connector through a
1:1 common-mode choke. The choke and coaxial feed are not modeled.</p>"""
        else:
            total_conductor_m = sum(wire.length_m for wire in antenna.wires)
            feed_rows = f"""
<tr><th>Wires</th><td>{len(antenna.wires)}</td></tr>
<tr><th>Total conductor</th><td>{total_conductor_m:.4f} m</td></tr>
<tr><th>Feed wire</th><td>{_escape(antenna.feed.wire_id)}</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
            construction_note = """<p>Custom geometry: use the wire table and feed
point above. Verify every connection and the feed gap before construction.</p>"""
    else:
        raise TypeError(f"unsupported antenna parameters: {type(parameters)!r}")

    bandwidth_row = ""
    if result is not None and len(result.frequencies) >= 2:
        swr_points = [
            (item.frequency_hz, item.swr)
            for item in result.frequencies
            if item.swr is not None and math.isfinite(item.swr)
        ]
        if len(swr_points) >= 2:
            bandwidth_hz = measure_bandwidth_hz(
                [point[0] for point in swr_points],
                [point[1] for point in swr_points],
                center_hz=parameters.frequency_hz,
                swr_limit=2.0,
            )
            if bandwidth_hz > 0.0:
                bandwidth_row = (
                    f"<tr><th>SWR ≤ 2 bandwidth</th><td>{bandwidth_hz / 1e3:.1f} kHz</td></tr>"
                )
    simulation_rows = ""
    if result is not None and frequency is not None:
        simulation_rows = f"""
<tr><th>Simulated frequency</th><td>{frequency.frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Impedance</th><td>{frequency.impedance_ohm.real:.3f} {frequency.impedance_ohm.imag:+.3f}j Ω</td></tr>
<tr><th>SWR ({result.spec.reference_impedance_ohm:g} Ω)</th><td>{_swr_text(frequency)}</td></tr>
<tr><th>Efficiency</th><td>{f"{efficiency:.2f} %" if efficiency is not None else "—"}</td></tr>
{"".join(f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>" for label, value in gain_metric_rows(result))}
{bandwidth_row}
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
