# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Sensitivity tuning assistant dialog."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.application.ports.antenna_solver import AntennaSolver
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.design.tuning import (
    TuningProbe,
    TuningProposal,
    TuningReferenceKind,
    TuningRequest,
    TuningStatus,
)
from antennadesk.domain.measurement import Measurement, MeasurementPoint
from antennadesk.domain.projects.project import DesignVariant
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.tuning_assistant_dialog import TuningAssistantDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


class _TuningSolver:
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="analytical",
            supports_frequency_sweep=True,
            supports_currents=True,
            supports_far_field=True,
            supports_perfect_ground=True,
            supports_finite_ground=True,
            supports_extended_thin_wire_kernel=True,
        )

    def validate(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        del model, spec
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="analytical", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: object = None,
        cancel_token: object = None,
    ) -> SimulationResult:
        del progress_callback, cancel_token
        length = model.wires[0].length_m
        resonance = 7_100_000.0 - 1_000_000.0 * (length - 20.0)
        frequencies = []
        for frequency_hz in spec.frequency_plan.frequencies_hz:
            impedance = complex(50.0, 50.0 * (frequency_hz - resonance) / 1e6)
            reflection = (impedance - 50.0) / (impedance + 50.0)
            magnitude = abs(reflection)
            frequencies.append(
                FrequencyResult(
                    frequency_hz=frequency_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=impedance,
                    swr=(1.0 + magnitude) / (1.0 - magnitude),
                    input_power_w=0.001,
                )
            )
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=tuple(frequencies),
            duration_s=0.0,
        )


def _measurement() -> Measurement:
    return Measurement(
        id=UUID("00000000-0000-0000-0000-000000000051"),
        name="Field sweep",
        created_at=datetime(2026, 11, 12, 15, 0, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(
            MeasurementPoint(7_000_000.0, complex(50.0, -10.0)),
            MeasurementPoint(7_100_000.0, complex(50.0, 10.0)),
        ),
    )


def _dialog(
    qtbot: QtBot,
    *,
    language: Language = Language.ENGLISH,
    solver: AntennaSolver | None = None,
) -> TuningAssistantDialog:
    design = DesignVariant(
        id=UUID("00000000-0000-0000-0000-000000000052"),
        name="40 m dipole",
        antenna_type="wire_dipole",
        parameters=DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        antenna=DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ).to_antenna(name="40 m dipole"),
    )
    dialog = TuningAssistantDialog(
        Translator(language),
        UnitSystem.METRIC,
        solver or _TuningSolver(),
        design,
        _measurement(),
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
    )
    qtbot.addWidget(dialog)
    return dialog


def _proposal(status: TuningStatus = TuningStatus.PROPOSED) -> TuningProposal:
    request = TuningRequest(
        target_frequency_hz=7_100_000.0,
        measured_frequency_hz=7_050_000.0,
        measured_kind=TuningReferenceKind.RESONANCE,
        current_dimension_m=20.0,
        max_adjustment_m=0.1,
    )
    if status is not TuningStatus.PROPOSED:
        return TuningProposal(
            status=status,
            request=request,
            bounds_min_m=19.9,
            bounds_max_m=20.1,
            message_key="tuning.message.no_sensitivity",
        )
    return TuningProposal(
        status=TuningStatus.PROPOSED,
        request=request,
        probes=(
            TuningProbe(20.0, 7_100_000.0, 1.2, None),
            TuningProbe(19.9, 7_200_000.0, 1.4, None),
            TuningProbe(20.1, 7_000_000.0, 1.6, None),
            TuningProbe(19.95, 7_150_000.0, 1.05, None),
        ),
        slope_hz_per_m=-1_000_000.0,
        proposed_dimension_m=19.95,
        proposed_change_m=-0.05,
        predicted_resonance_hz=7_150_000.0,
        predicted_swr=1.05,
        bounds_min_m=19.9,
        bounds_max_m=20.1,
        message_key="tuning.message.verified",
    )


def test_dialog_initial_state_and_measurement_reference(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert dialog.windowTitle() == "Sensitivity tuning assistant"
    assert dialog._target.value() == pytest.approx(7.1)
    assert "20.0000 m" in dialog._current_dimension_value.text()
    assert "Measured resonance" in dialog._measured_reference.text()
    assert dialog._analyze.isEnabled()
    assert dialog._apply.isEnabled() is False

    dialog._target.setValue(7.0)

    assert "Measured resonance" in dialog._measured_reference.text()


def test_dialog_renders_a_verified_proposal(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._show_proposal(_proposal())

    assert "-1000.000 kHz/m" in dialog._sensitivity.text()
    assert "Proposed change: -0.0500 m" in dialog._proposal.text()
    assert "Predicted model resonance" in dialog._prediction.text()
    assert dialog._table.rowCount() == 4
    assert dialog._apply.isEnabled() is True
    parameters = dialog.result_parameters()
    assert isinstance(parameters, DipoleParameters)
    assert parameters.total_length_m == pytest.approx(19.95)


def test_dialog_disables_apply_without_a_proposal(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._show_proposal(_proposal(TuningStatus.NO_SENSITIVITY))

    assert dialog._apply.isEnabled() is False
    assert "not sensitive" in dialog._message.text().lower()


def test_dialog_retranslates(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot, language=Language.SPANISH)

    assert dialog.windowTitle() == "Asistente de ajuste por sensibilidad"
    assert dialog._analyze.text() == "Analizar"
    assert dialog._table.horizontalHeaderItem(0).text() == "Sonda"


def test_dialog_runs_the_worker_and_accepts(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._start()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=15_000)

    proposal = dialog.proposal()
    assert proposal is not None
    assert proposal.status is TuningStatus.PROPOSED
    assert dialog._apply.isEnabled() is True
    dialog._apply_result()
    assert dialog.result() == QDialog.DialogCode.Accepted
