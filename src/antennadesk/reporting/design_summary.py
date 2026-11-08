# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Human-readable design rows shared by reports and construction sheets."""

from __future__ import annotations

from ..domain.antennas.beverage import BeverageParameters
from ..domain.antennas.biquad import BiquadParameters
from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ..domain.antennas.endfed import EndFedParameters, EndFedPreset
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.inverted_l import InvertedLParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.load import LumpedLoad, ParallelLoad
from ..domain.antennas.loaded_dipole import LoadedDipoleParameters
from ..domain.antennas.loop import LoopOrientation, LoopParameters
from ..domain.antennas.magnetic_loop import MagneticLoopParameters
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.phased_vertical import PhasedVerticalParameters
from ..domain.antennas.polarization import Polarization
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvParameters
from ..domain.antennas.t2fd import T2FDParameters
from ..domain.antennas.transmission_line import TransmissionLine
from ..domain.antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.antennas.zepp import ZeppParameters, parallel_wire_impedance_ohm
from ..domain.environment.ground import GroundModel
from ..domain.projects.project import DesignVariant


def ground_text(ground: GroundModel) -> str:
    if ground.relative_permittivity is not None and ground.conductivity_s_per_m is not None:
        return (
            f"{ground.kind.value} (eps_r={ground.relative_permittivity:g}, "
            f"sigma={ground.conductivity_s_per_m:g} S/m)"
        )
    return ground.kind.value


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


def design_summary_rows(
    parameters: AntennaDesignParameters,
) -> tuple[tuple[str, str], ...]:
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
                ("Ground", ground_text(parameters.ground)),
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
                ("Outer section", f"{parameters.outer_length_m:.4f} m each"),
                (
                    "Trap positions",
                    f"{left_position:.4f} m, {right_position:.4f} m from wire start",
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
                ("Ground", ground_text(parameters.ground)),
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
                ("Ground", ground_text(parameters.ground)),
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
                    f"{parameters.horizontal_segment_m:.4f} m each",
                ),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                (
                    "Feed offset below top",
                    f"{parameters.feed_offset_m:.4f} m",
                ),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground)),
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
                ("Ground", ground_text(parameters.ground)),
            ]
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
                ("Ground", ground_text(parameters.ground)),
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
                        f"{parameters.termination_resistance_ohm:.1f} Ω to ground"
                        if parameters.termination_enabled
                        else "disabled"
                    ),
                ),
                ("Feed", "near end"),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground)),
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
                        f"{parameters.reflector_spacing_m:.4f} m behind"
                        if parameters.reflector_enabled
                        else "disabled"
                    ),
                ),
                ("Total conductor", f"{parameters.total_conductor_length_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground)),
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
                ("Ground", ground_text(parameters.ground)),
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
                ("Ground", ground_text(parameters.ground)),
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
        }[parameters.preset]
        rows.extend(
            [
                ("Type", type_label),
                ("Length", f"{parameters.length_m:.4f} m"),
                ("Feed height", f"{parameters.feed_height_m:.4f} m"),
                ("End height", f"{parameters.end_height_m:.4f} m"),
                ("Transformer", f"{parameters.transformer_ratio:g}:1"),
                ("Counterpoise", counterpoise),
                (
                    "Counterpoise height",
                    f"{parameters.counterpoise_height_m:.4f} m",
                ),
                (
                    "Counterpoise azimuth",
                    f"{parameters.effective_counterpoise_azimuth_deg:.1f}°",
                ),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground)),
            ]
        )
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
                ("Apex height", f"{parameters.apex_height_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Ground", ground_text(parameters.ground)),
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
                ("Ground", ground_text(parameters.ground)),
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
                    f"{parameters.material.name} "
                    f"({parameters.material.conductivity_s_per_m:.3g} S/m)",
                ),
                ("Ground", ground_text(parameters.ground)),
            ]
        )
        return tuple(rows)
    rows.extend(
        [
            ("Wire diameter", f"{parameters.wire_radius_m * 2000.0:.3f} mm"),
            (
                "Material",
                f"{parameters.material.name} ({parameters.material.conductivity_s_per_m:.3g} S/m)",
            ),
            ("Ground", ground_text(parameters.ground)),
        ]
    )
    return tuple(rows)


def load_summary_rows(loads: tuple[LumpedLoad, ...]) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    for index, load in enumerate(loads, start=1):
        kind = "parallel" if isinstance(load, ParallelLoad) else "series"
        rows.append(
            (
                f"Load {index} ({kind})",
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
) -> tuple[tuple[str, str], ...]:
    rows: list[tuple[str, str]] = []
    for index, line in enumerate(lines, start=1):
        rows.append(
            (
                f"Transmission line {index}",
                (
                    f"{line.start_wire_id} @ {line.start_offset_m:.3f} m → "
                    f"{line.end_wire_id} @ {line.end_offset_m:.3f} m · "
                    f"{line.characteristic_impedance_ohm:g} Ω · "
                    f"{line.length_m:.3f} m · VF {line.velocity_factor:g}"
                ),
            )
        )
    return tuple(rows)
