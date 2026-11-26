# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic component-tolerance corners for the Wilkinson divider."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .feed_network import n_way_wilkinson
from .stacked_yagi import StackedYagiFeedMode, StackedYagiParameters


@dataclass(frozen=True, slots=True)
class WilkinsonToleranceResult:
    """Worst-case divider S-parameters over the component corners.

    The analysis covers the divider branches and isolation resistors, including
    the feed lines and excluding per-level matching networks and transformers.
    It is a bounded design-frequency check, not a Monte Carlo or broadband
    tolerance guarantee.
    """

    corner_count: int
    nominal_input_return_loss_db: float
    worst_input_return_loss_db: float
    nominal_isolation_db: float
    worst_isolation_db: float
    nominal_imbalance_db: float
    worst_imbalance_db: float


def _return_loss_db(magnitude: complex) -> float:
    return -20.0 * math.log10(max(abs(magnitude), 1e-12))


def _isolation_db(magnitude: complex) -> float:
    return -20.0 * math.log10(max(abs(magnitude), 1e-12))


def _imbalance_db(output_transmissions: tuple[float, ...]) -> float:
    low = max(min(output_transmissions), 1e-12)
    high = max(max(output_transmissions), low)
    return 20.0 * math.log10(high / low)


def _metrics(matrix: list[list[complex]]) -> tuple[float, float, float]:
    input_return_loss = _return_loss_db(matrix[0][0])
    output_count = len(matrix) - 1
    isolation = min(
        _isolation_db(matrix[row][column])
        for row in range(1, output_count + 1)
        for column in range(row + 1, output_count + 1)
    )
    transmissions = tuple(abs(matrix[row][0]) for row in range(1, output_count + 1))
    return input_return_loss, isolation, _imbalance_db(transmissions)


def analyze_stacked_yagi_tolerances(
    parameters: StackedYagiParameters,
) -> WilkinsonToleranceResult | None:
    """Return bounded divider tolerance corners, or None when not applicable."""

    feed = parameters.feed
    if feed.mode is not StackedYagiFeedMode.WILKINSON:
        return None
    branch_tolerance = feed.branch_impedance_tolerance_pct / 100.0
    resistor_tolerance = feed.isolation_resistor_tolerance_pct / 100.0
    if (
        branch_tolerance <= 0.0
        and resistor_tolerance <= 0.0
        and feed.branch_loss_db_per_100m <= 0.0
    ):
        return None

    nominal = (1.0,) * parameters.count
    corners: list[tuple[tuple[float, ...], tuple[float, ...]]] = []
    seen: set[tuple[tuple[float, ...], tuple[float, ...]]] = set()

    def add_corner(
        branch_scales: tuple[float, ...],
        resistor_scales: tuple[float, ...],
    ) -> None:
        key = (
            tuple(round(value, 12) for value in branch_scales),
            tuple(round(value, 12) for value in resistor_scales),
        )
        if key in seen:
            return
        seen.add(key)
        corners.append((branch_scales, resistor_scales))

    add_corner(nominal, nominal)
    if branch_tolerance > 0.0:
        add_corner(
            tuple(1.0 + branch_tolerance for _ in range(parameters.count)),
            nominal,
        )
        add_corner(
            tuple(1.0 - branch_tolerance for _ in range(parameters.count)),
            nominal,
        )
        for index in range(parameters.count):
            for sign in (1.0, -1.0):
                scales = list(nominal)
                scales[index] = 1.0 + sign * branch_tolerance
                add_corner(tuple(scales), nominal)
    if resistor_tolerance > 0.0:
        add_corner(
            nominal,
            tuple(1.0 + resistor_tolerance for _ in range(parameters.count)),
        )
        add_corner(
            nominal,
            tuple(1.0 - resistor_tolerance for _ in range(parameters.count)),
        )
        for index in range(parameters.count):
            for sign in (1.0, -1.0):
                scales = list(nominal)
                scales[index] = 1.0 + sign * resistor_tolerance
                add_corner(nominal, tuple(scales))
    if branch_tolerance > 0.0 and resistor_tolerance > 0.0:
        add_corner(
            tuple(1.0 + branch_tolerance for _ in range(parameters.count)),
            tuple(1.0 + resistor_tolerance for _ in range(parameters.count)),
        )
        add_corner(
            tuple(1.0 - branch_tolerance for _ in range(parameters.count)),
            tuple(1.0 - resistor_tolerance for _ in range(parameters.count)),
        )

    frequency_hz = parameters.splitter_design_frequency_hz
    z0 = feed.characteristic_impedance_ohm
    results: list[tuple[float, float, float]] = []
    for branch_scales, resistor_scales in corners:
        network = n_way_wilkinson(
            frequency_hz=frequency_hz,
            port_count=parameters.count,
            feed_line_lengths_m=tuple(
                feed.line_length_for_level(index) for index in range(parameters.count)
            ),
            system_impedance_ohm=z0,
            velocity_factor=feed.velocity_factor,
            level_matching_networks=(),
            branch_impedance_scales=branch_scales,
            isolation_resistor_scales=resistor_scales,
            branch_loss_db_per_100m=feed.branch_loss_db_per_100m,
        )
        results.append(_metrics(network.s_matrix(frequency_hz, z0)))

    nominal_metrics = results[0]
    return WilkinsonToleranceResult(
        corner_count=len(results),
        nominal_input_return_loss_db=nominal_metrics[0],
        worst_input_return_loss_db=min(result[0] for result in results),
        nominal_isolation_db=nominal_metrics[1],
        worst_isolation_db=min(result[1] for result in results),
        nominal_imbalance_db=nominal_metrics[2],
        worst_imbalance_db=max(result[2] for result in results),
    )
