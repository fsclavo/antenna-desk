# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
from antennadesk.domain.projects.project import Project
from antennadesk.reporting.wire_schedule import (
    WIRE_SCHEDULE_HEADER,
    feed_schedule_row,
    wire_schedule_html_rows,
    wire_schedule_lines,
    wire_schedule_rows,
    wire_schedule_to_csv,
)


def test_wire_schedule_lists_every_canonical_wire(sample_project: Project) -> None:
    design = sample_project.designs[0]
    rows = wire_schedule_rows(design.antenna)

    assert len(rows) == len(design.antenna.wires)
    assert rows[0].wire_id == design.antenna.wires[0].id
    assert rows[0].length_m == design.antenna.wires[0].length_m
    assert rows[0].diameter_mm == 2.0
    assert rows[0].material == "copper"
    assert all(math.isfinite(row.length_m) for row in rows)


def test_wire_schedule_covers_a_bent_multi_wire_family() -> None:
    model = published_hexbeam_parameters().to_antenna()
    rows = wire_schedule_rows(model)
    feed = feed_schedule_row(model)

    assert len(rows) == 9
    assert {row.wire_id for row in rows} == {wire.id for wire in model.wires}
    assert feed.wire_id == "hexbeam-feed"
    assert feed.height_m == 10.0
    assert all(row.length_m > 0.0 for row in rows)


def test_wire_schedule_csv_has_a_header_and_one_row_per_wire(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    lines = wire_schedule_to_csv(design).splitlines()

    assert lines[0] == ",".join(WIRE_SCHEDULE_HEADER)
    assert len(lines) == len(design.antenna.wires) + 1
    assert design.antenna.wires[0].id in lines[1]


def test_wire_schedule_html_and_pdf_lines_include_the_feed(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    html_rows = wire_schedule_html_rows(design)
    lines = wire_schedule_lines(design)

    assert len(html_rows) == len(design.antenna.wires)
    assert design.antenna.wires[0].id in html_rows[0]
    assert any("Feed:" in line for line in lines)
    assert any(design.antenna.feed.wire_id in line for line in lines)
