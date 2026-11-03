# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.dipole import DipoleOrientation
from antennadesk.domain.antennas.family import (
    AntennaFamily,
    antenna_family,
    antenna_template_id,
)
from antennadesk.domain.antennas.load import ParallelLoad
from antennadesk.domain.antennas.trap_dipole import (
    TRAP_LEFT_ID,
    TRAP_RIGHT_ID,
    TrapDipoleParameters,
)


def _parameters(**overrides: object) -> TrapDipoleParameters:
    values: dict[str, object] = {
        "frequency_hz": 7_100_000.0,
        "high_band_frequency_hz": 14_100_000.0,
        "inner_length_m": 10.0,
        "outer_length_m": 5.0,
        "trap_frequency_hz": 14_100_000.0,
        "trap_inductance_h": 10e-6,
        "height_m": 12.0,
    }
    values.update(overrides)
    return TrapDipoleParameters(**values)


def test_trap_dipole_builds_a_center_fed_wire_and_two_traps() -> None:
    parameters = _parameters()

    custom = parameters.to_custom_parameters()
    antenna = parameters.to_antenna(name="Trap")

    assert len(custom.wires) == 1
    assert custom.wires[0].length_m == pytest.approx(20.0)
    assert custom.feed.wire_id == "radiator"
    assert custom.feed.offset_m == pytest.approx(10.0)
    assert len(custom.loads) == 2
    assert all(isinstance(load, ParallelLoad) for load in custom.loads)
    assert [load.id for load in custom.loads] == [TRAP_LEFT_ID, TRAP_RIGHT_ID]
    assert [load.offset_m for load in custom.loads] == pytest.approx([5.0, 15.0])
    expected_c = 1.0 / ((2.0 * math.pi * 14_100_000.0) ** 2 * 10e-6)
    assert all(load.capacitance_f == pytest.approx(expected_c) for load in custom.loads)
    assert antenna == custom.to_antenna(name="Trap")
    assert custom.generator_id == "trap_dipole"


def test_trap_dipole_vertical_orientation_uses_base_height() -> None:
    parameters = _parameters(
        orientation=DipoleOrientation.VERTICAL,
        height_m=1.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
    )

    antenna = parameters.to_antenna()

    wire = antenna.wires[0]
    assert wire.start.z_m == pytest.approx(1.0)
    assert wire.end.z_m == pytest.approx(21.0)
    assert wire.start.x_m == pytest.approx(0.0)
    assert wire.end.x_m == pytest.approx(0.0)


def test_trap_dipole_rejects_invalid_band_and_geometry_values() -> None:
    with pytest.raises(ValueError, match="high_band_frequency_hz"):
        _parameters(high_band_frequency_hz=7_100_000.0)
    with pytest.raises(ValueError, match="inner_length_m"):
        _parameters(inner_length_m=0.0)
    with pytest.raises(ValueError, match="outer_length_m"):
        _parameters(outer_length_m=0.0)
    with pytest.raises(ValueError, match="trap_frequency_hz"):
        _parameters(trap_frequency_hz=0.0)
    with pytest.raises(ValueError, match="trap_inductance_h"):
        _parameters(trap_inductance_h=0.0)


def test_trap_dipole_total_length_updates_only_the_outer_sections() -> None:
    parameters = _parameters()

    edited = parameters.with_total_length(22.0)

    assert edited.total_length_m == pytest.approx(22.0)
    assert edited.inner_length_m == pytest.approx(10.0)
    assert edited.outer_length_m == pytest.approx(6.0)
    with pytest.raises(ValueError, match="exceed inner_length_m"):
        parameters.with_total_length(10.0)


def test_trap_dipole_maps_to_the_dipole_family() -> None:
    parameters = _parameters()

    assert parameters.trap_positions_m == pytest.approx((5.0, 15.0))
    assert parameters.managed_load_ids == frozenset({TRAP_LEFT_ID, TRAP_RIGHT_ID})
    assert antenna_family(parameters) is AntennaFamily.DIPOLE
    assert antenna_template_id(parameters) == "trap_dipole"
