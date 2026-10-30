# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided inverted-V generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.custom import CustomAntennaParameters
from ...domain.antennas.inverted_v import InvertedVParameters
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key

MATERIALS = (COPPER, ALUMINUM)


class InvertedVDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        parameters: CustomAntennaParameters | None = None,
        frequency_hz: float | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._parameters: CustomAntennaParameters | None = None

        self.setWindowTitle(translator.t("inverted_v.title"))
        self.resize(560, 520)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(frequency_hz / 1_000_000.0 if frequency_hz is not None else 7.1)
        self._frequency.valueChanged.connect(self._update_suggestion)

        self._apex_height = QDoubleSpinBox(self)
        self._apex_height.setDecimals(3)
        self._apex_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._apex_height.setValue(length_from_m(12.0, unit_system))

        self._leg_length = QDoubleSpinBox(self)
        self._leg_length.setDecimals(3)
        self._leg_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._leg_length.setValue(length_from_m(10.6, unit_system))

        self._included_angle = QDoubleSpinBox(self)
        self._included_angle.setRange(1.0, 179.0)
        self._included_angle.setDecimals(1)
        self._included_angle.setSuffix("°")
        self._included_angle.setValue(120.0)

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

        self._ground = QComboBox(self)
        self._ground.addItem("", GroundKind.FREE_SPACE.value)
        self._ground.addItem("", GroundKind.PERFECT.value)
        self._ground.addItem("", GroundKind.FINITE.value)
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
        self._hint = QLabel(translator.t("inverted_v.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("inverted_v.evidence"), self)
        self._evidence.setWordWrap(True)

        form = QFormLayout()
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("inverted_v.apex_height"), self._apex_height)
        form.addRow(translator.t("inverted_v.leg_length"), self._leg_length)
        form.addRow(translator.t("inverted_v.included_angle"), self._included_angle)
        form.addRow(translator.t("field.azimuth"), self._azimuth)
        form.addRow(translator.t("inverted_v.wire_radius"), self._radius)
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

        if parameters is not None:
            self._set_existing(parameters)
        self._update_ground_controls()
        self._update_suggestion()
        for widget in (
            self._apex_height,
            self._leg_length,
            self._included_angle,
            self._azimuth,
        ):
            widget.valueChanged.connect(self._update_suggestion)

    def _set_existing(self, parameters: CustomAntennaParameters) -> None:
        existing = InvertedVParameters.from_custom_parameters(parameters)
        self._frequency.setValue(existing.frequency_hz / 1_000_000.0)
        self._apex_height.setValue(length_from_m(existing.apex_height_m, self._unit_system))
        self._leg_length.setValue(length_from_m(existing.leg_length_m, self._unit_system))
        self._included_angle.setValue(existing.included_angle_deg)
        self._azimuth.setValue(existing.azimuth_deg)
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

    def _update_suggestion(self, *_args: object) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        self._geometry.setText(
            self._translator.t(
                "inverted_v.geometry",
                span=f"{length_from_m(parameters.horizontal_span_m, self._unit_system):.3f}",
                end=f"{length_from_m(parameters.end_height_m, self._unit_system):.3f}",
                unit=self._translator.t(length_unit_key(self._unit_system)),
            )
        )

    def parameters(self) -> InvertedVParameters:
        return InvertedVParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            leg_length_m=length_to_m(self._leg_length.value(), self._unit_system),
            apex_height_m=length_to_m(self._apex_height.value(), self._unit_system),
            included_angle_deg=self._included_angle.value(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=self._radius.value() / 1_000.0,
            material=self._selected_material(),
            ground=self._ground_model(),
        )

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters().to_custom_parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("inverted_v.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> CustomAntennaParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
