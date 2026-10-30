# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Human-readable design rows shared by reports and construction sheets."""

from __future__ import annotations

from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ..domain.antennas.endfed import EndFedParameters
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.load import LumpedLoad, ParallelLoad
from ..domain.antennas.loop import LoopParameters
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters
from ..domain.environment.ground import GroundModel


def ground_text(ground: GroundModel) -> str:
    if ground.relative_permittivity is not None and ground.conductivity_s_per_m is not None:
        return (
            f"{ground.kind.value} (eps_r={ground.relative_permittivity:g}, "
            f"sigma={ground.conductivity_s_per_m:g} S/m)"
        )
    return ground.kind.value


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
        rows.extend(
            [
                ("Type", "vertical"),
                ("Radiator height", f"{parameters.height_m:.4f} m"),
                ("Base height", f"{parameters.base_height_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                ("Radials", str(parameters.radial_count)),
                ("Radial length", f"{parameters.radial_length_m:.4f} m"),
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
    elif isinstance(parameters, LoopParameters):
        rows.extend(
            [
                ("Type", "loop"),
                ("Circumference", f"{parameters.circumference_m:.4f} m"),
                ("Sides", str(parameters.sides)),
                ("Equivalent diameter", f"{parameters.diameter_m:.4f} m"),
                ("Bottom height", f"{parameters.height_m:.4f} m"),
                ("Top height", f"{parameters.top_height_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
            ]
        )
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
        rows.extend(
            [
                ("Type", "end-fed wire"),
                ("Length", f"{parameters.length_m:.4f} m"),
                ("Feed height", f"{parameters.feed_height_m:.4f} m"),
                ("End height", f"{parameters.end_height_m:.4f} m"),
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
                ("Height", f"{parameters.height_m:.4f} m"),
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
                ("Height", f"{parameters.height_m:.4f} m"),
                ("Azimuth", f"{parameters.azimuth_deg:.1f}°"),
                ("Driven element", str(parameters.driven_index + 1)),
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
