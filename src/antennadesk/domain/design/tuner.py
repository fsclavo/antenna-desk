# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded tuner matchability checks for a simulated load.

The tuner is a design aid, not a model of a specific commercial ATU. Ranges are
entered by the operator; the domain checks whether a designed L/Pi/T network
fits those ranges and reports the limiting part. Component values can be
snapped to the E12 or E24 series before the check.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import StrEnum

from ..antennas.matching_network import (
    LNetwork,
    MatchingNetwork,
    PiNetwork,
    TNetwork,
)
from ..antennas.two_port import dissipative_loss_db
from ..common.reflection import calculate_swr
from ..common.units import ensure_non_negative, ensure_positive
from .smith_chart import MatchingPreviewTopology, design_preview_network

E12 = (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2)
E24 = (
    1.0,
    1.1,
    1.2,
    1.3,
    1.5,
    1.6,
    1.8,
    2.0,
    2.2,
    2.4,
    2.7,
    3.0,
    3.3,
    3.6,
    3.9,
    4.3,
    4.7,
    5.1,
    5.6,
    6.2,
    6.8,
    7.5,
    8.2,
    9.1,
)


class TunerStatus(StrEnum):
    MATCHED = "matched"
    OUT_OF_RANGE = "out_of_range"
    NO_SOLUTION = "no_solution"


@dataclass(frozen=True, slots=True)
class TunerLimits:
    """Component ranges of the operator's tuner, in canonical SI units."""

    capacitance_min_f: float
    capacitance_max_f: float
    inductance_min_h: float
    inductance_max_h: float

    def __post_init__(self) -> None:
        ensure_non_negative(self.capacitance_min_f, name="capacitance_min_f")
        ensure_non_negative(self.capacitance_max_f, name="capacitance_max_f")
        ensure_non_negative(self.inductance_min_h, name="inductance_min_h")
        ensure_non_negative(self.inductance_max_h, name="inductance_max_h")
        if self.capacitance_min_f > self.capacitance_max_f:
            raise ValueError("capacitance minimum must not exceed its maximum")
        if self.inductance_min_h > self.inductance_max_h:
            raise ValueError("inductance minimum must not exceed its maximum")


@dataclass(frozen=True, slots=True)
class TunerEvaluation:
    status: TunerStatus
    network: MatchingNetwork | None
    input_impedance_ohm: complex | None
    swr: float | None
    loss_db: float | None
    limiting: str | None = None


def nearest_e_series(value: float, series: str) -> float:
    """Return the nearest E12 or E24 value across the relevant decades."""

    if value <= 0.0:
        raise ValueError("value must be positive")
    if series not in {"e12", "e24"}:
        raise ValueError("series must be e12 or e24")
    base = E12 if series == "e12" else E24
    exponent = math.floor(math.log10(value))
    candidates: list[float] = []
    for decade in (exponent - 1, exponent, exponent + 1):
        factor = 10.0**decade
        candidates.extend(item * factor for item in base)
    return min(candidates, key=lambda candidate: abs(math.log(candidate / value)))


def realize_network(network: MatchingNetwork, series: str) -> MatchingNetwork:
    """Snap every active L/C branch to the requested E-series values."""

    if series == "ideal":
        return network
    if isinstance(network, LNetwork):
        series_l, series_c = _nearest_branch(
            network.series_inductance_h,
            network.series_capacitance_f,
            series,
        )
        shunt_l, shunt_c = _nearest_branch(
            network.shunt_inductance_h,
            network.shunt_capacitance_f,
            series,
        )
        return replace(
            network,
            series_inductance_h=series_l,
            series_capacitance_f=series_c,
            shunt_inductance_h=shunt_l,
            shunt_capacitance_f=shunt_c,
        )
    if isinstance(network, PiNetwork):
        input_l, input_c = _nearest_branch(
            network.input_shunt_inductance_h,
            network.input_shunt_capacitance_f,
            series,
        )
        series_l, series_c = _nearest_branch(
            network.series_inductance_h,
            network.series_capacitance_f,
            series,
        )
        output_l, output_c = _nearest_branch(
            network.output_shunt_inductance_h,
            network.output_shunt_capacitance_f,
            series,
        )
        return replace(
            network,
            input_shunt_inductance_h=input_l,
            input_shunt_capacitance_f=input_c,
            series_inductance_h=series_l,
            series_capacitance_f=series_c,
            output_shunt_inductance_h=output_l,
            output_shunt_capacitance_f=output_c,
        )
    if isinstance(network, TNetwork):
        input_l, input_c = _nearest_branch(
            network.input_series_inductance_h,
            network.input_series_capacitance_f,
            series,
        )
        shunt_l, shunt_c = _nearest_branch(
            network.shunt_inductance_h,
            network.shunt_capacitance_f,
            series,
        )
        output_l, output_c = _nearest_branch(
            network.output_series_inductance_h,
            network.output_series_capacitance_f,
            series,
        )
        return replace(
            network,
            input_series_inductance_h=input_l,
            input_series_capacitance_f=input_c,
            shunt_inductance_h=shunt_l,
            shunt_capacitance_f=shunt_c,
            output_series_inductance_h=output_l,
            output_series_capacitance_f=output_c,
        )
    return network


