# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Direct tests for the Qt-free typed-family simulation-spec builders."""

from __future__ import annotations

from dataclasses import replace
from typing import get_args

import pytest

from antennadesk.application.simulation_specs import (
    _BUILDERS,
    CustomSweepOptions,
    build_typed_family_simulation_spec,
)
from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters
from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.design import AntennaDesignParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.hexbeam import published_hexbeam_multiband_parameters
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters
from antennadesk.domain.antennas.log_periodic import cebik_10m_log_periodic_parameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import moxon_20m_wire
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
    stacked_yagi_parameters,
)
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.transmission_line_doublet import (
    DoubletPreset,
    doublet_starting_parameters,
)
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import nbs_five_element
from antennadesk.domain.antennas.zepp import zepp_starting_parameters
from antennadesk.domain.simulation.spec import FeedNetworkKind, FeedNetworkSpec

BASIC_FORM_TYPES = {DipoleParameters, FoldedDipoleParameters, LoopParameters}


def test_registry_covers_every_non_form_family() -> None:
    expected = set(get_args(AntennaDesignParameters)) - BASIC_FORM_TYPES

    assert set(_BUILDERS) == expected


def test_basic_form_family_raises_an_explicit_error() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )

    with pytest.raises(TypeError, match="basic form spec"):
        build_typed_family_simulation_spec(parameters)


def test_pattern_step_is_applied_to_the_far_field_request() -> None:
    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
    )

    spec = build_typed_family_simulation_spec(parameters, pattern_step_deg=10.0)

    assert spec.far_field.theta_step_deg == pytest.approx(10.0)
    assert spec.far_field.phi_step_deg == pytest.approx(10.0)


def test_ocfd_transformer_ratio_is_carried_into_the_spec() -> None:
    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        transformer_ratio=4.0,
    )

    spec = build_typed_family_simulation_spec(parameters)

    assert spec.feed_transformer_ratio == pytest.approx(4.0)


def _custom_parameters() -> CustomAntennaParameters:
    return CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                id="radiator",
                start=Point3D(-10.0, 0.0, 8.0),
                end=Point3D(10.0, 0.0, 8.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint(wire_id="radiator", offset_m=10.0),
    )


def test_custom_sweep_options_replace_the_single_frequency_plan() -> None:
    spec = build_typed_family_simulation_spec(
        _custom_parameters(),
        custom_sweep=CustomSweepOptions(
            enabled=True,
            start_hz=7_000_000.0,
            stop_hz=7_300_000.0,
            points=11,
        ),
    )

    assert spec.frequency_plan.start_hz == pytest.approx(7_000_000.0)
    assert spec.frequency_plan.stop_hz == pytest.approx(7_300_000.0)
    assert spec.frequency_plan.count == 11


def test_custom_sweep_disabled_keeps_the_design_frequency() -> None:
    spec = build_typed_family_simulation_spec(
        _custom_parameters(),
        custom_sweep=CustomSweepOptions(enabled=False),
    )

    assert spec.frequency_plan.count == 1
    assert spec.frequency_plan.start_hz == pytest.approx(7_100_000.0)
    assert spec.frequency_plan.stop_hz == pytest.approx(7_100_000.0)


def test_hexbeam_active_band_selects_the_band_center() -> None:
    parameters = published_hexbeam_multiband_parameters()
    active = parameters.resolved_bands[-1]

    spec = build_typed_family_simulation_spec(
        parameters,
        active_hexbeam_band=active.label,
    )

    center_hz = (spec.frequency_plan.start_hz + spec.frequency_plan.stop_hz) / 2.0
    assert center_hz == pytest.approx(active.frequency_hz)


def _every_typed_family_parameters() -> list[AntennaDesignParameters]:
    return [
        OCFDParameters(frequency_hz=7_100_000.0, total_length_m=20.0),
        VerticalParameters(
            frequency_hz=14_100_000.0,
            height_m=5.0,
            base_height_m=0.25,
            radial_count=4,
            radial_length_m=2.5,
        ),
        InvertedVParameters(
            frequency_hz=14_100_000.0,
            leg_length_m=5.0,
            apex_height_m=10.0,
        ),
        InvertedLParameters(
            frequency_hz=7_100_000.0,
            vertical_height_m=8.0,
            horizontal_length_m=12.0,
            base_height_m=0.5,
        ),
        MagneticLoopParameters(
            frequency_hz=14_100_000.0,
            diameter_m=1.0,
            tuning_capacitance_f=100e-12,
        ),
        nbs_five_element(frequency_hz=14_100_000.0, height_m=10.0),
        stacked_yagi_parameters(
            frequency_hz=14_100_000.0,
            count=2,
            height_m=10.0,
            spacing_m=10.0,
        ),
        moxon_20m_wire(),
        FanDipoleParameters(
            frequency_hz=7_100_000.0,
            elements=(FanElement(20.0, 120.0), FanElement(10.0, 90.0)),
            apex_height_m=10.0,
        ),
        TrapDipoleParameters(
            frequency_hz=7_100_000.0,
            high_band_frequency_hz=14_100_000.0,
            inner_length_m=10.0,
            outer_length_m=5.0,
            trap_frequency_hz=14_100_000.0,
            trap_inductance_h=10e-6,
            height_m=12.0,
        ),
        T2FDParameters(
            frequency_hz=3_500_000.0,
            highest_frequency_hz=30_000_000.0,
            length_m=26.0,
            spacing_m=0.9,
        ),
        CustomAntennaParameters(
            frequency_hz=7_100_000.0,
            wires=(
                Wire(
                    id="radiator",
                    start=Point3D(-10.0, 0.0, 8.0),
                    end=Point3D(10.0, 0.0, 8.0),
                    radius_m=0.001,
                    material=COPPER,
                ),
            ),
            feed=FeedPoint(wire_id="radiator", offset_m=10.0),
        ),
        JPoleParameters(
            frequency_hz=14_100_000.0,
            radiator_height_m=5.0,
            stub_length_m=1.0,
            spacing_m=0.1,
        ),
        RingoParameters(
            frequency_hz=14_100_000.0,
            radiator_height_m=3.1,
            ring_diameter_m=0.33,
        ),
        scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0),
        biquad_parameters(BiquadKind.SINGLE),
        beverage_parameters(),
        loaded_dipole_parameters(),
        phased_vertical_parameters(),
        quad_beam_parameters(),
        cebik_10m_log_periodic_parameters(),
        discone_parameters(),
        trap_yagi_parameters(),
        published_hexbeam_multiband_parameters(),
        doublet_starting_parameters(DoubletPreset.G5RV),
        zepp_starting_parameters(),
    ]


