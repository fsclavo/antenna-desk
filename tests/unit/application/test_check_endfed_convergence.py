# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.application.use_cases.check_endfed_convergence import (
    CheckEndFedConvergence,
    CheckEndFedConvergenceCommand,
    EndFedConvergencePoint,
    EndFedConvergenceResult,
)
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.common.validation import Diagnostic, Severity
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationResult, SimulationStatus
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


def _parameters() -> EndFedParameters:
    return EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_section_length_m=0.5,
        installation_return_length_m=0.1,
    )


def _spec() -> SimulationSpec:
    return SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))


def test_convergence_result_reports_a_stable_set() -> None:
    result = EndFedConvergenceResult(
        points=(
            EndFedConvergencePoint(10, complex(65.9, -15.4), 1.47),
            EndFedConvergencePoint(21, complex(66.7, -16.1), 1.49),
            EndFedConvergencePoint(51, complex(67.0, -16.4), 1.50),
        )
    )

    assert result.completed
    assert result.converged
    assert result.swr_spread == pytest.approx(0.03)
    assert result.resistance_spread_fraction == pytest.approx(0.01653, abs=1e-4)


def test_convergence_result_flags_a_segmentation_dependent_set() -> None:
    result = EndFedConvergenceResult(
        points=(
            EndFedConvergencePoint(10, complex(48.5, -21.7), 1.55),
            EndFedConvergencePoint(21, complex(86.4, -110.7), 4.94),
            EndFedConvergencePoint(51, complex(83.9, -298.9), 23.5),
        )
    )

    assert result.completed
    assert not result.converged


def test_convergence_command_validates_the_segment_counts() -> None:
    with pytest.raises(ValueError, match="two distinct"):
        CheckEndFedConvergenceCommand(_parameters(), _spec(), segment_counts=(10,))
    with pytest.raises(ValueError, match="at least 3"):
        CheckEndFedConvergenceCommand(_parameters(), _spec(), segment_counts=(2, 10))
    with pytest.raises(ValueError, match="frequency_hz"):
        CheckEndFedConvergenceCommand(_parameters(), _spec(), frequency_hz=0.0)


def test_convergence_reports_the_error_diagnostic_not_a_warning() -> None:
    from unittest.mock import Mock

    solver = Mock()
    solver.validate.return_value = ()
    solver.run.return_value = SimulationResult(
        status=SimulationStatus.ERROR,
        spec=_spec(),
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="fake", version="1.0"),
        frequencies=(),
        diagnostics=(
            Diagnostic(
                code="segmentation.feed_offset",
                severity=Severity.WARNING,
                message="warning first",
            ),
            Diagnostic(
                code="normalization.negative_resistance",
                severity=Severity.ERROR,
                message="real error",
            ),
        ),
    )

    result = CheckEndFedConvergence(solver).execute(
        CheckEndFedConvergenceCommand(_parameters(), _spec())
    )

    assert not result.completed
    assert result.error == "real error"


def test_radiator_segment_counts_keep_the_coil_node_and_total_count() -> None:
    from antennadesk.application.use_cases.check_endfed_convergence import (
        radiator_segment_counts,
    )
    from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters

    parameters = shortened_efhw_80_10_parameters()

    for total in (10, 21, 51):
        counts = radiator_segment_counts(parameters, total)
        assert counts is not None
        lower, upper = counts
        assert lower >= 3
        assert upper >= 3
        assert lower + upper == total


def test_impedance_only_result_ignores_a_large_swr_spread() -> None:
    result = EndFedConvergenceResult(
        points=(
            EndFedConvergencePoint(10, complex(0.20, -8.0), 205.0),
            EndFedConvergencePoint(21, complex(0.20, -9.0), 232.0),
            EndFedConvergencePoint(51, complex(0.20, -12.0), 300.0),
        ),
        swr_informational=True,
    )

    assert result.converged
    assert result.resistance_spread_ohm == pytest.approx(0.0)
    assert result.reactance_spread_ohm == pytest.approx(4.0)


def test_impedance_only_result_flags_a_resistance_spread() -> None:
    result = EndFedConvergenceResult(
        points=(
            EndFedConvergencePoint(10, complex(0.20, -8.0), 205.0),
            EndFedConvergencePoint(21, complex(2.20, -9.0), 232.0),
            EndFedConvergencePoint(51, complex(1.20, -12.0), 300.0),
        ),
        swr_informational=True,
    )

    assert not result.converged
    assert result.resistance_spread_ohm == pytest.approx(2.0)


def test_standard_result_still_requires_the_swr_spread() -> None:
    result = EndFedConvergenceResult(
        points=(
            EndFedConvergencePoint(10, complex(50.0, -1.0), 1.0),
            EndFedConvergencePoint(21, complex(50.0, -1.0), 2.0),
            EndFedConvergencePoint(51, complex(50.0, -1.0), 1.5),
        )
    )

    assert not result.converged
    assert result.swr_spread == pytest.approx(1.0)
