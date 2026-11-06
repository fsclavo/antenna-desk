# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Typical soil presets for the finite-ground editor."""

from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox

from ...domain.environment.ground import GroundKind
from ..i18n import Translator

CUSTOM_SOIL_KEY = "custom"


@dataclass(frozen=True, slots=True)
class SoilPreset:
    """A broad soil category with typical HF ground constants.

    The values are starting points adapted from the ARRL Antenna Book ground
    table as reproduced by L. B. Cebik, "The Second Medium", which credits
    Terman's Radio Engineer's Handbook. Moisture, frequency, and local geology
    change the real values, so the editor always keeps the numeric fields
    editable and labels the result as a typical value.
    """

    key: str
    label_key: str
    relative_permittivity: float
    conductivity_s_per_m: float


SOIL_PRESETS: tuple[SoilPreset, ...] = (
    SoilPreset("average", "soil.average", 13.0, 0.005),
    SoilPreset("rich", "soil.rich", 20.0, 0.0303),
    SoilPreset("dry_sand", "soil.dry_sand", 10.0, 0.002),
    SoilPreset("rocky", "soil.rocky", 13.0, 0.002),
    SoilPreset("fresh_water", "soil.fresh_water", 80.0, 0.001),
    SoilPreset("salt_water", "soil.salt_water", 81.0, 5.0),
)


def matching_soil_key(
    relative_permittivity: float,
    conductivity_s_per_m: float,
) -> str:
    """Return the preset key matching the numeric values, or ``custom``."""

    for preset in SOIL_PRESETS:
        if math.isclose(
            relative_permittivity,
            preset.relative_permittivity,
            rel_tol=1e-6,
            abs_tol=1e-9,
        ) and math.isclose(
            conductivity_s_per_m,
            preset.conductivity_s_per_m,
            rel_tol=1e-6,
            abs_tol=1e-12,
        ):
            return preset.key
    return CUSTOM_SOIL_KEY


class GroundPresetController:
    """Keep a soil preset selector in sync with the existing ground fields."""

    def __init__(
        self,
        ground_combo: QComboBox,
        soil_combo: QComboBox,
        permittivity: QDoubleSpinBox,
        conductivity: QDoubleSpinBox,
        translator: Translator,
    ) -> None:
        self._ground_combo = ground_combo
        self._soil_combo = soil_combo
        self._permittivity = permittivity
        self._conductivity = conductivity
        self._translator = translator
        self._updating = False

        self._populate()
        self._soil_combo.setToolTip(translator.t("soil.hint"))
        self._ground_combo.currentIndexChanged.connect(self._update_enabled)
        self._soil_combo.currentIndexChanged.connect(self._apply_selected)
        self._permittivity.valueChanged.connect(self._sync_selection)
        self._conductivity.valueChanged.connect(self._sync_selection)
        self._update_enabled()
        self._sync_selection()

    def _populate(self) -> None:
        current = self._soil_combo.currentData()
        self._soil_combo.blockSignals(True)
        try:
            self._soil_combo.clear()
            self._soil_combo.addItem(self._translator.t("soil.custom"), CUSTOM_SOIL_KEY)
            for preset in SOIL_PRESETS:
                self._soil_combo.addItem(self._translator.t(preset.label_key), preset.key)
            if current is not None:
                index = self._soil_combo.findData(current)
                if index >= 0:
                    self._soil_combo.setCurrentIndex(index)
        finally:
            self._soil_combo.blockSignals(False)

    def _update_enabled(self) -> None:
        finite = self._ground_combo.currentData() == GroundKind.FINITE.value
        self._soil_combo.setEnabled(finite)

    def _apply_selected(self) -> None:
        if self._updating:
            return
        key = self._soil_combo.currentData()
        preset = next((item for item in SOIL_PRESETS if item.key == key), None)
        if preset is None:
            return
        self._updating = True
        try:
            self._permittivity.setValue(preset.relative_permittivity)
            self._conductivity.setValue(preset.conductivity_s_per_m)
        finally:
            self._updating = False

    def _sync_selection(self, *_args: object) -> None:
        if self._updating:
            return
        key = matching_soil_key(
            self._permittivity.value(),
            self._conductivity.value(),
        )
        index = self._soil_combo.findData(key)
        if index < 0:
            return
        self._updating = True
        try:
            self._soil_combo.setCurrentIndex(index)
        finally:
            self._updating = False

    def retranslate(self) -> None:
        """Refresh the preset labels after a language change."""

        current = self._soil_combo.currentData()
        self._populate()
        index = self._soil_combo.findData(current) if current is not None else -1
        if index >= 0:
            self._soil_combo.setCurrentIndex(index)
        self._soil_combo.setToolTip(self._translator.t("soil.hint"))
