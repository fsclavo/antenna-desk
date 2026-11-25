# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Human-readable design rows shared by reports and construction sheets."""

from __future__ import annotations

from ..domain.antennas.balun import BalunLoss
from ..domain.antennas.beverage import BeverageParameters
from ..domain.antennas.biquad import BiquadParameters
from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ..domain.antennas.discone import DisconeParameters
from ..domain.antennas.endfed import EndFedParameters, EndFedPreset
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.feed_line import FeedLine
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.hexbeam import (
    HexbeamBandSetKind,
    HexbeamParameters,
    hexbeam_band_set_kind,
)
from ..domain.antennas.inverted_l import InvertedLParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.load import LumpedLoad, ParallelLoad
from ..domain.antennas.loaded_dipole import LoadedDipoleParameters
from ..domain.antennas.log_periodic import LogPeriodicParameters
from ..domain.antennas.loop import LoopOrientation, LoopParameters
from ..domain.antennas.magnetic_loop import MagneticLoopParameters
from ..domain.antennas.matching_network import (
    LNetwork,
    MatchingNetwork,
    MatchingNetworkPosition,
    PiNetwork,
    TNetwork,
    TransformerNetwork,
)
from ..domain.antennas.materials import ConductorMaterial
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.phased_vertical import PhasedVerticalParameters
from ..domain.antennas.polarization import Polarization
from ..domain.antennas.quad_beam import QuadBeamParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvParameters
from ..domain.antennas.stacked_yagi import (
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from ..domain.antennas.t2fd import T2FDParameters
from ..domain.antennas.transmission_line import TransmissionLine
from ..domain.antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.trap_yagi import TrapYagiParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zepp import ZeppParameters, parallel_wire_impedance_ohm
from ..domain.design.evidence import EVIDENCE
from ..domain.design.matching_resolution import resolve_matching_network
from ..domain.environment.ground import GroundModel
from ..domain.projects.installation import InstallationProfile
from ..domain.projects.project import DesignVariant
from ..presentation.units import DisplayUnits
from .localization import Labeler, identity_labeler

_HEXBEAM_BAND_SET_LABELS: dict[HexbeamBandSetKind, str] = {
    HexbeamBandSetKind.PUBLISHED: "published G3TXQ",
    HexbeamBandSetKind.SCALED: "reference-scaled",
    HexbeamBandSetKind.CUSTOM: "custom",
}


def hexbeam_band_set_label(parameters: HexbeamParameters) -> str:
    """Return the report label for a multi-band HexBeam band set."""

    kind = hexbeam_band_set_kind(parameters)
    return _HEXBEAM_BAND_SET_LABELS.get(kind, "custom")


def _length(
    value_m: float,
    display_units: DisplayUnits | None,
    *,
    decimals: int = 4,
) -> str:
    if display_units is None:
        return f"{value_m:.{decimals}f} m"
    return display_units.format_length(value_m, trim=False)


def ground_text(ground: GroundModel, labeler: Labeler | None = None) -> str:
    tr = labeler or identity_labeler
    kind = tr(ground.kind.value)
    if ground.relative_permittivity is not None and ground.conductivity_s_per_m is not None:
        return tr(
            "{kind} (eps_r={permittivity:g}, sigma={conductivity:g} S/m)",
            kind=kind,
            permittivity=ground.relative_permittivity,
            conductivity=ground.conductivity_s_per_m,
        )
    return kind


def material_text(material: ConductorMaterial, labeler: Labeler | None = None) -> str:
    tr = labeler or identity_labeler
    return tr(
        "{material} ({conductivity:.3g} S/m)",
        material=tr(material.name),
        conductivity=material.conductivity_s_per_m,
    )


def design_provenance_rows(
    design: DesignVariant,
    display_units: DisplayUnits | None = None,
) -> tuple[tuple[str, str], ...]:
    provenance = design.provenance
    if provenance is None:
        return ()
    return (
        ("Dimension source", provenance.method_id),
        ("Estimate confidence", provenance.confidence),
        ("Estimate tolerance", _length(provenance.tolerance_m, display_units)),
        ("Reference sources", ", ".join(provenance.source_ids) or "—"),
    )


def design_evidence_rows(
    design: DesignVariant,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, str], ...]:
    """Return the evidence level, source, tolerance, and limitation."""

    entry_key = design.antenna_type
    if isinstance(design.parameters, EndFedParameters):
        entry_key = {
            EndFedPreset.SHORTENED_80_10: "shortened_endfed_80_10",
            EndFedPreset.SHORTENED_40_10: "shortened_endfed_40_10",
        }.get(design.parameters.preset, "endfed")
    entry = EVIDENCE.get(entry_key)
    if entry is None:
        return ()
    tr = labeler or identity_labeler

    def evidence_text(field: str, text: str) -> str:
        key = f"evidence.{entry.template}.{field}"
        translated = tr(key)
        return text if translated == key else translated

    rows: list[tuple[str, str]] = [
        ("Evidence level", f"{entry.level.value} ({entry.level.name.lower()})"),
        ("Evidence source", evidence_text("source", entry.source)),
        ("Evidence tolerance", evidence_text("tolerance", entry.tolerance)),
        ("Limitation", evidence_text("limitation", entry.limitation)),
    ]
    if isinstance(design.parameters, EndFedParameters) and design.parameters.preset in {
        EndFedPreset.SHORTENED_80_10,
        EndFedPreset.SHORTENED_40_10,
    }:
        if design.parameters.installation_return_active:
            confidence = tr(
                "Absolute SWR is informational. The installation return is a "
                "model proxy, not a physical counterpoise; the real "
                "coax/mast/earth path dominates SWR."
            )
        else:
            confidence = tr(
                "Absolute SWR is informational; the shortened preset is judged by R/X convergence."
            )
        rows.append(("Model confidence", confidence))
    return tuple(rows)


