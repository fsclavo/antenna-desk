# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for an off-center-fed dipole."""

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

from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.ocfd import OCFD_REFERENCE_TRANSFORMER_RATIO, OCFDParameters
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import (
    UnitSystem,
    length_from_m,
    length_to_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
)
from .form_i18n import FormLabels, retranslate_combo
from .form_units import apply_length_suffixes, apply_radius_units

MATERIALS = (COPPER, ALUMINUM)


class OCFDForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: OCFDParameters | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self)
        self._unit_system = unit_system
        self._updating = False

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(7.1)

        self._length = QDoubleSpinBox(self)
        self._length.setDecimals(3)
        self._length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._length.setValue(length_from_m(20.0, unit_system))

        self._feed_ratio = QDoubleSpinBox(self)
        self._feed_ratio.setRange(1.0, 99.0)
        self._feed_ratio.setDecimals(1)
        self._feed_ratio.setSuffix(" %")
        self._feed_ratio.setValue(33.3)

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(10.0, unit_system))

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)
        self._radius.setValue(radius_from_m(0.001, unit_system))

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

        self._transformer = QDoubleSpinBox(self)
        self._transformer.setRange(1.0, 100_000.0)
        self._transformer.setDecimals(1)
        self._transformer.setSuffix(":1")
        self._transformer.setValue(OCFD_REFERENCE_TRANSFORMER_RATIO)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)
        self._transformer_hint = QLabel(translator.t("ocfd.transformer_hint"), self)
        self._transformer_hint.setWordWrap(True)

        form = QFormLayout()
        form.addRow(self._labels.label("field.fundamental_frequency"), self._frequency)
        form.addRow(self._labels.label("field.length"), self._length)
        form.addRow(self._labels.label("ocfd.feed_offset"), self._feed_ratio)
        form.addRow(self._labels.label("field.height"), self._height)
        form.addRow(self._labels.label("field.azimuth"), self._azimuth)
        form.addRow(self._labels.label("ocfd.wire_radius"), self._radius)
        form.addRow(self._labels.label("field.material"), self._material)
        form.addRow(self._labels.label("field.ground"), self._ground)
        form.addRow(self._labels.label("field.permittivity"), self._permittivity)
        form.addRow(self._labels.label("field.conductivity"), self._conductivity)
        form.addRow(self._labels.label("ocfd.transformer_ratio"), self._transformer)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(form)
        layout.addWidget(self._transformer_hint)
        layout.addWidget(self._geometry)

        for widget in (
            self._frequency,
            self._length,
            self._feed_ratio,
            self._height,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
            self._transformer,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        if parameters is not None:
            self.set_parameters(parameters)
        self._update_ground_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._labels.retranslate()
        self._transformer_hint.setText(self._translator.t("ocfd.transformer_hint"))
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

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            parameters = None
        self._unit_system = unit_system
        apply_radius_units(self._translator, unit_system, self._radius)
        apply_length_suffixes(
            self._translator,
            unit_system,
            self._length,
            self._height,
        )
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: OCFDParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._length.setValue(length_from_m(parameters.total_length_m, self._unit_system))
            self._feed_ratio.setValue(parameters.feed_ratio * 100.0)
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
            self._azimuth.setValue(parameters.azimuth_deg)
            self._radius.setValue(radius_from_m(parameters.wire_radius_m, self._unit_system))
            self._transformer.setValue(parameters.transformer_ratio)
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
                "ocfd.geometry",
                offset=f"{length_from_m(parameters.feed_offset_m, self._unit_system):.3f}",
                unit=unit,
                total=f"{length_from_m(parameters.total_length_m, self._unit_system):.3f}",
            )
        )

    def parameters(self) -> OCFDParameters:
        return OCFDParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            total_length_m=length_to_m(self._length.value(), self._unit_system),
            feed_ratio=self._feed_ratio.value() / 100.0,
            height_m=length_to_m(self._height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
            transformer_ratio=self._transformer.value(),
        )
