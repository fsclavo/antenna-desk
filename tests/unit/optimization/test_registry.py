# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import fields, replace
from typing import get_args

import pytest

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import (
    BiquadKind,
    BiquadParameters,
    biquad_parameters,
)
from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.design import AntennaDesignParameters, antenna_type_for
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.endfed import (
    EndFedParameters,
    EndFedPreset,
    shortened_efhw_80_10_parameters,
)
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.hexbeam import (
    HexbeamBand,
    published_hexbeam_multiband_parameters,
    published_hexbeam_parameters,
)
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters
from antennadesk.domain.antennas.log_periodic import cebik_10m_log_periodic_parameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
from antennadesk.domain.antennas.quad_beam import QuadBeamParameters, quad_beam_parameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
from antennadesk.domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
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
from antennadesk.domain.antennas.yagi import YagiElement, YagiMatchType, YagiParameters
from antennadesk.domain.antennas.zepp import zepp_starting_parameters
from antennadesk.domain.optimization.registry import (
    KNOWN_PARAMETER_TYPES,
    SUPPORTED_OPTIMIZER_TYPES,
    optimizer_availability,
)
from antennadesk.domain.optimization.variables import VariableKind


def _dipole() -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )


def _vertical() -> VerticalParameters:
    return VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=5.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=2.5,
        radial_angle_deg=30.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=10e-6,
        top_hat_enabled=True,
        top_hat_radius_m=0.75,
        top_hat_wire_count=4,
    )


def _yagi() -> YagiParameters:
    return YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
        match_type=YagiMatchType.BETA_HAIRPIN,
        match_length_m=0.2,
        match_spacing_m=0.1,
    )


def _stack_base_yagi() -> YagiParameters:
    return YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
    )


def _yagi_folded() -> YagiParameters:
    return YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
        driven_folded=True,
        driven_fold_spacing_m=0.1,
    )


def _custom() -> CustomAntennaParameters:
    return CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                "w1",
                Point3D(0.0, 0.0, 8.0),
                Point3D(10.0, 0.0, 8.0),
                0.001,
                COPPER,
            ),
        ),
        feed=FeedPoint("w1", 5.0),
    )


def test_every_parameter_type_has_a_registry_decision() -> None:
    union_types = set(get_args(AntennaDesignParameters))

    assert union_types <= KNOWN_PARAMETER_TYPES
    assert union_types >= SUPPORTED_OPTIMIZER_TYPES


@pytest.mark.parametrize(
    ("parameters", "expected_key"),
    [
        (_dipole(), "wire_dipole"),
        (_vertical(), "vertical"),
        (_yagi(), "yagi"),
        (scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0), "half_square"),
        (scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0), "bobtail_curtain"),
    ],
)
def test_pilot_families_have_a_descriptor(parameters: object, expected_key: str) -> None:
    availability = optimizer_availability(parameters)  # type: ignore[arg-type]

    assert availability.available
    assert availability.descriptor is not None
    assert availability.descriptor.key == expected_key


def test_descriptor_variables_cover_every_geometric_field() -> None:
    cases = [
        (
            _dipole(),
            {"total_length_m", "height_m", "wire_radius_m"},
        ),
        (
            _vertical(),
            {
                "height_m",
                "base_height_m",
                "radial_length_m",
                "radial_count",
                "radial_angle_deg",
                "radial_droop_deg",
                "loading_coil_inductance_h",
                "loading_coil_offset_m",
                "top_hat_radius_m",
                "top_hat_wire_count",
                "wire_radius_m",
            },
        ),
        (
            _yagi(),
            {
                "length_0",
                "length_1",
                "gap_1",
                "height_m",
                "match_length_m",
                "match_spacing_m",
            },
        ),
        (
            _yagi_folded(),
            {
                "length_0",
                "length_1",
                "gap_1",
                "height_m",
                "driven_fold_spacing_m",
                "transformer_ratio",
            },
        ),
        (
            scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0),
            {
                "horizontal_length_m",
                "vertical_height_m",
                "base_height_m",
                "feed_offset_m",
                "wire_radius_m",
            },
        ),
    ]

    for parameters, expected in cases:
        availability = optimizer_availability(parameters)  # type: ignore[arg-type]
        assert availability.descriptor is not None
        assert {variable.name for variable in availability.descriptor.variables} == expected

        # Every dataclass field must be either optimized or explicitly context.
        field_names = {field.name for field in fields(parameters)}  # type: ignore[arg-type]
        if isinstance(parameters, YagiParameters):
            field_names |= {f"length_{index}" for index in range(len(parameters.elements))}
            field_names |= {f"gap_{index}" for index in range(1, len(parameters.elements))}
        assert field_names, "the parameter class has no fields"
        assert expected <= field_names


def test_folded_dipole_descriptor_exposes_the_transformer_choice() -> None:
    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    availability = optimizer_availability(parameters)
    descriptor = availability.descriptor
    assert descriptor is not None

    variable = next(item for item in descriptor.variables if item.name == "transformer_ratio")
    assert variable.kind is VariableKind.CHOICE
    assert variable.locked_by_default
    assert 4.0 in variable.choices
    assert 6.0 in variable.choices

    rebuilt = descriptor.build_parameters({**descriptor.initial_values, "transformer_ratio": 6.0})
    assert isinstance(rebuilt, FoldedDipoleParameters)
    assert rebuilt.transformer_ratio == pytest.approx(6.0)


