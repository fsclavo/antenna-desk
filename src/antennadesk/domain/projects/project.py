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
from ..antennas.matching_network import MatchingNetwork, MatchingNetworkPosition
from ..antennas.transmission_line import TransmissionLine
from ..common.time import ensure_utc
from ..common.units import ensure_non_negative
from ..common.validation import Diagnostic, Severity, raise_if_errors
from ..design.band_plan import BandPlan
from ..design.matching_design import MatchingNetworkDesign
from ..measurement import Measurement, MeasurementSession
from ..optimization.summary import OptimizationSummary
from ..simulation.band_result import BandAnalysisResult
from ..simulation.run import SimulationRun
from .construction import ConstructionRecord
from .installation import InstallationProfile
from .journal import JournalEntry


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
    optimization_summary: OptimizationSummary | None = None

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
            .with_sources(self.antenna.sources)
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
        # A parameter change invalidates the previous optimizer summary. An
        # identical write-back (for example, the form apply that follows Apply
        # Best) must preserve the summary attached by the optimizer.
        summary = self.optimization_summary if parameters == self.parameters else None
        return replace(
            self,
            antenna_type=antenna_type_for(parameters),
            parameters=parameters,
            antenna=antenna,
            provenance=provenance,
            optimization_summary=summary,
        )

    def with_band_plan(self, band_plan: BandPlan | None) -> DesignVariant:
        return replace(self, band_plan=band_plan)

    def with_optimization_summary(
        self,
        optimization_summary: OptimizationSummary | None,
    ) -> DesignVariant:
        return replace(self, optimization_summary=optimization_summary)

    def with_loads(self, loads: tuple[LumpedLoad, ...]) -> DesignVariant:
        summary = self.optimization_summary if loads == self.antenna.loads else None
        return replace(
            self,
            antenna=self.antenna.with_loads(loads),
            optimization_summary=summary,
        )

    def with_transmission_lines(
        self,
        transmission_lines: tuple[TransmissionLine, ...],
    ) -> DesignVariant:
        summary = (
            self.optimization_summary
            if transmission_lines == self.antenna.transmission_lines
            else None
        )
        return replace(
            self,
            antenna=self.antenna.with_transmission_lines(transmission_lines),
            optimization_summary=summary,
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
    matching_network_position: MatchingNetworkPosition = MatchingNetworkPosition.FEEDPOINT
    matching_network_design: MatchingNetworkDesign | None = None
    balun_loss: BalunLoss | None = None
    current_balun: bool = False
    installation_profiles: tuple[InstallationProfile, ...] = field(default_factory=tuple)
    active_installation_profile_id: UUID | None = None
    construction_record: ConstructionRecord | None = None
    measurement_sessions: tuple[MeasurementSession, ...] = field(default_factory=tuple)
    journal_entries: tuple[JournalEntry, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "designs", tuple(self.designs))
        object.__setattr__(self, "simulation_runs", tuple(self.simulation_runs))
        object.__setattr__(self, "measurements", tuple(self.measurements))
        object.__setattr__(self, "measurement_sessions", tuple(self.measurement_sessions))
        object.__setattr__(self, "journal_entries", tuple(self.journal_entries))
        object.__setattr__(self, "installation_profiles", tuple(self.installation_profiles))
        object.__setattr__(
            self,
            "matching_network_position",
            MatchingNetworkPosition(self.matching_network_position),
        )
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

        profile_ids: set[UUID] = set()
        profile_names: set[str] = set()
        for profile in self.installation_profiles:
            if profile.id in profile_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.installation_profile.duplicate_id",
                        severity=Severity.ERROR,
                        message=f"duplicate installation profile id: {profile.id}",
                        field="installation_profiles",
                    )
                )
            profile_ids.add(profile.id)
            if profile.name in profile_names:
                diagnostics.append(
                    Diagnostic(
                        code="project.installation_profile.duplicate_name",
                        severity=Severity.ERROR,
                        message=f"duplicate installation profile name: {profile.name}",
                        field="installation_profiles",
                    )
                )
            profile_names.add(profile.name)

        if (
            self.active_installation_profile_id is not None
            and self.active_installation_profile_id not in profile_ids
        ):
            diagnostics.append(
                Diagnostic(
                    code="project.installation_profile.unknown_active",
                    severity=Severity.ERROR,
                    message=(
                        "active installation profile references an unknown profile: "
                        f"{self.active_installation_profile_id}"
                    ),
                    field="active_installation_profile_id",
                )
            )

        design_ids = {design.id for design in self.designs}
        session_ids: set[UUID] = set()
        for session in self.measurement_sessions:
            if session.id in session_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.measurement_session.duplicate_id",
                        severity=Severity.ERROR,
                        message=f"duplicate measurement session id: {session.id}",
                        field="measurement_sessions",
                    )
                )
            session_ids.add(session.id)
            if session.design_id is not None and session.design_id not in design_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.measurement_session.unknown_design",
                        severity=Severity.ERROR,
                        message=(
                            f"measurement session references an unknown design: {session.design_id}"
                        ),
                        field="measurement_sessions",
                    )
                )

        measurement_ids: set[UUID] = set()
        for measurement in self.measurements:
            if measurement.id in measurement_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.measurement.duplicate_id",
                        severity=Severity.ERROR,
                        message=f"duplicate measurement id: {measurement.id}",
                        field="measurements",
                    )
                )
            measurement_ids.add(measurement.id)
            if measurement.session_id is not None and measurement.session_id not in session_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.measurement.unknown_session",
                        severity=Severity.ERROR,
                        message=(
                            f"measurement references an unknown session: {measurement.session_id}"
                        ),
                        field="measurements",
                    )
                )

        seen_journal_ids: set[UUID] = set()
        for entry in self.journal_entries:
            if entry.id in seen_journal_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.journal_entry.duplicate_id",
                        severity=Severity.ERROR,
                        message=f"duplicate journal entry id: {entry.id}",
                        field="journal_entries",
                    )
                )
            seen_journal_ids.add(entry.id)
            if entry.design_id is not None and entry.design_id not in design_ids:
                diagnostics.append(
                    Diagnostic(
                        code="project.journal_entry.unknown_design",
                        severity=Severity.ERROR,
                        message=(f"journal entry references an unknown design: {entry.design_id}"),
                        field="journal_entries",
                    )
                )

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

    def installation_profile_by_id(self, profile_id: UUID) -> InstallationProfile:
        for profile in self.installation_profiles:
            if profile.id == profile_id:
                return profile
        raise KeyError(f"unknown installation profile id: {profile_id}")

    @property
    def active_installation_profile(self) -> InstallationProfile | None:
        if self.active_installation_profile_id is None:
            return None
        return self.installation_profile_by_id(self.active_installation_profile_id)

    def with_installation_state(
        self,
        profiles: tuple[InstallationProfile, ...],
        active_profile_id: UUID | None,
        *,
        updated_at: datetime,
    ) -> Project:
        """Replace the profile set and the active profile in one operation."""

        return replace(
            self,
            installation_profiles=tuple(profiles),
            active_installation_profile_id=active_profile_id,
            updated_at=updated_at,
        )

    def with_installation_profile(
        self,
        profile: InstallationProfile,
        *,
        make_active: bool = True,
        updated_at: datetime,
    ) -> Project:
        profiles = list(self.installation_profiles)
        for index, current in enumerate(profiles):
            if current.id == profile.id:
                profiles[index] = profile
                break
        else:
            profiles.append(profile)
        active_id = (
            profile.id
            if make_active or self.active_installation_profile_id is None
            else self.active_installation_profile_id
        )
        return replace(
            self,
            installation_profiles=tuple(profiles),
            active_installation_profile_id=active_id,
            updated_at=updated_at,
        )

    def without_installation_profile(
        self,
        profile_id: UUID,
        *,
        updated_at: datetime,
    ) -> Project:
        profiles = tuple(
            profile for profile in self.installation_profiles if profile.id != profile_id
        )
        if len(profiles) == len(self.installation_profiles):
            raise KeyError(f"unknown installation profile id: {profile_id}")
        active_id = self.active_installation_profile_id
        if active_id == profile_id:
            active_id = profiles[0].id if profiles else None
        return replace(
            self,
            installation_profiles=profiles,
            active_installation_profile_id=active_id,
            updated_at=updated_at,
        )

    def with_active_installation_profile(
        self,
        profile_id: UUID | None,
        *,
        updated_at: datetime,
    ) -> Project:
        if profile_id is not None:
            self.installation_profile_by_id(profile_id)
        return replace(
            self,
            active_installation_profile_id=profile_id,
            updated_at=updated_at,
        )

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

    def measurement_session_by_id(self, session_id: UUID) -> MeasurementSession:
        for session in self.measurement_sessions:
            if session.id == session_id:
                return session
        raise KeyError(f"unknown measurement session id: {session_id}")

    def measurements_for_session(self, session_id: UUID) -> tuple[Measurement, ...]:
        return tuple(
            measurement for measurement in self.measurements if measurement.session_id == session_id
        )

    def unassigned_measurements(self) -> tuple[Measurement, ...]:
        return tuple(
            measurement for measurement in self.measurements if measurement.session_id is None
        )

    def with_measurement_session(
        self,
        session: MeasurementSession,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(
            self,
            measurement_sessions=(*self.measurement_sessions, session),
            updated_at=updated_at,
        )

    def with_updated_measurement_session(
        self,
        session: MeasurementSession,
        *,
        updated_at: datetime,
    ) -> Project:
        if not any(item.id == session.id for item in self.measurement_sessions):
            raise KeyError(f"unknown measurement session id: {session.id}")
        return replace(
            self,
            measurement_sessions=tuple(
                session if item.id == session.id else item for item in self.measurement_sessions
            ),
            updated_at=updated_at,
        )

    def without_measurement_session(
        self,
        session_id: UUID,
        *,
        updated_at: datetime,
    ) -> Project:
        if not any(item.id == session_id for item in self.measurement_sessions):
            raise KeyError(f"unknown measurement session id: {session_id}")
        measurements = tuple(
            replace(measurement, session_id=None)
            if measurement.session_id == session_id
            else measurement
            for measurement in self.measurements
        )
        return replace(
            self,
            measurement_sessions=tuple(
                item for item in self.measurement_sessions if item.id != session_id
            ),
            measurements=measurements,
            updated_at=updated_at,
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

    def journal_entry_by_id(self, entry_id: UUID) -> JournalEntry:
        for entry in self.journal_entries:
            if entry.id == entry_id:
                return entry
        raise KeyError(f"unknown journal entry id: {entry_id}")

    def with_journal_entry(
        self,
        entry: JournalEntry,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(
            self,
            journal_entries=(*self.journal_entries, entry),
            updated_at=updated_at,
        )

    def with_updated_journal_entry(
        self,
        entry: JournalEntry,
        *,
        updated_at: datetime,
    ) -> Project:
        if not any(item.id == entry.id for item in self.journal_entries):
            raise KeyError(f"unknown journal entry id: {entry.id}")
        return replace(
            self,
            journal_entries=tuple(
                entry if item.id == entry.id else item for item in self.journal_entries
            ),
            updated_at=updated_at,
        )

    def without_journal_entry(
        self,
        entry_id: UUID,
        *,
        updated_at: datetime,
    ) -> Project:
        if not any(item.id == entry_id for item in self.journal_entries):
            raise KeyError(f"unknown journal entry id: {entry_id}")
        return replace(
            self,
            journal_entries=tuple(item for item in self.journal_entries if item.id != entry_id),
            updated_at=updated_at,
        )

    def with_construction_record(
        self,
        construction_record: ConstructionRecord | None,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(
            self,
            construction_record=construction_record,
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
        position: MatchingNetworkPosition | None = None,
        updated_at: datetime,
    ) -> Project:
        return replace(
            self,
            matching_network=matching_network,
            matching_network_position=(
                position if position is not None else self.matching_network_position
            ),
            matching_network_design=(
                self.matching_network_design if matching_network is not None else None
            ),
            updated_at=updated_at,
        )

    def with_matching_network_design(
        self,
        matching_network_design: MatchingNetworkDesign | None,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(
            self,
            matching_network_design=matching_network_design,
            updated_at=updated_at,
        )

    def with_balun_loss(
        self,
        balun_loss: BalunLoss | None,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(self, balun_loss=balun_loss, updated_at=updated_at)

    def with_current_balun(
        self,
        current_balun: bool,
        *,
        updated_at: datetime,
    ) -> Project:
        return replace(self, current_balun=bool(current_balun), updated_at=updated_at)

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
