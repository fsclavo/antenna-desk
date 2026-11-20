# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Composed stacked-Yagi geometry with ideal multi-source excitation.

This is the domain prototype for DL6.  It deliberately does not model the
power splitter or the phase-line hardware: each level is driven by an ideal
source with a fixed amplitude and phase progression.  The layout and feed
semantics are experimental until a traceable stack reference exists.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_positive
from .antenna import AntennaModel
from .feed import FeedPoint, Source
from .geometry import Point3D
from .wire import Wire
from .yagi import YagiParameters


@dataclass(frozen=True, slots=True)
class StackedYagiParameters:
    """Two to four identical Yagis on a vertical stack."""

    yagi: YagiParameters
    count: int = 2
    spacing_m: float = 0.0
    phase_step_deg: float = 0.0
    amplitude_ratio: float = 1.0

    def __post_init__(self) -> None:
        if self.count < 2 or self.count > 4:
            raise ValueError("a stacked Yagi requires 2 to 4 levels")
        if self.yagi.mast_diameter_m > 0.0 or self.yagi.guy_count > 0:
            raise ValueError("a stacked Yagi does not support mast or guy wires yet")
        ensure_positive(self.spacing_m, name="spacing_m")
        ensure_positive(self.amplitude_ratio, name="amplitude_ratio")
        if not math.isfinite(self.phase_step_deg):
            raise ValueError("phase_step_deg must be finite")

    def to_antenna(self, *, name: str = "Stacked Yagi") -> AntennaModel:
        base = self.yagi.to_antenna(name=name)
        wires: list[Wire] = []
        for level in range(self.count):
            z_offset = level * self.spacing_m
            prefix = f"level-{level + 1}-"
            for wire in base.wires:
                wires.append(
                    Wire(
                        id=prefix + wire.id,
                        start=Point3D(
                            wire.start.x_m,
                            wire.start.y_m,
                            wire.start.z_m + z_offset,
                        ),
                        end=Point3D(
                            wire.end.x_m,
                            wire.end.y_m,
                            wire.end.z_m + z_offset,
                        ),
                        radius_m=wire.radius_m,
                        material=wire.material,
                    )
                )
        primary_wire = f"level-1-{base.feed.wire_id}"
        sources = tuple(
            Source(
                wire_id=f"level-{level + 1}-{base.feed.wire_id}",
                offset_m=base.feed.offset_m,
                amplitude=self.amplitude_ratio,
                phase_deg=level * self.phase_step_deg,
            )
            for level in range(1, self.count)
        )
        return AntennaModel(
            name=name,
            design_frequency_hz=base.design_frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(wire_id=primary_wire, offset_m=base.feed.offset_m),
            environment=base.environment,
            sources=sources,
        )
