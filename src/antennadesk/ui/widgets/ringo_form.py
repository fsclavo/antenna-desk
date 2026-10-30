# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a Ringo-style vertical."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.ringo import MAX_RING_SIDES, MIN_RING_SIDES, RingoParameters
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key

MATERIALS = (COPPER, ALUMINUM)


class RingoForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: RingoParameters | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._updating = False

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(50.1)

        self._radiator_height = QDoubleSpinBox(self)
        self._radiator_height.setDecimals(3)
        self._radiator_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._radiator_height.setValue(length_from_m(3.0, unit_system))

        self._ring_diameter = QDoubleSpinBox(self)
        self._ring_diameter.setDecimals(3)
        self._ring_diameter.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._ring_diameter.setValue(length_from_m(0.33, unit_system))

        self._ring_height = QDoubleSpinBox(self)
        self._ring_height.setDecimals(3)
        self._ring_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._ring_height.setValue(0.0)

        self._ring_sides = QSpinBox(self)
        self._ring_sides.setRange(MIN_RING_SIDES, MAX_RING_SIDES)
        self._ring_sides.setValue(16)

        self._radius = QDoubleSpinBox(self)
        self._radius.setRange(0.01, 1_000.0)
        self._radius.setDecimals(3)
        self._radius.setSuffix(" mm")
        self._radius.setValue(1.0)

        self._material = QComboBox(self)
        for material in MATERIALS:
            self._material.addItem(material.name, material)
        self._material.setItemText(0, translator.t("material.copper"))
        self._material.setItemText(1, translator.t("material.aluminum"))

        self._ground = QComboBox(self)
        self._ground.addItem("", GroundKind.FREE_SPACE.value)
        self._ground.addItem("", GroundKind.PERFECT.value)
        self._ground.addItem("", GroundKind.FINITE.value)
        self._ground.setItemText(0, translator.t("ground.free_space"))
        self._ground.setItemText(1, translator.t("ground.perfect"))
        self._ground.setItemText(2, translator.t("ground.finite"))
        self._ground.setCurrentIndex(2)

        self._permittivity = QDoubleSpinBox(self)
        self._permittivity.setRange(1.0, 1_000.0)
        self._permittivity.setDecimals(2)
        self._permittivity.setValue(13.0)

        self._conductivity = QDoubleSpinBox(self)
        self._conductivity.setRange(0.000001, 1_000.0)
        self._conductivity.setDecimals(6)
        self._conductivity.setSingleStep(0.001)
        self._conductivity.setValue(0.005)
        self._conductivity.setSuffix(" S/m")

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        form = QFormLayout()
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("ringo.radiator_height"), self._radiator_height)
        form.addRow(translator.t("ringo.ring_diameter"), self._ring_diameter)
        form.addRow(translator.t("ringo.ring_height"), self._ring_height)
        form.addRow(translator.t("ringo.ring_sides"), self._ring_sides)
        form.addRow(translator.t("ringo.wire_radius"), self._radius)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(form)
        layout.addWidget(self._geometry)

        for widget in (
            self._frequency,
            self._radiator_height,
            self._ring_diameter,
            self._ring_height,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._ring_sides.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        if parameters is not None:
            self.set_parameters(parameters)
        self._update_ground_controls()
        self._update_geometry()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _ground_changed(self, *_args: object) -> None:
        self._update_ground_controls()
        self._emit_changed()

    def _update_ground_controls(self) -> None:
        finite = self._ground.currentData() == GroundKind.FINITE.value
        self._permittivity.setEnabled(finite)
        self._conductivity.setEnabled(finite)

    def _ground_model(self) -> GroundModel:
        kind = self._ground.currentData()
        if kind == GroundKind.FREE_SPACE.value:
            return GroundModel.free_space()
        if kind == GroundKind.PERFECT.value:
            return GroundModel.perfect()
        if kind == GroundKind.FINITE.value:
            return GroundModel.finite(
                relative_permittivity=self._permittivity.value(),
                conductivity_s_per_m=self._conductivity.value(),
            )
        raise ValueError("invalid ground model")

    def _selected_material(self) -> ConductorMaterial:
        value = self._material.currentData()
        return value if isinstance(value, ConductorMaterial) else COPPER

    def set_parameters(self, parameters: RingoParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._radiator_height.setValue(
                length_from_m(parameters.radiator_height_m, self._unit_system)
            )
            self._ring_diameter.setValue(
                length_from_m(parameters.ring_diameter_m, self._unit_system)
            )
            self._ring_height.setValue(length_from_m(parameters.ring_height_m, self._unit_system))
            self._ring_sides.setValue(parameters.ring_sides)
            self._radius.setValue(parameters.wire_radius_m * 1_000.0)
            material_index = self._material.findData(parameters.material)
            if material_index >= 0:
                self._material.setCurrentIndex(material_index)
            ground_index = self._ground.findData(parameters.ground.kind.value)
            if ground_index >= 0:
                self._ground.setCurrentIndex(ground_index)
            if parameters.ground.relative_permittivity is not None:
                self._permittivity.setValue(parameters.ground.relative_permittivity)
            if parameters.ground.conductivity_s_per_m is not None:
                self._conductivity.setValue(parameters.ground.conductivity_s_per_m)
        finally:
            self._updating = False
        self._update_ground_controls()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._frequency.setValue(frequency_hz / 1_000_000.0)

    def _update_geometry(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "ringo.geometry",
                height=f"{length_from_m(parameters.radiator_height_m, self._unit_system):.2f}",
                ring=f"{length_from_m(parameters.ring_diameter_m, self._unit_system):.2f}",
                unit=unit,
            )
        )

    def parameters(self) -> RingoParameters:
        return RingoParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            radiator_height_m=length_to_m(self._radiator_height.value(), self._unit_system),
            ring_diameter_m=length_to_m(self._ring_diameter.value(), self._unit_system),
            ring_height_m=length_to_m(self._ring_height.value(), self._unit_system),
            ring_sides=self._ring_sides.value(),
            wire_radius_m=self._radius.value() / 1_000.0,
            material=self._selected_material(),
            ground=self._ground_model(),
        )
