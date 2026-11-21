# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Log-periodic and phase-reversal persistence checks."""

from __future__ import annotations

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.design import AntennaDesignParameters
from antennadesk.domain.antennas.log_periodic import (
    cebik_10m_log_periodic_parameters,
)
from antennadesk.domain.antennas.transmission_line import TransmissionLine
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.schema import (
    LogPeriodicParametersPayload,
    document_from_project,
    project_from_document,
)


def _project(parameters: AntennaDesignParameters, name: str) -> Project:
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name=f"{name} project",
            variant_name=name,
            parameters=parameters,
        )
    )


def test_log_periodic_round_trips_with_its_transposed_phase_line() -> None:
    parameters = cebik_10m_log_periodic_parameters()
    original = _project(parameters, "LPDA")

    document = document_from_project(original)
    restored = project_from_document(document)

    payload = document.project.designs[0].parameters
    assert isinstance(payload, LogPeriodicParametersPayload)
    assert payload.phase_line_impedance_ohm == 75.0
    assert restored.designs[0].parameters == parameters
    assert restored.designs[0].antenna == original.designs[0].antenna
    assert restored.designs[0].antenna_type == "log_periodic"
    assert len(restored.designs[0].antenna.transmission_lines) == 3
    assert all(line.phase_reversal for line in restored.designs[0].antenna.transmission_lines)


def test_phase_reversal_round_trips_through_the_design_payload() -> None:
    parameters = cebik_10m_log_periodic_parameters()
    project = _project(parameters, "LPDA flag")
    design = project.designs[0]
    line = design.antenna.transmission_lines[0]
    assert line.phase_reversal
    replacement = TransmissionLine(
        id=line.id,
        start_wire_id=line.start_wire_id,
        start_offset_m=line.start_offset_m,
        end_wire_id=line.end_wire_id,
        end_offset_m=line.end_offset_m,
        characteristic_impedance_ohm=line.characteristic_impedance_ohm,
        length_m=line.length_m,
        velocity_factor=line.velocity_factor,
        phase_reversal=False,
    )
    updated = design.with_transmission_lines((replacement, *design.antenna.transmission_lines[1:]))
    project = project.with_design(updated, updated_at=project.updated_at)

    document = document_from_project(project)
    restored = project_from_document(document)

    assert not restored.designs[0].antenna.transmission_lines[0].phase_reversal
    assert restored.designs[0].antenna.transmission_lines[1].phase_reversal
