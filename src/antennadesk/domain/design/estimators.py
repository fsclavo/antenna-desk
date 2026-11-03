# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency-first dimension estimators for the current antenna families."""

from __future__ import annotations

import math

from ..antennas.custom import ANTENNA_TYPE_CUSTOM
from ..antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleParameters
from ..antennas.endfed import ANTENNA_TYPE_ENDFED, EndFedParameters
from ..antennas.fan_dipole import (
    ANTENNA_TYPE_FAN_DIPOLE,
    FanDipoleParameters,
    FanElement,
)
from ..antennas.folded_dipole import (
    ANTENNA_TYPE_FOLDED_DIPOLE,
    FoldedDipoleParameters,
)
from ..antennas.inverted_v import ANTENNA_TYPE_INVERTED_V, InvertedVParameters
from ..antennas.j_pole import ANTENNA_TYPE_J_POLE, JPoleParameters
from ..antennas.loop import ANTENNA_TYPE_LOOP, LoopParameters
from ..antennas.moxon import ANTENNA_TYPE_MOXON, MoxonParameters, moxon_20m_wire
from ..antennas.ocfd import ANTENNA_TYPE_OCFD, OCFDParameters
from ..antennas.ringo import ANTENNA_TYPE_RINGO, RingoParameters
from ..antennas.vertical import ANTENNA_TYPE_VERTICAL, VerticalParameters
from ..antennas.yagi import ANTENNA_TYPE_YAGI, YagiElement, YagiParameters
from .estimate import Confidence, DimensionEstimate, DimensionRow, DimensionUnit
from .formulas import (
    FOLDED_SPACING_FACTOR,
    MOXON_REFERENCE_FREQUENCY_HZ,
    RINGO_REFERENCE_FREQUENCY_HZ,
    SOURCE_APPLICATION_PRESET,
    SOURCE_ARRL_DIPOLE,
    SOURCE_ARRL_LOOP,
    SOURCE_ARRL_VERTICAL,
    SOURCE_CEBIK_MOXON,
    SOURCE_DL6WU_YAGI,
    default_radial_length_m,
    five_eighth_wave_length_m,
    half_wave_length_m,
    loop_circumference_m,
    quarter_wave_length_m,
    wavelength_m,
)
from .intent import DesignIntent, VerticalForm
from .yagi_reference import MAX_YAGI_ELEMENTS, MIN_YAGI_ELEMENTS, dl6wu_elements

# Application starting point for a half-wave end-fed installation. Both values
# are installation-specific and are documented in the estimator guide.
ENDFED_TRANSFORMER_RATIO = 49.0
ENDFED_COUNTERPOISE_FACTOR = 0.05


class UnsupportedEstimateError(ValueError):
    """The requested family or intent has no estimator."""


def _length_row(label_key: str, value_m: float) -> DimensionRow:
    return DimensionRow(label_key, value_m, DimensionUnit.LENGTH)


def _angle_row(label_key: str, value_deg: float) -> DimensionRow:
    return DimensionRow(label_key, value_deg, DimensionUnit.ANGLE)


def _count_row(label_key: str, value: int | float) -> DimensionRow:
    return DimensionRow(label_key, float(value), DimensionUnit.COUNT)


def estimate_dipole(intent: DesignIntent) -> DimensionEstimate:
    length = half_wave_length_m(intent.frequency_hz)
    parameters = DipoleParameters(
        frequency_hz=intent.frequency_hz,
        total_length_m=length,
        height_m=intent.height_m,
        orientation=intent.orientation,
        azimuth_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="dipole.half_wave_end_effect",
        confidence=Confidence.EMPIRICAL,
        tolerance_m=length * 0.03,
        source_ids=(SOURCE_ARRL_DIPOLE,),
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=("estimator.warning.starting_point",),
        rows=(
            _length_row("field.length", length),
            _length_row("field.height", intent.height_m),
        ),
    )


def estimate_folded_dipole(intent: DesignIntent) -> DimensionEstimate:
    length = half_wave_length_m(intent.frequency_hz)
    spacing = max(wavelength_m(intent.frequency_hz) * FOLDED_SPACING_FACTOR, 0.01)
    parameters = FoldedDipoleParameters(
        frequency_hz=intent.frequency_hz,
        total_length_m=length,
        height_m=intent.height_m,
        spacing_m=spacing,
        azimuth_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="folded_dipole.half_wave_end_effect",
        confidence=Confidence.EMPIRICAL,
        tolerance_m=length * 0.03,
        source_ids=(SOURCE_ARRL_DIPOLE,),
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=(
            "estimator.warning.starting_point",
            "estimator.warning.folded_impedance",
        ),
        rows=(
            _length_row("field.element_length", length),
            _length_row("field.spacing", spacing),
            _length_row("field.height", intent.height_m),
        ),
    )


