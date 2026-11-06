# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided classic Zepp generator with a real two-wire matching stub."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.custom import CustomAntennaParameters
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.zepp import (
    ZEPP_DEFAULT_BASE_HEIGHT_M,
    ZEPP_DEFAULT_SPACING_M,
    ZEPP_DESIGN_FREQUENCY_HZ,
    parallel_wire_impedance_ohm,
    zepp_parameters,
    zepp_starting_dimensions,
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

MATERIALS = (COPPER, ALUMINUM)


class ZeppDialog(QDialog):
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
        initial_frequency_hz = (
            frequency_hz if frequency_hz is not None else ZEPP_DESIGN_FREQUENCY_HZ
        )
        radiator_m, matching_m = zepp_starting_dimensions(initial_frequency_hz)
        self.setWindowTitle(translator.t("zepp.title"))
        self.resize(*scaled_dialog_size(640, 760))

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(initial_frequency_hz / 1_000_000.0)

        self._radiator_length = QDoubleSpinBox(self)
        self._radiator_length.setDecimals(3)
        self._radiator_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._radiator_length.setValue(length_from_m(radiator_m, unit_system))

        self._matching_length = QDoubleSpinBox(self)
        self._matching_length.setDecimals(3)
        self._matching_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._matching_length.setValue(length_from_m(matching_m, unit_system))

        self._spacing = QDoubleSpinBox(self)
        self._spacing.setDecimals(3)
        self._spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._spacing.setRange(
            length_from_m(0.01, unit_system),
            length_from_m(10.0, unit_system),
        )
        self._spacing.setSingleStep(length_from_m(0.01, unit_system))
        self._spacing.setValue(length_from_m(ZEPP_DEFAULT_SPACING_M, unit_system))

        self._impedance = QLabel(self)

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._base_height.setRange(0.0, length_from_m(1_000.0, unit_system))
        self._base_height.setSingleStep(length_from_m(0.1, unit_system))
        self._base_height.setValue(length_from_m(ZEPP_DEFAULT_BASE_HEIGHT_M, unit_system))

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

        self._start = QPushButton(self)
        self._start.clicked.connect(self._apply_starting_dimensions)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        form = QFormLayout()
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("zepp.radiator_length"), self._radiator_length)
        form.addRow(translator.t("zepp.matching_length"), self._matching_length)
        form.addRow(translator.t("zepp.spacing"), self._spacing)
        form.addRow(translator.t("zepp.impedance"), self._impedance)
        form.addRow(self._start)
        form.addRow(translator.t("zepp.base_height"), self._base_height)
        form.addRow(translator.t("field.azimuth"), self._azimuth)
        form.addRow(translator.t("g5rv.wire_radius"), self._radius)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)

        hint = QLabel(translator.t("zepp.hint"), self)
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("zepp.evidence"), self)
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

        self._ground.currentIndexChanged.connect(self._update_ground_controls)
        for spin in (
            self._frequency,
            self._radiator_length,
            self._matching_length,
            self._spacing,
            self._base_height,
            self._azimuth,
            self._radius,
        ):
            spin.valueChanged.connect(self._update_geometry)
        self._update_ground_controls()
        self._update_geometry()
        self.retranslate()

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

    def _spacing_m(self) -> float:
        return length_to_m(self._spacing.value(), self._unit_system)

    def _radius_m(self) -> float:
        return radius_to_m(self._radius.value(), self._unit_system)

    def _estimated_impedance(self) -> float | None:
        try:
            return parallel_wire_impedance_ohm(self._spacing_m(), self._radius_m())
        except ValueError:
            return None

    def _apply_starting_dimensions(self) -> None:
        radiator_m, matching_m = zepp_starting_dimensions(self._frequency.value() * 1_000_000.0)
        self._radiator_length.setValue(length_from_m(radiator_m, self._unit_system))
        self._matching_length.setValue(length_from_m(matching_m, self._unit_system))

    def _update_geometry(self, *_args: object) -> None:
        unit = self._translator.t(length_unit_key(self._unit_system))
        impedance = self._estimated_impedance()
        base_height_m = length_to_m(self._base_height.value(), self._unit_system)
        top_height_m = base_height_m + length_to_m(self._matching_length.value(), self._unit_system)
        self._impedance.setText("—" if impedance is None else f"{impedance:.1f} Ω")
        self._geometry.setText(
            self._translator.t(
                "zepp.geometry",
                radiator=f"{self._radiator_length.value():.3f}",
                matching=f"{self._matching_length.value():.3f}",
                spacing=f"{self._spacing.value():.3f}",
                impedance="—" if impedance is None else f"{impedance:.1f}",
                base_height=f"{self._base_height.value():.3f}",
                top_height=f"{length_from_m(top_height_m, self._unit_system):.3f}",
                unit=unit,
            )
        )

    def parameters(self) -> CustomAntennaParameters:
        return zepp_parameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            radiator_length_m=length_to_m(self._radiator_length.value(), self._unit_system),
            matching_section_length_m=length_to_m(self._matching_length.value(), self._unit_system),
            spacing_m=self._spacing_m(),
            base_height_m=length_to_m(self._base_height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=self._radius_m(),
            material=self._selected_material(),
            ground=self._ground_model(),
        )

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("zepp.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> CustomAntennaParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters

    def retranslate(self) -> None:
        self.setWindowTitle(self._translator.t("zepp.title"))
        self._start.setText(self._translator.t("zepp.starting_dimensions"))
        self._update_geometry()
