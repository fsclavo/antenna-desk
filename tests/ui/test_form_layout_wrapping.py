# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""UX59 form-width and long-label wrapping contract."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
)
from pytestqt.qtbot import QtBot

from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.widgets.form_dialog import FormDialogFrame
from antennadesk.ui.widgets.form_i18n import FormLabels
from antennadesk.ui.widgets.form_layout import configure_form_layout
from antennadesk.ui.widgets.sectioned_form import (
    FormLayoutMode,
    FormRow,
    FormSection,
    SectionedForm,
)

LONG_ENGLISH_LABEL = (
    "Design frequency and physical radiator length including the feed section "
    "and the installation return path in metres "
)
LONG_SPANISH_LABEL = (
    "Frecuencia de diseño y longitud física del radiador incluyendo la sección "
    "de alimentación y el camino de retorno de la instalación en metros "
)


def test_configure_form_layout_sets_the_width_contract() -> None:
    form = configure_form_layout(QFormLayout())

    assert form.rowWrapPolicy() is QFormLayout.RowWrapPolicy.WrapLongRows
    assert form.fieldGrowthPolicy() is QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
    assert form.contentsMargins().left() == 0
    assert form.contentsMargins().top() == 0
    assert form.horizontalSpacing() > 0
    assert form.verticalSpacing() > 0


def test_form_labels_wrap_by_default() -> None:
    parent = QLabel()
    labels = FormLabels(Translator(Language.SPANISH), parent)

    label = labels.label("field.design_frequency")

    assert label.wordWrap() is True


@pytest.mark.parametrize(
    ("language", "text"),
    [
        (Language.ENGLISH, LONG_ENGLISH_LABEL),
        (Language.SPANISH, LONG_SPANISH_LABEL),
    ],
)
@pytest.mark.parametrize("width", [560, 920])
def test_long_single_column_label_does_not_force_a_horizontal_scrollbar(
    qtbot: QtBot,
    language: Language,
    text: str,
    width: int,
) -> None:
    del language
    label = QLabel(text)
    form = SectionedForm(
        (FormSection((FormRow(label, QLineEdit()),)),),
        mode=FormLayoutMode.SINGLE,
        label_factory=lambda _text, _control: QLabel(text),
    )
    dialog = FormDialogFrame(
        title="Long label",
        form=form,
        initial_size=(width, 640),
    )
    qtbot.addWidget(dialog)
    dialog.resize(width, 640)
    dialog.show()
    QApplication.processEvents()

    scroll = dialog.findChild(QScrollArea)
    assert scroll is not None
    assert scroll.horizontalScrollBar().maximum() == 0
    assert label.wordWrap() is True
