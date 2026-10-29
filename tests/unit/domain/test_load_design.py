# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from uuid import uuid4

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
