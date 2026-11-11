# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Persisted design target for a project matching network."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_positive
from ..simulation.result import FrequencyResult
from ..simulation.spec import SimulationSpec

MATCHING_DESIGN_ORIGIN_MANUAL = "manual"
MATCHING_DESIGN_ORIGIN_SIMULATION = "simulation"


@dataclass(frozen=True, slots=True)
class MatchingNetworkDesign:
    """Frequency, load, and source impedance used to design a network."""

    frequency_hz: float
    load_resistance_ohm: float
    load_reactance_ohm: float
    source_impedance_ohm: float = 50.0
    origin: str | None = None

    def __post_init__(self) -> None:
        ensure_positive(self.frequency_hz, name="frequency_hz")
        ensure_positive(self.load_resistance_ohm, name="load_resistance_ohm")
        ensure_positive(self.source_impedance_ohm, name="source_impedance_ohm")
        if not math.isfinite(self.load_reactance_ohm):
            raise ValueError("load_reactance_ohm must be finite")
        origin = self.origin.strip() if self.origin is not None else None
        if origin is not None and len(origin) > 64:
            raise ValueError("origin must not exceed 64 characters")
        object.__setattr__(self, "origin", origin or None)

    @property
    def load_impedance_ohm(self) -> complex:
        return complex(self.load_resistance_ohm, self.load_reactance_ohm)


def matching_network_design_from_frequency(
    frequency: FrequencyResult,
    spec: SimulationSpec,
) -> MatchingNetworkDesign | None:
    """Return the raw primary-side design point for one frequency result.

    The solver's source result is the antenna-side feed impedance. The ideal
    transformer ratio is removed so the target is the load seen by the matching
    network. The post-processed ``FrequencyResult.impedance_ohm`` is deliberately
    not used because it already includes the matching network and feed line.
    """

    source = next(
        (item for item in frequency.source_results if item.tag == frequency.feed_tag),
        None,
    )
    if source is None and frequency.source_results:
        source = frequency.source_results[0]
    if source is None:
        return None
    impedance = source.impedance_ohm / spec.feed_transformer_ratio
    if not (math.isfinite(impedance.real) and math.isfinite(impedance.imag)):
        return None
    if impedance.real <= 0.0:
        return None
    return MatchingNetworkDesign(
        frequency_hz=frequency.frequency_hz,
        load_resistance_ohm=impedance.real,
        load_reactance_ohm=impedance.imag,
        source_impedance_ohm=spec.reference_impedance_ohm,
        origin=MATCHING_DESIGN_ORIGIN_SIMULATION,
    )
