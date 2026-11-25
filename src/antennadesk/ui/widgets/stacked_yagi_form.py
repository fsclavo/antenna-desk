# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for two to four identical Yagis on a vertical stack."""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.polarization import Polarization
from ...domain.antennas.stacked_yagi import (
    StackedYagiFeed,
    StackedYagiFeedMode,
    StackedYagiParameters,
    stacked_yagi_parameters,
)
from ...domain.antennas.yagi import nbs_five_element
from ..help import apply_help
from ..i18n import Translator
from ..units import (
    DisplayUnits,
    LengthPolicy,
    UnitSystem,
    length_bounds,
    length_from_m,
    length_unit_key,
)
from .form_i18n import FormLabels
from .form_units import LengthField, LengthFieldSpec
from .starting_dimensions import StartingDimensionsState
from .yagi_form import YagiForm


class StackedYagiForm(QWidget):
    """A Yagi editor plus the stack count, spacing, and ideal feed progression."""

    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: StackedYagiParameters | None = None,
        parent: QWidget | None = None,
        *,
        display_units: DisplayUnits | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self, family="stacked_yagi")
        self._unit_system = unit_system
        self._display_units = display_units or DisplayUnits(
            unit_system,
            LengthPolicy.AUTO,
        )
        self._updating = False
        minimum_length, maximum_length = length_bounds(unit_system)

        self._yagi = YagiForm(
            translator,
            unit_system,
            None if parameters is None else parameters.yagi,
            self,
            display_units=self._display_units,
            include_support_structures=True,
            include_feed_hardware=False,
        )

        # The embedded Yagi form owns the shared material and radius controls;
        # expose them for the common form-level tests and preview code.
        self._material = self._yagi._material
        self._radius = self._yagi._radius

        self._level_count = QSpinBox(self)
        self._level_count.setRange(2, 4)
        self._spacing = QDoubleSpinBox(self)
        self._spacing.setRange(minimum_length, maximum_length)
        self._spacing.setDecimals(3)
        self._spacing.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._spacing_field = LengthField(
            self._spacing,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._max_top_height = QDoubleSpinBox(self)
        self._max_top_height.setRange(0.0, maximum_length)
        self._max_top_height.setDecimals(3)
        self._max_top_height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._max_top_height_field = LengthField(
            self._max_top_height,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._phase_step = QDoubleSpinBox(self)
        self._phase_step.setRange(-360.0, 360.0)
        self._phase_step.setDecimals(1)
        self._phase_step.setSuffix("°")
        self._amplitude_ratio = QDoubleSpinBox(self)
        self._amplitude_ratio.setRange(0.05, 2.0)
        self._amplitude_ratio.setDecimals(2)
        self._amplitude_ratio.setSingleStep(0.05)

        self._feed_mode = QComboBox(self)
        self._feed_mode.addItem(
            translator.t("stacked_yagi.feed_mode.ideal"),
            StackedYagiFeedMode.IDEAL.value,
        )
        self._feed_mode.addItem(
            translator.t("stacked_yagi.feed_mode.phase_lines"),
            StackedYagiFeedMode.PHASE_LINES.value,
        )
        self._feed_mode.addItem(
            translator.t("stacked_yagi.feed_mode.network"),
            StackedYagiFeedMode.NETWORK.value,
        )
        self._reference_line = QDoubleSpinBox(self)
        self._reference_line.setRange(0.0, maximum_length)
        self._reference_line.setDecimals(3)
        self._reference_line.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._reference_line_field = LengthField(
            self._reference_line,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._line_increment = QDoubleSpinBox(self)
        self._line_increment.setRange(0.0, maximum_length)
        self._line_increment.setDecimals(3)
        self._line_increment.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._line_increment_field = LengthField(
            self._line_increment,
            LengthFieldSpec(0.0, 10_000.0, scale_hint="m"),
            translator,
            self._display_units,
        )
        self._velocity_factor = QDoubleSpinBox(self)
        self._velocity_factor.setRange(0.5, 1.0)
        self._velocity_factor.setDecimals(3)
        self._velocity_factor.setSingleStep(0.01)
        self._velocity_factor.setValue(1.0)
        self._line_z0 = QDoubleSpinBox(self)
        self._line_z0.setRange(10.0, 600.0)
        self._line_z0.setDecimals(1)
        self._line_z0.setSuffix(" Ω")
        self._line_z0.setValue(50.0)
        self._splitter_loss = QDoubleSpinBox(self)
        self._splitter_loss.setRange(0.0, 20.0)
        self._splitter_loss.setDecimals(2)
        self._splitter_loss.setSingleStep(0.05)
        self._splitter_loss.setSuffix(" dB")
        self._line_loss = QDoubleSpinBox(self)
        self._line_loss.setRange(0.0, 100.0)
        self._line_loss.setDecimals(2)
        self._line_loss.setSingleStep(0.1)
        self._line_loss.setSuffix(" dB/100 m")

        self._starting = QPushButton(
            translator.t("action.load_starting_dimensions"),
            self,
        )
        self._starting.clicked.connect(self.load_starting_dimensions)
        apply_help(self._starting, translator, "load_starting", family="stacked_yagi")
        self._starting_note = QLabel(self)
        self._starting_note.setWordWrap(True)
        self._starting_note.setStyleSheet("font-style: italic;")
        self._starting_note.setVisible(False)
        self._starting_state = StartingDimensionsState(translator, self._starting_note)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)
        self._overlap_warning = QLabel(self)
        self._overlap_warning.setWordWrap(True)
        self._overlap_warning.setStyleSheet("color: #9a6700;")
        self._overlap_warning.setVisible(False)
        self._envelope_warning = QLabel(self)
        self._envelope_warning.setWordWrap(True)
        self._envelope_warning.setStyleSheet("color: #9a6700;")
        self._envelope_warning.setVisible(False)
        self._phase_note = QLabel(self)
        self._phase_note.setWordWrap(True)
        self._phase_note.setVisible(False)
        self._network_note = QLabel(self)
        self._network_note.setWordWrap(True)
        self._network_note.setStyleSheet("font-style: italic;")
        self._network_note.setVisible(False)

        form = QFormLayout()
        form.addRow(self._labels.label("stacked_yagi.level_count"), self._level_count)
        form.addRow(self._labels.label("stacked_yagi.spacing"), self._spacing)
        form.addRow(
            self._labels.label("stacked_yagi.max_top_height"),
            self._max_top_height,
        )
        form.addRow(self._labels.label("stacked_yagi.phase_step"), self._phase_step)
        form.addRow(
            self._labels.label("stacked_yagi.amplitude_ratio"),
            self._amplitude_ratio,
        )
        form.addRow(self._labels.label("stacked_yagi.feed_mode"), self._feed_mode)
        form.addRow(
            self._labels.label("stacked_yagi.reference_line"),
            self._reference_line,
        )
        form.addRow(
            self._labels.label("stacked_yagi.line_increment"),
            self._line_increment,
        )
        form.addRow(
            self._labels.label("stacked_yagi.velocity_factor"),
            self._velocity_factor,
        )
        form.addRow(self._labels.label("stacked_yagi.line_z0"), self._line_z0)
        form.addRow(
            self._labels.label("stacked_yagi.splitter_loss"),
            self._splitter_loss,
        )
        form.addRow(self._labels.label("stacked_yagi.line_loss"), self._line_loss)
        form.addRow(self._starting)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._labels.bind_form(form)
        layout.addWidget(self._yagi, 1)
        layout.addLayout(form)
        layout.addWidget(self._geometry)
        layout.addWidget(self._overlap_warning)
        layout.addWidget(self._envelope_warning)
        layout.addWidget(self._phase_note)
        layout.addWidget(self._network_note)
        layout.addWidget(self._starting_note)

        for widget in (self._phase_step, self._amplitude_ratio):
            widget.valueChanged.connect(self._managed_field_changed)
        self._max_top_height.valueChanged.connect(self._emit_changed)
        for widget in (
            self._reference_line,
            self._line_increment,
            self._velocity_factor,
            self._line_z0,
            self._splitter_loss,
            self._line_loss,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._feed_mode.currentIndexChanged.connect(self._feed_mode_changed)
        self._level_count.valueChanged.connect(self._managed_field_changed)
        self._spacing.valueChanged.connect(self._managed_field_changed)
        self._yagi.changed.connect(self._on_yagi_changed)

        if parameters is None:
            base = self._yagi.parameters()
            initial = stacked_yagi_parameters(
                frequency_hz=base.frequency_hz,
                height_m=base.height_m,
                azimuth_deg=base.azimuth_deg,
                polarization=base.polarization,
                material=base.material,
                ground=base.ground,
                radius_m=base.elements[0].radius_m,
            )
        else:
            initial = parameters
        self.set_parameters(initial)
        if parameters is None:
            self.mark_starting_dimensions_pristine()
        self._update_feed_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._labels.retranslate()
        self._yagi.retranslate()
        self._feed_mode.setItemText(0, self._translator.t("stacked_yagi.feed_mode.ideal"))
        self._feed_mode.setItemText(
            1,
            self._translator.t("stacked_yagi.feed_mode.phase_lines"),
        )
        self._feed_mode.setItemText(
            2,
            self._translator.t("stacked_yagi.feed_mode.network"),
        )
        self._starting.setText(self._translator.t("action.load_starting_dimensions"))
        apply_help(
            self._starting,
            self._translator,
            "load_starting",
            family="stacked_yagi",
        )
        self._starting_state.retranslate()
        self._update_geometry()

    def _emit_changed(self) -> None:
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _managed_field_changed(self, *_args: object) -> None:
        if self._updating:
            return
        self._starting_state.mark_non_pristine()
        self._emit_changed()

    def _on_yagi_changed(self) -> None:
        self._emit_changed()

    def _feed_mode_changed(self, *_args: object) -> None:
        if self._updating:
            return
        self._update_feed_controls()
        self._update_geometry()
        self.changed.emit()

    def _update_feed_controls(self) -> None:
        phase_lines = self._feed_mode.currentData() in {
            StackedYagiFeedMode.PHASE_LINES.value,
            StackedYagiFeedMode.NETWORK.value,
        }
        for widget in (
            self._reference_line,
            self._line_increment,
            self._velocity_factor,
            self._line_z0,
            self._splitter_loss,
        ):
            widget.setEnabled(phase_lines)
        self._line_loss.setEnabled(
            self._feed_mode.currentData() == StackedYagiFeedMode.NETWORK.value
        )
        self._phase_step.setEnabled(not phase_lines)

    def mark_starting_dimensions_pristine(self) -> None:
        self._yagi.mark_starting_dimensions_pristine()
        self._starting_state.mark_pristine()

    def load_starting_dimensions(self) -> None:
        current = self._yagi.parameters()
        try:
            yagi = nbs_five_element(
                frequency_hz=current.frequency_hz,
                height_m=current.height_m,
                azimuth_deg=current.azimuth_deg,
                polarization=current.polarization,
                material=current.material,
                ground=current.ground,
                radius_m=current.elements[0].radius_m,
            )
            yagi = replace(
                yagi,
                mast_diameter_m=current.mast_diameter_m,
                mast_offset_m=current.mast_offset_m,
                guy_count=current.guy_count,
                guy_anchor_radius_m=current.guy_anchor_radius_m,
                guy_diameter_m=current.guy_diameter_m,
            )
        except ValueError as exc:
            self._starting_note.setText(str(exc))
            self._starting_note.setVisible(True)
            self._starting_state.mark_non_pristine()
            return
        wavelength = 299_792_458.0 / current.frequency_hz
        span = max(element.length_m for element in yagi.elements)
        spacing = 0.5 * wavelength
        if yagi.polarization is Polarization.VERTICAL:
            spacing = span + 0.1 * wavelength
        self._yagi.set_parameters(yagi)
        self._updating = True
        try:
            self._spacing_field.configure(spacing)
        finally:
            self._updating = False
        self._yagi.mark_starting_dimensions_pristine()
        self._starting_state.mark_pristine(frequency_mhz=current.frequency_hz / 1_000_000.0)
        self._update_geometry()
        self.changed.emit()

    def set_unit_system(self, unit_system: UnitSystem) -> None:
        if unit_system is self._unit_system:
            return
        was_pristine = self._starting_state.pristine
        self._unit_system = unit_system
        self._display_units = DisplayUnits(
            unit_system,
            self._display_units.length_policy,
        )
        self._spacing_field.set_display_units(self._display_units)
        self._max_top_height_field.set_display_units(self._display_units)
        self._reference_line_field.set_display_units(self._display_units)
        self._line_increment_field.set_display_units(self._display_units)
        self._yagi.set_unit_system(unit_system)
        if was_pristine:
            self.mark_starting_dimensions_pristine()

    def set_parameters(self, parameters: StackedYagiParameters) -> None:
        self._updating = True
        try:
            self._yagi.set_parameters(parameters.yagi)
            self._level_count.setValue(parameters.count)
            self._spacing_field.configure(parameters.spacing_m)
            self._max_top_height_field.configure(parameters.max_top_height_m)
            self._phase_step.setValue(parameters.phase_step_deg)
            self._amplitude_ratio.setValue(parameters.amplitude_ratio)
            mode_index = self._feed_mode.findData(parameters.feed.mode.value)
            if mode_index >= 0:
                self._feed_mode.setCurrentIndex(mode_index)
            self._reference_line_field.configure(parameters.feed.reference_length_m)
            self._line_increment_field.configure(parameters.feed.line_increment_m)
            self._velocity_factor.setValue(parameters.feed.velocity_factor)
            self._line_z0.setValue(parameters.feed.characteristic_impedance_ohm)
            self._splitter_loss.setValue(parameters.feed.splitter_loss_db)
            self._line_loss.setValue(parameters.feed.line_loss_db_per_100m)
            self._update_feed_controls()
        finally:
            self._updating = False
        self._starting_state.mark_non_pristine()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._yagi.set_frequency_hz(frequency_hz)

    def _update_geometry(self) -> None:
        try:
            yagi = self._yagi.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            self._overlap_warning.setVisible(False)
            return
        count = self._level_count.value()
        spacing_m = self._spacing_field.value_m()
        top_height_m = yagi.height_m + (count - 1) * spacing_m
        span = max(element.length_m for element in yagi.elements)
        top_tip_m = top_height_m + (
            span / 2.0 if yagi.polarization is Polarization.VERTICAL else 0.0
        )
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "stacked_yagi.geometry",
                count=count,
                spacing=f"{length_from_m(spacing_m, self._unit_system):.3f}",
                top=f"{length_from_m(top_tip_m, self._unit_system):.3f}",
                phase=f"{self._phase_step.value():.1f}",
                unit=unit,
            )
        )
        overlap = yagi.polarization is Polarization.VERTICAL and spacing_m <= span
        self._overlap_warning.setText(
            self._translator.t("stacked_yagi.overlap_warning") if overlap else ""
        )
        self._overlap_warning.setVisible(overlap)
        top_tip_m = top_height_m + (
            span / 2.0 if yagi.polarization is Polarization.VERTICAL else 0.0
        )
        maximum_top_m = self._max_top_height_field.value_m()
        beyond_envelope = maximum_top_m > 0.0 and top_tip_m > maximum_top_m + 1e-6
        self._envelope_warning.setText(
            self._translator.t("stacked_yagi.envelope_warning") if beyond_envelope else ""
        )
        self._envelope_warning.setVisible(beyond_envelope)
        network = self._feed_mode.currentData() == StackedYagiFeedMode.NETWORK.value
        phase_lines = self._feed_mode.currentData() in {
            StackedYagiFeedMode.PHASE_LINES.value,
            StackedYagiFeedMode.NETWORK.value,
        }
        if phase_lines:
            wavelength = 299_792_458.0 / yagi.frequency_hz
            derived = (
                -360.0
                * self._line_increment_field.value_m()
                / (self._velocity_factor.value() * wavelength)
            )
            self._phase_note.setText(
                self._translator.t("stacked_yagi.derived_phase", phase=f"{derived:.1f}")
            )
            self._phase_note.setVisible(True)
        else:
            self._phase_note.clear()
            self._phase_note.setVisible(False)
        self._network_note.setText(
            self._translator.t("stacked_yagi.network_note") if network else ""
        )
        self._network_note.setVisible(network)

    def parameters(self) -> StackedYagiParameters:
        return StackedYagiParameters(
            yagi=self._yagi.parameters(),
            count=self._level_count.value(),
            spacing_m=self._spacing_field.value_m(),
            phase_step_deg=self._phase_step.value(),
            amplitude_ratio=self._amplitude_ratio.value(),
            max_top_height_m=self._max_top_height_field.value_m(),
            feed=StackedYagiFeed(
                mode=StackedYagiFeedMode(self._feed_mode.currentData()),
                reference_length_m=self._reference_line_field.value_m(),
                line_increment_m=self._line_increment_field.value_m(),
                velocity_factor=self._velocity_factor.value(),
                characteristic_impedance_ohm=self._line_z0.value(),
                splitter_loss_db=self._splitter_loss.value(),
                line_loss_db_per_100m=self._line_loss.value(),
            ),
        )