def estimate_loop(intent: DesignIntent) -> DimensionEstimate:
    sides = intent.loop_shape.sides
    circumference = loop_circumference_m(intent.frequency_hz, sides)
    parameters = LoopParameters(
        frequency_hz=intent.frequency_hz,
        circumference_m=circumference,
        height_m=intent.height_m,
        sides=sides,
        azimuth_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="loop.resonant_circumference",
        confidence=Confidence.EMPIRICAL,
        tolerance_m=circumference * 0.04,
        source_ids=(SOURCE_ARRL_LOOP, SOURCE_APPLICATION_PRESET),
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=(
            "estimator.warning.starting_point",
            "estimator.warning.loop_matching",
        ),
        rows=(
            _length_row("field.circumference", circumference),
            _count_row("field.sides", sides),
            _length_row("field.height", intent.height_m),
        ),
    )


def estimate_vertical(intent: DesignIntent) -> DimensionEstimate:
    if intent.vertical_form is VerticalForm.HALF_WAVE:
        height = half_wave_length_m(intent.frequency_hz)
        method_id = "vertical.half_wave"
        confidence = Confidence.EMPIRICAL
        warnings: tuple[str, ...] = (
            "estimator.warning.starting_point",
            "estimator.warning.vertical_matching",
        )
    elif intent.vertical_form is VerticalForm.FIVE_EIGHTH_WAVE:
        height = five_eighth_wave_length_m(intent.frequency_hz)
        method_id = "vertical.five_eighth_wave"
        confidence = Confidence.PHYSICAL
        warnings = (
            "estimator.warning.starting_point",
            "estimator.warning.vertical_matching",
        )
    else:
        height = quarter_wave_length_m(intent.frequency_hz)
        method_id = "vertical.quarter_wave"
        confidence = Confidence.EMPIRICAL
        warnings = ("estimator.warning.starting_point",)
    radial_length = (
        intent.radial_length_m
        if intent.radial_length_m is not None
        else default_radial_length_m(intent.frequency_hz)
    )
    parameters = VerticalParameters(
        frequency_hz=intent.frequency_hz,
        height_m=height,
        base_height_m=intent.base_height_m,
        radial_count=intent.radial_count,
        radial_length_m=radial_length if intent.radial_count else 0.0,
        radial_angle_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    rows = [
        _length_row("field.height", height),
        _length_row("field.base_height", intent.base_height_m),
    ]
    if intent.radial_count:
        rows.append(_length_row("vertical.radial_length", radial_length))
        rows.append(_count_row("geometry.radials", intent.radial_count))
    return DimensionEstimate(
        parameters=parameters,
        method_id=method_id,
        confidence=confidence,
        tolerance_m=height * 0.03,
        source_ids=(SOURCE_ARRL_VERTICAL,),
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=warnings,
        rows=tuple(rows),
    )


def estimate_inverted_v(intent: DesignIntent) -> DimensionEstimate:
    total = half_wave_length_m(intent.frequency_hz)
    leg = total / 2.0
    apex_height = max(intent.height_m, 0.01)
    included_angle = intent.included_angle_deg
    warnings: tuple[str, ...] = ("estimator.warning.starting_point",)
    required_cosine = min(max(apex_height / leg, 0.0), 1.0)
    if required_cosine < math.cos(math.radians(included_angle / 2.0)):
        included_angle = min(
            179.0,
            2.0 * math.degrees(math.acos(required_cosine)),
        )
        required_apex = leg * math.cos(math.radians(included_angle / 2.0))
        if apex_height < required_apex:
            apex_height = required_apex + 0.01
        warnings = (*warnings, "estimator.warning.inverted_v_angle_increased")
    parameters = InvertedVParameters(
        frequency_hz=intent.frequency_hz,
        leg_length_m=leg,
        apex_height_m=apex_height,
        included_angle_deg=included_angle,
        azimuth_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="inverted_v.dipole_total_length",
        confidence=Confidence.EMPIRICAL,
        tolerance_m=total * 0.04,
        source_ids=(SOURCE_ARRL_DIPOLE,),
        assumptions=(
            "estimator.assumption.height_and_ground",
            "estimator.assumption.inverted_v_angle",
        ),
        warnings=warnings,
        rows=(
            _length_row("geometry.leg_length", leg),
            _length_row("field.height", apex_height),
            _angle_row("inverted_v.included_angle", included_angle),
        ),
    )


def estimate_fan_dipole(intent: DesignIntent) -> DimensionEstimate:
    bands = tuple(sorted(set(intent.fan_bands_hz or (intent.frequency_hz,))))
    apex_height = max(intent.height_m, 0.01)
    warnings: tuple[str, ...] = ("estimator.warning.starting_point",)
    elements: list[FanElement] = []
    previous_angle = 180.0
    for index, band in enumerate(bands):
        length = half_wave_length_m(band)
        half_length = length / 2.0
        requested_angle = max(20.0, intent.included_angle_deg - 20.0 * index)
        required_cosine = min(max(apex_height / half_length, 0.0), 1.0)
        minimum_angle = 2.0 * math.degrees(math.acos(required_cosine))
        target_angle = min(requested_angle, previous_angle - 5.0)
        if minimum_angle > target_angle:
            required_apex = half_length * math.cos(math.radians(target_angle / 2.0))
            apex_height = max(apex_height, required_apex + 0.01)
            required_cosine = min(max(apex_height / half_length, 0.0), 1.0)
            minimum_angle = 2.0 * math.degrees(math.acos(required_cosine))
            warnings = (*warnings, "estimator.warning.fan_angle_increased")
        included_angle = max(minimum_angle, target_angle)
        previous_angle = included_angle
        elements.append(
            FanElement(
                length_m=length,
                included_angle_deg=included_angle,
            )
        )
    parameters = FanDipoleParameters(
        frequency_hz=intent.frequency_hz,
        elements=tuple(elements),
        apex_height_m=apex_height,
        azimuth_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    warnings = (*warnings, "estimator.warning.fan_interaction")
    rows = tuple(_length_row("field.element_length", element.length_m) for element in elements)
    return DimensionEstimate(
        parameters=parameters,
        method_id="fan_dipole.per_band_half_wave",
        confidence=Confidence.EMPIRICAL,
        tolerance_m=half_wave_length_m(intent.frequency_hz) * 0.04,
        source_ids=(SOURCE_ARRL_DIPOLE,),
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=warnings,
        rows=(*rows, _length_row("field.height", apex_height)),
    )


def estimate_endfed(intent: DesignIntent) -> DimensionEstimate:
    length = half_wave_length_m(intent.frequency_hz)
    end_height = intent.end_height_m if intent.end_height_m is not None else intent.height_m
    warnings: tuple[str, ...] = (
        "estimator.warning.starting_point",
        "estimator.warning.endfed_matching",
    )
    if end_height < intent.height_m:
        clamped = max(0.0, intent.height_m - length)
        if end_height < clamped:
            end_height = clamped
            warnings = (*warnings, "estimator.warning.endfed_end_height_clamped")
    elif end_height - intent.height_m > length:
        end_height = intent.height_m + length
        warnings = (*warnings, "estimator.warning.endfed_end_height_clamped")
    counterpoise_length = wavelength_m(intent.frequency_hz) * ENDFED_COUNTERPOISE_FACTOR
    parameters = EndFedParameters(
        frequency_hz=intent.frequency_hz,
        length_m=length,
        feed_height_m=intent.height_m,
        end_height_m=end_height,
        azimuth_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
        transformer_ratio=ENDFED_TRANSFORMER_RATIO,
        counterpoise_length_m=counterpoise_length,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="endfed.half_wave",
        confidence=Confidence.HEURISTIC,
        tolerance_m=length * 0.05,
        source_ids=(SOURCE_ARRL_DIPOLE, SOURCE_APPLICATION_PRESET),
        assumptions=("estimator.assumption.endfed_matching",),
        warnings=warnings,
        rows=(
            _length_row("field.length", length),
            _length_row("geometry.feed_height", intent.height_m),
            _length_row("geometry.end_height", end_height),
            _count_row("endfed.transformer_ratio", ENDFED_TRANSFORMER_RATIO),
            _length_row("endfed.counterpoise_length", counterpoise_length),
        ),
    )


def estimate_ocfd(intent: DesignIntent) -> DimensionEstimate:
    length = half_wave_length_m(intent.frequency_hz)
    parameters = OCFDParameters(
        frequency_hz=intent.frequency_hz,
        total_length_m=length,
        feed_ratio=1.0 / 3.0,
        height_m=intent.height_m,
        azimuth_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="ocfd.half_wave_one_third_feed",
        confidence=Confidence.HEURISTIC,
        tolerance_m=length * 0.05,
        source_ids=(SOURCE_ARRL_DIPOLE,),
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=(
            "estimator.warning.starting_point",
            "estimator.warning.ocfd_matching",
        ),
        rows=(
            _length_row("field.length", length),
            _length_row("geometry.feed_offset", parameters.feed_offset_m),
            _length_row("field.height", intent.height_m),
        ),
    )


def estimate_j_pole(intent: DesignIntent) -> DimensionEstimate:
    stub = quarter_wave_length_m(intent.frequency_hz)
    # A J pole is a half-wave radiator above a quarter-wave matching stub.
    # In the non-folded geometry both start at the base, so the vertical
    # radiator height is the total 3/4-wave height; the Slim Jim uses the
    # half-wave radiator portion above its folded matching section.
    radiator = (
        half_wave_length_m(intent.frequency_hz) + stub
        if not intent.folded
        else half_wave_length_m(intent.frequency_hz)
    )
    spacing = max(wavelength_m(intent.frequency_hz) * 0.02, 0.01)
    default_feed = stub * (0.4 if not intent.folded else 0.2)
    feed_offset = intent.feed_offset_m if intent.feed_offset_m is not None else default_feed
    feed_offset = min(max(feed_offset, 1e-3), stub * 0.95)
    parameters = JPoleParameters(
        frequency_hz=intent.frequency_hz,
        radiator_height_m=max(radiator, stub),
        stub_length_m=stub,
        spacing_m=spacing,
        feed_offset_m=feed_offset,
        gap_m=intent.gap_m,
        base_height_m=max(intent.base_height_m, 0.01),
        folded=intent.folded,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="j_pole.half_wave_radiator_quarter_wave_stub",
        confidence=Confidence.EMPIRICAL,
        tolerance_m=radiator * 0.04,
        source_ids=(SOURCE_ARRL_DIPOLE,),
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=(
            "estimator.warning.starting_point",
            "estimator.warning.j_pole_matching",
        ),
        rows=(
            _length_row("geometry.radiator", parameters.radiator_height_m),
            _length_row("geometry.stub", parameters.stub_length_m),
            _length_row("field.spacing", parameters.spacing_m),
            _length_row("geometry.feed_offset", parameters.feed_offset_m),
        ),
    )


def estimate_ringo(intent: DesignIntent) -> DimensionEstimate:
    scale = intent.frequency_hz / RINGO_REFERENCE_FREQUENCY_HZ
    # Application preset calibrated for AntennaDesk's simplified Ringo
    # geometry: a 0.725-wave vertical with a small horizontal matching ring.
    reference_radiator = 4.34
    reference_ring_diameter = 0.84
    reference_ring_height = 0.06
    radiator = reference_radiator / scale
    parameters = RingoParameters(
        frequency_hz=intent.frequency_hz,
        radiator_height_m=radiator,
        ring_diameter_m=reference_ring_diameter / scale,
        ring_height_m=reference_ring_height / scale,
        ring_sides=16,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="ringo.scaled_application_preset",
        confidence=Confidence.HEURISTIC,
        tolerance_m=radiator * 0.06,
        source_ids=(SOURCE_APPLICATION_PRESET,),
        assumptions=("estimator.assumption.height_and_ground",),
        warnings=(
            "estimator.warning.starting_point",
            "estimator.warning.ringo_heuristic",
        ),
        rows=(
            _length_row("geometry.radiator", radiator),
            _length_row("geometry.diameter", parameters.ring_diameter_m),
            _length_row("field.height", parameters.ring_height_m),
        ),
    )


def estimate_yagi(intent: DesignIntent) -> DimensionEstimate:
    if not MIN_YAGI_ELEMENTS <= intent.yagi_elements <= MAX_YAGI_ELEMENTS:
        raise UnsupportedEstimateError(
            f"the Yagi estimator supports {MIN_YAGI_ELEMENTS} to {MAX_YAGI_ELEMENTS} elements"
        )
    wavelength = wavelength_m(intent.frequency_hz)
    normalized = dl6wu_elements(intent.yagi_elements)
    elements = tuple(
        YagiElement(
            position_m=spacing * wavelength,
            length_m=length * wavelength,
            radius_m=intent.wire_radius_m,
        )
        for length, spacing in normalized
    )
    parameters = YagiParameters(
        frequency_hz=intent.frequency_hz,
        elements=elements,
        height_m=intent.height_m,
        driven_index=1,
        azimuth_deg=intent.azimuth_deg,
        material=intent.material,
        ground=intent.ground,
    )
    rows = (
        _count_row("geometry.elements", len(elements)),
        *tuple(_length_row("field.element_length", element.length_m) for element in elements),
        _length_row(
            "geometry.boom_length",
            elements[-1].position_m - elements[0].position_m,
        ),
        _length_row("field.height", intent.height_m),
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="yagi.dl6wu_trimming_2_32",
        confidence=Confidence.REFERENCE_SCALED,
        tolerance_m=wavelength * 0.02,
        source_ids=(SOURCE_DL6WU_YAGI,),
        assumptions=(
            "estimator.assumption.yagi_reference",
            "estimator.assumption.yagi_element_diameter",
        ),
        warnings=(
            "estimator.warning.starting_point",
            "estimator.warning.yagi_not_unique",
        ),
        rows=rows,
    )


def estimate_moxon(intent: DesignIntent) -> DimensionEstimate:
    reference = moxon_20m_wire(
        height_m=intent.height_m,
        azimuth_deg=intent.azimuth_deg,
        material=intent.material,
        ground=intent.ground,
    )
    scale = MOXON_REFERENCE_FREQUENCY_HZ / intent.frequency_hz
    parameters = MoxonParameters(
        frequency_hz=intent.frequency_hz,
        width_m=reference.width_m * scale,
        depth_m=reference.depth_m * scale,
        reflector_tip_m=reference.reflector_tip_m * scale,
        driven_tip_m=reference.driven_tip_m * scale,
        height_m=intent.height_m,
        azimuth_deg=intent.azimuth_deg,
        wire_radius_m=intent.wire_radius_m,
        material=intent.material,
        ground=intent.ground,
    )
    return DimensionEstimate(
        parameters=parameters,
        method_id="moxon.cebik_20m_scaled",
        confidence=Confidence.REFERENCE_SCALED,
        tolerance_m=parameters.width_m * 0.02,
        source_ids=(SOURCE_CEBIK_MOXON,),
        assumptions=("estimator.assumption.reference_scaling",),
        warnings=(
            "estimator.warning.starting_point",
            "estimator.warning.moxon_gap",
        ),
        rows=(
            _length_row("geometry.width", parameters.width_m),
            _length_row("geometry.depth", parameters.depth_m),
            _length_row("geometry.gap", parameters.gap_m),
            _length_row("field.height", intent.height_m),
        ),
    )


ESTIMATORS = {
    ANTENNA_TYPE_WIRE_DIPOLE: estimate_dipole,
    ANTENNA_TYPE_FOLDED_DIPOLE: estimate_folded_dipole,
    ANTENNA_TYPE_LOOP: estimate_loop,
    ANTENNA_TYPE_VERTICAL: estimate_vertical,
    ANTENNA_TYPE_INVERTED_V: estimate_inverted_v,
    ANTENNA_TYPE_FAN_DIPOLE: estimate_fan_dipole,
    ANTENNA_TYPE_ENDFED: estimate_endfed,
    ANTENNA_TYPE_OCFD: estimate_ocfd,
    ANTENNA_TYPE_J_POLE: estimate_j_pole,
    ANTENNA_TYPE_RINGO: estimate_ringo,
    ANTENNA_TYPE_YAGI: estimate_yagi,
    ANTENNA_TYPE_MOXON: estimate_moxon,
}

SUPPORTED_ESTIMATOR_TYPES = frozenset(ESTIMATORS)


def estimate_intent(intent: DesignIntent) -> DimensionEstimate:
    estimator = ESTIMATORS.get(intent.antenna_type)
    if estimator is None:
        if intent.antenna_type == ANTENNA_TYPE_CUSTOM:
            raise UnsupportedEstimateError(
                "arbitrary custom geometry has no frequency-only estimator"
            )
        raise UnsupportedEstimateError(
            f"no estimator is registered for antenna type {intent.antenna_type!r}"
        )
    return estimator(intent)
