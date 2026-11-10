# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for phased vertical arrays."""

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
from ...domain.antennas.phased_vertical import (
    MAX_ELEMENTS,
    MAX_RADIALS,
    MIN_ELEMENTS,
    PhasedVerticalParameters,
    phased_vertical_parameters,
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


class PhasedVerticalForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: PhasedVerticalParameters | None = None,
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

        self._element_count = QSpinBox(self)
        self._element_count.setRange(MIN_ELEMENTS, MAX_ELEMENTS)

        self._spacing = QDoubleSpinBox(self)
        self._spacing.setRange(minimum_length, maximum_length)
        self._spacing.setDecimals(3)
        self._spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._height = QDoubleSpinBox(self)
        self._height.setRange(minimum_height, maximum_height)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setRange(minimum_height, maximum_height)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._phase_step = QDoubleSpinBox(self)
        self._phase_step.setRange(-360.0, 360.0)
        self._phase_step.setDecimals(1)
        self._phase_step.setSuffix("°")

        self._amplitude_taper = QDoubleSpinBox(self)
        self._amplitude_taper.setRange(0.0, 0.9)
        self._amplitude_taper.setDecimals(2)
        self._amplitude_taper.setSingleStep(0.01)

        self._radial_count = QSpinBox(self)
        self._radial_count.setRange(0, MAX_RADIALS)

        self._radial_length = QDoubleSpinBox(self)
        self._radial_length.setRange(minimum_length, maximum_length)
        self._radial_length.setDecimals(3)
        self._radial_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._radial_angle = QDoubleSpinBox(self)
        self._radial_angle.setRange(0.0, 360.0)
        self._radial_angle.setDecimals(1)
        self._radial_angle.setSuffix("°")

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
        self._overlap_warning = QLabel(self)
        self._overlap_warning.setWordWrap(True)
        self._overlap_warning.setStyleSheet("color: #9a6700;")
        self._overlap_warning.setVisible(False)

        form = QFormLayout()
        form.addRow(self._labels.label("field.frequency"), self._frequency)
        form.addRow(self._labels.label("phased_vertical.element_count"), self._element_count)
        form.addRow(self._labels.label("phased_vertical.spacing"), self._spacing)
        form.addRow(self._labels.label("field.height"), self._height)
        form.addRow(self._labels.label("field.base_height"), self._base_height)
        form.addRow(self._labels.label("phased_vertical.phase_step"), self._phase_step)
        form.addRow(
            self._labels.label("phased_vertical.amplitude_taper"),
            self._amplitude_taper,
        )
        form.addRow(self._labels.label("vertical.radial_count"), self._radial_count)
        form.addRow(self._labels.label("vertical.radial_length"), self._radial_length)
        form.addRow(self._labels.label("vertical.radial_angle"), self._radial_angle)
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
        layout.addWidget(self._overlap_warning)

        for widget in (
            self._frequency,
            self._spacing,
            self._height,
            self._base_height,
            self._phase_step,
            self._amplitude_taper,
            self._radial_length,
            self._radial_angle,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        for spin in (self._element_count, self._radial_count):
            spin.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        initial = parameters or phased_vertical_parameters(
            frequency_hz=14_100_000.0,
            ground=GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            ),
        )
        self.set_parameters(initial)
        self._update_ground_controls()
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

    def load_starting_dimensions(self) -> None:
        from ...domain.design.formulas import quarter_wave_length_m

        current = self.parameters()
        quarter = quarter_wave_length_m(current.frequency_hz)
        self.set_parameters(
            phased_vertical_parameters(
                frequency_hz=current.frequency_hz,
                element_count=current.element_count,
                height_m=quarter,
                spacing_m=quarter,
                base_height_m=current.base_height_m,
                phase_step_deg=current.phase_step_deg,
                amplitude_taper=current.amplitude_taper,
                radial_count=current.radial_count,
                radial_length_m=quarter,
                radial_angle_deg=current.radial_angle_deg,
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
                self._spacing,
                self._height,
                self._base_height,
                self._radial_length,
            )
            self._spacing.setRange(minimum_length, maximum_length)
            self._radial_length.setRange(minimum_length, maximum_length)
            self._height.setRange(minimum_height, maximum_height)
            self._base_height.setRange(minimum_height, maximum_height)
        finally:
            self._updating = previous_updating
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: PhasedVerticalParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._element_count.setValue(parameters.element_count)
            self._spacing.setValue(length_from_m(parameters.spacing_m, self._unit_system))
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
            self._base_height.setValue(length_from_m(parameters.base_height_m, self._unit_system))
            self._phase_step.setValue(parameters.phase_step_deg)
            self._amplitude_taper.setValue(parameters.amplitude_taper)
            self._radial_count.setValue(parameters.radial_count)
            self._radial_length.setValue(
                length_from_m(parameters.radial_length_m, self._unit_system)
            )
            self._radial_angle.setValue(parameters.radial_angle_deg)
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
            self._overlap_warning.setVisible(False)
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "phased_vertical.geometry",
                count=parameters.element_count,
                spacing=f"{length_from_m(parameters.spacing_m, self._unit_system):.3f}",
                height=f"{length_from_m(parameters.height_m, self._unit_system):.3f}",
                phase=f"{parameters.phase_step_deg:.1f}",
                taper=parameters.amplitude_taper * 100.0,
                radials=parameters.radial_count,
                unit=unit,
            )
        )
        self._overlap_warning.setText(self._translator.t("phased_vertical.radial_overlap_warning"))
        self._overlap_warning.setVisible(parameters.radial_screen_overlap)

    def parameters(self) -> PhasedVerticalParameters:
        return PhasedVerticalParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            height_m=length_to_m(self._height.value(), self._unit_system),
            spacing_m=length_to_m(self._spacing.value(), self._unit_system),
            element_count=self._element_count.value(),
            base_height_m=length_to_m(
                self._base_height.value(),
                self._unit_system,
            ),
            phase_step_deg=self._phase_step.value(),
            amplitude_taper=self._amplitude_taper.value(),
            radial_count=self._radial_count.value(),
            radial_length_m=length_to_m(
                self._radial_length.value(),
                self._unit_system,
            ),
            radial_angle_deg=self._radial_angle.value(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
