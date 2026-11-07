# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generic family-driven antenna optimizer dialog."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
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
from ...application.use_cases.optimize_antenna import (
    OptimizeAntennaCommand,
    OptimizeAntennaResult,
)
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.optimization.constraints import OptimizationMetric, SoftConstraint
from ...domain.optimization.descriptor import (
    AntennaOptimizerDescriptor,
    FamilyOptimizationObjective,
    OptimizationWeights,
)
from ...domain.optimization.engine import BudgetProfile, budget_for
from ...domain.optimization.variables import OptimizationVariable, VariableKind
from ...domain.simulation.spec import SimulationSpec
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_unit_key, radius_from_m, radius_unit_key
from ..workers.family_optimization_worker import FamilyOptimizationWorker

_OBJECTIVE_KEYS = {
    FamilyOptimizationObjective.TARGET_IMPEDANCE: "optimize.target_impedance_objective",
    FamilyOptimizationObjective.MIN_SWR: "optimize.min_swr_objective",
    FamilyOptimizationObjective.MAX_GAIN: "optimize.max_gain_objective",
    FamilyOptimizationObjective.MAX_FRONT_TO_BACK: "element_optimize.objective.max_front_to_back",
    FamilyOptimizationObjective.MAX_EFFICIENCY: "optimize.max_efficiency_objective",
    FamilyOptimizationObjective.MAX_BANDWIDTH: "optimize.max_bandwidth_objective",
    FamilyOptimizationObjective.MULTI_OBJECTIVE: "optimize.balanced_objective",
}


