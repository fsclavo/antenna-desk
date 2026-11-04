# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for an end-fed wire."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.endfed import EndFedParameters, EndFedPreset
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.design.formulas import half_wave_length_m
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key

MATERIALS = (COPPER, ALUMINUM)


class EndFedForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: EndFedParameters | None = None,
        parent: QWidget | None = None,
        *,
        preset: EndFedPreset = EndFedPreset.STANDARD,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._updating = False
        self._preset = EndFedPreset(preset)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(7.1)

        self._length = QDoubleSpinBox(self)
        self._length.setDecimals(3)
        self._length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._length.setValue(length_from_m(20.0, unit_system))

        self._feed_height = QDoubleSpinBox(self)
        self._feed_height.setDecimals(3)
        self._feed_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._feed_height.setValue(length_from_m(10.0, unit_system))

        self._end_height = QDoubleSpinBox(self)
        self._end_height.setDecimals(3)
        self._end_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._end_height.setValue(length_from_m(10.0, unit_system))

        self._transformer = QDoubleSpinBox(self)
        self._transformer.setRange(1.0, 100_000.0)
        self._transformer.setDecimals(1)
        self._transformer.setValue(49.0)
        self._transformer.setSuffix(":1")

        self._counterpoise_enabled = QCheckBox(translator.t("endfed.counterpoise_enabled"), self)
        self._counterpoise_enabled.setChecked(False)

        self._counterpoise_length = QDoubleSpinBox(self)
        self._counterpoise_length.setRange(0.0, 100_000.0)
        self._counterpoise_length.setDecimals(3)
        self._counterpoise_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._counterpoise_length.setValue(0.0)

        self._counterpoise_height = QDoubleSpinBox(self)
        self._counterpoise_height.setRange(0.0, 100_000.0)
        self._counterpoise_height.setDecimals(3)
        self._counterpoise_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._counterpoise_height.setValue(length_from_m(0.1, unit_system))

        self._counterpoise_azimuth = QDoubleSpinBox(self)
        self._counterpoise_azimuth.setRange(0.0, 360.0)
        self._counterpoise_azimuth.setDecimals(1)
        self._counterpoise_azimuth.setSuffix("°")
        self._counterpoise_azimuth.setValue(180.0)

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

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

        self._preset_label = QLabel(self)
        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        if parameters is None:
            self._apply_preset_defaults()

        form = QFormLayout()
        form.addRow(translator.t("field.template"), self._preset_label)
        form.addRow(translator.t("field.design_frequency"), self._frequency)
        form.addRow(translator.t("field.length"), self._length)
        form.addRow(translator.t("endfed.feed_height"), self._feed_height)
        form.addRow(translator.t("endfed.end_height"), self._end_height)
        form.addRow(translator.t("endfed.transformer_ratio"), self._transformer)
        form.addRow(self._counterpoise_enabled)
        form.addRow(translator.t("endfed.counterpoise_length"), self._counterpoise_length)
        form.addRow(translator.t("endfed.counterpoise_height"), self._counterpoise_height)
        form.addRow(
            translator.t("endfed.counterpoise_azimuth"),
            self._counterpoise_azimuth,
        )
        form.addRow(translator.t("field.azimuth"), self._azimuth)
        form.addRow(translator.t("endfed.wire_radius"), self._radius)
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
            self._length,
            self._feed_height,
            self._end_height,
            self._transformer,
            self._counterpoise_length,
            self._counterpoise_height,
            self._counterpoise_azimuth,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        self._counterpoise_length.valueChanged.connect(self._counterpoise_changed)
        self._counterpoise_enabled.toggled.connect(self._counterpoise_toggled)
        if parameters is not None:
            self.set_parameters(parameters)
        else:
            self._update_preset_label()
        self._update_ground_controls()
        self._update_counterpoise_controls()
        self._update_geometry()

    def _update_preset_label(self) -> None:
        self._preset_label.setText(self._translator.t(f"endfed.preset.{self._preset.value}"))

    def _apply_preset_defaults(self) -> None:
        if self._preset is EndFedPreset.STANDARD:
            self._update_preset_label()
            return
        frequency_hz = self._frequency.value() * 1_000_000.0
        wavelength_m = 299_792_458.0 / frequency_hz
        if self._preset is EndFedPreset.SLOPER:
            length_m = half_wave_length_m(frequency_hz)
            feed_height_m = 10.0
            end_height_m = max(feed_height_m - min(0.5 * length_m, feed_height_m - 0.5), 0.5)
            self._transformer.setValue(49.0)
        else:
            length_m = 17.0
            feed_height_m = 10.0
            end_height_m = 10.0
            self._transformer.setValue(9.0)
        self._length.setValue(length_from_m(length_m, self._unit_system))
        self._feed_height.setValue(length_from_m(feed_height_m, self._unit_system))
        self._end_height.setValue(length_from_m(end_height_m, self._unit_system))
        self._counterpoise_enabled.setChecked(True)
        self._counterpoise_length.setValue(length_from_m(0.05 * wavelength_m, self._unit_system))
        self._update_preset_label()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _ground_changed(self, *_args: object) -> None:
        self._update_ground_controls()
        self._emit_changed()

    def _counterpoise_changed(self, *_args: object) -> None:
        self._update_counterpoise_controls()

    def _counterpoise_toggled(self, checked: bool) -> None:
        if checked and self._counterpoise_length.value() <= 0.0:
            wavelength = 299.792458 / self._frequency.value()
            self._counterpoise_length.setValue(length_from_m(0.05 * wavelength, self._unit_system))
        self._update_counterpoise_controls()
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _update_counterpoise_controls(self) -> None:
        enabled = self._counterpoise_enabled.isChecked()
        self._counterpoise_length.setEnabled(enabled)
        self._counterpoise_height.setEnabled(enabled)
        self._counterpoise_azimuth.setEnabled(enabled)

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

    def set_parameters(self, parameters: EndFedParameters) -> None:
        self._updating = True
        try:
            self._preset = parameters.preset
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._length.setValue(length_from_m(parameters.length_m, self._unit_system))
            self._feed_height.setValue(length_from_m(parameters.feed_height_m, self._unit_system))
            self._end_height.setValue(length_from_m(parameters.end_height_m, self._unit_system))
            self._transformer.setValue(parameters.transformer_ratio)
            self._counterpoise_enabled.setChecked(parameters.counterpoise_length_m > 0.0)
            self._counterpoise_length.setValue(
                length_from_m(parameters.counterpoise_length_m, self._unit_system)
            )
            self._counterpoise_height.setValue(
                length_from_m(parameters.counterpoise_height_m, self._unit_system)
            )
            counterpoise_azimuth = parameters.counterpoise_azimuth_deg
            if counterpoise_azimuth is None:
                counterpoise_azimuth = parameters.effective_counterpoise_azimuth_deg
            self._counterpoise_azimuth.setValue(counterpoise_azimuth)
            self._azimuth.setValue(parameters.azimuth_deg)
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
        self._update_preset_label()
        self._update_ground_controls()
        self._update_counterpoise_controls()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._frequency.setValue(frequency_hz / 1_000_000.0)
        if self._preset is not EndFedPreset.STANDARD:
            self._apply_preset_defaults()

    def _update_geometry(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        counterpoise = (
            f"{length_from_m(parameters.counterpoise_length_m, self._unit_system):.2f} {unit}"
            if parameters.counterpoise_length_m > 0.0
            else "none"
        )
        self._geometry.setText(
            self._translator.t(
                "endfed.geometry",
                feed=f"{length_from_m(parameters.feed_height_m, self._unit_system):.2f}",
                end=f"{length_from_m(parameters.end_height_m, self._unit_system):.2f}",
                counterpoise=counterpoise,
                ratio=f"{parameters.transformer_ratio:g}",
                unit=unit,
            )
        )

    def parameters(self) -> EndFedParameters:
        return EndFedParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            length_m=length_to_m(self._length.value(), self._unit_system),
            feed_height_m=length_to_m(self._feed_height.value(), self._unit_system),
            end_height_m=length_to_m(self._end_height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=self._radius.value() / 1_000.0,
            material=self._selected_material(),
            ground=self._ground_model(),
            transformer_ratio=self._transformer.value(),
            counterpoise_length_m=(
                length_to_m(self._counterpoise_length.value(), self._unit_system)
                if self._counterpoise_enabled.isChecked()
                else 0.0
            ),
            counterpoise_height_m=length_to_m(self._counterpoise_height.value(), self._unit_system),
            counterpoise_azimuth_deg=self._counterpoise_azimuth.value(),
            preset=self._preset,
        )
