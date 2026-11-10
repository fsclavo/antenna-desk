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


def test_apply_help_clears_a_missing_key_instead_of_showing_it(
    qtbot: QtBot,
) -> None:
    parent = QWidget()
    qtbot.addWidget(parent)
    label = QLabel(parent)
    label.setToolTip("stale")

    apply_help(label, Translator(Language.ENGLISH), "field.unknown")

    assert label.toolTip() == ""


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
