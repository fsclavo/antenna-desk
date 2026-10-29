# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""User-defined straight-wire antenna parameters."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_positive
from ..environment.environment import Environment
from ..environment.ground import FREE_SPACE, GroundModel
from .antenna import AntennaModel
from .feed import FeedPoint
from .load import LumpedLoad
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

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        object.__setattr__(self, "wires", tuple(self.wires))
        object.__setattr__(self, "loads", tuple(self.loads))

    def to_antenna(self, *, name: str = "Custom antenna") -> AntennaModel:
        return AntennaModel(
            name=name,
            design_frequency_hz=self.frequency_hz,
            wires=self.wires,
            feed=self.feed,
            environment=Environment(ground=self.ground),
            loads=self.loads,
        )
