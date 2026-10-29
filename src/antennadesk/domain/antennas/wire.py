# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Physical wire conductors."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_positive
from .geometry import Point3D
from .materials import ConductorMaterial


@dataclass(frozen=True, slots=True)
class Wire:
    """A straight physical conductor with a circular cross-section."""

    id: str
    start: Point3D
    end: Point3D
    radius_m: float
    material: ConductorMaterial

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("wire id must not be empty")
        ensure_positive(self.radius_m, name="wire radius_m")
        if self.start == self.end:
            raise ValueError("wire must have non-zero length")

    @property
    def length_m(self) -> float:
        return self.start.distance_to(self.end)
