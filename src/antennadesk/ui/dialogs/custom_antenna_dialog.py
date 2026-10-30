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
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.antennas.wire import Wire
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key

MATERIALS = (COPPER, ALUMINUM)


class CustomAntennaDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: CustomAntennaParameters | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._loads: tuple[LumpedLoad, ...] = parameters.loads if parameters else ()
        self._warnings = ()
        self.setWindowTitle(translator.t("custom.title"))
        self.resize(980, 620)

        self._name = QLabel(translator.t("custom.metric_hint"), self)
        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue((parameters.frequency_hz if parameters else 7_100_000.0) / 1e6)

        self._material = QComboBox(self)
        for material in MATERIALS:
            self._material.addItem(material.name, material)

        self._ground = QComboBox(self)
        self._ground.addItem("", GroundKind.FREE_SPACE.value)
        self._ground.addItem("", GroundKind.PERFECT.value)
        self._ground.addItem("", GroundKind.FINITE.value)
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

        self._table = QTableWidget(0, 8, self)
        self._table.setHorizontalHeaderLabels(
            [
                translator.t("custom.id"),
                translator.t("custom.start_x"),
                translator.t("custom.start_y"),
                translator.t("custom.start_z"),
                translator.t("custom.end_x"),
                translator.t("custom.end_y"),
                translator.t("custom.end_z"),
                translator.t("custom.radius"),
            ]
        )
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
        self._radial_length.setValue(length_from_m(5.0, unit_system))
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

        form = QFormLayout()
        form.addRow(translator.t("field.frequency"), self._frequency)
        form.addRow(translator.t("field.material"), self._material)
        form.addRow(translator.t("field.ground"), self._ground)
        form.addRow(translator.t("field.permittivity"), self._permittivity)
        form.addRow(translator.t("field.conductivity"), self._conductivity)
        form.addRow(translator.t("custom.feed_wire"), self._feed_wire)
        form.addRow(translator.t("custom.feed_offset"), self._feed_offset)

        radial_group = QGroupBox(translator.t("custom.radials_title"), self)
        radial_form = QFormLayout(radial_group)
        radial_form.addRow(translator.t("custom.radial_count"), self._radial_count)
        radial_form.addRow(translator.t("custom.radial_length"), self._radial_length)
        radial_form.addRow(translator.t("custom.radial_angle"), self._radial_angle)
        radial_form.addRow(self._add_radials)
        radial_hint = QLabel(translator.t("custom.radials_hint"), radial_group)
        radial_hint.setWordWrap(True)
        radial_form.addRow(radial_hint)

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
            for wire in parameters.wires:
                self._append_wire(wire)
            self._set_ground(parameters.ground)
            self._set_material(parameters.wires[0].material if parameters.wires else COPPER)
        self._update_ground_controls()
        self._refresh_feed_values()
        if parameters is None:
            self._feed_offset.setValue(length_from_m(5.0, self._unit_system))

    def _append_wire(self, wire: Wire) -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        values = [
            wire.id,
            length_from_m(wire.start.x_m, self._unit_system),
            length_from_m(wire.start.y_m, self._unit_system),
            length_from_m(wire.start.z_m, self._unit_system),
            length_from_m(wire.end.x_m, self._unit_system),
            length_from_m(wire.end.y_m, self._unit_system),
            length_from_m(wire.end.z_m, self._unit_system),
            wire.radius_m * 1000.0,
        ]
        for column, value in enumerate(values):
            text = f"{value:.3f}" if isinstance(value, float) else str(value)
            self._table.setItem(row, column, QTableWidgetItem(text))

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
        length_m = length_to_m(self._radial_length.value(), self._unit_system)
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
            return length_to_m(float(item(column)), self._unit_system)

        return Wire(
            id=item(0),
            start=Point3D(coordinate(1), coordinate(2), coordinate(3)),
            end=Point3D(coordinate(4), coordinate(5), coordinate(6)),
            radius_m=float(item(7)) / 1000.0,
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
        self._feed_offset.setRange(0.0, length_from_m(wire.length_m, self._unit_system))

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
            feed=FeedPoint(feed_wire, length_to_m(self._feed_offset.value(), self._unit_system)),
            ground=self._ground_model(),
            loads=self._loads,
        )

    def result_parameters(self) -> CustomAntennaParameters:
        return self._parameters

    def result_warnings(self) -> tuple[object, ...]:
        return self._warnings
