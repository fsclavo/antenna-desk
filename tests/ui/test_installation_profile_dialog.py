# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Installation profile dialog behavior."""

from __future__ import annotations

from uuid import uuid4

from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.environment.ground import GroundKind
from antennadesk.domain.projects.installation import (
    InstallationProfile,
    InstallationSupport,
)
from antennadesk.ui.dialogs.installation_profile_dialog import InstallationProfileDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog(qtbot: QtBot, *, unit_system: UnitSystem = UnitSystem.METRIC):
    dialog = InstallationProfileDialog(
        Translator(Language.ENGLISH),
        unit_system,
    )
    qtbot.addWidget(dialog)
    return dialog


def test_empty_dialog_starts_with_a_default_profile(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    assert len(dialog.profiles()) == 1
    assert dialog.profiles()[0].name == "Site 1"
    assert dialog.active_profile_id() == dialog.profiles()[0].id
    assert dialog._list.count() == 1


def test_add_duplicate_and_remove_profiles(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)

    dialog._name.setText("Home")
    dialog._add_profile()
    assert [profile.name for profile in dialog.profiles()] == ["Home", "Site 2"]

    dialog._duplicate_profile()
    assert [profile.name for profile in dialog.profiles()] == [
        "Home",
        "Site 2",
        "Site 2 copy",
    ]

    dialog._remove_profile()
    assert [profile.name for profile in dialog.profiles()] == ["Home", "Site 2"]
    assert dialog.active_profile_id() == dialog.profiles()[-1].id


def test_accept_commits_the_form_and_returns_the_active_profile(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._name.setText("Home")
    dialog._height.setValue(12.0)
    dialog._width.setValue(30.0)
    dialog._orientation.setValue(90.0)
    dialog._support.setCurrentIndex(dialog._support.findData(InstallationSupport.TREE.value))
    dialog._notes.setPlainText("Back yard")

    dialog.accept()

    assert dialog.result() == QDialog.DialogCode.Accepted
    profile = dialog.profiles()[0]
    assert profile.name == "Home"
    assert profile.available_height_m == 12.0
    assert profile.available_width_m == 30.0
    assert profile.orientation_deg == 90.0
    assert profile.support is InstallationSupport.TREE
    assert profile.notes == "Back yard"
    assert dialog.active_profile_id() == profile.id


def test_imperial_units_round_trip_through_the_form(qtbot: QtBot) -> None:
    profile = InstallationProfile(
        id=uuid4(),
        name="Home",
        available_height_m=9.144,
        available_width_m=12.192,
    )
    dialog = InstallationProfileDialog(
        Translator(Language.ENGLISH),
        UnitSystem.IMPERIAL,
        (profile,),
        profile.id,
    )
    qtbot.addWidget(dialog)

    assert dialog._height.value() == 30.0
    assert dialog._width.value() == 40.0

    dialog.accept()

    assert dialog.profiles()[0].available_height_m == 9.144
    assert dialog.profiles()[0].available_width_m == 12.192


def test_ground_preset_is_preserved(qtbot: QtBot) -> None:
    dialog = _dialog(qtbot)
    dialog._ground.setCurrentIndex(1)

    dialog.accept()

    ground = dialog.profiles()[0].ground
    assert ground is not None
    assert ground.kind is GroundKind.FREE_SPACE
