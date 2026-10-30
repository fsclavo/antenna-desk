# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.load import SeriesLoad
from antennadesk.domain.environment.ground import GroundKind
from antennadesk.importers.nec2_deck import parse_nec2_deck


def _deck() -> str:
    return """CM test
GW 1 5 -5.0 0.0 8.0 5.0 0.0 8.0 0.001
GE 1
GN 0 0 0 0 13.0 0.005
FR 0 1 0 0 7.1 0
EX 0 1 3 0 1.0
LD 0 1 3 3 10.0 0.000012 0.0
RP 0 19 1 1000 0 0 10 0
EN
"""


def test_imports_wires_feed_ground_and_load() -> None:
    result = parse_nec2_deck(_deck())
    parameters = result.parameters

    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert len(parameters.wires) == 1
    assert parameters.wires[0].id == "w1"
    assert parameters.feed.wire_id == "w1"
    assert parameters.feed.offset_m == pytest.approx(5.0)
    assert parameters.ground.kind is GroundKind.FINITE
    assert parameters.loads == (
        SeriesLoad(
            "load-1",
            "w1",
            5.0,
            resistance_ohm=10.0,
            inductance_h=12e-6,
        ),
    )
    assert any("RP" in warning for warning in result.warnings)


def test_accepts_comma_separated_cards() -> None:
    result = parse_nec2_deck(
        "GW,1,5,-5,0,8,5,0,8,0.001\nGN,0,0,0,0,13,0.005\nFR,0,1,0,0,7.1,0\nEX,0,1,3,0,1\nEN\n"
    )

    assert result.parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert result.parameters.feed.offset_m == pytest.approx(5.0)


def test_rejects_a_deck_without_a_source() -> None:
    with pytest.raises(ValueError, match="EX"):
        parse_nec2_deck("GW 1 5 -5 0 8 5 0 8 0.001\nFR 0 1 0 0 7.1 0\n")


def test_rejects_a_deck_without_a_wire() -> None:
    with pytest.raises(ValueError, match="GW"):
        parse_nec2_deck("FR 0 1 0 0 7.1 0\n")
