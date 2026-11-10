# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for trapped Yagi antennas."""

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
from ...domain.antennas.trap_yagi import (
    MAX_ELEMENTS,
    MIN_ELEMENTS,
    TrapYagiParameters,
    trap_yagi_parameters,
)
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import (
    UnitSystem,
    height_bounds,
    length_bounds,
    length_from_m,
    length_to_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
)
from .form_i18n import FormLabels, retranslate_combo
from .form_units import apply_length_suffixes, apply_radius_units
from .ground_presets import GroundPresetController

MATERIALS = (COPPER, ALUMINUM)


class TrapYagiForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: TrapYagiParameters | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self)
        self._unit_system = unit_system
        self._updating = False
        minimum_length, maximum_length = length_bounds(unit_system)
        minimum_height, maximum_height = height_bounds(unit_system)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")

        self._high_band_frequency = QDoubleSpinBox(self)
        self._high_band_frequency.setRange(0.1, 100_000.0)
        self._high_band_frequency.setDecimals(6)
        self._high_band_frequency.setSuffix(" MHz")

        self._element_count = QSpinBox(self)
        self._element_count.setRange(MIN_ELEMENTS, MAX_ELEMENTS)

        self._driven_length = QDoubleSpinBox(self)
        self._driven_length.setRange(minimum_length, maximum_length)
        self._driven_length.setDecimals(3)
        self._driven_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._reflector_spacing = QDoubleSpinBox(self)
        self._reflector_spacing.setRange(minimum_length, maximum_length)
        self._reflector_spacing.setDecimals(3)
        self._reflector_spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._director_spacing = QDoubleSpinBox(self)
        self._director_spacing.setRange(minimum_length, maximum_length)
        self._director_spacing.setDecimals(3)
        self._director_spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._reflector_scale = QDoubleSpinBox(self)
        self._reflector_scale.setRange(1.0, 1.2)
        self._reflector_scale.setDecimals(3)
        self._reflector_scale.setSingleStep(0.005)

        self._director_scale = QDoubleSpinBox(self)
        self._director_scale.setRange(0.8, 1.0)
        self._director_scale.setDecimals(3)
        self._director_scale.setSingleStep(0.005)

        self._trap_inset = QDoubleSpinBox(self)
        self._trap_inset.setRange(minimum_length, maximum_length)
        self._trap_inset.setDecimals(3)
        self._trap_inset.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._trap_frequency = QDoubleSpinBox(self)
        self._trap_frequency.setRange(0.1, 100_000.0)
        self._trap_frequency.setDecimals(6)
        self._trap_frequency.setSuffix(" MHz")

        self._trap_inductance = QDoubleSpinBox(self)
        self._trap_inductance.setRange(0.0001, 10_000.0)
        self._trap_inductance.setDecimals(4)
        self._trap_inductance.setSuffix(" µH")

        self._height = QDoubleSpinBox(self)
        self._height.setRange(minimum_height, maximum_height)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)

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

        form = QFormLayout()
        form.addRow(self._labels.label("field.frequency"), self._frequency)
        form.addRow(
            self._labels.label("trap_yagi.high_band_frequency"),
            self._high_band_frequency,
        )
        form.addRow(self._labels.label("trap_yagi.element_count"), self._element_count)
        form.addRow(self._labels.label("trap_yagi.driven_length"), self._driven_length)
        form.addRow(
            self._labels.label("trap_yagi.reflector_spacing"),
            self._reflector_spacing,
        )
        form.addRow(
            self._labels.label("trap_yagi.director_spacing"),
            self._director_spacing,
        )
        form.addRow(
            self._labels.label("trap_yagi.reflector_scale"),
            self._reflector_scale,
        )
        form.addRow(
            self._labels.label("trap_yagi.director_scale"),
            self._director_scale,
        )
        form.addRow(self._labels.label("trap_yagi.trap_inset"), self._trap_inset)
        form.addRow(
            self._labels.label("trap_yagi.trap_frequency"),
            self._trap_frequency,
        )
        form.addRow(
            self._labels.label("trap_yagi.trap_inductance"),
            self._trap_inductance,
        )
        form.addRow(self._labels.label("field.height"), self._height)
        form.addRow(self._labels.label("field.azimuth"), self._azimuth)
        form.addRow(self._labels.label("field.wire_radius"), self._radius)
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

        for widget in (
            self._frequency,
            self._high_band_frequency,
            self._driven_length,
            self._reflector_spacing,
            self._director_spacing,
            self._reflector_scale,
            self._director_scale,
            self._trap_inset,
            self._trap_frequency,
            self._trap_inductance,
            self._height,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._element_count.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        initial = parameters or trap_yagi_parameters(
            ground=GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            )
        )
        self.set_parameters(initial)
        self._update_ground_controls()
        self._update_element_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        retranslate_combo(
            self._material,
            self._translator,
            ("material.copper", "material.aluminum"),
        )
        retranslate_combo(
            self._ground,
            self._translator,
            ("ground.free_space", "ground.perfect", "ground.finite"),
        )
        self._update_geometry()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self._update_element_controls()
            self._update_geometry()
            self.changed.emit()

    def _ground_changed(self, *_args: object) -> None:
        self._update_ground_controls()
        self._emit_changed()

    def _update_ground_controls(self) -> None:
        finite = self._ground.currentData() == GroundKind.FINITE.value
        self._permittivity.setEnabled(finite)
        self._conductivity.setEnabled(finite)

    def _update_element_controls(self) -> None:
        director = self._element_count.value() == MAX_ELEMENTS
        self._director_spacing.setEnabled(director)
        self._director_scale.setEnabled(director)

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

    def load_starting_dimensions(self) -> None:
        current = self.parameters()
        self.set_parameters(
            trap_yagi_parameters(
                frequency_hz=current.frequency_hz,
                high_band_frequency_hz=current.high_band_frequency_hz,
                element_count=current.element_count,
                trap_inductance_h=current.trap_inductance_h,
                reflector_scale=current.reflector_scale,
                director_scale=current.director_scale,
                height_m=current.height_m,
                azimuth_deg=current.azimuth_deg,
                wire_radius_m=current.wire_radius_m,
                material=current.material,
                ground=current.ground,
            )
        )
        self.changed.emit()

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            parameters = None
        self._unit_system = unit_system
        minimum_length, maximum_length = length_bounds(unit_system)
        minimum_height, maximum_height = height_bounds(unit_system)
        previous_updating = self._updating
        self._updating = True
        try:
            apply_radius_units(self._translator, unit_system, self._radius)
            apply_length_suffixes(
                self._translator,
                unit_system,
                self._driven_length,
                self._reflector_spacing,
                self._director_spacing,
                self._trap_inset,
                self._height,
            )
            for spin in (
                self._driven_length,
                self._reflector_spacing,
                self._director_spacing,
                self._trap_inset,
            ):
                spin.setRange(minimum_length, maximum_length)
            self._height.setRange(minimum_height, maximum_height)
        finally:
            self._updating = previous_updating
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: TrapYagiParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._high_band_frequency.setValue(parameters.high_band_frequency_hz / 1_000_000.0)
            self._element_count.setValue(parameters.element_count)
            self._driven_length.setValue(
                length_from_m(parameters.driven_length_m, self._unit_system)
            )
            self._reflector_spacing.setValue(
                length_from_m(parameters.reflector_spacing_m, self._unit_system)
            )
            self._director_spacing.setValue(
                length_from_m(parameters.director_spacing_m, self._unit_system)
            )
            self._reflector_scale.setValue(parameters.reflector_scale)
            self._director_scale.setValue(parameters.director_scale)
            self._trap_inset.setValue(length_from_m(parameters.trap_inset_m, self._unit_system))
            self._trap_frequency.setValue(parameters.trap_frequency_hz / 1_000_000.0)
            self._trap_inductance.setValue(parameters.trap_inductance_h * 1e6)
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
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
        self._update_element_controls()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._frequency.setValue(frequency_hz / 1_000_000.0)
        self._high_band_frequency.setValue(frequency_hz * 2.0 / 1_000_000.0)
        self._trap_frequency.setValue(frequency_hz * 2.0 / 1_000_000.0)

    def _update_geometry(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "trap_yagi.geometry",
                count=parameters.element_count,
                driven=f"{length_from_m(parameters.driven_length_m, self._unit_system):.3f}",
                boom=f"{length_from_m(parameters.boom_length_m, self._unit_system):.3f}",
                inset=f"{length_from_m(parameters.trap_inset_m, self._unit_system):.3f}",
                trap=parameters.trap_frequency_hz / 1_000_000.0,
                unit=unit,
            )
        )

    def parameters(self) -> TrapYagiParameters:
        return TrapYagiParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            high_band_frequency_hz=self._high_band_frequency.value() * 1_000_000.0,
            driven_length_m=length_to_m(self._driven_length.value(), self._unit_system),
            reflector_spacing_m=length_to_m(self._reflector_spacing.value(), self._unit_system),
            trap_inset_m=length_to_m(self._trap_inset.value(), self._unit_system),
            trap_frequency_hz=self._trap_frequency.value() * 1_000_000.0,
            trap_inductance_h=self._trap_inductance.value() * 1e-6,
            element_count=self._element_count.value(),
            director_spacing_m=length_to_m(self._director_spacing.value(), self._unit_system),
            reflector_scale=self._reflector_scale.value(),
            director_scale=self._director_scale.value(),
            height_m=length_to_m(self._height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