def optimization_summary_rows(design: DesignVariant) -> tuple[tuple[str, str], ...]:
    summary = design.optimization_summary
    if summary is None:
        return ()
    return (
        (
            "Last optimization",
            f"{summary.mode.value} · {summary.objective} · {summary.status}",
        ),
        (
            "Optimization budget",
            f"{summary.budget_profile} · {summary.evaluations} evaluations · seed {summary.seed}",
        ),
        (
            "Optimization completed",
            summary.completed_at.strftime("%Y-%m-%d %H:%M"),
        ),
    )


def _branch_text(
    inductance_h: float,
    capacitance_f: float,
    labeler: Labeler | None = None,
) -> str:
    tr = labeler or identity_labeler
    parts: list[str] = []
    if inductance_h:
        parts.append(tr("{value:g} µH", value=inductance_h * 1e6))
    if capacitance_f:
        parts.append(tr("{value:g} pF", value=capacitance_f * 1e12))
    return " + ".join(parts)


def _design_network_topology_label(network: MatchingNetwork) -> str:
    if isinstance(network, PiNetwork):
        return "Pi network (primary side)"
    if isinstance(network, TNetwork):
        return "T network (primary side)"
    return "L network (primary side)"


def _design_network_component_rows(
    network: MatchingNetwork,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, str], ...]:
    if isinstance(network, PiNetwork):
        return (
            (
                "Input shunt",
                _branch_text(
                    network.input_shunt_inductance_h,
                    network.input_shunt_capacitance_f,
                    labeler,
                ),
            ),
            (
                "Design series",
                _branch_text(
                    network.series_inductance_h,
                    network.series_capacitance_f,
                    labeler,
                ),
            ),
            (
                "Output shunt",
                _branch_text(
                    network.output_shunt_inductance_h,
                    network.output_shunt_capacitance_f,
                    labeler,
                ),
            ),
        )
    if isinstance(network, TNetwork):
        return (
            (
                "Input series",
                _branch_text(
                    network.input_series_inductance_h,
                    network.input_series_capacitance_f,
                    labeler,
                ),
            ),
            (
                "Design shunt",
                _branch_text(
                    network.shunt_inductance_h,
                    network.shunt_capacitance_f,
                    labeler,
                ),
            ),
            (
                "Output series",
                _branch_text(
                    network.output_series_inductance_h,
                    network.output_series_capacitance_f,
                    labeler,
                ),
            ),
        )
    if not isinstance(network, LNetwork):
        raise TypeError(f"unsupported design matching network: {type(network)!r}")
    return (
        (
            "Design series",
            _branch_text(
                network.series_inductance_h,
                network.series_capacitance_f,
                labeler,
            ),
        ),
        (
            "Design shunt",
            _branch_text(
                network.shunt_inductance_h,
                network.shunt_capacitance_f,
                labeler,
            ),
        ),
    )


def matching_network_description(
    network: MatchingNetwork,
    labeler: Labeler | None = None,
) -> str:
    """Return a compact, topology-specific description of a matching network."""

    tr = labeler or identity_labeler
    if isinstance(network, LNetwork):
        shunt_side = tr("input") if network.shunt_at_input else tr("output")
        description = tr(
            "L network (series {series}, {side} shunt {shunt})",
            series=_branch_text(network.series_inductance_h, network.series_capacitance_f, tr),
            side=shunt_side,
            shunt=_branch_text(network.shunt_inductance_h, network.shunt_capacitance_f, tr),
        )
    elif isinstance(network, PiNetwork):
        description = tr(
            "Pi network (input shunt {input_shunt}, series {series}, output shunt {output_shunt})",
            input_shunt=_branch_text(
                network.input_shunt_inductance_h,
                network.input_shunt_capacitance_f,
                tr,
            ),
            series=_branch_text(network.series_inductance_h, network.series_capacitance_f, tr),
            output_shunt=_branch_text(
                network.output_shunt_inductance_h,
                network.output_shunt_capacitance_f,
                tr,
            ),
        )
    elif isinstance(network, TNetwork):
        description = tr(
            "T network (input series {input_series}, shunt {shunt}, output series {output_series})",
            input_series=_branch_text(
                network.input_series_inductance_h,
                network.input_series_capacitance_f,
                tr,
            ),
            shunt=_branch_text(network.shunt_inductance_h, network.shunt_capacitance_f, tr),
            output_series=_branch_text(
                network.output_series_inductance_h,
                network.output_series_capacitance_f,
                tr,
            ),
        )
    elif isinstance(network, TransformerNetwork):
        description = tr(
            "Measured transformer (series {series}, input shunt {input_shunt})",
            series=_branch_text(network.series_inductance_h, 0.0, tr),
            input_shunt=_branch_text(
                network.input_shunt_inductance_h,
                network.input_shunt_capacitance_f,
                tr,
            ),
        )
    else:
        raise TypeError(f"unsupported matching network: {type(network)!r}")
    q_factor = getattr(network, "q_factor", None)
    if q_factor:
        description += tr(", Q {q:g}", q=q_factor)
    return description


def installation_profile_rows(
    profile: InstallationProfile | None,
    labeler: Labeler | None = None,
    *,
    display_units: DisplayUnits | None = None,
) -> tuple[tuple[str, str], ...]:
    """Return the active installation profile as report rows."""

    if profile is None:
        return ()
    tr = labeler or identity_labeler
    height = (
        _length(profile.available_height_m, display_units, decimals=3)
        if profile.available_height_m is not None
        else "—"
    )
    width = (
        _length(profile.available_width_m, display_units, decimals=3)
        if profile.available_width_m is not None
        else "—"
    )
    rows: list[tuple[str, str]] = [
        ("Installation profile", profile.name),
        ("Available height", height),
        ("Available space", width),
        ("Installation orientation", f"{profile.orientation_deg:.0f}°"),
        ("Support", tr(profile.support.value)),
        ("Profile ground", ground_text(profile.ground, tr) if profile.ground else "—"),
    ]
    if profile.notes.strip():
        rows.append(("Profile notes", profile.notes.strip()))
    return tuple(rows)


