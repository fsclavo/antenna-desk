# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math
from uuid import uuid4

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.load import SeriesLoad
from antennadesk.domain.projects.project import DesignVariant


def test_design_with_loads_validates_and_preserves_them() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    load = SeriesLoad("load-1", "radiator", 10.0, inductance_h=12e-6)
    antenna = parameters.to_antenna().with_loads((load,))
    design = DesignVariant(
        id=uuid4(),
        name="Loaded",
        antenna_type="wire_dipole",
        parameters=parameters,
        antenna=antenna,
    )

    edited = design.with_parameters(parameters.with_length(19.5))

    assert design.antenna.loads == (load,)
    assert edited.antenna.loads == (load,)
    assert edited.antenna.wires[0].length_m == 19.5


def test_design_with_loads_can_replace_them() -> None:
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Loaded",
        antenna_type="wire_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )
    load = SeriesLoad("load-1", "radiator", 10.0, resistance_ohm=50.0)

    loaded = design.with_loads((load,))

    assert loaded.antenna.loads == (load,)
    assert design.antenna.loads == ()
    assert loaded.parameters == parameters
    assert loaded.antenna.name == design.antenna.name


def test_vertical_design_replaces_its_managed_coil_and_keeps_user_loads() -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=1.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=0.5,
        loading_coil_inductance_h=10e-6,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Loaded vertical",
        antenna_type="vertical",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )
    user_load = SeriesLoad("user-load", "radiator", 1.5, resistance_ohm=50.0)
    design = design.with_loads((*design.antenna.loads, user_load))

    edited = design.with_parameters(
        replace(
            parameters,
            loading_coil_offset_m=1.0,
            loading_coil_inductance_h=20e-6,
        )
    )

    loads = {load.id: load for load in edited.antenna.loads}
    assert set(loads) == {"loading-coil", "user-load"}
    assert loads["loading-coil"].offset_m == 1.0
    assert loads["loading-coil"].inductance_h == 20e-6
    assert loads["user-load"] is user_load


def test_disabling_a_vertical_loading_coil_removes_it() -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=10e-6,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Loaded vertical",
        antenna_type="vertical",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )

    edited = design.with_parameters(replace(parameters, loading_coil_enabled=False))

    assert edited.antenna.loads == ()


def test_custom_parameter_loads_are_not_duplicated_when_editing() -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.custom import CustomAntennaParameters
    from antennadesk.domain.antennas.feed import FeedPoint
    from antennadesk.domain.antennas.geometry import Point3D
    from antennadesk.domain.antennas.materials import COPPER
    from antennadesk.domain.antennas.wire import Wire

    load = SeriesLoad("load-1", "w1", 5.0, inductance_h=12e-6)
    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                "w1",
                Point3D(-5.0, 0.0, 8.0),
                Point3D(5.0, 0.0, 8.0),
                0.001,
                COPPER,
            ),
        ),
        feed=FeedPoint("w1", 5.0),
        loads=(load,),
    )
    design = DesignVariant(
        id=uuid4(),
        name="Custom loaded",
        antenna_type="custom",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )

    edited = design.with_parameters(replace(parameters, frequency_hz=7_050_000.0))

    assert edited.antenna.loads == (load,)


def test_trap_dipole_design_regenerates_its_traps_and_keeps_user_loads() -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Trap dipole",
        antenna_type="trap_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )
    user_load = SeriesLoad("user-load", "radiator", 2.0, resistance_ohm=50.0)
    design = design.with_loads((*design.antenna.loads, user_load))

    edited = design.with_parameters(replace(parameters, trap_inductance_h=15e-6))

    loads = {load.id: load for load in edited.antenna.loads}
    assert set(loads) == {"trap-left", "trap-right", "user-load"}
    assert loads["trap-left"].inductance_h == 15e-6
    expected_c = 1.0 / ((2.0 * math.pi * 14_100_000.0) ** 2 * 15e-6)
    assert loads["trap-left"].capacitance_f == pytest.approx(expected_c)
    assert loads["user-load"] is user_load


def test_changing_a_trap_dipole_to_a_dipole_drops_the_traps() -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Trap dipole",
        antenna_type="trap_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )

    edited = design.with_parameters(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=12.0,
        )
    )

    assert edited.antenna.loads == ()


def test_changing_a_loaded_vertical_to_a_dipole_drops_the_loading_coil() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=10e-6,
    )
    design = DesignVariant(
        id=uuid4(),
        name="Loaded vertical",
        antenna_type="vertical",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )

    edited = design.with_parameters(
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=12.0,
        )
    )

    assert edited.antenna.loads == ()
