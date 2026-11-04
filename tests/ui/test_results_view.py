# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import itertools
import math
from datetime import UTC, datetime
from pathlib import Path

import pyqtgraph as pg
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

    assert view._tabs.count() == 6
    assert view._table.rowCount() == 3
    assert view._currents_frequency.count() == 3
    assert len(view._currents_plot.listDataItems()) >= 1
    assert "Resonance" in view._resonance_label.text()
    assert len(view._impedance_cursor._series) == 2
    view._impedance_cursor.show_at_x(7.1)
    assert "75.000" in view._impedance_cursor._label.text()
    assert "SWR 1.500" in view._impedance_cursor._label.text()
    view._swr_cursor.show_at_x(7.1)
    assert "SWR 1.500" in view._swr_cursor._label.text()
    view._currents_cursor.show_at_x(2.0)
    assert "segment 2" in view._currents_cursor._label.text()
    assert "0.2000 A" in view._currents_cursor._label.text()


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
    assert len(view._pattern_cursor._series) == 1
    view._pattern_cursor.show_at_x(45.0)
    assert "φ=45" in view._pattern_cursor._label.text()
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


def test_results_view_lists_only_pattern_snapshot_frequencies(qtbot: QtBot) -> None:
    from dataclasses import replace

    from antennadesk.domain.simulation.result import FarFieldPoint

    point = FarFieldPoint(
        theta_deg=0.0,
        phi_deg=0.0,
        gain_vertical_db=2.0,
        gain_horizontal_db=None,
        gain_total_db=2.0,
        axial_ratio=None,
        tilt_deg=None,
        polarization="LINEAR",
        e_theta_magnitude_v_per_m=None,
        e_theta_phase_deg=None,
        e_phi_magnitude_v_per_m=None,
        e_phi_phase_deg=None,
    )
    base = _make_result()
    result = replace(
        base,
        frequencies=(
            base.frequencies[0],
            replace(base.frequencies[1], far_field=(point,)),
            base.frequencies[2],
        ),
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_result(result)

    assert view._currents_frequency.count() == 3
    assert view._pattern_frequency.count() == 1
    assert view._pattern_frequency.itemText(0) == "7.1 MHz (40m)"
    assert view._selected_pattern_frequency() is result.frequencies[1]
    assert len(view._polar_pattern._points) == 1


def test_gain_color_maps_green_yellow_and_red() -> None:
    from antennadesk.ui.widgets.radiation_pattern_3d_view import gain_color

    low = gain_color(0.0)
    middle = gain_color(0.5)
    high = gain_color(1.0)

    assert low.green() > low.red()
    assert middle.red() > 200
    assert middle.green() > 150
    assert high.red() > high.green()
    assert gain_color(-1.0).getRgb()[:3] == gain_color(0.0).getRgb()[:3]
    assert gain_color(2.0).getRgb()[:3] == gain_color(1.0).getRgb()[:3]


def test_takeoff_angle_is_measured_from_the_ground_plane() -> None:
    from antennadesk.ui.widgets.radiation_pattern_3d_view import takeoff_angle_deg

    assert takeoff_angle_deg(0.0) == 90.0
    assert takeoff_angle_deg(30.0) == 60.0
    assert takeoff_angle_deg(90.0) == 0.0
    assert takeoff_angle_deg(150.0) == -60.0


def test_pattern_3d_max_label_shows_gain_and_takeoff_angle(qtbot: QtBot) -> None:
    from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView

    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.set_points(((75.0, 0.0, 12.34),), ground=True)
    assert view._max_gain_label((75.0, 0.0, 12.34)) == "Power gain 12.34 dBi · 15.0° above ground"

    view.set_points(((75.0, 0.0, 12.34),), ground=False)
    assert view._max_gain_label((75.0, 0.0, 12.34)) == "Power gain 12.34 dBi · 15.0° elevation"

    spanish = RadiationPattern3DView(Translator(Language.SPANISH))
    qtbot.addWidget(spanish)
    spanish.set_points(((75.0, 0.0, 12.34),), ground=True)
    assert (
        spanish._max_gain_label((75.0, 0.0, 12.34))
        == "Ganancia de potencia 12.34 dBi · 15.0° sobre el suelo"
    )


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


def test_pattern_3d_uses_a_coarser_mesh_during_interaction(qtbot: QtBot) -> None:
    from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView

    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.resize(800, 560)
    points = tuple(
        (
            float(theta),
            float(phi),
            5.0 + 3.0 * math.sin(math.radians(theta)),
        )
        for theta in range(0, 91)
        for phi in range(0, 361, 2)
    )

    view.set_points(points, ground=True)

    assert view._full_mesh is not None
    assert view._interactive_mesh is not None
    assert len(view._interactive_mesh.vertices) < len(view._full_mesh.vertices)
    assert len(view._interactive_mesh.segments) > 0
    assert view._interacting is False

    view._begin_interaction()
    assert view._interacting is True
    assert view.grab().isNull() is False
    view._end_interaction()
    assert view._interacting is False


def test_pattern_3d_reduces_the_full_mesh_resolution_by_40_percent(qtbot: QtBot) -> None:
    from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView

    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    points = tuple(
        (
            float(theta),
            float(phi),
            5.0 + 3.0 * math.sin(math.radians(theta)),
        )
        for theta in range(0, 91)
        for phi in range(0, 361, 2)
    )

    view.set_points(points, ground=True)

    assert view._full_mesh is not None
    assert view._interactive_mesh is not None
    original_vertices = 91 * 181
    ratio = len(view._full_mesh.vertices) / original_vertices
    assert 0.45 < ratio < 0.60
    assert len(view._full_mesh.vertices) > len(view._interactive_mesh.vertices)
    assert view._full_mesh.raw_max_gain == pytest.approx(8.0)
    theta_values = sorted({vertex.theta_deg for vertex in view._full_mesh.vertices})
    phi_values = sorted({vertex.phi_deg for vertex in view._full_mesh.vertices})
    theta_steps = [second - first for first, second in itertools.pairwise(theta_values)]
    phi_steps = [second - first for first, second in itertools.pairwise(phi_values)]
    assert max(theta_steps) - min(theta_steps) < 1e-6
    assert max(phi_steps) - min(phi_steps) < 1e-6


def test_pattern_3d_clips_below_ground_points(qtbot: QtBot) -> None:
    from antennadesk.ui.widgets.radiation_pattern_3d_view import RadiationPattern3DView

    view = RadiationPattern3DView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_points(
        ((0.0, 0.0, 2.0), (90.0, 0.0, 0.0), (180.0, 0.0, -5.0)),
        ground=True,
    )

    assert len(view._points) == 2
    assert all(theta <= 90.0 for theta, _phi, _gain in view._points)


def test_impedance_and_swr_charts_are_side_by_side(qtbot: QtBot) -> None:
    from PySide6.QtCore import Qt

    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    assert view._impedance_charts_splitter.orientation() == Qt.Orientation.Horizontal
    assert view._impedance_charts_splitter.count() == 2


def test_results_view_compares_measured_and_simulated_impedance(qtbot: QtBot) -> None:
    from uuid import UUID

    from antennadesk.domain.measurement import Measurement, MeasurementPoint

    measurement = Measurement(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        name="Field sweep",
        created_at=datetime(2026, 10, 30, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(70.0, -10.0)),
            MeasurementPoint(7_100_000.0, complex(75.0, 0.0)),
            MeasurementPoint(7_200_000.0, complex(80.0, 10.0)),
        ),
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_measurements((measurement,))
    view.set_result(_make_result())

    assert view._measurement_metric.count() == 4
    assert view._measurement_table.columnCount() == 8
    assert (
        len(
            [
                item
                for item in view._measurement_plot.listDataItems()
                if isinstance(item, pg.PlotDataItem)
            ]
        )
        == 2
    )
    assert "Compared 3 points" in view._measurement_comparison.text()
    assert "mean" in view._measurement_comparison.text()
    assert "Measured resonance" in view._measurement_resonance.text()
    assert "Simulated resonance" in view._measurement_resonance.text()
    assert "Resonance difference" in view._measurement_resonance.text()
    view._measurement_cursor.show_at_x(7.1)
    assert "7.100000 MHz" in view._measurement_cursor._label.text()
    assert "Measured" in view._measurement_cursor._label.text()
    assert "Simulated" in view._measurement_cursor._label.text()

    view._measurement_metric.setCurrentIndex(1)

    assert view._measurement_plot.getAxis("left").labelText == "R (Ω)"
    assert (
        len(
            [
                item
                for item in view._measurement_plot.listDataItems()
                if isinstance(item, pg.PlotDataItem)
            ]
        )
        == 2
    )


def test_results_view_requests_measurement_edit_and_delete(qtbot: QtBot) -> None:
    from uuid import UUID

    from antennadesk.domain.measurement import Measurement, MeasurementPoint

    measurement = Measurement(
        id=UUID("00000000-0000-0000-0000-000000000004"),
        name="Field sweep",
        created_at=datetime(2026, 10, 30, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),),
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.set_measurements((measurement,))

    with qtbot.waitSignal(view.measurement_edit_requested) as edit_signal:
        view._measurement_edit.click()
    assert edit_signal.args[0] == measurement

    with qtbot.waitSignal(view.measurement_delete_requested) as delete_signal:
        view._measurement_delete.click()
    assert delete_signal.args[0] == measurement


def test_results_view_shows_imported_measurements(qtbot: QtBot) -> None:
    from datetime import UTC, datetime
    from uuid import UUID

    from antennadesk.domain.measurement import Measurement, MeasurementPoint

    measurement = Measurement(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        name="Field sweep",
        created_at=datetime(2026, 10, 30, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(50.0, 0.0)),
            MeasurementPoint(7_100_000.0, complex(75.0, 0.0)),
        ),
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_measurements((measurement,))

    assert view._tabs.count() == 6
    assert view._measurement_selector.count() == 1
    assert view._measurement_table.rowCount() == 2
    assert view._measurement_plot.listDataItems()


def test_results_view_shows_directivity_and_realized_gain(qtbot: QtBot) -> None:
    from dataclasses import replace

    from antennadesk.domain.simulation.result import FarFieldPoint

    point = FarFieldPoint(
        theta_deg=90.0,
        phi_deg=0.0,
        gain_vertical_db=2.0,
        gain_horizontal_db=None,
        gain_total_db=2.0,
        axial_ratio=1.0,
        tilt_deg=0.0,
        polarization="linear",
        e_theta_magnitude_v_per_m=None,
        e_theta_phase_deg=None,
        e_phi_magnitude_v_per_m=None,
        e_phi_phase_deg=None,
    )
    result = _make_result()
    frequency = replace(
        result.frequencies[1],
        far_field=(point,),
        directivity_db=2.2,
        realized_gain_db=1.8,
        mismatch_loss_db=0.2,
        feed_line_loss_db=0.1,
        network_loss_db=0.05,
    )
    result = replace(result, frequencies=(frequency,))
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_result(result)

    text = view._gain_summary.text()
    assert "Power gain 2.00 dBi" in text
    assert "Directivity 2.20 dBi" in text
    assert "Realized gain 1.80 dBi" in text
    assert "Mismatch 0.20 dB" in text
    assert "line 0.10 dB" in text
    assert "network 0.05 dB" in text


def test_results_view_adds_a_band_summary_tab(qtbot: QtBot) -> None:
    from datetime import UTC, datetime
    from uuid import uuid4

    from antennadesk.domain.simulation.band_result import BandAnalysisResult, BandResult
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    bands = tuple(
        BandResult(amateur_band_by_id(band_id), _make_result())
        for band_id in ("40m", "20m")
        if amateur_band_by_id(band_id) is not None
    )
    analysis = BandAnalysisResult(
        design_id=uuid4(),
        batch_id=uuid4(),
        created_at=datetime(2026, 11, 3, tzinfo=UTC),
        bands=bands,
    )

    view.set_band_analysis(analysis)

    assert view._tabs.count() == 7
    assert view._bands_tab_index == 6
    assert view._bands_table.rowCount() == 2
    assert view._bands_table.item(0, 0).text() == "40m"
    assert view._bands_table.item(0, 2).text() == "1.500"
    assert view._bands_table.item(0, 7).text() == "Simulation completed"

    with qtbot.waitSignal(view.band_selected, timeout=1_000):
        view._bands_table.selectRow(1)
    assert view._result is not None
    assert view._result.frequencies[0].frequency_hz == 7_000_000.0

    view.set_band_analysis(None)
    assert view._tabs.count() == 6


def test_results_view_lists_all_band_patterns_in_one_selector(qtbot: QtBot) -> None:
    from dataclasses import replace
    from uuid import uuid4

    from antennadesk.domain.simulation.band_result import BandAnalysisResult, BandResult
    from antennadesk.domain.simulation.bands import amateur_band_by_id
    from antennadesk.domain.simulation.result import FarFieldPoint

    points = (FarFieldPoint(0.0, 0.0, 2.0, None, 2.0, 0.0, 0.0, "LINEAR", None, None, None, None),)
    base = _make_result()
    bands = []
    for band_id, frequency_hz in (("40m", 7_100_000.0), ("20m", 14_100_000.0)):
        band = amateur_band_by_id(band_id)
        assert band is not None
        frequency = replace(
            base.frequencies[1],
            frequency_hz=frequency_hz,
            far_field=points,
        )
        bands.append(BandResult(band, replace(base, frequencies=(frequency,))))
    analysis = BandAnalysisResult(
        design_id=uuid4(),
        batch_id=uuid4(),
        created_at=datetime(2026, 11, 3, tzinfo=UTC),
        bands=tuple(bands),
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.set_band_analysis(analysis)
    view.set_result(bands[0].result)

    assert view._pattern_frequency.count() == 2
    assert view._pattern_frequency.itemText(0).endswith("(40m)")
    assert view._pattern_frequency.itemText(1).endswith("(20m)")

    with qtbot.waitSignal(view.band_selected, timeout=1_000):
        view._pattern_frequency.setCurrentIndex(1)

    assert view._result is bands[1].result
    assert view._bands_table.currentRow() == 1


def test_results_view_saves_one_pattern_image_per_band(
    qtbot: QtBot,
    tmp_path: Path,
) -> None:
    from dataclasses import replace
    from uuid import uuid4

    from antennadesk.domain.simulation.band_result import BandAnalysisResult, BandResult
    from antennadesk.domain.simulation.bands import amateur_band_by_id
    from antennadesk.domain.simulation.result import FarFieldPoint

    points = (
        FarFieldPoint(0.0, 0.0, 2.0, None, 2.0, 0.0, 0.0, "LINEAR", None, None, None, None),
        FarFieldPoint(45.0, 0.0, 1.0, None, 1.0, 0.0, 0.0, None, None, None, None, None),
    )
    base = _make_result()
    result = replace(
        base,
        frequencies=tuple(replace(frequency, far_field=points) for frequency in base.frequencies),
    )
    bands = tuple(
        BandResult(amateur_band_by_id(band_id), result)
        for band_id in ("40m", "20m")
        if amateur_band_by_id(band_id) is not None
    )
    analysis = BandAnalysisResult(
        design_id=uuid4(),
        batch_id=uuid4(),
        created_at=datetime(2026, 11, 3, tzinfo=UTC),
        bands=bands,
    )
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.set_band_analysis(analysis)
    paths = tuple(tmp_path / f"{band.band.name}.png" for band in bands)

    saved = view.save_band_pattern_images(paths)

    assert saved == paths
    assert all(path.read_bytes().startswith(b"\x89PNG") for path in paths)


def test_results_view_selects_the_pattern_gain_metric(qtbot: QtBot) -> None:
    from dataclasses import replace

    from antennadesk.domain.simulation.pattern import PatternGainMetric
    from antennadesk.domain.simulation.result import FarFieldPoint

    points = (
        FarFieldPoint(0.0, 0.0, 2.0, None, 5.0, 0.0, 0.0, "LINEAR", None, None, None, None),
        FarFieldPoint(90.0, 0.0, 2.0, None, 2.0, 0.0, 0.0, "LINEAR", None, None, None, None),
    )
    base = _make_result()
    frequency = replace(
        base.frequencies[0],
        far_field=points,
        directivity_db=8.0,
        realized_gain_db=4.0,
    )
    result = replace(base, frequencies=(frequency,))
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.set_result(result)

    view._pattern_metric.setCurrentIndex(
        view._pattern_metric.findData(PatternGainMetric.DIRECTIVITY.value)
    )
    view._pattern_cursor.show_at_x(0.0)

    assert "Directivity" in view._pattern_cursor._label.text()
    assert "8.000 dBi" in view._pattern_cursor._label.text()

    frequency = replace(frequency, directivity_db=None)
    view.set_result(replace(result, frequencies=(frequency,)))
    view._pattern_metric.setCurrentIndex(
        view._pattern_metric.findData(PatternGainMetric.DIRECTIVITY.value)
    )
    assert "unavailable" in view._pattern_plot.plotItem.titleLabel.text