def feed_matching_rows(
    project_network: MatchingNetwork | None,
    feed_line: FeedLine | None,
    balun_loss: BalunLoss | None,
    labeler: Labeler | None = None,
    position: MatchingNetworkPosition = MatchingNetworkPosition.FEEDPOINT,
    *,
    current_balun: bool = False,
    display_units: DisplayUnits | None = None,
) -> tuple[tuple[str, str], ...]:
    """Return project-level feed and matching rows for a report."""

    tr = labeler or identity_labeler
    rows: list[tuple[str, str]] = []
    if project_network is not None:
        state = tr("active") if project_network.is_active else tr("inactive")
        position_text = (
            tr("in shack") if position is MatchingNetworkPosition.SHACK else tr("at feedpoint")
        )
        rows.append(
            (
                "Project matching",
                tr(
                    "{network} · {state} · {position}",
                    network=matching_network_description(project_network, tr),
                    state=state,
                    position=position_text,
                ),
            )
        )
    if feed_line is not None and feed_line.is_active:
        rows.append(
            (
                "Feed line",
                tr(
                    "{impedance:g} Ω, {length}, velocity factor {velocity:g}",
                    impedance=feed_line.characteristic_impedance_ohm,
                    length=_length(feed_line.length_m, display_units),
                    velocity=feed_line.velocity_factor,
                ),
            )
        )
    if balun_loss is not None and balun_loss.is_active:
        rows.append(
            (
                "Balun/unun loss",
                tr(
                    "{loss:.3f} dB at {frequency:.6f} MHz (exponent {exponent:g})",
                    loss=balun_loss.reference_loss_db,
                    frequency=balun_loss.reference_frequency_hz / 1e6,
                    exponent=balun_loss.exponent,
                ),
            )
        )
    if current_balun:
        rows.append(
            (
                "Current balun",
                "recorded; common-mode choking is not modeled",
            )
        )
    return tuple(rows)


