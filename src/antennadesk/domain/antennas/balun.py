# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency-dependent balun or unun insertion-loss model."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise

from ..common.units import ensure_non_negative, ensure_positive


@dataclass(frozen=True, slots=True)
class LossPoint:
    """One measured insertion-loss point."""

    frequency_hz: float
    loss_db: float

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_non_negative(self.loss_db, name="loss_db")


@dataclass(frozen=True, slots=True)
class BalunLoss:
    """A matched balun/unun insertion loss.

    Without ``points`` the loss is the power-law fit
    ``reference_loss_db * (f / reference_frequency_hz) ** exponent``.
    With ``points`` the loss is linearly interpolated in log frequency between
    measured points and clamped to the endpoint values outside the table range.
    It is a post-processing model: it reduces realized gain but does not change
    the antenna geometry or the impedance transformation ratio.
    """

    enabled: bool = True
    reference_frequency_hz: float = 7_000_000.0
    reference_loss_db: float = 0.5
    exponent: float = 0.5
    points: tuple[LossPoint, ...] = ()
    source: str = ""

    def __post_init__(self) -> None:
        ensure_positive(self.reference_frequency_hz, name="reference_frequency_hz")
        ensure_non_negative(self.reference_loss_db, name="reference_loss_db")
        ensure_non_negative(self.exponent, name="exponent")
        points = tuple(self.points)
        if points:
            if len(points) < 2:
                raise ValueError("a measured loss table needs at least two points")
            frequencies = [point.frequency_hz for point in points]
            if any(left >= right for left, right in pairwise(frequencies)):
                raise ValueError("loss table frequencies must be strictly increasing")
            if not self.source.strip():
                raise ValueError("a measured loss table requires a source")
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "source", self.source.strip())

    @property
    def is_active(self) -> bool:
        return self.enabled and (bool(self.points) or self.reference_loss_db > 0.0)

    @property
    def table_range_hz(self) -> tuple[float, float] | None:
        if not self.points:
            return None
        return self.points[0].frequency_hz, self.points[-1].frequency_hz

    def is_within_table_range(self, frequency_hz: float) -> bool:
        table_range = self.table_range_hz
        if table_range is None:
            return False
        ensure_positive(frequency_hz, name="frequency_hz")
        return table_range[0] <= frequency_hz <= table_range[1]

    def loss_db(self, frequency_hz: float) -> float:
        """Return the matched insertion loss at ``frequency_hz``."""

        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return 0.0
        if self.points:
            return self._interpolated_loss_db(frequency_hz)
        return float(
            self.reference_loss_db
            * math.pow(frequency_hz / self.reference_frequency_hz, self.exponent)
        )

    def _interpolated_loss_db(self, frequency_hz: float) -> float:
        points = self.points
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


# Squash Practice / AF7NX measured a 2xFT114-43, 5T/30T 49:1 transformer at
# 50 W FT8 (21 W average) and reported one thermal loss value per band. The
# exact spot frequencies are not published, so AntennaDesk assigns each value
# to the band center. This is a reference build, not a universal loss model.
SQUASH_PRACTICE_49_1_LOSS_SOURCE = (
    "Squash Practice / AF7NX, 2xFT114-43 5T/30T 49:1 transformer, 50 W FT8 "
    "thermal measurement; band values assigned to band centers"
)
SQUASH_PRACTICE_49_1_LOSS = BalunLoss(
    reference_frequency_hz=7_150_000.0,
    reference_loss_db=0.0,
    exponent=0.0,
    points=(
        LossPoint(3_750_000.0, 0.43),
        LossPoint(7_150_000.0, 0.33),
        LossPoint(14_175_000.0, 0.30),
        LossPoint(28_500_000.0, 0.32),
    ),
    source=SQUASH_PRACTICE_49_1_LOSS_SOURCE,
)
