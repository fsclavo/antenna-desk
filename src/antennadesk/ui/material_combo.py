# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared material selector population and retranslation."""

from __future__ import annotations

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox

from ..domain.antennas.materials import CONDUCTOR_MATERIALS, ConductorMaterial
from .i18n import Translator


def material_label(translator: Translator, material: ConductorMaterial) -> str:
    """Return the localized label, falling back to the stable material name."""

    return translator.optional(f"material.{material.name}") or material.name


def populate_material_combo(
    combo: QComboBox,
    translator: Translator,
    *,
    materials: tuple[ConductorMaterial, ...] = CONDUCTOR_MATERIALS,
) -> None:
    """Replace the combo contents with the shared ordered material presets."""

    blocker = QSignalBlocker(combo)
    combo.clear()
    for material in materials:
        combo.addItem(material_label(translator, material), material)
    del blocker


def retranslate_material_combo(combo: QComboBox, translator: Translator) -> None:
    """Refresh every material label without changing the current selection."""

    blocker = QSignalBlocker(combo)
    for index in range(combo.count()):
        data = combo.itemData(index)
        if isinstance(data, ConductorMaterial):
            combo.setItemText(index, material_label(translator, data))
    del blocker
