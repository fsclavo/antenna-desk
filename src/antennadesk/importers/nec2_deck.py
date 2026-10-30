# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Import a practical subset of NEC-2 input decks as custom wire designs."""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.feed import FeedPoint
from ..domain.antennas.geometry import Point3D
from ..domain.antennas.load import ParallelLoad, SeriesLoad
from ..domain.antennas.materials import COPPER
from ..domain.antennas.wire import Wire
from ..domain.environment.ground import GroundModel


@dataclass(frozen=True, slots=True)
class NecImportResult:
    parameters: CustomAntennaParameters
    warnings: tuple[str, ...]


@dataclass(slots=True)
class _WireSpec:
    tag: int
    segments: int
    start: Point3D
    end: Point3D
    radius_m: float


def _number(value: str, line_number: int, field: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"invalid {field} on NEC line {line_number}: {value!r}") from exc


def _integer(value: str, line_number: int, field: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"invalid {field} on NEC line {line_number}: {value!r}") from exc


def parse_nec2_deck(text: str) -> NecImportResult:
    wires: list[_WireSpec] = []
    tags: set[int] = set()
    feed: tuple[int, int] | None = None
    frequency_hz: float | None = None
    ground = GroundModel.free_space()
    ground_present = False
    loads: list[SeriesLoad | ParallelLoad] = []
    warnings: list[str] = []
    load_index = 1

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("CM") or line.startswith("CE"):
            continue
        parts = line.replace(",", " ").split()
        card = parts[0].upper()

        if card == "GW":
            if len(parts) < 10:
                raise ValueError(f"incomplete GW card on NEC line {line_number}")
            tag = _integer(parts[1], line_number, "GW tag")
            segments = _integer(parts[2], line_number, "GW segments")
            if tag in tags:
                raise ValueError(f"duplicate GW tag {tag} on NEC line {line_number}")
            if segments < 1:
                raise ValueError(f"GW segments must be positive on NEC line {line_number}")
            tags.add(tag)
            wires.append(
                _WireSpec(
                    tag=tag,
                    segments=segments,
                    start=Point3D(
                        _number(parts[3], line_number, "GW X1"),
                        _number(parts[4], line_number, "GW Y1"),
                        _number(parts[5], line_number, "GW Z1"),
                    ),
                    end=Point3D(
                        _number(parts[6], line_number, "GW X2"),
                        _number(parts[7], line_number, "GW Y2"),
                        _number(parts[8], line_number, "GW Z2"),
                    ),
                    radius_m=_number(parts[9], line_number, "GW radius"),
                )
            )
        elif card == "EX":
            if len(parts) < 4:
                raise ValueError(f"incomplete EX card on NEC line {line_number}")
            source_type = _integer(parts[1], line_number, "EX type")
            if source_type != 0:
                warnings.append(f"line {line_number}: EX type {source_type} ignored")
                continue
            tag = _integer(parts[2], line_number, "EX tag")
            segment = _integer(parts[3], line_number, "EX segment")
            if feed is not None:
                warnings.append(f"line {line_number}: additional EX source ignored")
            else:
                feed = (tag, segment)
        elif card == "FR":
            if len(parts) < 6:
                raise ValueError(f"incomplete FR card on NEC line {line_number}")
            if frequency_hz is not None:
                warnings.append(f"line {line_number}: additional FR card ignored")
                continue
            frequency_hz = _number(parts[5], line_number, "FR frequency") * 1_000_000.0
            count = _integer(parts[2], line_number, "FR count")
            if count > 1:
                warnings.append(
                    f"line {line_number}: only the first frequency of a sweep is imported"
                )
        elif card == "GN":
            if len(parts) < 2:
                raise ValueError(f"incomplete GN card on NEC line {line_number}")
            ground_type = _integer(parts[1], line_number, "GN type")
            ground_present = True
            if ground_type == 1:
                ground = GroundModel.perfect()
            elif ground_type == 0 and len(parts) >= 7:
                ground = GroundModel.finite(
                    relative_permittivity=_number(parts[5], line_number, "GN permittivity"),
                    conductivity_s_per_m=_number(parts[6], line_number, "GN conductivity"),
                )
            else:
                warnings.append(f"line {line_number}: unsupported GN type {ground_type}")
        elif card == "GE":
            if len(parts) >= 2 and _integer(parts[1], line_number, "GE flag") != 0:
                ground_present = True
                if ground.kind.value == "free_space":
                    ground = GroundModel.perfect()
        elif card in {"LD", "TL", "GM", "GR", "RP", "PT", "IS", "KH", "NE", "NH", "XQ"}:
            if card == "LD":
                if len(parts) < 8:
                    raise ValueError(f"incomplete LD card on NEC line {line_number}")
                load_type = _integer(parts[1], line_number, "LD type")
                tag = _integer(parts[2], line_number, "LD tag")
                first_segment = _integer(parts[3], line_number, "LD first segment")
                last_segment = _integer(parts[4], line_number, "LD last segment")
                wire = next((item for item in wires if item.tag == tag), None)
                if wire is None:
                    warnings.append(f"line {line_number}: LD references unknown tag {tag}")
                    continue
                if load_type not in {0, 1}:
                    if load_type != 5:
                        warnings.append(f"line {line_number}: LD type {load_type} ignored")
                    continue
                if first_segment != last_segment:
                    warnings.append(f"line {line_number}: LD segment range uses its first segment")
                ratio = (first_segment - 0.5) / wire.segments
                offset = wire.start.distance_to(wire.end) * min(max(ratio, 0.0), 1.0)
                load_class = SeriesLoad if load_type == 0 else ParallelLoad
                loads.append(
                    load_class(
                        id=f"load-{load_index}",
                        wire_id=f"w{tag}",
                        offset_m=offset,
                        resistance_ohm=max(_number(parts[5], line_number, "LD R"), 0.0),
                        inductance_h=max(_number(parts[6], line_number, "LD L"), 0.0),
                        capacitance_f=max(_number(parts[7], line_number, "LD C"), 0.0),
                    )
                )
                load_index += 1
            else:
                warnings.append(f"line {line_number}: unsupported {card} card ignored")
        elif card == "EN":
            break
        else:
            warnings.append(f"line {line_number}: unsupported {card} card ignored")

    if not wires:
        raise ValueError("NEC deck contains no GW wire cards")
    if feed is None:
        raise ValueError("NEC deck contains no EX voltage source")
    if frequency_hz is None:
        raise ValueError("NEC deck contains no FR frequency")
    feed_tag, feed_segment = feed
    feed_wire = next((item for item in wires if item.tag == feed_tag), None)
    if feed_wire is None:
        raise ValueError(f"EX references unknown GW tag {feed_tag}")
    if not 1 <= feed_segment <= feed_wire.segments:
        raise ValueError(
            f"EX segment {feed_segment} is outside GW tag {feed_tag} "
            f"with {feed_wire.segments} segments"
        )

    model_wires = tuple(
        Wire(
            id=f"w{wire.tag}",
            start=wire.start,
            end=wire.end,
            radius_m=wire.radius_m,
            material=COPPER,
        )
        for wire in wires
    )
    feed_offset = (
        (feed_segment - 0.5) / feed_wire.segments * feed_wire.start.distance_to(feed_wire.end)
    )
    if not ground_present:
        warnings.append("GE absent: using free-space ground")

    return NecImportResult(
        parameters=CustomAntennaParameters(
            frequency_hz=frequency_hz,
            wires=model_wires,
            feed=FeedPoint(f"w{feed_tag}", feed_offset),
            ground=ground,
            loads=tuple(loads),
        ),
        warnings=tuple(warnings),
    )
