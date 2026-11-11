# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a Moxon rectangle."""

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

from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.moxon import MoxonParameters, moxon_20m_wire
from ...domain.antennas.polarization import Polarization
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


class MoxonForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: MoxonParameters | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self, family="moxon")
        self._unit_system = unit_system
        self._updating = False

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(14.1)

        self._width = QDoubleSpinBox(self)
        self._width.setDecimals(3)
        self._width.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._width.setValue(length_from_m(10.6, unit_system))

        self._depth = QDoubleSpinBox(self)
        self._depth.setDecimals(3)
        self._depth.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._depth.setValue(length_from_m(2.5, unit_system))

        self._reflector_tip = QDoubleSpinBox(self)
        self._reflector_tip.setDecimals(3)
        self._reflector_tip.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._reflector_tip.setValue(length_from_m(1.0, unit_system))

        self._driven_tip = QDoubleSpinBox(self)
        self._driven_tip.setDecimals(3)
        self._driven_tip.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._driven_tip.setValue(length_from_m(1.0, unit_system))

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(10.0, unit_system))

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._polarization = QComboBox(self)
        self._polarization.addItem("", Polarization.HORIZONTAL.value)
        self._polarization.addItem("", Polarization.VERTICAL.value)
        self._polarization.setItemText(0, translator.t("orientation.horizontal"))
        self._polarization.setItemText(1, translator.t("orientation.vertical"))
        self._polarization.setToolTip(translator.t("moxon.polarization_hint"))

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

        self._reference = QPushButton(translator.t("moxon.reference_preset"), self)
        self._reference.clicked.connect(self._load_reference_preset)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        self._clearance_warning = QLabel(self)
        self._clearance_warning.setWordWrap(True)
        self._clearance_warning.setVisible(False)

        form = QFormLayout()
        form.addRow(self._labels.label("field.frequency"), self._frequency)
        form.addRow(self._labels.label("moxon.width"), self._width)
        form.addRow(self._labels.label("moxon.depth"), self._depth)
        form.addRow(self._labels.label("moxon.reflector_tip"), self._reflector_tip)
        form.addRow(self._labels.label("moxon.driven_tip"), self._driven_tip)
        form.addRow(self._labels.label("field.height"), self._height)
        form.addRow(self._labels.label("field.azimuth"), self._azimuth)
        form.addRow(self._labels.label("field.polarization"), self._polarization)
        form.addRow(self._labels.label("moxon.wire_radius"), self._radius)
        form.addRow(self._labels.label("field.material"), self._material)
        form.addRow(self._labels.label("field.ground"), self._ground)
        form.addRow(self._labels.label("field.soil_preset"), self._soil)
        form.addRow(self._labels.label("field.permittivity"), self._permittivity)
        form.addRow(self._labels.label("field.conductivity"), self._conductivity)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._labels.bind_form(form)
        layout.addLayout(form)
        layout.addWidget(self._reference)
        layout.addWidget(self._geometry)
        layout.addWidget(self._clearance_warning)

        for widget in (
            self._frequency,
            self._width,
            self._depth,
            self._reflector_tip,
            self._driven_tip,
            self._height,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._polarization.currentIndexChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        if parameters is not None:
            self.set_parameters(parameters)
        self._update_ground_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        self._polarization.setItemText(
            0,
            self._translator.t("orientation.horizontal"),
        )
        self._polarization.setItemText(
            1,
            self._translator.t("orientation.vertical"),
        )
        self._polarization.setToolTip(self._translator.t("moxon.polarization_hint"))
        self._reference.setText(self._translator.t("moxon.reference_preset"))
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

    def _selected_polarization(self) -> Polarization:
        return Polarization(str(self._polarization.currentData()))

    def _update_clearance_warning(self) -> None:
        vertical = self._selected_polarization() is Polarization.VERTICAL
        required = length_to_m(self._width.value(), self._unit_system) / 2.0
        current = length_to_m(self._height.value(), self._unit_system)
        invalid = vertical and required > 0.0 and current <= required
        self._clearance_warning.setText(
            self._translator.t(
                "moxon.clearance_warning",
                height=f"{length_from_m(required, self._unit_system):.3f}",
                unit=self._translator.t(length_unit_key(self._unit_system)),
            )
            if invalid
            else ""
        )
        self._clearance_warning.setVisible(invalid)

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
            self._width,
            self._depth,
            self._reflector_tip,
            self._driven_tip,
            self._height,
        )
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: MoxonParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._width.setValue(length_from_m(parameters.width_m, self._unit_system))
            self._depth.setValue(length_from_m(parameters.depth_m, self._unit_system))
            self._reflector_tip.setValue(
                length_from_m(parameters.reflector_tip_m, self._unit_system)
            )
            self._driven_tip.setValue(length_from_m(parameters.driven_tip_m, self._unit_system))
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
            self._azimuth.setValue(parameters.azimuth_deg)
            polarization_index = self._polarization.findData(parameters.polarization.value)
            if polarization_index >= 0:
                self._polarization.setCurrentIndex(polarization_index)
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

    def _load_reference_preset(self) -> None:
        try:
            parameters = moxon_20m_wire(
                frequency_hz=self._frequency.value() * 1_000_000.0,
                height_m=length_to_m(self._height.value(), self._unit_system),
                azimuth_deg=self._azimuth.value(),
                polarization=self._selected_polarization(),
                wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
                material=self._selected_material(),
                ground=self._ground_model(),
            )
        except ValueError:
            self._update_clearance_warning()
            return
        self.set_parameters(parameters)
        self._emit_changed()

    def _update_geometry(self) -> None:
        self._update_clearance_warning()
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "moxon.geometry",
                gap=f"{length_from_m(parameters.gap_m, self._unit_system):.3f}",
                unit=unit,
            )
        )

    def parameters(self) -> MoxonParameters:
        return MoxonParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            width_m=length_to_m(self._width.value(), self._unit_system),
            depth_m=length_to_m(self._depth.value(), self._unit_system),
            reflector_tip_m=length_to_m(self._reflector_tip.value(), self._unit_system),
            driven_tip_m=length_to_m(self._driven_tip.value(), self._unit_system),
            height_m=length_to_m(self._height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            polarization=self._selected_polarization(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
