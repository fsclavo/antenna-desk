# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Display-unit helpers for antenna-family forms."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QDoubleSpinBox

from ..i18n import Translator
from ..units import (
    DisplayUnits,
    LengthUnit,
    UnitSystem,
    length_unit_key,
    radius_unit_key,
)

_DEFAULT_STEP_M: dict[LengthUnit, float] = {
    "mm": 0.0001,
    "cm": 0.0001,
    "m": 0.001,
    "in": 0.000254,
    "ft": 0.0003048,
}


@dataclass(frozen=True, slots=True)
class LengthFieldSpec:
    """Physical range and presentation hints for one editable length field."""

    minimum_m: float
    maximum_m: float
    step_m: float | None = None
    scale_hint: LengthUnit | None = None


class LengthField:
    """Configure a QDoubleSpinBox with a physical range and display unit."""

    def __init__(
        self,
        spin_box: QDoubleSpinBox,
        spec: LengthFieldSpec,
        translator: Translator,
        display_units: DisplayUnits,
    ) -> None:
        self._spin_box = spin_box
        self._spec = spec
        self._translator = translator
        self._display_units = display_units
        self._unit: LengthUnit = display_units.unit_for(
            spec.minimum_m,
            scale_hint=spec.scale_hint,
        )

    @property
    def unit(self) -> LengthUnit:
        return self._unit

    @property
    def display_units(self) -> DisplayUnits:
        return self._display_units

    def configure(self, value_m: float, *, unit: LengthUnit | None = None) -> None:
        resolved = unit or self._display_units.unit_for(
            value_m,
            scale_hint=self._spec.scale_hint,
        )
        self._unit = resolved
        factor = self._display_units.meters_per_unit(resolved)
        step_m = self._spec.step_m or _DEFAULT_STEP_M[resolved]
        blocker = QSignalBlocker(self._spin_box)
        try:
            self._spin_box.setDecimals(self._display_units.decimals_for(resolved))
            self._spin_box.setRange(
                self._spec.minimum_m / factor,
                self._spec.maximum_m / factor,
            )
            self._spin_box.setSingleStep(step_m / factor)
            self._spin_box.setSuffix(f" {self._translator.t(f'unit.{resolved}')}")
            self._spin_box.setValue(value_m / factor)
        finally:
            del blocker

    def value_m(self) -> float:
        return self._spin_box.value() * self._display_units.meters_per_unit(self._unit)

    def set_value_m(self, value_m: float) -> None:
        self.configure(value_m, unit=self._unit)

    def set_display_units(self, display_units: DisplayUnits) -> None:
        value_m = self.value_m()
        self._display_units = display_units
        self.configure(value_m)


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
