# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Import common VNA CSV exports."""

from __future__ import annotations

import csv
import io
import math
import re
from dataclasses import dataclass

from ..domain.measurement import MeasurementPoint, impedance_from_reflection

DEFAULT_REFERENCE_IMPEDANCE_OHM = 50.0
MAX_VNA_TEXT_CHARS = 16 * 1024 * 1024
MAX_VNA_ROWS = 100_000
_UNIT_PATTERN = re.compile(r"(?i)(ghz|mhz|khz|hz)\s*$")


class VnaCsvError(ValueError):
    """The CSV does not contain a supported measurement table."""


@dataclass(frozen=True, slots=True)
class VnaColumnMapping:
    """Explicit column mapping used when automatic detection is ambiguous."""

    frequency: str
    mode: str
    first: str
    second: str
    reference_impedance_ohm: float = DEFAULT_REFERENCE_IMPEDANCE_OHM

    def __post_init__(self) -> None:
        if self.mode not in {"rx", "complex", "polar"}:
            raise ValueError("mapping mode must be rx, complex, or polar")
        if self.reference_impedance_ohm <= 0.0:
            raise ValueError("reference impedance must be positive")


@dataclass(frozen=True, slots=True)
class ParsedVnaCsv:
    points: tuple[MeasurementPoint, ...]
    reference_impedance_ohm: float
    warnings: tuple[str, ...] = ()
    profile: str = "Generic CSV"
    mapping: str = ""


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
        .replace("Ω", "")
        .replace("ω", "")
    )


def _find_column(headers: list[str], names: set[str]) -> int | None:
    for index, header in enumerate(headers):
        if header in names:
            return index
    return None


def _find_header(headers: list[str], name: str) -> int:
    normalized = _normalize_header(name)
    for index, header in enumerate(headers):
        if header == normalized:
            return index
    raise VnaCsvError(f"mapped column not found: {name}")


def vna_csv_headers(text: str) -> tuple[str, ...]:
    """Return the first data row's raw headers for a manual mapping dialog."""

    lines = [
        line
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "*", "!"))
    ]
    if not lines:
        return ()
    try:
        dialect = csv.Sniffer().sniff("\n".join(lines[:5]), delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(lines[0]), dialect))
    return tuple(rows[0]) if rows else ()


def parse_number(token: str) -> float:
    """Parse locale-aware decimal separators and simple unit suffixes."""

    value = token.strip().replace("\u00a0", "").replace("\u2212", "-")
    value = re.sub(r"[a-zA-ZΩ°µ]+$", "", value).strip()
    if not value:
        raise ValueError("empty numeric value")
    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        value = value.replace(",", "") if value.count(",") > 1 else value.replace(",", ".")
    elif value.count(".") > 1:
        value = value.replace(".", "")
    return float(value)


def _frequency_unit_scale(token: str) -> float | None:
    match = _UNIT_PATTERN.search(token)
    if match is None:
        return None
    return {
        "hz": 1.0,
        "khz": 1_000.0,
        "mhz": 1_000_000.0,
        "ghz": 1_000_000_000.0,
    }[match.group(1).lower()]


def _detect_profile(text: str) -> str:
    lowered = text.lower()
    for marker, profile in (
        ("nanovna", "NanoVNA Saver"),
        ("rigexpert", "RigExpert"),
        ("minivna", "miniVNA"),
        ("dg8saq", "DG8SAQ"),
    ):
        if marker in lowered:
            return profile
    return "Generic CSV"


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