def test_yagi_folded_descriptor_exposes_the_transformer_choice() -> None:
    parameters = _yagi_folded()
    availability = optimizer_availability(parameters)
    descriptor = availability.descriptor
    assert descriptor is not None

    variable = next(item for item in descriptor.variables if item.name == "transformer_ratio")
    assert variable.kind is VariableKind.CHOICE
    assert variable.locked_by_default
    assert 4.0 in variable.choices
    assert 6.0 in variable.choices

    rebuilt = descriptor.build_parameters({**descriptor.initial_values, "transformer_ratio": 4.0})
    assert isinstance(rebuilt, YagiParameters)
    assert rebuilt.transformer_ratio == pytest.approx(4.0)


def test_loop_descriptor_exposes_the_transformer_choice() -> None:
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
    )
    availability = optimizer_availability(parameters)
    descriptor = availability.descriptor
    assert descriptor is not None

    variable = next(item for item in descriptor.variables if item.name == "transformer_ratio")
    assert variable.kind is VariableKind.CHOICE
    assert variable.locked_by_default
    assert 2.0 in variable.choices
    assert 4.0 in variable.choices

    rebuilt = descriptor.build_parameters({**descriptor.initial_values, "transformer_ratio": 4.0})
    assert isinstance(rebuilt, LoopParameters)
    assert rebuilt.transformer_ratio == pytest.approx(4.0)


def test_biquad_descriptor_exposes_the_transformer_choice() -> None:
    parameters = biquad_parameters(BiquadKind.DOUBLE)
    availability = optimizer_availability(parameters)
    descriptor = availability.descriptor
    assert descriptor is not None

    variable = next(item for item in descriptor.variables if item.name == "transformer_ratio")
    assert variable.kind is VariableKind.CHOICE
    assert variable.locked_by_default
    assert 4.0 in variable.choices
    assert 6.0 in variable.choices

    rebuilt = descriptor.build_parameters({**descriptor.initial_values, "transformer_ratio": 6.0})
    assert isinstance(rebuilt, BiquadParameters)
    assert rebuilt.transformer_ratio == pytest.approx(6.0)


def _typed_samples() -> list[AntennaDesignParameters]:
    return [
        _dipole(),
        FoldedDipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
            spacing_m=0.2,
        ),
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=4,
        ),
        _vertical(),
        InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=10.0,
            apex_height_m=12.0,
        ),
        InvertedLParameters(
            frequency_hz=7_100_000.0,
            vertical_height_m=10.0,
            horizontal_length_m=20.0,
            base_height_m=1.0,
        ),
        JPoleParameters(
            frequency_hz=145_000_000.0,
            radiator_height_m=1.5,
            stub_length_m=0.5,
            spacing_m=0.05,
            feed_offset_m=0.1,
            folded=True,
        ),
        RingoParameters(
            frequency_hz=29_000_000.0,
            radiator_height_m=5.0,
            ring_diameter_m=0.5,
            ring_height_m=0.25,
        ),
        scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0),
        biquad_parameters(BiquadKind.SINGLE),
        biquad_parameters(BiquadKind.DOUBLE),
        beverage_parameters(),
        loaded_dipole_parameters(),
        discone_parameters(),
        trap_yagi_parameters(),
        published_hexbeam_parameters(),
        phased_vertical_parameters(),
        StackedYagiParameters(
            yagi=_stack_base_yagi(),
            count=2,
            spacing_m=10.6,
            max_top_height_m=25.0,
        ),
        StackedYagiParameters(
            yagi=_stack_base_yagi(),
            count=2,
            spacing_m=10.6,
            max_top_height_m=25.0,
            feed=StackedYagiFeed(
                mode=StackedYagiFeedMode.PHASE_LINES,
                reference_length_m=2.0,
                line_increment_m=2.5,
                velocity_factor=0.8,
                characteristic_impedance_ohm=75.0,
                splitter_loss_db=0.4,
            ),
        ),
        quad_beam_parameters(element_count=3),
        OCFDParameters(frequency_hz=7_100_000.0, total_length_m=40.0),
        EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            counterpoise_length_m=5.0,
        ),
        shortened_efhw_80_10_parameters(),
        FanDipoleParameters(
            frequency_hz=7_100_000.0,
            elements=(
                FanElement(20.0, 120.0),
                FanElement(10.0, 90.0),
            ),
            apex_height_m=12.0,
        ),
        TrapDipoleParameters(
            frequency_hz=7_100_000.0,
            high_band_frequency_hz=14_100_000.0,
            inner_length_m=10.0,
            outer_length_m=5.0,
            trap_frequency_hz=14_100_000.0,
            trap_inductance_h=10e-6,
        ),
        T2FDParameters(
            frequency_hz=3_500_000.0,
            highest_frequency_hz=30_000_000.0,
            length_m=26.0,
            spacing_m=0.9,
        ),
        _yagi(),
        _yagi_folded(),
        replace(
            _yagi(),
            match_type=YagiMatchType.NONE,
            taper_tip_length_m=0.3,
            taper_tip_radius_m=0.0005,
        ),
        MoxonParameters(
            frequency_hz=14_100_000.0,
            width_m=10.0,
            depth_m=3.0,
            reflector_tip_m=1.0,
            driven_tip_m=1.0,
            height_m=10.0,
        ),
        doublet_starting_parameters(DoubletPreset.G5RV),
        doublet_starting_parameters(DoubletPreset.ZS6BKW),
        zepp_starting_parameters(),
    ]


