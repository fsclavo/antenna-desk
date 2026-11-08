# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for single-band hexbeams."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.hexbeam import (
    HexbeamParameters,
    published_hexbeam_parameters,
)
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
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


class HexbeamForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: HexbeamParameters | None = None,
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

        self._driver_half = QDoubleSpinBox(self)
        self._driver_half.setRange(minimum_length, maximum_length)
        self._driver_half.setDecimals(3)
        self._driver_half.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._reflector_half = QDoubleSpinBox(self)
        self._reflector_half.setRange(minimum_length, maximum_length)
        self._reflector_half.setDecimals(3)
        self._reflector_half.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._turning_radius = QDoubleSpinBox(self)
        self._turning_radius.setRange(minimum_length, maximum_length)
        self._turning_radius.setDecimals(3)
        self._turning_radius.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._tip_gap = QDoubleSpinBox(self)
        self._tip_gap.setRange(minimum_length, maximum_length)
        self._tip_gap.setDecimals(3)
        self._tip_gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._height = QDoubleSpinBox(self)
        self._height.setRange(minimum_height, maximum_height)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._feed_gap = QDoubleSpinBox(self)
        self._feed_gap.setRange(minimum_length, maximum_length)
        self._feed_gap.setDecimals(4)
        self._feed_gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._element_separation = QDoubleSpinBox(self)
        self._element_separation.setRange(0.0, maximum_length)
        self._element_separation.setDecimals(4)
        self._element_separation.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

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
        form.addRow(self._labels.label("hexbeam.driver_half"), self._driver_half)
        form.addRow(self._labels.label("hexbeam.reflector_half"), self._reflector_half)
        form.addRow(self._labels.label("hexbeam.turning_radius"), self._turning_radius)
        form.addRow(self._labels.label("hexbeam.tip_gap"), self._tip_gap)
        form.addRow(self._labels.label("field.height"), self._height)
        form.addRow(self._labels.label("hexbeam.feed_gap"), self._feed_gap)
        form.addRow(
            self._labels.label("hexbeam.element_separation"),
            self._element_separation,
        )
        form.addRow(self._labels.label("field.azimuth"), self._azimuth)
        form.addRow(self._labels.label("field.wire_radius"), self._radius)
        form.addRow(self._labels.label("field.material"), self._material)
        form.addRow(self._labels.label("field.ground"), self._ground)
        form.addRow(self._labels.label("field.soil_preset"), self._soil)
        form.addRow(self._labels.label("field.permittivity"), self._permittivity)
        form.addRow(self._labels.label("field.conductivity"), self._conductivity)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(form)
        layout.addWidget(self._geometry)

        for widget in (
            self._frequency,
            self._driver_half,
            self._reflector_half,
            self._turning_radius,
            self._tip_gap,
            self._height,
            self._feed_gap,
            self._element_separation,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        initial = parameters or published_hexbeam_parameters(
            ground=GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            )
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
        current = self.parameters()
        self.set_parameters(
            published_hexbeam_parameters(
                frequency_hz=current.frequency_hz,
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
                self._driver_half,
                self._reflector_half,
                self._turning_radius,
                self._tip_gap,
                self._height,
                self._feed_gap,
                self._element_separation,
            )
            for spin in (
                self._driver_half,
                self._reflector_half,
                self._turning_radius,
                self._tip_gap,
                self._feed_gap,
            ):
                spin.setRange(minimum_length, maximum_length)
            self._element_separation.setRange(0.0, maximum_length)
            self._height.setRange(minimum_height, maximum_height)
        finally:
            self._updating = previous_updating
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: HexbeamParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._driver_half.setValue(
                length_from_m(parameters.driver_half_length_m, self._unit_system)
            )
            self._reflector_half.setValue(
                length_from_m(parameters.reflector_half_length_m, self._unit_system)
            )
            self._turning_radius.setValue(
                length_from_m(parameters.turning_radius_m, self._unit_system)
            )
            self._tip_gap.setValue(length_from_m(parameters.tip_gap_m, self._unit_system))
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
            self._feed_gap.setValue(length_from_m(parameters.feed_gap_m, self._unit_system))
            self._element_separation.setValue(
                length_from_m(parameters.element_separation_m, self._unit_system)
            )
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
        driver = length_from_m(parameters.driver_half_length_m, self._unit_system)
        reflector = length_from_m(parameters.reflector_half_length_m, self._unit_system)
        span = length_from_m(parameters.overall_span_m, self._unit_system)
        radius = length_from_m(parameters.turning_radius_m, self._unit_system)
        self._geometry.setText(
            self._translator.t(
                "hexbeam.geometry",
                driver=f"{driver:.3f}",
                reflector=f"{reflector:.3f}",
                span=f"{span:.3f}",
                radius=f"{radius:.3f}",
                unit=unit,
            )
        )

    def parameters(self) -> HexbeamParameters:
        return HexbeamParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            driver_half_length_m=length_to_m(self._driver_half.value(), self._unit_system),
            reflector_half_length_m=length_to_m(self._reflector_half.value(), self._unit_system),
            turning_radius_m=length_to_m(self._turning_radius.value(), self._unit_system),
            tip_gap_m=length_to_m(self._tip_gap.value(), self._unit_system),
            height_m=length_to_m(self._height.value(), self._unit_system),
            feed_gap_m=length_to_m(self._feed_gap.value(), self._unit_system),
            element_separation_m=length_to_m(self._element_separation.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
