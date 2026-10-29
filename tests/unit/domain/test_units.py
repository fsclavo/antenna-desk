from __future__ import annotations

import math

import pytest

from antennadesk.domain.common import units


def test_length_conversions() -> None:
    assert units.m_from_mm(1_000.0) == pytest.approx(1.0)
    assert units.m_from_cm(100.0) == pytest.approx(1.0)
    assert units.m_from_in(1.0) == pytest.approx(0.0254)
    assert units.m_from_ft(1.0) == pytest.approx(0.3048)
    assert units.mm_from_m(1.0) == pytest.approx(1_000.0)
    assert units.cm_from_m(1.0) == pytest.approx(100.0)
    assert units.in_from_m(0.0254) == pytest.approx(1.0)
    assert units.ft_from_m(0.3048) == pytest.approx(1.0)


def test_frequency_conversions() -> None:
    assert units.hz_from_khz(7.1) == pytest.approx(7_100.0)
    assert units.hz_from_mhz(7.1) == pytest.approx(7_100_000.0)
    assert units.hz_from_ghz(7.1) == pytest.approx(7_100_000_000.0)
    assert units.khz_from_hz(7_100.0) == pytest.approx(7.1)
    assert units.mhz_from_hz(7_100_000.0) == pytest.approx(7.1)
    assert units.ghz_from_hz(7_100_000_000.0) == pytest.approx(7.1)


def test_wavelength_at_seven_point_one_mhz() -> None:
    expected = 299_792_458.0 / 7_100_000.0
    assert units.wavelength_m(7_100_000.0) == pytest.approx(expected)


def test_wavelength_with_velocity_factor() -> None:
    expected = 299_792_458.0 * 0.66 / 7_100_000.0
    assert units.wavelength_m(7_100_000.0, velocity_factor=0.66) == pytest.approx(expected)


def test_azimuth_normalization() -> None:
    assert units.normalize_azimuth_degrees(0.0) == 0.0
    assert units.normalize_azimuth_degrees(359.0) == 359.0
    assert units.normalize_azimuth_degrees(360.0) == 0.0
    assert units.normalize_azimuth_degrees(370.0) == 10.0
    assert units.normalize_azimuth_degrees(-10.0) == 350.0


def test_angle_conversions() -> None:
    assert units.degrees_to_radians(180.0) == pytest.approx(math.pi)
    assert units.radians_to_degrees(math.pi) == pytest.approx(180.0)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_values_are_rejected(value: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        units.ensure_finite(value, name="value")


def test_positive_values_are_enforced() -> None:
    with pytest.raises(ValueError, match="positive"):
        units.ensure_positive(0.0, name="value")
    with pytest.raises(ValueError, match="positive"):
        units.ensure_positive(-1.0, name="value")


def test_non_negative_values_are_enforced() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        units.ensure_non_negative(-1.0, name="value")


def test_wavelength_rejects_zero_frequency() -> None:
    with pytest.raises(ValueError, match="positive"):
        units.wavelength_m(0.0)
