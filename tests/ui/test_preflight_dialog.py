# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction pre-flight dialog behavior."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from antennadesk.domain.common.validation import Severity
from antennadesk.domain.design.preflight import (
    PreflightAction,
    PreflightCategory,
    PreflightFinding,
    PreflightReport,
)
from antennadesk.ui.dialogs.preflight_dialog import PreflightDialog
from antennadesk.ui.i18n import Language, Translator


def _finding(
    code: str,
    category: PreflightCategory,
    severity: Severity,
    message: str,
    *,
    subject: str = "subject",
    action: PreflightAction = PreflightAction.NONE,
    values: tuple[tuple[str, str], ...] = (),
) -> PreflightFinding:
    return PreflightFinding(
        code=code,
        category=category,
        severity=severity,
        message=message,
        subject=subject,
        action=action,
        values=values,
    )


def _report() -> PreflightReport:
    return PreflightReport(
        (
            _finding(
                "supports.height_exceeded",
                PreflightCategory.SUPPORTS,
                Severity.ERROR,
                "too tall",
                subject="Small yard",
                action=PreflightAction.EDIT_SUPPORTS,
                values=(("top", "8.000"), ("available", "5.000")),
            ),
            _finding(
                "geometry.wire_crossing",
                PreflightCategory.GEOMETRY,
                Severity.WARNING,
                "wires cross",
                subject="a / b",
                action=PreflightAction.EDIT_GEOMETRY,
                values=(("first", "a"), ("second", "b")),
            ),
            _finding(
                "geometry.free_space",
                PreflightCategory.GEOMETRY,
                Severity.INFO,
                "free space",
                action=PreflightAction.EDIT_GEOMETRY,
            ),
        )
    )


def test_dialog_groups_by_severity_and_never_reports_ready_with_errors(
    qtbot: QtBot,
) -> None:
    dialog = PreflightDialog(Translator(Language.ENGLISH), _report())
    qtbot.addWidget(dialog)

    assert dialog._tree.topLevelItemCount() == 3
    assert "Not ready to build" in dialog._status.text()
    assert "1 error" in dialog._status.text()
    assert "Errors: 1" in dialog._counts.text()
    errors = dialog._tree.topLevelItem(0)
    assert errors.text(0) == "Errors"
    assert errors.childCount() == 1
    assert "exceeds" in errors.child(0).text(0)
    assert errors.child(0).text(1) == "Site and supports"
    assert errors.child(0).text(2) == "Small yard"
    assert errors.child(0).text(3) == "Open the installation profile"


def test_dialog_shows_a_ready_state_without_findings(qtbot: QtBot) -> None:
    dialog = PreflightDialog(Translator(Language.ENGLISH), PreflightReport())
    qtbot.addWidget(dialog)

    assert "Ready to build" in dialog._status.text()
    assert "no pre-flight issues" in dialog._status.text().lower()
    assert dialog._tree.topLevelItemCount() == 1
    assert "No pre-flight issues" in dialog._tree.topLevelItem(0).text(0)
    assert dialog._go_to.isEnabled() is False


def test_dialog_go_to_returns_the_selected_action(qtbot: QtBot) -> None:
    dialog = PreflightDialog(Translator(Language.ENGLISH), _report())
    qtbot.addWidget(dialog)
    errors = dialog._tree.topLevelItem(0)
    dialog._tree.setCurrentItem(errors.child(0))

    assert dialog._go_to.isEnabled() is True
    dialog._go_to.click()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.selected_action is PreflightAction.EDIT_SUPPORTS


def test_dialog_double_click_also_opens_the_action(qtbot: QtBot) -> None:
    dialog = PreflightDialog(Translator(Language.ENGLISH), _report())
    qtbot.addWidget(dialog)
    warnings = dialog._tree.topLevelItem(1)

    dialog._activate_item(warnings.child(0), 0)

    assert dialog.selected_action is PreflightAction.EDIT_GEOMETRY


def test_dialog_retranslates_to_spanish(qtbot: QtBot) -> None:
    dialog = PreflightDialog(Translator(Language.SPANISH), _report())
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Pre-flight de construcción"
    assert "No listo para construir" in dialog._status.text()
    assert "Errores: 1" in dialog._counts.text()
    errors = dialog._tree.topLevelItem(0)
    assert errors.text(0) == "Errores"
    assert errors.child(0).text(1) == "Sitio y soportes"
    assert errors.child(0).text(3) == "Abrir el perfil de instalación"
    assert "supera la altura disponible" in errors.child(0).text(0)


def test_dialog_ready_with_warnings_uses_warning_status(qtbot: QtBot) -> None:
    report = PreflightReport(
        (
            _finding(
                "supports.no_profile",
                PreflightCategory.SUPPORTS,
                Severity.WARNING,
                "no profile",
                action=PreflightAction.EDIT_SUPPORTS,
            ),
        )
    )
    dialog = PreflightDialog(Translator(Language.ENGLISH), report)
    qtbot.addWidget(dialog)

    assert "Ready to build with" in dialog._status.text()
    assert "1 warning" in dialog._status.text()
    assert dialog._go_to.isEnabled() is False


def test_dialog_ready_with_info_mentions_the_notes(qtbot: QtBot) -> None:
    report = PreflightReport(
        (
            _finding(
                "geometry.free_space",
                PreflightCategory.GEOMETRY,
                Severity.INFO,
                "free space",
                action=PreflightAction.EDIT_GEOMETRY,
            ),
        )
    )
    dialog = PreflightDialog(Translator(Language.ENGLISH), report)
    qtbot.addWidget(dialog)

    assert "Ready to build" in dialog._status.text()
    assert "1 informational note" in dialog._status.text()
    assert "no pre-flight issues" not in dialog._status.text().lower()


def test_dialog_selection_without_an_action_disables_go_to(qtbot: QtBot) -> None:
    report = PreflightReport(
        (
            _finding(
                "solver.permeability_unsupported",
                PreflightCategory.SOLVER,
                Severity.WARNING,
                "permeability",
            ),
        )
    )
    dialog = PreflightDialog(Translator(Language.ENGLISH), report)
    qtbot.addWidget(dialog)
    warnings = dialog._tree.topLevelItem(0)
    dialog._tree.setCurrentItem(warnings.child(0))

    assert dialog._go_to.isEnabled() is False
