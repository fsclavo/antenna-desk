# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Custom designs, NEC/MMANA import, loads, lines, and measurements."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import wait_for_condition
from PySide6.QtWidgets import QDialog, QFileDialog, QInputDialog, QMessageBox
from pytestqt.qtbot import QtBot

from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow


def test_new_custom_antenna_is_editable_and_simulatable(
    window: MainWindow,
    qtbot: QtBot,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.custom import CustomAntennaParameters
    from antennadesk.domain.antennas.feed import FeedPoint
    from antennadesk.domain.antennas.geometry import Point3D
    from antennadesk.domain.antennas.materials import COPPER
    from antennadesk.domain.antennas.wire import Wire

    parameters = CustomAntennaParameters(
        frequency_hz=7_100_000.0,
        wires=(
            Wire(
                id="wire-1",
                start=Point3D(-5.0, 0.0, 8.0),
                end=Point3D(5.0, 0.0, 8.0),
                radius_m=0.001,
                material=COPPER,
            ),
        ),
        feed=FeedPoint("wire-1", 5.0),
    )

    class FakeCustomDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> CustomAntennaParameters:
            return parameters

    monkeypatch.setattr(main_window_module, "CustomAntennaDialog", FakeCustomDialog)
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Custom", True))

    window.new_custom_antenna()

    assert window._project is not None
    assert window._project.name == "Custom"
    assert window._project.designs[0].antenna_type == "custom"
    assert window._design_stack.currentWidget() is window._custom_panel
    assert window._custom_simulation_spec(parameters).frequency_plan.count == 100

    window.simulate()
    wait_for_condition(lambda: not window._simulating and window._thread is None, timeout_ms=15_000)

    assert window._results._table.rowCount() == 1
    assert window._status_label.text() == "Simulation completed"
    window._dirty = False


def test_import_nec_deck_creates_a_custom_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "imported.nec"
    path.write_text(
        "GW 1 5 -5 0 8 5 0 8 0.001\nGN 0 0 0 0 13 0.005\nFR 0 1 0 0 7.1 0\nEX 0 1 3 0 1\nEN\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(path), ""),
    )

    window.import_nec_deck()

    assert window._project is not None
    assert window._project.name == "imported"
    assert window._project.designs[0].antenna_type == "custom"
    assert len(window._project.designs[0].antenna.wires) == 1
    assert window._design_stack.currentWidget() is window._custom_panel
    window._dirty = False


def test_import_mmana_file_creates_a_custom_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "imported.maa"
    path.write_text(
        "Test\n*\n7.1\n***Wires***\n1\n-5,0,8,5,0,8,0.001,-1\n*** Source ***\n1,1\nw1c,0,1\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(path), ""),
    )
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: None)

    window.import_mmana_file()

    assert window._project is not None
    assert window._project.name == "imported"
    assert window._project.designs[0].antenna_type == "custom"
    assert len(window._project.designs[0].antenna.wires) == 1
    window._dirty = False


def test_convert_to_custom_wires_preserves_geometry(window: MainWindow) -> None:
    original = window._project.designs[0].antenna if window._project is not None else None
    assert original is not None

    window.convert_to_custom_wires()

    assert window._project is not None
    design = window._project.designs[0]
    assert design.antenna_type == "custom"
    assert design.antenna.wires == original.wires
    assert design.antenna.feed == original.feed
    assert window._design_stack.currentWidget() is window._custom_panel
    assert window._optimize_action.isEnabled() is False
    window._dirty = False


def test_edit_loads_applies_series_loads(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.load import SeriesLoad

    load = SeriesLoad("load-1", "radiator", 10.0, resistance_ohm=50.0)

    class FakeLoadsDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def loads(self) -> tuple[SeriesLoad, ...]:
            return (load,)

    monkeypatch.setattr(main_window_module, "LoadsDialog", FakeLoadsDialog)
    window.edit_loads()

    assert window._project is not None
    assert window._project.designs[0].antenna.loads == (load,)
    assert window._dirty is True
    window._dirty = False


def test_edit_transmission_lines_applies_the_geometry(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.transmission_line import TransmissionLine

    line = TransmissionLine(
        id="line-1",
        start_wire_id="radiator",
        start_offset_m=0.0,
        end_wire_id="radiator",
        end_offset_m=10.0,
        characteristic_impedance_ohm=300.0,
        length_m=8.0,
        velocity_factor=0.9,
    )

    class FakeTransmissionLinesDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def transmission_lines(self) -> tuple[TransmissionLine, ...]:
            return (line,)

    monkeypatch.setattr(
        main_window_module,
        "TransmissionLinesDialog",
        FakeTransmissionLinesDialog,
    )
    window.edit_transmission_lines()

    assert window._project is not None
    assert window._transmission_lines == (line,)
    assert window._project.designs[0].antenna.transmission_lines == (line,)
    window._dirty = False


def test_import_vna_csv_adds_a_measurement(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    csv_path = tmp_path / "field.csv"
    csv_path.write_text(
        "frequency_hz,r_ohm,x_ohm\n7000000,50,0\n7100000,75,0\n",
        encoding="utf-8",
    )

    class FakeDetailsDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def name(self) -> str:
            return "Field measurement"

        def calibration(self) -> str:
            return "SOL"

        def reference_plane(self) -> str:
            return "antenna terminals"

        def feed_line(self) -> str:
            return "10 m RG-58"

        def notes(self) -> str:
            return "Dry ground"

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(csv_path), ""),
    )
    monkeypatch.setattr(
        main_window_module,
        "MeasurementDetailsDialog",
        FakeDetailsDialog,
    )

    window.import_vna_csv()

    assert window._project is not None
    assert len(window._project.measurements) == 1
    assert window._project.measurements[0].name == "Field measurement"
    assert window._project.measurements[0].calibration == "SOL"
    assert window._project.measurements[0].reference_plane == "antenna terminals"
    assert window._tabs_select_measurements() is None
    assert window._results._tabs.currentWidget() is window._results._measurements_tab
    assert window._dirty is True
    window._undo_stack.undo()
    assert len(window._project.measurements) == 0
    window._undo_stack.redo()
    assert len(window._project.measurements) == 1
    window._dirty = False


def test_edit_and_delete_measurement(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from datetime import UTC, datetime
    from uuid import UUID

    from antennadesk.domain.measurement import Measurement, MeasurementPoint

    measurement = Measurement(
        id=UUID("00000000-0000-0000-0000-000000000005"),
        name="Field sweep",
        created_at=datetime(2026, 11, 1, tzinfo=UTC),
        reference_impedance_ohm=50.0,
        points=(MeasurementPoint(7_100_000.0, complex(50.0, 0.0)),),
    )
    assert window._project is not None
    window._project = window._project.with_measurement(
        measurement,
        updated_at=window._project.updated_at,
    )
    window._results.set_measurements(window._project.measurements)

    class FakeDetailsDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def name(self) -> str:
            return "Edited sweep"

        def calibration(self) -> str:
            return "SOL"

        def reference_plane(self) -> str:
            return "terminals"

        def feed_line(self) -> str:
            return ""

        def notes(self) -> str:
            return "after tuning"

    monkeypatch.setattr(main_window_module, "MeasurementDetailsDialog", FakeDetailsDialog)
    window.edit_measurement(measurement)

    assert window._project.measurements[0].name == "Edited sweep"
    assert window._project.measurements[0].calibration == "SOL"
    assert window._project.measurements[0].notes == "after tuning"

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )
    window.delete_measurement(window._project.measurements[0])

    assert window._project.measurements == ()
    window._dirty = False
