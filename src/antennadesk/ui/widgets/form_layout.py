# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared QFormLayout policy for generator forms."""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout

FORM_HORIZONTAL_SPACING_PX = 8
FORM_VERTICAL_SPACING_PX = 6


def configure_form_layout(
    form: QFormLayout,
    *,
    vertical_spacing: int = FORM_VERTICAL_SPACING_PX,
) -> QFormLayout:
    """Apply the generator-form width and wrapping contract.

    Long labels wrap instead of forcing a horizontal scrollbar, non-fixed
    fields grow into the available width, and the form itself contributes no
    outer margins. The dialog frame owns the page margins.
    """

    form.setContentsMargins(0, 0, 0, 0)
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
    form.setHorizontalSpacing(FORM_HORIZONTAL_SPACING_PX)
    form.setVerticalSpacing(vertical_spacing)
    return form
