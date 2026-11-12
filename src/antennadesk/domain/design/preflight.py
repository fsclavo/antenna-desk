# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction pre-flight model and structural checks.

The pre-flight is deliberately conservative: it reports what the canonical
model, project metadata, and solver assumptions can prove.  It never turns a
warning into a pass and never claims that a design is buildable when an error
is present.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..antennas.antenna import AntennaModel
from ..antennas.beverage import BeverageParameters
from ..antennas.endfed import EndFedParameters
from ..antennas.fan_dipole import FanDipoleParameters
from ..antennas.geometry_checks import wire_pair_issues
from ..antennas.inverted_l import InvertedLParameters
from ..antennas.inverted_v import InvertedVParameters
from ..antennas.phased_vertical import PhasedVerticalParameters
from ..antennas.ringo import RingoParameters
from ..antennas.scv import ScvParameters
from ..antennas.vertical import VerticalParameters
from ..common.validation import Diagnostic, Severity
from ..environment.ground import GroundKind
from ..projects.construction import CONSTRUCTION_CHECKLIST_KEYS
from ..projects.project import DesignVariant, Project


class PreflightCategory(StrEnum):
    """The part of the construction package a finding belongs to."""

    GEOMETRY = "geometry"
    FEED = "feed"
    SEGMENTATION = "segmentation"
    SUPPORTS = "supports"
    CONSTRUCTION = "construction"
    SIMULATION = "simulation"
    SOLVER = "solver"


class PreflightAction(StrEnum):
    """Where the user should go to resolve a finding."""

    NONE = "none"
    EDIT_GEOMETRY = "edit_geometry"
    EDIT_FEED = "edit_feed"
    EDIT_LOADS = "edit_loads"
    EDIT_LINES = "edit_lines"
    EDIT_SEGMENTATION = "edit_segmentation"
    EDIT_SUPPORTS = "edit_supports"
    EDIT_CONSTRUCTION = "edit_construction"
    RUN_SIMULATION = "run_simulation"


class PreflightStatus(StrEnum):
    """Overall construction readiness."""

    READY = "ready"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class PreflightFinding:
    """One construction pre-flight result.

    ``code`` is stable and maps to ``diagnostic.<code>`` translations in the UI
    and reports.  ``message`` is the English fallback.  ``values`` carries the
    named placeholders used by a translation template.
    """

    code: str
    category: PreflightCategory
    severity: Severity
    message: str
    field: str | None = None
    subject: str | None = None
    action: PreflightAction = PreflightAction.NONE
    values: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("pre-flight finding code must not be empty")
        if not self.message.strip():
            raise ValueError("pre-flight finding message must not be empty")
        values = tuple((str(key), str(value)) for key, value in self.values)
        object.__setattr__(self, "values", values)

    def translation_values(self) -> dict[str, str]:
        return dict(self.values)


