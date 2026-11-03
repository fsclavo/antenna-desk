# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""CSV export for normalized simulation results."""

from __future__ import annotations

import math
from pathlib import Path

from ..domain.simulation.result import SimulationResult

CSV_HEADER = (
    "frequency_hz,frequency_mhz,resistance_ohm,reactance_ohm,"
    "impedance_magnitude_ohm,swr,input_power_w,max_gain_dbi,"
    "directivity_dbi,realized_gain_dbi,mismatch_loss_db,"
    "feed_line_loss_db,network_loss_db"
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
        directivity = "" if frequency.directivity_db is None else f"{frequency.directivity_db:.4f}"
        realized = "" if frequency.realized_gain_db is None else f"{frequency.realized_gain_db:.4f}"
        mismatch = "" if frequency.mismatch_loss_db is None else f"{frequency.mismatch_loss_db:.6f}"
        line_loss = (
            "" if frequency.feed_line_loss_db is None else f"{frequency.feed_line_loss_db:.6f}"
        )
        network = "" if frequency.network_loss_db is None else f"{frequency.network_loss_db:.6f}"
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
                    directivity,
                    realized,
                    mismatch,
                    line_loss,
                    network,
                ]
            )
        )
    return "\n".join(lines) + "\n"


def write_csv(result: SimulationResult, path: Path) -> None:
    path.write_text(result_to_csv(result), encoding="utf-8", newline="\n")


PATTERN_HEADER = (
    "frequency_hz,frequency_mhz,theta_deg,phi_deg,"
    "gain_vertical_db,gain_horizontal_db,gain_total_db,"
    "axial_ratio,tilt_deg,polarization,"
    "e_theta_magnitude_v_per_m,e_theta_phase_deg,"
    "e_phi_magnitude_v_per_m,e_phi_phase_deg"
)


def _optional(value: float | None) -> str:
    if value is None or value <= -100.0:
        return ""
    return f"{value:.6f}"


def pattern_to_csv(result: SimulationResult) -> str:
    lines = [PATTERN_HEADER]
    for frequency in result.frequencies:
        for point in frequency.far_field:
            lines.append(
                ",".join(
                    [
                        f"{frequency.frequency_hz:.6f}",
                        f"{frequency.frequency_hz / 1e6:.9f}",
                        f"{point.theta_deg:.6f}",
                        f"{point.phi_deg:.6f}",
                        _optional(point.gain_vertical_db),
                        _optional(point.gain_horizontal_db),
                        _optional(point.gain_total_db),
                        _optional(point.axial_ratio),
                        _optional(point.tilt_deg),
                        point.polarization or "",
                        _optional(point.e_theta_magnitude_v_per_m),
                        _optional(point.e_theta_phase_deg),
                        _optional(point.e_phi_magnitude_v_per_m),
                        _optional(point.e_phi_phase_deg),
                    ]
                )
            )
    return "\n".join(lines) + "\n"


def write_pattern_csv(result: SimulationResult, path: Path) -> None:
    path.write_text(pattern_to_csv(result), encoding="utf-8", newline="\n")
