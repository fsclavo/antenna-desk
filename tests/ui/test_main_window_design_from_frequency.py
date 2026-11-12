# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency-first estimation and applying the estimated design."""

from __future__ import annotations

import pytest
from main_window_support import use_parameters
from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem


def test_design_from_frequency_applies_estimated_parameters(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters
    from antennadesk.domain.design import Confidence, DimensionEstimate

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=41.0,
        height_m=8.0,
        sides=3,
    )
    assert window._project is not None
    current = window._project.design_by_id(window._design_id)
    initial = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=42.0,
        height_m=8.0,
        sides=4,
    )
    window._project = window._project.with_design(
        current.with_parameters(initial),
        updated_at=window._project.updated_at,
    )
    window._select_design(current.id)

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def estimated_estimate(self) -> DimensionEstimate:
            return DimensionEstimate(
                parameters=parameters,
                method_id="test.loop",
                confidence=Confidence.EMPIRICAL,
                tolerance_m=0.1,
                source_ids=("test.source",),
            )

        def estimated_parameters(self) -> LoopParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "DesignFromFrequencyDialog", FakeDialog)
    window._dirty = False

    assert window._estimate_button.text() == "Estimate Dimensions..."
    window._estimate_button.click()

    assert window._project is not None
    design = window._project.design_by_id(window._design_id)
    assert isinstance(design.parameters, LoopParameters)
    assert design.parameters.circumference_m == pytest.approx(41.0)
    assert design.parameters.sides == 3
    assert design.antenna_type == "loop"
    assert design.provenance is not None
    assert design.provenance.method_id == "test.loop"
    assert design.provenance.source_ids == ("test.source",)
    assert "test.loop" in window._provenance_label.text()
    assert window._design_stack.currentWidget() is window._form_scroll
    assert window._status_label.text() == "Estimated dimensions applied. Review them and simulate."
    window._undo_stack.undo()
    assert window._project.designs[0].parameters != parameters
    window._undo_stack.redo()
    assert window._project.designs[0].parameters.sides == 3
    window._dirty = False


def test_design_from_frequency_preserves_the_loop_orientation(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.loop import LoopOrientation, LoopParameters
    from antennadesk.domain.design import Confidence, DimensionEstimate

    estimated = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=41.0,
        height_m=8.0,
        sides=4,
    )
    assert window._project is not None
    current = window._project.design_by_id(window._design_id)
    initial = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=42.0,
        height_m=10.0,
        sides=4,
        orientation=LoopOrientation.HORIZONTAL,
    )
    window._project = window._project.with_design(
        current.with_parameters(initial),
        updated_at=window._project.updated_at,
    )
    window._select_design(current.id)

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def estimated_estimate(self) -> DimensionEstimate:
            return DimensionEstimate(
                parameters=estimated,
                method_id="test.loop",
                confidence=Confidence.EMPIRICAL,
                tolerance_m=0.1,
                source_ids=("test.source",),
            )

    monkeypatch.setattr(main_window_module, "DesignFromFrequencyDialog", FakeDialog)
    window._dirty = False

    window._estimate_button.click()

    assert window._project is not None
    parameters = window._project.design_by_id(window._design_id).parameters
    assert isinstance(parameters, LoopParameters)
    assert parameters.orientation is LoopOrientation.HORIZONTAL
    assert parameters.circumference_m == pytest.approx(41.0)
    window._dirty = False


