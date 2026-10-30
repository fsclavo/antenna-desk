# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate reproducible nec2c input decks from canonical models."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.antennas.antenna import AntennaModel
from ...domain.antennas.load import ParallelLoad
from ...domain.environment.ground import GroundKind
from ...domain.simulation.spec import SimulationSpec
from ..discretization import SegmentLayout, build_segment_layout


@dataclass(frozen=True, slots=True)
class Nec2Deck:
    text: str
    layout: SegmentLayout

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


def write_nec2_input(model: AntennaModel, spec: SimulationSpec) -> Nec2Deck:
    layout = build_segment_layout(model, spec)
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
            f"{_format(wire.start.x_m)} {_format(wire.start.y_m)} {_format(wire.start.z_m)} "
            f"{_format(wire.end.x_m)} {_format(wire.end.y_m)} {_format(wire.end.z_m)} "
            f"{_format(wire.radius_m)}"
        )

    ground = model.environment.ground
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
        index = int(load.offset_m / segmentation.segment_length_m)
        index = min(max(index, 0), segmentation.segments - 1)
        segment = segmentation.first_segment + index
        lines.append(
            f"LD {1 if isinstance(load, ParallelLoad) else 0} "
            f"{segmentation.tag} {segment} {segment} "
            f"{_format(load.resistance_ohm)} "
            f"{_format(load.inductance_h)} "
            f"{_format(load.capacitance_f, 12)}"
        )

    frequency_plan = spec.frequency_plan
    lines.append(
        "FR 0 "
        f"{frequency_plan.count} 0 0 "
        f"{_format(frequency_plan.start_hz / 1_000_000.0)} "
        f"{_format(frequency_plan.step_hz / 1_000_000.0)}"
    )
    lines.append(f"EX 0 {layout.feed_tag} {layout.feed_local_segment} 0 1.0")

    if spec.far_field.enabled:
        far_field = spec.far_field
        lines.append(
            "RP 0 "
            f"{far_field.theta_count} {far_field.phi_count} 1000 "
            f"{_format(far_field.theta_start_deg, 6)} "
            f"{_format(far_field.phi_start_deg, 6)} "
            f"{_format(far_field.theta_step_deg, 6)} "
            f"{_format(far_field.phi_step_deg, 6)}"
        )
    else:
        lines.append("XQ")

    lines.append("EN")
    return Nec2Deck(text="\n".join(lines) + "\n", layout=layout)
