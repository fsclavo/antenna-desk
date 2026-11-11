# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Matching-network design target validation."""

from __future__ import annotations

import pytest

from antennadesk.domain.design.matching_design import (
    MatchingNetworkDesign,
    matching_network_design_from_frequency,
)
from antennadesk.domain.simulation.result import FrequencyResult, SourceResult


def test_design_target_exposes_the_complex_load() -> None:
    design = MatchingNetworkDesign(
        frequency_hz=14_100_000.0,
        load_resistance_ohm=100.0,
        load_reactance_ohm=-25.0,
        source_impedance_ohm=50.0,
        origin=" simulation ",
    )

    assert design.load_impedance_ohm == complex(100.0, -25.0)
    assert design.origin == "simulation"


def test_design_target_requires_positive_resistances() -> None:
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=0.0,
            load_resistance_ohm=100.0,
            load_reactance_ohm=0.0,
        )
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=7_100_000.0,
            load_resistance_ohm=0.0,
            load_reactance_ohm=0.0,
        )
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=7_100_000.0,
            load_resistance_ohm=100.0,
            load_reactance_ohm=0.0,
            source_impedance_ohm=0.0,
        )


def test_design_target_rejects_a_non_finite_reactance() -> None:
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=7_100_000.0,
            load_resistance_ohm=100.0,
            load_reactance_ohm=float("inf"),
        )


def test_empty_origin_is_stored_as_none() -> None:
    design = MatchingNetworkDesign(
        frequency_hz=7_100_000.0,
        load_resistance_ohm=100.0,
        load_reactance_ohm=0.0,
        origin="   ",
    )

    assert design.origin is None


def test_origin_is_limited_to_the_persisted_length() -> None:
    with pytest.raises(ValueError):
        MatchingNetworkDesign(
            frequency_hz=7_100_000.0,
            load_resistance_ohm=100.0,
            load_reactance_ohm=0.0,
            origin="x" * 65,
        )


def _frequency_result(
    *,
    impedance_ohm: complex,
    source_impedance_ohm: complex | None,
) -> FrequencyResult:
    sources: tuple[SourceResult, ...] = ()
    if source_impedance_ohm is not None:
        sources = (
            SourceResult(
                wire_id="radiator",
                offset_m=0.0,
                tag=1,
                segment=11,
                amplitude=1.0,
                phase_deg=0.0,
                voltage_v=complex(1.0, 0.0),
                current_a=complex(0.005, 0.0),
                impedance_ohm=source_impedance_ohm,
                power_w=0.001,
            ),
        )
    return FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=11,
        impedance_ohm=impedance_ohm,
        swr=1.0,
        input_power_w=0.001,
        source_results=sources,
    )


def test_matching_point_uses_the_raw_source_before_the_post_chain() -> None:
    from antennadesk.domain.antennas.feed_line import FeedLine
    from antennadesk.domain.antennas.matching_network import LNetwork
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.spec import SimulationSpec

    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        feed_transformer_ratio=4.0,
        reference_impedance_ohm=75.0,
        feed_line=FeedLine(length_m=10.0),
        matching_network=LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12),
    )
    frequency = _frequency_result(
        impedance_ohm=complex(12.5, -3.0),
        source_impedance_ohm=complex(200.0, 20.0),
    )

    point = matching_network_design_from_frequency(frequency, spec)

    assert point is not None
    assert point.frequency_hz == pytest.approx(7_100_000.0)
    assert point.load_resistance_ohm == pytest.approx(50.0)
    assert point.load_reactance_ohm == pytest.approx(5.0)
    assert point.source_impedance_ohm == pytest.approx(75.0)
    assert point.origin == "simulation"


def test_matching_point_is_unavailable_without_raw_source_results() -> None:
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.spec import SimulationSpec

    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    frequency = _frequency_result(
        impedance_ohm=complex(50.0, 0.0),
        source_impedance_ohm=None,
    )

    assert matching_network_design_from_frequency(frequency, spec) is None


def test_matching_point_rejects_an_unusable_raw_resistance() -> None:
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.spec import SimulationSpec

    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    frequency = _frequency_result(
        impedance_ohm=complex(50.0, 0.0),
        source_impedance_ohm=complex(-10.0, 5.0),
    )

    assert matching_network_design_from_frequency(frequency, spec) is None
