# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided antenna creation wizard."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from ...domain.antennas.design import AntennaDesignParameters
from ...domain.antennas.dipole import (
    ANTENNA_TYPE_WIRE_DIPOLE,
    DipoleOrientation,
    DipoleParameters,
)
from ...domain.antennas.folded_dipole import (
    ANTENNA_TYPE_FOLDED_DIPOLE,
    FoldedDipoleParameters,
)
from ...domain.antennas.loop import ANTENNA_TYPE_LOOP, LoopParameters
from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.common import units
from ...domain.environment.ground import GroundKind, GroundModel
from ..i18n import Translator
from ..units import (
    UnitSystem,
    diameter_bounds,
    diameter_from_m,
    diameter_to_m,
    diameter_unit_key,
    height_bounds,
    length_bounds,
    length_from_m,
    length_to_m,
    length_unit_key,
)

BANDS: tuple[tuple[str, float | None], ...] = (
    ("160 m", 1.85),
    ("80 m", 3.7),
    ("60 m", 5.35),
    ("40 m", 7.1),
    ("30 m", 10.125),
    ("20 m", 14.1),
    ("17 m", 18.1),
    ("15 m", 21.1),
    ("12 m", 24.9),
    ("10 m", 28.5),
    ("6 m", 50.1),
    ("2 m", 145.0),
    ("70 cm", 435.0),
)

MATERIALS = (COPPER, ALUMINUM)


