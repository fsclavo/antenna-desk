# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Renderer-neutral feed-connection schematic."""

from __future__ import annotations

from collections.abc import Iterable
from html import escape

from ..domain.antennas.feed_connection import (
    BalunRequirement,
    FeedConnectionDetail,
    FeedInterface,
    FeedTerminal,
)
from .localization import Labeler, identity_labeler

WIDTH = 720
HEIGHT = 430
_LEFT_X = 28
_LEFT_LINE_END = 220
_DEVICE_X = 230
_DEVICE_WIDTH = 170
_DEVICE_Y = 80
_DEVICE_HEIGHT = 130
_COAX_LABEL_X = 610


def _text(x: float, y: float, value: str, *, size: int = 13, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="sans-serif" '
        f'font-size="{size}" text-anchor="{anchor}" fill="#222">{escape(value)}</text>'
    )


def _line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    width: float = 2.0,
    dash: bool = False,
    color: str = "#222",
) -> str:
    dash_attr = ' stroke-dasharray="6 4"' if dash else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{color}" stroke-width="{width:.1f}"{dash_attr}/>'
    )


def _path(
    data: str,
    *,
    width: float = 2.0,
    dash: bool = False,
    fill: str = "none",
    color: str = "#222",
) -> str:
    dash_attr = ' stroke-dasharray="6 4"' if dash else ""
    return (
        f'<path d="{data}" fill="{fill}" stroke="{color}" stroke-width="{width:.1f}"{dash_attr}/>'
    )


def _rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    radius: float = 8.0,
    fill: str = "#f4f4f4",
    dash: bool = False,
    stroke_width: float = 2.0,
) -> str:
    dash_attr = ' stroke-dasharray="6 4"' if dash else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
        f'rx="{radius:.1f}" fill="{fill}" stroke="#222" '
        f'stroke-width="{stroke_width:.1f}"{dash_attr}/>'
    )


def _circle(
    cx: float,
    cy: float,
    radius: float,
    *,
    fill: str = "none",
    stroke_width: float = 2.0,
) -> str:
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" '
        f'fill="{fill}" stroke="#222" stroke-width="{stroke_width:.1f}"/>'
    )


def _group(group_id: str, children: Iterable[str]) -> str:
    return f'<g id="{group_id}">' + "".join(children) + "</g>"


def _terminal_label(terminal: FeedTerminal, tr: Labeler) -> str:
    if terminal.side == "ground":
        return tr("Ground / radials")
    if terminal.side == "counterpoise":
        return tr("Counterpoise")
    if terminal.wire_id is not None and terminal.side in {"before", "after", "start", "end"}:
        return tr(f"Antenna terminal {terminal.role}")
    return tr("Return")


def _terminal_rows(detail: FeedConnectionDetail, tr: Labeler) -> list[str]:
    first, second = detail.terminals
    return [
        _text(_LEFT_X, 98, _terminal_label(first, tr), size=12),
        _line(_LEFT_X, 110, _LEFT_LINE_END, 110),
        _text(_LEFT_X, 178, _terminal_label(second, tr), size=12),
        _line(_LEFT_X, 190, _LEFT_LINE_END, 190),
    ]


def _device_block(
    title: str,
    subtitle: str | None = None,
    *,
    dashed: bool = False,
    title_size: int = 12,
    subtitle_size: int = 11,
) -> list[str]:
    parts = [_rect(_DEVICE_X, _DEVICE_Y, _DEVICE_WIDTH, _DEVICE_HEIGHT, dash=dashed)]
    parts.append(
        _text(
            _DEVICE_X + _DEVICE_WIDTH / 2.0,
            _DEVICE_Y + 56,
            title,
            size=title_size,
            anchor="middle",
        )
    )
    if subtitle:
        parts.append(
            _text(
                _DEVICE_X + _DEVICE_WIDTH / 2.0,
                _DEVICE_Y + 78,
                subtitle,
                size=subtitle_size,
                anchor="middle",
            )
        )
    return parts


