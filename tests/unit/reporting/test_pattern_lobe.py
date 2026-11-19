# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Static 3D far-field report figure."""

from __future__ import annotations

import math

from antennadesk.domain.simulation.result import FarFieldPoint, FrequencyResult
from antennadesk.reporting.localization import identity_labeler
from antennadesk.reporting.pattern_lobe import MAX_SEGMENTS, pattern_lobe


def _point(theta_deg: float, phi_deg: float, gain: float | None) -> FarFieldPoint:
    return FarFieldPoint(
        theta_deg,
        phi_deg,
        gain,
        None,
        gain,
        0.0,
        0.0,
        None,
        None,
        None,
        None,
        None,
    )


def _frequency(
    *,
    theta_step: int = 10,
    phi_step: int = 10,
    theta_stop: int = 180,
    phi_stop: int = 350,
    missing: set[tuple[int, int]] | None = None,
) -> FrequencyResult:
    missing = missing or set()
    points = tuple(
        _point(
            theta,
            phi,
            None
            if (theta, phi) in missing
            else 5.0 * math.sin(math.radians(theta)) * math.cos(math.radians(phi)),
        )
        for theta in range(0, theta_stop + 1, theta_step)
        for phi in range(0, phi_stop + 1, phi_step)
    )
    return FrequencyResult(
        145_000_000.0,
        1,
        1,
        complex(50.0, 0.0),
        1.0,
        1.0,
        far_field=points,
    )


def test_pattern_lobe_renders_wireframe_legend_and_max_marker() -> None:
    frequency = _frequency()
    stored = frequency.far_field

    lobe = pattern_lobe(frequency, identity_labeler, ground=False)

    assert lobe.svg is not None
    assert '<svg xmlns="http://www.w3.org/2000/svg"' in lobe.svg
    assert 'role="img"' in lobe.svg
    assert "<title" in lobe.svg
    assert "<desc" in lobe.svg
    assert "pattern-lobe" in lobe.svg
    assert lobe.svg.count("<path ") <= 12
    assert "<circle" in lobe.svg
    assert "dBi" in lobe.svg
    assert "3D far-field pattern" in lobe.svg
    assert "stored sampling 19x36" in lobe.svg
    assert "Ground" not in lobe.svg
    assert lobe.displayed_theta_count <= 19
    assert lobe.displayed_phi_count <= 37
    assert lobe.segment_count <= MAX_SEGMENTS
    assert frequency.far_field == stored


def test_pattern_lobe_is_byte_deterministic() -> None:
    frequency = _frequency()

    first = pattern_lobe(frequency, identity_labeler, ground=False)
    second = pattern_lobe(frequency, identity_labeler, ground=False)

    assert first == second


def test_pattern_lobe_ground_ring_filters_the_lower_hemisphere() -> None:
    frequency = _frequency()

    free_space = pattern_lobe(frequency, identity_labeler, ground=False)
    grounded = pattern_lobe(frequency, identity_labeler, ground=True)

    assert free_space.svg is not None
    assert grounded.svg is not None
    assert "Ground" not in free_space.svg
    assert "Ground" in grounded.svg
    assert grounded.displayed_theta_count <= 10
    assert "stored sampling 10x36" in grounded.svg


def test_pattern_lobe_rejects_a_single_cut() -> None:
    frequency = _frequency(phi_stop=0)

    lobe = pattern_lobe(frequency, identity_labeler, ground=False)

    assert lobe.svg is None
    assert lobe.unavailable_reason is not None
    assert "does not contain a 2D angular grid" in lobe.unavailable_reason


def test_pattern_lobe_rejects_all_missing_gains() -> None:
    frequency = _frequency(
        missing={(theta, phi) for theta in (0, 10) for phi in (0, 10, 20, 30)},
        theta_stop=10,
        phi_stop=30,
    )

    lobe = pattern_lobe(frequency, identity_labeler, ground=False)

    assert lobe.svg is None
    assert lobe.unavailable_reason is not None


def test_pattern_lobe_skips_non_finite_gains_without_nan_coordinates() -> None:
    frequency = _frequency(
        theta_stop=20,
        phi_stop=20,
        missing={(0, 0)},
    )
    points = tuple(
        point if point.theta_deg != 10 or point.phi_deg != 10 else _point(10.0, 10.0, math.nan)
        for point in frequency.far_field
    )
    frequency = FrequencyResult(
        frequency.frequency_hz,
        frequency.feed_tag,
        frequency.feed_segment,
        frequency.impedance_ohm,
        frequency.swr,
        frequency.input_power_w,
        far_field=points,
    )

    lobe = pattern_lobe(frequency, identity_labeler, ground=False)

    assert lobe.svg is not None
    assert "nan" not in lobe.svg.lower()
    assert "None" not in lobe.svg


def test_pattern_lobe_caps_the_displayed_mesh() -> None:
    frequency = _frequency(theta_step=5, phi_step=5, theta_stop=180, phi_stop=360)

    lobe = pattern_lobe(frequency, identity_labeler, ground=False)

    assert lobe.svg is not None
    assert lobe.displayed_theta_count == 19
    assert lobe.displayed_phi_count == 37
    assert lobe.segment_count <= MAX_SEGMENTS
    assert "stored sampling 37x72" in lobe.svg
