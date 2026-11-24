# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Live tuning preview dialog tests."""

from __future__ import annotations

from datetime import UTC, datetime

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.dipole import DipoleParameters
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
    def validate(self, model, spec):
        return ()

    def run(self, model, spec, *, cancel_token=None):
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
        is_simulation_running=lambda: False,
    )
    qtbot.addWidget(dialog)
    dialog.show()

    qtbot.waitUntil(lambda: "SWR 1.000" in dialog._result_label.text(), timeout=3000)
    dialog._slider.setValue(120)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._apply_clicked()
    qtbot.waitUntil(lambda: not dialog._applying, timeout=3000)

    assert applied
    assert applied[0].total_length_m != parameters.total_length_m
    assert dialog.isVisible()
    assert dialog._slider.value() == 100


def test_live_tuning_can_apply_twice_without_reopening(qtbot: QtBot) -> None:
    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    applied = []
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        applied.append,
        is_simulation_running=lambda: False,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)

    dialog._slider.setValue(120)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._apply_clicked()
    qtbot.waitUntil(lambda: not dialog._applying, timeout=3000)
    dialog._slider.setValue(80)
    qtbot.waitUntil(lambda: not dialog._busy, timeout=3000)
    dialog._apply_clicked()
    qtbot.waitUntil(lambda: not dialog._applying, timeout=3000)

    assert len(applied) == 2
    assert dialog.isVisible()
    assert applied[0].total_length_m != applied[1].total_length_m


def test_live_tuning_shows_a_coarse_pattern_and_can_hide_it(qtbot: QtBot) -> None:
    parameters = DipoleParameters(frequency_hz=7_000_000.0, total_length_m=20.0, height_m=10.0)
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_000_000.0))
    dialog = LiveTuningDialog(
        Translator(Language.ENGLISH),
        parameters,
        spec,
        _FakeSolver(),
        lambda parameters: None,
        is_simulation_running=lambda: False,
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
        is_simulation_running=lambda: False,
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
    qtbot.waitUntil(lambda: not dialog._applying, timeout=3000)

    assert applied
    assert applied[-1].height_m != parameters.height_m
    assert applied[-1].total_length_m == parameters.total_length_m
    assert dialog.isVisible()
