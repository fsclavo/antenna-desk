# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Template creation, type switching, and generated geometries."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog, QInputDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow


def test_orientation_control_updates_parameters(window: MainWindow) -> None:
    from antennadesk.domain.antennas.dipole import DipoleOrientation

    window._form._orientation.setCurrentIndex(1)
    parameters = window._form.parameters()

    assert parameters.orientation is DipoleOrientation.VERTICAL
    assert window._form._azimuth.isEnabled() is False
    assert window._form._labels()["field.height"].text() == "Base height"

    window._form._orientation.setCurrentIndex(0)
    assert window._form.parameters().orientation is DipoleOrientation.HORIZONTAL
    assert window._form._azimuth.isEnabled() is True
    window._dirty = False


def test_switching_to_a_folded_dipole_updates_the_design_and_view(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters

    window._form.set_antenna_type("folded_dipole")
    assert window._form.parameters().spacing_m > 0.0
    window._form._length.setValue(20.0)
    window._form._spacing.setValue(0.2)
    window.apply_design()

    assert window._project is not None
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, FoldedDipoleParameters)
    assert parameters.spacing_m == pytest.approx(0.2, abs=1e-6)
    assert len(window._project.designs[0].antenna.wires) == 4
    assert window._view_combo.currentData() == "construction"
    assert window._geometry.resolved_mode().value == "plan"
    assert window._optimize_action.isEnabled() is True
    window._dirty = False


def test_switching_to_a_loop_updates_the_design(window: MainWindow) -> None:
    from antennadesk.domain.antennas.loop import LoopParameters

    window._form.set_antenna_type("loop")
    window._form._length.setValue(40.0)
    window._form._sides.setValue(8)
    window.apply_design()

    assert window._project is not None
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, LoopParameters)
    assert parameters.sides == 8
    assert len(window._project.designs[0].antenna.wires) == 8
    assert window._view_combo.currentData() == "construction"
    assert window._geometry.resolved_mode().value == "elevation"
    assert window._form._sides.isHidden() is False
    assert window._form._spacing.isHidden() is True
    window._dirty = False


def test_loop_orientation_switches_between_vertical_and_horizontal(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.loop import LoopOrientation, LoopParameters

    window._form.set_antenna_type("loop")
    assert window._form._orientation.isHidden() is False
    assert window._form.parameters().orientation is LoopOrientation.VERTICAL
    assert window._form._labels()["field.height"].text() == "Base height"

    window._form._orientation.setCurrentIndex(0)
    window._form._length.setValue(40.0)
    window._form._height.setValue(10.0)
    window.apply_design()

    assert window._project is not None
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, LoopParameters)
    assert parameters.orientation is LoopOrientation.HORIZONTAL
    assert window._form._labels()["field.height"].text() == "Height"
    assert all(
        wire.start.z_m == pytest.approx(10.0) for wire in window._project.designs[0].antenna.wires
    )
    assert window._view_combo.currentData() == "construction"
    assert window._geometry.resolved_mode().value == "plan"
    window._dirty = False


