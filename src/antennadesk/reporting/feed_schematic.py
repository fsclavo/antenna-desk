# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Renderer-neutral feed-connection schematic."""

from __future__ import annotations

from html import escape

from ..domain.antennas.feed_connection import (
    FeedConnectionDetail,
    FeedInterface,
)
from .localization import Labeler, identity_labeler


def _text(x: float, y: float, value: str, *, size: int = 13, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" '
        f'font-size="{size}" text-anchor="{anchor}" fill="#222">{escape(value)}</text>'
    )


def _line(x1: float, y1: float, x2: float, y2: float, *, dash: bool = False) -> str:
    dash_attr = ' stroke-dasharray="6 4"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="#222" stroke-width="2"{dash_attr}/>'
    )


def _box(
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    *,
    dashed: bool = False,
) -> str:
    dash_attr = ' stroke-dasharray="6 4"' if dashed else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
        f'rx="8" fill="#f4f4f4" stroke="#222" stroke-width="2"{dash_attr}/>'
        + _text(x + width / 2.0, y + height / 2.0 + 5.0, label, anchor="middle")
    )


def feed_schematic_svg(
    detail: FeedConnectionDetail,
    labeler: Labeler | None = None,
) -> str:
    """Return a deterministic SVG schematic for one feed detail.

    The drawing is intentionally schematic. It is not a mechanical drawing and
    is never a source of construction dimensions.
    """

    tr = labeler or identity_labeler
    interface_label = {
        FeedInterface.DIRECT_COAX: tr("Direct coax"),
        FeedInterface.CURRENT_BALUN: tr("1:1 current balun"),
        FeedInterface.TRANSFORMER: tr("Transformer / balun"),
        FeedInterface.BALANCED_LINE: tr("Balanced feed line"),
        FeedInterface.MULTI_PORT: tr("Multi-port combining network"),
        FeedInterface.UNKNOWN: tr("Connection not classified"),
    }[detail.interface]

    ratio = f"{detail.transformer_ratio:g}:1" if detail.transformer_ratio is not None else ""
    if ratio and detail.interface is FeedInterface.TRANSFORMER:
        interface_label = f"{interface_label} · {ratio}"

    first, second = detail.terminals
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="270" viewBox="0 0 720 270">',
        '<rect width="720" height="270" fill="#ffffff"/>',
        _text(24, 30, tr("Feed connection"), size=18),
        _text(24, 48, tr("Schematic · not to scale"), size=12),
        # Antenna side.
        _line(40, 90, 170, 90),
        _line(40, 170, 170, 170),
        _text(40, 78, tr("Antenna terminal A"), size=12),
        _text(40, 158, tr("Antenna terminal B"), size=12),
        _text(178, 95, first.role),
        _text(178, 175, second.role),
        # Interface box.
        _line(170, 90, 245, 90),
        _line(170, 170, 245, 170),
        _box(
            245,
            70,
            230,
            120,
            interface_label,
            dashed=detail.interface is FeedInterface.UNKNOWN,
        ),
        # Coax side.
        _line(475, 90, 570, 90),
        _line(475, 170, 570, 170),
    ]
    if detail.interface is FeedInterface.BALANCED_LINE:
        parts.extend(
            [
                _text(580, 95, tr("Balanced line A"), size=12),
                _text(580, 175, tr("Balanced line B"), size=12),
            ]
        )
    elif detail.interface is FeedInterface.MULTI_PORT:
        parts.extend(
            [
                _text(580, 95, tr("Primary port"), size=12),
                _text(580, 175, tr("Additional sources"), size=12),
            ]
        )
    elif detail.interface is FeedInterface.UNKNOWN:
        parts.extend(
            [
                _text(580, 95, tr("Verify the wiring"), size=12),
                _text(580, 175, tr("Verify the wiring"), size=12),
            ]
        )
    else:
        parts.extend(
            [
                _text(580, 95, tr("Coax center"), size=12),
                _text(580, 175, tr("Coax shield"), size=12),
            ]
        )
    if detail.balance.value:
        parts.append(
            _text(
                24,
                235,
                tr("Balance: {balance}", balance=tr(detail.balance.value)),
                size=12,
            )
        )
    parts.append(_text(24, 255, tr("Construction aid, not a solver result."), size=11))
    parts.append("</svg>")
    return "".join(parts)
