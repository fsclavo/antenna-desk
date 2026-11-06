# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided center-fed doublet with an open-wire feed line."""

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

from ...domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ...domain.antennas.feed_line import FeedLine
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.design.formulas import half_wave_length_m
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

MATERIALS = (COPPER, ALUMINUM)


class DoubletDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: DipoleParameters | None = None,
        feed_line: FeedLine | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._parameters: DipoleParameters | None = None
        self._feed_line: FeedLine | None = None
        self.setWindowTitle(translator.t("doublet.title"))
        self.resize(*scaled_dialog_size(620, 760))

        initial_frequency_hz = (
            parameters.frequency_hz if parameters is not None else frequency_hz
        ) or 7_100_000.0
        initial_length_m = (
            parameters.total_length_m
            if parameters is not None
            else half_wave_length_m(initial_frequency_hz)
        )
        initial_height_m = parameters.height_m if parameters is not None else 10.0
        initial_orientation = (
            parameters.orientation if parameters is not None else DipoleOrientation.HORIZONTAL
        )
        initial_azimuth = parameters.azimuth_deg if parameters is not None else 0.0
        initial_radius_m = parameters.wire_radius_m if parameters is not None else 0.001
        initial_material = parameters.material if parameters is not None else COPPER
        initial_ground = (
            parameters.ground
            if parameters is not None
            else GroundModel.finite(relative_permittivity=13.0, conductivity_s_per_m=0.005)
        )
        line = (
            feed_line
            if feed_line is not None
            else FeedLine(
                characteristic_impedance_ohm=450.0,
                length_m=10.0,
                velocity_factor=0.9,
                matched_loss_db_per_100m=0.2,
            )
        )

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(initial_frequency_hz / 1_000_000.0)

        self._length = QDoubleSpinBox(self)
        self._length.setDecimals(3)
        self._length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._length.setValue(length_from_m(initial_length_m, unit_system))

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(initial_height_m, unit_system))

        self._orientation = QComboBox(self)
        self._orientation.addItem(
            translator.t("orientation.horizontal"),
            DipoleOrientation.HORIZONTAL.value,
        )
        self._orientation.addItem(
            translator.t("orientation.vertical"),
            DipoleOrientation.VERTICAL.value,
        )
        orientation_index = self._orientation.findData(initial_orientation.value)
        if orientation_index >= 0:
            self._orientation.setCurrentIndex(orientation_index)

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")
        self._azimuth.setValue(initial_azimuth)

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)
        self._radius.setValue(radius_from_m(initial_radius_m, unit_system))

        self._material = QComboBox(self)
        for material in MATERIALS:
            self._material.addItem(material.name, material)
        self._material.setItemText(0, translator.t("material.copper"))
        self._material.setItemText(1, translator.t("material.aluminum"))
        material_index = self._material.findData(initial_material)
        if material_index >= 0:
            self._material.setCurrentIndex(material_index)

        self._ground = QComboBox(self)
        self._ground.addItem("", GroundKind.FREE_SPACE.value)
        self._ground.addItem("", GroundKind.PERFECT.value)
        self._ground.addItem("", GroundKind.FINITE.value)
        self._ground.setItemText(0, translator.t("ground.free_space"))
        self._ground.setItemText(1, translator.t("ground.perfect"))
        self._ground.setItemText(2, translator.t("ground.finite"))
        ground_index = self._ground.findData(initial_ground.kind.value)
        if ground_index >= 0:
            self._ground.setCurrentIndex(ground_index)

        self._permittivity = QDoubleSpinBox(self)
        self._permittivity.setRange(1.0, 1_000.0)
        self._permittivity.setDecimals(2)
        self._permittivity.setValue(initial_ground.relative_permittivity or 13.0)

        self._conductivity = QDoubleSpinBox(self)
        self._conductivity.setRange(0.000001, 1_000.0)
        self._conductivity.setDecimals(6)
        self._conductivity.setSingleStep(0.001)
        self._conductivity.setSuffix(" S/m")
        self._conductivity.setValue(initial_ground.conductivity_s_per_m or 0.005)

        self._line_impedance = QDoubleSpinBox(self)
        self._line_impedance.setRange(1.0, 10_000.0)
        self._line_impedance.setDecimals(1)
        self._line_impedance.setSuffix(" Ω")
        self._line_impedance.setValue(line.characteristic_impedance_ohm)

        self._line_length = QDoubleSpinBox(self)
        self._line_length.setRange(0.0, 100_000.0)
        self._line_length.setDecimals(3)
        self._line_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._line_length.setValue(length_from_m(line.length_m, unit_system))

        self._line_velocity = QDoubleSpinBox(self)
        self._line_velocity.setRange(0.01, 1.0)
        self._line_velocity.setDecimals(3)
        self._line_velocity.setValue(line.velocity_factor)

        self._line_loss = QDoubleSpinBox(self)
        self._line_loss.setRange(0.0, 100.0)
        self._line_loss.setDecimals(3)
        self._line_loss.setSuffix(" dB/100 m")
        self._line_loss.setValue(line.matched_loss_db_per_100m)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        form = QFormLayout()
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("field.length"), self._length)
        form.addRow(translator.t("field.height"), self._height)
        form.addRow(translator.t("field.orientation"), self._orientation)
        form.addRow(translator.t("field.azimuth"), self._azimuth)
        form.addRow(translator.t("field.wire_radius"), self._radius)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)
        form.addRow(
            translator.t("feed_line.characteristic_impedance"),
            self._line_impedance,
        )
        form.addRow(translator.t("feed_line.length"), self._line_length)
        form.addRow(translator.t("feed_line.velocity_factor"), self._line_velocity)
        form.addRow(translator.t("feed_line.loss"), self._line_loss)

        hint = QLabel(translator.t("doublet.hint"), self)
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("doublet.evidence"), self)
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

        self._orientation.currentIndexChanged.connect(self._update_orientation_controls)
        self._ground.currentIndexChanged.connect(self._update_ground_controls)
        self._frequency.valueChanged.connect(self._update_geometry)
        self._length.valueChanged.connect(self._update_geometry)
        self._height.valueChanged.connect(self._update_geometry)
        self._line_impedance.valueChanged.connect(self._update_geometry)
        self._line_length.valueChanged.connect(self._update_geometry)
        self._line_velocity.valueChanged.connect(self._update_geometry)
        self._line_loss.valueChanged.connect(self._update_geometry)
        self._update_orientation_controls()
        self._update_ground_controls()
        self._update_geometry()

    def _update_orientation_controls(self) -> None:
        horizontal = self._orientation.currentData() == DipoleOrientation.HORIZONTAL.value
        self._azimuth.setEnabled(horizontal)

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

    def _selected_orientation(self) -> DipoleOrientation:
        value = self._orientation.currentData()
        return DipoleOrientation(value) if isinstance(value, str) else DipoleOrientation.HORIZONTAL

    def _update_geometry(self, *_args: object) -> None:
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "doublet.geometry",
                length=f"{self._length.value():.3f}",
                unit=unit,
                line=f"{self._line_impedance.value():.1f}",
            )
        )

    def parameters(self) -> DipoleParameters:
        return DipoleParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            total_length_m=length_to_m(self._length.value(), self._unit_system),
            height_m=length_to_m(self._height.value(), self._unit_system),
            orientation=self._selected_orientation(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )

    def feed_line(self) -> FeedLine:
        return FeedLine(
            characteristic_impedance_ohm=self._line_impedance.value(),
            length_m=length_to_m(self._line_length.value(), self._unit_system),
            velocity_factor=self._line_velocity.value(),
            matched_loss_db_per_100m=self._line_loss.value(),
        )

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
            self._feed_line = self.feed_line()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("doublet.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> DipoleParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters

    def result_feed_line(self) -> FeedLine:
        if self._feed_line is None:
            raise ValueError("the dialog has not produced a feed line")
        return self._feed_line
