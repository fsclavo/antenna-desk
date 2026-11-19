# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Gain, directivity, and link-budget summary rows."""

from __future__ import annotations

import math

from ..domain.simulation.metrics import decision_metrics
from ..domain.simulation.result import FrequencyResult, SimulationResult


def representative_gain_frequency(result: SimulationResult | None) -> FrequencyResult | None:
    """Return the frequency with the highest realized gain, then power gain."""

    if result is None or not result.frequencies:
        return None
    realized = [
        frequency for frequency in result.frequencies if frequency.realized_gain_db is not None
    ]
    if realized:
        return max(
            realized,
            key=lambda frequency: (
                frequency.realized_gain_db if frequency.realized_gain_db is not None else -1e30
            ),
        )
    with_pattern = [
        frequency
        for frequency in result.frequencies
        if any(point.gain_total_db is not None for point in frequency.far_field)
    ]
    if with_pattern:
        return max(
            with_pattern,
            key=lambda frequency: max(
                (
                    point.gain_total_db if point.gain_total_db is not None else -1e30
                    for point in frequency.far_field
                ),
                default=-1e30,
            ),
        )
    return result.frequencies[0]


def gain_metric_rows(result: SimulationResult | None) -> tuple[tuple[str, str], ...]:
    """Return report-ready rows for gain, directivity, and link losses."""

    if result is None:
        return ()
    rows: list[tuple[str, str]] = []
    max_gain = result.max_total_gain_db
    max_directivity = result.max_directivity_db
    max_realized = result.max_realized_gain_db
    if max_gain is not None:
        rows.append(("Max power gain (NEC)", f"{max_gain:.2f} dBi"))
    if max_directivity is not None:
        rows.append(("Max directivity", f"{max_directivity:.2f} dBi"))
    if max_realized is not None:
        rows.append(("Max realized gain", f"{max_realized:.2f} dBi"))

    frequency = representative_gain_frequency(result)
    if frequency is not None:
        rows.append(("Link metrics at", f"{frequency.frequency_hz / 1e6:.6f} MHz"))
        if frequency.mismatch_loss_db is not None:
            rows.append(("Mismatch loss", f"{frequency.mismatch_loss_db:.3f} dB"))
        if frequency.feed_line_loss_db is not None:
            rows.append(("Feed-line loss (matched)", f"{frequency.feed_line_loss_db:.3f} dB"))
        if frequency.network_loss_db is not None:
            rows.append(("Network loss", f"{frequency.network_loss_db:.3f} dB"))
        if frequency.balun_loss_db is not None:
            rows.append(("Balun/unun loss", f"{frequency.balun_loss_db:.3f} dB"))
        if frequency.transformer_loss_db is not None:
            rows.append(("Transformer loss", f"{frequency.transformer_loss_db:.3f} dB"))
        losses = [
            value
            for value in (
                frequency.mismatch_loss_db,
                frequency.feed_line_loss_db,
                frequency.network_loss_db,
                frequency.balun_loss_db,
                frequency.transformer_loss_db,
            )
            if value is not None
        ]
        if losses:
            rows.append(("Total feed-chain loss", f"{sum(losses):.3f} dB"))
    return tuple(rows)


def decision_metric_rows(result: SimulationResult | None) -> tuple[tuple[str, str], ...]:
    """Return report-ready decision metrics at the representative frequency."""

    frequency = representative_gain_frequency(result)
    if result is None or frequency is None:
        return ()
    metrics = decision_metrics(frequency, result.frequencies)
    bandwidth = metrics.swr_bandwidth_2_1
    if bandwidth.bandwidth_hz is not None:
        bandwidth_text = f"{bandwidth.bandwidth_hz / 1e6:.4f} MHz"
    elif bandwidth.lower_hz is not None:
        bandwidth_text = "unbracketed (sweep edge)"
    else:
        bandwidth_text = "unavailable"

    def metric(value: float | None, suffix: str) -> str:
        if value is None:
            return "unavailable"
        if math.isinf(value):
            return "infinite"
        return f"{value:.2f} {suffix}"

    return (
        ("2:1 SWR bandwidth", bandwidth_text),
        ("HPBW azimuth", metric(metrics.hpbw_azimuth.width_deg, "deg")),
        ("HPBW elevation", metric(metrics.hpbw_elevation.width_deg, "deg")),
        ("Front-to-back", metric(metrics.front_to_back_db, "dB")),
        ("Sidelobe level", metric(metrics.sidelobe_level_db, "dB")),
        ("Takeoff angle", metric(metrics.takeoff_deg, "deg")),
        ("Efficiency", metric(metrics.efficiency_percent, "%")),
        ("Axial ratio", metric(metrics.axial_ratio_db, "dB")),
        ("Polarization sense", metrics.polarization_sense or "unavailable"),
        ("Co-pol CP gain", metric(metrics.cp_gain_db, "dBi")),
        (
            "Cross-pol discrimination",
            metric(metrics.cross_polar_discrimination_db, "dB"),
        ),
        ("Pattern resolution", metric(metrics.pattern_resolution_deg, "deg")),
    )
