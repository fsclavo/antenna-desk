# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ground models supported by the domain."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..common.units import ensure_positive


class GroundKind(StrEnum):
    FREE_SPACE = "free_space"
    PERFECT = "perfect"
    FINITE = "finite"


@dataclass(frozen=True, slots=True)
class GroundModel:
    """A ground condition.

    Free-space and perfect-ground models carry no electrical parameters.
    Finite ground requires a relative permittivity greater than or equal to 1
    and a positive conductivity in S/m.
    """

    kind: GroundKind
    relative_permittivity: float | None = None
    conductivity_s_per_m: float | None = None

    def __post_init__(self) -> None:
        if self.kind is GroundKind.FINITE:
            if self.relative_permittivity is None or self.conductivity_s_per_m is None:
                raise ValueError(
                    "finite ground requires relative_permittivity and conductivity_s_per_m"
                )
            permittivity = ensure_positive(self.relative_permittivity, name="relative_permittivity")
            if permittivity < 1.0:
                raise ValueError("relative_permittivity must be greater than or equal to 1")
            ensure_positive(self.conductivity_s_per_m, name="conductivity_s_per_m")
        elif self.relative_permittivity is not None or self.conductivity_s_per_m is not None:
            raise ValueError(f"{self.kind.value} ground does not accept electrical parameters")

    @classmethod
    def free_space(cls) -> GroundModel:
        return cls(kind=GroundKind.FREE_SPACE)

    @classmethod
    def perfect(cls) -> GroundModel:
        return cls(kind=GroundKind.PERFECT)

    @classmethod
    def finite(
        cls,
        *,
        relative_permittivity: float,
        conductivity_s_per_m: float,
    ) -> GroundModel:
        return cls(
            kind=GroundKind.FINITE,
            relative_permittivity=relative_permittivity,
            conductivity_s_per_m=conductivity_s_per_m,
        )

    @property
    def is_finite(self) -> bool:
        return self.kind is GroundKind.FINITE


FREE_SPACE = GroundModel.free_space()
PERFECT_GROUND = GroundModel.perfect()
