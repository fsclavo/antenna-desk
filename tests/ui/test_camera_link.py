# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX49 linked 3D cameras between geometry and the pattern lobe."""

from __future__ import annotations

import math

import pytest
from helpers import make_completed_result
from main_window_support import use_parameters
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QWidget
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.ui.geometry.views import GeometryViewMode
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.geometry_view import GeometryView
from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView

DEFAULT_CAMERA = (GeometryView.DEFAULT_YAW_DEG, GeometryView.DEFAULT_PITCH_DEG)


def _drag(
    widget: QWidget,
    qtbot: QtBot,
    *,
    start: tuple[int, int] = (100, 100),
    delta: tuple[int, int] = (50, 20),
) -> None:
    start_point = QPoint(*start)
    end_point = QPoint(start[0] + delta[0], start[1] + delta[1])
    qtbot.mousePress(widget, Qt.MouseButton.LeftButton, pos=start_point)
    qtbot.mouseMove(widget, end_point)
    qtbot.mouseRelease(widget, Qt.MouseButton.LeftButton, pos=end_point)


def _set_view(window: MainWindow, mode: GeometryViewMode) -> None:
    index = window._view_combo.findData(mode.value)
    assert index >= 0
    window._view_combo.setCurrentIndex(index)


def _enable_link(window: MainWindow) -> None:
    window._link_3d_views.setChecked(True)


def test_link_switches_construction_to_3d_and_adopts_the_geometry_camera(
    window: MainWindow,
) -> None:
    window._geometry.set_camera(72.0, 11.0)

    _enable_link(window)

    assert window._geometry.mode is GeometryViewMode.THREE_D
    assert window._view_combo.currentData() == GeometryViewMode.THREE_D.value
    assert window._results.pattern_camera() == pytest.approx((72.0, 11.0))
    assert window._status_label.text() == "3D views linked; geometry camera adopted."


