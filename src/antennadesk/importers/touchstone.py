# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Parse one-port Touchstone (``.s1p``) measurement files."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

from ..domain.measurement import MeasurementPoint, impedance_from_reflection

DEFAULT_REFERENCE_IMPEDANCE_OHM = 50.0
_FREQUENCY_SCALES = {
    "HZ": 1.0,
    "KHZ": 1_000.0,
    "MHZ": 1_000_000.0,
    "GHZ": 1_000_000_000.0,
}
_DATA_FORMATS = {"RI", "MA", "DB"}
_NUMBER_PATTERN = re.compile(r"[\s,]+")


class TouchstoneError(ValueError):
    """The file is not a supported one-port Touchstone document."""


@dataclass(frozen=True, slots=True)
class ParsedTouchstone:
    points: tuple[MeasurementPoint, ...]
    reference_impedance_ohm: float
    warnings: tuple[str, ...] = ()
    profile: str = "Touchstone"
    mapping: str = ""


@dataclass(frozen=True, slots=True)
class _Options:
    frequency_scale: float = 1.0
    data_format: str = "MA"
    reference_impedance_ohm: float = DEFAULT_REFERENCE_IMPEDANCE_OHM


def looks_like_touchstone(text: str) -> bool:
    """Return whether the first meaningful line is a Touchstone option line."""

    text = text.lstrip("\ufeff")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("!"):
            continue
        return stripped.startswith("#")
    return False


def _parse_options(line: str, line_number: int) -> _Options:
    tokens = line[1:].split()
    if not tokens:
        raise TouchstoneError(f"line {line_number}: empty option line")
    frequency_scale = 1.0
    data_format = "MA"
    reference_impedance_ohm = DEFAULT_REFERENCE_IMPEDANCE_OHM
    index = 0
    while index < len(tokens):
        part = tokens[index].upper()
        if part in _FREQUENCY_SCALES:
            frequency_scale = _FREQUENCY_SCALES[part]
        elif part == "S":
            pass
        elif part in {"Y", "Z", "H", "G"}:
            raise TouchstoneError(
                f"line {line_number}: only S-parameter data is supported, not {part}"
            )
        elif part in _DATA_FORMATS:
            data_format = part
        elif part == "R":
            index += 1
            if index >= len(tokens):
                raise TouchstoneError(f"line {line_number}: missing reference impedance")
            try:
                reference_impedance_ohm = float(tokens[index])
            except ValueError as exc:
                raise TouchstoneError(f"line {line_number}: invalid reference impedance") from exc
            if not math.isfinite(reference_impedance_ohm) or reference_impedance_ohm <= 0:
                raise TouchstoneError(f"line {line_number}: invalid reference impedance")
        else:
            raise TouchstoneError(f"line {line_number}: unsupported option {tokens[index]!r}")
        index += 1
    return _Options(
        frequency_scale=frequency_scale,
        data_format=data_format,
        reference_impedance_ohm=reference_impedance_ohm,
    )


def _reflection_from_values(
    first: float,
    second: float,
    data_format: str,
) -> complex:
    if data_format == "RI":
        return complex(first, second)
    if data_format == "MA":
        angle = math.radians(second)
        return first * complex(math.cos(angle), math.sin(angle))
    magnitude = math.pow(10.0, first / 20.0)
    angle = math.radians(second)
    return magnitude * complex(math.cos(angle), math.sin(angle))


