# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dipole parameter form."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.design import AntennaDesignParameters
from ...domain.antennas.dipole import (
    ANTENNA_TYPE_WIRE_DIPOLE,
    DipoleOrientation,
    DipoleParameters,
)
from ...domain.antennas.folded_dipole import (
    ANTENNA_TYPE_FOLDED_DIPOLE,
    FoldedDipoleParameters,
)
from ...domain.antennas.loop import ANTENNA_TYPE_LOOP, LoopParameters
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.environment.ground import GroundKind, GroundModel
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
)
from ...domain.simulation.spec import SimulationSpec
from ..i18n import Translator
from ..units import (
    UnitSystem,
    diameter_bounds,
    diameter_from_m,
    diameter_to_m,
    diameter_unit_key,
    height_bounds,
    length_bounds,
    length_from_m,
    length_to_m,
    length_unit_key,
)

MATERIALS = (COPPER, ALUMINUM)


class DipoleForm(QWidget):
    apply_requested = Signal()
    optimize_requested = Signal()
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem = UnitSystem.METRIC,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._updating = False

        self._group = QGroupBox(self)
        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setValue(7.1)
        self._frequency.setSuffix(" MHz")

        self._type = QComboBox(self)
        self._type.addItem("", ANTENNA_TYPE_WIRE_DIPOLE)
        self._type.addItem("", ANTENNA_TYPE_FOLDED_DIPOLE)
        self._type.addItem("", ANTENNA_TYPE_LOOP)

        self._orientation = QComboBox(self)
        self._orientation.addItem("", DipoleOrientation.HORIZONTAL.value)
        self._orientation.addItem("", DipoleOrientation.VERTICAL.value)

        self._length = QDoubleSpinBox(self)
        self._spacing = QDoubleSpinBox(self)
        self._spacing.setValue(0.1)
        self._sides = QSpinBox(self)
        self._sides.setRange(3, 128)
        self._sides.setValue(16)
        self._height = QDoubleSpinBox(self)
        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")
        self._diameter = QDoubleSpinBox(self)

        self._material = QComboBox(self)
        for material in MATERIALS:
            self._material.addItem(material.name, material)

        self._ground = QComboBox(self)
        self._ground.addItem("", GroundKind.FREE_SPACE.value)
        self._ground.addItem("", GroundKind.PERFECT.value)
        self._ground.addItem("", GroundKind.FINITE.value)
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

        self._reference = QDoubleSpinBox(self)
        self._reference.setRange(1.0, 1_000.0)
        self._reference.setDecimals(1)
        self._reference.setValue(50.0)
        self._reference.setSuffix(" Ω")

        self._sweep_group = QGroupBox(self)
        self._sweep = QCheckBox(self._sweep_group)
        self._sweep.setChecked(True)
        self._sweep_start = QDoubleSpinBox(self._sweep_group)
        self._sweep_stop = QDoubleSpinBox(self._sweep_group)
        self._sweep_points = QSpinBox(self._sweep_group)
        self._sweep_points.setRange(2, 10_000)
        self._sweep_points.setValue(21)
        for spin in (self._sweep_start, self._sweep_stop):
            spin.setRange(0.1, 100_000.0)
            spin.setDecimals(6)
            spin.setSuffix(" MHz")

        self._apply = QPushButton(self)
        self._apply.clicked.connect(self.apply_requested)
        self._optimize = QPushButton(self)
        self._optimize.clicked.connect(self.optimize_requested)

        self._form_layout = QFormLayout()
        form = self._form_layout
        form.addRow(self._label("field.frequency"), self._frequency)
        form.addRow(self._label("field.antenna_type"), self._type)
        form.addRow(self._label("field.orientation"), self._orientation)
        form.addRow(self._label("field.length"), self._length)
        form.addRow(self._label("field.spacing"), self._spacing)
        form.addRow(self._label("field.sides"), self._sides)
        form.addRow(self._label("field.height"), self._height)
        form.addRow(self._label("field.azimuth"), self._azimuth)
        form.addRow(self._label("field.diameter"), self._diameter)
        form.addRow(self._label("field.material"), self._material)
        form.addRow(self._label("field.ground"), self._ground)
        form.addRow(self._label("field.permittivity"), self._permittivity)
        form.addRow(self._label("field.conductivity"), self._conductivity)
        form.addRow(self._label("field.reference_impedance"), self._reference)

        sweep_layout = QGridLayout(self._sweep_group)
        sweep_layout.addWidget(self._sweep, 0, 0, 1, 2)
        sweep_layout.addWidget(self._label("field.sweep_start"), 1, 0)
        sweep_layout.addWidget(self._sweep_start, 1, 1)
        sweep_layout.addWidget(self._label("field.sweep_stop"), 2, 0)
        sweep_layout.addWidget(self._sweep_stop, 2, 1)
        sweep_layout.addWidget(self._label("field.sweep_points"), 3, 0)
        sweep_layout.addWidget(self._sweep_points, 3, 1)

        group_layout = QVBoxLayout(self._group)
        group_layout.addLayout(form)
        group_layout.addWidget(self._sweep_group)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self._apply)
        button_layout.addWidget(self._optimize)
        group_layout.addLayout(button_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(self._group)
        layout.addStretch(1)

        self._ground.currentIndexChanged.connect(self._update_ground_controls)
        self._sweep.toggled.connect(self._update_sweep_controls)
        self._frequency.valueChanged.connect(self._on_frequency_changed)
        self._type.currentIndexChanged.connect(self._on_type_changed)
        self._orientation.currentIndexChanged.connect(self._update_orientation_labels)

        for spin in (
            self._frequency,
            self._length,
            self._spacing,
            self._height,
            self._azimuth,
            self._diameter,
            self._permittivity,
            self._conductivity,
            self._reference,
            self._sweep_start,
            self._sweep_stop,
        ):
            spin.valueChanged.connect(self._emit_changed)
        self._sweep_points.valueChanged.connect(self._emit_changed)
        self._sides.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._emit_changed)
        self._sweep.toggled.connect(self._emit_changed)
        self._type.currentIndexChanged.connect(self._emit_changed)
        self._orientation.currentIndexChanged.connect(self._emit_changed)

        self._apply_unit_system()
        self._update_ground_controls()
        self._update_sweep_controls()
        self._update_type_controls()
        self.set_parameters(
            DipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=8.0,
                wire_radius_m=0.001,
                ground=GroundModel.finite(
                    relative_permittivity=13.0,
                    conductivity_s_per_m=0.005,
                ),
            )
        )
        self.retranslate()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self.changed.emit()

    def _label(self, key: str) -> QLabel:
        label = QLabel(self)
        label.setObjectName(key)
        return label

    def _labels(self) -> dict[str, QLabel]:
        return {
            key: label
            for label in self.findChildren(QLabel)
            if (key := label.objectName()).startswith("field.")
        }

    def retranslate(self) -> None:
        self._group.setTitle(self._translator.t("panel.design"))
        self._sweep_group.setTitle(self._translator.t("field.sweep"))
        self._sweep.setText(self._translator.t("field.sweep_enabled"))
        self._apply.setText(self._translator.t("action.apply"))
        self._optimize.setText(self._translator.t("action.optimize"))
        labels = self._labels()
        for key, label in labels.items():
            label.setText(self._translator.t(key))
        self._material.setItemText(0, self._translator.t("material.copper"))
        self._material.setItemText(1, self._translator.t("material.aluminum"))
        self._ground.setItemText(0, self._translator.t("ground.free_space"))
        self._ground.setItemText(1, self._translator.t("ground.perfect"))
        self._ground.setItemText(2, self._translator.t("ground.finite"))
        self._orientation.setItemText(0, self._translator.t("orientation.horizontal"))
        self._orientation.setItemText(1, self._translator.t("orientation.vertical"))
        self._type.setItemText(0, self._translator.t("antenna_type.wire_dipole"))
        self._type.setItemText(1, self._translator.t("antenna_type.folded_dipole"))
        self._type.setItemText(2, self._translator.t("antenna_type.loop"))
        self._apply_unit_system()
        self._update_type_controls()

    def _apply_unit_system(
        self,
        length_m: float | None = None,
        height_m: float | None = None,
        diameter_m: float | None = None,
        spacing_m: float | None = None,
    ) -> None:
        previous_updating = self._updating
        self._updating = True
        try:
            self._apply_unit_system_values(length_m, height_m, diameter_m, spacing_m)
        finally:
            self._updating = previous_updating

    def _apply_unit_system_values(
        self,
        length_m: float | None = None,
        height_m: float | None = None,
        diameter_m: float | None = None,
        spacing_m: float | None = None,
    ) -> None:
        length_min, length_max = length_bounds(self._unit_system)
        height_min, height_max = height_bounds(self._unit_system)
        diameter_min, diameter_max = diameter_bounds(self._unit_system)

        current_length_m = length_m if length_m is not None else self._length_to_m_current()
        current_height_m = height_m if height_m is not None else self._height_to_m_current()
        current_diameter_m = diameter_m if diameter_m is not None else self._diameter_to_m_current()
        current_spacing_m = spacing_m if spacing_m is not None else self._spacing_to_m_current()

        self._length.setRange(length_min, length_max)
        self._spacing.setRange(length_min, length_max)
        self._height.setRange(height_min, height_max)
        self._diameter.setRange(diameter_min, diameter_max)
        self._length.setDecimals(3)
        self._spacing.setDecimals(3)
        self._height.setDecimals(3)
        self._diameter.setDecimals(3 if self._unit_system is UnitSystem.METRIC else 4)
        self._length.setSuffix(f" {self._translator.t(length_unit_key(self._unit_system))}")
        self._spacing.setSuffix(f" {self._translator.t(length_unit_key(self._unit_system))}")
        self._height.setSuffix(f" {self._translator.t(length_unit_key(self._unit_system))}")
        self._diameter.setSuffix(f" {self._translator.t(diameter_unit_key(self._unit_system))}")

        self._length.setValue(length_from_m(current_length_m, self._unit_system))
        self._spacing.setValue(length_from_m(current_spacing_m, self._unit_system))
        self._height.setValue(length_from_m(current_height_m, self._unit_system))
        self._diameter.setValue(diameter_from_m(current_diameter_m, self._unit_system))

    def _length_to_m_current(self) -> float:
        return length_to_m(self._length.value(), self._unit_system)

    def _spacing_to_m_current(self) -> float:
        return length_to_m(self._spacing.value(), self._unit_system)

    def _height_to_m_current(self) -> float:
        return length_to_m(self._height.value(), self._unit_system)

    def _diameter_to_m_current(self) -> float:
        return diameter_to_m(self._diameter.value(), self._unit_system)

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        length_m = self._length_to_m_current()
        height_m = self._height_to_m_current()
        diameter_m = self._diameter_to_m_current()
        spacing_m = self._spacing_to_m_current()
        self._unit_system = unit_system
        self._apply_unit_system(length_m, height_m, diameter_m, spacing_m)

    def set_parameters(
        self,
        parameters: AntennaDesignParameters,
        *,
        reset_sweep: bool = True,
    ) -> None:
        previous_updating = self._updating
        self._updating = True
        try:
            self._set_parameters(parameters, reset_sweep=reset_sweep)
        finally:
            self._updating = previous_updating

    def _set_parameters(
        self,
        parameters: AntennaDesignParameters,
        *,
        reset_sweep: bool = True,
    ) -> None:
        if isinstance(parameters, FoldedDipoleParameters):
            antenna_type = ANTENNA_TYPE_FOLDED_DIPOLE
            length_m = parameters.total_length_m
            self._spacing.setValue(length_from_m(parameters.spacing_m, self._unit_system))
        elif isinstance(parameters, LoopParameters):
            antenna_type = ANTENNA_TYPE_LOOP
            length_m = parameters.circumference_m
            self._sides.setValue(parameters.sides)
        else:
            antenna_type = ANTENNA_TYPE_WIRE_DIPOLE
            length_m = parameters.total_length_m
            orientation_index = self._orientation.findData(parameters.orientation.value)
            if orientation_index >= 0:
                self._orientation.setCurrentIndex(orientation_index)

        type_index = self._type.findData(antenna_type)
        if type_index >= 0:
            self._type.setCurrentIndex(type_index)
        self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
        self._length.setValue(length_from_m(length_m, self._unit_system))
        self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
        self._azimuth.setValue(parameters.azimuth_deg)
        self._diameter.setValue(diameter_from_m(parameters.wire_radius_m * 2.0, self._unit_system))

        material_index = self._material.findData(parameters.material)
        if material_index < 0:
            self._material.addItem(parameters.material.name, parameters.material)
            material_index = self._material.count() - 1
        self._material.setCurrentIndex(material_index)

        ground_index = self._ground.findData(parameters.ground.kind.value)
        if ground_index >= 0:
            self._ground.setCurrentIndex(ground_index)
        if parameters.ground.relative_permittivity is not None:
            self._permittivity.setValue(parameters.ground.relative_permittivity)
        if parameters.ground.conductivity_s_per_m is not None:
            self._conductivity.setValue(parameters.ground.conductivity_s_per_m)

        if reset_sweep:
            center_mhz = parameters.frequency_hz / 1_000_000.0
            self._sweep_start.setValue(center_mhz * 0.95)
            self._sweep_stop.setValue(center_mhz * 1.05)
            self._sweep_points.setValue(21)
            self._sweep.setChecked(True)
        self._update_ground_controls()
        self._update_sweep_controls()
        self._update_type_controls()

    def parameters(self) -> AntennaDesignParameters:
        material = self._material.currentData()
        if not isinstance(material, ConductorMaterial):
            raise ValueError("invalid conductor material")

        ground_kind = self._ground.currentData()
        if ground_kind == GroundKind.FREE_SPACE.value:
            ground = GroundModel.free_space()
        elif ground_kind == GroundKind.PERFECT.value:
            ground = GroundModel.perfect()
        elif ground_kind == GroundKind.FINITE.value:
            ground = GroundModel.finite(
                relative_permittivity=self._permittivity.value(),
                conductivity_s_per_m=self._conductivity.value(),
            )
        else:
            raise ValueError("invalid ground model")

        diameter_m = diameter_to_m(self._diameter.value(), self._unit_system)
        common = {
            "frequency_hz": self._frequency.value() * 1_000_000.0,
            "height_m": length_to_m(self._height.value(), self._unit_system),
            "azimuth_deg": self._azimuth.value(),
            "wire_radius_m": diameter_m / 2.0,
            "material": material,
            "ground": ground,
        }
        antenna_type = self._type.currentData()
        if antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE:
            return FoldedDipoleParameters(
                total_length_m=length_to_m(self._length.value(), self._unit_system),
                spacing_m=length_to_m(self._spacing.value(), self._unit_system),
                **common,
            )
        if antenna_type == ANTENNA_TYPE_LOOP:
            return LoopParameters(
                circumference_m=length_to_m(self._length.value(), self._unit_system),
                sides=self._sides.value(),
                **common,
            )
        return DipoleParameters(
            total_length_m=length_to_m(self._length.value(), self._unit_system),
            orientation=DipoleOrientation(self._orientation.currentData()),
            **common,
        )

    def antenna_type(self) -> str:
        value = self._type.currentData()
        return value if isinstance(value, str) else ANTENNA_TYPE_WIRE_DIPOLE

    def simulation_spec(self) -> SimulationSpec:
        parameters = self.parameters()
        center_hz = parameters.frequency_hz
        if self._sweep.isChecked():
            frequency_plan = FrequencyPlan.sweep(
                self._sweep_start.value() * 1_000_000.0,
                self._sweep_stop.value() * 1_000_000.0,
                self._sweep_points.value(),
            )
        else:
            frequency_plan = FrequencyPlan.single(center_hz)

        if parameters.ground.kind is GroundKind.FREE_SPACE:
            far_field = FarFieldRequest(
                enabled=True,
                theta_start_deg=0.0,
                theta_stop_deg=180.0,
                theta_count=19,
                phi_count=1,
            )
        else:
            far_field = FarFieldRequest(
                enabled=True,
                theta_start_deg=0.0,
                theta_stop_deg=90.0,
                theta_count=10,
                phi_count=1,
            )

        segmentation = aligned_policy_for_model(
            parameters.to_antenna(name="Segmentation preview"),
            frequency_plan.stop_hz,
            SegmentationPolicy(min_segments_per_wire=3),
        )
        return SimulationSpec(
            frequency_plan=frequency_plan,
            segmentation=segmentation,
            reference_impedance_ohm=self._reference.value(),
            far_field=far_field,
        )

    def _on_type_changed(self, *_args: object) -> None:
        self._update_type_controls()

    def _set_row_visible(self, field: QWidget, visible: bool) -> None:
        label = self._form_layout.labelForField(field)
        if label is not None:
            label.setVisible(visible)
        field.setVisible(visible)

    def _update_type_controls(self) -> None:
        antenna_type = self._type.currentData()
        is_dipole = antenna_type == ANTENNA_TYPE_WIRE_DIPOLE
        is_folded = antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE
        is_loop = antenna_type == ANTENNA_TYPE_LOOP
        self._set_row_visible(self._orientation, is_dipole)
        self._set_row_visible(self._spacing, is_folded)
        self._set_row_visible(self._sides, is_loop)
        self._optimize.setVisible(True)
        labels = self._labels()
        length_label = labels.get("field.length")
        if length_label is not None:
            if is_folded:
                length_label.setText(self._translator.t("field.element_length"))
            elif is_loop:
                length_label.setText(self._translator.t("field.circumference"))
            else:
                length_label.setText(self._translator.t("field.length"))
        self._update_orientation_labels()

    def _update_orientation_labels(self) -> None:
        is_dipole = self._type.currentData() == ANTENNA_TYPE_WIRE_DIPOLE
        vertical = is_dipole and self._orientation.currentData() == DipoleOrientation.VERTICAL.value
        self._azimuth.setEnabled(not vertical)
        labels = self._labels()
        height_label = labels.get("field.height")
        if height_label is not None:
            height_label.setText(
                self._translator.t("field.base_height" if vertical else "field.height")
            )

    def _update_ground_controls(self) -> None:
        finite = self._ground.currentData() == GroundKind.FINITE.value
        self._permittivity.setEnabled(finite)
        self._conductivity.setEnabled(finite)

    def _update_sweep_controls(self) -> None:
        enabled = self._sweep.isChecked()
        self._sweep_start.setEnabled(enabled)
        self._sweep_stop.setEnabled(enabled)
        self._sweep_points.setEnabled(enabled)

    def _on_frequency_changed(self, value: float) -> None:
        if not self._sweep_start.hasFocus() and not self._sweep_stop.hasFocus():
            self._sweep_start.setValue(value * 0.95)
            self._sweep_stop.setValue(value * 1.05)
