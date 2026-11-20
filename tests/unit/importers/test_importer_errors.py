# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit malformed-input cases for the MMANA and Touchstone importers."""

from __future__ import annotations

import pytest

from antennadesk.importers.mmana import parse_mmana_file
from antennadesk.importers.touchstone import (
    TouchstoneError,
    parse_touchstone_s1p,
    parse_touchstone_s2p,
)


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("", r"no '\*' separator"),
        ("*\n", "no frequency"),
        ("*\n7.1\n", "no wire count"),
        ("*\n7.1\n0\n", "no wires"),
        ("*\n7.1\n1\n0,0,0,1,0,0\n", "invalid MMANA wire row"),
        ("*\n7.1\n1\n0,0,0,1,0,0,nope\n", "invalid MMANA wire row"),
        ("*\n7.1\n1\n0,0,0,1,0,0,0.001\n", "no wire source"),
        (
            "*\n7.1\n1\n0,0,0,1,0,0,0.001\nw2c\n",
            "unknown wire 2",
        ),
    ],
)
def test_mmana_rejects_malformed_files(text: str, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        parse_mmana_file(text)


def test_mmana_unknown_source_suffix_is_visible() -> None:
    result = parse_mmana_file("*\n7.1\n1\n0,0,0,1,0,0,0.001\nw1x\n")

    assert any("unknown source suffix" in warning for warning in result.warnings)


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("", "empty"),
        ("#\n", "empty option line"),
        ("# S RI R\n7.1 0.2 0\n", "missing reference impedance"),
        ("# S RI R nope\n7.1 0.2 0\n", "invalid reference impedance"),
        ("# S RI X\n7.1 0.2 0\n", "unsupported option"),
        ("# S RI\n# S RI\n7.1 0.2 0\n", "multiple option lines"),
        ("# S RI\n7.1\n", "expected frequency"),
        ("# S RI\n7.1 nope 0\n", "invalid numeric value"),
        ("# S RI\n7.1 nan 0\n", "non-finite numeric value"),
        ("# S RI\n0 0.2 0\n", "frequency must be positive"),
        ("# S RI\n7.1 2 0\n", "no valid one-port"),
    ],
)
def test_one_port_touchstone_rejects_malformed_files(text: str, match: str) -> None:
    with pytest.raises(TouchstoneError, match=match):
        parse_touchstone_s1p(text)


def test_two_port_touchstone_validates_the_port_and_row_width() -> None:
    with pytest.raises(TouchstoneError, match="port must be 1 or 2"):
        parse_touchstone_s2p("# S RI\n7.1 0.2 0 0 0 0 0 0 0\n", port=0)
    with pytest.raises(TouchstoneError, match="S22 requires full 9-value"):
        parse_touchstone_s2p("# S RI\n7.1 0.2 0\n", port=2)
    with pytest.raises(TouchstoneError, match="expected 3, 5, or 9"):
        parse_touchstone_s2p("# S RI\n7.1 0.2\n")


def test_two_port_touchstone_skips_a_reflection_at_or_above_one() -> None:
    with pytest.raises(TouchstoneError, match="no valid two-port"):
        parse_touchstone_s2p("# S RI\n7.1 2 0 0 0 0 0 0 0\n")
