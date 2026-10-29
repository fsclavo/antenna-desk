# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dialog for bounded antenna-dimension optimization."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QComboBox,
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
from ...application.use_cases.optimize_dipole_length import (
    OptimizeAntennaDimensionCommand,
)
from ...domain.antennas.design import (
    AntennaDesignParameters,
    primary_dimension_m,
)
from ...domain.optimization.length import (
    LengthEvaluation,
    LengthOptimizationResult,
    LengthOptimizationSpec,
    OptimizationObjective,
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
from ..workers.optimization_worker import OptimizationWorker


class OptimizationDialog(QDialog):
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
        self._translator = translator
        self._unit_system = unit_system
        self._solver = solver
        self._base_parameters = base_parameters
        self._base_spec = base_spec
        self._thread: QThread | None = None
        self._worker: OptimizationWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._result: LengthOptimizationResult | None = None
        self._selected_length_m: float | None = None

        self.setWindowTitle(translator.t("optimize.title"))
        self.resize(960, 820)

        unit = translator.t(length_unit_key(unit_system))
        length_min, length_max = length_bounds(unit_system)
        base_dimension_m = primary_dimension_m(base_parameters)
        default_min = max(base_dimension_m * 0.9, 0.5)
        default_max = max(base_dimension_m * 1.1, default_min + 0.5)

        self._objective = QComboBox(self)
        self._objective.addItem("", OptimizationObjective.REACTANCE.value)
        self._objective.addItem("", OptimizationObjective.MIN_SWR.value)
        self._objective.addItem("", OptimizationObjective.MAX_BANDWIDTH.value)
        self._objective.currentIndexChanged.connect(self._objective_changed)

        self._min_length = QDoubleSpinBox(self)
        self._min_length.setRange(length_min, length_max)
        self._min_length.setDecimals(3)
        self._min_length.setSuffix(f" {unit}")
        self._min_length.setValue(length_from_m(default_min, unit_system))

        self._max_length = QDoubleSpinBox(self)
        self._max_length.setRange(length_min, length_max)
        self._max_length.setDecimals(3)
        self._max_length.setSuffix(f" {unit}")
        self._max_length.setValue(length_from_m(default_max, unit_system))

        self._target = QDoubleSpinBox(self)
        self._target.setRange(-1_000.0, 1_000.0)
        self._target.setDecimals(2)
        self._target.setValue(0.0)
        self._target.setSuffix(" Ω")

        self._swr_limit = QDoubleSpinBox(self)
        self._swr_limit.setRange(1.01, 10.0)
        self._swr_limit.setDecimals(2)
        self._swr_limit.setValue(2.0)

        self._max_evaluations = QSpinBox(self)
        self._max_evaluations.setRange(3, 50)
        self._max_evaluations.setValue(12)

        self._tolerance = QDoubleSpinBox(self)
        self._tolerance.setRange(0.001, 100.0)
        self._tolerance.setDecimals(3)
        self._tolerance.setValue(0.1)
        self._tolerance.setSuffix(" Ω")

        self._label_objective = QLabel(translator.t("optimize.objective"), self)
        self._label_min = QLabel(translator.t("optimize.min_length"), self)
        self._label_max = QLabel(translator.t("optimize.max_length"), self)
        self._label_target = QLabel(translator.t("optimize.target_reactance"), self)
        self._label_swr_limit = QLabel(translator.t("optimize.swr_limit"), self)
        self._label_evaluations = QLabel(translator.t("optimize.max_evaluations"), self)
        self._label_tolerance = QLabel(translator.t("optimize.tolerance"), self)
        self._form_layout = QFormLayout()
        self._form_layout.addRow(self._label_objective, self._objective)
        self._form_layout.addRow(self._label_min, self._min_length)
        self._form_layout.addRow(self._label_max, self._max_length)
        self._form_layout.addRow(self._label_target, self._target)
        self._form_layout.addRow(self._label_swr_limit, self._swr_limit)
        self._form_layout.addRow(self._label_evaluations, self._max_evaluations)
        self._form_layout.addRow(self._label_tolerance, self._tolerance)

        self._evaluations_label = QLabel(translator.t("optimize.evaluations"), self)
        self._evaluations = QTableWidget(0, 8, self)
        self._configure_table(self._evaluations)
        self._evaluations.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        self._sensitivity_label = QLabel(translator.t("optimize.sensitivity"), self)
        self._sensitivity = QTableWidget(0, 6, self)
        self._configure_table(self._sensitivity)
        self._sensitivity.horizontalHeader().setStretchLastSection(True)

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._hint = QLabel(translator.t("optimize.apply_hint"), self)
        self._hint.setWordWrap(True)

        self._run = QPushButton(translator.t("optimize.run"), self)
        self._cancel = QPushButton(translator.t("optimize.cancel_run"), self)
        self._apply = QPushButton(translator.t("optimize.apply"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._cancel.setEnabled(False)
        self._apply.setEnabled(False)
        self._run.clicked.connect(self._start)
        self._cancel.clicked.connect(self._cancel_run)
        self._apply.clicked.connect(self._apply_length)
        self._close.clicked.connect(self.reject)

        buttons = QHBoxLayout()
        buttons.addWidget(self._run)
        buttons.addWidget(self._cancel)
        buttons.addStretch(1)
        buttons.addWidget(self._apply)
        buttons.addWidget(self._close)

        layout = QVBoxLayout(self)
        layout.addLayout(self._form_layout)
        layout.addWidget(self._evaluations_label)
        layout.addWidget(self._evaluations, 1)
        layout.addWidget(self._sensitivity_label)
        layout.addWidget(self._sensitivity, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._hint)
        layout.addLayout(buttons)

        self._retranslate_tables()
        self._objective_changed()
        self._update_controls()

    @staticmethod
    def _configure_table(table: QTableWidget) -> None:
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.setMinimumHeight(150)

    def _retranslate_tables(self) -> None:
        t = self._translator.t
        self._label_objective.setText(t("optimize.objective"))
        self._objective.setItemText(0, t("optimize.reactance_objective"))
        self._objective.setItemText(1, t("optimize.min_swr_objective"))
        self._objective.setItemText(2, t("optimize.max_bandwidth_objective"))
        self._evaluations.setHorizontalHeaderLabels(
            [
                t("optimize.iteration"),
                t("optimize.length"),
                t("table.resistance"),
                t("table.reactance"),
                t("table.impedance"),
                t("table.swr"),
                t("optimize.bandwidth"),
                t("optimize.message"),
            ]
        )
        self._sensitivity.setHorizontalHeaderLabels(
            [
                t("optimize.offset"),
                t("optimize.length"),
                t("table.resistance"),
                t("table.reactance"),
                t("table.swr"),
                t("optimize.bandwidth"),
            ]
        )

    def _length_display(self, length_m: float) -> str:
        value = length_from_m(length_m, self._unit_system)
        unit = self._translator.t(length_unit_key(self._unit_system))
        return f"{value:.3f} {unit}"

    def _offset_display(self, offset_m: float) -> str:
        value = length_from_m(offset_m, self._unit_system)
        unit = self._translator.t(length_unit_key(self._unit_system))
        return f"{value:+.3f} {unit}"

    def _objective_value(self) -> OptimizationObjective:
        return OptimizationObjective(self._objective.currentData())

    def _set_row_visible(self, field: QWidget, visible: bool) -> None:
        label = self._form_layout.labelForField(field)
        if label is not None:
            label.setVisible(visible)
        field.setVisible(visible)

    def _objective_changed(self) -> None:
        objective = self._objective_value()
        is_swr = objective is OptimizationObjective.MIN_SWR
        is_bandwidth = objective is OptimizationObjective.MAX_BANDWIDTH
        self._target.setVisible(objective is OptimizationObjective.REACTANCE)
        self._label_target.setVisible(objective is OptimizationObjective.REACTANCE)
        self._swr_limit.setVisible(is_bandwidth)
        self._label_swr_limit.setVisible(is_bandwidth)
        self._set_row_visible(self._tolerance, not is_bandwidth)
        if is_bandwidth and self._max_evaluations.value() < 21:
            self._max_evaluations.setValue(41)
        if is_swr:
            self._label_tolerance.setText(self._translator.t("optimize.swr_tolerance"))
            self._tolerance.setDecimals(3)
            self._tolerance.setValue(0.05)
            self._tolerance.setSuffix("")
        else:
            self._label_tolerance.setText(self._translator.t("optimize.tolerance"))
            self._tolerance.setDecimals(3)
            self._tolerance.setValue(0.1)
            self._tolerance.setSuffix(" Ω")

    def _optimization_spec(self) -> LengthOptimizationSpec:
        objective = self._objective_value()
        return LengthOptimizationSpec(
            min_length_m=length_to_m(self._min_length.value(), self._unit_system),
            max_length_m=length_to_m(self._max_length.value(), self._unit_system),
            objective=objective,
            target_reactance_ohm=self._target.value(),
            max_evaluations=self._max_evaluations.value(),
            reactance_tolerance_ohm=self._tolerance.value(),
            swr_tolerance=self._tolerance.value(),
            swr_limit=self._swr_limit.value(),
        )

    def _start(self) -> None:
        if self._thread is not None:
            return
        if (
            self._objective_value() is OptimizationObjective.MAX_BANDWIDTH
            and self._base_spec.frequency_plan.count < 2
        ):
            QMessageBox.critical(
                self,
                self._translator.t("optimize.title"),
                self._translator.t("optimize.bandwidth_needs_sweep"),
            )
            return
        try:
            spec = self._optimization_spec()
        except ValueError as exc:
            QMessageBox.critical(
                self,
                self._translator.t("optimize.title"),
                str(exc),
            )
            return

        self._result = None
        self._selected_length_m = None
        self._evaluations.setRowCount(0)
        self._sensitivity.setRowCount(0)
        self._summary.setText(self._translator.t("optimize.running"))
        self._apply.setEnabled(False)
        self._cancel_token = EventCancelToken()
        command = OptimizeAntennaDimensionCommand(
            parameters=self._base_parameters,
            base_spec=self._base_spec,
            optimization_spec=spec,
            cancel_token=self._cancel_token,
        )
        thread = QThread(self)
        worker = OptimizationWorker(self._solver, command)
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
            self._summary.setText(self._translator.t("optimize.running"))
            self._cancel.setEnabled(False)

    def _on_finished(self, result: LengthOptimizationResult) -> None:
        self._result = result
        self._selected_length_m = result.best_length_m
        self._populate_evaluations(result.evaluations)
        self._populate_sensitivity(result)
        self._summary.setText(self._summary_text(result))
        self._apply.setEnabled(result.best_length_m is not None)

    def _on_failed(self, message: str) -> None:
        self._summary.setText(self._translator.t("error.optimize", message=message))
        QMessageBox.critical(
            self,
            self._translator.t("optimize.title"),
            self._translator.t("error.optimize", message=message),
        )

    def _on_thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._cancel_token = None
        self._update_controls()

    def _update_controls(self) -> None:
        running = self._thread is not None
        for widget in (
            self._objective,
            self._min_length,
            self._max_length,
            self._target,
            self._swr_limit,
            self._max_evaluations,
            self._tolerance,
        ):
            widget.setEnabled(not running)
        self._run.setEnabled(not running)
        self._cancel.setEnabled(running)
        self._close.setEnabled(not running)
        if running:
            self._apply.setEnabled(False)

    def _populate_evaluations(self, evaluations: tuple[LengthEvaluation, ...]) -> None:
        self._evaluations.setRowCount(len(evaluations))
        for row, evaluation in enumerate(evaluations):
            values = [
                str(evaluation.index),
                self._length_display(evaluation.length_m),
                (
                    f"{evaluation.impedance_ohm.real:.3f}"
                    if evaluation.impedance_ohm is not None
                    else "—"
                ),
                (
                    f"{evaluation.impedance_ohm.imag:+.3f}"
                    if evaluation.impedance_ohm is not None
                    else "—"
                ),
                (
                    f"{abs(evaluation.impedance_ohm):.3f}"
                    if evaluation.impedance_ohm is not None
                    else "—"
                ),
                (
                    "∞"
                    if evaluation.swr is not None and math.isinf(evaluation.swr)
                    else (f"{evaluation.swr:.3f}" if evaluation.swr is not None else "—")
                ),
                (
                    f"{evaluation.bandwidth_hz / 1e6:.3f}"
                    if evaluation.bandwidth_hz is not None
                    else "—"
                ),
                evaluation.error or "",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {2, 3, 4, 5, 6}:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self._evaluations.setItem(row, column, item)
        self._evaluations.resizeColumnsToContents()
        self._evaluations.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

    def _populate_sensitivity(self, result: LengthOptimizationResult) -> None:
        self._sensitivity.setRowCount(len(result.sensitivity))
        for row, point in enumerate(result.sensitivity):
            values = [
                self._offset_display(point.offset_m),
                self._length_display(point.length_m),
                (f"{point.impedance_ohm.real:.3f}" if point.impedance_ohm is not None else "—"),
                (f"{point.impedance_ohm.imag:+.3f}" if point.impedance_ohm is not None else "—"),
                (
                    "∞"
                    if point.swr is not None and math.isinf(point.swr)
                    else (f"{point.swr:.3f}" if point.swr is not None else "—")
                ),
                (f"{point.bandwidth_hz / 1e6:.3f}" if point.bandwidth_hz is not None else "—"),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {2, 3, 4, 5}:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self._sensitivity.setItem(row, column, item)
        self._sensitivity.resizeColumnsToContents()

    def _summary_text(self, result: LengthOptimizationResult) -> str:
        status = self._translator.t(f"optimize_status.{result.status.value}")
        if result.best_length_m is None:
            text = self._translator.t("optimize.no_best")
        else:
            reactance = (
                f"{result.best_impedance_ohm.imag:+.3f}"
                if result.best_impedance_ohm is not None
                else "—"
            )
            swr = (
                "∞"
                if result.best_swr is not None and math.isinf(result.best_swr)
                else (f"{result.best_swr:.3f}" if result.best_swr is not None else "—")
            )
            text = self._translator.t(
                "optimize.summary",
                status=status,
                length=self._length_display(result.best_length_m),
                reactance=reactance,
                swr=swr,
            )
            if result.best_bandwidth_hz is not None:
                text = (
                    text
                    + " · "
                    + self._translator.t(
                        "optimize.bandwidth_result",
                        value=f"{result.best_bandwidth_hz / 1e6:.3f}",
                    )
                )
        if result.message:
            text = f"{text} · {result.message}"
        return text

    def _apply_length(self) -> None:
        if self._selected_length_m is None:
            return
        self.accept()

    def selected_dimension_m(self) -> float | None:
        return self._selected_length_m

    def selected_length_m(self) -> float | None:
        return self._selected_length_m

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None:
            if self._cancel_token is not None:
                self._cancel_token.cancel()
            QMessageBox.information(
                self,
                self._translator.t("optimize.title"),
                self._translator.t("optimize.close_optimization"),
            )
            event.ignore()
            return
        super().closeEvent(event)
