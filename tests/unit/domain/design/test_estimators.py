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
    half_wave_length_m,
    loop_circumference_m,
    quarter_wave_length_m,
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


def test_j_pole_uses_total_three_quarter_wave_height() -> None:
    estimate = estimate_intent(_intent("j_pole", frequency_hz=146_000_000.0, folded=False))
    parameters = estimate.parameters

    assert isinstance(parameters, JPoleParameters)
    assert parameters.folded is False
    assert parameters.radiator_height_m == pytest.approx(
        half_wave_length_m(146_000_000.0) + quarter_wave_length_m(146_000_000.0)
    )
    assert parameters.feed_offset_m == pytest.approx(parameters.stub_length_m * 0.4)


def test_yagi_supports_two_through_thirty_two_elements() -> None:
    for count in range(2, 33):
        estimate = estimate_intent(_intent("yagi", frequency_hz=144_000_000.0, yagi_elements=count))
        parameters = estimate.parameters

        assert isinstance(parameters, YagiParameters)
        assert len(parameters.elements) == count
        assert parameters.driven_index == 1
        assert [element.position_m for element in parameters.elements] == sorted(
            element.position_m for element in parameters.elements
        )
        assert estimate.method_id == "yagi.dl6wu_trimming_2_32"
        assert estimate.confidence is Confidence.REFERENCE_SCALED
        assert estimate.source_ids == ("cebik.dl6wu.32_element_rsgb",)

    with pytest.raises(ValueError):
        _intent("yagi", yagi_elements=1)
    with pytest.raises(UnsupportedEstimateError):
        estimate_intent(_intent("yagi", yagi_elements=33))


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


@pytest.mark.parametrize(
    ("antenna_type", "frequency_hz", "kwargs"),
    [
        ("wire_dipole", 7_100_000.0, {}),
        ("folded_dipole", 7_100_000.0, {}),
        ("loop", 7_100_000.0, {"loop_shape": LoopShape.QUAD}),
        ("vertical", 146_000_000.0, {"radial_count": 8}),
        ("inverted_v", 7_100_000.0, {"height_m": 20.0}),
        ("fan_dipole", 7_100_000.0, {"height_m": 20.0}),
        ("endfed", 7_100_000.0, {}),
        ("ocfd", 7_100_000.0, {}),
        ("j_pole", 146_000_000.0, {"folded": False}),
        ("j_pole", 146_000_000.0, {"folded": True}),
        ("ringo", 146_000_000.0, {}),
        ("yagi", 146_000_000.0, {"yagi_elements": 5}),
        ("moxon", 14_170_000.0, {}),
    ],
)
def test_every_supported_estimator_produces_a_valid_antenna(
    antenna_type: str,
    frequency_hz: float,
    kwargs: dict[str, object],
) -> None:
    estimate = estimate_intent(_intent(antenna_type, frequency_hz, **kwargs))
    model = estimate.parameters.to_antenna()

    assert model.wires
    assert all(wire.length_m > 0.0 for wire in model.wires)
    assert estimate.rows
    assert estimate.tolerance_m > 0.0
    assert estimate.source_ids
    assert estimate.confidence in {
        Confidence.PHYSICAL,
        Confidence.EMPIRICAL,
        Confidence.REFERENCE_SCALED,
        Confidence.HEURISTIC,
    }


def test_folded_and_endfed_estimates_are_dimensionally_complete() -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    folded = estimate_intent(_intent("folded_dipole")).parameters
    endfed = estimate_intent(_intent("endfed", end_height_m=12.0)).parameters

    assert isinstance(folded, FoldedDipoleParameters)
    assert folded.spacing_m > 0.0
    assert isinstance(endfed, EndFedParameters)
    assert endfed.length_m > 0.0
    assert endfed.feed_height_m == pytest.approx(10.0)
    assert endfed.end_height_m == pytest.approx(12.0)


def test_ocfd_and_ringo_estimates_have_valid_special_geometry() -> None:
    from antennadesk.domain.antennas.ocfd import OCFDParameters
    from antennadesk.domain.antennas.ringo import RingoParameters

    ocfd = estimate_intent(_intent("ocfd")).parameters
    ringo = estimate_intent(_intent("ringo", frequency_hz=146_000_000.0)).parameters

    assert isinstance(ocfd, OCFDParameters)
    assert 0.0 < ocfd.feed_ratio < 1.0
    assert isinstance(ringo, RingoParameters)
    assert ringo.radiator_height_m > 0.0
    assert ringo.ring_diameter_m > 0.0
    assert ringo.ring_height_m > 0.0


def test_ringo_estimate_is_calibrated_for_the_simplified_geometry() -> None:
    frequency = 146_000_000.0
    parameters = estimate_intent(_intent("ringo", frequency_hz=frequency)).parameters
    wavelength = wavelength_m(frequency)

    assert parameters.radiator_height_m == pytest.approx(0.725 * wavelength, abs=0.01)
    assert parameters.ring_diameter_m == pytest.approx(0.14 * wavelength, abs=0.01)
    assert parameters.ring_height_m == pytest.approx(0.01 * wavelength, abs=0.005)