def test_descriptors_do_not_expose_dead_mode_capability_flags() -> None:
    for parameters in _typed_samples():
        availability = optimizer_availability(parameters)
        assert availability.descriptor is not None
        descriptor = availability.descriptor
        assert not hasattr(descriptor, "supports_band_aware")
        assert not hasattr(descriptor, "supports_robust")


def test_every_supported_typed_family_has_a_buildable_descriptor() -> None:
    for parameters in _typed_samples():
        availability = optimizer_availability(parameters)
        assert availability.available, type(parameters).__name__
        descriptor = availability.descriptor
        assert descriptor is not None
        assert descriptor.key == antenna_type_for(parameters)
        rebuilt = descriptor.build_parameters(descriptor.initial_values)
        assert rebuilt == parameters


_CONTEXT_FIELDS = {
    "frequency_hz",
    "orientation",
    "azimuth_deg",
    "material",
    "ground",
    "preset",
    "folded",
    "sides",
    "ring_sides",
    "polarization",
    "driven_index",
    "driven_folded",
    "driven_tip_m",
    "match_type",
    "driven_fold_spacing_m",
    "match_length_m",
    "match_spacing_m",
    "elements",
    "kind",
    "reflector_enabled",
    "termination_enabled",
    "sag_m",
    "taper_tip_length_m",
    "taper_tip_radius_m",
    "loading_coil_enabled",
    "loading_coil_offset_m",
    "loading_coil_inductance_h",
    "loading_coil_resistance_ohm",
    "link_open",
    "top_hat_enabled",
    "high_band_frequency_hz",
    "highest_frequency_hz",
    "counterpoise_azimuth_deg",
    "counterpoise_length_m",
    "counterpoise_height_m",
    "transformer_ratio",
    "transformer_model",
    "transformer_loss_model",
    "design_matching_network",
    "return_path",
    "common_mode_choke",
    "element_count",
    "radial_count",
    "radial_angle_deg",
    "wire_count",
    "disc_gap_m",
    "trap_frequency_hz",
    "feed_gap_m",
    "element_separation_m",
    "bands",
    "feed_section_length_m",
    "installation_return_length_m",
    "matching_capacitance_f",
    "transformer_leakage_inductance_h",
    "bend_enabled",
    "bend_vertical_length_m",
    "mast_diameter_m",
    "mast_offset_m",
    "guy_count",
    "guy_anchor_radius_m",
    "guy_diameter_m",
    "yagi",
    "feed",
}


def test_every_field_is_optimized_or_explicitly_classified_as_context() -> None:
    for parameters in _typed_samples():
        availability = optimizer_availability(parameters)
        assert availability.descriptor is not None
        variable_names = {variable.name for variable in availability.descriptor.variables}
        field_names = {field.name for field in fields(parameters)}
        if isinstance(parameters, YagiParameters):
            field_names |= {f"length_{index}" for index in range(len(parameters.elements))}
            field_names |= {f"gap_{index}" for index in range(1, len(parameters.elements))}
        unclassified = field_names - variable_names - _CONTEXT_FIELDS
        assert not unclassified, (
            f"{type(parameters).__name__} has unclassified fields: {unclassified}"
        )


