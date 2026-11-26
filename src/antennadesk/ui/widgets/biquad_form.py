# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for biquad and double-biquad antennas."""

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

from ...domain.antennas.biquad import (
    BIQUAD_REFERENCE_TRANSFORMER_RATIO,
    BiquadKind,
    BiquadParameters,
    biquad_parameters,
)
from ...domain.antennas.material_defaults import default_material_for_template
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
    height_bounds,
    length_bounds,
    length_from_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
)
from .form_i18n import FormLabels, retranslate_combo
from .form_units import LengthField, LengthFieldSpec, apply_radius_units
from .ground_presets import GroundPresetController
from .sectioned_form import FormColumn, FormLayoutMode, FormRow, FormSection, SectionedForm


class BiquadForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: BiquadParameters | None = None,
        parent: QWidget | None = None,
        *,
        kind: BiquadKind = BiquadKind.SINGLE,
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
        minimum_length, maximum_length = length_bounds(unit_system)
        minimum_height, maximum_height = height_bounds(unit_system)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")

        self._kind = QComboBox(self)
        for kind_value in BiquadKind:
            self._kind.addItem(
                translator.t(f"biquad.kind.{kind_value.value}"),
                kind_value.value,
            )

        self._loop_side = QDoubleSpinBox(self)
        self._loop_side.setRange(minimum_length, maximum_length)
        self._loop_side.setDecimals(3)
        self._loop_side.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setRange(minimum_height, maximum_height)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._reflector_enabled = QCheckBox(
            translator.t("biquad.reflector_enabled"),
            self,
        )
        self._reflector_spacing = QDoubleSpinBox(self)
        self._reflector_spacing.setRange(minimum_length, maximum_length)
        self._reflector_spacing.setDecimals(3)
        self._reflector_spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._loop_side_field = LengthField(
            self._loop_side,
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
        self._reflector_spacing_field = LengthField(
            self._reflector_spacing,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)

        self._transformer = QDoubleSpinBox(self)
        self._transformer.setRange(1.0, 100_000.0)
        self._transformer.setDecimals(1)
        self._transformer.setSuffix(":1")
        self._transformer.setValue(BIQUAD_REFERENCE_TRANSFORMER_RATIO)

        self._material = QComboBox(self)
        populate_template_material_combo(self._material, translator, "biquad")

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
        self._transformer_hint = QLabel(translator.t("biquad.transformer_hint"), self)
        self._transformer_hint.setWordWrap(True)

        left_rows = [
            FormRow("field.frequency", self._frequency),
            FormRow("biquad.kind", self._kind),
            FormRow("biquad.loop_side", self._loop_side),
            FormRow("field.base_height", self._base_height),
            FormRow(None, self._reflector_enabled),
            FormRow("biquad.reflector_spacing", self._reflector_spacing),
        ]
        right_rows = [
            FormRow("field.azimuth", self._azimuth),
            FormRow("field.wire_radius", self._radius),
            FormRow("field.material", self._material),
            FormRow("field.ground", self._ground),
            FormRow("field.soil_preset", self._soil),
            FormRow("field.permittivity", self._permittivity),
            FormRow("field.conductivity", self._conductivity),
            FormRow("biquad.transformer_ratio", self._transformer),
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
        layout.addWidget(self._transformer_hint)
        layout.addWidget(self._geometry)
        layout.addStretch(1)
        self._sectioned.apply_tab_order()

        for widget in (
            self._frequency,
            self._loop_side,
            self._base_height,
            self._reflector_spacing,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
            self._transformer,
        ):
            widget.valueChanged.connect(self._emit_changed)
        for combo in (self._kind, self._material):
            combo.currentIndexChanged.connect(self._emit_changed)
        self._reflector_enabled.toggled.connect(self._reflector_toggled)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        initial = parameters or biquad_parameters(
            kind,
            frequency_hz=14_100_000.0,
            material=default_material_for_template("biquad"),
            ground=GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            ),
        )
        self.set_parameters(initial)
        self._update_ground_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        retranslate_combo(
            self._kind,
            self._translator,
            tuple(f"biquad.kind.{kind.value}" for kind in BiquadKind),
        )
        self._reflector_enabled.setText(self._translator.t("biquad.reflector_enabled"))
        self._transformer_hint.setText(self._translator.t("biquad.transformer_hint"))
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

    def _reflector_toggled(self, *_args: object) -> None:
        self._update_reflector_controls()
        self._emit_changed()

    def _update_reflector_controls(self) -> None:
        self._reflector_spacing.setEnabled(self._reflector_enabled.isChecked())

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

    def _selected_kind(self) -> BiquadKind:
        value = self._kind.currentData()
        return BiquadKind(value) if isinstance(value, str) else BiquadKind.SINGLE

    def load_starting_dimensions(self) -> None:
        """Reload the quarter-wave side and eighth-wave spacing."""

        try:
            current = self.parameters()
        except (ValueError, TypeError):
            current = biquad_parameters(
                self._selected_kind(),
                material=self._selected_material(),
            )
        starting = biquad_parameters(
            current.kind,
            frequency_hz=current.frequency_hz,
            base_height_m=current.base_height_m,
            azimuth_deg=current.azimuth_deg,
            reflector_enabled=current.reflector_enabled,
            wire_radius_m=current.wire_radius_m,
            material=current.material,
            ground=current.ground,
            transformer_ratio=current.transformer_ratio,
        )
        self.set_parameters(starting)
        self.changed.emit()

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
        previous_updating = self._updating
        self._updating = True
        try:
            apply_radius_units(self._translator, unit_system, self._radius)
            self._loop_side_field.set_display_units(self._display_units)
            self._base_height_field.set_display_units(self._display_units)
            self._reflector_spacing_field.set_display_units(self._display_units)
        finally:
            self._updating = previous_updating
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: BiquadParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            kind_index = self._kind.findData(parameters.kind.value)
            if kind_index >= 0:
                self._kind.setCurrentIndex(kind_index)
            self._loop_side_field.configure(parameters.loop_side_m)
            self._base_height_field.configure(parameters.base_height_m)
            self._reflector_enabled.setChecked(parameters.reflector_enabled)
            self._reflector_spacing_field.configure(parameters.reflector_spacing_m)
            self._azimuth.setValue(parameters.azimuth_deg)
            self._radius.setValue(radius_from_m(parameters.wire_radius_m, self._unit_system))
            self._transformer.setValue(parameters.transformer_ratio)
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
        self._update_reflector_controls()
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
        reflector = (
            f"{length_from_m(parameters.reflector_spacing_m, self._unit_system):.3f} {unit}"
            if parameters.reflector_enabled
            else self._translator.t("biquad.reflector_off")
        )
        self._geometry.setText(
            self._translator.t(
                "biquad.geometry",
                loops=parameters.loop_count,
                side=f"{length_from_m(parameters.loop_side_m, self._unit_system):.3f}",
                height=f"{length_from_m(parameters.total_height_m, self._unit_system):.3f}",
                base=f"{length_from_m(parameters.base_height_m, self._unit_system):.3f}",
                reflector=reflector,
                unit=unit,
            )
        )

    def parameters(self) -> BiquadParameters:
        return BiquadParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            loop_side_m=self._loop_side_field.value_m(),
            reflector_spacing_m=self._reflector_spacing_field.value_m(),
            kind=self._selected_kind(),
            base_height_m=self._base_height_field.value_m(),
            reflector_enabled=self._reflector_enabled.isChecked(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
            transformer_ratio=self._transformer.value(),
        )
