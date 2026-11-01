# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Ideal L-network configuration dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.matching_network import LNetwork
from ..i18n import Translator


class MatchingNetworkDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        network: LNetwork | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._network = network
        self.setWindowTitle(translator.t("matching_network.title"))
        self.resize(460, 360)

        self._enabled = QCheckBox(translator.t("matching_network.enabled"), self)
        self._enabled.setChecked(network is not None)
        self._enabled.toggled.connect(self._update_controls)

        self._series_l = QDoubleSpinBox(self)
        self._series_l.setRange(0.0, 1_000_000.0)
        self._series_l.setDecimals(3)
        self._series_l.setSuffix(" µH")
        self._series_l.setValue((network.series_inductance_h * 1e6) if network else 1.0)

        self._series_c = QDoubleSpinBox(self)
        self._series_c.setRange(0.0, 1_000_000.0)
        self._series_c.setDecimals(3)
        self._series_c.setSuffix(" pF")
        self._series_c.setValue((network.series_capacitance_f * 1e12) if network else 0.0)

        self._shunt_l = QDoubleSpinBox(self)
        self._shunt_l.setRange(0.0, 1_000_000.0)
        self._shunt_l.setDecimals(3)
        self._shunt_l.setSuffix(" µH")
        self._shunt_l.setValue((network.shunt_inductance_h * 1e6) if network else 0.0)

        self._shunt_c = QDoubleSpinBox(self)
        self._shunt_c.setRange(0.0, 1_000_000.0)
        self._shunt_c.setDecimals(3)
        self._shunt_c.setSuffix(" pF")
        self._shunt_c.setValue((network.shunt_capacitance_f * 1e12) if network else 100.0)

        self._shunt_at_input = QCheckBox(translator.t("matching_network.shunt_at_input"), self)
        self._shunt_at_input.setChecked(network.shunt_at_input if network else False)

        form = QFormLayout()
        form.addRow(translator.t("matching_network.series_l"), self._series_l)
        form.addRow(translator.t("matching_network.series_c"), self._series_c)
        form.addRow(translator.t("matching_network.shunt_l"), self._shunt_l)
        form.addRow(translator.t("matching_network.shunt_c"), self._shunt_c)
        form.addRow("", self._shunt_at_input)

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

    def _update_controls(self) -> None:
        enabled = self._enabled.isChecked()
        for widget in (
            self._series_l,
            self._series_c,
            self._shunt_l,
            self._shunt_c,
            self._shunt_at_input,
        ):
            widget.setEnabled(enabled)

    def accept(self) -> None:
        try:
            self._network = self.network()
        except ValueError as exc:
            QMessageBox.critical(self, self._translator.t("matching_network.title"), str(exc))
            return
        super().accept()

    def network(self) -> LNetwork | None:
        if not self._enabled.isChecked():
            return None
        return LNetwork(
            series_inductance_h=self._series_l.value() * 1e-6,
            series_capacitance_f=self._series_c.value() * 1e-12,
            shunt_inductance_h=self._shunt_l.value() * 1e-6,
            shunt_capacitance_f=self._shunt_c.value() * 1e-12,
            shunt_at_input=self._shunt_at_input.isChecked(),
        )

    def result_network(self) -> LNetwork | None:
        return self._network