def test_moxon_optimizer_exposes_the_gap_and_rejects_non_moxon_geometry() -> None:
    parameters = MoxonParameters(
        frequency_hz=14_170_000.0,
        width_m=25.0 * 0.3048,
        depth_m=9.57 * 0.3048,
        reflector_tip_m=4.85 * 0.3048,
        driven_tip_m=4.00 * 0.3048,
        height_m=10.0,
        wire_radius_m=0.000912,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor

    assert "gap_m" in {variable.name for variable in descriptor.variables}
    assert "driven_tip_m" not in {variable.name for variable in descriptor.variables}
    assert descriptor.initial_values["gap_m"] == pytest.approx(parameters.gap_m)
    rebuilt = descriptor.build_parameters(descriptor.initial_values)
    assert rebuilt == parameters

    too_open = dict(descriptor.initial_values)
    too_open["gap_m"] = 1.22
    violations = descriptor.validate(too_open)

    assert any(item.message_key == "optimize.constraint.moxon_geometry" for item in violations)


def test_moxon_defaults_to_target_impedance_and_reports_bound_hits() -> None:
    from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective

    availability = optimizer_availability(
        MoxonParameters(
            frequency_hz=14_170_000.0,
            width_m=25.0 * 0.3048,
            depth_m=9.57 * 0.3048,
            reflector_tip_m=4.85 * 0.3048,
            driven_tip_m=4.00 * 0.3048,
            height_m=10.0,
            wire_radius_m=0.000912,
        )
    )

    assert availability.descriptor is not None
    assert availability.descriptor.default_objective is FamilyOptimizationObjective.TARGET_IMPEDANCE
    assert availability.descriptor.recommends_bound_hits is True


def test_only_array_descriptors_support_a_boom_constraint() -> None:
    yagi = optimizer_availability(_yagi())
    moxon = optimizer_availability(
        MoxonParameters(
            frequency_hz=14_100_000.0,
            width_m=10.0,
            depth_m=3.0,
            reflector_tip_m=1.0,
            driven_tip_m=1.0,
            height_m=10.0,
        )
    )
    dipole = optimizer_availability(_dipole())

    assert yagi.descriptor is not None
    assert moxon.descriptor is not None
    assert dipole.descriptor is not None
    assert yagi.descriptor.supports_boom_constraint is True
    assert moxon.descriptor.supports_boom_constraint is True
    assert dipole.descriptor.supports_boom_constraint is False


def test_biquad_without_a_reflector_does_not_optimize_its_spacing() -> None:
    parameters = biquad_parameters(BiquadKind.SINGLE, reflector_enabled=False)
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    names = {variable.name for variable in availability.descriptor.variables}

    assert "loop_side_m" in names
    assert "base_height_m" in names
    assert "transformer_ratio" in names
    assert "reflector_spacing_m" not in names


def test_beverage_without_termination_does_not_optimize_its_resistance() -> None:
    parameters = beverage_parameters(termination_enabled=False)
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    names = {variable.name for variable in availability.descriptor.variables}

    assert "length_m" in names
    assert "height_m" in names
    assert "transformer_ratio" in names
    assert "termination_resistance_ohm" not in names


def test_beverage_optimizer_includes_the_feed_transformer() -> None:
    parameters = beverage_parameters()
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    transformer = next(
        variable
        for variable in availability.descriptor.variables
        if variable.name == "transformer_ratio"
    )

    assert transformer.choices == (1.0, 4.0, 9.0, 16.0)
    assert availability.descriptor.initial_values["transformer_ratio"] == 9.0
    assert availability.descriptor.context_note_key is not None


def test_linked_dipole_optimizes_the_center_section_only() -> None:
    parameters = loaded_dipole_parameters(link_open=True)
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    names = {variable.name for variable in availability.descriptor.variables}

    assert "link_offset_m" in names
    assert "total_length_m" not in names
    assert "loading_coil_inductance_h" not in names
    assert "loading_coil_resistance_ohm" not in names


def test_discone_optimizes_the_wire_surfaces() -> None:
    availability = optimizer_availability(discone_parameters(wire_count=10))
    assert availability.descriptor is not None

    variables = {variable.name: variable for variable in availability.descriptor.variables}

    assert set(variables) == {
        "cone_height_m",
        "cone_radius_m",
        "disc_radius_m",
        "base_height_m",
        "wire_radius_m",
    }
    rebuilt = availability.descriptor.build_parameters(availability.descriptor.initial_values)
    assert rebuilt.wire_count == 10


def test_hexbeam_optimizes_the_bent_wire_path() -> None:
    availability = optimizer_availability(published_hexbeam_parameters())
    assert availability.descriptor is not None

    variables = {variable.name for variable in availability.descriptor.variables}

    assert variables == {
        "driver_half_length_m",
        "reflector_half_length_m",
        "turning_radius_m",
        "tip_gap_m",
        "height_m",
        "wire_radius_m",
    }
    descriptor = availability.descriptor
    assert descriptor.validate(descriptor.initial_values) == ()

    too_short_reflector = dict(descriptor.initial_values)
    too_short_reflector["reflector_half_length_m"] = 4.0
    assert any(
        violation.name == "reflector_half_length_m"
        and violation.message_key == "hexbeam.constraint.reflector_length"
        for violation in descriptor.validate(too_short_reflector)
    )

    too_long_driver = dict(descriptor.initial_values)
    too_long_driver["driver_half_length_m"] = 1.0
    assert any(
        violation.name == "driver_half_length_m"
        and violation.message_key == "hexbeam.constraint.driver_length"
        for violation in descriptor.validate(too_long_driver)
    )

    tip_past_spreader = dict(descriptor.initial_values)
    tip_past_spreader["reflector_half_length_m"] = 8.25
    assert any(
        violation.name == "tip_gap_m" and violation.message_key == "hexbeam.constraint.tip_gap"
        for violation in descriptor.validate(tip_past_spreader)
    )


def test_multiband_hexbeam_optimizer_is_explicitly_unavailable() -> None:
    primary = published_hexbeam_parameters()
    secondary = published_hexbeam_parameters(frequency_hz=21_200_000.0)
    parameters = replace(
        primary,
        bands=(
            HexbeamBand(
                label="20m",
                frequency_hz=primary.frequency_hz,
                driver_half_length_m=primary.driver_half_length_m,
                reflector_half_length_m=primary.reflector_half_length_m,
                tip_gap_m=primary.tip_gap_m,
                feed_gap_m=primary.feed_gap_m,
                vertical_offset_m=0.0,
            ),
            HexbeamBand(
                label="15m",
                frequency_hz=secondary.frequency_hz,
                driver_half_length_m=secondary.driver_half_length_m,
                reflector_half_length_m=secondary.reflector_half_length_m,
                tip_gap_m=secondary.tip_gap_m,
                feed_gap_m=secondary.feed_gap_m,
                vertical_offset_m=0.2286,
            ),
        ),
    )

    availability = optimizer_availability(parameters)

    assert availability.available is False
    assert availability.reason_key == "optimize.unavailable.hexbeam_multiband"


def test_multiband_hexbeam_band_optimizer_targets_one_band() -> None:
    parameters = published_hexbeam_multiband_parameters(labels=("20m", "15m", "10m"))
    band = parameters.bands[1]

    availability = optimizer_availability(parameters, hexbeam_band="15m")

    assert availability.descriptor is not None
    descriptor = availability.descriptor
    assert {variable.name for variable in descriptor.variables} == {
        "driver_half_length_m",
        "reflector_half_length_m",
        "tip_gap_m",
        "height_m",
    }
    assert descriptor.initial_values["driver_half_length_m"] == pytest.approx(
        band.driver_half_length_m
    )
    assert descriptor.initial_values["reflector_half_length_m"] == pytest.approx(
        band.reflector_half_length_m
    )
    assert descriptor.initial_values["tip_gap_m"] == pytest.approx(band.tip_gap_m)
    assert descriptor.validate(descriptor.initial_values) == ()

    values = dict(descriptor.initial_values)
    values["driver_half_length_m"] += 0.05
    rebuilt = descriptor.build_parameters(values)

    assert rebuilt.bands[0] == parameters.bands[0]
    assert rebuilt.bands[2] == parameters.bands[2]
    assert rebuilt.bands[1].driver_half_length_m == pytest.approx(band.driver_half_length_m + 0.05)
    assert rebuilt.driver_half_length_m == pytest.approx(parameters.driver_half_length_m)
    assert rebuilt.turning_radius_m == pytest.approx(parameters.turning_radius_m)

    assert descriptor.model_builder is not None
    model = descriptor.model_builder(parameters)
    assert model.feed.wire_id == "hexbeam-band2-feed"
    assert descriptor.evaluation_frequency_hz is not None
    assert descriptor.evaluation_frequency_hz(parameters) == pytest.approx(band.frequency_hz)


def test_multiband_hexbeam_band_optimizer_updates_the_primary_scalars() -> None:
    parameters = published_hexbeam_multiband_parameters(labels=("20m", "15m"))
    availability = optimizer_availability(parameters, hexbeam_band="20m")
    assert availability.descriptor is not None
    descriptor = availability.descriptor

    values = dict(descriptor.initial_values)
    values["reflector_half_length_m"] += 0.04
    rebuilt = descriptor.build_parameters(values)

    assert rebuilt.driver_half_length_m == pytest.approx(parameters.driver_half_length_m)
    assert rebuilt.reflector_half_length_m == pytest.approx(
        parameters.reflector_half_length_m + 0.04
    )
    assert rebuilt.bands[0].reflector_half_length_m == pytest.approx(
        parameters.bands[0].reflector_half_length_m + 0.04
    )
    assert rebuilt.bands[1] == parameters.bands[1]


def test_multiband_hexbeam_band_optimizer_rejects_shared_frame_overruns() -> None:
    parameters = published_hexbeam_multiband_parameters(labels=("20m", "15m"))
    availability = optimizer_availability(parameters, hexbeam_band="15m")
    assert availability.descriptor is not None
    descriptor = availability.descriptor

    too_short_reflector = dict(descriptor.initial_values)
    too_short_reflector["reflector_half_length_m"] = 1.0
    assert any(
        item.name == "reflector_half_length_m"
        and item.message_key == "hexbeam.constraint.reflector_length"
        for item in descriptor.validate(too_short_reflector)
    )

    tip_past_spreader = dict(descriptor.initial_values)
    tip_past_spreader["tip_gap_m"] = 5.0
    assert any(
        item.name == "tip_gap_m" and item.message_key == "hexbeam.constraint.tip_gap"
        for item in descriptor.validate(tip_past_spreader)
    )

    too_long_driver = dict(descriptor.initial_values)
    too_long_driver["driver_half_length_m"] = 0.5
    assert any(
        item.name == "driver_half_length_m"
        and item.message_key == "hexbeam.constraint.driver_length"
        for item in descriptor.validate(too_long_driver)
    )

    conductor_overlap = dict(descriptor.initial_values)
    conductor_overlap["tip_gap_m"] = 2.0 * parameters.wire_radius_m
    assert any(
        item.name == "tip_gap_m" and item.message_key == "optimize.constraint.conductor_spacing"
        for item in descriptor.validate(conductor_overlap)
    )


def test_multiband_hexbeam_band_optimizer_rejects_overlapping_bands() -> None:
    parameters = published_hexbeam_multiband_parameters(labels=("20m", "15m"))
    close_20m = replace(
        parameters.bands[0],
        label="20m-close",
        frequency_hz=parameters.bands[0].frequency_hz + 1_000.0,
    )
    overlapping = replace(
        parameters,
        bands=(parameters.bands[0], close_20m, parameters.bands[1]),
    )
    availability = optimizer_availability(overlapping, hexbeam_band="20m-close")
    assert availability.descriptor is not None

    violations = availability.descriptor.validate(availability.descriptor.initial_values)

    assert any(
        item.name == "band_radius" and item.message_key == "hexbeam.constraint.band_collision"
        for item in violations
    )


def test_multiband_hexbeam_unknown_band_stays_unavailable() -> None:
    parameters = published_hexbeam_multiband_parameters(labels=("20m", "15m"))

    availability = optimizer_availability(parameters, hexbeam_band="6m")

    assert availability.available is False
    assert availability.reason_key == "optimize.unavailable.hexbeam_multiband"


def test_trap_yagi_optimizes_the_trap_positions() -> None:
    availability = optimizer_availability(trap_yagi_parameters(element_count=3))
    assert availability.descriptor is not None

    variables = {variable.name: variable for variable in availability.descriptor.variables}

    assert "trap_inset_m" in variables
    assert "trap_inductance_h" in variables
    assert "director_scale" in variables
    assert "director_spacing_m" in variables
    assert "driven_length_m" in variables


def test_quad_beam_optimizes_geometry_and_optional_director() -> None:
    two = quad_beam_parameters(element_count=2)
    three = quad_beam_parameters(element_count=3)
    two_availability = optimizer_availability(two)
    three_availability = optimizer_availability(three)
    assert two_availability.descriptor is not None
    assert three_availability.descriptor is not None

    two_names = {variable.name for variable in two_availability.descriptor.variables}
    three_names = {variable.name for variable in three_availability.descriptor.variables}

    assert "director_spacing_m" not in two_names
    assert "director_scale" not in two_names
    assert "director_spacing_m" in three_names
    assert "director_scale" in three_names
    assert "loop_side_m" in two_names
    assert "reflector_scale" in two_names
    assert "transformer_ratio" in two_names
    assert "transformer_ratio" in three_names


def test_quad_beam_descriptor_exposes_the_transformer_choice() -> None:
    parameters = quad_beam_parameters(element_count=3)
    availability = optimizer_availability(parameters)
    descriptor = availability.descriptor
    assert descriptor is not None

    variable = next(item for item in descriptor.variables if item.name == "transformer_ratio")
    assert variable.kind is VariableKind.CHOICE
    assert variable.locked_by_default
    assert 2.0 in variable.choices
    assert 4.0 in variable.choices

    rebuilt = descriptor.build_parameters({**descriptor.initial_values, "transformer_ratio": 4.0})
    assert isinstance(rebuilt, QuadBeamParameters)
    assert rebuilt.transformer_ratio == pytest.approx(4.0)


def test_vertical_optimizer_covers_radial_droop_with_a_tip_clearance_constraint() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=3.0,
        radial_count=4,
        radial_length_m=5.0,
        radial_droop_deg=20.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    variables = {variable.name: variable for variable in descriptor.variables}

    assert "radial_droop_deg" in variables
    assert variables["radial_droop_deg"].locked_by_default is True
    assert variables["radial_droop_deg"].maximum > parameters.radial_droop_deg
    assert descriptor.initial_values["radial_droop_deg"] == pytest.approx(20.0)
    assert descriptor.build_parameters(descriptor.initial_values) == parameters

    too_steep = dict(descriptor.initial_values)
    too_steep["radial_droop_deg"] = 40.0
    violations = descriptor.validate(too_steep)

    assert any(item.message_key == "optimize.constraint.radial_tip_height" for item in violations)


def test_vertical_optimizer_bounds_include_a_droop_at_the_tip_limit() -> None:
    base = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=3.0,
        radial_count=4,
        radial_length_m=5.0,
    )
    parameters = replace(base, radial_droop_deg=base.max_radial_droop_deg)
    descriptor = optimizer_availability(parameters).descriptor
    assert descriptor is not None
    variable = next(item for item in descriptor.variables if item.name == "radial_droop_deg")

    assert descriptor.initial_values["radial_droop_deg"] == pytest.approx(
        parameters.radial_droop_deg
    )
    assert variable.minimum <= descriptor.initial_values["radial_droop_deg"] <= variable.maximum


