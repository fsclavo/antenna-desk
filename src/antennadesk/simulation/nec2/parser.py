"""Parse the text output produced by nec2c.

The parser is intentionally strict about the sections it needs and tolerant of
formatting noise.  It raises ``Nec2ParseError`` when a required section is
missing or malformed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

FREQUENCY_RE = re.compile(
    r"^\s*FREQUENCY\s*[:=]\s*([0-9.+\-Ee]+)\s*MHz",
    re.IGNORECASE,
)
POWER_RE = re.compile(
    r"(INPUT POWER|RADIATED POWER|STRUCTURE LOSS|NETWORK LOSS|EFFICIENCY)"
    r"\s*=\s*([0-9.+\-Ee]+)",
    re.IGNORECASE,
)


class Nec2ParseError(ValueError):
    """The solver output does not contain the expected NEC-2 sections."""


@dataclass(frozen=True, slots=True)
class ParsedInputParameters:
    tag: int
    segment: int
    voltage_v: complex
    current_a: complex
    impedance_ohm: complex
    admittance_s: complex
    power_w: float


@dataclass(frozen=True, slots=True)
class ParsedCurrent:
    segment: int
    tag: int
    x_m: float
    y_m: float
    z_m: float
    length_m: float
    current_a: complex
    magnitude_a: float
    phase_deg: float


@dataclass(frozen=True, slots=True)
class ParsedFarFieldPoint:
    theta_deg: float
    phi_deg: float
    gain_vertical_db: float | None
    gain_horizontal_db: float | None
    gain_total_db: float | None
    axial_ratio: float
    tilt_deg: float
    polarization: str | None
    e_theta_magnitude_v_per_m: float | None
    e_theta_phase_deg: float | None
    e_phi_magnitude_v_per_m: float | None
    e_phi_phase_deg: float | None


@dataclass(frozen=True, slots=True)
class ParsedPowerBudget:
    input_w: float
    radiated_w: float
    structure_loss_w: float
    network_loss_w: float
    efficiency_percent: float


@dataclass(slots=True)
class ParsedFrequency:
    frequency_hz: float
    input_parameters: list[ParsedInputParameters] = field(default_factory=list)
    currents: list[ParsedCurrent] = field(default_factory=list)
    far_field: list[ParsedFarFieldPoint] = field(default_factory=list)
    power_budget: ParsedPowerBudget | None = None


@dataclass(frozen=True, slots=True)
class ParsedNec2Output:
    frequencies: tuple[ParsedFrequency, ...]


def _is_number(token: str) -> bool:
    try:
        float(token)
    except ValueError:
        return False
    return True


def _optional_gain(value: float) -> float | None:
    return None if value <= -999.0 else value


def _parse_impedance_rows(
    lines: list[str],
    start: int,
) -> tuple[list[ParsedInputParameters], int]:
    rows: list[ParsedInputParameters] = []
    index = start + 1
    while index < len(lines) and "No:" not in lines[index]:
        index += 1
    index += 1

    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            break
        tokens = stripped.replace("*", " ").split()
        if len(tokens) < 11:
            break
        try:
            tag = int(tokens[0])
            segment = int(tokens[1])
            values = [float(token) for token in tokens[2:11]]
        except ValueError:
            break

        rows.append(
            ParsedInputParameters(
                tag=tag,
                segment=segment,
                voltage_v=complex(values[0], values[1]),
                current_a=complex(values[2], values[3]),
                impedance_ohm=complex(values[4], values[5]),
                admittance_s=complex(values[6], values[7]),
                power_w=values[8],
            )
        )
        index += 1

    return rows, index


def _parse_current_rows(
    lines: list[str],
    start: int,
) -> tuple[list[ParsedCurrent], int]:
    rows: list[ParsedCurrent] = []
    index = start + 1
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            if rows:
                break
            index += 1
            continue

        tokens = stripped.replace("*", " ").split()
        if len(tokens) >= 10:
            try:
                segment = int(tokens[0])
                tag = int(tokens[1])
                values = [float(token) for token in tokens[2:10]]
            except ValueError:
                if rows:
                    break
                index += 1
                continue

            rows.append(
                ParsedCurrent(
                    segment=segment,
                    tag=tag,
                    x_m=values[0],
                    y_m=values[1],
                    z_m=values[2],
                    length_m=values[3],
                    current_a=complex(values[4], values[5]),
                    magnitude_a=values[6],
                    phase_deg=values[7],
                )
            )
            index += 1
            continue

        if rows:
            break
        index += 1

    return rows, index


def _parse_far_field_rows(
    lines: list[str],
    start: int,
) -> tuple[list[ParsedFarFieldPoint], int]:
    rows: list[ParsedFarFieldPoint] = []
    index = start + 1
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            if rows:
                break
            index += 1
            continue

        tokens = stripped.split()
        if len(tokens) < 7:
            if rows:
                break
            index += 1
            continue

        try:
            theta, phi, vertical, horizontal, total, axial, tilt = (
                float(token) for token in tokens[:7]
            )
        except ValueError:
            if rows:
                break
            index += 1
            continue

        token_index = 7
        polarization: str | None = None
        if token_index < len(tokens) and not _is_number(tokens[token_index]):
            polarization = tokens[token_index]
            token_index += 1

        e_theta_magnitude = e_theta_phase = e_phi_magnitude = e_phi_phase = None
        if token_index + 3 < len(tokens):
            try:
                e_theta_magnitude = float(tokens[token_index])
                e_theta_phase = float(tokens[token_index + 1])
                e_phi_magnitude = float(tokens[token_index + 2])
                e_phi_phase = float(tokens[token_index + 3])
            except ValueError:
                pass

        rows.append(
            ParsedFarFieldPoint(
                theta_deg=theta,
                phi_deg=phi,
                gain_vertical_db=_optional_gain(vertical),
                gain_horizontal_db=_optional_gain(horizontal),
                gain_total_db=_optional_gain(total),
                axial_ratio=axial,
                tilt_deg=tilt,
                polarization=polarization,
                e_theta_magnitude_v_per_m=e_theta_magnitude,
                e_theta_phase_deg=e_theta_phase,
                e_phi_magnitude_v_per_m=e_phi_magnitude,
                e_phi_phase_deg=e_phi_phase,
            )
        )
        index += 1

    return rows, index


def _parse_power_budget(
    lines: list[str],
    start: int,
) -> ParsedPowerBudget | None:
    values: dict[str, float] = {}
    for line in lines[start + 1 : start + 16]:
        match = POWER_RE.search(line)
        if match:
            values[match.group(1).upper()] = float(match.group(2))

    required = {
        "INPUT POWER",
        "RADIATED POWER",
        "STRUCTURE LOSS",
        "NETWORK LOSS",
        "EFFICIENCY",
    }
    if not required.issubset(values):
        return None
    return ParsedPowerBudget(
        input_w=values["INPUT POWER"],
        radiated_w=values["RADIATED POWER"],
        structure_loss_w=values["STRUCTURE LOSS"],
        network_loss_w=values["NETWORK LOSS"],
        efficiency_percent=values["EFFICIENCY"],
    )


def parse_nec2_output(text: str) -> ParsedNec2Output:
    lines = text.splitlines()
    frequencies: list[ParsedFrequency] = []
    current: ParsedFrequency | None = None
    index = 0

    while index < len(lines):
        line = lines[index]
        frequency_match = FREQUENCY_RE.match(line)
        if frequency_match:
            current = ParsedFrequency(frequency_hz=float(frequency_match.group(1)) * 1_000_000.0)
            frequencies.append(current)
            index += 1
            continue

        if "ANTENNA INPUT PARAMETERS" in line:
            if current is None:
                raise Nec2ParseError(
                    f"input parameters found before a frequency at line {index + 1}"
                )
            input_rows, index = _parse_impedance_rows(lines, index)
            current.input_parameters.extend(input_rows)
            continue

        if "CURRENTS AND LOCATION" in line:
            if current is None:
                raise Nec2ParseError(f"currents found before a frequency at line {index + 1}")
            current_rows, index = _parse_current_rows(lines, index)
            current.currents.extend(current_rows)
            continue

        if "RADIATION PATTERNS" in line:
            if current is None:
                raise Nec2ParseError(
                    f"radiation patterns found before a frequency at line {index + 1}"
                )
            far_field_rows, index = _parse_far_field_rows(lines, index)
            current.far_field.extend(far_field_rows)
            continue

        if "POWER BUDGET" in line:
            if current is not None:
                budget = _parse_power_budget(lines, index)
                if budget is not None:
                    current.power_budget = budget
            index += 1
            continue

        index += 1

    if not frequencies:
        raise Nec2ParseError("no frequency blocks found in solver output")
    return ParsedNec2Output(frequencies=tuple(frequencies))
