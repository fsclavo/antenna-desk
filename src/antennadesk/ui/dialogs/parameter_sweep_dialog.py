# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded 1D/2D parameter sweep dialog."""

from __future__ import annotations

import math

import pyqtgraph as pg
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QBrush, QCloseEvent, QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...application.cancellation import EventCancelToken
from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.run_parameter_sweep import RunParameterSweepCommand
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.design.sweep import (
    MAX_SWEEP_POINTS,
    ParameterSweepResult,
    SweepAxis,
    SweepMetric,
    SweepPlan,
    SweepPoint,
    axis_values,
)
from ...domain.optimization.descriptor import AntennaOptimizerDescriptor
from ...domain.optimization.variables import OptimizationVariable, VariableKind
from ...domain.projects.project import DesignVariant
from ...domain.simulation.spec import SimulationSpec
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from ..theme import theme_colors
from ..units import (
    UnitSystem,
    length_from_m,
    length_to_m,
    length_unit_key,
    radius_from_m,
    radius_to_m,
    radius_unit_key,
)
from ..widgets.task_progress import TaskProgressBar
from ..workers.parameter_sweep_worker import ParameterSweepWorker


class ParameterSweepDialog(QDialog):
    """Run a bounded what-if sweep over one or two family variables."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        solver: AntennaSolver,
        descriptor: AntennaOptimizerDescriptor,
        design: DesignVariant,
        base_spec: SimulationSpec,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._solver = solver
        self._descriptor = descriptor
        self._design = design
        self._base_spec = base_spec
        self._colors = theme_colors(self.palette())
        self._result: ParameterSweepResult | None = None
        self._selected_parameters: AntennaDesignParameters | None = None
        self._selected_point: SweepPoint | None = None
        self._thread: QThread | None = None
        self._worker: ParameterSweepWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._updating_axes = False
        self._sweep_variables = tuple(
            variable
            for variable in descriptor.variables
            if variable.kind is not VariableKind.CHOICE
        )
        self.setWindowTitle(translator.t("sweep.title"))
        self.resize(*scaled_dialog_size(1_020, 820))

        self._x_variable = QComboBox(self)
        self._x_min = QDoubleSpinBox(self)
        self._x_max = QDoubleSpinBox(self)
        self._x_count = QSpinBox(self)
        self._x_count.setRange(2, 50)
        self._x_count.setValue(11)
        self._y_variable = QComboBox(self)
        self._y_min = QDoubleSpinBox(self)
        self._y_max = QDoubleSpinBox(self)
        self._y_count = QSpinBox(self)
        self._y_count.setRange(2, 50)
        self._y_count.setValue(9)
        self._metric = QComboBox(self)
        for metric in SweepMetric:
            self._metric.addItem(
                translator.t(f"sweep.metric.{metric.value}"),
                metric.value,
            )
        self._target = QDoubleSpinBox(self)
        self._target.setRange(0.1, 1_000.0)
        self._target.setDecimals(6)
        self._target.setValue(design.parameters.frequency_hz / 1e6)
        self._target.setSuffix(" MHz")
        self._budget = QLabel(self)
        self._budget.setWordWrap(True)
        self._budget_warning = QLabel(self)
        self._budget_warning.setWordWrap(True)
        self._budget_warning.setStyleSheet(f"color: {self._colors.reactance.name()};")
        self._validation = QLabel(self)
        self._validation.setWordWrap(True)
        self._validation.setStyleSheet(f"color: {self._colors.feed.name()};")
        self._validation.hide()

        self._run = QPushButton(translator.t("sweep.run"), self)
        self._cancel = QPushButton(translator.t("sweep.cancel"), self)
        self._apply_selected = QPushButton(translator.t("sweep.apply_selected"), self)
        self._apply_best = QPushButton(translator.t("sweep.apply_best"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._run.clicked.connect(self._start)
        self._cancel.clicked.connect(self._cancel_run)
        self._apply_selected.clicked.connect(self._apply_selected_point)
        self._apply_best.clicked.connect(self._apply_best_point)
        self._close.clicked.connect(self.reject)
        self._cancel.setEnabled(False)
        self._apply_selected.setEnabled(False)
        self._apply_best.setEnabled(False)
        for button, key in (
            (self._run, "sweep.run"),
            (self._cancel, "sweep.cancel"),
            (self._apply_selected, "sweep.apply_selected"),
            (self._apply_best, "sweep.apply_best"),
        ):
            apply_help(button, translator, key)

        self._progress = TaskProgressBar(translator, self)
        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._selection = QLabel(self)
        self._selection.setWordWrap(True)
        self._axis_hint = QLabel(self)
        self._axis_hint.setWordWrap(True)
        self._axis_hint.hide()

        self._plot = pg.PlotWidget(self)
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.addLegend()
        apply_help(self._plot, translator, "sweep.plot")

        self._table = QTableWidget(0, 0, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.itemSelectionChanged.connect(self._selection_changed)
        apply_help(self._table, translator, "sweep.table")

        self._splitter = QSplitter(Qt.Orientation.Vertical, self)
        self._splitter.addWidget(self._plot)
        self._splitter.addWidget(self._table)
        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 2)

        axis_group = QGroupBox(translator.t("sweep.axes"), self)
        self._axis_group = axis_group
        axis_form = QFormLayout(axis_group)
        self._axis_form = axis_form
        axis_form.addRow(translator.t("sweep.x_axis"), self._x_variable)
        axis_form.addRow(translator.t("sweep.from"), self._x_min)
        axis_form.addRow(translator.t("sweep.to"), self._x_max)
        axis_form.addRow(translator.t("sweep.points"), self._x_count)
        axis_form.addRow(translator.t("sweep.y_axis"), self._y_variable)
        axis_form.addRow(translator.t("sweep.from"), self._y_min)
        axis_form.addRow(translator.t("sweep.to"), self._y_max)
        axis_form.addRow(translator.t("sweep.points"), self._y_count)
        axis_form.addRow(translator.t("sweep.metric"), self._metric)
        axis_form.addRow(translator.t("sweep.target"), self._target)
        axis_form.addRow(self._budget)
        axis_form.addRow(self._budget_warning)
        apply_help(axis_group, translator, "sweep.axes")
        apply_help(self._x_variable, translator, "sweep.variable")
        apply_help(self._y_variable, translator, "sweep.variable")
        apply_help(self._metric, translator, "sweep.metric")
        apply_help(self._target, translator, "sweep.target")

        actions = QHBoxLayout()
        actions.addWidget(self._run)
        actions.addWidget(self._cancel)
        actions.addWidget(self._progress, 1)
        actions.addWidget(self._apply_selected)
        actions.addWidget(self._apply_best)
        actions.addWidget(self._close)

        layout = QVBoxLayout(self)
        layout.addWidget(axis_group)
        layout.addWidget(self._validation)
        layout.addWidget(self._summary)
        layout.addWidget(self._selection)
        layout.addWidget(self._axis_hint)
        layout.addWidget(self._splitter, 1)
        layout.addLayout(actions)

        self._x_variable.currentIndexChanged.connect(self._x_variable_changed)
        self._y_variable.currentIndexChanged.connect(self._y_variable_changed)
        for spin in (self._x_min, self._x_max, self._y_min, self._y_max):
            spin.valueChanged.connect(self._update_budget)
        for count_spin in (self._x_count, self._y_count):
            count_spin.valueChanged.connect(self._update_budget)
        self._metric.currentIndexChanged.connect(self._update_budget)
        self._target.valueChanged.connect(self._update_budget)

        self._populate_variables()
        self.retranslate()
        self._update_budget()

    def selected_parameters(self) -> AntennaDesignParameters | None:
        return self._selected_parameters

    def sweep_result(self) -> ParameterSweepResult | None:
        return self._result

    def _populate_variables(self) -> None:
        current_x = self._x_variable.currentData()
        current_y = self._y_variable.currentData()
        self._updating_axes = True
        self._x_variable.clear()
        self._y_variable.clear()
        self._y_variable.addItem(self._translator.t("sweep.none"), None)
        for variable in self._sweep_variables:
            label = self._translator.t(variable.label_key)
            group = self._translator.t(variable.group)
            text = f"{label} · {group}"
            self._x_variable.addItem(text, variable.name)
            self._y_variable.addItem(text, variable.name)
        if current_x is not None:
            index = self._x_variable.findData(current_x)
            if index >= 0:
                self._x_variable.setCurrentIndex(index)
        if current_y is not None:
            index = self._y_variable.findData(current_y)
            if index >= 0:
                self._y_variable.setCurrentIndex(index)
        self._updating_axes = False
        if self._x_variable.count() == 0:
            self._validation.setText(self._translator.t("sweep.no_variables"))
            self._validation.show()
            self._run.setEnabled(False)
            self._x_variable.setEnabled(False)
            self._y_variable.setEnabled(False)
            return
        self._configure_axis(
            self._x_variable,
            self._x_min,
            self._x_max,
            self._x_count,
            default_count=11,
        )
        self._configure_axis(
            self._y_variable,
            self._y_min,
            self._y_max,
            self._y_count,
            default_count=9,
        )

    def _variable(self, combo: QComboBox) -> OptimizationVariable | None:
        name = combo.currentData()
        if not isinstance(name, str):
            return None
        return next(
            (variable for variable in self._sweep_variables if variable.name == name),
            None,
        )

    def _configure_axis(
        self,
        variable_combo: QComboBox,
        minimum: QDoubleSpinBox,
        maximum: QDoubleSpinBox,
        count: QSpinBox,
        *,
        default_count: int,
    ) -> None:
        variable = self._variable(variable_combo)
        self._updating_axes = True
        try:
            if variable is None:
                minimum.setEnabled(False)
                maximum.setEnabled(False)
                count.setEnabled(False)
                return
            minimum.setEnabled(True)
            maximum.setEnabled(True)
            count.setEnabled(True)
            suffix = self._unit_suffix(variable.unit)
            decimals = self._decimals(variable.unit)
            minimum.setDecimals(decimals)
            maximum.setDecimals(decimals)
            minimum.setSuffix(suffix)
            maximum.setSuffix(suffix)
            low = self._to_display(variable.unit, variable.minimum)
            high = self._to_display(variable.unit, variable.maximum)
            minimum.setRange(low, high)
            maximum.setRange(low, high)
            minimum.setValue(low)
            maximum.setValue(high)
            step = abs(self._to_display(variable.unit, variable.step))
            minimum.setSingleStep(max(step, 10 ** (-decimals)))
            maximum.setSingleStep(max(step, 10 ** (-decimals)))
            count.setValue(min(max(default_count, 2), 50))
        finally:
            self._updating_axes = False

    def _unit_suffix(self, unit: str) -> str:
        text = self._unit_text(unit)
        return f" {text}" if text else ""

    def _unit_text(self, unit: str) -> str:
        if unit == "m":
            return self._translator.t(length_unit_key(self._unit_system))
        if unit == "radius":
            return self._translator.t(radius_unit_key(self._unit_system))
        if unit == "H":
            return "µH"
        if unit == "deg":
            return "°"
        if unit == "count":
            return ""
        return unit

    def _decimals(self, unit: str) -> int:
        if unit in {"m", "radius"}:
            return 4
        if unit == "H":
            return 6
        if unit == "deg":
            return 1
        if unit == "count":
            return 0
        return 3

    def _to_display(self, unit: str, value: float) -> float:
        if unit == "m":
            return length_from_m(value, self._unit_system)
        if unit == "radius":
            return radius_from_m(value, self._unit_system)
        if unit == "H":
            return value * 1e6
        return value

    def _from_display(self, unit: str, value: float) -> float:
        if unit == "m":
            return length_to_m(value, self._unit_system)
        if unit == "radius":
            return radius_to_m(value, self._unit_system)
        if unit == "H":
            return value * 1e-6
        return value

    def _axis(
        self,
        variable_combo: QComboBox,
        minimum: QDoubleSpinBox,
        maximum: QDoubleSpinBox,
        count: QSpinBox,
    ) -> SweepAxis | None:
        variable = self._variable(variable_combo)
        if variable is None:
            return None
        low = self._from_display(variable.unit, minimum.value())
        high = self._from_display(variable.unit, maximum.value())
        if high <= low:
            self._show_validation(self._translator.t("sweep.error.range"))
            return None
        try:
            values = axis_values(variable, low, high, count.value())
        except ValueError as exc:
            self._show_validation(str(exc))
            return None
        return SweepAxis(
            name=variable.name,
            label_key=variable.label_key,
            unit=variable.unit,
            values=values,
        )

    def _plan(self) -> SweepPlan | None:
        x_axis = self._axis(self._x_variable, self._x_min, self._x_max, self._x_count)
        if x_axis is None:
            return None
        y_axis = None
        if self._y_variable.currentData() is not None:
            if self._y_variable.currentData() == self._x_variable.currentData():
                self._show_validation(self._translator.t("sweep.error.duplicate"))
                return None
            y_axis = self._axis(
                self._y_variable,
                self._y_min,
                self._y_max,
                self._y_count,
            )
            if y_axis is None:
                return None
        points = x_axis.count * (y_axis.count if y_axis is not None else 1)
        if points > MAX_SWEEP_POINTS:
            self._show_validation(
                self._translator.t("sweep.error.too_many", maximum=MAX_SWEEP_POINTS)
            )
            return None
        try:
            plan = SweepPlan(
                x_axis=x_axis,
                y_axis=y_axis,
                metric=SweepMetric(str(self._metric.currentData())),
                target_frequency_hz=self._target.value() * 1e6,
            )
        except ValueError as exc:
            self._show_validation(str(exc))
            return None
        self._validation.hide()
        return plan

    def _show_validation(self, message: str) -> None:
        self._validation.setText(message)
        self._validation.show()

    def _update_budget(self, *_args: object) -> None:
        if self._updating_axes:
            return
        plan = self._plan()
        if plan is None:
            self._budget.setText(self._translator.t("sweep.budget_unavailable"))
            self._budget_warning.clear()
            self._run.setEnabled(False)
            return
        if plan.y_axis is None:
            self._budget.setText(
                self._translator.t(
                    "sweep.budget_1d",
                    runs=plan.point_count,
                    x=plan.x_axis.count,
                )
            )
        else:
            self._budget.setText(
                self._translator.t(
                    "sweep.budget_2d",
                    runs=plan.point_count,
                    x=plan.x_axis.count,
                    y=plan.y_axis.count,
                )
            )
        self._budget_warning.setText(
            self._translator.t("sweep.budget_warning", runs=plan.point_count)
            if plan.point_count > 100
            else ""
        )
        self._run.setEnabled(self._thread is None)

    def _x_variable_changed(self) -> None:
        if self._updating_axes:
            return
        if self._y_variable.currentData() == self._x_variable.currentData():
            self._y_variable.setCurrentIndex(0)
        self._configure_axis(
            self._x_variable,
            self._x_min,
            self._x_max,
            self._x_count,
            default_count=11,
        )
        self._update_budget()

    def _y_variable_changed(self) -> None:
        if self._updating_axes:
            return
        self._configure_axis(
            self._y_variable,
            self._y_min,
            self._y_max,
            self._y_count,
            default_count=9,
        )
        self._update_budget()

    def _set_running(self, running: bool) -> None:
        for widget in (
            self._x_variable,
            self._x_min,
            self._x_max,
            self._x_count,
            self._y_variable,
            self._y_min,
            self._y_max,
            self._y_count,
            self._metric,
            self._target,
        ):
            widget.setEnabled(not running)
        self._run.setEnabled(not running and self._plan() is not None)
        self._cancel.setEnabled(running)
        self._apply_selected.setEnabled(not running and self._selected_point is not None)
        self._apply_best.setEnabled(
            not running and self._result is not None and self._result.best_swr_point is not None
        )

    def _start(self) -> None:
        if self._thread is not None:
            return
        plan = self._plan()
        if plan is None:
            return
        self._result = None
        self._selected_parameters = None
        self._selected_point = None
        self._table.clear()
        self._table.setRowCount(0)
        self._table.setColumnCount(0)
        self._plot.clear()
        self._plot.show()
        self._axis_hint.hide()
        self._summary.clear()
        self._selection.clear()
        self._apply_selected.setEnabled(False)
        self._apply_best.setEnabled(False)
        self._progress.begin_determinate(
            plan.point_count,
            "sweep.progress",
            completed=0,
            total=plan.point_count,
        )
        self._cancel_token = EventCancelToken()
        command = RunParameterSweepCommand(
            descriptor=self._descriptor,
            base_spec=self._base_spec,
            plan=plan,
            cancel_token=self._cancel_token,
        )
        self._thread = QThread(self)
        self._worker = ParameterSweepWorker(self._solver, command)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._thread.finished.connect(self._cleanup)
        self._set_running(True)
        self._thread.start()

    def _on_progress(self, completed: int, total: int) -> None:
        self._progress.set_progress(
            completed,
            "sweep.progress",
            completed=completed,
            total=total,
        )

    def _on_finished(self, result: ParameterSweepResult) -> None:
        self._result = result
        self._show_result(result)
        if result.cancelled:
            self._progress.cancel("sweep.cancelled")
        else:
            self._progress.complete("sweep.progress_done")
        self._set_running(False)
        if self._thread is not None:
            self._thread.quit()

    def _on_failed(self, message: str) -> None:
        self._summary.setText(f"{self._translator.t('sweep.failed')} {message}")
        self._progress.fail("sweep.failed")
        self._set_running(False)
        if self._thread is not None:
            self._thread.quit()

    def _cleanup(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
        if self._thread is not None:
            self._thread.deleteLater()
        self._worker = None
        self._thread = None
        self._cancel_token = None

    def _cancel_run(self) -> None:
        if self._cancel_token is None:
            return
        self._cancel_token.cancel()
        self._cancel.setEnabled(False)
        self._progress.mark_cancelling("sweep.cancelling")

    def _show_result(self, result: ParameterSweepResult) -> None:
        self._selected_point = None
        self._selected_parameters = None
        self._selection.clear()
        self._apply_selected.setEnabled(False)
        plan = result.plan
        best = result.best_swr_point
        best_text = "—" if best is None else f"{best.swr:.3f}"
        summary_key = "sweep.summary_cancelled" if result.cancelled else "sweep.summary"
        self._summary.setText(
            self._translator.t(
                summary_key,
                completed=result.completed_count,
                total=plan.point_count,
                valid=result.valid_count,
                best=best_text,
            )
        )
        self._apply_best.setEnabled(best is not None)
        if plan.y_axis is None:
            self._show_1d_result(result)
        else:
            self._show_2d_result(result)

    def _show_1d_result(self, result: ParameterSweepResult) -> None:
        plan = result.plan
        self._plot.show()
        self._axis_hint.hide()
        self._plot.clear()
        self._plot.setTitle(
            self._translator.t(
                "sweep.plot_title",
                metric=self._translator.t(f"sweep.metric.{plan.metric.value}"),
            ),
            color=self._colors.text,
        )
        x_label = self._axis_label(plan.x_axis)
        self._plot.setLabel("bottom", x_label, color=self._colors.text)
        points = list(result.points)
        x_values = [self._to_display(plan.x_axis.unit, point.x_value) for point in points]
        if plan.metric is SweepMetric.SWR:
            self._plot.setLabel("left", "SWR", color=self._colors.text)
            self._plot.plot(
                x_values,
                [self._finite_or_nan(point.swr) for point in points],
                pen=pg.mkPen(self._colors.swr, width=2),
                name="SWR",
                connect="finite",
            )
        else:
            self._plot.setLabel("left", "Impedance (Ω)", color=self._colors.text)
            series = (
                ("R", self._colors.resistance, [point.resistance_ohm for point in points]),
                ("X", self._colors.reactance, [point.reactance_ohm for point in points]),
                (
                    "|Z|",
                    self._colors.pattern,
                    [point.impedance_magnitude_ohm for point in points],
                ),
            )
            for name, color, series_values in series:
                self._plot.plot(
                    x_values,
                    [self._finite_or_nan(value) for value in series_values],
                    pen=pg.mkPen(color, width=2),
                    name=name,
                    connect="finite",
                )
        current_value = self._descriptor.initial_values.get(plan.x_axis.name)
        if current_value is not None:
            self._plot.addLine(
                x=self._to_display(plan.x_axis.unit, current_value),
                pen=pg.mkPen(
                    self._colors.secondary_text,
                    width=1,
                    style=Qt.PenStyle.DashLine,
                ),
            )
        self._table.verticalHeader().setVisible(False)
        self._table.setRowCount(len(points))
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            [
                self._axis_label(plan.x_axis),
                "SWR",
                "R (Ω)",
                "X (Ω)",
                "|Z| (Ω)",
                self._translator.t("sweep.status"),
            ]
        )
        best = result.best_swr_point
        self._table.blockSignals(True)
        try:
            for row, point in enumerate(points):
                row_values = (
                    self._format_axis_value(plan.x_axis, point.x_value),
                    self._format_metric(point.swr),
                    self._format_metric(point.resistance_ohm),
                    self._format_metric(point.reactance_ohm),
                    self._format_metric(point.impedance_magnitude_ohm),
                    (
                        self._translator.t("sweep.best_swr")
                        if point is best
                        else (
                            self._translator.t("sweep.valid")
                            if point.valid
                            else self._error_text(point.error)
                        )
                    ),
                )
                for column, value in enumerate(row_values):
                    item = QTableWidgetItem(value)
                    item.setData(Qt.ItemDataRole.UserRole, row)
                    if column > 0:
                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                        )
                    if not point.valid:
                        item.setToolTip(point.error)
                    if point is best:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    self._table.setItem(row, column, item)
        finally:
            self._table.blockSignals(False)
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

    def _show_2d_result(self, result: ParameterSweepResult) -> None:
        plan = result.plan
        if plan.y_axis is None:
            return
        self._plot.hide()
        self._axis_hint.show()
        self._axis_hint.setText(
            self._translator.t(
                "sweep.heatmap_hint",
                x=self._axis_label(plan.x_axis),
                y=self._axis_label(plan.y_axis),
                metric=self._translator.t(f"sweep.metric.{plan.metric.value}"),
            )
        )
        x_count = plan.x_axis.count
        y_count = plan.y_axis.count
        self._table.verticalHeader().setVisible(True)
        self._table.setRowCount(y_count)
        self._table.setColumnCount(x_count)
        self._table.setHorizontalHeaderLabels(
            [self._format_axis_value(plan.x_axis, value) for value in plan.x_axis.values]
        )
        self._table.setVerticalHeaderLabels(
            [self._format_axis_value(plan.y_axis, value) for value in plan.y_axis.values]
        )
        metric_values = [
            point.metric(plan.metric)
            for point in result.points
            if point.valid and point.metric(plan.metric) is not None
        ]
        finite_values = [
            value for value in metric_values if value is not None and math.isfinite(value)
        ]
        low = min(finite_values) if finite_values else None
        high = max(finite_values) if finite_values else None
        low_color = self._colors.swr
        high_color = self._colors.feed
        self._table.blockSignals(True)
        try:
            for row in range(y_count):
                for column in range(x_count):
                    index = row * x_count + column
                    if index >= len(result.points):
                        item = QTableWidgetItem("—")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setBackground(QBrush(self._colors.light_line))
                        self._table.setItem(row, column, item)
                        continue
                    point = result.points[index]
                    value = point.metric(plan.metric)
                    item = QTableWidgetItem(self._format_metric(value) if point.valid else "—")
                    item.setData(Qt.ItemDataRole.UserRole, index)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if point.valid and value is not None and low is not None and high is not None:
                        ratio = (
                            0.5
                            if math.isclose(low, high, rel_tol=0.0, abs_tol=1e-15)
                            else (value - low) / (high - low)
                        )
                        color = self._blend(low_color, high_color, ratio)
                        item.setBackground(QBrush(color))
                        item.setForeground(
                            QBrush(
                                QColor("#ffffff") if color.lightness() < 128 else QColor("#222222")
                            )
                        )
                    elif not point.valid:
                        item.setBackground(QBrush(self._colors.light_line))
                    item.setToolTip(
                        point.error
                        if point.error
                        else self._translator.t(
                            "sweep.cell_tooltip",
                            swr=self._format_metric(point.swr),
                            r=self._format_metric(point.resistance_ohm),
                            x=self._format_metric(point.reactance_ohm),
                            z=self._format_metric(point.impedance_magnitude_ohm),
                        )
                    )
                    self._table.setItem(row, column, item)
        finally:
            self._table.blockSignals(False)
        self._table.resizeColumnsToContents()

    def _blend(self, low: QColor, high: QColor, ratio: float) -> QColor:
        ratio = min(max(ratio, 0.0), 1.0)
        return QColor(
            round(low.red() + (high.red() - low.red()) * ratio),
            round(low.green() + (high.green() - low.green()) * ratio),
            round(low.blue() + (high.blue() - low.blue()) * ratio),
        )

    def _axis_label(self, axis: SweepAxis) -> str:
        unit = self._unit_text(axis.unit)
        label = self._translator.t(axis.label_key)
        return f"{label} ({unit})" if unit else label

    def _format_axis_value(self, axis: SweepAxis, value: float) -> str:
        display = self._to_display(axis.unit, value)
        unit = self._unit_text(axis.unit)
        text = f"{display:.{self._decimals(axis.unit)}f}"
        return f"{text} {unit}" if unit else text

    @staticmethod
    def _format_metric(value: float | None) -> str:
        if value is None or not math.isfinite(value):
            return "—"
        return f"{value:.3f}"

    @staticmethod
    def _finite_or_nan(value: float | None) -> float:
        return value if value is not None and math.isfinite(value) else math.nan

    def _error_text(self, error: str) -> str:
        if not error:
            return ""
        translated = self._translator.t(error)
        return error if translated == error else translated

    def _selection_changed(self) -> None:
        if self._result is None:
            return
        plan = self._result.plan
        index: int | None = None
        if plan.y_axis is None:
            row = self._table.currentRow()
            if 0 <= row < len(self._result.points):
                index = row
        else:
            item = self._table.currentItem()
            if item is not None:
                data = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(data, int):
                    index = data
        if index is None:
            self._selected_point = None
            self._selected_parameters = None
            self._selection.clear()
            self._apply_selected.setEnabled(False)
            return
        point = self._result.points[index]
        self._selected_point = point
        self._selection.setText(
            self._translator.t(
                "sweep.selected",
                x=self._format_axis_value(plan.x_axis, point.x_value),
                y=(
                    self._format_axis_value(plan.y_axis, point.y_value)
                    if plan.y_axis is not None and point.y_value is not None
                    else "—"
                ),
                swr=self._format_metric(point.swr),
                r=self._format_metric(point.resistance_ohm),
                x_reactance=self._format_metric(point.reactance_ohm),
                z=self._format_metric(point.impedance_magnitude_ohm),
            )
        )
        if point.valid:
            values = dict(self._descriptor.initial_values)
            values[plan.x_axis.name] = point.x_value
            if plan.y_axis is not None and point.y_value is not None:
                values[plan.y_axis.name] = point.y_value
            try:
                self._selected_parameters = self._descriptor.build_parameters(values)
            except Exception:
                self._selected_parameters = None
        else:
            self._selected_parameters = None
        self._apply_selected.setEnabled(
            self._selected_parameters is not None and self._thread is None
        )

    def _apply_selected_point(self) -> None:
        if self._selected_parameters is None:
            return
        self.accept()

    def _apply_best_point(self) -> None:
        if self._result is None:
            return
        point = self._result.best_swr_point
        if point is None:
            return
        plan = self._result.plan
        values = dict(self._descriptor.initial_values)
        values[plan.x_axis.name] = point.x_value
        if plan.y_axis is not None and point.y_value is not None:
            values[plan.y_axis.name] = point.y_value
        try:
            self._selected_parameters = self._descriptor.build_parameters(values)
        except Exception:
            self._selected_parameters = None
            return
        self.accept()

    def retranslate(self) -> None:
        t = self._translator.t
        self.setWindowTitle(t("sweep.title"))
        self._axis_group.setTitle(t("sweep.axes"))
        self._y_variable.setItemText(0, t("sweep.none"))
        for combo in (self._x_variable, self._y_variable):
            for index in range(combo.count()):
                name = combo.itemData(index)
                if not isinstance(name, str):
                    continue
                variable = next(
                    (item for item in self._sweep_variables if item.name == name),
                    None,
                )
                if variable is not None:
                    combo.setItemText(
                        index,
                        f"{t(variable.label_key)} · {t(variable.group)}",
                    )
        for index, metric in enumerate(SweepMetric):
            self._metric.setItemText(index, t(f"sweep.metric.{metric.value}"))
        self._run.setText(t("sweep.run"))
        self._cancel.setText(t("sweep.cancel"))
        self._apply_selected.setText(t("sweep.apply_selected"))
        self._apply_best.setText(t("sweep.apply_best"))
        self._close.setText(t("action.close"))
        for widget, key in (
            (self._x_variable, "sweep.x_axis"),
            (self._x_min, "sweep.from"),
            (self._x_max, "sweep.to"),
            (self._x_count, "sweep.points"),
            (self._y_variable, "sweep.y_axis"),
            (self._y_min, "sweep.from"),
            (self._y_max, "sweep.to"),
            (self._y_count, "sweep.points"),
            (self._metric, "sweep.metric"),
            (self._target, "sweep.target"),
        ):
            label = self._axis_form.labelForField(widget)
            if isinstance(label, QLabel):
                label.setText(t(key))
        self._progress.retranslate()
        apply_help(self._plot, self._translator, "sweep.plot")
        apply_help(self._table, self._translator, "sweep.table")
        if self._result is not None:
            self._show_result(self._result)
        else:
            self._update_budget()

    def reject(self) -> None:
        if self._thread is not None:
            self._cancel_run()
            return
        super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None:
            self._cancel_run()
            event.ignore()
            return
        super().closeEvent(event)