def _device_ports() -> list[str]:
    return [
        _line(_LEFT_LINE_END, 110, _DEVICE_X, 110),
        _line(_LEFT_LINE_END, 190, _DEVICE_X, 190),
    ]


def _coax_cable(x1: float, x2: float, y: float) -> list[str]:
    shield_start = x1 + 55.0
    shield_half_height = 18.0
    return [
        _line(x1 - 15, y, x2, y, width=3.5),
        _path(
            (
                f"M {shield_start:.1f} {y - shield_half_height:.1f} "
                f"H {x2 - 12:.1f} "
                f"Q {x2:.1f} {y - shield_half_height:.1f} {x2:.1f} {y:.1f} "
                f"Q {x2:.1f} {y + shield_half_height:.1f} {x2 - 12:.1f} "
                f"{y + shield_half_height:.1f} "
                f"H {shield_start:.1f} Z"
            ),
            width=3.0,
        ),
        _line(
            shield_start,
            y - shield_half_height,
            shield_start,
            y + shield_half_height,
            width=3.0,
        ),
    ]


def _coax_cross_section(tr: Labeler) -> list[str]:
    center_x = 600.0
    center_y = 300.0
    return [
        _group(
            "coax-cross-section",
            [
                _text(520, 240, tr("Coax cross-section"), size=12),
                _circle(center_x, center_y, 42, stroke_width=5),
                _circle(center_x, center_y, 15, fill="#222"),
                _circle(520, 355, 6, fill="#222", stroke_width=1),
                _circle(520, 375, 6, fill="#ffffff", stroke_width=1),
                _text(535, 359, tr("Center conductor"), size=10),
                _text(535, 379, tr("Shield (braid)"), size=10),
            ],
        )
    ]


def _coax_side(tr: Labeler, *, with_cross_section: bool = True) -> list[str]:
    parts = [
        _line(400, 130, 450, 148),
        _line(400, 170, 450, 158),
    ]
    parts.append(_group("coax", _coax_cable(450, 600, 153)))
    parts.extend(
        [
            _text(_COAX_LABEL_X, 140, tr("Coax center"), size=12),
            _text(_COAX_LABEL_X, 180, tr("Coax shield"), size=12),
        ]
    )
    if with_cross_section:
        parts.extend(_coax_cross_section(tr))
    return parts


def _direct_coax(detail: FeedConnectionDetail, tr: Labeler) -> list[str]:
    parts = [
        _text(240, 78, tr("Direct coax"), size=12),
        _text(240, 96, tr("no balun recorded"), size=10),
        _path("M 220 110 H 250 V 150", width=2),
        _path("M 220 190 H 305 V 168", width=2),
    ]
    parts.append(_group("coax", _coax_cable(250, 600, 150)))
    parts.extend(
        [
            _text(_COAX_LABEL_X, 142, tr("Coax center"), size=12),
            _text(_COAX_LABEL_X, 178, tr("Coax shield"), size=12),
        ]
    )
    if detail.balun_requirement in {
        BalunRequirement.REQUIRED,
        BalunRequirement.RECOMMENDED,
    }:
        parts.append(
            _group(
                "recommended-choke",
                [
                    _path(
                        "M 410 122 C 445 122 445 178 410 178 C 375 178 375 122 410 122 Z",
                        dash=True,
                        width=2,
                    ),
                    _text(320, 218, tr("Recommended, not recorded"), size=10),
                ],
            )
        )
    parts.extend(_coax_cross_section(tr))
    return parts


def _balanced_line(tr: Labeler) -> list[str]:
    return [
        _text(240, 86, tr("Balanced feed line"), size=12),
        _line(_LEFT_LINE_END, 110, _LEFT_LINE_END, 120),
        _line(_LEFT_LINE_END, 190, _LEFT_LINE_END, 180),
        _line(_LEFT_LINE_END, 120, 600, 120),
        _line(_LEFT_LINE_END, 180, 600, 180),
        _text(_COAX_LABEL_X, 124, tr("Balanced line A"), size=12),
        _text(_COAX_LABEL_X, 184, tr("Balanced line B"), size=12),
        _text(
            240,
            250,
            tr("The balun location depends on the tuner; it is not modeled."),
            size=11,
        ),
    ]


