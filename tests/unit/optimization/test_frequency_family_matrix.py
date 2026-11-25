# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency/family matrix for the optimizer bound and geometry contract."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, fields

import pytest

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters
from antennadesk.domain.antennas.design import AntennaDesignParameters, antenna_type_for
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.moxon import (
    MoxonParameters,
    validate_moxon_geometry,
)
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
from antennadesk.domain.antennas.stacked_yagi import StackedYagiParameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.transmission_line_doublet import (
    DoubletPreset,
    doublet_starting_parameters,
)
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.antennas.zepp import zepp_starting_parameters
from antennadesk.domain.common import units
from antennadesk.domain.design.yagi_reference import dl6wu_elements
from antennadesk.domain.optimization.registry import (
    SUPPORTED_OPTIMIZER_TYPES,
    optimizer_availability,
)
from antennadesk.domain.optimization.variables import variable_bound_issue

FREQUENCIES_HZ = (
    1_800_000.0,
    3_500_000.0,
    7_000_000.0,
    14_000_000.0,
    28_000_000.0,
    50_000_000.0,
    144_000_000.0,
    435_000_000.0,
    1_296_000_000.0,
    2_400_000_000.0,
    5_800_000_000.0,
)

ALL_FREQUENCIES = FREQUENCIES_HZ
HF_FREQUENCIES = FREQUENCIES_HZ[:5]
LOW_VHF_FREQUENCIES = FREQUENCIES_HZ[:6]

MOXON_REFERENCE_HZ = 14_170_000.0
MOXON_REFERENCE_WIDTH_M = 25.00 * 0.3048
MOXON_REFERENCE_DEPTH_M = 9.57 * 0.3048
MOXON_REFERENCE_REFLECTOR_TIP_M = 4.85 * 0.3048
MOXON_REFERENCE_DRIVEN_TIP_M = 4.00 * 0.3048
MOXON_MAX_WAVELENGTH_RATIO = 0.10


def _assert_rebuilds(
    expected: AntennaDesignParameters,
    actual: AntennaDesignParameters,
) -> None:
    """Compare every field, tolerating derived-value round-off.

    The Moxon optimizer derives ``driven_tip_m`` from depth, gap, and reflector
    tip, so rebuilding the initial vector can differ in the last bit.
    """

    assert type(actual) is type(expected)
    for field in fields(expected):
        left = getattr(expected, field.name)
        right = getattr(actual, field.name)
        if isinstance(left, float):
            assert math.isclose(left, right, rel_tol=1e-12, abs_tol=0.0), field.name
        else:
            assert left == right, field.name


def _frequency_id(frequency_hz: float) -> str:
    if frequency_hz >= 1_000_000_000.0:
        return f"{frequency_hz / 1_000_000_000.0:g}GHz"
    return f"{frequency_hz / 1_000_000.0:g}MHz"


def _wavelength(frequency_hz: float) -> float:
    return units.wavelength_m(frequency_hz)


def _radius(frequency_hz: float) -> float:
    if frequency_hz < 30_000_000.0:
        return 0.001
    if frequency_hz < 300_000_000.0:
        return 0.0006
    if frequency_hz < 1_000_000_000.0:
        return 0.0004
    return 0.0003


def _height(frequency_hz: float) -> float:
    if frequency_hz < 30_000_000.0:
        return 10.0
    if frequency_hz < 300_000_000.0:
        return 2.0
    if frequency_hz < 1_000_000_000.0:
        return 1.0
    return 0.5


