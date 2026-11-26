# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded component-tolerance corners for the Wilkinson divider."""

from __future__ import annotations

import pytest

from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
    stacked_yagi_parameters,
)
from antennadesk.domain.antennas.wilkinson_tolerance import (
    analyze_stacked_yagi_tolerances,
)


def _parameters(
    *,
    branch_tolerance_pct: float = 5.0,
    resistor_tolerance_pct: float = 5.0,
    mode: StackedYagiFeedMode = StackedYagiFeedMode.WILKINSON,
) -> StackedYagiParameters:
    base = stacked_yagi_parameters(
        frequency_hz=14_100_000.0,
        count=2,
        height_m=10.0,
        spacing_m=10.6,
    )
    return StackedYagiParameters(
        yagi=base.yagi,
        count=2,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=mode,
            reference_length_m=2.0,
            line_increment_m=0.0,
            velocity_factor=0.8,
            characteristic_impedance_ohm=50.0,
            splitter_design_frequency_hz=14_100_000.0,
            branch_impedance_tolerance_pct=branch_tolerance_pct,
            isolation_resistor_tolerance_pct=resistor_tolerance_pct,
        ),
    )


def test_wilkinson_tolerance_corners_are_deterministic_and_bounded() -> None:
    result = analyze_stacked_yagi_tolerances(_parameters())

    assert result is not None
    assert result.corner_count == 15
    assert result.worst_input_return_loss_db <= result.nominal_input_return_loss_db
    assert result.worst_isolation_db <= result.nominal_isolation_db
    assert result.worst_imbalance_db >= result.nominal_imbalance_db


def test_wilkinson_tolerance_analysis_is_optional_and_mode_specific() -> None:
    assert (
        analyze_stacked_yagi_tolerances(
            _parameters(branch_tolerance_pct=0.0, resistor_tolerance_pct=0.0)
        )
        is None
    )
    assert (
        analyze_stacked_yagi_tolerances(_parameters(mode=StackedYagiFeedMode.PHASE_LINES)) is None
    )


def test_wilkinson_tolerance_rejects_out_of_range_percentages() -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        _parameters(branch_tolerance_pct=100.0)
    with pytest.raises(ValueError, match="between 0 and 100"):
        _parameters(resistor_tolerance_pct=-1.0)


def test_wilkinson_branch_loss_produces_a_nominal_s_parameter_check() -> None:
    parameters = _parameters(branch_tolerance_pct=0.0, resistor_tolerance_pct=0.0)
    parameters = StackedYagiParameters(
        yagi=parameters.yagi,
        count=parameters.count,
        spacing_m=parameters.spacing_m,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.WILKINSON,
            reference_length_m=2.0,
            velocity_factor=0.8,
            branch_loss_db_per_100m=10.0,
        ),
    )

    result = analyze_stacked_yagi_tolerances(parameters)

    assert result is not None
    assert result.corner_count == 1
    assert result.worst_input_return_loss_db == pytest.approx(result.nominal_input_return_loss_db)
    assert result.worst_isolation_db == pytest.approx(result.nominal_isolation_db)
    assert result.worst_imbalance_db == pytest.approx(result.nominal_imbalance_db)
