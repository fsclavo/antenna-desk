#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run the Phase 0 nec2c reference cases and compare them to published values.

The reference values live in ``expected/reference_values.json`` and come from
the printed NEC-2 User's Guide output, not from nec2c itself.

Cases are copied to a short temporary directory before execution because the
nec2c command-line parser has a small fixed buffer for input file names.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from parse_nec2c import parse_output

PHASE0_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _run_case(nec2c: Path, source: Path, workdir: Path, stem: str) -> Path:
    input_path = workdir / f"{stem}.nec"
    output_path = workdir / f"{stem}.out"
    shutil.copy2(source, input_path)
    completed = subprocess.run(
        [str(nec2c), "-i", input_path.name, "-o", output_path.name],
        cwd=workdir,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{source.name}: nec2c exited with {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    if not output_path.is_file():
        raise RuntimeError(f"{source.name}: nec2c produced no output file")
    return output_path


def _impedance_check(case: dict[str, Any], parsed: dict[str, Any]) -> Check:
    name = case["name"]
    expected = case["expected_impedance_ohm"]
    tolerance = float(
        case.get(
            "impedance_absolute_tolerance_ohm",
            0.05,
        )
    )
    impedances = parsed["input_impedances"]
    if not impedances:
        return Check(name, False, "no ANTENNA INPUT PARAMETERS block found")

    actual = impedances[0]
    real_error = abs(actual["impedance_real"] - expected["real"])
    imag_error = abs(actual["impedance_imag"] - expected["imag"])
    passed = real_error <= tolerance and imag_error <= tolerance
    detail = (
        f"Z={actual['impedance_real']:.4f}{actual['impedance_imag']:+.4f}j ohm; "
        f"expected {expected['real']:.4f}{expected['imag']:+.4f}j; "
        f"|dR|={real_error:.4f}, |dX|={imag_error:.4f}, tol={tolerance}"
    )
    return Check(name, passed, detail)


def _count_check(
    name: str,
    expected: int,
    actual: int,
    label: str,
) -> Check:
    return Check(
        name,
        actual == expected,
        f"{label}: expected {expected}, got {actual}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--nec2c",
        type=Path,
        required=True,
        help="path to the nec2c executable to test",
    )
    parser.add_argument(
        "--expected",
        type=Path,
        default=PHASE0_ROOT / "expected" / "reference_values.json",
        help="reference values file",
    )
    parser.add_argument(
        "--keep",
        action="store_true",
        help="keep the temporary work directory and print its path",
    )
    args = parser.parse_args()

    nec2c = args.nec2c.resolve()
    if not nec2c.is_file():
        parser.error(f"nec2c executable not found: {nec2c}")

    specification = json.loads(args.expected.read_text(encoding="utf-8"))
    checks: list[Check] = []

    workdir = Path(tempfile.mkdtemp(prefix="adp0-"))
    try:
        for index, case in enumerate(specification["cases"], start=1):
            source = PHASE0_ROOT / case["file"]
            output = _run_case(nec2c, source, workdir, f"c{index}")
            parsed = parse_output(output)

            checks.append(_impedance_check(case, parsed))
            checks.append(
                _count_check(
                    case["name"],
                    int(case.get("expected_frequency_count", 1)),
                    len(parsed["frequencies_hz"]),
                    "frequency count",
                )
            )
            checks.append(
                _count_check(
                    case["name"],
                    int(case.get("expected_radiation_pattern_sections", 0)),
                    int(parsed["radiation_pattern_sections"]),
                    "radiation pattern sections",
                )
            )
            checks.append(
                Check(
                    case["name"],
                    bool(parsed["has_run_time"]),
                    "output contains TOTAL RUN TIME",
                )
            )

        for index, case in enumerate(specification.get("smoke_cases", []), start=101):
            source = PHASE0_ROOT / case["file"]
            output = _run_case(nec2c, source, workdir, f"c{index}")
            parsed = parse_output(output)

            checks.append(
                _count_check(
                    case["name"],
                    int(case["expected_frequency_count"]),
                    len(parsed["frequencies_hz"]),
                    "frequency count",
                )
            )
            checks.append(
                _count_check(
                    case["name"],
                    int(case["expected_radiation_pattern_sections"]),
                    int(parsed["radiation_pattern_sections"]),
                    "radiation pattern sections",
                )
            )
            checks.append(
                _count_check(
                    case["name"],
                    int(case["expected_current_sections"]),
                    int(parsed["current_sections"]),
                    "current sections",
                )
            )

        width = max(len(check.name) for check in checks)
        for check in checks:
            status = "PASS" if check.passed else "FAIL"
            print(f"[{status}] {check.name:<{width}}  {check.detail}")

        if args.keep:
            print(f"\nWork directory kept at: {workdir}")

        failures = [check for check in checks if not check.passed]
        print(f"\n{len(checks) - len(failures)}/{len(checks)} checks passed")
        if failures:
            print(f"{len(failures)} check(s) failed", file=sys.stderr)
            return 1
        return 0
    finally:
        if not args.keep:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
