# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Lazy project session over a persisted run store.

The project metadata and designs are materialized eagerly because every screen
needs them. Simulation runs are indexed from the container manifest and loaded
only when a design or report asks for them, so opening a project with a long
history does not allocate every far-field array.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Protocol
from uuid import UUID

from ..domain.projects.project import Project
from ..domain.simulation.band_result import BandAnalysisResult
from ..domain.simulation.run import SimulationRun


@dataclass(frozen=True, slots=True)
class RunIndexEntry:
    """Manifest-level run metadata that does not require the run payload."""

    id: UUID
    design_id: UUID
    created_at: datetime
    band_id: str | None = None
    batch_id: UUID | None = None


class ProjectRunStore(Protocol):
    """Persistence boundary for lazy run materialization."""

    @property
    def run_index(self) -> tuple[RunIndexEntry, ...]:
        """Return the run index without reading run payloads."""

    def load_run(self, run_id: UUID) -> SimulationRun:
        """Load one run by id."""

    def load_all_runs(self) -> tuple[SimulationRun, ...]:
        """Load every run in persisted order."""


class ProjectSession:
    """A project with lazy simulation runs.

    ``project`` never contains simulation runs. Use :meth:`latest_run`,
    :meth:`latest_band_analysis`, or :meth:`materialize` to load payloads.
    """

    def __init__(self, project: Project, store: ProjectRunStore) -> None:
        if project.simulation_runs:
            raise ValueError("a project session requires a run-free project")
        self.project = project
        self._store = store
        self._cache: dict[UUID, SimulationRun] = {}

    @property
    def run_index(self) -> tuple[RunIndexEntry, ...]:
        return self._store.run_index

    def run_ids(self) -> tuple[UUID, ...]:
        return tuple(entry.id for entry in self.run_index)

    def run_count(self) -> int:
        return len(self.run_index)

    def load_run(self, run_id: UUID) -> SimulationRun:
        cached = self._cache.get(run_id)
        if cached is not None:
            return cached
        run = self._store.load_run(run_id)
        self._cache[run.id] = run
        return run

    def load_all_runs(self) -> tuple[SimulationRun, ...]:
        loaded = {run.id: run for run in self._cache.values()}
        for run in self._store.load_all_runs():
            loaded.setdefault(run.id, run)
        ordered = [loaded[entry.id] for entry in self.run_index if entry.id in loaded]
        return tuple(ordered)

    def materialize(self) -> Project:
        return replace(self.project, simulation_runs=self.load_all_runs())

    def with_project(self, project: Project) -> ProjectSession:
        if project.simulation_runs:
            raise ValueError("a project session requires a run-free project")
        session = ProjectSession(project, self._store)
        session._cache = dict(self._cache)
        return session

    def latest_run(self, design_id: UUID) -> SimulationRun | None:
        latest: RunIndexEntry | None = None
        for entry in self.run_index:
            if entry.design_id != design_id or entry.band_id is not None:
                continue
            if latest is None or entry.created_at >= latest.created_at:
                latest = entry
        return self.load_run(latest.id) if latest is not None else None

    def latest_band_analysis(self, design_id: UUID) -> BandAnalysisResult | None:
        batches: dict[UUID, list[RunIndexEntry]] = {}
        latest_single: RunIndexEntry | None = None
        for entry in self.run_index:
            if entry.design_id != design_id:
                continue
            if entry.batch_id is not None:
                batches.setdefault(entry.batch_id, []).append(entry)
            elif latest_single is None or entry.created_at > latest_single.created_at:
                latest_single = entry
        if not batches:
            return None
        batch_id, entries = max(
            batches.items(),
            key=lambda item: max(entry.created_at for entry in item[1]),
        )
        created_at = max(entry.created_at for entry in entries)
        if latest_single is not None and latest_single.created_at > created_at:
            return None
        ordered = sorted(entries, key=lambda entry: entry.created_at)
        runs = tuple((entry.band_id or "", self.load_run(entry.id).result) for entry in ordered)
        return BandAnalysisResult.from_runs(
            design_id=design_id,
            batch_id=batch_id,
            created_at=created_at,
            runs=runs,
        )

    def retained_run_ids(self) -> tuple[UUID, ...]:
        retained: set[UUID] = set()
        for design_id in {entry.design_id for entry in self.run_index}:
            latest_single: RunIndexEntry | None = None
            batches: dict[UUID, list[RunIndexEntry]] = {}
            for entry in self.run_index:
                if entry.design_id != design_id:
                    continue
                if entry.batch_id is not None:
                    batches.setdefault(entry.batch_id, []).append(entry)
                elif latest_single is None or entry.created_at >= latest_single.created_at:
                    latest_single = entry
            if latest_single is not None:
                retained.add(latest_single.id)
            if batches:
                _, entries = max(
                    batches.items(),
                    key=lambda item: max(entry.created_at for entry in item[1]),
                )
                retained.update(entry.id for entry in entries)
        return tuple(entry.id for entry in self.run_index if entry.id in retained)

    def retained_run_count(self) -> int:
        return len(self.retained_run_ids())

    def has_compactable_history(self) -> bool:
        return self.run_count() > self.retained_run_count()

    def cached_runs(self) -> Mapping[UUID, SimulationRun]:
        return dict(self._cache)
