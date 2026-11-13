# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Renderer-neutral feed schematic."""

from __future__ import annotations

from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.design.feed_connection import feed_connection_detail
from antennadesk.reporting.feed_schematic import feed_schematic_svg
from antennadesk.ui.i18n import Language, Translator


def _detail():
    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
    )
    return feed_connection_detail(parameters, parameters.to_antenna())


def test_feed_schematic_is_deterministic_and_english() -> None:
    detail = _detail()
    first = feed_schematic_svg(detail)
    second = feed_schematic_svg(detail)

    assert first == second
    assert first.startswith("<svg")
    assert "Feed connection" in first
    assert "Direct coax" in first
    assert "Coax center" in first
    assert "not to scale" in first


def test_feed_schematic_translates_to_spanish() -> None:
    detail = _detail()
    svg = feed_schematic_svg(detail, Translator(Language.SPANISH).report)

    assert "Conexión de alimentación" in svg
    assert "Coaxil directo" in svg
    assert "Centro del coaxil" in svg
    assert "no a escala" in svg
