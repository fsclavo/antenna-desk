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
            supports_far_field=False,
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
