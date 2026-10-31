# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for J-pole and Slim-Jim verticals."""

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

from ...domain.antennas.j_pole import JPoleParameters
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key

MATERIALS = (COPPER, ALUMINUM)


class JPoleForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: JPoleParameters | None = None,
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
        self._frequency.setValue(145.0)

        self._radiator_height = QDoubleSpinBox(self)
        self._radiator_height.setDecimals(3)
        self._radiator_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._radiator_height.setValue(length_from_m(1.0, unit_system))

        self._stub_length = QDoubleSpinBox(self)
        self._stub_length.setDecimals(3)
        self._stub_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._stub_length.setValue(length_from_m(0.5, unit_system))

        self._spacing = QDoubleSpinBox(self)
        self._spacing.setDecimals(3)
        self._spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._spacing.setValue(length_from_m(0.05, unit_system))

        self._feed_offset = QDoubleSpinBox(self)
        self._feed_offset.setDecimals(3)
        self._feed_offset.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._feed_offset.setValue(length_from_m(0.1, unit_system))

        self._gap = QDoubleSpinBox(self)
        self._gap.setDecimals(3)
        self._gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._gap.setValue(length_from_m(0.01, unit_system))

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._base_height.setValue(length_from_m(0.25, unit_system))

        self._folded = QCheckBox(translator.t("j_pole.folded"), self)

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
        form.addRow(translator.t("j_pole.radiator_height"), self._radiator_height)
        form.addRow(translator.t("j_pole.stub_length"), self._stub_length)
        form.addRow(translator.t("j_pole.spacing"), self._spacing)
        form.addRow(translator.t("j_pole.feed_offset"), self._feed_offset)
        form.addRow(translator.t("j_pole.gap"), self._gap)
        form.addRow(translator.t("j_pole.base_height"), self._base_height)
        form.addRow(self._folded)
        form.addRow(translator.t("j_pole.wire_radius"), self._radius)
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
            self._stub_length,
            self._spacing,
            self._feed_offset,
            self._gap,
            self._base_height,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._folded.toggled.connect(self._emit_changed)
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

    def set_parameters(self, parameters: JPoleParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._radiator_height.setValue(
                length_from_m(parameters.radiator_height_m, self._unit_system)
            )
            self._stub_length.setValue(length_from_m(parameters.stub_length_m, self._unit_system))
            self._spacing.setValue(length_from_m(parameters.spacing_m, self._unit_system))
            self._feed_offset.setValue(length_from_m(parameters.feed_offset_m, self._unit_system))
            self._base_height.setValue(length_from_m(parameters.base_height_m, self._unit_system))
            self._folded.setChecked(parameters.folded)
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
                "j_pole.geometry",
                template=parameters.template_name,
                height=f"{length_from_m(parameters.radiator_height_m, self._unit_system):.2f}",
                unit=unit,
            )
        )

    def parameters(self) -> JPoleParameters:
        return JPoleParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            radiator_height_m=length_to_m(self._radiator_height.value(), self._unit_system),
            stub_length_m=length_to_m(self._stub_length.value(), self._unit_system),
            spacing_m=length_to_m(self._spacing.value(), self._unit_system),
            feed_offset_m=length_to_m(self._feed_offset.value(), self._unit_system),
            gap_m=length_to_m(self._gap.value(), self._unit_system),
            base_height_m=length_to_m(self._base_height.value(), self._unit_system),
            folded=self._folded.isChecked(),
            wire_radius_m=self._radius.value() / 1_000.0,
            material=self._selected_material(),
            ground=self._ground_model(),
        )
