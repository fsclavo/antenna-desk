# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reference library integration in the main window."""

from __future__ import annotations

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.design.reference_library import REFERENCE_DESIGNS
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow

_DIPOLE = next(design for design in REFERENCE_DESIGNS if design.key == "arrl_dipole_40m")


def test_reference_library_action_is_available_and_retranslates(
    window: MainWindow,
) -> None:
    assert window._reference_library_action in window._file_menu.actions()
    assert window._reference_library_action.isEnabled()
    assert window._reference_library_action.text() == "Reference Design Library..."
    assert "source-backed" in window._reference_library_action.toolTip().lower()

    window._set_language(Language.SPANISH)

    assert window._reference_library_action.text() == ("Biblioteca de diseños de referencia...")
    assert "fuente" in window._reference_library_action.toolTip().lower()
    window._set_language(Language.ENGLISH)


def test_reference_library_opens_a_new_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeLibraryDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> int:
            return 1

        def selected_reference(self) -> object:
            return _DIPOLE

        def simulate_after_open(self) -> bool:
            return False

    monkeypatch.setattr(
        main_window_module,
        "ReferenceLibraryDialog",
        FakeLibraryDialog,
    )
    monkeypatch.setattr(window, "_ask_project_name", lambda default: "Reference dipole")

    window.show_reference_library()

    assert window._project is not None
    assert window._project.name == "Reference dipole"
    assert "Reference design" in window._project.description
    assert "half-wave length" in window._project.description
    assert window._project.designs[0].name == "Initial"
    expected = _DIPOLE.parameters
    assert isinstance(expected, DipoleParameters)
    parameters = window._project.designs[0].parameters
    assert isinstance(parameters, DipoleParameters)
    assert parameters.total_length_m == pytest.approx(expected.total_length_m)
    assert window._dirty is True
    assert window._last_status_key == "status.reference_opened"
    window._dirty = False


def test_reference_library_can_run_the_normal_simulation(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    class FakeLibraryDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> int:
            return 1

        def selected_reference(self) -> object:
            return _DIPOLE

        def simulate_after_open(self) -> bool:
            return True

    monkeypatch.setattr(
        main_window_module,
        "ReferenceLibraryDialog",
        FakeLibraryDialog,
    )
    monkeypatch.setattr(window, "_ask_project_name", lambda default: "Reference dipole")
    monkeypatch.setattr(window, "simulate", lambda: calls.append("simulate"))

    window.show_reference_library()

    assert calls == ["simulate"]
    window._dirty = False


def test_reference_library_cancel_changes_nothing(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    before = window._project

    class FakeLibraryDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> int:
            return 0

    monkeypatch.setattr(
        main_window_module,
        "ReferenceLibraryDialog",
        FakeLibraryDialog,
    )

    window.show_reference_library()

    assert window._project == before
    assert window._dirty is False