@dataclass(frozen=True, slots=True)
class PreflightReport:
    """An immutable collection of pre-flight findings."""

    findings: tuple[PreflightFinding, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "findings", tuple(self.findings))

    @property
    def errors(self) -> tuple[PreflightFinding, ...]:
        return tuple(finding for finding in self.findings if finding.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[PreflightFinding, ...]:
        return tuple(finding for finding in self.findings if finding.severity is Severity.WARNING)

    @property
    def infos(self) -> tuple[PreflightFinding, ...]:
        return tuple(finding for finding in self.findings if finding.severity is Severity.INFO)

    @property
    def ready(self) -> bool:
        return not self.errors

    @property
    def status(self) -> PreflightStatus:
        if self.errors:
            return PreflightStatus.ERROR
        if self.warnings:
            return PreflightStatus.WARNING
        return PreflightStatus.READY

    def sorted_findings(self) -> tuple[PreflightFinding, ...]:
        severity_order = {
            Severity.ERROR: 0,
            Severity.WARNING: 1,
            Severity.INFO: 2,
        }
        category_order = {
            PreflightCategory.GEOMETRY: 0,
            PreflightCategory.FEED: 1,
            PreflightCategory.SEGMENTATION: 2,
            PreflightCategory.SUPPORTS: 3,
            PreflightCategory.SOLVER: 4,
            PreflightCategory.SIMULATION: 5,
            PreflightCategory.CONSTRUCTION: 6,
        }
        return tuple(
            sorted(
                self.findings,
                key=lambda finding: (
                    severity_order[finding.severity],
                    category_order[finding.category],
                    finding.code,
                    finding.subject or "",
                ),
            )
        )


def _category_for_diagnostic(code: str) -> PreflightCategory:
    if code.startswith(("antenna.feed", "antenna.load", "antenna.source")):
        return PreflightCategory.FEED
    if code.startswith("antenna.transmission_line"):
        return PreflightCategory.FEED
    if code.startswith("segmentation."):
        return PreflightCategory.SEGMENTATION
    if code.startswith("geometry."):
        return PreflightCategory.GEOMETRY
    if code.startswith("solver."):
        return PreflightCategory.SOLVER
    if code.startswith("far_field."):
        return PreflightCategory.SIMULATION
    return PreflightCategory.GEOMETRY


def _action_for_diagnostic(code: str) -> PreflightAction:
    if code.startswith("antenna.feed"):
        return PreflightAction.EDIT_FEED
    if code.startswith("antenna.load"):
        return PreflightAction.EDIT_LOADS
    if code.startswith("antenna.transmission_line"):
        return PreflightAction.EDIT_LINES
    if code.startswith("antenna.source"):
        return PreflightAction.EDIT_FEED
    if code.startswith("segmentation.feed_offset"):
        return PreflightAction.EDIT_FEED
    if code.startswith("segmentation.transmission_line_offset"):
        return PreflightAction.EDIT_LINES
    if code.startswith("segmentation."):
        return PreflightAction.EDIT_SEGMENTATION
    if code.startswith("geometry.below_ground"):
        return PreflightAction.EDIT_GEOMETRY
    if code.startswith("geometry.ground_mounted_wires"):
        return PreflightAction.EDIT_GEOMETRY
    return PreflightAction.NONE


def diagnostic_finding(
    diagnostic: Diagnostic,
    *,
    category: PreflightCategory | None = None,
    action: PreflightAction | None = None,
) -> PreflightFinding:
    """Convert a diagnostic into a pre-flight finding."""

    return PreflightFinding(
        code=diagnostic.code,
        category=category or _category_for_diagnostic(diagnostic.code),
        severity=diagnostic.severity,
        message=diagnostic.message,
        field=diagnostic.field,
        subject=diagnostic.field,
        action=action or _action_for_diagnostic(diagnostic.code),
    )


def _model_extent_m(model: AntennaModel) -> tuple[float, float]:
    """Return ``(top_height, largest_horizontal_span)`` in metres."""

    points = tuple(point for wire in model.wires for point in (wire.start, wire.end))
    top_height = max(point.z_m for point in points)
    x_span = max(point.x_m for point in points) - min(point.x_m for point in points)
    y_span = max(point.y_m for point in points) - min(point.y_m for point in points)
    return top_height, max(x_span, y_span)


def _geometry_findings(model: AntennaModel) -> tuple[PreflightFinding, ...]:
    findings: list[PreflightFinding] = []

    for wire in model.wires:
        if wire.length_m < 0.01:
            findings.append(
                PreflightFinding(
                    code="geometry.wire_too_short",
                    category=PreflightCategory.GEOMETRY,
                    severity=Severity.WARNING,
                    message=f"wire {wire.id} is shorter than 1 cm",
                    field="wires",
                    subject=wire.id,
                    action=PreflightAction.EDIT_GEOMETRY,
                    values=(("wire", wire.id),),
                )
            )

    for issue in wire_pair_issues(tuple(model.wires)):
        if issue.kind == "overlap":
            findings.append(
                PreflightFinding(
                    code="geometry.wire_overlap",
                    category=PreflightCategory.GEOMETRY,
                    severity=Severity.WARNING,
                    message=f"wires {issue.first_id} and {issue.second_id} overlap",
                    field="wires",
                    subject=f"{issue.first_id} / {issue.second_id}",
                    action=PreflightAction.EDIT_GEOMETRY,
                    values=(("first", issue.first_id), ("second", issue.second_id)),
                )
            )
        else:
            findings.append(
                PreflightFinding(
                    code="geometry.wire_crossing",
                    category=PreflightCategory.GEOMETRY,
                    severity=Severity.WARNING,
                    message=f"wires {issue.first_id} and {issue.second_id} cross",
                    field="wires",
                    subject=f"{issue.first_id} / {issue.second_id}",
                    action=PreflightAction.EDIT_GEOMETRY,
                    values=(("first", issue.first_id), ("second", issue.second_id)),
                )
            )

    if model.environment.ground.kind is GroundKind.FREE_SPACE:
        findings.append(
            PreflightFinding(
                code="geometry.free_space",
                category=PreflightCategory.GEOMETRY,
                severity=Severity.INFO,
                message=(
                    "the model uses free space; confirm that this matches the installed antenna"
                ),
                field="environment.ground",
                subject="ground",
                action=PreflightAction.EDIT_GEOMETRY,
            )
        )

    return tuple(findings)


def _support_findings(project: Project, model: AntennaModel) -> tuple[PreflightFinding, ...]:
    findings: list[PreflightFinding] = []
    profile = project.active_installation_profile
    top_height, span = _model_extent_m(model)

    if profile is None:
        findings.append(
            PreflightFinding(
                code="supports.no_profile",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.WARNING,
                message=(
                    "no active installation profile; available height, width, "
                    "and support type have not been checked"
                ),
                field="installation_profiles",
                subject="site",
                action=PreflightAction.EDIT_SUPPORTS,
            )
        )
        return tuple(findings)

    if profile.available_height_m is None:
        findings.append(
            PreflightFinding(
                code="supports.height_unknown",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.WARNING,
                message=(
                    "the installation profile does not specify an available height; "
                    f"confirm that the {top_height:.3f} m top height fits"
                ),
                field="installation_profile.available_height_m",
                subject=profile.name,
                action=PreflightAction.EDIT_SUPPORTS,
                values=(("top", f"{top_height:.3f}"),),
            )
        )
    elif top_height > profile.available_height_m + 1e-9:
        findings.append(
            PreflightFinding(
                code="supports.height_exceeded",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.ERROR,
                message=(
                    f"the design top height {top_height:.3f} m exceeds the "
                    f"profile's available height {profile.available_height_m:.3f} m"
                ),
                field="installation_profile.available_height_m",
                subject=profile.name,
                action=PreflightAction.EDIT_SUPPORTS,
                values=(
                    ("top", f"{top_height:.3f}"),
                    ("available", f"{profile.available_height_m:.3f}"),
                ),
            )
        )

    if profile.available_width_m is None:
        findings.append(
            PreflightFinding(
                code="supports.width_unknown",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.WARNING,
                message=(
                    "the installation profile does not specify available width; "
                    f"confirm that the {span:.3f} m horizontal span fits"
                ),
                field="installation_profile.available_width_m",
                subject=profile.name,
                action=PreflightAction.EDIT_SUPPORTS,
                values=(("span", f"{span:.3f}"),),
            )
        )
    elif span > profile.available_width_m + 1e-9:
        findings.append(
            PreflightFinding(
                code="supports.width_exceeded",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.ERROR,
                message=(
                    f"the design horizontal span {span:.3f} m exceeds the "
                    f"profile's available width {profile.available_width_m:.3f} m"
                ),
                field="installation_profile.available_width_m",
                subject=profile.name,
                action=PreflightAction.EDIT_SUPPORTS,
                values=(
                    ("span", f"{span:.3f}"),
                    ("available", f"{profile.available_width_m:.3f}"),
                ),
            )
        )

    if profile.ground is not None and profile.ground != model.environment.ground:
        findings.append(
            PreflightFinding(
                code="supports.ground_mismatch",
                category=PreflightCategory.SUPPORTS,
                severity=Severity.WARNING,
                message=(
                    "the model ground differs from the installation profile's "
                    "recommended ground; confirm the model matches the site"
                ),
                field="environment.ground",
                subject=profile.name,
                action=PreflightAction.EDIT_SUPPORTS,
            )
        )

    return tuple(findings)


def _construction_findings(project: Project) -> tuple[PreflightFinding, ...]:
    record = project.construction_record
    if record is None:
        return (
            PreflightFinding(
                code="construction.record_missing",
                category=PreflightCategory.CONSTRUCTION,
                severity=Severity.WARNING,
                message=(
                    "no as-built record or checklist has been started; start one "
                    "before construction"
                ),
                field="construction_record",
                subject="project",
                action=PreflightAction.EDIT_CONSTRUCTION,
            ),
        )

    findings: list[PreflightFinding] = []
    if not record.dimensions:
        findings.append(
            PreflightFinding(
                code="construction.dimensions_missing",
                category=PreflightCategory.CONSTRUCTION,
                severity=Severity.INFO,
                message="the as-built record has no measured dimensions yet",
                field="construction_record.dimensions",
                subject="project",
                action=PreflightAction.EDIT_CONSTRUCTION,
            )
        )
    checked = record.checked_keys()
    if len(checked) < len(CONSTRUCTION_CHECKLIST_KEYS):
        findings.append(
            PreflightFinding(
                code="construction.checklist_incomplete",
                category=PreflightCategory.CONSTRUCTION,
                severity=Severity.INFO,
                message="the construction checklist is not complete",
                field="construction_record.checklist",
                subject="project",
                action=PreflightAction.EDIT_CONSTRUCTION,
                values=(
                    ("checked", str(len(checked))),
                    ("total", str(len(CONSTRUCTION_CHECKLIST_KEYS))),
                ),
            )
        )
    return tuple(findings)


_END_FEED_IS_EXPECTED = (
    BeverageParameters,
    EndFedParameters,
    FanDipoleParameters,
    InvertedLParameters,
    InvertedVParameters,
    PhasedVerticalParameters,
    RingoParameters,
    ScvParameters,
    VerticalParameters,
)


def run_model_preflight(
    project: Project,
    design: DesignVariant,
) -> tuple[PreflightFinding, ...]:
    """Run the checks that do not need a simulation specification."""

    model = design.antenna
    end_feed_is_expected = isinstance(design.parameters, _END_FEED_IS_EXPECTED)
    findings: list[PreflightFinding] = [
        diagnostic_finding(diagnostic)
        for diagnostic in model.validate()
        if not (end_feed_is_expected and diagnostic.code == "antenna.feed.at_wire_end")
    ]
    findings.extend(_geometry_findings(model))
    findings.extend(_support_findings(project, model))
    findings.extend(_construction_findings(project))
    return tuple(findings)
