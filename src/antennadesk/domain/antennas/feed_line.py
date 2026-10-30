# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Transmission-line model between the transmitter and the antenna feed."""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass

from ..common.units import SPEED_OF_LIGHT_M_PER_S, ensure_non_negative, ensure_positive


@dataclass(frozen=True, slots=True)
class FeedLine:
    """A uniform transmission line evaluated at each simulation frequency.

    ``matched_loss_db_per_100m`` is the matched-line power loss.  The input
    impedance is transformed to the transmitter end of the line.  Radiation
    patterns and antenna gain are unchanged by an ideal or lossy feed line;
    only the impedance/SWR seen by the transmitter changes.
    """

    characteristic_impedance_ohm: float = 50.0
    length_m: float = 0.0
    velocity_factor: float = 1.0
    matched_loss_db_per_100m: float = 0.0

    def __post_init__(self) -> None:
        ensure_positive(self.characteristic_impedance_ohm, name="characteristic_impedance_ohm")
        ensure_non_negative(self.length_m, name="length_m")
        ensure_positive(self.velocity_factor, name="velocity_factor")
        if self.velocity_factor > 1.0:
            raise ValueError("velocity_factor must not exceed 1")
        ensure_non_negative(
            self.matched_loss_db_per_100m,
            name="matched_loss_db_per_100m",
        )

    @property
    def is_active(self) -> bool:
        return self.length_m > 0.0

    def input_impedance(self, load_impedance_ohm: complex, frequency_hz: float) -> complex:
        """Return the impedance at the transmitter end of the line."""

        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return load_impedance_ohm

        attenuation_np_per_m = self.matched_loss_db_per_100m * math.log(10.0) / (20.0 * 100.0)
        phase_rad_per_m = (
            2.0 * math.pi * frequency_hz / (SPEED_OF_LIGHT_M_PER_S * self.velocity_factor)
        )
        electrical_length = complex(
            attenuation_np_per_m * self.length_m,
            phase_rad_per_m * self.length_m,
        )
        tangent = cmath.tanh(electrical_length)
        z0 = self.characteristic_impedance_ohm
        return z0 * (load_impedance_ohm + z0 * tangent) / (z0 + load_impedance_ohm * tangent)
