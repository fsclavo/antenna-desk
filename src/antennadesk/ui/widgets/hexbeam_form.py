# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for single- and multi-band hexbeams."""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.hexbeam import (
    HEXBEAM_BAND_LABELS,
    HexbeamBand,
    HexbeamParameters,
    published_hexbeam_multiband_parameters,
    published_hexbeam_parameters,
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


def _small_length_minimum(unit_system: UnitSystem) -> float:
    minimum_m = 0.0001
    return minimum_m if unit_system is UnitSystem.METRIC else minimum_m / 0.3048


class HexbeamForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: HexbeamParameters | None = None,
        parent: QWidget | None = None,
        *,
        display_units: DisplayUnits | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self, family="hexbeam")
        self._unit_system = unit_system
        self._display_units = display_units or DisplayUnits(
            unit_system,
            LengthPolicy.FIXED,
        )
        self._updating = False
        self._preserved_bands: tuple[HexbeamBand, ...] = ()
        minimum_length, maximum_length = length_bounds(unit_system)
        minimum_height, maximum_height = height_bounds(unit_system)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")

        self._driver_half = QDoubleSpinBox(self)
        self._driver_half.setRange(minimum_length, maximum_length)
        self._driver_half.setDecimals(3)
        self._driver_half.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._reflector_half = QDoubleSpinBox(self)
        self._reflector_half.setRange(minimum_length, maximum_length)
        self._reflector_half.setDecimals(3)
        self._reflector_half.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._turning_radius = QDoubleSpinBox(self)
        self._turning_radius.setRange(minimum_length, maximum_length)
        self._turning_radius.setDecimals(3)
        self._turning_radius.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._tip_gap = QDoubleSpinBox(self)
        self._tip_gap.setRange(_small_length_minimum(unit_system), maximum_length)
        self._tip_gap.setDecimals(4)
        self._tip_gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._height = QDoubleSpinBox(self)
        self._height.setRange(minimum_height, maximum_height)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._feed_gap = QDoubleSpinBox(self)
        self._feed_gap.setRange(_small_length_minimum(unit_system), maximum_length)
        self._feed_gap.setDecimals(4)
        self._feed_gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._element_separation = QDoubleSpinBox(self)
        self._element_separation.setRange(0.0, maximum_length)
        self._element_separation.setDecimals(4)
        self._element_separation.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._driver_half_field = LengthField(
            self._driver_half,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._reflector_half_field = LengthField(
            self._reflector_half,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._turning_radius_field = LengthField(
            self._turning_radius,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._tip_gap_field = LengthField(
            self._tip_gap,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._feed_gap_field = LengthField(
            self._feed_gap,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._element_separation_field = LengthField(
            self._element_separation,
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
        populate_template_material_combo(self._material, translator, "hexbeam")

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

        self._band_group = QGroupBox(translator.t("hexbeam.bands"), self)
        self._band_checks: dict[str, QCheckBox] = {}
        checks_layout = QVBoxLayout()
        for label in HEXBEAM_BAND_LABELS:
            check = QCheckBox(translator.t(f"hexbeam.band.{label}"), self._band_group)
            check.setObjectName(f"band_{label}")
            check.toggled.connect(self._band_toggled)
            apply_help(check, translator, f"band_{label}", family="hexbeam")
            self._band_checks[label] = check
            checks_layout.addWidget(check)
        self._bands_note = QLabel(translator.t("hexbeam.bands_hint"), self._band_group)
        self._bands_note.setWordWrap(True)
        self._band_table = QTableWidget(0, 6, self._band_group)
        self._band_table.verticalHeader().setVisible(False)
        self._band_table.setAlternatingRowColors(True)
        self._band_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._band_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._band_table.setMinimumHeight(130)
        self._band_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._retranslate_band_table_headers()
        band_layout = QVBoxLayout(self._band_group)
        band_layout.addLayout(checks_layout)
        band_layout.addWidget(self._bands_note)
        band_layout.addWidget(self._band_table)
        apply_help(self._band_group, translator, "bands", family="hexbeam")

        self._starting = QPushButton(
            translator.t("action.load_starting_dimensions"),
            self,
        )
        self._starting.clicked.connect(self.load_starting_dimensions)
        apply_help(self._starting, translator, "load_starting", family="hexbeam")
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
        form.addRow(self._labels.label("hexbeam.driver_half"), self._driver_half)
        form.addRow(self._labels.label("hexbeam.reflector_half"), self._reflector_half)
        form.addRow(self._labels.label("hexbeam.turning_radius"), self._turning_radius)
        form.addRow(self._labels.label("hexbeam.tip_gap"), self._tip_gap)
        form.addRow(self._labels.label("field.height"), self._height)
        form.addRow(self._labels.label("hexbeam.feed_gap"), self._feed_gap)
        form.addRow(
            self._labels.label("hexbeam.element_separation"),
            self._element_separation,
        )
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
        layout.addWidget(self._band_group)
        layout.addWidget(self._geometry)
        layout.addWidget(self._starting_note)

        self._frequency.valueChanged.connect(self._frequency_changed)
        for widget in (
            self._driver_half,
            self._reflector_half,
            self._turning_radius,
            self._tip_gap,
            self._feed_gap,
        ):
            widget.valueChanged.connect(self._band_dimension_changed)
        self._element_separation.valueChanged.connect(self._managed_field_changed)
        for widget in (
            self._height,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        initial = parameters or published_hexbeam_parameters(
            material=default_material_for_template("hexbeam"),
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
        apply_help(self._starting, self._translator, "load_starting", family="hexbeam")
        self._starting_state.retranslate()
        retranslate_material_combo(self._material, self._translator)
        retranslate_combo(
            self._ground,
            self._translator,
            ("ground.free_space", "ground.perfect", "ground.finite"),
        )
        self._band_group.setTitle(self._translator.t("hexbeam.bands"))
        self._bands_note.setText(self._translator.t("hexbeam.bands_hint"))
        apply_help(self._band_group, self._translator, "bands", family="hexbeam")
        for label, check in self._band_checks.items():
            check.setText(self._translator.t(f"hexbeam.band.{label}"))
            apply_help(check, self._translator, f"band_{label}", family="hexbeam")
        labels = self._selected_band_labels()
        if len(labels) > 1:
            self._populate_band_table(self._multiband_parameters_for(labels).bands)
        elif self._preserved_bands:
            self._populate_band_table(self._preserved_bands)
        else:
            self._band_table.setRowCount(0)
            self._band_table.setVisible(False)
        self._update_geometry()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _frequency_changed(self, _value: float) -> None:
        if self._updating:
            return
        if self._selected_band_labels():
            self._set_band_checks(())
            self._set_multiband_widgets(False)
            self._band_table.setRowCount(0)
            self._band_table.setVisible(False)
        if self._starting_state.pristine:
            try:
                self.load_starting_dimensions()
            except (ValueError, TypeError):
                self._starting_state.show_stale(self._frequency.value())
                self._emit_changed()
            return
        self._starting_state.show_stale(self._frequency.value())
        self._emit_changed()

    def _band_dimension_changed(self, *_args: object) -> None:
        if self._updating:
            return
        if self._selected_band_labels():
            self._set_band_checks(())
            self._band_table.setRowCount(0)
            self._band_table.setVisible(False)
        self._managed_field_changed()

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

    def _selected_band_labels(self) -> tuple[str, ...]:
        return tuple(label for label in HEXBEAM_BAND_LABELS if self._band_checks[label].isChecked())

    def _set_band_checks(self, labels: tuple[str, ...]) -> None:
        previous = self._updating
        self._updating = True
        try:
            selected = set(labels)
            for label, check in self._band_checks.items():
                check.setChecked(label in selected)
        finally:
            self._updating = previous

    def _retranslate_band_table_headers(self, unit: str | None = None) -> None:
        suffix = f" ({unit})" if unit else ""
        self._band_table.setHorizontalHeaderLabels(
            (
                self._translator.t("band.table.band"),
                f"{self._translator.t('field.frequency')} (MHz)",
                f"{self._translator.t('hexbeam.driver_half')}{suffix}",
                f"{self._translator.t('hexbeam.reflector_half')}{suffix}",
                f"{self._translator.t('hexbeam.tip_gap')}{suffix}",
                f"{self._translator.t('hexbeam.vertical_offset')}{suffix}",
            )
        )

    def _populate_band_table(self, bands: tuple[HexbeamBand, ...]) -> None:
        if len(bands) < 2:
            self._band_table.setRowCount(0)
            self._band_table.setVisible(False)
            return
        values = [
            value
            for band in bands
            for value in (
                band.driver_half_length_m,
                band.reflector_half_length_m,
                band.tip_gap_m,
                band.vertical_offset_m,
            )
        ]
        unit = self._display_units.table_unit(values)
        self._retranslate_band_table_headers(str(unit))
        self._band_table.setRowCount(len(bands))
        for row, band in enumerate(bands):
            items = (
                self._translator.t(f"hexbeam.band.{band.label}"),
                f"{band.frequency_hz / 1_000_000.0:.3f}",
                self._display_units.format_number(
                    band.driver_half_length_m,
                    unit=unit,
                    trim=False,
                ),
                self._display_units.format_number(
                    band.reflector_half_length_m,
                    unit=unit,
                    trim=False,
                ),
                self._display_units.format_number(band.tip_gap_m, unit=unit, trim=False),
                self._display_units.format_number(
                    band.vertical_offset_m,
                    unit=unit,
                    trim=False,
                ),
            )
            for column, text in enumerate(items):
                item = QTableWidgetItem(text)
                if column > 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self._band_table.setItem(row, column, item)
        self._band_table.setVisible(True)

    def _set_multiband_widgets(self, multiband: bool) -> None:
        for widget in (
            self._frequency,
            self._driver_half,
            self._reflector_half,
            self._turning_radius,
            self._tip_gap,
            self._feed_gap,
        ):
            widget.setEnabled(not multiband)

    def _multiband_parameters_for(self, labels: tuple[str, ...]) -> HexbeamParameters:
        base = published_hexbeam_multiband_parameters(
            labels=labels,
            height_m=self._height_field.value_m(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
        return replace(
            base,
            element_separation_m=self._element_separation_field.value_m(),
        )

    def _single_band_preset_parameters(self, label: str) -> HexbeamParameters:
        return replace(self._multiband_parameters_for((label,)), bands=())

    def _band_toggled(self, _checked: bool) -> None:
        if self._updating:
            return
        self._preserved_bands = ()
        labels = self._selected_band_labels()
        if len(labels) > 1:
            self.set_parameters(self._multiband_parameters_for(labels))
            self._starting_state.mark_pristine()
        elif len(labels) == 1:
            self.set_parameters(self._single_band_preset_parameters(labels[0]))
            self._set_band_checks(labels)
            self._starting_state.mark_pristine()
        else:
            self._set_multiband_widgets(False)
            self._band_table.setRowCount(0)
            self._band_table.setVisible(False)
            self._starting_state.mark_non_pristine()
            self._emit_changed()

    def load_starting_dimensions(self) -> None:
        labels = self._selected_band_labels()
        if labels:
            parameters = (
                self._multiband_parameters_for(labels)
                if len(labels) > 1
                else self._single_band_preset_parameters(labels[0])
            )
            self.set_parameters(parameters)
            if len(labels) == 1:
                self._set_band_checks(labels)
            self._starting_state.mark_pristine(frequency_mhz=self._frequency.value())
            self.changed.emit()
            return
        try:
            current = self.parameters()
        except (ValueError, TypeError):
            frequency_hz = self._frequency.value() * 1_000_000.0
            height_m = self._height_field.value_m()
            azimuth_deg = self._azimuth.value()
            wire_radius_m = radius_to_m(self._radius.value(), self._unit_system)
            material = self._selected_material()
            ground = self._ground_model()
        else:
            frequency_hz = current.frequency_hz
            height_m = current.height_m
            azimuth_deg = current.azimuth_deg
            wire_radius_m = current.wire_radius_m
            material = current.material
            ground = current.ground
        self.set_parameters(
            published_hexbeam_parameters(
                frequency_hz=frequency_hz,
                height_m=height_m,
                azimuth_deg=azimuth_deg,
                wire_radius_m=wire_radius_m,
                material=material,
                ground=ground,
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
            for field in (
                self._driver_half_field,
                self._reflector_half_field,
                self._turning_radius_field,
                self._tip_gap_field,
                self._feed_gap_field,
                self._element_separation_field,
                self._height_field,
            ):
                field.set_display_units(self._display_units)
        finally:
            self._updating = previous_updating
        if parameters is not None:
            self.set_parameters(parameters)
            if was_pristine:
                self.mark_starting_dimensions_pristine()

    def set_parameters(self, parameters: HexbeamParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._driver_half_field.configure(parameters.driver_half_length_m)
            self._reflector_half_field.configure(parameters.reflector_half_length_m)
            self._turning_radius_field.configure(parameters.turning_radius_m)
            self._tip_gap_field.configure(parameters.tip_gap_m)
            self._height_field.configure(parameters.height_m)
            self._feed_gap_field.configure(parameters.feed_gap_m)
            self._element_separation_field.configure(parameters.element_separation_m)
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
            labels = tuple(band.label for band in parameters.bands)
            known_labels = set(HEXBEAM_BAND_LABELS)
            self._preserved_bands = (
                parameters.bands
                if any(band.label not in known_labels for band in parameters.bands)
                else ()
            )
            self._set_band_checks(labels)
            self._populate_band_table(parameters.bands)
            self._set_multiband_widgets(len(parameters.bands) > 1)
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
        if len(parameters.bands) > 1:
            self._geometry.setText(
                self._translator.t(
                    "hexbeam.multiband_geometry",
                    bands=len(parameters.bands),
                    span=f"{length_from_m(parameters.overall_span_m, self._unit_system):.3f}",
                    radius=f"{length_from_m(parameters.turning_radius_m, self._unit_system):.3f}",
                    height=f"{length_from_m(parameters.height_m, self._unit_system):.3f}",
                    unit=unit,
                )
            )
            return
        driver = length_from_m(parameters.driver_half_length_m, self._unit_system)
        reflector = length_from_m(parameters.reflector_half_length_m, self._unit_system)
        span = length_from_m(parameters.overall_span_m, self._unit_system)
        radius = length_from_m(parameters.turning_radius_m, self._unit_system)
        self._geometry.setText(
            self._translator.t(
                "hexbeam.geometry",
                driver=f"{driver:.3f}",
                reflector=f"{reflector:.3f}",
                span=f"{span:.3f}",
                radius=f"{radius:.3f}",
                unit=unit,
            )
        )

    def parameters(self) -> HexbeamParameters:
        labels = self._selected_band_labels()
        if len(labels) > 1:
            return self._multiband_parameters_for(labels)
        parameters = HexbeamParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            driver_half_length_m=self._driver_half_field.value_m(),
            reflector_half_length_m=self._reflector_half_field.value_m(),
            turning_radius_m=self._turning_radius_field.value_m(),
            tip_gap_m=self._tip_gap_field.value_m(),
            height_m=self._height_field.value_m(),
            feed_gap_m=self._feed_gap_field.value_m(),
            element_separation_m=self._element_separation_field.value_m(),
            azimuth_deg=self._azimuth.value(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
        if self._preserved_bands:
            return replace(parameters, bands=self._preserved_bands)
        return parameters
