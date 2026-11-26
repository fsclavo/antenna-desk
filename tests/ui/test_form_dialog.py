# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Contract for the family-agnostic form dialog frame."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget
from pytestqt.qtbot import QtBot

from antennadesk.ui.widgets.form_dialog import FormDialogFrame


def _form(parent: QWidget | None = None) -> QWidget:
    form = QWidget(parent)
    layout = QVBoxLayout(form)
    layout.addWidget(QLineEdit(form))
    layout.addWidget(QLineEdit(form))
    return form


def test_frame_keeps_notes_and_actions_outside_the_scroll(qtbot: QtBot) -> None:
    form = _form()
    note = QLabel("note")
    dialog = FormDialogFrame(
        title="Test",
        form=form,
        notes=(note,),
        initial_size=(920, 640),
        scroll_form=True,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.wait(10)

    assert dialog.form is form
    assert dialog.notes == (note,)
    assert dialog.form_scroll is not None
    assert dialog.form_scroll.widget() is form
    assert dialog.form_scroll.isAncestorOf(note) is False
    assert dialog.form_scroll.isAncestorOf(dialog.buttons) is False
    assert dialog.buttons.isVisible() is True
    assert dialog.buttons.geometry().bottom() <= dialog.rect().bottom()


def test_frame_can_embed_a_compact_form_without_scroll(qtbot: QtBot) -> None:
    form = _form()
    dialog = FormDialogFrame(
        title="Compact",
        form=form,
        initial_size=(560, 500),
        scroll_form=False,
    )
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.wait(10)

    assert dialog.form_scroll is None
    assert form.isVisible() is True
    assert dialog.buttons.isVisible() is True


def test_subclass_accept_hook_can_reject_the_close(qtbot: QtBot) -> None:
    class RejectingDialog(FormDialogFrame):
        def __init__(self) -> None:
            super().__init__(
                title="Reject",
                form=_form(),
                initial_size=(560, 500),
                scroll_form=False,
            )
            self.rejected = False

        def _accept(self) -> None:
            self.rejected = True

    dialog = RejectingDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.wait(10)

    dialog.buttons.accepted.emit()

    assert dialog.rejected is True
    assert dialog.isVisible() is True
