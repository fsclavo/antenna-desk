# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small dependency-free SVG line charts for HTML reports."""

from __future__ import annotations

from dataclasses import dataclass
from xml.sax.saxutils import escape


@dataclass(frozen=True, slots=True)
class SvgSeries:
    label: str
    color: str
    points: tuple[tuple[float, float], ...]


def _format_tick(value: float) -> str:
    if abs(value) >= 1000.0 or (value != 0.0 and abs(value) < 0.01):
        return f"{value:.2g}"
    return f"{value:.3g}"


def line_chart_svg(
    *,
    title: str,
    x_label: str,
    y_label: str,
    series: tuple[SvgSeries, ...],
    width: int = 760,
    height: int = 260,
) -> str:
    left = 64
    right = 24
    top = 42
    bottom = 52
    plot_width = width - left - right
    plot_height = height - top - bottom
    all_points = [point for item in series for point in item.points]

    if not all_points:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
            f'<rect width="{width}" height="{height}" fill="#ffffff"/>'
            f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="12" fill="#666666">'
            f"No data</text></svg>"
        )

    xs = [point[0] for point in all_points]
    ys = [point[1] for point in all_points]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    if x_max == x_min:
        x_max = x_min + 1.0
    if y_max == y_min:
        y_max = y_min + 1.0
    y_padding = (y_max - y_min) * 0.08
    y_min -= y_padding
    y_max += y_padding

    def map_x(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_width

    def map_y(value: float) -> float:
        return top + plot_height - (value - y_min) / (y_max - y_min) * plot_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width / 2}" y="22" text-anchor="middle" '
        f'font-family="sans-serif" font-size="14" font-weight="bold" fill="#222222">'
        f"{escape(title)}</text>",
    ]

    for index in range(5):
        ratio = index / 4
        x_value = x_min + (x_max - x_min) * ratio
        y_value = y_min + (y_max - y_min) * ratio
        x_pos = left + plot_width * ratio
        y_pos = top + plot_height * (1.0 - ratio)
        parts.append(
            f'<line x1="{x_pos:.2f}" y1="{top}" x2="{x_pos:.2f}" '
            f'y2="{top + plot_height}" stroke="#e5e5e5" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{left}" y1="{y_pos:.2f}" x2="{left + plot_width}" '
            f'y2="{y_pos:.2f}" stroke="#e5e5e5" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x_pos:.2f}" y="{top + plot_height + 20}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="10" fill="#555555">'
            f"{escape(_format_tick(x_value))}</text>"
        )
        parts.append(
            f'<text x="{left - 8}" y="{y_pos + 3:.2f}" text-anchor="end" '
            f'font-family="sans-serif" font-size="10" fill="#555555">'
            f"{escape(_format_tick(y_value))}</text>"
        )

    parts.extend(
        [
            f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" '
            f'y2="{top + plot_height}" stroke="#333333" stroke-width="1"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" '
            f'stroke="#333333" stroke-width="1"/>',
            f'<text x="{left + plot_width / 2}" y="{height - 12}" text-anchor="middle" '
            f'font-family="sans-serif" font-size="11" fill="#333333">'
            f"{escape(x_label)}</text>",
            f'<text x="16" y="{top + plot_height / 2}" text-anchor="middle" '
            f'transform="rotate(-90 16 {top + plot_height / 2})" '
            f'font-family="sans-serif" font-size="11" fill="#333333">'
            f"{escape(y_label)}</text>",
        ]
    )

    for index, item in enumerate(series):
        if not item.points:
            continue
        polyline = " ".join(f"{map_x(x):.2f},{map_y(y):.2f}" for x, y in item.points)
        parts.append(
            f'<polyline points="{polyline}" fill="none" stroke="{item.color}" stroke-width="2"/>'
        )
        legend_x = left + index * 180
        legend_y = height - 30
        parts.append(
            f'<line x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 22}" '
            f'y2="{legend_y}" stroke="{item.color}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{legend_x + 28}" y="{legend_y + 4}" font-family="sans-serif" '
            f'font-size="10" fill="#333333">{escape(item.label)}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)
