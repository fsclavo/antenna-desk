# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Optimization and synthesis dialogs applied to the main window."""

from __future__ import annotations

import pytest
from helpers import wait_for_condition
from main_window_support import use_parameters
from PySide6.QtWidgets import QDialog, QInputDialog
from pytestqt.qtbot import QtBot

from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow


def test_optimize_length_applies_and_simulates(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_dimension_m(self) -> float:
            return 19.8

    monkeypatch.setattr(
        main_window_module,
        "OptimizationDialog",
        FakeOptimizationDialog,
    )

    assert window._optimize_action.isEnabled() is True
    window.optimize_length()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert window._form.parameters().total_length_m == pytest.approx(19.8)
    assert window._project is not None
    assert window._project.designs[0].parameters.total_length_m == pytest.approx(19.8)
    assert window._results._table.rowCount() == 1
    window._dirty = False


def test_optimize_endfed_applies_to_the_endfed_form(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters

    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=10.0,
    )

    class FakeEndFedDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> EndFedParameters:
            return parameters

        def result_band_plan(self):
            from antennadesk.domain.design.band_plan import default_band_plan

            return default_band_plan(parameters).plan

    monkeypatch.setattr(main_window_module, "EndFedDialog", FakeEndFedDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("End-fed", True))
    window.new_endfed_antenna()

    class FakeOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_dimension_m(self) -> float:
            return 21.0

    monkeypatch.setattr(
        main_window_module,
        "OptimizationDialog",
        FakeOptimizationDialog,
    )

    assert window._optimize_action.isEnabled() is True
    window.optimize_length()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert window._endfed_form.parameters().length_m == pytest.approx(21.0)
    assert window._project is not None
    assert window._project.designs[0].parameters.length_m == pytest.approx(21.0)
    assert window._results._table.rowCount() == 1
    window._dirty = False


def test_optimize_biquad_applies_to_the_biquad_form(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters

    parameters = biquad_parameters(BiquadKind.SINGLE)
    use_parameters(window, parameters)
    optimized = replace(
        parameters,
        loop_side_m=parameters.loop_side_m * 1.03,
    )

    class FakeFamilyOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> object:
            return optimized

    monkeypatch.setattr(
        main_window_module,
        "FamilyOptimizationDialog",
        FakeFamilyOptimizationDialog,
    )
    monkeypatch.setattr(window, "simulate", lambda: None)

    window.optimize_current_design()
    window._dirty = False

    assert window._project is not None
    assert window._project.designs[0].antenna_type == "biquad"
    assert window._project.designs[0].parameters.loop_side_m == pytest.approx(
        optimized.loop_side_m,
        abs=1e-3,
    )
    assert window._biquad_form.parameters().loop_side_m == pytest.approx(
        optimized.loop_side_m,
        abs=1e-3,
    )
    window._dirty = False


def test_optimize_current_design_persists_the_run_summary(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dataclasses import replace
    from datetime import UTC, datetime

    from antennadesk.application.use_cases.optimize_antenna import (
        OptimizeAntennaResult,
    )
    from antennadesk.domain.optimization.engine import (
        BudgetProfile,
        OptimizationStatus,
        budget_for,
    )
    from antennadesk.domain.optimization.summary import (
        OptimizationMode,
        OptimizationSummary,
    )

    assert window._project is not None
    current = window._project.designs[0]
    optimized = replace(current.parameters, total_length_m=19.5)
    summary = OptimizationSummary(
        mode=OptimizationMode.SINGLE,
        objective="min_swr",
        status="converged",
        budget_profile="fast",
        evaluations=60,
        seed=0,
        best_values={"total_length_m": 19.5},
        best_metrics={"swr": 1.1},
        completed_at=datetime(2026, 11, 7, 12, 0, tzinfo=UTC),
    )
    result = OptimizeAntennaResult(
        status=OptimizationStatus.CONVERGED,
        best_parameters=optimized,
        best_values={"total_length_m": 19.5},
        best_score=1.1,
        best_metrics={"swr": 1.1},
        evaluations=(),
        sensitivity=(),
        budget=budget_for(BudgetProfile.FAST, 3),
        seed=0,
        summary=summary,
    )

    class FakeFamilyOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> object:
            return optimized

        def selected_result(self) -> OptimizeAntennaResult:
            return result

    monkeypatch.setattr(
        main_window_module,
        "FamilyOptimizationDialog",
        FakeFamilyOptimizationDialog,
    )
    monkeypatch.setattr(window, "simulate", lambda: None)

    window.optimize_current_design()

    stored = window._project.designs[0].optimization_summary
    assert stored == summary
    assert window._project.designs[0].parameters.total_length_m == pytest.approx(19.5)
    window._dirty = False


def test_every_supported_optimizer_has_a_ui_adapter() -> None:
    from antennadesk.domain.optimization.registry import SUPPORTED_OPTIMIZER_TYPES
    from antennadesk.ui.optimization_adapters import ADAPTERS

    assert set(ADAPTERS) == SUPPORTED_OPTIMIZER_TYPES


def test_optimize_bobtail_curtain_applies_to_the_scv_form(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.scv import ScvKind, scv_parameters

    parameters = scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0)
    use_parameters(window, parameters)
    optimized = replace(parameters, horizontal_length_m=39.0)

    class FakeFamilyOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> object:
            return optimized

    monkeypatch.setattr(
        main_window_module,
        "FamilyOptimizationDialog",
        FakeFamilyOptimizationDialog,
    )
    monkeypatch.setattr(window, "simulate", lambda: None)

    assert window._optimize_action.isEnabled() is True
    window.optimize_current_design()

    assert window._scv_form.parameters().horizontal_length_m == pytest.approx(39.0)
    assert window._project is not None
    assert window._project.designs[0].parameters.horizontal_length_m == pytest.approx(39.0)
    window._dirty = False


def test_optimize_ocfd_applies_to_the_ocfd_form(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.ocfd import OCFDParameters

    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        feed_ratio=0.33,
        height_m=10.0,
    )

    class FakeOCFDDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> OCFDParameters:
            return parameters

        def result_band_plan(self):
            from antennadesk.domain.design.band_plan import default_band_plan

            return default_band_plan(parameters).plan

    monkeypatch.setattr(main_window_module, "OCFDDialog", FakeOCFDDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("OCFD", True))
    window.new_ocfd_antenna()

    class FakeOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_dimension_m(self) -> float:
            return 21.0

    monkeypatch.setattr(
        main_window_module,
        "OptimizationDialog",
        FakeOptimizationDialog,
    )

    assert window._optimize_action.isEnabled() is True
    window.optimize_length()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert window._ocfd_form.parameters().total_length_m == pytest.approx(21.0)
    assert window._project is not None
    assert window._project.designs[0].parameters.total_length_m == pytest.approx(21.0)
    assert window._results._table.rowCount() == 1
    window._dirty = False


def test_synthesize_dimensions_applies_and_simulates(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.ocfd import OCFDParameters

    parameters = OCFDParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        feed_ratio=0.33,
        height_m=10.0,
    )

    class FakeOCFDDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> OCFDParameters:
            return parameters

        def result_band_plan(self):
            from antennadesk.domain.design.band_plan import default_band_plan

            return default_band_plan(parameters).plan

    monkeypatch.setattr(main_window_module, "OCFDDialog", FakeOCFDDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("OCFD", True))
    window.new_ocfd_antenna()

    synthesized = replace(parameters, total_length_m=21.0, feed_ratio=0.4)

    class FakeSynthesisDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> OCFDParameters:
            return synthesized

    monkeypatch.setattr(main_window_module, "SynthesisDialog", FakeSynthesisDialog)

    assert window._optimize_action.isEnabled() is True
    window.synthesize_dimensions()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert window._ocfd_form.parameters().total_length_m == pytest.approx(21.0)
    assert window._project is not None
    assert window._project.designs[0].parameters.total_length_m == pytest.approx(21.0)
    assert window._project.designs[0].parameters.feed_ratio == pytest.approx(0.4)
    assert window._results._table.rowCount() == 1
    window._dirty = False


def test_optimize_loop_applies_circumference_and_simulates(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    class FakeOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_dimension_m(self) -> float:
            return 41.2

    monkeypatch.setattr(
        main_window_module,
        "OptimizationDialog",
        FakeOptimizationDialog,
    )
    window._form.set_antenna_type("loop")
    window._form._length.setValue(40.0)
    window._form._sides.setValue(4)
    window.apply_design()
    assert window._optimize_action.isEnabled() is True

    window.optimize_length()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )

    assert window._project is not None
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, LoopParameters)
    assert parameters.circumference_m == pytest.approx(41.2, abs=1e-6)
    assert window._results._table.rowCount() == 1
    window._dirty = False


def test_optimize_yagi_applies_and_simulates(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dataclasses import replace

    from antennadesk.domain.antennas.yagi import YagiParameters, nbs_five_element

    parameters = nbs_five_element(frequency_hz=14_100_000.0, height_m=12.0)

    class FakeYagiDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> object:
            return parameters

    monkeypatch.setattr(main_window_module, "YagiDialog", FakeYagiDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Yagi", True))
    window.new_yagi_antenna()

    elements = list(parameters.elements)
    elements[0] = replace(elements[0], length_m=elements[0].length_m + 0.1)
    optimized = replace(parameters, elements=tuple(elements))

    captured: dict[str, object] = {}

    class FakeYagiOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> object:
            return optimized

    monkeypatch.setattr(
        main_window_module,
        "ElementOptimizationDialog",
        FakeYagiOptimizationDialog,
    )

    assert window._optimize_action.isEnabled() is True
    monkeypatch.setattr(window, "simulate", lambda: None)
    window.optimize_yagi_elements()

    variables = captured["variables"]
    assert isinstance(variables, tuple)
    assert all(variable.name != "element_count" for variable in variables)
    assert len(variables) == 2 * len(parameters.elements) - 1
    gap_variable = next(variable for variable in variables if variable.name == "gap_1")
    assert gap_variable.minimum == 0.1
    assert captured["hint_key"] == "element_optimize.yagi_hint"

    build = captured["build_parameters"]
    built = build({variable.name: variable.current_m for variable in variables})
    assert isinstance(built, YagiParameters)
    assert len(built.elements) == len(parameters.elements)

    assert window._yagi_form.parameters().elements[0].length_m == pytest.approx(
        optimized.elements[0].length_m, abs=1e-3
    )
    assert window._project is not None
    assert window._project.designs[0].parameters.elements[0].length_m == pytest.approx(
        optimized.elements[0].length_m, abs=1e-3
    )
    window._dirty = False


def test_zs6bkw_optimizer_requires_a_typed_generator(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.zs6bkw import zs6bkw_parameters

    use_parameters(window, zs6bkw_parameters())
    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", errors.append)

    assert window._estimate_button.isEnabled() is False
    assert window._optimize_action.isEnabled() is False
    window.optimize_current_design()

    assert errors == [window._translator.t("optimize.unavailable.custom_generator")]
    window._dirty = False


def test_t2fd_can_estimate_and_optimize(window: MainWindow) -> None:
    from antennadesk.domain.antennas.t2fd import T2FDParameters

    use_parameters(
        window,
        T2FDParameters(
            frequency_hz=1_800_000.0,
            highest_frequency_hz=30_000_000.0,
            length_m=50.8,
            spacing_m=1.69,
        ),
    )

    assert window._estimate_button.isEnabled() is True
    assert window._design_from_frequency_action.isEnabled() is True
    assert window._optimize_action.isEnabled() is True


def test_fan_optimizer_opens_on_the_selected_band(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement

    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=20.0, included_angle_deg=120.0),
            FanElement(length_m=5.0, included_angle_deg=100.0),
        ),
        apex_height_m=10.0,
    )

    class FakeFanDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> FanDipoleParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "FanDipoleDialog", FakeFanDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Fan", True))
    window.new_fan_dipole_antenna()
    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=5_000,
    )
    window._results._bands_table.selectRow(1)
    wait_for_condition(
        lambda: (
            window._design_id is not None
            and window._selected_band_ids.get(window._design_id) == "10m"
        ),
        timeout_ms=1_000,
    )

    captured: dict[str, object] = {}

    class FakeOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Rejected

    monkeypatch.setattr(
        main_window_module,
        "ElementOptimizationDialog",
        FakeOptimizationDialog,
    )
    window.optimize_fan_dipole_elements()

    from antennadesk.domain.design.formulas import frequency_for_half_wave_length

    assert captured["default_band_id"] == "10m"
    assert captured["default_frequency_hz"] == pytest.approx(frequency_for_half_wave_length(5.0))
    band_ids = {band.band_id for band in captured["bands"]}
    assert band_ids == {"40m", "10m"}
    window._dirty = False


def test_fan_optimizer_defaults_to_the_lowest_element_band(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
    from antennadesk.domain.design.formulas import frequency_for_half_wave_length

    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=10.0, included_angle_deg=120.0),
            FanElement(length_m=5.0, included_angle_deg=100.0),
        ),
        apex_height_m=10.0,
    )

    class FakeFanDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> FanDipoleParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "FanDipoleDialog", FakeFanDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Fan", True))
    window.new_fan_dipole_antenna()

    captured: dict[str, object] = {}

    class FakeOptimizationDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Rejected

    monkeypatch.setattr(
        main_window_module,
        "ElementOptimizationDialog",
        FakeOptimizationDialog,
    )
    window.optimize_fan_dipole_elements()

    assert captured["default_band_id"] is None
    assert captured["default_frequency_hz"] == pytest.approx(frequency_for_half_wave_length(10.0))
    window._dirty = False
