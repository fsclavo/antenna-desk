"""Solver metadata and capabilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SolverMetadata:
    name: str
    version: str
    executable: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("solver name must not be empty")
        if not self.version.strip():
            raise ValueError("solver version must not be empty")


@dataclass(frozen=True, slots=True)
class SolverCapabilities:
    name: str
    supports_frequency_sweep: bool
    supports_currents: bool
    supports_far_field: bool
    supports_perfect_ground: bool
    supports_finite_ground: bool
    supports_extended_thin_wire_kernel: bool
    supports_loads: bool = False
    supports_networks: bool = False
