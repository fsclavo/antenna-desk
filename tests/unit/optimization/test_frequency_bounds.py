# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""HF3: every supported optimizer family keeps sane relative bounds."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters
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
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.transmission_line_doublet import (
    DoubletPreset,
    TransmissionLineDoubletParameters,
)
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.antennas.zepp import zepp_starting_parameters
from antennadesk.domain.optimization.registry import optimizer_availability

_C_M_S = 299_792_458.0
_FOOT_M = 0.3048
_FREQUENCIES_HZ = (1_800_000.0, 14_000_000.0, 144_000_000.0, 2_400_000_000.0, 5_800_000_000.0)
_WIRE_RADIUS_M = 0.0005


def _wavelength(frequency_hz: float) -> float:
    return _C_M_S / frequency_hz


def _dipole(frequency_hz: float) -> DipoleParameters:
    wavelength = _wavelength(frequency_hz)
    return DipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=0.5 * wavelength,
        height_m=max(1.0, 0.25 * wavelength),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _folded_dipole(frequency_hz: float) -> FoldedDipoleParameters:
    wavelength = _wavelength(frequency_hz)
    return FoldedDipoleParameters(
        frequency_hz=frequency_hz,
        total_length_m=0.5 * wavelength,
        height_m=max(1.0, 0.25 * wavelength),
        spacing_m=max(4.0 * _WIRE_RADIUS_M, 0.01 * wavelength),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _inverted_v(frequency_hz: float) -> InvertedVParameters:
    leg = 0.25 * _wavelength(frequency_hz)
    return InvertedVParameters(
        frequency_hz=frequency_hz,
        leg_length_m=leg,
        apex_height_m=0.8 * leg,
        included_angle_deg=90.0,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _vertical(frequency_hz: float) -> VerticalParameters:
    wavelength = _wavelength(frequency_hz)
    return VerticalParameters(
        frequency_hz=frequency_hz,
        height_m=0.25 * wavelength,
        base_height_m=0.001,
        radial_count=4,
        radial_length_m=0.25 * wavelength,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _j_pole(frequency_hz: float) -> JPoleParameters:
    wavelength = _wavelength(frequency_hz)
    return JPoleParameters(
        frequency_hz=frequency_hz,
        radiator_height_m=0.5 * wavelength,
        stub_length_m=0.25 * wavelength,
        spacing_m=max(4.0 * _WIRE_RADIUS_M, 0.01 * wavelength),
        feed_offset_m=0.05 * wavelength,
        gap_m=max(4.0 * _WIRE_RADIUS_M, 0.005 * wavelength),
        base_height_m=max(0.001, 0.01 * wavelength),
        folded=True,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _ringo(frequency_hz: float) -> RingoParameters:
    wavelength = _wavelength(frequency_hz)
    return RingoParameters(
        frequency_hz=frequency_hz,
        radiator_height_m=0.5 * wavelength,
        ring_diameter_m=0.05 * wavelength,
        ring_height_m=0.25 * wavelength,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _quad(frequency_hz: float) -> object:
    return quad_beam_parameters(
        frequency_hz=frequency_hz,
        element_count=3,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _discone(frequency_hz: float) -> object:
    return discone_parameters(
        frequency_hz=frequency_hz,
        base_height_m=0.001,
        disc_gap_m=max(4.0 * _WIRE_RADIUS_M, 0.001 * _wavelength(frequency_hz)),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _hexbeam(frequency_hz: float) -> object:
    return published_hexbeam_parameters(
        frequency_hz=frequency_hz,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _biquad(frequency_hz: float) -> object:
    return biquad_parameters(
        BiquadKind.SINGLE,
        frequency_hz=frequency_hz,
        base_height_m=max(0.001, 0.01 * _wavelength(frequency_hz)),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _moxon(frequency_hz: float) -> MoxonParameters:
    scale = 14_170_000.0 / frequency_hz
    return MoxonParameters(
        frequency_hz=frequency_hz,
        width_m=25.00 * _FOOT_M * scale,
        depth_m=9.57 * _FOOT_M * scale,
        reflector_tip_m=4.85 * _FOOT_M * scale,
        driven_tip_m=4.00 * _FOOT_M * scale,
        height_m=max(1.0, 0.25 * _wavelength(frequency_hz)),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _yagi(frequency_hz: float) -> YagiParameters:
    wavelength = _wavelength(frequency_hz)
    return YagiParameters(
        frequency_hz=frequency_hz,
        elements=(
            YagiElement(
                position_m=0.0,
                length_m=0.5 * wavelength,
                radius_m=_WIRE_RADIUS_M,
            ),
            YagiElement(
                position_m=0.1 * wavelength,
                length_m=0.48 * wavelength,
                radius_m=_WIRE_RADIUS_M,
            ),
        ),
        height_m=max(1.0, 0.25 * wavelength),
    )


def _loop(frequency_hz: float) -> LoopParameters:
    wavelength = _wavelength(frequency_hz)
    return LoopParameters(
        frequency_hz=frequency_hz,
        circumference_m=wavelength,
        height_m=max(1.0, 0.2 * wavelength),
        sides=16,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _inverted_l(frequency_hz: float) -> InvertedLParameters:
    wavelength = _wavelength(frequency_hz)
    return InvertedLParameters(
        frequency_hz=frequency_hz,
        vertical_height_m=0.25 * wavelength,
        horizontal_length_m=0.25 * wavelength,
        base_height_m=0.001,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _scv(frequency_hz: float) -> object:
    return scv_parameters(
        ScvKind.HALF_SQUARE,
        frequency_hz,
        base_height_m=0.001,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _beverage(frequency_hz: float) -> object:
    wavelength = _wavelength(frequency_hz)
    return beverage_parameters(
        frequency_hz=frequency_hz,
        length_m=wavelength,
        height_m=max(0.001, 0.01 * wavelength),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _loaded_dipole(frequency_hz: float) -> object:
    wavelength = _wavelength(frequency_hz)
    return loaded_dipole_parameters(
        frequency_hz=frequency_hz,
        total_length_m=0.5 * wavelength,
        height_m=max(1.0, 0.25 * wavelength),
        link_offset_m=0.125 * wavelength,
        loading_coil_enabled=False,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _phased_vertical(frequency_hz: float) -> object:
    return phased_vertical_parameters(
        frequency_hz=frequency_hz,
        element_count=2,
        base_height_m=0.001,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _endfed(frequency_hz: float) -> EndFedParameters:
    wavelength = _wavelength(frequency_hz)
    return EndFedParameters(
        frequency_hz=frequency_hz,
        length_m=0.5 * wavelength,
        feed_height_m=max(1.0, 0.25 * wavelength),
        end_height_m=max(1.0, 0.25 * wavelength),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _fan_dipole(frequency_hz: float) -> FanDipoleParameters:
    wavelength = _wavelength(frequency_hz)
    return FanDipoleParameters(
        frequency_hz=frequency_hz,
        elements=(
            FanElement(length_m=0.5 * wavelength, included_angle_deg=90.0),
            FanElement(length_m=0.48 * wavelength, included_angle_deg=100.0),
        ),
        apex_height_m=0.4 * wavelength,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _trap_dipole(frequency_hz: float) -> TrapDipoleParameters:
    wavelength = _wavelength(frequency_hz)
    return TrapDipoleParameters(
        frequency_hz=frequency_hz,
        high_band_frequency_hz=2.0 * frequency_hz,
        inner_length_m=0.25 * wavelength,
        outer_length_m=0.1 * wavelength,
        trap_frequency_hz=2.0 * frequency_hz,
        trap_inductance_h=5e-6,
        height_m=max(1.0, 0.25 * wavelength),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _trap_yagi(frequency_hz: float) -> object:
    wavelength = _wavelength(frequency_hz)
    return trap_yagi_parameters(
        frequency_hz=frequency_hz,
        high_band_frequency_hz=2.0 * frequency_hz,
        element_count=2,
        driven_length_m=0.5 * wavelength,
        reflector_spacing_m=0.2 * wavelength,
        height_m=max(1.0, 0.25 * wavelength),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _t2fd(frequency_hz: float) -> T2FDParameters:
    wavelength = _wavelength(frequency_hz)
    return T2FDParameters(
        frequency_hz=frequency_hz,
        highest_frequency_hz=2.0 * frequency_hz,
        length_m=0.5 * wavelength,
        spacing_m=max(4.0 * _WIRE_RADIUS_M, 0.01 * wavelength),
        height_m=max(1.0, 0.25 * wavelength),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _doublet(frequency_hz: float) -> TransmissionLineDoubletParameters:
    wavelength = _wavelength(frequency_hz)
    return TransmissionLineDoubletParameters(
        frequency_hz=frequency_hz,
        preset=DoubletPreset.G5RV,
        dipole_total_length_m=0.5 * wavelength,
        height_m=max(1.0, 0.25 * wavelength),
        feed_height_m=0.001,
        line_impedance_ohm=450.0,
        line_length_m=0.5 * wavelength,
        line_velocity_factor=0.9,
        wire_radius_m=_WIRE_RADIUS_M,
    )


def _zepp(frequency_hz: float) -> object:
    wavelength = _wavelength(frequency_hz)
    return zepp_starting_parameters(
        frequency_hz=frequency_hz,
        base_height_m=0.001,
        spacing_m=max(4.0 * _WIRE_RADIUS_M, 0.01 * wavelength),
        wire_radius_m=_WIRE_RADIUS_M,
    )


def test_around_keeps_a_small_design_relative_to_its_current_value() -> None:
    from antennadesk.domain.optimization.families.common import around

    low, high = around(0.02, 0.2, minimum=1e-6)

    assert low == pytest.approx(0.016)
    assert high == pytest.approx(0.024)
    assert high - low > 0.001


def test_conductor_floor_and_step_are_scale_aware() -> None:
    from antennadesk.domain.optimization.families.common import (
        conductor_floor_m,
        relative_step,
    )

    assert conductor_floor_m(0.0005) == pytest.approx(0.001)
    assert conductor_floor_m(0.0000001) == pytest.approx(1e-6)
    assert relative_step(0.01, 0.02) == pytest.approx(0.0001)


_BUILDERS: tuple[tuple[str, Callable[[float], object]], ...] = (
    ("dipole", _dipole),
    ("folded_dipole", _folded_dipole),
    ("inverted_v", _inverted_v),
    ("vertical", _vertical),
    ("j_pole", _j_pole),
    ("ringo", _ringo),
    ("quad", _quad),
    ("discone", _discone),
    ("hexbeam", _hexbeam),
    ("biquad", _biquad),
    ("moxon", _moxon),
    ("yagi", _yagi),
    ("loop", _loop),
    ("inverted_l", _inverted_l),
    ("scv", _scv),
    ("beverage", _beverage),
    ("loaded_dipole", _loaded_dipole),
    ("phased_vertical", _phased_vertical),
    ("endfed", _endfed),
    ("fan_dipole", _fan_dipole),
    ("trap_dipole", _trap_dipole),
    ("trap_yagi", _trap_yagi),
    ("t2fd", _t2fd),
    ("doublet", _doublet),
    ("zepp", _zepp),
)


@pytest.mark.parametrize("frequency_hz", _FREQUENCIES_HZ, ids=lambda value: f"{value:g}")
@pytest.mark.parametrize(("name", "builder"), _BUILDERS, ids=[item[0] for item in _BUILDERS])
def test_priority_families_keep_sane_relative_bounds(
    name: str,
    builder: Callable[[float], object],
    frequency_hz: float,
) -> None:
    parameters = builder(frequency_hz)

    availability = optimizer_availability(parameters)  # type: ignore[arg-type]

    assert availability.available is True, (
        name,
        frequency_hz,
        availability.reason_key,
        availability.reason_values,
    )
    assert availability.descriptor is not None
    for variable in availability.descriptor.variables:
        value = availability.descriptor.initial_values[variable.name]
        assert variable.minimum <= value <= variable.maximum, (name, variable.name, value)
        span = variable.maximum - variable.minimum
        assert span > 0.0, (name, variable.name)
        assert variable.step <= span, (name, variable.name, variable.step, span)
