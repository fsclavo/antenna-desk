# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a terminated folded dipole (T2FD)."""

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
from ...domain.antennas.t2fd import (
    DEFAULT_T2FD_HEIGHT_M,
    DEFAULT_T2FD_TERMINATION_OHM,
    DEFAULT_T2FD_TRANSFORMER_RATIO,
    T2FDParameters,
    t2fd_starting_dimensions,
)
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key

MATERIALS = (COPPER, ALUMINUM)
DEFAULT_LOWEST_FREQUENCY_HZ = 3_500_000.0
DEFAULT_HIGHEST_FREQUENCY_HZ = 30_000_000.0


class T2FDForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: T2FDParameters | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._updating = False

        self._lowest_frequency = QDoubleSpinBox(self)
        self._lowest_frequency.setRange(0.1, 100_000.0)
        self._lowest_frequency.setDecimals(6)
        self._lowest_frequency.setSuffix(" MHz")
        self._lowest_frequency.setValue(DEFAULT_LOWEST_FREQUENCY_HZ / 1_000_000.0)

        self._highest_frequency = QDoubleSpinBox(self)
        self._highest_frequency.setRange(0.1, 100_000.0)
        self._highest_frequency.setDecimals(6)
        self._highest_frequency.setSuffix(" MHz")
        self._highest_frequency.setValue(DEFAULT_HIGHEST_FREQUENCY_HZ / 1_000_000.0)

        self._length = QDoubleSpinBox(self)
        self._length.setDecimals(3)
        self._length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._spacing = QDoubleSpinBox(self)
        self._spacing.setDecimals(3)
        self._spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._start = QPushButton(translator.t("t2fd.starting_dimensions"), self)

        self._termination = QDoubleSpinBox(self)
        self._termination.setRange(1.0, 100_000.0)
        self._termination.setDecimals(1)
        self._termination.setSuffix(" Ω")
        self._termination.setValue(DEFAULT_T2FD_TERMINATION_OHM)

        self._transformer = QDoubleSpinBox(self)
        self._transformer.setRange(1.0, 100.0)
        self._transformer.setDecimals(2)
        self._transformer.setSuffix(":1")
        self._transformer.setValue(DEFAULT_T2FD_TRANSFORMER_RATIO)

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(DEFAULT_T2FD_HEIGHT_M, unit_system))
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

        self._band_warning = QLabel(self)
        self._band_warning.setWordWrap(True)
        self._band_warning.setStyleSheet("font-style: italic;")
        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        form = QFormLayout()
        form.addRow(translator.t("t2fd.lowest_frequency"), self._lowest_frequency)
        form.addRow(translator.t("t2fd.highest_frequency"), self._highest_frequency)
        form.addRow(translator.t("t2fd.length"), self._length)
        form.addRow(translator.t("t2fd.spacing"), self._spacing)
        form.addRow(self._start)
        form.addRow(translator.t("t2fd.termination"), self._termination)
        form.addRow(translator.t("t2fd.transformer"), self._transformer)
        form.addRow(self._height_label, self._height)
        form.addRow(translator.t("field.orientation"), self._orientation)
        form.addRow(translator.t("field.azimuth"), self._azimuth)
        form.addRow(translator.t("t2fd.wire_radius"), self._radius)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(form)
        layout.addWidget(self._band_warning)
        layout.addWidget(self._geometry)

        for widget in (
            self._lowest_frequency,
            self._highest_frequency,
            self._length,
            self._spacing,
            self._termination,
            self._transformer,
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
        valid = self._highest_frequency.value() > self._lowest_frequency.value()
        self._start.setEnabled(valid)
        self._band_warning.setText("" if valid else self._translator.t("t2fd.band_order"))

    def _set_starting_dimensions(self) -> None:
        lowest_hz = self._lowest_frequency.value() * 1_000_000.0
        span_m, spacing_m = t2fd_starting_dimensions(lowest_hz)
        self._length.setValue(length_from_m(span_m, self._unit_system))
        self._spacing.setValue(length_from_m(spacing_m, self._unit_system))

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

    def set_parameters(self, parameters: T2FDParameters) -> None:
        self._updating = True
        try:
            self._lowest_frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._highest_frequency.setValue(parameters.highest_frequency_hz / 1_000_000.0)
            self._length.setValue(length_from_m(parameters.length_m, self._unit_system))
            self._spacing.setValue(length_from_m(parameters.spacing_m, self._unit_system))
            self._termination.setValue(parameters.termination_resistance_ohm)
            self._transformer.setValue(parameters.transformer_ratio)
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
            orientation_index = self._orientation.findData(parameters.orientation.value)
            if orientation_index >= 0:
                self._orientation.setCurrentIndex(orientation_index)
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
        self._update_ground_controls()
        self._update_orientation_controls()
        self._update_band_controls()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._lowest_frequency.setValue(frequency_hz / 1_000_000.0)
        if self._highest_frequency.value() <= self._lowest_frequency.value():
            self._highest_frequency.setValue(self._lowest_frequency.value() * 6.0)
        self._apply_starting_dimensions()

    def _update_geometry(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "t2fd.geometry",
                low=f"{parameters.frequency_hz / 1e6:.3f}",
                high=f"{parameters.highest_frequency_hz / 1e6:.3f}",
                length=f"{length_from_m(parameters.length_m, self._unit_system):.3f}",
                spacing=f"{length_from_m(parameters.spacing_m, self._unit_system):.3f}",
                termination=f"{parameters.termination_resistance_ohm:g}",
                ratio=f"{parameters.transformer_ratio:g}",
                unit=unit,
            )
        )

    def parameters(self) -> T2FDParameters:
        return T2FDParameters(
            frequency_hz=self._lowest_frequency.value() * 1_000_000.0,
            highest_frequency_hz=self._highest_frequency.value() * 1_000_000.0,
            length_m=length_to_m(self._length.value(), self._unit_system),
            spacing_m=length_to_m(self._spacing.value(), self._unit_system),
            height_m=length_to_m(self._height.value(), self._unit_system),
            orientation=self._selected_orientation(),
            termination_resistance_ohm=self._termination.value(),
            transformer_ratio=self._transformer.value(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=self._radius.value() / 1_000.0,
            material=self._selected_material(),
            ground=self._ground_model(),
        )
