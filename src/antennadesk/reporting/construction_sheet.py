# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Printable construction sheet for a design."""

from __future__ import annotations

import html
import math
import re
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
from ..domain.antennas.log_periodic import LogPeriodicParameters
from ..domain.antennas.loop import LoopOrientation, LoopParameters
from ..domain.antennas.magnetic_loop import MagneticLoopParameters
from ..domain.antennas.matching_network import (
    LNetwork,
    MatchingNetwork,
    PiNetwork,
    TNetwork,
)
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.phased_vertical import PhasedVerticalParameters
from ..domain.antennas.quad_beam import QuadBeamParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvKind, ScvParameters
from ..domain.antennas.stacked_yagi import (
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from ..domain.antennas.t2fd import T2FDParameters
from ..domain.antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.trap_yagi import TrapYagiParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.wilkinson_tolerance import analyze_stacked_yagi_tolerances
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zepp import (
    ZEPP_MATCHING_FEED_ID,
    ZEPP_MATCHING_OPEN_ID,
    ZEPP_RADIATOR_ID,
    ZeppParameters,
    parallel_wire_impedance_ohm,
)
from ..domain.design.feed_balance import requires_current_balun
from ..domain.design.feed_connection import feed_connection_detail
from ..domain.design.matching_resolution import resolve_matching_network
from ..domain.design.preflight import PreflightReport, PreflightStatus
from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.metrics import measure_swr_bandwidth
from ..domain.simulation.resonance import find_resonances
from ..domain.simulation.result import FrequencyResult, SimulationResult
from ..presentation.units import DisplayUnits, LengthPolicy, UnitSystem
from .bom_costs import bom_cost_entries, bom_cost_total, format_cost, hardware_cost_key
from .construction_package import (
    as_built_rows,
    checklist_rows,
    coil_trap_rows,
    hardware_bom_items,
)
from .design_summary import (
    design_evidence_rows,
    design_provenance_rows,
    design_summary_rows,
    feed_matching_rows,
    hexbeam_band_set_label,
    installation_profile_rows,
    load_summary_rows,
    matching_network_description,
    optimization_summary_rows,
    transmission_line_summary_rows,
)
from .feed_schematic import feed_schematic_svg
from .localization import (
    PREFLIGHT_CATEGORY_LABELS,
    Labeler,
    identity_labeler,
    localize_html_labels,
    localize_preflight_message,
    localize_rows,
)
from .result_summary import gain_metric_rows
from .wire_schedule import (
    bom_summary_rows,
    conductor_bom_rows,
    feed_schedule_row,
    wire_schedule_html_rows,
    wire_schedule_table_unit,
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
.feed-schematic { border: 1px solid #ddd; background: #fff; padding: 8px; margin: 10px 0; }
.feed-schematic svg { display: block; width: 100%; height: auto; }
.preflight { padding: 8px 12px; margin: 8px 0; border-left: 4px solid #888; }
.preflight-error { background: #fef3f2; border-left-color: #b42318; }
.preflight-warning { background: #fffaeb; border-left-color: #b54708; }
.preflight-ready { background: #ecfdf3; border-left-color: #067647; }
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


def _design_topology_label(network: MatchingNetwork) -> str:
    if isinstance(network, PiNetwork):
        return "Pi network (primary side)"
    if isinstance(network, TNetwork):
        return "T network (primary side)"
    return "L network (primary side)"


def _design_component_rows(
    network: MatchingNetwork,
) -> tuple[tuple[str, float, float], ...]:
    if isinstance(network, PiNetwork):
        return (
            (
                "Input shunt",
                network.input_shunt_inductance_h,
                network.input_shunt_capacitance_f,
            ),
            ("Design series", network.series_inductance_h, network.series_capacitance_f),
            (
                "Output shunt",
                network.output_shunt_inductance_h,
                network.output_shunt_capacitance_f,
            ),
        )
    if isinstance(network, TNetwork):
        return (
            (
                "Input series",
                network.input_series_inductance_h,
                network.input_series_capacitance_f,
            ),
            ("Design shunt", network.shunt_inductance_h, network.shunt_capacitance_f),
            (
                "Output series",
                network.output_series_inductance_h,
                network.output_series_capacitance_f,
            ),
        )
    if not isinstance(network, LNetwork):
        raise TypeError(f"unsupported design matching network: {type(network)!r}")
    return (
        ("Design series", network.series_inductance_h, network.series_capacitance_f),
        ("Design shunt", network.shunt_inductance_h, network.shunt_capacitance_f),
    )


def _network_branch_text(inductance_h: float, capacitance_f: float) -> str:
    if inductance_h > 0.0:
        return f"{inductance_h * 1e6:g} µH"
    if capacitance_f > 0.0:
        return f"{capacitance_f * 1e12:g} pF"
    return "—"


def _render_note(
    labeler: Labeler,
    template: str,
    *,
    display_units: DisplayUnits | None = None,
    **values: object,
) -> str:
    """Render one localized construction paragraph."""

    if display_units is None:
        return f"<p>{labeler(template, **values)}</p>"
    names = re.findall(r"\{(\w+)(?::[^}]*)?\} m", template)
    lengths: list[float] = []
    for name in names:
        raw = values.get(name)
        try:
            lengths.append(float(raw))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
    if not lengths:
        return f"<p>{labeler(template, **values)}</p>"
    unit = display_units.unit_for(max(lengths))
    factor = display_units.meters_per_unit(unit)
    decimals = display_units.decimals_for(unit)
    converted = dict(values)
    for name in names:
        raw = values.get(name)
        try:
            meters = float(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        converted[name] = f"{meters / factor:.{decimals}f}"
    text = labeler(template, **converted).replace(" m", f" {unit}")
    return f"<p>{text}</p>"


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


def _preflight_status_text(report: PreflightReport, tr: Labeler) -> str:
    if report.status is PreflightStatus.ERROR:
        return tr("Not ready to build: fix the errors below.")
    if report.status is PreflightStatus.WARNING:
        return tr("Ready to build with warnings.")
    return tr("Ready to build.")


def _preflight_section(report: PreflightReport | None, tr: Labeler) -> str:
    if report is None:
        return ""
    status_text = _preflight_status_text(report, tr)
    css_class = f"preflight-{report.status.value}"
    if not report.findings:
        return (
            "<h2>Construction pre-flight</h2>"
            f'<div class="preflight {css_class}">'
            f"<p>{_escape(status_text)}</p>"
            f"<p>{_escape(tr('No pre-flight issues found.'))}</p>"
            "</div>"
        )
    rows = "".join(
        "<tr>"
        f"<td>{_escape(tr(finding.severity.value.title()))}</td>"
        f"<td>{_escape(tr(PREFLIGHT_CATEGORY_LABELS[finding.category]))}</td>"
        f"<td>{_escape(localize_preflight_message(finding, tr))}</td>"
        f"<td>{_escape(finding.subject or finding.field or '—')}</td>"
        "</tr>"
        for finding in report.sorted_findings()
    )
    return f"""
<h2>Construction pre-flight</h2>
<div class="preflight {css_class}"><p>{_escape(status_text)}</p></div>
<table class="schedule">
<thead>
<tr><th>Severity</th><th>Category</th><th>Finding</th><th>Where</th></tr>
</thead>
<tbody>
{rows}
</tbody>
</table>
"""


def _length(
    value_m: float,
    display_units: DisplayUnits | None,
    *,
    decimals: int = 4,
) -> str:
    if display_units is None:
        return f"{value_m:.{decimals}f} m"
    return display_units.format_length(value_m, trim=False)


def _units_title(display_units: DisplayUnits | None) -> str:
    if display_units is None:
        return "SI (m, MHz, Ω)"
    system = "Metric" if display_units.system is UnitSystem.METRIC else "Imperial"
    policy = "auto" if display_units.length_policy is LengthPolicy.AUTO else "fixed"
    units = "mm/cm/m" if display_units.system is UnitSystem.METRIC else "in/ft"
    return f"{system} {policy} ({units}, MHz, Ω)"


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
    preflight: PreflightReport | None = None,
    display_units: DisplayUnits | None = None,
) -> str:
    tr = labeler or identity_labeler
    parameters = design.parameters
    antenna = design.antenna

    def _note(labeler: Labeler, template: str, **values: object) -> str:
        return _render_note(
            labeler,
            template,
            display_units=display_units,
            **values,
        )

    feed_detail = feed_connection_detail(
        parameters,
        antenna,
        current_balun=project.current_balun,
        feed_line=project.feed_line,
        balun_loss=project.balun_loss,
    )
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
                    display_units=display_units,
                ),
                *installation_profile_rows(
                    project.active_installation_profile,
                    labeler=tr,
                    display_units=display_units,
                ),
                *feed_matching_rows(
                    project.matching_network,
                    project.feed_line,
                    project.balun_loss,
                    labeler=tr,
                    position=project.matching_network_position,
                    current_balun=project.current_balun,
                    display_units=display_units,
                ),
                *optimization_summary_rows(design),
                *design_provenance_rows(design, display_units),
                *load_summary_rows(
                    design.antenna.loads,
                    labeler=tr,
                    display_units=display_units,
                ),
                *transmission_line_summary_rows(
                    design.antenna.transmission_lines,
                    labeler=tr,
                    display_units=display_units,
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
<tr><th>Units</th><td>{_escape(_units_title(display_units))}</td><th>Updated</th><td>{project.updated_at:%Y-%m-%d}</td></tr>
</table>
"""
    schedule_rows = "".join(wire_schedule_html_rows(design, display_units))
    schedule_unit = wire_schedule_table_unit(design, display_units)
    feed = feed_schedule_row(antenna)
    cost_entries = {entry.key: entry for entry in bom_cost_entries(project, design, tr)}
    costs = project.bom_costs
    currency = costs.currency if costs is not None else ""
    conductor_cost_headers = (
        "<th>Unit cost / m</th><th>Line total</th>" if costs is not None else ""
    )
    hardware_cost_headers = "<th>Unit cost</th><th>Line total</th>" if costs is not None else ""

    def _cost_cells(entry_key: str) -> str:
        if costs is None:
            return ""
        entry = cost_entries.get(entry_key)
        if entry is None:
            return '<td class="num">—</td><td class="num">—</td>'
        return (
            f'<td class="num">{_escape(format_cost(entry.unit_cost, currency))}</td>'
            f'<td class="num">{_escape(format_cost(entry.line_total, currency))}</td>'
        )

    bom_conductor_rows = "".join(
        "<tr>"
        f"<td>{_escape(tr(row.material))}</td>"
        f'<td class="num">Ø{row.diameter_mm:.3f} mm</td>'
        f'<td class="num">{row.wire_count}</td>'
        f'<td class="num">{_length(row.total_length_m, display_units)}</td>'
        f"{_cost_cells(row.cost_key)}"
        "</tr>"
        for row in conductor_bom_rows(antenna)
    )
    bom_summary = "".join(
        f"<tr><th>{_escape(label)}</th><td>{_escape(value)}</td></tr>"
        for label, value in localize_rows(bom_summary_rows(antenna, display_units), tr)
    )
    bom_section = f"""
<h2>Bill of materials</h2>
<table class="schedule">
<thead>
<tr><th>Material</th><th>Diameter</th><th>Wires</th><th>Total length</th>{conductor_cost_headers}</tr>
</thead>
<tbody>
{bom_conductor_rows}
</tbody>
</table>
<table>
{bom_summary}
</table>
"""
    record = project.construction_record
    as_built_section = ""
    if record is not None:
        as_built_values = "".join(
            "<tr>"
            f"<td>{_escape(label)}</td>"
            f"<td>{_escape(design_value)}</td>"
            f"<td>{_escape(actual_value)}</td>"
            f"<td>{_escape(difference)}</td>"
            f"<td>{_escape(notes)}</td>"
            "</tr>"
            for label, design_value, actual_value, difference, notes in as_built_rows(
                record,
                tr,
            )
        )
        notes = (
            f'<div class="notes"><p>{_escape(record.as_built_notes)}</p></div>'
            if record.as_built_notes.strip()
            else ""
        )
        if as_built_values or notes:
            as_built_section = f"""
<h2>As-built record</h2>
{notes}
<table class="schedule">
<thead>
<tr><th>Dimension</th><th>Design</th><th>Actual</th><th>Difference</th><th>Notes</th></tr>
</thead>
<tbody>
{as_built_values}
</tbody>
</table>
"""
    hardware_values = "".join(
        "<tr>"
        f"<td>{_escape(tr(row.label))}</td>"
        f"<td>{_escape(row.quantity)}</td>"
        f"<td>{_escape(row.unit)}</td>"
        f"<td>{_escape(tr(row.note))}</td>"
        f"{_cost_cells(hardware_cost_key(row.key))}"
        "</tr>"
        for row in hardware_bom_items(project, design)
    )
    hardware_section = f"""
<h2>Hardware BOM</h2>
<table class="schedule">
<thead>
<tr><th>Item</th><th>Qty</th><th>Unit</th><th>Notes</th>{hardware_cost_headers}</tr>
</thead>
<tbody>
{hardware_values}
</tbody>
</table>
"""
    bom_total = bom_cost_total(tuple(cost_entries.values()))
    bom_total_section = (
        f"<p><strong>{_escape(tr('BOM total'))}:</strong> "
        f"{_escape(format_cost(bom_total, currency))}</p>"
        if costs is not None
        else ""
    )
    coil_values = "".join(
        "<tr>"
        f"<td>{_escape(kind)}</td>"
        f"<td>{_escape(wire_id)}</td>"
        f"<td>{_escape(position)}</td>"
        f"<td>{_escape(inductance)}</td>"
        f"<td>{_escape(capacitance)}</td>"
        f"<td>{_escape(resistance)}</td>"
        f"<td>{_escape(note)}</td>"
        "</tr>"
        for kind, wire_id, position, inductance, capacitance, resistance, note in coil_trap_rows(
            design,
            tr,
        )
    )
    coil_section = (
        f"""
<h2>Coils and traps</h2>
<table class="schedule">
<thead>
<tr><th>Type</th><th>Wire</th><th>Position</th><th>Inductance</th><th>Capacitance</th><th>Resistance</th><th>Notes</th></tr>
</thead>
<tbody>
{coil_values}
</tbody>
</table>
"""
        if coil_values
        else ""
    )
    checklist_values = "".join(
        f"<tr><td>{'&#9745;' if checked else '&#9744;'}</td><td>{_escape(label)}</td></tr>"
        for label, checked in checklist_rows(record, tr)
    )
    checklist_section = f"""
<h2>Construction checklist</h2>
<table>
{checklist_values}
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
<tr><th>#</th><th>Wire</th><th>Start ({schedule_unit})</th><th>End ({schedule_unit})</th><th>Length ({schedule_unit})</th><th>Ø (mm)</th><th>Material</th></tr>
</thead>
<tbody>
{schedule_rows}
</tbody>
</table>
<table>
<tr><th>Feed wire</th><td><code>{_escape(feed.wire_id)}</code></td></tr>
<tr><th>Feed offset</th><td>{_escape(tr("{offset} from the wire start", offset=_length(feed.offset_m, display_units)))}</td></tr>
<tr><th>Feed coordinates</th><td>{feed.point.x_m:.4f}, {feed.point.y_m:.4f}, {_length(feed.point.z_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed.height_m, display_units)}</td></tr>
</table>
"""
    if isinstance(parameters, DipoleParameters):
        if parameters.sag_m > 0.0:
            feed_rows = f"""
<tr><th>Span</th><td>{_length(parameters.total_length_m, display_units)}</td></tr>
<tr><th>Conductor length</th><td>{_length(parameters.conductor_length_m, display_units)}</td></tr>
<tr><th>Wire height at supports</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Center sag</th><td>{_length(parameters.sag_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>First leg (from wire start)</th><td>{_length(feed_offset_m, display_units)}</td></tr>
<tr><th>Second leg (from feed)</th><td>{_length(other_leg_m, display_units)}</td></tr>
<tr><th>Wire height at start</th><td>{_length(feed_wire.start.z_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Total wire length</th><td>{_length(parameters.total_length_m, display_units)}</td></tr>
<tr><th>Center section</th><td>{_length(parameters.inner_length_m, display_units)}</td></tr>
<tr><th>Outer sections</th><td>{_escape(tr("{length} each", length=_length(parameters.outer_length_m, display_units)))}</td></tr>
<tr><th>Trap positions</th><td>{_escape(tr("{left}, {right} from wire start", left=_length(left_position, display_units), right=_length(right_position, display_units)))}</td></tr>
<tr><th>Trap frequency</th><td>{parameters.trap_frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Trap inductance</th><td>{parameters.trap_inductance_h * 1e6:.4f} µH</td></tr>
<tr><th>Trap capacitance</th><td>{parameters.trap_capacitance_f * 1e12:.4f} pF</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Element length</th><td>{_escape(tr("{length} each", length=_length(parameters.length_m, display_units)))}</td></tr>
<tr><th>Conductor spacing</th><td>{_length(parameters.spacing_m, display_units)}</td></tr>
<tr><th>Design band</th><td>{parameters.frequency_hz / 1e6:.6f} MHz to {parameters.highest_frequency_hz / 1e6:.6f} MHz</td></tr>
<tr><th>Termination resistor</th><td>{parameters.termination_resistance_ohm:g} Ω non-inductive</td></tr>
<tr><th>Feed transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Driven element length</th><td>{_length(parameters.total_length_m, display_units)}</td></tr>
<tr><th>End connector length</th><td>{_length(parameters.spacing_m, display_units)}</td></tr>
<tr><th>Feed location</th><td>{_escape(tr("center of driven element"))}</td></tr>
<tr><th>Feed transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
        if parameters.transformer_ratio == 1.0:
            construction_note = _note(
                tr,
                "Cut two equal driven elements of {total} m and two end connectors of "
                "{spacing} m. Join them at both ends and feed the center of one "
                "element. The total conductor length is {conductor} m.",
                total=f"{parameters.total_length_m:.4f}",
                spacing=f"{parameters.spacing_m:.4f}",
                conductor=f"{parameters.total_conductor_length_m:.4f}",
            )
        else:
            construction_note = _note(
                tr,
                "Cut two equal driven elements of {total} m and two end connectors of "
                "{spacing} m. Join them at both ends and feed the center of one "
                "element through a {ratio}:1 transformer. The total conductor "
                "length is {conductor} m.",
                total=f"{parameters.total_length_m:.4f}",
                spacing=f"{parameters.spacing_m:.4f}",
                ratio=f"{parameters.transformer_ratio:g}",
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
<tr><th>Horizontal length</th><td>{_length(parameters.horizontal_length_m, display_units)}</td></tr>
<tr><th>Horizontal segment</th><td>{_escape(tr("{length} each", length=_length(parameters.horizontal_segment_m, display_units)))}</td></tr>
<tr><th>Vertical length</th><td>{_length(parameters.vertical_height_m, display_units)}</td></tr>
<tr><th>Vertical elements</th><td>{parameters.vertical_count}</td></tr>
<tr><th>Base height</th><td>{_length(parameters.base_height_m, display_units)}</td></tr>
<tr><th>Top height</th><td>{_length(parameters.top_height_m, display_units)}</td></tr>
<tr><th>Feed offset below top</th><td>{_length(parameters.feed_offset_m, display_units)}</td></tr>
<tr><th>Total conductor</th><td>{_length(parameters.total_conductor_length_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Active length</th><td>{_length(parameters.active_length_m, display_units)}</td></tr>
<tr><th>Full length</th><td>{_length(parameters.total_length_m, display_units)}</td></tr>
<tr><th>Link offset</th><td>{_length(parameters.link_offset_m, display_units)}</td></tr>
<tr><th>Height</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
        band_rows = ""
        if len(parameters.bands) > 1:
            band_rows = (
                f"<tr><th>Band set</th><td>{hexbeam_band_set_label(parameters)}</td></tr>"
                f"<tr><th>Bands</th><td>{len(parameters.bands)}</td></tr>"
                "<tr><th>Feed model</th><td>one driven band; other bands passive; "
                "coax harness and balun not modeled</td></tr>"
            ) + "".join(
                f"<tr><th>Band</th><td>{band.label}: "
                f"driver {_length(band.driver_half_length_m, display_units)}"
                f" · reflector {_length(band.reflector_half_length_m, display_units)}"
                f" · tip gap {_length(band.tip_gap_m, display_units)}"
                f" · offset {_length(band.vertical_offset_m, display_units)}</td></tr>"
                for band in parameters.bands
            )
        feed_rows = f"""
<tr><th>Type</th><td>{parameters.template_name}</td></tr>
<tr><th>Driver half-length</th><td>{_length(parameters.driver_half_length_m, display_units)}</td></tr>
<tr><th>Reflector half-length</th><td>{_length(parameters.reflector_half_length_m, display_units)}</td></tr>
<tr><th>Turning radius</th><td>{_length(parameters.turning_radius_m, display_units)}</td></tr>
<tr><th>Tip gap</th><td>{_length(parameters.tip_gap_m, display_units)}</td></tr>
<tr><th>Overall span</th><td>{_length(parameters.overall_span_m, display_units)}</td></tr>
{band_rows}
<tr><th>Feed height above ground</th><td>{_length(parameters.height_m, display_units)}</td></tr>
"""
        construction_note = _note(
            tr,
            "Build an M-shaped driver with {driver} m half-lengths and a U-shaped "
            "reflector with {reflector} m half-lengths on a six-spreader frame "
            "with a {turning} m turning radius. Set the tip gap to {tip_gap} m and "
            "feed the center of the M. The reflector wraps the rear three sides; "
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
<tr><th>Driven element</th><td>{_length(parameters.driven_length_m, display_units)}</td></tr>
<tr><th>Reflector element</th><td>{_length(parameters.reflector_length_m, display_units)}</td></tr>
<tr><th>Boom length</th><td>{_length(parameters.boom_length_m, display_units)}</td></tr>
<tr><th>Trap inset</th><td>{_length(parameters.trap_inset_m, display_units)}</td></tr>
<tr><th>Trap frequency</th><td>{parameters.trap_frequency_hz / 1e6:.3f} MHz</td></tr>
<tr><th>Trap inductance</th><td>{parameters.trap_inductance_h * 1e6:.3f} µH</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Cone height</th><td>{_length(parameters.cone_height_m, display_units)}</td></tr>
<tr><th>Cone base radius</th><td>{_length(parameters.cone_radius_m, display_units)}</td></tr>
<tr><th>Disc radius</th><td>{_length(parameters.disc_radius_m, display_units)}</td></tr>
<tr><th>Base height</th><td>{_length(parameters.base_height_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(parameters.feed_height_m, display_units)}</td></tr>
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
    elif isinstance(parameters, LogPeriodicParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Elements</th><td>{parameters.element_count}</td></tr>
<tr><th>Band</th><td>{parameters.frequency_low_hz / 1e6:.3f}-{parameters.frequency_high_hz / 1e6:.3f} MHz</td></tr>
<tr><th>Longest element</th><td>{_length(parameters.longest_element_length_m, display_units)}</td></tr>
<tr><th>Shortest element</th><td>{_length(parameters.shortest_element_length_m, display_units)}</td></tr>
<tr><th>Tau</th><td>{parameters.tau:.4f}</td></tr>
<tr><th>Sigma</th><td>{parameters.sigma:.4f}</td></tr>
<tr><th>Boom length</th><td>{_length(parameters.boom_length_m, display_units)}</td></tr>
<tr><th>Phase-line Z0</th><td>{parameters.phase_line_impedance_ohm:.1f} Ω</td></tr>
<tr><th>Phase-line velocity factor</th><td>{parameters.phase_line_velocity_factor:.3f}</td></tr>
<tr><th>Feed transformer</th><td>{parameters.feed_transformer_ratio:.1f}:1</td></tr>
<tr><th>Height</th><td>{_length(parameters.height_m, display_units)}</td></tr>
"""
        construction_note = _note(
            tr,
            "Cut {count} straight elements with the longest at {longest} m and "
            "the shortest at {shortest} m. Space them along the boom using the "
            "generated schedule, with the rear element at the back. Run the "
            "transposed phase line between adjacent element centers with a "
            "crossover between each pair; short the rear element center and feed "
            "the front element center through the {ratio}:1 transformer. The "
            "phase line is an ideal lossless two-port; the balun, feed-line loss, "
            "rear stub, boom, mast, and construction tolerances are not modeled.",
            count=parameters.element_count,
            longest=f"{parameters.longest_element_length_m:.4f}",
            shortest=f"{parameters.shortest_element_length_m:.4f}",
            ratio=f"{parameters.feed_transformer_ratio:.1f}",
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
<tr><th>Driven loop side</th><td>{_length(parameters.loop_side_m, display_units)}</td></tr>
<tr><th>Reflector side</th><td>{_length(parameters.reflector_side_m, display_units)}</td></tr>
<tr><th>Reflector spacing</th><td>{_length(parameters.reflector_spacing_m, display_units)}</td></tr>
<tr><th>Boom length</th><td>{_length(parameters.boom_length_m, display_units)}</td></tr>
<tr><th>Height</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Feed transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Feed height above ground</th><td>{_length(parameters.feed_height_m, display_units)}</td></tr>
"""
        transformer_note = (
            tr(
                " Feed the midpoint through a {ratio}:1 transformer.",
                ratio=f"{parameters.transformer_ratio:g}",
            )
            if parameters.transformer_ratio != 1.0
            else tr(" Feed the midpoint directly; no transformer is modeled.")
        )
        construction_note = _note(
            tr,
            "Build {count} square loops with the driven loop at {side} m per side "
            "and the reflector at {reflector} m per side. Set the reflector "
            "{spacing} m behind the driven loop.{director_note} Feed the midpoint "
            "of the driven loop's left vertical side and keep the loops square. "
            "The boom, spreaders, mast, and any additional matching network are "
            "not modeled; the feed transformer is ideal. Tune the match for the "
            "installed antenna.{transformer_note}",
            count=parameters.element_count,
            side=f"{parameters.loop_side_m:.4f}",
            reflector=f"{parameters.reflector_side_m:.4f}",
            spacing=f"{parameters.reflector_spacing_m:.4f}",
            director_note=director_note,
            transformer_note=transformer_note,
        )
    elif isinstance(parameters, PhasedVerticalParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Verticals</th><td>{parameters.element_count}</td></tr>
<tr><th>Element spacing</th><td>{_length(parameters.spacing_m, display_units)}</td></tr>
<tr><th>Vertical element length</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Base height</th><td>{_length(parameters.base_height_m, display_units)}</td></tr>
<tr><th>Phase step</th><td>{parameters.phase_step_deg:.1f}°</td></tr>
<tr><th>Amplitude taper</th><td>{parameters.amplitude_taper * 100.0:.0f}%</td></tr>
<tr><th>Radials per element</th><td>{parameters.radial_count}</td></tr>
<tr><th>Radial length</th><td>{_length(parameters.radial_length_m, display_units)}</td></tr>
<tr><th>Total conductor</th><td>{_length(parameters.total_conductor_length_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
        construction_note = _note(
            tr,
            "Build {count} vertical radiators of {length} m, spaced {spacing} m "
            "along one line, with their bases at {base} m above ground. Fit "
            "{radials} radials of {radial_length} m to each base. Drive the first "
            "vertical as the primary feed and the remaining verticals with the "
            "listed phase and amplitude steps. The combining network is ideal and "
            "is not included; use an explicit feed network and verify the match.",
            count=parameters.element_count,
            length=f"{parameters.height_m:.4f}",
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
<tr><th>Length</th><td>{_length(parameters.length_m, display_units)}</td></tr>
<tr><th>Height</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Termination</th><td>{termination_row}</td></tr>
<tr><th>{_escape(tr("Feed transformer"))}</th><td>{parameters.transformer_ratio:.1f}:1</td></tr>
<tr><th>Total conductor</th><td>{_length(parameters.total_conductor_length_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
        construction_note = _note(
            tr,
            "Run one horizontal wire of {length} m at {height} m above ground. "
            "Connect a short vertical feed stub from the near end to ground and "
            "feed it through a {ratio:.1f}:1 transformer. Keep the wire straight. "
            "{termination_note} The one-wavelength starting length, termination "
            "value, and transformer ratio are assumptions; the pattern and "
            "receiving performance are not independently validated.",
            length=f"{parameters.length_m:.4f}",
            height=f"{parameters.height_m:.4f}",
            ratio=parameters.transformer_ratio,
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
<tr><th>Loop side</th><td>{_length(parameters.loop_side_m, display_units)}</td></tr>
<tr><th>Stack height</th><td>{_length(parameters.total_height_m, display_units)}</td></tr>
<tr><th>Base height</th><td>{_length(parameters.base_height_m, display_units)}</td></tr>
<tr><th>Feed height</th><td>{_length(parameters.feed_height_m, display_units)}</td></tr>
<tr><th>Reflector</th><td>{_escape(tr("{spacing} behind", spacing=_length(parameters.reflector_spacing_m, display_units)))}</td></tr>
<tr><th>Total conductor</th><td>{_length(parameters.total_conductor_length_m, display_units)}</td></tr>
<tr><th>Feed transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
        transformer_note = (
            tr(
                " Feed the midpoint through a {ratio}:1 transformer.",
                ratio=f"{parameters.transformer_ratio:g}",
            )
            if parameters.transformer_ratio != 1.0
            else tr(" Feed the midpoint directly; no transformer is modeled.")
        )
        construction_note = _note(
            tr,
            "Build {count} square loops with {side} m sides. Join them at the "
            "shared horizontal rails, starting at {base} m above ground, and feed "
            "the midpoint of the central rail at {feed_height} m. {reflector_note} "
            "The quarter-wave side and eighth-wave reflector spacing are starting "
            "dimensions; tune them for the installation.{transformer_note}",
            count=parameters.loop_count,
            side=f"{parameters.loop_side_m:.4f}",
            base=f"{parameters.base_height_m:.4f}",
            feed_height=f"{feed_height_m:.4f}",
            reflector_note=reflector_note,
            transformer_note=transformer_note,
        )
    elif isinstance(parameters, RingoParameters):
        feed_rows = f"""
<tr><th>Radiator length</th><td>{_length(parameters.radiator_height_m, display_units)}</td></tr>
<tr><th>Ring diameter</th><td>{_length(parameters.ring_diameter_m, display_units)}</td></tr>
<tr><th>Ring height</th><td>{_length(parameters.ring_height_m, display_units)}</td></tr>
<tr><th>Ring sides</th><td>{parameters.ring_sides}</td></tr>
"""
        construction_note = _note(
            tr,
            "Build a {length} m vertical radiator with a {diameter} m matching "
            "ring at {ring_height} m above ground.",
            length=f"{parameters.radiator_height_m:.4f}",
            diameter=f"{parameters.ring_diameter_m:.4f}",
            ring_height=f"{parameters.ring_height_m:.4f}",
        )
    elif isinstance(parameters, JPoleParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Radiator length</th><td>{_length(parameters.radiator_height_m, display_units)}</td></tr>
<tr><th>Stub length</th><td>{_length(parameters.stub_length_m, display_units)}</td></tr>
<tr><th>Stub spacing</th><td>{_length(parameters.spacing_m, display_units)}</td></tr>
<tr><th>Feed offset</th><td>{_length(parameters.feed_offset_m, display_units)}</td></tr>
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
        resolution = resolve_matching_network(parameters, project.matching_network)
        if resolution.project_active:
            matching_status = tr("retained; project network overrides")
        elif resolution.design_active:
            matching_status = tr("retained; design network overrides")
        else:
            matching_status = tr("active")
        design_status = (
            tr("retained; project network overrides") if resolution.project_active else tr("active")
        )
        counterpoise = (
            f"{parameters.counterpoise_length_m:.4f} m at "
            f"{parameters.effective_return_height_m:.4f} m"
            if parameters.counterpoise_active
            else tr("none")
        )
        return_path_label = {
            "auto": tr("automatic"),
            "installation_proxy": tr("installation proxy"),
            "counterpoise": tr("counterpoise"),
            "coax_shield": tr("coax shield"),
        }[parameters.return_path.value]
        transformer_loss_label = {
            "none": tr("none"),
            "squash_practice_49_1": tr("measured 49:1 (Squash Practice)"),
        }[parameters.transformer_loss_model.value]
        choke = tr("none")
        if parameters.common_mode_choke_active and parameters.common_mode_choke is not None:
            value = parameters.common_mode_choke
            sign = "+" if value.reactance_ohm >= 0.0 else "-"
            choke = (
                f"{value.resistance_ohm:g} {sign} j{abs(value.reactance_ohm):g} Ω "
                f"at {value.measurement_frequency_hz / 1e6:g} MHz"
            )
        return_path_row = f"<tr><th>Return path</th><td>{_escape(return_path_label)}</td></tr>\n"
        coax_shield_row = (
            f"<tr><th>Coax shield</th><td>{_length(parameters.effective_return_length_m, display_units)}</td></tr>\n"
            if parameters.coax_shield_active
            else ""
        )
        feed_section_row = (
            f"<tr><th>Feed section</th><td>{_length(parameters.feed_section_length_m, display_units)}</td></tr>\n"
            if parameters.feed_section_active
            else ""
        )
        installation_return_row = (
            f"<tr><th>Installation return (proxy)</th><td>{_length(parameters.installation_return_length_m, display_units)} (coax/mast proxy)</td></tr>\n"
            if parameters.installation_return_active
            else ""
        )
        matching_rows = (
            f"<tr><th>Matching capacitor</th><td>{parameters.matching_capacitance_f * 1e12:.1f} pF (primary shunt, {_escape(matching_status)})</td></tr>\n"
            f"<tr><th>Transformer leakage</th><td>{parameters.transformer_leakage_inductance_h * 1e6:.4f} µH ({_escape(matching_status)})</td></tr>\n"
            if parameters.matching_network_active
            else ""
        )
        design_matching_rows = ""
        if (
            parameters.design_matching_network_active
            and parameters.design_matching_network is not None
        ):
            network = parameters.design_matching_network
            design_matching_rows = (
                "<tr><th>Design matching network</th><td>"
                f"{_escape(tr(_design_topology_label(network)))}</td></tr>\n"
            )
            for label, inductance_h, capacitance_f in _design_component_rows(network):
                design_matching_rows += (
                    f"<tr><th>{_escape(tr(label))}</th><td>"
                    f"{_escape(_network_branch_text(inductance_h, capacitance_f))} "
                    f"({_escape(design_status)})</td></tr>\n"
                )
        height_rows = (
            f"<tr><th>Vertical section</th><td>{_length(parameters.bend_vertical_length_m, display_units)}</td></tr>\n"
            f"<tr><th>Horizontal run</th><td>{_length(parameters.bend_horizontal_length_m, display_units)}</td></tr>\n"
            f"<tr><th>Top height</th><td>{_length(parameters.bend_top_height_m, display_units)}</td></tr>\n"
            if parameters.bend_active
            else f"<tr><th>End height</th><td>{_length(parameters.end_height_m, display_units)}</td></tr>\n"
        )
        feed_rows = f"""
<tr><th>Wire length</th><td>{_length(parameters.length_m, display_units)}</td></tr>
{feed_section_row}<tr><th>Feed height</th><td>{_length(parameters.feed_height_m, display_units)}</td></tr>
{height_rows}<tr><th>Transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Transformer loss</th><td>{_escape(transformer_loss_label)}</td></tr>
{matching_rows}{design_matching_rows}{return_path_row}<tr><th>Counterpoise</th><td>{counterpoise}</td></tr>
<tr><th>Common-mode choke</th><td>{_escape(choke)}</td></tr>
{coax_shield_row}{installation_return_row}"""
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
            if resolution.project_active:
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
<tr><th>Apex height</th><td>{_length(parameters.apex_height_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Element width</th><td>{_length(parameters.width_m, display_units)}</td></tr>
<tr><th>Element spacing</th><td>{_length(parameters.depth_m, display_units)}</td></tr>
<tr><th>Reflector tip</th><td>{_length(parameters.reflector_tip_m, display_units)}</td></tr>
<tr><th>Driven tip</th><td>{_length(parameters.driven_tip_m, display_units)}</td></tr>
<tr><th>Tip gap</th><td>{_length(parameters.gap_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
        construction_note = _note(
            tr,
            "Build a Moxon rectangle with {width} m elements, {depth} m spacing, "
            "and bent tips leaving a {gap} m gap.",
            width=f"{parameters.width_m:.4f}",
            depth=f"{parameters.depth_m:.4f}",
            gap=f"{parameters.gap_m:.4f}",
        )
    elif isinstance(parameters, StackedYagiParameters):
        yagi = parameters.yagi
        mast_note = (
            " One shared mast runs from ground to the top boom and the guys attach to its top."
            if yagi.mast_diameter_m > 0.0
            else " The shared mast and guys are not modeled."
        )
        folded_row = ""
        folded_note = ""
        if yagi.driven_folded:
            folded_row = f"""
<tr><th>Folded driven element</th><td>{_escape(tr("yes"))}</td></tr>
<tr><th>Fold spacing</th><td>{_length(yagi.driven_fold_spacing_m, display_units)}</td></tr>
"""
            folded_note = tr(
                " Each level uses the folded driven element: join both conductors at "
                "both ends and feed one conductor at its center. No transformer is "
                "built into the geometry; in Wilkinson mode set the per-level "
                "transformer or matching network."
            )
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Levels</th><td>{parameters.count}</td></tr>
<tr><th>Level spacing</th><td>{_length(parameters.spacing_m, display_units)}</td></tr>
<tr><th>Base Yagi elements</th><td>{len(yagi.elements)}</td></tr>
<tr><th>Base boom length</th><td>{_length(parameters.boom_length_m, display_units)}</td></tr>
<tr><th>Base boom height</th><td>{_length(yagi.height_m, display_units)}</td></tr>
<tr><th>Top level height</th><td>{_length(parameters.highest_tip_m, display_units)}</td></tr>
{folded_row}
<tr><th>Phase step</th><td>{"set by the feed network" if parameters.feed.mode is StackedYagiFeedMode.WILKINSON else f"{parameters.effective_phase_step_deg:.1f}°"}</td></tr>
<tr><th>Additional-level ratio</th><td>{"set by the feed network" if parameters.feed.mode is StackedYagiFeedMode.WILKINSON else f"{parameters.amplitude_ratio:.2f}"}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
        match_row = ""
        if yagi.match_type.value == "beta_hairpin":
            match_row = f"""
<tr><th>Feed match</th><td>beta / hairpin</td></tr>
<tr><th>Hairpin length</th><td>{_length(yagi.match_length_m, display_units)}</td></tr>
<tr><th>Hairpin spacing</th><td>{_length(yagi.match_spacing_m, display_units)}</td></tr>
"""
        if parameters.feed.mode is not StackedYagiFeedMode.IDEAL:
            is_network = parameters.feed.mode is StackedYagiFeedMode.NETWORK
            is_wilkinson = parameters.feed.mode is StackedYagiFeedMode.WILKINSON
            has_line_loss = is_network or is_wilkinson
            line_rows = "".join(
                f"<tr><th>Level {index + 1} line</th><td>"
                f"{_length(parameters.feed.line_length_for_level(index), display_units)}"
                f"{f' ({parameters.feed.line_loss_for_level(index):.2f} dB matched)' if has_line_loss else ''}"
                f"</td></tr>"
                for index in range(parameters.count)
            )
            wilkinson_rows = ""
            if is_wilkinson:
                branch_impedance = parameters.feed.characteristic_impedance_ohm * math.sqrt(
                    parameters.count
                )
                level_matching_rows = "".join(
                    f"<tr><th>{_escape(tr('Level {level} matching', level=level_index + 1))}</th>"
                    f"<td>{_escape(matching_network_description(network, tr))}</td></tr>"
                    for level_index, network in enumerate(parameters.feed.level_matching_networks)
                    if network is not None
                )
                level_transformer_rows = "".join(
                    f"<tr><th>{_escape(tr('Level {level} transformer', level=level_index + 1))}</th>"
                    f"<td>{ratio:g}:1</td></tr>"
                    for level_index, ratio in enumerate(parameters.feed.level_transformer_ratios)
                    if not math.isclose(ratio, 1.0, rel_tol=0.0, abs_tol=1e-12)
                )
                tolerance = analyze_stacked_yagi_tolerances(parameters)
                tolerance_rows = ""
                if parameters.feed.branch_loss_db_per_100m > 0.0:
                    tolerance_rows += (
                        f"<tr><th>Branch matched loss</th><td>"
                        f"{parameters.feed.branch_loss_db_per_100m:.2f} dB/100 m</td></tr>"
                    )
                if parameters.feed.isolation_resistor_inductance_h > 0.0:
                    tolerance_rows += (
                        f"<tr><th>Isolation resistor inductance</th><td>"
                        f"{parameters.feed.isolation_resistor_inductance_h * 1e9:.1f} nH"
                        f"</td></tr>"
                    )
                if tolerance is not None:
                    tolerance_rows += (
                        f"<tr><th>Branch impedance tolerance</th><td>"
                        f"{parameters.feed.branch_impedance_tolerance_pct:.1f}%</td></tr>"
                        f"<tr><th>Isolation resistor tolerance</th><td>"
                        f"{parameters.feed.isolation_resistor_tolerance_pct:.1f}%</td></tr>"
                        f"<tr><th>Tolerance corners</th><td>{tolerance.corner_count}</td></tr>"
                        f"<tr><th>Worst input return loss</th><td>"
                        f"{tolerance.worst_input_return_loss_db:.2f} dB</td></tr>"
                        f"<tr><th>Worst output isolation</th><td>"
                        f"{tolerance.worst_isolation_db:.2f} dB</td></tr>"
                        f"<tr><th>Worst output imbalance</th><td>"
                        f"{tolerance.worst_imbalance_db:.2f} dB</td></tr>"
                        "<tr><th>Tolerance model</th><td>divider S-parameters; "
                        "matching and transformers excluded</td></tr>"
                    )
                wilkinson_rows = (
                    f"<tr><th>Divider design frequency</th><td>"
                    f"{parameters.splitter_design_frequency_hz / 1_000_000.0:.4f} MHz</td></tr>"
                    f"<tr><th>Branch impedance</th><td>{branch_impedance:.1f} Ω</td></tr>"
                    f"<tr><th>Isolation resistors</th><td>{parameters.count} x "
                    f"{parameters.feed.characteristic_impedance_ohm:.1f} Ω star</td></tr>"
                    "<tr><th>Divider model</th><td>ideal quarter-wave branches and "
                    "star resistors</td></tr>"
                    f"{level_matching_rows}"
                    f"{level_transformer_rows}"
                    f"{tolerance_rows}"
                )
            feed_rows += f"""
<tr><th>Feed network</th><td>{"Wilkinson N-port divider" if is_wilkinson else "splitter + phase lines (co-simulated lossless TL network)" if is_network else "splitter + phase lines"}</td></tr>
{line_rows}
<tr><th>Line velocity factor</th><td>{parameters.feed.velocity_factor:.3f}</td></tr>
<tr><th>Line Z0</th><td>{parameters.feed.characteristic_impedance_ohm:.1f} Ω</td></tr>
<tr><th>Splitter excess loss</th><td>{parameters.feed.splitter_loss_db:.2f} dB</td></tr>
{wilkinson_rows}
{f"<tr><th>Matched line loss</th><td>{parameters.feed.line_loss_db_per_100m:.2f} dB/100 m</td></tr>" if has_line_loss else ""}
"""
            if is_wilkinson:
                branch_impedance = parameters.feed.characteristic_impedance_ohm * math.sqrt(
                    parameters.count
                )
                construction_note = _note(
                    tr,
                    "Build {count} identical Yagis on one vertical stack with {spacing} m "
                    "between level booms. The splitter is an equal {count}-way Wilkinson: "
                    "{branch} Ω quarter-wave branches and a star of {count} "
                    "{isolation} Ω isolation resistors, designed at {design} MHz. Feed "
                    "line lengths are {lengths}, with {velocity} velocity factor and "
                    "{z0} Ω characteristic impedance. Record {loss} dB of splitter excess "
                    "loss and {line_loss} dB/100 m of matched line loss plus a per-port "
                    "mismatch correction, applied to realized gain. The N-port solver "
                    "combines the divider with the antenna port admittance; the pattern "
                    "is reconstructed from the solved port voltages. Branches and "
                    "resistors are ideal; component loss, tolerance, and broadband "
                    "behavior are not modeled. Fit each level as a complete Yagi from "
                    "the base element table. {folded_note} {mast_note} Verify the "
                    "combined pattern and match.",
                    count=parameters.count,
                    spacing=f"{parameters.spacing_m:.4f}",
                    branch=f"{branch_impedance:.1f}",
                    isolation=f"{parameters.feed.characteristic_impedance_ohm:.1f}",
                    design=f"{parameters.splitter_design_frequency_hz / 1_000_000.0:.4f}",
                    lengths=", ".join(
                        f"L{index + 1} {parameters.feed.line_length_for_level(index):.4f} m"
                        for index in range(parameters.count)
                    ),
                    velocity=f"{parameters.feed.velocity_factor:.3f}",
                    z0=f"{parameters.feed.characteristic_impedance_ohm:.1f}",
                    loss=f"{parameters.feed.splitter_loss_db:.2f}",
                    line_loss=f"{parameters.feed.line_loss_db_per_100m:.2f}",
                    folded_note=folded_note,
                    mast_note=mast_note,
                )
            elif parameters.feed.mode is StackedYagiFeedMode.NETWORK:
                construction_note = _note(
                    tr,
                    "Build {count} identical Yagis on one vertical stack with {spacing} m "
                    "between level booms. The splitter node is a 1 cm numerical feed "
                    "point above the stack, not an antenna conductor. Feed "
                    "every level through a {count}-way splitter and a lossless "
                    "transmission-line network: level 1 is {reference} m, and each "
                    "higher level adds {increment} m of {velocity} velocity-factor "
                    "line. Record {loss} dB of splitter excess loss and {line_loss} "
                    "dB/100 m of matched line loss plus a per-port mismatch correction, "
                    "applied to realized gain. The solver "
                    "co-simulates the network and reports every port; the primary SWR is "
                    "the lossless network input and splitter internal mismatch is not "
                    "modeled. Fit each level as a "
                    "complete Yagi from the base element table. {folded_note} "
                    "Per-level matching is not modeled in the co-simulated network "
                    "mode. {mast_note} Verify the combined pattern and match.",
                    count=parameters.count,
                    spacing=f"{parameters.spacing_m:.4f}",
                    reference=f"{parameters.feed.reference_length_m:.4f}",
                    increment=f"{parameters.feed.line_increment_m:.4f}",
                    velocity=f"{parameters.feed.velocity_factor:.3f}",
                    loss=f"{parameters.feed.splitter_loss_db:.2f}",
                    line_loss=f"{parameters.feed.line_loss_db_per_100m:.2f}",
                    folded_note=folded_note,
                    mast_note=mast_note,
                )
            else:
                construction_note = _note(
                    tr,
                    "Build {count} identical Yagis on one vertical stack with {spacing} m "
                    "between level booms. Level 1 is the primary feed; drive levels 2 to "
                    "{last} with a {ratio} relative amplitude. Feed the levels through a "
                    "{count}-way splitter and phase lines: level 1 is {reference} m, and "
                    "each higher level adds {increment} m of {velocity} velocity-factor "
                    "line. Record {loss} dB of splitter excess loss. The line impedance "
                    "transformation and line loss are not modeled; the solver uses ideal "
                    "voltage sources. Fit each level as a complete Yagi from the base "
                    "element table. {folded_note} Per-level matching is not modeled in "
                    "phase-line mode. {mast_note} Verify the combined pattern and match.",
                    count=parameters.count,
                    spacing=f"{parameters.spacing_m:.4f}",
                    last=parameters.count,
                    ratio=f"{parameters.amplitude_ratio:.2f}",
                    reference=f"{parameters.feed.reference_length_m:.4f}",
                    increment=f"{parameters.feed.line_increment_m:.4f}",
                    velocity=f"{parameters.feed.velocity_factor:.3f}",
                    loss=f"{parameters.feed.splitter_loss_db:.2f}",
                    folded_note=folded_note,
                    mast_note=mast_note,
                )
        else:
            construction_note = _note(
                tr,
                "Build {count} identical Yagis on one vertical stack with {spacing} m "
                "between level booms. Level 1 is the primary feed; drive levels 2 to "
                "{last} as ideal sources with a {phase}° phase step and {ratio} relative "
                "amplitude. Fit each level as a complete Yagi from the base element "
                "table. {folded_note} The power splitter, phase lines, splitter loss, "
                "and per-level matching are not modeled. {mast_note} Verify the "
                "combined pattern and match.",
                count=parameters.count,
                spacing=f"{parameters.spacing_m:.4f}",
                last=parameters.count,
                phase=f"{parameters.effective_phase_step_deg:.1f}",
                ratio=f"{parameters.amplitude_ratio:.2f}",
                folded_note=folded_note,
                mast_note=mast_note,
            )
        feed_rows += match_row
    elif isinstance(parameters, YagiParameters):
        positions = [element.position_m for element in parameters.elements]
        folded_row = ""
        folded_note = ""
        transformer_row = ""
        if parameters.driven_folded:
            folded_row = f"""
<tr><th>Folded driven element</th><td>{_escape(tr("yes"))}</td></tr>
<tr><th>Fold spacing</th><td>{_length(parameters.driven_fold_spacing_m, display_units)}</td></tr>
"""
            transformer_row = (
                f"<tr><th>Feed transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>"
            )
            folded_note = tr(
                " The driven element is folded with {spacing:.4f} m spacing and "
                "two end connectors. Feed one conductor at its center; the second "
                "conductor remains passive.",
                spacing=parameters.driven_fold_spacing_m,
            )
            if parameters.transformer_ratio != 1.0:
                folded_note += tr(
                    " Feed the folded element through a {ratio}:1 transformer.",
                    ratio=f"{parameters.transformer_ratio:g}",
                )
        match_row = ""
        match_note = ""
        if parameters.match_type.value == "beta_hairpin":
            match_row = f"""
<tr><th>Feed match</th><td>{_escape(tr("beta / hairpin"))}</td></tr>
<tr><th>Hairpin length</th><td>{_length(parameters.match_length_m, display_units)}</td></tr>
<tr><th>Hairpin spacing</th><td>{_length(parameters.match_spacing_m, display_units)}</td></tr>
"""
            match_note = tr(
                " A beta/hairpin stub is connected across the {spacing:.4f} m "
                "driven-element gap and shorted {length:.4f} m along the boom.",
                spacing=parameters.match_spacing_m,
                length=parameters.match_length_m,
            )
        feed_rows = f"""
<tr><th>Elements</th><td>{len(parameters.elements)}</td></tr>
<tr><th>Boom length</th><td>{_length(max(positions) - min(positions), display_units)}</td></tr>
<tr><th>Driven element</th><td>{parameters.driven_index + 1}</td></tr>
{folded_row}
{transformer_row}
{match_row}
<tr><th>Height</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Vertical section</th><td>{_length(parameters.vertical_height_m, display_units)}</td></tr>
<tr><th>Horizontal top run</th><td>{_length(parameters.horizontal_length_m, display_units)}</td></tr>
<tr><th>Base height</th><td>{_length(parameters.base_height_m, display_units)}</td></tr>
<tr><th>Top height</th><td>{_length(parameters.top_height_m, display_units)}</td></tr>
<tr><th>Total wire length</th><td>{_length(parameters.total_length_m, display_units)}</td></tr>
<tr><th>Azimuth</th><td>{parameters.azimuth_deg:.1f}°</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Leg length</th><td>{_length(parameters.leg_length_m, display_units)}</td></tr>
<tr><th>Apex height</th><td>{_length(parameters.apex_height_m, display_units)}</td></tr>
<tr><th>End height</th><td>{_length(parameters.end_height_m, display_units)}</td></tr>
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
<tr><th>Top hat radius</th><td>{_length(parameters.top_hat_radius_m, display_units)}</td></tr>
"""
            top_hat_note = tr(
                " Add {count} horizontal top-hat wires of {radius:.4f} m at the radiator top.",
                count=parameters.top_hat_wire_count,
                radius=parameters.top_hat_radius_m,
            )
        radial_droop_rows = ""
        radial_droop_note = ""
        if parameters.radial_count > 0:
            radial_droop_rows = f"""
<tr><th>Radial droop</th><td>{parameters.radial_droop_deg:.1f}°</td></tr>
<tr><th>Radial tip height</th><td>{_length(parameters.radial_tip_height_m, display_units)}</td></tr>
"""
            if parameters.radial_droop_deg > 0.0:
                radial_droop_note = tr(
                    " Slope them {droop}° downward; the tips are {tip} m above ground.",
                    droop=f"{parameters.radial_droop_deg:.1f}",
                    tip=f"{parameters.radial_tip_height_m:.4f}",
                )
            else:
                radial_droop_note = tr(" Keep them horizontal at the base plane.")
        feed_rows = f"""
<tr><th>Radiator length</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Base height</th><td>{_length(parameters.base_height_m, display_units)}</td></tr>
<tr><th>Radials</th><td>{parameters.radial_count}</td></tr>
<tr><th>Radial length</th><td>{_length(parameters.radial_length_m, display_units)}</td></tr>
{radial_droop_rows}
{top_hat_rows}
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
        construction_note = _note(
            tr,
            "Install a {length} m vertical radiator with its base {base} m above "
            "ground. Add {radials} radials of {radial_length} m.{radial_droop_note}"
            "{top_hat_note}",
            length=f"{parameters.height_m:.4f}",
            base=f"{parameters.base_height_m:.4f}",
            radials=parameters.radial_count,
            radial_length=f"{parameters.radial_length_m:.4f}",
            radial_droop_note=radial_droop_note,
            top_hat_note=top_hat_note,
        )
    elif isinstance(parameters, OCFDParameters):
        other_leg_m = max(feed_wire.length_m - feed_offset_m, 0.0)
        feed_rows = f"""
<tr><th>Feed offset from start</th><td>{_length(feed_offset_m, display_units)}</td></tr>
<tr><th>Remaining leg</th><td>{_length(other_leg_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Loop diameter</th><td>{_length(parameters.diameter_m, display_units)}</td></tr>
<tr><th>Loop circumference</th><td>{_length(parameters.circumference_m, display_units)}</td></tr>
<tr><th>Metal conductor length</th><td>{_length(parameters.loop_conductor_length_m, display_units)}</td></tr>
<tr><th>Polygon sides</th><td>{parameters.sides}</td></tr>
<tr><th>Tuning gap</th><td>{_length(parameters.gap_length_m, display_units)}</td></tr>
<tr><th>Tuning capacitance</th><td>{parameters.tuning_capacitance_f * 1e12:.3f} pF</td></tr>
<tr><th>Capacitor ESR</th><td>{parameters.capacitor_esr_ohm:.3f} Ω</td></tr>
<tr><th>Bottom height</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Top height</th><td>{_length(parameters.top_height_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
            f"<tr><th>Plane height</th><td>{_length(parameters.height_m, display_units)}</td></tr>"
            if horizontal
            else f"<tr><th>Base height</th><td>{_length(parameters.height_m, display_units)}</td></tr>"
        )
        feed_rows = f"""
<tr><th>Orientation</th><td>{_escape(tr(parameters.orientation.value))}</td></tr>
<tr><th>Side length</th><td>{_length(parameters.side_length_m, display_units)}</td></tr>
{height_row}
<tr><th>Feed side</th><td>{_escape(antenna.feed.wire_id)}</td></tr>
<tr><th>Feed location</th><td>{_escape(tr("midpoint of the first side"))}</td></tr>
<tr><th>Feed transformer</th><td>{parameters.transformer_ratio:g}:1</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
        plane = tr("horizontal" if horizontal else "vertical")
        if parameters.transformer_ratio == 1.0:
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
        else:
            construction_note = _note(
                tr,
                "Cut one conductor to {circumference} m and close it into {sides} "
                "equal sides of {side} m in a {plane} plane. Feed the midpoint of the "
                "first side through a {ratio}:1 transformer.",
                circumference=f"{parameters.circumference_m:.4f}",
                sides=parameters.sides,
                side=f"{parameters.side_length_m:.4f}",
                plane=plane,
                ratio=f"{parameters.transformer_ratio:g}",
            )
    elif isinstance(parameters, TransmissionLineDoubletParameters):
        feed_rows = f"""
<tr><th>Type</th><td>{_escape(tr(parameters.template_name))}</td></tr>
<tr><th>Dipole length</th><td>{_length(parameters.dipole_total_length_m, display_units)}</td></tr>
<tr><th>Height</th><td>{_length(parameters.height_m, display_units)}</td></tr>
<tr><th>Matching line</th><td>{parameters.line_impedance_ohm:g} Ω, {_length(parameters.line_length_m, display_units)}, vf={parameters.line_velocity_factor:.3f}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Radiator length</th><td>{_length(parameters.radiator_length_m, display_units)}</td></tr>
<tr><th>Matching section</th><td>{_length(parameters.matching_section_length_m, display_units)}</td></tr>
<tr><th>Conductor spacing</th><td>{_length(parameters.spacing_m, display_units)}</td></tr>
<tr><th>Estimated stub impedance</th><td>{impedance:.1f} Ω</td></tr>
<tr><th>Base height</th><td>{_length(parameters.base_height_m, display_units)}</td></tr>
<tr><th>Radiator height</th><td>{_length(parameters.base_height_m + parameters.matching_section_length_m, display_units)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
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
<tr><th>Radiator length</th><td>{_length(radiator.length_m, display_units)}</td></tr>
<tr><th>Matching stub length</th><td>{_length(matching_feed.length_m, display_units)}</td></tr>
<tr><th>Conductor spacing</th><td>{_length(spacing_m, display_units)}</td></tr>
<tr><th>Estimated stub impedance</th><td>{impedance_ohm:.1f} Ω</td></tr>
<tr><th>Feed/base height</th><td>{_length(feed_height_m, display_units)}</td></tr>
<tr><th>Radiator height</th><td>{_length(radiator.start.z_m, display_units)}</td></tr>
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
<tr><th>Total conductor</th><td>{_length(total_conductor_m, display_units)}</td></tr>
<tr><th>Feed wire</th><td>{_escape(antenna.feed.wire_id)}</td></tr>
<tr><th>Feed height above ground</th><td>{_length(feed_height_m, display_units)}</td></tr>
"""
            construction_note = _note(
                tr,
                "Custom geometry: use the wire table and feed point above. "
                "Verify every connection and the feed gap before construction.",
            )
    else:
        raise TypeError(f"unsupported antenna parameters: {type(parameters)!r}")

    balance_note = ""
    if requires_current_balun(parameters):
        balance_note = _note(
            tr,
            (
                "Balanced antenna: a current balun/choke is recorded in the "
                "project. Common-mode choking is not modeled."
                if project.current_balun
                else "Balanced antenna: install a current balun/choke at the "
                "feed. Common-mode choking is not modeled."
            ),
        )

    bandwidth_row = ""
    if result is not None and len(result.frequencies) >= 2:
        swr_points = [
            (item.frequency_hz, item.swr)
            for item in result.frequencies
            if item.swr is not None and math.isfinite(item.swr)
        ]
        if len(swr_points) >= 2:
            bandwidth = measure_swr_bandwidth(
                [point[0] for point in swr_points],
                [point[1] for point in swr_points],
                center_hz=parameters.frequency_hz,
                swr_limit=2.0,
            )
            if bandwidth.bandwidth_hz is not None:
                bandwidth_value = f"{bandwidth.bandwidth_hz / 1e3:.1f} kHz"
            elif bandwidth.lower_hz is not None and bandwidth.upper_hz is not None:
                bandwidth_value = tr("unbracketed (sweep edge)")
            else:
                bandwidth_value = ""
            if bandwidth_value:
                bandwidth_row = (
                    f"<tr><th>{_escape(tr('SWR ≤ 2 bandwidth'))}</th>"
                    f"<td>{_escape(bandwidth_value)}</td></tr>"
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

    feed_connection_svg = feed_schematic_svg(feed_detail, tr)
    connection_rows = "".join(
        "<tr>"
        f"<td>{_escape(tr(connection.source))}</td>"
        f"<td>{_escape(tr(connection.target))}</td>"
        f"<td>{_escape(tr(connection.note) if connection.note else '')}</td>"
        "</tr>"
        for connection in feed_detail.connections
    )
    state_blocks = []
    for title, values in (
        ("Modeled", feed_detail.modeled),
        ("Recorded", feed_detail.recorded),
        ("Recommended", feed_detail.recommended),
        ("Not modeled", feed_detail.not_modeled),
    ):
        items = "".join(f"<li>{_escape(tr(value))}</li>" for value in values) or "<li>—</li>"
        state_blocks.append(f"<h3>{_escape(tr(title))}</h3><ul>{items}</ul>")
    hardware_block = (
        f"<p><strong>{_escape(tr('Matching hardware'))}:</strong> "
        f"{_escape(tr(feed_detail.match_hardware))}</p>"
        if feed_detail.match_hardware
        else ""
    )
    feed_connection_section = f"""
<h2>{_escape(tr("Feed connection"))}</h2>
<div class="feed-schematic">{feed_connection_svg}</div>
<p>{_escape(tr(feed_detail.summary))}</p>
<h3>{_escape(tr("Connection table"))}</h3>
<table>
<thead><tr><th>{_escape(tr("From"))}</th><th>{_escape(tr("To"))}</th><th>{_escape(tr("Notes"))}</th></tr></thead>
<tbody>{connection_rows}</tbody>
</table>
{"".join(state_blocks)}
{hardware_block}
<h3>{_escape(tr("Assembly steps"))}</h3>
<ol>{"".join(f"<li>{_escape(tr(step))}</li>" for step in feed_detail.steps)}</ol>
<h3>{_escape(tr("Limitations"))}</h3>
<ul>{"".join(f"<li>{_escape(tr(item))}</li>" for item in feed_detail.limitations)}</ul>
"""

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
<p class="muted">{_escape(tr("AntennaDesk construction sheet · SI units (m, MHz, Ω)") if display_units is None else "AntennaDesk construction sheet · " + _units_title(display_units))}</p>
{figure_section}
<h2>Dimensions</h2>
<table>
{dimension_rows}
{feed_rows}
</table>
{as_built_section}
{schedule_section}
{bom_section}
{hardware_section}
{bom_total_section}
{coil_section}
{checklist_section}
{_preflight_section(preflight, tr)}
{evidence_section}
<h2>Simulation</h2>
<table>
{simulation_rows}
</table>

{feed_connection_section}
<h2>Construction notes</h2>
<div class="notes">
{construction_note}
{balance_note}
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
    preflight: PreflightReport | None = None,
    display_units: DisplayUnits | None = None,
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
            preflight=preflight,
            display_units=display_units,
        ),
        encoding="utf-8",
        newline="\n",
    )
