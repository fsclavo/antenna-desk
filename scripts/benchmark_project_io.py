#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Measure project open/save/compact memory and wall time.

This is a development benchmark, not a test. It generates a project with
representative far-field arrays and raw solver text, then runs each operation in
a separate process so ``ru_maxrss`` reflects that operation instead of the
generator. The generated project is disposable and must not be committed.

Example:

    uv run python scripts/benchmark_project_io.py --step all
    uv run python scripts/benchmark_project_io.py --step all \\
        --runs 6 --patterns 5 --step-deg 1.0 --raw-mb 20
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import tracemalloc
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Final

try:
    import resource
except ImportError:  # pragma: no cover - Windows development host
    resource = None  # type: ignore[assignment]

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.application.use_cases.record_simulation_run import (
    RecordSimulationRun,
    RecordSimulationRunCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.persistence.container import ProjectContainerRepository

FREQUENCY_HZ: Final = 7_100_000.0
DEFAULT_RUNS: Final = 4
DEFAULT_PATTERNS: Final = 5
DEFAULT_STEP_DEG: Final = 2.0
DEFAULT_RAW_MB: Final = 8
STEPS: Final = (
    "open",
    "select",
    "save",
    "save-lazy",
    "compact",
    "compact-lazy",
    "design-only",
)


def _peak_rss_mb() -> float | None:
    if resource is None:
        return None
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports KiB; macOS reports bytes. Normalize by the platform size.
    divisor = 1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0
    return value / divisor


def _line(label: str, elapsed_s: float) -> str:
    peak = _peak_rss_mb()
    current, traced = tracemalloc.get_traced_memory()
    del current
    peak_text = f"{peak:.1f}" if peak is not None else "n/a"
    return (
        f"{label}: elapsed={elapsed_s:.2f}s peak_rss_mb={peak_text} "
        f"tracemalloc_peak_mb={traced / (1024 * 1024):.1f}"
    )


def _far_field(
    theta_count: int,
    phi_count: int,
) -> tuple[FarFieldPoint, ...]:
    points: list[FarFieldPoint] = []
    for theta_index in range(theta_count):
        theta = 180.0 * theta_index / max(1, theta_count - 1)
        for phi_index in range(phi_count):
            phi = 360.0 * phi_index / max(1, phi_count)
            points.append(
                FarFieldPoint(
                    theta_deg=theta,
                    phi_deg=phi,
                    gain_vertical_db=2.15,
                    gain_horizontal_db=None,
                    gain_total_db=2.15,
                    axial_ratio=0.0,
                    tilt_deg=0.0,
                    polarization="LINEAR",
                    e_theta_magnitude_v_per_m=0.67,
                    e_theta_phase_deg=-122.0,
                    e_phi_magnitude_v_per_m=0.0,
                    e_phi_phase_deg=0.0,
                )
            )
    return tuple(points)


def _raw_output(target_mb: int) -> str:
    if target_mb <= 0:
        return ""
    line = "FREQUENCY 7.100000E+06 60 21 0 0 0 0 0\n"
    count = max(1, (target_mb * 1024 * 1024) // len(line))
    return line * count


def _synthetic_result(
    *,
    pattern_count: int,
    step_deg: float,
    raw_mb: int,
) -> SimulationResult:
    pattern_count = max(1, pattern_count)
    if pattern_count == 1:
        plan = FrequencyPlan.single(FREQUENCY_HZ)
    else:
        plan = FrequencyPlan.sweep(
            FREQUENCY_HZ - 100_000.0,
            FREQUENCY_HZ + 100_000.0,
            pattern_count,
        )
    theta_count = max(2, round(180.0 / step_deg) + 1)
    phi_count = max(1, round(360.0 / step_deg))
    far_field = _far_field(theta_count, phi_count)
    frequencies = tuple(
        FrequencyResult(
            frequency_hz=frequency,
            feed_tag=1,
            feed_segment=11,
            impedance_ohm=complex(50.0, 0.0),
            swr=1.0,
            input_power_w=0.001,
            far_field=far_field,
            directivity_db=2.15,
            realized_gain_db=2.05,
            mismatch_loss_db=0.1,
        )
        for frequency in plan.frequencies_hz
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=SimulationSpec(
            frequency_plan=plan,
            far_field=FarFieldRequest(
                enabled=True,
                theta_start_deg=0.0,
                theta_stop_deg=180.0,
                theta_count=theta_count,
                phi_start_deg=0.0,
                phi_stop_deg=360.0,
                phi_count=phi_count,
            ),
            pattern_frequencies_hz=plan.frequencies_hz,
        ),
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=frequencies,
        raw_input="GW 1 11 -10 0 8 10 0 8 0.001\n",
        raw_output=_raw_output(raw_mb),
    )


def _generate(
    path: Path,
    *,
    runs: int,
    patterns: int,
    step_deg: float,
    raw_mb: int,
) -> None:
    parameters = DipoleParameters(
        frequency_hz=FREQUENCY_HZ,
        total_length_m=20.0,
        height_m=8.0,
        wire_radius_m=0.001,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )
    project = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="I/O benchmark",
            variant_name="Initial",
            parameters=parameters,
            description="Synthetic project for the project I/O benchmark.",
        ),
        now=datetime(2026, 11, 21, tzinfo=UTC),
    )
    design = project.designs[0]
    started = time.perf_counter()
    for index in range(max(1, runs)):
        created_at = datetime(2026, 11, 21, tzinfo=UTC) + timedelta(minutes=index)
        project = RecordSimulationRun().execute(
            RecordSimulationRunCommand(
                project=project,
                design_id=design.id,
                result=_synthetic_result(
                    pattern_count=patterns,
                    step_deg=step_deg,
                    raw_mb=raw_mb,
                ),
                created_at=created_at,
            )
        )
    repository = ProjectContainerRepository()
    prepared = repository.prepare_payload(project)
    repository.write_payload(path, prepared)
    elapsed = time.perf_counter() - started
    print(
        f"generate: runs={len(project.simulation_runs)} "
        f"container_mb={prepared.compressed_bytes / (1024 * 1024):.1f} "
        f"expanded_mb={prepared.expanded_bytes / (1024 * 1024):.1f} "
        f"elapsed={elapsed:.2f}s"
    )


