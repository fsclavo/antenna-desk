# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Live tuning preview dialog tests."""

from __future__ import annotations

import threading
from datetime import UTC, datetime

from PySide6.QtCore import QThread
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.application.cancellation import EventCancelToken
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.flower_pot import flower_pot_2m
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.common.reflection import calculate_swr
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.live_tuning_dialog import LiveTuningDialog
from antennadesk.ui.i18n import Language, Translator


class _FakeSolver:
    def __init__(self) -> None:
        self.calls: list[SimulationSpec] = []

    def validate(self, model, spec):
        return ()

    def run(self, model, spec, *, cancel_token=None):
        self.calls.append(spec)
        frequency = spec.frequency_plan.start_hz
        impedance = complex(50.0, 0.0)
        far_field = (
            tuple(
                FarFieldPoint(
                    theta_deg=theta,
                    phi_deg=0.0,
                    gain_vertical_db=2.0,
                    gain_horizontal_db=None,
                    gain_total_db=2.0 - abs(theta - 90.0) / 45.0,
                    axial_ratio=0.0,
                    tilt_deg=0.0,
                    polarization="LINEAR",
                    e_theta_magnitude_v_per_m=None,
                    e_theta_phase_deg=None,
                    e_phi_magnitude_v_per_m=None,
                    e_phi_phase_deg=None,
                )
                for theta in (0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0)
            )
            if spec.far_field.enabled
            else ()
        )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=SolverMetadata(name="fake", version="1"),
            frequencies=(
                FrequencyResult(
                    frequency,
                    1,
                    1,
                    impedance,
                    calculate_swr(impedance, 50.0),
                    0.01,
                    far_field=far_field,
                ),
            ),
            duration_s=0.01,
            started_at=datetime(2026, 11, 20, tzinfo=UTC),
            finished_at=datetime(2026, 11, 20, tzinfo=UTC),
        )

    def capabilities(self):
        return SolverCapabilities(
            name="fake",
            supports_frequency_sweep=True,
            supports_currents=False,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )


def test_live_tuning_previews_and_applies(qtbot: QtBot) -> None:
    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    applied = []
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        applied.append,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    qtbot.waitUntil(lambda: "SWR 1.000" in dialog._result_label.text(), timeout=3000)
    dialog._slider.setValue(120)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._apply_clicked()

    assert applied
    assert applied[0].total_length_m != parameters.total_length_m
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert not dialog.isVisible()


def test_live_tuning_shows_a_coarse_pattern_and_can_hide_it(qtbot: QtBot) -> None:
    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        lambda parameters: None,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: bool(dialog._pattern_view._points), timeout=3000)

    assert dialog._pattern_preview.isChecked() is True
    assert dialog._pattern_view._points

    dialog._pattern_preview.setChecked(False)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    assert dialog._pattern_view._points == ()


def test_live_tuning_can_switch_to_a_secondary_dimension(qtbot: QtBot) -> None:
    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    applied = []
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        applied.append,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)

    height_index = dialog._dimension_combo.findData("height")
    assert height_index >= 0
    dialog._dimension_combo.setCurrentIndex(height_index)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._slider.setValue(120)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._apply_clicked()

    assert applied
    assert applied[-1].height_m != parameters.height_m
    assert applied[-1].total_length_m == parameters.total_length_m
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_live_tuning_exposes_flower_pot_feed_and_choke_heights(qtbot: QtBot) -> None:
    parameters = flower_pot_2m()
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(parameters.frequency_hz))
    applied = []
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        applied.append,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)

    choke_index = dialog._dimension_combo.findData("choke_height")
    assert choke_index >= 0
    dialog._dimension_combo.setCurrentIndex(choke_index)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._slider.setValue(dialog._slider.value() + 5)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._apply_clicked()

    assert applied
    assert applied[-1].choke_height_m != parameters.choke_height_m
    assert applied[-1].base_height_m == parameters.base_height_m


