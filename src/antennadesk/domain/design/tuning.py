# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded sensitivity-based tuning from a measured resonance.

The calculation is intentionally local: it probes the solver around the
current primary dimension, estimates the resonance slope, and proposes at most
the user-selected adjustment. It never claims that a physical antenna will move
by the predicted amount; the UI must present the estimate as model guidance and
require a new measurement after trimming.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from ..measurement import Measurement, swr_for_impedance
from ..measurement_comparison import interpolate_impedance
from ..simulation.resonance import find_resonances

DEFAULT_SLOPE_THRESHOLD_HZ_PER_M = 1_000.0
MIN_TUNING_DIMENSION_M = 0.01


class TuningStatus(StrEnum):
    PROPOSED = "proposed"
    NO_CHANGE = "no_change"
    NO_SENSITIVITY = "no_sensitivity"
    NO_RESONANCE = "no_resonance"
    CANCELLED = "cancelled"
    ERROR = "error"


class TuningReferenceKind(StrEnum):
    RESONANCE = "resonance"
    MIN_SWR = "min_swr"


@dataclass(frozen=True, slots=True)
class TuningProbe:
    """One solver probe at a candidate primary dimension."""

    dimension_m: float
    resonance_hz: float | None
    swr_at_target: float | None
    impedance_at_target_ohm: complex | None


@dataclass(frozen=True, slots=True)
class TuningRequest:
    target_frequency_hz: float
    measured_frequency_hz: float
    measured_kind: TuningReferenceKind
    current_dimension_m: float
    max_adjustment_m: float
    slope_threshold_hz_per_m: float = DEFAULT_SLOPE_THRESHOLD_HZ_PER_M

    def __post_init__(self) -> None:
        for name, value in (
            ("target_frequency_hz", self.target_frequency_hz),
            ("measured_frequency_hz", self.measured_frequency_hz),
            ("current_dimension_m", self.current_dimension_m),
            ("max_adjustment_m", self.max_adjustment_m),
        ):
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be positive and finite")
        if not math.isfinite(self.slope_threshold_hz_per_m) or (
            self.slope_threshold_hz_per_m < 0.0
        ):
            raise ValueError("slope_threshold_hz_per_m must be non-negative and finite")


@dataclass(frozen=True, slots=True)
class TuningProposal:
    status: TuningStatus
    request: TuningRequest
    probes: tuple[TuningProbe, ...] = ()
    slope_hz_per_m: float | None = None
    proposed_dimension_m: float | None = None
    proposed_change_m: float | None = None
    predicted_resonance_hz: float | None = None
    predicted_swr: float | None = None
    bounds_min_m: float = 0.0
    bounds_max_m: float = 0.0
    clipped: bool = False
    message_key: str = "tuning.message.proposed"
    detail: str = ""


def measurement_tuning_reference(
    measurement: Measurement,
    target_frequency_hz: float,
) -> tuple[float, TuningReferenceKind]:
    """Return the measured frequency to tune and how it was selected."""

    resonances = find_resonances(
        [point.frequency_hz for point in measurement.points],
        [point.impedance_ohm for point in measurement.points],
    )
    if resonances:
        closest = min(
            resonances,
            key=lambda point: abs(point.frequency_hz - target_frequency_hz),
        )
        return closest.frequency_hz, TuningReferenceKind.RESONANCE
    closest_swr = min(
        measurement.points,
        key=lambda point: (
            point.swr(measurement.reference_impedance_ohm),
            abs(point.frequency_hz - target_frequency_hz),
        ),
    )
    return closest_swr.frequency_hz, TuningReferenceKind.MIN_SWR


def tuning_sweep_bounds(
    target_frequency_hz: float,
    measured_frequency_hz: float,
) -> tuple[float, float]:
    """Return a sweep that covers the target and the measured reference."""

    for name, value in (
        ("target_frequency_hz", target_frequency_hz),
        ("measured_frequency_hz", measured_frequency_hz),
    ):
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be positive and finite")
    span = max(
        0.02 * target_frequency_hz,
        2.0 * abs(target_frequency_hz - measured_frequency_hz) + 0.02 * target_frequency_hz,
        50_000.0,
    )
    center = (target_frequency_hz + measured_frequency_hz) / 2.0
    return max(1.0, center - span / 2.0), center + span / 2.0


