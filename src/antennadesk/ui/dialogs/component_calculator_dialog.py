# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Integrated coil, trap, LC, balun, and conductor calculators."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.materials import ALUMINUM, COPPER, ConductorMaterial
from ...domain.design.component_calculators import (
    capacitance_for_resonance_f,
    capacitive_reactance_ohm,
    impedance_ratio_for_turns_ratio,
    inductance_for_resonance_f,
    inductive_reactance_ohm,
    lc_resonance_hz,
    round_wire_resistance_per_m,
    solenoid_inductance_h,
    solenoid_turns_for_inductance,
    turns_ratio_for_impedance_ratio,
)
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator
from ..units import (
    UnitSystem,
    diameter_from_m,
    diameter_to_m,
    diameter_unit_key,
)


class CalculatorKind(StrEnum):
    COIL = "coil"
    TRAP = "trap"


@dataclass(frozen=True, slots=True)
class CalculatorResult:
    kind: CalculatorKind
    inductance_h: float | None = None
    capacitance_f: float | None = None
    frequency_hz: float | None = None


@dataclass(frozen=True, slots=True)
class CalculatorSeed:
    tab: str = "coil"
    inductance_h: float | None = None
    capacitance_f: float | None = None
    frequency_hz: float | None = None


class ComponentCalculatorDialog(QDialog):
    """Small deterministic helpers for construction components."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        *,
        seed: CalculatorSeed | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._result: CalculatorResult | None = None
        self.setWindowTitle(translator.t("component_calculator.title"))
        self.resize(*scaled_dialog_size(760, 620))

        self._tabs = QTabWidget(self)
        self._tabs.addTab(self._build_coil_tab(), translator.t("component_calculator.coil"))
        self._tabs.addTab(self._build_trap_tab(), translator.t("component_calculator.trap"))
        self._tabs.addTab(
            self._build_balun_tab(),
            translator.t("component_calculator.balun"),
        )
        self._tabs.addTab(
            self._build_conductor_tab(),
            translator.t("component_calculator.conductor"),
        )
        self._tabs.addTab(
            self._build_choke_tab(),
            translator.t("component_calculator.choke"),
        )

        self._use_button = QPushButton(translator.t("component_calculator.use"), self)
        self._use_button.setEnabled(False)
        self._use_button.clicked.connect(self.accept)
        apply_help(self._use_button, translator, "component_calculator.use")
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))
        buttons.addButton(self._use_button, QDialogButtonBox.ButtonRole.ActionRole)

        layout = QVBoxLayout(self)
        layout.addWidget(self._tabs, 1)
        layout.addWidget(buttons)
        if seed is not None:
            self._apply_seed(seed)

    def _small_spin(self, suffix: str) -> QDoubleSpinBox:
        spin = QDoubleSpinBox(self)
        spin.setRange(0.1, 1_000_000.0)
        spin.setDecimals(3)
        spin.setSuffix(suffix)
        return spin

    def _build_coil_tab(self) -> QWidget:
        t = self._translator.t
        tab = QWidget(self)
        form = QFormLayout()
        unit = t(diameter_unit_key(self._unit_system))
        self._coil_target_l = self._small_spin(" µH")
        self._coil_target_l.setValue(10.0)
        self._coil_diameter = self._small_spin(f" {unit}")
        self._coil_diameter.setValue(diameter_from_m(0.05, self._unit_system))
        self._coil_length = self._small_spin(f" {unit}")
        self._coil_length.setValue(diameter_from_m(0.05, self._unit_system))
        self._coil_turns = self._small_spin("")
        self._coil_turns.setRange(0.1, 10_000.0)
        self._coil_turns.setValue(10.0)

        self._coil_l_button = QPushButton(t("component_calculator.from_turns"), tab)
        self._coil_turns_button = QPushButton(t("component_calculator.for_inductance"), tab)
        self._coil_l_button.clicked.connect(self._coil_from_turns)
        self._coil_turns_button.clicked.connect(self._coil_turns_for_l)
        apply_help(self._coil_l_button, self._translator, "component_calculator.from_turns")
        apply_help(
            self._coil_turns_button,
            self._translator,
            "component_calculator.for_inductance",
        )
        self._coil_result = QLabel(tab)
        self._coil_result.setWordWrap(True)
        self._coil_hint = QLabel(t("component_calculator.coil_hint"), tab)
        self._coil_hint.setWordWrap(True)

        rows = [
            (t("component_calculator.inductance"), self._coil_target_l),
            (t("component_calculator.diameter"), self._coil_diameter),
            (t("component_calculator.winding_length"), self._coil_length),
            (t("component_calculator.turns"), self._coil_turns),
        ]
        for row, (label_text, widget) in enumerate(rows):
            label = QLabel(label_text, tab)
            form.addRow(label, widget)
            apply_row_help(
                form,
                row,
                self._translator,
                f"component_calculator.{self._coil_help_key(row)}",
            )
        buttons = QHBoxLayout()
        buttons.addWidget(self._coil_l_button)
        buttons.addWidget(self._coil_turns_button)
        buttons.addStretch(1)
        layout = QVBoxLayout(tab)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self._coil_result)
        layout.addWidget(self._coil_hint)
        layout.addStretch(1)
        apply_help(tab, self._translator, "component_calculator.coil")
        return tab

    @staticmethod
    def _coil_help_key(row: int) -> str:
        return ("inductance", "diameter", "winding_length", "turns")[row]

    def _build_trap_tab(self) -> QWidget:
        t = self._translator.t
        tab = QWidget(self)
        form = QFormLayout()
        self._trap_frequency = self._small_spin(" MHz")
        self._trap_frequency.setValue(14.1)
        self._trap_inductance = self._small_spin(" µH")
        self._trap_inductance.setValue(10.0)
        self._trap_capacitance = self._small_spin(" pF")
        self._trap_capacitance.setValue(100.0)
        self._trap_solve_c = QPushButton(t("component_calculator.solve_c"), tab)
        self._trap_solve_l = QPushButton(t("component_calculator.solve_l"), tab)
        self._trap_solve_f = QPushButton(t("component_calculator.solve_f"), tab)
        self._trap_solve_c.clicked.connect(self._trap_for_c)
        self._trap_solve_l.clicked.connect(self._trap_for_l)
        self._trap_solve_f.clicked.connect(self._trap_for_f)
        for button, key in (
            (self._trap_solve_c, "component_calculator.solve_c"),
            (self._trap_solve_l, "component_calculator.solve_l"),
            (self._trap_solve_f, "component_calculator.solve_f"),
        ):
            apply_help(button, self._translator, key)
        self._trap_result = QLabel(tab)
        self._trap_result.setWordWrap(True)
        self._trap_hint = QLabel(t("component_calculator.trap_hint"), tab)
        self._trap_hint.setWordWrap(True)

        rows = [
            (t("component_calculator.frequency"), self._trap_frequency),
            (t("component_calculator.inductance"), self._trap_inductance),
            (t("component_calculator.capacitance"), self._trap_capacitance),
        ]
        for row, (label_text, widget) in enumerate(rows):
            label = QLabel(label_text, tab)
            form.addRow(label, widget)
            apply_row_help(
                form,
                row,
                self._translator,
                f"component_calculator.{self._trap_help_key(row)}",
            )
        buttons = QHBoxLayout()
        buttons.addWidget(self._trap_solve_c)
        buttons.addWidget(self._trap_solve_l)
        buttons.addWidget(self._trap_solve_f)
        buttons.addStretch(1)
        layout = QVBoxLayout(tab)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self._trap_result)
        layout.addWidget(self._trap_hint)
        layout.addStretch(1)
        apply_help(tab, self._translator, "component_calculator.trap")
        return tab

    @staticmethod
    def _trap_help_key(row: int) -> str:
        return ("frequency", "inductance", "capacitance")[row]

    def _build_balun_tab(self) -> QWidget:
        t = self._translator.t
        tab = QWidget(self)
        form = QFormLayout()
        self._balun_turns = self._small_spin(" : 1")
        self._balun_turns.setValue(4.0)
        self._balun_impedance = self._small_spin(" : 1")
        self._balun_impedance.setValue(16.0)
        self._balun_turns_button = QPushButton(
            t("component_calculator.impedance_from_turns"),
            tab,
        )
        self._balun_impedance_button = QPushButton(
            t("component_calculator.turns_from_impedance"),
            tab,
        )
        self._balun_turns_button.clicked.connect(self._balun_from_turns)
        self._balun_impedance_button.clicked.connect(self._balun_from_impedance)
        for button, key in (
            (self._balun_turns_button, "component_calculator.impedance_from_turns"),
            (self._balun_impedance_button, "component_calculator.turns_from_impedance"),
        ):
            apply_help(button, self._translator, key)
        self._balun_result = QLabel(tab)
        self._balun_result.setWordWrap(True)
        self._balun_hint = QLabel(t("component_calculator.balun_hint"), tab)
        self._balun_hint.setWordWrap(True)
        rows = [
            (t("component_calculator.turns_ratio"), self._balun_turns),
            (t("component_calculator.impedance_ratio"), self._balun_impedance),
        ]
        for row, (label_text, widget) in enumerate(rows):
            label = QLabel(label_text, tab)
            form.addRow(label, widget)
            apply_row_help(
                form,
                row,
                self._translator,
                f"component_calculator.{self._balun_help_key(row)}",
            )
        buttons = QHBoxLayout()
        buttons.addWidget(self._balun_turns_button)
        buttons.addWidget(self._balun_impedance_button)
        buttons.addStretch(1)
        layout = QVBoxLayout(tab)
        layout.addLayout(form)
        layout.addLayout(buttons)
        layout.addWidget(self._balun_result)
        layout.addWidget(self._balun_hint)
        layout.addStretch(1)
        apply_help(tab, self._translator, "component_calculator.balun")
        return tab

    @staticmethod
    def _balun_help_key(row: int) -> str:
        return ("turns_ratio", "impedance_ratio")[row]

    def _build_conductor_tab(self) -> QWidget:
        t = self._translator.t
        tab = QWidget(self)
        form = QFormLayout()
        self._material = QComboBox(tab)
        self._material.addItem(t("component_calculator.copper"), COPPER)
        self._material.addItem(t("component_calculator.aluminum"), ALUMINUM)
        self._conductor_diameter = self._small_spin(f" {t(diameter_unit_key(self._unit_system))}")
        self._conductor_diameter.setValue(diameter_from_m(0.001, self._unit_system))
        self._conductor_frequency = self._small_spin(" MHz")
        self._conductor_frequency.setValue(7.1)
        self._conductor_button = QPushButton(t("component_calculator.calculate"), tab)
        self._conductor_button.clicked.connect(self._conductor_calculate)
        apply_help(self._conductor_button, self._translator, "component_calculator.calculate")
        self._conductor_result = QLabel(tab)
        self._conductor_result.setWordWrap(True)
        self._conductor_hint = QLabel(t("component_calculator.conductor_hint"), tab)
        self._conductor_hint.setWordWrap(True)
        rows = [
            (t("component_calculator.material"), self._material),
            (t("component_calculator.diameter"), self._conductor_diameter),
            (t("component_calculator.frequency"), self._conductor_frequency),
        ]
        for row, (label_text, widget) in enumerate(rows):
            label = QLabel(label_text, tab)
            form.addRow(label, widget)
            apply_row_help(
                form,
                row,
                self._translator,
                f"component_calculator.{self._conductor_help_key(row)}",
            )
        layout = QVBoxLayout(tab)
        layout.addLayout(form)
        layout.addWidget(self._conductor_button)
        layout.addWidget(self._conductor_result)
        layout.addWidget(self._conductor_hint)
        layout.addStretch(1)
        apply_help(tab, self._translator, "component_calculator.conductor")
        return tab

    @staticmethod
    def _conductor_help_key(row: int) -> str:
        return ("material", "diameter", "frequency")[row]

    def _build_choke_tab(self) -> QWidget:
        tab = QWidget(self)
        text = QTextBrowser(tab)
        text.setOpenExternalLinks(False)
        text.setHtml(self._translator.t("component_calculator.choke_text"))
        layout = QVBoxLayout(tab)
        layout.addWidget(text)
        apply_help(tab, self._translator, "component_calculator.choke")
        return tab

    def _apply_seed(self, seed: CalculatorSeed) -> None:
        if seed.tab == "trap":
            self._tabs.setCurrentIndex(1)
            if seed.frequency_hz is not None:
                self._trap_frequency.setValue(seed.frequency_hz / 1e6)
            if seed.inductance_h is not None:
                self._trap_inductance.setValue(seed.inductance_h * 1e6)
            if seed.capacitance_f is not None:
                self._trap_capacitance.setValue(seed.capacitance_f * 1e12)
        else:
            if seed.inductance_h is not None:
                self._coil_target_l.setValue(seed.inductance_h * 1e6)

    def _set_result(self, result: CalculatorResult | None) -> None:
        self._result = result
        self._use_button.setEnabled(result is not None)

    def _coil_dimensions(self) -> tuple[float, float]:
        diameter = diameter_to_m(self._coil_diameter.value(), self._unit_system)
        length = diameter_to_m(self._coil_length.value(), self._unit_system)
        return diameter, length

    def _coil_from_turns(self) -> None:
        try:
            diameter, length = self._coil_dimensions()
            inductance = solenoid_inductance_h(
                turns=round(self._coil_turns.value()),
                diameter_m=diameter,
                length_m=length,
            )
        except ValueError as exc:
            self._coil_result.setText(str(exc))
            return
        self._coil_target_l.setValue(inductance * 1e6)
        self._coil_result.setText(
            self._translator.t(
                "component_calculator.result_coil",
                inductance=f"{inductance * 1e6:.3f}",
                turns=f"{self._coil_turns.value():.0f}",
            )
        )
        self._set_result(CalculatorResult(CalculatorKind.COIL, inductance_h=inductance))

    def _coil_turns_for_l(self) -> None:
        try:
            diameter, length = self._coil_dimensions()
            turns = solenoid_turns_for_inductance(
                inductance_h=self._coil_target_l.value() * 1e-6,
                diameter_m=diameter,
                length_m=length,
            )
        except ValueError as exc:
            self._coil_result.setText(str(exc))
            return
        self._coil_turns.setValue(turns)
        self._coil_result.setText(
            self._translator.t(
                "component_calculator.result_turns",
                turns=f"{turns:.2f}",
                inductance=f"{self._coil_target_l.value():.3f}",
            )
        )
        self._set_result(
            CalculatorResult(
                CalculatorKind.COIL,
                inductance_h=self._coil_target_l.value() * 1e-6,
            )
        )

    def _trap_for_c(self) -> None:
        try:
            capacitance = capacitance_for_resonance_f(
                inductance_h=self._trap_inductance.value() * 1e-6,
                frequency_hz=self._trap_frequency.value() * 1e6,
            )
        except ValueError as exc:
            self._trap_result.setText(str(exc))
            return
        self._trap_capacitance.setValue(capacitance * 1e12)
        self._trap_result.setText(
            self._translator.t(
                "component_calculator.result_trap_c",
                capacitance=f"{capacitance * 1e12:.3f}",
                frequency=f"{self._trap_frequency.value():.6f}",
            )
        )
        self._set_result(
            CalculatorResult(
                CalculatorKind.TRAP,
                inductance_h=self._trap_inductance.value() * 1e-6,
                capacitance_f=capacitance,
                frequency_hz=self._trap_frequency.value() * 1e6,
            )
        )

    def _trap_for_l(self) -> None:
        try:
            inductance = inductance_for_resonance_f(
                capacitance_f=self._trap_capacitance.value() * 1e-12,
                frequency_hz=self._trap_frequency.value() * 1e6,
            )
        except ValueError as exc:
            self._trap_result.setText(str(exc))
            return
        self._trap_inductance.setValue(inductance * 1e6)
        self._trap_result.setText(
            self._translator.t(
                "component_calculator.result_trap_l",
                inductance=f"{inductance * 1e6:.3f}",
                frequency=f"{self._trap_frequency.value():.6f}",
            )
        )
        self._set_result(
            CalculatorResult(
                CalculatorKind.TRAP,
                inductance_h=inductance,
                capacitance_f=self._trap_capacitance.value() * 1e-12,
                frequency_hz=self._trap_frequency.value() * 1e6,
            )
        )

    def _trap_for_f(self) -> None:
        try:
            frequency = lc_resonance_hz(
                inductance_h=self._trap_inductance.value() * 1e-6,
                capacitance_f=self._trap_capacitance.value() * 1e-12,
            )
            xl = inductive_reactance_ohm(
                inductance_h=self._trap_inductance.value() * 1e-6,
                frequency_hz=frequency,
            )
            xc = capacitive_reactance_ohm(
                capacitance_f=self._trap_capacitance.value() * 1e-12,
                frequency_hz=frequency,
            )
        except ValueError as exc:
            self._trap_result.setText(str(exc))
            return
        self._trap_frequency.setValue(frequency / 1e6)
        self._trap_result.setText(
            self._translator.t(
                "component_calculator.result_trap_f",
                frequency=f"{frequency / 1e6:.6f}",
                xl=f"{xl:.3f}",
                xc=f"{xc:.3f}",
            )
        )
        self._set_result(
            CalculatorResult(
                CalculatorKind.TRAP,
                inductance_h=self._trap_inductance.value() * 1e-6,
                capacitance_f=self._trap_capacitance.value() * 1e-12,
                frequency_hz=frequency,
            )
        )

    def _balun_from_turns(self) -> None:
        ratio = impedance_ratio_for_turns_ratio(self._balun_turns.value())
        self._balun_impedance.setValue(ratio)
        self._balun_result.setText(
            self._translator.t(
                "component_calculator.result_balun_impedance",
                turns=f"{self._balun_turns.value():g}",
                ratio=f"{ratio:g}",
            )
        )

    def _balun_from_impedance(self) -> None:
        turns = turns_ratio_for_impedance_ratio(self._balun_impedance.value())
        self._balun_turns.setValue(turns)
        self._balun_result.setText(
            self._translator.t(
                "component_calculator.result_balun_turns",
                ratio=f"{self._balun_impedance.value():g}",
                turns=f"{turns:g}",
            )
        )

    def _conductor_calculate(self) -> None:
        material = self._material.currentData()
        if not isinstance(material, ConductorMaterial):
            return
        try:
            dc, rf, depth = round_wire_resistance_per_m(
                frequency_hz=self._conductor_frequency.value() * 1e6,
                diameter_m=diameter_to_m(
                    self._conductor_diameter.value(),
                    self._unit_system,
                ),
                material=material,
            )
        except ValueError as exc:
            self._conductor_result.setText(str(exc))
            return
        self._conductor_result.setText(
            self._translator.t(
                "component_calculator.result_conductor",
                dc=f"{dc:.4f}",
                rf=f"{rf:.4f}",
                depth=f"{depth * 1e6:.3f}",
            )
        )

    def calculator_result(self) -> CalculatorResult | None:
        return self._result
