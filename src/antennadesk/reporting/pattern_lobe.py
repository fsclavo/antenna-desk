# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic static 3D far-field wireframe for exported reports."""

from __future__ import annotations

import math
from dataclasses import dataclass
from xml.sax.saxutils import escape

from ..domain.simulation.result import FrequencyResult
from .localization import Labeler

WIDTH = 760
HEIGHT = 460
PLOT_LEFT = 40.0
PLOT_TOP = 28.0
PLOT_WIDTH = 600.0
PLOT_HEIGHT = 350.0
MAX_THETA_POSITIONS = 19
MAX_PHI_POSITIONS = 37
GAIN_BINS = 12
MAX_SEGMENTS = 2 * MAX_THETA_POSITIONS * MAX_PHI_POSITIONS
YAW_DEG = 38.0
PITCH_DEG = 26.0
MIN_RADIUS = 0.02
MIN_VALID_GAIN_DB = -100.0

_GAIN_STOPS = (
    (0.0, (21, 128, 61)),
    (0.5, (161, 98, 7)),
    (1.0, (185, 28, 28)),
)


@dataclass(frozen=True, slots=True)
class PatternLobe:
    """One rendered lobe or an explicit reason why it is unavailable."""

    svg: str | None
    unavailable_reason: str | None = None
    displayed_theta_count: int = 0
    displayed_phi_count: int = 0
    segment_count: int = 0


@dataclass(frozen=True, slots=True)
class _Grid:
    theta_values: tuple[float, ...]
    phi_values: tuple[float, ...]
    gains: dict[tuple[int, int], float]


def _retained_positions(count: int, target_count: int) -> tuple[int, ...]:
    if count <= target_count:
        return tuple(range(count))
    target_count = max(2, target_count)
    return tuple(
        sorted({round(index * (count - 1) / (target_count - 1)) for index in range(target_count)})
    )


