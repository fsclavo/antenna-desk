# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Wire, feed, and load schedule for construction sheets.

A dimensioned sketch can hide a low-priority dimension when space is tight.
The schedule is the authoritative construction data: every canonical wire with
its endpoints, length, diameter, and material, plus the feed point.
"""

from __future__ import annotations

import csv
import html
import io
import math
from dataclasses import dataclass
from pathlib import Path

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.endfed import (
    BEND_RADIATOR_ID,
    BEND_RADIATOR_TOP_ID,
    FEED_SECTION_ID,
    LOADING_COIL_SECTION_ID,
    RADIATOR_ID,
    RADIATOR_TOP_ID,
    is_model_only_wire,
)
from ..domain.antennas.geometry import Point3D
from ..domain.antennas.wire import Wire
from ..domain.projects.bom_costs import BomCostRecord
from ..domain.projects.project import DesignVariant
from .localization import Labeler, identity_labeler

_ENDFED_PARTITION_IDS = frozenset(
    {
        FEED_SECTION_ID,
        RADIATOR_ID,
        LOADING_COIL_SECTION_ID,
        RADIATOR_TOP_ID,
        BEND_RADIATOR_ID,
        BEND_RADIATOR_TOP_ID,
    }
)
_ENDFED_PARTITION_MARKERS = frozenset(
    {
        FEED_SECTION_ID,
        LOADING_COIL_SECTION_ID,
        RADIATOR_TOP_ID,
        BEND_RADIATOR_ID,
        BEND_RADIATOR_TOP_ID,
    }
)

WIRE_SCHEDULE_HEADER = (
    "index",
    "wire_id",
    "start_x_m",
    "start_y_m",
    "start_z_m",
    "end_x_m",
    "end_y_m",
    "end_z_m",
    "length_m",
    "diameter_mm",
    "material",
)


@dataclass(frozen=True, slots=True)
class WireScheduleRow:
    """One canonical wire in a construction schedule."""

    index: int
    wire_id: str
    start: Point3D
    end: Point3D
    length_m: float
    radius_m: float
    material: str

    @property
    def diameter_mm(self) -> float:
        return self.radius_m * 2000.0

    def csv_row(self) -> tuple[str, ...]:
        return (
            str(self.index),
            self.wire_id,
            f"{self.start.x_m:.6f}",
            f"{self.start.y_m:.6f}",
            f"{self.start.z_m:.6f}",
            f"{self.end.x_m:.6f}",
            f"{self.end.y_m:.6f}",
            f"{self.end.z_m:.6f}",
            f"{self.length_m:.6f}",
            f"{self.diameter_mm:.6f}",
            self.material,
        )


@dataclass(frozen=True, slots=True)
class ConductorBomRow:
    """Conductor total grouped by material and diameter."""

    material: str
    diameter_mm: float
    wire_count: int
    total_length_m: float

    @property
    def cost_key(self) -> str:
        material = self.material.strip().lower().replace(" ", "_")
        return f"conductor:{material}:{self.diameter_mm:.3f}"


@dataclass(frozen=True, slots=True)
class FeedScheduleRow:
    """The primary feed point in model coordinates."""

    wire_id: str
    offset_m: float
    point: Point3D
    height_m: float


def _wire_direction(wire: Wire) -> tuple[float, float, float]:
    if wire.length_m <= 1e-12:
        return (0.0, 0.0, 0.0)
    return (
        (wire.end.x_m - wire.start.x_m) / wire.length_m,
        (wire.end.y_m - wire.start.y_m) / wire.length_m,
        (wire.end.z_m - wire.start.z_m) / wire.length_m,
    )


def _same_direction(first: Wire, second: Wire) -> bool:
    first_direction = _wire_direction(first)
    second_direction = _wire_direction(second)
    return all(
        math.isclose(a, b, rel_tol=0.0, abs_tol=1e-6)
        for a, b in zip(first_direction, second_direction, strict=True)
    )


def _physical_wires(model: AntennaModel) -> tuple[Wire, ...]:
    """Return physical conductors, merging collinear end-fed partitions."""
    wires = tuple(wire for wire in model.wires if not is_model_only_wire(wire.id))
    if not any(wire.id in _ENDFED_PARTITION_MARKERS for wire in wires):
        return wires

    partition = [wire for wire in wires if wire.id in _ENDFED_PARTITION_IDS]
    if not partition:
        return wires

    groups: list[list[Wire]] = [[partition[0]]]
    for wire in partition[1:]:
        if _same_direction(groups[-1][-1], wire):
            groups[-1].append(wire)
        else:
            groups.append([wire])

    merged_groups: list[Wire] = []
    for index, group in enumerate(groups):
        first = group[0]
        last = group[-1]
        merged_groups.append(
            Wire(
                id=RADIATOR_ID if index == 0 else first.id,
                start=first.start,
                end=last.end,
                radius_m=first.radius_m,
                material=first.material,
            )
        )

    physical: list[Wire] = []
    inserted = False
    for wire in wires:
        if wire.id in _ENDFED_PARTITION_IDS:
            if not inserted:
                physical.extend(merged_groups)
                inserted = True
            continue
        physical.append(wire)
    return tuple(physical)


def wire_schedule_rows(model: AntennaModel) -> tuple[WireScheduleRow, ...]:
    """Return one row per physical wire, excluding numerical model proxies."""

    return tuple(
        WireScheduleRow(
            index=index,
            wire_id=wire.id,
            start=wire.start,
            end=wire.end,
            length_m=wire.length_m,
            radius_m=wire.radius_m,
            material=wire.material.name,
        )
        for index, wire in enumerate(_physical_wires(model), start=1)
    )


def feed_schedule_row(model: AntennaModel) -> FeedScheduleRow:
    """Return the primary feed point and its height above ground."""

    wire = model.feed_wire
    ratio = (
        0.0 if wire.length_m <= 1e-12 else min(max(model.feed.offset_m / wire.length_m, 0.0), 1.0)
    )
    point = Point3D(
        x_m=wire.start.x_m + (wire.end.x_m - wire.start.x_m) * ratio,
        y_m=wire.start.y_m + (wire.end.y_m - wire.start.y_m) * ratio,
        z_m=wire.start.z_m + (wire.end.z_m - wire.start.z_m) * ratio,
    )
    return FeedScheduleRow(
        wire_id=(RADIATOR_ID if wire.id in _ENDFED_PARTITION_MARKERS else wire.id),
        offset_m=model.feed.offset_m,
        point=point,
        height_m=point.z_m,
    )


def schedule_rows_for_design(design: DesignVariant) -> tuple[WireScheduleRow, ...]:
    return wire_schedule_rows(design.antenna)


def conductor_bom_rows(model: AntennaModel) -> tuple[ConductorBomRow, ...]:
    """Group the physical wires by material and diameter."""

    groups: dict[tuple[str, float], list[float]] = {}
    for wire in _physical_wires(model):
        key = (wire.material.name, round(wire.radius_m * 2000.0, 3))
        groups.setdefault(key, []).append(wire.length_m)
    return tuple(
        ConductorBomRow(
            material=material,
            diameter_mm=diameter_mm,
            wire_count=len(lengths),
            total_length_m=sum(lengths),
        )
        for (material, diameter_mm), lengths in sorted(groups.items())
    )


def bom_summary_rows(model: AntennaModel) -> tuple[tuple[str, str], ...]:
    """Return the non-conductor totals shown in the bill of materials."""

    wires = _physical_wires(model)
    return (
        ("Wires", str(len(wires))),
        ("Total conductor", f"{sum(wire.length_m for wire in wires):.4f} m"),
        ("Loads", str(len(model.loads))),
        ("Transmission lines", str(len(model.transmission_lines))),
        ("Driven sources", str(1 + len(model.sources))),
    )


def wire_schedule_to_csv(design: DesignVariant) -> str:
    """Return the wire schedule as CSV with an explicit header."""

    lines = [",".join(WIRE_SCHEDULE_HEADER)]
    for row in schedule_rows_for_design(design):
        lines.append(",".join(row.csv_row()))
    return "\n".join(lines) + "\n"


def write_wire_schedule_csv(design: DesignVariant, path: Path) -> None:
    path.write_text(wire_schedule_to_csv(design), encoding="utf-8", newline="\n")


BOM_HEADER = ("material", "diameter_mm", "wire_count", "total_length_m")
BOM_COST_HEADER = (*BOM_HEADER, "currency", "unit_cost_per_m", "line_total")


def bom_to_csv(
    design: DesignVariant,
    *,
    costs: BomCostRecord | None = None,
) -> str:
    """Return the conductor bill of materials as CSV.

    Without ``costs`` the historical four-column format is preserved.  With a
    cost record, three optional columns carry the project currency, the manual
    unit cost per metre, and the line total.
    """

    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(BOM_COST_HEADER if costs is not None else BOM_HEADER)
    for row in conductor_bom_rows(design.antenna):
        if costs is None:
            writer.writerow(
                (
                    row.material,
                    f"{row.diameter_mm:.6f}",
                    row.wire_count,
                    f"{row.total_length_m:.6f}",
                )
            )
            continue
        unit_cost = costs.cost_for(row.cost_key)
        writer.writerow(
            (
                row.material,
                f"{row.diameter_mm:.6f}",
                row.wire_count,
                f"{row.total_length_m:.6f}",
                costs.currency,
                "" if unit_cost is None else f"{unit_cost:.6f}",
                "" if unit_cost is None else f"{row.total_length_m * unit_cost:.6f}",
            )
        )
    return buffer.getvalue()


def write_bom_csv(
    design: DesignVariant,
    path: Path,
    *,
    costs: BomCostRecord | None = None,
) -> None:
    path.write_text(bom_to_csv(design, costs=costs), encoding="utf-8", newline="\n")


def wire_schedule_html_rows(design: DesignVariant) -> tuple[str, ...]:
    """Return pre-escaped HTML table rows for the construction sheet."""

    rows: list[str] = []
    for row in schedule_rows_for_design(design):
        rows.append(
            "<tr>"
            f"<td>{row.index}</td>"
            f"<td><code>{html.escape(row.wire_id, quote=True)}</code></td>"
            f'<td class="num">{row.start.x_m:.4f}, {row.start.y_m:.4f}, {row.start.z_m:.4f}</td>'
            f'<td class="num">{row.end.x_m:.4f}, {row.end.y_m:.4f}, {row.end.z_m:.4f}</td>'
            f'<td class="num">{row.length_m:.4f}</td>'
            f'<td class="num">{row.diameter_mm:.3f}</td>'
            f"<td>{html.escape(row.material, quote=True)}</td>"
            "</tr>"
        )
    return tuple(rows)


def wire_schedule_lines(
    design: DesignVariant,
    labeler: Labeler | None = None,
) -> tuple[str, ...]:
    """Return compact lines for the native PDF construction sheet."""

    tr = labeler or identity_labeler
    lines: list[str] = []
    for row in schedule_rows_for_design(design):
        lines.append(
            tr(
                "W{index} {wire}: ({start_x}, {start_y}, {start_z}) -> "
                "({end_x}, {end_y}, {end_z}) · {length} m · Ø{diameter} mm · "
                "{material}",
                index=row.index,
                wire=row.wire_id,
                start_x=f"{row.start.x_m:.3f}",
                start_y=f"{row.start.y_m:.3f}",
                start_z=f"{row.start.z_m:.3f}",
                end_x=f"{row.end.x_m:.3f}",
                end_y=f"{row.end.y_m:.3f}",
                end_z=f"{row.end.z_m:.3f}",
                length=f"{row.length_m:.4f}",
                diameter=f"{row.diameter_mm:.3f}",
                material=tr(row.material),
            )
        )
    feed = feed_schedule_row(design.antenna)
    lines.append(
        tr(
            "Feed: {wire} @ {offset} m · ({x}, {y}, {z}) · height {height} m",
            wire=feed.wire_id,
            offset=f"{feed.offset_m:.4f}",
            x=f"{feed.point.x_m:.3f}",
            y=f"{feed.point.y_m:.3f}",
            z=f"{feed.point.z_m:.3f}",
            height=f"{feed.height_m:.4f}",
        )
    )
    return tuple(lines)
