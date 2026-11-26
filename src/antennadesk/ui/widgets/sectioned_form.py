# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Semantic one/two-column form layout for generator dialogs."""

from __future__ import annotations

import itertools
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import IntEnum, StrEnum

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)


class FormLayoutMode(StrEnum):
    SINGLE = "single"
    TWO_COLUMN = "two_column"
    AUTO = "auto"


class FormColumn(IntEnum):
    LEFT = 0
    RIGHT = 1


@dataclass(frozen=True, slots=True)
class FormRow:
    """One labelled control, a widget-only row, or a prebuilt label."""

    label: str | QLabel | None
    control: QWidget


@dataclass(frozen=True, slots=True)
class FormSection:
    """A semantic group kept together in one column."""

    rows: tuple[FormRow, ...]
    column: FormColumn | None = None
    title: str | QLabel | None = None


class SectionedForm(QWidget):
    """Lay out semantic sections in one or two atomic columns.

    The helper owns the ``QFormLayout`` instances so callers can bind their
    existing label/help registry to every column. It never duplicates labels
    or controls.
    """

    def __init__(
        self,
        sections: Sequence[FormSection],
        *,
        mode: FormLayoutMode,
        label_factory: Callable[[str, QWidget], QLabel],
        row_threshold: int = 12,
        width_threshold: int = 920,
        target_width_px: int | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if not sections:
            raise ValueError("at least one section is required")
        if row_threshold < 1 or width_threshold < 1:
            raise ValueError("layout thresholds must be positive")
        self._sections = tuple(sections)
        self._label_factory = label_factory
        self._mode = FormLayoutMode(mode)
        total_rows = sum(len(section.rows) for section in self._sections)
        available_width = target_width_px if target_width_px is not None else width_threshold
        if self._mode is FormLayoutMode.SINGLE:
            column_count = 1
        elif self._mode is FormLayoutMode.TWO_COLUMN:
            column_count = 2
        else:
            column_count = (
                2 if total_rows >= row_threshold and available_width >= width_threshold else 1
            )
        self._column_count = column_count

        assigned = self._assign_sections(column_count)
        self._forms: list[QFormLayout] = []
        columns = QHBoxLayout(self)
        columns.setContentsMargins(0, 0, 0, 0)
        columns.setSpacing(24 if column_count == 2 else 0)
        for column_sections in assigned:
            form = QFormLayout()
            form.setContentsMargins(0, 0, 0, 0)
            form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            if column_count == 2:
                form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
                form.setVerticalSpacing(6)
            self._populate(form, column_sections)
            self._forms.append(form)
            columns.addLayout(form, 1)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    @property
    def forms(self) -> tuple[QFormLayout, ...]:
        return tuple(self._forms)

    @property
    def column_count(self) -> int:
        return self._column_count

    @property
    def sections(self) -> tuple[FormSection, ...]:
        return self._sections

    def tab_order(self) -> tuple[QWidget, ...]:
        """Return controls in visual reading order.

        Two-column forms read the left column first, then the right column.
        Hidden controls remain in the sequence; Qt skips them at runtime.
        """

        order: list[QWidget] = []
        for column_sections in self._assign_sections(self._column_count):
            for section in column_sections:
                order.extend(row.control for row in section.rows)
        return tuple(order)

    def apply_tab_order(self, *trailing: QWidget) -> None:
        """Chain the section controls and optional trailing widgets."""

        for first, second in itertools.pairwise(self.tab_order() + trailing):
            QWidget.setTabOrder(first, second)

    def _assign_sections(self, column_count: int) -> list[list[FormSection]]:
        if column_count == 1:
            return [list(self._sections)]
        assigned: list[list[FormSection]] = [[], []]
        counts = [0, 0]
        for section in self._sections:
            if section.column is not None:
                column = int(section.column)
                if column not in (0, 1):
                    raise ValueError("section column must be left or right")
            else:
                column = 0 if counts[0] <= counts[1] else 1
            assigned[column].append(section)
            counts[column] += len(section.rows)
        return assigned

    def _populate(self, form: QFormLayout, sections: Sequence[FormSection]) -> None:
        for section in sections:
            if section.title is not None:
                title = (
                    section.title
                    if isinstance(section.title, QLabel)
                    else QLabel(section.title, self)
                )
                title.setWordWrap(True)
                form.addRow(title)
            for row in section.rows:
                if row.label is None:
                    form.addRow(row.control)
                elif isinstance(row.label, QLabel):
                    form.addRow(row.label, row.control)
                else:
                    form.addRow(
                        self._label_factory(row.label, row.control),
                        row.control,
                    )
