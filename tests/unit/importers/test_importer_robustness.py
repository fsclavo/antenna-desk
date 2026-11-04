# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Property-based robustness checks for the untrusted-input importers.

Imported files are untrusted data.  These tests assert the contract that the
adapters already promise: malformed input is reported as ``ValueError`` (the
VNA parser uses a subclass), never as an unexpected ``IndexError``,
``KeyError``, ``ZeroDivisionError``, or ``OverflowError``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from antennadesk.importers.mmana import parse_mmana_file
from antennadesk.importers.nec2_deck import parse_nec2_deck
from antennadesk.importers.vna_csv import parse_vna_csv

PARSERS: tuple[Callable[[str], Any], ...] = (
    parse_mmana_file,
    parse_nec2_deck,
    parse_vna_csv,
)

_NOISE_LINES = st.sampled_from(
    [
        "",
        "*",
        "***Wires***",
        "*** Source ***",
        "*** Segmentation ***",
        "0",
        "1",
        "2",
        "-1",
        "7.1",
        "1e999",
        "nan",
        "inf",
        ",",
        ",,,",
        "0,0,0,1,0,0,0.001",
        "GW 1 5 0 0 0 1 0 0 0.001",
        "GE 1",
        "FR 0 1 0 0 7.1 0",
        "frequency_hz,r_ohm,x_ohm",
        "7000000,50,0",
    ]
)


def _line_garbage() -> st.SearchStrategy[str]:
    return st.lists(
        st.one_of(_NOISE_LINES, st.text(max_size=40)),
        max_size=30,
    ).map("\n".join)


def _parse(parser: Callable[[str], Any], text: str) -> None:
    try:
        parser(text)
    except ValueError:
        return


@settings(
    max_examples=200,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(st.text(max_size=2000))
def test_parsers_report_arbitrary_text_as_value_error(text: str) -> None:
    for parser in PARSERS:
        _parse(parser, text)


@settings(
    max_examples=300,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(_line_garbage())
def test_parsers_report_line_oriented_garbage_as_value_error(text: str) -> None:
    for parser in PARSERS:
        _parse(parser, text)


@settings(max_examples=100, deadline=None)
@given(
    st.lists(
        st.tuples(
            st.floats(min_value=1e-3, max_value=1e9, allow_nan=False, allow_infinity=False),
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=20,
    )
)
def test_vna_rx_rows_never_raise_an_unexpected_error(
    rows: list[tuple[float, float, float]],
) -> None:
    text = "frequency_hz,r_ohm,x_ohm\n" + "".join(
        f"{frequency},{resistance},{reactance}\n" for frequency, resistance, reactance in rows
    )
    parsed = parse_vna_csv(text)
    assert len(parsed.points) == len(rows)
