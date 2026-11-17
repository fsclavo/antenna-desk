# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dispatch VNA measurement files to the CSV or Touchstone parser."""

from __future__ import annotations

from .touchstone import ParsedTouchstone, looks_like_touchstone, parse_touchstone_s1p
from .vna_csv import ParsedVnaCsv, parse_vna_csv

ParsedVnaData = ParsedVnaCsv | ParsedTouchstone


def parse_vna_data(text: str, *, suffix: str = "") -> ParsedVnaData:
    """Parse a VNA export, using the suffix and content to choose the format."""

    normalized = suffix.lower()
    if normalized == ".s1p":
        return parse_touchstone_s1p(text)
    if normalized not in {".csv", ".txt"} and looks_like_touchstone(text):
        return parse_touchstone_s1p(text)
    return parse_vna_csv(text)
