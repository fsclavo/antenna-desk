"""Conductor materials."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_positive


@dataclass(frozen=True, slots=True)
class ConductorMaterial:
    """A homogeneous conductor material.

    Conductivity is expressed in S/m.  The values in the presets are nominal
    engineering values, not measurements of a specific piece of wire.
    """

    name: str
    conductivity_s_per_m: float
    relative_permeability: float = 1.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("material name must not be empty")
        ensure_positive(self.conductivity_s_per_m, name="conductivity_s_per_m")
        ensure_positive(self.relative_permeability, name="relative_permeability")


COPPER = ConductorMaterial(name="copper", conductivity_s_per_m=5.8e7)
ALUMINUM = ConductorMaterial(name="aluminum", conductivity_s_per_m=3.5e7)
