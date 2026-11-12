# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Tolerance and robustness analysis dialog."""

from __future__ import annotations

import math

import pyqtgraph as pg
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...application.cancellation import EventCancelToken
from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.run_robustness import RunRobustnessCommand
from ...domain.design.robustness import (
    MAX_CORNER_DIMENSIONS,
    MAX_ROBUSTNESS_RUNS,
    ROBUSTNESS_DIMENSION_UNITS,
    RobustnessResult,
    RobustnessSpec,
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
    length_unit_key,
    radius_from_m,
    radius_unit_key,
)
from ..widgets.task_progress import TaskProgressBar
from ..workers.robustness_worker import RobustnessWorker


class RobustnessDialog(QDialog):
    """Corner-case and Monte Carlo tolerance analysis for critical dimensions."""

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
        self._result: RobustnessResult | None = None
        self._thread: QThread | None = None
        self._worker: RobustnessWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._variables = tuple(
            variable
            for variable in descriptor.variables
            if variable.kind is VariableKind.CONTINUOUS
            and variable.unit in ROBUSTNESS_DIMENSION_UNITS
        )
        self.setWindowTitle(translator.t("robustness.title"))
        self.resize(*scaled_dialog_size(1_020, 820))

        self._variables_list = QListWidget(self)
        for variable in self._variables:
            item = QListWidgetItem(
                f"{translator.t(variable.label_key)} · {translator.t(variable.group)}"
            )
            item.setData(Qt.ItemDataRole.UserRole, variable.name)
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsSelectable
            )
            item.setCheckState(
                Qt.CheckState.Checked
                if self._variables.index(variable) < MAX_CORNER_DIMENSIONS
                else Qt.CheckState.Unchecked
            )
            self._variables_list.addItem(item)
        self._variables_list.itemChanged.connect(self._update_budget)
        apply_help(self._variables_list, translator, "robustness.variables")

        self._tolerance = QDoubleSpinBox(self)
        self._tolerance.setRange(0.1, 10.0)
        self._tolerance.setDecimals(2)
        self._tolerance.setSingleStep(0.1)
        self._tolerance.setValue(2.0)
        self._tolerance.setSuffix(" %")
        apply_help(self._tolerance, translator, "robustness.tolerance")
        self._corners = QCheckBox(translator.t("robustness.include_corners"), self)
        self._corners.setChecked(True)
        self._corners.toggled.connect(self._update_budget)
        apply_help(self._corners, translator, "robustness.corners")
        self._samples = QSpinBox(self)
        self._samples.setRange(0, 200)
        self._samples.setValue(30)
        self._samples.valueChanged.connect(self._update_budget)
        apply_help(self._samples, translator, "robustness.samples")
        self._seed = QSpinBox(self)
        self._seed.setRange(0, 999_999)
        self._seed.setValue(0)
        self._seed.valueChanged.connect(self._update_budget)
        apply_help(self._seed, translator, "robustness.seed")
        self._swr_limit = QDoubleSpinBox(self)
        self._swr_limit.setRange(1.1, 10.0)
        self._swr_limit.setDecimals(2)
        self._swr_limit.setValue(2.0)
        self._swr_limit.valueChanged.connect(self._update_budget)
        apply_help(self._swr_limit, translator, "robustness.swr_limit")
        self._target = QDoubleSpinBox(self)
        self._target.setRange(0.1, 1_000.0)
        self._target.setDecimals(6)
        self._target.setValue(design.parameters.frequency_hz / 1e6)
        self._target.setSuffix(" MHz")
        self._target.valueChanged.connect(self._update_budget)
        apply_help(self._target, translator, "robustness.target")
        self._budget = QLabel(self)
        self._budget.setWordWrap(True)
        self._budget_warning = QLabel(self)
        self._budget_warning.setWordWrap(True)
        self._budget_warning.setStyleSheet(f"color: {self._colors.reactance.name()};")
        self._validation = QLabel(self)
        self._validation.setWordWrap(True)
        self._validation.setStyleSheet(f"color: {self._colors.feed.name()};")
        self._validation.hide()

        self._run = QPushButton(translator.t("robustness.run"), self)
        self._cancel = QPushButton(translator.t("robustness.cancel"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._run.clicked.connect(self._start)
        self._cancel.clicked.connect(self._cancel_run)
        self._close.clicked.connect(self.reject)
        self._cancel.setEnabled(False)
        for button, key in (
            (self._run, "robustness.run"),
            (self._cancel, "robustness.cancel"),
        ):
            apply_help(button, translator, key)

        self._progress = TaskProgressBar(translator, self)
        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._corner_summary = QLabel(self)
        self._corner_summary.setWordWrap(True)
        self._mc_summary = QLabel(self)
        self._mc_summary.setWordWrap(True)
        self._plot = pg.PlotWidget(self)
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        apply_help(self._plot, translator, "robustness.plot")
        self._table = QTableWidget(0, 7, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        apply_help(self._table, translator, "robustness.table")

        variables_group = QGroupBox(translator.t("robustness.critical_dimensions"), self)
        self._variables_group = variables_group
        variables_layout = QVBoxLayout(variables_group)
        variables_layout.addWidget(self._variables_list)
        self._variables_hint = QLabel(translator.t("robustness.variables_hint"), self)
        self._variables_hint.setWordWrap(True)
        variables_layout.addWidget(self._variables_hint)

        settings_group = QGroupBox(translator.t("robustness.settings"), self)
        self._settings_group = settings_group
        self._settings_form = QFormLayout(settings_group)
        self._settings_form.addRow(translator.t("robustness.tolerance"), self._tolerance)
        self._settings_form.addRow(self._corners)
        self._settings_form.addRow(translator.t("robustness.samples"), self._samples)
        self._settings_form.addRow(translator.t("robustness.seed"), self._seed)
        self._settings_form.addRow(translator.t("robustness.swr_limit"), self._swr_limit)
        self._settings_form.addRow(translator.t("robustness.target"), self._target)
        self._settings_form.addRow(self._budget)
        self._settings_form.addRow(self._budget_warning)

        actions = QHBoxLayout()
        actions.addWidget(self._run)
        actions.addWidget(self._cancel)
        actions.addWidget(self._progress, 1)
        actions.addStretch(1)
        actions.addWidget(self._close)

        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(variables_group, 1)
        top.addWidget(settings_group, 1)
        layout.addLayout(top)
        layout.addWidget(self._validation)
        layout.addWidget(self._summary)
        layout.addWidget(self._corner_summary)
        layout.addWidget(self._mc_summary)
        layout.addWidget(self._plot, 2)
        layout.addWidget(self._table, 2)
        layout.addLayout(actions)

        self.retranslate()
        self._update_budget()

    def robustness_result(self) -> RobustnessResult | None:
        return self._result

    def _selected_variables(self) -> tuple[OptimizationVariable, ...]:
        names: list[str] = []
        for row in range(self._variables_list.count()):
            item = self._variables_list.item(row)
            if item.checkState() is Qt.CheckState.Checked:
                name = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(name, str):
                    names.append(name)
        return tuple(variable for variable in self._variables if variable.name in names)

    def _spec(self) -> RobustnessSpec | None:
        variables = self._selected_variables()
        if not variables:
            self._show_validation(self._translator.t("robustness.no_variables"))
            return None
        if len(variables) > MAX_CORNER_DIMENSIONS:
            self._show_validation(
                self._translator.t(
                    "robustness.too_many_variables",
                    maximum=MAX_CORNER_DIMENSIONS,
                )
            )
            return None
        try:
            spec = RobustnessSpec(
                target_frequency_hz=self._target.value() * 1e6,
                tolerance=self._tolerance.value() / 100.0,
                variable_names=tuple(variable.name for variable in variables),
                include_corners=self._corners.isChecked(),
                monte_carlo_samples=self._samples.value(),
                seed=self._seed.value(),
                swr_limit=self._swr_limit.value(),
            )
        except ValueError as exc:
            self._show_validation(str(exc))
            return None
        if spec.total_runs > MAX_ROBUSTNESS_RUNS:
            self._show_validation(
                self._translator.t(
                    "robustness.too_many_runs",
                    maximum=MAX_ROBUSTNESS_RUNS,
                )
            )
            return None
        self._validation.hide()
        return spec

    def _show_validation(self, message: str) -> None:
        self._validation.setText(message)
        self._validation.show()

    def _update_budget(self, *_args: object) -> None:
        spec = self._spec()
        if spec is None:
            self._budget.setText(self._translator.t("robustness.budget_unavailable"))
            self._budget_warning.clear()
            self._run.setEnabled(False)
            return
        self._budget.setText(
            self._translator.t(
                "robustness.budget",
                runs=spec.total_runs,
                corners=spec.corner_count,
                samples=spec.monte_carlo_samples,
            )
        )
        self._budget_warning.setText(
            self._translator.t("robustness.budget_warning", runs=spec.total_runs)
            if spec.total_runs > 100
            else ""
        )
        self._run.setEnabled(self._thread is None)

    def _set_running(self, running: bool) -> None:
        for widget in (
            self._variables_list,
            self._tolerance,
            self._corners,
            self._samples,
            self._seed,
            self._swr_limit,
            self._target,
        ):
            widget.setEnabled(not running)
        self._run.setEnabled(not running and self._spec() is not None)
        self._cancel.setEnabled(running)

    def _start(self) -> None:
        if self._thread is not None:
            return
        spec = self._spec()
        if spec is None:
            return
        self._result = None
        self._table.setRowCount(0)
        self._plot.clear()
        self._summary.clear()
        self._corner_summary.clear()
        self._mc_summary.clear()
        self._progress.begin_determinate(
            spec.total_runs,
            "robustness.progress",
            completed=0,
            total=spec.total_runs,
        )
        self._cancel_token = EventCancelToken()
        command = RunRobustnessCommand(
            descriptor=self._descriptor,
            base_spec=self._base_spec,
            spec=spec,
            cancel_token=self._cancel_token,
        )
        self._thread = QThread(self)
        self._worker = RobustnessWorker(self._solver, command)
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
            "robustness.progress",
            completed=completed,
            total=total,
        )

    def _on_finished(self, result: RobustnessResult) -> None:
        self._result = result
        self._show_result(result)
        if result.cancelled:
            self._progress.cancel("robustness.cancelled")
        else:
            self._progress.complete("robustness.progress_done")
        self._set_running(False)
        if self._thread is not None:
            self._thread.quit()

    def _on_failed(self, message: str) -> None:
        self._summary.setText(f"{self._translator.t('robustness.failed')} {message}")
        self._progress.fail("robustness.failed")
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
        self._progress.mark_cancelling("robustness.cancelling")

    def _show_result(self, result: RobustnessResult) -> None:
        spec = result.spec
        nominal = result.nominal
        self._summary.setText(
            self._translator.t(
                "robustness.summary_nominal",
                swr=self._format_swr(nominal.swr if nominal is not None else None),
                completed=len(result.scenarios),
                total=spec.total_runs,
            )
        )
        worst = result.worst_corner
        self._corner_summary.setText(
            self._translator.t(
                "robustness.summary_corner",
                swr=self._format_swr(worst.swr if worst is not None else None),
                values=(self._format_values(worst.values) if worst is not None else "—"),
            )
        )
        stats = result.statistics
        if stats.count == 0:
            self._mc_summary.setText(self._translator.t("robustness.summary_no_mc"))
        else:
            self._mc_summary.setText(
                self._translator.t(
                    "robustness.summary_mc",
                    count=stats.count,
                    median=self._format_swr(stats.median_swr),
                    p90=self._format_swr(stats.p90_swr),
                    p95=self._format_swr(stats.p95_swr),
                    passed=stats.passed,
                    limit=f"{spec.swr_limit:.2f}",
                    fraction=f"{(stats.pass_fraction or 0.0) * 100.0:.0f}",
                )
            )
        self._show_histogram(result)
        self._show_table(result)

    def _show_histogram(self, result: RobustnessResult) -> None:
        self._plot.clear()
        self._plot.setTitle(
            self._translator.t("robustness.plot_title"),
            color=self._colors.text,
        )
        self._plot.setLabel("bottom", "SWR", color=self._colors.text)
        self._plot.setLabel("left", self._translator.t("robustness.count"), color=self._colors.text)
        bins = result.histogram
        if not bins:
            return
        centers = [(item.left + item.right) / 2.0 for item in bins]
        widths = [max(item.right - item.left, 1e-9) * 0.9 for item in bins]
        self._plot.addItem(
            pg.BarGraphItem(
                x=centers,
                height=[item.count for item in bins],
                width=widths,
                brush=self._colors.swr,
                pen=pg.mkPen(self._colors.text),
            )
        )
        self._plot.addItem(
            pg.InfiniteLine(
                pos=result.spec.swr_limit,
                angle=90,
                pen=pg.mkPen(
                    self._colors.feed,
                    width=1,
                    style=Qt.PenStyle.DashLine,
                ),
            )
        )

    def _show_table(self, result: RobustnessResult) -> None:
        scenarios = result.scenarios
        self._table.setRowCount(len(scenarios))
        self._table.setHorizontalHeaderLabels(
            [
                self._translator.t("robustness.method"),
                self._translator.t("robustness.dimensions"),
                "SWR",
                "R (Ω)",
                "X (Ω)",
                "|Z| (Ω)",
                self._translator.t("sweep.status"),
            ]
        )
        worst = result.worst_corner
        self._table.blockSignals(True)
        try:
            for row, scenario in enumerate(scenarios):
                method = self._translator.t(f"robustness.method.{scenario.kind.value}")
                values = (
                    method,
                    self._format_values(scenario.values),
                    self._format_swr(scenario.swr),
                    self._format_number(scenario.resistance_ohm),
                    self._format_number(scenario.reactance_ohm),
                    self._format_number(scenario.impedance_magnitude_ohm),
                    (
                        self._translator.t("robustness.worst_corner")
                        if scenario is worst
                        else (
                            self._translator.t("sweep.valid")
                            if scenario.valid
                            else self._error_text(scenario.error)
                        )
                    ),
                )
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    if column >= 2:
                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                        )
                    if not scenario.valid:
                        item.setToolTip(scenario.error)
                    if scenario is worst:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    self._table.setItem(row, column, item)
        finally:
            self._table.blockSignals(False)
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def _format_values(self, values: tuple[tuple[str, float], ...]) -> str:
        by_name = {variable.name: variable for variable in self._variables}
        parts = []
        for name, value in values:
            variable = by_name.get(name)
            if variable is None:
                continue
            unit = self._unit_text(variable.unit)
            display = self._to_display(variable.unit, value)
            text = f"{display:.4f}"
            if unit:
                text += f" {unit}"
            parts.append(f"{self._translator.t(variable.label_key)}={text}")
        return " · ".join(parts)

    def _unit_text(self, unit: str) -> str:
        if unit == "m":
            return self._translator.t(length_unit_key(self._unit_system))
        if unit == "radius":
            return self._translator.t(radius_unit_key(self._unit_system))
        return unit

    def _to_display(self, unit: str, value: float) -> float:
        if unit == "m":
            return length_from_m(value, self._unit_system)
        if unit == "radius":
            return radius_from_m(value, self._unit_system)
        return value

    @staticmethod
    def _format_swr(value: float | None) -> str:
        if value is None:
            return "—"
        if math.isinf(value):
            return "∞"
        if not math.isfinite(value):
            return "—"
        return f"{value:.3f}"

    @staticmethod
    def _format_number(value: float | None) -> str:
        if value is None or not math.isfinite(value):
            return "—"
        return f"{value:.3f}"

    def _error_text(self, error: str) -> str:
        if not error:
            return ""
        translated = self._translator.t(error)
        return error if translated == error else translated

    def retranslate(self) -> None:
        t = self._translator.t
        self.setWindowTitle(t("robustness.title"))
        self._variables_group.setTitle(t("robustness.critical_dimensions"))
        self._variables_hint.setText(t("robustness.variables_hint"))
        self._settings_group.setTitle(t("robustness.settings"))
        for row in range(self._variables_list.count()):
            item = self._variables_list.item(row)
            name = item.data(Qt.ItemDataRole.UserRole)
            variable = next(
                (value for value in self._variables if value.name == name),
                None,
            )
            if variable is not None:
                item.setText(f"{t(variable.label_key)} · {t(variable.group)}")
        self._corners.setText(t("robustness.include_corners"))
        self._run.setText(t("robustness.run"))
        self._cancel.setText(t("robustness.cancel"))
        self._close.setText(t("action.close"))
        for widget, key in (
            (self._tolerance, "robustness.tolerance"),
            (self._samples, "robustness.samples"),
            (self._seed, "robustness.seed"),
            (self._swr_limit, "robustness.swr_limit"),
            (self._target, "robustness.target"),
        ):
            label = self._settings_form.labelForField(widget)
            if isinstance(label, QLabel):
                label.setText(t(key))
        self._progress.retranslate()
        apply_help(self._plot, self._translator, "robustness.plot")
        apply_help(self._table, self._translator, "robustness.table")
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
