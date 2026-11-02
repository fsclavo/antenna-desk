# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace

import pytest

from antennadesk.application.use_cases.optimize_yagi_elements import (
    OptimizeYagiElements,
    OptimizeYagiElementsCommand,
    YagiOptimizationObjective,
    resize_yagi,
)
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.common.units import wavelength_m
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.design.yagi_reference import dl6wu_elements
from antennadesk.domain.optimization.multi_variable import BoundedStatus, BoundedVariable
from antennadesk.domain.optimization.synthesis import SynthesisTarget
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec


class AnalyticalYagiSolver:
    def __init__(self) -> None:
        self.specs: list[SimulationSpec] = []

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

    def validate(self, model: AntennaModel, spec: SimulationSpec) -> tuple[Diagnostic, ...]:
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="analytical", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        self.specs.append(spec)
        reflector, driven = model.wires[0].length_m, model.wires[1].length_m
        impedance = complex(50.0 + 10.0 * (reflector - 10.5), 10.0 * (driven - 10.0))
        deviation = abs(reflector - 10.5)
        forward = 8.0 - deviation
        rear = -12.0 + deviation
        far_field = tuple(
            FarFieldPoint(
                theta_deg=90.0,
                phi_deg=phi,
                gain_vertical_db=gain,
                gain_horizontal_db=None,
                gain_total_db=gain,
                axial_ratio=None,
                tilt_deg=None,
                polarization="LINEAR",
                e_theta_magnitude_v_per_m=None,
                e_theta_phase_deg=None,
                e_phi_magnitude_v_per_m=None,
                e_phi_phase_deg=None,
            )
            for phi, gain in ((0.0, forward), (180.0, rear))
        )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=model.design_frequency_hz,
                    feed_tag=2,
                    feed_segment=1,
                    impedance_ohm=impedance,
                    swr=1.0,
                    input_power_w=0.001,
                    far_field=far_field,
                ),
            ),
        )


def _yagi(count: int, driven_index: int = 1) -> YagiParameters:
    wavelength = wavelength_m(14_100_000.0)
    return YagiParameters(
        frequency_hz=14_100_000.0,
        elements=tuple(
            YagiElement(
                position_m=index * 0.2 * wavelength,
                length_m=(0.48 - 0.01 * index) * wavelength,
                radius_m=0.002,
            )
            for index in range(count)
        ),
        height_m=12.0,
        driven_index=driven_index,
    )


def test_resize_yagi_adds_reference_directors() -> None:
    base = _yagi(3)
    resized = resize_yagi(base, 6)

    assert len(resized.elements) == 6
    assert resized.driven_index == base.driven_index
    assert resized.elements[:3] == base.elements
    reference = dl6wu_elements(6)
    wavelength = wavelength_m(base.frequency_hz)
    for index in range(3, 6):
        assert resized.elements[index].length_m == pytest.approx(reference[index][0] * wavelength)
        assert resized.elements[index].position_m > resized.elements[index - 1].position_m


def test_resize_yagi_removes_trailing_elements() -> None:
    base = _yagi(5)
    resized = resize_yagi(base, 3)

    assert len(resized.elements) == 3
    assert resized.elements == base.elements[:3]


def test_resize_yagi_keeps_the_driven_element() -> None:
    base = _yagi(5, driven_index=2)

    assert len(resize_yagi(base, 3).elements) == 3
    with pytest.raises(ValueError, match="at least 3 elements"):
        resize_yagi(base, 2)


def test_resize_yagi_rejects_more_than_the_reference_supports() -> None:
    with pytest.raises(ValueError, match="limited to 32 elements"):
        resize_yagi(_yagi(3), 33)


class CountingYagiSolver(AnalyticalYagiSolver):
    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        result = super().run(
            model,
            spec,
            progress_callback=progress_callback,
            cancel_token=cancel_token,
        )
        count = len(model.wires)
        gain = 8.0 - 0.5 * abs(count - 7)
        frequency = result.frequencies[0]
        far_field = tuple(
            replace(
                point,
                gain_vertical_db=gain,
                gain_total_db=gain,
            )
            for point in frequency.far_field
        )
        return replace(
            result,
            frequencies=(replace(frequency, far_field=far_field),),
        )


def test_optimizes_yagi_element_count() -> None:
    base = _yagi(5)

    def build(values: dict[str, float]) -> YagiParameters:
        return resize_yagi(base, round(values["element_count"]))

    result = OptimizeYagiElements(CountingYagiSolver()).execute(
        OptimizeYagiElementsCommand(
            build_parameters=build,
            variables=(BoundedVariable("element_count", 2, 12, integer=True),),
            start_values={"element_count": 5.0},
            target=SynthesisTarget(14_100_000.0, 50.0, 0.0),
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.single(14_100_000.0),
                far_field=FarFieldRequest(enabled=True),
            ),
            objective=YagiOptimizationObjective.MAX_GAIN,
            max_evaluations=30,
            samples=5,
            passes=4,
        )
    )

    assert result.status is BoundedStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["element_count"] == pytest.approx(7.0)