def parse_touchstone_s2p(text: str, *, port: int = 1) -> ParsedTouchstone:
    """Parse a two-port Touchstone file and use only the selected port.

    ``port=1`` reads S11; ``port=2`` reads S22 and requires full 9-value rows.
    S21 and S12 are never used as the measurement, even when S11 is absent.
    """

    if port not in {1, 2}:
        raise TouchstoneError("port must be 1 or 2")
    if not text.strip():
        raise TouchstoneError("the Touchstone file is empty")

    text = text.lstrip("\ufeff")
    options = _Options()
    options_seen = False
    points: list[MeasurementPoint] = []
    warnings: list[str] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            if options_seen:
                raise TouchstoneError(f"line {line_number}: multiple option lines")
            options = _parse_options(line, line_number)
            options_seen = True
            continue
        values = [value for value in _NUMBER_PATTERN.split(line) if value]
        if len(values) not in (3, 5, 9):
            raise TouchstoneError(
                f"line {line_number}: expected 3, 5, or 9 numeric values for a 2-port file"
            )
        if port == 2 and len(values) != 9:
            raise TouchstoneError(f"line {line_number}: S22 requires full 9-value 2-port rows")
        try:
            numbers = [float(value) for value in values]
        except ValueError as exc:
            raise TouchstoneError(f"line {line_number}: invalid numeric value") from exc
        if not all(math.isfinite(number) for number in numbers):
            raise TouchstoneError(f"line {line_number}: non-finite numeric value")
        frequency_hz = numbers[0] * options.frequency_scale
        if frequency_hz <= 0.0:
            raise TouchstoneError(f"line {line_number}: frequency must be positive")
        first = numbers[1] if port == 1 else numbers[7]
        second = numbers[2] if port == 1 else numbers[8]
        reflection = _reflection_from_values(first, second, options.data_format)
        if abs(reflection) >= 1.0:
            warnings.append(f"line {line_number}: reflection coefficient magnitude >= 1 skipped")
            continue
        points.append(
            MeasurementPoint(
                frequency_hz=frequency_hz,
                impedance_ohm=impedance_from_reflection(
                    reflection,
                    options.reference_impedance_ohm,
                ),
            )
        )
    if not points:
        raise TouchstoneError("no valid two-port measurement points found")
    return ParsedTouchstone(
        points=tuple(points),
        reference_impedance_ohm=options.reference_impedance_ohm,
        warnings=tuple(warnings),
        profile="Touchstone S2P port 1" if port == 1 else "Touchstone S2P port 2",
        mapping="frequency, S11" if port == 1 else "frequency, S22",
    )


def parse_touchstone_s1p(text: str) -> ParsedTouchstone:
    """Parse a one-port Touchstone file and convert S11 to impedance.

    The option line defaults to ``# Hz S MA R 50``. Supported formats are RI,
    MA, and DB; supported frequency units are Hz, kHz, MHz, and GHz.
    """

    if not text.strip():
        raise TouchstoneError("the Touchstone file is empty")

    text = text.lstrip("\ufeff")
    options = _Options()
    options_seen = False
    points: list[MeasurementPoint] = []
    warnings: list[str] = []

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("!", 1)[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            if options_seen:
                raise TouchstoneError(f"line {line_number}: multiple option lines")
            options = _parse_options(line, line_number)
            options_seen = True
            continue

        values = [value for value in _NUMBER_PATTERN.split(line) if value]
        if len(values) not in (2, 3):
            raise TouchstoneError(f"line {line_number}: expected frequency and one-port S11 data")
        try:
            numbers = [float(value) for value in values]
        except ValueError as exc:
            raise TouchstoneError(f"line {line_number}: invalid numeric value") from exc
        if not all(math.isfinite(number) for number in numbers):
            raise TouchstoneError(f"line {line_number}: non-finite numeric value")

        frequency_hz = numbers[0] * options.frequency_scale
        if frequency_hz <= 0.0:
            raise TouchstoneError(f"line {line_number}: frequency must be positive")
        if len(numbers) == 2:
            second = 0.0
            warnings.append(f"line {line_number}: missing angle or imaginary part assumed 0")
        else:
            second = numbers[2]
        reflection = _reflection_from_values(numbers[1], second, options.data_format)
        if abs(reflection) >= 1.0:
            warnings.append(f"line {line_number}: reflection coefficient magnitude >= 1 skipped")
            continue
        points.append(
            MeasurementPoint(
                frequency_hz=frequency_hz,
                impedance_ohm=impedance_from_reflection(
                    reflection,
                    options.reference_impedance_ohm,
                ),
            )
        )

    if not points:
        raise TouchstoneError("no valid one-port measurement points found")
    return ParsedTouchstone(
        points=tuple(points),
        reference_impedance_ohm=options.reference_impedance_ohm,
        warnings=tuple(warnings),
        profile="Touchstone S1P",
        mapping="frequency, S11",
    )