def test_stacked_yagi_optimizer_uses_the_top_height_envelope() -> None:
    parameters = StackedYagiParameters(
        yagi=_stack_base_yagi(),
        count=2,
        spacing_m=10.6,
        phase_step_deg=90.0,
        max_top_height_m=25.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor

    variables = {variable.name: variable for variable in descriptor.variables}
    assert set(variables) == {
        "spacing_m",
        "phase_step_deg",
        "amplitude_ratio",
        "count",
        "max_top_height_m",
    }
    assert variables["spacing_m"].minimum == pytest.approx(parameters.minimum_spacing_m)
    assert variables["spacing_m"].maximum == pytest.approx(parameters.maximum_spacing_m)
    assert variables["phase_step_deg"].minimum == pytest.approx(-180.0)
    assert variables["phase_step_deg"].maximum == pytest.approx(180.0)
    assert variables["amplitude_ratio"].locked_by_default
    assert variables["count"].locked_by_default
    assert variables["max_top_height_m"].locked_by_default
    assert descriptor.build_parameters(descriptor.initial_values) == parameters

    too_wide = dict(descriptor.initial_values)
    too_wide["spacing_m"] = parameters.maximum_spacing_m + 0.5
    violations = descriptor.validate(too_wide)
    assert any(
        item.message_key == "optimize.constraint.stacked_yagi_envelope" for item in violations
    )

    too_tight = dict(descriptor.initial_values)
    too_tight["spacing_m"] = parameters.minimum_spacing_m - 0.5
    assert any(
        item.message_key == "optimize.constraint.stacked_yagi_overlap"
        for item in descriptor.validate(too_tight)
    )

    bad_phase = dict(descriptor.initial_values)
    bad_phase["phase_step_deg"] = 200.0
    assert any(
        item.message_key == "stacked_yagi.constraint.phase"
        for item in descriptor.validate(bad_phase)
    )


def test_stacked_yagi_phase_line_optimizer_moves_the_line_increment() -> None:
    feed = StackedYagiFeed(
        mode=StackedYagiFeedMode.PHASE_LINES,
        reference_length_m=2.0,
        line_increment_m=2.0,
        velocity_factor=0.8,
        characteristic_impedance_ohm=75.0,
        splitter_loss_db=0.4,
    )
    parameters = StackedYagiParameters(
        yagi=_stack_base_yagi(),
        count=2,
        spacing_m=10.6,
        max_top_height_m=25.0,
        feed=feed,
    )
    descriptor = optimizer_availability(parameters).descriptor
    assert descriptor is not None

    variables = {variable.name: variable for variable in descriptor.variables}
    assert "line_increment_m" in variables
    assert "phase_step_deg" in variables
    assert variables["phase_step_deg"].locked_by_default
    assert descriptor.build_parameters(descriptor.initial_values) == parameters
    assert descriptor.validate(descriptor.initial_values) == ()

    too_long = dict(descriptor.initial_values)
    too_long["line_increment_m"] = variables["line_increment_m"].maximum + 0.1
    assert any(
        item.message_key == "stacked_yagi.constraint.line_increment"
        for item in descriptor.validate(too_long)
    )


def test_stacked_yagi_without_an_envelope_is_unavailable() -> None:
    parameters = StackedYagiParameters(
        yagi=_stack_base_yagi(),
        count=2,
        spacing_m=10.6,
    )

    availability = optimizer_availability(parameters)

    assert availability.descriptor is None
    assert availability.reason_key == "optimize.unavailable.stacked_yagi_envelope"


def test_phased_vertical_optimizes_geometry_and_excitation() -> None:
    parameters = phased_vertical_parameters(
        element_count=3,
        phase_step_deg=120.0,
        amplitude_taper=0.2,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    variables = {variable.name: variable for variable in availability.descriptor.variables}

    assert set(variables) == {
        "height_m",
        "spacing_m",
        "base_height_m",
        "phase_step_deg",
        "amplitude_taper",
        "radial_length_m",
        "wire_radius_m",
    }
    assert variables["phase_step_deg"].minimum == pytest.approx(-180.0)
    assert variables["phase_step_deg"].maximum == pytest.approx(180.0)
    assert variables["amplitude_taper"].minimum == pytest.approx(0.0)
    assert variables["amplitude_taper"].maximum == pytest.approx(0.9)


def test_phased_vertical_without_radials_does_not_optimize_radial_length() -> None:
    parameters = phased_vertical_parameters(radial_count=0, radial_length_m=0.0)
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    names = {variable.name for variable in availability.descriptor.variables}

    assert "radial_length_m" not in names
    assert "height_m" in names


def test_descriptor_initial_values_rebuild_the_current_parameters() -> None:
    cases = [
        _dipole(),
        _vertical(),
        _yagi(),
        _yagi_folded(),
        scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0),
        scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0),
    ]

    for parameters in cases:
        availability = optimizer_availability(parameters)
        assert availability.descriptor is not None
        descriptor = availability.descriptor
        rebuilt = descriptor.build_parameters(descriptor.initial_values)
        assert rebuilt == parameters


