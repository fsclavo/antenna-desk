# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Radial-system starting presets for vertical antennas."""

from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QSpinBox

from ...domain.common import units
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m

CUSTOM_RADIAL_KEY = "custom"


@dataclass(frozen=True, slots=True)
class RadialPreset:
    """A UI-only starting point for the radial field.

    The preset is not persisted. Only the numeric radial fields and base height
    it writes are saved with the design.
    """

    key: str
    label_key: str
    radial_count: int
    length_fraction: float | None
    base_height_m: float | None


RADIAL_PRESETS: tuple[RadialPreset, ...] = (
    RadialPreset("none", "radial_preset.none", 0, None, None),
    RadialPreset("ground", "radial_preset.ground", 16, 0.25, 0.25),
    RadialPreset("elevated", "radial_preset.elevated", 4, 0.25, 2.0),
    RadialPreset("screen", "radial_preset.screen", 32, 0.10, 0.25),
)


def radial_length_m(preset: RadialPreset, frequency_hz: float) -> float:
    """Return the starting radial length for a preset at a frequency."""

    if preset.length_fraction is None:
        return 0.0
    return units.wavelength_m(frequency_hz) * preset.length_fraction


def matching_radial_key(
    frequency_hz: float,
    base_height_m: float,
    radial_count: int,
    radial_length_m_value: float,
) -> str:
    """Return the preset matching the numeric fields, or ``custom``."""

    for preset in RADIAL_PRESETS:
        if radial_count != preset.radial_count:
            continue
        if preset.key == "none":
            return preset.key
        if preset.base_height_m is not None and not math.isclose(
            base_height_m,
            preset.base_height_m,
            abs_tol=1e-3,
        ):
            continue
        expected_length = radial_length_m(preset, frequency_hz)
        if math.isclose(
            radial_length_m_value,
            expected_length,
            rel_tol=1e-6,
            abs_tol=1e-3,
        ):
            return preset.key
    return CUSTOM_RADIAL_KEY


class RadialPresetController:
    """Keep the radial-system selector in sync with the numeric radial fields."""

    def __init__(
        self,
        preset_combo: QComboBox,
        frequency: QDoubleSpinBox,
        base_height: QDoubleSpinBox,
        radial_count: QSpinBox,
        radial_length: QDoubleSpinBox,
        translator: Translator,
        unit_system: UnitSystem,
    ) -> None:
        self._preset_combo = preset_combo
        self._frequency = frequency
        self._base_height = base_height
        self._radial_count = radial_count
        self._radial_length = radial_length
        self._translator = translator
        self._unit_system = unit_system
        self._updating = False

        self._populate()
        self._preset_combo.setToolTip(translator.t("vertical.radial_system_hint"))
        self._preset_combo.currentIndexChanged.connect(self._apply_selected)
        self._frequency.valueChanged.connect(self._frequency_changed)
        self._base_height.valueChanged.connect(self._sync_selection)
        self._radial_count.valueChanged.connect(self._sync_selection)
        self._radial_length.valueChanged.connect(self._sync_selection)
        self._sync_selection()

    def _populate(self) -> None:
        current = self._preset_combo.currentData()
        self._preset_combo.blockSignals(True)
        try:
            self._preset_combo.clear()
            self._preset_combo.addItem(
                self._translator.t("radial_preset.custom"),
                CUSTOM_RADIAL_KEY,
            )
            for preset in RADIAL_PRESETS:
                self._preset_combo.addItem(
                    self._translator.t(preset.label_key),
                    preset.key,
                )
            if current is not None:
                index = self._preset_combo.findData(current)
                if index >= 0:
                    self._preset_combo.setCurrentIndex(index)
        finally:
            self._preset_combo.blockSignals(False)

    def _preset(self) -> RadialPreset | None:
        key = self._preset_combo.currentData()
        return next((preset for preset in RADIAL_PRESETS if preset.key == key), None)

    def _frequency_hz(self) -> float:
        return self._frequency.value() * 1_000_000.0

    def _apply_selected(self) -> None:
        if self._updating:
            return
        preset = self._preset()
        if preset is None:
            return
        self._updating = True
        try:
            if preset.base_height_m is not None:
                self._base_height.setValue(length_from_m(preset.base_height_m, self._unit_system))
            self._radial_count.setValue(preset.radial_count)
            self._radial_length.setValue(
                length_from_m(radial_length_m(preset, self._frequency_hz()), self._unit_system)
            )
        finally:
            self._updating = False

    def _frequency_changed(self, *_args: object) -> None:
        if self._updating:
            return
        preset = self._preset()
        if preset is None or preset.length_fraction is None:
            return
        self._updating = True
        try:
            self._radial_length.setValue(
                length_from_m(radial_length_m(preset, self._frequency_hz()), self._unit_system)
            )
        finally:
            self._updating = False

    def _sync_selection(self, *_args: object) -> None:
        if self._updating:
            return
        key = matching_radial_key(
            self._frequency_hz(),
            length_to_m(self._base_height.value(), self._unit_system),
            self._radial_count.value(),
            length_to_m(self._radial_length.value(), self._unit_system),
        )
        index = self._preset_combo.findData(key)
        if index < 0 or self._preset_combo.currentIndex() == index:
            return
        self._updating = True
        try:
            self._preset_combo.setCurrentIndex(index)
        finally:
            self._updating = False

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        self._unit_system = unit_system

    def retranslate(self) -> None:
        self._populate()
        self._preset_combo.setToolTip(self._translator.t("vertical.radial_system_hint"))
