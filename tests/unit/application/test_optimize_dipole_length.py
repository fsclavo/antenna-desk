# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.application.use_cases.optimize_dipole_length import (
    OptimizeDipoleLength,
    OptimizeDipoleLengthCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.length import (
    LengthOptimizationSpec,
    LengthOptimizationStatus,
)
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class AnalyticalDipoleSolver:
    def __init__(self, resonance_length_m: float = 20.3) -> None:
        self.resonance_length_m = resonance_length_m
        self.specs: list[SimulationSpec] = []
        self.lengths: list[float] = []

    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="analytical",
            supports_frequency_sweep=True,
            supports_currents=True,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(
        self,
        model: object,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="analytical", version="1.0")

    def run(
        self,
        model: object,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        from antennadesk.domain.antennas.antenna import AntennaModel

        assert isinstance(model, AntennaModel)
        length = model.wires[0].length_m
        self.lengths.append(length)
        self.specs.append(spec)
        reactance = 5.0 * (length - self.resonance_length_m)
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=model.design_frequency_hz,
                    feed_tag=1,
                    feed_segment=11,
                    impedance_ohm=complex(70.0, reactance),
                    swr=2.0,
                    input_power_w=0.001,
                ),
            ),
            duration_s=0.0,
        )


def test_optimizes_length_and_computes_sensitivity() -> None:
    solver = AnalyticalDipoleSolver()
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    base_spec = SimulationSpec(
        frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_300_000.0, 21),
        far_field=FarFieldRequest(enabled=True),
    )
    result = OptimizeDipoleLength(solver).execute(
        OptimizeDipoleLengthCommand(
            parameters=parameters,
            base_spec=base_spec,
            optimization_spec=LengthOptimizationSpec(
                min_length_m=18.0,
                max_length_m=22.0,
                max_evaluations=12,
                reactance_tolerance_ohm=0.05,
            ),
        )
    )

    assert result.status is LengthOptimizationStatus.CONVERGED
    assert result.best_length_m == pytest.approx(20.3, abs=0.01)
    assert result.best_impedance_ohm is not None
    assert result.best_impedance_ohm.imag == pytest.approx(0.0, abs=0.05)
    assert len(result.sensitivity) == 4
    assert all(spec.frequency_plan.is_single for spec in solver.specs)
    assert all(spec.far_field.enabled is False for spec in solver.specs)
    assert min(solver.lengths) == pytest.approx(18.0)
    assert max(solver.lengths) == pytest.approx(22.0)


def test_optimizes_a_folded_dipole_element_length() -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    solver = AnalyticalDipoleSolver()
    parameters = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
    )
    result = OptimizeDipoleLength(solver).execute(
        OptimizeDipoleLengthCommand(
            parameters=parameters,
            base_spec=SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
            optimization_spec=LengthOptimizationSpec(
                min_length_m=18.0,
                max_length_m=22.0,
                max_evaluations=12,
            ),
        )
    )

    assert result.status is LengthOptimizationStatus.CONVERGED
    assert result.best_length_m == pytest.approx(20.3, abs=0.01)


def test_optimizes_a_loop_circumference() -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    solver = AnalyticalDipoleSolver(resonance_length_m=10.3)
    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
    )
    result = OptimizeDipoleLength(solver).execute(
        OptimizeDipoleLengthCommand(
            parameters=parameters,
            base_spec=SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
            optimization_spec=LengthOptimizationSpec(
                min_length_m=36.0,
                max_length_m=44.0,
                max_evaluations=12,
            ),
        )
    )

    assert result.status is LengthOptimizationStatus.CONVERGED
    assert result.best_length_m == pytest.approx(41.2, abs=0.02)
    assert max(solver.lengths) == pytest.approx(11.0)


class BandwidthSolver:
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="bandwidth",
            supports_frequency_sweep=True,
            supports_currents=True,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(self, model: object, spec: SimulationSpec) -> tuple[Diagnostic, ...]:
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="bandwidth", version="1.0")

    def run(
        self,
        model: object,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        from antennadesk.domain.antennas.antenna import AntennaModel

        assert isinstance(model, AntennaModel)
        length = model.wires[0].length_m
        half_width = max(0.0, 200_000.0 - abs(length - 20.3) * 100_000.0)
        frequencies = tuple(
            FrequencyResult(
                frequency_hz=frequency_hz,
                feed_tag=1,
                feed_segment=11,
                impedance_ohm=complex(50.0, 0.0),
                swr=1.5 if abs(frequency_hz - 7_100_000.0) <= half_width else 3.0,
                input_power_w=0.001,
            )
            for frequency_hz in spec.frequency_plan.frequencies_hz
        )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=frequencies,
        )


def test_optimizes_for_maximum_swr_bandwidth() -> None:
    from antennadesk.domain.optimization.length import OptimizationObjective

    solver = BandwidthSolver()
    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    )
    result = OptimizeDipoleLength(solver).execute(
        OptimizeDipoleLengthCommand(
            parameters=parameters,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.sweep(6_800_000.0, 7_400_000.0, 13)
            ),
            optimization_spec=LengthOptimizationSpec(
                min_length_m=18.0,
                max_length_m=22.0,
                objective=OptimizationObjective.MAX_BANDWIDTH,
                swr_limit=2.0,
                max_evaluations=40,
                length_tolerance_m=0.02,
            ),
        )
    )

    assert result.status is LengthOptimizationStatus.CONVERGED
    assert result.best_length_m is not None
    assert 19.5 <= result.best_length_m <= 21.0
    assert result.best_bandwidth_hz is not None
    assert result.best_bandwidth_hz > 250_000.0
    assert solver is not None