def test_optimizes_selected_yagi_element_lengths() -> None:
    base = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(0.0, 10.5, 0.002),
            YagiElement(2.0, 10.0, 0.002),
        ),
        height_m=12.0,
        driven_index=1,
    )
    target = SynthesisTarget(14_100_000.0, 50.0, 0.0)

    def build(values: dict[str, float]) -> YagiParameters:
        return YagiParameters(
            frequency_hz=target.frequency_hz,
            elements=(
                YagiElement(0.0, values["reflector_m"], 0.002),
                YagiElement(2.0, values["driven_m"], 0.002),
            ),
            height_m=base.height_m,
            driven_index=1,
        )

    solver = AnalyticalYagiSolver()
    result = OptimizeYagiElements(solver).execute(
        OptimizeYagiElementsCommand(
            build_parameters=build,
            variables=(
                BoundedVariable("reflector_m", 9.5, 11.5),
                BoundedVariable("driven_m", 9.0, 11.0),
            ),
            start_values={"reflector_m": 10.0, "driven_m": 10.0},
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.sweep(13_900_000.0, 14_300_000.0, 21),
                far_field=FarFieldRequest(enabled=True),
            ),
            max_evaluations=60,
            samples=5,
            passes=4,
        )
    )

    assert result.status is BoundedStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["reflector_m"] == pytest.approx(10.5, abs=0.05)
    assert result.best_values["driven_m"] == pytest.approx(10.0, abs=0.05)
    assert result.best_score == pytest.approx(0.0, abs=0.1)
    assert all(spec.frequency_plan.is_single for spec in solver.specs)
    assert all(spec.far_field.enabled is False for spec in solver.specs)


def test_optimizes_yagi_for_gain() -> None:
    base = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(0.0, 10.5, 0.002),
            YagiElement(2.0, 10.0, 0.002),
        ),
        height_m=12.0,
        driven_index=1,
    )
    target = SynthesisTarget(14_100_000.0, 50.0, 0.0)

    def build(values: dict[str, float]) -> YagiParameters:
        return YagiParameters(
            frequency_hz=target.frequency_hz,
            elements=(
                YagiElement(0.0, values["reflector_m"], 0.002),
                YagiElement(2.0, 10.0, 0.002),
            ),
            height_m=base.height_m,
            driven_index=1,
        )

    result = OptimizeYagiElements(AnalyticalYagiSolver()).execute(
        OptimizeYagiElementsCommand(
            build_parameters=build,
            variables=(BoundedVariable("reflector_m", 9.5, 11.5),),
            start_values={"reflector_m": 10.0},
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.single(14_100_000.0),
                far_field=FarFieldRequest(enabled=True, theta_count=3, phi_count=3),
            ),
            objective=YagiOptimizationObjective.MAX_GAIN,
            max_evaluations=20,
            samples=5,
            passes=3,
        )
    )

    assert result.status is BoundedStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["reflector_m"] == pytest.approx(10.5, abs=0.05)
    assert result.best_score == pytest.approx(-8.0, abs=0.1)


def test_optimizes_yagi_for_front_to_back() -> None:
    base = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(0.0, 10.5, 0.002),
            YagiElement(2.0, 10.0, 0.002),
        ),
        height_m=12.0,
        driven_index=1,
    )
    target = SynthesisTarget(14_100_000.0, 50.0, 0.0)

    def build(values: dict[str, float]) -> YagiParameters:
        return YagiParameters(
            frequency_hz=target.frequency_hz,
            elements=(
                YagiElement(0.0, values["reflector_m"], 0.002),
                YagiElement(2.0, 10.0, 0.002),
            ),
            height_m=base.height_m,
            driven_index=1,
        )

    result = OptimizeYagiElements(AnalyticalYagiSolver()).execute(
        OptimizeYagiElementsCommand(
            build_parameters=build,
            variables=(BoundedVariable("reflector_m", 9.5, 11.5),),
            start_values={"reflector_m": 10.0},
            target=target,
            base_spec=SimulationSpec(
                frequency_plan=FrequencyPlan.single(14_100_000.0),
                far_field=FarFieldRequest(enabled=True, theta_count=3, phi_count=3),
            ),
            objective=YagiOptimizationObjective.MAX_FRONT_TO_BACK,
            max_evaluations=20,
            samples=5,
            passes=3,
        )
    )

    assert result.status is BoundedStatus.CONVERGED
    assert result.best_values is not None
    assert result.best_values["reflector_m"] == pytest.approx(10.5, abs=0.05)
    assert result.best_score == pytest.approx(-20.0, abs=0.2)
