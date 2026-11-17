# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared material selector population and retranslation."""

from __future__ import annotations

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QComboBox

from ..domain.antennas.material_defaults import default_material_for_template
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
    selected: ConductorMaterial | None = None,
) -> None:
    """Replace the combo contents with the shared ordered material presets."""

    blocker = QSignalBlocker(combo)
    combo.clear()
    for material in materials:
        combo.addItem(material_label(translator, material), material)
    if selected is not None:
        index = combo.findData(selected)
        if index >= 0:
            combo.setCurrentIndex(index)
    del blocker


def select_material(combo: QComboBox, material: ConductorMaterial) -> None:
    """Select a material by stable value, ignoring an unknown preset."""

    index = combo.findData(material)
    if index >= 0:
        combo.setCurrentIndex(index)


def populate_template_material_combo(
    combo: QComboBox,
    translator: Translator,
    template_id: str,
) -> None:
    """Populate the shared presets and preselect the template default."""

    populate_material_combo(
        combo,
        translator,
        selected=default_material_for_template(template_id),
    )


def retranslate_material_combo(combo: QComboBox, translator: Translator) -> None:
    """Refresh every material label without changing the current selection."""

    blocker = QSignalBlocker(combo)
    for index in range(combo.count()):
        data = combo.itemData(index)
        if isinstance(data, ConductorMaterial):
            combo.setItemText(index, material_label(translator, data))
    del blocker
