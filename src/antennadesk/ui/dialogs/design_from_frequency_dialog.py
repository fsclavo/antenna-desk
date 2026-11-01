# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency-first dimension estimation dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...application.use_cases.estimate_antenna_dimensions import (
    EstimateAntennaDimensions,
)
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.antennas.dipole import ANTENNA_TYPE_WIRE_DIPOLE, DipoleOrientation
from ...domain.antennas.endfed import ANTENNA_TYPE_ENDFED
from ...domain.antennas.fan_dipole import ANTENNA_TYPE_FAN_DIPOLE
from ...domain.antennas.folded_dipole import ANTENNA_TYPE_FOLDED_DIPOLE
from ...domain.antennas.inverted_v import ANTENNA_TYPE_INVERTED_V
from ...domain.antennas.j_pole import ANTENNA_TYPE_J_POLE
from ...domain.antennas.loop import ANTENNA_TYPE_LOOP
from ...domain.antennas.moxon import ANTENNA_TYPE_MOXON
from ...domain.antennas.ocfd import ANTENNA_TYPE_OCFD
from ...domain.antennas.ringo import ANTENNA_TYPE_RINGO
from ...domain.antennas.vertical import ANTENNA_TYPE_VERTICAL
from ...domain.antennas.yagi import ANTENNA_TYPE_YAGI
from ...domain.design import (
    DesignIntent,
    DimensionEstimate,
    DimensionUnit,
    LoopShape,
    UnsupportedEstimateError,
    VerticalForm,
)
from ..i18n import Translator
from ..units import (
    UnitSystem,
    length_bounds,
    length_from_m,
    length_to_m,
    length_unit_key,
)


