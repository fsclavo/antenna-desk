# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Renderer-neutral azimuth and elevation cuts for exported reports."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..domain.simulation.result import FarFieldPoint, FrequencyResult
from .localization import Labeler
from .svg_chart import SvgSeries


@dataclass(frozen=True, slots=True)
class PatternCut:
    title: str
    x_label: str
    series: tuple[SvgSeries, ...]
    angle_deg: float


def _valid_points(frequency: FrequencyResult) -> tuple[FarFieldPoint, ...]:
    return tuple(
        point
        for point in frequency.far_field
        if point.gain_total_db is not None and math.isfinite(point.gain_total_db)
    )


def _group(
    points: tuple[FarFieldPoint, ...],
    *,
    fixed: str,
) -> dict[float, list[tuple[float, float]]]:
    groups: dict[float, list[tuple[float, float]]] = {}
    for point in points:
        if fixed == "theta":
            key = round(point.theta_deg, 3)
            angle = point.phi_deg % 360.0
        else:
            key = round(point.phi_deg, 3)
            angle = point.theta_deg
        groups.setdefault(key, []).append((angle, point.gain_total_db or 0.0))
    return groups


def _select_group(
    groups: dict[float, list[tuple[float, float]]],
    preferred: float,
) -> tuple[float, list[tuple[float, float]]] | None:
    if not groups:
        return None
    preferred_key = round(preferred, 3)
    preferred_points = groups.get(preferred_key)
    if preferred_points is not None and len(preferred_points) >= 2:
        return preferred_key, preferred_points
    key = max(groups, key=lambda item: (len(groups[item]), -abs(item - preferred)))
    points = groups[key]
    return (key, points) if len(points) >= 2 else None


def pattern_cuts(
    frequency: FrequencyResult,
    tr: Labeler,
) -> tuple[PatternCut | None, PatternCut | None]:
    """Return the azimuth and elevation cuts at the maximum-gain direction."""

    points = _valid_points(frequency)
    if not points:
        return None, None
    peak = max(points, key=lambda point: point.gain_total_db or -math.inf)

    azimuth_group = _select_group(_group(points, fixed="theta"), peak.theta_deg)
    elevation_group = _select_group(_group(points, fixed="phi"), peak.phi_deg)

    azimuth = None
    if azimuth_group is not None:
        angle, values = azimuth_group
        azimuth = PatternCut(
            title=tr("Azimuth cut at θ = {angle:.0f}°", angle=angle),
            x_label=tr("Azimuth φ (°)"),
            series=(
                SvgSeries(
                    tr("Total gain"),
                    "#7b4ea3",
                    tuple(sorted(values)),
                ),
            ),
            angle_deg=angle,
        )

    elevation = None
    if elevation_group is not None:
        angle, values = elevation_group
        elevation = PatternCut(
            title=tr("Elevation cut at φ = {angle:.0f}°", angle=angle),
            x_label=tr("Elevation θ (°)"),
            series=(
                SvgSeries(
                    tr("Total gain"),
                    "#7b4ea3",
                    tuple(sorted(values)),
                ),
            ),
            angle_deg=angle,
        )
    return azimuth, elevation
