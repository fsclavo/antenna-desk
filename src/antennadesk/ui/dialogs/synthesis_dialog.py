# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dialog for bounded feed-point impedance synthesis."""

from __future__ import annotations

import math
from dataclasses import replace

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...application.cancellation import EventCancelToken
from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.synthesize_antenna import SynthesizeAntennaCommand
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.antennas.j_pole import JPoleParameters
from ...domain.antennas.ocfd import OCFDParameters
from ...domain.optimization.synthesis import (
    SynthesisEvaluation,
    SynthesisResult,
    SynthesisTarget,
    SynthesisVariable,
    rank_evaluations,
)
from ...domain.simulation.spec import SimulationSpec
from ..i18n import Translator
from ..units import (
    UnitSystem,
    length_bounds,
    length_from_m,
    length_to_m,
    length_unit_key,
)
from ..workers.synthesis_worker import SynthesisWorker


class SynthesisDialog(QDialog):
    """Two-variable numerical starting point for OCFD and J-pole designs."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        solver: AntennaSolver,
        base_parameters: AntennaDesignParameters,
        base_spec: SimulationSpec,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if not isinstance(base_parameters, (OCFDParameters, JPoleParameters)):
            raise TypeError("synthesis supports OCFD, J Pole and Slim Jim designs")
        self._translator = translator
        self._unit_system = unit_system
        self._solver = solver
        self._base_parameters = base_parameters
        self._base_spec = base_spec
        self._thread: QThread | None = None
        self._worker: SynthesisWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._result: SynthesisResult | None = None
        self._selected_parameters: AntennaDesignParameters | None = None
        self._run_target: SynthesisTarget | None = None

        self._is_ocfd = isinstance(base_parameters, OCFDParameters)
        self._folded = isinstance(base_parameters, JPoleParameters) and base_parameters.folded
        self.setWindowTitle(translator.t("synthesis.title"))
        self.resize(1_000, 760)

        length_min, length_max = length_bounds(unit_system)
        scale = 1.0

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(base_parameters.frequency_hz / 1_000_000.0)

        self._target_r = QDoubleSpinBox(self)
        self._target_r.setRange(1.0, 10_000.0)
        self._target_r.setDecimals(3)
        self._target_r.setValue(50.0)
        self._target_r.setSuffix(" Ω")

        self._target_x = QDoubleSpinBox(self)
        self._target_x.setRange(-10_000.0, 10_000.0)
        self._target_x.setDecimals(3)
        self._target_x.setValue(0.0)
        self._target_x.setSuffix(" Ω")

        self._min_a = self._length_spin(length_min, length_max)
        self._max_a = self._length_spin(length_min, length_max)
        self._min_b = self._length_spin(length_min, length_max)
        self._max_b = self._length_spin(length_min, length_max)

        if self._is_ocfd:
            assert isinstance(base_parameters, OCFDParameters)
            center = base_parameters.total_length_m * scale
            self._set_length_pair(self._min_a, self._max_a, center, 0.85, 1.15)
            self._set_ratio_pair(self._min_b, self._max_b, base_parameters.feed_ratio)
            self._label_a_key = "field.length"
            self._label_b_key = "ocfd.feed_offset"
        else:
            assert isinstance(base_parameters, JPoleParameters)
            center = base_parameters.radiator_height_m * scale
            minimum = 0.85 * center
            if not self._folded:
                minimum = max(minimum, base_parameters.stub_length_m * 1.001)
            maximum = max(1.15 * center, minimum * 1.05)
            self._set_length_pair(self._min_a, self._max_a, center, 0.85, 1.15)
            self._min_a.setValue(length_from_m(minimum, unit_system))
            self._max_a.setValue(length_from_m(maximum, unit_system))
            if self._folded:
                self._set_length_pair(
                    self._min_b,
                    self._max_b,
                    base_parameters.stub_length_m * scale,
                    0.8,
                    1.2,
                )
                self._min_b.setValue(
                    max(
                        self._min_b.value(),
                        length_from_m(base_parameters.feed_offset_m + 0.01, unit_system),
                    )
                )
                self._label_a_key = "j_pole.radiator_height"
                self._label_b_key = "j_pole.stub_length"
            else:
                self._set_length_pair(
                    self._min_b,
                    self._max_b,
                    base_parameters.feed_offset_m * scale,
                    0.25,
                    3.0,
                )
                self._max_b.setValue(
                    min(
                        self._max_b.value(),
                        length_from_m(base_parameters.stub_length_m * 0.95, unit_system),
                    )
                )
                self._min_b.setValue(max(self._min_b.value(), length_from_m(0.01, unit_system)))
                self._label_a_key = "j_pole.radiator_height"
                self._label_b_key = "j_pole.feed_offset"

        self._max_evaluations = QSpinBox(self)
        self._max_evaluations.setRange(9, 225)
        self._max_evaluations.setValue(81)

        self._label_frequency = QLabel(translator.t("synthesis.target_frequency"), self)
        self._label_r = QLabel(translator.t("synthesis.target_resistance"), self)
        self._label_x = QLabel(translator.t("synthesis.target_reactance"), self)
        self._label_min_a = QLabel(translator.t("synthesis.minimum"), self)
        self._label_max_a = QLabel(translator.t("synthesis.maximum"), self)
        self._label_min_b = QLabel(translator.t("synthesis.minimum"), self)
        self._label_max_b = QLabel(translator.t("synthesis.maximum"), self)
        self._label_min_a.setText(
            f"{translator.t(self._label_a_key)} — {translator.t('synthesis.minimum')}"
        )
        self._label_max_a.setText(
            f"{translator.t(self._label_a_key)} — {translator.t('synthesis.maximum')}"
        )
        self._label_min_b.setText(
            f"{translator.t(self._label_b_key)} — {translator.t('synthesis.minimum')}"
        )
        self._label_max_b.setText(
            f"{translator.t(self._label_b_key)} — {translator.t('synthesis.maximum')}"
        )
        self._label_evaluations = QLabel(translator.t("optimize.max_evaluations"), self)
        self._transformer_note = QLabel(self)
        self._transformer_note.setWordWrap(True)

        form = QFormLayout()
        form.addRow(self._label_frequency, self._frequency)
        form.addRow(self._label_r, self._target_r)
        form.addRow(self._label_x, self._target_x)
        form.addRow(self._transformer_note)
        form.addRow(self._label_min_a, self._min_a)
        form.addRow(self._label_max_a, self._max_a)
        form.addRow(self._label_min_b, self._min_b)
        form.addRow(self._label_max_b, self._max_b)
        form.addRow(self._label_evaluations, self._max_evaluations)
        self._target_r.valueChanged.connect(self._update_transformer_note)
        self._update_transformer_note()

        self._evaluations = QTableWidget(0, 9, self)
        self._configure_table(self._evaluations)
        self._evaluations_label = QLabel(translator.t("optimize.evaluations"), self)

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._hint = QLabel(translator.t("synthesis.apply_hint"), self)
        self._hint.setWordWrap(True)

        self._run = QPushButton(translator.t("synthesis.run"), self)
        self._cancel = QPushButton(translator.t("optimize.cancel_run"), self)
        self._apply = QPushButton(translator.t("synthesis.apply"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._cancel.setEnabled(False)
        self._apply.setEnabled(False)
        self._run.clicked.connect(self._start)
        self._cancel.clicked.connect(self._cancel_run)
        self._apply.clicked.connect(self._apply_result)
        self._close.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(self._run)
        buttons.addWidget(self._cancel)
        buttons.addStretch(1)
        buttons.addWidget(self._apply)
        buttons.addWidget(self._close)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._evaluations_label)
        layout.addWidget(self._evaluations, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._hint)
        layout.addLayout(buttons)

        self._retranslate_table()
        self._update_controls()

    def _update_transformer_note(self) -> None:
        if not isinstance(self._base_parameters, OCFDParameters):
            self._transformer_note.setVisible(False)
            return
        ratio = self._base_parameters.transformer_ratio
        if ratio == 1.0:
            self._transformer_note.setVisible(False)
            return
        target = self._target_r.value()
        self._transformer_note.setText(
            self._translator.t(
                "synthesis.ocfd_transformer_note",
                ratio=f"{ratio:g}",
                target=f"{target:.1f}",
                antenna=f"{target * ratio:.1f}",
            )
        )
        self._transformer_note.setVisible(True)

    def _length_spin(self, minimum: float, maximum: float) -> QDoubleSpinBox:
        spin = QDoubleSpinBox(self)
        spin.setRange(minimum, maximum)
        spin.setDecimals(4)
        spin.setSuffix(f" {self._translator.t(length_unit_key(self._unit_system))}")
        return spin

    def _set_length_pair(
        self,
        minimum: QDoubleSpinBox,
        maximum: QDoubleSpinBox,
        center_m: float,
        low_factor: float,
        high_factor: float,
    ) -> None:
        minimum.setValue(length_from_m(center_m * low_factor, self._unit_system))
        maximum.setValue(length_from_m(center_m * high_factor, self._unit_system))

    def _set_ratio_pair(
        self,
        minimum: QDoubleSpinBox,
        maximum: QDoubleSpinBox,
        ratio: float,
    ) -> None:
        for spin in (minimum, maximum):
            spin.setRange(1.0, 99.0)
            spin.setDecimals(2)
            spin.setSuffix(" %")
        minimum.setValue(5.0)
        maximum.setValue(90.0)
        if not 5.0 <= ratio * 100.0 <= 90.0:
            minimum.setValue(1.0)
            maximum.setValue(99.0)

    @staticmethod
    def _configure_table(table: QTableWidget) -> None:
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(220)
        table.horizontalHeader().setStretchLastSection(True)

    def _retranslate_table(self) -> None:
        t = self._translator.t
        self._evaluations.setHorizontalHeaderLabels(
            [
                t("optimize.rank"),
                t("optimize.iteration"),
                t(self._label_a_key),
                t(self._label_b_key),
                t("table.resistance"),
                t("table.reactance"),
                t("table.swr"),
                t("synthesis.impedance_error"),
                t("optimize.message"),
            ]
        )

    def _variables(self) -> tuple[SynthesisVariable, ...]:
        if self._is_ocfd:
            a = "length_m"
            b = "feed_ratio"
            min_a = length_to_m(self._min_a.value(), self._unit_system)
            max_a = length_to_m(self._max_a.value(), self._unit_system)
            min_b = self._min_b.value() / 100.0
            max_b = self._max_b.value() / 100.0
        else:
            a = "radiator_height_m"
            b = "stub_length_m" if self._folded else "feed_offset_m"
            min_a = length_to_m(self._min_a.value(), self._unit_system)
            max_a = length_to_m(self._max_a.value(), self._unit_system)
            min_b = length_to_m(self._min_b.value(), self._unit_system)
            max_b = length_to_m(self._max_b.value(), self._unit_system)
        return (
            SynthesisVariable(a, min_a, max_a),
            SynthesisVariable(b, min_b, max_b),
        )

    def _build_parameters(self, values: dict[str, float]) -> AntennaDesignParameters:
        frequency_hz = self._frequency.value() * 1_000_000.0
        if isinstance(self._base_parameters, OCFDParameters):
            return replace(
                self._base_parameters,
                frequency_hz=frequency_hz,
                total_length_m=values["length_m"],
                feed_ratio=values["feed_ratio"],
            )
        assert isinstance(self._base_parameters, JPoleParameters)
        if self._folded:
            return replace(
                self._base_parameters,
                frequency_hz=frequency_hz,
                radiator_height_m=values["radiator_height_m"],
                stub_length_m=values["stub_length_m"],
            )
        return replace(
            self._base_parameters,
            frequency_hz=frequency_hz,
            radiator_height_m=values["radiator_height_m"],
            feed_offset_m=values["feed_offset_m"],
        )

    def _target(self) -> SynthesisTarget:
        return SynthesisTarget(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            resistance_ohm=self._target_r.value(),
            reactance_ohm=self._target_x.value(),
        )

    def _start(self) -> None:
        if self._thread is not None:
            return
        try:
            variables = self._variables()
            target = self._target()
        except ValueError as exc:
            QMessageBox.critical(self, self._translator.t("synthesis.title"), str(exc))
            return
        self._result = None
        self._selected_parameters = None
        self._run_target = target
        self._evaluations.setRowCount(0)
        self._summary.setText(self._translator.t("synthesis.running"))
        self._apply.setEnabled(False)
        self._cancel_token = EventCancelToken()
        command = SynthesizeAntennaCommand(
            build_parameters=lambda values: self._build_parameters(dict(values)),
            variables=variables,
            target=target,
            base_spec=self._base_spec,
            max_evaluations=self._max_evaluations.value(),
            cancel_token=self._cancel_token,
        )
        thread = QThread(self)
        worker = SynthesisWorker(self._solver, command)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_thread_finished)
        self._thread = thread
        self._worker = worker
        self._update_controls()
        thread.start()

    def _cancel_run(self) -> None:
        if self._cancel_token is not None:
            self._cancel_token.cancel()
            self._summary.setText(self._translator.t("synthesis.running"))
            self._cancel.setEnabled(False)

    def _on_finished(self, result: SynthesisResult) -> None:
        self._result = result
        self._populate_evaluations(result.evaluations)
        self._summary.setText(self._summary_text(result))
        if result.best_values is not None:
            self._selected_parameters = self._build_parameters(dict(result.best_values))
        self._apply.setEnabled(self._selected_parameters is not None)

    def _on_failed(self, message: str) -> None:
        self._summary.setText(self._translator.t("synthesis.error", message=message))
        QMessageBox.critical(
            self,
            self._translator.t("synthesis.title"),
            self._translator.t("synthesis.error", message=message),
        )

    def _on_thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._cancel_token = None
        self._update_controls()

    def _update_controls(self) -> None:
        running = self._thread is not None
        for widget in (
            self._frequency,
            self._target_r,
            self._target_x,
            self._min_a,
            self._max_a,
            self._min_b,
            self._max_b,
            self._max_evaluations,
        ):
            widget.setEnabled(not running)
        self._run.setEnabled(not running)
        self._cancel.setEnabled(running)
        self._close.setEnabled(not running)
        if running:
            self._apply.setEnabled(False)

    def _value_a(self, value: float) -> str:
        if self._is_ocfd:
            return self._length_display(value)
        return self._length_display(value)

    def _value_b(self, value: float) -> str:
        if self._is_ocfd:
            return f"{value * 100.0:.2f} %"
        return self._length_display(value)

    def _length_display(self, value_m: float) -> str:
        value = length_from_m(value_m, self._unit_system)
        unit = self._translator.t(length_unit_key(self._unit_system))
        return f"{value:.4f} {unit}"

    def _populate_evaluations(self, evaluations: tuple[SynthesisEvaluation, ...]) -> None:
        ordered = (
            rank_evaluations(evaluations, self._run_target)
            if self._run_target is not None
            else evaluations
        )
        self._evaluations.setRowCount(len(ordered))
        for row, evaluation in enumerate(ordered):
            a = evaluation.values.get("length_m")
            if a is None:
                a = evaluation.values.get("radiator_height_m")
            b = evaluation.values.get("feed_ratio")
            if b is None:
                b = evaluation.values.get("stub_length_m")
            if b is None:
                b = evaluation.values.get("feed_offset_m")
            impedance = evaluation.impedance_ohm
            error = (
                abs(impedance - self._run_target.impedance_ohm)
                if impedance is not None and self._run_target is not None
                else None
            )
            values = [
                str(row + 1),
                str(evaluation.index),
                self._value_a(a) if a is not None else "—",
                self._value_b(b) if b is not None else "—",
                f"{impedance.real:.3f}" if impedance is not None else "—",
                f"{impedance.imag:+.3f}" if impedance is not None else "—",
                (
                    "∞"
                    if evaluation.swr is not None and math.isinf(evaluation.swr)
                    else (f"{evaluation.swr:.3f}" if evaluation.swr is not None else "—")
                ),
                f"{error:.3f}" if error is not None else "—",
                evaluation.error or "",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {4, 5, 6, 7}:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self._evaluations.setItem(row, column, item)
        self._evaluations.resizeColumnsToContents()
        self._evaluations.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)

    def _summary_text(self, result: SynthesisResult) -> str:
        status = self._translator.t(f"optimize_status.{result.status.value}")
        if result.best_values is None or result.best_impedance_ohm is None:
            text = self._translator.t("synthesis.no_best", status=status)
        else:
            a = result.best_values.get("length_m")
            if a is None:
                a = result.best_values.get("radiator_height_m")
            b = result.best_values.get("feed_ratio")
            if b is None:
                b = result.best_values.get("stub_length_m")
            if b is None:
                b = result.best_values.get("feed_offset_m")
            impedance = result.best_impedance_ohm
            swr = (
                "∞"
                if result.best_swr is not None and math.isinf(result.best_swr)
                else (f"{result.best_swr:.3f}" if result.best_swr is not None else "—")
            )
            text = self._translator.t(
                "synthesis.summary",
                status=status,
                a=self._value_a(a) if a is not None else "—",
                b=self._value_b(b) if b is not None else "—",
                resistance=f"{impedance.real:.3f}",
                reactance=f"{impedance.imag:+.3f}",
                swr=swr,
                error=(
                    f"{result.best_error_ohm:.3f}" if result.best_error_ohm is not None else "—"
                ),
            )
        return text

    def _apply_result(self) -> None:
        if self._selected_parameters is None:
            return
        self.accept()

    def selected_parameters(self) -> AntennaDesignParameters | None:
        return self._selected_parameters

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None:
            if self._cancel_token is not None:
                self._cancel_token.cancel()
            QMessageBox.information(
                self,
                self._translator.t("synthesis.title"),
                self._translator.t("synthesis.close_synthesis"),
            )
            event.ignore()
            return
        super().closeEvent(event)
