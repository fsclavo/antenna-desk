# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Import the basic wire geometry and source from an MMANA-GAL .maa file."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.feed import FeedPoint
from ..domain.antennas.geometry import Point3D
from ..domain.antennas.materials import COPPER
from ..domain.antennas.wire import Wire
from ..domain.environment.ground import GroundModel

_SOURCE_PATTERN = re.compile(r"^w(\d+)([a-z])$", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class MmanaImportResult:
    parameters: CustomAntennaParameters
    warnings: tuple[str, ...]


def parse_mmana_file(text: str) -> MmanaImportResult:
    lines = [line.strip() for line in text.splitlines()]
    warnings: list[str] = []

    star_index = next((index for index, line in enumerate(lines) if line == "*"), None)
    if star_index is None:
        raise ValueError("MMANA file has no '*' separator")
    frequency_hz: float | None = None
    for line in lines[star_index + 1 :]:
        if not line or line.startswith("*"):
            continue
        try:
            frequency_hz = float(line) * 1_000_000.0
        except ValueError:
            continue
        break
    if frequency_hz is None:
        raise ValueError("MMANA file has no frequency")

    wire_count_index: int | None = None
    for index, line in enumerate(lines[star_index + 1 :], start=star_index + 1):
        if line.isdigit():
            wire_count_index = index
            break
    if wire_count_index is None:
        raise ValueError("MMANA file has no wire count")
    try:
        wire_count = int(lines[wire_count_index])
    except ValueError as exc:
        raise ValueError("invalid MMANA wire count") from exc
    if wire_count < 1:
        raise ValueError("MMANA file has no wires")

    wires: list[Wire] = []
    for offset in range(wire_count):
        line_index = wire_count_index + 1 + offset
        if line_index >= len(lines):
            raise ValueError("MMANA wire table is incomplete")
        parts = [part.strip() for part in lines[line_index].split(",")]
        if len(parts) < 7:
            raise ValueError(f"invalid MMANA wire row: {lines[line_index]!r}")
        try:
            values = [float(part) for part in parts[:7]]
        except ValueError as exc:
            raise ValueError(f"invalid MMANA wire row: {lines[line_index]!r}") from exc
        wires.append(
            Wire(
                id=f"w{offset + 1}",
                start=Point3D(values[0], values[1], values[2]),
                end=Point3D(values[3], values[4], values[5]),
                radius_m=values[6],
                material=COPPER,
            )
        )

    source_line = next(
        (
            line
            for line in lines[wire_count_index + wire_count + 1 :]
            if _SOURCE_PATTERN.match(line.split(",")[0].strip())
        ),
        None,
    )
    if source_line is None:
        raise ValueError("MMANA file has no wire source")
    source_match = _SOURCE_PATTERN.match(source_line.split(",")[0].strip())
    assert source_match is not None
    source_wire_index = int(source_match.group(1))
    suffix = source_match.group(2).lower()
    if not 1 <= source_wire_index <= len(wires):
        raise ValueError(f"MMANA source references unknown wire {source_wire_index}")
    source_wire = wires[source_wire_index - 1]
    ratio = {"s": 0.0, "e": 1.0, "c": 0.5, "b": 0.5}.get(suffix)
    if ratio is None:
        ratio = 0.5
        warnings.append(f"unknown source suffix {suffix!r}; using wire center")
    warnings.append("MMANA ground and load settings are not imported; using free space")

    return MmanaImportResult(
        parameters=CustomAntennaParameters(
            frequency_hz=frequency_hz,
            wires=tuple(wires),
            feed=FeedPoint(source_wire.id, source_wire.length_m * ratio),
            ground=GroundModel.free_space(),
        ),
        warnings=tuple(warnings),
    )