def parse_vna_csv(
    text: str,
    *,
    mapping: VnaColumnMapping | None = None,
) -> ParsedVnaCsv:
    """Parse locale-aware frequency/R/X, S11, or magnitude/phase CSV data."""

    if len(text) > MAX_VNA_TEXT_CHARS:
        raise VnaCsvError(
            f"the CSV is too large ({len(text)} characters; limit is {MAX_VNA_TEXT_CHARS})"
        )
    lines = [
        line
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "*", "!"))
    ]
    if not lines:
        raise VnaCsvError("the CSV is empty")
    if len(lines) > MAX_VNA_ROWS:
        raise VnaCsvError(f"the CSV has too many rows ({len(lines)}; limit is {MAX_VNA_ROWS})")
    try:
        dialect = csv.Sniffer().sniff("\n".join(lines[:5]), delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel

    rows = list(csv.reader(io.StringIO("\n".join(lines)), dialect))
    raw_headers = rows[0]
    headers = [_normalize_header(value) for value in raw_headers]
    frequency_index: int
    first_index: int
    second_index: int
    mode: str
    if mapping is not None:
        frequency_index = _find_header(headers, mapping.frequency)
        first_index = _find_header(headers, mapping.first)
        second_index = _find_header(headers, mapping.second)
        mode = mapping.mode
    else:
        detected_frequency = _find_column(
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
                "frequencyghz",
                "freqghz",
            },
        )
        if detected_frequency is None:
            raise VnaCsvError("no frequency column found")
        frequency_index = detected_frequency

        r_index = _find_column(headers, {"r", "rohm", "resistance", "resistanceohm"})
        x_index = _find_column(headers, {"x", "xohm", "reactance", "reactanceohm"})
        real_index = _find_column(headers, {"s11real", "s11re", "s11r", "re", "real"})
        imag_index = _find_column(
            headers,
            {"s11imag", "s11im", "s11x", "im", "imag", "imaginary"},
        )
        magnitude_index = _find_column(
            headers,
            {"s11mag", "s11magnitude", "magnitude", "mag"},
        )
        phase_index = _find_column(
            headers,
            {"s11phase", "phase", "phasedeg", "phaseangle"},
        )

        if r_index is not None and x_index is not None:
            mode = "rx"
            first_index, second_index = r_index, x_index
        elif real_index is not None and imag_index is not None:
            mode = "complex"
            first_index, second_index = real_index, imag_index
        elif magnitude_index is not None and phase_index is not None:
            mode = "polar"
            first_index, second_index = magnitude_index, phase_index
        else:
            raise VnaCsvError("no supported impedance or S11 columns found")

    raw_frequencies: list[float] = []
    parsed_rows: list[tuple[str, float, float, float]] = []
    warnings: list[str] = []
    for line_number, row in enumerate(rows[1:], start=2):
        try:
            raw_frequency = row[frequency_index]
            frequency = parse_number(raw_frequency)
            first = parse_number(row[first_index])
            second = parse_number(row[second_index])
        except (IndexError, ValueError) as exc:
            raise VnaCsvError(
                f"row {line_number}: invalid numeric value in a mapped column: {exc}"
            ) from exc
        raw_frequencies.append(frequency)
        parsed_rows.append((raw_frequency, frequency, first, second))

    if not parsed_rows:
        raise VnaCsvError("no valid measurement rows found")

    header_scale = _frequency_scale(headers[frequency_index], raw_frequencies)
    reference = (
        mapping.reference_impedance_ohm if mapping is not None else DEFAULT_REFERENCE_IMPEDANCE_OHM
    )
    points: list[MeasurementPoint] = []
    for raw_frequency, frequency, first, second in parsed_rows:
        scale = _frequency_unit_scale(raw_frequency) or header_scale
        if mode == "rx":
            impedance = complex(first, second)
        elif mode == "complex":
            reflection = complex(first, second)
            if abs(reflection) >= 1.0:
                warnings.append("reflection coefficient magnitude >= 1 was skipped")
                continue
            impedance = impedance_from_reflection(reflection, reference)
        else:
            reflection = first * complex(
                math.cos(math.radians(second)),
                math.sin(math.radians(second)),
            )
            if abs(reflection) >= 1.0:
                warnings.append("reflection coefficient magnitude >= 1 was skipped")
                continue
            impedance = impedance_from_reflection(reflection, reference)
        points.append(
            MeasurementPoint(
                frequency_hz=frequency * scale,
                impedance_ohm=impedance,
            )
        )
    if not points:
        raise VnaCsvError("no valid measurement points found")
    profile = _detect_profile(text)
    mapping_text = (
        f"frequency={raw_headers[frequency_index]}; "
        f"mode={mode}; first={raw_headers[first_index]}; "
        f"second={raw_headers[second_index]}"
    )
    return ParsedVnaCsv(
        points=tuple(points),
        reference_impedance_ohm=reference,
        warnings=tuple(warnings),
        profile=profile,
        mapping=mapping_text,
    )
