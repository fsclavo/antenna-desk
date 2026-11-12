# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Model-level construction pre-flight checks."""

from __future__ import annotations

from uuid import uuid4

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.common.validation import Severity
from antennadesk.domain.design.preflight import (
    PreflightAction,
    PreflightCategory,
    PreflightFinding,
    PreflightReport,
    PreflightStatus,
    run_model_preflight,
)
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.projects.construction import (
    CONSTRUCTION_CHECKLIST_KEYS,
    AsBuiltDimension,
    ConstructionChecklistItem,
    ConstructionRecord,
)
from antennadesk.domain.projects.installation import InstallationProfile
from antennadesk.domain.projects.project import Project


def _custom_model(*wires: Wire, ground: GroundModel | None = None) -> Project:
    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=wires,
        feed=FeedPoint(wires[0].id, wires[0].length_m / 2.0),
        ground=ground or GroundModel.free_space(),
    )
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="custom",
            variant_name="custom",
            parameters=parameters,
        )
    )


def _wire(
    wire_id: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
) -> Wire:
    return Wire(
        id=wire_id,
        start=Point3D(*start),
        end=Point3D(*end),
        radius_m=0.001,
        material=COPPER,
    )


def _codes(project: Project) -> set[str]:
    return {finding.code for finding in run_model_preflight(project, project.designs[0])}


def test_missing_site_and_construction_data_are_warnings(sample_project: Project) -> None:
    findings = run_model_preflight(sample_project, sample_project.designs[0])

    codes = {finding.code for finding in findings}
    assert "supports.no_profile" in codes
    assert "construction.record_missing" in codes
    assert all(
        finding.severity is Severity.WARNING
        for finding in findings
        if finding.code in {"supports.no_profile", "construction.record_missing"}
    )


def test_profile_height_and_width_are_hard_errors(sample_project: Project) -> None:
    profile = InstallationProfile(
        id=uuid4(),
        name="Small yard",
        available_height_m=5.0,
        available_width_m=10.0,
    )
    project = sample_project.with_installation_state(
        (profile,),
        profile.id,
        updated_at=sample_project.updated_at,
    )

    findings = run_model_preflight(project, project.designs[0])
    by_code = {finding.code: finding for finding in findings}

    assert by_code["supports.height_exceeded"].severity is Severity.ERROR
    assert by_code["supports.width_exceeded"].severity is Severity.ERROR
    assert by_code["supports.height_exceeded"].action is PreflightAction.EDIT_SUPPORTS
    assert by_code["supports.height_exceeded"].translation_values()["top"] == "8.000"
    assert by_code["supports.width_exceeded"].translation_values()["span"] == "20.000"


def test_matching_profile_removes_the_site_warnings(sample_project: Project) -> None:
    profile = InstallationProfile(
        id=uuid4(),
        name="Back yard",
        available_height_m=12.0,
        available_width_m=25.0,
    )
    project = sample_project.with_installation_state(
        (profile,),
        profile.id,
        updated_at=sample_project.updated_at,
    )

    codes = _codes(project)

    assert not {code for code in codes if code.startswith("supports.")}


def test_profile_with_unknown_envelope_warns(sample_project: Project) -> None:
    profile = InstallationProfile(id=uuid4(), name="Portable")
    project = sample_project.with_installation_state(
        (profile,),
        profile.id,
        updated_at=sample_project.updated_at,
    )

    codes = _codes(project)

    assert "supports.height_unknown" in codes
    assert "supports.width_unknown" in codes


def test_profile_ground_mismatch_warns(sample_project: Project) -> None:
    profile = InstallationProfile(
        id=uuid4(),
        name="Sandy site",
        available_height_m=12.0,
        available_width_m=25.0,
        ground=GroundModel.perfect(),
    )
    project = sample_project.with_installation_state(
        (profile,),
        profile.id,
        updated_at=sample_project.updated_at,
    )

    codes = _codes(project)

    assert "supports.ground_mismatch" in codes


def test_crossing_and_overlapping_wires_are_reported() -> None:
    project = _custom_model(
        _wire("a", (-5.0, 0.0, 8.0), (5.0, 0.0, 8.0)),
        _wire("b", (0.0, -5.0, 8.0), (0.0, 5.0, 8.0)),
        _wire("c", (2.0, 0.0, 8.0), (6.0, 0.0, 8.0)),
    )

    findings = run_model_preflight(project, project.designs[0])
    by_code = {finding.code: finding for finding in findings}

    assert by_code["geometry.wire_crossing"].subject == "a / b"
    assert by_code["geometry.wire_overlap"].subject == "a / c"
    assert by_code["geometry.wire_crossing"].values == (("first", "a"), ("second", "b"))


