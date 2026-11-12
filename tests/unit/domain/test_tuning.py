# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded tuning sensitivity calculations."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from antennadesk.domain.design.tuning import (
    TuningProbe,
    TuningReferenceKind,
    TuningRequest,
    TuningStatus,
    build_tuning_estimate,
    measurement_tuning_reference,
    tuning_sweep_bounds,
    with_tuning_verification,
)
from antennadesk.domain.measurement import Measurement, MeasurementPoint


def _measurement(*points: MeasurementPoint) -> Measurement:
    return Measurement(
        id=UUID("00000000-0000-0000-0000-000000000041"),
        name="Field sweep",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=points,
    )


def _request(*, target: float = 7_100_000.0, measured: float = 7_050_000.0) -> TuningRequest:
    return TuningRequest(
        target_frequency_hz=target,
        measured_frequency_hz=measured,
        measured_kind=TuningReferenceKind.RESONANCE,
        current_dimension_m=20.0,
        max_adjustment_m=0.1,
    )


def _probe(
    dimension: float,
    resonance: float | None,
    swr: float | None = 1.2,
) -> TuningProbe:
    return TuningProbe(
        dimension_m=dimension,
        resonance_hz=resonance,
        swr_at_target=swr,
        impedance_at_target_ohm=None,
    )


def test_measurement_reference_prefers_the_nearest_resonance() -> None:
    measurement = _measurement(
        MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        MeasurementPoint(14_000_000.0, complex(50.0, -10.0)),
        MeasurementPoint(14_100_000.0, complex(50.0, 10.0)),
    )

    frequency, kind = measurement_tuning_reference(measurement, 14_050_000.0)

    assert frequency == pytest.approx(14_050_000.0)
    assert kind is TuningReferenceKind.RESONANCE


def test_measurement_reference_falls_back_to_minimum_swr() -> None:
    measurement = _measurement(
        MeasurementPoint(7_000_000.0, complex(75.0, 10.0)),
        MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        MeasurementPoint(7_200_000.0, complex(100.0, 10.0)),
    )

    frequency, kind = measurement_tuning_reference(measurement, 7_150_000.0)

    assert frequency == pytest.approx(7_100_000.0)
    assert kind is TuningReferenceKind.MIN_SWR


def test_sweep_bounds_cover_target_and_measurement() -> None:
    start, stop = tuning_sweep_bounds(7_100_000.0, 7_500_000.0)

    assert start < 7_100_000.0 < stop
    assert start < 7_500_000.0 < stop


def test_estimate_proposes_a_bounded_shortening() -> None:
    proposal = build_tuning_estimate(
        _request(),
        current=_probe(20.0, 7_100_000.0),
        low=_probe(19.9, 7_200_000.0),
        high=_probe(20.1, 7_000_000.0),
    )

    assert proposal.status is TuningStatus.PROPOSED
    assert proposal.slope_hz_per_m == pytest.approx(-1_000_000.0)
    assert proposal.proposed_change_m == pytest.approx(-0.05)
    assert proposal.proposed_dimension_m == pytest.approx(19.95)
    assert proposal.clipped is False


def test_estimate_clips_to_the_adjustment_bound() -> None:
    proposal = build_tuning_estimate(
        _request(target=7_500_000.0, measured=7_000_000.0),
        current=_probe(20.0, 7_100_000.0),
        low=_probe(19.9, 7_200_000.0),
        high=_probe(20.1, 7_000_000.0),
    )

    assert proposal.status is TuningStatus.PROPOSED
    assert proposal.proposed_change_m == pytest.approx(-0.1)
    assert proposal.clipped is True


def test_estimate_reports_no_change_and_no_sensitivity() -> None:
    no_change = build_tuning_estimate(
        _request(target=7_100_000.0, measured=7_100_000.0),
        current=_probe(20.0, 7_100_000.0),
        low=_probe(19.9, 7_200_000.0),
        high=_probe(20.1, 7_000_000.0),
    )
    no_sensitivity = build_tuning_estimate(
        _request(),
        current=_probe(20.0, 7_100_000.0),
        low=_probe(19.9, 7_100_000.1),
        high=_probe(20.1, 7_100_000.2),
    )

    assert no_change.status is TuningStatus.NO_CHANGE
    assert no_sensitivity.status is TuningStatus.NO_SENSITIVITY


def test_estimate_reports_no_resonance() -> None:
    proposal = build_tuning_estimate(
        _request(),
        current=_probe(20.0, None),
        low=_probe(19.9, None),
        high=_probe(20.1, None),
    )

    assert proposal.status is TuningStatus.NO_RESONANCE


def test_verification_attaches_predictions() -> None:
    proposal = build_tuning_estimate(
        _request(),
        current=_probe(20.0, 7_100_000.0),
        low=_probe(19.9, 7_200_000.0),
        high=_probe(20.1, 7_000_000.0),
    )

    verified = with_tuning_verification(
        proposal,
        _probe(19.95, 7_050_000.0, swr=1.1),
    )

    assert verified.predicted_resonance_hz == pytest.approx(7_050_000.0)
    assert verified.predicted_swr == pytest.approx(1.1)
    assert verified.message_key == "tuning.message.verified"
    assert len(verified.probes) == 4
