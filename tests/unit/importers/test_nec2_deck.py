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


def test_ignores_a_line_that_is_only_separators() -> None:
    result = parse_nec2_deck(",\nGW 1 5 -5 0 8 5 0 8 0.001\nFR 0 1 0 0 7.1 0\nEX 0 1 3 0 1.0\n")

    assert len(result.parameters.wires) == 1


def _minimal_deck(*extra: str) -> str:
    return "GW 1 5 -5.0 0.0 8.0 5.0 0.0 8.0 0.001\nFR 0 1 0 0 7.1 0\nEX 0 1 3 0 1.0\n" + "".join(
        f"{line}\n" for line in extra
    )


def test_rejects_an_incomplete_gw_card() -> None:
    with pytest.raises(ValueError, match="incomplete GW"):
        parse_nec2_deck("GW 1 5 0 0 0\nFR 0 1 0 0 7.1 0\nEX 0 1 3 0 1.0\n")


def test_rejects_a_duplicate_gw_tag() -> None:
    with pytest.raises(ValueError, match="duplicate GW"):
        parse_nec2_deck(
            "GW 1 5 -5 0 8 5 0 8 0.001\n"
            "GW 1 5 5 0 8 5 5 8 0.001\n"
            "FR 0 1 0 0 7.1 0\n"
            "EX 0 1 3 0 1.0\n"
        )


def test_rejects_non_positive_gw_segments() -> None:
    with pytest.raises(ValueError, match="segments must be positive"):
        parse_nec2_deck("GW 1 0 -5 0 8 5 0 8 0.001\nFR 0 1 0 0 7.1 0\nEX 0 1 3 0 1.0\n")


def test_rejects_a_non_numeric_gw_field() -> None:
    with pytest.raises(ValueError, match="invalid GW radius"):
        parse_nec2_deck("GW 1 5 -5 0 8 5 0 8 abc\nFR 0 1 0 0 7.1 0\nEX 0 1 3 0 1.0\n")


def test_rejects_an_incomplete_ex_card() -> None:
    with pytest.raises(ValueError, match="incomplete EX"):
        parse_nec2_deck("GW 1 5 -5 0 8 5 0 8 0.001\nFR 0 1 0 0 7.1 0\nEX 0 1\n")


def test_ignores_non_voltage_ex_sources() -> None:
    result = parse_nec2_deck(
        "GW 1 5 -5 0 8 5 0 8 0.001\nFR 0 1 0 0 7.1 0\nEX 1 1 3 0 1.0\nEX 0 1 3 0 1.0\n"
    )

    assert any("EX type 1 ignored" in warning for warning in result.warnings)


def test_warns_about_an_additional_ex_source() -> None:
    result = parse_nec2_deck(_minimal_deck("EX 0 1 3 0 2.0"))

    assert any("additional EX source ignored" in warning for warning in result.warnings)


def test_rejects_an_incomplete_fr_card() -> None:
    with pytest.raises(ValueError, match="incomplete FR"):
        parse_nec2_deck("GW 1 5 -5 0 8 5 0 8 0.001\nFR 0 1 0\nEX 0 1 3 0 1.0\n")


def test_warns_about_a_sweep_and_an_additional_fr() -> None:
    result = parse_nec2_deck(
        "GW 1 5 -5 0 8 5 0 8 0.001\nFR 0 2 0 0 7.1 0\nEX 0 1 3 0 1.0\nFR 0 1 0 0 14.1 0\n"
    )

    assert result.parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert any("only the first frequency" in warning for warning in result.warnings)
    assert any("additional FR card ignored" in warning for warning in result.warnings)


def test_rejects_an_incomplete_gn_card() -> None:
    with pytest.raises(ValueError, match="incomplete GN"):
        parse_nec2_deck(_minimal_deck("GN"))


def test_warns_about_an_unsupported_gn_type() -> None:
    result = parse_nec2_deck(_minimal_deck("GN 2"))

    assert result.parameters.ground.kind is GroundKind.FREE_SPACE
    assert any("unsupported GN type 2" in warning for warning in result.warnings)


def test_rejects_an_incomplete_ld_card() -> None:
    with pytest.raises(ValueError, match="incomplete LD"):
        parse_nec2_deck(_minimal_deck("LD 0 1 1"))


def test_warns_about_an_ld_unknown_tag() -> None:
    result = parse_nec2_deck(_minimal_deck("LD 0 99 1 1 10 0 0"))

    assert any("unknown tag 99" in warning for warning in result.warnings)


def test_warns_about_an_unsupported_ld_type() -> None:
    result = parse_nec2_deck(_minimal_deck("LD 2 1 1 1 10 0 0"))

    assert any("LD type 2 ignored" in warning for warning in result.warnings)


def test_warns_when_an_ld_range_uses_its_first_segment() -> None:
    result = parse_nec2_deck(_minimal_deck("LD 0 1 1 3 10 0 0"))

    assert any("uses its first segment" in warning for warning in result.warnings)


def test_warns_about_an_unsupported_card() -> None:
    result = parse_nec2_deck(_minimal_deck("ZZ 1"))

    assert any("unsupported ZZ card ignored" in warning for warning in result.warnings)


def test_rejects_an_ex_with_an_unknown_tag() -> None:
    with pytest.raises(ValueError, match="EX references unknown GW tag 99"):
        parse_nec2_deck("GW 1 5 -5 0 8 5 0 8 0.001\nFR 0 1 0 0 7.1 0\nEX 0 99 3 0 1.0\n")


def test_rejects_an_ex_segment_out_of_range() -> None:
    with pytest.raises(ValueError, match="outside GW tag 1"):
        parse_nec2_deck("GW 1 5 -5 0 8 5 0 8 0.001\nFR 0 1 0 0 7.1 0\nEX 0 1 99 0 1.0\n")
