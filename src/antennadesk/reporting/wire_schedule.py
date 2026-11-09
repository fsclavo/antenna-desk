# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Wire, feed, and load schedule for construction sheets.

A dimensioned sketch can hide a low-priority dimension when space is tight.
The schedule is the authoritative construction data: every canonical wire with
its endpoints, length, diameter, and material, plus the feed point.
"""

from __future__ import annotations

import html
from dataclasses import dataclass

from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.geometry import Point3D
from ..domain.projects.project import DesignVariant

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
class FeedScheduleRow:
    """The primary feed point in model coordinates."""

    wire_id: str
    offset_m: float
    point: Point3D
    height_m: float


def wire_schedule_rows(model: AntennaModel) -> tuple[WireScheduleRow, ...]:
    """Return one row per canonical wire, in model order."""

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
        for index, wire in enumerate(model.wires, start=1)
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
        wire_id=wire.id,
        offset_m=model.feed.offset_m,
        point=point,
        height_m=point.z_m,
    )


def schedule_rows_for_design(design: DesignVariant) -> tuple[WireScheduleRow, ...]:
    return wire_schedule_rows(design.antenna)


def wire_schedule_to_csv(design: DesignVariant) -> str:
    """Return the wire schedule as CSV with an explicit header."""

    lines = [",".join(WIRE_SCHEDULE_HEADER)]
    for row in schedule_rows_for_design(design):
        lines.append(",".join(row.csv_row()))
    return "\n".join(lines) + "\n"


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


def wire_schedule_lines(design: DesignVariant) -> tuple[str, ...]:
    """Return compact lines for the native PDF construction sheet."""

    lines: list[str] = []
    for row in schedule_rows_for_design(design):
        lines.append(
            f"W{row.index} {row.wire_id}: "
            f"({row.start.x_m:.3f}, {row.start.y_m:.3f}, {row.start.z_m:.3f}) -> "
            f"({row.end.x_m:.3f}, {row.end.y_m:.3f}, {row.end.z_m:.3f}) · "
            f"{row.length_m:.4f} m · Ø{row.diameter_mm:.3f} mm · {row.material}"
        )
    feed = feed_schedule_row(design.antenna)
    lines.append(
        f"Feed: {feed.wire_id} @ {feed.offset_m:.4f} m · "
        f"({feed.point.x_m:.3f}, {feed.point.y_m:.3f}, {feed.point.z_m:.3f}) · "
        f"height {feed.height_m:.4f} m"
    )
    return tuple(lines)
