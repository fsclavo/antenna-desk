# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import fields, replace
from typing import get_args

import pytest

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import (
    BiquadKind,
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
from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
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
    "element_count",
    "radial_count",
    "radial_angle_deg",
    "wire_count",
    "disc_gap_m",
    "trap_frequency_hz",
    "feed_gap_m",
    "element_separation_m",
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
    assert "reflector_spacing_m" not in names


def test_beverage_without_termination_does_not_optimize_its_resistance() -> None:
    parameters = beverage_parameters(termination_enabled=False)
    availability = optimizer_availability(parameters)
    assert availability.descriptor is not None

    names = {variable.name for variable in availability.descriptor.variables}

    assert "length_m" in names
    assert "height_m" in names
    assert "termination_resistance_ohm" not in names


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
