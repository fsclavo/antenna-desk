# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-point definitions."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common import units
from ..common.units import ensure_non_negative, ensure_positive


@dataclass(frozen=True, slots=True)
class FeedPoint:
    """A feed point located along a wire, measured from its start."""

    wire_id: str
    offset_m: float

    def __post_init__(self) -> None:
        if not self.wire_id.strip():
            raise ValueError("feed wire_id must not be empty")
        ensure_non_negative(self.offset_m, name="feed offset_m")


@dataclass(frozen=True, slots=True)
class Source:
    """An additional driven source relative to the primary feed.

    The primary ``AntennaModel.feed`` is always source 1 with unit amplitude
    and zero phase. ``Source`` instances add further excitations. Amplitude is
    a positive voltage scale and phase is in degrees; the pair is converted to
    the real/imaginary form used by NEC.
    """

    wire_id: str
    offset_m: float
    amplitude: float = 1.0
    phase_deg: float = 0.0

    def __post_init__(self) -> None:
        if not self.wire_id.strip():
            raise ValueError("source wire_id must not be empty")
        ensure_non_negative(self.offset_m, name="source offset_m")
        ensure_positive(self.amplitude, name="source amplitude")
        if not math.isfinite(self.phase_deg):
            raise ValueError("source phase must be finite")
        object.__setattr__(
            self,
            "phase_deg",
            units.normalize_azimuth_degrees(self.phase_deg),
        )

    @property
    def real(self) -> float:
        return self.amplitude * math.cos(math.radians(self.phase_deg))

    @property
    def imaginary(self) -> float:
        return self.amplitude * math.sin(math.radians(self.phase_deg))
