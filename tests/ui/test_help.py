# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Help-resolution and tooltip application tests."""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QWidget
from pytestqt.qtbot import QtBot

from antennadesk.ui.help import apply_form_help, apply_help, help_text
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.dipole_form import DipoleForm
from antennadesk.ui.widgets.form_i18n import FormLabels


def test_help_resolution_order_and_missing_keys() -> None:
    translator = Translator(Language.ENGLISH)

    explicit = help_text(
        translator,
        "field.height",
        explicit_key="help.wire_dipole.field.height",
    )
    family = help_text(translator, "field.height", family="wire_dipole")
    shared = help_text(translator, "field.height", family="yagi")
    hint = help_text(translator, "yagi.polarization")
    missing = help_text(translator, "field.unknown")

    assert explicit == family
    assert "horizontal wire" in (explicit or "")
    assert "selected ground model" in (shared or "")
    assert "polarization" in (hint or "").lower()
    assert missing is None


def test_apply_form_help_sets_and_retranslates_label_and_control(
    qtbot: QtBot,
) -> None:
    translator = Translator(Language.ENGLISH)
    parent = QWidget()
    qtbot.addWidget(parent)
    form = QFormLayout(parent)
    label = QLabel(parent)
    label.setObjectName("field.height")
    control = QLineEdit(parent)
    form.addRow(label, control)

    apply_form_help(form, translator)

    assert label.toolTip() == control.toolTip()
    assert "selected ground model" in label.toolTip()

    translator.set_language(Language.SPANISH)
    apply_form_help(form, translator)

    assert "modelo de suelo" in label.toolTip()
    assert label.toolTip() == control.toolTip()


def test_form_labels_sets_family_help_and_refreshes(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    parent = QWidget()
    qtbot.addWidget(parent)
    control = QLineEdit(parent)
    labels = FormLabels(translator, parent, family="wire_dipole")

    label = labels.label("field.height", control)

    assert "horizontal wire" in label.toolTip()
    assert control.toolTip() == label.toolTip()

    translator.set_language(Language.SPANISH)
    labels.retranslate()

    assert "hilo horizontal" in label.toolTip()
    assert control.toolTip() == label.toolTip()


def test_form_labels_binds_controls_from_a_form(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    parent = QWidget()
    qtbot.addWidget(parent)
    form = QFormLayout(parent)
    labels = FormLabels(translator, parent)
    label = labels.label("field.height")
    control = QLineEdit(parent)
    form.addRow(label, control)

    labels.bind_form(form)

    assert "selected ground model" in label.toolTip()
    assert control.toolTip() == label.toolTip()

    control.setEnabled(False)
    labels.retranslate()

    assert "selected ground model" in label.toolTip()


def test_yagi_form_applies_help_to_shared_fields(qtbot: QtBot) -> None:
    from antennadesk.ui.widgets.yagi_form import YagiForm

    form = YagiForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.retranslate()

    labels = {
        label.objectName(): label
        for label in form.findChildren(QLabel)
        if label.objectName().startswith("field.")
    }

    assert "selected ground model" in labels["field.height"].toolTip()
    assert form._height.toolTip() == labels["field.height"].toolTip()
    assert "Design frequency" in labels["field.frequency"].toolTip()
    assert form._frequency.toolTip() == labels["field.frequency"].toolTip()


def test_apply_help_clears_a_missing_key_instead_of_showing_it(
    qtbot: QtBot,
) -> None:
    parent = QWidget()
    qtbot.addWidget(parent)
    label = QLabel(parent)
    label.setToolTip("stale")

    apply_help(label, Translator(Language.ENGLISH), "field.unknown")

    assert label.toolTip() == ""


def test_main_window_sections_actions_and_tabs_have_help(window) -> None:  # type: ignore[no-untyped-def]
    assert "Antenna type" in window._design_panel.toolTip()
    assert "solver timeout" in window._solver_group.toolTip()
    assert "Frequency range" in window._sweep_group.toolTip()
    assert "Far-field" in window._pattern_group.toolTip()
    assert "amateur bands" in window._band_group.toolTip()
    assert "Dimensioned construction" in window._geometry.toolTip()
    assert "amateur bands" in window._analyze_bands_action.toolTip()
    assert "form values" in window._apply_button.toolTip()
    assert "family optimizer" in window._optimize_button.toolTip()

    tabs = window._results._tabs
    impedance = tabs.indexOf(window._results._impedance_tab)
    pattern = tabs.indexOf(window._results._pattern_tab)
    assert "Impedance" in tabs.tabToolTip(impedance)
    assert "radiation" in tabs.tabToolTip(pattern)

    window._set_language(Language.SPANISH)
    assert "Tiempo límite" in window._solver_group.toolTip()
    assert "bandas" in window._analyze_bands_action.toolTip()


def test_dipole_form_applies_help_to_its_labels_and_controls(qtbot: QtBot) -> None:
    form = DipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.retranslate()

    labels = {
        label.objectName(): label
        for label in form.findChildren(QLabel)
        if label.objectName().startswith("field.")
    }

    assert "Design frequency" in labels["field.frequency"].toolTip()
    assert form._frequency.toolTip() == labels["field.frequency"].toolTip()
    assert "selected ground model" in labels["field.height"].toolTip()
    assert form._height.toolTip() == labels["field.height"].toolTip()
    assert "frequency sweep" in form._sweep.toolTip()
    assert "custom sweep" in form._sweep_start.toolTip()
    assert "custom sweep" in form._sweep_stop.toolTip()
