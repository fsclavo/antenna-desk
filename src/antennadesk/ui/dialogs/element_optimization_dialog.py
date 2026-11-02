# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generic bounded multi-element optimization dialog."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

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
from ...application.use_cases.optimize_elements import (
    ElementOptimizationObjective,
    ElementOptimizationWeights,
    OptimizeElementsCommand,
)
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.optimization.multi_variable import (
    BoundedEvaluation,
    BoundedResult,
    BoundedVariable,
    rank_bounded,
)
from ...domain.optimization.pareto import ParetoObjectives, pareto_ranks
from ...domain.optimization.synthesis import SynthesisTarget
from ...domain.simulation.spec import SimulationSpec
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_unit_key
from ..workers.element_optimization_worker import ElementOptimizationWorker


@dataclass(frozen=True, slots=True)
class ElementOptimizationVariable:
    name: str
    label: str
    current_m: float


BuildParameters = Callable[[dict[str, float]], AntennaDesignParameters]


class ElementOptimizationDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        solver: AntennaSolver,
        base_spec: SimulationSpec,
        *,
        title_key: str,
        variables: tuple[ElementOptimizationVariable, ...],
        build_parameters: BuildParameters,
        objectives: tuple[ElementOptimizationObjective, ...],
        default_frequency_hz: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._solver = solver
        self._base_spec = base_spec
        self._variables_spec = variables
        self._build = build_parameters
        self._objectives = objectives
        self._thread: QThread | None = None
        self._worker: ElementOptimizationWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._result: BoundedResult | None = None
        self._selected_parameters: AntennaDesignParameters | None = None
        self._run_objective = objectives[0]
        self._run_weights = ElementOptimizationWeights()
        self._ordered_evaluations: tuple[BoundedEvaluation, ...] = ()
        self._updating = False

        self.setWindowTitle(translator.t(title_key))
        self.resize(1_050, 760)

        self._objective = QComboBox(self)
        for objective in objectives:
            self._objective.addItem("", objective.value)
        self._objective.currentIndexChanged.connect(self._objective_changed)

        self._frequency = QDoubleSpinBox(self)
        self._frequency.setRange(0.1, 100_000.0)
        self._frequency.setDecimals(6)
        self._frequency.setSuffix(" MHz")
        self._frequency.setValue(default_frequency_hz / 1_000_000.0)

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

        def weight() -> QDoubleSpinBox:
            box = QDoubleSpinBox(self)
            box.setRange(0.0, 100.0)
            box.setDecimals(2)
            box.setSingleStep(0.1)
            return box

        self._weight_gain = weight()
        self._weight_gain.setValue(1.0)
        self._weight_fb = weight()
        self._weight_fb.setValue(1.0)
        self._weight_swr = weight()
        self._weight_swr.setValue(1.0)
        self._weight_efficiency = weight()
        self._weight_efficiency.setValue(0.0)
        self._label_weight_gain = QLabel(translator.t("element_optimize.weight_gain"), self)
        self._label_weight_fb = QLabel(translator.t("element_optimize.weight_fb"), self)
        self._label_weight_swr = QLabel(translator.t("element_optimize.weight_swr"), self)
        self._label_weight_efficiency = QLabel(
            translator.t("element_optimize.weight_efficiency"), self
        )

        self._bound_percent = QDoubleSpinBox(self)
        self._bound_percent.setRange(1.0, 50.0)
        self._bound_percent.setDecimals(1)
        self._bound_percent.setValue(10.0)
        self._bound_percent.setSuffix(" %")
        self._bound_percent.valueChanged.connect(self._update_bounds)

        self._max_evaluations = QSpinBox(self)
        self._max_evaluations.setRange(10, 500)
        self._max_evaluations.setValue(81)

        self._samples = QSpinBox(self)
        self._samples.setRange(3, 9)
        self._samples.setValue(5)

        self._passes = QSpinBox(self)
        self._passes.setRange(1, 8)
        self._passes.setValue(4)

        self._table = QTableWidget(len(variables), 5, self)
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
        self._label_evaluations = QLabel(translator.t("optimize.max_evaluations"), self)
        self._label_samples = QLabel(translator.t("yagi_optimize.samples"), self)
        self._label_passes = QLabel(translator.t("yagi_optimize.passes"), self)

        form = QFormLayout()
        form.addRow(self._label_objective, self._objective)
        form.addRow(self._label_frequency, self._frequency)
        form.addRow(self._label_r, self._target_r)
        form.addRow(self._label_x, self._target_x)
        form.addRow(self._label_weight_gain, self._weight_gain)
        form.addRow(self._label_weight_fb, self._weight_fb)
        form.addRow(self._label_weight_swr, self._weight_swr)
        form.addRow(self._label_weight_efficiency, self._weight_efficiency)
        form.addRow(self._label_bound, self._bound_percent)
        form.addRow(self._label_evaluations, self._max_evaluations)
        form.addRow(self._label_samples, self._samples)
        form.addRow(self._label_passes, self._passes)

        self._evaluations = QTableWidget(0, 11, self)
        self._evaluations.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._evaluations.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._evaluations.setAlternatingRowColors(True)
        self._evaluations.verticalHeader().setVisible(False)
        self._evaluations.horizontalHeader().setStretchLastSection(True)
        self._evaluations_label = QLabel(translator.t("optimize.evaluations"), self)
        self._evaluations.itemSelectionChanged.connect(self._on_evaluation_selected)

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._hint = QLabel(translator.t("element_optimize.hint"), self)
        self._hint.setWordWrap(True)

        self._run = QPushButton(translator.t("element_optimize.run"), self)
        self._cancel = QPushButton(translator.t("optimize.cancel_run"), self)
        self._apply = QPushButton(translator.t("element_optimize.apply"), self)
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
        for index, objective in enumerate(self._objectives):
            self._objective.setItemText(index, t(f"element_optimize.objective.{objective.value}"))
        self._table.setHorizontalHeaderLabels(
            [
                t("moxon_optimize.variable"),
                t("yagi_optimize.use"),
                t("yagi_optimize.current_length"),
                t("yagi_optimize.minimum"),
                t("yagi_optimize.maximum"),
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
                t("optimize.efficiency"),
                t("element_optimize.pareto"),
                t("yagi_optimize.objective_value"),
                t("optimize.message"),
            ]
        )

    def _populate_table(self) -> None:
        self._updating = True
        try:
            for row, variable in enumerate(self._variables_spec):
                self._table.setItem(row, 0, QTableWidgetItem(variable.label))
                use = QTableWidgetItem("")
                use.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                use.setCheckState(Qt.CheckState.Checked)
                self._table.setItem(row, 1, use)
                self._table.setItem(
                    row,
                    2,
                    QTableWidgetItem(f"{length_from_m(variable.current_m, self._unit_system):.3f}"),
                )
        finally:
            self._updating = False
        self._update_bounds()

    def _update_bounds(self, *_args: object) -> None:
        if self._updating:
            return
        factor = self._bound_percent.value() / 100.0
        self._updating = True
        try:
            for row, variable in enumerate(self._variables_spec):
                low = length_from_m(variable.current_m * (1.0 - factor), self._unit_system)
                high = length_from_m(variable.current_m * (1.0 + factor), self._unit_system)
                self._table.setItem(row, 3, QTableWidgetItem(f"{low:.3f}"))
                self._table.setItem(row, 4, QTableWidgetItem(f"{high:.3f}"))
        finally:
            self._updating = False

    def _selected_indices(self) -> tuple[int, ...]:
        return tuple(
            row
            for row in range(self._table.rowCount())
            if (item := self._table.item(row, 1)) is not None
            and item.checkState() == Qt.CheckState.Checked
        )

    def _objective_value(self) -> ElementOptimizationObjective:
        return ElementOptimizationObjective(str(self._objective.currentData()))

    def _objective_changed(self, *_args: object) -> None:
        target = self._objective_value() is ElementOptimizationObjective.TARGET_IMPEDANCE
        multi = self._objective_value() is ElementOptimizationObjective.MULTI_OBJECTIVE
        self._label_r.setVisible(target)
        self._label_x.setVisible(target)
        self._target_r.setVisible(target)
        self._target_x.setVisible(target)
        for label, widget in (
            (self._label_weight_gain, self._weight_gain),
            (self._label_weight_fb, self._weight_fb),
            (self._label_weight_swr, self._weight_swr),
            (self._label_weight_efficiency, self._weight_efficiency),
        ):
            label.setVisible(multi)
            widget.setVisible(multi)

    def _target(self) -> SynthesisTarget:
        return SynthesisTarget(
            frequency_hz=self._frequency.value() * 1_000_000.0,
            resistance_ohm=self._target_r.value(),
            reactance_ohm=self._target_x.value(),
        )

    def _variables(self) -> tuple[tuple[BoundedVariable, ...], dict[str, float]]:
        factor = self._bound_percent.value() / 100.0
        variables: list[BoundedVariable] = []
        starts: dict[str, float] = {}
        for index in self._selected_indices():
            variable = self._variables_spec[index]
            variables.append(
                BoundedVariable(
                    variable.name,
                    max(variable.current_m * (1.0 - factor), 1e-3),
                    variable.current_m * (1.0 + factor),
                )
            )
            starts[variable.name] = variable.current_m
        if not variables:
            raise ValueError(self._translator.t("element_optimize.no_variables"))
        return tuple(variables), starts

    def _build_with_frequency(self, values: dict[str, float]) -> AntennaDesignParameters:
        target = self._target()
        return self._build({**values, "__frequency_hz": target.frequency_hz})

    def _start(self) -> None:
        if self._thread is not None:
            return
        try:
            variables, starts = self._variables()
            target = self._target()
        except ValueError as exc:
            QMessageBox.critical(self, self.windowTitle(), str(exc))
            return
        self._result = None
        self._selected_parameters = None
        self._run_objective = self._objective_value()
        self._run_weights = ElementOptimizationWeights(
            gain=self._weight_gain.value(),
            front_to_back=self._weight_fb.value(),
            swr=self._weight_swr.value(),
            efficiency=self._weight_efficiency.value(),
        )
        self._evaluations.setRowCount(0)
        self._summary.setText(self._translator.t("element_optimize.running"))
        self._apply.setEnabled(False)
        self._cancel_token = EventCancelToken()
        command = OptimizeElementsCommand(
            build_parameters=self._build_with_frequency,
            variables=variables,
            start_values=starts,
            target=target,
            base_spec=self._base_spec,
            objective=self._run_objective,
            weights=self._run_weights,
            max_evaluations=self._max_evaluations.value(),
            samples=self._samples.value(),
            passes=self._passes.value(),
            cancel_token=self._cancel_token,
        )
        thread = QThread(self)
        worker = ElementOptimizationWorker(self._solver, command)
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
            self._summary.setText(self._translator.t("element_optimize.running"))
            self._cancel.setEnabled(False)

    def _on_finished(self, result: BoundedResult) -> None:
        self._result = result
        self._populate_evaluations(result)
        self._summary.setText(self._summary_text(result))
        if result.best_values is not None:
            self._selected_parameters = self._build_with_frequency(dict(result.best_values))
        self._apply.setEnabled(self._selected_parameters is not None)

    def _on_failed(self, message: str) -> None:
        self._summary.setText(self._translator.t("element_optimize.error", message=message))
        QMessageBox.critical(
            self,
            self.windowTitle(),
            self._translator.t("element_optimize.error", message=message),
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
            self._frequency,
            self._target_r,
            self._target_x,
            self._weight_gain,
            self._weight_fb,
            self._weight_swr,
            self._weight_efficiency,
            self._bound_percent,
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

    def _objective_text(self, evaluation: BoundedEvaluation) -> str:
        if evaluation.score is None:
            return "—"
        if self._run_objective is ElementOptimizationObjective.TARGET_IMPEDANCE:
            return f"ΔZ={evaluation.score:.3f} Ω"
        gain = evaluation.metrics.get("max_gain_db")
        front_to_back = evaluation.metrics.get("front_to_back_db")
        if self._run_objective is ElementOptimizationObjective.MAX_GAIN and gain is not None:
            return f"G={gain:.2f} dBi"
        if self._run_objective is ElementOptimizationObjective.MULTI_OBJECTIVE:
            return f"Score={-evaluation.score:.3f}"
        if front_to_back is not None:
            return f"F/B={front_to_back:.2f} dB"
        return "—"

    def _populate_evaluations(self, result: BoundedResult) -> None:
        ordered = rank_bounded(result.evaluations)
        self._ordered_evaluations = ordered
        ranks: dict[int, int] = {}
        if self._run_objective is ElementOptimizationObjective.MULTI_OBJECTIVE:
            ranks = pareto_ranks(
                ordered,
                ParetoObjectives(
                    gain=self._run_weights.gain > 0.0,
                    front_to_back=self._run_weights.front_to_back > 0.0,
                    swr=self._run_weights.swr > 0.0,
                    efficiency=self._run_weights.efficiency > 0.0,
                ),
            )
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
            efficiency = evaluation.metrics.get("efficiency_percent")
            values = [
                str(row + 1),
                str(evaluation.index),
                f"{impedance.real:.3f}" if impedance is not None else "—",
                f"{impedance.imag:+.3f}" if impedance is not None else "—",
                (f"{evaluation.metrics['swr']:.3f}" if "swr" in evaluation.metrics else "—"),
                f"{gain:.2f}" if gain is not None else "—",
                f"{front_to_back:.2f}" if front_to_back is not None else "—",
                f"{efficiency:.2f}" if efficiency is not None else "—",
                str(ranks[evaluation.index]) if evaluation.index in ranks else "—",
                self._objective_text(evaluation),
                evaluation.error or "",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in {2, 3, 4, 5, 6, 7, 8, 9}:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self._evaluations.setItem(row, column, item)
        self._evaluations.resizeColumnsToContents()
        self._evaluations.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)

    def _on_evaluation_selected(self) -> None:
        rows = sorted({index.row() for index in self._evaluations.selectedIndexes()})
        if not rows or rows[0] >= len(self._ordered_evaluations):
            return
        evaluation = self._ordered_evaluations[rows[0]]
        if evaluation.score is None:
            return
        try:
            self._selected_parameters = self._build_with_frequency(dict(evaluation.values))
        except (ValueError, TypeError):
            return
        self._apply.setEnabled(True)
        self._summary.setText(
            self._translator.t(
                "element_optimize.selected_summary",
                objective=self._objective_text(evaluation),
            )
        )

    def _summary_text(self, result: BoundedResult) -> str:
        if result.best_values is None:
            return self._translator.t("element_optimize.no_best")
        best = next(
            (
                evaluation
                for evaluation in result.evaluations
                if evaluation.values == result.best_values
            ),
            None,
        )
        dimensions = ", ".join(
            f"{name}={self._length_display(value)}"
            for name, value in sorted(result.best_values.items())
        )
        return self._translator.t(
            "element_optimize.summary",
            dimensions=dimensions,
            objective=self._objective_text(best) if best is not None else "—",
        )

    def _apply_result(self) -> None:
        if self._selected_parameters is not None:
            self.accept()

    def selected_parameters(self) -> AntennaDesignParameters | None:
        return self._selected_parameters

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None:
            if self._cancel_token is not None:
                self._cancel_token.cancel()
            QMessageBox.information(
                self,
                self.windowTitle(),
                self._translator.t("element_optimize.close"),
            )
            event.ignore()
            return
        super().closeEvent(event)