def test_live_tuning_can_tune_an_angle_dimension(qtbot: QtBot) -> None:
    parameters = InvertedVParameters(
        frequency_hz=7_000_000.0,
        leg_length_m=10.0,
        apex_height_m=10.0,
        included_angle_deg=120.0,
    )
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    applied = []
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        applied.append,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    index = dialog._dimension_combo.findData("included_angle")
    assert index >= 0
    dialog._dimension_combo.setCurrentIndex(index)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._slider.setValue(120)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)

    assert "°" in dialog._dimension_label.text()
    dialog._apply_clicked()

    assert applied
    assert applied[-1].included_angle_deg != parameters.included_angle_deg
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_live_tuning_can_tune_radial_droop(qtbot: QtBot) -> None:
    parameters = VerticalParameters(
        frequency_hz=7_000_000.0,
        height_m=10.0,
        base_height_m=3.0,
        radial_count=4,
        radial_length_m=5.0,
        radial_droop_deg=10.0,
    )
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    applied = []
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        applied.append,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    index = dialog._dimension_combo.findData("radial_droop")
    assert index >= 0
    dialog._dimension_combo.setCurrentIndex(index)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._slider.setValue(120)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)

    assert "°" in dialog._dimension_label.text()
    dialog._apply_clicked()

    assert applied
    assert applied[-1].radial_droop_deg > parameters.radial_droop_deg
    assert applied[-1].radial_tip_height_m > 0.0
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_live_tuning_discards_a_stale_result_after_the_target_changes(
    qtbot: QtBot,
) -> None:
    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    solver = _FakeSolver()
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        solver,
        lambda updated: None,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: bool(solver.calls) and not dialog._busy, timeout=3000)
    dialog._debounce.stop()

    old_request = dialog._request_id
    token = EventCancelToken()
    dialog._token = token
    dialog._busy = True
    height_index = dialog._dimension_combo.findData("height")
    assert height_index >= 0
    dialog._dimension_combo.setCurrentIndex(height_index)
    dialog._debounce.stop()

    assert token.is_cancelled()
    assert dialog._request_id > old_request

    dialog._result_label.clear()
    stale_result = solver.run(parameters.to_antenna(), spec)
    dialog._finished(old_request, stale_result)

    assert dialog._result_label.text() == ""
    assert dialog._busy is False


def test_live_tuning_apply_stops_a_pending_debounce(qtbot: QtBot) -> None:
    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    solver = _FakeSolver()
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        solver,
        lambda updated: None,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: len(solver.calls) == 1 and not dialog._busy, timeout=3000)

    dialog._slider.setValue(120)
    assert dialog._debounce.isActive()
    dialog._apply_clicked()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog._debounce.isActive() is False
    qtbot.wait(400)
    assert len(solver.calls) == 1


def test_live_tuning_delivers_results_on_the_gui_thread(qtbot: QtBot) -> None:
    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    finished_threads: list[QThread] = []

    class ThreadCheckingDialog(LiveTuningDialog):
        def _finished(self, request_id, result):
            finished_threads.append(QThread.currentThread())
            super()._finished(request_id, result)

    dialog = ThreadCheckingDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        lambda parameters: None,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: bool(finished_threads), timeout=3000)

    assert all(thread is dialog.thread() for thread in finished_threads)
    dialog.close()


def test_live_tuning_close_detaches_a_running_preview(qtbot: QtBot) -> None:
    class SlowSolver(_FakeSolver):
        def __init__(self) -> None:
            super().__init__()
            self.started = threading.Event()
            self.release = threading.Event()
            self.done = threading.Event()

        def run(self, model, spec, *, cancel_token=None):
            self.started.set()
            try:
                self.release.wait(5.0)
                return super().run(model, spec, cancel_token=cancel_token)
            finally:
                self.done.set()

    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    solver = SlowSolver()
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        solver,
        lambda updated: None,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(solver.started.is_set, timeout=3_000)

    dialog.close()
    solver.release.set()
    qtbot.waitUntil(solver.done.is_set, timeout=5_000)
    qtbot.wait(100)

    assert dialog.isVisible() is False


def test_live_tuning_repeated_close_during_a_preview_is_stable(qtbot: QtBot) -> None:
    class DelayedSolver(_FakeSolver):
        def run(self, model, spec, *, cancel_token=None):
            QThread.msleep(20)
            return super().run(model, spec, cancel_token=cancel_token)

    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    for _ in range(10):
        dialog = LiveTuningDialog(
            Translator(Language.ENGLISH),
            parameters,
            spec,
            DelayedSolver(),
            lambda updated: None,
        )
        qtbot.addWidget(dialog)
        dialog._debounce.setInterval(1)
        dialog.show()
        qtbot.waitUntil(lambda current=dialog: current._busy, timeout=3_000)
        dialog.close()
        qtbot.wait(30)
