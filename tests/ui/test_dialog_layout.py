# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Layout guard for every family generator dialog in the UX52-UX55 registry."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QScrollArea,
    QWidget,
)
from pytestqt.qtbot import QtBot

from antennadesk.ui.dialogs.basic_antenna_dialog import BasicAntennaDialog
from antennadesk.ui.dialogs.beverage_dialog import BeverageDialog
from antennadesk.ui.dialogs.biquad_dialog import BiquadDialog
from antennadesk.ui.dialogs.discone_dialog import DisconeDialog
from antennadesk.ui.dialogs.endfed_dialog import EndFedDialog
from antennadesk.ui.dialogs.fan_dipole_dialog import FanDipoleDialog
from antennadesk.ui.dialogs.flower_pot_dialog import FlowerPotDialog
from antennadesk.ui.dialogs.hexbeam_dialog import HexbeamDialog
from antennadesk.ui.dialogs.inverted_l_dialog import InvertedLDialog
from antennadesk.ui.dialogs.inverted_v_dialog import InvertedVDialog
from antennadesk.ui.dialogs.j_pole_dialog import JPoleDialog
from antennadesk.ui.dialogs.loaded_dipole_dialog import LoadedDipoleDialog
from antennadesk.ui.dialogs.log_periodic_dialog import LogPeriodicDialog
from antennadesk.ui.dialogs.magnetic_loop_dialog import MagneticLoopDialog
from antennadesk.ui.dialogs.moxon_dialog import MoxonDialog
from antennadesk.ui.dialogs.ocfd_dialog import OCFDDialog
from antennadesk.ui.dialogs.phased_vertical_dialog import PhasedVerticalDialog
from antennadesk.ui.dialogs.quad_beam_dialog import QuadBeamDialog
from antennadesk.ui.dialogs.ringo_dialog import RingoDialog
from antennadesk.ui.dialogs.scv_dialog import ScvDialog
from antennadesk.ui.dialogs.stacked_yagi_dialog import StackedYagiDialog
from antennadesk.ui.dialogs.t2fd_dialog import T2FDDialog
from antennadesk.ui.dialogs.trap_dipole_dialog import TrapDipoleDialog
from antennadesk.ui.dialogs.trap_yagi_dialog import TrapYagiDialog
from antennadesk.ui.dialogs.vertical_dialog import VerticalDialog
from antennadesk.ui.dialogs.yagi_dialog import YagiDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.preferences import FontSize, FontSizeController
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.form_dialog import FormDialogFrame
from antennadesk.ui.widgets.yagi_form import YagiForm

WIDTH_BUDGET_PX = 920
HEIGHT_BUDGET_PX = 640


@dataclass(frozen=True, slots=True)
class DialogCase:
    name: str
    dialog_type: type[QDialog]
    exception: str | None = None


# No exceptions: every registered family dialog fits the height budget or owns
# a form scroll area. Future migrations must remove their exception when the
# layout guard starts passing.
REGISTRY: tuple[DialogCase, ...] = (
    DialogCase("yagi", YagiDialog),
    DialogCase("loaded_dipole", LoadedDipoleDialog),
    DialogCase("biquad", BiquadDialog),
    DialogCase("moxon", MoxonDialog),
    DialogCase("magnetic_loop", MagneticLoopDialog),
    DialogCase("beverage", BeverageDialog),
    DialogCase("scv", ScvDialog),
    DialogCase("j_pole", JPoleDialog),
    DialogCase("ocfd", OCFDDialog),
    DialogCase("stacked_yagi", StackedYagiDialog),
    DialogCase("endfed", EndFedDialog),
    DialogCase("vertical", VerticalDialog),
    DialogCase("log_periodic", LogPeriodicDialog),
    DialogCase("hexbeam", HexbeamDialog),
    DialogCase("trap_yagi", TrapYagiDialog),
    DialogCase("phased_vertical", PhasedVerticalDialog),
    DialogCase("quad_beam", QuadBeamDialog),
    DialogCase("trap_dipole", TrapDipoleDialog),
    DialogCase("t2fd", T2FDDialog),
    DialogCase("discone", DisconeDialog),
    DialogCase("basic_antenna", BasicAntennaDialog),
    DialogCase("fan_dipole", FanDipoleDialog),
    DialogCase("ringo", RingoDialog),
    DialogCase("flower_pot", FlowerPotDialog),
    DialogCase("inverted_v", InvertedVDialog),
    DialogCase("inverted_l", InvertedLDialog),
)
LANGUAGES = [Language.ENGLISH, Language.SPANISH]


def _form_scroll(dialog: QDialog, form: QWidget) -> QScrollArea | None:
    return next(
        (scroll for scroll in dialog.findChildren(QScrollArea) if scroll.widget() is form),
        None,
    )


