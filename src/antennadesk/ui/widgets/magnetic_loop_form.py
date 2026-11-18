# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a small tuned magnetic loop."""

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

from ...domain.antennas.magnetic_loop import (
    MAX_SIDES,
    MIN_SIDES,
    MagneticLoopParameters,
)
from ...domain.antennas.materials import COPPER, ConductorMaterial
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..material_combo import (
    populate_material_combo,
    retranslate_material_combo,
)
from ..units import (
    DisplayUnits,
    LengthPolicy,
    UnitSystem,
    length_from_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
)
from .form_i18n import FormLabels, retranslate_combo
from .form_units import LengthField, LengthFieldSpec, apply_radius_units
from .ground_presets import GroundPresetController


class MagneticLoopForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: MagneticLoopParameters | None = None,
        parent: QWidget | None = None,
        *,
        display_units: DisplayUnits | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self)
        self._unit_system = unit_system
        self._display_units = display_units or DisplayUnits(
            unit_system,
            LengthPolicy.FIXED,
        )
        self._updating = False

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(7.1)

        self._diameter = QDoubleSpinBox(self)
        self._diameter.setDecimals(3)
        self._diameter.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._diameter.setValue(length_from_m(1.0, unit_system))

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(1.0, unit_system))

        self._sides = QSpinBox(self)
        self._sides.setRange(MIN_SIDES, MAX_SIDES)
        self._sides.setSingleStep(2)
        self._sides.setValue(36)

        self._gap = QDoubleSpinBox(self)
        self._gap.setDecimals(3)
        self._gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._gap.setValue(length_from_m(0.05, unit_system))

        self._diameter_field = LengthField(
            self._diameter,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._height_field = LengthField(
            self._height,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._gap_field = LengthField(
            self._gap,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._diameter_field.configure(1.0)
        self._height_field.configure(1.0)
        self._gap_field.configure(0.05)

        self._capacitance = QDoubleSpinBox(self)
        self._capacitance.setRange(0.001, 1_000_000.0)
        self._capacitance.setDecimals(3)
        self._capacitance.setSuffix(" pF")
        self._capacitance.setValue(200.0)

        self._esr = QDoubleSpinBox(self)
        self._esr.setRange(0.0, 100_000.0)
        self._esr.setDecimals(3)
        self._esr.setSuffix(" Ω")

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)
        self._radius.setValue(radius_from_m(0.005, unit_system))

        self._material = QComboBox(self)
        populate_material_combo(self._material, translator)

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
        self._soil = QComboBox(self)
        self._ground_presets = GroundPresetController(
            self._ground,
            self._soil,
            self._permittivity,
            self._conductivity,
            translator,
        )

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)
        self._hint = QLabel(self)
        self._hint.setWordWrap(True)
        self._hint.setText(translator.t("magnetic_loop.model_hint"))

        form = QFormLayout()
        form.addRow(self._labels.label("field.frequency"), self._frequency)
        form.addRow(self._labels.label("magnetic_loop.diameter"), self._diameter)
        form.addRow(self._labels.label("magnetic_loop.height"), self._height)
        form.addRow(self._labels.label("magnetic_loop.sides"), self._sides)
        form.addRow(self._labels.label("magnetic_loop.gap"), self._gap)
        form.addRow(self._labels.label("magnetic_loop.capacitance"), self._capacitance)
        form.addRow(self._labels.label("magnetic_loop.esr"), self._esr)
        form.addRow(self._labels.label("field.azimuth"), self._azimuth)
        form.addRow(self._labels.label("vertical.wire_radius"), self._radius)
        form.addRow(self._labels.label("field.material"), self._material)
        form.addRow(self._labels.label("field.ground"), self._ground)
        form.addRow(self._labels.label("field.soil_preset"), self._soil)
        form.addRow(self._labels.label("field.permittivity"), self._permittivity)
        form.addRow(self._labels.label("field.conductivity"), self._conductivity)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._labels.bind_form(form)
        layout.addLayout(form)
        layout.addWidget(self._geometry)
        layout.addWidget(self._hint)

        for widget in (
            self._frequency,
            self._diameter,
            self._height,
            self._gap,
            self._capacitance,
            self._esr,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._sides.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        if parameters is not None:
            self.set_parameters(parameters)
        self._update_ground_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        self._hint.setText(self._translator.t("magnetic_loop.model_hint"))
        retranslate_material_combo(self._material, self._translator)
        retranslate_combo(
            self._ground,
            self._translator,
            ("ground.free_space", "ground.perfect", "ground.finite"),
        )
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

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            parameters = None
        self._unit_system = unit_system
        self._display_units = DisplayUnits(
            unit_system,
            self._display_units.length_policy,
        )
        apply_radius_units(self._translator, unit_system, self._radius)
        for field in (self._diameter_field, self._height_field, self._gap_field):
            field.set_display_units(self._display_units)
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: MagneticLoopParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._diameter_field.configure(parameters.diameter_m)
            self._height_field.configure(parameters.height_m)
            self._sides.setValue(parameters.sides)
            self._gap_field.configure(parameters.gap_length_m)
            self._capacitance.setValue(parameters.tuning_capacitance_f * 1e12)
            self._esr.setValue(parameters.capacitor_esr_ohm)
            self._azimuth.setValue(parameters.azimuth_deg)
            self._radius.setValue(radius_from_m(parameters.wire_radius_m, self._unit_system))
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
                "magnetic_loop.geometry",
                diameter=f"{length_from_m(parameters.diameter_m, self._unit_system):.3f}",
                circumference=f"{length_from_m(parameters.circumference_m, self._unit_system):.3f}",
                top=f"{length_from_m(parameters.top_height_m, self._unit_system):.3f}",
                gap=f"{length_from_m(parameters.gap_length_m, self._unit_system):.3f}",
                capacitance=f"{parameters.tuning_capacitance_f * 1e12:.3f}",
                unit=unit,
            )
        )

    def parameters(self) -> MagneticLoopParameters:
        return MagneticLoopParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            diameter_m=self._diameter_field.value_m(),
            tuning_capacitance_f=self._capacitance.value() * 1e-12,
            height_m=self._height_field.value_m(),
            sides=self._sides.value(),
            gap_length_m=self._gap_field.value_m(),
            capacitor_esr_ohm=self._esr.value(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
