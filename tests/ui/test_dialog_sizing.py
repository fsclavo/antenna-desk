# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX60 layout-based dialog sizing and compact controls."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.basic_antenna_dialog import BasicAntennaDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.form_dialog import FormDialogFrame


def _form(minimum_width: int) -> QWidget:
    form = QWidget()
    layout = QVBoxLayout(form)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(QLabel("A field"))
    form.setMinimumWidth(minimum_width)
    return form


def test_dialog_grows_only_when_the_form_needs_the_width(qtbot: QtBot) -> None:
    dialog = FormDialogFrame(
        title="Sizing",
        form=_form(300),
        initial_size=(560, 640),
    )
    qtbot.addWidget(dialog)

    assert dialog.width() == 560


def test_dialog_grows_to_the_form_minimum_width(qtbot: QtBot) -> None:
    form = _form(640)
    dialog = FormDialogFrame(
        title="Sizing",
        form=form,
        initial_size=(560, 640),
    )
    qtbot.addWidget(dialog)

    assert dialog.width() >= form.minimumWidth()
    assert dialog.width() > 560


def test_dialog_width_stays_inside_the_screen_cap(qtbot: QtBot) -> None:
    form = _form(4_000)
    dialog = FormDialogFrame(
        title="Sizing",
        form=form,
        initial_size=(560, 640),
    )
    qtbot.addWidget(dialog)
    screen = QApplication.primaryScreen()
    assert screen is not None
    cap = max(320, round(screen.availableGeometry().width() * 0.9))

    assert dialog.width() <= cap


def test_basic_antenna_template_value_has_a_compact_policy(qtbot: QtBot) -> None:
    dialog = BasicAntennaDialog(Translator(Language.SPANISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert (
        dialog._basic_form._template_value.sizePolicy().horizontalPolicy()
        is QSizePolicy.Policy.Ignored
    )
    assert (
        dialog._basic_form._family_value.sizePolicy().horizontalPolicy()
        is QSizePolicy.Policy.Ignored
    )
    assert dialog._basic_form._template_value.toolTip()


def test_scroll_area_content_does_not_drive_an_unbounded_width(qtbot: QtBot) -> None:
    dialog = FormDialogFrame(
        title="Sizing",
        form=_form(2_000),
        initial_size=(560, 640),
    )
    qtbot.addWidget(dialog)
    dialog.show()
    QApplication.processEvents()

    scroll = dialog.findChild(QScrollArea)
    assert scroll is not None
    assert scroll.horizontalScrollBar().maximum() > 0
