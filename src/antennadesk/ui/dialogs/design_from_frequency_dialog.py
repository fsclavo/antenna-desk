# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency-first dimension estimation for the current template."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
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
from ...domain.antennas.design import AntennaDesignParameters, antenna_type_for
from ...domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ...domain.antennas.endfed import EndFedParameters
from ...domain.antennas.fan_dipole import FanDipoleParameters
from ...domain.antennas.folded_dipole import FoldedDipoleParameters
from ...domain.antennas.inverted_v import InvertedVParameters
from ...domain.antennas.j_pole import JPoleParameters
from ...domain.antennas.loop import LoopParameters
from ...domain.antennas.materials import COPPER
from ...domain.antennas.moxon import MoxonParameters
from ...domain.antennas.ocfd import OCFDParameters
from ...domain.antennas.polarization import Polarization
from ...domain.antennas.t2fd import T2FDParameters
from ...domain.antennas.vertical import VerticalParameters
from ...domain.antennas.yagi import YagiParameters
from ...domain.design import (
    DesignIntent,
    DimensionEstimate,
    DimensionUnit,
    LoopShape,
    UnsupportedEstimateError,
    VerticalForm,
)
from ...domain.design.estimators import estimator_type_for
from ...domain.design.formulas import (
    five_eighth_wave_length_m,
    frequency_for_half_wave_length,
    half_wave_length_m,
    quarter_wave_length_m,
)
from ...domain.environment.ground import FREE_SPACE, GroundModel
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..template_identity import label_key_for
from ..units import (
    UnitSystem,
    length_bounds,
    length_from_m,
    length_to_m,
    length_unit_key,
)


def _vertical_form_for(height_m: float, frequency_hz: float) -> VerticalForm:
    choices = (
        (VerticalForm.QUARTER_WAVE, quarter_wave_length_m(frequency_hz)),
        (VerticalForm.HALF_WAVE, half_wave_length_m(frequency_hz)),
        (VerticalForm.FIVE_EIGHTH_WAVE, five_eighth_wave_length_m(frequency_hz)),
    )
    return min(choices, key=lambda item: abs(item[1] - height_m))[0]