def _open_session(path: Path) -> tuple[ProjectContainerRepository, object]:
    repository = ProjectContainerRepository()
    session = repository.open_session(path)
    return repository, session


def _run_step(path: Path, step: str) -> None:
    tracemalloc.start()
    started = time.perf_counter()
    repository, session = _open_session(path)
    if step == "open":
        elapsed = time.perf_counter() - started
        print(
            _line(
                f"open: runs={session.run_count()} "
                f"materialized_runs={len(session.project.simulation_runs)}",
                elapsed,
            )
        )
        return
    design_id = session.project.designs[0].id
    if step == "select":
        analysis = session.latest_band_analysis(design_id)
        run = session.latest_run(design_id)
        elapsed = time.perf_counter() - started
        print(
            _line(
                f"select: loaded_runs={len(session.cached_runs())} "
                f"band={analysis is not None} single={run is not None}",
                elapsed,
            )
        )
        return
    if step == "save":
        full = session.materialize()
        prepared = repository.prepare_payload(full)
        output = path.with_name(path.stem + ".saved.antennadesk")
        repository.write_payload(output, prepared)
        elapsed = time.perf_counter() - started
        print(
            _line(
                f"save: runs={len(full.simulation_runs)} "
                f"container_mb={prepared.compressed_bytes / (1024 * 1024):.1f} "
                f"expanded_mb={prepared.expanded_bytes / (1024 * 1024):.1f}",
                elapsed,
            )
        )
        return
    if step == "save-lazy":
        prepared = repository.prepare_session_payload(session, session.project)
        output = path.with_name(path.stem + ".lazy-saved.antennadesk")
        repository.write_payload(output, prepared)
        elapsed = time.perf_counter() - started
        print(
            _line(
                f"save-lazy: runs={session.run_count()} "
                f"container_mb={prepared.compressed_bytes / (1024 * 1024):.1f} "
                f"expanded_mb={prepared.expanded_bytes / (1024 * 1024):.1f}",
                elapsed,
            )
        )
        return
    if step == "compact":
        full = session.materialize()
        before = len(full.simulation_runs)
        compacted = full.with_latest_simulation_runs_only(
            updated_at=datetime(2026, 11, 21, tzinfo=UTC)
        )
        prepared = repository.prepare_payload(compacted)
        output = path.with_name(path.stem + ".compacted.antennadesk")
        repository.write_payload(output, prepared)
        elapsed = time.perf_counter() - started
        print(
            _line(
                f"compact: runs={before}->{len(compacted.simulation_runs)} "
                f"container_mb={prepared.compressed_bytes / (1024 * 1024):.1f}",
                elapsed,
            )
        )
        return
    if step == "compact-lazy":
        before = session.run_count()
        compacted_project = replace(
            session.project,
            updated_at=datetime(2026, 11, 21, tzinfo=UTC),
        )
        prepared = repository.prepare_session_payload(
            session,
            compacted_project,
            retained_only=True,
        )
        output = path.with_name(path.stem + ".lazy-compacted.antennadesk")
        repository.write_payload(output, prepared)
        elapsed = time.perf_counter() - started
        print(
            _line(
                f"compact-lazy: runs={before}->{session.retained_run_count()} "
                f"container_mb={prepared.compressed_bytes / (1024 * 1024):.1f}",
                elapsed,
            )
        )
        return
    if step == "design-only":
        project = replace(
            session.project,
            simulation_runs=(),
            designs=tuple(
                replace(design, optimization_summary=None) for design in session.project.designs
            ),
        )
        prepared = repository.prepare_payload(project)
        output = path.with_name(path.stem + ".design-only.antennadesk")
        repository.write_payload(output, prepared)
        elapsed = time.perf_counter() - started
        print(
            _line(
                f"design-only: runs={len(project.simulation_runs)} "
                f"container_mb={prepared.compressed_bytes / (1024 * 1024):.1f}",
                elapsed,
            )
        )
        return
    raise SystemExit(f"unknown step: {step}")


