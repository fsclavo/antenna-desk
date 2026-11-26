# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX53 wave 2: Beverage, SCV, J-pole, and OCFD."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QWidget
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.beverage_dialog import BeverageDialog
from antennadesk.ui.dialogs.j_pole_dialog import JPoleDialog
from antennadesk.ui.dialogs.ocfd_dialog import OCFDDialog
from antennadesk.ui.dialogs.scv_dialog import ScvDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.beverage_form import BeverageForm
from antennadesk.ui.widgets.form_dialog import FormDialogFrame
from antennadesk.ui.widgets.j_pole_form import JPoleForm
from antennadesk.ui.widgets.ocfd_form import OCFDForm
from antennadesk.ui.widgets.scv_form import ScvForm


@dataclass(frozen=True, slots=True)
class WaveCase:
    name: str
    dialog_type: type[QDialog]
    form_type: type[QWidget]
    rows: int


CASES = (
    WaveCase("beverage", BeverageDialog, BeverageForm, 13),
    WaveCase("scv", ScvDialog, ScvForm, 13),
    WaveCase("j_pole", JPoleDialog, JPoleForm, 14),
    WaveCase("ocfd", OCFDDialog, OCFDForm, 12),
)
LANGUAGES = [Language.ENGLISH, Language.SPANISH]


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_wave2_dialogs_use_the_shared_scaffold(
    qtbot: QtBot,
    case: WaveCase,
) -> None:
    dialog = case.dialog_type(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert isinstance(dialog, FormDialogFrame)
    assert dialog._form._wide_layout is True
    assert dialog._form._sectioned.column_count == 2
    assert dialog._scroll is not None
    assert dialog._scroll.widget() is dialog._form
    assert dialog._buttons.parent() is dialog
    assert all(not dialog._scroll.isAncestorOf(note) for note in dialog.notes)


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_wave2_sidebar_forms_stay_single_column(
    qtbot: QtBot,
    case: WaveCase,
) -> None:
    form = case.form_type(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)

    assert form._wide_layout is False
    assert form._sectioned.column_count == 1
    assert len(form._sectioned.forms) == 1
    assert sum(len(section.rows) for section in form._sectioned.sections) == case.rows


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_wave2_dialogs_fit_the_budget(
    qtbot: QtBot,
    case: WaveCase,
    language: Language,
) -> None:
    dialog = case.dialog_type(Translator(language), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog.resize(920, 640)
    dialog.show()
    qtbot.wait(10)

    assert dialog.minimumSizeHint().height() <= 640
    assert dialog._form.minimumSizeHint().height() <= 640
    assert dialog._scroll is not None
    assert dialog._scroll.verticalScrollBar().maximum() == 0
    assert dialog._scroll.horizontalScrollBar().maximum() == 0
    buttons = dialog.findChild(QDialogButtonBox)
    assert buttons is not None
    assert buttons.isVisible() is True
    assert buttons.geometry().bottom() <= dialog.rect().bottom()


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_wave2_parameter_round_trip(
    qtbot: QtBot,
    case: WaveCase,
) -> None:
    dialog = case.dialog_type(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    expected = dialog.parameters()

    dialog._accept()

    assert dialog.result_parameters() == expected


def test_ocfd_band_plan_footer_stays_outside_the_scroll(qtbot: QtBot) -> None:
    dialog = OCFDDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    dialog.resize(920, 640)
    dialog.show()
    qtbot.wait(10)

    assert dialog._scroll is not None
    assert dialog._scroll.isAncestorOf(dialog._band_plan_button) is False
    assert dialog._band_plan_button.isVisible() is True
    assert dialog._band_plan_label.text()
