# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Human-readable design rows shared by reports and construction sheets."""

from __future__ import annotations

from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.load import LumpedLoad, ParallelLoad
from ..domain.antennas.loop import LoopParameters
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
