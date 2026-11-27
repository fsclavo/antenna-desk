# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Family-agnostic dialog frame with a scroll/action split."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..fonts import scaled_dialog_size


class FormDialogFrame(QDialog):
    """A dialog with a form area, notes, and an always-visible action box.

    Subclasses override ``_accept`` for validation. The frame never inspects
    the form's family or fields.
    """

    def __init__(
        self,
        *,
        title: str,
        form: QWidget,
        notes: Sequence[QWidget] = (),
        initial_size: tuple[int, int] = (920, 860),
        scroll_form: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._form = form
        self._notes = tuple(notes)
        self.setWindowTitle(title)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self._buttons.accepted.connect(self._accept)
        self._buttons.rejected.connect(self.reject)

        self._scroll: QScrollArea | None = None
        layout = QVBoxLayout(self)
        if scroll_form:
            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setWidget(form)
            self._scroll = scroll
            layout.addWidget(scroll, 1)
        else:
            layout.addWidget(form, 1)
        for note in self._notes:
            layout.addWidget(note)
        layout.addWidget(self._buttons)
        self.resize(
            *scaled_dialog_size(
                *initial_size,
                minimum_width=self._minimum_content_width(layout),
            )
        )

    def _minimum_content_width(self, layout: QVBoxLayout) -> int:
        """Return the form/chrome width needed before the screen cap applies."""

        content = max(self._form.minimumWidth(), self._form.minimumSizeHint().width())
        if self._scroll is not None:
            content = max(content, self._scroll.minimumSizeHint().width())
        for note in self._notes:
            content = max(content, note.minimumSizeHint().width())
        content = max(content, self._buttons.minimumSizeHint().width())
        margins = layout.contentsMargins()
        return content + margins.left() + margins.right()

    @property
    def form(self) -> QWidget:
        return self._form

    @property
    def buttons(self) -> QDialogButtonBox:
        return self._buttons

    @property
    def form_scroll(self) -> QScrollArea | None:
        return self._scroll

    @property
    def notes(self) -> tuple[QWidget, ...]:
        return self._notes

    def _accept(self) -> None:
        self.accept()