def design_summary_rows(
    parameters: AntennaDesignParameters,
    labeler: Labeler | None = None,
    *,
    project_network: MatchingNetwork | None = None,
    display_units: DisplayUnits | None = None,
) -> tuple[tuple[str, str], ...]:
    tr = labeler or identity_labeler
    rows: list[tuple[str, str]] = [
        ("Frequency", f"{parameters.frequency_hz / 1e6:.6f} MHz"),
    ]
    if isinstance(parameters, CustomAntennaParameters):
        heights = [point.z_m for wire in parameters.wires for point in (wire.start, wire.end)]
        materials = ", ".join(sorted({wire.material.name for wire in parameters.wires}))
        rows.extend(
            [
                ("Type", "custom wires"),
                ("Generator", parameters.generator_name or "custom"),
                ("Wires", str(len(parameters.wires))),
                (
                    "Total conductor",
                    _length(sum(wire.length_m for wire in parameters.wires), display_units),
                ),
                ("Min height", _length(min(heights), display_units)),
                ("Max height", _length(max(heights), display_units)),
                ("Materials", materials),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, DipoleParameters):
        height_label = (
            "Base height" if parameters.orientation is DipoleOrientation.VERTICAL else "Wire height"
        )
        rows.extend(
            [
                ("Type", "wire dipole"),
                ("Orientation", parameters.orientation.value),
                ("Total wire length", _length(parameters.total_length_m, display_units)),
                (height_label, _length(parameters.height_m, display_units)),
                (
                    "Azimuth",
                    f"{parameters.azimuth_deg:.1f}°"
                    if parameters.orientation is DipoleOrientation.HORIZONTAL
                    else "—",
                ),
            ]
        )
        if parameters.sag_m > 0.0:
            rows.extend(
                [
                    ("Sag", _length(parameters.sag_m, display_units)),
                    (
                        "Conductor length",
                        _length(parameters.conductor_length_m, display_units),
                    ),
                ]
            )
    elif isinstance(parameters, TrapDipoleParameters):
        height_label = (
            "Base height" if parameters.orientation is DipoleOrientation.VERTICAL else "Wire height"
        )
        left_position, right_position = parameters.trap_positions_m
        rows.extend(
            [
                ("Type", "trap dipole"),
                ("Orientation", parameters.orientation.value),
                ("Low band", f"{parameters.frequency_hz / 1e6:.6f} MHz"),
                ("High band", f"{parameters.high_band_frequency_hz / 1e6:.6f} MHz"),
                ("Total wire length", _length(parameters.total_length_m, display_units)),
                ("Center section", _length(parameters.inner_length_m, display_units)),
                ("Outer section", tr("{length:.4f} m each", length=parameters.outer_length_m)),
                (
                    "Trap positions",
                    tr(
                        "{left:.4f} m, {right:.4f} m from wire start",
                        left=left_position,
                        right=right_position,
                    ),
                ),
                ("Trap frequency", f"{parameters.trap_frequency_hz / 1e6:.6f} MHz"),
                ("Trap inductance", f"{parameters.trap_inductance_h * 1e6:.4f} µH"),
                (
                    "Trap capacitance",
                    f"{parameters.trap_capacitance_f * 1e12:.4f} pF",
                ),
                (height_label, _length(parameters.height_m, display_units)),
                (
                    "Azimuth",
                    f"{parameters.azimuth_deg:.1f}°"
                    if parameters.orientation is DipoleOrientation.HORIZONTAL
                    else "—",
                ),
            ]
        )
    elif isinstance(parameters, T2FDParameters):
        height_label = (
            "Base height" if parameters.orientation is DipoleOrientation.VERTICAL else "Wire height"
        )
        rows.extend(
            [
                ("Type", "terminated folded dipole (T2FD)"),
                ("Orientation", parameters.orientation.value),
                (
                    "Design band",
                    f"{parameters.frequency_hz / 1e6:.6f} MHz to "
                    f"{parameters.highest_frequency_hz / 1e6:.6f} MHz",
                ),
                ("Element length", _length(parameters.length_m, display_units)),
                ("Conductor spacing", _length(parameters.spacing_m, display_units)),
                (
                    "Total conductor length",
                    _length(parameters.total_conductor_length_m, display_units),
                ),
                (
                    "Termination resistor",
                    f"{parameters.termination_resistance_ohm:g} Ω non-inductive",
                ),
                ("Feed transformer", f"{parameters.transformer_ratio:g}:1"),
                (height_label, _length(parameters.height_m, display_units)),
                (
                    "Azimuth",
                    f"{parameters.azimuth_deg:.1f}°"
                    if parameters.orientation is DipoleOrientation.HORIZONTAL
                    else "-",
                ),
            ]
        )
    elif isinstance(parameters, FoldedDipoleParameters):
        rows.extend(
            [
                ("Type", "folded dipole"),
                ("Element length", _length(parameters.total_length_m, display_units)),
                ("Spacing", _length(parameters.spacing_m, display_units)),
                (
                    "Total conductor length",
                    _length(parameters.total_conductor_length_m, display_units),
                ),
                ("Feed transformer", f"{parameters.transformer_ratio:g}:1"),
                ("Height", _length(parameters.height_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
    elif isinstance(parameters, VerticalParameters):
        type_name = "loaded vertical" if parameters.loading_coil_enabled else "vertical"
        if parameters.top_hat_enabled:
            type_name = "top-loaded vertical"
        rows.extend(
            [
                ("Type", type_name),
                ("Radiator length", _length(parameters.height_m, display_units)),
                ("Base height", _length(parameters.base_height_m, display_units)),
                ("Top height", _length(parameters.top_height_m, display_units)),
                ("Radials", str(parameters.radial_count)),
                ("Radial length", _length(parameters.radial_length_m, display_units)),
            ]
        )
        if parameters.radial_count > 0:
            rows.extend(
                [
                    ("Radial droop", f"{parameters.radial_droop_deg:.1f}°"),
                    (
                        "Radial tip height",
                        _length(parameters.radial_tip_height_m, display_units),
                    ),
                ]
            )
        if parameters.loading_coil_enabled:
            rows.append(
                (
                    "Loading coil",
                    f"{parameters.loading_coil_inductance_h * 1e6:.4f} µH at "
                    f"{parameters.loading_coil_offset_m:.4f} m; "
                    f"R={parameters.loading_coil_resistance_ohm:g} Ω",
                )
            )
        if parameters.top_hat_enabled:
            rows.extend(
                [
                    ("Top hat wires", str(parameters.top_hat_wire_count)),
                    ("Top hat radius", _length(parameters.top_hat_radius_m, display_units)),
                ]
            )
    elif isinstance(parameters, InvertedLParameters):
        rows.extend(
            [
                ("Type", "inverted L"),
                ("Vertical length", _length(parameters.vertical_height_m, display_units)),
                ("Horizontal length", _length(parameters.horizontal_length_m, display_units)),
                ("Total wire length", _length(parameters.total_length_m, display_units)),
                ("Base height", _length(parameters.base_height_m, display_units)),
                ("Top height", _length(parameters.top_height_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
    elif isinstance(parameters, InvertedVParameters):
        rows.extend(
            [
                ("Type", "inverted-V"),
                ("Leg length", _length(parameters.leg_length_m, display_units)),
                ("Apex height", _length(parameters.apex_height_m, display_units)),
                ("End height", _length(parameters.end_height_m, display_units)),
                ("Included angle", f"{parameters.included_angle_deg:.1f}°"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
    elif isinstance(parameters, OCFDParameters):
        rows.extend(
            [
                ("Type", "off-center-fed dipole"),
                ("Total wire length", _length(parameters.total_length_m, display_units)),
                (
                    "Feed offset",
                    f"{parameters.feed_offset_m:.4f} m ({parameters.feed_ratio * 100:.1f}%)",
                ),
                ("Height", _length(parameters.height_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
    elif isinstance(parameters, MagneticLoopParameters):
        rows.extend(
            [
                ("Type", "magnetic loop"),
                ("Diameter", _length(parameters.diameter_m, display_units)),
                ("Circumference", _length(parameters.circumference_m, display_units)),
                ("Loop conductor", _length(parameters.loop_conductor_length_m, display_units)),
                ("Sides", str(parameters.sides)),
                ("Bottom height", _length(parameters.height_m, display_units)),
                ("Top height", _length(parameters.top_height_m, display_units)),
                ("Tuning gap", _length(parameters.gap_length_m, display_units)),
                ("Tuning capacitance", f"{parameters.tuning_capacitance_f * 1e12:.3f} pF"),
                ("Capacitor ESR", f"{parameters.capacitor_esr_ohm:.3f} Ω"),
                ("Capacitor reactance", f"{parameters.capacitor_reactance_ohm:.2f} Ω"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
    elif isinstance(parameters, LoopParameters):
        rows.extend(
            [
                ("Type", "loop"),
                ("Orientation", parameters.orientation.value),
                ("Circumference", _length(parameters.circumference_m, display_units)),
                ("Sides", str(parameters.sides)),
                ("Equivalent diameter", _length(parameters.diameter_m, display_units)),
                ("Feed transformer", f"{parameters.transformer_ratio:g}:1"),
            ]
        )
        if parameters.orientation is LoopOrientation.HORIZONTAL:
            rows.append(("Height", _length(parameters.height_m, display_units)))
        else:
            rows.extend(
                [
                    ("Bottom height", _length(parameters.height_m, display_units)),
                    ("Top height", _length(parameters.top_height_m, display_units)),
                ]
            )
        rows.append(("Azimuth", f"{parameters.azimuth_deg:.1f}°"))
    if isinstance(parameters, TransmissionLineDoubletParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Dipole length", _length(parameters.dipole_total_length_m, display_units)),
                ("Height", _length(parameters.height_m, display_units)),
                ("Feed height", _length(parameters.feed_height_m, display_units)),
                (
                    "Matching line",
                    f"{parameters.line_impedance_ohm:g} Ω, "
                    f"{parameters.line_length_m:.4f} m, "
                    f"vf={parameters.line_velocity_factor:.3f}",
                ),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, ZeppParameters):
        impedance = parallel_wire_impedance_ohm(
            parameters.spacing_m,
            parameters.wire_radius_m,
        )
        rows.extend(
            [
                ("Type", "Zepp"),
                ("Radiator length", _length(parameters.radiator_length_m, display_units)),
                ("Matching section", _length(parameters.matching_section_length_m, display_units)),
                ("Spacing", _length(parameters.spacing_m, display_units)),
                ("Base height", _length(parameters.base_height_m, display_units)),
                (
                    "Radiator height",
                    _length(
                        parameters.base_height_m + parameters.matching_section_length_m,
                        display_units,
                    ),
                ),
                ("Estimated stub impedance", f"{impedance:.1f} Ω"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, ScvParameters):
        rows.extend(
            [
                ("Type", parameters.template_name.lower()),
                ("Horizontal length", _length(parameters.horizontal_length_m, display_units)),
                ("Vertical length", _length(parameters.vertical_height_m, display_units)),
                ("Vertical elements", str(parameters.vertical_count)),
                (
                    "Horizontal segment",
                    tr(
                        "{length:.4f} m each",
                        length=parameters.horizontal_segment_m,
                    ),
                ),
                ("Base height", _length(parameters.base_height_m, display_units)),
                ("Top height", _length(parameters.top_height_m, display_units)),
                (
                    "Feed offset below top",
                    _length(parameters.feed_offset_m, display_units),
                ),
                ("Total conductor", _length(parameters.total_conductor_length_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, LoadedDipoleParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Active length", _length(parameters.active_length_m, display_units)),
                ("Full length", _length(parameters.total_length_m, display_units)),
                ("Link offset", _length(parameters.link_offset_m, display_units)),
                (
                    "State",
                    "links open"
                    if parameters.link_open
                    else (
                        f"loaded, {parameters.loading_coil_inductance_h * 1e6:.3f} µH"
                        if parameters.coil_active
                        else "no loading coils"
                    ),
                ),
                (
                    "Coil Q",
                    "—" if parameters.coil_q is None else f"{parameters.coil_q:.1f}",
                ),
                ("Height", _length(parameters.height_m, display_units)),
                ("Orientation", parameters.orientation.value),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, HexbeamParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Driver half-length", _length(parameters.driver_half_length_m, display_units)),
                (
                    "Reflector half-length",
                    _length(parameters.reflector_half_length_m, display_units),
                ),
                ("Turning radius", _length(parameters.turning_radius_m, display_units)),
                ("Tip gap", _length(parameters.tip_gap_m, display_units)),
                ("Overall span", _length(parameters.overall_span_m, display_units)),
                ("Height", _length(parameters.height_m, display_units)),
                ("Feed", "center of the M driver"),
                ("Total conductor", _length(parameters.total_conductor_length_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        if len(parameters.bands) > 1:
            rows.append(("Band set", hexbeam_band_set_label(parameters)))
            rows.append(("Bands", str(len(parameters.bands))))
            rows.append(
                (
                    "Feed model",
                    "one driven band; other bands passive; coax harness and balun not modeled",
                )
            )
            for band in parameters.bands:
                rows.append(
                    (
                        "Band",
                        f"{band.label}: driver {_length(band.driver_half_length_m, display_units)}"
                        f" · reflector {_length(band.reflector_half_length_m, display_units)}"
                        f" · tip gap {_length(band.tip_gap_m, display_units)}"
                        f" · offset {_length(band.vertical_offset_m, display_units)}",
                    )
                )
        return tuple(rows)
    if isinstance(parameters, TrapYagiParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Elements", str(parameters.element_count)),
                ("Driven element", _length(parameters.driven_length_m, display_units)),
                ("Reflector element", _length(parameters.reflector_length_m, display_units)),
                ("Reflector spacing", _length(parameters.reflector_spacing_m, display_units)),
                ("Boom length", _length(parameters.boom_length_m, display_units)),
                ("Trap inset", _length(parameters.trap_inset_m, display_units)),
                ("Trap frequency", f"{parameters.trap_frequency_hz / 1e6:.3f} MHz"),
                (
                    "Trap inductance",
                    f"{parameters.trap_inductance_h * 1e6:.3f} µH",
                ),
                ("Height", _length(parameters.height_m, display_units)),
                ("Feed", "driven element center"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        if parameters.element_count == 3:
            rows.insert(
                4, ("Director element", _length(parameters.director_length_m, display_units))
            )
            rows.insert(
                6, ("Director spacing", _length(parameters.director_spacing_m, display_units))
            )
        return tuple(rows)
    if isinstance(parameters, DisconeParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Radial wires", str(parameters.wire_count)),
                ("Cone height", _length(parameters.cone_height_m, display_units)),
                ("Cone base radius", _length(parameters.cone_radius_m, display_units)),
                ("Disc radius", _length(parameters.disc_radius_m, display_units)),
                ("Base height", _length(parameters.base_height_m, display_units)),
                ("Feed gap", _length(parameters.disc_gap_m, display_units)),
                ("Top height", _length(parameters.top_height_m, display_units)),
                ("Feed", "across the apex gap"),
                ("Total conductor", _length(parameters.total_conductor_length_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, LogPeriodicParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Elements", str(parameters.element_count)),
                (
                    "Band",
                    f"{parameters.frequency_low_hz / 1e6:.3f}-"
                    f"{parameters.frequency_high_hz / 1e6:.3f} MHz",
                ),
                ("Longest element", _length(parameters.longest_element_length_m, display_units)),
                ("Shortest element", _length(parameters.shortest_element_length_m, display_units)),
                ("Tau", f"{parameters.tau:.4f}"),
                ("Sigma", f"{parameters.sigma:.4f}"),
                ("Boom length", _length(parameters.boom_length_m, display_units)),
                ("Phase line Z0", f"{parameters.phase_line_impedance_ohm:.1f} Ω"),
                (
                    "Phase line velocity factor",
                    f"{parameters.phase_line_velocity_factor:.3f}",
                ),
                ("Feed transformer", f"{parameters.feed_transformer_ratio:.1f}:1"),
                ("Height", _length(parameters.height_m, display_units)),
                ("Feed", "front element center"),
                ("Total conductor", _length(parameters.total_conductor_length_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, QuadBeamParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Loops", str(parameters.element_count)),
                ("Driven loop side", _length(parameters.loop_side_m, display_units)),
                ("Reflector side", _length(parameters.reflector_side_m, display_units)),
                ("Reflector spacing", _length(parameters.reflector_spacing_m, display_units)),
                ("Boom length", _length(parameters.boom_length_m, display_units)),
                ("Height", _length(parameters.height_m, display_units)),
                ("Feed", "driven loop side midpoint"),
                ("Polarization", "horizontal"),
                ("Total conductor", _length(parameters.total_conductor_length_m, display_units)),
                ("Feed transformer", f"{parameters.transformer_ratio:g}:1"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        if parameters.element_count == 3:
            rows.insert(
                4,
                ("Director side", _length(parameters.director_side_m, display_units)),
            )
            rows.insert(
                5,
                ("Director spacing", _length(parameters.director_spacing_m, display_units)),
            )
        return tuple(rows)
    if isinstance(parameters, PhasedVerticalParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Verticals", str(parameters.element_count)),
                ("Element spacing", _length(parameters.spacing_m, display_units)),
                ("Vertical element length", _length(parameters.height_m, display_units)),
                ("Base height", _length(parameters.base_height_m, display_units)),
                ("Phase step", f"{parameters.phase_step_deg:.1f}°"),
                ("Amplitude taper", f"{parameters.amplitude_taper * 100.0:.0f}%"),
                ("Radials per element", str(parameters.radial_count)),
                ("Radial length", _length(parameters.radial_length_m, display_units)),
                ("Total conductor", _length(parameters.total_conductor_length_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Feed", "first vertical (primary)"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, BeverageParameters):
        rows.extend(
            [
                ("Type", "Beverage"),
                ("Length", _length(parameters.length_m, display_units)),
                ("Height", _length(parameters.height_m, display_units)),
                (
                    "Termination",
                    (
                        tr(
                            "{resistance:.1f} Ω to ground",
                            resistance=parameters.termination_resistance_ohm,
                        )
                        if parameters.termination_enabled
                        else "disabled"
                    ),
                ),
                ("Feed", "near end, ground-referenced stub"),
                ("Feed transformer", f"{parameters.transformer_ratio:.1f}:1"),
                ("Total conductor", _length(parameters.total_conductor_length_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, BiquadParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Loops", str(parameters.loop_count)),
                ("Loop side", _length(parameters.loop_side_m, display_units)),
                ("Stack height", _length(parameters.total_height_m, display_units)),
                ("Base height", _length(parameters.base_height_m, display_units)),
                ("Top height", _length(parameters.top_height_m, display_units)),
                ("Feed height", _length(parameters.feed_height_m, display_units)),
                (
                    "Reflector",
                    (
                        tr(
                            "{spacing:.4f} m behind",
                            spacing=parameters.reflector_spacing_m,
                        )
                        if parameters.reflector_enabled
                        else "disabled"
                    ),
                ),
                ("Total conductor", _length(parameters.total_conductor_length_m, display_units)),
                ("Feed transformer", f"{parameters.transformer_ratio:g}:1"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, RingoParameters):
        rows.extend(
            [
                ("Type", "Ringo"),
                ("Radiator length", _length(parameters.radiator_height_m, display_units)),
                ("Ring diameter", _length(parameters.ring_diameter_m, display_units)),
                ("Ring height", _length(parameters.ring_height_m, display_units)),
                ("Ring sides", str(parameters.ring_sides)),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, JPoleParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Radiator length", _length(parameters.radiator_height_m, display_units)),
                ("Stub length", _length(parameters.stub_length_m, display_units)),
                ("Stub spacing", _length(parameters.spacing_m, display_units)),
                ("Feed offset", _length(parameters.feed_offset_m, display_units)),
                ("Base height", _length(parameters.base_height_m, display_units)),
                ("Folded", "yes" if parameters.folded else "no"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, EndFedParameters):
        counterpoise = (
            _length(parameters.counterpoise_length_m, display_units)
            if parameters.counterpoise_active
            else "none"
        )
        return_path_label = {
            "auto": "automatic",
            "installation_proxy": "installation proxy",
            "counterpoise": "counterpoise",
            "coax_shield": "coax shield",
        }[parameters.return_path.value]
        transformer_loss_label = {
            "none": "none",
            "squash_practice_49_1": "measured 49:1 (Squash Practice)",
        }[parameters.transformer_loss_model.value]
        choke = "none"
        if parameters.common_mode_choke_active and parameters.common_mode_choke is not None:
            value = parameters.common_mode_choke
            sign = "+" if value.reactance_ohm >= 0.0 else "-"
            choke = (
                f"{value.resistance_ohm:g} {sign} j{abs(value.reactance_ohm):g} Ω "
                f"at {value.measurement_frequency_hz / 1e6:g} MHz"
            )
        type_label = {
            EndFedPreset.STANDARD: "end-fed wire",
            EndFedPreset.SLOPER: "sloper",
            EndFedPreset.RANDOM_WIRE: "random wire",
            EndFedPreset.SHORTENED_80_10: "shortened EFHW 80-10 m",
            EndFedPreset.SHORTENED_40_10: "shortened EFHW 40-20-10 m",
        }[parameters.preset]
        rows.extend(
            [
                ("Type", type_label),
                ("Length", _length(parameters.length_m, display_units)),
                ("Feed section", _length(parameters.feed_section_length_m, display_units)),
                ("Feed height", _length(parameters.feed_height_m, display_units)),
                *(
                    [
                        (
                            "Vertical section",
                            _length(parameters.bend_vertical_length_m, display_units),
                        ),
                        (
                            "Horizontal run",
                            _length(parameters.bend_horizontal_length_m, display_units),
                        ),
                        ("Top height", _length(parameters.bend_top_height_m, display_units)),
                    ]
                    if parameters.bend_active
                    else [("End height", _length(parameters.end_height_m, display_units))]
                ),
                ("Transformer", f"{parameters.transformer_ratio:g}:1"),
                ("Transformer loss", transformer_loss_label),
                ("Return path", return_path_label),
                ("Return length", _length(parameters.effective_return_length_m, display_units)),
                ("Common-mode choke", choke),
                ("Counterpoise", counterpoise),
                (
                    "Installation return",
                    (
                        f"{parameters.installation_return_length_m:.4f} m (coax/mast proxy)"
                        if parameters.installation_return_active
                        else "not used"
                    ),
                ),
                (
                    "Counterpoise height",
                    _length(parameters.effective_return_height_m, display_units),
                ),
                (
                    "Counterpoise azimuth",
                    f"{parameters.effective_counterpoise_azimuth_deg:.1f}°",
                ),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        if parameters.matching_network_active:
            resolution = resolve_matching_network(parameters, project_network)
            if resolution.project_active:
                matching_status = tr("retained; project network overrides")
            elif resolution.design_active:
                matching_status = tr("retained; design network overrides")
            else:
                matching_status = tr("active")
            rows.extend(
                [
                    (
                        "Matching capacitor",
                        tr(
                            "{value:.1f} pF (primary shunt, {status})",
                            value=parameters.matching_capacitance_f * 1e12,
                            status=matching_status,
                        ),
                    ),
                    (
                        "Transformer leakage",
                        tr(
                            "{value:.4f} µH ({status})",
                            value=parameters.transformer_leakage_inductance_h * 1e6,
                            status=matching_status,
                        ),
                    ),
                ]
            )
        if (
            parameters.design_matching_network_active
            and parameters.design_matching_network is not None
        ):
            resolution = resolve_matching_network(parameters, project_network)
            design_status = (
                tr("retained; project network overrides")
                if resolution.project_active
                else tr("active")
            )
            network = parameters.design_matching_network
            rows.append(
                (
                    "Design matching network",
                    tr(_design_network_topology_label(network)),
                )
            )
            for label, branch_value in _design_network_component_rows(network, labeler):
                rows.append(
                    (
                        label,
                        tr(
                            "{value} ({status})",
                            value=branch_value,
                            status=design_status,
                        ),
                    )
                )
        if parameters.coil_active:
            rows.extend(
                [
                    (
                        "Loading coil",
                        f"{parameters.loading_coil_inductance_h * 1e6:.4f} µH",
                    ),
                    (
                        "Coil position",
                        tr(
                            "{offset:.4f} m from feed",
                            offset=parameters.loading_coil_offset_m,
                        ),
                    ),
                    (
                        "Top section",
                        _length(parameters.loading_coil_top_length_m, display_units),
                    ),
                ]
            )
            if parameters.loading_coil_q is not None:
                rows.append(("Coil Q", f"{parameters.loading_coil_q:.1f}"))
        return tuple(rows)
    if isinstance(parameters, FanDipoleParameters):
        rows.extend(
            [
                ("Type", "fan dipole"),
                ("Pairs", str(len(parameters.elements))),
                (
                    "Element lengths",
                    ", ".join(
                        _length(element.length_m, display_units) for element in parameters.elements
                    ),
                ),
                (
                    "Included angles",
                    ", ".join(
                        f"{element.included_angle_deg:.1f}°" for element in parameters.elements
                    ),
                ),
                (
                    "End heights",
                    ", ".join(
                        _length(parameters.element_end_height_m(element), display_units)
                        for element in parameters.elements
                    ),
                ),
                ("Apex height", _length(parameters.apex_height_m, display_units)),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, MoxonParameters):
        rows.extend(
            [
                ("Type", "Moxon rectangle"),
                ("Element width", _length(parameters.width_m, display_units)),
                ("Element spacing", _length(parameters.depth_m, display_units)),
                ("Reflector tip", _length(parameters.reflector_tip_m, display_units)),
                ("Driven tip", _length(parameters.driven_tip_m, display_units)),
                ("Tip gap", _length(parameters.gap_m, display_units)),
                ("Polarization", parameters.polarization.value),
                ("Boom height", _length(parameters.height_m, display_units)),
            ]
        )
        if parameters.polarization is Polarization.VERTICAL:
            rows.append(("Lowest edge", _length(parameters.lowest_edge_m, display_units)))
        rows.extend(
            [
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, StackedYagiParameters):
        yagi = parameters.yagi
        total_conductor = parameters.count * sum(element.length_m for element in yagi.elements)
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Levels", str(parameters.count)),
                ("Level spacing", _length(parameters.spacing_m, display_units)),
                ("Base Yagi elements", str(len(yagi.elements))),
                ("Base boom length", _length(parameters.boom_length_m, display_units)),
                ("Base boom height", _length(yagi.height_m, display_units)),
                ("Top level height", _length(parameters.highest_tip_m, display_units)),
                ("Phase step", f"{parameters.effective_phase_step_deg:.1f}°"),
                ("Additional-level ratio", f"{parameters.amplitude_ratio:.2f}"),
                ("Polarization", yagi.polarization.value),
                (
                    "Feed",
                    (
                        "splitter node (primary input); every level is a network port"
                        if parameters.feed.mode is StackedYagiFeedMode.NETWORK
                        else "level 1 (primary); additional levels are ideal sources"
                    ),
                ),
                (
                    "Feed network",
                    (
                        "co-simulated TL network"
                        if parameters.feed.mode is StackedYagiFeedMode.NETWORK
                        else "splitter + phase lines"
                        if parameters.feed.mode is StackedYagiFeedMode.PHASE_LINES
                        else "ideal phase step"
                    ),
                ),
                *(
                    [
                        (
                            "Reference line",
                            _length(parameters.feed.reference_length_m, display_units),
                        ),
                        (
                            "Line increment",
                            _length(parameters.feed.line_increment_m, display_units),
                        ),
                        (
                            "Velocity factor",
                            f"{parameters.feed.velocity_factor:.3f}",
                        ),
                        (
                            "Line Z0",
                            f"{parameters.feed.characteristic_impedance_ohm:.1f} Ω",
                        ),
                        (
                            "Splitter excess loss",
                            f"{parameters.feed.splitter_loss_db:.2f} dB",
                        ),
                    ]
                    if parameters.feed.mode is not StackedYagiFeedMode.IDEAL
                    else []
                ),
                *(
                    [
                        (
                            "Matched line loss",
                            f"{parameters.feed.line_loss_db_per_100m:.2f} dB/100 m",
                        ),
                        (
                            "Line losses",
                            " · ".join(
                                f"L{index + 1} {parameters.feed.line_loss_for_level(index):.2f} dB"
                                for index in range(parameters.count)
                            ),
                        ),
                    ]
                    if parameters.feed.mode is StackedYagiFeedMode.NETWORK
                    else []
                ),
                ("Total conductor", _length(total_conductor, display_units)),
                ("Material", material_text(yagi.material, labeler)),
                ("Ground", ground_text(yagi.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, YagiParameters):
        positions = [element.position_m for element in parameters.elements]
        rows.extend(
            [
                ("Type", "Yagi"),
                ("Elements", str(len(parameters.elements))),
                ("Boom length", _length(max(positions) - min(positions), display_units)),
                ("Polarization", parameters.polarization.value),
                ("Boom height", _length(parameters.height_m, display_units)),
                *(
                    [
                        (
                            "Mast",
                            f"{_length(parameters.mast_diameter_m, display_units)} diameter, "
                            f"{_length(parameters.mast_offset_m, display_units)} behind reflector",
                        ),
                        (
                            "Guy wires",
                            f"{parameters.guy_count} at "
                            f"{_length(parameters.guy_anchor_radius_m, display_units)} "
                            "anchor radius",
                        ),
                    ]
                    if parameters.mast_diameter_m > 0.0
                    else []
                ),
            ]
        )
        if parameters.polarization is Polarization.VERTICAL:
            rows.append(("Lowest tip", _length(parameters.lowest_tip_m, display_units)))
        if parameters.is_tapered:
            rows.append(
                (
                    "Tapered tips",
                    f"{parameters.taper_tip_length_m:.4f} m at "
                    f"{parameters.taper_tip_radius_m * 1000.0:.3f} mm radius",
                )
            )
        rows.extend(
            [
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Driven element", str(parameters.driven_index + 1)),
                ("Folded driven", "yes" if parameters.driven_folded else "no"),
                *(
                    [
                        ("Fold spacing", _length(parameters.driven_fold_spacing_m, display_units)),
                        ("Feed transformer", f"{parameters.transformer_ratio:g}:1"),
                    ]
                    if parameters.driven_folded
                    else []
                ),
                ("Feed match", parameters.match_type.value),
                *(
                    [
                        ("Hairpin length", _length(parameters.match_length_m, display_units)),
                        ("Hairpin spacing", _length(parameters.match_spacing_m, display_units)),
                    ]
                    if parameters.match_type.value == "beta_hairpin"
                    else []
                ),
                (
                    "Material",
                    material_text(parameters.material, labeler),
                ),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    rows.extend(
        [
            ("Wire diameter", f"{parameters.wire_radius_m * 2000.0:.3f} mm"),
            (
                "Material",
                material_text(parameters.material, labeler),
            ),
            ("Ground", ground_text(parameters.ground, labeler)),
        ]
    )
    return tuple(rows)


def load_summary_rows(
    loads: tuple[LumpedLoad, ...],
    labeler: Labeler | None = None,
    *,
    display_units: DisplayUnits | None = None,
) -> tuple[tuple[str, str], ...]:
    tr = labeler or identity_labeler
    rows: list[tuple[str, str]] = []
    for index, load in enumerate(loads, start=1):
        kind = tr("parallel" if isinstance(load, ParallelLoad) else "series")
        rows.append(
            (
                tr("Load {index} ({kind})", index=index, kind=kind),
                (
                    f"{load.wire_id} @ {_length(load.offset_m, display_units, decimals=3)} · "
                    f"R={load.resistance_ohm:g} Ω · "
                    f"L={load.inductance_h * 1e6:g} µH · "
                    f"C={load.capacitance_f * 1e12:g} pF"
                ),
            )
        )
    return tuple(rows)


def transmission_line_summary_rows(
    lines: tuple[TransmissionLine, ...],
    labeler: Labeler | None = None,
    *,
    display_units: DisplayUnits | None = None,
) -> tuple[tuple[str, str], ...]:
    tr = labeler or identity_labeler
    rows: list[tuple[str, str]] = []
    for index, line in enumerate(lines, start=1):
        rows.append(
            (
                tr("Transmission line {index}", index=index),
                (
                    f"{line.start_wire_id} @ "
                    f"{_length(line.start_offset_m, display_units, decimals=3)} → "
                    f"{line.end_wire_id} @ "
                    f"{_length(line.end_offset_m, display_units, decimals=3)} · "
                    f"{line.characteristic_impedance_ohm:g} Ω · "
                    f"{_length(line.length_m, display_units, decimals=3)} · "
                    f"VF {line.velocity_factor:g}"
                ),
            )
        )
    return tuple(rows)
