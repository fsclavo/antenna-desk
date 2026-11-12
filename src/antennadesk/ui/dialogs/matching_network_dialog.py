# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ideal L, Pi, and T matching-network configuration dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.matching_network import (
    LNetwork,
    MatchingNetwork,
    MatchingNetworkPosition,
    PiNetwork,
    TNetwork,
    design_l_network,
)
from ...domain.design.matching_design import (
    MATCHING_DESIGN_ORIGIN_MANUAL,
    MATCHING_DESIGN_ORIGIN_SIMULATION,
    MatchingNetworkDesign,
)
from ..fonts import scaled_dialog_size
from ..help import apply_form_help, apply_help
from ..i18n import Translator


class MatchingNetworkDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        network: MatchingNetwork | None = None,
        parent: QWidget | None = None,
        *,
        frequency_hz: float = 14_100_000.0,
        internal_matching_active: bool = False,
        design: MatchingNetworkDesign | None = None,
        current_point: MatchingNetworkDesign | None = None,
        position: MatchingNetworkPosition = MatchingNetworkPosition.FEEDPOINT,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._network = network
        self._position = MatchingNetworkPosition(position)
        self._frequency_hz = frequency_hz
        self._internal_matching_active = internal_matching_active
        self._current_point = current_point
        self._origin = design.origin if design is not None else None
        self._updating_target = False
        self.setWindowTitle(translator.t("matching_network.title"))
        self.resize(*scaled_dialog_size(540, 680))

        self._enabled = QCheckBox(translator.t("matching_network.enabled"), self)
        self._enabled.setChecked(network is not None)
        self._enabled.toggled.connect(self._update_controls)

        def spin(suffix: str) -> QDoubleSpinBox:
            box = QDoubleSpinBox(self)
            box.setRange(0.0, 1_000_000.0)
            box.setDecimals(3)
            box.setSuffix(suffix)
            return box

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(
            (design.frequency_hz if design is not None else frequency_hz) / 1_000_000.0
        )

        self._load_r = QDoubleSpinBox(self)
        self._load_r.setRange(0.1, 100_000.0)
        self._load_r.setDecimals(3)
        self._load_r.setSuffix(" Ω")
        self._load_r.setValue(design.load_resistance_ohm if design is not None else 50.0)

        self._load_x = QDoubleSpinBox(self)
        self._load_x.setRange(-100_000.0, 100_000.0)
        self._load_x.setDecimals(3)
        self._load_x.setSuffix(" Ω")
        self._load_x.setValue(design.load_reactance_ohm if design is not None else 0.0)

        self._source_impedance = QDoubleSpinBox(self)
        self._source_impedance.setRange(0.1, 100_000.0)
        self._source_impedance.setDecimals(3)
        self._source_impedance.setSuffix(" Ω")
        self._source_impedance.setValue(design.source_impedance_ohm if design is not None else 50.0)

        self._use_current_point = QPushButton(
            translator.t("matching_network.use_current_point"),
            self,
        )
        self._use_current_point.setEnabled(current_point is not None)
        self._use_current_point.clicked.connect(self._apply_current_point)
        apply_help(self._use_current_point, translator, "matching_network.use_current_point")

        self._origin_value = QLabel(self)
        self._update_origin_value()

        self._auto = QPushButton(translator.t("matching_network.auto_design"), self)
        self._auto.clicked.connect(self._auto_design)
        apply_help(self._auto, translator, "matching_network.auto_design")

        target_group = QGroupBox(translator.t("matching_network.design_target"), self)
        target_form = QFormLayout(target_group)
        self._target_label_frequency = self._label("matching_network.frequency")
        self._target_label_r = self._label("matching_network.load_r")
        self._target_label_x = self._label("matching_network.load_x")
        self._target_label_source = self._label("matching_network.source_impedance")
        self._target_label_origin = self._label("matching_network.design_origin")
        target_form.addRow(self._target_label_frequency, self._frequency)
        target_form.addRow(self._target_label_r, self._load_r)
        target_form.addRow(self._target_label_x, self._load_x)
        target_form.addRow(self._target_label_source, self._source_impedance)
        target_form.addRow(self._target_label_origin, self._origin_value)
        target_form.addRow("", self._use_current_point)
        target_form.addRow("", self._auto)
        apply_form_help(target_form, translator)

        self._topology = QComboBox(self)
        self._topology.addItem("L", "l")
        self._topology.addItem("Pi", "pi")
        self._topology.addItem("T", "t")
        if isinstance(network, PiNetwork):
            self._topology.setCurrentIndex(1)
        elif isinstance(network, TNetwork):
            self._topology.setCurrentIndex(2)
        self._topology.currentIndexChanged.connect(self._topology_changed)

        self._position_combo = QComboBox(self)
        self._position_combo.addItem(
            translator.t("matching_network.position_feedpoint"),
            MatchingNetworkPosition.FEEDPOINT.value,
        )
        self._position_combo.addItem(
            translator.t("matching_network.position_shack"),
            MatchingNetworkPosition.SHACK.value,
        )
        index = self._position_combo.findData(self._position.value)
        if index >= 0:
            self._position_combo.setCurrentIndex(index)
        apply_help(
            self._position_combo,
            translator,
            "matching_network.position",
        )

        def initial_value(name: str, default: float) -> float:
            if network is None:
                return default
            return float(getattr(network, name, default))

        self._series_l = spin(" µH")
        self._series_l.setValue(initial_value("series_inductance_h", 1.0) * 1e6)
        self._series_c = spin(" pF")
        self._series_c.setValue(initial_value("series_capacitance_f", 0.0) * 1e12)
        self._shunt_l = spin(" µH")
        self._shunt_l.setValue(initial_value("shunt_inductance_h", 0.0) * 1e6)
        self._shunt_c = spin(" pF")
        self._shunt_c.setValue(initial_value("shunt_capacitance_f", 100.0) * 1e12)
        self._shunt_at_input = QCheckBox(translator.t("matching_network.shunt_at_input"), self)
        self._shunt_at_input.setChecked(
            network.shunt_at_input if isinstance(network, LNetwork) else False
        )
        apply_help(
            self._shunt_at_input,
            translator,
            "matching_network.shunt_at_input",
        )

        self._input_shunt_l = spin(" µH")
        self._input_shunt_c = spin(" pF")
        self._output_shunt_l = spin(" µH")
        self._output_shunt_c = spin(" pF")
        self._input_series_l = spin(" µH")
        self._input_series_c = spin(" pF")
        self._output_series_l = spin(" µH")
        self._output_series_c = spin(" pF")
        if isinstance(network, PiNetwork):
            self._input_shunt_l.setValue(network.input_shunt_inductance_h * 1e6)
            self._input_shunt_c.setValue(network.input_shunt_capacitance_f * 1e12)
            self._output_shunt_l.setValue(network.output_shunt_inductance_h * 1e6)
            self._output_shunt_c.setValue(network.output_shunt_capacitance_f * 1e12)
        elif isinstance(network, TNetwork):
            self._input_series_l.setValue(network.input_series_inductance_h * 1e6)
            self._input_series_c.setValue(network.input_series_capacitance_f * 1e12)
            self._output_series_l.setValue(network.output_series_inductance_h * 1e6)
            self._output_series_c.setValue(network.output_series_capacitance_f * 1e12)

        self._q_factor = QDoubleSpinBox(self)
        self._q_factor.setRange(0.0, 100_000.0)
        self._q_factor.setDecimals(1)
        self._q_factor.setValue(
            network.q_factor if network is not None and network.q_factor else 0.0
        )
        self._q_factor.setSpecialValueText(translator.t("matching_network.lossless"))

        self._components_group = QGroupBox(
            translator.t("matching_network.components"),
            self,
        )
        components_form = QFormLayout(self._components_group)
        self._components_label_topology = self._label("matching_network.topology")
        components_form.addRow(self._components_label_topology, self._topology)
        self._components_label_position = self._label("matching_network.position")
        components_form.addRow(self._components_label_position, self._position_combo)
        self._components_label_q = self._label("matching_network.q_factor")
        components_form.addRow(self._components_label_q, self._q_factor)
        self._rows: dict[str, tuple[QLabel, QWidget]] = {}

        def add_component_row(key: str, widget: QWidget) -> None:
            label = self._label(key)
            components_form.addRow(label, widget)
            self._rows[key] = (label, widget)

        add_component_row("matching_network.series_l", self._series_l)
        add_component_row("matching_network.series_c", self._series_c)
        add_component_row("matching_network.shunt_l", self._shunt_l)
        add_component_row("matching_network.shunt_c", self._shunt_c)
        components_form.addRow("", self._shunt_at_input)
        add_component_row("matching_network.input_shunt_l", self._input_shunt_l)
        add_component_row("matching_network.input_shunt_c", self._input_shunt_c)
        add_component_row("matching_network.output_shunt_l", self._output_shunt_l)
        add_component_row("matching_network.output_shunt_c", self._output_shunt_c)
        add_component_row("matching_network.input_series_l", self._input_series_l)
        add_component_row("matching_network.input_series_c", self._input_series_c)
        add_component_row("matching_network.output_series_l", self._output_series_l)
        add_component_row("matching_network.output_series_c", self._output_series_c)
        apply_form_help(components_form, translator)

        hint = QLabel(translator.t("matching_network.hint"), self)
        hint.setWordWrap(True)
        self._override_warning = QLabel(
            translator.t("matching_network.override_warning"),
            self,
        )
        self._override_warning.setWordWrap(True)
        self._override_warning.setStyleSheet("color: #8a5a00;")
        apply_help(self._override_warning, translator, "feed_matching.override")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._enabled)
        layout.addWidget(target_group)
        layout.addWidget(self._components_group)
        layout.addWidget(self._override_warning)
        layout.addWidget(hint)
        layout.addStretch(1)
        layout.addWidget(buttons)
        for widget in (self._frequency, self._load_r, self._load_x, self._source_impedance):
            widget.valueChanged.connect(self._target_edited)
        self._update_controls()
        self._topology_changed()

    def _label(self, key: str) -> QLabel:
        label = QLabel(self._translator.t(key), self)
        label.setObjectName(key)
        return label

    def _target_edited(self, *_args: object) -> None:
        if self._updating_target:
            return
        self._origin = MATCHING_DESIGN_ORIGIN_MANUAL
        self._update_origin_value()

    def _apply_current_point(self) -> None:
        point = self._current_point
        if point is None:
            return
        self._updating_target = True
        try:
            self._frequency.setValue(point.frequency_hz / 1_000_000.0)
            self._load_r.setValue(point.load_resistance_ohm)
            self._load_x.setValue(point.load_reactance_ohm)
            self._source_impedance.setValue(point.source_impedance_ohm)
        finally:
            self._updating_target = False
        self._origin = point.origin or MATCHING_DESIGN_ORIGIN_SIMULATION
        self._update_origin_value()

    def _update_origin_value(self) -> None:
        if self._origin is None:
            key = "matching_network.origin.none"
        elif self._origin == MATCHING_DESIGN_ORIGIN_SIMULATION:
            key = "matching_network.origin.simulation"
        elif self._origin == MATCHING_DESIGN_ORIGIN_MANUAL:
            key = "matching_network.origin.manual"
        else:
            self._origin_value.setText(self._origin)
            return
        self._origin_value.setText(self._translator.t(key))

    def _topology_changed(self, *_args: object) -> None:
        topology = self._topology.currentData()
        l_rows = topology == "l"
        pi_rows = topology == "pi"
        t_rows = topology == "t"
        for key in ("matching_network.series_l", "matching_network.series_c"):
            self._set_row_visible(key, l_rows or pi_rows)
        for key in ("matching_network.shunt_l", "matching_network.shunt_c"):
            self._set_row_visible(key, l_rows or t_rows)
        self._shunt_at_input.setVisible(l_rows)
        for key in (
            "matching_network.input_shunt_l",
            "matching_network.input_shunt_c",
            "matching_network.output_shunt_l",
            "matching_network.output_shunt_c",
        ):
            self._set_row_visible(key, pi_rows)
        for key in (
            "matching_network.input_series_l",
            "matching_network.input_series_c",
            "matching_network.output_series_l",
            "matching_network.output_series_c",
        ):
            self._set_row_visible(key, t_rows)
        self._auto.setVisible(l_rows)
        self._auto.setEnabled(l_rows)
        self._update_controls()

    def _set_row_visible(self, key: str, visible: bool) -> None:
        label, widget = self._rows[key]
        label.setVisible(visible)
        widget.setVisible(visible)

    def _auto_design(self) -> None:
        network = design_l_network(
            complex(self._load_r.value(), self._load_x.value()),
            self._frequency.value() * 1_000_000.0,
            source_impedance_ohm=self._source_impedance.value(),
        )
        if network is None:
            QMessageBox.information(
                self,
                self._translator.t("matching_network.title"),
                self._translator.t("matching_network.auto_unavailable"),
            )
            return
        self._enabled.setChecked(True)
        self._series_l.setValue(network.series_inductance_h * 1e6)
        self._series_c.setValue(network.series_capacitance_f * 1e12)
        self._shunt_l.setValue(network.shunt_inductance_h * 1e6)
        self._shunt_c.setValue(network.shunt_capacitance_f * 1e12)
        self._shunt_at_input.setChecked(network.shunt_at_input)

    def _update_controls(self) -> None:
        enabled = self._enabled.isChecked()
        self._override_warning.setVisible(enabled and self._internal_matching_active)
        for widget in (
            self._series_l,
            self._series_c,
            self._shunt_l,
            self._shunt_c,
            self._shunt_at_input,
            self._topology,
            self._position_combo,
            self._q_factor,
            self._input_shunt_l,
            self._input_shunt_c,
            self._output_shunt_l,
            self._output_shunt_c,
            self._input_series_l,
            self._input_series_c,
            self._output_series_l,
            self._output_series_c,
        ):
            widget.setEnabled(enabled)
        self._use_current_point.setEnabled(self._current_point is not None)

    def accept(self) -> None:
        try:
            self._network = self.network()
            self.result_design()
        except ValueError as exc:
            QMessageBox.critical(self, self._translator.t("matching_network.title"), str(exc))
            return
        super().accept()

    def network(self) -> MatchingNetwork | None:
        if not self._enabled.isChecked():
            return None
        topology = self._topology.currentData()
        q_factor = self._q_factor.value() or None
        if topology == "pi":
            return PiNetwork(
                input_shunt_inductance_h=self._input_shunt_l.value() * 1e-6,
                input_shunt_capacitance_f=self._input_shunt_c.value() * 1e-12,
                series_inductance_h=self._series_l.value() * 1e-6,
                series_capacitance_f=self._series_c.value() * 1e-12,
                output_shunt_inductance_h=self._output_shunt_l.value() * 1e-6,
                output_shunt_capacitance_f=self._output_shunt_c.value() * 1e-12,
                q_factor=q_factor,
            )
        if topology == "t":
            return TNetwork(
                input_series_inductance_h=self._input_series_l.value() * 1e-6,
                input_series_capacitance_f=self._input_series_c.value() * 1e-12,
                shunt_inductance_h=self._shunt_l.value() * 1e-6,
                shunt_capacitance_f=self._shunt_c.value() * 1e-12,
                output_series_inductance_h=self._output_series_l.value() * 1e-6,
                output_series_capacitance_f=self._output_series_c.value() * 1e-12,
                q_factor=q_factor,
            )
        return LNetwork(
            series_inductance_h=self._series_l.value() * 1e-6,
            series_capacitance_f=self._series_c.value() * 1e-12,
            shunt_inductance_h=self._shunt_l.value() * 1e-6,
            shunt_capacitance_f=self._shunt_c.value() * 1e-12,
            shunt_at_input=self._shunt_at_input.isChecked(),
            q_factor=q_factor,
        )

    def position(self) -> MatchingNetworkPosition:
        value = self._position_combo.currentData()
        return MatchingNetworkPosition(value) if isinstance(value, str) else self._position

    def result_design(self) -> MatchingNetworkDesign:
        return MatchingNetworkDesign(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            load_resistance_ohm=self._load_r.value(),
            load_reactance_ohm=self._load_x.value(),
            source_impedance_ohm=self._source_impedance.value(),
            origin=self._origin,
        )

    def result_network(self) -> MatchingNetwork | None:
        return self._network
