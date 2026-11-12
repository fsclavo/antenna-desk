# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""User-defined straight-wire antenna parameters."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_positive
from ..common.validation import Diagnostic
from ..environment.environment import Environment
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint
from .geometry_checks import wire_geometry_warnings
from .load import LumpedLoad
from .transmission_line import TransmissionLine
from .wire import Wire

ANTENNA_TYPE_CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class CustomAntennaParameters:
    """A user-defined set of straight wires, one feed, and optional loads."""

    frequency_hz: float
    wires: tuple[Wire, ...]
    feed: FeedPoint
    ground: GroundModel = FREE_SPACE
    loads: tuple[LumpedLoad, ...] = ()
    transmission_lines: tuple[TransmissionLine, ...] = ()
    generator_id: str | None = None
    generator_name: str | None = None
    feed_transformer_ratio: float = 1.0

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.feed_transformer_ratio, name="feed_transformer_ratio")
        object.__setattr__(self, "wires", tuple(self.wires))
        object.__setattr__(self, "loads", tuple(self.loads))
        object.__setattr__(
            self,
            "transmission_lines",
            tuple(self.transmission_lines),
        )
        for field_name in ("generator_id", "generator_name"):
            value = getattr(self, field_name)
            if value is not None and not value.strip():
                raise ValueError(f"{field_name} must not be empty when provided")

    def to_antenna(self, *, name: str = "Custom antenna") -> AntennaModel:
        return AntennaModel(
            name=name,
            design_frequency_hz=self.frequency_hz,
            wires=self.wires,
            feed=self.feed,
            environment=Environment(ground=self.ground),
            loads=self.loads,
            transmission_lines=self.transmission_lines,
        )


def geometry_warnings(parameters: CustomAntennaParameters) -> tuple[Diagnostic, ...]:
    """Return construction geometry warnings for a custom antenna."""

    return wire_geometry_warnings(tuple(parameters.wires))
