# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.reporting.svg_chart import SvgSeries, line_chart_svg


def test_line_chart_contains_svg_and_polyline() -> None:
    svg = line_chart_svg(
        title="SWR <test>",
        x_label="Frequency",
        y_label="SWR",
        series=(SvgSeries("A", "#ff0000", ((1.0, 2.0), (2.0, 1.5), (3.0, 2.5))),),
    )

    assert svg.startswith("<svg")
    assert "<polyline" in svg
    assert "SWR &lt;test&gt;" in svg
    assert "nan" not in svg.lower()


def test_empty_chart_has_no_data_message() -> None:
    svg = line_chart_svg(
        title="Empty",
        x_label="X",
        y_label="Y",
        series=(),
    )
    assert "No data" in svg
