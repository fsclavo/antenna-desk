# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Property-based checks for the unit conversions used across the domain."""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from antennadesk.domain.common import units

POSITIVE = st.floats(
    min_value=1e-6,
    max_value=1e9,
    allow_nan=False,
    allow_infinity=False,
)
FINITE = st.floats(
    min_value=-1e9,
    max_value=1e9,
    allow_nan=False,
    allow_infinity=False,
)


@settings(max_examples=200, deadline=None)
@given(POSITIVE)
def test_length_unit_round_trips(value: float) -> None:
    pairs = (
        (units.m_from_mm, units.mm_from_m),
        (units.m_from_cm, units.cm_from_m),
        (units.m_from_in, units.in_from_m),
        (units.m_from_ft, units.ft_from_m),
    )
    for to_meters, from_meters in pairs:
        assert from_meters(to_meters(value)) == pytest.approx(value, rel=1e-12)


@settings(max_examples=200, deadline=None)
@given(POSITIVE)
def test_frequency_unit_round_trips(value: float) -> None:
    pairs = (
        (units.hz_from_khz, units.khz_from_hz),
        (units.hz_from_mhz, units.mhz_from_hz),
        (units.hz_from_ghz, units.ghz_from_hz),
    )
    for to_hz, from_hz in pairs:
        assert from_hz(to_hz(value)) == pytest.approx(value, rel=1e-12)


@settings(max_examples=100, deadline=None)
@given(POSITIVE)
def test_wavelength_is_positive_and_finite(frequency_hz: float) -> None:
    wavelength = units.wavelength_m(frequency_hz)
    assert math.isfinite(wavelength)
    assert wavelength > 0.0


@settings(max_examples=100, deadline=None)
@given(
    POSITIVE,
    st.floats(min_value=0.1, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_wavelength_scales_with_velocity_factor(
    frequency_hz: float,
    velocity_factor: float,
) -> None:
    scaled = units.wavelength_m(frequency_hz, velocity_factor=velocity_factor)
    assert scaled == pytest.approx(units.wavelength_m(frequency_hz) * velocity_factor, rel=1e-12)


@settings(max_examples=200, deadline=None)
@given(FINITE)
def test_azimuth_normalization_stays_in_range(value: float) -> None:
    normalized = units.normalize_azimuth_degrees(value)
    assert 0.0 <= normalized < 360.0


@settings(max_examples=100, deadline=None)
@given(st.floats(max_value=0.0, allow_nan=False, allow_infinity=False))
def test_ensure_positive_rejects_non_positive_values(value: float) -> None:
    with pytest.raises(ValueError):
        units.ensure_positive(value, name="value")


@settings(max_examples=100, deadline=None)
@given(
    st.sampled_from([float("nan"), float("inf"), float("-inf")]),
)
def test_ensure_finite_rejects_non_finite_values(value: float) -> None:
    with pytest.raises(ValueError):
        units.ensure_finite(value, name="value")
