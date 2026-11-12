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
from ..domain.antennas.discone import DisconeParameters
from ..domain.antennas.endfed import EndFedParameters
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.hexbeam import HexbeamParameters
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
from ..domain.antennas.trap_yagi import TrapYagiParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zepp import (
    ZEPP_MATCHING_FEED_ID,
    ZEPP_MATCHING_OPEN_ID,
    ZEPP_RADIATOR_ID,
    ZeppParameters,
    parallel_wire_impedance_ohm,
)
from ..domain.design.matching_resolution import resolve_matching_network
from ..domain.optimization.length import measure_bandwidth_hz
from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import FrequencyResult, SimulationResult
from .design_summary import (
    design_evidence_rows,
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
    localize_html_labels,
    localize_rows,
)
from .result_summary import gain_metric_rows
from .wire_schedule import (
    bom_summary_rows,
    conductor_bom_rows,
    feed_schedule_row,
    wire_schedule_html_rows,
)

CSS = """
body { font-family: system-ui, sans-serif; margin: 28px; color: #222; background: #fff; }
h1 { font-size: 22px; margin-bottom: 2px; }
h2 { font-size: 15px; margin-top: 24px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
p { line-height: 1.45; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 13px; }
th, td { border: 1px solid #ddd; padding: 6px 8px; text-align: left; }
th { background: #f3f3f3; width: 34%; }
table.schedule th { width: auto; }
table.title-block th { width: auto; background: #f7f7f7; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
.muted { color: #666; font-size: 12px; }
.notes { background: #f7f7f7; border-left: 4px solid #888; padding: 10px 14px; }
.construction-figure, .installation-figure, .isometric-figure { display: block; width: 100%; max-width: 100%; height: auto; border: 1px solid #ddd; background: #fff; margin: 12px 0 2px; }
figure { margin: 0 0 12px; }
figcaption { color: #555; font-size: 12px; margin-top: 4px; }
.views { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 12px 0; }
.views figure { margin: 0; }
.views .view-main, .views .view-wide { grid-column: 1 / -1; }
.views .construction-figure, .views .installation-figure, .views .isometric-figure { margin: 0; }
@media (max-width: 640px) {
  .views { grid-template-columns: 1fr; }
  .views .view-main, .views .view-wide { grid-column: auto; }
}
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


def _note(labeler: Labeler, template: str, **values: object) -> str:
    """Render one localized construction paragraph."""

    return f"<p>{labeler(template, **values)}</p>"


def _resonance_text(result: SimulationResult | None, tr: Labeler) -> str:
    if result is None or len(result.frequencies) < 2:
        return "—"
    resonances = find_resonances(
        [frequency.frequency_hz for frequency in result.frequencies],
        [frequency.impedance_ohm for frequency in result.frequencies],
    )
    if not resonances:
        return tr("No resonance in the sweep.")
    return " · ".join(
        f"{point.frequency_hz / 1e6:.3f} MHz (R={point.impedance_ohm.real:.1f} Ω)"
        for point in resonances
    )


def render_construction_sheet(
    project: Project,
    design: DesignVariant,
    result: SimulationResult | None,
    *,
    figure_png_data_uri: str | None = None,
    auxiliary_png_data_uri: str | None = None,
    isometric_png_data_uri: str | None = None,
    auxiliary_kind: str | None = None,
    labeler: Labeler | None = None,
    language: str = "en",
) -> str:
    tr = labeler or identity_labeler
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
                    position=project.matching_network_position,
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
    antenna_label = getattr(
        parameters,
        "template_name",
        design.antenna_type.replace("_", " ").title(),
    )
    title_block = f"""
