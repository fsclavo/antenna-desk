# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction pre-flight integration in the main window."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.design.preflight import (
    PreflightAction,
    PreflightReport,
)
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


class _FakePreflightDialog:
    captured_report: PreflightReport | None = None
    next_action: PreflightAction | None = None

    def __init__(
        self,
        translator: object,
        report: PreflightReport,
        parent: object = None,
    ) -> None:
        del translator, parent
        type(self).captured_report = report

    def exec(self) -> QDialog.DialogCode:
        return QDialog.DialogCode.Accepted

    @property
    def selected_action(self) -> PreflightAction | None:
        return type(self).next_action


def test_preflight_action_is_available_and_retranslates(window: MainWindow) -> None:
    assert window._preflight_action in window._design_menu.actions()
    assert window._preflight_action.isEnabled()
    assert window._preflight_action.text() == "Construction Pre-flight..."

    window._set_language(Language.SPANISH)

    assert window._preflight_action.text() == "Pre-flight de construcción..."
    window._set_language(Language.ENGLISH)


def test_show_preflight_builds_a_report_from_the_current_design(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _FakePreflightDialog.next_action = None
    monkeypatch.setattr(main_window_module, "PreflightDialog", _FakePreflightDialog)

    window.show_preflight()

    report = _FakePreflightDialog.captured_report
    assert report is not None
    codes = {finding.code for finding in report.findings}
    assert "supports.no_profile" in codes
    assert "construction.record_missing" in codes
    assert "simulation.missing" in codes


@pytest.mark.parametrize(
    ("action", "method_name"),
    [
        (PreflightAction.EDIT_LOADS, "edit_loads"),
        (PreflightAction.EDIT_LINES, "edit_transmission_lines"),
        (PreflightAction.EDIT_SUPPORTS, "edit_installation_profile"),
        (PreflightAction.EDIT_CONSTRUCTION, "edit_construction_record"),
        (PreflightAction.RUN_SIMULATION, "simulate"),
    ],
)
def test_preflight_dialog_action_opens_the_editor(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    action: PreflightAction,
    method_name: str,
) -> None:
    called: list[str] = []
    monkeypatch.setattr(
        window,
        method_name,
        lambda: called.append(method_name),
    )
    monkeypatch.setattr(
        _FakePreflightDialog,
        "next_action",
        action,
        raising=False,
    )
    monkeypatch.setattr(main_window_module, "PreflightDialog", _FakePreflightDialog)

    window.show_preflight()

    assert called == [method_name]


def test_preflight_geometry_action_opens_custom_wires_for_custom_designs(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    called: list[str] = []
    monkeypatch.setattr(window, "edit_custom_wires", lambda: called.append("custom"))
    monkeypatch.setattr(
        main_window_module,
        "CustomAntennaParameters",
        type(window._project.designs[0].parameters),
    )

    window._handle_preflight_action(PreflightAction.EDIT_GEOMETRY)

    assert called == ["custom"]


def test_preflight_geometry_action_focuses_the_design_editor(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    focused: list[str] = []
    monkeypatch.setattr(window._design_panel, "setFocus", lambda: focused.append("panel"))
    current = window._design_stack.currentWidget()
    assert current is not None
    monkeypatch.setattr(current, "setFocus", lambda: focused.append("editor"))

    window._handle_preflight_action(PreflightAction.EDIT_GEOMETRY)

    assert focused == ["panel", "editor"]


def test_construction_sheet_receives_the_current_preflight(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeConstructionDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured["args"] = args
            captured["kwargs"] = kwargs

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

    monkeypatch.setattr(main_window_module, "ConstructionDialog", FakeConstructionDialog)
    for name in (
        "construction_image",
        "auxiliary_image",
        "three_d_image",
        "construction_svg",
        "auxiliary_svg",
        "three_d_svg",
    ):
        monkeypatch.setattr(window._geometry, name, lambda: None)
    monkeypatch.setattr(window._geometry, "auxiliary_view_kind", lambda: None)

    window.show_construction_sheet()

    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    preflight = kwargs.get("preflight")
    assert isinstance(preflight, PreflightReport)
    assert any(finding.code == "supports.no_profile" for finding in preflight.findings)
