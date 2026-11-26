# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared painters for geometry and pattern diagrams."""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen


def draw_feed_marker(
    painter: QPainter,
    point: QPointF,
    color: QColor,
    *,
    radius: float = 4.0,
) -> None:
    """Draw the shared antenna feed marker."""

    painter.setPen(QPen(color, 2.0))
    painter.setBrush(color)
    painter.drawEllipse(point, radius, radius)
    painter.setBrush(Qt.BrushStyle.NoBrush)
