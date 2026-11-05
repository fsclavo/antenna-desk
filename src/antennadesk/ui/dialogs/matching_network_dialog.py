# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ideal L-network configuration dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.matching_network import (
    LNetwork,
    MatchingNetwork,
    PiNetwork,
    TNetwork,
    design_l_network,
)
from ..i18n import Translator


class MatchingNetworkDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        network: MatchingNetwork | None = None,
        parent: QWidget | None = None,
        *,
        frequency_hz: float = 14_100_000.0,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._network = network
        self._frequency_hz = frequency_hz
        self.setWindowTitle(translator.t("matching_network.title"))
        self.resize(480, 440)

        self._enabled = QCheckBox(translator.t("matching_network.enabled"), self)
        self._enabled.setChecked(network is not None)
        self._enabled.toggled.connect(self._update_controls)

        self._topology = QComboBox(self)
        self._topology.addItem("L", "l")
        self._topology.addItem("Pi", "pi")
        self._topology.addItem("T", "t")
        if isinstance(network, PiNetwork):
            self._topology.setCurrentIndex(1)
        elif isinstance(network, TNetwork):
            self._topology.setCurrentIndex(2)
        self._topology.currentIndexChanged.connect(self._topology_changed)

        def initial_value(name: str, default: float) -> float:
            if network is None:
                return default
            return float(getattr(network, name, default))

        self._series_l = QDoubleSpinBox(self)
        self._series_l.setRange(0.0, 1_000_000.0)
        self._series_l.setDecimals(3)
        self._series_l.setSuffix(" µH")
        self._series_l.setValue(initial_value("series_inductance_h", 1.0) * 1e6)

        self._series_c = QDoubleSpinBox(self)
        self._series_c.setRange(0.0, 1_000_000.0)
        self._series_c.setDecimals(3)
        self._series_c.setSuffix(" pF")
        self._series_c.setValue(initial_value("series_capacitance_f", 0.0) * 1e12)

        self._shunt_l = QDoubleSpinBox(self)
        self._shunt_l.setRange(0.0, 1_000_000.0)
        self._shunt_l.setDecimals(3)
        self._shunt_l.setSuffix(" µH")
        self._shunt_l.setValue(initial_value("shunt_inductance_h", 0.0) * 1e6)

        self._shunt_c = QDoubleSpinBox(self)
        self._shunt_c.setRange(0.0, 1_000_000.0)
        self._shunt_c.setDecimals(3)
        self._shunt_c.setSuffix(" pF")
        self._shunt_c.setValue(initial_value("shunt_capacitance_f", 100.0) * 1e12)

        self._shunt_at_input = QCheckBox(translator.t("matching_network.shunt_at_input"), self)
        self._shunt_at_input.setChecked(
            network.shunt_at_input if isinstance(network, LNetwork) else False
        )

        def spin(suffix: str) -> QDoubleSpinBox:
            box = QDoubleSpinBox(self)
            box.setRange(0.0, 1_000_000.0)
            box.setDecimals(3)
            box.setSuffix(suffix)
            return box

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

        self._load_r = QDoubleSpinBox(self)
        self._load_r.setRange(0.1, 100_000.0)
        self._load_r.setDecimals(3)
        self._load_r.setSuffix(" Ω")
        self._load_r.setValue(50.0)
        self._load_x = QDoubleSpinBox(self)
        self._load_x.setRange(-100_000.0, 100_000.0)
        self._load_x.setDecimals(3)
        self._load_x.setSuffix(" Ω")
        self._load_x.setValue(0.0)
        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(frequency_hz / 1_000_000.0)
        self._auto = QPushButton(translator.t("matching_network.auto_design"), self)
        self._auto.clicked.connect(self._auto_design)

        form = QFormLayout()
        form.addRow(translator.t("matching_network.topology"), self._topology)
        form.addRow(translator.t("matching_network.q_factor"), self._q_factor)
        form.addRow(translator.t("matching_network.load_r"), self._load_r)
        form.addRow(translator.t("matching_network.load_x"), self._load_x)
        form.addRow(translator.t("matching_network.frequency"), self._frequency)
        form.addRow("", self._auto)
        form.addRow(translator.t("matching_network.series_l"), self._series_l)
        form.addRow(translator.t("matching_network.series_c"), self._series_c)
        form.addRow(translator.t("matching_network.shunt_l"), self._shunt_l)
        form.addRow(translator.t("matching_network.shunt_c"), self._shunt_c)
        form.addRow("", self._shunt_at_input)
        form.addRow(translator.t("matching_network.input_shunt_l"), self._input_shunt_l)
        form.addRow(translator.t("matching_network.input_shunt_c"), self._input_shunt_c)
        form.addRow(translator.t("matching_network.output_shunt_l"), self._output_shunt_l)
        form.addRow(translator.t("matching_network.output_shunt_c"), self._output_shunt_c)
        form.addRow(translator.t("matching_network.input_series_l"), self._input_series_l)
        form.addRow(translator.t("matching_network.input_series_c"), self._input_series_c)
        form.addRow(translator.t("matching_network.output_series_l"), self._output_series_l)
        form.addRow(translator.t("matching_network.output_series_c"), self._output_series_c)

        hint = QLabel(translator.t("matching_network.hint"), self)
        hint.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._enabled)
        layout.addLayout(form)
        layout.addWidget(hint)
        layout.addStretch(1)
        layout.addWidget(buttons)
        self._update_controls()
        self._topology_changed()

    def _topology_changed(self, *_args: object) -> None:
        topology = self._topology.currentData()
        l_rows = topology == "l"
        pi_rows = topology == "pi"
        t_rows = topology == "t"
        for widget in (self._series_l, self._series_c, self._shunt_l, self._shunt_c):
            widget.setVisible(l_rows or pi_rows or t_rows)
        self._shunt_at_input.setVisible(l_rows)
        for widget in (
            self._input_shunt_l,
            self._input_shunt_c,
            self._output_shunt_l,
            self._output_shunt_c,
        ):
            widget.setVisible(pi_rows)
        for widget in (
            self._input_series_l,
            self._input_series_c,
            self._output_series_l,
            self._output_series_c,
        ):
            widget.setVisible(t_rows)
        self._auto.setVisible(l_rows)
        self._auto.setEnabled(l_rows)
        self._update_controls()

    def _auto_design(self) -> None:
        network = design_l_network(
            complex(self._load_r.value(), self._load_x.value()),
            self._frequency.value() * 1_000_000.0,
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
        for widget in (
            self._series_l,
            self._series_c,
            self._shunt_l,
            self._shunt_c,
            self._shunt_at_input,
            self._topology,
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

    def accept(self) -> None:
        try:
            self._network = self.network()
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

    def result_network(self) -> MatchingNetwork | None:
        return self._network
