# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided ZS6BKW preset using a geometry transmission line."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.custom import CustomAntennaParameters
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.transmission_line_doublet import (
    DoubletPreset,
    TransmissionLineDoubletParameters,
)
from ...domain.antennas.zs6bkw import (
    ZS6BKW_DESIGN_FREQUENCY_HZ,
    ZS6BKW_VARIANTS,
    ZS6BKWVariant,
    zs6bkw_parameters,
)
from ...domain.environment.ground import GroundKind, GroundModel
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import (
    UnitSystem,
    length_from_m,
    length_to_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
)
from ..widgets.form_units import apply_radius_units
from ..widgets.ground_presets import GroundPresetController

MATERIALS = (COPPER, ALUMINUM)


class ZS6BKWDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._parameters: CustomAntennaParameters | None = None
        self.setWindowTitle(translator.t("zs6bkw.title"))
        self.resize(*scaled_dialog_size(620, 700))

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(
            (frequency_hz if frequency_hz is not None else ZS6BKW_DESIGN_FREQUENCY_HZ) / 1_000_000.0
        )

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(10.0, unit_system))

        self._feed_height = QDoubleSpinBox(self)
        self._feed_height.setDecimals(3)
        self._feed_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._feed_height.setValue(length_from_m(1.0, unit_system))

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)
        self._radius.setValue(radius_from_m(0.001, unit_system))

        self._variant = QComboBox(self)
        for index, _variant in enumerate(ZS6BKW_VARIANTS):
            self._variant.addItem(translator.t(f"zs6bkw.variant.{index}"), index)
        self._variant.setCurrentIndex(0)

        self._velocity = QDoubleSpinBox(self)
        self._velocity.setRange(0.01, 1.0)
        self._velocity.setDecimals(3)
        self._velocity.setValue(1.0)

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
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("field.height"), self._height)
        form.addRow(translator.t("g5rv.feed_height"), self._feed_height)
        form.addRow(translator.t("field.azimuth"), self._azimuth)
        form.addRow(translator.t("g5rv.wire_radius"), self._radius)
        form.addRow(translator.t("zs6bkw.variant_label"), self._variant)
        form.addRow(translator.t("g5rv.velocity_factor"), self._velocity)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.soil_preset"), self._soil)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)

        hint = QLabel(translator.t("zs6bkw.hint"), self)
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("zs6bkw.evidence"), self)
        evidence.setWordWrap(True)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        body = QWidget(self)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.addLayout(form)
        body_layout.addWidget(self._geometry)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(body)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll, 1)
        layout.addWidget(hint)
        layout.addWidget(evidence)
        layout.addWidget(buttons)

        self._variant.currentIndexChanged.connect(self._update_geometry)
        self._ground.currentIndexChanged.connect(self._update_ground_controls)
        for spin in (
            self._frequency,
            self._height,
            self._feed_height,
            self._azimuth,
            self._radius,
            self._velocity,
        ):
            spin.valueChanged.connect(self._update_geometry)
        self._update_ground_controls()
        self._update_geometry()

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

    def _selected_variant(self) -> ZS6BKWVariant:
        index = self._variant.currentData()
        if not isinstance(index, int):
            return ZS6BKW_VARIANTS[0]
        return ZS6BKW_VARIANTS[index]

    def _update_geometry(self, *_args: object) -> None:
        variant = self._selected_variant()
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "zs6bkw.geometry",
                dipole=f"{length_from_m(variant.dipole_total_length_m, self._unit_system):.3f}",
                line_impedance=f"{variant.characteristic_impedance_ohm:g}",
                line_length=f"{length_from_m(variant.line_length_m, self._unit_system):.3f}",
                unit=unit,
            )
        )

    def parameters(self) -> CustomAntennaParameters:
        return zs6bkw_parameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            height_m=length_to_m(self._height.value(), self._unit_system),
            feed_height_m=length_to_m(self._feed_height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            variant=self._selected_variant(),
            line_velocity_factor=self._velocity.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )

    def typed_parameters(self) -> TransmissionLineDoubletParameters:
        variant = self._selected_variant()
        return TransmissionLineDoubletParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            preset=DoubletPreset.ZS6BKW,
            dipole_total_length_m=variant.dipole_total_length_m,
            height_m=length_to_m(self._height.value(), self._unit_system),
            feed_height_m=length_to_m(self._feed_height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            line_impedance_ohm=variant.characteristic_impedance_ohm,
            line_length_m=variant.line_length_m,
            line_velocity_factor=self._velocity.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )

    def typed_result_parameters(self) -> TransmissionLineDoubletParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self.typed_parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("zs6bkw.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> CustomAntennaParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
