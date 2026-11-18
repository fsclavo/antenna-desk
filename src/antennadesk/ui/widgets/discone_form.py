# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for discone antennas."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.discone import (
    MAX_WIRES,
    MIN_WIRES,
    DisconeParameters,
    discone_parameters,
)
from ...domain.antennas.material_defaults import default_material_for_template
from ...domain.antennas.materials import COPPER, ConductorMaterial
from ...domain.environment.ground import GroundKind, GroundModel
from ..help import apply_help
from ..i18n import Translator
from ..material_combo import (
    populate_template_material_combo,
    retranslate_material_combo,
)
from ..units import (
    DisplayUnits,
    LengthPolicy,
    UnitSystem,
    height_bounds,
    length_bounds,
    length_from_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
)
from .form_i18n import FormLabels, retranslate_combo
from .form_units import (
    LengthField,
    LengthFieldSpec,
    apply_radius_units,
)
from .ground_presets import GroundPresetController
from .starting_dimensions import StartingDimensionsState


class DisconeForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: DisconeParameters | None = None,
        parent: QWidget | None = None,
        *,
        display_units: DisplayUnits | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self)
        self._unit_system = unit_system
        self._display_units = display_units or DisplayUnits(
            unit_system,
            LengthPolicy.FIXED,
        )
        self._updating = False
        minimum_length, maximum_length = length_bounds(unit_system)
        minimum_height, maximum_height = height_bounds(unit_system)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")

        self._cone_height = QDoubleSpinBox(self)
        self._cone_height.setRange(minimum_height, maximum_height)
        self._cone_height.setDecimals(3)
        self._cone_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._cone_radius = QDoubleSpinBox(self)
        self._cone_radius.setRange(minimum_length, maximum_length)
        self._cone_radius.setDecimals(3)
        self._cone_radius.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._disc_radius = QDoubleSpinBox(self)
        self._disc_radius.setRange(minimum_length, maximum_length)
        self._disc_radius.setDecimals(3)
        self._disc_radius.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setRange(minimum_height, maximum_height)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._disc_gap = QDoubleSpinBox(self)
        self._disc_gap.setRange(minimum_length, maximum_length)
        self._disc_gap.setDecimals(4)
        self._disc_gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._cone_height_field = LengthField(
            self._cone_height,
            LengthFieldSpec(minimum_m=0.0001, maximum_m=10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._cone_radius_field = LengthField(
            self._cone_radius,
            LengthFieldSpec(minimum_m=0.0001, maximum_m=10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._disc_radius_field = LengthField(
            self._disc_radius,
            LengthFieldSpec(minimum_m=0.0001, maximum_m=10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._base_height_field = LengthField(
            self._base_height,
            LengthFieldSpec(minimum_m=0.0, maximum_m=10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._disc_gap_field = LengthField(
            self._disc_gap,
            LengthFieldSpec(minimum_m=0.0001, maximum_m=10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )

        self._wire_count = QSpinBox(self)
        self._wire_count.setRange(MIN_WIRES, MAX_WIRES)

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)

        self._material = QComboBox(self)
        populate_template_material_combo(self._material, translator, "discone")

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

        self._starting = QPushButton(
            translator.t("action.load_starting_dimensions"),
            self,
        )
        self._starting.clicked.connect(self.load_starting_dimensions)
        apply_help(self._starting, translator, "load_starting", family="discone")
        self._starting_note = QLabel(self)
        self._starting_note.setWordWrap(True)
        self._starting_note.setStyleSheet("font-style: italic;")
        self._starting_note.setVisible(False)
        self._starting_state = StartingDimensionsState(translator, self._starting_note)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        form = QFormLayout()
        form.addRow(self._labels.label("field.frequency"), self._frequency)
        form.addRow(self._starting)
        form.addRow(self._labels.label("discone.cone_height"), self._cone_height)
        form.addRow(self._labels.label("discone.cone_radius"), self._cone_radius)
        form.addRow(self._labels.label("discone.disc_radius"), self._disc_radius)
        form.addRow(self._labels.label("field.base_height"), self._base_height)
        form.addRow(self._labels.label("discone.disc_gap"), self._disc_gap)
        form.addRow(self._labels.label("discone.wire_count"), self._wire_count)
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
        layout.addWidget(self._starting_note)

        self._frequency.valueChanged.connect(self._frequency_changed)
        for widget in (
            self._cone_height,
            self._cone_radius,
            self._disc_radius,
        ):
            widget.valueChanged.connect(self._managed_field_changed)
        for widget in (
            self._base_height,
            self._disc_gap,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._wire_count.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        initial = parameters or discone_parameters(
            frequency_hz=145_000_000.0,
            material=default_material_for_template("discone"),
            ground=GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            ),
        )
        self.set_parameters(initial)
        if parameters is None:
            self.mark_starting_dimensions_pristine()
        self._update_ground_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        self._starting.setText(self._translator.t("action.load_starting_dimensions"))
        apply_help(self._starting, self._translator, "load_starting", family="discone")
        self._starting_state.retranslate()
        retranslate_material_combo(self._material, self._translator)
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

    def _frequency_changed(self, _value: float) -> None:
        if self._updating:
            return
        if self._starting_state.pristine:
            try:
                self.load_starting_dimensions()
            except (ValueError, TypeError):
                self._starting_state.show_stale(self._frequency.value())
                self._emit_changed()
            return
        self._starting_state.show_stale(self._frequency.value())
        self._emit_changed()

    def _managed_field_changed(self, *_args: object) -> None:
        if self._updating:
            return
        self._starting_state.mark_non_pristine()
        self._emit_changed()

    def mark_starting_dimensions_pristine(self) -> None:
        self._starting_state.mark_pristine()

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

    def load_starting_dimensions(self) -> None:
        current = self.parameters()
        self.set_parameters(
            discone_parameters(
                frequency_hz=current.frequency_hz,
                base_height_m=current.base_height_m,
                disc_gap_m=current.disc_gap_m,
                wire_count=current.wire_count,
                azimuth_deg=current.azimuth_deg,
                wire_radius_m=current.wire_radius_m,
                material=current.material,
                ground=current.ground,
            )
        )
        self._starting_state.mark_pristine(frequency_mhz=self._frequency.value())
        self.changed.emit()

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        was_pristine = self._starting_state.pristine
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            parameters = None
        self._unit_system = unit_system
        self._display_units = DisplayUnits(
            unit_system,
            self._display_units.length_policy,
        )
        previous_updating = self._updating
        self._updating = True
        try:
            apply_radius_units(self._translator, unit_system, self._radius)
            self._cone_height_field.set_display_units(self._display_units)
            self._cone_radius_field.set_display_units(self._display_units)
            self._disc_radius_field.set_display_units(self._display_units)
            self._base_height_field.set_display_units(self._display_units)
            self._disc_gap_field.set_display_units(self._display_units)
        finally:
            self._updating = previous_updating
        if parameters is not None:
            self.set_parameters(parameters)
            if was_pristine:
                self.mark_starting_dimensions_pristine()

    def set_parameters(self, parameters: DisconeParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._cone_height_field.configure(parameters.cone_height_m)
            self._cone_radius_field.configure(parameters.cone_radius_m)
            self._disc_radius_field.configure(parameters.disc_radius_m)
            self._base_height_field.configure(parameters.base_height_m)
            self._disc_gap_field.configure(parameters.disc_gap_m)
            self._wire_count.setValue(parameters.wire_count)
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
        self._starting_state.mark_non_pristine()
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
        self._geometry.setText(
            self._translator.t(
                "discone.geometry",
                height=f"{length_from_m(parameters.cone_height_m, self._unit_system):.3f}",
                radius=f"{length_from_m(parameters.cone_radius_m, self._unit_system):.3f}",
                disc=f"{length_from_m(parameters.disc_radius_m, self._unit_system):.3f}",
                count=parameters.wire_count,
                unit=unit,
            )
        )

    def parameters(self) -> DisconeParameters:
        return DisconeParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            cone_height_m=self._cone_height_field.value_m(),
            cone_radius_m=self._cone_radius_field.value_m(),
            disc_radius_m=self._disc_radius_field.value_m(),
            base_height_m=self._base_height_field.value_m(),
            disc_gap_m=self._disc_gap_field.value_m(),
            wire_count=self._wire_count.value(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
