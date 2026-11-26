# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX55 compact-family closure: fan dipole, Ringo, inverted V/L."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.fan_dipole_dialog import FanDipoleDialog
from antennadesk.ui.dialogs.inverted_l_dialog import InvertedLDialog
from antennadesk.ui.dialogs.inverted_v_dialog import InvertedVDialog
from antennadesk.ui.dialogs.ringo_dialog import RingoDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.preferences import FontSize, FontSizeController
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.form_dialog import FormDialogFrame


@dataclass(frozen=True, slots=True)
class CompactCase:
    name: str
    dialog_type: type[QDialog]
    size: tuple[int, int]
    primary: str


CASES = (
    CompactCase("fan_dipole", FanDipoleDialog, (620, 620), "_frequency"),
    CompactCase("ringo", RingoDialog, (560, 620), "_frequency"),
    CompactCase("inverted_v", InvertedVDialog, (560, 560), "_frequency"),
    CompactCase("inverted_l", InvertedLDialog, (560, 600), "_frequency"),
)


def _dialog(case: CompactCase) -> QDialog:
    return case.dialog_type(Translator(Language.ENGLISH), UnitSystem.METRIC)


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_ux55_compact_dialogs_use_the_scaffold_without_scroll(
    qtbot: QtBot,
    case: CompactCase,
) -> None:
    dialog = _dialog(case)
    qtbot.addWidget(dialog)

    assert isinstance(dialog, FormDialogFrame)
    assert dialog._scroll is None
    assert dialog._buttons.parent() is dialog
    assert dialog._form.isVisible() is False
    assert dialog.notes


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_ux55_compact_dialogs_fit_the_budget(
    qtbot: QtBot,
    case: CompactCase,
) -> None:
    dialog = _dialog(case)
    qtbot.addWidget(dialog)
    dialog.resize(*case.size)
    dialog.show()
    qtbot.wait(10)
    QApplication.processEvents()

    assert dialog.minimumSizeHint().height() <= 640
    control = getattr(dialog._form, case.primary)
    position = control.mapTo(dialog, QPoint(0, 0))
    assert position.y() >= 0
    buttons = dialog.findChild(QDialogButtonBox)
    assert buttons is not None
    assert buttons.isVisible() is True
    assert buttons.geometry().bottom() <= dialog.rect().bottom()


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_ux55_compact_dialogs_fit_large_spanish(
    qtbot: QtBot,
    case: CompactCase,
) -> None:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    controller = FontSizeController(QFont("Sans Serif", 10))
    controller.apply(FontSize.LARGE)
    try:
        dialog = case.dialog_type(Translator(Language.SPANISH), UnitSystem.METRIC)
        qtbot.addWidget(dialog)
        dialog.resize(*case.size)
        dialog.show()
        qtbot.wait(10)
        QApplication.processEvents()

        assert dialog.minimumSizeHint().height() <= 640
        assert dialog._scroll is None
        buttons = dialog.findChild(QDialogButtonBox)
        assert buttons is not None
        assert buttons.isVisible() is True
        assert buttons.geometry().bottom() <= dialog.rect().bottom()
    finally:
        controller.apply(FontSize.MEDIUM)


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_ux55_compact_dialogs_round_trip(
    qtbot: QtBot,
    case: CompactCase,
) -> None:
    dialog = _dialog(case)
    qtbot.addWidget(dialog)
    expected = dialog.parameters()

    dialog._accept()

    assert dialog.result_parameters() == expected
