# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only tuner matchability table for the current simulation result."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.design.smith_chart import MatchingPreviewTopology
from ...domain.design.tuner import (
    TunerLimits,
    evaluate_tuner_match,
)
from ...domain.simulation.bands import AMATEUR_BANDS, amateur_band_for
from ...domain.simulation.result import FrequencyResult, SimulationResult
from ..fonts import scaled_dialog_size
from ..help import apply_row_help
from ..i18n import Translator


class TunerMatchDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        result: SimulationResult,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._result = result
        self.setWindowTitle(translator.t("tuner.title"))
        self.resize(*scaled_dialog_size(900, 520))

        self._topology = QComboBox(self)
        for key, value in (
            ("smith.match.l", MatchingPreviewTopology.L.value),
            ("smith.match.pi", MatchingPreviewTopology.PI.value),
            ("smith.match.t", MatchingPreviewTopology.T.value),
        ):
            self._topology.addItem(translator.t(key), value)
        self._rows = QComboBox(self)
        for key, value in (
            ("tuner.rows.frequencies", "frequencies"),
            ("tuner.rows.bands", "bands"),
        ):
            self._rows.addItem(translator.t(key), value)
        self._series = QComboBox(self)
        for key, value in (
            ("tuner.series_ideal", "ideal"),
            ("tuner.series_e12", "e12"),
            ("tuner.series_e24", "e24"),
        ):
            self._series.addItem(translator.t(key), value)
        self._q = QDoubleSpinBox(self)
        self._q.setRange(0.0, 100.0)
        self._q.setDecimals(2)
        self._q.setSingleStep(0.5)
        self._q.setValue(0.0)
        self._q.setSuffix(" Q")
        self._power = QDoubleSpinBox(self)
        self._power.setRange(1.0, 10_000.0)
        self._power.setDecimals(0)
        self._power.setValue(100.0)
        self._power.setSuffix(" W")
        self._c_min = self._component_spin(1.0, 100_000.0, 5.0, "pf")
        self._c_max = self._component_spin(1.0, 100_000.0, 1_000.0, "pf")
        self._l_min = self._component_spin(0.01, 10_000.0, 0.1, "uh")
        self._l_max = self._component_spin(0.01, 10_000.0, 100.0, "uh")

        form = QFormLayout()
        form.addRow(QLabel(translator.t("tuner.topology"), self), self._topology)
        form.addRow(QLabel(translator.t("tuner.rows"), self), self._rows)
        form.addRow(QLabel(translator.t("tuner.series"), self), self._series)
        form.addRow(QLabel(translator.t("tuner.q"), self), self._q)
        form.addRow(QLabel(translator.t("tuner.power"), self), self._power)
        form.addRow(QLabel(translator.t("tuner.c_min"), self), self._c_min)
        form.addRow(QLabel(translator.t("tuner.c_max"), self), self._c_max)
        form.addRow(QLabel(translator.t("tuner.l_min"), self), self._l_min)
        form.addRow(QLabel(translator.t("tuner.l_max"), self), self._l_max)
        for row, key in enumerate(
            (
                "tuner.topology",
                "tuner.rows",
                "tuner.series",
                "tuner.q",
                "tuner.power",
                "tuner.c_min",
                "tuner.c_max",
                "tuner.l_min",
                "tuner.l_max",
            )
        ):
            apply_row_help(form, row, translator, key)

        self._note = QLabel(translator.t("tuner.note"), self)
        self._note.setWordWrap(True)
        self._error = QLabel(self)
        self._error.setWordWrap(True)
        self._error.setStyleSheet("color: #b00020;")
        self._recompute_button = QPushButton(translator.t("tuner.recompute"), self)
        self._recompute_button.clicked.connect(self._recompute)
        controls = QHBoxLayout()
        controls.addWidget(self._recompute_button)
        controls.addStretch(1)

        self._table = QTableWidget(0, 12, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._note)
        layout.addWidget(self._error)
        layout.addLayout(controls)
        layout.addWidget(self._table, 1)
        layout.addWidget(buttons)
        self._retranslate()
        self._recompute()

    def _component_spin(
        self,
        minimum: float,
        maximum: float,
        value: float,
        unit: str,
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox(self)
        spin.setRange(minimum, maximum)
        spin.setDecimals(3)
        spin.setValue(value)
        spin.setSuffix(f" {self._translator.t(f'smith.unit_{unit}')}")
        return spin

    def _recompute(self) -> None:
        self._error.clear()
        try:
            limits = TunerLimits(
                capacitance_min_f=self._c_min.value() * 1e-12,
                capacitance_max_f=self._c_max.value() * 1e-12,
                inductance_min_h=self._l_min.value() * 1e-6,
                inductance_max_h=self._l_max.value() * 1e-6,
            )
        except ValueError as exc:
            self._error.setText(str(exc))
            self._table.setRowCount(0)
            return
        topology = self._topology.currentData() or MatchingPreviewTopology.L.value
        series = self._series.currentData() or "ideal"
        q = self._q.value()
        rows = []
        if self._rows.currentData() == "bands":
            lowest = min(frequency.frequency_hz for frequency in self._result.frequencies)
            highest = max(frequency.frequency_hz for frequency in self._result.frequencies)
            for band in AMATEUR_BANDS:
                if band.stop_hz < lowest or band.start_hz > highest:
                    continue
                nearest = min(
                    self._result.frequencies,
                    key=lambda frequency: abs(frequency.frequency_hz - band.center_hz),
                )
                load = (
                    nearest.source_results[0].impedance_ohm
                    if nearest.source_results
                    else nearest.impedance_ohm
                )
                evaluation = evaluate_tuner_match(
                    load,
                    band.center_hz,
                    limits,
                    topology,
                    source_impedance_ohm=self._result.spec.reference_impedance_ohm,
                    loaded_q=q if q > 0.0 else None,
                    series=series if isinstance(series, str) else "ideal",
                    power_w=self._power.value(),
                )
                rows.append(
                    (
                        FrequencyResult(
                            band.center_hz,
                            nearest.feed_tag,
                            nearest.feed_segment,
                            load,
                            nearest.swr,
                            nearest.input_power_w,
                        ),
                        load,
                        evaluation,
                        band.name,
                    )
                )
        else:
            for frequency in self._result.frequencies:
                load = (
                    frequency.source_results[0].impedance_ohm
                    if frequency.source_results
                    else frequency.impedance_ohm
                )
                evaluation = evaluate_tuner_match(
                    load,
                    frequency.frequency_hz,
                    limits,
                    topology,
                    source_impedance_ohm=self._result.spec.reference_impedance_ohm,
                    loaded_q=q if q > 0.0 else None,
                    series=series if isinstance(series, str) else "ideal",
                    power_w=self._power.value(),
                )
                band_match = amateur_band_for(frequency.frequency_hz)
                rows.append((frequency, load, evaluation, band_match.name if band_match else ""))
        self._table.setRowCount(len(rows))
        for row, (frequency, load, evaluation, band_name) in enumerate(rows):
            values = (
                f"{frequency.frequency_hz / 1e6:.6f}",
                band_name,
                f"{load.real:.3f}",
                f"{load.imag:+.3f}",
                self._translator.t(f"tuner.status.{evaluation.status.value}"),
                "—" if evaluation.swr is None else f"{evaluation.swr:.3f}",
                "—" if evaluation.loss_db is None else f"{evaluation.loss_db:.3f}",
                (
                    "—"
                    if evaluation.limiting is None
                    else self._translator.t(f"tuner.limit.{evaluation.limiting}")
                ),
                "—" if evaluation.input_voltage_v is None else f"{evaluation.input_voltage_v:.1f}",
                "—" if evaluation.input_current_a is None else f"{evaluation.input_current_a:.3f}",
                "—" if evaluation.load_voltage_v is None else f"{evaluation.load_voltage_v:.1f}",
                "—" if evaluation.load_current_a is None else f"{evaluation.load_current_a:.3f}",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._table.setItem(row, column, item)
        self._table.resizeColumnsToContents()

    def _retranslate(self) -> None:
        self.setWindowTitle(self._translator.t("tuner.title"))
        self._recompute_button.setText(self._translator.t("tuner.recompute"))
        self._note.setText(self._translator.t("tuner.note"))
        self._rows.setItemText(0, self._translator.t("tuner.rows.frequencies"))
        self._rows.setItemText(1, self._translator.t("tuner.rows.bands"))
        self._table.setHorizontalHeaderLabels(
            [
                self._translator.t("tuner.column.frequency"),
                self._translator.t("tuner.column.band"),
                self._translator.t("tuner.column.resistance"),
                self._translator.t("tuner.column.reactance"),
                self._translator.t("tuner.column.status"),
                self._translator.t("tuner.column.swr"),
                self._translator.t("tuner.column.loss"),
                self._translator.t("tuner.column.limiting"),
                self._translator.t("tuner.column.input_voltage"),
                self._translator.t("tuner.column.input_current"),
                self._translator.t("tuner.column.load_voltage"),
                self._translator.t("tuner.column.load_current"),
            ]
        )
