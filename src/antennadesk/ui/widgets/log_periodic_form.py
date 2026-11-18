# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a log-periodic dipole array."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.log_periodic import (
    MAX_ELEMENTS,
    MAX_SIGMA,
    MAX_TAU,
    MIN_ELEMENTS,
    MIN_SIGMA,
    MIN_TAU,
    LogPeriodicParameters,
    log_periodic_parameters,
)
from ...domain.antennas.materials import ALUMINUM, ConductorMaterial
from ...domain.environment.ground import GroundKind, GroundModel
from ..help import apply_help
from ..i18n import Translator
from ..material_combo import (
    populate_material_combo,
    retranslate_material_combo,
)
from ..units import (
    DisplayUnits,
    LengthPolicy,
    LengthUnit,
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
from .table_headers import fit_header_sections


class LogPeriodicForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: LogPeriodicParameters | None = None,
        parent: QWidget | None = None,
        *,
        display_units: DisplayUnits | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self, family="log_periodic")
        self._unit_system = unit_system
        self._display_units = display_units or DisplayUnits(
            unit_system,
            LengthPolicy.AUTO,
        )
        self._table_unit: LengthUnit = "m" if unit_system is UnitSystem.METRIC else "ft"
        self._updating = False
        self._last_frequency_low_mhz = 28.0

        minimum_length, maximum_length = length_bounds(unit_system)
        minimum_height, maximum_height = height_bounds(unit_system)

        self._frequency_low = QDoubleSpinBox(self)
        self._frequency_low.setRange(0.1, 100_000.0)
        self._frequency_low.setDecimals(6)
        self._frequency_low.setSuffix(" MHz")

        self._frequency_high = QDoubleSpinBox(self)
        self._frequency_high.setRange(0.1, 100_000.0)
        self._frequency_high.setDecimals(6)
        self._frequency_high.setSuffix(" MHz")

        self._longest_element = QDoubleSpinBox(self)
        self._longest_element.setRange(minimum_length, maximum_length)
        self._longest_element.setDecimals(3)
        self._longest_element.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._tau = QDoubleSpinBox(self)
        self._tau.setRange(MIN_TAU, MAX_TAU)
        self._tau.setDecimals(4)
        self._tau.setSingleStep(0.001)

        self._sigma = QDoubleSpinBox(self)
        self._sigma.setRange(MIN_SIGMA, MAX_SIGMA)
        self._sigma.setDecimals(4)
        self._sigma.setSingleStep(0.001)

        self._element_count = QSpinBox(self)
        self._element_count.setRange(MIN_ELEMENTS, MAX_ELEMENTS)

        self._phase_line_impedance = QDoubleSpinBox(self)
        self._phase_line_impedance.setRange(10.0, 1_000.0)
        self._phase_line_impedance.setDecimals(1)
        self._phase_line_impedance.setSuffix(" Ω")

        self._phase_line_velocity_factor = QDoubleSpinBox(self)
        self._phase_line_velocity_factor.setRange(0.5, 1.0)
        self._phase_line_velocity_factor.setDecimals(3)
        self._phase_line_velocity_factor.setSingleStep(0.001)

        self._feed_transformer_ratio = QDoubleSpinBox(self)
        self._feed_transformer_ratio.setRange(1.0, 16.0)
        self._feed_transformer_ratio.setDecimals(1)
        self._feed_transformer_ratio.setSuffix(":1")

        self._height = QDoubleSpinBox(self)
        self._height.setRange(minimum_height, maximum_height)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._longest_element_field = LengthField(
            self._longest_element,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._height_field = LengthField(
            self._height,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)

        self._material = QComboBox(self)
        populate_material_combo(self._material, translator)
        index = self._material.findData(ALUMINUM)
        if index >= 0:
            self._material.setCurrentIndex(index)

        self._ground = QComboBox(self)
        self._ground.addItem("", GroundKind.FREE_SPACE.value)
        self._ground.addItem("", GroundKind.PERFECT.value)
        self._ground.addItem("", GroundKind.FINITE.value)
        self._ground.setItemText(0, translator.t("ground.free_space"))
        self._ground.setItemText(1, translator.t("ground.perfect"))
        self._ground.setItemText(2, translator.t("ground.finite"))

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

        self._table = QTableWidget(0, 4, self)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._table.setMinimumHeight(140)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._retranslate_table_headers()

        self._preset = QPushButton(translator.t("log_periodic.reference_preset"), self)
        self._preset.clicked.connect(self._load_reference_preset)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)
        self._evidence = QLabel(translator.t("log_periodic.evidence"), self)
        self._evidence.setWordWrap(True)

        form = QFormLayout()
        form.addRow(self._labels.label("log_periodic.frequency_low"), self._frequency_low)
        form.addRow(self._labels.label("log_periodic.frequency_high"), self._frequency_high)
        form.addRow(self._labels.label("log_periodic.longest_element"), self._longest_element)
        form.addRow(self._labels.label("log_periodic.tau"), self._tau)
        form.addRow(self._labels.label("log_periodic.sigma"), self._sigma)
        form.addRow(self._labels.label("log_periodic.element_count"), self._element_count)
        form.addRow(
            self._labels.label("log_periodic.phase_line_impedance"),
            self._phase_line_impedance,
        )
        form.addRow(
            self._labels.label("log_periodic.phase_line_velocity_factor"),
            self._phase_line_velocity_factor,
        )
        form.addRow(
            self._labels.label("log_periodic.feed_transformer_ratio"),
            self._feed_transformer_ratio,
        )
        form.addRow(self._labels.label("field.height"), self._height)
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
        layout.addWidget(self._table, 1)
        layout.addWidget(self._preset)
        layout.addWidget(self._geometry)
        layout.addWidget(self._evidence)

        self._frequency_low.valueChanged.connect(self._frequency_low_changed)
        self._frequency_high.valueChanged.connect(self._emit_changed)
        for widget in (
            self._longest_element,
            self._tau,
            self._sigma,
            self._phase_line_impedance,
            self._phase_line_velocity_factor,
            self._feed_transformer_ratio,
            self._height,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._element_count.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)

        apply_help(self._table, translator, "log_periodic.table")
        apply_help(self._preset, translator, "log_periodic.reference_preset")
        apply_help(self._geometry, translator, "log_periodic.geometry_summary")
        apply_help(self._evidence, translator, "log_periodic.evidence")

        initial = parameters or log_periodic_parameters()
        self.set_parameters(initial)
        self._update_ground_controls()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        retranslate_material_combo(self._material, self._translator)
        retranslate_combo(
            self._ground,
            self._translator,
            ("ground.free_space", "ground.perfect", "ground.finite"),
        )
        self._preset.setText(self._translator.t("log_periodic.reference_preset"))
        self._evidence.setText(self._translator.t("log_periodic.evidence"))
        self._retranslate_table_headers()
        self._update_geometry()

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            parameters = None
        self._unit_system = unit_system
        self._display_units = DisplayUnits(unit_system, self._display_units.length_policy)
        previous_updating = self._updating
        self._updating = True
        try:
            apply_radius_units(self._translator, unit_system, self._radius)
            self._longest_element_field.set_display_units(self._display_units)
            self._height_field.set_display_units(self._display_units)
        finally:
            self._updating = previous_updating
        if parameters is not None:
            self.set_parameters(parameters)

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self.set_parameters(log_periodic_parameters(frequency_hz=frequency_hz))

    def set_parameters(self, parameters: LogPeriodicParameters) -> None:
        self._updating = True
        try:
            self._frequency_low.setValue(parameters.frequency_low_hz / 1_000_000.0)
            self._frequency_high.setValue(parameters.frequency_high_hz / 1_000_000.0)
            self._last_frequency_low_mhz = parameters.frequency_low_hz / 1_000_000.0
            self._longest_element_field.configure(parameters.longest_element_length_m)
            self._tau.setValue(parameters.tau)
            self._sigma.setValue(parameters.sigma)
            self._element_count.setValue(parameters.element_count)
            self._phase_line_impedance.setValue(parameters.phase_line_impedance_ohm)
            self._phase_line_velocity_factor.setValue(parameters.phase_line_velocity_factor)
            self._feed_transformer_ratio.setValue(parameters.feed_transformer_ratio)
            self._height_field.configure(parameters.height_m)
            self._azimuth.setValue(parameters.azimuth_deg)
            self._radius.setValue(radius_from_m(parameters.wire_radius_m, self._unit_system))
            self._select_material(parameters.material)
            self._select_ground(parameters.ground)
            self._update_table()
            self._update_geometry()
        finally:
            self._updating = False

    def parameters(self) -> LogPeriodicParameters:
        return LogPeriodicParameters(
            frequency_low_hz=self._frequency_low.value() * 1_000_000.0,
            frequency_high_hz=self._frequency_high.value() * 1_000_000.0,
            longest_element_length_m=self._longest_element_field.value_m(),
            tau=self._tau.value(),
            sigma=self._sigma.value(),
            element_count=self._element_count.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            phase_line_impedance_ohm=self._phase_line_impedance.value(),
            phase_line_velocity_factor=self._phase_line_velocity_factor.value(),
            feed_transformer_ratio=self._feed_transformer_ratio.value(),
            height_m=self._height_field.value_m(),
            azimuth_deg=self._azimuth.value(),
            material=self._selected_material(),
            ground=self._ground_model(),
        )

    def _retranslate_table_headers(self) -> None:
        self._table.setHorizontalHeaderLabels(
            [
                self._translator.t("log_periodic.element"),
                f"{self._translator.t('log_periodic.length')} ({self._table_unit})",
                f"{self._translator.t('log_periodic.spacing')} ({self._table_unit})",
                f"{self._translator.t('log_periodic.position')} ({self._table_unit})",
            ]
        )
        fit_header_sections(self._table)

    def _select_material(self, material: ConductorMaterial) -> None:
        index = self._material.findData(material)
        if index < 0:
            index = self._material.findData(ALUMINUM)
        if index >= 0:
            self._material.setCurrentIndex(index)

    def _select_ground(self, ground: GroundModel) -> None:
        index = self._ground.findData(ground.kind.value)
        if index >= 0:
            self._ground.setCurrentIndex(index)
        if ground.kind is GroundKind.FINITE:
            if ground.relative_permittivity is not None:
                self._permittivity.setValue(ground.relative_permittivity)
            if ground.conductivity_s_per_m is not None:
                self._conductivity.setValue(ground.conductivity_s_per_m)

    def _selected_material(self) -> ConductorMaterial:
        value = self._material.currentData()
        return value if isinstance(value, ConductorMaterial) else ALUMINUM

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

    def _frequency_low_changed(self, value: float) -> None:
        if self._updating:
            return
        previous = self._last_frequency_low_mhz
        if previous <= 0.0 or value <= 0.0 or math.isclose(previous, value):
            self._last_frequency_low_mhz = value
            self._emit_changed()
            return
        frequency_scale = value / previous
        length_scale = previous / value
        self._updating = True
        try:
            self._last_frequency_low_mhz = value
            self._frequency_high.setValue(self._frequency_high.value() * frequency_scale)
            self._longest_element_field.set_value_m(
                self._longest_element_field.value_m() * length_scale
            )
            self._update_table()
            self._update_geometry()
        finally:
            self._updating = False
        self.changed.emit()

    def _ground_changed(self, *_args: object) -> None:
        self._update_ground_controls()
        self._emit_changed()

    def _update_ground_controls(self) -> None:
        finite = self._ground.currentData() == GroundKind.FINITE.value
        self._permittivity.setEnabled(finite)
        self._conductivity.setEnabled(finite)

    def _emit_changed(self, *_args: object) -> None:
        if self._updating:
            return
        self._update_table()
        self._update_geometry()
        self.changed.emit()

    def _update_table(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            return
        lengths = parameters.element_lengths_m
        spacings = parameters.element_spacings_m
        positions = parameters.element_positions_m
        self._table_unit = self._display_units.table_unit((*lengths, *spacings, *positions))
        self._retranslate_table_headers()
        self._table.setRowCount(len(lengths))
        for row, (length, position) in enumerate(zip(lengths, positions, strict=True)):
            spacing = "" if row == 0 else self._format_length(spacings[row - 1])
            values = (
                str(row + 1),
                self._format_length(length),
                spacing,
                self._format_length(position),
            )
            for column, text in enumerate(values):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._table.setItem(row, column, item)

    def _format_length(self, value_m: float) -> str:
        value = value_m / self._display_units.meters_per_unit(self._table_unit)
        return f"{value:.{self._display_units.decimals_for(self._table_unit)}f}"

    def _update_geometry(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            self._geometry.setText(str(exc))
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "log_periodic.geometry_summary",
                elements=parameters.element_count,
                boom=f"{length_from_m(parameters.boom_length_m, self._unit_system):.3f} {unit}",
                longest=(
                    f"{length_from_m(parameters.longest_element_length_m, self._unit_system):.3f} "
                    f"{unit}"
                ),
                shortest=(
                    f"{length_from_m(parameters.shortest_element_length_m, self._unit_system):.3f} "
                    f"{unit}"
                ),
                z0=f"{parameters.phase_line_impedance_ohm:.1f}",
            )
        )

    def _load_reference_preset(self) -> None:
        self.set_parameters(
            log_periodic_parameters(
                frequency_hz=self._frequency_low.value() * 1_000_000.0,
                height_m=self._height_field.value_m(),
                azimuth_deg=self._azimuth.value(),
                material=self._selected_material(),
                ground=self._ground_model(),
            )
        )
        self.changed.emit()
