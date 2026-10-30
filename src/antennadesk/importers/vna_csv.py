# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Import common VNA CSV exports."""

from __future__ import annotations

import csv
import io
import math
from dataclasses import dataclass

from ..domain.measurement import MeasurementPoint

DEFAULT_REFERENCE_IMPEDANCE_OHM = 50.0


class VnaCsvError(ValueError):
    """The CSV does not contain a supported measurement table."""


@dataclass(frozen=True, slots=True)
class ParsedVnaCsv:
    points: tuple[MeasurementPoint, ...]
    reference_impedance_ohm: float
    warnings: tuple[str, ...] = ()


def _normalize_header(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
        .replace("°", "")
    )


def _find_column(headers: list[str], names: set[str]) -> int | None:
    for index, header in enumerate(headers):
        if header in names:
            return index
    return None


def _frequency_scale(header: str, values: list[float]) -> float:
    if "ghz" in header:
        return 1_000_000_000.0
    if "mhz" in header:
        return 1_000_000.0
    if "khz" in header:
        return 1_000.0
    if "hz" in header:
        return 1.0
    maximum = max(values) if values else 0.0
    if maximum > 1_000_000.0:
        return 1.0
    if maximum > 1_000.0:
        return 1_000_000.0
    return 1_000_000.0


def parse_vna_csv(text: str) -> ParsedVnaCsv:
    """Parse frequency/R/X, S11 real/imaginary, or magnitude/phase CSV data."""

    lines = [
        line
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "*", "!"))
    ]
    if not lines:
        raise VnaCsvError("the CSV is empty")
    try:
        dialect = csv.Sniffer().sniff("\n".join(lines[:5]), delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel

    rows = list(csv.reader(io.StringIO("\n".join(lines)), dialect))
    headers = [_normalize_header(value) for value in rows[0]]
    frequency_index = _find_column(
        headers,
        {
            "frequencyhz",
            "freqhz",
            "frequency",
            "freq",
            "frequencymhz",
            "freqmhz",
            "frequencykhz",
            "freqkhz",
        },
    )
    if frequency_index is None:
        raise VnaCsvError("no frequency column found")

    r_index = _find_column(headers, {"r", "rohm", "resistance", "resistanceohm"})
    x_index = _find_column(headers, {"x", "xohm", "reactance", "reactanceohm"})
    real_index = _find_column(headers, {"s11real", "s11re", "re", "real"})
    imag_index = _find_column(headers, {"s11imag", "s11im", "im", "imag", "imaginary"})
    magnitude_index = _find_column(headers, {"s11mag", "s11magnitude", "magnitude", "mag"})
    phase_index = _find_column(headers, {"s11phase", "phase", "phasedeg", "phaseangle"})

    mode: str
    if r_index is not None and x_index is not None:
        mode = "rx"
    elif real_index is not None and imag_index is not None:
        mode = "complex"
    elif magnitude_index is not None and phase_index is not None:
        mode = "polar"
    else:
        raise VnaCsvError("no supported impedance or S11 columns found")

    raw_frequencies: list[float] = []
    parsed_rows: list[tuple[float, float, float]] = []
    warnings: list[str] = []
    for line_number, row in enumerate(rows[1:], start=2):
        try:
            frequency = float(row[frequency_index])
            if mode == "rx":
                assert r_index is not None and x_index is not None
                first = float(row[r_index])
                second = float(row[x_index])
            elif mode == "complex":
                assert real_index is not None and imag_index is not None
                first = float(row[real_index])
                second = float(row[imag_index])
            else:
                assert magnitude_index is not None and phase_index is not None
                first = float(row[magnitude_index])
                second = float(row[phase_index])
        except (IndexError, ValueError):
            warnings.append(f"skipped row {line_number}: invalid numeric value")
            continue
        raw_frequencies.append(frequency)
        parsed_rows.append((frequency, first, second))

    if not parsed_rows:
        raise VnaCsvError("no valid measurement rows found")

    scale = _frequency_scale(headers[frequency_index], raw_frequencies)
    reference = DEFAULT_REFERENCE_IMPEDANCE_OHM
    points: list[MeasurementPoint] = []
    for frequency, first, second in parsed_rows:
        if mode == "rx":
            impedance = complex(first, second)
        elif mode == "complex":
            reflection = complex(first, second)
            if abs(reflection) >= 1.0:
                warnings.append("reflection coefficient magnitude >= 1 was skipped")
                continue
            impedance = reference * (1.0 + reflection) / (1.0 - reflection)
        else:
            reflection = first * complex(
                math.cos(math.radians(second)),
                math.sin(math.radians(second)),
            )
            if abs(reflection) >= 1.0:
                warnings.append("reflection coefficient magnitude >= 1 was skipped")
                continue
            impedance = reference * (1.0 + reflection) / (1.0 - reflection)
        points.append(
            MeasurementPoint(
                frequency_hz=frequency * scale,
                impedance_ohm=impedance,
            )
        )
    if not points:
        raise VnaCsvError("no valid measurement points found")
    return ParsedVnaCsv(
        points=tuple(points),
        reference_impedance_ohm=reference,
        warnings=tuple(warnings),
    )
