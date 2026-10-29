from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.environment.ground import GroundModel


def test_dipole_generates_centered_wire(dipole_parameters: DipoleParameters) -> None:
    antenna = dipole_parameters.to_antenna()

    assert antenna.name == "Dipole"
    assert antenna.design_frequency_hz == pytest.approx(7_100_000.0)
    assert len(antenna.wires) == 1

    wire = antenna.wires[0]
    assert wire.id == "radiator"
    assert wire.length_m == pytest.approx(20.0)
    assert wire.start.x_m == pytest.approx(-10.0)
    assert wire.end.x_m == pytest.approx(10.0)
    assert wire.start.z_m == pytest.approx(8.0)
    assert wire.end.z_m == pytest.approx(8.0)
    assert antenna.feed.wire_id == "radiator"
    assert antenna.feed.offset_m == pytest.approx(10.0)


def test_azimuth_rotates_the_wire() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        azimuth_deg=90.0,
    )
    wire = parameters.to_antenna().wires[0]

    assert wire.start.x_m == pytest.approx(0.0, abs=1e-12)
    assert wire.start.y_m == pytest.approx(-10.0)
    assert wire.end.x_m == pytest.approx(0.0, abs=1e-12)
    assert wire.end.y_m == pytest.approx(10.0)


def test_azimuth_is_normalized() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        azimuth_deg=370.0,
    )
    assert parameters.azimuth_deg == pytest.approx(10.0)


def test_with_length_returns_a_new_value(dipole_parameters: DipoleParameters) -> None:
    edited = dipole_parameters.with_length(19.5)

    assert edited is not dipole_parameters
    assert edited.total_length_m == pytest.approx(19.5)
    assert dipole_parameters.total_length_m == pytest.approx(20.0)
    assert edited.to_antenna().wires[0].length_m == pytest.approx(19.5)


def test_wavelength_and_half_length(dipole_parameters: DipoleParameters) -> None:
    assert dipole_parameters.wavelength_m == pytest.approx(299_792_458.0 / 7_100_000.0)
    assert dipole_parameters.half_length_m == pytest.approx(10.0)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("frequency_hz", 0.0),
        ("frequency_hz", -1.0),
        ("total_length_m", 0.0),
        ("height_m", -1.0),
        ("wire_radius_m", 0.0),
        ("frequency_hz", math.nan),
    ],
)
def test_invalid_parameters_are_rejected(field: str, value: float) -> None:
    values = {
        "frequency_hz": 7_100_000.0,
        "total_length_m": 20.0,
        "height_m": 8.0,
        "wire_radius_m": 0.001,
    }
    values[field] = value

    with pytest.raises(ValueError):
        DipoleParameters(**values)


def test_finite_ground_is_preserved(dipole_parameters: DipoleParameters) -> None:
    ground = GroundModel.finite(
        relative_permittivity=13.0,
        conductivity_s_per_m=0.005,
    )
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        ground=ground,
    )
    assert parameters.to_antenna().environment.ground == ground
