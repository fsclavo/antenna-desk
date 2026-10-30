# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided Yagi generator with an editable element table."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.custom import CustomAntennaParameters
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.yagi import YagiElement, YagiParameters, nbs_five_element
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key

MATERIALS = (COPPER, ALUMINUM)


class YagiDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: CustomAntennaParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._parameters: CustomAntennaParameters | None = None
        self._updating = False

        self.setWindowTitle(translator.t("yagi.title"))
        self.resize(920, 680)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(frequency_hz / 1_000_000.0 if frequency_hz is not None else 14.1)

        self._height = QDoubleSpinBox(self)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(12.0, unit_system))

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._radius = QDoubleSpinBox(self)
        self._radius.setRange(0.01, 1_000.0)
        self._radius.setDecimals(3)
        self._radius.setSuffix(" mm")
        self._radius.setValue(6.35)

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
        self._ground.currentIndexChanged.connect(self._update_ground_controls)

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

        self._table = QTableWidget(0, 4, self)
        self._table.setHorizontalHeaderLabels(
            [
                translator.t("yagi.element"),
                translator.t("yagi.position"),
                translator.t("yagi.length"),
                translator.t("yagi.radius_mm"),
            ]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.itemChanged.connect(self._refresh_driven_values)

        self._add = QPushButton(translator.t("yagi.add_element"), self)
        self._remove = QPushButton(translator.t("yagi.remove_element"), self)
        self._preset = QPushButton(translator.t("yagi.nbs_preset"), self)
        self._add.clicked.connect(self._add_element)
        self._remove.clicked.connect(self._remove_element)
        self._preset.clicked.connect(self._load_preset)

        self._driven = QComboBox(self)

        self._hint = QLabel(translator.t("yagi.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("yagi.evidence"), self)
        self._evidence.setWordWrap(True)

        form = QFormLayout()
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("field.height"), self._height)
        form.addRow(translator.t("field.azimuth"), self._azimuth)
        form.addRow(translator.t("yagi.radius_mm"), self._radius)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)
        form.addRow(translator.t("yagi.driven"), self._driven)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        element_buttons = QHBoxLayout()
        element_buttons.addWidget(self._add)
        element_buttons.addWidget(self._remove)
        element_buttons.addWidget(self._preset)
        element_buttons.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addWidget(self._table, 1)
        layout.addLayout(element_buttons)
        layout.addWidget(buttons)

        if parameters is not None:
            self._set_existing(parameters)
        else:
            self._load_preset()
        self._update_ground_controls()

    def _set_existing(self, parameters: CustomAntennaParameters) -> None:
        existing = YagiParameters.from_custom_parameters(parameters)
        self._frequency.setValue(existing.frequency_hz / 1_000_000.0)
        self._height.setValue(length_from_m(existing.height_m, self._unit_system))
        self._azimuth.setValue(existing.azimuth_deg)
        if existing.elements:
            self._radius.setValue(existing.elements[0].radius_m * 1_000.0)
        material_index = self._material.findData(existing.material)
        if material_index >= 0:
            self._material.setCurrentIndex(material_index)
        ground_index = self._ground.findData(existing.ground.kind.value)
        if ground_index >= 0:
            self._ground.setCurrentIndex(ground_index)
        if existing.ground.relative_permittivity is not None:
            self._permittivity.setValue(existing.ground.relative_permittivity)
        if existing.ground.conductivity_s_per_m is not None:
            self._conductivity.setValue(existing.ground.conductivity_s_per_m)
        self._table.setRowCount(0)
        self._updating = True
        try:
            for element in existing.elements:
                self._append_element(element)
        finally:
            self._updating = False
        index = self._driven.findData(existing.driven_index)
        if index >= 0:
            self._driven.setCurrentIndex(index)

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

    def _radius_m(self) -> float:
        return self._radius.value() / 1_000.0

    def _append_element(self, element: YagiElement) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        values = (
            f"element-{row + 1}",
            f"{length_from_m(element.position_m, self._unit_system):.3f}",
            f"{length_from_m(element.length_m, self._unit_system):.3f}",
            f"{element.radius_m * 1_000.0:.3f}",
        )
        self._updating = True
        try:
            for column, value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(value))
        finally:
            self._updating = False
        self._refresh_driven_values()

    def _load_preset(self) -> None:
        yagi = nbs_five_element(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            height_m=length_to_m(self._height.value(), self._unit_system),
            azimuth_deg=self._azimuth.value(),
            material=self._selected_material(),
            ground=self._ground_model(),
            radius_m=self._radius_m(),
        )
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

    def _refresh_driven_values(self, *_args: object) -> None:
        if self._updating:
            return
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
            radius_m=float(text(3)) / 1_000.0,
        )

    def parameters(self) -> CustomAntennaParameters:
        elements = tuple(self._element_from_row(row) for row in range(self._table.rowCount()))
        driven_index = self._driven.currentData()
        if not isinstance(driven_index, int):
            raise ValueError("select a driven element")
        yagi = YagiParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            elements=elements,
            height_m=length_to_m(self._height.value(), self._unit_system),
            driven_index=driven_index,
            azimuth_deg=self._azimuth.value(),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
        return yagi.to_custom_parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("yagi.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> CustomAntennaParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
