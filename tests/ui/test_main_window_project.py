# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Project lifecycle, shell, variants, units, and menus."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import wait_for_condition
from main_window_support import FakeSolver
from PySide6.QtWidgets import QDialog, QInputDialog, QMessageBox, QWizard
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem


def test_main_window_starts_without_a_project(qtbot: QtBot) -> None:
    window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(window)

    assert window._project is None
    assert window._design_id is None
    assert window._main_stack.currentWidget() is window._start_page
    assert window._new_action.isEnabled() is True
    assert window._open_action.isEnabled() is True
    assert window._save_action.isEnabled() is False
    assert window._simulate_action.isEnabled() is False
    assert window._estimate_button.isEnabled() is False
    assert window._variant_combo.count() == 0
    assert window._toolbar.isHidden() is True
    assert window.windowTitle() == "AntennaDesk — Antenna Designer"

    window.close()


def test_new_antenna_from_the_empty_state_creates_a_project(
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.dipole import DipoleParameters

    window = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(window)

    class FakeCatalog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_key(self) -> str:
            return "wire_dipole"

    class FakeWizard:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QWizard.DialogCode:
            return QWizard.DialogCode.Accepted

        def build_parameters(self) -> DipoleParameters:
            return DipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=8.0,
            )

        def project_name(self) -> str:
            return "First antenna"

    monkeypatch.setattr(main_window_module, "AntennaCatalogDialog", FakeCatalog)
    monkeypatch.setattr(main_window_module, "DipoleWizard", FakeWizard)

    window.new_antenna()

    assert window._project is not None
    assert window._project.name == "First antenna"
    assert window._main_stack.currentIndex() == 1
    assert window._form.parameters().total_length_m == pytest.approx(20.0)
    window._dirty = False
    window.close()


