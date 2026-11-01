# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.custom import ANTENNA_TYPE_CUSTOM
from antennadesk.domain.antennas.dipole import DipoleOrientation
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.moxon import MoxonParameters, moxon_20m_wire
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiParameters
from antennadesk.domain.design import (
    Confidence,
    DesignIntent,
    LoopShape,
    UnsupportedEstimateError,
    VerticalForm,
    estimate_intent,
)
from antennadesk.domain.design.estimators import SUPPORTED_ESTIMATOR_TYPES
from antennadesk.domain.design.formulas import (
    HALF_WAVE_FACTOR,
    loop_circumference_m,
    wavelength_m,
)


def _intent(antenna_type: str, frequency_hz: float = 7_100_000.0, **kwargs: object):
    return DesignIntent(frequency_hz=frequency_hz, antenna_type=antenna_type, **kwargs)


def test_dipole_estimate_uses_half_wave_and_orientation() -> None:
    estimate = estimate_intent(
        _intent(
            "wire_dipole",
            height_m=12.0,
            orientation=DipoleOrientation.VERTICAL,
        )
    )

    from antennadesk.domain.antennas.dipole import DipoleParameters

    assert isinstance(estimate.parameters, DipoleParameters)
    assert estimate.parameters.total_length_m == pytest.approx(
        wavelength_m(7_100_000.0) * HALF_WAVE_FACTOR
    )
    assert estimate.parameters.orientation is DipoleOrientation.VERTICAL
    assert estimate.confidence is Confidence.EMPIRICAL
    assert estimate.source_ids


def test_loop_estimate_uses_shape_side_count() -> None:
    delta = estimate_intent(_intent("loop", loop_shape=LoopShape.DELTA))
    quad = estimate_intent(_intent("loop", loop_shape=LoopShape.QUAD))

    assert isinstance(delta.parameters, LoopParameters)
    assert isinstance(quad.parameters, LoopParameters)
    assert delta.parameters.sides == 3
    assert quad.parameters.sides == 4
    assert delta.parameters.circumference_m == pytest.approx(loop_circumference_m(7_100_000.0))


def test_vertical_estimate_supports_quarter_and_five_eighth() -> None:
    quarter = estimate_intent(
        _intent(
            "vertical",
            frequency_hz=146_000_000.0,
            vertical_form=VerticalForm.QUARTER_WAVE,
            radial_count=8,
        )
    )
    five_eighth = estimate_intent(
        _intent(
            "vertical",
            frequency_hz=146_000_000.0,
            vertical_form=VerticalForm.FIVE_EIGHTH_WAVE,
            radial_count=8,
        )
    )

    assert isinstance(quarter.parameters, VerticalParameters)
    assert isinstance(five_eighth.parameters, VerticalParameters)
    assert five_eighth.parameters.height_m > quarter.parameters.height_m
    assert quarter.parameters.radial_count == 8
    assert quarter.parameters.radial_length_m > 0.0
    assert any("vertical_matching" in warning for warning in five_eighth.warnings)


def test_inverted_v_and_fan_estimates_keep_angle_and_bands() -> None:
    inverted = estimate_intent(_intent("inverted_v", included_angle_deg=90.0, height_m=12.0))
    fan = estimate_intent(
        _intent(
            "fan_dipole",
            fan_bands_hz=(7_100_000.0, 14_100_000.0),
            included_angle_deg=110.0,
        )
    )

    assert inverted.parameters.leg_length_m > 0.0
    assert inverted.parameters.included_angle_deg == pytest.approx(90.0)
    assert isinstance(fan.parameters, FanDipoleParameters)
    assert len(fan.parameters.elements) == 2
    assert all(
        element.included_angle_deg == pytest.approx(110.0) for element in fan.parameters.elements
    )


def test_j_pole_feed_offset_stays_inside_the_stub() -> None:
    estimate = estimate_intent(_intent("j_pole", frequency_hz=146_000_000.0, folded=True))
    parameters = estimate.parameters

    assert isinstance(parameters, JPoleParameters)
    assert 0.0 < parameters.feed_offset_m < parameters.stub_length_m
    assert parameters.folded is True


def test_yagi_uses_the_reference_preset_and_rejects_other_counts() -> None:
    estimate = estimate_intent(_intent("yagi", frequency_hz=144_000_000.0, yagi_elements=5))
    assert isinstance(estimate.parameters, YagiParameters)
    assert len(estimate.parameters.elements) == 5
    assert estimate.confidence is Confidence.REFERENCE_SCALED

    with pytest.raises(UnsupportedEstimateError):
        estimate_intent(_intent("yagi", yagi_elements=3))


def test_moxon_scales_the_published_reference() -> None:
    reference = moxon_20m_wire(height_m=10.0)
    estimate = estimate_intent(_intent("moxon", frequency_hz=14_170_000.0, height_m=10.0))
    parameters = estimate.parameters

    assert isinstance(parameters, MoxonParameters)
    assert parameters.width_m == pytest.approx(reference.width_m)
    assert parameters.depth_m == pytest.approx(reference.depth_m)
    assert parameters.reflector_tip_m == pytest.approx(reference.reflector_tip_m)
    assert parameters.driven_tip_m == pytest.approx(reference.driven_tip_m)


def test_custom_geometry_is_explicitly_unsupported() -> None:
    with pytest.raises(UnsupportedEstimateError):
        estimate_intent(_intent(ANTENNA_TYPE_CUSTOM))


def test_registry_covers_every_current_domain_antenna_type() -> None:
    from antennadesk.domain.antennas import (
        dipole,
        endfed,
        fan_dipole,
        folded_dipole,
        inverted_v,
        j_pole,
        loop,
        moxon,
        ocfd,
        ringo,
        vertical,
        yagi,
    )

    modules = (
        dipole,
        endfed,
        fan_dipole,
        folded_dipole,
        inverted_v,
        j_pole,
        loop,
        moxon,
        ocfd,
        ringo,
        vertical,
        yagi,
    )
    domain_types = {
        value
        for module in modules
        for name, value in vars(module).items()
        if name.startswith("ANTENNA_TYPE_") and isinstance(value, str)
    }

    assert domain_types <= SUPPORTED_ESTIMATOR_TYPES
    assert ANTENNA_TYPE_CUSTOM not in SUPPORTED_ESTIMATOR_TYPES