def test_short_wire_is_reported() -> None:
    project = _custom_model(
        _wire("long", (-5.0, 0.0, 8.0), (5.0, 0.0, 8.0)),
        _wire("stub", (0.0, 1.0, 8.0), (0.005, 1.0, 8.0)),
    )

    findings = run_model_preflight(project, project.designs[0])
    by_code = {finding.code: finding for finding in findings}

    assert by_code["geometry.wire_too_short"].subject == "stub"
    assert by_code["geometry.wire_too_short"].values == (("wire", "stub"),)


def test_base_fed_verticals_do_not_warn_about_a_feed_at_the_wire_end() -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(frequency_hz=7_100_000.0, height_m=10.0)
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="vertical",
            variant_name="vertical",
            parameters=parameters,
        )
    )

    codes = _codes(project)

    assert "antenna.feed.at_wire_end" not in codes


def test_custom_end_feed_keeps_the_feed_at_wire_end_warning() -> None:
    wire = _wire("random-wire", (0.0, 0.0, 8.0), (20.0, 0.0, 8.0))
    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(wire,),
        feed=FeedPoint(wire.id, 0.0),
    )
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="random wire",
            variant_name="random wire",
            parameters=parameters,
        )
    )

    codes = _codes(project)

    assert "antenna.feed.at_wire_end" in codes


def test_free_space_is_an_information_finding() -> None:
    project = _custom_model(
        _wire("radiator", (-5.0, 0.0, 8.0), (5.0, 0.0, 8.0)),
    )
    findings = run_model_preflight(project, project.designs[0])
    free_space = next(finding for finding in findings if finding.code == "geometry.free_space")

    assert free_space.severity is Severity.INFO
    assert free_space.category is PreflightCategory.GEOMETRY
    assert free_space.action is PreflightAction.EDIT_GEOMETRY


def test_construction_record_info_findings(sample_project: Project) -> None:
    record = ConstructionRecord(
        dimensions=(AsBuiltDimension(id=uuid4(), label="Radiator length", actual_value_m=19.9),),
        checklist=(ConstructionChecklistItem(CONSTRUCTION_CHECKLIST_KEYS[0], checked=True),),
    )
    project = sample_project.with_construction_record(
        record,
        updated_at=sample_project.updated_at,
    )

    codes = _codes(project)

    assert "construction.record_missing" not in codes
    assert "construction.dimensions_missing" not in codes
    assert "construction.checklist_incomplete" in codes


def test_complete_construction_record_has_no_construction_findings(
    sample_project: Project,
) -> None:
    record = ConstructionRecord(
        dimensions=(AsBuiltDimension(id=uuid4(), label="Radiator length", actual_value_m=19.9),),
        checklist=tuple(
            ConstructionChecklistItem(key, checked=True) for key in CONSTRUCTION_CHECKLIST_KEYS
        ),
    )
    project = sample_project.with_construction_record(
        record,
        updated_at=sample_project.updated_at,
    )

    codes = _codes(project)

    assert not {code for code in codes if code.startswith("construction.")}


def test_report_readiness_depends_on_errors() -> None:
    warning = PreflightFinding(
        code="supports.no_profile",
        category=PreflightCategory.SUPPORTS,
        severity=Severity.WARNING,
        message="no profile",
    )
    error = PreflightFinding(
        code="supports.height_exceeded",
        category=PreflightCategory.SUPPORTS,
        severity=Severity.ERROR,
        message="too tall",
    )

    warning_report = PreflightReport((warning,))
    error_report = PreflightReport((warning, error))
    ready_report = PreflightReport()

    assert warning_report.ready is True
    assert warning_report.status is PreflightStatus.WARNING
    assert error_report.ready is False
    assert error_report.status is PreflightStatus.ERROR
    assert error_report.errors == (error,)
    assert ready_report.status is PreflightStatus.READY


def test_findings_are_sorted_by_severity_and_category() -> None:
    report = PreflightReport(
        (
            PreflightFinding(
                code="construction.record_missing",
                category=PreflightCategory.CONSTRUCTION,
                severity=Severity.WARNING,
                message="record",
            ),
            PreflightFinding(
                code="supports.height_exceeded",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.ERROR,
                message="height",
            ),
            PreflightFinding(
                code="geometry.free_space",
                category=PreflightCategory.GEOMETRY,
                severity=Severity.INFO,
                message="free space",
            ),
        )
    )

    assert [finding.severity for finding in report.sorted_findings()] == [
        Severity.ERROR,
        Severity.WARNING,
        Severity.INFO,
    ]


def test_finding_requires_code_and_message() -> None:
    with pytest.raises(ValueError, match="code"):
        PreflightFinding(
            code=" ",
            category=PreflightCategory.GEOMETRY,
            severity=Severity.INFO,
            message="x",
        )
    with pytest.raises(ValueError, match="message"):
        PreflightFinding(
            code="x",
            category=PreflightCategory.GEOMETRY,
            severity=Severity.INFO,
            message=" ",
        )
