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
from ..domain.antennas.hexbeam import HexbeamParameters
from ..domain.antennas.inverted_l import InvertedLParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.load import LumpedLoad, ParallelLoad
from ..domain.antennas.loaded_dipole import LoadedDipoleParameters
from ..domain.antennas.loop import LoopOrientation, LoopParameters
from ..domain.antennas.magnetic_loop import MagneticLoopParameters
from ..domain.antennas.matching_network import (
    LNetwork,
    MatchingNetwork,
    MatchingNetworkPosition,
    PiNetwork,
    TNetwork,
)
from ..domain.antennas.materials import ConductorMaterial
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.phased_vertical import PhasedVerticalParameters
from ..domain.antennas.polarization import Polarization
from ..domain.antennas.quad_beam import QuadBeamParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvParameters
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
from .localization import Labeler, identity_labeler


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


def design_provenance_rows(design: DesignVariant) -> tuple[tuple[str, str], ...]:
    provenance = design.provenance
    if provenance is None:
        return ()
    return (
        ("Dimension source", provenance.method_id),
        ("Estimate confidence", provenance.confidence),
        ("Estimate tolerance", f"{provenance.tolerance_m:.4f} m"),
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

    return (
        ("Evidence level", f"{entry.level.value} ({entry.level.name.lower()})"),
        ("Evidence source", evidence_text("source", entry.source)),
        ("Evidence tolerance", evidence_text("tolerance", entry.tolerance)),
        ("Limitation", evidence_text("limitation", entry.limitation)),
    )


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
    else:
        raise TypeError(f"unsupported matching network: {type(network)!r}")
    if network.q_factor:
        description += tr(", Q {q:g}", q=network.q_factor)
    return description


def installation_profile_rows(
    profile: InstallationProfile | None,
    labeler: Labeler | None = None,
) -> tuple[tuple[str, str], ...]:
    """Return the active installation profile as report rows."""

    if profile is None:
        return ()
    tr = labeler or identity_labeler
    height = (
        f"{profile.available_height_m:.3f} m" if profile.available_height_m is not None else "—"
    )
    width = f"{profile.available_width_m:.3f} m" if profile.available_width_m is not None else "—"
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
                    "{impedance:g} Ω, {length:.4f} m, velocity factor {velocity:g}",
                    impedance=feed_line.characteristic_impedance_ohm,
                    length=feed_line.length_m,
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
    return tuple(rows)


def design_summary_rows(
    parameters: AntennaDesignParameters,
    labeler: Labeler | None = None,
    *,
    project_network: MatchingNetwork | None = None,
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
                ("Total conductor", f"{sum(wire.length_m for wire in parameters.wires):.4f} m"),
                ("Min height", f"{min(heights):.4f} m"),
                ("Max height", f"{max(heights):.4f} m"),
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
                ("Total wire length", f"{parameters.total_length_m:.4f} m"),
                (height_label, f"{parameters.height_m:.4f} m"),
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
                    ("Sag", f"{parameters.sag_m:.4f} m"),
                    (
                        "Conductor length",
                        f"{parameters.conductor_length_m:.4f} m",
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
                ("Total wire length", f"{parameters.total_length_m:.4f} m"),
                ("Center section", f"{parameters.inner_length_m:.4f} m"),
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
                (height_label, f"{parameters.height_m:.4f} m"),
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
                ("Element length", f"{parameters.length_m:.4f} m"),
                ("Conductor spacing", f"{parameters.spacing_m:.4f} m"),
                (
                    "Total conductor length",
                    f"{parameters.total_conductor_length_m:.4f} m",
                ),
                (
                    "Termination resistor",
                    f"{parameters.termination_resistance_ohm:g} Ω non-inductive",
                ),
                ("Feed transformer", f"{parameters.transformer_ratio:g}:1"),
                (height_label, f"{parameters.height_m:.4f} m"),
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
                ("Element length", f"{parameters.total_length_m:.4f} m"),
                ("Spacing", f"{parameters.spacing_m:.4f} m"),
                ("Total conductor length", f"{parameters.total_conductor_length_m:.4f} m"),
                ("Height", f"{parameters.height_m:.4f} m"),
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
                ("Radiator height", f"{parameters.height_m:.4f} m"),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                ("Radials", str(parameters.radial_count)),
                ("Radial length", f"{parameters.radial_length_m:.4f} m"),
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
                    ("Top hat radius", f"{parameters.top_hat_radius_m:.4f} m"),
                ]
            )
    elif isinstance(parameters, InvertedLParameters):
        rows.extend(
            [
                ("Type", "inverted L"),
                ("Vertical height", f"{parameters.vertical_height_m:.4f} m"),
                ("Horizontal length", f"{parameters.horizontal_length_m:.4f} m"),
                ("Total wire length", f"{parameters.total_length_m:.4f} m"),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
    elif isinstance(parameters, InvertedVParameters):
        rows.extend(
            [
                ("Type", "inverted-V"),
                ("Leg length", f"{parameters.leg_length_m:.4f} m"),
                ("Apex height", f"{parameters.apex_height_m:.4f} m"),
                ("End height", f"{parameters.end_height_m:.4f} m"),
                ("Included angle", f"{parameters.included_angle_deg:.1f}°"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
    elif isinstance(parameters, OCFDParameters):
        rows.extend(
            [
                ("Type", "off-center-fed dipole"),
                ("Total wire length", f"{parameters.total_length_m:.4f} m"),
                (
                    "Feed offset",
                    f"{parameters.feed_offset_m:.4f} m ({parameters.feed_ratio * 100:.1f}%)",
                ),
                ("Height", f"{parameters.height_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
    elif isinstance(parameters, MagneticLoopParameters):
        rows.extend(
            [
                ("Type", "magnetic loop"),
                ("Diameter", f"{parameters.diameter_m:.4f} m"),
                ("Circumference", f"{parameters.circumference_m:.4f} m"),
                ("Loop conductor", f"{parameters.loop_conductor_length_m:.4f} m"),
                ("Sides", str(parameters.sides)),
                ("Bottom height", f"{parameters.height_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                ("Tuning gap", f"{parameters.gap_length_m:.4f} m"),
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
                ("Circumference", f"{parameters.circumference_m:.4f} m"),
                ("Sides", str(parameters.sides)),
                ("Equivalent diameter", f"{parameters.diameter_m:.4f} m"),
            ]
        )
        if parameters.orientation is LoopOrientation.HORIZONTAL:
            rows.append(("Height", f"{parameters.height_m:.4f} m"))
        else:
            rows.extend(
                [
                    ("Bottom height", f"{parameters.height_m:.4f} m"),
                    ("Top height", f"{parameters.top_height_m:.4f} m"),
                ]
            )
        rows.append(("Azimuth", f"{parameters.azimuth_deg:.1f}°"))
    if isinstance(parameters, TransmissionLineDoubletParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Dipole length", f"{parameters.dipole_total_length_m:.4f} m"),
                ("Height", f"{parameters.height_m:.4f} m"),
                ("Feed height", f"{parameters.feed_height_m:.4f} m"),
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
                ("Radiator length", f"{parameters.radiator_length_m:.4f} m"),
                ("Matching section", f"{parameters.matching_section_length_m:.4f} m"),
                ("Spacing", f"{parameters.spacing_m:.4f} m"),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                (
                    "Radiator height",
                    f"{parameters.base_height_m + parameters.matching_section_length_m:.4f} m",
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
                ("Horizontal length", f"{parameters.horizontal_length_m:.4f} m"),
                ("Vertical height", f"{parameters.vertical_height_m:.4f} m"),
                ("Vertical elements", str(parameters.vertical_count)),
                (
                    "Horizontal segment",
                    tr(
                        "{length:.4f} m each",
                        length=parameters.horizontal_segment_m,
                    ),
                ),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                (
                    "Feed offset below top",
                    f"{parameters.feed_offset_m:.4f} m",
                ),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, LoadedDipoleParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Active length", f"{parameters.active_length_m:.4f} m"),
                ("Full length", f"{parameters.total_length_m:.4f} m"),
                ("Link offset", f"{parameters.link_offset_m:.4f} m"),
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
                ("Height", f"{parameters.height_m:.4f} m"),
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
                ("Driver half-length", f"{parameters.driver_half_length_m:.4f} m"),
                ("Reflector half-length", f"{parameters.reflector_half_length_m:.4f} m"),
                ("Turning radius", f"{parameters.turning_radius_m:.4f} m"),
                ("Tip gap", f"{parameters.tip_gap_m:.4f} m"),
                ("Overall span", f"{parameters.overall_span_m:.4f} m"),
                ("Height", f"{parameters.height_m:.4f} m"),
                ("Feed", "center of the W driver"),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, TrapYagiParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Elements", str(parameters.element_count)),
                ("Driven element", f"{parameters.driven_length_m:.4f} m"),
                ("Reflector element", f"{parameters.reflector_length_m:.4f} m"),
                ("Reflector spacing", f"{parameters.reflector_spacing_m:.4f} m"),
                ("Boom length", f"{parameters.boom_length_m:.4f} m"),
                ("Trap inset", f"{parameters.trap_inset_m:.4f} m"),
                ("Trap frequency", f"{parameters.trap_frequency_hz / 1e6:.3f} MHz"),
                (
                    "Trap inductance",
                    f"{parameters.trap_inductance_h * 1e6:.3f} µH",
                ),
                ("Height", f"{parameters.height_m:.4f} m"),
                ("Feed", "driven element center"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        if parameters.element_count == 3:
            rows.insert(4, ("Director element", f"{parameters.director_length_m:.4f} m"))
            rows.insert(6, ("Director spacing", f"{parameters.director_spacing_m:.4f} m"))
        return tuple(rows)
    if isinstance(parameters, DisconeParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Radial wires", str(parameters.wire_count)),
                ("Cone height", f"{parameters.cone_height_m:.4f} m"),
                ("Cone base radius", f"{parameters.cone_radius_m:.4f} m"),
                ("Disc radius", f"{parameters.disc_radius_m:.4f} m"),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Feed gap", f"{parameters.disc_gap_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                ("Feed", "across the apex gap"),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
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
                ("Driven loop side", f"{parameters.loop_side_m:.4f} m"),
                ("Reflector side", f"{parameters.reflector_side_m:.4f} m"),
                ("Reflector spacing", f"{parameters.reflector_spacing_m:.4f} m"),
                ("Boom length", f"{parameters.boom_length_m:.4f} m"),
                ("Height", f"{parameters.height_m:.4f} m"),
                ("Feed", "driven loop side midpoint"),
                ("Polarization", "horizontal"),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        if parameters.element_count == 3:
            rows.insert(
                4,
                ("Director side", f"{parameters.director_side_m:.4f} m"),
            )
            rows.insert(
                5,
                ("Director spacing", f"{parameters.director_spacing_m:.4f} m"),
            )
        return tuple(rows)
    if isinstance(parameters, PhasedVerticalParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Verticals", str(parameters.element_count)),
                ("Element spacing", f"{parameters.spacing_m:.4f} m"),
                ("Height", f"{parameters.height_m:.4f} m"),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Phase step", f"{parameters.phase_step_deg:.1f}°"),
                ("Amplitude taper", f"{parameters.amplitude_taper * 100.0:.0f}%"),
                ("Radials per element", str(parameters.radial_count)),
                ("Radial length", f"{parameters.radial_length_m:.4f} m"),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
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
                ("Length", f"{parameters.length_m:.4f} m"),
                ("Height", f"{parameters.height_m:.4f} m"),
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
                ("Feed", "near end"),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
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
                ("Loop side", f"{parameters.loop_side_m:.4f} m"),
                ("Stack height", f"{parameters.total_height_m:.4f} m"),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                ("Feed height", f"{parameters.feed_height_m:.4f} m"),
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
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, RingoParameters):
        rows.extend(
            [
                ("Type", "Ringo"),
                ("Radiator height", f"{parameters.radiator_height_m:.4f} m"),
                ("Ring diameter", f"{parameters.ring_diameter_m:.4f} m"),
                ("Ring height", f"{parameters.ring_height_m:.4f} m"),
                ("Ring sides", str(parameters.ring_sides)),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, JPoleParameters):
        rows.extend(
            [
                ("Type", parameters.template_name),
                ("Radiator height", f"{parameters.radiator_height_m:.4f} m"),
                ("Stub length", f"{parameters.stub_length_m:.4f} m"),
                ("Stub spacing", f"{parameters.spacing_m:.4f} m"),
                ("Feed offset", f"{parameters.feed_offset_m:.4f} m"),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Folded", "yes" if parameters.folded else "no"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, EndFedParameters):
        counterpoise = (
            f"{parameters.counterpoise_length_m:.4f} m"
            if parameters.counterpoise_length_m > 0.0
            else "none"
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
                ("Length", f"{parameters.length_m:.4f} m"),
                ("Feed section", f"{parameters.feed_section_length_m:.4f} m"),
                ("Feed height", f"{parameters.feed_height_m:.4f} m"),
                *(
                    [
                        ("Vertical section", f"{parameters.bend_vertical_length_m:.4f} m"),
                        ("Horizontal run", f"{parameters.bend_horizontal_length_m:.4f} m"),
                        ("Top height", f"{parameters.bend_top_height_m:.4f} m"),
                    ]
                    if parameters.bend_active
                    else [("End height", f"{parameters.end_height_m:.4f} m")]
                ),
                ("Transformer", f"{parameters.transformer_ratio:g}:1"),
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
                    f"{parameters.counterpoise_height_m:.4f} m",
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
            override_active = resolve_matching_network(parameters, project_network).override_active
            matching_status = (
                tr("retained; project network overrides") if override_active else tr("active")
            )
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
                        f"{parameters.loading_coil_top_length_m:.4f} m",
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
                    ", ".join(f"{element.length_m:.4f} m" for element in parameters.elements),
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
                        f"{parameters.element_end_height_m(element):.4f} m"
                        for element in parameters.elements
                    ),
                ),
                ("Apex height", f"{parameters.apex_height_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, MoxonParameters):
        rows.extend(
            [
                ("Type", "Moxon rectangle"),
                ("Element width", f"{parameters.width_m:.4f} m"),
                ("Element spacing", f"{parameters.depth_m:.4f} m"),
                ("Reflector tip", f"{parameters.reflector_tip_m:.4f} m"),
                ("Driven tip", f"{parameters.driven_tip_m:.4f} m"),
                ("Tip gap", f"{parameters.gap_m:.4f} m"),
                ("Polarization", parameters.polarization.value),
                ("Boom height", f"{parameters.height_m:.4f} m"),
            ]
        )
        if parameters.polarization is Polarization.VERTICAL:
            rows.append(("Lowest edge", f"{parameters.lowest_edge_m:.4f} m"))
        rows.extend(
            [
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground, labeler)),
            ]
        )
        return tuple(rows)
    if isinstance(parameters, YagiParameters):
        positions = [element.position_m for element in parameters.elements]
        rows.extend(
            [
                ("Type", "Yagi"),
                ("Elements", str(len(parameters.elements))),
                ("Boom length", f"{max(positions) - min(positions):.4f} m"),
                ("Polarization", parameters.polarization.value),
                ("Boom height", f"{parameters.height_m:.4f} m"),
            ]
        )
        if parameters.polarization is Polarization.VERTICAL:
            rows.append(("Lowest tip", f"{parameters.lowest_tip_m:.4f} m"))
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
                    [("Fold spacing", f"{parameters.driven_fold_spacing_m:.4f} m")]
                    if parameters.driven_folded
                    else []
                ),
                ("Feed match", parameters.match_type.value),
                *(
                    [
                        ("Hairpin length", f"{parameters.match_length_m:.4f} m"),
                        ("Hairpin spacing", f"{parameters.match_spacing_m:.4f} m"),
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
) -> tuple[tuple[str, str], ...]:
    tr = labeler or identity_labeler
    rows: list[tuple[str, str]] = []
    for index, load in enumerate(loads, start=1):
        kind = tr("parallel" if isinstance(load, ParallelLoad) else "series")
        rows.append(
            (
                tr("Load {index} ({kind})", index=index, kind=kind),
                (
                    f"{load.wire_id} @ {load.offset_m:.3f} m · "
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
) -> tuple[tuple[str, str], ...]:
    tr = labeler or identity_labeler
    rows: list[tuple[str, str]] = []
    for index, line in enumerate(lines, start=1):
        rows.append(
            (
                tr("Transmission line {index}", index=index),
                (
                    f"{line.start_wire_id} @ {line.start_offset_m:.3f} m → "
                    f"{line.end_wire_id} @ {line.end_offset_m:.3f} m · "
                    f"{line.characteristic_impedance_ohm:g} Ω · "
                    f"{line.length_m:.3f} m · VF {line.velocity_factor:g}"
                ),
            )
        )
    return tuple(rows)
