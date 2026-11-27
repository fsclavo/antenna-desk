# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX54 audit contract for the scroll-heavy generator dialogs."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox
from pytestqt.qtbot import QtBot
from qt_font_support import resolved_test_font

from antennadesk.ui.dialogs.basic_antenna_dialog import BasicAntennaDialog
from antennadesk.ui.dialogs.discone_dialog import DisconeDialog
from antennadesk.ui.dialogs.endfed_dialog import EndFedDialog
from antennadesk.ui.dialogs.hexbeam_dialog import HexbeamDialog
from antennadesk.ui.dialogs.log_periodic_dialog import LogPeriodicDialog
from antennadesk.ui.dialogs.phased_vertical_dialog import PhasedVerticalDialog
from antennadesk.ui.dialogs.quad_beam_dialog import QuadBeamDialog
from antennadesk.ui.dialogs.stacked_yagi_dialog import StackedYagiDialog
from antennadesk.ui.dialogs.t2fd_dialog import T2FDDialog
from antennadesk.ui.dialogs.trap_dipole_dialog import TrapDipoleDialog
from antennadesk.ui.dialogs.trap_yagi_dialog import TrapYagiDialog
from antennadesk.ui.dialogs.vertical_dialog import VerticalDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.preferences import FontSize, FontSizeController
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.form_dialog import FormDialogFrame

WIDTH_1080 = 972
WIDTH_768 = 691


@dataclass(frozen=True, slots=True)
class AuditCase:
    name: str
    dialog_type: type[QDialog]
    size: tuple[int, int]
    primary: str


CASES = (
    AuditCase("stacked_yagi", StackedYagiDialog, (940, 900), "_level_count"),
    AuditCase("endfed", EndFedDialog, (620, 780), "_length"),
    AuditCase("vertical", VerticalDialog, (560, 700), "_height"),
    AuditCase("log_periodic", LogPeriodicDialog, (640, 900), "_frequency_low"),
    AuditCase("hexbeam", HexbeamDialog, (580, 820), "_driver_half"),
    AuditCase("trap_yagi", TrapYagiDialog, (580, 860), "_frequency"),
    AuditCase("phased_vertical", PhasedVerticalDialog, (560, 820), "_element_count"),
    AuditCase("quad_beam", QuadBeamDialog, (560, 780), "_loop_side"),
    AuditCase("trap_dipole", TrapDipoleDialog, (600, 760), "_inner_length"),
    AuditCase("t2fd", T2FDDialog, (620, 780), "_length"),
    AuditCase("discone", DisconeDialog, (560, 780), "_cone_height"),
    AuditCase("basic_antenna", BasicAntennaDialog, (560, 740), "_frequency"),
)


def _dialog(case: AuditCase) -> QDialog:
    return case.dialog_type(Translator(Language.ENGLISH), UnitSystem.METRIC)


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_ux54_dialogs_use_the_shared_scaffold(
    qtbot: QtBot,
    case: AuditCase,
) -> None:
    dialog = _dialog(case)
    qtbot.addWidget(dialog)

    assert isinstance(dialog, FormDialogFrame)
    assert dialog._scroll is not None
    assert dialog._scroll.widget() is dialog._form
    assert dialog._buttons.parent() is dialog
    assert all(not dialog._scroll.isAncestorOf(note) for note in dialog.notes)


@pytest.mark.parametrize("target_height", [WIDTH_1080, WIDTH_768])
@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_ux54_primary_controls_are_visible(
    qtbot: QtBot,
    case: AuditCase,
    target_height: int,
) -> None:
    dialog = _dialog(case)
    qtbot.addWidget(dialog)
    height = min(case.size[1], target_height)
    dialog.resize(case.size[0], height)
    dialog.show()
    qtbot.wait(10)
    QApplication.processEvents()

    assert dialog._scroll is not None
    control = getattr(dialog._form, case.primary)
    position = control.mapTo(dialog._scroll.viewport(), QPoint(0, 0))
    assert position.y() >= 0
    assert position.y() + control.height() <= dialog._scroll.viewport().height()

    buttons = dialog.findChild(QDialogButtonBox)
    assert buttons is not None
    assert buttons.isVisible() is True
    assert buttons.geometry().bottom() <= dialog.rect().bottom()
    assert dialog._scroll.horizontalScrollBar().maximum() == 0


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_ux59_large_spanish_initial_width_has_no_horizontal_bar(
    qtbot: QtBot,
    case: AuditCase,
) -> None:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    controller = FontSizeController(resolved_test_font(10.0))
    controller.apply(FontSize.LARGE)
    try:
        dialog = case.dialog_type(Translator(Language.SPANISH), UnitSystem.METRIC)
        qtbot.addWidget(dialog)
        dialog.resize(case.size[0], min(case.size[1], 640))
        dialog.show()
        qtbot.wait(10)
        QApplication.processEvents()

        assert dialog._scroll is not None
        assert dialog._scroll.horizontalScrollBar().maximum() == 0
        buttons = dialog.findChild(QDialogButtonBox)
        assert buttons is not None
        assert buttons.isVisible() is True
        assert buttons.geometry().bottom() <= dialog.rect().bottom()
    finally:
        controller.apply(FontSize.MEDIUM)


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_ux54_parameter_round_trip(
    qtbot: QtBot,
    case: AuditCase,
) -> None:
    dialog = _dialog(case)
    qtbot.addWidget(dialog)
    expected = dialog.parameters()

    dialog._accept()

    assert dialog.result_parameters() == expected


def test_stacked_yagi_puts_the_stacked_controls_above_the_yagi_editor(
    qtbot: QtBot,
) -> None:
    dialog = StackedYagiDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog.resize(940, 900)
    dialog.show()
    qtbot.wait(10)
    QApplication.processEvents()

    assert dialog._scroll is not None
    viewport = dialog._scroll.viewport()
    stacked = dialog._form._level_count.mapTo(viewport, QPoint(0, 0))
    editor = dialog._form._yagi.mapTo(viewport, QPoint(0, 0))
    assert stacked.y() < editor.y()
    assert stacked.y() + dialog._form._level_count.height() <= viewport.height()