def test_yagi_optimizer_blocks_a_gross_frequency_mismatch() -> None:
    parameters = YagiParameters(
        frequency_hz=2_400_000_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=1.0,
    )

    availability = optimizer_availability(parameters)

    assert availability.available is False
    assert availability.reason_key == "optimize.unavailable.frequency_mismatch"
    assert availability.reason_values["family"] == "yagi"
    assert availability.reason_values["element"] == 1


def test_unavailable_families_have_explicit_reasons() -> None:
    magnetic = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.0,
    )
    random_wire = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=17.0,
        preset=EndFedPreset.RANDOM_WIRE,
    )
    custom = _custom()

    for parameters, expected in (
        (magnetic, "optimize.unavailable.magnetic_loop"),
        (random_wire, "optimize.unavailable.random_wire"),
        (custom, "optimize.unavailable.custom_geometry"),
    ):
        availability = optimizer_availability(parameters)
        assert not availability.available
        assert availability.reason_key == expected


def test_custom_generator_is_not_silently_treated_as_custom_geometry() -> None:
    parameters = _custom()
    with_generator = parameters.__class__(
        **{
            **{
                field.name: getattr(parameters, field.name)
                for field in fields(parameters)
                if field.name not in {"generator_id", "generator_name"}
            },
            "generator_id": "zs6bkw",
            "generator_name": "ZS6BKW",
        }
    )

    availability = optimizer_availability(with_generator)

    assert not availability.available
    assert availability.reason_key == "optimize.unavailable.custom_generator"


