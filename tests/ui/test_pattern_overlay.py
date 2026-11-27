# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Canonical antenna overlay and outline helpers for UX48."""

from __future__ import annotations

import math

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.pattern_overlay import (
    AUTO_FULL_WIRE_LIMIT,
    OVERLAY_EXTENT_FRACTION,
    AntennaOverlay,
    OverlayMode,
    OverlayWire,
    convex_hull,
    overlay_from_model,
    overlay_scale,
)
from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView


def test_overlay_uses_one_uniform_scale_from_its_center() -> None:
    model = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
            YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
        ),
        height_m=10.0,
    ).to_antenna()
    overlay = overlay_from_model(model)
    assert overlay is not None

    fed = overlay.feed
    scale = overlay_scale(overlay)
    distances = [
        math.dist(point, fed) * scale for wire in overlay.wires for point in (wire.start, wire.end)
    ]

    assert max(distances) == pytest.approx(OVERLAY_EXTENT_FRACTION)
    assert all(distance <= OVERLAY_EXTENT_FRACTION + 1e-12 for distance in distances)


@pytest.mark.parametrize("azimuth_deg", [0.0, 90.0])
def test_beam_overlay_centers_on_the_symmetry_plane(azimuth_deg: float) -> None:
    parameters = quad_beam_parameters(frequency_hz=14_100_000.0, azimuth_deg=azimuth_deg)
    overlay = overlay_from_model(
        parameters.to_antenna(),
        forward_azimuth=azimuth_deg,
    )
    assert overlay is not None
    assert overlay.center is not None

    points = [
        point for wire in overlay.wires if not wire.support for point in (wire.start, wire.end)
    ]
    center_x = (min(point[0] for point in points) + max(point[0] for point in points)) / 2.0
    center_y = (min(point[1] for point in points) + max(point[1] for point in points)) / 2.0
    angle = math.radians(azimuth_deg)
    cross = (-math.sin(angle), math.cos(angle))
    offset = (overlay.feed[0] - center_x) * cross[0] + (overlay.feed[1] - center_y) * cross[1]

    assert (
        (overlay.center[0] - center_x) * cross[0] + (overlay.center[1] - center_y) * cross[1]
    ) == pytest.approx(0.0, abs=1e-9)
    assert overlay.feed[0] - overlay.center[0] == pytest.approx(offset * cross[0])
    assert overlay.feed[1] - overlay.center[1] == pytest.approx(offset * cross[1])
    assert overlay.center[2] == pytest.approx(overlay.feed[2])
    assert overlay.center != overlay.feed

    scale = overlay_scale(overlay)
    distances = [
        math.dist(point, overlay.center) * scale
        for wire in overlay.wires
        for point in (wire.start, wire.end)
    ]
    assert max(distances) == pytest.approx(OVERLAY_EXTENT_FRACTION)


def test_center_fed_beam_and_non_beam_overlays_keep_the_feed_center() -> None:
    yagi = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
            YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
        ),
        height_m=10.0,
        azimuth_deg=90.0,
    )
    beam = overlay_from_model(yagi.to_antenna(), forward_azimuth=90.0)
    vertical = overlay_from_model(yagi.to_antenna())
    assert beam is not None
    assert vertical is not None

    assert beam.center == pytest.approx(beam.feed)
    assert vertical.center == pytest.approx(vertical.feed)


def test_overlay_keeps_support_wires_and_excludes_transmission_lines() -> None:
    model = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
            YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
        ),
        height_m=10.0,
        mast_diameter_m=0.05,
        mast_offset_m=1.5,
        guy_count=2,
        guy_anchor_radius_m=4.0,
        guy_diameter_m=0.003,
    ).to_antenna()
    overlay = overlay_from_model(model)
    assert overlay is not None

    assert overlay.wire_count == len(model.wires)
    assert any(wire.support for wire in overlay.wires)
    assert all(wire.start is not None and wire.end is not None for wire in overlay.wires)


def test_auto_mode_uses_full_below_the_budget_and_outline_above() -> None:
    small = AntennaOverlay(
        wires=tuple(
            OverlayWire((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)) for _ in range(AUTO_FULL_WIRE_LIMIT)
        ),
        feed=(0.0, 0.0, 0.0),
    )
    large = AntennaOverlay(
        wires=tuple(
            OverlayWire((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)) for _ in range(AUTO_FULL_WIRE_LIMIT + 1)
        ),
        feed=(0.0, 0.0, 0.0),
    )
    view = RadiationPattern3DView(Translator(Language.ENGLISH))

    view.set_overlay(small)
    view.set_overlay_mode(OverlayMode.AUTO)
    assert view._effective_overlay_mode() is OverlayMode.FULL

    view.set_overlay(large)
    assert view._effective_overlay_mode() is OverlayMode.OUTLINE
    view.set_overlay_mode(OverlayMode.FULL)
    assert view._effective_overlay_mode() is OverlayMode.FULL


def test_convex_hull_derives_an_envelope_from_endpoints() -> None:
    hull = convex_hull(((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.5, 0.5)))

    assert set(hull) == {(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)}


def test_pattern_view_accepts_the_overlay_snapshot(qtbot: QtBot) -> None:
    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()
    overlay = overlay_from_model(model)
    assert overlay is not None
    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.resize(720, 480)
    view.set_points(
        ((0.0, 0.0, 10.0), (45.0, 0.0, 5.0), (90.0, 0.0, 1.0), (90.0, 180.0, 1.0)),
        footprint_segments=((0.0, -10.0, 0.0, 10.0),),
        feed_point=(0.0, 0.0),
    )
    view.set_overlay(overlay)
    view.set_overlay_visible(True)

    view.show()
    qtbot.wait(10)

    assert view._overlay_visible is True
    assert view.grab().isNull() is False
    assert "Schematic" in view._overlay_note()
