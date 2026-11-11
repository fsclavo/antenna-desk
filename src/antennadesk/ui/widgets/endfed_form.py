# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for an end-fed wire."""

from __future__ import annotations

import math
from dataclasses import replace

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.endfed import (
    DEFAULT_BEND_VERTICAL_LENGTH_M,
    DEFAULT_FEED_SECTION_LENGTH_M,
    DEFAULT_INSTALLATION_RETURN_LENGTH_M,
    EFHW_PRESET_LENGTHS_M,
    EndFedParameters,
    EndFedPreset,
    efhw_parameters,
    endfed_model_warning_keys,
    shortened_efhw_40_10_parameters,
    shortened_efhw_80_10_parameters,
)
from ...domain.antennas.matching_network import MatchingNetwork
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.design.formulas import half_wave_length_m
from ...domain.design.matching_resolution import resolve_matching_network
from ...domain.environment.ground import GroundKind, GroundModel
from ..help import apply_help
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


class EndFedForm(QWidget):
    changed = Signal()
    matching_network_edit_requested = Signal()
    matching_network_remove_requested = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: EndFedParameters | None = None,
        parent: QWidget | None = None,
        *,
        preset: EndFedPreset = EndFedPreset.STANDARD,
        show_override_actions: bool = True,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self)
        self._unit_system = unit_system
        self._updating = False
        self._preset = EndFedPreset(preset)
        self._project_matching_network: MatchingNetwork | None = None
        self._show_override_actions = show_override_actions

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(7.1)

        self._length = QDoubleSpinBox(self)
        self._length.setDecimals(3)
        self._length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._length.setValue(length_from_m(20.0, unit_system))

        self._feed_section = QDoubleSpinBox(self)
        self._feed_section.setRange(0.0, 100_000.0)
        self._feed_section.setDecimals(3)
        self._feed_section.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._feed_section.setValue(length_from_m(DEFAULT_FEED_SECTION_LENGTH_M, unit_system))
        self._feed_section.setToolTip(translator.t("endfed.feed_section_hint"))

        self._feed_height = QDoubleSpinBox(self)
        self._feed_height.setDecimals(3)
        self._feed_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._feed_height.setValue(length_from_m(10.0, unit_system))

        self._end_height = QDoubleSpinBox(self)
        self._end_height.setDecimals(3)
        self._end_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._end_height.setValue(length_from_m(10.0, unit_system))

        self._bend_enabled = QCheckBox(translator.t("endfed.bend_enabled"), self)
        self._bend_enabled.setChecked(False)
        self._bend_vertical = QDoubleSpinBox(self)
        self._bend_vertical.setRange(0.0, 100_000.0)
        self._bend_vertical.setDecimals(3)
        self._bend_vertical.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._bend_vertical.setValue(length_from_m(DEFAULT_BEND_VERTICAL_LENGTH_M, unit_system))
        self._bend_horizontal = QLabel(self)
        self._bend_horizontal.setWordWrap(True)

        self._transformer = QDoubleSpinBox(self)
        self._transformer.setRange(1.0, 100_000.0)
        self._transformer.setDecimals(1)
        self._transformer.setValue(49.0)
        self._transformer.setSuffix(":1")

        self._matching_capacitance = QDoubleSpinBox(self)
        self._matching_capacitance.setRange(0.0, 100_000.0)
        self._matching_capacitance.setDecimals(2)
        self._matching_capacitance.setSuffix(" pF")
        self._matching_capacitance.setValue(0.0)
        self._matching_capacitance.setToolTip(translator.t("endfed.matching_capacitance_hint"))

        self._transformer_leakage = QDoubleSpinBox(self)
        self._transformer_leakage.setRange(0.0, 100_000.0)
        self._transformer_leakage.setDecimals(3)
        self._transformer_leakage.setSuffix(" µH")
        self._transformer_leakage.setValue(0.0)
        self._transformer_leakage.setToolTip(translator.t("endfed.transformer_leakage_hint"))

        self._matching_override = QLabel(self)
        self._matching_override.setWordWrap(True)
        self._matching_override.setStyleSheet("color: #8a5a00;")
        self._matching_override_edit = QPushButton(self)
        self._matching_override_edit.setFlat(True)
        self._matching_override_edit.clicked.connect(self.matching_network_edit_requested)
        self._matching_override_remove = QPushButton(self)
        self._matching_override_remove.setFlat(True)
        self._matching_override_remove.clicked.connect(self.matching_network_remove_requested)
        self._matching_override_actions = QWidget(self)
        matching_override_actions = QHBoxLayout(self._matching_override_actions)
        matching_override_actions.setContentsMargins(0, 0, 0, 0)
        matching_override_actions.addWidget(self._matching_override_edit)
        matching_override_actions.addWidget(self._matching_override_remove)
        matching_override_actions.addStretch(1)
        self._matching_override_widget = QWidget(self)
        matching_override_layout = QVBoxLayout(self._matching_override_widget)
        matching_override_layout.setContentsMargins(0, 0, 0, 0)
        matching_override_layout.addWidget(self._matching_override)
        matching_override_layout.addWidget(self._matching_override_actions)
        self._matching_override_widget.setVisible(False)

        self._loading_coil_group = QGroupBox(translator.t("endfed.loading_coil"), self)
        self._loading_coil_group.setCheckable(True)
        self._loading_coil_group.setChecked(False)
        coil_form = QFormLayout(self._loading_coil_group)
        self._loading_coil_offset = QDoubleSpinBox(self._loading_coil_group)
        self._loading_coil_offset.setDecimals(3)
        self._loading_coil_offset.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._loading_coil_offset.setRange(0.0, 100_000.0)
        self._loading_coil_inductance = QDoubleSpinBox(self._loading_coil_group)
        self._loading_coil_inductance.setRange(0.0, 1_000_000.0)
        self._loading_coil_inductance.setDecimals(3)
        self._loading_coil_inductance.setSuffix(" µH")
        self._loading_coil_resistance = QDoubleSpinBox(self._loading_coil_group)
        self._loading_coil_resistance.setRange(0.0, 10_000.0)
        self._loading_coil_resistance.setDecimals(3)
        self._loading_coil_resistance.setSuffix(" Ω")
        self._loading_coil_q = QLabel(self._loading_coil_group)
        coil_form.addRow(
            self._labels.label("endfed.loading_coil_offset"),
            self._loading_coil_offset,
        )
        coil_form.addRow(
            self._labels.label("endfed.loading_coil_inductance"),
            self._loading_coil_inductance,
        )
        coil_form.addRow(
            self._labels.label("endfed.loading_coil_resistance"),
            self._loading_coil_resistance,
        )
        coil_form.addRow(
            self._labels.label("endfed.loading_coil_q"),
            self._loading_coil_q,
        )

        self._counterpoise_enabled = QCheckBox(translator.t("endfed.counterpoise_enabled"), self)
        self._counterpoise_enabled.setChecked(False)

        self._counterpoise_length = QDoubleSpinBox(self)
        self._counterpoise_length.setRange(0.0, 100_000.0)
        self._counterpoise_length.setDecimals(3)
        self._counterpoise_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._counterpoise_length.setValue(0.0)

        self._counterpoise_height = QDoubleSpinBox(self)
        self._counterpoise_height.setRange(0.0, 100_000.0)
        self._counterpoise_height.setDecimals(3)
        self._counterpoise_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._counterpoise_height.setValue(length_from_m(0.1, unit_system))

        self._counterpoise_azimuth = QDoubleSpinBox(self)
        self._counterpoise_azimuth.setRange(0.0, 360.0)
        self._counterpoise_azimuth.setDecimals(1)
        self._counterpoise_azimuth.setSuffix("°")
        self._counterpoise_azimuth.setValue(180.0)

        self._installation_return = QDoubleSpinBox(self)
        self._installation_return.setRange(0.0, 100_000.0)
        self._installation_return.setDecimals(3)
        self._installation_return.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._installation_return.setValue(
            length_from_m(DEFAULT_INSTALLATION_RETURN_LENGTH_M, unit_system)
        )
        self._installation_return.setToolTip(translator.t("endfed.installation_return_hint"))

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
        self._soil = QComboBox(self)
        self._ground_presets = GroundPresetController(
            self._ground,
            self._soil,
            self._permittivity,
            self._conductivity,
            translator,
        )

        self._preset_label = QLabel(self)
        self._efhw_label = QLabel(translator.t("endfed.efhw_presets"), self)
        self._efhw_widget = QWidget(self)
        efhw_layout = QHBoxLayout(self._efhw_widget)
        efhw_layout.setContentsMargins(0, 0, 0, 0)
        efhw_layout.addWidget(self._efhw_label, 1)
        self._efhw_buttons: dict[str, QPushButton] = {}
        for band_id in EFHW_PRESET_LENGTHS_M:
            button = QPushButton(band_id, self._efhw_widget)
            button.clicked.connect(
                lambda _checked=False, band=band_id: self._load_efhw_preset(band)
            )
            efhw_layout.addWidget(button)
            self._efhw_buttons[band_id] = button
        self._shortened_label = QLabel(translator.t("endfed.shortened_presets"), self)
        self._shortened_widget = QWidget(self)
        shortened_layout = QHBoxLayout(self._shortened_widget)
        shortened_layout.setContentsMargins(0, 0, 0, 0)
        shortened_layout.addWidget(self._shortened_label, 1)
        self._shortened_buttons: dict[EndFedPreset, QPushButton] = {}
        for preset, label_key in (
            (EndFedPreset.SHORTENED_80_10, "endfed.preset.shortened_80_10"),
            (EndFedPreset.SHORTENED_40_10, "endfed.preset.shortened_40_10"),
        ):
            button = QPushButton(translator.t(label_key), self._shortened_widget)
            button.clicked.connect(
                lambda _checked=False, value=preset: self._load_shortened_preset(value)
            )
            shortened_layout.addWidget(button)
            self._shortened_buttons[preset] = button
        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)
        self._model_warning = QLabel(self)
        self._model_warning.setWordWrap(True)
        self._model_warning.setStyleSheet("color: #8a5a00;")
        self._installation_return_hint = QLabel(
            translator.t("endfed.installation_return_hint"),
            self,
        )
        self._installation_return_hint.setWordWrap(True)

        if parameters is None:
            self._apply_preset_defaults()

        form = QFormLayout()
        form.addRow(self._labels.label("field.template"), self._preset_label)
        form.addRow(self._labels.label("field.design_frequency"), self._frequency)
        form.addRow(self._labels.label("field.length"), self._length)
        form.addRow(self._labels.label("endfed.feed_section"), self._feed_section)
        form.addRow(self._labels.label("endfed.feed_height"), self._feed_height)
        form.addRow(self._labels.label("endfed.end_height"), self._end_height)
        form.addRow(self._bend_enabled)
        form.addRow(self._labels.label("endfed.bend_vertical"), self._bend_vertical)
        form.addRow(self._labels.label("endfed.bend_horizontal"), self._bend_horizontal)
        form.addRow(self._labels.label("endfed.transformer_ratio"), self._transformer)
        form.addRow(
            self._labels.label("endfed.matching_capacitance"),
            self._matching_capacitance,
        )
        form.addRow(
            self._labels.label("endfed.transformer_leakage"),
            self._transformer_leakage,
        )
        form.addRow(self._matching_override_widget)
        form.addRow(self._loading_coil_group)
        form.addRow(self._counterpoise_enabled)
        form.addRow(self._labels.label("endfed.counterpoise_length"), self._counterpoise_length)
        form.addRow(self._labels.label("endfed.counterpoise_height"), self._counterpoise_height)
        form.addRow(
            self._labels.label("endfed.counterpoise_azimuth"),
            self._counterpoise_azimuth,
        )
        form.addRow(self._labels.label("endfed.installation_return"), self._installation_return)
        form.addRow(self._installation_return_hint)
        form.addRow(self._labels.label("field.azimuth"), self._azimuth)
        form.addRow(self._labels.label("endfed.wire_radius"), self._radius)
        form.addRow(self._labels.label("field.material"), self._material)
        form.addRow(self._labels.label("field.ground"), self._ground)
        form.addRow(self._labels.label("field.soil_preset"), self._soil)
        form.addRow(self._labels.label("field.permittivity"), self._permittivity)
        form.addRow(self._labels.label("field.conductivity"), self._conductivity)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._labels.bind_form(form)
        layout.addLayout(form)
        layout.addWidget(self._efhw_widget)
        layout.addWidget(self._shortened_widget)
        layout.addWidget(self._geometry)
        layout.addWidget(self._model_warning)

        for widget in (
            self._frequency,
            self._length,
            self._feed_section,
            self._feed_height,
            self._end_height,
            self._bend_vertical,
            self._transformer,
            self._matching_capacitance,
            self._transformer_leakage,
            self._loading_coil_offset,
            self._loading_coil_inductance,
            self._loading_coil_resistance,
            self._counterpoise_length,
            self._counterpoise_height,
            self._counterpoise_azimuth,
            self._installation_return,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._loading_coil_group.toggled.connect(self._loading_coil_toggled)
        self._bend_enabled.toggled.connect(self._bend_toggled)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        self._counterpoise_length.valueChanged.connect(self._counterpoise_changed)
        self._counterpoise_enabled.toggled.connect(self._counterpoise_toggled)
        if parameters is not None:
            self.set_parameters(parameters)
        else:
            self._update_preset_label()
        self._update_ground_controls()
        self._update_counterpoise_controls()
        self._update_loading_coil_controls()
        self._update_efhw_visibility()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        self._counterpoise_enabled.setText(self._translator.t("endfed.counterpoise_enabled"))
        self._installation_return_hint.setText(
            self._translator.t("endfed.installation_return_hint")
        )
        self._feed_section.setToolTip(self._translator.t("endfed.feed_section_hint"))
        self._installation_return.setToolTip(self._translator.t("endfed.installation_return_hint"))
        self._bend_enabled.setText(self._translator.t("endfed.bend_enabled"))
        self._bend_vertical.setToolTip(self._translator.t("endfed.bend_vertical_hint"))
        apply_help(self._bend_enabled, self._translator, "endfed.bend_enabled")
        apply_help(self._bend_vertical, self._translator, "endfed.bend_vertical")
        self._matching_capacitance.setToolTip(
            self._translator.t("endfed.matching_capacitance_hint")
        )
        self._transformer_leakage.setToolTip(self._translator.t("endfed.transformer_leakage_hint"))
        self._matching_override.setText(self._translator.t("endfed.matching_override"))
        self._matching_override_edit.setText(self._translator.t("feed_matching.edit"))
        self._matching_override_remove.setText(self._translator.t("feed_matching.remove"))
        apply_help(self._matching_override, self._translator, "feed_matching.override")
        apply_help(
            self._matching_override_edit,
            self._translator,
            "action.matching_network",
        )
        apply_help(
            self._matching_override_remove,
            self._translator,
            "feed_matching.remove",
        )
        self._efhw_label.setText(self._translator.t("endfed.efhw_presets"))
        self._shortened_label.setText(self._translator.t("endfed.shortened_presets"))
        self._loading_coil_group.setTitle(self._translator.t("endfed.loading_coil"))
        self._shortened_buttons[EndFedPreset.SHORTENED_80_10].setText(
            self._translator.t("endfed.preset.shortened_80_10")
        )
        self._shortened_buttons[EndFedPreset.SHORTENED_40_10].setText(
            self._translator.t("endfed.preset.shortened_40_10")
        )
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
        self._update_preset_label()
        self._update_efhw_visibility()
        self._update_geometry()

    def _update_preset_label(self) -> None:
        self._preset_label.setText(self._translator.t(f"endfed.preset.{self._preset.value}"))

    def _apply_preset_defaults(self) -> None:
        if self._preset is EndFedPreset.STANDARD:
            self._update_preset_label()
            return
        if self._preset in {
            EndFedPreset.SHORTENED_80_10,
            EndFedPreset.SHORTENED_40_10,
        }:
            self.set_parameters(self._shortened_parameters(self._preset))
            return
        frequency_hz = self._frequency.value() * 1_000_000.0
        wavelength_m = 299_792_458.0 / frequency_hz
        if self._preset is EndFedPreset.SLOPER:
            length_m = half_wave_length_m(frequency_hz)
            feed_height_m = 10.0
            end_height_m = max(feed_height_m - min(0.5 * length_m, feed_height_m - 0.5), 0.5)
            self._transformer.setValue(49.0)
        else:
            length_m = 17.0
            feed_height_m = 10.0
            end_height_m = 10.0
            self._transformer.setValue(9.0)
        self._length.setValue(length_from_m(length_m, self._unit_system))
        self._feed_height.setValue(length_from_m(feed_height_m, self._unit_system))
        self._end_height.setValue(length_from_m(end_height_m, self._unit_system))
        self._counterpoise_enabled.setChecked(True)
        self._counterpoise_length.setValue(length_from_m(0.05 * wavelength_m, self._unit_system))
        self._update_preset_label()

    def _shortened_parameters(
        self,
        preset: EndFedPreset,
        *,
        preserve_installation: bool = False,
    ) -> EndFedParameters:
        builder = (
            shortened_efhw_80_10_parameters
            if preset is EndFedPreset.SHORTENED_80_10
            else shortened_efhw_40_10_parameters
        )
        azimuth_deg = self._azimuth.value()
        wire_radius_m = radius_to_m(self._radius.value(), self._unit_system)
        material = self._selected_material()
        ground = self._ground_model()
        if preserve_installation:
            try:
                parameters = builder(
                    feed_height_m=length_to_m(
                        self._feed_height.value(),
                        self._unit_system,
                    ),
                    end_height_m=length_to_m(
                        self._end_height.value(),
                        self._unit_system,
                    ),
                    azimuth_deg=azimuth_deg,
                    wire_radius_m=wire_radius_m,
                    material=material,
                    ground=ground,
                )
                return replace(
                    parameters,
                    matching_capacitance_f=self._matching_capacitance.value() * 1e-12,
                    transformer_leakage_inductance_h=(self._transformer_leakage.value() * 1e-6),
                    bend_enabled=self._bend_enabled.isChecked(),
                    bend_vertical_length_m=length_to_m(
                        self._bend_vertical.value(),
                        self._unit_system,
                    ),
                )
            except ValueError:
                pass
        return builder(
            azimuth_deg=azimuth_deg,
            wire_radius_m=wire_radius_m,
            material=material,
            ground=ground,
        )

    def _load_shortened_preset(self, preset: EndFedPreset) -> None:
        self._updating = True
        try:
            self.set_parameters(self._shortened_parameters(preset, preserve_installation=True))
        finally:
            self._updating = False
        self.changed.emit()

    def _update_efhw_visibility(self) -> None:
        self._efhw_widget.setVisible(self._preset is EndFedPreset.STANDARD)
        self._shortened_widget.setVisible(
            self._preset
            in {
                EndFedPreset.SHORTENED_80_10,
                EndFedPreset.SHORTENED_40_10,
            }
        )

    def _load_efhw_preset(self, band_id: str) -> None:
        if self._preset is not EndFedPreset.STANDARD:
            return
        parameters = efhw_parameters(
            band_id,
            feed_height_m=length_to_m(self._feed_height.value(), self._unit_system),
            end_height_m=length_to_m(self._end_height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._length.setValue(length_from_m(parameters.length_m, self._unit_system))
            self._feed_section.setValue(
                length_from_m(parameters.feed_section_length_m, self._unit_system)
            )
            self._installation_return.setValue(
                length_from_m(parameters.installation_return_length_m, self._unit_system)
            )
            self._transformer.setValue(parameters.transformer_ratio)
            self._counterpoise_enabled.setChecked(True)
            self._counterpoise_length.setValue(
                length_from_m(parameters.counterpoise_length_m, self._unit_system)
            )
        finally:
            self._updating = False
        self._update_counterpoise_controls()
        self._update_geometry()
        self.changed.emit()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _ground_changed(self, *_args: object) -> None:
        self._update_ground_controls()
        self._emit_changed()

    def _counterpoise_changed(self, *_args: object) -> None:
        self._update_counterpoise_controls()

    def _counterpoise_toggled(self, checked: bool) -> None:
        if checked and self._counterpoise_length.value() <= 0.0:
            wavelength = 299.792458 / self._frequency.value()
            self._counterpoise_length.setValue(length_from_m(0.05 * wavelength, self._unit_system))
        self._update_counterpoise_controls()
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _loading_coil_toggled(self, _checked: bool) -> None:
        self._update_loading_coil_controls()
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _bend_toggled(self, checked: bool) -> None:
        if checked:
            length_display = self._length.value()
            max_display = max(length_display - 0.001, 0.001)
            min_display = min(max(self._feed_section.value() + 0.001, 0.001), max_display)
            self._bend_vertical.setMaximum(max_display)
            self._bend_vertical.setMinimum(min_display)
            if self._bend_vertical.value() <= min_display:
                default_display = min(
                    length_from_m(DEFAULT_BEND_VERTICAL_LENGTH_M, self._unit_system),
                    max_display,
                )
                self._bend_vertical.setValue(max(default_display, min_display))
        self._update_bend_controls()
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _update_bend_controls(self) -> None:
        enabled = self._bend_enabled.isChecked()
        length_display = self._length.value()
        max_display = max(length_display - 0.001, 0.001)
        min_display = (
            min(max(self._feed_section.value() + 0.001, 0.001), max_display) if enabled else 0.0
        )
        self._bend_vertical.setMaximum(max_display)
        self._bend_vertical.setMinimum(min_display)
        self._bend_vertical.setEnabled(enabled)
        self._end_height.setEnabled(not enabled)
        if not enabled:
            self._bend_horizontal.setText(self._translator.t("endfed.bend_horizontal_none"))
            return
        length_m = length_to_m(length_display, self._unit_system)
        vertical_m = length_to_m(self._bend_vertical.value(), self._unit_system)
        horizontal_m = max(length_m - vertical_m, 0.0)
        top_height_m = length_to_m(self._feed_height.value(), self._unit_system) + vertical_m
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._bend_horizontal.setText(
            self._translator.t(
                "endfed.bend_horizontal_value",
                horizontal=f"{length_from_m(horizontal_m, self._unit_system):.2f}",
                top=f"{length_from_m(top_height_m, self._unit_system):.2f}",
                unit=unit,
            )
        )

    def _update_loading_coil_controls(self) -> None:
        enabled = self._loading_coil_group.isChecked()
        self._loading_coil_offset.setEnabled(enabled)
        self._loading_coil_inductance.setEnabled(enabled)
        self._loading_coil_resistance.setEnabled(enabled)
        if enabled and self._loading_coil_inductance.value() > 0.0:
            if self._loading_coil_resistance.value() > 0.0:
                reactance = (
                    2.0
                    * math.pi
                    * self._frequency.value()
                    * self._loading_coil_inductance.value()
                    * 1e-6
                )
                q_value = reactance / self._loading_coil_resistance.value()
                self._loading_coil_q.setText(f"{q_value:.1f}")
            else:
                self._loading_coil_q.setText(self._translator.t("endfed.ideal_coil"))
        else:
            self._loading_coil_q.setText("—")

    def _update_counterpoise_controls(self) -> None:
        enabled = self._counterpoise_enabled.isChecked()
        self._counterpoise_length.setEnabled(enabled)
        self._counterpoise_height.setEnabled(enabled)
        self._counterpoise_azimuth.setEnabled(enabled)
        self._installation_return.setEnabled(not enabled)
        self._installation_return_hint.setVisible(not enabled)

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
        apply_radius_units(self._translator, unit_system, self._radius)
        apply_length_suffixes(
            self._translator,
            unit_system,
            self._length,
            self._feed_section,
            self._feed_height,
            self._end_height,
            self._counterpoise_length,
            self._counterpoise_height,
            self._installation_return,
            self._loading_coil_offset,
        )
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: EndFedParameters) -> None:
        self._updating = True
        try:
            self._preset = parameters.preset
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._length.setValue(length_from_m(parameters.length_m, self._unit_system))
            self._feed_section.setValue(
                length_from_m(parameters.feed_section_length_m, self._unit_system)
            )
            self._installation_return.setValue(
                length_from_m(parameters.installation_return_length_m, self._unit_system)
            )
            self._bend_enabled.setChecked(parameters.bend_enabled)
            self._bend_vertical.setValue(
                length_from_m(parameters.bend_vertical_length_m, self._unit_system)
            )
            self._feed_height.setValue(length_from_m(parameters.feed_height_m, self._unit_system))
            self._end_height.setValue(length_from_m(parameters.end_height_m, self._unit_system))
            self._transformer.setValue(parameters.transformer_ratio)
            self._matching_capacitance.setValue(parameters.matching_capacitance_f * 1e12)
            self._transformer_leakage.setValue(parameters.transformer_leakage_inductance_h * 1e6)
            self._loading_coil_group.setChecked(parameters.loading_coil_enabled)
            self._loading_coil_offset.setValue(
                length_from_m(parameters.loading_coil_offset_m, self._unit_system)
            )
            self._loading_coil_inductance.setValue(parameters.loading_coil_inductance_h * 1e6)
            self._loading_coil_resistance.setValue(parameters.loading_coil_resistance_ohm)
            self._counterpoise_enabled.setChecked(parameters.counterpoise_length_m > 0.0)
            self._counterpoise_length.setValue(
                length_from_m(parameters.counterpoise_length_m, self._unit_system)
            )
            self._counterpoise_height.setValue(
                length_from_m(parameters.counterpoise_height_m, self._unit_system)
            )
            counterpoise_azimuth = parameters.counterpoise_azimuth_deg
            if counterpoise_azimuth is None:
                counterpoise_azimuth = parameters.effective_counterpoise_azimuth_deg
            self._counterpoise_azimuth.setValue(counterpoise_azimuth)
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
        self._update_preset_label()
        self._update_ground_controls()
        self._update_counterpoise_controls()
        self._update_loading_coil_controls()
        self._update_efhw_visibility()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._frequency.setValue(frequency_hz / 1_000_000.0)
        if self._preset in {
            EndFedPreset.SHORTENED_80_10,
            EndFedPreset.SHORTENED_40_10,
        }:
            return
        if self._preset is not EndFedPreset.STANDARD:
            self._apply_preset_defaults()

    def set_project_matching_network(self, network: MatchingNetwork | None) -> None:
        self._project_matching_network = network
        self._update_matching_override()

    def _update_matching_override(self) -> None:
        self._matching_override.setText(self._translator.t("endfed.matching_override"))
        self._matching_override_edit.setText(self._translator.t("feed_matching.edit"))
        self._matching_override_remove.setText(self._translator.t("feed_matching.remove"))
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            override_active = False
        else:
            override_active = resolve_matching_network(
                parameters,
                self._project_matching_network,
            ).override_active
        self._matching_override_widget.setVisible(override_active)
        self._matching_override_actions.setVisible(override_active and self._show_override_actions)
        self._matching_capacitance.setEnabled(not override_active)
        self._transformer_leakage.setEnabled(not override_active)

    def _update_geometry(self) -> None:
        self._update_loading_coil_controls()
        self._update_matching_override()
        self._update_bend_controls()
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            self._model_warning.clear()
            self._model_warning.setVisible(False)
            return
        warning_keys = endfed_model_warning_keys(parameters)
        self._model_warning.setText(" · ".join(self._translator.t(key) for key in warning_keys))
        self._model_warning.setVisible(bool(warning_keys))
        unit = self._translator.t(length_unit_key(self._unit_system))
        counterpoise = (
            f"{length_from_m(parameters.counterpoise_length_m, self._unit_system):.2f} {unit}"
            if parameters.counterpoise_length_m > 0.0
            else "none"
        )
        vertical_display = length_from_m(
            parameters.bend_vertical_length_m,
            self._unit_system,
        )
        horizontal_display = length_from_m(
            parameters.bend_horizontal_length_m,
            self._unit_system,
        )
        top_height_display = length_from_m(
            parameters.bend_top_height_m,
            self._unit_system,
        )
        if parameters.coil_active:
            coil_position = length_from_m(
                parameters.loading_coil_offset_m,
                self._unit_system,
            )
            top_length = length_from_m(
                parameters.loading_coil_top_length_m,
                self._unit_system,
            )
            if parameters.bend_active:
                text = self._translator.t(
                    "endfed.loaded_bend_geometry",
                    feed=f"{length_from_m(parameters.feed_height_m, self._unit_system):.2f}",
                    vertical=f"{vertical_display:.2f}",
                    horizontal=f"{horizontal_display:.2f}",
                    top_height=f"{top_height_display:.2f}",
                    coil=f"{coil_position:.2f}",
                    inductance=f"{parameters.loading_coil_inductance_h * 1e6:.1f}",
                    top=f"{top_length:.2f}",
                    counterpoise=counterpoise,
                    ratio=f"{parameters.transformer_ratio:g}",
                    unit=unit,
                )
            else:
                text = self._translator.t(
                    "endfed.loaded_geometry",
                    feed=f"{length_from_m(parameters.feed_height_m, self._unit_system):.2f}",
                    end=f"{length_from_m(parameters.end_height_m, self._unit_system):.2f}",
                    coil=f"{coil_position:.2f}",
                    inductance=f"{parameters.loading_coil_inductance_h * 1e6:.1f}",
                    top=f"{top_length:.2f}",
                    counterpoise=counterpoise,
                    ratio=f"{parameters.transformer_ratio:g}",
                    unit=unit,
                )
        elif parameters.bend_active:
            text = self._translator.t(
                "endfed.bend_geometry",
                feed=f"{length_from_m(parameters.feed_height_m, self._unit_system):.2f}",
                vertical=f"{vertical_display:.2f}",
                horizontal=f"{horizontal_display:.2f}",
                top_height=f"{top_height_display:.2f}",
                counterpoise=counterpoise,
                ratio=f"{parameters.transformer_ratio:g}",
                unit=unit,
            )
        else:
            text = self._translator.t(
                "endfed.geometry",
                feed=f"{length_from_m(parameters.feed_height_m, self._unit_system):.2f}",
                end=f"{length_from_m(parameters.end_height_m, self._unit_system):.2f}",
                counterpoise=counterpoise,
                ratio=f"{parameters.transformer_ratio:g}",
                unit=unit,
            )
        if parameters.feed_section_active:
            text += " · " + self._translator.t(
                "endfed.feed_section_summary",
                value=f"{length_from_m(parameters.feed_section_length_m, self._unit_system):.2f}",
                unit=unit,
            )
        if parameters.installation_return_active:
            installation_return_display = length_from_m(
                parameters.installation_return_length_m,
                self._unit_system,
            )
            text += " · " + self._translator.t(
                "endfed.installation_return_summary",
                value=f"{installation_return_display:.2f}",
                unit=unit,
            )
        if parameters.matching_network_active:
            text += " · " + self._translator.t(
                "endfed.matching_summary",
                capacitance=f"{parameters.matching_capacitance_f * 1e12:g}",
                leakage=f"{parameters.transformer_leakage_inductance_h * 1e6:g}",
            )
        self._geometry.setText(text)

    def parameters(self) -> EndFedParameters:
        return EndFedParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            length_m=length_to_m(self._length.value(), self._unit_system),
            feed_section_length_m=length_to_m(self._feed_section.value(), self._unit_system),
            installation_return_length_m=length_to_m(
                self._installation_return.value(),
                self._unit_system,
            ),
            bend_enabled=self._bend_enabled.isChecked(),
            bend_vertical_length_m=length_to_m(
                self._bend_vertical.value(),
                self._unit_system,
            ),
            feed_height_m=length_to_m(self._feed_height.value(), self._unit_system),
            end_height_m=length_to_m(self._end_height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
            transformer_ratio=self._transformer.value(),
            matching_capacitance_f=self._matching_capacitance.value() * 1e-12,
            transformer_leakage_inductance_h=(self._transformer_leakage.value() * 1e-6),
            counterpoise_length_m=(
                length_to_m(self._counterpoise_length.value(), self._unit_system)
                if self._counterpoise_enabled.isChecked()
                else 0.0
            ),
            counterpoise_height_m=length_to_m(self._counterpoise_height.value(), self._unit_system),
            counterpoise_azimuth_deg=self._counterpoise_azimuth.value(),
            loading_coil_enabled=self._loading_coil_group.isChecked(),
            loading_coil_offset_m=(
                length_to_m(self._loading_coil_offset.value(), self._unit_system)
                if self._loading_coil_group.isChecked()
                else 0.0
            ),
            loading_coil_inductance_h=(
                self._loading_coil_inductance.value() * 1e-6
                if self._loading_coil_group.isChecked()
                else 0.0
            ),
            loading_coil_resistance_ohm=(
                self._loading_coil_resistance.value()
                if self._loading_coil_group.isChecked()
                else 0.0
            ),
            preset=self._preset,
        )
