# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.design import (
    antenna_type_for,
    primary_dimension_m,
    with_primary_dimension,
)
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)
from antennadesk.domain.antennas.phased_vertical import (
    PhasedVerticalParameters,
    phased_vertical_parameters,
)


def test_phased_vertical_builds_spaced_verticals_and_radials() -> None:
    parameters = phased_vertical_parameters(
        frequency_hz=14_100_000.0,
        element_count=3,
        height_m=5.0,
        spacing_m=5.5,
        base_height_m=0.5,
        radial_count=4,
        radial_length_m=5.0,
    )

    model = parameters.to_antenna()

    verticals = tuple(wire for wire in model.wires if wire.id.startswith("phased-vertical-"))
    radials = tuple(wire for wire in model.wires if wire.id.startswith("phased-radial-"))
    assert parameters.template_name == "Phased vertical array"
    assert len(verticals) == 3
    assert len(radials) == 12
    assert [wire.start.x_m for wire in verticals] == pytest.approx([0.0, 5.5, 11.0])
    assert all(wire.start.z_m == pytest.approx(0.5) for wire in verticals)
    assert all(wire.end.z_m == pytest.approx(5.5) for wire in verticals)
    assert model.feed.wire_id == verticals[0].id
    assert model.feed.offset_m == 0.0
    assert len(model.sources) == 2
    assert parameters.total_conductor_length_m == pytest.approx(3 * 5.0 + 3 * 4 * 5.0)


def test_phased_vertical_detects_overlapping_radial_screens() -> None:
    overlapping = phased_vertical_parameters(
        element_count=4,
        spacing_m=5.0,
        radial_count=36,
        radial_length_m=5.0,
    )
    separated = phased_vertical_parameters(
        element_count=4,
        spacing_m=5.0,
        radial_count=36,
        radial_length_m=2.0,
    )
    no_radials = phased_vertical_parameters(
        element_count=4,
        spacing_m=5.0,
        radial_count=0,
    )

    assert overlapping.radial_screen_overlap is True
    assert separated.radial_screen_overlap is False
    assert no_radials.radial_screen_overlap is False


def test_phased_vertical_assigns_ideal_phase_and_amplitude_steps() -> None:
    parameters = phased_vertical_parameters(
        element_count=4,
        phase_step_deg=90.0,
        amplitude_taper=0.6,
    )

    model = parameters.to_antenna()

    assert parameters.source_amplitudes == pytest.approx((1.0, 0.8, 0.6, 0.4))
    assert parameters.source_phases == pytest.approx((0.0, 90.0, 180.0, 270.0))
    assert [source.wire_id for source in model.sources] == [
        "phased-vertical-1",
        "phased-vertical-2",
        "phased-vertical-3",
    ]
    assert [source.amplitude for source in model.sources] == pytest.approx([0.8, 0.6, 0.4])
    assert [source.phase_deg for source in model.sources] == pytest.approx([90.0, 180.0, 270.0])
    primary, *later = model.effective_sources
    assert primary.wire_id == "phased-vertical-0"
    assert primary.amplitude == 1.0
    assert primary.phase_deg == 0.0
    assert later == list(model.sources)


def test_phased_vertical_rotates_the_array_line_with_azimuth() -> None:
    parameters = phased_vertical_parameters(
        element_count=2,
        spacing_m=5.0,
        radial_count=0,
        azimuth_deg=90.0,
    )

    verticals = tuple(
        wire for wire in parameters.to_antenna().wires if wire.id.startswith("phased-vertical-")
    )

    assert verticals[0].start.x_m == pytest.approx(0.0, abs=1e-12)
    assert verticals[0].start.y_m == pytest.approx(0.0, abs=1e-12)
    assert verticals[1].start.x_m == pytest.approx(0.0, abs=1e-12)
    assert verticals[1].start.y_m == pytest.approx(5.0)


def test_phased_vertical_primary_dimension_tracks_the_radiator_height() -> None:
    parameters = phased_vertical_parameters(height_m=5.0)

    assert primary_dimension_m(parameters) == pytest.approx(5.0)

    scaled = with_primary_dimension(parameters, 6.5)

    assert isinstance(scaled, PhasedVerticalParameters)
    assert scaled.height_m == pytest.approx(6.5)
    assert scaled.spacing_m == pytest.approx(parameters.spacing_m)


def test_phased_vertical_design_identity() -> None:
    parameters = phased_vertical_parameters()

    assert antenna_type_for(parameters) == "phased_vertical"
    assert antenna_template_id(parameters) == "phased_vertical"
    assert antenna_family(parameters) is AntennaFamily.VERTICAL


def test_phased_vertical_rejects_invalid_configurations() -> None:
    with pytest.raises(ValueError, match="element_count"):
        phased_vertical_parameters(element_count=1)
    with pytest.raises(ValueError, match="amplitude_taper"):
        phased_vertical_parameters(amplitude_taper=0.95)
    with pytest.raises(ValueError, match="radial screen requires a positive"):
        phased_vertical_parameters(radial_count=4, radial_length_m=0.0)
    with pytest.raises(ValueError, match="conductor diameter"):
        phased_vertical_parameters(spacing_m=0.001, wire_radius_m=0.001)
    with pytest.raises(ValueError, match="phase_step_deg"):
        phased_vertical_parameters(phase_step_deg=400.0)


def test_phased_vertical_normalizes_azimuth_and_radial_angle() -> None:
    parameters = phased_vertical_parameters(
        azimuth_deg=-90.0,
        radial_angle_deg=450.0,
    )

    assert parameters.azimuth_deg == pytest.approx(270.0)
    assert parameters.radial_angle_deg == pytest.approx(90.0)


def test_phased_vertical_starting_spacing_is_quarter_wave() -> None:
    from antennadesk.domain.design.formulas import quarter_wave_length_m

    parameters = phased_vertical_parameters(frequency_hz=7_100_000.0)
    quarter = quarter_wave_length_m(7_100_000.0)

    assert parameters.height_m == pytest.approx(quarter)
    assert parameters.spacing_m == pytest.approx(quarter)
    assert math.isfinite(parameters.height_m)
