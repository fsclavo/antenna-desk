# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.reporting.design_summary import design_summary_rows


def test_loaded_vertical_summary_reports_the_template_and_coil() -> None:
    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=1.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=12e-6,
        loading_coil_resistance_ohm=0.5,
    )

    rows = dict(design_summary_rows(parameters))

    assert rows["Type"] == "loaded vertical"
    assert "12.0000 µH" in rows["Loading coil"]
    assert "1.0000 m" in rows["Loading coil"]
    assert "0.5 Ω" in rows["Loading coil"]
