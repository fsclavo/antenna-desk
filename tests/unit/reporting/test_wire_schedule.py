# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
from antennadesk.domain.projects.project import Project
from antennadesk.reporting.wire_schedule import (
    BOM_HEADER,
    WIRE_SCHEDULE_HEADER,
    bom_summary_rows,
    bom_to_csv,
    conductor_bom_rows,
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


def test_wire_schedule_excludes_the_endfed_installation_return_proxy() -> None:
    from antennadesk.domain.antennas.endfed import (
        INSTALLATION_RETURN_ID,
        shortened_efhw_80_10_parameters,
    )

    model = shortened_efhw_80_10_parameters().to_antenna()
    rows = wire_schedule_rows(model)
    summary = dict(bom_summary_rows(model))
    feed = feed_schedule_row(model)

    assert INSTALLATION_RETURN_ID in {wire.id for wire in model.wires}
    assert len(rows) == 1
    assert rows[0].wire_id == "radiator"
    assert rows[0].length_m == pytest.approx(22.74)
    assert feed.wire_id == "radiator"
    assert feed.offset_m == pytest.approx(0.0)
    assert summary["Wires"] == "1"
    assert summary["Total conductor"] == "22.7400 m"


def test_conductor_bom_groups_by_material_and_diameter(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    rows = conductor_bom_rows(design.antenna)

    assert len(rows) == 1
    assert rows[0].material == "copper"
    assert rows[0].diameter_mm == pytest.approx(2.0)
    assert rows[0].wire_count == 1
    assert rows[0].total_length_m == pytest.approx(20.0)

    summary = dict(bom_summary_rows(design.antenna))
    assert summary["Wires"] == "1"
    assert summary["Total conductor"] == "20.0000 m"
    assert summary["Loads"] == "0"
    assert summary["Driven sources"] == "1"


def test_conductor_bom_covers_a_multi_wire_family() -> None:
    model = published_hexbeam_parameters().to_antenna()
    rows = conductor_bom_rows(model)

    assert len(rows) == 1
    assert rows[0].wire_count == 9
    assert rows[0].total_length_m == pytest.approx(sum(wire.length_m for wire in model.wires))


def test_conductor_bom_separates_materials() -> None:
    from antennadesk.domain.antennas.custom import CustomAntennaParameters
    from antennadesk.domain.antennas.feed import FeedPoint
    from antennadesk.domain.antennas.geometry import Point3D
    from antennadesk.domain.antennas.materials import ALUMINUM, COPPER
    from antennadesk.domain.antennas.wire import Wire

    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                "copper-wire",
                Point3D(0.0, 0.0, 5.0),
                Point3D(10.0, 0.0, 5.0),
                0.001,
                COPPER,
            ),
            Wire(
                "aluminum-wire",
                Point3D(0.0, 1.0, 5.0),
                Point3D(10.0, 1.0, 5.0),
                0.002,
                ALUMINUM,
            ),
        ),
        feed=FeedPoint("copper-wire", 0.0),
    )
    rows = conductor_bom_rows(parameters.to_antenna())

    assert {(row.material, row.diameter_mm) for row in rows} == {
        ("copper", 2.0),
        ("aluminum", 4.0),
    }


def test_bom_csv_has_a_header_and_the_grouped_totals(sample_project: Project) -> None:
    lines = bom_to_csv(sample_project.designs[0]).splitlines()

    assert lines[0] == ",".join(BOM_HEADER)
    assert len(lines) == 2
    assert lines[1].startswith("copper,2.000000,1,20.000000")


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
