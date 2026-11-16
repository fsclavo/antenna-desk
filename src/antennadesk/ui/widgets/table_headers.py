# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared table header sizing helpers."""

from __future__ import annotations

from PySide6.QtWidgets import QTableWidget

HEADER_PADDING_PX = 12


def fit_header_sections(table: QTableWidget, padding: int = HEADER_PADDING_PX) -> None:
    """Keep every header label readable, even when the table is narrow.

    Stretch mode distributes the viewport width across the sections. On a small
    screen, a large font scale can make a label wider than its section. Set the
    header's minimum section size to the widest label so the table scrolls
    horizontally instead of clipping the text.
    """

    header = table.horizontalHeader()
    metrics = header.fontMetrics()
    widest = 0
    for column in range(header.count()):
        item = table.horizontalHeaderItem(column)
        if item is not None:
            widest = max(widest, metrics.horizontalAdvance(item.text()))
    if widest:
        header.setMinimumSectionSize(widest + padding)
