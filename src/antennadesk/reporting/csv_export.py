# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""CSV export for normalized simulation results."""

from __future__ import annotations

import math
from pathlib import Path

from ..domain.simulation.band_result import BandAnalysisResult
from ..domain.simulation.metrics import decision_metrics, swr_bandwidth_rows
from ..domain.simulation.result import SimulationResult

CSV_HEADER = (
    "frequency_hz,frequency_mhz,resistance_ohm,reactance_ohm,"
    "impedance_magnitude_ohm,swr,input_power_w,max_gain_dbi,"
    "directivity_dbi,realized_gain_dbi,mismatch_loss_db,"
    "feed_line_loss_db,network_loss_db,balun_loss_db,transformer_loss_db,"
    "swr_2_1_bandwidth_hz,swr_2_1_bracketed,hpbw_azimuth_deg,"
    "hpbw_elevation_deg,front_to_back_db,sidelobe_level_db,takeoff_deg,"
    "efficiency_percent,axial_ratio_db,polarization_sense,cp_gain_dbi,"
    "cross_polar_discrimination_db,pattern_resolution_deg"
)


def _result_rows(result: SimulationResult) -> list[str]:
    rows: list[str] = []
    bandwidths = swr_bandwidth_rows(
        [frequency.frequency_hz for frequency in result.frequencies],
        [frequency.swr for frequency in result.frequencies],
    )
    for index, frequency in enumerate(result.frequencies):
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
        balun = "" if frequency.balun_loss_db is None else f"{frequency.balun_loss_db:.6f}"
        transformer = (
            "" if frequency.transformer_loss_db is None else f"{frequency.transformer_loss_db:.6f}"
        )
        metrics = decision_metrics(
            frequency,
            result.frequencies,
            bandwidth=bandwidths[index],
        )
        rows.append(
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
                    balun,
                    transformer,
                    (
                        ""
                        if metrics.swr_bandwidth_2_1.bandwidth_hz is None
                        else f"{metrics.swr_bandwidth_2_1.bandwidth_hz:.6f}"
                    ),
                    str(metrics.swr_bandwidth_2_1.bracketed).lower(),
                    _metric(metrics.hpbw_azimuth.width_deg),
                    _metric(metrics.hpbw_elevation.width_deg),
                    _metric(metrics.front_to_back_db),
                    _metric(metrics.sidelobe_level_db),
                    _metric(metrics.takeoff_deg),
                    _metric(metrics.efficiency_percent),
                    _metric(metrics.axial_ratio_db),
                    metrics.polarization_sense or "",
                    _metric(metrics.cp_gain_db),
                    _metric(metrics.cross_polar_discrimination_db),
                    _metric(metrics.pattern_resolution_deg),
                ]
            )
        )
    return rows


def _metric(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return ""
    return f"{value:.6f}"


def result_to_csv(result: SimulationResult) -> str:
    return "\n".join([CSV_HEADER, *_result_rows(result)]) + "\n"


SOURCES_HEADER = (
    "frequency_hz,frequency_mhz,source,wire_id,offset_m,tag,segment,"
    "amplitude,phase_deg,voltage_real_v,voltage_imag_v,current_real_a,"
    "current_imag_a,impedance_real_ohm,impedance_imag_ohm,power_w"
)


def _source_rows(result: SimulationResult) -> list[str]:
    rows: list[str] = []
    for frequency in result.frequencies:
        for source_index, source in enumerate(frequency.source_results, start=1):
            rows.append(
                ",".join(
                    [
                        f"{frequency.frequency_hz:.6f}",
                        f"{frequency.frequency_hz / 1e6:.9f}",
                        f"S{source_index}",
                        source.wire_id,
                        f"{source.offset_m:.6f}",
                        str(source.tag),
                        str(source.segment),
                        f"{source.amplitude:.6f}",
                        f"{source.phase_deg:.6f}",
                        f"{source.voltage_v.real:.9g}",
                        f"{source.voltage_v.imag:.9g}",
                        f"{source.current_a.real:.9g}",
                        f"{source.current_a.imag:.9g}",
                        f"{source.impedance_ohm.real:.6f}",
                        f"{source.impedance_ohm.imag:.6f}",
                        f"{source.power_w:.9g}",
                    ]
                )
            )
    return rows


def sources_to_csv(result: SimulationResult) -> str:
    return "\n".join([SOURCES_HEADER, *_source_rows(result)]) + "\n"


def band_analysis_sources_to_csv(analysis: BandAnalysisResult) -> str:
    lines = [f"band,{SOURCES_HEADER}"]
    for band in analysis.bands:
        lines.extend(f"{band.band.name},{row}" for row in _source_rows(band.result))
    return "\n".join(lines) + "\n"


def write_sources_csv(result: SimulationResult, path: Path) -> None:
    path.write_text(sources_to_csv(result), encoding="utf-8", newline="\n")


def write_band_analysis_sources_csv(analysis: BandAnalysisResult, path: Path) -> None:
    path.write_text(band_analysis_sources_to_csv(analysis), encoding="utf-8", newline="\n")


def band_analysis_to_csv(analysis: BandAnalysisResult) -> str:
    lines = [f"band,{CSV_HEADER}"]
    for band in analysis.bands:
        lines.extend(f"{band.band.name},{row}" for row in _result_rows(band.result))
    return "\n".join(lines) + "\n"


def write_csv(result: SimulationResult, path: Path) -> None:
    path.write_text(result_to_csv(result), encoding="utf-8", newline="\n")


def write_band_analysis_csv(analysis: BandAnalysisResult, path: Path) -> None:
    path.write_text(band_analysis_to_csv(analysis), encoding="utf-8", newline="\n")


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


def _pattern_rows(result: SimulationResult) -> list[str]:
    rows: list[str] = []
    for frequency in result.frequencies:
        for point in frequency.far_field:
            rows.append(
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
    return rows


def pattern_to_csv(result: SimulationResult) -> str:
    return "\n".join([PATTERN_HEADER, *_pattern_rows(result)]) + "\n"


def band_analysis_pattern_to_csv(analysis: BandAnalysisResult) -> str:
    lines = [f"band,{PATTERN_HEADER}"]
    for band in analysis.bands:
        lines.extend(f"{band.band.name},{row}" for row in _pattern_rows(band.result))
    return "\n".join(lines) + "\n"


def write_pattern_csv(result: SimulationResult, path: Path) -> None:
    path.write_text(pattern_to_csv(result), encoding="utf-8", newline="\n")


def write_band_analysis_pattern_csv(analysis: BandAnalysisResult, path: Path) -> None:
    path.write_text(
        band_analysis_pattern_to_csv(analysis),
        encoding="utf-8",
        newline="\n",
    )
