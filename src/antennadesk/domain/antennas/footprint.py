# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Physical footprint helpers for optimizer space constraints."""

from __future__ import annotations

import math

from .antenna import AntennaModel
from .design import AntennaDesignParameters
from .moxon import MoxonParameters
from .yagi import YagiParameters

# The mast is at the boom midpoint for arrays and at the feed's horizontal
# projection for every other family. This is a presentation/mechanical model,
# not an electromagnetic quantity.
BOOM_FAMILIES = (YagiParameters, MoxonParameters)


def boom_length_m(parameters: AntennaDesignParameters) -> float | None:
    """Return the boom length for array families, or ``None``."""

    if isinstance(parameters, YagiParameters):
        positions = [element.position_m for element in parameters.elements]
        return max(positions) - min(positions)
    if isinstance(parameters, MoxonParameters):
        return parameters.depth_m
    return None


def rotation_center_m(
    parameters: AntennaDesignParameters,
    model: AntennaModel,
) -> tuple[float, float]:
    """Return the horizontal mast/rotation center used for turning radius."""

    if isinstance(parameters, YagiParameters):
        positions = [element.position_m for element in parameters.elements]
        center = (min(positions) + max(positions)) / 2.0
        angle = math.radians(parameters.azimuth_deg)
        return center * math.cos(angle), center * math.sin(angle)
    if isinstance(parameters, MoxonParameters):
        center = parameters.depth_m / 2.0
        angle = math.radians(parameters.azimuth_deg)
        return center * math.cos(angle), center * math.sin(angle)
    feed_wire = model.feed_wire
    point = feed_wire.point_at(min(max(model.feed.offset_m, 0.0), feed_wire.length_m))
    return point.x_m, point.y_m


def turning_radius_m(
    parameters: AntennaDesignParameters,
    model: AntennaModel,
) -> float:
    """Return the maximum horizontal distance from the rotation center."""

    center_x, center_y = rotation_center_m(parameters, model)
    return max(
        math.hypot(point.x_m - center_x, point.y_m - center_y)
        for wire in model.wires
        for point in (wire.start, wire.end)
    )
