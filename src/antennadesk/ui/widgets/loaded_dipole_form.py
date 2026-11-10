# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for the loaded/linked dipole."""

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

from ...domain.antennas.dipole import DipoleOrientation
from ...domain.antennas.loaded_dipole import (
    LoadedDipoleParameters,
    loaded_dipole_parameters,
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


class LoadedDipoleForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: LoadedDipoleParameters | None = None,
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

        self._orientation = QComboBox(self)
        self._orientation.addItem("", DipoleOrientation.HORIZONTAL.value)
        self._orientation.addItem("", DipoleOrientation.VERTICAL.value)

        self._total_length = QDoubleSpinBox(self)
        self._total_length.setRange(minimum_length, maximum_length)
        self._total_length.setDecimals(3)
        self._total_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._height = QDoubleSpinBox(self)
        self._height.setRange(minimum_height, maximum_height)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._link_open = QCheckBox(translator.t("loaded_dipole.link_open"), self)
        self._link_offset = QDoubleSpinBox(self)
        self._link_offset.setRange(minimum_length, maximum_length)
        self._link_offset.setDecimals(3)
        self._link_offset.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._coil_enabled = QCheckBox(
            translator.t("loaded_dipole.coil_enabled"),
            self,
        )
        self._inductance = QDoubleSpinBox(self)
        self._inductance.setRange(0.0, 1_000_000.0)
        self._inductance.setDecimals(3)
        self._inductance.setSuffix(" µH")
        self._coil_resistance = QDoubleSpinBox(self)
        self._coil_resistance.setRange(0.0, 10_000.0)
        self._coil_resistance.setDecimals(3)
        self._coil_resistance.setSuffix(" Ω")

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
        form.addRow(self._labels.label("field.orientation"), self._orientation)
        form.addRow(self._labels.label("field.length"), self._total_length)
        form.addRow(self._labels.label("field.height"), self._height)
        form.addRow(self._link_open)
        form.addRow(self._labels.label("loaded_dipole.link_offset"), self._link_offset)
        form.addRow(self._coil_enabled)
        form.addRow(self._labels.label("loaded_dipole.coil_inductance"), self._inductance)
        form.addRow(self._labels.label("loaded_dipole.coil_resistance"), self._coil_resistance)
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
            self._total_length,
            self._height,
            self._link_offset,
            self._inductance,
            self._coil_resistance,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        for combo in (self._orientation, self._material):
            combo.currentIndexChanged.connect(self._emit_changed)
        self._link_open.toggled.connect(self._link_toggled)
        self._coil_enabled.toggled.connect(self._coil_toggled)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        initial = parameters or loaded_dipole_parameters(
            frequency_hz=7_100_000.0,
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
        self._orientation.setItemText(0, self._translator.t("orientation.horizontal"))
        self._orientation.setItemText(1, self._translator.t("orientation.vertical"))
        self._link_open.setText(self._translator.t("loaded_dipole.link_open"))
        self._coil_enabled.setText(self._translator.t("loaded_dipole.coil_enabled"))
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

    def _link_toggled(self, *_args: object) -> None:
        self._update_link_controls()
        self._emit_changed()

    def _coil_toggled(self, *_args: object) -> None:
        self._update_link_controls()
        self._emit_changed()

    def _update_link_controls(self) -> None:
        link_open = self._link_open.isChecked()
        coil_enabled = self._coil_enabled.isChecked() and not link_open
        self._total_length.setEnabled(not link_open)
        self._inductance.setEnabled(coil_enabled)
        self._coil_resistance.setEnabled(coil_enabled)

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
        minimum_length, maximum_length = length_bounds(unit_system)
        minimum_height, maximum_height = height_bounds(unit_system)
        previous_updating = self._updating
        self._updating = True
        try:
            apply_radius_units(self._translator, unit_system, self._radius)
            apply_length_suffixes(
                self._translator,
                unit_system,
                self._total_length,
                self._height,
                self._link_offset,
            )
            for box in (self._total_length, self._link_offset):
                box.setRange(minimum_length, maximum_length)
            self._height.setRange(minimum_height, maximum_height)
        finally:
            self._updating = previous_updating
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: LoadedDipoleParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            orientation_index = self._orientation.findData(parameters.orientation.value)
            if orientation_index >= 0:
                self._orientation.setCurrentIndex(orientation_index)
            self._total_length.setValue(length_from_m(parameters.total_length_m, self._unit_system))
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
            self._link_open.setChecked(parameters.link_open)
            self._link_offset.setValue(length_from_m(parameters.link_offset_m, self._unit_system))
            self._coil_enabled.setChecked(parameters.loading_coil_enabled)
            self._inductance.setValue(parameters.loading_coil_inductance_h * 1e6)
            self._coil_resistance.setValue(parameters.loading_coil_resistance_ohm)
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
        self._update_link_controls()
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
        if parameters.link_open:
            state = self._translator.t("loaded_dipole.state_linked")
        elif parameters.coil_active:
            q_value = parameters.coil_q
            state = self._translator.t(
                "loaded_dipole.state_loaded",
                inductance=parameters.loading_coil_inductance_h * 1e6,
                q="—" if q_value is None else f"{q_value:.1f}",
            )
        else:
            state = self._translator.t("loaded_dipole.state_plain")
        self._geometry.setText(
            self._translator.t(
                "loaded_dipole.geometry",
                active=f"{length_from_m(parameters.active_length_m, self._unit_system):.3f}",
                total=f"{length_from_m(parameters.total_length_m, self._unit_system):.3f}",
                offset=f"{length_from_m(parameters.link_offset_m, self._unit_system):.3f}",
                state=state,
                unit=unit,
            )
        )

    def parameters(self) -> LoadedDipoleParameters:
        return LoadedDipoleParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            total_length_m=length_to_m(
                self._total_length.value(),
                self._unit_system,
            ),
            height_m=length_to_m(self._height.value(), self._unit_system),
            link_offset_m=length_to_m(
                self._link_offset.value(),
                self._unit_system,
            ),
            link_open=self._link_open.isChecked(),
            loading_coil_enabled=self._coil_enabled.isChecked(),
            loading_coil_inductance_h=self._inductance.value() * 1e-6,
            loading_coil_resistance_ohm=self._coil_resistance.value(),
            orientation=DipoleOrientation(self._orientation.currentData()),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
