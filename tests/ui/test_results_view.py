# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    CurrentSample,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.widgets.results_view import ResultsView


def _make_result() -> SimulationResult:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.sweep(7_000_000.0, 7_200_000.0, 3))
    currents = (
        CurrentSample(1, 1, -1.0, 0.0, 8.0, 1.0, complex(0.1, 0.0), 0.1, 0.0),
        CurrentSample(2, 1, 0.0, 0.0, 8.0, 1.0, complex(0.2, 0.0), 0.2, 0.0),
        CurrentSample(3, 1, 1.0, 0.0, 8.0, 1.0, complex(0.1, 0.0), 0.1, 0.0),
    )
    frequencies = (
        FrequencyResult(7_000_000.0, 1, 2, complex(70.0, -10.0), 2.5, 0.001, currents=currents),
        FrequencyResult(7_100_000.0, 1, 2, complex(75.0, 0.0), 1.5, 0.001, currents=currents),
        FrequencyResult(7_200_000.0, 1, 2, complex(80.0, 10.0), 2.0, 0.001, currents=currents),
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=frequencies,
        duration_s=0.1,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def test_results_view_shows_currents_and_resonance(qtbot: QtBot) -> None:
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_result(_make_result())

    assert view._tabs.count() == 5
    assert view._table.rowCount() == 3
    assert view._currents_frequency.count() == 3
    assert len(view._currents_plot.listDataItems()) >= 1
    assert "Resonance" in view._resonance_label.text()


def test_results_view_localizes_known_diagnostics(qtbot: QtBot) -> None:
    from dataclasses import replace

    from antennadesk.domain.common.validation import Diagnostic, Severity

    result = replace(
        _make_result(),
        diagnostics=(
            Diagnostic(
                code="solver.timeout",
                severity=Severity.ERROR,
                message="nec2c timed out after 30 s",
            ),
        ),
    )
    view = ResultsView(Translator(Language.SPANISH))
    qtbot.addWidget(view)

    view.set_result(result)

    message_item = view._diagnostics.item(0, 2)
    assert message_item.text() == "El solver agotó el tiempo de espera."
    assert message_item.toolTip() == "nec2c timed out after 30 s"


def test_results_view_builds_a_polar_lobe_plot(qtbot: QtBot, tmp_path: Path) -> None:
    from dataclasses import replace

    from antennadesk.domain.simulation.result import FarFieldPoint

    points = tuple(
        FarFieldPoint(
            theta_deg=float(theta),
            phi_deg=phi,
            gain_vertical_db=gain,
            gain_horizontal_db=None,
            gain_total_db=gain,
            axial_ratio=None,
            tilt_deg=None,
            polarization="LINEAR",
            e_theta_magnitude_v_per_m=None,
            e_theta_phase_deg=None,
            e_phi_magnitude_v_per_m=None,
            e_phi_phase_deg=None,
        )
        for phi in (0.0, 90.0)
        for theta, gain in ((0.0, 2.0), (45.0, 1.0), (90.0, -2.0), (180.0, -8.0))
    )
    result = replace(
        _make_result(),
        frequencies=(
            replace(
                _make_result().frequencies[0],
                far_field=points,
            ),
        ),
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_result(result)
    view._pattern_frequency.setCurrentIndex(0)

    assert view._pattern_mode.currentData() == "azimuth"
    assert view._pattern_cut.currentData() == pytest.approx(0.0)
    assert len(view._polar_pattern._points) == 2
    assert view._polar_pattern._mirror is False
    assert view._polar_pattern.grab().isNull() is False

    view._pattern_mode.setCurrentIndex(1)
    assert view._pattern_mode.currentData() == "elevation"
    assert view._pattern_cut.currentData() == pytest.approx(0.0)
    assert len(view._polar_pattern._points) == 4
    assert view._polar_pattern._mirror is True
    assert len(view._pattern_3d._points) == 8
    view._pattern_view_tabs.setCurrentIndex(1)
    assert view._pattern_3d.grab().isNull() is False

    image_path = tmp_path / "pattern.png"
    view._pattern_view_tabs.setCurrentIndex(0)
    view.save_pattern_image(image_path)
    assert image_path.read_bytes().startswith(b"\x89PNG")


def test_pattern_3d_can_draw_a_ground_plane(qtbot: QtBot) -> None:
    from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView

    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    points = tuple(
        (float(theta), float(phi), 2.0 - theta / 90.0)
        for theta in range(0, 91, 10)
        for phi in range(0, 361, 30)
    )

    view.set_points(points, ground=True)

    assert view._ground is True
    assert view.grab().isNull() is False


def test_pattern_3d_supports_rotation_zoom_and_reset(qtbot: QtBot) -> None:
    from PySide6.QtCore import QPoint, Qt

    from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView

    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.show()
    view.set_points(((0.0, 0.0, 1.0), (90.0, 0.0, 0.0), (90.0, 180.0, 0.0), (45.0, 90.0, 0.5)))

    initial_yaw = view._yaw_deg
    initial_pitch = view._pitch_deg
    qtbot.mousePress(view, Qt.MouseButton.LeftButton, pos=QPoint(20, 20))
    qtbot.mouseMove(view, QPoint(60, 40))
    qtbot.mouseRelease(view, Qt.MouseButton.LeftButton, pos=QPoint(60, 40))
    assert view._yaw_deg != initial_yaw
    assert view._pitch_deg != initial_pitch

    class Wheel:
        def angleDelta(self) -> QPoint:
            return QPoint(0, 120)

        def accept(self) -> None:
            pass

    old_zoom = view._zoom
    view.wheelEvent(Wheel())  # type: ignore[arg-type]
    assert view._zoom > old_zoom

    view.reset_view()
    assert view._yaw_deg == 38.0
    assert view._pitch_deg == 26.0
    assert view._zoom == 1.0
