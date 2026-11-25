# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Transmission-line two-port connections between antenna segments."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..common.units import ensure_non_negative, ensure_positive


@dataclass(frozen=True, slots=True)
class TransmissionLine:
    """A lossless transmission line connecting two points on the structure.

    The connection points are wire identifiers plus offsets from the wire
    start.  ``length_m`` is the physical line length and ``velocity_factor``
    converts it to the electrical length used by the solver:

    ``electrical_length_m = length_m / velocity_factor``.

    The line is a mathematical two-port, not a radiating wire.  NEC-2's TL card
    does not model distributed loss; use a separate feed-line post-processing
    model when line loss matters.

    ``phase_reversal`` swaps the polarity of the two-port.  It is a generic
    line property, not a log-periodic-specific one: the NEC adapter maps it to
    the negative-characteristic-impedance convention.
    """

    id: str
    start_wire_id: str
    start_offset_m: float
    end_wire_id: str
    end_offset_m: float
    characteristic_impedance_ohm: float
    length_m: float
    velocity_factor: float = 1.0
    phase_reversal: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("transmission line id must not be empty")
        if not self.start_wire_id.strip():
            raise ValueError("transmission line start_wire_id must not be empty")
        if not self.end_wire_id.strip():
            raise ValueError("transmission line end_wire_id must not be empty")
        ensure_non_negative(self.start_offset_m, name="start_offset_m")
        ensure_non_negative(self.end_offset_m, name="end_offset_m")
        ensure_positive(
            self.characteristic_impedance_ohm,
            name="characteristic_impedance_ohm",
        )
        ensure_positive(self.length_m, name="length_m")
        ensure_positive(self.velocity_factor, name="velocity_factor")
        if self.velocity_factor > 1.0:
            raise ValueError("velocity_factor must not exceed 1")

    @property
    def electrical_length_m(self) -> float:
        return self.length_m / self.velocity_factor


def mismatched_line_loss_db(
    *,
    length_m: float,
    loss_db_per_100m: float,
    characteristic_impedance_ohm: float,
    load_impedance_ohm: complex,
) -> float:
    """Return matched plus load-mismatch loss for one line.

    ``a = 10 ** (-matched_loss_db / 10)`` is the matched power attenuation.
    With load reflection ``Gamma_L``, the input reflection magnitude is
    ``|Gamma_L| * a`` and the total loss is::

        matched - 10 log10((1 - |Gamma_L|^2) / (1 - |Gamma_L|^2 a^2))

    The result is clamped to at least the matched loss. The estimate assumes
    the source delivers the same incident power; the input-impedance shift
    caused by the loss is not re-solved. Active or singular loads fall back to
    the matched loss.
    """

    matched = loss_db_per_100m * length_m / 100.0
    if matched <= 0.0:
        return 0.0
    denominator = load_impedance_ohm + characteristic_impedance_ohm
    if abs(denominator) <= 1e-12:
        return matched
    gamma = abs((load_impedance_ohm - characteristic_impedance_ohm) / denominator)
    if gamma <= 0.0 or gamma >= 1.0:
        return matched
    attenuation = 10.0 ** (-matched / 10.0)
    gamma_in = gamma * attenuation
    numerator = 1.0 - gamma * gamma
    denominator_power = 1.0 - gamma_in * gamma_in
    if numerator <= 0.0 or denominator_power <= 0.0:
        return matched
    extra_db = max(0.0, -10.0 * math.log10(numerator / denominator_power))
    return matched + extra_db
