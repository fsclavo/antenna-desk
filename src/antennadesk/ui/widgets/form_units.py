# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Display-unit helpers for antenna-family forms."""

from __future__ import annotations

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QDoubleSpinBox

from ..i18n import Translator
from ..units import UnitSystem, length_unit_key, radius_unit_key


def apply_length_suffixes(
    translator: Translator,
    unit_system: UnitSystem,
    *spin_boxes: QDoubleSpinBox,
) -> None:
    suffix = f" {translator.t(length_unit_key(unit_system))}"
    for spin_box in spin_boxes:
        spin_box.setSuffix(suffix)


def apply_radius_units(
    translator: Translator,
    unit_system: UnitSystem,
    *spin_boxes: QDoubleSpinBox,
) -> None:
    suffix = f" {translator.t(radius_unit_key(unit_system))}"
    decimals = 3 if unit_system is UnitSystem.METRIC else 4
    minimum, maximum = (0.01, 1_000.0) if unit_system is UnitSystem.METRIC else (0.0004, 40.0)
    blockers = [QSignalBlocker(spin_box) for spin_box in spin_boxes]
    try:
        for spin_box in spin_boxes:
            spin_box.setRange(minimum, maximum)
            spin_box.setDecimals(decimals)
            spin_box.setSuffix(suffix)
    finally:
        del blockers
