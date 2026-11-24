# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Site-ground dialog fields and optional profile."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.environment.site_ground import EdgeShape, SiteGroundProfile
from antennadesk.ui.dialogs.site_ground_dialog import SiteGroundDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import DisplayUnits, UnitSystem


def _dialog(qtbot: QtBot, profile: SiteGroundProfile | None = None) -> SiteGroundDialog:
    dialog = SiteGroundDialog(
        Translator(Language.ENGLISH),
        DisplayUnits(UnitSystem.METRIC),
        profile,
    )
    qtbot.addWidget(dialog)
    return dialog


def test_site_ground_dialog_is_disabled_without_a_profile(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert dialog.profile() is None
    assert dialog._enabled.isChecked() is False
    assert dialog._permittivity.isEnabled() is False


def test_site_ground_dialog_returns_the_edited_profile(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._enabled.setChecked(True)
    dialog._permittivity.setValue(81.0)
    dialog._conductivity.setValue(5.0)
    dialog._edge_shape.setCurrentIndex(dialog._edge_shape.findData(EdgeShape.CIRCULAR))
    dialog._edge_distance_field.set_value_m(25.0)
    dialog._edge_height_field.set_value_m(1.5)
    dialog._label.setText("  Coast  ")
    dialog._notes.setPlainText("  Water at the edge  ")
    dialog.accept()

    profile = dialog.profile()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert profile == SiteGroundProfile(
        second_medium_relative_permittivity=81.0,
        second_medium_conductivity_s_per_m=5.0,
        edge_distance_m=25.0,
        edge_shape=EdgeShape.CIRCULAR,
        edge_height_m=1.5,
        label="Coast",
        notes="Water at the edge",
    )
