#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run the Phase 2 reference dipole through the real solver adapter."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from antennadesk.application.use_cases.run_simulation import (
    RunSimulation,
    RunSimulationCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.solver import Nec2cSolver

IMPEDANCE_REAL_OHM = 82.6979
IMPEDANCE_IMAG_OHM = 46.3060
SWR = 2.351965
MAX_GAIN_DBI = 2.15


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--nec2c",
        type=Path,
        default=Path(os.environ["NEC2C"]) if "NEC2C" in os.environ else None,
        help="path to the nec2c executable (or set NEC2C)",
    )
    args = parser.parse_args()
    if args.nec2c is None:
        parser.error("--nec2c is required (or set the NEC2C environment variable)")

    solver = Nec2cSolver(args.nec2c)
    model = DipoleParameters(
        frequency_hz=299_800_000.0,
        total_length_m=0.5,
        height_m=0.0,
        wire_radius_m=0.001,
    ).to_antenna(name="NEC-2 manual example 1")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(299_800_000.0),
        segmentation=SegmentationPolicy(segments_per_wire=7),
        include_conductor_losses=False,
        far_field=FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=180.0,
            theta_count=19,
            phi_count=1,
        ),
    )

    result = RunSimulation(solver).execute(RunSimulationCommand(model=model, spec=spec))

    print(f"solver: {result.solver.name} {result.solver.version}")
    print(f"status: {result.status.value}")
    if result.status is not SimulationStatus.COMPLETED or not result.frequencies:
        for diagnostic in result.diagnostics:
            print(f"{diagnostic.severity.value}: {diagnostic.code}: {diagnostic.message}")
        return 1

    frequency = result.frequencies[0]
    impedance = frequency.impedance_ohm
    max_gain = result.max_total_gain_db
    print(f"frequency: {frequency.frequency_hz / 1e6:g} MHz")
    print(f"impedance: {impedance.real:.4f} {impedance.imag:+.4f}j ohm")
    print(f"swr (50 ohm): {frequency.swr:.6f}")
    print(f"max power gain: {max_gain:.2f} dBi" if max_gain is not None else "max power gain: n/a")
    print(f"current samples: {len(frequency.currents)}")
    print(f"far-field points: {len(frequency.far_field)}")

    checks = {
        "impedance real": abs(impedance.real - IMPEDANCE_REAL_OHM) <= 0.05,
        "impedance imag": abs(impedance.imag - IMPEDANCE_IMAG_OHM) <= 0.05,
        "swr": abs(frequency.swr - SWR) <= 0.01,
        "max gain": max_gain is not None and abs(max_gain - MAX_GAIN_DBI) <= 0.2,
    }
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