def test_shortened_endfed_optimizer_marks_the_matching_network_as_context() -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
    from antennadesk.domain.optimization.registry import optimizer_availability

    shortened = optimizer_availability(shortened_efhw_80_10_parameters())
    standard = optimizer_availability(EndFedParameters(frequency_hz=7_100_000.0, length_m=20.0))

    from antennadesk.domain.optimization.descriptor import FamilyOptimizationObjective

    assert shortened.descriptor is not None
    assert shortened.descriptor.context_note_key == "optimize.endfed.matching_context"
    assert shortened.descriptor.default_objective is FamilyOptimizationObjective.MIN_SWR
    assert shortened.descriptor.recommends_bound_hits is True
    assert standard.descriptor is not None
    assert standard.descriptor.context_note_key is None
    assert standard.descriptor.recommends_bound_hits is True
    assert standard.descriptor.default_objective is FamilyOptimizationObjective.TARGET_IMPEDANCE


def test_design_specific_l_network_adds_bounded_optimizer_variables() -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_40_10_parameters
    from antennadesk.domain.antennas.matching_network import LNetwork
    from antennadesk.domain.optimization.registry import optimizer_availability

    network = LNetwork(
        series_inductance_h=1.2e-6,
        shunt_capacitance_f=82e-12,
    )
    parameters = replace(
        shortened_efhw_40_10_parameters(),
        design_matching_network=network,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    names = {variable.name for variable in descriptor.variables}
    assert "design_series_inductance_h" in names
    assert "design_shunt_capacitance_f" in names
    assert "design_series_capacitance_f" not in names
    assert "design_shunt_inductance_h" not in names

    rebuilt = descriptor.build_parameters(descriptor.initial_values)
    assert rebuilt.design_matching_network is not None
    assert rebuilt.design_matching_network.series_inductance_h == pytest.approx(1.2e-6)
    assert rebuilt.design_matching_network.shunt_capacitance_f == pytest.approx(82e-12)


def test_design_pi_network_adds_its_active_component_variables() -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_40_10_parameters
    from antennadesk.domain.antennas.matching_network import PiNetwork
    from antennadesk.domain.optimization.registry import optimizer_availability

    network = PiNetwork(
        input_shunt_capacitance_f=120e-12,
        series_inductance_h=1.1e-6,
        output_shunt_capacitance_f=68e-12,
    )
    parameters = replace(
        shortened_efhw_40_10_parameters(),
        design_matching_network=network,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    names = {variable.name for variable in descriptor.variables}
    assert "design_input_shunt_capacitance_f" in names
    assert "design_series_inductance_h" in names
    assert "design_output_shunt_capacitance_f" in names
    assert "design_shunt_capacitance_f" not in names

    rebuilt = descriptor.build_parameters(descriptor.initial_values)
    assert isinstance(rebuilt.design_matching_network, PiNetwork)
    assert rebuilt.design_matching_network == network


def test_coax_shield_endfed_optimizer_searches_the_return_length() -> None:
    from antennadesk.domain.antennas.endfed import (
        EndFedReturnPath,
        shortened_efhw_40_10_parameters,
    )
    from antennadesk.domain.optimization.registry import optimizer_availability

    parameters = replace(
        shortened_efhw_40_10_parameters(),
        return_path=EndFedReturnPath.COAX_SHIELD,
        counterpoise_length_m=5.0,
        counterpoise_height_m=0.0,
        counterpoise_azimuth_deg=180.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    names = {variable.name for variable in availability.descriptor.variables}
    assert "counterpoise_length_m" in names
    assert "counterpoise_height_m" not in names
    assert "counterpoise_azimuth_deg" in names


def test_log_periodic_has_an_explicit_unavailable_reason() -> None:
    availability = optimizer_availability(cebik_10m_log_periodic_parameters())

    assert not availability.available
    assert availability.reason_key == "optimize.unavailable.log_periodic"


def test_bent_endfed_optimizer_searches_the_bend_instead_of_the_end_height() -> None:
    parameters = replace(
        shortened_efhw_80_10_parameters(),
        bend_enabled=True,
        bend_vertical_length_m=8.0,
    )
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None
    descriptor = availability.descriptor
    names = {variable.name for variable in descriptor.variables}

    assert "bend_vertical_length_m" in names
    assert "end_height_m" not in names
    assert descriptor.validate(descriptor.initial_values) == ()
    assert descriptor.build_parameters(descriptor.initial_values) == parameters
