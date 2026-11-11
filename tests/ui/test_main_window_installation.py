# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Installation profile integration in the main window."""

from __future__ import annotations

from uuid import uuid4

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.projects.installation import (
    InstallationProfile,
    InstallationSupport,
)
from antennadesk.ui.dialogs.installation_profile_dialog import InstallationProfileDialog
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


def test_installation_profile_action_follows_project_state(window: MainWindow) -> None:
    assert window._installation_profile_action.isEnabled()
    assert window._installation_edit.isEnabled()
    assert window._installation_label.text() == "No installation profile"


def test_edit_installation_profile_updates_the_project_and_summary(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = InstallationProfile(
        id=uuid4(),
        name="Home",
        available_height_m=10.0,
        available_width_m=20.0,
        support=InstallationSupport.TREE,
    )
    monkeypatch.setattr(
        InstallationProfileDialog,
        "exec",
        lambda self: QDialog.DialogCode.Accepted,
    )
    monkeypatch.setattr(InstallationProfileDialog, "profiles", lambda self: (profile,))
    monkeypatch.setattr(
        InstallationProfileDialog,
        "active_profile_id",
        lambda self: profile.id,
    )

    window.edit_installation_profile()

    assert window._project is not None
    assert window._project.active_installation_profile == profile
    assert window._dirty is True
    assert "Home" in window._installation_label.text()
    assert "10.000 m" in window._installation_label.text()
    assert window._last_status_key == "status.installation_profile"
    window._dirty = False


def test_installation_profile_undo_restores_the_previous_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = InstallationProfile(id=uuid4(), name="Portable")
    monkeypatch.setattr(
        InstallationProfileDialog,
        "exec",
        lambda self: QDialog.DialogCode.Accepted,
    )
    monkeypatch.setattr(InstallationProfileDialog, "profiles", lambda self: (profile,))
    monkeypatch.setattr(
        InstallationProfileDialog,
        "active_profile_id",
        lambda self: profile.id,
    )

    window.edit_installation_profile()
    assert window._undo_stack.canUndo() is True
    assert "Portable" in window._installation_label.text()

    window._undo_stack.undo()

    assert window._project is not None
    assert window._project.active_installation_profile is None
    assert window._installation_label.text() == "No installation profile"
    window._dirty = False


def test_installation_profile_retranslates(window: MainWindow) -> None:
    window._set_language(Language.SPANISH)

    assert window._installation_profile_action.text() == "Perfil de instalación..."
    assert window._installation_label.text() == "Sin perfil de instalación"

    window._set_language(Language.ENGLISH)

    assert window._installation_profile_action.text() == "Installation profile..."
    assert window._installation_label.text() == "No installation profile"
