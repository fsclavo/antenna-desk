# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Wire presets, end-fed variants, and loop templates."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog, QInputDialog, QMessageBox, QWizard
from pytestqt.qtbot import QtBot

from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow


def test_new_trap_dipole_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
    )

    class FakeTrapDipoleDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> TrapDipoleParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "TrapDipoleDialog", FakeTrapDipoleDialog)
    monkeypatch.setattr(
        QInputDialog,
        "getText",
        lambda *args, **kwargs: ("Trap dipole", True),
    )
    errors: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args, **kwargs: errors.append(args) or QMessageBox.StandardButton.Ok,
    )

    window.new_trap_dipole_antenna()

    assert window._project is not None
    assert window._project.name == "Trap dipole"
    design = window._project.designs[0]
    assert design.antenna_type == "trap_dipole"
    assert [load.id for load in design.antenna.loads] == ["trap-left", "trap-right"]
    assert window._design_stack.currentWidget() is window._trap_dipole_scroll
    form_parameters = window._trap_dipole_form.parameters()
    assert form_parameters.trap_inductance_h == pytest.approx(parameters.trap_inductance_h)
    assert form_parameters.inner_length_m == pytest.approx(parameters.inner_length_m)

    window._trap_dipole_form._trap_inductance.setValue(15.0)
    window.apply_design()

    assert window._project.designs[0].parameters.trap_inductance_h == pytest.approx(15e-6)
    assert window._project.designs[0].antenna.loads[0].inductance_h == pytest.approx(15e-6)
    assert errors == []
    window._dirty = False


def test_trap_dipole_spec_sweeps_both_bands(window: MainWindow) -> None:
    from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters

    parameters = TrapDipoleParameters(
        frequency_hz=7_100_000.0,
        high_band_frequency_hz=14_100_000.0,
        inner_length_m=10.0,
        outer_length_m=5.0,
        trap_frequency_hz=14_100_000.0,
        trap_inductance_h=10e-6,
        height_m=12.0,
    )

    spec = window._trap_dipole_simulation_spec(parameters)

    assert spec.frequency_plan.count == 61
    assert spec.frequency_plan.start_hz == pytest.approx(7_100_000.0 * 0.95)
    assert spec.frequency_plan.stop_hz == pytest.approx(14_100_000.0 * 1.05)


def test_new_t2fd_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.t2fd import T2FDParameters

    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=26.0,
        spacing_m=0.9,
        height_m=12.0,
        termination_resistance_ohm=800.0,
        transformer_ratio=16.0,
    )

    class FakeT2FDDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> T2FDParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "T2FDDialog", FakeT2FDDialog)
    monkeypatch.setattr(
        QInputDialog,
        "getText",
        lambda *args, **kwargs: ("T2FD", True),
    )
    errors: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args, **kwargs: errors.append(args) or QMessageBox.StandardButton.Ok,
    )

    window.new_t2fd_antenna()

    assert window._project is not None
    assert window._project.name == "T2FD"
    design = window._project.designs[0]
    assert design.antenna_type == "t2fd"
    assert [load.id for load in design.antenna.loads] == ["t2fd-termination"]
    assert design.antenna.loads[0].resistance_ohm == pytest.approx(800.0)
    assert window._design_stack.currentWidget() is window._t2fd_scroll
    assert window._t2fd_form.parameters().spacing_m == pytest.approx(0.9)

    window._t2fd_form._termination.setValue(820.0)
    window.apply_design()

    updated = window._project.designs[0]
    assert updated.parameters.termination_resistance_ohm == pytest.approx(820.0)
    assert updated.antenna.loads[0].resistance_ohm == pytest.approx(820.0)
    assert errors == []
    window._dirty = False