def _all(
    path: Path,
    *,
    runs: int,
    patterns: int,
    step_deg: float,
    raw_mb: int,
) -> None:
    # Run the generator in a child too: a forked child inherits the parent's
    # peak RSS and would otherwise report the generator's memory as its own.
    for step in ("generate", *STEPS):
        command = [
            sys.executable,
            __file__,
            "--project",
            str(path),
            "--step",
            step,
        ]
        if step == "generate":
            command.extend(
                [
                    "--runs",
                    str(runs),
                    "--patterns",
                    str(patterns),
                    "--step-deg",
                    str(step_deg),
                    "--raw-mb",
                    str(raw_mb),
                ]
            )
        result = subprocess.run(  # noqa: S603 - fixed interpreter and script path
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        output = result.stdout.strip() or result.stderr.strip()
        print(output)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        type=Path,
        default=Path(
            # Approved local scratch directory.
            "/tmp/user/1000/opencode/project-io-benchmark.antennadesk"  # noqa: S108
        ),
    )
    parser.add_argument("--step", choices=(*STEPS, "generate", "all"), default="all")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--patterns", type=int, default=DEFAULT_PATTERNS)
    parser.add_argument("--step-deg", type=float, default=DEFAULT_STEP_DEG)
    parser.add_argument("--raw-mb", type=int, default=DEFAULT_RAW_MB)
    args = parser.parse_args()
    if args.step == "generate":
        _generate(
            args.project,
            runs=args.runs,
            patterns=args.patterns,
            step_deg=args.step_deg,
            raw_mb=args.raw_mb,
        )
        return
    if args.step == "all":
        _all(
            args.project,
            runs=args.runs,
            patterns=args.patterns,
            step_deg=args.step_deg,
            raw_mb=args.raw_mb,
        )
        return
    _run_step(args.project, args.step)


if __name__ == "__main__":
    main()