class ProjectPage(QWizardPage):
    def __init__(self, translator: Translator, parent: QWizard | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._setting_frequency = False

        self._name = QLineEdit(self)
        self._name.setPlaceholderText("40 m dipole")
        self._name.textChanged.connect(self.completeChanged)
        self._name_edited = False
        self._name.textEdited.connect(self._on_name_edited)

        self._type = QComboBox(self)
        self._type.addItem(translator.t("antenna_type.wire_dipole"), ANTENNA_TYPE_WIRE_DIPOLE)
        self._type.addItem(translator.t("antenna_type.folded_dipole"), ANTENNA_TYPE_FOLDED_DIPOLE)
        self._type.addItem(translator.t("antenna_type.loop"), ANTENNA_TYPE_LOOP)
        self._type.currentIndexChanged.connect(self._type_changed)

        self._band = QComboBox(self)
        for label, frequency in BANDS:
            self._band.addItem(label, frequency)
        self._band.addItem("", None)
        self._band.setCurrentIndex(3)
        self._band.currentIndexChanged.connect(self._band_changed)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setValue(7.1)
        self._frequency.setSuffix(" MHz")
        self._frequency.valueChanged.connect(self._frequency_changed)
        self._frequency.valueChanged.connect(self.completeChanged)

        form = QFormLayout(self)
        form.addRow(self._label("field.project_name"), self._name)
        form.addRow(self._label("field.template"), self._type)
        form.addRow(self._label("wizard.band"), self._band)
        form.addRow(self._label("field.frequency"), self._frequency)

        self._name.setText(self._default_name())

        self.setTitle(translator.t("wizard.project_page"))
        self.setSubTitle(translator.t("wizard.project_page_desc"))

    def _label(self, key: str) -> QLabel:
        label = QLabel(self._translator.t(key), self)
        label.setObjectName(key)
        return label

    def set_project_name(self, name: str) -> None:
        self._name.setText(name)
        self._name_edited = True

    def set_frequency_hz(self, frequency_hz: float) -> None:
        self._frequency.setValue(frequency_hz / 1_000_000.0)

    def set_antenna_type(self, antenna_type: str) -> None:
        index = self._type.findData(antenna_type)
        if index >= 0:
            self._type.setCurrentIndex(index)

    def antenna_type(self) -> str:
        value = self._type.currentData()
        return value if isinstance(value, str) else ANTENNA_TYPE_WIRE_DIPOLE

    def project_name(self) -> str:
        return self._name.text().strip()

    def frequency_hz(self) -> float:
        return self._frequency.value() * 1_000_000.0

    def isComplete(self) -> bool:
        return bool(self.project_name()) and self._frequency.value() > 0.0

    def _on_name_edited(self, _text: str) -> None:
        self._name_edited = True

    def _type_label(self) -> str:
        key = {
            ANTENNA_TYPE_WIRE_DIPOLE: "wizard.name_wire",
            ANTENNA_TYPE_FOLDED_DIPOLE: "wizard.name_folded",
            ANTENNA_TYPE_LOOP: "wizard.name_loop",
        }[self.antenna_type()]
        return self._translator.t(key)

    def _default_name(self) -> str:
        band = self._band.currentText()
        if self._band.currentData() is None:
            band = f"{self._frequency.value():g} MHz"
        return f"{band} {self._type_label()}"

    def _update_default_name(self) -> None:
        if not self._name_edited:
            self._name.setText(self._default_name())

    def _type_changed(self) -> None:
        self._update_default_name()

    def _band_changed(self) -> None:
        frequency = self._band.currentData()
        if frequency is None:
            self._update_default_name()
            return
        self._setting_frequency = True
        self._frequency.setValue(float(frequency))
        self._setting_frequency = False
        self._update_default_name()

    def _frequency_changed(self) -> None:
        if self._setting_frequency:
            return
        value = self._frequency.value()
        for index, (_, band_frequency) in enumerate(BANDS):
            if band_frequency is not None and abs(value - band_frequency) < 1e-9:
                self._band.blockSignals(True)
                self._band.setCurrentIndex(index)
                self._band.blockSignals(False)
                self._update_default_name()
                return
        self._band.blockSignals(True)
        self._band.setCurrentIndex(self._band.count() - 1)
        self._band.blockSignals(False)
        self._update_default_name()


class GeometryPage(QWizardPage):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWizard | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._initialized = False

        length_min, length_max = length_bounds(unit_system)
        height_min, height_max = height_bounds(unit_system)
        unit = translator.t(length_unit_key(unit_system))

        self._orientation = QComboBox(self)
        self._orientation.addItem("", DipoleOrientation.HORIZONTAL.value)
        self._orientation.addItem("", DipoleOrientation.VERTICAL.value)
        self._orientation.currentIndexChanged.connect(self._orientation_changed)

        self._length = QDoubleSpinBox(self)
        self._length.setRange(length_min, length_max)
        self._length.setDecimals(3)
        self._length.setSuffix(f" {unit}")
        self._length.setValue(length_from_m(20.0, unit_system))

        self._spacing = QDoubleSpinBox(self)
        self._spacing.setRange(length_min, length_max)
        self._spacing.setDecimals(3)
        self._spacing.setSuffix(f" {unit}")
        self._spacing.setValue(length_from_m(0.1, unit_system))

        self._sides = QSpinBox(self)
        self._sides.setRange(3, 128)
        self._sides.setValue(16)

        self._height = QDoubleSpinBox(self)
        self._height.setRange(height_min, height_max)
        self._height.setDecimals(3)
        self._height.setSuffix(f" {unit}")
        self._height.setValue(length_from_m(8.0, unit_system))

        self._azimuth = QDoubleSpinBox(self)
        self._azimuth.setRange(0.0, 360.0)
        self._azimuth.setDecimals(1)
        self._azimuth.setSuffix("°")

        self._suggest = QPushButton(self)
        self._suggest.clicked.connect(self._suggest_length)

        self._form_layout = QFormLayout(self)
        form = self._form_layout
        form.addRow(self._label("field.orientation"), self._orientation)
        form.addRow(self._label("field.length"), self._length)
        form.addRow(self._label("field.spacing"), self._spacing)
        form.addRow(self._label("field.sides"), self._sides)
        form.addRow(self._label("field.height"), self._height)
        form.addRow(self._label("field.azimuth"), self._azimuth)
        form.addRow(self._suggest)

        self.setTitle(translator.t("wizard.geometry_page"))
        self.setSubTitle(translator.t("wizard.geometry_page_desc"))
        self.retranslate()

    def _label(self, key: str) -> QLabel:
        label = QLabel(self._translator.t(key), self)
        label.setObjectName(key)
        return label

    def retranslate(self) -> None:
        for label in self.findChildren(QLabel):
            key = label.objectName()
            if key:
                label.setText(self._translator.t(key))
        self._suggest.setText(self._translator.t("wizard.suggest_length"))
        self._orientation.setItemText(0, self._translator.t("orientation.horizontal"))
        self._orientation.setItemText(1, self._translator.t("orientation.vertical"))
        self._update_orientation_labels()
        self._update_type_labels()

    def _orientation_changed(self) -> None:
        self._update_orientation_labels()

    def antenna_type(self) -> str:
        wizard = self.wizard()
        if isinstance(wizard, DipoleWizard):
            return wizard.project_page.antenna_type()
        return ANTENNA_TYPE_WIRE_DIPOLE

    def _set_row_visible(self, field: QWidget, visible: bool) -> None:
        label = self._form_layout.labelForField(field)
        if label is not None:
            label.setVisible(visible)
        field.setVisible(visible)

    def _update_type_labels(self) -> None:
        antenna_type = self.antenna_type()
        is_wire = antenna_type == ANTENNA_TYPE_WIRE_DIPOLE
        self._set_row_visible(self._orientation, is_wire)
        self._set_row_visible(self._spacing, antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE)
        self._set_row_visible(self._sides, antenna_type == ANTENNA_TYPE_LOOP)
        length_key = {
            ANTENNA_TYPE_WIRE_DIPOLE: "field.length",
            ANTENNA_TYPE_FOLDED_DIPOLE: "field.element_length",
            ANTENNA_TYPE_LOOP: "field.circumference",
        }[antenna_type]
        for label in self.findChildren(QLabel):
            if label.objectName() == "field.length":
                label.setText(self._translator.t(length_key))
                break
        self._update_orientation_labels()

    def _update_orientation_labels(self) -> None:
        antenna_type = self.antenna_type()
        is_wire = antenna_type == ANTENNA_TYPE_WIRE_DIPOLE
        vertical = is_wire and self._orientation.currentData() == DipoleOrientation.VERTICAL.value
        self._azimuth.setEnabled(not vertical)
        base_height = vertical or antenna_type == ANTENNA_TYPE_LOOP
        for label in self.findChildren(QLabel):
            if label.objectName() == "field.height":
                label.setText(
                    self._translator.t("field.base_height" if base_height else "field.height")
                )
                break

    def orientation(self) -> DipoleOrientation:
        return DipoleOrientation(self._orientation.currentData())

    def initializePage(self) -> None:
        antenna_type = self.antenna_type()
        if not self._initialized or antenna_type != getattr(self, "_last_type", None):
            self._initialized = True
            self._last_type = antenna_type
            self._suggest_length()
        self._update_type_labels()

    def _suggest_length(self) -> None:
        wizard = self.wizard()
        if not isinstance(wizard, DipoleWizard):
            return
        wavelength = units.wavelength_m(wizard.frequency_hz())
        factor = 1.0 if self.antenna_type() == ANTENNA_TYPE_LOOP else 0.5
        suggested_m = wavelength * factor * 0.95
        self._length.setValue(length_from_m(suggested_m, self._unit_system))

    def length_m(self) -> float:
        return length_to_m(self._length.value(), self._unit_system)

    def height_m(self) -> float:
        return length_to_m(self._height.value(), self._unit_system)

    def spacing_m(self) -> float:
        return length_to_m(self._spacing.value(), self._unit_system)

    def sides(self) -> int:
        return self._sides.value()

    def azimuth_deg(self) -> float:
        return self._azimuth.value()


class ConductorPage(QWizardPage):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWizard | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system

        self._material = QComboBox(self)
        for material in MATERIALS:
            self._material.addItem(material.name, material)

        diameter_min, diameter_max = diameter_bounds(unit_system)
        self._diameter = QDoubleSpinBox(self)
        self._diameter.setRange(diameter_min, diameter_max)
        self._diameter.setDecimals(3 if unit_system is UnitSystem.METRIC else 4)
        self._diameter.setSuffix(f" {translator.t(diameter_unit_key(unit_system))}")
        self._diameter.setValue(diameter_from_m(0.002, unit_system))

        form = QFormLayout(self)
        form.addRow(self._label("field.material"), self._material)
        form.addRow(self._label("field.diameter"), self._diameter)

        self.setTitle(translator.t("wizard.conductor_page"))
        self.setSubTitle(translator.t("wizard.conductor_page_desc"))
        self.retranslate()

    def _label(self, key: str) -> QLabel:
        label = QLabel(self._translator.t(key), self)
        label.setObjectName(key)
        return label

    def retranslate(self) -> None:
        for label in self.findChildren(QLabel):
            key = label.objectName()
            if key:
                label.setText(self._translator.t(key))
        self._material.setItemText(0, self._translator.t("material.copper"))
        self._material.setItemText(1, self._translator.t("material.aluminum"))

    def material(self) -> ConductorMaterial:
        value = self._material.currentData()
        if not isinstance(value, ConductorMaterial):
            raise ValueError("invalid material")
        return value

    def radius_m(self) -> float:
        return diameter_to_m(self._diameter.value(), self._unit_system) / 2.0


class GroundPage(QWizardPage):
    def __init__(self, translator: Translator, parent: QWizard | None = None) -> None:
        super().__init__(parent)
        self._translator = translator

        self._ground = QComboBox(self)
        self._ground.addItem("", GroundKind.FREE_SPACE.value)
        self._ground.addItem("", GroundKind.PERFECT.value)
        self._ground.addItem("", GroundKind.FINITE.value)
        self._ground.setCurrentIndex(2)
        self._ground.currentIndexChanged.connect(self._update_controls)

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

        form = QFormLayout(self)
        form.addRow(self._label("field.ground"), self._ground)
        form.addRow(self._label("field.permittivity"), self._permittivity)
        form.addRow(self._label("field.conductivity"), self._conductivity)

        self.setTitle(translator.t("wizard.ground_page"))
        self.setSubTitle(translator.t("wizard.ground_page_desc"))
        self.retranslate()
        self._update_controls()

    def _label(self, key: str) -> QLabel:
        label = QLabel(self._translator.t(key), self)
        label.setObjectName(key)
        return label

    def retranslate(self) -> None:
        for label in self.findChildren(QLabel):
            key = label.objectName()
            if key:
                label.setText(self._translator.t(key))
        self._ground.setItemText(0, self._translator.t("ground.free_space"))
        self._ground.setItemText(1, self._translator.t("ground.perfect"))
        self._ground.setItemText(2, self._translator.t("ground.finite"))

    def _update_controls(self) -> None:
        finite = self._ground.currentData() == GroundKind.FINITE.value
        self._permittivity.setEnabled(finite)
        self._conductivity.setEnabled(finite)

    def ground(self) -> GroundModel:
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


class ReviewPage(QWizardPage):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWizard | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._valid = False

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self._summary)

        self.setTitle(translator.t("wizard.review_page"))
        self.setSubTitle(translator.t("wizard.review_page_desc"))

    def initializePage(self) -> None:
        wizard = self.wizard()
        if not isinstance(wizard, DipoleWizard):
            self._valid = False
            return
        try:
            parameters = wizard.build_parameters()
        except ValueError as exc:
            self._valid = False
            self._summary.setText(str(exc))
            self.completeChanged.emit()
            return
        self._valid = True
        self.completeChanged.emit()
        unit = self._translator.t(length_unit_key(self._unit_system))
        diameter_unit = self._translator.t(diameter_unit_key(self._unit_system))
        material_key = {
            "copper": "material.copper",
            "aluminum": "material.aluminum",
        }.get(parameters.material.name)
        material = (
            self._translator.t(material_key)
            if material_key is not None
            else parameters.material.name
        )
        ground_key = {
            GroundKind.FREE_SPACE: "ground.free_space",
            GroundKind.PERFECT: "ground.perfect",
            GroundKind.FINITE: "ground.finite",
        }[parameters.ground.kind]

        if isinstance(parameters, FoldedDipoleParameters):
            primary_label = self._translator.t("field.element_length")
            primary = f"{length_from_m(parameters.total_length_m, self._unit_system):.3f} {unit}"
            secondary_label = self._translator.t("field.spacing")
            secondary = f"{length_from_m(parameters.spacing_m, self._unit_system):.3f} {unit}"
            height_label = self._translator.t("field.height")
            azimuth = f"{parameters.azimuth_deg:.1f}"
        elif isinstance(parameters, LoopParameters):
            primary_label = self._translator.t("field.circumference")
            primary = f"{length_from_m(parameters.circumference_m, self._unit_system):.3f} {unit}"
            secondary_label = self._translator.t("field.sides")
            secondary = str(parameters.sides)
            height_label = self._translator.t("field.base_height")
            azimuth = f"{parameters.azimuth_deg:.1f}"
        else:
            primary_label = self._translator.t("field.length")
            primary = f"{length_from_m(parameters.total_length_m, self._unit_system):.3f} {unit}"
            secondary_label = self._translator.t("field.orientation")
            secondary = self._translator.t(f"orientation.{parameters.orientation.value}")
            vertical = parameters.orientation is DipoleOrientation.VERTICAL
            height_label = self._translator.t("field.base_height" if vertical else "field.height")
            azimuth = "—" if vertical else f"{parameters.azimuth_deg:.1f}"

        self._summary.setText(
            self._translator.t(
                "wizard.review",
                project=wizard.project_name(),
                type=self._translator.t(f"antenna_type.{wizard.project_page.antenna_type()}"),
                frequency=parameters.frequency_hz / 1e6,
                primary_label=primary_label,
                primary=primary,
                secondary_label=secondary_label,
                secondary=secondary,
                height_label=height_label,
                height=f"{length_from_m(parameters.height_m, self._unit_system):.3f} {unit}",
                azimuth=azimuth,
                diameter=(
                    f"{diameter_from_m(parameters.wire_radius_m * 2.0, self._unit_system):.3f} "
                    f"{diameter_unit}"
                ),
                material=material,
                ground=self._translator.t(ground_key),
            )
        )

    def isComplete(self) -> bool:
        return self._valid


