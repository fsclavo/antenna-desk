# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction pre-flight orchestration for a concrete simulation spec."""

from __future__ import annotations

from ..domain.antennas.antenna import AntennaModel
from ..domain.common.validation import Diagnostic, Severity
from ..domain.design.preflight import (
    PreflightAction,
    PreflightCategory,
    PreflightFinding,
    PreflightReport,
    diagnostic_finding,
    run_model_preflight,
)
from ..domain.projects.project import DesignVariant, Project
from ..domain.simulation.result import SimulationResult, SimulationStatus
from ..domain.simulation.spec import SimulationSpec
from .assumptions import validate_nec2_assumptions
from .discretization import validate_segmentation
from .fingerprint import model_fingerprint

_RESULT_PROBLEM_CODES = frozenset(
    {
        "normalization.negative_resistance",
        "normalization.impedance_missing",
        "normalization.feed_segment_missing",
    }
)


def _segmentation_findings(
    model: AntennaModel,
    spec: SimulationSpec,
) -> tuple[PreflightFinding, ...]:
    try:
        diagnostics = validate_segmentation(model, spec)
    except (KeyError, ValueError) as exc:
        return (
            PreflightFinding(
                code="segmentation.invalid",
                category=PreflightCategory.SEGMENTATION,
                severity=Severity.ERROR,
                message=f"segmentation could not be evaluated: {exc}",
                field="segmentation",
                subject="segmentation",
                action=PreflightAction.EDIT_SEGMENTATION,
            ),
        )
    return tuple(diagnostic_finding(diagnostic) for diagnostic in diagnostics)


def _assumption_findings(
    model: AntennaModel,
    spec: SimulationSpec,
) -> tuple[PreflightFinding, ...]:
    diagnostics = validate_nec2_assumptions(model, spec)
    return tuple(diagnostic_finding(diagnostic) for diagnostic in diagnostics)


def _latest_result(
    project: Project,
    design: DesignVariant,
) -> SimulationResult | None:
    run = project.latest_simulation_run(design.id)
    if run is not None:
        return run.result
    analysis = project.latest_band_analysis(design.id)
    if analysis is not None and analysis.bands:
        return analysis.bands[0].result
    return None


def _finding_from_result_diagnostic(diagnostic: Diagnostic) -> PreflightFinding:
    return PreflightFinding(
        code=diagnostic.code,
        category=PreflightCategory.SIMULATION,
        severity=diagnostic.severity,
        message=diagnostic.message,
        field=diagnostic.field,
        subject="result",
        action=PreflightAction.RUN_SIMULATION,
    )


def _simulation_findings(
    design: DesignVariant,
    result: SimulationResult | None,
) -> tuple[PreflightFinding, ...]:
    if result is None:
        return (
            PreflightFinding(
                code="simulation.missing",
                category=PreflightCategory.SIMULATION,
                severity=Severity.WARNING,
                message=(
                    "no simulation result is stored for this design; electrical "
                    "performance is unverified"
                ),
                field="simulation_runs",
                subject="result",
                action=PreflightAction.RUN_SIMULATION,
            ),
        )

    findings: list[PreflightFinding] = []
    problems = tuple(
        diagnostic for diagnostic in result.diagnostics if diagnostic.code in _RESULT_PROBLEM_CODES
    )
    findings.extend(_finding_from_result_diagnostic(problem) for problem in problems)

    problem_has_error = any(problem.severity is Severity.ERROR for problem in problems)
    if result.status is SimulationStatus.ERROR and not problem_has_error:
        findings.append(
            PreflightFinding(
                code="simulation.failed",
                category=PreflightCategory.SIMULATION,
                severity=Severity.ERROR,
                message="the latest simulation finished with an error",
                field="simulation_runs",
                subject="result",
                action=PreflightAction.RUN_SIMULATION,
            )
        )
    elif result.status is SimulationStatus.CANCELLED:
        findings.append(
            PreflightFinding(
                code="simulation.cancelled",
                category=PreflightCategory.SIMULATION,
                severity=Severity.WARNING,
                message="the latest simulation was cancelled",
                field="simulation_runs",
                subject="result",
                action=PreflightAction.RUN_SIMULATION,
            )
        )
    elif result.status is SimulationStatus.PARTIAL and not problems:
        findings.append(
            PreflightFinding(
                code="simulation.partial",
                category=PreflightCategory.SIMULATION,
                severity=Severity.WARNING,
                message="the latest simulation finished only partially",
                field="simulation_runs",
                subject="result",
                action=PreflightAction.RUN_SIMULATION,
            )
        )

    if result.model_fingerprint:
        expected = model_fingerprint(design.antenna, result.spec)
        if result.model_fingerprint != expected:
            findings.append(
                PreflightFinding(
                    code="simulation.stale",
                    category=PreflightCategory.SIMULATION,
                    severity=Severity.WARNING,
                    message=(
                        "the latest simulation used a different antenna model; "
                        "re-run it before building"
                    ),
                    field="simulation_runs",
                    subject="result",
                    action=PreflightAction.RUN_SIMULATION,
                )
            )

    return tuple(findings)


def run_preflight(
    project: Project,
    design: DesignVariant,
    spec: SimulationSpec,
    *,
    result: SimulationResult | None = None,
) -> PreflightReport:
    """Return the construction pre-flight report for one design.

    ``result`` should be the result the UI currently shows for the design; when
    omitted, the latest persisted single-band or band-analysis result is used.
    """

    findings = list(run_model_preflight(project, design))
    findings.extend(_segmentation_findings(design.antenna, spec))
    findings.extend(_assumption_findings(design.antenna, spec))
    findings.extend(_simulation_findings(design, result or _latest_result(project, design)))
    return PreflightReport(tuple(findings))
