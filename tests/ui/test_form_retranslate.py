# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Language switches retranslate every antenna-family form."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QLabel, QWidget
from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.beverage_form import BeverageForm
from antennadesk.ui.widgets.biquad_form import BiquadForm
from antennadesk.ui.widgets.discone_form import DisconeForm
from antennadesk.ui.widgets.endfed_form import EndFedForm
from antennadesk.ui.widgets.fan_dipole_form import FanDipoleForm
from antennadesk.ui.widgets.hexbeam_form import HexbeamForm
from antennadesk.ui.widgets.inverted_l_form import InvertedLForm
from antennadesk.ui.widgets.inverted_v_form import InvertedVForm
from antennadesk.ui.widgets.j_pole_form import JPoleForm
from antennadesk.ui.widgets.loaded_dipole_form import LoadedDipoleForm
from antennadesk.ui.widgets.magnetic_loop_form import MagneticLoopForm
from antennadesk.ui.widgets.moxon_form import MoxonForm
from antennadesk.ui.widgets.ocfd_form import OCFDForm
from antennadesk.ui.widgets.phased_vertical_form import PhasedVerticalForm
from antennadesk.ui.widgets.quad_beam_form import QuadBeamForm
from antennadesk.ui.widgets.ringo_form import RingoForm
from antennadesk.ui.widgets.scv_form import ScvForm
from antennadesk.ui.widgets.t2fd_form import T2FDForm
from antennadesk.ui.widgets.transmission_line_doublet_form import (
    TransmissionLineDoubletForm,
)
from antennadesk.ui.widgets.trap_dipole_form import TrapDipoleForm
from antennadesk.ui.widgets.trap_yagi_form import TrapYagiForm
from antennadesk.ui.widgets.vertical_form import VerticalForm
from antennadesk.ui.widgets.yagi_form import YagiForm
from antennadesk.ui.widgets.zepp_form import ZeppForm

FORMS = (
    (OCFDForm, "field.fundamental_frequency"),
    (VerticalForm, "vertical.height"),
    (InvertedLForm, "inverted_l.vertical_height"),
    (InvertedVForm, "inverted_v.apex_height"),
    (MagneticLoopForm, "magnetic_loop.diameter"),
    (YagiForm, "field.frequency"),
    (MoxonForm, "moxon.width"),
    (FanDipoleForm, "field.frequency"),
    (TrapDipoleForm, "trap_dipole.low_band"),
    (TrapYagiForm, "trap_yagi.trap_inset"),
    (HexbeamForm, "hexbeam.turning_radius"),
    (T2FDForm, "t2fd.lowest_frequency"),
    (EndFedForm, "field.design_frequency"),
    (JPoleForm, "j_pole.radiator_height"),
    (RingoForm, "ringo.radiator_height"),
    (ScvForm, "scv.horizontal_length"),
    (BiquadForm, "biquad.loop_side"),
    (BeverageForm, "beverage.termination_resistance"),
    (LoadedDipoleForm, "loaded_dipole.link_offset"),
    (DisconeForm, "discone.cone_radius"),
    (PhasedVerticalForm, "phased_vertical.phase_step"),
    (QuadBeamForm, "quad_beam.reflector_spacing"),
    (TransmissionLineDoubletForm, "g5rv.line_impedance"),
    (ZeppForm, "zepp.radiator_length"),
)


@pytest.mark.parametrize(("form_type", "label_key"), FORMS)
def test_family_form_retranslates_its_labels(
    qtbot: QtBot,
    form_type: type[QWidget],
    label_key: str,
) -> None:
    translator = Translator(Language.ENGLISH)
    form = form_type(translator, UnitSystem.METRIC)
    qtbot.addWidget(form)

    spanish_text = Translator(Language.SPANISH).t(label_key)
    assert spanish_text not in [label.text() for label in form.findChildren(QLabel)]

    translator.set_language(Language.SPANISH)
    form.retranslate()

    assert spanish_text in [label.text() for label in form.findChildren(QLabel)]


def test_family_form_retranslates_options_and_buttons(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    form = YagiForm(translator, UnitSystem.METRIC)
    qtbot.addWidget(form)

    translator.set_language(Language.SPANISH)
    form.retranslate()

    spanish = Translator(Language.SPANISH)
    assert form._table.horizontalHeaderItem(0).text() == spanish.t("yagi.element")
    assert form._material.itemText(0) == spanish.t("material.copper")
    assert form._add.text() == spanish.t("yagi.add_element")
    assert form._polarization.toolTip() == spanish.t("yagi.polarization_hint")


def test_main_window_retranslates_all_family_forms(window: MainWindow) -> None:
    window._set_language(Language.SPANISH)

    spanish = Translator(Language.SPANISH)
    for form, label_key in (
        (window._ocfd_form, "field.fundamental_frequency"),
        (window._yagi_form, "field.frequency"),
        (window._vertical_form, "vertical.height"),
        (window._endfed_form, "field.design_frequency"),
    ):
        assert spanish.t(label_key) in [label.text() for label in form.findChildren(QLabel)]
