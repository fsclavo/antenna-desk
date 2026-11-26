# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX52 wave 1: loaded dipole, biquad, Moxon, and magnetic loop."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QWidget
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.biquad_dialog import BiquadDialog
from antennadesk.ui.dialogs.loaded_dipole_dialog import LoadedDipoleDialog
from antennadesk.ui.dialogs.magnetic_loop_dialog import MagneticLoopDialog
from antennadesk.ui.dialogs.moxon_dialog import MoxonDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.biquad_form import BiquadForm
from antennadesk.ui.widgets.form_dialog import FormDialogFrame
from antennadesk.ui.widgets.loaded_dipole_form import LoadedDipoleForm
from antennadesk.ui.widgets.magnetic_loop_form import MagneticLoopForm
from antennadesk.ui.widgets.moxon_form import MoxonForm


@dataclass(frozen=True, slots=True)
class WaveCase:
    name: str
    dialog_type: type[QDialog]
    form_type: type[QWidget]
    rows: int


CASES = (
    WaveCase("loaded_dipole", LoadedDipoleDialog, LoadedDipoleForm, 16),
    WaveCase("biquad", BiquadDialog, BiquadForm, 14),
    WaveCase("moxon", MoxonDialog, MoxonForm, 14),
    WaveCase("magnetic_loop", MagneticLoopDialog, MagneticLoopForm, 14),
)
LANGUAGES = [Language.ENGLISH, Language.SPANISH]


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_wave1_dialogs_use_the_shared_scaffold(
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


@pytest.mark.parametrize("case", CASES, ids=[case.name for case in CASES])
def test_wave1_sidebar_forms_stay_single_column(
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
def test_wave1_dialogs_fit_the_budget(
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
def test_wave1_parameter_round_trip(
    qtbot: QtBot,
    case: WaveCase,
) -> None:
    dialog = case.dialog_type(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)
    expected = dialog.parameters()

    dialog._accept()

    assert dialog.result_parameters() == expected
