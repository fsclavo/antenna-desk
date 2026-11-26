# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Inline editor for a Moxon rectangle."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.materials import COPPER, ConductorMaterial
from ...domain.antennas.moxon import (
    MOXON_GROSS_WIDTH_MAX_WAVELENGTH_RATIO,
    MOXON_GROSS_WIDTH_MIN_WAVELENGTH_RATIO,
    MoxonParameters,
    moxon_20m_wire,
    moxon_frequency_mismatch,
    validate_moxon_geometry,
)
from ...domain.antennas.polarization import Polarization
from ...domain.common import units
from ...domain.environment.ground import GroundKind, GroundModel
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
from .sectioned_form import FormColumn, FormLayoutMode, FormRow, FormSection, SectionedForm
from .starting_dimensions import StartingDimensionsState

# The editor starts on the 10 m band.  The geometry is the published Cebik
# 20 m wire reference scaled to this frequency; it is a heuristic starting
# point, not a second independent reference.
MOXON_DEFAULT_FREQUENCY_HZ = 28_500_000.0
MOXON_DEFAULT_HEIGHT_M = 10.0


class MoxonForm(QWidget):
    changed = Signal()

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parameters: MoxonParameters | None = None,
        parent: QWidget | None = None,
        *,
        display_units: DisplayUnits | None = None,
        wide_layout: bool = False,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._labels = FormLabels(translator, self, family="moxon")
        self._wide_layout = wide_layout
        self._unit_system = unit_system
        self._display_units = display_units or DisplayUnits(
            unit_system,
            LengthPolicy.FIXED,
        )
        self._updating = False

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(MOXON_DEFAULT_FREQUENCY_HZ / 1_000_000.0)

        default_geometry = moxon_20m_wire(
            frequency_hz=MOXON_DEFAULT_FREQUENCY_HZ,
            height_m=MOXON_DEFAULT_HEIGHT_M,
        )

        self._width = QDoubleSpinBox(self)
        self._width.setDecimals(3)
        self._width.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._width.setValue(length_from_m(default_geometry.width_m, unit_system))

        self._depth = QDoubleSpinBox(self)
        self._depth.setDecimals(3)
        self._depth.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._depth.setValue(length_from_m(default_geometry.depth_m, unit_system))

        self._reflector_tip = QDoubleSpinBox(self)
        self._reflector_tip.setDecimals(3)
        self._reflector_tip.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._reflector_tip.setValue(length_from_m(default_geometry.reflector_tip_m, unit_system))

        self._driven_tip = QDoubleSpinBox(self)
        self._driven_tip.setDecimals(3)
        self._driven_tip.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._driven_tip.setValue(length_from_m(default_geometry.driven_tip_m, unit_system))

        self._height = QDoubleSpinBox(self)
        self._height.setRange(*height_bounds(unit_system))
        self._height.setDecimals(3)
        self._height.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._height.setValue(length_from_m(MOXON_DEFAULT_HEIGHT_M, unit_system))

        self._width_field = LengthField(
            self._width,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._depth_field = LengthField(
            self._depth,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._reflector_tip_field = LengthField(
            self._reflector_tip,
            LengthFieldSpec(0.0001, 10_000.0, scale_hint="mm"),
            translator,
            self._display_units,
        )
        self._driven_tip_field = LengthField(
            self._driven_tip,
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
        # The initial spin-box values were set in the construction unit. Apply
        # the display-unit policy now so an AUTO field does not reinterpret
        # metres as millimetres.
        self._width_field.configure(default_geometry.width_m)
        self._depth_field.configure(default_geometry.depth_m)
        self._reflector_tip_field.configure(default_geometry.reflector_tip_m)
        self._driven_tip_field.configure(default_geometry.driven_tip_m)
        self._height_field.configure(MOXON_DEFAULT_HEIGHT_M)

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._polarization = QComboBox(self)
        self._polarization.addItem("", Polarization.HORIZONTAL.value)
        self._polarization.addItem("", Polarization.VERTICAL.value)
        self._polarization.setItemText(0, translator.t("orientation.horizontal"))
        self._polarization.setItemText(1, translator.t("orientation.vertical"))
        self._polarization.setToolTip(translator.t("moxon.polarization_hint"))

        self._radius = QDoubleSpinBox(self)
        apply_radius_units(translator, unit_system, self._radius)
        self._radius.setValue(radius_from_m(0.001, unit_system))

        self._material = QComboBox(self)
        populate_template_material_combo(self._material, translator, "moxon")

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

        self._reference = QPushButton(translator.t("moxon.reference_preset"), self)
        self._reference.clicked.connect(self._load_reference_preset)

        self._geometry = QLabel(self)
        self._geometry.setWordWrap(True)

        self._clearance_warning = QLabel(self)
        self._clearance_warning.setWordWrap(True)
        self._clearance_warning.setVisible(False)

        self._frequency_warning = QLabel(self)
        self._frequency_warning.setWordWrap(True)
        self._frequency_warning.setVisible(False)

        self._starting_note = QLabel(self)
        self._starting_note.setWordWrap(True)
        self._starting_note.setVisible(False)
        self._starting_state = StartingDimensionsState(translator, self._starting_note)

        left_rows = [
            FormRow("field.frequency", self._frequency),
            FormRow("moxon.width", self._width),
            FormRow("moxon.depth", self._depth),
            FormRow("moxon.reflector_tip", self._reflector_tip),
            FormRow("moxon.driven_tip", self._driven_tip),
            FormRow("field.height", self._height),
        ]
        right_rows = [
            FormRow("field.azimuth", self._azimuth),
            FormRow("field.polarization", self._polarization),
            FormRow("moxon.wire_radius", self._radius),
            FormRow("field.material", self._material),
            FormRow("field.ground", self._ground),
            FormRow("field.soil_preset", self._soil),
            FormRow("field.permittivity", self._permittivity),
            FormRow("field.conductivity", self._conductivity),
        ]
        self._sectioned = SectionedForm(
            (
                FormSection(tuple(left_rows), column=FormColumn.LEFT),
                FormSection(tuple(right_rows), column=FormColumn.RIGHT),
            ),
            mode=FormLayoutMode.TWO_COLUMN if wide_layout else FormLayoutMode.SINGLE,
            label_factory=self._labels.label,
            target_width_px=920 if wide_layout else None,
            parent=self,
        )
        for form in self._sectioned.forms:
            self._labels.bind_form(form)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._sectioned)
        layout.addWidget(self._reference)
        layout.addWidget(self._starting_note)
        layout.addWidget(self._geometry)
        layout.addWidget(self._clearance_warning)
        layout.addWidget(self._frequency_warning)
        layout.addStretch(1)
        self._sectioned.apply_tab_order(self._reference)

        self._frequency.valueChanged.connect(self._frequency_changed)
        for widget in (
            self._width,
            self._depth,
            self._reflector_tip,
            self._driven_tip,
        ):
            widget.valueChanged.connect(self._managed_field_changed)
        for widget in (
            self._height,
            self._azimuth,
            self._radius,
            self._permittivity,
            self._conductivity,
        ):
            widget.valueChanged.connect(self._emit_changed)
        self._polarization.currentIndexChanged.connect(self._emit_changed)
        self._material.currentIndexChanged.connect(self._emit_changed)
        self._ground.currentIndexChanged.connect(self._ground_changed)
        if parameters is not None:
            self.set_parameters(parameters)
        else:
            self.mark_starting_dimensions_pristine()
        self._update_ground_controls()
        self._update_geometry()

    def retranslate(self) -> None:
        self._ground_presets.retranslate()
        self._labels.retranslate()
        self._polarization.setItemText(
            0,
            self._translator.t("orientation.horizontal"),
        )
        self._polarization.setItemText(
            1,
            self._translator.t("orientation.vertical"),
        )
        self._polarization.setToolTip(self._translator.t("moxon.polarization_hint"))
        self._reference.setText(self._translator.t("moxon.reference_preset"))
        self._starting_state.retranslate()
        retranslate_material_combo(self._material, self._translator)
        retranslate_combo(
            self._ground,
            self._translator,
            ("ground.free_space", "ground.perfect", "ground.finite"),
        )
        self._update_geometry()

    def _emit_changed(self, *_args: object) -> None:
        if not self._updating:
            self._update_geometry()
            self.changed.emit()

    def _frequency_changed(self, value: float) -> None:
        if self._updating:
            return
        if self._starting_state.pristine:
            self._load_reference_preset()
            return
        self._starting_state.show_stale(value)
        self._emit_changed()

    def _managed_field_changed(self, *_args: object) -> None:
        if self._updating:
            return
        self._starting_state.mark_non_pristine()
        self._emit_changed()

    def mark_starting_dimensions_pristine(self) -> None:
        """Mark the current geometry as generated for its design frequency."""

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

    def _selected_polarization(self) -> Polarization:
        return Polarization(str(self._polarization.currentData()))

    def _update_clearance_warning(self) -> None:
        geometry_issues = validate_moxon_geometry(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            width_m=self._width_field.value_m(),
            depth_m=self._depth_field.value_m(),
            reflector_tip_m=self._reflector_tip_field.value_m(),
            driven_tip_m=self._driven_tip_field.value_m(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
        )
        if geometry_issues:
            issue = geometry_issues[0]
            self._clearance_warning.setText(
                self._translator.t(issue.message_key, **issue.message_values())
            )
            self._clearance_warning.setVisible(True)
            return
        vertical = self._selected_polarization() is Polarization.VERTICAL
        required = self._width_field.value_m() / 2.0
        current = self._height_field.value_m()
        invalid = vertical and required > 0.0 and current <= required
        self._clearance_warning.setText(
            self._translator.t(
                "moxon.clearance_warning",
                height=f"{length_from_m(required, self._unit_system):.3f}",
                unit=self._translator.t(length_unit_key(self._unit_system)),
            )
            if invalid
            else ""
        )
        self._clearance_warning.setVisible(invalid)

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
        apply_radius_units(self._translator, unit_system, self._radius)
        for field in (
            self._width_field,
            self._depth_field,
            self._reflector_tip_field,
            self._driven_tip_field,
            self._height_field,
        ):
            field.set_display_units(self._display_units)
        if parameters is not None:
            self.set_parameters(parameters)
            if was_pristine:
                self.mark_starting_dimensions_pristine()

    def set_parameters(self, parameters: MoxonParameters) -> None:
        self._updating = True
        try:
            self._frequency.setValue(parameters.frequency_hz / 1_000_000.0)
            self._width_field.configure(parameters.width_m)
            self._depth_field.configure(parameters.depth_m)
            self._reflector_tip_field.configure(parameters.reflector_tip_m)
            self._driven_tip_field.configure(parameters.driven_tip_m)
            self._height_field.configure(parameters.height_m)
            self._azimuth.setValue(parameters.azimuth_deg)
            polarization_index = self._polarization.findData(parameters.polarization.value)
            if polarization_index >= 0:
                self._polarization.setCurrentIndex(polarization_index)
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
        self._starting_state.mark_non_pristine()
        self._update_ground_controls()
        self._update_geometry()

    def set_frequency_hz(self, frequency_hz: float) -> None:
        """Set the starting frequency and regenerate the scaled reference."""

        self._frequency.setValue(frequency_hz / 1_000_000.0)
        self._load_reference_preset()

    def _load_reference_preset(self) -> None:
        try:
            parameters = moxon_20m_wire(
                frequency_hz=self._frequency.value() * 1_000_000.0,
                height_m=self._height_field.value_m(),
                azimuth_deg=self._azimuth.value(),
                polarization=self._selected_polarization(),
                wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
                material=self._selected_material(),
                ground=self._ground_model(),
            )
        except ValueError:
            self._update_clearance_warning()
            self._emit_changed()
            return
        self.set_parameters(parameters)
        self._starting_state.mark_pristine(frequency_mhz=self._frequency.value())
        self._emit_changed()

    def _update_geometry(self) -> None:
        self._update_clearance_warning()
        try:
            parameters = self.parameters()
        except (ValueError, TypeError):
            self._geometry.setText("")
            self._update_frequency_warning(None)
            return
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._geometry.setText(
            self._translator.t(
                "moxon.geometry",
                gap=f"{length_from_m(parameters.gap_m, self._unit_system):.3f}",
                unit=unit,
            )
        )
        self._update_frequency_warning(parameters)

    def _update_frequency_warning(self, parameters: MoxonParameters | None) -> None:
        ratio: float | None
        if parameters is not None:
            ratio = moxon_frequency_mismatch(parameters)
        else:
            width_m = self._width_field.value_m()
            frequency_hz = self._frequency.value() * 1_000_000.0
            ratio = (
                width_m / units.wavelength_m(frequency_hz)
                if width_m > 0.0 and frequency_hz > 0.0
                else None
            )
            if ratio is not None and (
                MOXON_GROSS_WIDTH_MIN_WAVELENGTH_RATIO
                <= ratio
                <= MOXON_GROSS_WIDTH_MAX_WAVELENGTH_RATIO
            ):
                ratio = None
        if ratio is not None:
            self._frequency_warning.setText(
                self._translator.t(
                    "moxon.frequency_mismatch",
                    wavelength_ratio=f"{ratio:.3g}",
                )
            )
            self._frequency_warning.setVisible(True)
            return
        self._frequency_warning.clear()
        self._frequency_warning.setVisible(False)

    def parameters(self) -> MoxonParameters:
        return MoxonParameters(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            width_m=self._width_field.value_m(),
            depth_m=self._depth_field.value_m(),
            reflector_tip_m=self._reflector_tip_field.value_m(),
            driven_tip_m=self._driven_tip_field.value_m(),
            height_m=self._height_field.value_m(),
            azimuth_deg=self._azimuth.value(),
            polarization=self._selected_polarization(),
            wire_radius_m=radius_to_m(self._radius.value(), self._unit_system),
            material=self._selected_material(),
            ground=self._ground_model(),
        )