<table class="title-block">
<tr><th>Project</th><td>{_escape(project.name)}</td><th>Design</th><td>{_escape(design.name)}</td></tr>
<tr><th>Antenna</th><td>{_escape(antenna_label)}</td><th>Frequency</th><td>{parameters.frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Units</th><td>SI (m, MHz, Ω)</td><th>Updated</th><td>{project.updated_at:%Y-%m-%d}</td></tr>
</table>
"""
    schedule_rows = "".join(wire_schedule_html_rows(design))
    feed = feed_schedule_row(antenna)
    bom_conductor_rows = "".join(
        "<tr>"
        f"<td>{_escape(tr(row.material))}</td>"
        f'<td class="num">Ø{row.diameter_mm:.3f} mm</td>'
        f'<td class="num">{row.wire_count}</td>'
        f'<td class="num">{row.total_length_m:.4f} m</td>'
        "</tr>"
        for row in conductor_bom_rows(antenna)
    )
    bom_summary = "".join(
        f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>"
        for label, value in localize_rows(bom_summary_rows(antenna), tr)
    )
    bom_section = f"""
<h2>Bill of materials</h2>
<table class="schedule">
<thead>
<tr><th>Material</th><th>Diameter</th><th>Wires</th><th>Total length</th></tr>
</thead>
<tbody>
{bom_conductor_rows}
</tbody>
</table>
<table>
{bom_summary}
</table>
"""
    evidence_rows = "".join(
        f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>"
        for label, value in localize_rows(design_evidence_rows(design, labeler=tr), tr)
    )
    evidence_section = (
        f"""
<h2>Evidence and limitations</h2>
<table>
{evidence_rows}
</table>
"""
        if evidence_rows
        else ""
    )
    figures: list[tuple[str, str, str]] = []
    if figure_png_data_uri:
        figures.append(
            ("construction-figure view-main", tr("Construction view"), figure_png_data_uri)
        )
    if auxiliary_png_data_uri:
        auxiliary_caption = tr(
            "Top layout" if auxiliary_kind == "top" else "Installation view (front)"
        )
        figures.append(
            ("installation-figure view-secondary", auxiliary_caption, auxiliary_png_data_uri)
        )
    if isometric_png_data_uri:
        figures.append(
            ("isometric-figure view-secondary", tr("Isometric view"), isometric_png_data_uri)
        )
    if len(figures) == 2:
        class_name, caption, uri = figures[1]
        figures[1] = (class_name.replace("view-secondary", "view-wide"), caption, uri)
    figure_section = (
        '<div class="views">'
        + "".join(
            f'<figure><img class="{class_name}" alt="{_escape(caption)}" '
            f'src="{_escape(uri)}"><figcaption>{_escape(caption)}</figcaption></figure>'
            for class_name, caption, uri in figures
        )
        + "</div>"
        if figures
        else ""
    )
    schedule_section = f"""
<h2>Wire schedule</h2>
<table class="schedule">
<thead>
<tr><th>#</th><th>Wire</th><th>Start (m)</th><th>End (m)</th><th>Length (m)</th><th>Ø (mm)</th><th>Material</th></tr>
</thead>
<tbody>
{schedule_rows}
</tbody>
</table>
<table>
<tr><th>Feed wire</th><td><code>{_escape(feed.wire_id)}</code></td></tr>
<tr><th>Feed offset</th><td>{_escape(tr("{offset:.4f} m from the wire start", offset=feed.offset_m))}</td></tr>
<tr><th>Feed coordinates</th><td>{feed.point.x_m:.4f}, {feed.point.y_m:.4f}, {feed.point.z_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed.height_m:.4f} m</td></tr>
</table>
"""
    if isinstance(parameters, DipoleParameters):
        if parameters.sag_m > 0.0:
            feed_rows = f"""
<tr><th>Span</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>Conductor length</th><td>{parameters.conductor_length_m:.4f} m</td></tr>
<tr><th>Wire height at supports</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Center sag</th><td>{parameters.sag_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
            construction_note = _note(
                tr,
                "Cut one conductor to {conductor_length} m. Support the ends at "
                "{height} m and let the center sag by {sag} m; the feed is at the "
                "lowest point, {feed_height} m above ground. The sagged shape is "
                "approximated by straight NEC segments between the sampled points.",
                conductor_length=f"{parameters.conductor_length_m:.4f}",
                height=f"{parameters.height_m:.4f}",
                sag=f"{parameters.sag_m:.4f}",
                feed_height=f"{feed_height_m:.4f}",
            )
        else:
            other_leg_m = max(feed_wire.length_m - feed_offset_m, 0.0)
            feed_rows = f"""
<tr><th>First leg (from wire start)</th><td>{feed_offset_m:.4f} m</td></tr>
<tr><th>Second leg (from feed)</th><td>{other_leg_m:.4f} m</td></tr>
<tr><th>Wire height at start</th><td>{feed_wire.start.z_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
            construction_note = _note(
                tr,
                "Cut the two legs to the dimensions above, leaving a small feed "
                "gap at the center. The feed point is {feed_offset} m from the "
                "start of the wire and {other_leg} m from the end.",
                feed_offset=f"{feed_offset_m:.4f}",
                other_leg=f"{other_leg_m:.4f}",
            )
    elif isinstance(parameters, TrapDipoleParameters):
        left_position, right_position = parameters.trap_positions_m
        feed_rows = f"""
<tr><th>Total wire length</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>Center section</th><td>{parameters.inner_length_m:.4f} m</td></tr>
<tr><th>Outer sections</th><td>{_escape(tr("{length:.4f} m each", length=parameters.outer_length_m))}</td></tr>
<tr><th>Trap positions</th><td>{_escape(tr("{left:.4f} m, {right:.4f} m from wire start", left=left_position, right=right_position))}</td></tr>
<tr><th>Trap frequency</th><td>{parameters.trap_frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Trap inductance</th><td>{parameters.trap_inductance_h * 1e6:.4f} µH</td></tr>
<tr><th>Trap capacitance</th><td>{parameters.trap_capacitance_f * 1e12:.4f} pF</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut one conductor to {total} m. Mark the trap positions at {left} m "
            "and {right} m from the start, leaving a {inner} m center section. "
            "Install parallel LC traps tuned to {frequency} MHz ({inductance} µH, "
            "{capacitance} pF). Feed the center of the element.",
            total=f"{parameters.total_length_m:.4f}",
            left=f"{left_position:.4f}",
            right=f"{right_position:.4f}",
            inner=f"{parameters.inner_length_m:.4f}",
            frequency=f"{parameters.trap_frequency_hz / 1e6:.6f}",
            inductance=f"{parameters.trap_inductance_h * 1e6:.4f}",
            capacitance=f"{parameters.trap_capacitance_f * 1e12:.4f}",
        )
    elif isinstance(parameters, T2FDParameters):
        feed_rows = f"""
<tr><th>Element length</th><td>{_escape(tr("{length:.4f} m each", length=parameters.length_m))}</td></tr>
<tr><th>Conductor spacing</th><td>{parameters.spacing_m:.4f} m</td></tr>
<tr><th>Design band</th><td>{parameters.frequency_hz / 1e6:.6f} MHz to {parameters.highest_frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Termination resistor</th><td>{parameters.termination_resistance_ohm:g} Ω non-inductive</td></tr>
<tr><th>Feed transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut two equal conductors of {length} m and two end connectors of "
            "{spacing} m. Join them at both ends to form a folded loop. Feed the "
            "midpoint of one conductor through a {ratio}:1 transformer. Install a "
            "{resistance} Ω non-inductive resistor at the midpoint of the other "
            "conductor, opposite the feed point. The total conductor length is "
            "{total} m.",
            length=f"{parameters.length_m:.4f}",
            spacing=f"{parameters.spacing_m:.4f}",
            ratio=f"{parameters.transformer_ratio:g}",
            resistance=f"{parameters.termination_resistance_ohm:g}",
            total=f"{parameters.total_conductor_length_m:.4f}",
        )
    elif isinstance(parameters, FoldedDipoleParameters):
        feed_rows = f"""
<tr><th>Driven element length</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>End connector length</th><td>{parameters.spacing_m:.4f} m</td></tr>
<tr><th>Feed location</th><td>{_escape(tr("center of driven element"))}</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut two equal driven elements of {total} m and two end connectors of "
            "{spacing} m. Join them at both ends and feed the center of one "
            "element. The total conductor length is {conductor} m.",
            total=f"{parameters.total_length_m:.4f}",
            spacing=f"{parameters.spacing_m:.4f}",
            conductor=f"{parameters.total_conductor_length_m:.4f}",
        )
    elif isinstance(parameters, ScvParameters):
        if parameters.kind is ScvKind.HALF_SQUARE:
            feed_point = tr("the top corner of one outer vertical")
            wire_note = tr(
                "Cut two vertical wires of {height:.4f} m and one top wire of {horizontal:.4f} m.",
                height=parameters.vertical_height_m,
                horizontal=parameters.horizontal_length_m,
            )
        else:
            feed_point = tr("the top junction of the center vertical and the top wires")
            wire_note = tr(
                "Cut three vertical wires of {height:.4f} m and two top wires of "
                "{segment:.4f} m each.",
                height=parameters.vertical_height_m,
                segment=parameters.horizontal_segment_m,
            )
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Horizontal length</th><td>{parameters.horizontal_length_m:.4f} m</td></tr>
<tr><th>Horizontal segment</th><td>{_escape(tr("{length:.4f} m each", length=parameters.horizontal_segment_m))}</td></tr>
<tr><th>Vertical height</th><td>{parameters.vertical_height_m:.4f} m</td></tr>
<tr><th>Vertical elements</th><td>{parameters.vertical_count}</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Top height</th><td>{parameters.top_height_m:.4f} m</td></tr>
<tr><th>Feed offset below top</th><td>{parameters.feed_offset_m:.4f} m</td></tr>
<tr><th>Total conductor</th><td>{parameters.total_conductor_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build a {kind} with {count} vertical elements joined at the top. "
            "{wire_note} Keep the bottom ends insulated from ground and feed "
            "{feed_point}. The feed is {feed_offset} m below the top junction at "
            "{feed_height} m above ground.",
            kind=tr(parameters.template_name).lower(),
            count=parameters.vertical_count,
            wire_note=wire_note,
            feed_point=feed_point,
            feed_offset=f"{parameters.feed_offset_m:.4f}",
            feed_height=f"{feed_height_m:.4f}",
        )
    elif isinstance(parameters, LoadedDipoleParameters):
        coil_note = (
            tr(
                "Fit two {inductance:.3f} µH loading coils at {offset:.4f} m either "
                "side of the feed; each coil has {resistance:.3f} Ω series "
                "resistance.",
                inductance=parameters.loading_coil_inductance_h * 1e6,
                offset=parameters.link_offset_m,
                resistance=parameters.loading_coil_resistance_ohm,
            )
            if parameters.coil_active
            else (
                tr("Leave the links open and use only the center section.")
                if parameters.link_open
                else tr("No loading coils are fitted.")
            )
        )
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Active length</th><td>{parameters.active_length_m:.4f} m</td></tr>
<tr><th>Full length</th><td>{parameters.total_length_m:.4f} m</td></tr>
<tr><th>Link offset</th><td>{parameters.link_offset_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut the full {total} m wire and mark the link positions at {offset} m "
            "either side of the center. Feed the center. {coil_note} The coil "
            "model is an ideal series R-L load; tune it for the installed height "
            "and ground.",
            total=f"{parameters.total_length_m:.4f}",
            offset=f"{parameters.link_offset_m:.4f}",
            coil_note=coil_note,
        )
    elif isinstance(parameters, HexbeamParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Driver half-length</th><td>{parameters.driver_half_length_m:.4f} m</td></tr>
<tr><th>Reflector half-length</th><td>{parameters.reflector_half_length_m:.4f} m</td></tr>
<tr><th>Turning radius</th><td>{parameters.turning_radius_m:.4f} m</td></tr>
<tr><th>Tip gap</th><td>{parameters.tip_gap_m:.4f} m</td></tr>
<tr><th>Overall span</th><td>{parameters.overall_span_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{parameters.height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build a W-shaped driver with {driver} m half-lengths and a U-shaped "
            "reflector with {reflector} m half-lengths on a six-spreader frame "
            "with a {turning} m turning radius. Set the tip gap to {tip_gap} m and "
            "feed the center of the W. The model reconstructs the bent wire path; "
            "the frame, spreader sag, feed balun, and multi-band nesting are not "
            "modeled.",
            driver=f"{parameters.driver_half_length_m:.4f}",
            reflector=f"{parameters.reflector_half_length_m:.4f}",
            turning=f"{parameters.turning_radius_m:.4f}",
            tip_gap=f"{parameters.tip_gap_m:.4f}",
        )
    elif isinstance(parameters, TrapYagiParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Elements</th><td>{parameters.element_count}</td></tr>
<tr><th>Driven element</th><td>{parameters.driven_length_m:.4f} m</td></tr>
<tr><th>Reflector element</th><td>{parameters.reflector_length_m:.4f} m</td></tr>
<tr><th>Boom length</th><td>{parameters.boom_length_m:.4f} m</td></tr>
<tr><th>Trap inset</th><td>{parameters.trap_inset_m:.4f} m</td></tr>
<tr><th>Trap frequency</th><td>{parameters.trap_frequency_hz / 1e6:.3f} MHz</td></tr>
<tr><th>Trap inductance</th><td>{parameters.trap_inductance_h * 1e6:.3f} µH</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build {count} Yagi elements with the driven element at {driven} m and "
            "the reflector at {reflector} m. Fit a parallel LC trap on each side "
            "of every element at {inset} m from its center, using {inductance} µH "
            "and the capacitance for {frequency} MHz. The trap model is ideal; boom "
            "mounting, trap loss, feed line, and matching network are not modeled.",
            count=parameters.element_count,
            driven=f"{parameters.driven_length_m:.4f}",
            reflector=f"{parameters.reflector_length_m:.4f}",
            inset=f"{parameters.trap_inset_m:.4f}",
            inductance=f"{parameters.trap_inductance_h * 1e6:.3f}",
            frequency=f"{parameters.trap_frequency_hz / 1e6:.3f}",
        )
    elif isinstance(parameters, DisconeParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Radial wires</th><td>{parameters.wire_count}</td></tr>
<tr><th>Cone height</th><td>{parameters.cone_height_m:.4f} m</td></tr>
<tr><th>Cone base radius</th><td>{parameters.cone_radius_m:.4f} m</td></tr>
<tr><th>Disc radius</th><td>{parameters.disc_radius_m:.4f} m</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{parameters.feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build {count} cone wires from the apex at {apex} m down to a base ring "
            "of {radius} m radius at {base} m. Add {count} disc wires of {disc} m "
            "above the apex with a {gap} m feed gap. Feed across that gap. The cone "
            "and disc are wire approximations; the coax, mast, and solid surfaces "
            "are not modeled.",
            count=parameters.wire_count,
            apex=f"{parameters.apex_height_m:.4f}",
            radius=f"{parameters.cone_radius_m:.4f}",
            base=f"{parameters.base_height_m:.4f}",
            disc=f"{parameters.disc_radius_m:.4f}",
            gap=f"{parameters.disc_gap_m:.4f}",
        )
    elif isinstance(parameters, QuadBeamParameters):
        director_note = (
            tr(
                " The director loop is {side} m per side at {spacing} m in front "
                "of the driven loop.",
                side=f"{parameters.director_side_m:.4f}",
                spacing=f"{parameters.director_spacing_m:.4f}",
            )
            if parameters.element_count == 3
            else ""
        )
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Loops</th><td>{parameters.element_count}</td></tr>
<tr><th>Driven loop side</th><td>{parameters.loop_side_m:.4f} m</td></tr>
<tr><th>Reflector side</th><td>{parameters.reflector_side_m:.4f} m</td></tr>
<tr><th>Reflector spacing</th><td>{parameters.reflector_spacing_m:.4f} m</td></tr>
<tr><th>Boom length</th><td>{parameters.boom_length_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{parameters.feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build {count} square loops with the driven loop at {side} m per side "
            "and the reflector at {reflector} m per side. Set the reflector "
            "{spacing} m behind the driven loop.{director_note} Feed the midpoint "
            "of the driven loop's left vertical side and keep the loops square. "
            "The boom, spreaders, mast, and matching network are not modeled; tune "
            "the match for the installed antenna.",
            count=parameters.element_count,
            side=f"{parameters.loop_side_m:.4f}",
            reflector=f"{parameters.reflector_side_m:.4f}",
            spacing=f"{parameters.reflector_spacing_m:.4f}",
            director_note=director_note,
        )
    elif isinstance(parameters, PhasedVerticalParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
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
        construction_note = _note(
            tr,
            "Build {count} vertical radiators of {height} m, spaced {spacing} m "
            "along one line, with their bases at {base} m above ground. Fit "
            "{radials} radials of {radial_length} m to each base. Drive the first "
            "vertical as the primary feed and the remaining verticals with the "
            "listed phase and amplitude steps. The combining network is ideal and "
            "is not included; use an explicit feed network and verify the match.",
            count=parameters.element_count,
            height=f"{parameters.height_m:.4f}",
            spacing=f"{parameters.spacing_m:.4f}",
            base=f"{parameters.base_height_m:.4f}",
            radials=parameters.radial_count,
            radial_length=f"{parameters.radial_length_m:.4f}",
        )
    elif isinstance(parameters, BeverageParameters):
        termination_note = (
            tr(
                "Fit a {resistance:.1f} Ω resistor from the far end to a ground rod.",
                resistance=parameters.termination_resistance_ohm,
            )
            if parameters.termination_enabled
            else tr("Leave the far end open for a bidirectional receiving pattern.")
        )
        termination_row = (
            tr(
                "{resistance:.1f} Ω to ground",
                resistance=parameters.termination_resistance_ohm,
            )
            if parameters.termination_enabled
            else tr("disabled")
        )
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr("Beverage"))}</td></tr>
<tr><th>Length</th><td>{parameters.length_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Termination</th><td>{termination_row}</td></tr>
<tr><th>Total conductor</th><td>{parameters.total_conductor_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Run one horizontal wire of {length} m at {height} m above ground. "
            "Feed the near end directly and keep the wire straight. "
            "{termination_note} The one-wavelength starting length and termination "
            "value are heuristics; the pattern and receiving performance are not "
            "independently validated.",
            length=f"{parameters.length_m:.4f}",
            height=f"{parameters.height_m:.4f}",
            termination_note=termination_note,
        )
    elif isinstance(parameters, BiquadParameters):
        reflector_note = (
            tr(
                "A wire reflector sits {spacing:.4f} m behind the driven plane.",
                spacing=parameters.reflector_spacing_m,
            )
            if parameters.reflector_enabled
            else tr("This variant has no reflector.")
        )
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Loops</th><td>{parameters.loop_count}</td></tr>
<tr><th>Loop side</th><td>{parameters.loop_side_m:.4f} m</td></tr>
<tr><th>Stack height</th><td>{parameters.total_height_m:.4f} m</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Feed height</th><td>{parameters.feed_height_m:.4f} m</td></tr>
<tr><th>Reflector</th><td>{_escape(tr("{spacing:.4f} m behind", spacing=parameters.reflector_spacing_m))}</td></tr>
<tr><th>Total conductor</th><td>{parameters.total_conductor_length_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build {count} square loops with {side} m sides. Join them at the "
            "shared horizontal rails, starting at {base} m above ground, and feed "
            "the midpoint of the central rail at {feed_height} m. {reflector_note} "
            "The quarter-wave side and eighth-wave reflector spacing are starting "
            "dimensions; tune them for the installation.",
            count=parameters.loop_count,
            side=f"{parameters.loop_side_m:.4f}",
            base=f"{parameters.base_height_m:.4f}",
            feed_height=f"{feed_height_m:.4f}",
            reflector_note=reflector_note,
        )
    elif isinstance(parameters, RingoParameters):
        feed_rows = f"""
<tr><th>Radiator height</th><td>{parameters.radiator_height_m:.4f} m</td></tr>
<tr><th>Ring diameter</th><td>{parameters.ring_diameter_m:.4f} m</td></tr>
<tr><th>Ring height</th><td>{parameters.ring_height_m:.4f} m</td></tr>
<tr><th>Ring sides</th><td>{parameters.ring_sides}</td></tr>
"""
        construction_note = _note(
            tr,
            "Build a {height} m vertical radiator with a {diameter} m matching "
            "ring at {ring_height} m above ground.",
            height=f"{parameters.radiator_height_m:.4f}",
            diameter=f"{parameters.ring_diameter_m:.4f}",
            ring_height=f"{parameters.ring_height_m:.4f}",
        )
    elif isinstance(parameters, JPoleParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Radiator height</th><td>{parameters.radiator_height_m:.4f} m</td></tr>
<tr><th>Stub length</th><td>{parameters.stub_length_m:.4f} m</td></tr>
<tr><th>Stub spacing</th><td>{parameters.spacing_m:.4f} m</td></tr>
<tr><th>Feed offset</th><td>{parameters.feed_offset_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build a {kind} with a {radiator} m radiator and a {stub} m stub spaced {spacing} m.",
            kind=tr(parameters.template_name),
            radiator=f"{parameters.radiator_height_m:.4f}",
            stub=f"{parameters.stub_length_m:.4f}",
            spacing=f"{parameters.spacing_m:.4f}",
        )
    elif isinstance(parameters, EndFedParameters):
        override_active = resolve_matching_network(
            parameters, project.matching_network
        ).override_active
        matching_status = (
            tr("retained; project network overrides") if override_active else tr("active")
        )
        counterpoise = (
            f"{parameters.counterpoise_length_m:.4f} m at {parameters.counterpoise_height_m:.4f} m"
            if parameters.counterpoise_length_m > 0.0
            else tr("none")
        )
        feed_section_row = (
            f"<tr><th>Feed section</th><td>{parameters.feed_section_length_m:.4f} m</td></tr>\n"
            if parameters.feed_section_active
            else ""
        )
        installation_return_row = (
            f"<tr><th>Installation return (proxy)</th><td>{parameters.installation_return_length_m:.4f} m (coax/mast proxy)</td></tr>\n"
            if parameters.installation_return_active
            else ""
        )
        matching_rows = (
            f"<tr><th>Matching capacitor</th><td>{parameters.matching_capacitance_f * 1e12:.1f} pF (primary shunt, {_escape(matching_status)})</td></tr>\n"
            f"<tr><th>Transformer leakage</th><td>{parameters.transformer_leakage_inductance_h * 1e6:.4f} µH ({_escape(matching_status)})</td></tr>\n"
            if parameters.matching_network_active
            else ""
        )
        height_rows = (
            f"<tr><th>Vertical section</th><td>{parameters.bend_vertical_length_m:.4f} m</td></tr>\n"
            f"<tr><th>Horizontal run</th><td>{parameters.bend_horizontal_length_m:.4f} m</td></tr>\n"
            f"<tr><th>Top height</th><td>{parameters.bend_top_height_m:.4f} m</td></tr>\n"
            if parameters.bend_active
            else f"<tr><th>End height</th><td>{parameters.end_height_m:.4f} m</td></tr>\n"
        )
        feed_rows = f"""
<tr><th>Wire length</th><td>{parameters.length_m:.4f} m</td></tr>
{feed_section_row}<tr><th>Feed height</th><td>{parameters.feed_height_m:.4f} m</td></tr>
{height_rows}<tr><th>Transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
{matching_rows}<tr><th>Counterpoise</th><td>{counterpoise}</td></tr>
{installation_return_row}"""
        if parameters.bend_active and parameters.coil_active:
            construction_note = _note(
                tr,
                "Cut one wire to {length} m. Run {vertical} m vertically from the "
                "feed, bend 90°, then run {horizontal} m horizontally at {top} m. Fit "
                "the {inductance} µH loading coil at {offset} m from the feed; the "
                "remaining {top_section} m is the top section. Use a {ratio}:1 "
                "transformer; the counterpoise is {counterpoise}.",
                length=f"{parameters.length_m:.4f}",
                vertical=f"{parameters.bend_vertical_length_m:.4f}",
                horizontal=f"{parameters.bend_horizontal_length_m:.4f}",
                top=f"{parameters.bend_top_height_m:.4f}",
                inductance=f"{parameters.loading_coil_inductance_h * 1e6:.4f}",
                offset=f"{parameters.loading_coil_offset_m:.4f}",
                top_section=f"{parameters.loading_coil_top_length_m:.4f}",
                ratio=f"{parameters.transformer_ratio:g}",
                counterpoise=counterpoise,
            )
        elif parameters.bend_active:
            construction_note = _note(
                tr,
                "Cut one wire to {length} m. Run {vertical} m vertically from the "
                "feed, bend 90°, then run {horizontal} m horizontally at {top} m. "
                "Use a {ratio}:1 transformer; the counterpoise is {counterpoise}.",
                length=f"{parameters.length_m:.4f}",
                vertical=f"{parameters.bend_vertical_length_m:.4f}",
                horizontal=f"{parameters.bend_horizontal_length_m:.4f}",
                top=f"{parameters.bend_top_height_m:.4f}",
                ratio=f"{parameters.transformer_ratio:g}",
                counterpoise=counterpoise,
            )
        elif parameters.coil_active:
            construction_note = _note(
                tr,
                "Cut one wire to {length} m. Fit the {inductance} µH loading coil "
                "at {offset} m from the feed; the remaining {top} m is the top "
                "section. Use a {ratio}:1 transformer and the matching unit "
                "described below; the counterpoise is {counterpoise}.",
                length=f"{parameters.length_m:.4f}",
                inductance=f"{parameters.loading_coil_inductance_h * 1e6:.4f}",
                offset=f"{parameters.loading_coil_offset_m:.4f}",
                top=f"{parameters.loading_coil_top_length_m:.4f}",
                ratio=f"{parameters.transformer_ratio:g}",
                counterpoise=counterpoise,
            )
        else:
            construction_note = _note(
                tr,
                "Cut one wire to {length} m and feed it at one end. The feed is at "
                "{feed_height} m and the far end at {end_height} m. Use a {ratio}:1 "
                "transformer; the counterpoise is {counterpoise}.",
                length=f"{parameters.length_m:.4f}",
                feed_height=f"{parameters.feed_height_m:.4f}",
                end_height=f"{parameters.end_height_m:.4f}",
                ratio=f"{parameters.transformer_ratio:g}",
                counterpoise=counterpoise,
            )
        if parameters.bend_active:
            construction_note += (
                "<p>"
                + _escape(
                    tr(
                        "The bend is a 90° corner at {vertical} m from the feed. Use one "
                        "continuous conductor and keep the corner mechanically supported; "
                        "the model uses a sharp corner.",
                        vertical=f"{parameters.bend_vertical_length_m:.4f}",
                    )
                )
                + "</p>"
            )
        if parameters.feed_section_active:
            construction_note += (
                "<p>"
                + _escape(
                    tr(
                        "The first {length} m is a fixed feed section of the same wire; "
                        "do not cut a separate conductor.",
                        length=f"{parameters.feed_section_length_m:.4f}",
                    )
                )
                + "</p>"
            )
        if parameters.installation_return_active:
            construction_note += (
                "<p>"
                + _escape(
                    tr(
                        "The {length} m installation return is a model proxy for the "
                        "coax/mast/earth path, not a physical radial.",
                        length=f"{parameters.installation_return_length_m:.4f}",
                    )
                )
                + "</p>"
            )
        if parameters.matching_network_active:
            if override_active:
                construction_note += (
                    "<p>"
                    + _escape(
                        tr(
                            "The project matching network replaces the internal EFHW "
                            "matching unit. The {capacitance} pF capacitor and {leakage} "
                            "µH leakage are retained in the design but are not installed "
                            "or applied; do not cascade both networks. The {ratio}:1 "
                            "transformer ratio still applies.",
                            capacitance=f"{parameters.matching_capacitance_f * 1e12:.1f}",
                            leakage=f"{parameters.transformer_leakage_inductance_h * 1e6:.4f}",
                            ratio=f"{parameters.transformer_ratio:g}",
                        )
                    )
                    + "</p>"
                )
            else:
                construction_note += (
                    "<p>"
                    + _escape(
                        tr(
                            "The {capacitance} pF capacitor is an ideal shunt across the "
                            "transformer primary. The {leakage} µH leakage is a starting "
                            "estimate; measure your transformer. Core loss, capacitor ESR, "
                            "and winding capacitance are not modeled.",
                            capacitance=f"{parameters.matching_capacitance_f * 1e12:.1f}",
                            leakage=f"{parameters.transformer_leakage_inductance_h * 1e6:.4f}",
                        )
                    )
                    + "</p>"
                )
    elif isinstance(parameters, FanDipoleParameters):
        lengths = ", ".join(f"{element.length_m:.4f} m" for element in parameters.elements)
        angles = ", ".join(f"{element.included_angle_deg:.1f}°" for element in parameters.elements)
        end_heights = ", ".join(
            f"{parameters.element_end_height_m(element):.4f} m" for element in parameters.elements
        )
        feed_rows = f"""
<tr><th>Pairs</th><td>{len(parameters.elements)}</td></tr>
<tr><th>Element lengths</th><td>{_escape(lengths)}</td></tr>
<tr><th>Included angles</th><td>{_escape(angles)}</td></tr>
<tr><th>End heights</th><td>{_escape(end_heights)}</td></tr>
<tr><th>Apex height</th><td>{parameters.apex_height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut {count} dipole pairs with lengths {lengths} at included angles "
            "{angles}. Join all pairs at the common apex and feed there. The ends "
            "sit at {end_heights} above ground.",
            count=len(parameters.elements),
            lengths=_escape(lengths),
            angles=_escape(angles),
            end_heights=_escape(end_heights),
        )
    elif isinstance(parameters, MoxonParameters):
        feed_rows = f"""
<tr><th>Element width</th><td>{parameters.width_m:.4f} m</td></tr>
<tr><th>Element spacing</th><td>{parameters.depth_m:.4f} m</td></tr>
<tr><th>Reflector tip</th><td>{parameters.reflector_tip_m:.4f} m</td></tr>
<tr><th>Driven tip</th><td>{parameters.driven_tip_m:.4f} m</td></tr>
<tr><th>Tip gap</th><td>{parameters.gap_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build a Moxon rectangle with {width} m elements, {depth} m spacing, "
            "and bent tips leaving a {gap} m gap.",
            width=f"{parameters.width_m:.4f}",
            depth=f"{parameters.depth_m:.4f}",
            gap=f"{parameters.gap_m:.4f}",
        )
    elif isinstance(parameters, YagiParameters):
        positions = [element.position_m for element in parameters.elements]
        folded_row = ""
        folded_note = ""
        if parameters.driven_folded:
            folded_row = f"""
<tr><th>Folded driven element</th><td>{_escape(tr("yes"))}</td></tr>
<tr><th>Fold spacing</th><td>{parameters.driven_fold_spacing_m:.4f} m</td></tr>
"""
            folded_note = tr(
                " The driven element is folded with {spacing:.4f} m spacing and "
                "two end connectors. Feed one conductor at its center; the second "
                "conductor remains passive.",
                spacing=parameters.driven_fold_spacing_m,
            )
        match_row = ""
        match_note = ""
        if parameters.match_type.value == "beta_hairpin":
            match_row = f"""
<tr><th>Feed match</th><td>{_escape(tr("beta / hairpin"))}</td></tr>
<tr><th>Hairpin length</th><td>{parameters.match_length_m:.4f} m</td></tr>
<tr><th>Hairpin spacing</th><td>{parameters.match_spacing_m:.4f} m</td></tr>
"""
            match_note = tr(
                " A beta/hairpin stub is connected across the {spacing:.4f} m "
                "driven-element gap and shorted {length:.4f} m along the boom.",
                spacing=parameters.match_spacing_m,
                length=parameters.match_length_m,
            )
        feed_rows = f"""
<tr><th>Elements</th><td>{len(parameters.elements)}</td></tr>
<tr><th>Boom length</th><td>{max(positions) - min(positions):.4f} m</td></tr>
<tr><th>Driven element</th><td>{parameters.driven_index + 1}</td></tr>
{folded_row}
{match_row}
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Build {count} parallel elements on a {boom} m boom. Feed the center "
            "of element {driven}.{folded_note}{match_note}",
            count=len(parameters.elements),
            boom=f"{max(positions) - min(positions):.4f}",
            driven=parameters.driven_index + 1,
            folded_note=folded_note,
            match_note=match_note,
        )
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
        construction_note = _note(
            tr,
            "Cut one conductor to {total} m. Install {vertical} m vertically "
            "with the base {base} m above ground, then run the remaining "
            "{horizontal} m horizontally at {top} m. Feed the base of the "
            "vertical section.",
            total=f"{parameters.total_length_m:.4f}",
            vertical=f"{parameters.vertical_height_m:.4f}",
            base=f"{parameters.base_height_m:.4f}",
            horizontal=f"{parameters.horizontal_length_m:.4f}",
            top=f"{parameters.top_height_m:.4f}",
        )
    elif isinstance(parameters, InvertedVParameters):
        feed_rows = f"""
<tr><th>Leg length</th><td>{parameters.leg_length_m:.4f} m</td></tr>
<tr><th>Apex height</th><td>{parameters.apex_height_m:.4f} m</td></tr>
<tr><th>End height</th><td>{parameters.end_height_m:.4f} m</td></tr>
<tr><th>Included angle</th><td>{parameters.included_angle_deg:.1f}°</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut two legs of {leg} m and join them at the apex with an included "
            "angle of {angle}°. The apex is {apex} m above ground.",
            leg=f"{parameters.leg_length_m:.4f}",
            angle=f"{parameters.included_angle_deg:.1f}",
            apex=f"{parameters.apex_height_m:.4f}",
        )
    elif isinstance(parameters, VerticalParameters):
        top_hat_rows = ""
        top_hat_note = ""
        if parameters.top_hat_enabled:
            top_hat_rows = f"""
<tr><th>Top hat wires</th><td>{parameters.top_hat_wire_count}</td></tr>
<tr><th>Top hat radius</th><td>{parameters.top_hat_radius_m:.4f} m</td></tr>
"""
            top_hat_note = tr(
                " Add {count} horizontal top-hat wires of {radius:.4f} m at the radiator top.",
                count=parameters.top_hat_wire_count,
                radius=parameters.top_hat_radius_m,
            )
        feed_rows = f"""
<tr><th>Radiator height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Base height</th><td>{parameters.base_height_m:.4f} m</td></tr>
<tr><th>Radials</th><td>{parameters.radial_count}</td></tr>
<tr><th>Radial length</th><td>{parameters.radial_length_m:.4f} m</td></tr>
{top_hat_rows}
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Install a {height} m vertical radiator with its base {base} m above "
            "ground. Add {radials} radials of {radial_length} m in the base "
            "plane.{top_hat_note}",
            height=f"{parameters.height_m:.4f}",
            base=f"{parameters.base_height_m:.4f}",
            radials=parameters.radial_count,
            radial_length=f"{parameters.radial_length_m:.4f}",
            top_hat_note=top_hat_note,
        )
    elif isinstance(parameters, OCFDParameters):
        other_leg_m = max(feed_wire.length_m - feed_offset_m, 0.0)
        feed_rows = f"""
<tr><th>Feed offset from start</th><td>{feed_offset_m:.4f} m</td></tr>
<tr><th>Remaining leg</th><td>{other_leg_m:.4f} m</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut one conductor to {total} m. Feed it {offset} m from the start "
            "({percent}% of its length).",
            total=f"{parameters.total_length_m:.4f}",
            offset=f"{feed_offset_m:.4f}",
            percent=f"{parameters.feed_ratio * 100:.1f}",
        )
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
        construction_note = _note(
            tr,
            "Form a {diameter} m loop with {sides} sides. Leave a {gap} m gap at "
            "the top and install a {capacitance} pF capacitor with about {esr} Ω "
            "ESR. Feed the midpoint of the bottom side. Conductor loss comes from "
            "the selected material and wire radius; a coupling loop and the "
            "capacitor voltage are not modeled.",
            diameter=f"{parameters.diameter_m:.4f}",
            sides=parameters.sides,
            gap=f"{parameters.gap_length_m:.4f}",
            capacitance=f"{parameters.tuning_capacitance_f * 1e12:.3f}",
            esr=f"{parameters.capacitor_esr_ohm:.3f}",
        )
    elif isinstance(parameters, LoopParameters):
        horizontal = parameters.orientation is LoopOrientation.HORIZONTAL
        height_row = (
            f"<tr><th>Plane height</th><td>{parameters.height_m:.4f} m</td></tr>"
            if horizontal
            else f"<tr><th>Base height</th><td>{parameters.height_m:.4f} m</td></tr>"
        )
        feed_rows = f"""
<tr><th>Orientation</th><td>{_escape(tr(parameters.orientation.value))}</td></tr>
<tr><th>Side length</th><td>{parameters.side_length_m:.4f} m</td></tr>
{height_row}
<tr><th>Feed side</th><td>{_escape(antenna.feed.wire_id)}</td></tr>
<tr><th>Feed location</th><td>{_escape(tr("midpoint of the first side"))}</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        plane = tr("horizontal" if horizontal else "vertical")
        construction_note = _note(
            tr,
            "Cut one conductor to {circumference} m and close it into {sides} "
            "equal sides of {side} m in a {plane} plane. Feed the midpoint of the "
            "first side.",
            circumference=f"{parameters.circumference_m:.4f}",
            sides=parameters.sides,
            side=f"{parameters.side_length_m:.4f}",
            plane=plane,
        )
    elif isinstance(parameters, TransmissionLineDoubletParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Dipole length</th><td>{parameters.dipole_total_length_m:.4f} m</td></tr>
<tr><th>Height</th><td>{parameters.height_m:.4f} m</td></tr>
<tr><th>Matching line</th><td>{parameters.line_impedance_ohm:g} Ω, {parameters.line_length_m:.4f} m, vf={parameters.line_velocity_factor:.3f}</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut one dipole conductor to {length} m and install it at {height} m. "
            "Add a short source stub at the center and a {line_length} m, "
            "{impedance} Ω matching line. The line velocity factor is {velocity}; "
            "the published dimensions are starting points.",
            length=f"{parameters.dipole_total_length_m:.4f}",
            height=f"{parameters.height_m:.4f}",
            line_length=f"{parameters.line_length_m:.4f}",
            impedance=f"{parameters.line_impedance_ohm:g}",
            velocity=f"{parameters.line_velocity_factor:.3f}",
        )
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
        construction_note = _note(
            tr,
            "Cut the radiator to {radiator} m and two matching-stub conductors "
            "to {stub} m, spaced {spacing} m. Join the stub conductors at the "
            "base and feed the center of that connector; leave the antenna end "
            "of the second conductor open. The estimated stub impedance is "
            "{impedance} Ω. The 1:1 common-mode choke is a construction "
            "requirement and is not part of the NEC model.",
            radiator=f"{parameters.radiator_length_m:.4f}",
            stub=f"{parameters.matching_section_length_m:.4f}",
            spacing=f"{parameters.spacing_m:.4f}",
            impedance=f"{impedance:.1f}",
        )
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
            construction_note = _note(
                tr,
                "Cut the radiator to {radiator} m and two matching-stub "
                "conductors to {stub} m. Join one stub conductor to the radiator, "
                "leave the second open at the antenna end, and join both at the "
                "base connector. Feed the middle of the base connector through a "
                "1:1 common-mode choke. The choke and coaxial feed are not modeled.",
                radiator=f"{radiator.length_m:.4f}",
                stub=f"{matching_feed.length_m:.4f}",
            )
        else:
            total_conductor_m = sum(wire.length_m for wire in antenna.wires)
            feed_rows = f"""
<tr><th>Wires</th><td>{len(antenna.wires)}</td></tr>
<tr><th>Total conductor</th><td>{total_conductor_m:.4f} m</td></tr>
<tr><th>Feed wire</th><td>{_escape(antenna.feed.wire_id)}</td></tr>
<tr><th>Feed height above ground</th><td>{feed_height_m:.4f} m</td></tr>
"""
            construction_note = _note(
                tr,
                "Custom geometry: use the wire table and feed point above. "
                "Verify every connection and the feed gap before construction.",
            )
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
<tr><th>{_escape(tr("SWR ({impedance:g} Ω)", impedance=result.spec.reference_impedance_ohm))}</th><td>{_swr_text(frequency)}</td></tr>
<tr><th>Efficiency</th><td>{f"{efficiency:.2f} %" if efficiency is not None else "—"}</td></tr>
{"".join(f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>" for label, value in localize_rows(gain_metric_rows(result), tr))}
{bandwidth_row}
<tr><th>Resonance</th><td>{_escape(_resonance_text(result, tr))}</td></tr>
<tr><th>Solver</th><td>{_escape(result.solver.name)} {_escape(result.solver.version)}</td></tr>
<tr><th>Fingerprint</th><td><code>{_escape(result.model_fingerprint)}</code></td></tr>
"""
    else:
        simulation_rows = f"<tr><th>Simulation</th><td>{_escape(tr('No result yet.'))}</td></tr>"

    document = f"""<!DOCTYPE html>
<html lang="{_escape(language)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_escape(project.name)} — {_escape(design.name)} — {_escape(tr("construction sheet"))}</title>
<style>{CSS}</style>
</head>
<body>
<h1>{_escape(project.name)} — {_escape(design.name)}</h1>
{title_block}
<p class="muted">{_escape(tr("AntennaDesk construction sheet · SI units (m, MHz, Ω)"))}</p>
{figure_section}
<h2>Dimensions</h2>
<table>
{dimension_rows}
{feed_rows}
</table>
{schedule_section}
{bom_section}
{evidence_section}
<h2>Simulation</h2>
<table>
{simulation_rows}
</table>

<h2>Construction notes</h2>
<div class="notes">
{construction_note}
<p>{_escape(tr("Trim and re-measure after installation. Real ground, supports, feed line, and nearby objects can shift the result. A low SWR does not prove high efficiency or a useful radiation pattern."))}</p>
</div>

<footer>{_escape(tr("AntennaDesk · GPL-3.0-or-later · Use the browser print dialog to save this sheet as PDF."))}</footer>
</body>
</html>
"""
    return localize_html_labels(document, tr)


def write_construction_sheet(
    project: Project,
    design: DesignVariant,
    result: SimulationResult | None,
    path: Path,
    *,
    figure_png_data_uri: str | None = None,
    auxiliary_png_data_uri: str | None = None,
    isometric_png_data_uri: str | None = None,
    auxiliary_kind: str | None = None,
    labeler: Labeler | None = None,
    language: str = "en",
) -> None:
    path.write_text(
        render_construction_sheet(
            project,
            design,
            result,
            figure_png_data_uri=figure_png_data_uri,
            auxiliary_png_data_uri=auxiliary_png_data_uri,
            isometric_png_data_uri=isometric_png_data_uri,
            auxiliary_kind=auxiliary_kind,
            labeler=labeler,
            language=language,
        ),
        encoding="utf-8",
        newline="\n",
    )