def test_t2fd_spec_sweeps_the_design_band_with_centered_termination(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.t2fd import (
        T2FD_DRIVEN_WIRE_ID,
        T2FD_TERMINATED_WIRE_ID,
        T2FDParameters,
    )

    parameters = T2FDParameters(
        frequency_hz=3_500_000.0,
        highest_frequency_hz=30_000_000.0,
        length_m=26.0,
        spacing_m=0.9,
        height_m=12.0,
        termination_resistance_ohm=800.0,
        transformer_ratio=16.0,
    )

    spec = window._t2fd_simulation_spec(parameters)
    model = parameters.to_antenna()
    driven_count = spec.segmentation.segments_for(
        model.wire_by_id(T2FD_DRIVEN_WIRE_ID),
        spec.frequency_plan.stop_hz,
    )
    terminated_count = spec.segmentation.segments_for(
        model.wire_by_id(T2FD_TERMINATED_WIRE_ID),
        spec.frequency_plan.stop_hz,
    )

    assert spec.frequency_plan.count == 31
    assert spec.frequency_plan.start_hz == pytest.approx(3_500_000.0)
    assert spec.frequency_plan.stop_hz == pytest.approx(30_000_000.0)
    assert spec.feed_transformer_ratio == pytest.approx(16.0)
    assert driven_count == terminated_count
    assert driven_count % 2 == 1
    segment_length = parameters.length_m / driven_count
    assert parameters.termination_offset_m == pytest.approx(
        (driven_count // 2 + 0.5) * segment_length
    )


def test_new_sloper_uses_the_endfed_preset(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset

    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=2.0,
        preset=EndFedPreset.SLOPER,
    )
    captured: dict[str, object] = {}

    class FakeEndFedDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> EndFedParameters:
            return parameters

        def result_band_plan(self):
            from antennadesk.domain.design.band_plan import default_band_plan

            return default_band_plan(parameters).plan

    monkeypatch.setattr(main_window_module, "EndFedDialog", FakeEndFedDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Sloper", True))

    window.new_sloper_antenna()

    assert captured["preset"] is EndFedPreset.SLOPER
    assert window._project is not None
    assert window._project.designs[0].parameters.preset is EndFedPreset.SLOPER
    window._dirty = False


def test_new_g5rv_creates_the_custom_preset_with_a_line(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.g5rv import g5rv_parameters
    from antennadesk.domain.environment.ground import GroundModel

    parameters = g5rv_parameters(
        frequency_hz=14_100_000.0,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )

    class FakeG5RVDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self):
            return parameters

    monkeypatch.setattr(main_window_module, "G5RVDialog", FakeG5RVDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("G5RV", True))

    window.new_g5rv_antenna()

    assert window._project is not None
    assert window._project.name == "G5RV"
    design = window._project.designs[0]
    assert design.parameters.generator_id == "g5rv"
    assert len(design.antenna.transmission_lines) == 1
    assert window._design_stack.currentWidget() is window._custom_panel
    assert window._custom_sweep_start.value() == pytest.approx(3.5)
    assert window._custom_sweep_stop.value() == pytest.approx(30.0)
    assert window._custom_sweep_points.value() == 41
    assert window._custom_run_pattern_step_deg is None
    spec = window._custom_simulation_spec(design.parameters)
    dipole = design.antenna.wire_by_id("dipole")
    count = spec.segmentation.segments_for(dipole, spec.frequency_plan.stop_hz)
    assert count % 2 == 1
    assert spec.frequency_plan.count == 41
    fitted = window._fit_spec_to_budget(design.antenna, spec)
    assert len(fitted.pattern_frequencies_hz) == 9
    assert any(abs(frequency - 14_100_000.0) < 1.0 for frequency in fitted.pattern_frequencies_hz)
    assert fitted.far_field.theta_count == 91
    assert fitted.far_field.phi_count == 361
    assert "1°" in window._custom_pattern_status.text()
    assert "9 pattern frequencies" in window._custom_pattern_status.text()
    assert "Using 1°" in window._custom_pattern_status.text()
    assert "MB" in window._custom_pattern_status.text()

    window._custom_pattern_resolution.setCurrentIndex(
        window._custom_pattern_resolution.findData(5.0)
    )
    assert window._custom_run_pattern_step_deg == 5.0
    requested = window._custom_simulation_spec(design.parameters)
    exact = window._fit_spec_to_budget(design.antenna, requested)
    assert exact.far_field.theta_count == 19
    assert "Using 5°" in window._custom_pattern_status.text()
    assert "9 pattern frequencies" in window._custom_pattern_status.text()

    window._custom_pattern_frequency_mode.setCurrentIndex(
        window._custom_pattern_frequency_mode.findData(5)
    )
    assert window._custom_pattern_frequency_count == 5
    five = window._custom_simulation_spec(design.parameters)
    fitted_five = window._fit_spec_to_budget(design.antenna, five)
    assert len(fitted_five.pattern_frequencies_hz) == 5
    assert fitted_five.far_field.theta_count == 19
    assert "5 pattern frequencies" in window._custom_pattern_status.text()
    window._dirty = False


def test_new_zs6bkw_creates_the_custom_preset_with_a_line(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.zs6bkw import zs6bkw_parameters

    parameters = zs6bkw_parameters()

    class FakeZS6BKWDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self):
            return parameters

    monkeypatch.setattr(main_window_module, "ZS6BKWDialog", FakeZS6BKWDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("ZS6BKW", True))

    window.new_zs6bkw_antenna()

    assert window._project is not None
    assert window._project.name == "ZS6BKW"
    design = window._project.designs[0]
    assert design.parameters.generator_id == "zs6bkw"
    assert len(design.antenna.transmission_lines) == 1
    assert window._design_stack.currentWidget() is window._custom_panel
    assert window._custom_sweep_start.value() == pytest.approx(7.0)
    assert window._custom_sweep_stop.value() == pytest.approx(29.7)
    assert window._custom_sweep_points.value() == 61
    spec = window._custom_simulation_spec(design.parameters)
    dipole = design.antenna.wire_by_id("zs6bkw-dipole")
    count = spec.segmentation.segments_for(dipole, spec.frequency_plan.stop_hz)
    assert count % 2 == 1
    fitted = window._fit_spec_to_budget(design.antenna, spec)
    assert fitted.pattern_frequencies_hz
    window._dirty = False


def test_new_zepp_creates_the_refined_custom_preset(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.zepp import zepp_parameters

    parameters = zepp_parameters()

    class FakeZeppDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self):
            return parameters

    monkeypatch.setattr(main_window_module, "ZeppDialog", FakeZeppDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Zepp", True))

    window.new_zepp_antenna()

    assert window._project is not None
    assert window._project.name == "Zepp"
    design = window._project.designs[0]
    assert design.parameters.generator_id == "zepp"
    assert len(design.antenna.wires) == 4
    assert len(design.antenna.transmission_lines) == 0
    assert window._design_stack.currentWidget() is window._custom_panel
    assert window._custom_sweep_start.value() == pytest.approx(7.0)
    assert window._custom_sweep_stop.value() == pytest.approx(29.7)
    assert window._custom_sweep_points.value() == 61
    assert window._custom_simulation_spec(design.parameters).frequency_plan.count == 61
    window._dirty = False


def test_new_doublet_sets_the_project_feed_line(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.dipole import DipoleParameters
    from antennadesk.domain.antennas.feed_line import FeedLine

    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=10.0,
    )
    line = FeedLine(
        characteristic_impedance_ohm=450.0,
        length_m=12.0,
        velocity_factor=0.9,
        matched_loss_db_per_100m=0.2,
    )

    class FakeDoubletDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> DipoleParameters:
            return parameters

        def result_feed_line(self) -> FeedLine:
            return line

    monkeypatch.setattr(main_window_module, "DoubletDialog", FakeDoubletDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Doublet", True))

    window.new_doublet_antenna()

    assert window._project is not None
    assert window._project.name == "Doublet"
    assert window._project.feed_line == line
    assert window._feed_line == line
    assert window._project.designs[0].antenna_type == "wire_dipole"
    window._dirty = False


def test_change_template_to_doublet_updates_the_feed_line(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.dipole import DipoleParameters
    from antennadesk.domain.antennas.feed_line import FeedLine

    parameters = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=10.0,
    )
    line = FeedLine(
        characteristic_impedance_ohm=300.0,
        length_m=8.0,
        velocity_factor=0.85,
        matched_loss_db_per_100m=0.3,
    )

    class FakeCatalog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_key(self) -> str:
            return "doublet"

    class FakeDoubletDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def parameters(self) -> DipoleParameters:
            return parameters

        def feed_line(self) -> FeedLine:
            return line

    monkeypatch.setattr(main_window_module, "AntennaCatalogDialog", FakeCatalog)
    monkeypatch.setattr(main_window_module, "DoubletDialog", FakeDoubletDialog)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    window.change_template()

    assert window._project is not None
    assert window._project.feed_line == line
    assert window._feed_line == line
    assert window._project.designs[0].parameters == parameters
    window._dirty = False


def test_new_ocfd_creates_a_first_class_design(
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

    assert window._project is not None
    assert window._project.name == "OCFD"
    assert window._project.designs[0].antenna_type == "ocfd"
    assert window._project.designs[0].band_plan is not None
    assert window._project.designs[0].band_plan.band_ids == ("40m", "20m", "10m")
    assert window._band_plans[window._project.designs[0].id].band_ids == (
        "40m",
        "20m",
        "10m",
    )
    assert window._design_stack.currentWidget() is window._ocfd_scroll
    assert window._ocfd_form.parameters() == parameters
    window._ocfd_form._length.setValue(22.0)
    window.apply_design()
    assert window._project.designs[0].parameters.total_length_m == pytest.approx(22.0)
    window._dirty = False


def test_new_fan_dipole_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement

    parameters = FanDipoleParameters(
        frequency_hz=7_100_000.0,
        elements=(
            FanElement(length_m=20.0, included_angle_deg=120.0),
            FanElement(length_m=10.0, included_angle_deg=90.0),
        ),
        apex_height_m=12.0,
    )

    class FakeFanDipoleDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> FanDipoleParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "FanDipoleDialog", FakeFanDipoleDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Fan", True))

    window.new_fan_dipole_antenna()

    assert window._project is not None
    assert window._project.name == "Fan"
    assert window._project.designs[0].antenna_type == "fan_dipole"
    assert window._design_stack.currentWidget() is window._fan_dipole_scroll
    assert window._fan_dipole_form.parameters() == parameters
    window._dirty = False


def test_new_endfed_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.endfed import EndFedParameters

    parameters = EndFedParameters(
        frequency_hz=7_100_000.0,
        length_m=20.0,
        feed_height_m=10.0,
        end_height_m=5.0,
        counterpoise_azimuth_deg=180.0,
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

    assert window._project is not None
    assert window._project.name == "End-fed"
    assert window._project.designs[0].antenna_type == "endfed"
    assert window._project.designs[0].band_plan is not None
    assert window._project.designs[0].band_plan.band_ids == ("40m", "20m", "10m")
    assert window._band_plans[window._project.designs[0].id].band_ids == (
        "40m",
        "20m",
        "10m",
    )
    assert window._design_stack.currentWidget() is window._endfed_scroll
    assert window._endfed_form.parameters() == parameters
    window._dirty = False


def test_new_j_pole_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.j_pole import JPoleParameters

    parameters = JPoleParameters(
        frequency_hz=145_000_000.0,
        radiator_height_m=1.0,
        stub_length_m=0.5,
        spacing_m=0.05,
        feed_offset_m=0.1,
    )

    class FakeJPoleDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> JPoleParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "JPoleDialog", FakeJPoleDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("J Pole", True))

    window.new_j_pole_antenna(folded=False)

    assert window._project is not None
    assert window._project.name == "J Pole"
    assert window._project.designs[0].antenna_type == "j_pole"
    assert window._design_stack.currentWidget() is window._j_pole_scroll
    assert window._j_pole_form.parameters() == parameters
    window._dirty = False


def test_typed_transmission_line_preset_uses_the_inline_editor(
    window: MainWindow,
) -> None:
    from main_window_support import use_parameters

    from antennadesk.domain.antennas.transmission_line_doublet import (
        DoubletPreset,
        doublet_starting_parameters,
    )

    doublet = doublet_starting_parameters(DoubletPreset.G5RV)
    use_parameters(window, doublet)
    assert window._project is not None
    assert window._project.designs[0].antenna_type == "g5rv"
    assert window._design_stack.currentWidget() is window._doublet_scroll
    assert window._doublet_form.parameters() == doublet
    assert window._optimize_action.isEnabled() is True
    window._dirty = False


def test_typed_zepp_preset_uses_the_inline_editor(
    window: MainWindow,
) -> None:
    from main_window_support import use_parameters

    from antennadesk.domain.antennas.zepp import zepp_starting_parameters

    zepp = zepp_starting_parameters()
    use_parameters(window, zepp)
    assert window._project is not None
    assert window._project.designs[0].antenna_type == "zepp"
    assert window._design_stack.currentWidget() is window._zepp_scroll
    restored = window._zepp_form.parameters()
    assert restored.frequency_hz == pytest.approx(zepp.frequency_hz)
    assert restored.radiator_length_m == pytest.approx(zepp.radiator_length_m, abs=1e-3)
    assert restored.matching_section_length_m == pytest.approx(
        zepp.matching_section_length_m, abs=1e-3
    )
    assert restored.spacing_m == pytest.approx(zepp.spacing_m, abs=1e-3)
    assert window._optimize_action.isEnabled() is True
    window._dirty = False


def test_biquad_presets_use_the_inline_editor(window: MainWindow) -> None:
    from main_window_support import use_parameters

    from antennadesk.domain.antennas.biquad import BiquadKind, biquad_parameters

    parameters = biquad_parameters(BiquadKind.SINGLE)
    use_parameters(window, parameters)
    assert window._project is not None
    assert window._project.designs[0].antenna_type == "biquad"
    assert window._design_stack.currentWidget() is window._biquad_scroll
    restored = window._biquad_form.parameters()
    assert restored.kind is BiquadKind.SINGLE
    assert restored.loop_side_m == pytest.approx(parameters.loop_side_m, abs=1e-3)
    assert restored.reflector_spacing_m == pytest.approx(parameters.reflector_spacing_m, abs=1e-3)
    assert window._optimize_action.isEnabled() is True

    double = biquad_parameters(BiquadKind.DOUBLE)
    use_parameters(window, double)
    assert window._project.designs[0].antenna_type == "double_biquad"
    assert window._biquad_form.parameters().kind is BiquadKind.DOUBLE
    window._dirty = False


def test_beverage_preset_uses_the_inline_editor(window: MainWindow) -> None:
    from main_window_support import use_parameters

    from antennadesk.domain.antennas.beverage import beverage_parameters

    parameters = beverage_parameters(frequency_hz=7_100_000.0, length_m=42.0)
    use_parameters(window, parameters)
    assert window._project is not None
    assert window._project.designs[0].antenna_type == "beverage"
    assert window._design_stack.currentWidget() is window._beverage_scroll
    restored = window._beverage_form.parameters()
    assert restored.length_m == pytest.approx(42.0, abs=1e-3)
    assert restored.termination_enabled is True
    assert window._optimize_action.isEnabled() is True
    window._dirty = False


def test_loaded_dipole_preset_uses_the_inline_editor(window: MainWindow) -> None:
    from main_window_support import use_parameters

    from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters

    parameters = loaded_dipole_parameters(total_length_m=18.0, link_offset_m=2.5)
    use_parameters(window, parameters)
    assert window._project is not None
    assert window._project.designs[0].antenna_type == "loaded_dipole"
    assert window._design_stack.currentWidget() is window._loaded_dipole_scroll
    restored = window._loaded_dipole_form.parameters()
    assert restored.total_length_m == pytest.approx(18.0, abs=1e-3)
    assert restored.loading_coil_inductance_h == pytest.approx(10e-6)
    assert window._optimize_action.isEnabled() is True
    window._dirty = False


def test_new_ringo_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.ringo import RingoParameters

    parameters = RingoParameters(
        frequency_hz=50_100_000.0,
        radiator_height_m=3.0,
        ring_diameter_m=0.33,
        ring_height_m=0.1,
        ring_sides=8,
    )

    class FakeRingoDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> RingoParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "RingoDialog", FakeRingoDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Ringo", True))

    window.new_ringo_antenna()

    assert window._project is not None
    assert window._project.name == "Ringo"
    assert window._project.designs[0].antenna_type == "ringo"
    assert window._design_stack.currentWidget() is window._ringo_scroll
    assert window._ringo_form.parameters() == parameters
    window._dirty = False


def test_new_scv_templates_use_the_shared_array_editor(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.scv import ScvKind, ScvParameters

    parameters = ScvParameters(
        frequency_hz=7_150_000.0,
        kind=ScvKind.BOBTAIL_CURTAIN,
        horizontal_length_m=38.1,
        vertical_height_m=11.5,
        base_height_m=1.5,
        feed_offset_m=0.5,
        azimuth_deg=30.0,
    )

    class FakeScvDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> object:
            return parameters

    monkeypatch.setattr(main_window_module, "ScvDialog", FakeScvDialog)
    monkeypatch.setattr(
        QInputDialog,
        "getText",
        lambda *args, **kwargs: ("Bobtail curtain", True),
    )

    window.new_bobtail_curtain_antenna()

    assert window._project is not None
    assert window._project.name == "Bobtail curtain"
    assert window._project.designs[0].antenna_type == "bobtail_curtain"
    assert window._design_stack.currentWidget() is window._scv_scroll
    assert window._scv_form.parameters() == parameters
    window._dirty = False


def test_switching_between_delta_and_quad_changes_the_rendered_polygon(
    window: MainWindow,
) -> None:
    window._form.set_antenna_type("loop")
    window._form._length.setValue(40.0)
    window._form._sides.setValue(3)
    window.apply_design()
    window._geometry._scene = None
    delta = window._geometry._ensure_scene()

    window._form._sides.setValue(4)
    window.apply_design()
    window._geometry._scene = None
    quad = window._geometry._ensure_scene()

    assert delta is not None
    assert quad is not None
    assert len(delta.polylines) == 3
    assert len(quad.polylines) == 4
    assert "Delta loop" in delta.summary
    assert "Quad loop" in quad.summary
    assert window._geometry._zoom == pytest.approx(1.0)
    window._dirty = False


def test_change_template_to_delta_and_quad_loop_creates_real_loops(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    class FakeCatalog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_key(self) -> str:
            return "delta_loop"

    class FakeWizard:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self._initial_sides = kwargs.get("initial_sides")

        def exec(self) -> QWizard.DialogCode:
            return QWizard.DialogCode.Accepted

        def build_parameters(self) -> LoopParameters:
            return LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=int(self._initial_sides or 3),
            )

    monkeypatch.setattr(main_window_module, "AntennaCatalogDialog", FakeCatalog)
    monkeypatch.setattr(main_window_module, "DipoleWizard", FakeWizard)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    window.change_template()

    assert window._project is not None
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, LoopParameters)
    assert parameters.sides == 3
    window._geometry._scene = None
    scene = window._geometry._ensure_scene()
    assert scene is not None
    assert len(scene.polylines) == 3
    assert "Delta loop" in scene.summary
    window._dirty = False


def test_new_delta_and_quad_loop_pass_the_expected_side_count(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeWizard:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QWizard.DialogCode:
            return QWizard.DialogCode.Rejected

    class FakeCatalog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_key(self) -> str:
            return "quad_loop"

    monkeypatch.setattr(main_window_module, "AntennaCatalogDialog", FakeCatalog)
    monkeypatch.setattr(main_window_module, "DipoleWizard", FakeWizard)
    window._dirty = False

    window.new_antenna()

    assert captured["initial_antenna_type"] == "loop"
    assert captured["initial_sides"] == 4