def evaluate_tuner_match(
    load_impedance_ohm: complex,
    frequency_hz: float,
    limits: TunerLimits,
    topology: MatchingPreviewTopology | str,
    *,
    source_impedance_ohm: float = 50.0,
    loaded_q: float | None = None,
    series: str = "ideal",
) -> TunerEvaluation:
    """Design a network, snap it if requested, and check the tuner ranges."""

    ensure_positive(frequency_hz, name="frequency_hz")
    if abs(load_impedance_ohm - source_impedance_ohm) <= max(1e-9, source_impedance_ohm * 1e-9):
        return TunerEvaluation(
            TunerStatus.MATCHED,
            None,
            load_impedance_ohm,
            calculate_swr(load_impedance_ohm, source_impedance_ohm),
            0.0,
        )
    network = design_preview_network(
        load_impedance_ohm,
        frequency_hz,
        topology,
        source_impedance_ohm=source_impedance_ohm,
        loaded_q=loaded_q,
    )
    if network is None:
        return TunerEvaluation(TunerStatus.NO_SOLUTION, None, None, None, None)
    if series != "ideal":
        network = realize_network(network, series)
    limiting = _limiting_component(network, limits)
    input_impedance = network.input_impedance(load_impedance_ohm, frequency_hz)
    loss_db = dissipative_loss_db(
        network.abcd(frequency_hz),
        source_impedance_ohm,
        load_impedance_ohm,
    )
    return TunerEvaluation(
        status=TunerStatus.MATCHED if limiting is None else TunerStatus.OUT_OF_RANGE,
        network=network,
        input_impedance_ohm=input_impedance,
        swr=calculate_swr(input_impedance, source_impedance_ohm),
        loss_db=loss_db if math.isfinite(loss_db) else None,
        limiting=limiting,
    )


def _nearest_branch(
    inductance_h: float,
    capacitance_f: float,
    series: str,
) -> tuple[float, float]:
    if inductance_h > 0.0:
        return nearest_e_series(inductance_h, series), 0.0
    if capacitance_f > 0.0:
        return 0.0, nearest_e_series(capacitance_f, series)
    return 0.0, 0.0


def _limiting_component(network: MatchingNetwork, limits: TunerLimits) -> str | None:
    for kind, value in _active_components(network):
        if value <= 0.0:
            continue
        if kind == "c":
            if value < limits.capacitance_min_f:
                return "capacitance_min"
            if value > limits.capacitance_max_f:
                return "capacitance_max"
        else:
            if value < limits.inductance_min_h:
                return "inductance_min"
            if value > limits.inductance_max_h:
                return "inductance_max"
    return None


def _active_components(network: MatchingNetwork) -> tuple[tuple[str, float], ...]:
    if isinstance(network, LNetwork):
        return (
            ("l", network.series_inductance_h),
            ("c", network.series_capacitance_f),
            ("l", network.shunt_inductance_h),
            ("c", network.shunt_capacitance_f),
        )
    if isinstance(network, PiNetwork):
        return (
            ("l", network.input_shunt_inductance_h),
            ("c", network.input_shunt_capacitance_f),
            ("l", network.series_inductance_h),
            ("c", network.series_capacitance_f),
            ("l", network.output_shunt_inductance_h),
            ("c", network.output_shunt_capacitance_f),
        )
    if isinstance(network, TNetwork):
        return (
            ("l", network.input_series_inductance_h),
            ("c", network.input_series_capacitance_f),
            ("l", network.shunt_inductance_h),
            ("c", network.shunt_capacitance_f),
            ("l", network.output_series_inductance_h),
            ("c", network.output_series_capacitance_f),
        )
    return ()
