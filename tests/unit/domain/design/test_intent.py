# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation boundaries for the frequency-first design intent."""

from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.dipole import DipoleOrientation
from antennadesk.domain.antennas.polarization import Polarization
from antennadesk.domain.design import DesignIntent, LoopShape, VerticalForm

FREQUENCY_HZ = 7_100_000.0


def _intent(**overrides: object) -> DesignIntent:
    values: dict[str, object] = {
        "frequency_hz": FREQUENCY_HZ,
        "antenna_type": "wire_dipole",
    }
    values.update(overrides)
    return DesignIntent(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "overrides",
    [
        {"frequency_hz": 0.0},
        {"frequency_hz": -1.0},
        {"height_m": -1.0},
        {"base_height_m": -1.0},
        {"wire_radius_m": 0.0},
        {"antenna_type": ""},
        {"antenna_type": "   "},
        {"orientation": "sideways"},
        {"polarization": "diagonal"},
        {"loop_shape": "hexagon"},
        {"vertical_form": "eighth_wave"},
        {"included_angle_deg": 0.0},
        {"included_angle_deg": 180.0},
        {"included_angle_deg": -1.0},
        {"included_angle_deg": 181.0},
        {"radial_count": -1},
        {"radial_count": 129},
        {"radial_length_m": 0.0},
        {"feed_offset_m": -1.0},
        {"gap_m": 0.0},
        {"gap_m": -1.0},
        {"fan_bands_hz": (0.0,)},
        {"fan_bands_hz": (-1.0,)},
        {"yagi_elements": 1},
        {"end_height_m": -1.0},
        {"highest_frequency_hz": 0.0},
        {"highest_frequency_hz": FREQUENCY_HZ},
        {"highest_frequency_hz": FREQUENCY_HZ - 1.0},
        {"azimuth_deg": math.nan},
        {"azimuth_deg": math.inf},
    ],
)
def test_rejects_invalid_intent_fields(overrides: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _intent(**overrides)


def test_accepts_the_valid_boundaries() -> None:
    low = _intent(radial_count=0, yagi_elements=2, included_angle_deg=0.5)
    high = _intent(
        radial_count=128,
        included_angle_deg=179.999,
        highest_frequency_hz=FREQUENCY_HZ + 1.0,
    )

    assert low.radial_count == 0
    assert low.included_angle_deg == 0.5
    assert high.radial_count == 128
    assert high.yagi_elements == 5


def test_normalizes_string_enums_and_fan_bands() -> None:
    intent = _intent(
        orientation="vertical",
        polarization="vertical",
        loop_shape="delta",
        vertical_form="half_wave",
        fan_bands_hz=[7_100_000.0, 14_100_000.0],
    )

    assert intent.orientation is DipoleOrientation.VERTICAL
    assert intent.polarization is Polarization.VERTICAL
    assert intent.loop_shape is LoopShape.DELTA
    assert intent.loop_shape.sides == 3
    assert intent.vertical_form is VerticalForm.HALF_WAVE
    assert intent.fan_bands_hz == (7_100_000.0, 14_100_000.0)
