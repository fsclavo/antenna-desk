# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from uuid import uuid4

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.transmission_line import TransmissionLine
from antennadesk.domain.projects.project import DesignVariant


def _dipole() -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )


def _line() -> TransmissionLine:
    return TransmissionLine(
        id="line-1",
        start_wire_id="radiator",
        start_offset_m=0.0,
        end_wire_id="radiator",
        end_offset_m=10.0,
        characteristic_impedance_ohm=300.0,
        length_m=10.0,
        velocity_factor=0.9,
    )


def test_design_parameters_preserve_transmission_lines() -> None:
    parameters = _dipole()
    design = DesignVariant(
        id=uuid4(),
        name="Line",
        antenna_type="wire_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna().with_transmission_lines((_line(),)),
    )

    edited = design.with_parameters(parameters.with_length(19.0))

    assert edited.antenna.transmission_lines == (_line(),)
    assert edited.antenna.wires[0].length_m == 19.0


def test_design_can_replace_transmission_lines() -> None:
    parameters = _dipole()
    design = DesignVariant(
        id=uuid4(),
        name="Line",
        antenna_type="wire_dipole",
        parameters=parameters,
        antenna=parameters.to_antenna(),
    )

    replaced = design.with_transmission_lines((_line(),))

    assert replaced.antenna.transmission_lines == (_line(),)
    assert design.antenna.transmission_lines == ()