def _gain_color(normalized: float) -> str:
    value = min(max(normalized, 0.0), 1.0)
    for index in range(len(_GAIN_STOPS) - 1):
        start_position, start_color = _GAIN_STOPS[index]
        end_position, end_color = _GAIN_STOPS[index + 1]
        if value <= end_position:
            span = end_position - start_position
            ratio = 0.0 if span <= 0.0 else (value - start_position) / span
            red = round(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            green = round(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            blue = round(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            return f"#{red:02x}{green:02x}{blue:02x}"
    red, green, blue = _GAIN_STOPS[-1][1]
    return f"#{red:02x}{green:02x}{blue:02x}"


def _valid_grid(frequency: FrequencyResult, *, ground: bool) -> _Grid | None:
    by_angle: dict[tuple[float, float], float] = {}
    for point in frequency.far_field:
        gain = point.gain_total_db
        if gain is None or not math.isfinite(gain) or gain <= MIN_VALID_GAIN_DB:
            continue
        if ground and point.theta_deg > 90.0 + 1e-6:
            continue
        theta = round(point.theta_deg, 3)
        phi = round(point.phi_deg % 360.0, 3)
        by_angle[(theta, phi)] = gain
    if len(by_angle) < 4:
        return None
    theta_values = tuple(sorted({theta for theta, _phi in by_angle}))
    phi_values = tuple(sorted({phi for _theta, phi in by_angle}))
    if len(theta_values) < 2 or len(phi_values) < 2:
        return None
    index = {(theta, phi): gain for (theta, phi), gain in by_angle.items()}
    gains: dict[tuple[int, int], float] = {}
    for theta_position, theta in enumerate(theta_values):
        for phi_position, phi in enumerate(phi_values):
            gain = index.get((theta, phi))
            if gain is not None:
                gains[(theta_position, phi_position)] = gain
    return _Grid(theta_values, phi_values, gains)


def _world_point(theta_deg: float, phi_deg: float, radius: float) -> tuple[float, float, float]:
    theta = math.radians(theta_deg)
    phi = math.radians(phi_deg)
    return (
        math.sin(theta) * math.cos(phi) * radius,
        math.sin(theta) * math.sin(phi) * radius,
        math.cos(theta) * radius,
    )


def _project_world(
    x: float,
    y: float,
    z: float,
    *,
    cos_yaw: float,
    sin_yaw: float,
    cos_pitch: float,
    sin_pitch: float,
) -> tuple[float, float]:
    rotated_x = x * cos_yaw - y * sin_yaw
    rotated_y = x * sin_yaw + y * cos_yaw
    return rotated_x, rotated_y * sin_pitch + z * cos_pitch


def pattern_lobe(
    frequency: FrequencyResult,
    tr: Labeler,
    *,
    ground: bool,
) -> PatternLobe:
    """Build one static SVG wireframe or an explicit unavailable reason."""

    grid = _valid_grid(frequency, ground=ground)
    if grid is None:
        return PatternLobe(
            svg=None,
            unavailable_reason=tr(
                "3D pattern unavailable: the far-field data does not contain a 2D angular grid."
            ),
        )

    theta_positions = _retained_positions(len(grid.theta_values), MAX_THETA_POSITIONS)
    phi_positions = _retained_positions(len(grid.phi_values), MAX_PHI_POSITIONS)
    retained = [
        (theta_position, phi_position, grid.gains[(theta_position, phi_position)])
        for theta_position in theta_positions
        for phi_position in phi_positions
        if (theta_position, phi_position) in grid.gains
    ]
    if len(retained) < 4:
        return PatternLobe(
            svg=None,
            unavailable_reason=tr(
                "3D pattern unavailable: the far-field data does not contain a 2D angular grid."
            ),
        )

    gains = [gain for _theta, _phi, gain in retained]
    raw_min = min(gains)
    raw_max = max(gains)
    uniform = math.isclose(raw_min, raw_max, rel_tol=1e-12, abs_tol=1e-12)
    gain_span = max(raw_max - raw_min, 1e-9)
    max_theta_position, max_phi_position, max_gain = max(
        retained,
        key=lambda item: item[2],
    )

    def normalized(gain: float) -> float:
        if uniform:
            return 0.5
        return min(max((gain - raw_min) / gain_span, 0.0), 1.0)

    cos_yaw = math.cos(math.radians(YAW_DEG))
    sin_yaw = math.sin(math.radians(YAW_DEG))
    cos_pitch = math.cos(math.radians(PITCH_DEG))
    sin_pitch = math.sin(math.radians(PITCH_DEG))

    def project_angle(theta_deg: float, phi_deg: float, gain: float) -> tuple[float, float]:
        radius = max(normalized(gain), MIN_RADIUS)
        x, y, z = _world_point(theta_deg, phi_deg, radius)
        return _project_world(
            x,
            y,
            z,
            cos_yaw=cos_yaw,
            sin_yaw=sin_yaw,
            cos_pitch=cos_pitch,
            sin_pitch=sin_pitch,
        )

    vertex_by_grid: dict[tuple[int, int], int] = {}
    projected: list[tuple[float, float]] = []
    for theta_position, phi_position, gain in retained:
        theta = grid.theta_values[theta_position]
        phi = grid.phi_values[phi_position]
        vertex_by_grid[(theta_position, phi_position)] = len(projected)
        projected.append(project_angle(theta, phi, gain))

    segments: list[tuple[int, int, int]] = []
    for phi_position in phi_positions:
        previous: tuple[int, float] | None = None
        for theta_position in theta_positions:
            index = vertex_by_grid.get((theta_position, phi_position))
            if index is None:
                previous = None
                continue
            gain = grid.gains[(theta_position, phi_position)]
            current = (index, normalized(gain))
            if previous is not None:
                segments.append(
                    (
                        previous[0],
                        current[0],
                        min(
                            int((previous[1] + current[1]) * 0.5 * GAIN_BINS),
                            GAIN_BINS - 1,
                        ),
                    )
                )
            previous = current
    for theta_position in theta_positions:
        previous = None
        for phi_position in phi_positions:
            index = vertex_by_grid.get((theta_position, phi_position))
            if index is None:
                previous = None
                continue
            gain = grid.gains[(theta_position, phi_position)]
            current = (index, normalized(gain))
            if previous is not None:
                segments.append(
                    (
                        previous[0],
                        current[0],
                        min(
                            int((previous[1] + current[1]) * 0.5 * GAIN_BINS),
                            GAIN_BINS - 1,
                        ),
                    )
                )
            previous = current
    if len(segments) > MAX_SEGMENTS:
        segments = segments[:MAX_SEGMENTS]

    # Fit the projected wireframe and the world axes into the plot rectangle.
    axis_points = [
        _project_world(
            1.0,
            0.0,
            0.0,
            cos_yaw=cos_yaw,
            sin_yaw=sin_yaw,
            cos_pitch=cos_pitch,
            sin_pitch=sin_pitch,
        ),
        _project_world(
            -1.0,
            0.0,
            0.0,
            cos_yaw=cos_yaw,
            sin_yaw=sin_yaw,
            cos_pitch=cos_pitch,
            sin_pitch=sin_pitch,
        ),
        _project_world(
            0.0,
            1.0,
            0.0,
            cos_yaw=cos_yaw,
            sin_yaw=sin_yaw,
            cos_pitch=cos_pitch,
            sin_pitch=sin_pitch,
        ),
        _project_world(
            0.0,
            -1.0,
            0.0,
            cos_yaw=cos_yaw,
            sin_yaw=sin_yaw,
            cos_pitch=cos_pitch,
            sin_pitch=sin_pitch,
        ),
        _project_world(
            0.0,
            0.0,
            1.0,
            cos_yaw=cos_yaw,
            sin_yaw=sin_yaw,
            cos_pitch=cos_pitch,
            sin_pitch=sin_pitch,
        ),
        _project_world(
            0.0,
            0.0,
            -1.0,
            cos_yaw=cos_yaw,
            sin_yaw=sin_yaw,
            cos_pitch=cos_pitch,
            sin_pitch=sin_pitch,
        ),
    ]
    extent = [*projected, *axis_points]
    min_x = min(point[0] for point in extent)
    max_x = max(point[0] for point in extent)
    min_y = min(point[1] for point in extent)
    max_y = max(point[1] for point in extent)
    span_x = max(max_x - min_x, 1e-9)
    span_y = max(max_y - min_y, 1e-9)
    scale = min(PLOT_WIDTH / span_x, PLOT_HEIGHT / span_y) * 0.92
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0

    def screen(px: float, py: float) -> tuple[float, float]:
        return (
            PLOT_LEFT + PLOT_WIDTH / 2.0 + (px - center_x) * scale,
            PLOT_TOP + PLOT_HEIGHT / 2.0 - (py - center_y) * scale,
        )

    screen_points = [screen(px, py) for px, py in projected]
    max_theta = grid.theta_values[max_theta_position]
    max_phi = grid.phi_values[max_phi_position]
    marker_x, marker_y = screen(*project_angle(max_theta, max_phi, max_gain))

    title = tr("3D far-field pattern")
    description = tr(
        "Static total-gain wireframe at the report pattern frequency. "
        "The separate geometry figure shows the antenna orientation."
    )
    caption_samples = tr(
        "Total-gain pattern at {frequency:.3f} MHz · stored sampling {theta_count}x{phi_count}",
        frequency=frequency.frequency_hz / 1e6,
        theta_count=len(grid.theta_values),
        phi_count=len(grid.phi_values),
    )
    caption_max = tr(
        "Max {gain:.2f} dBi at θ={theta:.0f}°, φ={phi:.0f}°. "
        "The geometry figure shows orientation.",
        gain=max_gain,
        theta=max_theta,
        phi=max_phi,
    )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        'aria-labelledby="pattern-lobe-title pattern-lobe-desc" '
        'class="pattern-lobe">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<title id="pattern-lobe-title">{escape(title)}</title>',
        f'<desc id="pattern-lobe-desc">{escape(description)}</desc>',
        f'<text x="{WIDTH / 2:.1f}" y="20" text-anchor="middle" '
        f'font-family="sans-serif" font-size="13" font-weight="bold" fill="#222222">'
        f"{escape(title)}</text>",
    ]

    if ground:
        ring = [
            screen(
                *_project_world(
                    0.88 * math.cos(math.radians(phi)),
                    0.88 * math.sin(math.radians(phi)),
                    0.0,
                    cos_yaw=cos_yaw,
                    sin_yaw=sin_yaw,
                    cos_pitch=cos_pitch,
                    sin_pitch=sin_pitch,
                )
            )
            for phi in range(0, 361, 12)
        ]
        ring_points = " ".join(f"{x:.2f},{y:.2f}" for x, y in ring)
        parts.append(
            f'<polyline points="{ring_points}" fill="none" stroke="#9ca3af" '
            'stroke-width="1" stroke-dasharray="2 3"/>'
        )
        for phi in range(0, 360, 45):
            start = screen(
                *_project_world(
                    0.0,
                    0.0,
                    0.0,
                    cos_yaw=cos_yaw,
                    sin_yaw=sin_yaw,
                    cos_pitch=cos_pitch,
                    sin_pitch=sin_pitch,
                )
            )
            end = screen(
                *_project_world(
                    0.88 * math.cos(math.radians(phi)),
                    0.88 * math.sin(math.radians(phi)),
                    0.0,
                    cos_yaw=cos_yaw,
                    sin_yaw=sin_yaw,
                    cos_pitch=cos_pitch,
                    sin_pitch=sin_pitch,
                )
            )
            parts.append(
                f'<line x1="{start[0]:.2f}" y1="{start[1]:.2f}" '
                f'x2="{end[0]:.2f}" y2="{end[1]:.2f}" stroke="#d1d5db" stroke-width="0.8"/>'
            )
        ground_label = screen(
            *_project_world(
                0.0,
                -0.98,
                0.0,
                cos_yaw=cos_yaw,
                sin_yaw=sin_yaw,
                cos_pitch=cos_pitch,
                sin_pitch=sin_pitch,
            )
        )
        parts.append(
            f'<text x="{ground_label[0]:.1f}" y="{ground_label[1] + 12:.1f}" '
            f'text-anchor="middle" font-family="sans-serif" font-size="9" '
            f'fill="#555555">{escape(tr("Ground"))}</text>'
        )

    for axis_end, label in (
        ((1.0, 0.0, 0.0), "X"),
        ((0.0, 1.0, 0.0), "Y"),
        ((0.0, 0.0, 1.0), "Z"),
    ):
        start = screen(
            *_project_world(
                0.0,
                0.0,
                0.0,
                cos_yaw=cos_yaw,
                sin_yaw=sin_yaw,
                cos_pitch=cos_pitch,
                sin_pitch=sin_pitch,
            )
        )
        end = screen(
            *_project_world(
                *axis_end,
                cos_yaw=cos_yaw,
                sin_yaw=sin_yaw,
                cos_pitch=cos_pitch,
                sin_pitch=sin_pitch,
            )
        )
        parts.append(
            f'<line x1="{start[0]:.2f}" y1="{start[1]:.2f}" '
            f'x2="{end[0]:.2f}" y2="{end[1]:.2f}" stroke="#6b7280" stroke-width="0.8"/>'
        )
        parts.append(
            f'<text x="{end[0] + 3:.1f}" y="{end[1] - 3:.1f}" '
            f'font-family="sans-serif" font-size="9" fill="#374151">{label}</text>'
        )

    for bin_index in range(GAIN_BINS):
        commands = []
        for first, second, segment_bin in segments:
            if segment_bin != bin_index:
                continue
            first_x, first_y = screen_points[first]
            second_x, second_y = screen_points[second]
            commands.append(f"M {first_x:.2f} {first_y:.2f} L {second_x:.2f} {second_y:.2f}")
        if not commands:
            continue
        color = _gain_color((bin_index + 0.5) / GAIN_BINS)
        parts.append(
            f'<path d="{" ".join(commands)}" fill="none" stroke="{color}" '
            'stroke-width="0.9" stroke-linecap="round"/>'
        )

    max_label = tr(
        "Max {gain:.2f} dBi at θ={theta:.0f}°, φ={phi:.0f}°",
        gain=max_gain,
        theta=max_theta,
        phi=max_phi,
    )
    label_x = min(marker_x + 8, WIDTH - 190)
    label_y = max(marker_y - 8, 34)
    label_width = min(180.0, len(max_label) * 5.2 + 8.0)
    parts.extend(
        [
            f'<circle cx="{marker_x:.2f}" cy="{marker_y:.2f}" r="4" '
            'fill="#111827" stroke="#ffffff" stroke-width="1.5"/>',
            f'<rect x="{label_x - 3:.1f}" y="{label_y - 10:.1f}" '
            f'width="{label_width:.1f}" height="14" fill="#ffffff" '
            'fill-opacity="0.88"/>',
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" font-family="sans-serif" '
            f'font-size="10" fill="#111827">{escape(max_label)}</text>',
        ]
    )

    swatch_height = 32
    swatch_count = 6
    for index in range(swatch_count):
        swatch_gain = 1.0 - index / (swatch_count - 1)
        swatch_y = 58 + index * swatch_height
        parts.append(
            f'<rect x="676" y="{swatch_y}" width="14" height="{swatch_height}" '
            f'fill="{_gain_color(swatch_gain)}" stroke="#ffffff" stroke-width="0.6"/>'
        )
    parts.extend(
        [
            f'<rect x="676" y="58" width="14" height="{swatch_height * swatch_count}" '
            'fill="none" stroke="#6b7280" stroke-width="0.8"/>',
            '<text x="696" y="54" font-family="sans-serif" font-size="9" '
            f'fill="#374151">{escape(tr("dBi"))}</text>',
            f'<text x="696" y="66" font-family="sans-serif" font-size="9" '
            f'fill="#374151">{max_gain:.1f}</text>',
            f'<text x="696" y="252" font-family="sans-serif" font-size="9" '
            f'fill="#374151">{raw_min:.1f}</text>',
            f'<text x="656" y="288" text-anchor="middle" font-family="sans-serif" '
            f'font-size="9" fill="#374151">{escape(tr("Gain"))}</text>',
            f'<text x="{WIDTH / 2:.1f}" y="414" text-anchor="middle" '
            f'font-family="sans-serif" font-size="11" fill="#333333">'
            f"{escape(caption_samples)}</text>",
            f'<text x="{WIDTH / 2:.1f}" y="434" text-anchor="middle" '
            f'font-family="sans-serif" font-size="11" fill="#333333">'
            f"{escape(caption_max)}</text>",
            "</svg>",
        ]
    )
    return PatternLobe(
        svg="".join(parts),
        displayed_theta_count=len(theta_positions),
        displayed_phi_count=len(phi_positions),
        segment_count=len(segments),
    )