def audit_generator_dialog(
    dialog: QDialog,
    *,
    width: int = WIDTH_BUDGET_PX,
    height: int = HEIGHT_BUDGET_PX,
) -> tuple[str, ...]:
    """Return layout-contract violations for one generator dialog."""

    issues: list[str] = []
    form = getattr(dialog, "_form", None)
    if not isinstance(form, QWidget):
        return ("dialog does not expose a form widget",)

    dialog.resize(width, height)
    dialog.show()
    QApplication.processEvents()

    minimum_height = dialog.minimumSizeHint().height()
    if minimum_height > height:
        issues.append(f"dialog minimum height {minimum_height} px exceeds {height} px")

    form_minimum = max(form.minimumSizeHint().height(), form.minimumHeight())
    scroll = _form_scroll(dialog, form)
    if form_minimum > height and scroll is None:
        issues.append(
            f"form minimum height {form_minimum} px exceeds {height} px without a scroll area"
        )

    buttons = dialog.findChild(QDialogButtonBox)
    if buttons is None:
        issues.append("dialog has no button box")
    else:
        if not buttons.isVisible():
            issues.append("button box is not visible")
        if buttons.geometry().top() < 0 or buttons.geometry().bottom() > dialog.rect().bottom():
            issues.append("button box lies outside the dialog rectangle")
        if scroll is not None and scroll.isAncestorOf(buttons):
            issues.append("button box is inside the form scroll area")

    for scroll_area in dialog.findChildren(QScrollArea):
        if scroll_area.horizontalScrollBar().maximum() > 0:
            issues.append("a scroll area needs a horizontal scrollbar")
            break

    return tuple(issues)


@pytest.mark.parametrize("language", LANGUAGES)
@pytest.mark.parametrize("case", REGISTRY, ids=[case.name for case in REGISTRY])
def test_generator_dialog_layout_guard(
    qtbot: QtBot,
    case: DialogCase,
    language: Language,
) -> None:
    dialog = case.dialog_type(Translator(language), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert isinstance(dialog, FormDialogFrame)
    issues = audit_generator_dialog(dialog)

    if case.exception is not None:
        assert issues, f"{case.name} now passes; remove the exception: {case.exception}"
        return
    assert issues == (), f"{case.name} ({language.value}): " + "; ".join(issues)


@pytest.mark.parametrize("case", REGISTRY, ids=[case.name for case in REGISTRY])
def test_ux59_large_font_at_920_has_no_horizontal_bar(
    qtbot: QtBot,
    case: DialogCase,
) -> None:
    app = QApplication.instance()
    assert isinstance(app, QApplication)
    controller = FontSizeController(QFont("Sans Serif", 10))
    controller.apply(FontSize.LARGE)
    try:
        dialog = case.dialog_type(Translator(Language.SPANISH), UnitSystem.METRIC)
        qtbot.addWidget(dialog)
        dialog.resize(WIDTH_BUDGET_PX, HEIGHT_BUDGET_PX)
        dialog.show()
        QApplication.processEvents()

        if dialog._scroll is not None:
            assert dialog._scroll.horizontalScrollBar().maximum() == 0
        else:
            assert dialog._form.minimumSizeHint().width() <= dialog.width()
        buttons = dialog.findChild(QDialogButtonBox)
        assert buttons is not None
        assert buttons.isVisible() is True
        assert buttons.geometry().bottom() <= dialog.rect().bottom()
    finally:
        controller.apply(FontSize.MEDIUM)


def test_registry_covers_every_family_generator_dialog() -> None:
    names = [case.name for case in REGISTRY]

    assert len(names) == len(set(names)) == 26


def test_guard_rejects_a_deliberately_tall_form_without_scroll(qtbot: QtBot) -> None:
    form = QWidget()
    form.setMinimumHeight(1087)
    dialog = FormDialogFrame(
        title="Tall fake form",
        form=form,
        initial_size=(WIDTH_BUDGET_PX, HEIGHT_BUDGET_PX),
        scroll_form=False,
    )
    qtbot.addWidget(dialog)

    issues = audit_generator_dialog(dialog)

    assert any("without a scroll area" in issue for issue in issues)
    assert any("minimum height" in issue for issue in issues)


def test_guard_rejects_the_old_single_column_yagi_shape(qtbot: QtBot) -> None:
    form = YagiForm(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        wide_layout=False,
    )
    dialog = FormDialogFrame(
        title="Legacy Yagi",
        form=form,
        initial_size=(WIDTH_BUDGET_PX, HEIGHT_BUDGET_PX),
        scroll_form=False,
    )
    qtbot.addWidget(dialog)

    issues = audit_generator_dialog(dialog)

    assert any("without a scroll area" in issue for issue in issues)
    assert any("minimum height" in issue for issue in issues)
