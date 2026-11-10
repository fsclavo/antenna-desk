# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Segmentation convergence check for end-fed wires."""

from __future__ import annotations

from dataclasses import dataclass, replace

from ...domain.antennas.endfed import (
    ENDFED_FEED_SECTION_SEGMENTS,
    FEED_SECTION_ID,
    RADIATOR_ID,
    EndFedParameters,
)
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import SimulationStatus
from ...domain.simulation.segmentation import SegmentationPolicy
from ...domain.simulation.spec import SimulationSpec
from ..ports.antenna_solver import AntennaSolver
from .run_simulation import RunSimulation, RunSimulationCommand

DEFAULT_SEGMENT_COUNTS = (10, 21, 51)
MAX_SWR_SPREAD = 0.1
MAX_RESISTANCE_SPREAD_FRACTION = 0.05
MAX_REACTANCE_SPREAD_OHM = 10.0


@dataclass(frozen=True, slots=True)
class EndFedConvergencePoint:
    segments: int
    impedance_ohm: complex
    swr: float


@dataclass(frozen=True, slots=True)
class EndFedConvergenceResult:
    points: tuple[EndFedConvergencePoint, ...]
    error: str | None = None

    @property
    def completed(self) -> bool:
        return len(self.points) >= 2 and self.error is None

    @property
    def swr_spread(self) -> float | None:
        if not self.completed:
            return None
        values = [point.swr for point in self.points]
        return max(values) - min(values)

    @property
    def resistance_spread_fraction(self) -> float | None:
        if not self.completed:
            return None
        values = [point.impedance_ohm.real for point in self.points]
        mean = sum(values) / len(values)
        return 0.0 if mean <= 0.0 else (max(values) - min(values)) / mean

    @property
    def reactance_spread_ohm(self) -> float | None:
        if not self.completed:
            return None
        values = [point.impedance_ohm.imag for point in self.points]
        return max(values) - min(values)

    @property
    def converged(self) -> bool:
        swr_spread = self.swr_spread
        resistance_spread = self.resistance_spread_fraction
        reactance_spread = self.reactance_spread_ohm
        if swr_spread is None or resistance_spread is None or reactance_spread is None:
            return False
        return (
            swr_spread <= MAX_SWR_SPREAD
            and resistance_spread <= MAX_RESISTANCE_SPREAD_FRACTION
            and reactance_spread <= MAX_REACTANCE_SPREAD_OHM
        )


@dataclass(frozen=True, slots=True)
class CheckEndFedConvergenceCommand:
    parameters: EndFedParameters
    base_spec: SimulationSpec
    segment_counts: tuple[int, ...] = DEFAULT_SEGMENT_COUNTS
    frequency_hz: float | None = None

    def __post_init__(self) -> None:
        counts = tuple(sorted(set(self.segment_counts)))
        if len(counts) < 2:
            raise ValueError("at least two distinct segment counts are required")
        if any(count < 3 for count in counts):
            raise ValueError("segment counts must be at least 3")
        object.__setattr__(self, "segment_counts", counts)
        if self.frequency_hz is not None and self.frequency_hz <= 0.0:
            raise ValueError("frequency_hz must be positive")


@dataclass(frozen=True, slots=True)
class CheckEndFedConvergence:
    solver: AntennaSolver

    def execute(self, command: CheckEndFedConvergenceCommand) -> EndFedConvergenceResult:
        parameters = command.parameters
        frequency_hz = command.frequency_hz or parameters.frequency_hz
        model = parameters.to_antenna(name="End-fed convergence")
        points: list[EndFedConvergencePoint] = []
        for count in command.segment_counts:
            wire_segments: list[tuple[str, int]] = []
            if parameters.feed_section_active:
                wire_segments.append((FEED_SECTION_ID, ENDFED_FEED_SECTION_SEGMENTS))
            wire_segments.append((RADIATOR_ID, count))
            spec = replace(
                command.base_spec,
                frequency_plan=FrequencyPlan.single(frequency_hz),
                segmentation=SegmentationPolicy(
                    min_segments_per_wire=1,
                    wire_segments=tuple(wire_segments),
                ),
                far_field=FarFieldRequest(enabled=False),
            )
            result = RunSimulation(self.solver).execute(
                RunSimulationCommand(model=model, spec=spec)
            )
            if result.status is not SimulationStatus.COMPLETED or not result.frequencies:
                message = next(
                    (diagnostic.message for diagnostic in result.diagnostics),
                    result.status.value,
                )
                return EndFedConvergenceResult(points=tuple(points), error=message)
            point = result.frequencies[0]
            points.append(
                EndFedConvergencePoint(
                    segments=count,
                    impedance_ohm=point.impedance_ohm,
                    swr=point.swr,
                )
            )
        return EndFedConvergenceResult(points=tuple(points))
