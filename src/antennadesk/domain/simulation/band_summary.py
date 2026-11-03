# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-band metrics derived from normalized simulation results."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .bands import AmateurBand
from .pattern import takeoff_angle_deg
from .result import SimulationResult, SimulationStatus


@dataclass(frozen=True, slots=True)
class BandMetrics:
    band: AmateurBand
    best_swr: float | None
    best_swr_hz: float | None
    max_gain_db: float | None
    takeoff_deg: float | None
    efficiency_percent: float | None
    status: SimulationStatus


def summarize_band(band: AmateurBand, result: SimulationResult) -> BandMetrics:
    """Return a compact summary for one band result.

    ``max_gain_db`` is NEC power gain (dBi), not realized gain. The takeoff
    angle is taken at the direction with the highest sampled power gain.
    """

    finite_swr = [frequency for frequency in result.frequencies if math.isfinite(frequency.swr)]
    best = min(finite_swr, key=lambda frequency: frequency.swr) if finite_swr else None
    best_swr = best.swr if best is not None else None
    best_swr_hz = best.frequency_hz if best is not None else None
    efficiency = (
        best.power_budget.efficiency_percent
        if best is not None and best.power_budget is not None
        else None
    )

    points = [
        point
        for frequency in result.frequencies
        for point in frequency.far_field
        if point.gain_total_db is not None
        and math.isfinite(point.gain_total_db)
        and point.gain_total_db > -100.0
    ]
    if points:
        strongest = max(points, key=lambda point: point.gain_total_db or -math.inf)
        max_gain = strongest.gain_total_db
        takeoff = takeoff_angle_deg(strongest.theta_deg)
    else:
        max_gain = None
        takeoff = None

    return BandMetrics(
        band=band,
        best_swr=best_swr,
        best_swr_hz=best_swr_hz,
        max_gain_db=max_gain,
        takeoff_deg=takeoff,
        efficiency_percent=efficiency,
        status=result.status,
    )
