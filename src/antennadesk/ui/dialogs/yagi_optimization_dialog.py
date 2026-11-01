# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dialog for bounded multi-element Yagi length and spacing optimization."""

from __future__ import annotations

from dataclasses import replace

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
from ...application.use_cases.optimize_yagi_elements import (
    OptimizeYagiElementsCommand,
    YagiOptimizationObjective,
)
from ...domain.antennas.yagi import YagiParameters
from ...domain.optimization.multi_variable import (
    BoundedResult,
    BoundedVariable,
    rank_bounded,
)
from ...domain.optimization.synthesis import SynthesisTarget
from ...domain.simulation.spec import SimulationSpec
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key
from ..workers.yagi_optimization_worker import YagiOptimizationWorker


class YagiOptimizationDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        solver: AntennaSolver,
        base_parameters: YagiParameters,
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
        self._worker: YagiOptimizationWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._result: BoundedResult | None = None
        self._selected_parameters: YagiParameters | None = None
        self._run_objective = YagiOptimizationObjective.TARGET_IMPEDANCE
        self._updating = False

        self.setWindowTitle(translator.t("yagi_optimize.title"))
        self.resize(1_100, 780)

        self._objective = QComboBox(self)
        self._objective.addItem("", YagiOptimizationObjective.TARGET_IMPEDANCE.value)
        self._objective.addItem("", YagiOptimizationObjective.MAX_GAIN.value)
        self._objective.addItem("", YagiOptimizationObjective.MAX_FRONT_TO_BACK.value)
        self._objective.currentIndexChanged.connect(self._objective_changed)

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

        self._bound_percent = QDoubleSpinBox(self)
        self._bound_percent.setRange(1.0, 50.0)
        self._bound_percent.setDecimals(1)
        self._bound_percent.setValue(10.0)
        self._bound_percent.setSuffix(" %")
        self._bound_percent.valueChanged.connect(self._update_bounds)

        self._min_gap = QDoubleSpinBox(self)
        self._min_gap.setRange(
            length_from_m(0.001, unit_system), length_from_m(1_000.0, unit_system)
        )
        self._min_gap.setDecimals(3)
        self._min_gap.setValue(length_from_m(0.1, unit_system))
        self._min_gap.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._min_gap.valueChanged.connect(self._update_bounds)

        self._max_evaluations = QSpinBox(self)
        self._max_evaluations.setRange(10, 500)
        self._max_evaluations.setValue(81)

        self._samples = QSpinBox(self)
        self._samples.setRange(3, 9)
        self._samples.setValue(5)

        self._passes = QSpinBox(self)
        self._passes.setRange(1, 8)
        self._passes.setValue(4)

        self._table = QTableWidget(len(base_parameters.elements), 8, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)

        self._label_objective = QLabel(translator.t("optimize.objective"), self)
        self._label_frequency = QLabel(translator.t("synthesis.target_frequency"), self)
        self._label_r = QLabel(translator.t("synthesis.target_resistance"), self)
        self._label_x = QLabel(translator.t("synthesis.target_reactance"), self)
        self._label_bound = QLabel(translator.t("yagi_optimize.bound"), self)
        self._label_min_gap = QLabel(translator.t("yagi_optimize.min_gap"), self)
        self._label_evaluations = QLabel(translator.t("optimize.max_evaluations"), self)
        self._label_samples = QLabel(translator.t("yagi_optimize.samples"), self)
        self._label_passes = QLabel(translator.t("yagi_optimize.passes"), self)

        form = QFormLayout()
        form.addRow(self._label_objective, self._objective)
        form.addRow(self._label_frequency, self._frequency)
        form.addRow(self._label_r, self._target_r)
        form.addRow(self._label_x, self._target_x)
        form.addRow(self._label_bound, self._bound_percent)
        form.addRow(self._label_min_gap, self._min_gap)
        form.addRow(self._label_evaluations, self._max_evaluations)
        form.addRow(self._label_samples, self._samples)
        form.addRow(self._label_passes, self._passes)

        self._evaluations = QTableWidget(0, 8, self)
        self._evaluations.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._evaluations.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._evaluations.setAlternatingRowColors(True)
        self._evaluations.verticalHeader().setVisible(False)
        self._evaluations.horizontalHeader().setStretchLastSection(True)
        self._evaluations_label = QLabel(translator.t("optimize.evaluations"), self)

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._hint = QLabel(translator.t("yagi_optimize.hint"), self)
        self._hint.setWordWrap(True)

        self._run = QPushButton(translator.t("yagi_optimize.run"), self)
        self._cancel = QPushButton(translator.t("optimize.cancel_run"), self)
        self._apply = QPushButton(translator.t("yagi_optimize.apply"), self)
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
        layout.addWidget(self._table, 1)
        layout.addWidget(self._evaluations_label)
        layout.addWidget(self._evaluations, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._hint)
        layout.addLayout(buttons)

        self._retranslate()
        self._populate_table()
        self._objective_changed()
        self._update_controls()

    def _retranslate(self) -> None:
        t = self._translator.t
        self._objective.setItemText(0, t("yagi_optimize.target_impedance_objective"))
        self._objective.setItemText(1, t("yagi_optimize.max_gain_objective"))
        self._objective.setItemText(2, t("yagi_optimize.max_front_to_back_objective"))
        self._table.setHorizontalHeaderLabels(
            [
                t("yagi.element"),
                t("yagi.driven"),
                t("yagi_optimize.opt_length"),
                t("yagi_optimize.opt_gap"),
                t("yagi_optimize.current_length"),
                t("yagi_optimize.length_range"),
                t("yagi_optimize.current_gap"),
                t("yagi_optimize.gap_range"),
            ]
        )
        self._evaluations.setHorizontalHeaderLabels(
            [
                t("optimize.rank"),
                t("optimize.iteration"),
                t("table.resistance"),
                t("table.reactance"),
                t("table.swr"),
                t("optimize.gain"),
                t("yagi_optimize.front_to_back"),
                t("yagi_optimize.objective_value"),
                t("optimize.message"),
            ]
        )

    def _check_item(self, checked: bool) -> QTableWidgetItem:
        item = QTableWidgetItem("")
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        return item

    def _current_gap_m(self, row: int) -> float:
        elements = self._base_parameters.elements
        return elements[row].position_m - elements[row - 1].position_m

    def _objective_value(self) -> YagiOptimizationObjective:
        return YagiOptimizationObjective(str(self._objective.currentData()))

    def _objective_changed(self, *_args: object) -> None:
        target = self._objective_value() is YagiOptimizationObjective.TARGET_IMPEDANCE
        for widget in (self._target_r, self._target_x):
            widget.setEnabled(target)
        self._label_r.setVisible(target)
        self._label_x.setVisible(target)
        self._target_r.setVisible(target)
        self._target_x.setVisible(target)

    def _populate_table(self) -> None:
        self._updating = True
        try:
            for row, element in enumerate(self._base_parameters.elements):
                self._table.setItem(row, 0, QTableWidgetItem(f"element-{row + 1}"))
                self._table.setItem(
                    row,
                    1,
                    QTableWidgetItem("✓" if row == self._base_parameters.driven_index else ""),
                )
                self._table.setItem(row, 2, self._check_item(True))
                if row == 0:
                    first_gap = QTableWidgetItem("—")
                    first_gap.setFlags(Qt.ItemFlag.NoItemFlags)
                    self._table.setItem(row, 3, first_gap)
                else:
                    self._table.setItem(row, 3, self._check_item(True))
                self._table.setItem(
                    row,
                    4,
                    QTableWidgetItem(f"{length_from_m(element.length_m, self._unit_system):.3f}"),
                )
                self._table.setItem(
                    row,
                    6,
                    QTableWidgetItem(
                        "—"
                        if row == 0
                        else f"{length_from_m(self._current_gap_m(row), self._unit_system):.3f}"
                    ),
                )
        finally:
            self._updating = False
        self._update_bounds()

    def _update_bounds(self, *_args: object) -> None:
        if self._updating:
            return
        factor = self._bound_percent.value() / 100.0
        min_gap_m = length_to_m(self._min_gap.value(), self._unit_system)
        self._updating = True
        try:
            for row, element in enumerate(self._base_parameters.elements):
                length_min = element.length_m * (1.0 - factor)
                length_max = element.length_m * (1.0 + factor)
                self._table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        f"{length_from_m(length_min, self._unit_system):.3f} .. "
                        f"{length_from_m(length_max, self._unit_system):.3f}"
                    ),
                )
                if row == 0:
                    self._table.setItem(row, 7, QTableWidgetItem("—"))
                    continue
                current_gap = self._current_gap_m(row)
                gap_min = max(current_gap * (1.0 - factor), min_gap_m)
                gap_max = max(current_gap * (1.0 + factor), gap_min + max(current_gap * 0.01, 1e-3))
                self._table.setItem(
                    row,
                    7,
                    QTableWidgetItem(
                        f"{length_from_m(gap_min, self._unit_system):.3f} .. "
                        f"{length_from_m(gap_max, self._unit_system):.3f}"
                    ),
                )
        finally:
            self._updating = False

    def _selected_length_indices(self) -> tuple[int, ...]:
        return tuple(
            row
            for row in range(self._table.rowCount())
            if (item := self._table.item(row, 2)) is not None
            and item.checkState() == Qt.CheckState.Checked
        )

    def _selected_gap_indices(self) -> tuple[int, ...]:
        return tuple(
            row
            for row in range(1, self._table.rowCount())
            if (item := self._table.item(row, 3)) is not None
            and item.checkState() == Qt.CheckState.Checked
        )

    def _build_parameters(self, values: dict[str, float]) -> YagiParameters:
        elements = list(self._base_parameters.elements)
        for index in self._selected_length_indices():
            elements[index] = replace(elements[index], length_m=values[f"length_{index}"])
        positions = [self._base_parameters.elements[0].position_m]
        for index in range(1, len(elements)):
            gap = values.get(
                f"gap_{index}",
                self._base_parameters.elements[index].position_m
                - self._base_parameters.elements[index - 1].position_m,
            )
            positions.append(positions[-1] + gap)
        elements = [
            replace(element, position_m=positions[index]) for index, element in enumerate(elements)
        ]
        return replace(
            self._base_parameters,
            frequency_hz=self._frequency.value() * 1_000_000.0,
            elements=tuple(elements),
        )

    def _target(self) -> SynthesisTarget:
        return SynthesisTarget(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            resistance_ohm=self._target_r.value(),
            reactance_ohm=self._target_x.value(),
        )

    def _variables(self) -> tuple[tuple[BoundedVariable, ...], dict[str, float]]:
        factor = self._bound_percent.value() / 100.0
        min_gap_m = length_to_m(self._min_gap.value(), self._unit_system)
        variables: list[BoundedVariable] = []
        starts: dict[str, float] = {}
        for index in self._selected_length_indices():
            length = self._base_parameters.elements[index].length_m
            name = f"length_{index}"
            variables.append(
                BoundedVariable(name, max(length * (1.0 - factor), 1e-3), length * (1.0 + factor))
            )
            starts[name] = length
        for index in self._selected_gap_indices():
            gap = self._current_gap_m(index)
            name = f"gap_{index}"
            gap_min = max(gap * (1.0 - factor), min_gap_m)
            gap_max = max(gap * (1.0 + factor), gap_min + max(gap * 0.01, 1e-3))
            variables.append(BoundedVariable(name, gap_min, gap_max))
            starts[name] = max(gap, gap_min)
        if not variables:
            raise ValueError(self._translator.t("yagi_optimize.no_elements"))
        return tuple(variables), starts

    def _start(self) -> None:
        if self._thread is not None:
            return
        try:
            variables, starts = self._variables()
            target = self._target()
        except ValueError as exc:
            QMessageBox.critical(self, self._translator.t("yagi_optimize.title"), str(exc))
            return
        self._result = None
        self._selected_parameters = None
        self._run_objective = self._objective_value()
        self._evaluations.setRowCount(0)
        self._summary.setText(self._translator.t("yagi_optimize.running"))
        self._apply.setEnabled(False)
        self._cancel_token = EventCancelToken()
        command = OptimizeYagiElementsCommand(
            build_parameters=self._build_parameters,
            variables=variables,
            start_values=starts,
            target=target,
            base_spec=self._base_spec,
            objective=self._objective_value(),
            max_evaluations=self._max_evaluations.value(),
            samples=self._samples.value(),
            passes=self._passes.value(),
            cancel_token=self._cancel_token,
        )
        thread = QThread(self)
        worker = YagiOptimizationWorker(self._solver, command)
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
            self._summary.setText(self._translator.t("yagi_optimize.running"))
            self._cancel.setEnabled(False)

    def _on_finished(self, result: BoundedResult) -> None:
        self._result = result
        self._populate_evaluations(result)
        self._summary.setText(self._summary_text(result))
        if result.best_values is not None:
            self._selected_parameters = self._build_parameters(dict(result.best_values))
        self._apply.setEnabled(self._selected_parameters is not None)

    def _on_failed(self, message: str) -> None:
        self._summary.setText(self._translator.t("yagi_optimize.error", message=message))
        QMessageBox.critical(
            self,
            self._translator.t("yagi_optimize.title"),
            self._translator.t("yagi_optimize.error", message=message),
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
            self._bound_percent,
            self._min_gap,
            self._max_evaluations,
            self._samples,
            self._passes,
            self._table,
        ):
            widget.setEnabled(not running)
        self._run.setEnabled(not running)
        self._cancel.setEnabled(running)
        self._close.setEnabled(not running)
        if running:
            self._apply.setEnabled(False)

    def _length_display(self, value_m: float) -> str:
        value = length_from_m(value_m, self._unit_system)
        unit = self._translator.t(length_unit_key(self._unit_system))
        return f"{value:.3f} {unit}"

    def _populate_evaluations(self, result: BoundedResult) -> None:
        ordered = rank_bounded(result.evaluations)
        self._evaluations.setRowCount(len(ordered))
        for row, evaluation in enumerate(ordered):
            impedance = None
            if "resistance_ohm" in evaluation.metrics and "reactance_ohm" in evaluation.metrics:
                impedance = complex(
                    evaluation.metrics["resistance_ohm"],
                    evaluation.metrics["reactance_ohm"],
                )
            gain = evaluation.metrics.get("max_gain_db")
            front_to_back = evaluation.metrics.get("front_to_back_db")
            objective_value = "—"
            if evaluation.score is not None:
                if self._objective_value() is YagiOptimizationObjective.TARGET_IMPEDANCE:
                    objective_value = f"ΔZ={evaluation.score:.3f} Ω"
                elif (
                    self._objective_value() is YagiOptimizationObjective.MAX_GAIN
                    and gain is not None
                ):
                    objective_value = f"G={gain:.2f} dBi"
                elif front_to_back is not None:
                    objective_value = f"F/B={front_to_back:.2f} dB"
            values = [
                str(row + 1),
                str(evaluation.index),
                f"{impedance.real:.3f}" if impedance is not None else "—",
                f"{impedance.imag:+.3f}" if impedance is not None else "—",
                (f"{evaluation.metrics['swr']:.3f}" if "swr" in evaluation.metrics else "—"),
                f"{gain:.2f}" if gain is not None else "—",
                f"{front_to_back:.2f}" if front_to_back is not None else "—",
                objective_value,
                evaluation.error or "",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {2, 3, 4, 5, 6, 7}:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self._evaluations.setItem(row, column, item)
        self._evaluations.resizeColumnsToContents()
        self._evaluations.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

    def _summary_text(self, result: BoundedResult) -> str:
        if result.best_values is None:
            return self._translator.t("yagi_optimize.no_best")
        parts = []
        for name, value in sorted(result.best_values.items()):
            index = int(name.rsplit("_", 1)[1]) + 1
            if name.startswith("length_"):
                parts.append(f"L{index}={self._length_display(value)}")
            else:
                parts.append(f"G{index}={self._length_display(value)}")
        best = next(
            (
                evaluation
                for evaluation in result.evaluations
                if evaluation.values == result.best_values
            ),
            None,
        )
        objective_value = "—"
        if best is not None:
            if self._run_objective is YagiOptimizationObjective.TARGET_IMPEDANCE:
                if best.score is not None:
                    objective_value = f"ΔZ={best.score:.3f} Ω"
            elif self._run_objective is YagiOptimizationObjective.MAX_GAIN:
                gain = best.metrics.get("max_gain_db")
                if gain is not None:
                    objective_value = f"G={gain:.2f} dBi"
            else:
                front_to_back = best.metrics.get("front_to_back_db")
                if front_to_back is not None:
                    objective_value = f"F/B={front_to_back:.2f} dB"
        return self._translator.t(
            "yagi_optimize.summary",
            lengths=", ".join(parts),
            error=objective_value,
        )

    def _apply_result(self) -> None:
        if self._selected_parameters is not None:
            self.accept()

    def selected_parameters(self) -> YagiParameters | None:
        return self._selected_parameters

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None:
            if self._cancel_token is not None:
                self._cancel_token.cancel()
            QMessageBox.information(
                self,
                self._translator.t("yagi_optimize.title"),
                self._translator.t("yagi_optimize.close"),
            )
            event.ignore()
            return
        super().closeEvent(event)