@pytest.mark.parametrize(
    "parameters",
    _every_typed_family_parameters(),
    ids=lambda parameters: type(parameters).__name__,
)
def test_every_registered_builder_produces_a_spec(
    parameters: AntennaDesignParameters,
) -> None:
    spec = build_typed_family_simulation_spec(parameters)

    assert spec.frequency_plan.count >= 1
    assert spec.segmentation.min_segments_per_wire >= 1


def test_stacked_yagi_phase_lines_apply_the_splitter_loss() -> None:
    parameters = stacked_yagi_parameters(
        frequency_hz=14_100_000.0,
        count=2,
        height_m=10.0,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.PHASE_LINES,
            reference_length_m=2.0,
            line_increment_m=2.65,
            velocity_factor=0.8,
            characteristic_impedance_ohm=75.0,
            splitter_loss_db=0.4,
        ),
    )

    spec = build_typed_family_simulation_spec(parameters)

    assert spec.feed_network_loss_db == pytest.approx(0.4)
    assert parameters.to_antenna().sources[0].phase_deg == pytest.approx(
        360.0 - 360.0 * 2.65 / (0.8 * parameters.wavelength_m)
    )


def test_stacked_yagi_network_mode_passes_the_line_loss() -> None:
    parameters = stacked_yagi_parameters(
        frequency_hz=14_100_000.0,
        count=2,
        height_m=10.0,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.NETWORK,
            reference_length_m=2.0,
            line_increment_m=2.65,
            velocity_factor=0.8,
            characteristic_impedance_ohm=75.0,
            splitter_loss_db=0.4,
            line_loss_db_per_100m=1.5,
        ),
    )

    spec = build_typed_family_simulation_spec(parameters)

    assert spec.co_simulate_feed_network is True
    assert spec.feed_network_loss_db == pytest.approx(0.4)
    assert spec.feed_network_line_loss_db_per_100m == pytest.approx(1.5)


def test_stacked_yagi_wilkinson_mode_builds_a_feed_network_spec() -> None:
    parameters = stacked_yagi_parameters(
        frequency_hz=14_100_000.0,
        count=2,
        height_m=10.0,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.WILKINSON,
            reference_length_m=2.0,
            line_increment_m=1.0,
            velocity_factor=0.8,
            characteristic_impedance_ohm=50.0,
            splitter_loss_db=0.2,
            line_loss_db_per_100m=1.5,
            splitter_design_frequency_hz=14_200_000.0,
        ),
    )

    spec = build_typed_family_simulation_spec(parameters)

    assert spec.feed_network == FeedNetworkSpec(
        kind=FeedNetworkKind.WILKINSON,
        design_frequency_hz=14_200_000.0,
        port_count=2,
        feed_line_lengths_m=(2.0, 3.0),
        feed_line_impedance_ohm=50.0,
        velocity_factor=0.8,
        splitter_excess_loss_db=0.2,
        line_loss_db_per_100m=1.5,
    )
    assert spec.co_simulate_feed_network is False
    assert spec.feed_network_loss_db == pytest.approx(0.0)
    assert spec.feed_network_line_loss_db_per_100m == pytest.approx(0.0)


def test_stacked_yagi_folded_element_keeps_the_per_level_transformer_out() -> None:
    yagi = replace(
        nbs_five_element(frequency_hz=14_100_000.0, height_m=10.0),
        driven_folded=True,
        driven_fold_spacing_m=0.1,
        transformer_ratio=1.0,
    )
    parameters = StackedYagiParameters(
        yagi=yagi,
        count=2,
        spacing_m=10.6,
        feed=StackedYagiFeed(
            mode=StackedYagiFeedMode.WILKINSON,
            reference_length_m=2.0,
            velocity_factor=0.8,
            level_transformer_ratios=(4.0, 1.0),
            branch_impedance_tolerance_pct=5.0,
            isolation_resistor_tolerance_pct=2.0,
            branch_loss_db_per_100m=10.0,
            isolation_resistor_inductance_h=120e-9,
        ),
    )

    spec = build_typed_family_simulation_spec(parameters)

    assert spec.feed_transformer_ratio == pytest.approx(1.0)
    assert spec.feed_network is not None
    assert spec.feed_network.port_count == 2
    assert spec.feed_network.level_transformer_ratios == (4.0, 1.0)
    assert spec.feed_network.branch_impedance_tolerance_pct == pytest.approx(5.0)
    assert spec.feed_network.isolation_resistor_tolerance_pct == pytest.approx(2.0)
    assert spec.feed_network.branch_loss_db_per_100m == pytest.approx(10.0)
    assert spec.feed_network.isolation_resistor_inductance_h == pytest.approx(120e-9)