def test_basic_form_template_is_read_only(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[bool] = []
    monkeypatch.setattr(window, "change_template", lambda: calls.append(True))

    assert window._form._template_value.text() == "Wire dipole"
    assert window._form._change_template.text() == "Change..."
    assert not hasattr(window._form, "_type")

    window._form._change_template.click()

    assert calls == [True]


def test_new_template_asks_for_the_project_name_after_the_template(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.ringo import RingoParameters

    parameters = RingoParameters(
        frequency_hz=7_100_000.0,
        radiator_height_m=5.0,
        ring_diameter_m=1.0,
    )
    events: list[str] = []
    suggested: list[str] = []

    class FakeRingoDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            events.append("template")
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> RingoParameters:
            return parameters

    def fake_get_text(*args: object, **kwargs: object) -> tuple[str, bool]:
        events.append("name")
        suggested.append(str(kwargs["text"]))
        return "My Ringo", True

    monkeypatch.setattr(main_window_module, "RingoDialog", FakeRingoDialog)
    monkeypatch.setattr(QInputDialog, "getText", fake_get_text)

    window.new_ringo_antenna()

    assert events == ["template", "name"]
    assert suggested[0].endswith("Ringo")
    assert window._project is not None
    assert window._project.name == "My Ringo"
    window._dirty = False


def test_project_is_ready(window: MainWindow) -> None:
    assert window._project is not None
    assert window._project.name == "40 m dipole"
    assert window._main_stack.currentIndex() == 1
    parameters = window._form.parameters()
    assert parameters.frequency_hz == pytest.approx(7_100_000.0)
    assert parameters.total_length_m == pytest.approx(20.0)
    assert parameters.height_m == pytest.approx(8.0)
    assert window._geometry._model is not None
    assert window._results._table.rowCount() == 0


def test_save_project_writes_a_native_file(
    window: MainWindow,
    tmp_path: Path,
) -> None:
    path = tmp_path / "saved.antennadesk"

    assert window._save_to(path) is True

    assert path.is_file()
    assert window._dirty is False


def test_editing_form_marks_project_dirty(window: MainWindow) -> None:
    window._dirty = False
    window._form._length.setValue(window._form._length.value() + 1.0)

    assert window._dirty is True
    window._dirty = False


def test_language_switch_updates_actions(window: MainWindow) -> None:
    window._set_language(Language.SPANISH)
    assert window._simulate_action.text() == "Simular"
    assert window._estimate_button.text() == "Estimar dimensiones..."
    assert window._new_variant_action.text() == "Nuevo diseño en el proyecto..."
    assert window._variant_label.text() == "Diseño"

    window._set_language(Language.ENGLISH)
    assert window._simulate_action.text() == "Simulate"
    assert window._estimate_button.text() == "Estimate Dimensions..."
    assert window._new_variant_action.text() == "New Design in Project..."
    assert window._variant_label.text() == "Design"


def test_unit_switch_preserves_physical_length(window: MainWindow) -> None:
    window._set_unit_system(UnitSystem.IMPERIAL)
    assert window._form.parameters().total_length_m == pytest.approx(20.0, abs=0.01)

    window._set_unit_system(UnitSystem.METRIC)
    assert window._form.parameters().total_length_m == pytest.approx(20.0, abs=0.001)


def test_unit_switch_does_not_mark_project_dirty(window: MainWindow) -> None:
    window._dirty = False
    window._set_unit_system(UnitSystem.IMPERIAL)

    assert window._dirty is False


def test_new_variant_switches_to_the_copy(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Second", True))

    window.new_variant()

    assert window._project is not None
    assert len(window._project.designs) == 2
    assert window._variant_combo.count() == 2
    assert window._design_id == window._project.designs[-1].id
    window._dirty = False


def test_rename_variant_updates_the_selector(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Renamed", True))

    window.rename_variant()

    assert window._project is not None
    assert window._project.designs[0].name == "Renamed"
    assert window._variant_combo.itemText(0) == "Renamed"
    window._dirty = False


def test_delete_variant_keeps_one_design(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Second", True))
    window.new_variant()
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    window.delete_variant()

    assert window._project is not None
    assert len(window._project.designs) == 1
    assert window._variant_combo.count() == 1
    window._dirty = False


def test_variant_switch_restores_the_cached_result(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window.simulate()
    wait_for_condition(
        lambda: not window._simulating and window._thread is None,
        timeout_ms=15_000,
    )
    assert window._results._table.rowCount() == 1
    assert window._export_csv_action.isEnabled() is True

    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Second", True))
    window.new_variant()

    assert window._results._table.rowCount() == 0
    assert window._export_csv_action.isEnabled() is False

    window._variant_combo.setCurrentIndex(0)

    assert window._results._table.rowCount() == 1
    assert window._export_csv_action.isEnabled() is True
    window._dirty = False


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


def test_zoom_control_scales_the_geometry_view(window: MainWindow) -> None:
    assert window._geometry._zoom == pytest.approx(1.0)
    index = window._zoom_combo.findData(2.0)
    window._zoom_combo.setCurrentIndex(index)

    assert window._geometry._zoom == pytest.approx(2.0)

    index = window._zoom_combo.findData(1.0)
    window._zoom_combo.setCurrentIndex(index)
    assert window._geometry._zoom == pytest.approx(1.0)


def test_geometry_view_has_a_3d_option(window: MainWindow) -> None:
    assert window._view_combo.count() == 3
    assert window._view_combo.itemData(2) == "3d"


def test_main_menu_is_grouped_by_task(window: MainWindow) -> None:
    edit_menu_titles = [action.text() for action in window._edit_menu.actions()]
    import_menu_titles = [action.text() for action in window._import_menu.actions()]
    export_menu_titles = [action.text() for action in window._export_menu.actions()]
    design_titles = [action.text() for action in window._design_menu.actions()]
    simulation_titles = [action.text() for action in window._simulation_menu.actions()]

    assert edit_menu_titles[0].startswith("Undo")
    assert edit_menu_titles[1].startswith("Redo")
    assert "Preferences..." in edit_menu_titles
    assert "Import NEC Deck..." in import_menu_titles
    assert "Import MMANA File..." in import_menu_titles
    assert "Export CSV..." in export_menu_titles
    assert "Export Geometry SVG..." in export_menu_titles
    assert "Export Geometry PDF..." in export_menu_titles
    assert "Export Geometry DXF..." in export_menu_titles
    assert "Export PDF Report..." in export_menu_titles
    assert "Optimize..." in design_titles
    assert "Estimate Dimensions..." in design_titles
    assert "Change Template..." in design_titles
    assert "Optimize Dimension..." not in design_titles
    assert "Design from Frequency..." not in design_titles
    assert "Synthesize Dimensions..." not in design_titles
    assert "Optimize Yagi Elements..." not in design_titles
    assert "Optimize Fan Elements..." not in design_titles
    assert "Optimize Moxon Dimensions..." not in design_titles
    assert "Edit Series Loads..." in design_titles
    assert "Simulate" in simulation_titles
    assert "Analyze Bands..." in simulation_titles
    assert "Feed Line..." in simulation_titles
    assert "Matching Network..." in simulation_titles


def test_menu_order_follows_the_standard_desktop_layout(window: MainWindow) -> None:
    menu_titles = [action.text() for action in window.menuBar().actions() if action.text()]

    assert menu_titles == ["File", "Edit", "Design", "Simulation", "Tools", "Help"]
    edit_titles = [action.text() for action in window._edit_menu.actions()]
    tools_titles = [action.text() for action in window._tools_menu.actions()]
    assert "Preferences..." in edit_titles
    assert "Preferences..." not in tools_titles
    assert "Language" not in tools_titles
    assert "Units" not in tools_titles
    assert "Font Size" not in tools_titles
    assert window._preferences_action.shortcut().toString() == "Ctrl+,"
    assert window._change_template_action.shortcut().toString() == "Ctrl+Shift+T"
    assert window._design_from_frequency_action.shortcut().toString() == "Ctrl+Shift+E"


def test_save_warns_and_can_cancel_a_large_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "large.antennadesk"
    monkeypatch.setattr(
        window._repository,
        "serialized_size",
        lambda project: 21 * 1024 * 1024,
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )

    assert window._save_to(path) is False
    assert path.exists() is False
    window._dirty = False


def test_save_blocks_a_project_above_the_hard_limit(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "too-large.antennadesk"
    monkeypatch.setattr(
        window._repository,
        "serialized_size",
        lambda project: 33 * 1024 * 1024,
    )
    messages: list[str] = []
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args, **kwargs: messages.append(args[2]) or QMessageBox.StandardButton.Ok,
    )

    assert window._save_to(path) is False
    assert path.exists() is False
    assert messages
    assert "32 MB" in messages[0]
    window._dirty = False


def test_compacting_simulation_history_keeps_the_latest_run(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window.simulate()
    wait_for_condition(lambda: not window._simulating and window._thread is None, timeout_ms=15_000)
    window.simulate()
    wait_for_condition(lambda: not window._simulating and window._thread is None, timeout_ms=15_000)
    assert window._project is not None
    assert len(window._project.simulation_runs) == 2
    assert window._compact_history_action.isEnabled() is True

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    window.compact_simulation_history()

    assert len(window._project.simulation_runs) == 1
    assert window._dirty is True
    assert window._status_label.text() == "Simulation history compacted."
    window._dirty = False
