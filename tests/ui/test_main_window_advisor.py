# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Antenna advisor integration in the main window."""

from __future__ import annotations

from dataclasses import replace
from typing import ClassVar
from uuid import uuid4

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.projects.installation import (
    InstallationProfile,
    InstallationSupport,
)
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


class _FakeAdvisorDialog:
    captured: ClassVar[dict[str, object]] = {}

    def __init__(self, *args: object, **kwargs: object) -> None:
        type(self).captured = {
            "translator": args[0],
            "unit_system": args[1],
            **kwargs,
        }

    def exec(self) -> QDialog.DialogCode:
        return QDialog.DialogCode.Accepted

    def selected_catalog_key(self) -> str:
        return "wire_dipole"


def test_advisor_action_opens_the_selected_family(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected: list[str] = []
    monkeypatch.setattr(
        main_window_module,
        "AntennaAdvisorDialog",
        _FakeAdvisorDialog,
    )
    monkeypatch.setattr(
        window,
        "_new_antenna_from_key",
        lambda key: selected.append(key),
    )

    window.show_antenna_advisor()

    assert selected == ["wire_dipole"]


def test_advisor_receives_the_active_installation_profile(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile = InstallationProfile(
        id=uuid4(),
        name="Portable site",
        available_height_m=12.0,
        available_width_m=30.0,
        support=InstallationSupport.PORTABLE,
    )
    assert window._project is not None
    window._project = replace(
        window._project,
        installation_profiles=(profile,),
        active_installation_profile_id=profile.id,
    )
    monkeypatch.setattr(
        main_window_module,
        "AntennaAdvisorDialog",
        _FakeAdvisorDialog,
    )
    monkeypatch.setattr(
        window,
        "_new_antenna_from_key",
        lambda _key: None,
    )

    window.show_antenna_advisor()

    captured = _FakeAdvisorDialog.captured
    assert captured["initial_height_m"] == 12.0
    assert captured["initial_width_m"] == 30.0
    assert captured["portable"] is True


def test_advisor_action_is_in_the_file_menu_and_retranslates(window: MainWindow) -> None:
    assert window._advisor_action in window._file_menu.actions()
    assert window._advisor_action.text() == "Help me choose..."

    window._set_language(Language.SPANISH)

    assert window._advisor_action.text() == "Ayúdame a elegir..."
    assert "catálogo" in window._advisor_action.toolTip()

    window._set_language(Language.ENGLISH)


def test_start_page_exposes_the_advisor_signal(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._start_page._advise_button.text() == "Help me choose..."
    received: list[bool] = []
    monkeypatch.setattr(
        window,
        "show_antenna_advisor",
        lambda: received.append(True),
    )

    window._start_page._advise_button.click()

    assert received == [True]
