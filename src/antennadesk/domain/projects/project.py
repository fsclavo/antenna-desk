# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Projects and design variants."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import UUID

from ..antennas.antenna import AntennaModel
from ..antennas.design import AntennaDesignParameters, antenna_type_for
from ..antennas.feed_line import FeedLine
from ..antennas.load import LumpedLoad
from ..common.time import ensure_utc
from ..common.validation import Diagnostic, Severity, raise_if_errors
from ..measurement import Measurement
from ..simulation.run import SimulationRun


@dataclass(frozen=True, slots=True)
class DesignVariant:
    """A named antenna design and its derived canonical model."""

    id: UUID
    name: str
    antenna_type: str
    parameters: AntennaDesignParameters
    antenna: AntennaModel

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("design name must not be empty")
        if not self.antenna_type.strip():
            raise ValueError("antenna_type must not be empty")
        expected_type = antenna_type_for(self.parameters)
        if self.antenna_type != expected_type:
            raise ValueError(
                f"antenna_type {self.antenna_type!r} does not match "
                f"the parameter type {expected_type!r}"
            )
        expected = self.parameters.to_antenna(name=self.antenna.name).with_loads(self.antenna.loads)
        if expected != self.antenna:
            raise ValueError("antenna geometry is inconsistent with its design parameters")

    def with_parameters(
        self,
        parameters: AntennaDesignParameters,
    ) -> DesignVariant:
        antenna = parameters.to_antenna(name=self.antenna.name).with_loads(self.antenna.loads)
        return replace(
            self,
            antenna_type=antenna_type_for(parameters),
            parameters=parameters,
            antenna=antenna,
        )

    def with_loads(self, loads: tuple[LumpedLoad, ...]) -> DesignVariant:
        return replace(self, antenna=self.antenna.with_loads(loads))


@dataclass(frozen=True, slots=True)
class Project:
    """An immutable project containing one or more design variants."""

    id: UUID
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    designs: tuple[DesignVariant, ...] = field(default_factory=tuple)
    simulation_runs: tuple[SimulationRun, ...] = field(default_factory=tuple)
    measurements: tuple[Measurement, ...] = field(default_factory=tuple)
    feed_line: FeedLine | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "designs", tuple(self.designs))
        object.__setattr__(self, "simulation_runs", tuple(self.simulation_runs))
        object.__setattr__(self, "measurements", tuple(self.measurements))
        raise_if_errors(self._invariants())

    def _invariants(self) -> tuple[Diagnostic, ...]:
        diagnostics: list[Diagnostic] = []

        if not self.name.strip():
            diagnostics.append(
                Diagnostic(
                    code="project.name.empty",
                    severity=Severity.ERROR,
                    message="project name must not be empty",
                    field="name",
                )
            )

        for field_name, value in (
            ("created_at", self.created_at),
            ("updated_at", self.updated_at),
        ):
            try:
                ensure_utc(value, name=field_name)
            except ValueError as exc:
                diagnostics.append(
                    Diagnostic(
                        code="project.timestamp.invalid",
                        severity=Severity.ERROR,
                        message=str(exc),
                        field=field_name,
                    )
                )

        if (
            self.created_at.tzinfo is not None
            and self.updated_at.tzinfo is not None
            and self.updated_at < self.created_at
        ):
            diagnostics.append(
                Diagnostic(
                    code="project.timestamp.order",
                    severity=Severity.ERROR,
                    message="updated_at must not be earlier than created_at",
                    field="updated_at",
                )
            )

        seen_ids: set[UUID] = set()
        seen_names: set[str] = set()
        for design in self.designs:
            if design.id in seen_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.design.duplicate_id",
                        severity=Severity.ERROR,
                        message=f"duplicate design id: {design.id}",
                        field="designs",
                    )
                )
            seen_ids.add(design.id)

            if design.name in seen_names:
                diagnostics.append(
                    Diagnostic(
                        code="project.design.duplicate_name",
                        severity=Severity.ERROR,
                        message=f"duplicate design name: {design.name}",
                        field="designs",
                    )
                )
            seen_names.add(design.name)

        design_ids = {design.id for design in self.designs}
        seen_run_ids: set[UUID] = set()
        for run in self.simulation_runs:
            if run.id in seen_run_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.simulation_run.duplicate_id",
                        severity=Severity.ERROR,
                        message=f"duplicate simulation run id: {run.id}",
                        field="simulation_runs",
                    )
                )
            seen_run_ids.add(run.id)
            if run.design_id not in design_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.simulation_run.unknown_design",
                        severity=Severity.ERROR,
                        message=(f"simulation run references an unknown design: {run.design_id}"),
                        field="simulation_runs",
                    )
                )

        return tuple(diagnostics)

    def validate(self) -> tuple[Diagnostic, ...]:
        return self._invariants()

    def design_by_id(self, design_id: UUID) -> DesignVariant:
        for design in self.designs:
            if design.id == design_id:
                return design
        raise KeyError(f"unknown design id: {design_id}")

    def with_simulation_run(
        self,
        run: SimulationRun,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(
            self,
            simulation_runs=(*self.simulation_runs, run),
            updated_at=updated_at,
        )

    def latest_simulation_run(self, design_id: UUID) -> SimulationRun | None:
        latest: SimulationRun | None = None
        for run in self.simulation_runs:
            if run.design_id == design_id:
                latest = run
        return latest

    def with_measurement(
        self,
        measurement: Measurement,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(
            self,
            measurements=(*self.measurements, measurement),
            updated_at=updated_at,
        )

    def with_feed_line(
        self,
        feed_line: FeedLine | None,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(self, feed_line=feed_line, updated_at=updated_at)

    def with_latest_simulation_runs_only(self, *, updated_at: datetime) -> Project:
        latest_runs = tuple(
            run
            for design in self.designs
            if (run := self.latest_simulation_run(design.id)) is not None
        )
        return replace(self, simulation_runs=latest_runs, updated_at=updated_at)

    def with_design(self, design: DesignVariant, *, updated_at: datetime) -> Project:
        replaced = False
        designs: list[DesignVariant] = []
        for current in self.designs:
            if current.id == design.id:
                designs.append(design)
                replaced = True
            else:
                designs.append(current)
        if not replaced:
            designs.append(design)
        return replace(self, designs=tuple(designs), updated_at=updated_at)
