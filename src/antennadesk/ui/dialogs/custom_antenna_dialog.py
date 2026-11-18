# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Editor for custom straight-wire antennas."""

from __future__ import annotations

import math

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.custom import CustomAntennaParameters, geometry_warnings
from ...domain.antennas.feed import FeedPoint
from ...domain.antennas.geometry import Point3D
from ...domain.antennas.load import LumpedLoad
from ...domain.antennas.materials import COPPER, ConductorMaterial
from ...domain.antennas.wire import Wire
from ...domain.common.validation import Diagnostic
from ...domain.environment.ground import GroundKind, GroundModel
from ..fonts import scaled_dialog_size
from ..help import apply_row_help
from ..i18n import Translator
from ..material_combo import (
    populate_material_combo,
)
from ..units import (
    DisplayUnits,
    LengthPolicy,
    LengthUnit,
    UnitSystem,
    length_unit_key,
    radius_from_m,
    radius_to_m,
    radius_unit_key,
)
from ..widgets.form_units import LengthField, LengthFieldSpec
from ..widgets.ground_presets import GroundPresetController


class CustomAntennaDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: CustomAntennaParameters | None = None,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        display_units: DisplayUnits | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._display_units = display_units or DisplayUnits(
            unit_system,
            LengthPolicy.FIXED,
        )
        self._table_unit: LengthUnit = self._display_units.table_unit(())
        self._loads: tuple[LumpedLoad, ...] = parameters.loads if parameters else ()
        self._generator_id = parameters.generator_id if parameters else None
        self._generator_name = parameters.generator_name if parameters else None
        self._warnings: tuple[Diagnostic, ...] = ()
        self.setWindowTitle(translator.t("custom.title"))
        self.resize(*scaled_dialog_size(980, 620))

        self._name = QLabel(translator.t("custom.metric_hint"), self)
        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        initial_frequency_hz = (
            parameters.frequency_hz
            if parameters
            else (frequency_hz if frequency_hz is not None else 7_100_000.0)
        )
        self._frequency.setValue(initial_frequency_hz / 1e6)

        self._material = QComboBox(self)
        populate_material_combo(self._material, translator)

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
        self._soil = QComboBox(self)
        self._ground_presets = GroundPresetController(
            self._ground,
            self._soil,
            self._permittivity,
            self._conductivity,
            translator,
        )

        self._table = QTableWidget(0, 8, self)
        self._retranslate_table_headers()
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.itemChanged.connect(self._refresh_feed_values)

        self._add = QPushButton(translator.t("custom.add_wire"), self)
        self._remove = QPushButton(translator.t("custom.remove_wire"), self)
        self._add.clicked.connect(self._add_wire)
        self._remove.clicked.connect(self._remove_wire)

        self._radial_count = QSpinBox(self)
        self._radial_count.setRange(1, 64)
        self._radial_count.setValue(8)
        self._radial_length = QDoubleSpinBox(self)
        self._radial_length.setRange(0.1, 1_000.0)
        self._radial_length.setDecimals(3)
        self._radial_length.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._radial_angle = QDoubleSpinBox(self)
        self._radial_angle.setRange(0.0, 360.0)
        self._radial_angle.setDecimals(1)
        self._radial_angle.setSuffix("°")
        self._add_radials = QPushButton(translator.t("custom.add_radials"), self)
        self._add_radials.clicked.connect(self._add_radial_wires)

        self._feed_wire = QComboBox(self)
        self._feed_wire.currentIndexChanged.connect(self._update_feed_range)
        self._feed_offset = QDoubleSpinBox(self)
        self._feed_offset.setDecimals(3)
        self._feed_offset.setRange(0.0, 1.0)
        self._feed_offset.setSuffix(f" {translator.t(length_unit_key(unit_system))}")

        self._radial_length_field = LengthField(
            self._radial_length,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._feed_offset_field = LengthField(
            self._feed_offset,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._radial_length_field.configure(5.0)
        self._feed_offset_field.configure(0.0)

        form = QFormLayout()
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.soil_preset"), self._soil)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)
        form.addRow(translator.t("custom.feed_wire"), self._feed_wire)
        form.addRow(translator.t("custom.feed_offset"), self._feed_offset)
        for row, key in enumerate(
            (
                "field.frequency",
                "field.material",
                "field.ground",
                "field.soil_preset",
                "field.permittivity",
                "field.conductivity",
                "custom.feed_wire",
                "custom.feed_offset",
            )
        ):
            apply_row_help(form, row, translator, key)

        radial_group = QGroupBox(translator.t("custom.radials_title"), self)
        radial_form = QFormLayout(radial_group)
        radial_form.addRow(translator.t("custom.radial_count"), self._radial_count)
        radial_form.addRow(translator.t("custom.radial_length"), self._radial_length)
        radial_form.addRow(translator.t("custom.radial_angle"), self._radial_angle)
        radial_form.addRow(self._add_radials)
        radial_hint = QLabel(translator.t("custom.radials_hint"), radial_group)
        radial_hint.setWordWrap(True)
        radial_form.addRow(radial_hint)
        apply_row_help(radial_form, 0, translator, "custom.radial_count")
        apply_row_help(radial_form, 1, translator, "custom.radial_length")
        apply_row_help(radial_form, 2, translator, "custom.radial_angle")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        add_remove = QHBoxLayout()
        add_remove.addWidget(self._add)
        add_remove.addWidget(self._remove)
        add_remove.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(self._name)
        layout.addWidget(self._table, 1)
        layout.addLayout(add_remove)
        layout.addWidget(radial_group)
        layout.addLayout(form)
        layout.addWidget(buttons)

        if parameters is None:
            self._append_wire(
                Wire(
                    id="wire-1",
                    start=Point3D(-5.0, 0.0, 8.0),
                    end=Point3D(5.0, 0.0, 8.0),
                    radius_m=0.001,
                    material=COPPER,
                )
            )
        else:
            self._set_table_unit_from_wires(parameters.wires)
            for wire in parameters.wires:
                self._append_wire(wire)
            self._set_ground(parameters.ground)
            self._set_material(parameters.wires[0].material if parameters.wires else COPPER)
        self._update_ground_controls()
        self._refresh_feed_values()
        if parameters is None:
            self._feed_offset_field.configure(5.0)

    def _retranslate_table_headers(self) -> None:
        t = self._translator.t
        coordinate_keys = (
            "custom.start_x",
            "custom.start_y",
            "custom.start_z",
            "custom.end_x",
            "custom.end_y",
            "custom.end_z",
        )
        self._table.setHorizontalHeaderLabels(
            [
                t("custom.id"),
                *(f"{t(key)} ({self._table_unit})" for key in coordinate_keys),
                t(
                    "custom.radius",
                    unit=t(radius_unit_key(self._unit_system)),
                ),
            ]
        )

    def _table_value(self, value_m: float) -> str:
        value = value_m / self._display_units.meters_per_unit(self._table_unit)
        return f"{value:.{self._display_units.decimals_for(self._table_unit)}f}"

    def _table_value_m(self, text: str) -> float:
        return float(text) * self._display_units.meters_per_unit(self._table_unit)

    def _set_table_unit_from_wires(self, wires: tuple[Wire, ...]) -> None:
        values = [
            coordinate
            for wire in wires
            for coordinate in (
                wire.start.x_m,
                wire.start.y_m,
                wire.start.z_m,
                wire.end.x_m,
                wire.end.y_m,
                wire.end.z_m,
            )
        ]
        self._table_unit = self._display_units.table_unit(values)
        self._retranslate_table_headers()

    def _append_wire(self, wire: Wire) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        values = [
            wire.id,
            self._table_value(wire.start.x_m),
            self._table_value(wire.start.y_m),
            self._table_value(wire.start.z_m),
            self._table_value(wire.end.x_m),
            self._table_value(wire.end.y_m),
            self._table_value(wire.end.z_m),
            f"{radius_from_m(wire.radius_m, self._unit_system):.4f}",
        ]
        for column, value in enumerate(values):
            self._table.setItem(row, column, QTableWidgetItem(value))

    def _add_wire(self) -> None:
        index = self._table.rowCount() + 1
        self._append_wire(
            Wire(
                id=f"wire-{index}",
                start=Point3D(-5.0, 0.0, 8.0),
                end=Point3D(5.0, 0.0, 8.0),
                radius_m=0.001,
                material=self._selected_material(),
            )
        )
        self._refresh_feed_values()

    def _add_radial_wires(self) -> None:
        count = self._radial_count.value()
        length_m = self._radial_length_field.value_m()
        step = 360.0 / count
        material = self._selected_material()
        start = self._table.rowCount() + 1
        for index in range(count):
            angle = math.radians(self._radial_angle.value() + index * step)
            wire_id = f"radial-{start + index}"
            self._append_wire(
                Wire(
                    id=wire_id,
                    start=Point3D(0.0, 0.0, 0.0),
                    end=Point3D(
                        length_m * math.cos(angle),
                        length_m * math.sin(angle),
                        0.0,
                    ),
                    radius_m=max(
                        self._selected_material().conductivity_s_per_m * 0.0 + 0.001, 0.001
                    ),
                    material=material,
                )
            )
        self._refresh_feed_values()

    def _remove_wire(self) -> None:
        rows = sorted({index.row() for index in self._table.selectedIndexes()}, reverse=True)
        for row in rows:
            self._table.removeRow(row)
        self._refresh_feed_values()

    def _selected_material(self) -> ConductorMaterial:
        value = self._material.currentData()
        return value if isinstance(value, ConductorMaterial) else COPPER

    def _set_material(self, material: ConductorMaterial) -> None:
        index = self._material.findData(material)
        if index >= 0:
            self._material.setCurrentIndex(index)

    def _set_ground(self, ground: GroundModel) -> None:
        index = self._ground.findData(ground.kind.value)
        if index >= 0:
            self._ground.setCurrentIndex(index)
        if ground.relative_permittivity is not None:
            self._permittivity.setValue(ground.relative_permittivity)
        if ground.conductivity_s_per_m is not None:
            self._conductivity.setValue(ground.conductivity_s_per_m)

    def _table_wire(self, row: int) -> Wire:
        def item(column: int) -> str:
            cell = self._table.item(row, column)
            return cell.text().strip() if cell is not None else ""

        def coordinate(column: int) -> float:
            return self._table_value_m(item(column))

        return Wire(
            id=item(0),
            start=Point3D(coordinate(1), coordinate(2), coordinate(3)),
            end=Point3D(coordinate(4), coordinate(5), coordinate(6)),
            radius_m=radius_to_m(float(item(7)), self._unit_system),
            material=self._selected_material(),
        )

    def _wires(self) -> tuple[Wire, ...]:
        return tuple(self._table_wire(row) for row in range(self._table.rowCount()))

    def _refresh_feed_values(self, *_args: object) -> None:
        current = self._feed_wire.currentData()
        self._feed_wire.blockSignals(True)
        self._feed_wire.clear()
        for row in range(self._table.rowCount()):
            cell = self._table.item(row, 0)
            if cell is not None and cell.text().strip():
                self._feed_wire.addItem(cell.text().strip(), cell.text().strip())
        self._feed_wire.blockSignals(False)
        if isinstance(current, str):
            index = self._feed_wire.findData(current)
            if index >= 0:
                self._feed_wire.setCurrentIndex(index)
        self._update_feed_range()

    def _update_feed_range(self) -> None:
        wire_id = self._feed_wire.currentData()
        if not isinstance(wire_id, str):
            return
        try:
            wire = next((item for item in self._wires() if item.id == wire_id), None)
        except ValueError:
            return
        if wire is None:
            return
        self._feed_offset_field.set_range_m(0.0, wire.length_m)

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

    def _accept(self) -> None:
        try:
            parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("custom.title"), str(exc))
            return
        self._parameters = parameters
        self._warnings = geometry_warnings(parameters)
        if self._warnings:
            QMessageBox.warning(
                self,
                self._translator.t("custom.title"),
                "\n".join(diagnostic.message for diagnostic in self._warnings),
            )
        self.accept()

    def parameters(self) -> CustomAntennaParameters:
        wires = self._wires()
        feed_wire = self._feed_wire.currentData()
        if not isinstance(feed_wire, str):
            raise ValueError("select a feed wire")
        return CustomAntennaParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            wires=wires,
            feed=FeedPoint(feed_wire, self._feed_offset_field.value_m()),
            ground=self._ground_model(),
            loads=self._loads,
            generator_id=self._generator_id,
            generator_name=self._generator_name,
        )

    def result_parameters(self) -> CustomAntennaParameters:
        return self._parameters

    def result_warnings(self) -> tuple[Diagnostic, ...]:
        return self._warnings
