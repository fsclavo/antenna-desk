# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for J-pole and Slim-Jim verticals."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.j_pole import JPoleParameters
from ...domain.antennas.materials import COPPER, ConductorMaterial
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..material_combo import (
    populate_template_material_combo,
    retranslate_material_combo,
)
from ..units import (
    DisplayUnits,
    LengthPolicy,
    UnitSystem,
    length_from_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
)
from .form_i18n import FormLabels, retranslate_combo
from .form_units import LengthField, LengthFieldSpec, apply_radius_units
from .ground_presets import GroundPresetController
from .sectioned_form import FormColumn, FormLayoutMode, FormRow, FormSection, SectionedForm


class JPoleForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: JPoleParameters | None = None,
        parent: QWidget | None = None,
        *,
        display_units: DisplayUnits | None = None,
        wide_layout: bool = False,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self)
        self._wide_layout = wide_layout
        self._unit_system = unit_system
        self._display_units = display_units or DisplayUnits(
            unit_system,
            LengthPolicy.FIXED,
        )
        self._updating = False

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(145.0)

        self._radiator_height = QDoubleSpinBox(self)
        self._radiator_height.setDecimals(3)
        self._radiator_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._radiator_height.setValue(length_from_m(1.0, unit_system))

        self._stub_length = QDoubleSpinBox(self)
        self._stub_length.setDecimals(3)
        self._stub_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._stub_length.setValue(length_from_m(0.5, unit_system))

        self._spacing = QDoubleSpinBox(self)
        self._spacing.setDecimals(3)
        self._spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._spacing.setValue(length_from_m(0.05, unit_system))

        self._feed_offset = QDoubleSpinBox(self)
        self._feed_offset.setDecimals(3)
        self._feed_offset.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._feed_offset.setValue(length_from_m(0.1, unit_system))

        self._gap = QDoubleSpinBox(self)
        self._gap.setDecimals(3)
        self._gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._gap.setValue(length_from_m(0.01, unit_system))

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._base_height.setValue(length_from_m(0.25, unit_system))

        self._radiator_height_field = LengthField(
            self._radiator_height,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._stub_length_field = LengthField(
            self._stub_length,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._spacing_field = LengthField(
            self._spacing,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._feed_offset_field = LengthField(
            self._feed_offset,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._gap_field = LengthField(
            self._gap,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._base_height_field = LengthField(
            self._base_height,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._radiator_height_field.configure(1.0)
        self._stub_length_field.configure(0.5)
        self._spacing_field.configure(0.05)
        self._feed_offset_field.configure(0.1)
        self._gap_field.configure(0.01)
        self._base_height_field.configure(0.25)

        self._folded = QCheckBox(translator.t("j_pole.folded"), self)

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)
        self._radius.setValue(radius_from_m(0.001, unit_system))

        self._material = QComboBox(self)
        populate_template_material_combo(self._material, translator, "j_pole")

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

        left_rows = [
            FormRow("field.frequency", self._frequency),
            FormRow("j_pole.radiator_height", self._radiator_height),
            FormRow("j_pole.stub_length", self._stub_length),
            FormRow("j_pole.spacing", self._spacing),
            FormRow("j_pole.feed_offset", self._feed_offset),
            FormRow("j_pole.gap", self._gap),
            FormRow("j_pole.base_height", self._base_height),
            FormRow(None, self._folded),
        ]
        right_rows = [
            FormRow("j_pole.wire_radius", self._radius),
            FormRow("field.material", self._material),
            FormRow("field.ground", self._ground),
            FormRow("field.soil_preset", self._soil),
            FormRow("field.permittivity", self._permittivity),
            FormRow("field.conductivity", self._conductivity),
        ]
        self._sectioned = SectionedForm(
            (
                FormSection(tuple(left_rows), column=FormColumn.LEFT),
                FormSection(tuple(right_rows), column=FormColumn.RIGHT),
            ),
            mode=FormLayoutMode.TWO_COLUMN if wide_layout else FormLayoutMode.SINGLE,
            label_factory=self._labels.label,
            target_width_px=920 if wide_layout else None,
            parent=self,
        )
        for form in self._sectioned.forms:
            self._labels.bind_form(form)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._sectioned)
        layout.addWidget(self._geometry)
        layout.addStretch(1)
        self._sectioned.apply_tab_order()

        for widget in (
            self._frequency,
            self._radiator_height,
            self._stub_length,
            self._spacing,
            self._feed_offset,
            self._gap,
            self._base_height,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._folded.toggled.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        if parameters is not None:
            self.set_parameters(parameters)
        self._update_ground_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        self._folded.setText(self._translator.t("j_pole.folded"))
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

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            parameters = None
        self._unit_system = unit_system
        self._display_units = DisplayUnits(
            unit_system,
            self._display_units.length_policy,
        )
        apply_radius_units(self._translator, unit_system, self._radius)
        for field in (
            self._radiator_height_field,
            self._stub_length_field,
            self._spacing_field,
            self._feed_offset_field,
            self._gap_field,
            self._base_height_field,
        ):
            field.set_display_units(self._display_units)
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: JPoleParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._radiator_height_field.configure(parameters.radiator_height_m)
            self._stub_length_field.configure(parameters.stub_length_m)
            self._spacing_field.configure(parameters.spacing_m)
            self._feed_offset_field.configure(parameters.feed_offset_m)
            self._gap_field.configure(parameters.gap_m)
            self._base_height_field.configure(parameters.base_height_m)
            self._folded.setChecked(parameters.folded)
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

    def _update_geometry(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "j_pole.geometry",
                template=parameters.template_name,
                height=f"{length_from_m(parameters.radiator_height_m, self._unit_system):.2f}",
                unit=unit,
            )
        )

    def parameters(self) -> JPoleParameters:
        return JPoleParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            radiator_height_m=self._radiator_height_field.value_m(),
            stub_length_m=self._stub_length_field.value_m(),
            spacing_m=self._spacing_field.value_m(),
            feed_offset_m=self._feed_offset_field.value_m(),
            gap_m=self._gap_field.value_m(),
            base_height_m=self._base_height_field.value_m(),
            folded=self._folded.isChecked(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
