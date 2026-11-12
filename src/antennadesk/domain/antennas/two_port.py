# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Two-port ABCD helpers for feed-line and matching-network cascades."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_positive


@dataclass(frozen=True, slots=True)
class Abcd:
    """A two-port network in ABCD (transmission) form.

    The port convention is ``[V1, I1] = [[A, B], [C, D]] [V2, I2]`` with the
    output current flowing into the load.  Cascades multiply from input to
    output.
    """

    a: complex = 1.0 + 0.0j
    b: complex = 0.0 + 0.0j
    c: complex = 0.0 + 0.0j
    d: complex = 1.0 + 0.0j

    def __matmul__(self, other: Abcd) -> Abcd:
        return Abcd(
            a=self.a * other.a + self.b * other.c,
            b=self.a * other.b + self.b * other.d,
            c=self.c * other.a + self.d * other.c,
            d=self.c * other.b + self.d * other.d,
        )

    @classmethod
    def series(cls, impedance_ohm: complex) -> Abcd:
        return cls(a=1.0 + 0.0j, b=impedance_ohm, c=0.0 + 0.0j, d=1.0 + 0.0j)

    @classmethod
    def shunt(cls, admittance_s: complex) -> Abcd:
        return cls(a=1.0 + 0.0j, b=0.0 + 0.0j, c=admittance_s, d=1.0 + 0.0j)

    def input_impedance(self, load_impedance_ohm: complex) -> complex:
        denominator = self.c * load_impedance_ohm + self.d
        if abs(denominator) < 1e-18:
            raise ValueError("the two-port input impedance is singular")
        return (self.a * load_impedance_ohm + self.b) / denominator


def transducer_gain_db(
    cascade: Abcd,
    source_impedance_ohm: float,
    load_impedance_ohm: complex,
) -> float:
    """Return the source-to-load transducer gain in dB.

    The source impedance is real.  The result includes source mismatch, the
    two-port loss, and load mismatch.  A non-positive or singular gain returns
    ``-inf``.
    """

    ensure_positive(source_impedance_ohm, name="source_impedance_ohm")
    if load_impedance_ohm.real <= 0.0:
        return -math.inf
    denominator = (
        cascade.a * load_impedance_ohm
        + cascade.b
        + source_impedance_ohm * (cascade.c * load_impedance_ohm + cascade.d)
    )
    denominator_magnitude = abs(denominator)
    if denominator_magnitude < 1e-18:
        return -math.inf
    gain = (
        4.0
        * source_impedance_ohm
        * load_impedance_ohm.real
        / (denominator_magnitude * denominator_magnitude)
    )
    if not math.isfinite(gain) or gain <= 0.0:
        return -math.inf
    return 10.0 * math.log10(gain)


def dissipative_loss_db(
    cascade: Abcd,
    source_impedance_ohm: float,
    load_impedance_ohm: complex,
) -> float:
    """Return the power dissipated inside a passive two-port in dB.

    The result is the ratio between the power entering the two-port and the
    power delivered to its load, evaluated with the actual source and load
    impedances. Mismatch at the input is not counted as dissipation; it changes
    both powers by the same factor. A lossless network returns approximately
    zero even with a mismatched load.
    """

    ensure_positive(source_impedance_ohm, name="source_impedance_ohm")
    if load_impedance_ohm.real <= 0.0:
        return math.inf
    input_impedance = cascade.input_impedance(load_impedance_ohm)
    if input_impedance.real <= 0.0:
        return math.inf
    denominator = source_impedance_ohm + input_impedance
    if abs(denominator) < 1e-18:
        return math.inf
    input_current = 1.0 / denominator
    input_power = 0.5 * abs(input_current) ** 2 * input_impedance.real
    output_denominator = cascade.c * load_impedance_ohm + cascade.d
    if abs(output_denominator) < 1e-18:
        return math.inf
    output_current = input_current / output_denominator
    output_power = 0.5 * abs(output_current) ** 2 * load_impedance_ohm.real
    if input_power <= 0.0 or output_power <= 0.0:
        return math.inf
    loss = 10.0 * math.log10(input_power / output_power)
    return max(0.0, loss)


def reflection_loss_db(
    impedance_ohm: complex,
    reference_impedance_ohm: float,
) -> float:
    """Return the mismatch loss for a load relative to a real reference."""

    ensure_positive(reference_impedance_ohm, name="reference_impedance_ohm")
    denominator = impedance_ohm + reference_impedance_ohm
    if abs(denominator) < 1e-18:
        return math.inf
    reflection = (impedance_ohm - reference_impedance_ohm) / denominator
    reflected_power = abs(reflection) ** 2
    if reflected_power >= 1.0:
        return math.inf
    return -10.0 * math.log10(1.0 - reflected_power)
