# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a parametric Yagi."""

from __future__ import annotations

import math

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.polarization import Polarization
from ...domain.antennas.yagi import (
    YAGI_FOLDED_REFERENCE_TRANSFORMER_RATIO,
    YagiElement,
    YagiMatchType,
    YagiParameters,
    nbs_five_element,
)
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import (
    UnitSystem,
    length_from_m,
    length_to_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
    radius_unit_key,
)
from .form_i18n import FormLabels, retranslate_combo
from .form_units import apply_length_suffixes, apply_radius_units
from .ground_presets import GroundPresetController

MATERIALS = (COPPER, ALUMINUM)

# The editor starts on the 2 m band.  The geometry is the published NBS
# TN-688 five-element design scaled to this frequency; the published
# reference itself is at 50.1 MHz.
YAGI_DEFAULT_FREQUENCY_HZ = 145_000_000.0


class YagiForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: YagiParameters | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self, family="yagi")
        self._unit_system = unit_system
        self._updating = False

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(YAGI_DEFAULT_FREQUENCY_HZ / 1_000_000.0)
        self._last_frequency_mhz = YAGI_DEFAULT_FREQUENCY_HZ / 1_000_000.0

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(12.0, unit_system))

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._polarization = QComboBox(self)
        self._polarization.addItem("", Polarization.HORIZONTAL.value)
        self._polarization.addItem("", Polarization.VERTICAL.value)
        self._polarization.setItemText(0, translator.t("orientation.horizontal"))
        self._polarization.setItemText(1, translator.t("orientation.vertical"))
        self._polarization.setToolTip(translator.t("yagi.polarization_hint"))

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)
        self._radius.setValue(radius_from_m(0.00635, unit_system))

        self._taper_length = QDoubleSpinBox(self)
        self._taper_length.setDecimals(3)
        self._taper_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._taper_radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._taper_radius)
        self._taper_radius.setValue(0.0)

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
        self._table.setHorizontalHeaderLabels(
            [
                translator.t("yagi.element"),
                translator.t("yagi.position"),
                translator.t("yagi.length"),
                translator.t("yagi.radius"),
            ]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._table.itemChanged.connect(self._refresh_driven_values)

        self._add = QPushButton(translator.t("yagi.add_element"), self)
        self._remove = QPushButton(translator.t("yagi.remove_element"), self)
        self._preset = QPushButton(translator.t("yagi.nbs_preset"), self)
        self._add.clicked.connect(self._add_element)
        self._remove.clicked.connect(self._remove_element)
        self._preset.clicked.connect(self._load_preset)
        self._driven = QComboBox(self)
        self._driven_folded = QCheckBox(translator.t("yagi.folded_driven"), self)
        self._driven_folded.setToolTip(translator.t("yagi.folded_hint"))
        self._driven_fold_spacing = QDoubleSpinBox(self)
        self._driven_fold_spacing.setDecimals(3)
        self._driven_fold_spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._driven_fold_spacing.setValue(length_from_m(0.1, unit_system))
        self._transformer = QDoubleSpinBox(self)
        self._transformer.setRange(1.0, 100.0)
        self._transformer.setDecimals(1)
        self._transformer.setSuffix(":1")
        self._transformer.setValue(1.0)
        self._transformer_label = self._labels.label("field.transformer_ratio")

        self._match_type = QComboBox(self)
        self._match_type.addItem(translator.t("yagi.match_none"), YagiMatchType.NONE.value)
        self._match_type.addItem(
            translator.t("yagi.match_beta_hairpin"),
            YagiMatchType.BETA_HAIRPIN.value,
        )
        self._match_type.setToolTip(translator.t("yagi.match_hint"))
        self._match_length = QDoubleSpinBox(self)
        self._match_length.setDecimals(3)
        self._match_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._match_length.setValue(length_from_m(0.2, unit_system))
        self._match_spacing = QDoubleSpinBox(self)
        self._match_spacing.setDecimals(3)
        self._match_spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._match_spacing.setValue(length_from_m(0.1, unit_system))
        self._match_note = QLabel(translator.t("yagi.gamma_note"), self)
        self._match_note.setWordWrap(True)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)
        self._frequency_warning = QLabel(self)
        self._frequency_warning.setWordWrap(True)
        self._frequency_warning.setVisible(False)

        self._clearance_warning = QLabel(self)
        self._clearance_warning.setWordWrap(True)
        self._clearance_warning.setVisible(False)

        self._match_warning = QLabel(self)
        self._match_warning.setWordWrap(True)
        self._match_warning.setVisible(False)

        form = QFormLayout()
        form.addRow(self._labels.label("field.frequency"), self._frequency)
        form.addRow(self._labels.label("field.height"), self._height)
        form.addRow(self._labels.label("field.azimuth"), self._azimuth)
        form.addRow(self._labels.label("field.polarization"), self._polarization)
        form.addRow(self._labels.label("yagi.radius"), self._radius)
        form.addRow(self._labels.label("yagi.taper_length"), self._taper_length)
        form.addRow(self._labels.label("yagi.taper_radius"), self._taper_radius)
        form.addRow(self._labels.label("field.material"), self._material)
        form.addRow(self._labels.label("field.ground"), self._ground)
        form.addRow(self._labels.label("field.soil_preset"), self._soil)
        form.addRow(self._labels.label("field.permittivity"), self._permittivity)
        form.addRow(self._labels.label("field.conductivity"), self._conductivity)
        form.addRow(self._labels.label("yagi.driven"), self._driven)
        form.addRow(self._driven_folded)
        form.addRow(self._labels.label("yagi.fold_spacing"), self._driven_fold_spacing)
        form.addRow(self._transformer_label, self._transformer)
        form.addRow(self._labels.label("yagi.match_type"), self._match_type)
        form.addRow(self._labels.label("yagi.match_length"), self._match_length)
        form.addRow(self._labels.label("yagi.match_spacing"), self._match_spacing)

        element_buttons = QHBoxLayout()
        element_buttons.addWidget(self._add)
        element_buttons.addWidget(self._remove)
        element_buttons.addWidget(self._preset)
        element_buttons.addStretch(1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._labels.bind_form(form)
        layout.addLayout(form)
        layout.addWidget(self._table, 1)
        layout.addLayout(element_buttons)
        layout.addWidget(self._match_note)
        layout.addWidget(self._geometry)
        layout.addWidget(self._frequency_warning)
        layout.addWidget(self._clearance_warning)
        layout.addWidget(self._match_warning)

        self._frequency.valueChanged.connect(self._frequency_changed)
        for widget in (
            self._height,
            self._azimuth,
            self._radius,
            self._taper_length,
            self._taper_radius,
            self._driven_fold_spacing,
            self._transformer,
            self._match_length,
            self._match_spacing,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._polarization.currentIndexChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        self._driven.currentIndexChanged.connect(self._emit_changed)
        self._driven_folded.toggled.connect(self._folded_changed)
        self._match_type.currentIndexChanged.connect(self._match_changed)
        if parameters is not None:
            self.set_parameters(parameters)
        else:
            self._load_preset()
        self._update_ground_controls()
        self._update_folded_controls()
        self._update_match_controls()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _frequency_changed(self, value: float) -> None:
        previous = self._last_frequency_mhz
        self._last_frequency_mhz = value
        if self._updating or previous <= 0.0 or value <= 0.0:
            if not self._updating:
                self._emit_changed()
            return
        if math.isclose(previous, value, rel_tol=1e-12, abs_tol=1e-12):
            self._emit_changed()
            return
        scale = previous / value
        self._updating = True
        try:
            for row in range(self._table.rowCount()):
                for column in (1, 2):
                    cell = self._table.item(row, column)
                    if cell is None:
                        continue
                    try:
                        current_m = length_to_m(float(cell.text()), self._unit_system)
                    except ValueError:
                        continue
                    cell.setText(f"{length_from_m(current_m * scale, self._unit_system):.3f}")
        finally:
            self._updating = False
        self._refresh_driven_values()
        self._update_geometry()
        self.changed.emit()

    def _ground_changed(self, *_args: object) -> None:
        self._update_ground_controls()
        self._emit_changed()

    def _folded_changed(self, *_args: object) -> None:
        if self._driven_folded.isChecked():
            index = self._match_type.findData(YagiMatchType.NONE.value)
            if index >= 0:
                self._match_type.setCurrentIndex(index)
            if math.isclose(self._transformer.value(), 1.0, abs_tol=1e-9):
                self._transformer.setValue(YAGI_FOLDED_REFERENCE_TRANSFORMER_RATIO)
        else:
            self._transformer.setValue(1.0)
        self._update_folded_controls()
        self._update_match_controls()
        self._emit_changed()

    def _match_changed(self, *_args: object) -> None:
        self._update_match_controls()
        self._emit_changed()

    def _update_folded_controls(self) -> None:
        folded = self._driven_folded.isChecked()
        self._driven_fold_spacing.setEnabled(folded)
        self._match_type.setEnabled(not folded)
        self._transformer_label.setVisible(folded)
        self._transformer.setVisible(folded)
        self._transformer.setEnabled(folded)

    def _update_match_controls(self) -> None:
        active = self._selected_match_type() is YagiMatchType.BETA_HAIRPIN
        self._match_length.setEnabled(active)
        self._match_spacing.setEnabled(active)

    def _selected_match_type(self) -> YagiMatchType:
        return YagiMatchType(str(self._match_type.currentData()))

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        self._table.setHorizontalHeaderLabels(
            [
                self._translator.t("yagi.element"),
                self._translator.t("yagi.position"),
                self._translator.t("yagi.length"),
                self._translator.t("yagi.radius"),
            ]
        )
        self._add.setText(self._translator.t("yagi.add_element"))
        self._remove.setText(self._translator.t("yagi.remove_element"))
        self._preset.setText(self._translator.t("yagi.nbs_preset"))
        self._driven_folded.setText(self._translator.t("yagi.folded_driven"))
        self._driven_folded.setToolTip(self._translator.t("yagi.folded_hint"))
        self._match_type.setItemText(0, self._translator.t("yagi.match_none"))
        self._match_type.setItemText(1, self._translator.t("yagi.match_beta_hairpin"))
        self._match_type.setToolTip(self._translator.t("yagi.match_hint"))
        self._match_note.setText(self._translator.t("yagi.gamma_note"))
        retranslate_combo(
            self._polarization,
            self._translator,
            ("orientation.horizontal", "orientation.vertical"),
        )
        self._polarization.setToolTip(self._translator.t("yagi.polarization_hint"))
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

    def _selected_polarization(self) -> Polarization:
        return Polarization(str(self._polarization.currentData()))

    def _longest_element_m(self) -> float:
        lengths: list[float] = []
        for row in range(self._table.rowCount()):
            cell = self._table.item(row, 2)
            if cell is None:
                continue
            try:
                lengths.append(length_to_m(float(cell.text()), self._unit_system))
            except ValueError:
                continue
        return max(lengths, default=0.0)

    def _update_clearance_warning(self) -> None:
        vertical = self._selected_polarization() is Polarization.VERTICAL
        required = self._longest_element_m() / 2.0
        current = length_to_m(self._height.value(), self._unit_system)
        invalid = vertical and required > 0.0 and current <= required
        self._clearance_warning.setText(
            self._translator.t(
                "yagi.clearance_warning",
                height=f"{length_from_m(required, self._unit_system):.3f}",
                unit=self._translator.t(length_unit_key(self._unit_system)),
            )
            if invalid
            else ""
        )
        self._clearance_warning.setVisible(invalid)

    def _radius_m(self) -> float:
        return radius_to_m(self._radius.value(), self._unit_system)

    def _append_element(self, element: YagiElement) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        values = (
            f"element-{row + 1}",
            f"{length_from_m(element.position_m, self._unit_system):.3f}",
            f"{length_from_m(element.length_m, self._unit_system):.3f}",
            f"{radius_from_m(element.radius_m, self._unit_system):.4f}",
        )
        previous_updating = self._updating
        self._updating = True
        try:
            for column, value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(value))
        finally:
            self._updating = previous_updating
        self._refresh_driven_values()

    def _load_preset(self) -> None:
        try:
            yagi = nbs_five_element(
                frequency_hz=self._frequency.value() * 1_000_000.0,
                height_m=length_to_m(self._height.value(), self._unit_system),
                azimuth_deg=self._azimuth.value(),
                polarization=self._selected_polarization(),
                material=self._selected_material(),
                ground=self._ground_model(),
                radius_m=self._radius_m(),
                folded_driven=self._driven_folded.isChecked(),
                folded_spacing_m=length_to_m(
                    self._driven_fold_spacing.value(),
                    self._unit_system,
                ),
            )
        except ValueError:
            self._update_clearance_warning()
            return
        self._table.setRowCount(0)
        self._updating = True
        try:
            for element in yagi.elements:
                self._append_element(element)
        finally:
            self._updating = False
        index = self._driven.findData(yagi.driven_index)
        if index >= 0:
            self._driven.setCurrentIndex(index)
        self._transformer.setValue(yagi.transformer_ratio)
        self._update_geometry()

    def _refresh_driven_values(self, *_args: object) -> None:
        current = self._driven.currentData()
        self._driven.blockSignals(True)
        self._driven.clear()
        for row in range(self._table.rowCount()):
            cell = self._table.item(row, 0)
            if cell is not None and cell.text().strip():
                self._driven.addItem(cell.text().strip(), row)
        self._driven.blockSignals(False)
        if isinstance(current, int):
            index = self._driven.findData(current)
            if index >= 0:
                self._driven.setCurrentIndex(index)
        if not self._updating:
            self._emit_changed()

    def _add_element(self) -> None:
        wavelength = 299_792_458.0 / (self._frequency.value() * 1_000_000.0)
        last_position = 0.0
        if self._table.rowCount():
            cell = self._table.item(self._table.rowCount() - 1, 1)
            if cell is not None:
                last_position = length_to_m(float(cell.text()), self._unit_system)
        self._append_element(
            YagiElement(
                position_m=last_position + 0.2 * wavelength,
                length_m=0.44 * wavelength,
                radius_m=self._radius_m(),
            )
        )

    def _remove_element(self) -> None:
        rows = sorted({index.row() for index in self._table.selectedIndexes()}, reverse=True)
        for row in rows:
            self._table.removeRow(row)
        self._refresh_driven_values()

    def _element_from_row(self, row: int) -> YagiElement:
        def text(column: int) -> str:
            cell = self._table.item(row, column)
            return cell.text().strip() if cell is not None else ""

        return YagiElement(
            position_m=length_to_m(float(text(1)), self._unit_system),
            length_m=length_to_m(float(text(2)), self._unit_system),
            radius_m=radius_to_m(float(text(3)), self._unit_system),
        )

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            parameters = None
        self._unit_system = unit_system
        apply_radius_units(self._translator, unit_system, self._radius)
        apply_radius_units(self._translator, unit_system, self._taper_radius)
        apply_length_suffixes(
            self._translator,
            unit_system,
            self._height,
            self._taper_length,
            self._driven_fold_spacing,
            self._match_length,
            self._match_spacing,
        )
        if parameters is not None:
            self.set_parameters(parameters)

    def set_parameters(self, parameters: YagiParameters) -> None:
        self._updating = True
        try:
            self._last_frequency_mhz = parameters.frequency_hz / 1_000_000.0
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._height.setValue(length_from_m(parameters.height_m, self._unit_system))
            self._azimuth.setValue(parameters.azimuth_deg)
            polarization_index = self._polarization.findData(parameters.polarization.value)
            if polarization_index >= 0:
                self._polarization.setCurrentIndex(polarization_index)
            if parameters.elements:
                self._radius.setValue(
                    radius_from_m(parameters.elements[0].radius_m, self._unit_system)
                )
            self._taper_length.setValue(
                length_from_m(parameters.taper_tip_length_m, self._unit_system)
            )
            self._taper_radius.setValue(
                radius_from_m(parameters.taper_tip_radius_m, self._unit_system)
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
            self._driven_folded.setChecked(parameters.driven_folded)
            self._driven_fold_spacing.setValue(
                length_from_m(parameters.driven_fold_spacing_m, self._unit_system)
            )
            self._transformer.setValue(parameters.transformer_ratio)
            match_index = self._match_type.findData(parameters.match_type.value)
            if match_index >= 0:
                self._match_type.setCurrentIndex(match_index)
            self._match_length.setValue(length_from_m(parameters.match_length_m, self._unit_system))
            self._match_spacing.setValue(
                length_from_m(parameters.match_spacing_m, self._unit_system)
            )
            self._table.setRowCount(0)
            for element in parameters.elements:
                self._append_element(element)
            index = self._driven.findData(parameters.driven_index)
            if index >= 0:
                self._driven.setCurrentIndex(index)
        finally:
            self._updating = False
        self._update_ground_controls()
        self._update_folded_controls()
        self._update_match_controls()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._frequency.setValue(frequency_hz / 1_000_000.0)

    def _update_match_warning(self) -> None:
        driven_row = self._driven.currentData()
        if not isinstance(driven_row, int):
            self._match_warning.setVisible(False)
            return
        try:
            radius_m = self._element_from_row(driven_row).radius_m
        except (ValueError, TypeError):
            self._match_warning.setVisible(False)
            return
        invalid: list[str] = []
        if self._driven_folded.isChecked():
            spacing_m = length_to_m(self._driven_fold_spacing.value(), self._unit_system)
            if spacing_m <= 2.0 * radius_m:
                invalid.append(
                    self._translator.t(
                        "yagi.fold_spacing_clearance",
                        minimum=f"{length_from_m(2.0 * radius_m, self._unit_system):.3f}",
                        unit=self._translator.t(length_unit_key(self._unit_system)),
                    )
                )
        if self._selected_match_type() is YagiMatchType.BETA_HAIRPIN:
            spacing_m = length_to_m(self._match_spacing.value(), self._unit_system)
            length_m = length_to_m(self._match_length.value(), self._unit_system)
            minimum = 2.0 * radius_m
            if spacing_m <= minimum or length_m <= minimum:
                invalid.append(
                    self._translator.t(
                        "yagi.match_clearance_warning",
                        minimum=f"{length_from_m(minimum, self._unit_system):.3f}",
                        unit=self._translator.t(length_unit_key(self._unit_system)),
                    )
                )
        self._match_warning.setText(" ".join(invalid))
        self._match_warning.setVisible(bool(invalid))

    def _update_geometry(self) -> None:
        self._update_clearance_warning()
        self._update_match_warning()
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            return
        positions = [element.position_m for element in parameters.elements]
        unit = self._translator.t(length_unit_key(self._unit_system))
        wavelength = 299_792_458.0 / parameters.frequency_hz
        lengths = [element.length_m for element in parameters.elements]
        mismatch = bool(lengths) and any(
            not 0.35 * wavelength <= length <= 0.65 * wavelength for length in lengths
        )
        self._frequency_warning.setText(
            self._translator.t("yagi.frequency_mismatch") if mismatch else ""
        )
        self._frequency_warning.setVisible(mismatch)
        geometry = self._translator.t(
            "yagi.geometry",
            count=len(parameters.elements),
            boom=f"{length_from_m(max(positions) - min(positions), self._unit_system):.2f}",
            unit=unit,
        )
        if parameters.driven_folded:
            geometry += " · " + self._translator.t(
                "yagi.folded_geometry",
                spacing=f"{length_from_m(parameters.driven_fold_spacing_m, self._unit_system):.3f}",
                unit=unit,
            )
            if parameters.transformer_ratio != 1.0:
                geometry += " · " + self._translator.t(
                    "yagi.transformer_geometry",
                    ratio=f"{parameters.transformer_ratio:g}",
                )
        if parameters.match_type is YagiMatchType.BETA_HAIRPIN:
            geometry += " · " + self._translator.t(
                "yagi.match_geometry",
                length=f"{length_from_m(parameters.match_length_m, self._unit_system):.3f}",
                spacing=f"{length_from_m(parameters.match_spacing_m, self._unit_system):.3f}",
                unit=unit,
            )
        if parameters.is_tapered:
            geometry += " · " + self._translator.t(
                "yagi.taper_geometry",
                length=f"{length_from_m(parameters.taper_tip_length_m, self._unit_system):.3f}",
                radius=f"{radius_from_m(parameters.taper_tip_radius_m, self._unit_system):.4f}",
                unit=unit,
                radius_unit=self._translator.t(radius_unit_key(self._unit_system)),
            )
        self._geometry.setText(geometry)

    def parameters(self) -> YagiParameters:
        driven_row = self._driven.currentData()
        if not isinstance(driven_row, int):
            raise ValueError("select a driven element")
        rows = [(row, self._element_from_row(row)) for row in range(self._table.rowCount())]
        rows.sort(key=lambda item: item[1].position_m)
        driven_index = next(
            index for index, (row, _element) in enumerate(rows) if row == driven_row
        )
        taper_length_m = length_to_m(
            self._taper_length.value(),
            self._unit_system,
        )
        return YagiParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            elements=tuple(element for _row, element in rows),
            height_m=length_to_m(self._height.value(), self._unit_system),
            taper_tip_length_m=taper_length_m,
            taper_tip_radius_m=(
                radius_to_m(self._taper_radius.value(), self._unit_system)
                if taper_length_m > 0.0
                else 0.0
            ),
            driven_index=driven_index,
            driven_folded=self._driven_folded.isChecked(),
            driven_fold_spacing_m=length_to_m(
                self._driven_fold_spacing.value(),
                self._unit_system,
            ),
            match_type=self._selected_match_type(),
            match_length_m=length_to_m(self._match_length.value(), self._unit_system),
            match_spacing_m=length_to_m(self._match_spacing.value(), self._unit_system),
            transformer_ratio=(
                self._transformer.value() if self._driven_folded.isChecked() else 1.0
            ),
            azimuth_deg=self._azimuth.value(),
            polarization=self._selected_polarization(),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