def _multi_port(tr: Labeler) -> list[str]:
    return [
        *_device_ports(),
        _group(
            "interface-device",
            _device_block(
                tr("Multi-port combining network"),
                tr("Combining network not modeled"),
                title_size=10,
                subtitle_size=9,
            ),
        ),
        _line(400, 120, 600, 120),
        _line(400, 180, 600, 180),
        _text(_COAX_LABEL_X, 124, tr("Primary port"), size=12),
        _text(_COAX_LABEL_X, 184, tr("Additional sources"), size=12),
    ]


def _unknown(tr: Labeler) -> list[str]:
    return [
        _text(240, 74, tr("Connection not classified"), size=12),
        _group(
            "unknown",
            [
                *_device_ports(),
                _rect(_DEVICE_X, _DEVICE_Y, _DEVICE_WIDTH, _DEVICE_HEIGHT, dash=True),
                _text(_DEVICE_X + _DEVICE_WIDTH / 2.0, 135, "?", size=28, anchor="middle"),
                _text(
                    _DEVICE_X + _DEVICE_WIDTH / 2.0,
                    165,
                    tr("Verify the wiring"),
                    size=12,
                    anchor="middle",
                ),
            ],
        ),
        _line(400, 150, 600, 150),
        _text(_COAX_LABEL_X, 154, tr("Verify the wiring"), size=12),
    ]


def _interface_drawing(detail: FeedConnectionDetail, tr: Labeler) -> list[str]:
    if detail.interface is FeedInterface.DIRECT_COAX:
        return _direct_coax(detail, tr)
    if detail.interface is FeedInterface.BALANCED_LINE:
        return [_group("balanced-line", _balanced_line(tr))]
    if detail.interface is FeedInterface.MULTI_PORT:
        return _multi_port(tr)
    if detail.interface is FeedInterface.UNKNOWN:
        return _unknown(tr)

    title = (
        tr("1:1 current balun")
        if detail.interface is FeedInterface.CURRENT_BALUN
        else tr("Transformer / balun")
    )
    subtitle = (
        tr("Recorded")
        if detail.interface is FeedInterface.CURRENT_BALUN
        else tr("Modeled as ideal")
    )
    if detail.interface is FeedInterface.TRANSFORMER and detail.transformer_ratio is not None:
        subtitle = f"{detail.transformer_ratio:g}:1 · {subtitle}"
    parts = [
        *_device_ports(),
        _group("interface-device", _device_block(title, subtitle)),
        *_coax_side(tr),
    ]
    if detail.interface is FeedInterface.TRANSFORMER:
        parts.extend(
            [
                _text(_DEVICE_X, 230, tr("Secondary"), size=10),
                _text(435, 230, tr("Primary"), size=10),
            ]
        )
    return parts


def feed_schematic_svg(
    detail: FeedConnectionDetail,
    labeler: Labeler | None = None,
) -> str:
    """Return a deterministic SVG schematic for one feed detail.

    The drawing is intentionally schematic. It is not a mechanical drawing and
    is never a source of construction dimensions.
    """

    tr = labeler or identity_labeler
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
        _text(24, 30, tr("Feed connection"), size=18),
        _text(24, 48, tr("Schematic · not to scale"), size=12),
        _group("antenna-side", _terminal_rows(detail, tr)),
        *_interface_drawing(detail, tr),
    ]
    if detail.balance.value:
        parts.append(
            _text(
                24,
                400,
                tr("Balance: {balance}", balance=tr(detail.balance.value)),
                size=12,
            )
        )
    parts.append(_text(24, 420, tr("Construction aid, not a solver result."), size=11))
    parts.append("</svg>")
    return "".join(parts)