def test_design_from_frequency_can_open_the_refiner_after_applying(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    parameters = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=41.0,
        height_m=8.0,
        sides=4,
    )
    calls: list[bool] = []
    assert window._project is not None
    current = window._project.design_by_id(window._design_id)
    initial = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=42.0,
        height_m=8.0,
        sides=3,
    )
    window._project = window._project.with_design(
        current.with_parameters(initial),
        updated_at=window._project.updated_at,
    )
    window._select_design(current.id)

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def estimated_estimate(self):
            from antennadesk.domain.design import Confidence, DimensionEstimate

            return DimensionEstimate(
                parameters=parameters,
                method_id="test.loop",
                confidence=Confidence.EMPIRICAL,
                tolerance_m=0.1,
                source_ids=("test.source",),
            )

        def estimated_parameters(self) -> LoopParameters:
            return parameters

        def refine_requested(self) -> bool:
            return True

    monkeypatch.setattr(main_window_module, "DesignFromFrequencyDialog", FakeDialog)
    monkeypatch.setattr(window, "optimize_current_design", lambda: calls.append(True))
    window._dirty = False

    window.design_from_frequency()

    assert calls == [True]
    window._dirty = False


def test_design_from_frequency_passes_the_current_template(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.ringo import RingoParameters
    from antennadesk.domain.design import Confidence, DimensionEstimate

    initial = RingoParameters(
        frequency_hz=7_100_000.0,
        radiator_height_m=5.0,
        ring_diameter_m=1.0,
    )
    estimated = RingoParameters(
        frequency_hz=7_100_000.0,
        radiator_height_m=5.2,
        ring_diameter_m=1.1,
    )
    use_parameters(window, initial)
    captured: dict[str, object] = {}

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def estimated_estimate(self) -> DimensionEstimate:
            return DimensionEstimate(
                parameters=estimated,
                method_id="test.ringo",
                confidence=Confidence.HEURISTIC,
                tolerance_m=0.1,
            )

    monkeypatch.setattr(main_window_module, "DesignFromFrequencyDialog", FakeDialog)
    window._dirty = False

    window.design_from_frequency()

    assert isinstance(captured["initial_parameters"], RingoParameters)
    assert window._project is not None
    design = window._project.design_by_id(window._design_id)
    assert isinstance(design.parameters, RingoParameters)
    assert design.parameters.radiator_height_m == pytest.approx(5.2)
    assert design.antenna_type == "ringo"
    window._dirty = False


def test_design_from_frequency_rejects_a_template_change(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.ringo import RingoParameters
    from antennadesk.domain.design import Confidence, DimensionEstimate

    initial = RingoParameters(
        frequency_hz=7_100_000.0,
        radiator_height_m=5.0,
        ring_diameter_m=1.0,
    )
    use_parameters(window, initial)
    errors: list[str] = []

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def estimated_estimate(self) -> DimensionEstimate:
            return DimensionEstimate(
                parameters=window._form.parameters(),
                method_id="test.wrong-template",
                confidence=Confidence.EMPIRICAL,
                tolerance_m=0.1,
            )

    monkeypatch.setattr(main_window_module, "DesignFromFrequencyDialog", FakeDialog)
    monkeypatch.setattr(window, "_show_error", errors.append)
    window._dirty = False

    window.design_from_frequency()

    assert errors
    assert "template" in errors[0].lower()
    assert window._project is not None
    design = window._project.design_by_id(window._design_id)
    assert isinstance(design.parameters, RingoParameters)
    assert design.parameters.radiator_height_m == pytest.approx(5.0)
    window._dirty = False


def test_estimate_is_disabled_for_templates_without_an_estimator(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    use_parameters(
        window,
        TrapDipoleParameters(
            frequency_hz=7_100_000.0,
            high_band_frequency_hz=14_100_000.0,
            inner_length_m=10.0,
            outer_length_m=5.0,
            trap_frequency_hz=14_100_000.0,
            trap_inductance_h=10e-6,
        ),
    )

    assert window._estimate_button.isEnabled() is False
    assert window._design_from_frequency_action.isEnabled() is False
    assert "estimator" in window._estimate_button.toolTip().lower()


def test_design_from_frequency_preserves_t2fd_matching(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.t2fd import T2FDParameters
    from antennadesk.domain.design import Confidence, DimensionEstimate

    current = T2FDParameters(
        frequency_hz=1_800_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=50.0,
        spacing_m=1.7,
        termination_resistance_ohm=390.0,
        transformer_ratio=4.0,
    )
    use_parameters(window, current)
    estimated = T2FDParameters(
        frequency_hz=1_800_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=50.8,
        spacing_m=1.69,
    )

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def estimated_estimate(self) -> DimensionEstimate:
            return DimensionEstimate(
                parameters=estimated,
                method_id="test.t2fd",
                confidence=Confidence.HEURISTIC,
                tolerance_m=1.0,
            )

    monkeypatch.setattr(main_window_module, "DesignFromFrequencyDialog", FakeDialog)
    window._dirty = False

    window.design_from_frequency()

    assert window._project is not None
    design = window._project.designs[0]
    assert isinstance(design.parameters, T2FDParameters)
    assert design.parameters.length_m == pytest.approx(50.8)
    assert design.parameters.termination_resistance_ohm == pytest.approx(390.0)
    assert design.parameters.transformer_ratio == pytest.approx(4.0)
    window._dirty = False


def test_design_from_frequency_preserves_folded_dipole_transformer(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
    from antennadesk.domain.design import Confidence, DimensionEstimate

    current = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        spacing_m=0.2,
        transformer_ratio=6.0,
    )
    use_parameters(window, current)
    estimated = FoldedDipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=19.8,
        height_m=8.0,
        spacing_m=0.84,
    )

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def estimated_estimate(self) -> DimensionEstimate:
            return DimensionEstimate(
                parameters=estimated,
                method_id="test.folded",
                confidence=Confidence.EMPIRICAL,
                tolerance_m=0.5,
            )

    monkeypatch.setattr(main_window_module, "DesignFromFrequencyDialog", FakeDialog)
    window._dirty = False

    window.design_from_frequency()

    assert window._project is not None
    design = window._project.designs[0]
    assert isinstance(design.parameters, FoldedDipoleParameters)
    assert design.parameters.total_length_m == pytest.approx(19.8)
    assert design.parameters.transformer_ratio == pytest.approx(6.0)
    window._dirty = False


def test_design_from_frequency_preserves_loop_transformer(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters
    from antennadesk.domain.design import Confidence, DimensionEstimate

    current = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=40.0,
        height_m=8.0,
        sides=4,
        transformer_ratio=4.0,
    )
    use_parameters(window, current)
    estimated = LoopParameters(
        frequency_hz=7_100_000.0,
        circumference_m=44.2,
        height_m=8.0,
        sides=4,
    )

    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def estimated_estimate(self) -> DimensionEstimate:
            return DimensionEstimate(
                parameters=estimated,
                method_id="test.loop",
                confidence=Confidence.EMPIRICAL,
                tolerance_m=0.5,
            )

    monkeypatch.setattr(main_window_module, "DesignFromFrequencyDialog", FakeDialog)
    window._dirty = False

    window.design_from_frequency()

    assert window._project is not None
    design = window._project.designs[0]
    assert isinstance(design.parameters, LoopParameters)
    assert design.parameters.circumference_m == pytest.approx(44.2)
    assert design.parameters.transformer_ratio == pytest.approx(4.0)
    window._dirty = False


def test_apply_design_saves_without_simulating(window: MainWindow) -> None:
    window._form._length.setValue(22.0)

    window.apply_design()

    assert window._project is not None
    assert window._project.designs[0].parameters.total_length_m == pytest.approx(22.0)
    assert window._results._table.rowCount() == 0
    assert window._dirty is True
    window._dirty = False


def test_estimate_dimensions_does_not_require_a_solver(
    qtbot: QtBot,
    sample_project,
) -> None:
    window = MainWindow(
        JsonProjectRepository(),
        None,
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(window)
    window._set_project(
        sample_project,
        sample_project.designs[0].id,
        path=None,
        dirty=False,
    )

    assert window._estimate_button.isEnabled() is True
    assert window._optimize_button.isEnabled() is False
    assert window._simulate_action.isEnabled() is False

    window._dirty = False
    window.close()