class DesignFromFrequencyDialog(QDialog):
    """Estimate initial dimensions from a frequency and a family intent."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        *,
        initial_frequency_hz: float = 7_100_000.0,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._estimate_use_case = EstimateAntennaDimensions()
        self._estimate: DimensionEstimate | None = None
        self.setWindowTitle(translator.t("design_from_frequency.title"))
        self.resize(760, 680)

        self._family = QComboBox(self)
        for key, antenna_type in (
            ("antenna_type.wire_dipole", ANTENNA_TYPE_WIRE_DIPOLE),
            ("antenna_type.folded_dipole", ANTENNA_TYPE_FOLDED_DIPOLE),
            ("antenna_type.loop", ANTENNA_TYPE_LOOP),
            ("vertical.title", ANTENNA_TYPE_VERTICAL),
            ("inverted_v.title", ANTENNA_TYPE_INVERTED_V),
            ("fan_dipole.title", ANTENNA_TYPE_FAN_DIPOLE),
            ("endfed.title", ANTENNA_TYPE_ENDFED),
            ("ocfd.title", ANTENNA_TYPE_OCFD),
            ("j_pole.title", ANTENNA_TYPE_J_POLE),
            ("ringo.title", ANTENNA_TYPE_RINGO),
            ("yagi.title", ANTENNA_TYPE_YAGI),
            ("moxon.title", ANTENNA_TYPE_MOXON),
        ):
            self._family.addItem(translator.t(key), antenna_type)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(initial_frequency_hz / 1_000_000.0)

        length_min, length_max = length_bounds(unit_system)
        unit = translator.t(length_unit_key(unit_system))
        self._height = QDoubleSpinBox(self)
        self._height.setRange(length_min, length_max)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {unit}")
        self._height.setValue(length_from_m(10.0, unit_system))

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setRange(0.0, length_max)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {unit}")
        self._base_height.setValue(length_from_m(0.25, unit_system))

        self._end_height = QDoubleSpinBox(self)
        self._end_height.setRange(0.0, length_max)
        self._end_height.setDecimals(3)
        self._end_height.setSuffix(f" {unit}")
        self._end_height.setValue(length_from_m(10.0, unit_system))

        self._orientation = QComboBox(self)
        self._orientation.addItem("", DipoleOrientation.HORIZONTAL.value)
        self._orientation.addItem("", DipoleOrientation.VERTICAL.value)

        self._loop_shape = QComboBox(self)
        self._loop_shape.addItem(translator.t("antenna_type.loop"), LoopShape.LOOP.value)
        self._loop_shape.addItem(translator.t("catalog.quad_loop"), LoopShape.QUAD.value)
        self._loop_shape.addItem(translator.t("catalog.delta_loop"), LoopShape.DELTA.value)

        self._vertical_form = QComboBox(self)
        self._vertical_form.addItem("1/4 λ", VerticalForm.QUARTER_WAVE.value)
        self._vertical_form.addItem("5/8 λ", VerticalForm.FIVE_EIGHTH_WAVE.value)

        self._j_pole_variant = QComboBox(self)
        self._j_pole_variant.addItem(translator.t("catalog.j_pole"), False)
        self._j_pole_variant.addItem(translator.t("catalog.slim_jim"), True)

        self._included_angle = QDoubleSpinBox(self)
        self._included_angle.setRange(1.0, 179.0)
        self._included_angle.setDecimals(1)
        self._included_angle.setSuffix("°")
        self._included_angle.setValue(120.0)

        self._fan_bands = QLineEdit(self)
        self._fan_bands.setPlaceholderText("7.1, 14.1, 21.0")
        self._fan_bands.setText(f"{initial_frequency_hz / 1_000_000.0:.3f}")

        self._radial_count = QSpinBox(self)
        self._radial_count.setRange(0, 32)
        self._radial_count.setValue(4)

        self._yagi_elements = QSpinBox(self)
        self._yagi_elements.setRange(5, 5)
        self._yagi_elements.setValue(5)

        self._form = QFormLayout()
        self._rows: dict[str, tuple[QLabel, QWidget]] = {}
        self._add_row("family", "design_from_frequency.family", self._family)
        self._add_row("frequency", "field.frequency", self._frequency)
        self._add_row("height", "field.height", self._height)
        self._add_row("base_height", "field.base_height", self._base_height)
        self._add_row("end_height", "geometry.end_height", self._end_height)
        self._add_row("orientation", "field.orientation", self._orientation)
        self._add_row("loop_shape", "design_from_frequency.loop_shape", self._loop_shape)
        self._add_row("vertical_form", "design_from_frequency.vertical_form", self._vertical_form)
        self._add_row("j_pole_variant", "field.template", self._j_pole_variant)
        self._add_row("included_angle", "inverted_v.included_angle", self._included_angle)
        self._add_row("fan_bands", "design_from_frequency.fan_bands", self._fan_bands)
        self._add_row("radial_count", "vertical.radial_count", self._radial_count)
        self._add_row("yagi_elements", "geometry.elements", self._yagi_elements)

        self._estimate_button = QPushButton(
            translator.t("design_from_frequency.estimate"),
            self,
        )
        self._estimate_button.clicked.connect(self._run_estimate)

        self._results = QTableWidget(0, 2, self)
        self._results.setHorizontalHeaderLabels(
            [
                translator.t("design_from_frequency.dimension"),
                translator.t("design_from_frequency.value"),
            ]
        )
        self._results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._results.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        self._assumptions = QLabel(self)
        self._assumptions.setWordWrap(True)
        self._warnings = QLabel(self)
        self._warnings.setWordWrap(True)
        self._sources = QLabel(self)
        self._sources.setWordWrap(True)
        self._hint = QLabel(translator.t("design_from_frequency.hint"), self)
        self._hint.setWordWrap(True)

        self._apply = QPushButton(translator.t("design_from_frequency.apply"), self)
        self._apply.setEnabled(False)
        self._apply.clicked.connect(self._accept)
        close = QPushButton(translator.t("action.close"), self)
        close.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(self._estimate_button)
        buttons.addStretch(1)
        buttons.addWidget(self._apply)
        buttons.addWidget(close)

        layout = QVBoxLayout(self)
        layout.addLayout(self._form)
        layout.addWidget(self._results, 1)
        layout.addWidget(self._assumptions)
        layout.addWidget(self._warnings)
        layout.addWidget(self._sources)
        layout.addWidget(self._hint)
        layout.addLayout(buttons)

        self._family.currentIndexChanged.connect(self._update_rows)
        for signal in (
            self._frequency.valueChanged,
            self._height.valueChanged,
            self._base_height.valueChanged,
            self._end_height.valueChanged,
            self._orientation.currentIndexChanged,
            self._loop_shape.currentIndexChanged,
            self._vertical_form.currentIndexChanged,
            self._j_pole_variant.currentIndexChanged,
            self._included_angle.valueChanged,
            self._fan_bands.textChanged,
            self._radial_count.valueChanged,
            self._yagi_elements.valueChanged,
        ):
            signal.connect(self._clear_estimate)
        self._update_rows()
        self.retranslate()

    def _add_row(self, key: str, label_key: str, widget: QWidget) -> None:
        label = QLabel(self)
        label.setObjectName(label_key)
        self._form.addRow(label, widget)
        self._rows[key] = (label, widget)

    def _update_rows(self) -> None:
        family = self._family.currentData()
        visible = {"family", "frequency"}
        if family in {ANTENNA_TYPE_WIRE_DIPOLE, ANTENNA_TYPE_FOLDED_DIPOLE, ANTENNA_TYPE_LOOP}:
            visible.add("height")
        if family == ANTENNA_TYPE_WIRE_DIPOLE:
            visible.add("orientation")
        if family == ANTENNA_TYPE_LOOP:
            visible.add("loop_shape")
        if family in {ANTENNA_TYPE_VERTICAL, ANTENNA_TYPE_J_POLE}:
            visible.add("base_height")
        if family == ANTENNA_TYPE_VERTICAL:
            visible.update({"vertical_form", "radial_count"})
        if family == ANTENNA_TYPE_J_POLE:
            visible.add("j_pole_variant")
        if family in {ANTENNA_TYPE_INVERTED_V, ANTENNA_TYPE_FAN_DIPOLE}:
            visible.add("included_angle")
        if family == ANTENNA_TYPE_FAN_DIPOLE:
            visible.add("fan_bands")
        if family == ANTENNA_TYPE_ENDFED:
            visible.update({"height", "end_height"})
        if family in {
            ANTENNA_TYPE_OCFD,
            ANTENNA_TYPE_YAGI,
            ANTENNA_TYPE_MOXON,
        }:
            visible.add("height")
        if family == ANTENNA_TYPE_YAGI:
            visible.add("yagi_elements")
        for key, (label, widget) in self._rows.items():
            label.setVisible(key in visible)
            widget.setVisible(key in visible)
        self._clear_estimate()

    def _clear_estimate(self, *_args: object) -> None:
        self._estimate = None
        self._results.setRowCount(0)
        self._apply.setEnabled(False)
        self._assumptions.clear()
        self._warnings.clear()
        self._sources.clear()

    def _build_intent(self) -> DesignIntent:
        family = str(self._family.currentData())
        fan_bands: tuple[float, ...] = ()
        if family == ANTENNA_TYPE_FAN_DIPOLE:
            raw = self._fan_bands.text().replace(";", ",")
            bands = [float(part.strip()) * 1_000_000.0 for part in raw.split(",") if part.strip()]
            if not bands:
                raise ValueError(self._translator.t("design_from_frequency.invalid_bands"))
            fan_bands = tuple(bands)
        return DesignIntent(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            antenna_type=family,
            height_m=length_to_m(self._height.value(), self._unit_system),
            base_height_m=length_to_m(self._base_height.value(), self._unit_system),
            end_height_m=length_to_m(self._end_height.value(), self._unit_system),
            orientation=DipoleOrientation(str(self._orientation.currentData())),
            loop_shape=LoopShape(str(self._loop_shape.currentData())),
            vertical_form=VerticalForm(str(self._vertical_form.currentData())),
            folded=bool(self._j_pole_variant.currentData()),
            included_angle_deg=self._included_angle.value(),
            radial_count=self._radial_count.value(),
            fan_bands_hz=fan_bands,
            yagi_elements=self._yagi_elements.value(),
        )

    def _run_estimate(self) -> None:
        try:
            intent = self._build_intent()
            self._estimate = self._estimate_use_case.execute(intent)
        except (UnsupportedEstimateError, ValueError, TypeError) as exc:
            self._estimate = None
            self._results.setRowCount(0)
            self._apply.setEnabled(False)
            self._assumptions.clear()
            self._warnings.clear()
            self._sources.clear()
            QMessageBox.warning(
                self,
                self._translator.t("design_from_frequency.title"),
                str(exc),
            )
            return
        self._show_estimate(self._estimate)

    def _show_estimate(self, estimate: DimensionEstimate) -> None:
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._results.setRowCount(0)
        for row in estimate.rows:
            index = self._results.rowCount()
            self._results.insertRow(index)
            self._results.setItem(
                index,
                0,
                QTableWidgetItem(self._translator.t(row.label_key)),
            )
            if row.unit is DimensionUnit.LENGTH:
                value = f"{length_from_m(row.value, self._unit_system):.3f} {unit}"
            elif row.unit is DimensionUnit.ANGLE:
                value = f"{row.value:.1f}°"
            else:
                value = f"{row.value:g}"
            self._results.setItem(index, 1, QTableWidgetItem(value))
        tolerance = f"{length_from_m(estimate.tolerance_m, self._unit_system):.3f} {unit}"
        self._assumptions.setText(
            self._translator.t(
                "design_from_frequency.confidence",
                value=self._translator.t(f"confidence.{estimate.confidence.value}"),
            )
            + " · "
            + self._translator.t(
                "design_from_frequency.tolerance",
                value=tolerance,
            )
            + "\n"
            + self._translator.t(
                "design_from_frequency.assumptions",
                values=" · ".join(self._translator.t(key) for key in estimate.assumptions),
            )
        )
        self._warnings.setText(
            self._translator.t(
                "design_from_frequency.warnings",
                values=" · ".join(self._translator.t(key) for key in estimate.warnings),
            )
        )
        self._sources.setText(
            self._translator.t(
                "design_from_frequency.sources",
                values=" · ".join(
                    self._translator.t(f"source.{source_id}") for source_id in estimate.source_ids
                ),
            )
        )
        self._apply.setEnabled(True)

    def _accept(self) -> None:
        if self._estimate is None:
            return
        self.accept()

    def estimated_parameters(self) -> AntennaDesignParameters:
        if self._estimate is None:
            raise ValueError("no dimension estimate has been produced")
        return self._estimate.parameters

    def retranslate(self) -> None:
        self.setWindowTitle(self._translator.t("design_from_frequency.title"))
        self._results.setHorizontalHeaderLabels(
            [
                self._translator.t("design_from_frequency.dimension"),
                self._translator.t("design_from_frequency.value"),
            ]
        )
        for label, _widget in self._rows.values():
            label.setText(self._translator.t(label.objectName()))
        self._estimate_button.setText(self._translator.t("design_from_frequency.estimate"))
        self._apply.setText(self._translator.t("design_from_frequency.apply"))
        self._hint.setText(self._translator.t("design_from_frequency.hint"))