class FamilyOptimizationDialog(QDialog):
    """One dialog for every registered family optimizer."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        solver: AntennaSolver,
        descriptor: AntennaOptimizerDescriptor,
        base_spec: SimulationSpec,
        parent: QWidget | None = None,
        *,
        topology_label: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._solver = solver
        self._descriptor = descriptor
        self._base_spec = base_spec
        self._thread: QThread | None = None
        self._worker: FamilyOptimizationWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._result: OptimizeAntennaResult | None = None
        self._selected_parameters: AntennaDesignParameters | None = None
        self._variables = descriptor.variables
        self._updating = False
        self._ready = False

        self.setWindowTitle(translator.t("optimize.family_title"))
        self.resize(*scaled_dialog_size(1_100, 820))

        self._objective = QComboBox(self)
        for objective in sorted(descriptor.objectives, key=lambda item: item.value):
            self._objective.addItem(translator.t(_OBJECTIVE_KEYS[objective]), objective.value)
        index = self._objective.findData(descriptor.default_objective.value)
        if index >= 0:
            self._objective.setCurrentIndex(index)
        self._objective.currentIndexChanged.connect(self._objective_changed)

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

        self._weight_gain = self._weight_spin(1.0)
        self._weight_fb = self._weight_spin(1.0)
        self._weight_swr = self._weight_spin(1.0)
        self._weight_efficiency = self._weight_spin(0.0)

        self._budget = QComboBox(self)
        for profile in (BudgetProfile.FAST, BudgetProfile.BALANCED, BudgetProfile.THOROUGH):
            self._budget.addItem(
                translator.t(f"optimize.budget.{profile.value}"),
                profile.value,
            )
        self._budget.setCurrentIndex(self._budget.findData(BudgetProfile.BALANCED.value))
        self._budget.currentIndexChanged.connect(self._budget_changed)

        self._seed = QSpinBox(self)
        self._seed.setRange(0, 2_147_483_647)
        self._seed.setValue(0)

        self._max_swr = QDoubleSpinBox(self)
        self._max_swr.setRange(1.0, 20.0)
        self._max_swr.setDecimals(2)
        self._max_swr.setValue(2.0)
        self._max_swr_enabled = QCheckBox(translator.t("optimize.max_swr_constraint"), self)
        self._max_swr_row = QWidget(self)
        swr_layout = QHBoxLayout(self._max_swr_row)
        swr_layout.setContentsMargins(0, 0, 0, 0)
        swr_layout.addWidget(self._max_swr_enabled)
        swr_layout.addWidget(self._max_swr)
        self._max_swr.setEnabled(False)
        self._max_swr_enabled.toggled.connect(self._max_swr.setEnabled)

        self._budget_hint = QLabel(self)
        self._budget_hint.setWordWrap(True)
        self._locked_hint = QLabel(translator.t("optimize.locked_partial"), self)
        self._locked_hint.setWordWrap(True)
        self._locked_hint.setVisible(False)

        self._table = QTableWidget(len(self._variables), 6, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.itemChanged.connect(self._use_changed)
        self._populate_variables()

        self._evaluations = QTableWidget(0, 10, self)
        self._evaluations.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._evaluations.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._evaluations.setAlternatingRowColors(True)
        self._evaluations.verticalHeader().setVisible(False)
        self._evaluations.horizontalHeader().setStretchLastSection(True)
        self._evaluations_label = QLabel(translator.t("optimize.evaluations"), self)

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._sensitivity = QLabel(self)
        self._sensitivity.setWordWrap(True)

        self._run = QPushButton(translator.t("optimize.run_family"), self)
        self._cancel = QPushButton(translator.t("optimize.cancel_run"), self)
        self._apply = QPushButton(translator.t("optimize.apply_best"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._cancel.setEnabled(False)
        self._apply.setEnabled(False)
        self._run.clicked.connect(self._start)
        self._cancel.clicked.connect(self._cancel_run)
        self._apply.clicked.connect(self._apply_result)
        self._close.clicked.connect(self.reject)

        self._target_r_label = QLabel(translator.t("synthesis.target_resistance"), self)
        self._target_x_label = QLabel(translator.t("synthesis.target_reactance"), self)
        self._objective_label = QLabel(translator.t("optimize.objective"), self)
        self._budget_label = QLabel(translator.t("optimize.budget_profile"), self)
        self._seed_label = QLabel(translator.t("optimize.seed"), self)
        self._weight_gain_label = QLabel(translator.t("optimize.gain_weight"), self)
        self._weight_fb_label = QLabel(translator.t("element_optimize.weight_fb"), self)
        self._weight_swr_label = QLabel(translator.t("optimize.swr_weight"), self)
        self._weight_efficiency_label = QLabel(translator.t("optimize.efficiency_weight"), self)

        form = QFormLayout()
        if topology_label:
            form.addRow(QLabel(translator.t("field.template"), self), QLabel(topology_label, self))
        form.addRow(self._objective_label, self._objective)
        form.addRow(self._target_r_label, self._target_r)
        form.addRow(self._target_x_label, self._target_x)
        form.addRow(self._weight_gain_label, self._weight_gain)
        form.addRow(self._weight_fb_label, self._weight_fb)
        form.addRow(self._weight_swr_label, self._weight_swr)
        form.addRow(self._weight_efficiency_label, self._weight_efficiency)
        form.addRow(self._budget_label, self._budget)
        form.addRow(self._seed_label, self._seed)
        form.addRow(self._budget_hint)
        form.addRow(self._max_swr_row)

        self._table.setHorizontalHeaderLabels(
            [
                translator.t("optimize.variables"),
                translator.t("optimize.group"),
                translator.t("optimize.use"),
                translator.t("optimize.current"),
                translator.t("optimize.minimum"),
                translator.t("optimize.maximum"),
            ]
        )
        self._evaluations.setHorizontalHeaderLabels(
            [
                translator.t("optimize.rank"),
                translator.t("optimize.iteration"),
                translator.t("optimize.score"),
                translator.t("table.resistance"),
                translator.t("table.reactance"),
                translator.t("table.swr"),
                translator.t("optimize.gain"),
                translator.t("yagi_optimize.front_to_back"),
                translator.t("optimize.efficiency"),
                translator.t("optimize.message"),
            ]
        )

        buttons = QHBoxLayout()
        buttons.addWidget(self._run)
        buttons.addWidget(self._cancel)
        buttons.addStretch(1)
        buttons.addWidget(self._apply)
        buttons.addWidget(self._close)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._locked_hint)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._evaluations_label)
        layout.addWidget(self._evaluations, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._sensitivity)
        layout.addLayout(buttons)

        self._ready = True
        self._objective_changed()
        self._budget_changed()
        self._update_controls()

    def _weight_spin(self, value: float) -> QDoubleSpinBox:
        box = QDoubleSpinBox(self)
        box.setRange(0.0, 100.0)
        box.setDecimals(2)
        box.setSingleStep(0.1)
        box.setValue(value)
        return box

    def _populate_variables(self) -> None:
        self._updating = True
        try:
            for row, variable in enumerate(self._variables):
                self._table.setItem(
                    row,
                    0,
                    QTableWidgetItem(self._translator.t(variable.label_key)),
                )
                self._table.setItem(
                    row,
                    1,
                    QTableWidgetItem(self._translator.t(variable.group)),
                )
                use = QTableWidgetItem("")
                use.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                use.setCheckState(
                    Qt.CheckState.Unchecked if variable.locked_by_default else Qt.CheckState.Checked
                )
                self._table.setItem(row, 2, use)
                self._table.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        self._display(variable, self._descriptor.initial_values[variable.name])
                    ),
                )
                self._table.setItem(
                    row, 4, QTableWidgetItem(self._display(variable, variable.minimum))
                )
                self._table.setItem(
                    row, 5, QTableWidgetItem(self._display(variable, variable.maximum))
                )
        finally:
            self._updating = False

    def _display(self, variable: OptimizationVariable, value: float) -> str:
        if variable.kind is VariableKind.INTEGER or variable.unit == "count":
            return f"{value:.0f}"
        if variable.unit == "deg":
            return f"{value:.1f}°"
        if variable.unit == "H":
            return f"{value * 1e6:.3f} µH"
        if variable.unit == "Hz":
            return f"{value / 1e6:.6f} MHz"
        if variable.unit == "ratio":
            return f"{value:g}:1"
        if variable.unit == "fraction":
            return f"{value * 100.0:.1f}%"
        if variable.unit == "ohm":
            return f"{value:.3f} Ω"
        if variable.unit == "radius":
            unit = self._translator.t(radius_unit_key(self._unit_system))
            return f"{radius_from_m(value, self._unit_system):.4f} {unit}"
        unit = self._translator.t(length_unit_key(self._unit_system))
        return f"{length_from_m(value, self._unit_system):.3f} {unit}"

    def _selected_indices(self) -> tuple[int, ...]:
        return tuple(
            row
            for row in range(self._table.rowCount())
            if (item := self._table.item(row, 2)) is not None
            and item.checkState() == Qt.CheckState.Checked
        )

    def _use_changed(self, item: QTableWidgetItem) -> None:
        if not self._ready or self._updating or item.column() != 2:
            return
        selected = len(self._selected_indices())
        self._locked_hint.setVisible(selected < len(self._variables))
        self._update_controls()

    def _objective_value(self) -> FamilyOptimizationObjective:
        return FamilyOptimizationObjective(str(self._objective.currentData()))

    def _objective_changed(self, *_args: object) -> None:
        objective = self._objective_value()
        target = objective is FamilyOptimizationObjective.TARGET_IMPEDANCE
        multi = objective is FamilyOptimizationObjective.MULTI_OBJECTIVE
        for widget in (
            self._target_r_label,
            self._target_x_label,
            self._target_r,
            self._target_x,
        ):
            widget.setVisible(target)
        for spin in (
            self._weight_gain,
            self._weight_fb,
            self._weight_swr,
            self._weight_efficiency,
        ):
            spin.setVisible(multi)
        for label in (
            self._weight_gain_label,
            self._weight_fb_label,
            self._weight_swr_label,
            self._weight_efficiency_label,
        ):
            label.setVisible(multi)
        self._budget_changed()

    def _budget_profile(self) -> BudgetProfile:
        return BudgetProfile(str(self._budget.currentData()))

    def _budget_changed(self, *_args: object) -> None:
        if not self._ready:
            return
        count = len(self._selected_indices())
        budget = budget_for(self._budget_profile(), max(1, count))
        multiplier = 1
        if self._objective_value() is FamilyOptimizationObjective.MAX_BANDWIDTH:
            multiplier = max(1, self._base_spec.frequency_plan.count)
        runs = (budget.total + 2 * max(1, count)) * multiplier
        key = "optimize.budget_hint_sweep" if multiplier > 1 else "optimize.budget_hint"
        self._budget_hint.setText(
            self._translator.t(
                key,
                count=runs,
                points=self._base_spec.frequency_plan.count,
            )
        )
        self._update_controls()

    def _update_controls(self) -> None:
        running = self._thread is not None
        selected = len(self._selected_indices())
        self._run.setEnabled(not running and selected > 0)
        self._cancel.setEnabled(running)
        self._apply.setEnabled(not running and self._selected_parameters is not None)
        for widget in (
            self._objective,
            self._target_r,
            self._target_x,
            self._weight_gain,
            self._weight_fb,
            self._weight_swr,
            self._weight_efficiency,
            self._budget,
            self._seed,
            self._table,
            self._max_swr_enabled,
        ):
            widget.setEnabled(not running)
        self._max_swr.setEnabled(not running and self._max_swr_enabled.isChecked())
        if running:
            self._apply.setEnabled(False)

    def _start(self) -> None:
        if self._thread is not None:
            return
        selected = self._selected_indices()
        if not selected:
            QMessageBox.critical(
                self,
                self.windowTitle(),
                self._translator.t("element_optimize.no_variables"),
            )
            return
        selected_names = {self._variables[index].name for index in selected}
        locked = frozenset(
            variable.name for variable in self._variables if variable.name not in selected_names
        )
        budget = budget_for(self._budget_profile(), len(selected))
        constraints: tuple[SoftConstraint, ...] = ()
        if self._max_swr_enabled.isChecked():
            constraints = (
                SoftConstraint(
                    metric=OptimizationMetric.SWR,
                    maximum=self._max_swr.value(),
                    weight=1.0,
                ),
            )
        self._cancel_token = EventCancelToken()
        try:
            command = OptimizeAntennaCommand(
                descriptor=self._descriptor,
                base_spec=self._base_spec,
                objective=self._objective_value(),
                budget=budget,
                weights=OptimizationWeights(
                    gain=self._weight_gain.value(),
                    front_to_back=self._weight_fb.value(),
                    swr=self._weight_swr.value(),
                    efficiency=self._weight_efficiency.value(),
                ),
                target_resistance_ohm=self._target_r.value(),
                target_reactance_ohm=self._target_x.value(),
                soft_constraints=constraints,
                locked_variables=locked,
                seed=self._seed.value(),
                cancel_token=self._cancel_token,
            )
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self.windowTitle(), str(exc))
            return
        self._result = None
        self._selected_parameters = None
        self._evaluations.setRowCount(0)
        self._summary.setText(self._translator.t("optimize.running"))
        self._sensitivity.setText("")
        self._apply.setEnabled(False)
        thread = QThread(self)
        worker = FamilyOptimizationWorker(self._solver, command)
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
            self._cancel.setEnabled(False)
            self._summary.setText(self._translator.t("optimize.running"))

    def _on_finished(self, result: OptimizeAntennaResult) -> None:
        self._result = result
        self._selected_parameters = result.best_parameters
        self._populate_evaluations(result)
        self._summary.setText(self._summary_text(result))
        self._sensitivity.setText(self._sensitivity_text(result))

    def _on_failed(self, message: str) -> None:
        self._summary.setText(self._translator.t("error.optimize", message=message))
        QMessageBox.critical(
            self,
            self.windowTitle(),
            self._translator.t("error.optimize", message=message),
        )

    def _on_thread_finished(self) -> None:
        self._thread = None
        self._worker = None
        self._cancel_token = None
        self._update_controls()

    def _populate_evaluations(self, result: OptimizeAntennaResult) -> None:
        from ...domain.optimization.engine import rank_evaluations

        ranked = rank_evaluations(result.evaluations)
        self._evaluations.setRowCount(len(ranked))
        for row, evaluation in enumerate(ranked):
            metrics = evaluation.metrics
            values = [
                str(row + 1),
                str(evaluation.index),
                self._number(evaluation.score),
                self._number(metrics.get("resistance_ohm")),
                self._number(metrics.get("reactance_ohm")),
                self._number(metrics.get("swr")),
                self._number(metrics.get("max_gain_db")),
                self._number(metrics.get("front_to_back_db")),
                self._number(metrics.get("efficiency_percent")),
                evaluation.error or "",
            ]
            for column, value in enumerate(values):
                self._evaluations.setItem(row, column, QTableWidgetItem(value))

    @staticmethod
    def _number(value: float | None) -> str:
        if value is None or not math.isfinite(value):
            return "—"
        return f"{value:.4g}"

    def _summary_text(self, result: OptimizeAntennaResult) -> str:
        status = self._translator.t(f"optimize_status.{result.status.value}")
        if result.best_score is None:
            return self._translator.t(
                "optimize.family_summary",
                status=status,
                count=len(result.evaluations),
                score="—",
            )
        return self._translator.t(
            "optimize.family_summary",
            status=status,
            count=len(result.evaluations),
            score=f"{result.best_score:.6g}",
        )

    def _sensitivity_text(self, result: OptimizeAntennaResult) -> str:
        ranked = sorted(
            (point for point in result.sensitivity if point.delta is not None),
            key=lambda point: point.delta or 0.0,
            reverse=True,
        )
        if not ranked:
            return ""
        parts = []
        for point in ranked[:5]:
            variable = next(item for item in self._variables if item.name == point.name)
            label = self._translator.t(variable.label_key)
            parts.append(f"{label}: {point.delta:.6g}")
        return self._translator.t("optimize.sensitivity") + ": " + " · ".join(parts)

    def _apply_result(self) -> None:
        if self._selected_parameters is None:
            return
        self.accept()

    def selected_parameters(self) -> AntennaDesignParameters | None:
        return self._selected_parameters

    def selected_result(self) -> OptimizeAntennaResult | None:
        return self._result

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None:
            if self._cancel_token is not None:
                self._cancel_token.cancel()
            QMessageBox.information(
                self,
                self.windowTitle(),
                self._translator.t("optimize.close_optimization"),
            )
            event.ignore()
            return
        super().closeEvent(event)