class DipoleWizard(QWizard):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        initial_frequency_hz: float = 7_100_000.0,
        initial_antenna_type: str = ANTENNA_TYPE_WIRE_DIPOLE,
        parent: QWizard | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system

        self.setWindowTitle(translator.t("wizard.title"))
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)

        self.project_page = ProjectPage(translator, self)
        self.geometry_page = GeometryPage(translator, unit_system, self)
        self.conductor_page = ConductorPage(translator, unit_system, self)
        self.ground_page = GroundPage(translator, self)
        self.review_page = ReviewPage(translator, unit_system, self)

        self.setPage(0, self.project_page)
        self.setPage(1, self.geometry_page)
        self.setPage(2, self.conductor_page)
        self.setPage(3, self.ground_page)
        self.setPage(4, self.review_page)

        self.project_page.set_antenna_type(initial_antenna_type)
        self.project_page.set_frequency_hz(initial_frequency_hz)

        self.setButtonText(
            QWizard.WizardButton.NextButton,
            translator.t("action.next"),
        )
        self.setButtonText(
            QWizard.WizardButton.BackButton,
            translator.t("action.back"),
        )
        self.setButtonText(
            QWizard.WizardButton.FinishButton,
            translator.t("action.finish"),
        )
        self.setButtonText(
            QWizard.WizardButton.CancelButton,
            translator.t("action.cancel"),
        )

    def project_name(self) -> str:
        return self.project_page.project_name()

    def frequency_hz(self) -> float:
        return self.project_page.frequency_hz()

    def build_parameters(self) -> AntennaDesignParameters:
        common = {
            "frequency_hz": self.frequency_hz(),
            "height_m": self.geometry_page.height_m(),
            "azimuth_deg": self.geometry_page.azimuth_deg(),
            "wire_radius_m": self.conductor_page.radius_m(),
            "material": self.conductor_page.material(),
            "ground": self.ground_page.ground(),
        }
        antenna_type = self.project_page.antenna_type()
        if antenna_type == ANTENNA_TYPE_FOLDED_DIPOLE:
            return FoldedDipoleParameters(
                total_length_m=self.geometry_page.length_m(),
                spacing_m=self.geometry_page.spacing_m(),
                **common,
            )
        if antenna_type == ANTENNA_TYPE_LOOP:
            return LoopParameters(
                circumference_m=self.geometry_page.length_m(),
                sides=self.geometry_page.sides(),
                **common,
            )
        return DipoleParameters(
            total_length_m=self.geometry_page.length_m(),
            orientation=self.geometry_page.orientation(),
            **common,
        )
