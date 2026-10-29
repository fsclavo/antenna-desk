# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.application.ports.antenna_solver import ProgressCallback
from antennadesk.application.ports.cancellation import CancelToken
from antennadesk.domain.antennas.antenna import AntennaModel
from antennadesk.domain.common.validation import Diagnostic
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverCapabilities, SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem


class FakeSolver:
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            name="fake",
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
        return ()

    def version(self) -> SolverMetadata:
        return SolverMetadata(name="fake", version="1.0")

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        return SimulationResult(
            status=SimulationStatus.COMPLETED,
            spec=spec,
            model_fingerprint="a" * 64,
            solver=self.version(),
            frequencies=(
                FrequencyResult(
                    frequency_hz=7_100_000.0,
                    feed_tag=1,
                    feed_segment=11,
                    impedance_ohm=complex(50.0, 0.0),
                    swr=1.0,
                    input_power_w=0.001,
                ),
            ),
            duration_s=0.01,
        )


@pytest.fixture
def window(qtbot: QtBot) -> Iterator[MainWindow]:
    main_window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(main_window)
    yield main_window
    main_window._dirty = False
    main_window.close()


def test_default_project_is_ready(window: MainWindow) -> None:
    assert window._project is not None
    assert window._project.name == "40 m dipole"
    parameters = window._form.parameters()
    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert parameters.total_length_m == pytest.approx(20.0)
    assert parameters.height_m == pytest.approx(8.0)
    assert window._geometry._model is not None
    assert window._results._table.rowCount() == 0


def test_simulate_updates_results(window: MainWindow, qtbot: QtBot) -> None:
    window.simulate()
    qtbot.waitUntil(
        lambda: not window._simulating and window._thread is None,
        timeout=5_000,
    )

    assert window._results._table.rowCount() == 1
    assert window._results._table.item(0, 0).text() == "7.100000"
    assert window._status_label.text() == "Simulation completed"
    window._dirty = False


def test_save_project_writes_a_native_file(
    window: MainWindow,
    tmp_path: Path,
) -> None:
    path = tmp_path / "saved.antennadesk"

    assert window._save_to(path) is True

    assert path.is_file()
    assert window._dirty is False


def test_language_switch_updates_actions(window: MainWindow) -> None:
    window._set_language(Language.SPANISH)
    assert window._simulate_action.text() == "Simular"

    window._set_language(Language.ENGLISH)
    assert window._simulate_action.text() == "Simulate"


def test_unit_switch_preserves_physical_length(window: MainWindow) -> None:
    window._set_unit_system(UnitSystem.IMPERIAL)
    assert window._form.parameters().total_length_m == pytest.approx(20.0, abs=0.01)

    window._set_unit_system(UnitSystem.METRIC)
    assert window._form.parameters().total_length_m == pytest.approx(20.0, abs=0.001)


def test_editing_form_marks_project_dirty(window: MainWindow) -> None:
    window._dirty = False
    window._form._length.setValue(window._form._length.value() + 1.0)

    assert window._dirty is True
    window._dirty = False


def test_unit_switch_does_not_mark_project_dirty(window: MainWindow) -> None:
    window._dirty = False
    window._set_unit_system(UnitSystem.IMPERIAL)

    assert window._dirty is False


def test_geometry_view_mode_controls(window: MainWindow) -> None:
    assert window._view_combo.currentData() == "elevation"
    assert window._height_combo.isEnabled() is True

    window._view_combo.setCurrentIndex(1)
    assert window._geometry._mode.value == "plan"
    assert window._height_combo.isEnabled() is False

    window._view_combo.setCurrentIndex(0)
    assert window._geometry._mode.value == "elevation"
    assert window._height_combo.isEnabled() is True


def test_height_exaggeration_control(window: MainWindow) -> None:
    window._height_combo.setCurrentIndex(2)

    assert window._geometry._height_exaggeration == pytest.approx(2.0)
