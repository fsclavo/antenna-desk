# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ideal L-network evaluated at the antenna feedpoint."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_non_negative, ensure_positive


@dataclass(frozen=True, slots=True)
class LNetwork:
    """A lossless L matching network.

    The series branch is between the antenna and the shunt branch.  When
    ``shunt_at_input`` is true the shunt branch is on the transmitter side;
    otherwise it is on the antenna side.
    """

    series_inductance_h: float = 0.0
    series_capacitance_f: float = 0.0
    shunt_inductance_h: float = 0.0
    shunt_capacitance_f: float = 0.0
    shunt_at_input: bool = False

    def __post_init__(self) -> None:
        for name, value in (
            ("series_inductance_h", self.series_inductance_h),
            ("series_capacitance_f", self.series_capacitance_f),
            ("shunt_inductance_h", self.shunt_inductance_h),
            ("shunt_capacitance_f", self.shunt_capacitance_f),
        ):
            ensure_non_negative(value, name=name)
        series = self.series_inductance_h > 0.0 or self.series_capacitance_f > 0.0
        shunt = self.shunt_inductance_h > 0.0 or self.shunt_capacitance_f > 0.0
        if series != shunt:
            raise ValueError("an L-network needs both a series and a shunt element")
        if series and shunt and self.series_inductance_h > 0.0 and self.series_capacitance_f > 0.0:
            raise ValueError("the series branch must use either L or C, not both")
        if series and shunt and self.shunt_inductance_h > 0.0 and self.shunt_capacitance_f > 0.0:
            raise ValueError("the shunt branch must use either L or C, not both")

    @property
    def is_active(self) -> bool:
        return (
            self.series_inductance_h > 0.0
            or self.series_capacitance_f > 0.0
            or self.shunt_inductance_h > 0.0
            or self.shunt_capacitance_f > 0.0
        )

    def input_impedance(self, load_impedance_ohm: complex, frequency_hz: float) -> complex:
        """Return the impedance seen at the network input."""

        ensure_positive(frequency_hz, name="frequency_hz")
        if not self.is_active:
            return load_impedance_ohm
        omega = 2.0 * math.pi * frequency_hz
        series = complex(0.0, 0.0)
        if self.series_inductance_h:
            series += complex(0.0, omega * self.series_inductance_h)
        if self.series_capacitance_f:
            series += complex(0.0, -1.0 / (omega * self.series_capacitance_f))
        shunt = complex(0.0, 0.0)
        if self.shunt_inductance_h:
            shunt += complex(0.0, -1.0 / (omega * self.shunt_inductance_h))
        if self.shunt_capacitance_f:
            shunt += complex(0.0, omega * self.shunt_capacitance_f)
        if self.shunt_at_input:
            return 1.0 / (shunt + 1.0 / (series + load_impedance_ohm))
        return series + 1.0 / (shunt + 1.0 / load_impedance_ohm)
