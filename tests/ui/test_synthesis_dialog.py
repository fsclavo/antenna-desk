# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.optimization.synthesis import SynthesisStatus
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import FrequencyResult, SimulationResult, SimulationStatus
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.dialogs.synthesis_dialog import SynthesisDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


class AnalyticalOCFDSolver:
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

    def validate(self, model: AntennaModel, spec: SimulationSpec) -> tuple[Diagnostic, ...]:
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
        length = model.wires[0].length_m
        ratio = model.feed.offset_m / length
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=model.design_frequency_hz,
                    feed_tag=1,
                    feed_segment=1,
                    impedance_ohm=complex(50.0 + 100.0 * (ratio - 0.33), 20.0 * (length - 20.0)),
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
        )


@pytest.mark.parametrize("folded", [False, True])
def test_synthesis_dialog_exposes_j_pole_variables(folded: bool, qtbot: QtBot) -> None:
    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
        folded=folded,
    )
    dialog = SynthesisDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalOCFDSolver(),
        parameters,
        SimulationSpec(frequency_plan=FrequencyPlan.single(145_000_000.0)),
    )
    qtbot.addWidget(dialog)
    variables = dialog._variables()
    assert variables[0].name == "radiator_height_m"
    assert variables[1].name == ("stub_length_m" if folded else "feed_offset_m")
    values = {
        "radiator_height_m": 1.05,
        "stub_length_m": 0.55,
        "feed_offset_m": 0.12,
    }
    built = dialog._build_parameters(values)
    assert isinstance(built, JPoleParameters)
    assert built.folded is folded


def test_synthesis_dialog_finds_ocfd_dimensions(qtbot: QtBot) -> None:
    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        feed_ratio=0.33,
        height_m=10.0,
    )
    dialog = SynthesisDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        AnalyticalOCFDSolver(),
        parameters,
        SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0)),
    )
    qtbot.addWidget(dialog)
    dialog._min_a.setValue(19.0)
    dialog._max_a.setValue(21.0)
    dialog._min_b.setValue(23.0)
    dialog._max_b.setValue(43.0)
    dialog.show()

    dialog._run.click()
    qtbot.waitUntil(lambda: dialog._thread is None, timeout=5_000)

    assert dialog._result is not None
    assert dialog._result.status is SynthesisStatus.CONVERGED
    assert dialog.selected_parameters() is not None
    selected = dialog.selected_parameters()
    assert isinstance(selected, OCFDParameters)
    assert selected.total_length_m == pytest.approx(20.0, abs=0.01)
    assert selected.feed_ratio == pytest.approx(0.33, abs=0.001)
    assert dialog._apply.isEnabled() is True

    dialog._apply.click()
    assert dialog.result() == QDialog.DialogCode.Accepted
