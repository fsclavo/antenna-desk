# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided log-periodic editor tests."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QHeaderView, QLabel
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.log_periodic import (
    LogPeriodicParameters,
    cebik_10m_log_periodic_parameters,
)
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.ui.dialogs.log_periodic_dialog import LogPeriodicDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog() -> LogPeriodicDialog:
    return LogPeriodicDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)


def test_log_periodic_dialog_builds_the_reference_design(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)

    parameters = dialog.parameters()

    assert dialog.windowTitle() == "Log-Periodic Dipole Array"
    assert parameters.element_count == 4
    assert parameters.tau == pytest.approx(cebik_10m_log_periodic_parameters().tau, abs=1e-4)
    assert parameters.sigma == pytest.approx(cebik_10m_log_periodic_parameters().sigma, abs=1e-4)
    assert parameters.phase_line_impedance_ohm == pytest.approx(75.0)
    assert len(parameters.to_antenna().wires) == 4
    assert len(parameters.to_antenna().transmission_lines) == 3
    assert dialog._form._table.rowCount() == 4
    assert dialog._form._table.columnCount() == 4
    header = dialog._form._table.horizontalHeader()
    assert header.sectionResizeMode(0) is QHeaderView.ResizeMode.Stretch


def test_log_periodic_dialog_updates_the_element_table(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._element_count.setValue(6)

    parameters = dialog.parameters()

    assert parameters.element_count == 6
    assert dialog._form._table.rowCount() == 6
    assert len(parameters.element_lengths_m) == 6
    assert len(parameters.element_spacings_m) == 5


def test_log_periodic_dialog_scales_with_the_low_frequency(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    original = dialog.parameters()

    dialog._form._frequency_low.setValue(14.0)

    parameters = dialog.parameters()
    assert parameters.frequency_low_hz == pytest.approx(14_000_000.0)
    assert parameters.frequency_high_hz == pytest.approx(15_000_000.0)
    assert parameters.longest_element_length_m == pytest.approx(
        original.longest_element_length_m * 2.0
    )


def test_log_periodic_dialog_restores_the_reference_preset(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._tau.setValue(0.95)
    dialog._form._sigma.setValue(0.1)
    dialog._form._element_count.setValue(6)

    dialog._form._load_reference_preset()

    parameters = dialog.parameters()
    assert parameters.tau == pytest.approx(cebik_10m_log_periodic_parameters().tau, abs=1e-4)
    assert parameters.sigma == pytest.approx(cebik_10m_log_periodic_parameters().sigma, abs=1e-4)
    assert parameters.element_count == 4


def test_log_periodic_reference_preset_preserves_the_material(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    index = dialog._form._material.findData(COPPER)
    assert index >= 0
    dialog._form._material.setCurrentIndex(index)

    dialog._form._load_reference_preset()

    assert dialog.parameters().material.name == "copper"


def test_log_periodic_form_preserves_geometry_when_switching_units(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    original = dialog.parameters()

    dialog._form.set_unit_system(UnitSystem.IMPERIAL)

    parameters = dialog.parameters()
    assert parameters.longest_element_length_m == pytest.approx(
        original.longest_element_length_m, rel=1e-3
    )
    assert parameters.phase_line_impedance_ohm == pytest.approx(75.0)
    assert dialog._form._longest_element.suffix().strip() == "ft"


def test_log_periodic_form_applies_family_help(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form.retranslate()

    labels = {
        label.objectName(): label
        for label in dialog._form.findChildren(QLabel)
        if label.objectName().startswith("log_periodic.")
    }

    assert "tau" in labels["log_periodic.tau"].toolTip().lower()
    assert "sigma" in labels["log_periodic.sigma"].toolTip().lower()
    assert "phase line" in labels["log_periodic.phase_line_impedance"].toolTip().lower()
    assert "schedule" in dialog._form._table.toolTip().lower()
    assert "Cebik" in dialog._form._preset.toolTip()


def test_log_periodic_dialog_retranslates(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    dialog = LogPeriodicDialog(translator, UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    translator.set_language(Language.SPANISH)
    dialog._form.retranslate()

    assert "Nivel B" in dialog._form._evidence.text()
    assert dialog._form._preset.text().startswith("Cargar")


def test_log_periodic_dialog_accepts_a_valid_design(qtbot: QtBot) -> None:
    dialog = _dialog()
    qtbot.addWidget(dialog)
    dialog._form._element_count.setValue(5)

    dialog._accept()

    assert isinstance(dialog.result_parameters(), LogPeriodicParameters)
