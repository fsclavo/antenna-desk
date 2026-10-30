# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided vertical radiator with an optional radial ground plane."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.custom import CustomAntennaParameters
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.vertical import MAX_RADIALS, VerticalParameters
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key

MATERIALS = (COPPER, ALUMINUM)


class VerticalDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: CustomAntennaParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._parameters: CustomAntennaParameters | None = None

        self.setWindowTitle(translator.t("vertical.title"))
        self.resize(560, 600)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(frequency_hz / 1_000_000.0 if frequency_hz is not None else 7.1)

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(10.0, unit_system))

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._base_height.setValue(length_from_m(0.25, unit_system))

        self._radial_count = QSpinBox(self)
        self._radial_count.setRange(0, MAX_RADIALS)
        self._radial_count.setValue(16)
        self._radial_count.valueChanged.connect(self._update_controls)

        self._radial_length = QDoubleSpinBox(self)
        self._radial_length.setDecimals(3)
        self._radial_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._radial_length.setValue(length_from_m(5.0, unit_system))

        self._radial_angle = QDoubleSpinBox(self)
        self._radial_angle.setRange(0.0, 360.0)
        self._radial_angle.setDecimals(1)
        self._radial_angle.setSuffix("°")

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
        self._ground.currentIndexChanged.connect(self._update_ground_controls)

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
        self._hint = QLabel(translator.t("vertical.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("vertical.evidence"), self)
        self._evidence.setWordWrap(True)

        form = QFormLayout()
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("vertical.height"), self._height)
        form.addRow(translator.t("vertical.base_height"), self._base_height)
        form.addRow(translator.t("vertical.radial_count"), self._radial_count)
        form.addRow(translator.t("vertical.radial_length"), self._radial_length)
        form.addRow(translator.t("vertical.radial_angle"), self._radial_angle)
        form.addRow(translator.t("vertical.wire_radius"), self._radius)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._geometry)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addStretch(1)
        layout.addWidget(buttons)

        for widget in (self._height, self._base_height, self._radial_length):
            widget.valueChanged.connect(self._update_geometry)
        if parameters is not None:
            self._set_existing(parameters)
        self._update_ground_controls()
        self._update_controls()

    def _set_existing(self, parameters: CustomAntennaParameters) -> None:
        existing = VerticalParameters.from_custom_parameters(parameters)
        self._frequency.setValue(existing.frequency_hz / 1_000_000.0)
        self._height.setValue(length_from_m(existing.height_m, self._unit_system))
        self._base_height.setValue(length_from_m(existing.base_height_m, self._unit_system))
        self._radial_count.setValue(existing.radial_count)
        self._radial_length.setValue(length_from_m(existing.radial_length_m, self._unit_system))
        self._radial_angle.setValue(existing.radial_angle_deg)
        self._radius.setValue(existing.wire_radius_m * 1_000.0)
        material_index = self._material.findData(existing.material)
        if material_index >= 0:
            self._material.setCurrentIndex(material_index)
        ground_index = self._ground.findData(existing.ground.kind.value)
        if ground_index >= 0:
            self._ground.setCurrentIndex(ground_index)
        if existing.ground.relative_permittivity is not None:
            self._permittivity.setValue(existing.ground.relative_permittivity)
        if existing.ground.conductivity_s_per_m is not None:
            self._conductivity.setValue(existing.ground.conductivity_s_per_m)

    def _update_ground_controls(self) -> None:
        finite = self._ground.currentData() == GroundKind.FINITE.value
        self._permittivity.setEnabled(finite)
        self._conductivity.setEnabled(finite)

    def _update_controls(self) -> None:
        enabled = self._radial_count.value() > 0
        self._radial_length.setEnabled(enabled)
        self._radial_angle.setEnabled(enabled)
        self._update_geometry()

    def _update_geometry(self, *_args: object) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        self._geometry.setText(
            self._translator.t(
                "vertical.geometry",
                top=f"{length_from_m(parameters.top_height_m, self._unit_system):.3f}",
                unit=self._translator.t(length_unit_key(self._unit_system)),
                count=parameters.radial_count,
            )
        )

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

    def parameters(self) -> VerticalParameters:
        return VerticalParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            height_m=length_to_m(self._height.value(), self._unit_system),
            base_height_m=length_to_m(self._base_height.value(), self._unit_system),
            radial_count=self._radial_count.value(),
            radial_length_m=length_to_m(self._radial_length.value(), self._unit_system),
            radial_angle_deg=self._radial_angle.value(),
            wire_radius_m=self._radius.value() / 1_000.0,
            material=self._selected_material(),
            ground=self._ground_model(),
        )

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters().to_custom_parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("vertical.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> CustomAntennaParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
