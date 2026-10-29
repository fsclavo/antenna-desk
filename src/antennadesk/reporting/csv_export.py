# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""CSV export for normalized simulation results."""

from __future__ import annotations

import math
from pathlib import Path

from ..domain.simulation.result import SimulationResult

CSV_HEADER = (
    "frequency_hz,frequency_mhz,resistance_ohm,reactance_ohm,"
    "impedance_magnitude_ohm,swr,input_power_w,max_gain_dbi"
)


def result_to_csv(result: SimulationResult) -> str:
    lines = [CSV_HEADER]
    for frequency in result.frequencies:
        gains = [
            point.gain_total_db for point in frequency.far_field if point.gain_total_db is not None
        ]
        max_gain = max(gains) if gains else None
        swr = "inf" if math.isinf(frequency.swr) else f"{frequency.swr:.6f}"
        gain = "" if max_gain is None else f"{max_gain:.4f}"
        lines.append(
            ",".join(
                [
                    f"{frequency.frequency_hz:.6f}",
                    f"{frequency.frequency_hz / 1e6:.9f}",
                    f"{frequency.impedance_ohm.real:.6f}",
                    f"{frequency.impedance_ohm.imag:.6f}",
                    f"{abs(frequency.impedance_ohm):.6f}",
                    swr,
                    f"{frequency.input_power_w:.9g}",
                    gain,
                ]
            )
        )
    return "\n".join(lines) + "\n"


def write_csv(result: SimulationResult, path: Path) -> None:
    path.write_text(result_to_csv(result), encoding="utf-8", newline="\n")
