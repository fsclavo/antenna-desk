# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Transmission-line two-port connections between antenna segments."""

from __future__ import annotations

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
    """

    id: str
    start_wire_id: str
    start_offset_m: float
    end_wire_id: str
    end_offset_m: float
    characteristic_impedance_ohm: float
    length_m: float
    velocity_factor: float = 1.0

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
