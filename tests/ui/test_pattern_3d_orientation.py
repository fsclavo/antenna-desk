# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX46 orientation indicators in the 3D pattern view."""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QRectF
from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.pattern_overlay import OverlayMode
from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView

POINTS = (
    (0.0, 0.0, 12.3),
    (45.0, 0.0, 6.0),
    (45.0, 90.0, 3.0),
    (90.0, 0.0, 1.0),
    (90.0, 180.0, 0.5),
)


def test_pattern_3d_accepts_orientation_and_back_ray_metadata(qtbot: QtBot) -> None:
    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_points(
        POINTS,
        antenna_azimuth=90.0,
        forward_azimuth=90.0,
        front_to_back_db=12.34,
    )

    assert view._antenna_azimuth == pytest.approx(90.0)
    assert view._forward_azimuth == pytest.approx(90.0)
    assert view._front_to_back_db == pytest.approx(12.34)
    assert view._shows_back_ray() is True
    assert view._back_label() == "Back (same elevation) · F/B 12.3 dB"
    assert view._antenna_label() == "Antenna φ=90°"
    assert "φ=90°" in view._max_gain_label_with_azimuth((75.0, 90.0, 12.34))


def test_pattern_3d_vertical_antenna_uses_a_dot_not_a_front_axis(qtbot: QtBot) -> None:
    view = RadiationPattern3DView(Translator(Language.SPANISH))
    qtbot.addWidget(view)

    view.set_points(
        POINTS,
        antenna_azimuth=0.0,
        antenna_vertical=True,
        front_to_back_db=None,
    )

    assert view._antenna_label() == "Antena"
    assert view._back_label() == "Atrás (misma elevación)"
    assert view._shows_back_ray() is False
    assert view.accessibleDescription()


def test_pattern_3d_orientation_labels_survive_compact_sizes(qtbot: QtBot) -> None:
    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.resize(300, 220)
    view.set_points(
        POINTS,
        antenna_azimuth=0.0,
        forward_azimuth=0.0,
        front_to_back_db=8.0,
    )

    view.show()
    qtbot.wait(10)

    assert view.grab().isNull() is False


def test_results_view_passes_forward_axis_and_front_to_back(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    from datetime import UTC, datetime

    from antennadesk.application.use_cases.create_dipole_project import (
        CreateDipoleProject,
        CreateDipoleProjectCommand,
    )
    from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
    from antennadesk.domain.simulation.frequency import FrequencyPlan
    from antennadesk.domain.simulation.result import (
        FarFieldPoint,
        FrequencyResult,
        SimulationResult,
        SimulationStatus,
    )
    from antennadesk.domain.simulation.solver import SolverMetadata
    from antennadesk.domain.simulation.spec import SimulationSpec
    from antennadesk.ui.widgets.results_view import ResultsView

    parameters = YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.2, radius_m=0.001),
            YagiElement(position_m=2.1, length_m=9.8, radius_m=0.001),
        ),
        height_m=10.0,
        azimuth_deg=90.0,
    )
    design = CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="Orientation",
            variant_name="Yagi",
            parameters=parameters,
        )
    )
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(parameters.frequency_hz))
    frequency = FrequencyResult(
        frequency_hz=parameters.frequency_hz,
        feed_tag=1,
        feed_segment=1,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=0.001,
        far_field=(
            FarFieldPoint(45.0, 0.0, None, None, 10.0, 0.0, 0.0, None, None, None, None, None),
            FarFieldPoint(45.0, 180.0, None, None, 0.0, 0.0, 0.0, None, None, None, None, None),
        ),
    )
    result = SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="fake", version="1.0"),
        frequencies=(frequency,),
        duration_s=0.1,
        started_at=datetime(2026, 11, 26, tzinfo=UTC),
        finished_at=datetime(2026, 11, 26, tzinfo=UTC),
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_result(result)
    view.set_design(design.designs[0])

    assert view._pattern_3d._antenna_azimuth == pytest.approx(90.0)
    assert view._pattern_3d._forward_azimuth == pytest.approx(90.0)
    assert view._pattern_3d._front_to_back_db == pytest.approx(10.0)
    assert view._pattern_3d._footprint_segments
    assert view._pattern_3d._feed_point is not None
    assert view._pattern_overlay_show.isChecked() is False
    view._pattern_overlay_show.setChecked(True)
    assert view._pattern_3d._overlay_visible is True
    view._pattern_overlay_mode.setCurrentIndex(
        view._pattern_overlay_mode.findData(OverlayMode.OUTLINE.value)
    )
    assert view._pattern_3d._overlay_mode is OverlayMode.OUTLINE
    image_path = tmp_path / "pattern-overlay.png"
    view.save_pattern_image(image_path)
    assert image_path.read_bytes().startswith(b"\x89PNG")


def test_pattern_3d_draws_a_plan_inset_with_footprint_and_feed(qtbot: QtBot) -> None:
    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.resize(720, 480)
    view.set_points(
        POINTS,
        antenna_azimuth=90.0,
        forward_azimuth=90.0,
        front_to_back_db=6.0,
        footprint_segments=((0.0, -5.0, 0.0, 5.0), (2.1, -4.9, 2.1, 4.9)),
        feed_point=(2.1, 0.0),
    )

    assert view._feed_point == (2.1, 0.0)
    assert view._minimap_rect(QRectF(0.0, 0.0, 632.0, 402.0)) is not None
    view.show()
    qtbot.wait(10)
    assert view.grab().isNull() is False


def test_pattern_3d_hides_the_plan_inset_at_compact_sizes(qtbot: QtBot) -> None:
    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    assert view._minimap_rect(QRectF(0.0, 0.0, 320.0, 220.0)) is None