def test_linked_drag_propagates_in_both_directions(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    _enable_link(window)

    _drag(window._geometry, qtbot)
    geometry_camera = window._geometry.camera_angles()
    assert geometry_camera != pytest.approx(DEFAULT_CAMERA)
    assert window._results.pattern_camera() == pytest.approx(geometry_camera)

    pattern_before = window._results.pattern_camera()
    _drag(window._results._pattern_3d, qtbot, start=(120, 120), delta=(-60, 30))

    assert window._results.pattern_camera() != pytest.approx(pattern_before)
    assert window._geometry.camera_angles() == pytest.approx(window._results.pattern_camera())


def test_unlinked_views_stay_independent(window: MainWindow, qtbot: QtBot) -> None:
    window._geometry.set_camera(61.0, 9.0)
    window._results.set_pattern_camera(12.0, 4.0)

    _drag(window._geometry, qtbot)
    assert window._results.pattern_camera() == pytest.approx((12.0, 4.0))

    geometry_before = window._geometry.camera_angles()
    _drag(window._results._pattern_3d, qtbot)
    assert window._results.pattern_camera() != pytest.approx((12.0, 4.0))
    assert window._geometry.camera_angles() == pytest.approx(geometry_before)


def test_linked_double_click_resets_both_cameras(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    _enable_link(window)
    _drag(window._geometry, qtbot)
    assert window._results.pattern_camera() != pytest.approx(DEFAULT_CAMERA)

    qtbot.mouseDClick(
        window._results._pattern_3d,
        Qt.MouseButton.LeftButton,
        pos=QPoint(80, 80),
    )
    assert window._geometry.camera_angles() == pytest.approx(DEFAULT_CAMERA)
    assert window._results.pattern_camera() == pytest.approx(DEFAULT_CAMERA)

    _drag(window._results._pattern_3d, qtbot)
    assert window._geometry.camera_angles() != pytest.approx(DEFAULT_CAMERA)
    qtbot.mouseDClick(
        window._geometry,
        Qt.MouseButton.LeftButton,
        pos=QPoint(80, 80),
    )
    assert window._geometry.camera_angles() == pytest.approx(DEFAULT_CAMERA)
    assert window._results.pattern_camera() == pytest.approx(DEFAULT_CAMERA)


def test_linked_design_change_resets_both_cameras_and_keeps_3d(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    _enable_link(window)
    _drag(window._geometry, qtbot)
    assert window._results.pattern_camera() != pytest.approx(DEFAULT_CAMERA)

    use_parameters(
        window,
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=21.0,
            height_m=8.0,
        ),
    )

    assert window._link_3d_views.isChecked() is True
    assert window._geometry.mode is GeometryViewMode.THREE_D
    assert window._view_combo.currentData() == GeometryViewMode.THREE_D.value
    assert window._geometry.camera_angles() == pytest.approx(DEFAULT_CAMERA)
    assert window._results.pattern_camera() == pytest.approx(DEFAULT_CAMERA)


def test_linked_model_refresh_without_auto_select_keeps_3d(window: MainWindow) -> None:
    _enable_link(window)
    assert window._project is not None
    assert window._design_id is not None
    design = window._project.design_by_id(window._design_id)

    window._set_geometry_model(design)

    assert window._geometry.mode is GeometryViewMode.THREE_D
    assert window._view_combo.currentData() == GeometryViewMode.THREE_D.value
    assert window._geometry.camera_angles() == pytest.approx(DEFAULT_CAMERA)
    assert window._results.pattern_camera() == pytest.approx(DEFAULT_CAMERA)


def test_pattern_result_refresh_keeps_the_linked_camera(window: MainWindow) -> None:
    _enable_link(window)
    window._results.set_pattern_camera(66.0, 14.0)
    window._geometry.set_camera(66.0, 14.0)

    window._results.set_result(make_completed_result())

    assert window._results.pattern_camera() == pytest.approx((66.0, 14.0))
    assert window._geometry.camera_angles() == pytest.approx((66.0, 14.0))


def test_link_off_on_sequence_adopts_the_geometry_camera_again(
    window: MainWindow,
    qtbot: QtBot,
) -> None:
    _enable_link(window)
    _drag(window._geometry, qtbot)
    synced_camera = window._geometry.camera_angles()

    window._link_3d_views.setChecked(False)
    _drag(window._geometry, qtbot)
    independent_camera = window._geometry.camera_angles()
    assert independent_camera != pytest.approx(synced_camera)
    assert window._results.pattern_camera() == pytest.approx(synced_camera)

    window._link_3d_views.setChecked(True)
    assert window._results.pattern_camera() == pytest.approx(independent_camera)


def test_switching_to_construction_turns_the_link_off(window: MainWindow) -> None:
    _enable_link(window)

    _set_view(window, GeometryViewMode.CONSTRUCTION)

    assert window._link_3d_views.isChecked() is False
    assert window._status_label.text() == ("3D view link off: geometry is in Construction view.")


def test_link_help_and_labels_retranslate(window: MainWindow) -> None:
    _enable_link(window)
    window._set_language(Language.SPANISH)

    assert window._link_3d_views.text() == "Vincular 3D"
    assert window._status_label.text() == (
        "Vistas 3D vinculadas; se adoptó la cámara de geometría."
    )
    assert window._link_3d_views.accessibleDescription()
    assert window._link_3d_views.toolTip()


def test_set_camera_is_silent_and_user_interaction_emits(
    qtbot: QtBot,
) -> None:
    pattern = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(pattern)
    pattern_emissions: list[tuple[float, float]] = []
    pattern.camera_changed.connect(lambda yaw, pitch: pattern_emissions.append((yaw, pitch)))
    pattern.set_camera(64.0, 15.0)
    assert pattern_emissions == []
    _drag(pattern, qtbot)
    assert pattern_emissions
    assert pattern.camera_angles() == pytest.approx(pattern_emissions[-1])

    geometry = GeometryView(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(geometry)
    geometry_model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna()
    geometry.set_model(geometry_model)
    geometry.set_view_mode(GeometryViewMode.THREE_D)
    geometry_emissions: list[tuple[float, float]] = []
    geometry.camera_changed.connect(lambda yaw, pitch: geometry_emissions.append((yaw, pitch)))
    geometry.set_camera(64.0, 15.0)
    assert geometry_emissions == []
    geometry.reset_view()
    assert geometry_emissions == [pytest.approx(DEFAULT_CAMERA)]
    assert geometry.camera_angles() == pytest.approx(DEFAULT_CAMERA)


def test_projection_is_exact_across_both_3d_views() -> None:
    yaw_deg = 38.0
    pitch_deg = 26.0
    cos_yaw = math.cos(math.radians(yaw_deg))
    sin_yaw = math.sin(math.radians(yaw_deg))
    cos_pitch = math.cos(math.radians(pitch_deg))
    sin_pitch = math.sin(math.radians(pitch_deg))
    takeoff = math.radians(20.0)
    beam_forward = (0.0, math.cos(takeoff), math.sin(takeoff))

    for vector in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), beam_forward):
        geometry = GeometryView._project_3d(
            *vector,
            cos_yaw,
            sin_yaw,
            cos_pitch,
            sin_pitch,
        )
        pattern = RadiationPattern3DView._project_world_point(
            *vector,
            cos_yaw,
            sin_yaw,
            cos_pitch,
            sin_pitch,
        )
        assert geometry == pytest.approx(pattern, abs=1e-9)
