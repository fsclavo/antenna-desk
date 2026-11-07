# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.reporting.result_summary import (
    gain_metric_rows,
    representative_gain_frequency,
)


def _result() -> SimulationResult:
    point = FarFieldPoint(
        theta_deg=90.0,
        phi_deg=0.0,
        gain_vertical_db=2.15,
        gain_horizontal_db=None,
        gain_total_db=2.15,
        axial_ratio=1.0,
        tilt_deg=0.0,
        polarization="linear",
        e_theta_magnitude_v_per_m=None,
        e_theta_phase_deg=None,
        e_phi_magnitude_v_per_m=None,
        e_phi_phase_deg=None,
    )
    frequency = FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=1,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=0.001,
        far_field=(point,),
        directivity_db=2.20,
        realized_gain_db=1.85,
        mismatch_loss_db=0.20,
        feed_line_loss_db=0.10,
        network_loss_db=0.05,
        balun_loss_db=0.03,
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(frequency,),
    )


def test_gain_metrics_report_power_directivity_and_realized_gain() -> None:
    rows = dict(gain_metric_rows(_result()))

    assert rows["Max power gain (NEC)"] == "2.15 dBi"
    assert rows["Max directivity"] == "2.20 dBi"
    assert rows["Max realized gain"] == "1.85 dBi"
    assert rows["Mismatch loss"] == "0.200 dB"
    assert rows["Feed-line loss (matched)"] == "0.100 dB"
    assert rows["Network loss"] == "0.050 dB"
    assert rows["Balun/unun loss"] == "0.030 dB"
    assert rows["Link metrics at"] == "7.100000 MHz"


def test_representative_frequency_prefers_max_realized_gain() -> None:
    result = _result()

    assert representative_gain_frequency(result) is result.frequencies[0]
    assert representative_gain_frequency(None) is None
