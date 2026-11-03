# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate reproducible nec2c input decks from canonical models."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.load import ParallelLoad
from ...domain.environment.ground import GroundKind
from ...domain.simulation.spec import SimulationSpec
from ..discretization import SegmentLayout, WireSegmentation, build_segment_layout

# NEC-2 requires wires to be separated from a ground plane. Ground-mounted
# radials and dipoles are raised by this small physical clearance when the
# canonical model sits exactly on the ground.
GROUND_CLEARANCE_M = 0.01


@dataclass(frozen=True, slots=True)
class Nec2Deck:
    text: str
    layout: SegmentLayout
    z_offset_m: float = 0.0

    @property
    def feed_tag(self) -> int:
        return self.layout.feed_tag

    @property
    def feed_segment(self) -> int:
        return self.layout.feed_segment

    @property
    def feed_local_segment(self) -> int:
        return self.layout.feed_local_segment


def _format(value: float, precision: int = 9) -> str:
    if abs(value) < 1e-15:
        value = 0.0
    return f"{value:.{precision}f}"


def _comment(text: str, limit: int = 70) -> str:
    cleaned = text.encode("ascii", errors="replace").decode("ascii").replace("\n", " ")
    return cleaned[:limit]


def _local_segment_for_offset(segmentation: WireSegmentation, offset_m: float) -> int:
    """Map a wire offset to a one-based segment number within its tag."""

    index = int(offset_m / segmentation.segment_length_m)
    index = min(max(index, 0), segmentation.segments - 1)
    return index + 1


def write_nec2_input(model: AntennaModel, spec: SimulationSpec) -> Nec2Deck:
    layout = build_segment_layout(model, spec)
    ground = model.environment.ground
    z_offset = 0.0
    if ground.kind is not GroundKind.FREE_SPACE:
        min_z = min(point.z_m for wire in model.wires for point in (wire.start, wire.end))
        if 0.0 <= min_z < GROUND_CLEARANCE_M:
            z_offset = GROUND_CLEARANCE_M - min_z
    lines: list[str] = [
        "CM AntennaDesk generated NEC-2 input",
        f"CM Model: {_comment(model.name)}",
        "CE",
    ]

    for segmentation in layout.wires:
        wire = segmentation.wire
        lines.append(
            "GW "
            f"{segmentation.tag} {segmentation.segments} "
            f"{_format(wire.start.x_m)} {_format(wire.start.y_m)} "
            f"{_format(wire.start.z_m + z_offset)} "
            f"{_format(wire.end.x_m)} {_format(wire.end.y_m)} "
            f"{_format(wire.end.z_m + z_offset)} "
            f"{_format(wire.radius_m)}"
        )

    lines.append("GE 1" if ground.kind is not GroundKind.FREE_SPACE else "GE 0")
    if ground.kind is GroundKind.PERFECT:
        lines.append("GN 1")
    elif ground.kind is GroundKind.FINITE:
        assert ground.relative_permittivity is not None
        assert ground.conductivity_s_per_m is not None
        lines.append(
            "GN 0 0 0 0 "
            f"{_format(ground.relative_permittivity)} "
            f"{_format(ground.conductivity_s_per_m)}"
        )

    if spec.extended_thin_wire_kernel:
        lines.append("EK")

    if spec.include_conductor_losses:
        for segmentation in layout.wires:
            lines.append(
                "LD 5 "
                f"{segmentation.tag} 0 0 "
                f"{_format(segmentation.wire.material.conductivity_s_per_m)}"
            )

    for load in model.loads:
        segmentation = layout.wire_segmentation(load.wire_id)
        segment = _local_segment_for_offset(segmentation, load.offset_m)
        lines.append(
            f"LD {1 if isinstance(load, ParallelLoad) else 0} "
            f"{segmentation.tag} {segment} {segment} "
            f"{_format(load.resistance_ohm)} "
            f"{_format(load.inductance_h)} "
            f"{_format(load.capacitance_f, 12)}"
        )

    for transmission_line in model.transmission_lines:
        start = layout.wire_segmentation(transmission_line.start_wire_id)
        end = layout.wire_segmentation(transmission_line.end_wire_id)
        start_segment = _local_segment_for_offset(start, transmission_line.start_offset_m)
        end_segment = _local_segment_for_offset(end, transmission_line.end_offset_m)
        lines.append(
            "TL "
            f"{start.tag} {start_segment} {end.tag} {end_segment} "
            f"{_format(transmission_line.characteristic_impedance_ohm)} "
            f"{_format(transmission_line.electrical_length_m)} "
            "0.000000000 0.000000000 0.000000000 0.000000000"
        )

    frequency_plan = spec.frequency_plan
    lines.append(
        "FR 0 "
        f"{frequency_plan.count} 0 0 "
        f"{_format(frequency_plan.start_hz / 1_000_000.0)} "
        f"{_format(frequency_plan.step_hz / 1_000_000.0)}"
    )
    lines.append(f"EX 0 {layout.feed_tag} {layout.feed_local_segment} 0 1.0")

    def append_pattern_card() -> None:
        far_field = spec.far_field
        lines.append(
            "RP 0 "
            f"{far_field.theta_count} {far_field.phi_count} 1000 "
            f"{_format(far_field.theta_start_deg, 6)} "
            f"{_format(far_field.phi_start_deg, 6)} "
            f"{_format(far_field.theta_step_deg, 6)} "
            f"{_format(far_field.phi_step_deg, 6)}"
        )

    if not spec.far_field.enabled:
        lines.append("XQ")
    elif spec.pattern_frequencies_hz:
        # The sweep block computes impedance and currents without patterns.
        # Each snapshot then gets its own single-frequency block with an RP
        # card, so the pattern can be much finer than a pattern at every sweep
        # point would allow.
        lines.append("XQ")
        for frequency_hz in spec.pattern_frequencies_hz:
            lines.append(f"FR 0 1 0 0 {_format(frequency_hz / 1_000_000.0)} 0.000000000")
            lines.append(f"EX 0 {layout.feed_tag} {layout.feed_local_segment} 0 1.0")
            append_pattern_card()
    else:
        append_pattern_card()

    lines.append("EN")
    return Nec2Deck(text="\n".join(lines) + "\n", layout=layout, z_offset_m=z_offset)