def _slope_hz_per_m(
    current: TuningProbe,
    low: TuningProbe,
    high: TuningProbe,
) -> float | None:
    if (
        low.resonance_hz is not None
        and high.resonance_hz is not None
        and high.dimension_m > low.dimension_m
    ):
        return (high.resonance_hz - low.resonance_hz) / (high.dimension_m - low.dimension_m)
    if (
        current.resonance_hz is not None
        and high.resonance_hz is not None
        and high.dimension_m > current.dimension_m
    ):
        return (high.resonance_hz - current.resonance_hz) / (high.dimension_m - current.dimension_m)
    if (
        low.resonance_hz is not None
        and current.resonance_hz is not None
        and current.dimension_m > low.dimension_m
    ):
        return (current.resonance_hz - low.resonance_hz) / (current.dimension_m - low.dimension_m)
    return None


def build_tuning_estimate(
    request: TuningRequest,
    *,
    current: TuningProbe,
    low: TuningProbe,
    high: TuningProbe,
) -> TuningProposal:
    """Estimate a bounded dimension change from three local solver probes."""

    bounds_min = max(
        MIN_TUNING_DIMENSION_M,
        request.current_dimension_m - request.max_adjustment_m,
    )
    bounds_max = request.current_dimension_m + request.max_adjustment_m
    probes = (current, low, high)
    slope = _slope_hz_per_m(current, low, high)
    if slope is None:
        return TuningProposal(
            status=TuningStatus.NO_RESONANCE,
            request=request,
            probes=probes,
            bounds_min_m=bounds_min,
            bounds_max_m=bounds_max,
            message_key="tuning.message.no_resonance",
        )
    if abs(slope) < request.slope_threshold_hz_per_m:
        return TuningProposal(
            status=TuningStatus.NO_SENSITIVITY,
            request=request,
            probes=probes,
            slope_hz_per_m=slope,
            bounds_min_m=bounds_min,
            bounds_max_m=bounds_max,
            message_key="tuning.message.no_sensitivity",
        )
    raw_dimension = (
        request.current_dimension_m
        + (request.target_frequency_hz - request.measured_frequency_hz) / slope
    )
    proposed = min(max(raw_dimension, bounds_min), bounds_max)
    change = proposed - request.current_dimension_m
    if abs(change) < 1e-6:
        return TuningProposal(
            status=TuningStatus.NO_CHANGE,
            request=request,
            probes=probes,
            slope_hz_per_m=slope,
            proposed_dimension_m=proposed,
            proposed_change_m=0.0,
            bounds_min_m=bounds_min,
            bounds_max_m=bounds_max,
            message_key="tuning.message.no_change",
        )
    return TuningProposal(
        status=TuningStatus.PROPOSED,
        request=request,
        probes=probes,
        slope_hz_per_m=slope,
        proposed_dimension_m=proposed,
        proposed_change_m=change,
        bounds_min_m=bounds_min,
        bounds_max_m=bounds_max,
        clipped=abs(raw_dimension - proposed) > 1e-12,
        message_key="tuning.message.proposed",
    )


def with_tuning_verification(
    proposal: TuningProposal,
    verification: TuningProbe,
) -> TuningProposal:
    """Attach the solver verification at the proposed dimension."""

    if proposal.status is not TuningStatus.PROPOSED:
        return proposal
    return TuningProposal(
        status=proposal.status,
        request=proposal.request,
        probes=(*proposal.probes, verification),
        slope_hz_per_m=proposal.slope_hz_per_m,
        proposed_dimension_m=proposal.proposed_dimension_m,
        proposed_change_m=proposal.proposed_change_m,
        predicted_resonance_hz=verification.resonance_hz,
        predicted_swr=verification.swr_at_target,
        bounds_min_m=proposal.bounds_min_m,
        bounds_max_m=proposal.bounds_max_m,
        clipped=proposal.clipped,
        message_key=(
            "tuning.message.verified"
            if verification.resonance_hz is not None
            else "tuning.message.verified_no_resonance"
        ),
        detail=proposal.detail,
    )


def target_swr_from_sweep(
    frequencies_hz: tuple[float, ...],
    impedances_ohm: tuple[complex, ...],
    target_frequency_hz: float,
    reference_impedance_ohm: float,
) -> tuple[complex | None, float | None]:
    """Interpolate a sweep at the target and compute SWR there."""

    impedance = interpolate_impedance(
        frequencies_hz,
        impedances_ohm,
        target_frequency_hz,
    )
    if impedance is None:
        return None, None
    return impedance, swr_for_impedance(impedance, reference_impedance_ohm)