def test_new_antenna_uses_the_current_antenna_type(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeWizard:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Rejected

    class FakeCatalog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_key(self) -> str:
            return "loop"

    monkeypatch.setattr(main_window_module, "AntennaCatalogDialog", FakeCatalog)
    monkeypatch.setattr(main_window_module, "DipoleWizard", FakeWizard)
    window._dirty = False

    window.new_antenna()

    assert captured["initial_antenna_type"] == "loop"
    assert window._new_action.text() == "New Antenna..."


def test_new_dipole_alias_still_opens_the_wizard(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: list[bool] = []

    def fake_new_antenna() -> None:
        called.append(True)

    monkeypatch.setattr(window, "new_antenna", fake_new_antenna)
    window.new_dipole()

    assert called == [True]


def test_new_yagi_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.yagi import YagiParameters, nbs_five_element

    parameters = nbs_five_element(frequency_hz=14_100_000.0, height_m=12.0)

    class FakeYagiDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> YagiParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "YagiDialog", FakeYagiDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Yagi", True))

    window.new_yagi_antenna()

    assert window._project is not None
    assert window._project.name == "Yagi"
    assert window._project.designs[0].antenna_type == "yagi"
    assert window._design_stack.currentWidget() is window._yagi_scroll
    form_parameters = window._yagi_form.parameters()
    assert form_parameters.frequency_hz == pytest.approx(parameters.frequency_hz)
    assert len(form_parameters.elements) == len(parameters.elements)
    assert form_parameters.driven_index == parameters.driven_index
    window._dirty = False


def test_new_vertical_yagi_creates_vertical_wires(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.polarization import Polarization
    from antennadesk.domain.antennas.yagi import YagiParameters, nbs_five_element

    parameters = nbs_five_element(
        frequency_hz=50_100_000.0,
        height_m=8.0,
        polarization=Polarization.VERTICAL,
    )

    class FakeYagiDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> YagiParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "YagiDialog", FakeYagiDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Yagi", True))

    window.new_yagi_antenna()

    assert window._project is not None
    assert window._yagi_form.parameters().polarization is Polarization.VERTICAL
    model = window._project.designs[0].antenna
    assert all(wire.start.x_m == pytest.approx(wire.end.x_m) for wire in model.wires)
    assert all(wire.start.y_m == pytest.approx(wire.end.y_m) for wire in model.wires)
    window._dirty = False


def test_new_inverted_v_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.inverted_v import InvertedVParameters

    parameters = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.6,
        apex_height_m=12.0,
        included_angle_deg=120.0,
    )

    class FakeInvertedVDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> InvertedVParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "InvertedVDialog", FakeInvertedVDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Inv V", True))

    window.new_inverted_v_antenna()

    assert window._project is not None
    assert window._project.name == "Inv V"
    assert window._project.designs[0].antenna_type == "inverted_v"
    assert window._design_stack.currentWidget() is window._inverted_v_scroll
    assert window._view_combo.currentData() == "construction"
    assert window._geometry.resolved_mode().value == "elevation"
    assert window._inverted_v_form.parameters() == parameters
    window._dirty = False


def test_new_inverted_l_creates_a_first_class_design(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.inverted_l import InvertedLParameters

    parameters = InvertedLParameters(
        frequency_hz=7_100_000.0,
        vertical_height_m=10.0,
        horizontal_length_m=20.0,
        base_height_m=1.0,
    )

    class FakeInvertedLDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> InvertedLParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "InvertedLDialog", FakeInvertedLDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Inv L", True))

    window.new_inverted_l_antenna()

    assert window._project is not None
    assert window._project.name == "Inv L"
    assert window._project.designs[0].antenna_type == "inverted_l"
    assert window._design_stack.currentWidget() is window._inverted_l_scroll
    assert window._view_combo.currentData() == "construction"
    assert window._geometry.resolved_mode().value == "elevation"
    assert window._inverted_l_form.parameters() == parameters
    assert window._optimize_action.isEnabled() is True
    window._dirty = False


def test_new_magnetic_loop_creates_a_first_class_design(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters

    parameters = MagneticLoopParameters(
        frequency_hz=7_100_000.0,
        diameter_m=1.0,
        tuning_capacitance_f=180e-12,
        height_m=1.5,
        gap_length_m=0.04,
        capacitor_esr_ohm=0.2,
    )

    class FakeMagneticLoopDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> MagneticLoopParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "MagneticLoopDialog", FakeMagneticLoopDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Mag loop", True))

    window.new_magnetic_loop_antenna()

    assert window._project is not None
    assert window._project.name == "Mag loop"
    assert window._project.designs[0].antenna_type == "magnetic_loop"
    assert window._design_stack.currentWidget() is window._magnetic_loop_scroll
    assert window._view_combo.currentData() == "construction"
    assert window._geometry.resolved_mode().value == "elevation"
    assert window._magnetic_loop_form.parameters() == parameters
    assert window._estimate_button.isEnabled() is False
    assert window._optimize_action.isEnabled() is False

    errors: list[str] = []
    monkeypatch.setattr(window, "_show_error", errors.append)
    window.optimize_current_design()
    assert errors == [window._translator.t("optimize.unavailable.magnetic_loop")]

    from antennadesk.ui.units import UnitSystem

    window._set_unit_system(UnitSystem.IMPERIAL)
    assert window._magnetic_loop_form._diameter.suffix().strip() == "ft"
    assert window._magnetic_loop_form.parameters().diameter_m == pytest.approx(1.0, abs=0.01)
    window._set_unit_system(UnitSystem.METRIC)
    assert window._magnetic_loop_form._diameter.suffix().strip() == "m"
    window._dirty = False


def test_change_template_replaces_the_current_design(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.inverted_v import InvertedVParameters

    parameters = InvertedVParameters(
        frequency_hz=7_100_000.0,
        leg_length_m=10.6,
        apex_height_m=12.0,
        included_angle_deg=110.0,
    )

    catalog_kwargs: dict[str, object] = {}

    class FakeCatalog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            catalog_kwargs.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_key(self) -> str:
            return "inverted_v"

    class FakeInvertedVDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            assert "frequency_hz" in kwargs

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> InvertedVParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "AntennaCatalogDialog", FakeCatalog)
    monkeypatch.setattr(main_window_module, "InvertedVDialog", FakeInvertedVDialog)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    assert window._estimate_button.isHidden() is False
    assert window._estimate_button.text() == "Estimate Dimensions..."
    assert window._change_template_action.text() == "Change Template..."
    assert window._change_template_action.isEnabled() is True
    window.change_template()

    assert catalog_kwargs["initial_key"] == "wire_dipole"
    assert window._project is not None
    assert window._project.designs[0].antenna_type == "inverted_v"
    assert window._design_stack.currentWidget() is window._inverted_v_scroll
    assert window._inverted_v_form.parameters() == parameters
    window._undo_stack.undo()
    assert window._project.designs[0].antenna_type == "wire_dipole"
    window._undo_stack.redo()
    assert window._project.designs[0].antenna_type == "inverted_v"
    window._dirty = False


def test_new_vertical_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=10.0,
        base_height_m=0.25,
        radial_count=16,
        radial_length_m=5.0,
    )

    class FakeVerticalDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> VerticalParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "VerticalDialog", FakeVerticalDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Vertical", True))

    window.new_vertical_antenna()

    assert window._project is not None
    assert window._project.name == "Vertical"
    assert window._project.designs[0].antenna_type == "vertical"
    assert window._design_stack.currentWidget() is window._vertical_scroll
    assert window._vertical_form.parameters() == parameters
    window._dirty = False


def test_new_loaded_vertical_creates_a_design_with_the_loading_coil(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.vertical import VerticalParameters

    parameters = VerticalParameters(
        frequency_hz=7_100_000.0,
        height_m=2.0,
        base_height_m=0.25,
        radial_count=4,
        radial_length_m=1.0,
        loading_coil_enabled=True,
        loading_coil_offset_m=1.0,
        loading_coil_inductance_h=12e-6,
        loading_coil_resistance_ohm=0.5,
    )

    class FakeVerticalDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> VerticalParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "VerticalDialog", FakeVerticalDialog)
    monkeypatch.setattr(
        QInputDialog,
        "getText",
        lambda *args, **kwargs: ("Loaded vertical", True),
    )

    window.new_loaded_vertical_antenna()

    assert window._project is not None
    assert window._project.name == "Loaded vertical"
    design = window._project.designs[0]
    assert design.antenna_type == "vertical"
    assert len(design.antenna.loads) == 1
    assert design.antenna.loads[0].id == "loading-coil"
    assert design.antenna.loads[0].inductance_h == pytest.approx(12e-6)
    assert window._vertical_form.parameters() == parameters
    assert window._vertical_form._coil_enabled.isChecked() is True
    window._dirty = False


def test_new_moxon_creates_a_first_class_design(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.moxon import MoxonParameters

    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
    )

    class FakeMoxonDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> MoxonParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "MoxonDialog", FakeMoxonDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Moxon", True))

    window.new_moxon_antenna()

    assert window._project is not None
    assert window._project.name == "Moxon"
    assert window._project.designs[0].antenna_type == "moxon"
    assert window._design_stack.currentWidget() is window._moxon_scroll
    assert window._moxon_form.parameters() == parameters
    window._dirty = False


def test_new_vertical_moxon_creates_a_vertical_rectangle(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.moxon import MoxonParameters
    from antennadesk.domain.antennas.polarization import Polarization

    parameters = MoxonParameters(
        frequency_hz=14_100_000.0,
        width_m=10.6,
        depth_m=2.5,
        reflector_tip_m=1.0,
        driven_tip_m=1.0,
        height_m=10.0,
        polarization=Polarization.VERTICAL,
    )

    class FakeMoxonDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> MoxonParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "MoxonDialog", FakeMoxonDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Moxon", True))

    window.new_moxon_antenna()

    assert window._project is not None
    assert window._moxon_form.parameters() == parameters
    model = window._project.designs[0].antenna
    reflector = next(wire for wire in model.wires if wire.id == "reflector")
    assert reflector.start.x_m == pytest.approx(reflector.end.x_m)
    assert reflector.start.y_m == pytest.approx(reflector.end.y_m)
    window._dirty = False
