# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Projects and design variants."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import UUID

from ..antennas.antenna import AntennaModel
from ..antennas.balun import BalunLoss
from ..antennas.design import AntennaDesignParameters, antenna_type_for, template_load_ids
from ..antennas.feed_line import FeedLine
from ..antennas.load import LumpedLoad
from ..antennas.matching_network import MatchingNetwork
from ..antennas.transmission_line import TransmissionLine
from ..common.time import ensure_utc
from ..common.units import ensure_non_negative
from ..common.validation import Diagnostic, Severity, raise_if_errors
from ..design.band_plan import BandPlan
from ..measurement import Measurement
from ..simulation.band_result import BandAnalysisResult
from ..simulation.run import SimulationRun


@dataclass(frozen=True, slots=True)
class DesignProvenance:
    """Traceability metadata attached to a design produced by an estimator."""

    method_id: str
    confidence: str
    assumptions: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    tolerance_m: float = 0.0
    source_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise ValueError("provenance method_id must not be empty")
        if not self.confidence.strip():
            raise ValueError("provenance confidence must not be empty")
        ensure_non_negative(self.tolerance_m, name="tolerance_m")
        object.__setattr__(self, "assumptions", tuple(self.assumptions))
        object.__setattr__(self, "warnings", tuple(self.warnings))
        object.__setattr__(self, "source_ids", tuple(self.source_ids))


@dataclass(frozen=True, slots=True)
class DesignVariant:
    """A named antenna design and its derived canonical model."""

    id: UUID
    name: str
    antenna_type: str
    parameters: AntennaDesignParameters
    antenna: AntennaModel
    provenance: DesignProvenance | None = None
    band_plan: BandPlan | None = None

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
        expected = (
            self.parameters.to_antenna(name=self.antenna.name)
            .with_loads(self.antenna.loads)
            .with_transmission_lines(self.antenna.transmission_lines)
        )
        if expected != self.antenna:
            raise ValueError("antenna geometry is inconsistent with its design parameters")

    def with_parameters(
        self,
        parameters: AntennaDesignParameters,
        *,
        provenance: DesignProvenance | None = None,
    ) -> DesignVariant:
        generated = parameters.to_antenna(name=self.antenna.name)
        managed_ids = (
            template_load_ids(self.parameters)
            | template_load_ids(parameters)
            | {load.id for load in generated.loads}
        )
        preserved = tuple(load for load in self.antenna.loads if load.id not in managed_ids)
        generated_lines = generated.transmission_lines
        managed_line_ids = {line.id for line in generated_lines}
        preserved_lines = tuple(
            line for line in self.antenna.transmission_lines if line.id not in managed_line_ids
        )
        antenna = generated.with_loads(generated.loads + preserved).with_transmission_lines(
            generated_lines + preserved_lines
        )
        return replace(
            self,
            antenna_type=antenna_type_for(parameters),
            parameters=parameters,
            antenna=antenna,
            provenance=provenance,
        )

    def with_band_plan(self, band_plan: BandPlan | None) -> DesignVariant:
        return replace(self, band_plan=band_plan)

    def with_loads(self, loads: tuple[LumpedLoad, ...]) -> DesignVariant:
        return replace(self, antenna=self.antenna.with_loads(loads))

    def with_transmission_lines(
        self,
        transmission_lines: tuple[TransmissionLine, ...],
    ) -> DesignVariant:
        return replace(
            self,
            antenna=self.antenna.with_transmission_lines(transmission_lines),
        )


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
    matching_network: MatchingNetwork | None = None
    balun_loss: BalunLoss | None = None

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
        """Return the latest single-band run for a design.

        Band-analysis runs carry a ``band_id`` and are retrieved through
        :meth:`latest_band_analysis` or :meth:`latest_simulation_run_for_band`.
        """

        latest: SimulationRun | None = None
        for run in self.simulation_runs:
            if run.design_id == design_id and run.band_id is None:
                latest = run
        return latest

    def latest_simulation_run_for_band(
        self,
        design_id: UUID,
        band_id: str,
    ) -> SimulationRun | None:
        latest: SimulationRun | None = None
        for run in self.simulation_runs:
            if run.design_id == design_id and run.band_id == band_id:
                latest = run
        return latest

    def latest_band_analysis(self, design_id: UUID) -> BandAnalysisResult | None:
        batches: dict[UUID, list[SimulationRun]] = {}
        for run in self.simulation_runs:
            if run.design_id != design_id or run.batch_id is None:
                continue
            batches.setdefault(run.batch_id, []).append(run)
        if not batches:
            return None
        batch_id, runs = max(
            batches.items(),
            key=lambda item: max(run.created_at for run in item[1]),
        )
        ordered = sorted(runs, key=lambda run: run.created_at)
        return BandAnalysisResult.from_runs(
            design_id=design_id,
            batch_id=batch_id,
            created_at=max(run.created_at for run in runs),
            runs=tuple((run.band_id or "", run.result) for run in ordered),
        )

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

    def with_updated_measurement(
        self,
        measurement: Measurement,
        *,
        updated_at: datetime,
    ) -> Project:
        if not any(item.id == measurement.id for item in self.measurements):
            raise KeyError(f"unknown measurement id: {measurement.id}")
        return replace(
            self,
            measurements=tuple(
                measurement if item.id == measurement.id else item for item in self.measurements
            ),
            updated_at=updated_at,
        )

    def without_measurement(
        self,
        measurement_id: UUID,
        *,
        updated_at: datetime,
    ) -> Project:
        if not any(item.id == measurement_id for item in self.measurements):
            raise KeyError(f"unknown measurement id: {measurement_id}")
        return replace(
            self,
            measurements=tuple(item for item in self.measurements if item.id != measurement_id),
            updated_at=updated_at,
        )

    def with_feed_line(
        self,
        feed_line: FeedLine | None,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(self, feed_line=feed_line, updated_at=updated_at)

    def with_matching_network(
        self,
        matching_network: MatchingNetwork | None,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(self, matching_network=matching_network, updated_at=updated_at)

    def with_balun_loss(
        self,
        balun_loss: BalunLoss | None,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(self, balun_loss=balun_loss, updated_at=updated_at)

    def _retained_simulation_runs(self) -> tuple[SimulationRun, ...]:
        retained_ids: set[UUID] = set()
        for design in self.designs:
            latest_single = self.latest_simulation_run(design.id)
            if latest_single is not None:
                retained_ids.add(latest_single.id)
            batches: dict[UUID, list[SimulationRun]] = {}
            for run in self.simulation_runs:
                if run.design_id == design.id and run.batch_id is not None:
                    batches.setdefault(run.batch_id, []).append(run)
            if batches:
                _, runs = max(
                    batches.items(),
                    key=lambda item: max(run.created_at for run in item[1]),
                )
                retained_ids.update(run.id for run in runs)
        return tuple(run for run in self.simulation_runs if run.id in retained_ids)

    def has_compactable_simulation_history(self) -> bool:
        return len(self.simulation_runs) > len(self._retained_simulation_runs())

    def retained_simulation_run_count(self) -> int:
        return len(self._retained_simulation_runs())

    def with_latest_simulation_runs_only(self, *, updated_at: datetime) -> Project:
        return replace(
            self,
            simulation_runs=self._retained_simulation_runs(),
            updated_at=updated_at,
        )

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
