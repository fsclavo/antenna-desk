# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Transmission-line model between the transmitter and the antenna feed."""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from itertools import pairwise

from ..common.units import SPEED_OF_LIGHT_M_PER_S, ensure_non_negative, ensure_positive
from .balun import LossPoint
from .two_port import Abcd


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
    attenuation_points: tuple[LossPoint, ...] = ()
    attenuation_source: str = ""

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
        points = tuple(self.attenuation_points)
        if points:
            if len(points) < 2:
                raise ValueError("a feed-line attenuation table needs at least two points")
            frequencies = [point.frequency_hz for point in points]
            if any(left >= right for left, right in pairwise(frequencies)):
                raise ValueError("feed-line attenuation frequencies must be strictly increasing")
            if not self.attenuation_source.strip():
                raise ValueError("a feed-line attenuation table requires a source")
        object.__setattr__(self, "attenuation_points", points)
        object.__setattr__(self, "attenuation_source", self.attenuation_source.strip())

    @property
    def is_active(self) -> bool:
        return self.length_m > 0.0

    @property
    def is_frequency_dependent(self) -> bool:
        return bool(self.attenuation_points)

    @property
    def attenuation_range_hz(self) -> tuple[float, float] | None:
        if not self.attenuation_points:
            return None
        return self.attenuation_points[0].frequency_hz, self.attenuation_points[-1].frequency_hz

    def is_within_attenuation_range(self, frequency_hz: float) -> bool:
        attenuation_range = self.attenuation_range_hz
        if attenuation_range is None:
            return True
        ensure_positive(frequency_hz, name="frequency_hz")
        return attenuation_range[0] <= frequency_hz <= attenuation_range[1]

    def matched_loss_db_per_100m_at(self, frequency_hz: float) -> float:
        """Return the matched attenuation at ``frequency_hz``.

        A table is interpolated linearly in log frequency and clamped to the
        endpoint values outside its documented range. Preflight warns when the
        frequency plan exceeds that range.
        """

        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.attenuation_points:
            return self.matched_loss_db_per_100m
        points = self.attenuation_points
        if frequency_hz <= points[0].frequency_hz:
            return points[0].loss_db
        if frequency_hz >= points[-1].frequency_hz:
            return points[-1].loss_db
        log_frequency = math.log10(frequency_hz)
        for left, right in pairwise(points):
            if left.frequency_hz <= frequency_hz <= right.frequency_hz:
                span = math.log10(right.frequency_hz) - math.log10(left.frequency_hz)
                fraction = (log_frequency - math.log10(left.frequency_hz)) / span
                return left.loss_db + fraction * (right.loss_db - left.loss_db)
        return points[-1].loss_db

    def abcd(self, frequency_hz: float) -> Abcd:
        """Return the line's ABCD matrix at ``frequency_hz``."""

        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return Abcd()
        attenuation_np_per_m = (
            self.matched_loss_db_per_100m_at(frequency_hz) * math.log(10.0) / (20.0 * 100.0)
        )
        phase_rad_per_m = (
            2.0 * math.pi * frequency_hz / (SPEED_OF_LIGHT_M_PER_S * self.velocity_factor)
        )
        electrical_length = complex(
            attenuation_np_per_m * self.length_m,
            phase_rad_per_m * self.length_m,
        )
        hyperbolic_sine = cmath.sinh(electrical_length)
        hyperbolic_cosine = cmath.cosh(electrical_length)
        return Abcd(
            a=hyperbolic_cosine,
            b=self.characteristic_impedance_ohm * hyperbolic_sine,
            c=hyperbolic_sine / self.characteristic_impedance_ohm,
            d=hyperbolic_cosine,
        )

    def input_impedance(self, load_impedance_ohm: complex, frequency_hz: float) -> complex:
        """Return the impedance at the transmitter end of the line."""

        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return load_impedance_ohm
        return self.abcd(frequency_hz).input_impedance(load_impedance_ohm)