class DesignFromFrequencyDialog(QDialog):
    """Estimate dimensions for the template already loaded in the editor."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        *,
        initial_parameters: AntennaDesignParameters,
        can_refine: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._estimate_use_case = EstimateAntennaDimensions()
        self._estimate: DimensionEstimate | None = None
        self._estimator_type = estimator_type_for(initial_parameters)
        self._template_label_key = label_key_for(initial_parameters)
        self.setWindowTitle(translator.t("design_from_frequency.title"))
        self.resize(*scaled_dialog_size(760, 680))

        frequency_hz = initial_parameters.frequency_hz
        highest_frequency_hz = frequency_hz * 6.0
        height_m = 10.0
        base_height_m = 0.25
        end_height_m = 10.0
        orientation = DipoleOrientation.HORIZONTAL
        polarization = Polarization.HORIZONTAL
        loop_shape = LoopShape.LOOP
        vertical_form = VerticalForm.QUARTER_WAVE
        folded = False
        included_angle = 120.0
        fan_bands: tuple[float, ...] = ()
        radial_count = 4
        radial_length_m: float | None = None
        feed_offset_m: float | None = None
        gap_m = 0.01
        yagi_elements = 5
        azimuth_deg = 0.0
        wire_radius_m = 0.001
        material = COPPER
        ground: GroundModel = FREE_SPACE

        if isinstance(parameters := initial_parameters, DipoleParameters):
            height_m = parameters.height_m
            orientation = parameters.orientation
        elif isinstance(parameters, FoldedDipoleParameters):
            height_m = parameters.height_m
        elif isinstance(parameters, LoopParameters):
            height_m = parameters.height_m
            loop_shape = {
                3: LoopShape.DELTA,
                4: LoopShape.QUAD,
            }.get(parameters.sides, LoopShape.LOOP)
        elif isinstance(parameters, VerticalParameters):
            base_height_m = parameters.base_height_m
            vertical_form = _vertical_form_for(parameters.height_m, frequency_hz)
            radial_count = parameters.radial_count
            radial_length_m = (
                parameters.radial_length_m if parameters.radial_length_m > 0.0 else None
            )
            azimuth_deg = parameters.radial_angle_deg
        elif isinstance(parameters, InvertedVParameters):
            height_m = parameters.apex_height_m
            included_angle = parameters.included_angle_deg
        elif isinstance(parameters, FanDipoleParameters):
            height_m = parameters.apex_height_m
            if parameters.elements:
                included_angle = parameters.elements[0].included_angle_deg
            fan_bands = tuple(
                frequency_for_half_wave_length(element.length_m) for element in parameters.elements
            )
        elif isinstance(parameters, EndFedParameters):
            height_m = parameters.feed_height_m
            end_height_m = parameters.end_height_m
        elif isinstance(parameters, OCFDParameters):
            height_m = parameters.height_m
        elif isinstance(parameters, T2FDParameters):
            height_m = parameters.height_m
            highest_frequency_hz = parameters.highest_frequency_hz
            orientation = parameters.orientation
        elif isinstance(parameters, JPoleParameters):
            base_height_m = parameters.base_height_m
            folded = parameters.folded
            feed_offset_m = parameters.feed_offset_m
            gap_m = parameters.gap_m
        elif isinstance(parameters, (YagiParameters, MoxonParameters)):
            height_m = parameters.height_m
            polarization = parameters.polarization
            if isinstance(parameters, YagiParameters):
                yagi_elements = len(parameters.elements)
        if hasattr(initial_parameters, "azimuth_deg"):
            azimuth_deg = initial_parameters.azimuth_deg
        if hasattr(initial_parameters, "wire_radius_m"):
            wire_radius_m = initial_parameters.wire_radius_m
        if isinstance(initial_parameters, YagiParameters) and initial_parameters.elements:
            wire_radius_m = initial_parameters.elements[0].radius_m
        if hasattr(initial_parameters, "material"):
            material = initial_parameters.material
        if hasattr(initial_parameters, "ground"):
            ground = initial_parameters.ground

        self._azimuth_deg = azimuth_deg
        self._wire_radius_m = wire_radius_m
        self._material = material
        self._ground = ground
        self._radial_length_m = radial_length_m
        self._feed_offset_m = feed_offset_m
        self._gap_m = gap_m

        self._template_value = QLabel(self)
        self._template_value.setStyleSheet("font-weight: bold;")
        self._template_value.setText(translator.t(self._template_label_key))

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(frequency_hz / 1_000_000.0)

        self._highest_frequency = QDoubleSpinBox(self)
        self._highest_frequency.setRange(0.1, 100_000.0)
        self._highest_frequency.setDecimals(6)
        self._highest_frequency.setSuffix(" MHz")
        self._highest_frequency.setValue(highest_frequency_hz / 1_000_000.0)

        length_min, length_max = length_bounds(unit_system)
        unit = translator.t(length_unit_key(unit_system))
        self._height = QDoubleSpinBox(self)
        self._height.setRange(length_min, length_max)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {unit}")
        self._height.setValue(length_from_m(height_m, unit_system))

        self._base_height = QDoubleSpinBox(self)
        self._base_height.setRange(0.0, length_max)
        self._base_height.setDecimals(3)
        self._base_height.setSuffix(f" {unit}")
        self._base_height.setValue(length_from_m(base_height_m, unit_system))

        self._end_height = QDoubleSpinBox(self)
        self._end_height.setRange(0.0, length_max)
        self._end_height.setDecimals(3)
        self._end_height.setSuffix(f" {unit}")
        self._end_height.setValue(length_from_m(end_height_m, unit_system))

        self._orientation = QComboBox(self)
        self._orientation.addItem("", DipoleOrientation.HORIZONTAL.value)
        self._orientation.addItem("", DipoleOrientation.VERTICAL.value)
        orientation_index = self._orientation.findData(orientation.value)
        self._orientation.setCurrentIndex(max(orientation_index, 0))

        self._polarization = QComboBox(self)
        self._polarization.addItem("", Polarization.HORIZONTAL.value)
        self._polarization.addItem("", Polarization.VERTICAL.value)
        polarization_index = self._polarization.findData(polarization.value)
        self._polarization.setCurrentIndex(max(polarization_index, 0))

        self._loop_shape = QComboBox(self)
        self._loop_shape.addItem("", LoopShape.LOOP.value)
        self._loop_shape.addItem("", LoopShape.QUAD.value)
        self._loop_shape.addItem("", LoopShape.DELTA.value)
        loop_index = self._loop_shape.findData(loop_shape.value)
        self._loop_shape.setCurrentIndex(max(loop_index, 0))
        self._loop_shape.setEnabled(False)

        self._vertical_form = QComboBox(self)
        self._vertical_form.addItem("", VerticalForm.QUARTER_WAVE.value)
        self._vertical_form.addItem("", VerticalForm.HALF_WAVE.value)
        self._vertical_form.addItem("", VerticalForm.FIVE_EIGHTH_WAVE.value)
        vertical_index = self._vertical_form.findData(vertical_form.value)
        self._vertical_form.setCurrentIndex(max(vertical_index, 0))

        self._j_pole_variant = QComboBox(self)
        self._j_pole_variant.addItem("", False)
        self._j_pole_variant.addItem("", True)
        j_pole_index = self._j_pole_variant.findData(folded)
        self._j_pole_variant.setCurrentIndex(max(j_pole_index, 0))
        self._j_pole_variant.setEnabled(False)

        self._included_angle = QDoubleSpinBox(self)
        self._included_angle.setRange(1.0, 179.0)
        self._included_angle.setDecimals(1)
        self._included_angle.setSuffix("°")
        self._included_angle.setValue(included_angle)

        self._fan_bands = QLineEdit(self)
        self._fan_bands.setPlaceholderText("7.1, 14.1, 21.0")
        self._fan_bands.setText(
            ", ".join(f"{band_hz / 1_000_000.0:.3f}" for band_hz in fan_bands)
            or f"{frequency_hz / 1_000_000.0:.3f}"
        )

        self._radial_count = QSpinBox(self)
        self._radial_count.setRange(0, 128)
        self._radial_count.setValue(radial_count)

        self._yagi_elements = QSpinBox(self)
        self._yagi_elements.setRange(2, 32)
        self._yagi_elements.setValue(yagi_elements)

        self._form = QFormLayout()
        self._rows: dict[str, tuple[QLabel, QWidget]] = {}
        self._add_row("template", "field.template", self._template_value)
        self._add_row("frequency", "field.frequency", self._frequency)
        self._add_row(
            "highest_frequency",
            "t2fd.highest_frequency",
            self._highest_frequency,
        )
        self._add_row("height", "field.height", self._height)
        self._add_row("base_height", "field.base_height", self._base_height)
        self._add_row("end_height", "geometry.end_height", self._end_height)
        self._add_row("orientation", "field.orientation", self._orientation)
        self._add_row("polarization", "field.polarization", self._polarization)
        self._add_row("loop_shape", "design_from_frequency.loop_shape", self._loop_shape)
        self._add_row("vertical_form", "design_from_frequency.vertical_form", self._vertical_form)
        self._add_row("j_pole_variant", "field.template", self._j_pole_variant)
        self._add_row("included_angle", "inverted_v.included_angle", self._included_angle)
        self._add_row("fan_bands", "design_from_frequency.fan_bands", self._fan_bands)
        self._add_row("radial_count", "vertical.radial_count", self._radial_count)
        self._add_row("yagi_elements", "geometry.elements", self._yagi_elements)

        self._template_hint = QLabel(self)
        self._template_hint.setWordWrap(True)
        self._template_hint.setStyleSheet("font-style: italic;")

        self._estimate_button = QPushButton(self)
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
        self._hint = QLabel(self)
        self._hint.setWordWrap(True)

        self._refine = QCheckBox(self)
        self._refine.setVisible(can_refine)
        self._apply = QPushButton(self)
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
        layout.addWidget(self._template_hint)
        layout.addWidget(self._results, 1)
        layout.addWidget(self._assumptions)
        layout.addWidget(self._warnings)
        layout.addWidget(self._sources)
        layout.addWidget(self._hint)
        layout.addWidget(self._refine)
        layout.addLayout(buttons)

        for signal in (
            self._frequency.valueChanged,
            self._highest_frequency.valueChanged,
            self._height.valueChanged,
            self._base_height.valueChanged,
            self._end_height.valueChanged,
            self._orientation.currentIndexChanged,
            self._polarization.currentIndexChanged,
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
        family = self._estimator_type
        visible = {"template", "frequency"}
        if family in {
            "wire_dipole",
            "folded_dipole",
            "loop",
            "ocfd",
            "yagi",
            "moxon",
        }:
            visible.add("height")
        if family == "wire_dipole":
            visible.add("orientation")
        if family == "loop":
            visible.add("loop_shape")
        if family in {"vertical", "j_pole"}:
            visible.add("base_height")
        if family == "vertical":
            visible.update({"vertical_form", "radial_count"})
        if family == "j_pole":
            visible.add("j_pole_variant")
        if family in {"inverted_v", "fan_dipole"}:
            visible.add("included_angle")
        if family == "fan_dipole":
            visible.add("fan_bands")
        if family == "endfed":
            visible.update({"height", "end_height"})
        if family == "t2fd":
            visible.update({"highest_frequency", "height", "orientation"})
        if family in {"yagi", "moxon"}:
            visible.add("polarization")
        if family == "yagi":
            visible.add("yagi_elements")
        height_label, _height_widget = self._rows["height"]
        height_label.setObjectName("endfed.feed_height" if family == "endfed" else "field.height")
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
        family = self._estimator_type
        fan_bands: tuple[float, ...] = ()
        if family == "fan_dipole":
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
            polarization=Polarization(str(self._polarization.currentData())),
            azimuth_deg=self._azimuth_deg,
            wire_radius_m=self._wire_radius_m,
            material=self._material,
            ground=self._ground,
            loop_shape=LoopShape(str(self._loop_shape.currentData())),
            vertical_form=VerticalForm(str(self._vertical_form.currentData())),
            folded=bool(self._j_pole_variant.currentData()),
            included_angle_deg=self._included_angle.value(),
            radial_count=self._radial_count.value(),
            radial_length_m=self._radial_length_m,
            feed_offset_m=self._feed_offset_m,
            gap_m=self._gap_m,
            fan_bands_hz=fan_bands,
            yagi_elements=self._yagi_elements.value(),
            highest_frequency_hz=(
                self._highest_frequency.value() * 1_000_000.0 if family == "t2fd" else None
            ),
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
        if antenna_type_for(self._estimate.parameters) != self._estimator_type:
            QMessageBox.warning(
                self,
                self._translator.t("design_from_frequency.title"),
                self._translator.t("error.estimate_changes_template"),
            )
            return
        self.accept()

    def estimated_estimate(self) -> DimensionEstimate:
        if self._estimate is None:
            raise ValueError("no dimension estimate has been produced")
        return self._estimate

    def estimated_parameters(self) -> AntennaDesignParameters:
        return self.estimated_estimate().parameters

    def refine_requested(self) -> bool:
        return self._refine.isChecked()

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
        self._template_value.setText(self._translator.t(self._template_label_key))
        self._orientation.setItemText(0, self._translator.t("orientation.horizontal"))
        self._orientation.setItemText(1, self._translator.t("orientation.vertical"))
        self._polarization.setItemText(0, self._translator.t("orientation.horizontal"))
        self._polarization.setItemText(1, self._translator.t("orientation.vertical"))
        self._loop_shape.setItemText(0, self._translator.t("antenna_type.loop"))
        self._loop_shape.setItemText(1, self._translator.t("catalog.quad_loop"))
        self._loop_shape.setItemText(2, self._translator.t("catalog.delta_loop"))
        self._vertical_form.setItemText(0, "1/4 λ")
        self._vertical_form.setItemText(1, "1/2 λ")
        self._vertical_form.setItemText(2, "5/8 λ")
        self._j_pole_variant.setItemText(0, self._translator.t("catalog.j_pole"))
        self._j_pole_variant.setItemText(1, self._translator.t("catalog.slim_jim"))
        locked_hint = self._translator.t("design_from_frequency.template_locked")
        self._loop_shape.setToolTip(locked_hint)
        self._j_pole_variant.setToolTip(locked_hint)
        self._template_hint.setText(
            self._translator.t("design_from_frequency.current_template_hint")
        )
        self._estimate_button.setText(self._translator.t("design_from_frequency.estimate"))
        self._apply.setText(self._translator.t("design_from_frequency.apply"))
        self._refine.setText(self._translator.t("design_from_frequency.refine_after_apply"))
        self._hint.setText(self._translator.t("design_from_frequency.hint"))
