# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run a segmentation-density ladder through the solver port."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from math import isfinite

from ...domain.antennas.antenna import AntennaModel
from ...domain.common.validation import Severity
from ...domain.simulation.convergence import (
    DEFAULT_CONVERGENCE_THRESHOLDS,
    ConvergencePoint,
    ConvergenceResult,
    ConvergenceThresholds,
    ConvergenceWireMetric,
)
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.pattern import max_power_gain_db, takeoff_angle_deg
from ...domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from ...domain.simulation.segmentation import SegmentationPolicy
from ...domain.simulation.spec import SimulationSpec
from ...simulation.discretization import (
    SegmentLayout,
    build_segment_layout,
    resolve_model_quality,
    validate_segmentation,
)
from ..ports.antenna_solver import AntennaSolver
from ..ports.cancellation import CancelToken
from .run_simulation import RunSimulation, RunSimulationCommand

DEFAULT_CONVERGENCE_DENSITIES = (0.10, 0.05, 0.025, 0.0125)
MIN_SEGMENTS_PER_WIRE = 3


@dataclass(frozen=True, slots=True)
class RunConvergenceStudyCommand:
    model: AntennaModel
    base_spec: SimulationSpec
    densities: tuple[float, ...] = DEFAULT_CONVERGENCE_DENSITIES
    thresholds: ConvergenceThresholds = DEFAULT_CONVERGENCE_THRESHOLDS
    frequency_hz: float | None = None
    cancel_token: CancelToken | None = None
    progress: Callable[[int, int], None] | None = None

    def __post_init__(self) -> None:
        densities = tuple(sorted({float(value) for value in self.densities}, reverse=True))
        if len(densities) < 3:
            raise ValueError("a convergence study needs at least three densities")
        if len(densities) > 5:
            raise ValueError("a convergence study accepts at most five densities")
        if any(not isfinite(value) or value <= 0.0 for value in densities):
            raise ValueError("densities must be positive and finite")
        object.__setattr__(self, "densities", densities)
        if self.frequency_hz is not None and self.frequency_hz <= 0.0:
            raise ValueError("frequency_hz must be positive")


@dataclass(frozen=True, slots=True)
class RunConvergenceStudy:
    solver: AntennaSolver

    def execute(self, command: RunConvergenceStudyCommand) -> ConvergenceResult:
        frequency_hz = command.frequency_hz or command.model.design_frequency_hz
        points: list[ConvergencePoint] = []
        cancelled = False
        base_segmentation = command.base_spec.segmentation
        capabilities = self._capabilities()
        total = len(command.densities)
        for index, density in enumerate(command.densities):
            if command.cancel_token is not None and command.cancel_token.is_cancelled():
                cancelled = True
                break
            with_pattern = index in {0, total - 1}
            spec = replace(
                command.base_spec,
                frequency_plan=FrequencyPlan.single(frequency_hz),
                segmentation=SegmentationPolicy(
                    target_segment_length_wavelengths=density,
                    min_segments_per_wire=max(
                        MIN_SEGMENTS_PER_WIRE,
                        base_segmentation.min_segments_per_wire,
                    ),
                    max_segments_per_wire=base_segmentation.max_segments_per_wire,
                ),
                far_field=(
                    self._pattern_request(command.base_spec.far_field)
                    if with_pattern
                    else FarFieldRequest(enabled=False)
                ),
            )
            quality = resolve_model_quality(
                command.model,
                spec,
                supports_extended_kernel=capabilities,
            )
            spec = quality.spec
            layout = build_segment_layout(command.model, spec)
            diagnostics = validate_segmentation(command.model, spec)
            diagnostic_text = tuple(
                f"{diagnostic.code}: {diagnostic.message}" for diagnostic in diagnostics
            )
            try:
                result = RunSimulation(self.solver).execute(
                    RunSimulationCommand(
                        model=command.model,
                        spec=spec,
                        cancel_token=command.cancel_token,
                    )
                )
            except Exception as exc:
                return ConvergenceResult(
                    points=tuple(points),
                    thresholds=command.thresholds,
                    cancelled=cancelled,
                    error=str(exc),
                )
            if result.status is SimulationStatus.CANCELLED:
                cancelled = True
                break
            if result.status is not SimulationStatus.COMPLETED or not result.frequencies:
                message = self._result_error(result)
                points.append(
                    self._invalid_point(
                        density,
                        layout,
                        diagnostic_text,
                        message,
                    )
                )
            else:
                points.append(
                    self._point(
                        density,
                        layout,
                        result.frequencies[0],
                        diagnostic_text,
                    )
                )
            if command.progress is not None:
                command.progress(index + 1, total)
        return ConvergenceResult(
            points=tuple(points),
            thresholds=command.thresholds,
            cancelled=cancelled,
        )

    def _capabilities(self) -> bool:
        try:
            return bool(self.solver.capabilities().supports_extended_thin_wire_kernel)
        except Exception:
            return False

    @staticmethod
    def _pattern_request(base: FarFieldRequest) -> FarFieldRequest:
        if base.enabled:
            return base
        return FarFieldRequest()

    @staticmethod
    def _result_error(result: SimulationResult) -> str:
        for diagnostic in result.diagnostics:
            if diagnostic.severity is Severity.ERROR:
                return diagnostic.message
        for diagnostic in result.diagnostics:
            return diagnostic.message
        return result.status.value

    @staticmethod
    def _wire_metrics(layout: SegmentLayout) -> tuple[ConvergenceWireMetric, ...]:
        return tuple(
            ConvergenceWireMetric(
                wire_id=segmentation.wire.id,
                segments=segmentation.segments,
                segment_length_m=segmentation.segment_length_m,
                radius_m=segmentation.wire.radius_m,
            )
            for segmentation in layout.wires
        )

    def _point(
        self,
        density: float,
        layout: SegmentLayout,
        frequency: FrequencyResult,
        diagnostics: tuple[str, ...],
    ) -> ConvergencePoint:
        gain = max_power_gain_db(frequency.far_field)
        peak = max(
            (point for point in frequency.far_field if point.gain_total_db is not None),
            key=lambda point: point.gain_total_db or float("-inf"),
            default=None,
        )
        takeoff = takeoff_angle_deg(peak.theta_deg) if peak is not None else None
        impedance = frequency.impedance_ohm
        return ConvergencePoint(
            density_wavelengths=density,
            total_segments=sum(segmentation.segments for segmentation in layout.wires),
            resistance_ohm=impedance.real,
            reactance_ohm=impedance.imag,
            impedance_magnitude_ohm=abs(impedance),
            swr=float(frequency.swr),
            wire_metrics=self._wire_metrics(layout),
            max_gain_db=gain,
            takeoff_deg=takeoff,
            diagnostics=diagnostics,
        )

    def _invalid_point(
        self,
        density: float,
        layout: SegmentLayout,
        diagnostics: tuple[str, ...],
        error: str,
    ) -> ConvergencePoint:
        return ConvergencePoint(
            density_wavelengths=density,
            total_segments=sum(segmentation.segments for segmentation in layout.wires),
            resistance_ohm=float("nan"),
            reactance_ohm=float("nan"),
            impedance_magnitude_ohm=float("nan"),
            swr=float("nan"),
            wire_metrics=self._wire_metrics(layout),
            diagnostics=diagnostics,
            error=error,
        )
