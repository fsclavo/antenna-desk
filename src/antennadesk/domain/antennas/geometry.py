# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Three-dimensional geometry primitives."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_finite


@dataclass(frozen=True, slots=True)
class Point3D:
    """A point in the canonical right-handed coordinate system, in meters."""

    x_m: float
    y_m: float
    z_m: float

    def __post_init__(self) -> None:
        ensure_finite(self.x_m, name="x_m")
        ensure_finite(self.y_m, name="y_m")
        ensure_finite(self.z_m, name="z_m")

    def distance_to(self, other: Point3D) -> float:
        return math.dist(
            (self.x_m, self.y_m, self.z_m),
            (other.x_m, other.y_m, other.z_m),
        )
