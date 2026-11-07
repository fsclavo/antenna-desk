# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.family import AntennaFamily, antenna_family, antenna_template_id
from antennadesk.domain.antennas.transmission_line_doublet import (
    DoubletPreset,
    doublet_starting_parameters,
)
from antennadesk.domain.antennas.zepp import zepp_starting_parameters


@pytest.mark.parametrize("preset", list(DoubletPreset))
def test_typed_doublet_builds_the_published_antenna(preset: DoubletPreset) -> None:
    parameters = doublet_starting_parameters(preset)
    model = parameters.to_antenna()

    assert parameters.template_name in {"G5RV", "ZS6BKW"}
    assert len(model.wires) == 2
    assert len(model.transmission_lines) == 1
    assert model.transmission_lines[0].length_m == pytest.approx(parameters.line_length_m)
    assert model.transmission_lines[0].characteristic_impedance_ohm == pytest.approx(
        parameters.line_impedance_ohm
    )
    assert antenna_family(parameters) is AntennaFamily.DIPOLE
    assert antenna_template_id(parameters) == preset.value


def test_g5rv_typed_start_matches_the_published_defaults() -> None:
    parameters = doublet_starting_parameters(DoubletPreset.G5RV)

    assert parameters.frequency_hz == pytest.approx(14_100_000.0)
    assert parameters.dipole_total_length_m == pytest.approx(31.1)
    assert parameters.line_impedance_ohm == pytest.approx(450.0)
    assert parameters.line_length_m == pytest.approx(10.36)
    assert parameters.line_velocity_factor == pytest.approx(1.0)


def test_zs6bkw_typed_start_matches_the_published_defaults() -> None:
    parameters = doublet_starting_parameters(DoubletPreset.ZS6BKW)

    assert parameters.dipole_total_length_m == pytest.approx(28.4)
    assert parameters.line_impedance_ohm == pytest.approx(400.0)
    assert parameters.line_length_m == pytest.approx(13.6)


def test_typed_doublet_rejects_an_invalid_velocity_factor() -> None:
    parameters = doublet_starting_parameters(DoubletPreset.G5RV)

    with pytest.raises(ValueError, match="velocity_factor"):
        parameters.__class__(
            **{
                **{
                    field: getattr(parameters, field)
                    for field in (
                        "frequency_hz",
                        "preset",
                        "dipole_total_length_m",
                        "height_m",
                        "feed_height_m",
                        "azimuth_deg",
                        "line_impedance_ohm",
                        "line_length_m",
                        "wire_radius_m",
                        "material",
                        "ground",
                    )
                },
                "line_velocity_factor": 1.1,
            }
        )


def test_typed_zepp_matches_the_legacy_geometry() -> None:
    parameters = zepp_starting_parameters()
    model = parameters.to_antenna()

    assert len(model.wires) == 4
    assert parameters.template_name == "Zepp"
    assert antenna_family(parameters) is AntennaFamily.DIPOLE
    assert antenna_template_id(parameters) == "zepp"
    assert parameters.radiator_length_m > 0.0
    assert parameters.matching_section_length_m > 0.0
