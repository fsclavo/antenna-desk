# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolve optional UI help text and apply it to widgets.

Help is intentionally separate from the visible label. A field may keep its
short label while the tooltip explains a model assumption, a unit convention,
or a value the user cannot infer from the label alone.
"""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QWidget

from .i18n import Translator


def help_text(
    translator: Translator,
    key: str,
    *,
    family: str | None = None,
    explicit_key: str | None = None,
) -> str | None:
    """Return the best available help for ``key``.

    Resolution order:

    1. an explicit key supplied by the caller;
    2. a family-specific override, ``help.<family>.<key>``;
    3. the shared key, ``help.<key>``;
    4. the existing ``<key>_hint`` convention.

    Missing translations return ``None`` so callers never render a raw key.
    """

    candidates: list[str] = []
    if explicit_key:
        candidates.append(explicit_key)
    if family:
        candidates.append(f"help.{family}.{key}")
    candidates.append(f"help.{key}")
    candidates.append(f"{key}_hint")
    for candidate in candidates:
        text = translator.optional(candidate)
        if text is not None and text.strip():
            return text
    return None


def apply_help(
    widget: QWidget,
    translator: Translator,
    key: str,
    *,
    family: str | None = None,
    explicit_key: str | None = None,
) -> None:
    """Set or clear the tooltip for one help-managed widget."""

    text = help_text(
        translator,
        key,
        family=family,
        explicit_key=explicit_key,
    )
    widget.setToolTip(text or "")


def apply_form_help(
    form: QFormLayout,
    translator: Translator,
    *,
    family: str | None = None,
) -> None:
    """Apply help to every labelled row in a form.

    The label's ``objectName`` is the help key. This lets forms keep their
    existing construction code and opt into help by naming their labels.
    """

    for row in range(form.rowCount()):
        label_item = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
        label_widget = label_item.widget() if label_item is not None else None
        key = label_widget.objectName() if isinstance(label_widget, QLabel) else ""
        if not key:
            continue
        apply_row_help(form, row, translator, key, family=family)


def apply_row_help(
    form: QFormLayout,
    row: int,
    translator: Translator,
    key: str,
    *,
    family: str | None = None,
) -> None:
    """Apply help to one label/control row without naming the label."""

    label_item = form.itemAt(row, QFormLayout.ItemRole.LabelRole)
    field_item = form.itemAt(row, QFormLayout.ItemRole.FieldRole)
    label = label_item.widget() if label_item is not None else None
    text = help_text(translator, key, family=family)
    if isinstance(label, QLabel):
        label.setToolTip(text or "")
    field = field_item.widget() if field_item is not None else None
    if field is not None:
        field.setToolTip(text or "")
