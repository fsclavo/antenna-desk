#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parse the text output produced by nec2c.

This is a deliberately small Phase 0 parser.  It is not the production
normalizer; it exists to prove that the information needed by AntennaDesk is
present and can be extracted without depending on private solver state.

The parser only understands the sections used by the Phase 0 reference cases:
frequency, antenna input parameters, currents and radiation patterns.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

FREQUENCY_RE = re.compile(r"FREQUENCY\s*:\s*([0-9.+\-Ee]+)\s*MHz")
NUMBER_RE = re.compile(r"[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[Ee][+-]?\d+)?")


def _parse_impedance_block(lines: list[str], start: int) -> list[dict[str, Any]]:
    """Parse one ANTENNA INPUT PARAMETERS block.

    nec2c prints an 11-column row:
      tag segment V_real V_imag I_real I_imag Z_real Z_imag Y_real Y_imag P
    """
    rows: list[dict[str, Any]] = []
    i = start
    while i < len(lines) and "No:" not in lines[i] and "REAL" not in lines[i]:
        i += 1
    i += 1

    while i < len(lines):
        line = lines[i].strip().replace("*", " ")
        if not line:
            break
        tokens = line.split()
        if len(tokens) < 11:
            break
        try:
            tag = int(tokens[0])
            segment = int(tokens[1])
            values = [float(token) for token in tokens[2:11]]
        except ValueError:
            break

        rows.append(
            {
                "tag": tag,
                "segment": segment,
                "voltage_real": values[0],
                "voltage_imag": values[1],
                "current_real": values[2],
                "current_imag": values[3],
                "impedance_real": values[4],
                "impedance_imag": values[5],
                "admittance_real": values[6],
                "admittance_imag": values[7],
                "power_w": values[8],
            }
        )
        i += 1

    return rows


def parse_output(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    frequencies_hz = [float(match.group(1)) * 1_000_000.0 for match in FREQUENCY_RE.finditer(text)]

    impedances: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if "ANTENNA INPUT PARAMETERS" in line:
            impedances.extend(_parse_impedance_block(lines, index))

    return {
        "path": str(path),
        "frequencies_hz": frequencies_hz,
        "input_impedances": impedances,
        "radiation_pattern_sections": sum(
            1 for line in lines if "RADIATION PATTERNS" in line
        ),
        "current_sections": sum(
            1 for line in lines if "CURRENTS AND LOCATION" in line
        ),
        "power_budget_sections": sum(
            1 for line in lines if "POWER BUDGET" in line
        ),
        "has_run_time": "TOTAL RUN TIME" in text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="nec2c output file")
    args = parser.parse_args()

    if not args.output.is_file():
        parser.error(f"file not found: {args.output}")

    print(json.dumps(parse_output(args.output), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
