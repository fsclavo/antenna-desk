# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit contract for the shared sectioned form layout."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QScrollArea
from pytestqt.qtbot import QtBot

from antennadesk.ui.widgets.sectioned_form import (
    FormColumn,
    FormLayoutMode,
    FormRow,
    FormSection,
    SectionedForm,
)


def _label(key: str, _control: QLineEdit) -> QLabel:
    return QLabel(key)


def _section(
    prefix: str,
    count: int,
    *,
    column: FormColumn | None = None,
) -> FormSection:
    return FormSection(
        tuple(FormRow(f"{prefix}.{index}", QLineEdit()) for index in range(count)),
        column=column,
    )


def _form(
    sections: tuple[FormSection, ...],
    *,
    mode: FormLayoutMode = FormLayoutMode.AUTO,
    target_width_px: int = 920,
    parent: QDialog | None = None,
) -> SectionedForm:
    return SectionedForm(
        sections,
        mode=mode,
        label_factory=_label,
        target_width_px=target_width_px,
        parent=parent,
    )


def test_single_mode_uses_one_form_and_keeps_section_order(qtbot: QtBot) -> None:
    left = _section("left", 2)
    right = _section("right", 3)
    form = _form((left, right), mode=FormLayoutMode.SINGLE)
    qtbot.addWidget(form)

    assert form.column_count == 1
    assert len(form.forms) == 1
    controls = [row.control for section in (left, right) for row in section.rows]
    assert form.tab_order() == tuple(controls)


def test_two_column_mode_keeps_sections_atomic(qtbot: QtBot) -> None:
    left = _section("left", 2, column=FormColumn.LEFT)
    right = _section("right", 3, column=FormColumn.RIGHT)
    form = _form((left, right), mode=FormLayoutMode.TWO_COLUMN)
    qtbot.addWidget(form)

    assert form.column_count == 2
    assert len(form.forms) == 2
    left_controls = [row.control for row in left.rows]
    right_controls = [row.control for row in right.rows]
    assert form.tab_order() == tuple(left_controls + right_controls)
    assert all(form.forms[0].indexOf(control) >= 0 for control in left_controls)
    assert all(form.forms[1].indexOf(control) >= 0 for control in right_controls)
    assert all(form.forms[0].indexOf(control) < 0 for control in right_controls)
    assert all(form.forms[1].indexOf(control) < 0 for control in left_controls)


def test_auto_mode_uses_the_row_and_width_thresholds(qtbot: QtBot) -> None:
    eleven = _form((_section("eleven", 11),), target_width_px=920)
    twelve = _form((_section("twelve", 12),), target_width_px=920)
    narrow = _form((_section("narrow", 12),), target_width_px=800)
    for form in (eleven, twelve, narrow):
        qtbot.addWidget(form)

    assert eleven.column_count == 1
    assert twelve.column_count == 2
    assert narrow.column_count == 1


def test_two_columns_read_left_then_right_for_focus(qtbot: QtBot) -> None:
    left = _section("left", 2, column=FormColumn.LEFT)
    right = _section("right", 2, column=FormColumn.RIGHT)
    dialog = QDialog()
    qtbot.addWidget(dialog)
    form = _form((left, right), mode=FormLayoutMode.TWO_COLUMN, parent=dialog)
    trailing = QLineEdit(dialog)
    form.apply_tab_order(trailing)
    dialog.show()
    qtbot.wait(10)

    first = left.rows[0].control
    second = left.rows[1].control
    third = right.rows[0].control
    first.setFocus()
    QApplication.processEvents()
    dialog.focusNextChild()
    assert second.hasFocus()
    dialog.focusNextChild()
    assert third.hasFocus()


def test_spanish_labels_do_not_force_horizontal_scrolling(qtbot: QtBot) -> None:
    left = FormSection(
        (
            FormRow("Longitud de punta cónica (0 = recto)", QLineEdit()),
            FormRow("Diámetro del mástil", QLineEdit()),
        ),
        column=FormColumn.LEFT,
    )
    right = FormSection(
        (
            FormRow("Elemento alimentado plegado", QLineEdit()),
            FormRow("Permitividad relativa del suelo", QLineEdit()),
        ),
        column=FormColumn.RIGHT,
    )
    form = _form((left, right), mode=FormLayoutMode.TWO_COLUMN)
    scroll = QScrollArea()
    qtbot.addWidget(scroll)
    scroll.setWidgetResizable(True)
    scroll.setWidget(form)
    scroll.resize(920, 400)
    scroll.show()
    qtbot.wait(10)

    assert form.column_count == 2
    assert scroll.horizontalScrollBar().maximum() == 0
