# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measured feedpoint common-mode choke impedance for end-fed antennas."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_non_negative, ensure_positive


@dataclass(frozen=True, slots=True)
class CommonModeChoke:
    """A measured series common-mode impedance at the feedpoint.

    ``resistance_ohm`` and ``reactance_ohm`` are the series equivalent values
    measured at ``measurement_frequency_hz``. The model holds the resistance
    constant and realizes a positive reactance as a series inductance or a
    negative reactance as a series capacitance, so the reactance changes with
    frequency across a sweep. This is a bounded feedpoint model, not a
    frequency-interpolated choke table and not a shack-end choke.
    """

    enabled: bool = False
    measurement_frequency_hz: float = 7_100_000.0
    resistance_ohm: float = 0.0
    reactance_ohm: float = 0.0
    source: str = ""

    def __post_init__(self) -> None:
        ensure_positive(self.measurement_frequency_hz, name="measurement_frequency_hz")
        ensure_non_negative(self.resistance_ohm, name="resistance_ohm")
        source = self.source.strip()
        if self.enabled:
            if self.resistance_ohm == 0.0 and self.reactance_ohm == 0.0:
                raise ValueError("an enabled common-mode choke needs a non-zero R or X")
            if not source:
                raise ValueError("an enabled common-mode choke requires a measurement source")
        object.__setattr__(self, "source", source)

    @property
    def is_active(self) -> bool:
        return self.enabled and (self.resistance_ohm > 0.0 or self.reactance_ohm != 0.0)

    @property
    def impedance_ohm(self) -> complex:
        return complex(self.resistance_ohm, self.reactance_ohm)

    @property
    def series_inductance_h(self) -> float:
        if self.reactance_ohm <= 0.0:
            return 0.0
        omega = 2.0 * math.pi * self.measurement_frequency_hz
        return float(self.reactance_ohm / omega)

    @property
    def series_capacitance_f(self) -> float:
        if self.reactance_ohm >= 0.0:
            return 0.0
        omega = 2.0 * math.pi * self.measurement_frequency_hz
        return float(-1.0 / (omega * self.reactance_ohm))

    @property
    def is_predominantly_reactive(self) -> bool:
        return abs(self.reactance_ohm) > self.resistance_ohm
