# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a half-wave Flower Pot coax vertical."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.flower_pot import (
    FLOWER_POT_2M_BOTTOM_LENGTH_M,
    FLOWER_POT_2M_CHOKE_HEIGHT_M,
    FLOWER_POT_2M_FREQUENCY_HZ,
    FLOWER_POT_2M_TOP_LENGTH_M,
    FLOWER_POT_6M_BOTTOM_LENGTH_M,
    FLOWER_POT_6M_CHOKE_HEIGHT_M,
    FLOWER_POT_6M_FREQUENCY_HZ,
    FLOWER_POT_6M_TOP_LENGTH_M,
    FLOWER_POT_CONSTRUCTION_SHORTENING_FACTOR,
    FLOWER_POT_DEFAULT_BASE_HEIGHT_M,
    FLOWER_POT_DEFAULT_BOTTOM_RADIUS_M,
    FLOWER_POT_DEFAULT_TOP_RADIUS_M,
    FLOWER_POT_ELECTRICAL_LENGTH_SCALE,
    FlowerPotParameters,
)
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
from .form_layout import configure_form_layout
from .form_units import LengthField, LengthFieldSpec, apply_radius_units
from .ground_presets import GroundPresetController


class FlowerPotForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: FlowerPotParameters | None = None,
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
        self._electrical_length_scale = FLOWER_POT_ELECTRICAL_LENGTH_SCALE

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(FLOWER_POT_2M_FREQUENCY_HZ / 1_000_000.0)

        self._top_length = QDoubleSpinBox(self)
        self._top_length.setDecimals(3)
        self._top_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._bottom_length = QDoubleSpinBox(self)
        self._bottom_length.setDecimals(3)
        self._bottom_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._base_height = QDoubleSpinBox(self)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._choke_height = QDoubleSpinBox(self)
        self._choke_height.setDecimals(3)
        self._choke_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._top_length_field = LengthField(
            self._top_length,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._bottom_length_field = LengthField(
            self._bottom_length,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._base_height_field = LengthField(
            self._base_height,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._choke_height_field = LengthField(
            self._choke_height,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._top_length_field.configure(FLOWER_POT_2M_TOP_LENGTH_M)
        self._bottom_length_field.configure(FLOWER_POT_2M_BOTTOM_LENGTH_M)
        self._base_height_field.configure(FLOWER_POT_DEFAULT_BASE_HEIGHT_M)
        self._choke_height_field.configure(FLOWER_POT_2M_CHOKE_HEIGHT_M)

        self._construction_factor = QDoubleSpinBox(self)
        self._construction_factor.setRange(0.5, 1.0)
        self._construction_factor.setDecimals(3)
        self._construction_factor.setSingleStep(0.001)
        self._construction_factor.setValue(FLOWER_POT_CONSTRUCTION_SHORTENING_FACTOR)

        self._top_radius = QDoubleSpinBox(self)
        self._bottom_radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._top_radius, self._bottom_radius)
        self._top_radius.setValue(radius_from_m(FLOWER_POT_DEFAULT_TOP_RADIUS_M, unit_system))
        self._bottom_radius.setValue(radius_from_m(FLOWER_POT_DEFAULT_BOTTOM_RADIUS_M, unit_system))

        self._material = QComboBox(self)
        populate_template_material_combo(self._material, translator, "flower_pot")

        self._ground = QComboBox(self)
        self._ground.addItem("", GroundKind.FREE_SPACE.value)
        self._ground.addItem("", GroundKind.PERFECT.value)
        self._ground.addItem("", GroundKind.FINITE.value)
        self._ground.setItemText(0, translator.t("ground.free_space"))
        self._ground.setItemText(1, translator.t("ground.perfect"))
        self._ground.setItemText(2, translator.t("ground.finite"))
        self._ground.setCurrentIndex(0)

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
        self._model_note = QLabel(translator.t("flower_pot.model_note"))
        self._model_note.setWordWrap(True)

        form = QFormLayout()
        configure_form_layout(form)
        form.addRow(self._labels.label("field.frequency"), self._frequency)
        form.addRow(self._labels.label("flower_pot.top_length"), self._top_length)
        form.addRow(self._labels.label("flower_pot.bottom_length"), self._bottom_length)
        form.addRow(self._labels.label("flower_pot.base_height"), self._base_height)
        form.addRow(self._labels.label("flower_pot.choke_height"), self._choke_height)
        form.addRow(
            self._labels.label("flower_pot.construction_factor"),
            self._construction_factor,
        )
        form.addRow(self._labels.label("flower_pot.top_radius"), self._top_radius)
        form.addRow(self._labels.label("flower_pot.bottom_radius"), self._bottom_radius)
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
        layout.addWidget(self._model_note)

        for widget in (
            self._frequency,
            self._top_length,
            self._bottom_length,
            self._base_height,
            self._construction_factor,
            self._top_radius,
            self._bottom_radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        if parameters is not None:
            self.set_parameters(parameters)
        self._update_ground_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        retranslate_material_combo(self._material, self._translator)
        retranslate_combo(
            self._ground,
            self._translator,
            ("ground.free_space", "ground.perfect", "ground.finite"),
        )
        self._model_note.setText(self._translator.t("flower_pot.model_note"))
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

    def load_2m_example(self) -> None:
        """Load the published 2 m physical cut row."""

        self._load_row(
            FLOWER_POT_2M_FREQUENCY_HZ,
            FLOWER_POT_2M_TOP_LENGTH_M,
            FLOWER_POT_2M_BOTTOM_LENGTH_M,
            FLOWER_POT_2M_CHOKE_HEIGHT_M,
        )

    def load_6m_example(self) -> None:
        """Load the published 6 m physical cut row."""

        self._load_row(
            FLOWER_POT_6M_FREQUENCY_HZ,
            FLOWER_POT_6M_TOP_LENGTH_M,
            FLOWER_POT_6M_BOTTOM_LENGTH_M,
            FLOWER_POT_6M_CHOKE_HEIGHT_M,
        )

    def _load_row(
        self,
        frequency_hz: float,
        top_length_m: float,
        bottom_length_m: float,
        choke_height_m: float,
    ) -> None:
        self._updating = True
        try:
            self._frequency.setValue(frequency_hz / 1_000_000.0)
            self._top_length_field.configure(top_length_m)
            self._bottom_length_field.configure(bottom_length_m)
            self._base_height_field.configure(FLOWER_POT_DEFAULT_BASE_HEIGHT_M)
            self._choke_height_field.configure(choke_height_m)
        finally:
            self._updating = False
        self._update_geometry()
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
        apply_radius_units(
            self._translator,
            unit_system,
            self._top_radius,
            self._bottom_radius,
        )
        self._top_length_field.set_display_units(self._display_units)
        self._bottom_length_field.set_display_units(self._display_units)
        self._base_height_field.set_display_units(self._display_units)
        self._choke_height_field.set_display_units(self._display_units)
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: FlowerPotParameters) -> None:
        self._updating = True
        try:
            self._electrical_length_scale = parameters.electrical_length_scale
            self._construction_factor.setValue(parameters.construction_shortening_factor)
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._top_length_field.configure(parameters.top_length_m)
            self._bottom_length_field.configure(parameters.bottom_length_m)
            self._base_height_field.configure(parameters.base_height_m)
            self._choke_height_field.configure(parameters.choke_height_m)
            self._top_radius.setValue(radius_from_m(parameters.top_radius_m, self._unit_system))
            self._bottom_radius.setValue(
                radius_from_m(parameters.bottom_radius_m, self._unit_system)
            )
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
        physical = length_from_m(parameters.physical_total_length_m, self._unit_system)
        electrical = length_from_m(parameters.electrical_total_length_m, self._unit_system)
        feed = length_from_m(parameters.physical_feed_height_m, self._unit_system)
        choke = length_from_m(parameters.choke_height_m, self._unit_system)
        self._geometry.setText(
            self._translator.t(
                "flower_pot.geometry",
                physical=f"{physical:.2f}",
                electrical=f"{electrical:.2f}",
                feed=f"{feed:.2f}",
                choke=f"{choke:.2f}",
                unit=unit,
            )
        )

    def parameters(self) -> FlowerPotParameters:
        return FlowerPotParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            top_length_m=self._top_length_field.value_m(),
            bottom_length_m=self._bottom_length_field.value_m(),
            top_radius_m=radius_to_m(self._top_radius.value(), self._unit_system),
            bottom_radius_m=radius_to_m(self._bottom_radius.value(), self._unit_system),
            base_height_m=self._base_height_field.value_m(),
            choke_height_m=self._choke_height_field.value_m(),
            construction_shortening_factor=self._construction_factor.value(),
            electrical_length_scale=self._electrical_length_scale,
            material=self._selected_material(),
            ground=self._ground_model(),
        )
