# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generic family-driven antenna optimizer dialog."""

from __future__ import annotations

import math
import time

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
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
    MAX_SEED_RUNS,
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
from ...domain.optimization.engine import BudgetProfile, OptimizationStatus, budget_for
from ...domain.optimization.summary import (
    OptimizationMode,
    OptimizationRecommendation,
    OptimizationSummary,
    RecommendationSeverity,
)
from ...domain.optimization.variables import OptimizationVariable, VariableKind
from ...domain.simulation.spec import SimulationSpec
from ...reporting.optimizer_csv import write_optimization_csv
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from ..parallelism import MAX_UI_PARALLEL_WORKERS, default_parallel_workers
from ..units import (
    UnitSystem,
    length_bounds,
    length_from_m,
    length_to_m,
    length_unit_key,
    radius_from_m,
    radius_unit_key,
)
from ..widgets.task_progress import TaskProgressBar, TaskProgressState
from ..workers.family_optimization_worker import FamilyOptimizationWorker

_OBJECTIVE_KEYS = {
    FamilyOptimizationObjective.TARGET_IMPEDANCE: "optimize.target_impedance_objective",
    FamilyOptimizationObjective.MIN_SWR: "optimize.min_swr_edges_objective",
    FamilyOptimizationObjective.MIN_SWR_OPERATING: "optimize.min_swr_operating_objective",
    FamilyOptimizationObjective.MAX_GAIN: "optimize.max_gain_objective",
    FamilyOptimizationObjective.MAX_FRONT_TO_BACK: "element_optimize.objective.max_front_to_back",
    FamilyOptimizationObjective.MAX_EFFICIENCY: "optimize.max_efficiency_objective",
    FamilyOptimizationObjective.MAX_BANDWIDTH: "optimize.max_bandwidth_objective",
    FamilyOptimizationObjective.MULTI_OBJECTIVE: "optimize.balanced_objective",
}
THOROUGH_DEFAULT_SEED_RUNS = 3


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
        band_edges_hz: tuple[float, ...] = (),
        operating_frequencies_hz: tuple[float, ...] = (),
        last_summary: OptimizationSummary | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._solver = solver
        self._descriptor = descriptor
        self._base_spec = base_spec
        self._band_edges_hz = tuple(band_edges_hz)
        self._operating_frequencies_hz = tuple(operating_frequencies_hz)
        self._last_summary = last_summary
        self._thread: QThread | None = None
        self._worker: FamilyOptimizationWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._result: OptimizeAntennaResult | None = None
        self._selected_parameters: AntennaDesignParameters | None = None
        self._variables = descriptor.variables
        self._updating = False
        self._ready = False
        self._updating_seed_runs = False
        self._seed_runs_user_set = False
        self._run_estimated_evaluations = 0
        self._last_progress_emit = 0.0

        self.setWindowTitle(translator.t("optimize.family_title"))
        self.resize(*scaled_dialog_size(1_100, 820))

        self._objective = QComboBox(self)
        for objective in sorted(descriptor.objectives, key=lambda item: item.value):
            self._objective.addItem(translator.t(_OBJECTIVE_KEYS[objective]), objective.value)
        index = self._objective.findData(descriptor.default_objective.value)
        if index >= 0:
            self._objective.setCurrentIndex(index)
        self._objective.currentIndexChanged.connect(self._objective_changed)

        self._mode = QComboBox(self)
        for mode in (
            OptimizationMode.SINGLE,
            OptimizationMode.BAND_AWARE,
            OptimizationMode.ROBUST,
        ):
            self._mode.addItem(translator.t(f"optimize.mode.{mode.value}"), mode.value)
        self._mode.currentIndexChanged.connect(self._mode_changed)

        self._band_edges = QLineEdit(self)
        self._band_edges.setPlaceholderText(translator.t("optimize.band_edges_hint"))
        self._band_edges.setText(
            ", ".join(f"{frequency_hz / 1e6:.6f}" for frequency_hz in self._initial_band_edges())
        )

        self._robust_tolerance = QDoubleSpinBox(self)
        self._robust_tolerance.setRange(0.1, 10.0)
        self._robust_tolerance.setDecimals(2)
        self._robust_tolerance.setSingleStep(0.1)
        self._robust_tolerance.setValue(1.0)
        self._robust_tolerance.setSuffix(" %")

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
        self._budget.currentIndexChanged.connect(self._budget_profile_changed)

        self._seed = QSpinBox(self)
        self._seed.setRange(0, 2_147_483_647)
        self._seed.setValue(0)

        self._seed_runs = QSpinBox(self)
        self._seed_runs.setRange(1, MAX_SEED_RUNS)
        self._seed_runs.setValue(1)
        self._seed_runs.setToolTip(translator.t("optimize.seed_runs_hint"))
        self._seed_runs.valueChanged.connect(self._seed_runs_changed)

        self._workers = QSpinBox(self)
        self._workers.setRange(1, MAX_UI_PARALLEL_WORKERS)
        self._workers.setValue(default_parallel_workers())
        self._workers.setToolTip(translator.t("optimize.workers_hint"))

        _minimum_length, maximum_length = length_bounds(unit_system)
        self._max_boom = QDoubleSpinBox(self)
        self._max_boom.setRange(0.0, maximum_length)
        self._max_boom.setDecimals(3)
        self._max_boom.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._max_boom.setSpecialValueText(translator.t("optimize.no_limit"))
        self._max_turning = QDoubleSpinBox(self)
        self._max_turning.setRange(0.0, maximum_length)
        self._max_turning.setDecimals(3)
        self._max_turning.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        self._max_turning.setSpecialValueText(translator.t("optimize.no_limit"))
        self._max_boom.setVisible(descriptor.supports_boom_constraint)

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
        self._matching_override_warning = QLabel(
            translator.t("optimize.matching_override"),
            self,
        )
        self._matching_override_warning.setWordWrap(True)
        self._matching_override_warning.setStyleSheet("color: #8a5a00;")
        self._matching_override_warning.setVisible(base_spec.matching_network_override)
        apply_help(self._matching_override_warning, translator, "feed_matching.override")

        self._context_note = QLabel(self)
        self._context_note.setWordWrap(True)
        if descriptor.context_note_key:
            self._context_note.setText(translator.t(descriptor.context_note_key))
        self._context_note.setVisible(descriptor.context_note_key is not None)

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
        self._task_progress = TaskProgressBar(translator, self)
        self._verification = QLabel(self)
        self._verification.setWordWrap(True)
        self._sensitivity = QLabel(self)
        self._sensitivity.setWordWrap(True)
        self._last_summary_label = QLabel(self)
        self._last_summary_label.setWordWrap(True)
        if last_summary is not None:
            self._last_summary_label.setText(self._summary_line(last_summary))
        self._recommendations = QLabel(self)
        self._recommendations.setWordWrap(True)
        self._pareto_label = QLabel(translator.t("optimize.pareto"), self)
        self._pareto = QTableWidget(0, 8, self)
        self._pareto.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._pareto.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._pareto.setAlternatingRowColors(True)
        self._pareto.verticalHeader().setVisible(False)
        self._pareto.horizontalHeader().setStretchLastSection(True)
        self._pareto_label.setVisible(False)
        self._pareto.setVisible(False)

        self._run = QPushButton(translator.t("optimize.run_family"), self)
        self._cancel = QPushButton(translator.t("optimize.cancel_run"), self)
        self._export = QPushButton(translator.t("optimize.export_csv"), self)
        self._apply = QPushButton(translator.t("optimize.apply_best"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._cancel.setEnabled(False)
        self._export.setEnabled(False)
        self._apply.setEnabled(False)
        self._run.clicked.connect(self._start)
        self._cancel.clicked.connect(self._cancel_run)
        self._export.clicked.connect(self._export_csv)
        self._apply.clicked.connect(self._apply_result)
        self._close.clicked.connect(self.reject)

        self._target_r_label = QLabel(translator.t("synthesis.target_resistance"), self)
        self._target_x_label = QLabel(translator.t("synthesis.target_reactance"), self)
        self._objective_label = QLabel(translator.t("optimize.objective"), self)
        self._mode_label = QLabel(translator.t("optimize.mode"), self)
        self._band_edges_label = QLabel(translator.t("optimize.band_edges"), self)
        self._operating_frequencies_label = QLabel(self)
        self._operating_frequencies_label.setWordWrap(True)
        self._operating_frequencies_label.setVisible(False)
        self._robust_tolerance_label = QLabel(
            translator.t("optimize.robust_tolerance"),
            self,
        )
        self._budget_label = QLabel(translator.t("optimize.budget_profile"), self)
        self._seed_label = QLabel(translator.t("optimize.seed"), self)
        self._seed_runs_label = QLabel(translator.t("optimize.seed_runs"), self)
        self._workers_label = QLabel(translator.t("optimize.workers"), self)
        self._max_boom_label = QLabel(translator.t("optimize.max_boom"), self)
        self._max_turning_label = QLabel(translator.t("optimize.max_turning"), self)
        self._max_boom_label.setVisible(descriptor.supports_boom_constraint)
        self._weight_gain_label = QLabel(translator.t("optimize.gain_weight"), self)
        self._weight_fb_label = QLabel(translator.t("element_optimize.weight_fb"), self)
        self._weight_swr_label = QLabel(translator.t("optimize.swr_weight"), self)
        self._weight_efficiency_label = QLabel(translator.t("optimize.efficiency_weight"), self)

        form = QFormLayout()
        if topology_label:
            form.addRow(QLabel(translator.t("field.template"), self), QLabel(topology_label, self))
        form.addRow(self._objective_label, self._objective)
        form.addRow(self._mode_label, self._mode)
        form.addRow(self._band_edges_label, self._band_edges)
        form.addRow(self._operating_frequencies_label)
        form.addRow(self._robust_tolerance_label, self._robust_tolerance)
        form.addRow(self._target_r_label, self._target_r)
        form.addRow(self._target_x_label, self._target_x)
        form.addRow(self._weight_gain_label, self._weight_gain)
        form.addRow(self._weight_fb_label, self._weight_fb)
        form.addRow(self._weight_swr_label, self._weight_swr)
        form.addRow(self._weight_efficiency_label, self._weight_efficiency)
        form.addRow(self._budget_label, self._budget)
        form.addRow(self._seed_label, self._seed)
        form.addRow(self._seed_runs_label, self._seed_runs)
        form.addRow(self._workers_label, self._workers)
        form.addRow(self._max_boom_label, self._max_boom)
        form.addRow(self._max_turning_label, self._max_turning)
        form.addRow(self._budget_hint)
        form.addRow(self._max_swr_row)
        if descriptor.context_note_key:
            form.addRow(self._context_note)

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
        self._pareto.setHorizontalHeaderLabels(
            [
                translator.t("optimize.rank"),
                translator.t("optimize.score"),
                translator.t("table.resistance"),
                translator.t("table.reactance"),
                translator.t("table.swr"),
                translator.t("optimize.gain"),
                translator.t("yagi_optimize.front_to_back"),
                translator.t("optimize.efficiency"),
            ]
        )

        buttons = QHBoxLayout()
        buttons.addWidget(self._run)
        buttons.addWidget(self._cancel)
        buttons.addWidget(self._export)
        buttons.addStretch(1)
        buttons.addWidget(self._apply)
        buttons.addWidget(self._close)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._matching_override_warning)
        layout.addWidget(self._last_summary_label)
        layout.addWidget(self._locked_hint)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._evaluations_label)
        layout.addWidget(self._evaluations, 1)
        layout.addWidget(self._pareto_label)
        layout.addWidget(self._pareto, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._verification)
        layout.addWidget(self._sensitivity)
        layout.addWidget(self._recommendations)
        layout.addWidget(self._task_progress)
        layout.addLayout(buttons)

        self._ready = True
        self._objective_changed()
        self._mode_changed()
        self._budget_changed()
        self._update_controls()

    def _weight_spin(self, value: float) -> QDoubleSpinBox:
        box = QDoubleSpinBox(self)
        box.setRange(0.0, 100.0)
        box.setDecimals(2)
        box.setSingleStep(0.1)
        box.setValue(value)
        return box

    def _initial_band_edges(self) -> tuple[float, ...]:
        if self._band_edges_hz:
            return tuple(sorted(set(self._band_edges_hz)))
        plan = self._base_spec.frequency_plan
        if plan.is_single:
            return (
                plan.start_hz * 0.95,
                plan.start_hz,
                plan.start_hz * 1.05,
            )
        return (
            plan.start_hz,
            (plan.start_hz + plan.stop_hz) / 2.0,
            plan.stop_hz,
        )

    def _mode_value(self) -> OptimizationMode:
        return OptimizationMode(str(self._mode.currentData()))

    def _mode_changed(self, *_args: object) -> None:
        if not self._ready:
            return
        mode = self._mode_value()
        band_aware = mode is not OptimizationMode.SINGLE
        robust = mode is OptimizationMode.ROBUST
        for band_widget in (self._band_edges, self._band_edges_label):
            band_widget.setEnabled(band_aware)
        for tolerance_widget in (self._robust_tolerance, self._robust_tolerance_label):
            tolerance_widget.setEnabled(robust)
        self._update_operating_frequencies_hint()
        self._budget_changed()

    def _update_operating_frequencies_hint(self) -> None:
        visible = (
            self._objective_value() is FamilyOptimizationObjective.MIN_SWR_OPERATING
            and self._mode_value() is not OptimizationMode.SINGLE
            and bool(self._operating_frequencies_hz)
        )
        self._operating_frequencies_label.setVisible(visible)
        if not visible:
            return
        frequencies = ", ".join(
            f"{frequency_hz / 1e6:.4f} MHz" for frequency_hz in self._operating_frequencies_hz
        )
        self._operating_frequencies_label.setText(
            self._translator.t("optimize.operating_frequencies", frequencies=frequencies)
        )

    def _parse_band_edges(self) -> tuple[float, ...]:
        text = self._band_edges.text().replace(";", ",")
        try:
            values = [float(part) for part in text.split(",") if part.strip()]
        except ValueError as exc:
            raise ValueError(self._translator.t("optimize.band_edges_invalid")) from exc
        if len(values) < 2:
            raise ValueError(self._translator.t("optimize.band_edges_invalid"))
        if any(not math.isfinite(value) or value <= 0.0 for value in values):
            raise ValueError(self._translator.t("optimize.band_edges_invalid"))
        return tuple(sorted({value * 1e6 for value in values}))

    def _scenario_count(self) -> int:
        return 3 if self._mode_value() is OptimizationMode.ROBUST else 1

    def _summary_line(self, summary: OptimizationSummary) -> str:
        objective: FamilyOptimizationObjective | None
        try:
            objective = FamilyOptimizationObjective(summary.objective)
        except ValueError:
            objective = None
        if objective is None:
            objective_key = "optimize.objective"
        else:
            objective_key = _OBJECTIVE_KEYS.get(objective, "optimize.objective")
        swr_metric = (
            "operating_swr_rms"
            if objective is FamilyOptimizationObjective.MIN_SWR_OPERATING
            else "swr"
        )
        return self._translator.t(
            "optimize.last_summary",
            date=summary.completed_at.strftime("%Y-%m-%d %H:%M"),
            mode=self._translator.t(f"optimize.mode.{summary.mode.value}"),
            objective=self._translator.t(objective_key),
            status=self._translator.t(f"optimize_status.{summary.status}"),
            count=summary.evaluations,
            swr=self._number(summary.best_metrics.get(swr_metric)),
        )

    def _recommendations_text(
        self,
        recommendations: tuple[OptimizationRecommendation, ...],
    ) -> str:
        if not recommendations:
            return ""
        lines: list[str] = []
        for recommendation in recommendations:
            severity = self._translator.t(
                "optimize.recommend.warning"
                if recommendation.severity is RecommendationSeverity.WARNING
                else "optimize.recommend.info"
            )
            labels = ", ".join(
                self._translator.t(
                    next(
                        (
                            variable.label_key
                            for variable in self._variables
                            if variable.name == name
                        ),
                        name,
                    )
                )
                for name in recommendation.variables
            )
            lines.append(f"{severity}: " + self._translator.t(recommendation.key, variables=labels))
        return self._translator.t("optimize.recommendations") + ": " + "\n".join(lines)

    def _populate_pareto(self, result: OptimizeAntennaResult) -> None:
        self._pareto.setRowCount(len(result.pareto))
        for row, candidate in enumerate(result.pareto):
            metrics = candidate.metrics
            values = [
                str(row + 1),
                self._number(candidate.score),
                self._number(metrics.get("resistance_ohm")),
                self._number(metrics.get("reactance_ohm")),
                self._number(metrics.get("swr")),
                self._number(metrics.get("max_gain_db")),
                self._number(metrics.get("front_to_back_db")),
                self._number(metrics.get("efficiency_percent")),
            ]
            for column, value in enumerate(values):
                self._pareto.setItem(row, column, QTableWidgetItem(value))
        visible = bool(result.pareto)
        self._pareto_label.setVisible(visible)
        self._pareto.setVisible(visible)

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
        self._locked_hint.setVisible(len(self._selected_indices()) < len(self._variables))

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
        self._update_operating_frequencies_hint()
        self._budget_changed()

    def _budget_profile(self) -> BudgetProfile:
        return BudgetProfile(str(self._budget.currentData()))

    def _budget_profile_changed(self, *_args: object) -> None:
        if not self._ready:
            return
        if not self._seed_runs_user_set:
            self._updating_seed_runs = True
            self._seed_runs.setValue(
                THOROUGH_DEFAULT_SEED_RUNS
                if self._budget_profile() is BudgetProfile.THOROUGH
                else 1
            )
            self._updating_seed_runs = False
        self._budget_changed()

    def _seed_runs_changed(self, *_args: object) -> None:
        if not self._ready:
            return
        if not self._updating_seed_runs:
            self._seed_runs_user_set = True
        self._budget_changed()

    def _budget_changed(self, *_args: object) -> None:
        if not self._ready:
            return
        count = len(self._selected_indices())
        budget = budget_for(self._budget_profile(), max(1, count))
        multiplier = 1
        points = self._base_spec.frequency_plan.count
        key = "optimize.budget_hint"
        if self._objective_value() is FamilyOptimizationObjective.MAX_BANDWIDTH:
            multiplier = max(1, points)
            key = "optimize.budget_hint_sweep"
        elif self._mode_value() is not OptimizationMode.SINGLE:
            if (
                self._objective_value() is FamilyOptimizationObjective.MIN_SWR_OPERATING
                and self._operating_frequencies_hz
            ):
                points = len(self._operating_frequencies_hz)
            else:
                try:
                    points = len(self._parse_band_edges())
                except ValueError:
                    points = 3
            multiplier = points * self._scenario_count()
            key = "optimize.budget_hint_quality"
        seed_runs = self._seed_runs.value()
        if seed_runs > 1:
            key = f"{key}_seeds"
        runs = (budget.total + 2 * max(1, count)) * multiplier * seed_runs
        self._budget_hint.setText(
            self._translator.t(
                key,
                count=runs,
                points=points,
                scenarios=self._scenario_count(),
                seeds=seed_runs,
            )
        )
        self._update_controls()

    def _update_controls(self) -> None:
        running = self._thread is not None
        selected = len(self._selected_indices())
        self._run.setEnabled(not running and selected > 0)
        self._cancel.setEnabled(running)
        self._export.setEnabled(not running and self._result is not None)
        self._apply.setEnabled(not running and self._selected_parameters is not None)
        for widget in (
            self._objective,
            self._mode,
            self._target_r,
            self._target_x,
            self._weight_gain,
            self._weight_fb,
            self._weight_swr,
            self._weight_efficiency,
            self._budget,
            self._seed,
            self._seed_runs,
            self._workers,
            self._max_boom,
            self._max_turning,
            self._table,
            self._max_swr_enabled,
        ):
            widget.setEnabled(not running)
        mode = self._mode_value()
        self._band_edges.setEnabled(not running and mode is not OptimizationMode.SINGLE)
        self._robust_tolerance.setEnabled(not running and mode is OptimizationMode.ROBUST)
        self._max_swr.setEnabled(not running and self._max_swr_enabled.isChecked())
        if running:
            self._apply.setEnabled(False)

    def _estimated_evaluations(self) -> int:
        count = max(1, len(self._selected_indices()))
        budget = budget_for(self._budget_profile(), count)
        return max(1, (budget.total + 2 * count) * self._seed_runs.value())

    def _on_progress(self, completed: int, best_score: object) -> None:
        if self._task_progress.state is not TaskProgressState.RUNNING:
            return
        if self._run_estimated_evaluations <= 0:
            return
        now = time.monotonic()
        if now - self._last_progress_emit < 0.1 and completed < self._run_estimated_evaluations:
            return
        self._last_progress_emit = now
        total = max(1, self._run_estimated_evaluations)
        display = min(completed, max(0, total - 1))
        score = float(best_score) if isinstance(best_score, (int, float)) else None
        self._task_progress.set_progress(
            display,
            "optimize.progress",
            completed=completed,
            total=total,
            score=self._number(score),
        )

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
        mode = self._mode_value()
        try:
            band_edges = self._parse_band_edges() if mode is not OptimizationMode.SINGLE else ()
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
                seed_runs=self._seed_runs.value(),
                parallel_workers=self._workers.value(),
                mode=mode,
                band_edges_hz=band_edges,
                operating_frequencies_hz=self._operating_frequencies_hz,
                robust_tolerance=(
                    self._robust_tolerance.value() / 100.0
                    if mode is OptimizationMode.ROBUST
                    else 0.0
                ),
                max_boom_length_m=(
                    length_to_m(self._max_boom.value(), self._unit_system)
                    if self._descriptor.supports_boom_constraint and self._max_boom.value() > 0.0
                    else None
                ),
                max_turning_radius_m=(
                    length_to_m(self._max_turning.value(), self._unit_system)
                    if self._max_turning.value() > 0.0
                    else None
                ),
                budget_profile=self._budget_profile(),
                cancel_token=self._cancel_token,
            )
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self.windowTitle(), str(exc))
            return
        self._result = None
        self._selected_parameters = None
        self._evaluations.setRowCount(0)
        self._pareto.setRowCount(0)
        self._pareto_label.setVisible(False)
        self._pareto.setVisible(False)
        self._summary.setText(self._translator.t("optimize.running"))
        self._verification.setText("")
        self._sensitivity.setText("")
        self._recommendations.setText("")
        self._export.setEnabled(False)
        self._apply.setEnabled(False)
        self._run_estimated_evaluations = self._estimated_evaluations()
        self._last_progress_emit = 0.0
        self._task_progress.begin_determinate(
            self._run_estimated_evaluations,
            "optimize.running",
        )
        thread = QThread(self)
        worker = FamilyOptimizationWorker(self._solver, command)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        # The dialog owns the thread, and Python owns the worker until the
        # finished slot drops the reference after the event loop has stopped.
        # Deleting the worker explicitly from its own thread's finished signal
        # can race with Shiboken wrapper destruction on some PySide6 versions.
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
            self._task_progress.mark_cancelling("status.cancelling")

    def _on_finished(self, result: OptimizeAntennaResult) -> None:
        if result.status is OptimizationStatus.CANCELLED:
            self._task_progress.cancel("progress.cancelled")
        elif result.status is OptimizationStatus.ERROR:
            self._task_progress.fail("progress.failed")
        else:
            self._task_progress.complete(
                "optimize.progress_completed",
                count=len(result.evaluations),
            )
        self._result = result
        self._selected_parameters = result.best_parameters
        self._populate_evaluations(result)
        self._populate_pareto(result)
        self._summary.setText(self._summary_text(result))
        self._verification.setText(self._verification_text(result))
        self._sensitivity.setText(self._sensitivity_text(result))
        if result.summary is not None:
            self._last_summary_label.setText(self._summary_line(result.summary))
            self._recommendations.setText(
                self._recommendations_text(result.summary.recommendations)
            )

    def _on_failed(self, message: str) -> None:
        self._task_progress.fail("progress.failed")
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
                self._localized_error(evaluation.error),
            ]
            for column, value in enumerate(values):
                self._evaluations.setItem(row, column, QTableWidgetItem(value))

    def _localized_error(self, error: str | None) -> str:
        if not error:
            return ""
        parts = [part.strip() for part in error.split(";") if part.strip()]
        return "; ".join(
            self._translator.t(part)
            if part.startswith(("optimize.constraint.", "loaded_dipole.constraint."))
            else part
            for part in parts
        )

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

    def _verification_text(self, result: OptimizeAntennaResult) -> str:
        requested = result.best_metrics.get("seed_requested")
        if requested is None or requested <= 1.0:
            return ""
        scored = result.best_metrics.get("seed_scored_count", 0.0)
        score_spread = result.best_metrics.get("seed_score_spread", 0.0)
        parameter_spread = result.best_metrics.get("seed_parameter_spread", 0.0)
        converged = result.best_metrics.get("seed_converged", 0.0) >= 0.5
        key = (
            "optimize.seed_verification_converged"
            if converged
            else "optimize.seed_verification_diverged"
        )
        return self._translator.t(
            key,
            count=int(scored),
            requested=int(requested),
            score_spread=self._number(score_spread),
            parameter_spread=f"{parameter_spread * 100.0:.1f}",
            seed=result.seed,
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

    def _export_csv(self) -> None:
        if self._result is None:
            return
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.csv_title"),
            "optimization.csv",
            self._translator.t("dialog.csv_filter"),
        )
        if not path:
            return
        try:
            write_optimization_csv(
                path,
                self._result.evaluations,
                pareto_indices=(candidate.index for candidate in self._result.pareto),
                variable_names=tuple(variable.name for variable in self._descriptor.variables),
            )
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.windowTitle(),
                self._translator.t("error.optimize", message=str(exc)),
            )

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