def _dipole(frequency_hz: float) -> AntennaDesignParameters:
    return DipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=0.468 * _wavelength(frequency_hz),
        height_m=_height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _folded_dipole(frequency_hz: float) -> AntennaDesignParameters:
    return FoldedDipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=0.468 * _wavelength(frequency_hz),
        height_m=_height(frequency_hz),
        spacing_m=0.02 * _wavelength(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _loop(frequency_hz: float) -> AntennaDesignParameters:
    return LoopParameters(
        frequency_hz=frequency_hz,
        circumference_m=1.05 * _wavelength(frequency_hz),
        height_m=_height(frequency_hz),
        sides=4,
        wire_radius_m=_radius(frequency_hz),
    )


def _vertical(frequency_hz: float) -> AntennaDesignParameters:
    return VerticalParameters(
        frequency_hz=frequency_hz,
        height_m=0.25 * _wavelength(frequency_hz),
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=0.25 * _wavelength(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _inverted_v(frequency_hz: float) -> AntennaDesignParameters:
    leg_length = 0.25 * _wavelength(frequency_hz)
    return InvertedVParameters(
        frequency_hz=frequency_hz,
        leg_length_m=leg_length,
        apex_height_m=max(_height(frequency_hz), leg_length),
        wire_radius_m=_radius(frequency_hz),
    )


def _inverted_l(frequency_hz: float) -> AntennaDesignParameters:
    return InvertedLParameters(
        frequency_hz=frequency_hz,
        vertical_height_m=0.25 * _wavelength(frequency_hz),
        horizontal_length_m=0.25 * _wavelength(frequency_hz),
        base_height_m=min(1.0, _height(frequency_hz)),
        wire_radius_m=_radius(frequency_hz),
    )


def _j_pole(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    stub = 0.25 * wavelength
    return JPoleParameters(
        frequency_hz=frequency_hz,
        radiator_height_m=0.75 * wavelength,
        stub_length_m=stub,
        spacing_m=0.02 * wavelength,
        feed_offset_m=0.25 * stub,
        gap_m=max(0.01 * wavelength, 4.0 * _radius(frequency_hz)),
        base_height_m=min(0.25, _height(frequency_hz)),
        folded=True,
        wire_radius_m=_radius(frequency_hz),
    )


def _ringo(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    return RingoParameters(
        frequency_hz=frequency_hz,
        radiator_height_m=0.5 * wavelength,
        ring_diameter_m=0.05 * wavelength,
        ring_height_m=0.5 * _height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _moxon(frequency_hz: float) -> MoxonParameters:
    scale = MOXON_REFERENCE_HZ / frequency_hz
    depth = MOXON_REFERENCE_DEPTH_M * scale
    reflector_tip = MOXON_REFERENCE_REFLECTOR_TIP_M * scale
    driven_tip = MOXON_REFERENCE_DRIVEN_TIP_M * scale
    gap = depth - reflector_tip - driven_tip
    return MoxonParameters(
        frequency_hz=frequency_hz,
        width_m=MOXON_REFERENCE_WIDTH_M * scale,
        depth_m=depth,
        reflector_tip_m=reflector_tip,
        driven_tip_m=driven_tip,
        height_m=_height(frequency_hz),
        wire_radius_m=min(_radius(frequency_hz), gap / 5.0),
    )


def _yagi(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    radius = min(_radius(frequency_hz), 0.002 * 432_000_000.0 / frequency_hz)
    return YagiParameters(
        frequency_hz=frequency_hz,
        elements=tuple(
            YagiElement(
                position_m=spacing * wavelength,
                length_m=length * wavelength,
                radius_m=radius,
            )
            for length, spacing in dl6wu_elements(5)
        ),
        height_m=_height(frequency_hz),
        driven_index=1,
    )


def _stacked_yagi(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    yagi = _yagi(frequency_hz)
    assert isinstance(yagi, YagiParameters)
    spacing = 0.5 * wavelength
    return StackedYagiParameters(
        yagi=yagi,
        count=2,
        spacing_m=spacing,
        phase_step_deg=90.0,
        max_top_height_m=yagi.height_m + spacing + 0.5 * wavelength,
    )


def _biquad(frequency_hz: float) -> AntennaDesignParameters:
    return biquad_parameters(
        BiquadKind.SINGLE,
        frequency_hz=frequency_hz,
        base_height_m=min(0.25, _height(frequency_hz)),
        wire_radius_m=_radius(frequency_hz),
    )


def _quad_beam(frequency_hz: float) -> AntennaDesignParameters:
    return quad_beam_parameters(
        frequency_hz=frequency_hz,
        element_count=3,
        height_m=_height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _discone(frequency_hz: float) -> AntennaDesignParameters:
    disc_gap = max(0.001, 0.01 * 145_000_000.0 / frequency_hz)
    return discone_parameters(
        frequency_hz=frequency_hz,
        base_height_m=0.5,
        disc_gap_m=disc_gap,
        wire_radius_m=min(_radius(frequency_hz), disc_gap / 4.0),
    )


def _hexbeam(frequency_hz: float) -> AntennaDesignParameters:
    return published_hexbeam_parameters(
        frequency_hz=frequency_hz,
        height_m=_height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _scv(frequency_hz: float) -> AntennaDesignParameters:
    return scv_parameters(
        ScvKind.HALF_SQUARE,
        frequency_hz,
        base_height_m=2.5,
        wire_radius_m=_radius(frequency_hz),
    )


def _beverage(frequency_hz: float) -> AntennaDesignParameters:
    return beverage_parameters(
        frequency_hz=frequency_hz,
        wire_radius_m=_radius(frequency_hz),
    )


def _loaded_dipole(frequency_hz: float) -> AntennaDesignParameters:
    length = 0.468 * _wavelength(frequency_hz)
    return loaded_dipole_parameters(
        frequency_hz=frequency_hz,
        total_length_m=length,
        height_m=_height(frequency_hz),
        link_offset_m=0.25 * length,
        wire_radius_m=_radius(frequency_hz),
    )


def _ocfd(frequency_hz: float) -> AntennaDesignParameters:
    return OCFDParameters(
        frequency_hz=frequency_hz,
        total_length_m=0.9 * _wavelength(frequency_hz),
        height_m=_height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _endfed(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    height = _height(frequency_hz)
    return EndFedParameters(
        frequency_hz=frequency_hz,
        length_m=0.5 * wavelength,
        feed_height_m=0.5 * height,
        end_height_m=0.5 * height,
        counterpoise_length_m=0.1 * wavelength,
        wire_radius_m=_radius(frequency_hz),
    )


def _fan_dipole(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    longest = 0.468 * wavelength
    return FanDipoleParameters(
        frequency_hz=frequency_hz,
        elements=(
            FanElement(longest, 110.0),
            FanElement(0.234 * wavelength, 90.0),
        ),
        apex_height_m=max(_height(frequency_hz), longest),
        wire_radius_m=_radius(frequency_hz),
    )


def _trap_dipole(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    return TrapDipoleParameters(
        frequency_hz=frequency_hz,
        high_band_frequency_hz=2.0 * frequency_hz,
        inner_length_m=0.25 * wavelength,
        outer_length_m=0.125 * wavelength,
        trap_frequency_hz=2.0 * frequency_hz,
        trap_inductance_h=10e-6,
        height_m=_height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _trap_yagi(frequency_hz: float) -> AntennaDesignParameters:
    return trap_yagi_parameters(
        frequency_hz=frequency_hz,
        high_band_frequency_hz=2.0 * frequency_hz,
        element_count=3,
        height_m=_height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _t2fd(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    return T2FDParameters(
        frequency_hz=frequency_hz,
        highest_frequency_hz=10.0 * frequency_hz,
        length_m=0.4 * wavelength,
        spacing_m=0.01 * wavelength,
        height_m=_height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _doublet(frequency_hz: float) -> AntennaDesignParameters:
    return doublet_starting_parameters(
        DoubletPreset.G5RV,
        frequency_hz=frequency_hz,
        height_m=_height(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _zepp(frequency_hz: float) -> AntennaDesignParameters:
    return zepp_starting_parameters(
        frequency_hz=frequency_hz,
        base_height_m=min(0.25, _height(frequency_hz)),
        spacing_m=0.02 * _wavelength(frequency_hz),
        wire_radius_m=_radius(frequency_hz),
    )


def _phased_vertical(frequency_hz: float) -> AntennaDesignParameters:
    wavelength = _wavelength(frequency_hz)
    return phased_vertical_parameters(
        frequency_hz=frequency_hz,
        element_count=2,
        height_m=0.25 * wavelength,
        spacing_m=0.25 * wavelength,
        base_height_m=0.25,
        phase_step_deg=90.0,
        radial_count=4,
        radial_length_m=0.25 * wavelength,
        wire_radius_m=_radius(frequency_hz),
    )


@dataclass(frozen=True)
class _MatrixCase:
    name: str
    builder: Callable[[float], AntennaDesignParameters]
    frequencies: tuple[float, ...]


CASES = (
    _MatrixCase("dipole", _dipole, ALL_FREQUENCIES),
    _MatrixCase("folded-dipole", _folded_dipole, ALL_FREQUENCIES),
    _MatrixCase("loop", _loop, ALL_FREQUENCIES),
    _MatrixCase("vertical", _vertical, ALL_FREQUENCIES),
    _MatrixCase("inverted-v", _inverted_v, ALL_FREQUENCIES),
    _MatrixCase("inverted-l", _inverted_l, ALL_FREQUENCIES),
    _MatrixCase("j-pole", _j_pole, ALL_FREQUENCIES),
    _MatrixCase("ringo", _ringo, ALL_FREQUENCIES),
    _MatrixCase("moxon", _moxon, ALL_FREQUENCIES),
    _MatrixCase("yagi", _yagi, ALL_FREQUENCIES),
    _MatrixCase("biquad", _biquad, ALL_FREQUENCIES),
    _MatrixCase("quad-beam", _quad_beam, ALL_FREQUENCIES),
    _MatrixCase("discone", _discone, ALL_FREQUENCIES),
    _MatrixCase("loaded-dipole", _loaded_dipole, ALL_FREQUENCIES),
    _MatrixCase("ocfd", _ocfd, ALL_FREQUENCIES),
    _MatrixCase("endfed", _endfed, ALL_FREQUENCIES),
    _MatrixCase("fan-dipole", _fan_dipole, ALL_FREQUENCIES),
    _MatrixCase("t2fd", _t2fd, LOW_VHF_FREQUENCIES),
    _MatrixCase("zepp", _zepp, ALL_FREQUENCIES),
    _MatrixCase("phased-vertical", _phased_vertical, FREQUENCIES_HZ[:8]),
    _MatrixCase("stacked-yagi", _stacked_yagi, ALL_FREQUENCIES),
    _MatrixCase("hexbeam", _hexbeam, (7_000_000.0, 14_000_000.0, 28_000_000.0, 50_000_000.0)),
    _MatrixCase("scv-half-square", _scv, LOW_VHF_FREQUENCIES),
    _MatrixCase("beverage", _beverage, HF_FREQUENCIES),
    _MatrixCase("trap-dipole", _trap_dipole, HF_FREQUENCIES),
    _MatrixCase("trap-yagi", _trap_yagi, HF_FREQUENCIES),
    _MatrixCase("doublet-g5rv", _doublet, (14_000_000.0,)),
)

_MATRIX_PARAMETERS = tuple(
    pytest.param(
        case,
        frequency_hz,
        id=f"{case.name}-{_frequency_id(frequency_hz)}",
    )
    for case in CASES
    for frequency_hz in case.frequencies
)


@pytest.mark.parametrize(("case", "frequency_hz"), _MATRIX_PARAMETERS)
def test_matrix_preserves_optimizer_bounds_and_geometry(
    case: _MatrixCase,
    frequency_hz: float,
) -> None:
    parameters = case.builder(frequency_hz)
    availability = optimizer_availability(parameters)

    assert availability.available, availability.reason_key
    descriptor = availability.descriptor
    assert descriptor is not None
    assert descriptor.key == antenna_type_for(parameters)

    for variable in descriptor.variables:
        value = descriptor.initial_values[variable.name]
        assert variable.minimum <= value <= variable.maximum, variable.name
        assert variable.maximum - variable.minimum > 0.0, variable.name
        assert variable.step > 0.0, variable.name
        assert variable_bound_issue(variable, value) is None, variable.name

    rebuilt = descriptor.build_parameters(descriptor.initial_values)
    _assert_rebuilds(parameters, rebuilt)
    assert descriptor.validate(descriptor.initial_values) == ()


def test_matrix_covers_every_required_frequency() -> None:
    covered = {frequency_hz for case in CASES for frequency_hz in case.frequencies}

    assert covered == set(FREQUENCIES_HZ)


def test_matrix_covers_every_supported_optimizer_type() -> None:
    covered = {type(case.builder(case.frequencies[0])) for case in CASES}

    assert covered == set(SUPPORTED_OPTIMIZER_TYPES)


def test_moxon_matrix_cases_stay_inside_the_geometry_envelope() -> None:
    for case in CASES:
        if case.name != "moxon":
            continue
        for frequency_hz in case.frequencies:
            parameters = case.builder(frequency_hz)
            assert isinstance(parameters, MoxonParameters)
            wavelength = _wavelength(frequency_hz)
            gap = parameters.gap_m

            assert 0.004 <= gap / wavelength <= MOXON_MAX_WAVELENGTH_RATIO
            assert parameters.gap_m > 2.0 * parameters.wire_radius_m
            assert (
                validate_moxon_geometry(
                    frequency_hz=parameters.frequency_hz,
                    width_m=parameters.width_m,
                    depth_m=parameters.depth_m,
                    reflector_tip_m=parameters.reflector_tip_m,
                    driven_tip_m=parameters.driven_tip_m,
                    wire_radius_m=parameters.wire_radius_m,
                )
                == ()
            )


def test_yagi_matrix_cases_stay_inside_the_element_contract() -> None:
    for case in CASES:
        if case.name != "yagi":
            continue
        for frequency_hz in case.frequencies:
            parameters = case.builder(frequency_hz)
            assert isinstance(parameters, YagiParameters)
            wavelength = _wavelength(frequency_hz)
            max_radius = max(element.radius_m for element in parameters.elements)

            for index, element in enumerate(parameters.elements):
                assert 0.35 <= element.length_m / wavelength <= 0.65
                if index == 0:
                    continue
                gap = element.position_m - parameters.elements[index - 1].position_m
                assert gap >= 8.0 * max_radius


def test_2_4ghz_moxon_bounds_reject_the_old_067_lambda_gap() -> None:
    parameters = _moxon(2_400_000_000.0)
    availability = optimizer_availability(parameters)

    assert availability.descriptor is not None
    descriptor = availability.descriptor
    width = next(variable for variable in descriptor.variables if variable.name == "width_m")
    depth = next(variable for variable in descriptor.variables if variable.name == "depth_m")

    assert width.minimum <= parameters.width_m <= width.maximum
    assert depth.minimum <= parameters.depth_m <= depth.maximum

    wavelength = _wavelength(parameters.frequency_hz)
    assert parameters.gap_m / wavelength <= MOXON_MAX_WAVELENGTH_RATIO

    old_geometry = {
        **descriptor.initial_values,
        "gap_m": 0.67 * wavelength,
    }
    assert descriptor.validate(old_geometry)

    # The old failure mode is representable only with a depth larger than the
    # gap; build it explicitly so the envelope can reject the 0.67 lambda gap.
    assert validate_moxon_geometry(
        frequency_hz=parameters.frequency_hz,
        width_m=0.45 * wavelength,
        depth_m=1.0 * wavelength,
        reflector_tip_m=0.10 * wavelength,
        driven_tip_m=0.23 * wavelength,
        wire_radius_m=parameters.wire_radius_m,
    )
