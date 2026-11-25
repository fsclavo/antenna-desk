# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Constructive feed-connection resolution."""

from __future__ import annotations

from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.feed_connection import (
    BalunRequirement,
    FeedBalance,
    FeedInterface,
    FeedTopology,
)
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import YagiElement, YagiMatchType, YagiParameters
from antennadesk.domain.design.feed_connection import feed_connection_detail


def _yagi(**overrides: object) -> YagiParameters:
    values: dict[str, object] = {
        "frequency_hz": 14_100_000.0,
        "elements": (
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        "height_m": 10.0,
    }
    values.update(overrides)
    return YagiParameters(**values)  # type: ignore[arg-type]


def test_yagi_straight_reports_direct_coax_and_recommends_a_balun() -> None:
    parameters = _yagi()
    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert detail.topology is FeedTopology.CENTER_FED_DIPOLE
    assert detail.interface is FeedInterface.DIRECT_COAX
    assert detail.balance is FeedBalance.BALANCED
    assert detail.balun_requirement is BalunRequirement.REQUIRED
    assert detail.terminals[0].wire_id == detail.terminals[1].wire_id
    assert detail.terminals[0].side == "before"
    assert detail.terminals[1].side == "after"
    assert ("A", "Coax center") in [(item.source, item.target) for item in detail.connections]
    assert "1:1 current balun" in " ".join(detail.recommended)
    assert "Gamma" in " ".join(detail.not_modeled)


def test_yagi_straight_with_recorded_balun_uses_the_balun_interface() -> None:
    parameters = _yagi()
    detail = feed_connection_detail(
        parameters,
        parameters.to_antenna(),
        current_balun=True,
    )

    assert detail.interface is FeedInterface.CURRENT_BALUN
    assert "Current balun/choke installed" in detail.recorded
    assert ("A", "Balun balanced A") in [(item.source, item.target) for item in detail.connections]


def test_yagi_folded_reports_the_transformer_and_continuous_second_conductor() -> None:
    parameters = _yagi(driven_folded=True, transformer_ratio=4.0)
    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert detail.topology is FeedTopology.FOLDED_DIPOLE
    assert detail.interface is FeedInterface.TRANSFORMER
    assert detail.transformer_ratio == 4.0
    assert detail.match_hardware is not None
    assert "not a parasitic" in detail.match_hardware
    assert ("A", "Transformer secondary A") in [
        (item.source, item.target) for item in detail.connections
    ]
    assert "Ideal feed transformer" in detail.modeled


def test_yagi_beta_hairpin_is_matching_hardware_not_a_balun() -> None:
    parameters = _yagi(
        match_type=YagiMatchType.BETA_HAIRPIN,
        match_length_m=0.2,
        match_spacing_m=0.1,
    )
    detail = feed_connection_detail(
        parameters,
        parameters.to_antenna(),
        current_balun=True,
    )

    assert detail.topology is FeedTopology.BETA_HAIRPIN
    assert detail.interface is FeedInterface.CURRENT_BALUN
    assert detail.match_hardware is not None
    assert "not a balun" in detail.match_hardware
    assert "The hairpin is a matching stub, not a balun." in detail.limitations


def test_log_periodic_reports_a_balanced_center_feed_and_phase_line() -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.log_periodic import (
        cebik_10m_log_periodic_parameters,
    )

    parameters = cebik_10m_log_periodic_parameters()
    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert detail.topology is FeedTopology.CENTER_FED_DIPOLE
    assert detail.interface is FeedInterface.DIRECT_COAX
    assert detail.balance is FeedBalance.BALANCED
    assert detail.balun_requirement is BalunRequirement.REQUIRED
    assert detail.match_hardware is not None
    assert "transposed phase line" in detail.match_hardware.lower()
    assert "1:1 current balun" in " ".join(detail.recommended)

    transformer = replace(parameters, feed_transformer_ratio=4.0)
    transformed = feed_connection_detail(transformer, transformer.to_antenna())
    assert transformed.interface is FeedInterface.TRANSFORMER
    assert transformed.transformer_ratio == 4.0
    assert "Ideal feed transformer" in transformed.modeled


def test_vertical_base_feed_uses_the_ground_return() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.25,
    )
    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert detail.topology is FeedTopology.BASE_FED_VERTICAL
    assert detail.interface is FeedInterface.DIRECT_COAX
    assert detail.balance is FeedBalance.UNBALANCED
    assert detail.balun_requirement is BalunRequirement.NOT_REQUIRED
    assert detail.terminals[1].side == "ground"
    assert detail.terminals[1].wire_id is None


def test_endfed_uses_the_transformer_and_counterpoise() -> None:
    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        transformer_ratio=49.0,
    )
    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert detail.topology is FeedTopology.END_FED
    assert detail.interface is FeedInterface.TRANSFORMER
    assert detail.transformer_ratio == 49.0
    assert detail.terminals[1].side == "counterpoise"


def test_custom_geometry_is_explicitly_unknown() -> None:
    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                id="wire-1",
                start=Point3D(x_m=0.0, y_m=0.0, z_m=10.0),
                end=Point3D(x_m=10.0, y_m=0.0, z_m=10.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint("wire-1", 5.0),
    )
    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert detail.topology is FeedTopology.UNKNOWN
    assert detail.interface is FeedInterface.UNKNOWN
    assert detail.balun_requirement is BalunRequirement.UNKNOWN
    assert "not classified" in detail.summary


def test_stacked_yagi_reports_a_multi_port_ideal_feed() -> None:
    parameters = StackedYagiParameters(yagi=_yagi(), count=2, spacing_m=10.6)

    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert detail.topology is FeedTopology.MULTI_PORT
    assert detail.interface is FeedInterface.MULTI_PORT
    assert "Level 1 is the primary port" in (detail.match_hardware or "")


def test_stacked_yagi_phase_lines_report_the_splitter_feed() -> None:
    parameters = StackedYagiParameters(
        yagi=_yagi(),
        count=2,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.PHASE_LINES,
            reference_length_m=2.0,
            line_increment_m=2.5,
            velocity_factor=0.8,
            characteristic_impedance_ohm=75.0,
            splitter_loss_db=0.4,
        ),
    )

    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert "splitter + phase lines" in (detail.match_hardware or "")


def test_stacked_yagi_network_mode_reports_the_co_simulated_feed() -> None:
    parameters = StackedYagiParameters(
        yagi=_yagi(),
        count=2,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.NETWORK,
            reference_length_m=2.0,
            line_increment_m=2.5,
            velocity_factor=0.8,
            characteristic_impedance_ohm=75.0,
        ),
    )

    detail = feed_connection_detail(parameters, parameters.to_antenna())

    assert "Splitter node is the primary input" in (detail.match_hardware or "")
