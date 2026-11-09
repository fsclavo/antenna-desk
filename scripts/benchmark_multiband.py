#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measure the per-band multiband batch against the real NEC-2 adapter.

The benchmark is intentionally representative rather than exhaustive. It uses
15 sweep points and five pattern frequencies per band at a 5-degree pattern
step, records the produced runs in a project, and reports wall time, compressed
project size, and process peak RSS. Run it once per worker setting to compare
the sequential and parallel paths in separate processes.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

try:
    import resource
except ImportError:  # pragma: no cover - Windows development host
    resource = None  # type: ignore[assignment]
from dataclasses import dataclass
from pathlib import Path

from antennadesk.application.use_cases.analyze_bands import (
    AnalyzeBands,
    AnalyzeBandsCommand,
    BandSimulationRequest,
)
from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.application.use_cases.record_simulation_run import (
    RecordSimulationRun,
    RecordSimulationRunCommand,
)
from antennadesk.domain.antennas.design import AntennaDesignParameters
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.g5rv import g5rv_parameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.design.band_plan import BandPlan, BandSelection
from antennadesk.domain.simulation.bands import amateur_band_by_id
from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
)
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.simulation.nec2.solver import Nec2cSolver
from antennadesk.ui.pattern_resolution import far_field_request

DEFAULT_SWEEP_POINTS = 15
DEFAULT_PATTERN_FREQUENCIES = 5
DEFAULT_PATTERN_STEP_DEG = 5.0


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    key: str
    name: str
    parameters: AntennaDesignParameters
    band_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    name: str
    bands: int
    seconds: float
    compressed_bytes: int
    peak_rss_kib: int
    statuses: tuple[str, ...]


def _cases() -> tuple[BenchmarkCase, ...]:
    bands_3 = ("40m", "20m", "10m")
    bands_5 = ("80m", "40m", "20m", "15m", "10m")
    bands_8 = ("80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m")
    oc = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.4,
        height_m=10.0,
        transformer_ratio=4.0,
    )
    g5rv = g5rv_parameters(frequency_hz=14_100_000.0)
    fan = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=20.2, included_angle_deg=120.0),
            FanElement(length_m=10.1, included_angle_deg=100.0),
        ),
        apex_height_m=12.0,
    )
    return (
        BenchmarkCase("ocfd-3", "OCFD 40 m", oc, bands_3),
        BenchmarkCase("g5rv-3", "G5RV", g5rv, bands_3),
        BenchmarkCase("g5rv-5", "G5RV", g5rv, bands_5),
        BenchmarkCase("g5rv-8", "G5RV", g5rv, bands_8),
        BenchmarkCase("fan-3", "Fan dipole 40/20/10 m", fan, bands_3),
        BenchmarkCase("fan-8", "Fan dipole wide", fan, bands_8),
    )


def _band_plan(case: BenchmarkCase) -> BandPlan:
    selections = []
    for band_id in case.band_ids:
        band = amateur_band_by_id(band_id)
        if band is None:
            raise ValueError(f"unknown band: {band_id}")
        selections.append(BandSelection(band, points=DEFAULT_SWEEP_POINTS))
    return BandPlan(tuple(selections))


def _requests(
    case: BenchmarkCase,
    plan: BandPlan,
) -> tuple[BandSimulationRequest, ...]:
    model = case.parameters.to_antenna(name=case.name)
    requests = []
    for selection in plan.selections:
        frequency_plan = selection.frequency_plan
        segmentation = aligned_policy_for_model(
            model,
            frequency_plan.stop_hz,
            SegmentationPolicy(min_segments_per_wire=3),
        )
        pattern_frequencies = frequency_plan.snapshot_frequencies(
            DEFAULT_PATTERN_FREQUENCIES,
            preferred_frequency_hz=case.parameters.frequency_hz,
        )
        spec = SimulationSpec(
            frequency_plan=frequency_plan,
            segmentation=segmentation,
            far_field=far_field_request(
                DEFAULT_PATTERN_STEP_DEG,
                model.environment.ground,
            ),
            pattern_frequencies_hz=pattern_frequencies,
        )
        requests.append(BandSimulationRequest(selection.band, spec))
    return tuple(requests)


def _peak_rss_kib() -> int:
    if resource is None:
        return 0
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def _run_case(
    solver: Nec2cSolver,
    repository: JsonProjectRepository,
    case: BenchmarkCase,
    workers: int,
) -> BenchmarkResult:
    plan = _band_plan(case)
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name=f"Benchmark {case.name}",
            variant_name="Initial",
            parameters=case.parameters,
            band_plan=plan,
        )
    )
    design = project.designs[0]
    requests = _requests(case, plan)
    peak_before = _peak_rss_kib()
    started = time.perf_counter()
    analysis = AnalyzeBands(solver).execute(
        AnalyzeBandsCommand(
            design_id=design.id,
            model=design.antenna,
            requests=requests,
            parallel_workers=workers,
        )
    )
    elapsed = time.perf_counter() - started
    for band_result in analysis.bands:
        if band_result.result.status not in {
            SimulationStatus.COMPLETED,
            SimulationStatus.PARTIAL,
        }:
            continue
        project = RecordSimulationRun().execute(
            RecordSimulationRunCommand(
                project=project,
                design_id=design.id,
                result=band_result.result,
                band_id=band_result.band.name,
                batch_id=analysis.batch_id,
            )
        )
    peak_after = _peak_rss_kib()
    return BenchmarkResult(
        name=case.name,
        bands=len(plan),
        seconds=elapsed,
        compressed_bytes=repository.serialized_size(project),
        peak_rss_kib=max(peak_before, peak_after),
        statuses=tuple(band.result.status.value for band in analysis.bands),
    )


def _print_markdown(results: tuple[BenchmarkResult, ...]) -> None:
    print(
        "| Design | Bands | Sweep points/band | Pattern freqs/band | "
        "Seconds | Compressed MB | Peak RSS MiB | Status |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---|")
    for result in results:
        status = "ok" if set(result.statuses) == {"completed"} else ", ".join(result.statuses)
        rss = "n/a" if result.peak_rss_kib == 0 else f"{result.peak_rss_kib / 1024:.0f}"
        print(
            f"| {result.name} | {result.bands} | {DEFAULT_SWEEP_POINTS} | "
            f"{DEFAULT_PATTERN_FREQUENCIES} | {result.seconds:.2f} | "
            f"{result.compressed_bytes / (1024 * 1024):.2f} | {rss} | {status} |"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--nec2c",
        type=Path,
        default=Path(os.environ["NEC2C"]) if "NEC2C" in os.environ else None,
        help="path to the nec2c executable (or set NEC2C)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="parallel band workers (1 keeps the sequential path)",
    )
    parser.add_argument(
        "--case",
        choices=tuple(case.key for case in _cases()),
        help="run only one benchmark case",
    )
    args = parser.parse_args()
    if args.nec2c is None:
        parser.error("--nec2c is required (or set the NEC2C environment variable)")
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")

    solver = Nec2cSolver(args.nec2c)
    repository = JsonProjectRepository()
    cases = tuple(case for case in _cases() if args.case is None or case.key == args.case)
    print(f"Workers: {args.workers}")
    results = tuple(_run_case(solver, repository, case, args.workers) for case in cases)
    _print_markdown(results)
    parent_peak = max(result.peak_rss_kib for result in results)
    print(f"Parent process peak RSS: {parent_peak / 1024:.0f} MiB")
    return 0 if all(set(result.statuses) == {"completed"} for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
