# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a two-band trap dipole."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.dipole import DipoleOrientation
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.trap_dipole import TrapDipoleParameters
from ...domain.design.formulas import half_wave_length_m
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
from .ground_presets import GroundPresetController

MATERIALS = (COPPER, ALUMINUM)
DEFAULT_LOW_BAND_HZ = 7_100_000.0
DEFAULT_HIGH_BAND_HZ = 14_100_000.0
DEFAULT_TRAP_INDUCTANCE_H = 10e-6


class TrapDipoleForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: TrapDipoleParameters | None = None,
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
        self._frequency.setValue(DEFAULT_LOW_BAND_HZ / 1_000_000.0)

        self._high_band = QDoubleSpinBox(self)
        self._high_band.setRange(0.1, 100_000.0)
        self._high_band.setDecimals(6)
        self._high_band.setSuffix(" MHz")
        self._high_band.setValue(DEFAULT_HIGH_BAND_HZ / 1_000_000.0)

        self._inner_length = QDoubleSpinBox(self)
        self._inner_length.setDecimals(3)
        self._inner_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._outer_length = QDoubleSpinBox(self)
        self._outer_length.setDecimals(3)
        self._outer_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._start = QPushButton(translator.t("trap_dipole.starting_dimensions"), self)

        self._trap_frequency = QDoubleSpinBox(self)
        self._trap_frequency.setRange(0.1, 100_000.0)
        self._trap_frequency.setDecimals(6)
        self._trap_frequency.setSuffix(" MHz")
        self._trap_frequency.setValue(DEFAULT_HIGH_BAND_HZ / 1_000_000.0)

        self._trap_inductance = QDoubleSpinBox(self)
        self._trap_inductance.setRange(0.001, 100_000.0)
        self._trap_inductance.setDecimals(3)
        self._trap_inductance.setSuffix(" µH")
        self._trap_inductance.setValue(DEFAULT_TRAP_INDUCTANCE_H * 1e6)

        self._trap_capacitance = QLabel(self)

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(10.0, unit_system))
        self._height_label = QLabel(translator.t("field.height"), self)

        self._orientation = QComboBox(self)
        self._orientation.addItem(
            translator.t("orientation.horizontal"),
            DipoleOrientation.HORIZONTAL.value,
        )
        self._orientation.addItem(
            translator.t("orientation.vertical"),
            DipoleOrientation.VERTICAL.value,
        )

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
        self._soil = QComboBox(self)
        self._ground_presets = GroundPresetController(
            self._ground,
            self._soil,
            self._permittivity,
            self._conductivity,
            translator,
        )

        self._trap_warning = QLabel(self)
        self._trap_warning.setWordWrap(True)
        self._trap_warning.setStyleSheet("font-style: italic;")
        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        form = QFormLayout()
        form.addRow(self._labels.label("trap_dipole.low_band"), self._frequency)
        form.addRow(self._labels.label("trap_dipole.high_band"), self._high_band)
        form.addRow(self._labels.label("trap_dipole.inner_length"), self._inner_length)
        form.addRow(self._labels.label("trap_dipole.outer_length"), self._outer_length)
        form.addRow(self._start)
        form.addRow(self._labels.label("trap_dipole.trap_frequency"), self._trap_frequency)
        form.addRow(self._labels.label("trap_dipole.trap_inductance"), self._trap_inductance)
        form.addRow(self._labels.label("trap_dipole.trap_capacitance"), self._trap_capacitance)
        form.addRow(self._height_label, self._height)
        form.addRow(self._labels.label("field.orientation"), self._orientation)
        form.addRow(self._labels.label("field.azimuth"), self._azimuth)
        form.addRow(self._labels.label("trap_dipole.wire_radius"), self._radius)
        form.addRow(self._labels.label("field.material"), self._material)
        form.addRow(self._labels.label("field.ground"), self._ground)
        form.addRow(self._labels.label("field.soil_preset"), self._soil)
        form.addRow(self._labels.label("field.permittivity"), self._permittivity)
        form.addRow(self._labels.label("field.conductivity"), self._conductivity)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(form)
        layout.addWidget(self._trap_warning)
        layout.addWidget(self._geometry)

        for widget in (
            self._frequency,
            self._high_band,
            self._inner_length,
            self._outer_length,
            self._trap_frequency,
            self._trap_inductance,
            self._height,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._orientation.currentIndexChanged.connect(self._orientation_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        self._start.clicked.connect(self._apply_starting_dimensions)

        if parameters is not None:
            self.set_parameters(parameters)
        else:
            self._set_starting_dimensions()
        self._update_ground_controls()
        self._update_orientation_controls()
        self._update_band_controls()
        self._update_geometry()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self._update_band_controls()
            self._update_geometry()
            self.changed.emit()

    def _orientation_changed(self, *_args: object) -> None:
        self._update_orientation_controls()
        self._emit_changed()

    def _ground_changed(self, *_args: object) -> None:
        self._update_ground_controls()
        self._emit_changed()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        self._start.setText(self._translator.t("trap_dipole.starting_dimensions"))
        retranslate_combo(
            self._orientation,
            self._translator,
            ("orientation.horizontal", "orientation.vertical"),
        )
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
        self._update_orientation_controls()
        self._update_band_controls()
        self._update_geometry()

    def _update_ground_controls(self) -> None:
        finite = self._ground.currentData() == GroundKind.FINITE.value
        self._permittivity.setEnabled(finite)
        self._conductivity.setEnabled(finite)

    def _update_orientation_controls(self) -> None:
        horizontal = self._orientation.currentData() == DipoleOrientation.HORIZONTAL.value
        self._azimuth.setEnabled(horizontal)
        self._height_label.setText(
            self._translator.t("field.height" if horizontal else "field.base_height")
        )

    def _update_band_controls(self) -> None:
        low_hz = self._frequency.value() * 1_000_000.0
        high_hz = self._high_band.value() * 1_000_000.0
        self._start.setEnabled(high_hz > low_hz)
        trap_hz = self._trap_frequency.value() * 1_000_000.0
        below = trap_hz < high_hz
        self._trap_warning.setText(
            self._translator.t("trap_dipole.trap_below_high_band") if below else ""
        )

    def _set_starting_dimensions(self) -> None:
        low_hz = self._frequency.value() * 1_000_000.0
        high_hz = self._high_band.value() * 1_000_000.0
        if high_hz <= low_hz:
            return
        inner = half_wave_length_m(high_hz)
        total = half_wave_length_m(low_hz)
        outer = max((total - inner) / 2.0, 0.01)
        self._inner_length.setValue(length_from_m(inner, self._unit_system))
        self._outer_length.setValue(length_from_m(outer, self._unit_system))
        self._trap_frequency.setValue(high_hz / 1_000_000.0)

    def _apply_starting_dimensions(self) -> None:
        self._set_starting_dimensions()
        self._update_band_controls()
        self._update_geometry()
        if not self._updating:
            self.changed.emit()

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

    def _selected_orientation(self) -> DipoleOrientation:
        value = self._orientation.currentData()
        return DipoleOrientation(value) if isinstance(value, str) else DipoleOrientation.HORIZONTAL

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
            self._inner_length,
            self._outer_length,
            self._height,
        )
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: TrapDipoleParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._high_band.setValue(parameters.high_band_frequency_hz / 1_000_000.0)
            self._inner_length.setValue(length_from_m(parameters.inner_length_m, self._unit_system))
            self._outer_length.setValue(length_from_m(parameters.outer_length_m, self._unit_system))
            self._trap_frequency.setValue(parameters.trap_frequency_hz / 1_000_000.0)
            self._trap_inductance.setValue(parameters.trap_inductance_h * 1e6)
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
            orientation_index = self._orientation.findData(parameters.orientation.value)
            if orientation_index >= 0:
                self._orientation.setCurrentIndex(orientation_index)
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
        self._update_orientation_controls()
        self._update_band_controls()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._frequency.setValue(frequency_hz / 1_000_000.0)
        if self._high_band.value() <= self._frequency.value():
            self._high_band.setValue(self._frequency.value() * 2.0)
        self._apply_starting_dimensions()

    def _update_geometry(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            self._trap_capacitance.setText("—")
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        left, right = parameters.trap_positions_m
        self._trap_capacitance.setText(f"{parameters.trap_capacitance_f * 1e12:.3f} pF")
        self._geometry.setText(
            self._translator.t(
                "trap_dipole.geometry",
                total=f"{length_from_m(parameters.total_length_m, self._unit_system):.3f}",
                inner=f"{length_from_m(parameters.inner_length_m, self._unit_system):.3f}",
                left=f"{length_from_m(left, self._unit_system):.3f}",
                right=f"{length_from_m(right, self._unit_system):.3f}",
                unit=unit,
            )
        )

    def parameters(self) -> TrapDipoleParameters:
        return TrapDipoleParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            high_band_frequency_hz=self._high_band.value() * 1_000_000.0,
            inner_length_m=length_to_m(self._inner_length.value(), self._unit_system),
            outer_length_m=length_to_m(self._outer_length.value(), self._unit_system),
            trap_frequency_hz=self._trap_frequency.value() * 1_000_000.0,
            trap_inductance_h=self._trap_inductance.value() * 1e-6,
            height_m=length_to_m(self._height.value(), self._unit_system),
            orientation=self._selected_orientation(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
