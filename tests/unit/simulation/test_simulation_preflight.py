# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pre-flight orchestration with a simulation spec and stored result."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER, ConductorMaterial
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.common.validation import Diagnostic, Severity
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationResult, SimulationStatus
from antennadesk.domain.simulation.run import SimulationRun
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.fingerprint import model_fingerprint
from antennadesk.simulation.preflight import run_preflight


def _spec(frequency_hz: float = 7_100_000.0) -> SimulationSpec:
    return SimulationSpec(frequency_plan=FrequencyPlan.single(frequency_hz))


def _result(
    spec: SimulationSpec,
    *,
    status: SimulationStatus = SimulationStatus.COMPLETED,
    fingerprint: str = "a" * 64,
    diagnostics: tuple[Diagnostic, ...] = (),
) -> SimulationResult:
    return SimulationResult(
        status=status,
        spec=spec,
        model_fingerprint=fingerprint,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(),
        diagnostics=diagnostics,
        started_at=datetime(2026, 11, 12, tzinfo=UTC),
        finished_at=datetime(2026, 11, 12, tzinfo=UTC),
    )


def _below_ground_project() -> Project:
    wire = Wire(
        id="buried",
        start=Point3D(-5.0, 0.0, -1.0),
        end=Point3D(5.0, 0.0, -1.0),
        radius_m=0.001,
        material=COPPER,
    )
    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(wire,),
        feed=FeedPoint("buried", 5.0),
        ground=GroundModel.perfect(),
    )
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="buried",
            variant_name="buried",
            parameters=parameters,
        )
    )


def _permeable_project() -> Project:
    steel = ConductorMaterial(
        name="steel",
        conductivity_s_per_m=1e6,
        relative_permeability=100.0,
    )
    wire = Wire(
        id="radiator",
        start=Point3D(-5.0, 0.0, 8.0),
        end=Point3D(5.0, 0.0, 8.0),
        radius_m=0.001,
        material=steel,
    )
    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(wire,),
        feed=FeedPoint("radiator", 5.0),
    )
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="steel",
            variant_name="steel",
            parameters=parameters,
        )
    )


def test_permeability_assumption_is_reported() -> None:
    project = _permeable_project()
    design = project.designs[0]

    report = run_preflight(project, design, _spec())

    finding = next(
        finding for finding in report.findings if finding.code == "solver.permeability_unsupported"
    )
    assert finding.severity is Severity.WARNING
    assert finding.category.value == "solver"


def test_below_ground_is_a_blocking_error() -> None:
    project = _below_ground_project()
    design = project.designs[0]

    report = run_preflight(project, design, _spec())

    finding = next(
        finding for finding in report.findings if finding.code == "geometry.below_ground"
    )
    assert finding.severity is Severity.ERROR
    assert report.ready is False
    assert report.status.value == "error"


def test_segmentation_diagnostics_are_included(sample_project: Project) -> None:
    design = sample_project.designs[0]

    report = run_preflight(sample_project, design, _spec())

    codes = {finding.code for finding in report.findings}
    assert "segmentation.feed_offset" in codes
    finding = next(
        finding for finding in report.findings if finding.code == "segmentation.feed_offset"
    )
    assert finding.severity is Severity.WARNING
    assert finding.action.value == "edit_feed"


def test_missing_result_is_a_warning(sample_project: Project) -> None:
    design = sample_project.designs[0]

    report = run_preflight(sample_project, design, _spec())

    finding = next(finding for finding in report.findings if finding.code == "simulation.missing")
    assert finding.severity is Severity.WARNING
    assert finding.action.value == "run_simulation"


@pytest.mark.parametrize(
    ("status", "code"),
    [
        (SimulationStatus.CANCELLED, "simulation.cancelled"),
        (SimulationStatus.PARTIAL, "simulation.partial"),
    ],
)
def test_non_completed_results_are_warnings(
    sample_project: Project,
    status: SimulationStatus,
    code: str,
) -> None:
    design = sample_project.designs[0]
    spec = _spec()
    result = _result(spec, status=status)

    report = run_preflight(sample_project, design, spec, result=result)
    finding = next(finding for finding in report.findings if finding.code == code)

    assert finding.severity is Severity.WARNING


def test_failed_result_is_an_error(sample_project: Project) -> None:
    design = sample_project.designs[0]
    spec = _spec()
    result = _result(spec, status=SimulationStatus.ERROR)

    report = run_preflight(sample_project, design, spec, result=result)

    assert "simulation.failed" in {finding.code for finding in report.findings}
    assert report.ready is False


def test_negative_resistance_diagnostic_is_reported(sample_project: Project) -> None:
    design = sample_project.designs[0]
    spec = _spec()
    result = _result(
        spec,
        diagnostics=(
            Diagnostic(
                code="normalization.negative_resistance",
                severity=Severity.ERROR,
                message="negative resistance",
                field="impedance",
            ),
        ),
    )

    report = run_preflight(sample_project, design, spec, result=result)
    finding = next(
        finding
        for finding in report.findings
        if finding.code == "normalization.negative_resistance"
    )

    assert finding.severity is Severity.ERROR
    assert finding.category.value == "simulation"
    assert report.ready is False


def test_stale_result_is_a_warning(sample_project: Project) -> None:
    design = sample_project.designs[0]
    spec = _spec()
    result = _result(spec, fingerprint="b" * 64)

    report = run_preflight(sample_project, design, spec, result=result)

    finding = next(finding for finding in report.findings if finding.code == "simulation.stale")
    assert finding.severity is Severity.WARNING


def test_current_result_has_no_staleness_warning(sample_project: Project) -> None:
    design = sample_project.designs[0]
    spec = _spec()
    result = _result(
        spec,
        fingerprint=model_fingerprint(design.antenna, spec),
    )

    report = run_preflight(sample_project, design, spec, result=result)

    codes = {finding.code for finding in report.findings}
    assert "simulation.stale" not in codes
    assert "simulation.missing" not in codes
    assert "simulation.failed" not in codes


def test_persisted_result_is_used_when_not_passed(sample_project: Project) -> None:
    design = sample_project.designs[0]
    spec = _spec()
    result = _result(spec, status=SimulationStatus.ERROR)
    project = sample_project.with_simulation_run(
        SimulationRun(
            id=uuid4(),
            design_id=design.id,
            created_at=sample_project.updated_at,
            result=result,
        ),
        updated_at=sample_project.updated_at,
    )

    report = run_preflight(project, design, spec)

    assert "simulation.failed" in {finding.code for finding in report.findings}
