# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded sensitivity-based tuning assistant dialog."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
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

from ...application.cancellation import EventCancelToken
from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.tune_measurement import TuneMeasurementCommand
from ...domain.antennas.design import (
    AntennaDesignParameters,
    primary_dimension_m,
    with_primary_dimension,
)
from ...domain.design.tuning import (
    TuningProposal,
    TuningReferenceKind,
    TuningStatus,
    measurement_tuning_reference,
)
from ...domain.measurement import Measurement
from ...domain.projects.project import DesignVariant
from ...domain.simulation.spec import SimulationSpec
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from ..units import (
    UnitSystem,
    length_from_m,
    length_to_m,
    length_unit_key,
)
from ..widgets.task_progress import TaskProgressBar
from ..workers.tuning_worker import TuningWorker


class TuningAssistantDialog(QDialog):
    """Propose a bounded primary-dimension change from measurement + solver."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        solver: AntennaSolver,
        design: DesignVariant,
        measurement: Measurement,
        base_spec: SimulationSpec,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._solver = solver
        self._design = design
        self._measurement = measurement
        self._base_spec = base_spec
        self._current_dimension_m = primary_dimension_m(design.parameters)
        self._result: TuningProposal | None = None
        self._result_parameters: AntennaDesignParameters | None = None
        self._thread: QThread | None = None
        self._worker: TuningWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self.setWindowTitle(translator.t("tuning.title"))
        self.resize(*scaled_dialog_size(920, 760))

        self._measurement_label = QLabel(self)
        self._measurement_value = QLabel(self)
        self._measurement_value.setTextFormat(Qt.TextFormat.PlainText)
        self._measurement_value.setWordWrap(True)
        self._target = QDoubleSpinBox(self)
        self._target.setRange(0.1, 1_000.0)
        self._target.setDecimals(6)
        self._target.setValue(design.parameters.frequency_hz / 1e6)
        self._target.setSuffix(" MHz")
        apply_help(self._target, translator, "tuning.target")
        self._current_dimension_label = QLabel(self)
        self._current_dimension_value = QLabel(self)
        self._max_adjustment = QDoubleSpinBox(self)
        self._max_adjustment.setDecimals(3)
        self._max_adjustment.setRange(
            length_from_m(0.001, unit_system),
            length_from_m(10.0, unit_system),
        )
        self._max_adjustment.setValue(
            length_from_m(
                max(0.01, min(0.05 * self._current_dimension_m, 0.5)),
                unit_system,
            )
        )
        self._max_adjustment.setSuffix(f" {translator.t(length_unit_key(unit_system))}")
        apply_help(self._max_adjustment, translator, "tuning.max_adjustment")
        self._measured_reference = QLabel(self)
        self._measured_reference.setWordWrap(True)
        self._measured_reference.setTextFormat(Qt.TextFormat.PlainText)
        self._target.valueChanged.connect(self._update_measurement_reference)
        self._message = QLabel(self)
        self._message.setWordWrap(True)
        self._message.setTextFormat(Qt.TextFormat.PlainText)
        self._sensitivity = QLabel(self)
        self._sensitivity.setWordWrap(True)
        self._proposal = QLabel(self)
        self._proposal.setWordWrap(True)
        self._prediction = QLabel(self)
        self._prediction.setWordWrap(True)
        self._bounds = QLabel(self)
        self._bounds.setWordWrap(True)
        self._assumptions = QLabel(self)
        self._assumptions.setWordWrap(True)
        self._assumptions.setStyleSheet("color: #8a5a00;")
        apply_help(self._assumptions, translator, "tuning.assumptions")

        self._table = QTableWidget(0, 4, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        apply_help(self._table, translator, "tuning.table")

        self._analyze = QPushButton(translator.t("tuning.analyze"), self)
        self._cancel = QPushButton(translator.t("tuning.cancel"), self)
        self._apply = QPushButton(translator.t("tuning.apply"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._analyze.clicked.connect(self._start)
        self._cancel.clicked.connect(self._cancel_run)
        self._apply.clicked.connect(self._apply_result)
        self._close.clicked.connect(self.reject)
        self._cancel.setEnabled(False)
        self._apply.setEnabled(False)
        for button, key in (
            (self._analyze, "tuning.analyze"),
            (self._cancel, "tuning.cancel"),
            (self._apply, "tuning.apply"),
        ):
            apply_help(button, translator, key)

        self._progress = TaskProgressBar(translator, self)

        form = QFormLayout()
        form.addRow(self._measurement_label, self._measurement_value)
        form.addRow(translator.t("tuning.target"), self._target)
        form.addRow(self._current_dimension_label, self._current_dimension_value)
        form.addRow(translator.t("tuning.max_adjustment"), self._max_adjustment)
        apply_help(
            self._measurement_value,
            translator,
            "tuning.measurement",
        )
        apply_help(
            self._current_dimension_value,
            translator,
            "tuning.current_dimension",
        )

        actions = QHBoxLayout()
        actions.addWidget(self._analyze)
        actions.addWidget(self._cancel)
        actions.addStretch(1)
        actions.addWidget(self._apply)
        actions.addWidget(self._close)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._measured_reference)
        layout.addWidget(self._message)
        layout.addWidget(self._sensitivity)
        layout.addWidget(self._proposal)
        layout.addWidget(self._prediction)
        layout.addWidget(self._bounds)
        layout.addWidget(self._assumptions)
        layout.addWidget(self._progress)
        layout.addWidget(self._table, 1)
        layout.addLayout(actions)
        self.retranslate()
        self._update_measurement_reference()
        self._show_message("tuning.message.ready", warning=False)

    def result_parameters(self) -> AntennaDesignParameters | None:
        return self._result_parameters

    def proposal(self) -> TuningProposal | None:
        return self._result

    def retranslate(self) -> None:
        t = self._translator.t
        self.setWindowTitle(t("tuning.title"))
        self._measurement_label.setText(t("tuning.measurement"))
        self._measurement_value.setText(
            f"{self._measurement.name} · {self._measurement.created_at:%Y-%m-%d %H:%M}"
        )
        self._current_dimension_label.setText(t("tuning.current_dimension"))
        self._analyze.setText(t("tuning.analyze"))
        self._cancel.setText(t("tuning.cancel"))
        self._apply.setText(t("tuning.apply"))
        self._close.setText(t("action.close"))
        unit = t(length_unit_key(self._unit_system))
        self._current_dimension_value.setText(
            f"{length_from_m(self._current_dimension_m, self._unit_system):.4f} {unit}"
        )
        self._table.setHorizontalHeaderLabels(
            [
                t("tuning.table.probe"),
                t("tuning.table.dimension"),
                t("tuning.table.resonance"),
                t("tuning.table.swr"),
            ]
        )
        self._assumptions.setText(t("tuning.assumptions_text"))
        apply_help(self._table, self._translator, "tuning.table")

    def _update_measurement_reference(self, *_args: object) -> None:
        target_hz = self._target.value() * 1e6
        frequency_hz, kind = measurement_tuning_reference(
            self._measurement,
            target_hz,
        )
        key = (
            "tuning.measured_resonance"
            if kind is TuningReferenceKind.RESONANCE
            else "tuning.measured_min_swr"
        )
        self._measured_reference.setText(
            self._translator.t(key, value=f"{frequency_hz / 1e6:.6f} MHz")
        )

    def _show_message(self, key: str, *, warning: bool = False) -> None:
        self._message.setText(self._translator.t(key))
        self._message.setStyleSheet("color: #b54708;" if warning else "")

    def _start(self) -> None:
        if self._thread is not None:
            return
        self._result = None
        self._result_parameters = None
        self._apply.setEnabled(False)
        self._table.setRowCount(0)
        self._sensitivity.clear()
        self._proposal.clear()
        self._prediction.clear()
        self._bounds.clear()
        self._show_message("tuning.message.running")
        self._analyze.setEnabled(False)
        self._cancel.setEnabled(True)
        self._target.setEnabled(False)
        self._max_adjustment.setEnabled(False)
        self._progress.begin_determinate(4, "tuning.progress", completed=0, total=4)
        self._cancel_token = EventCancelToken()
        command = TuneMeasurementCommand(
            parameters=self._design.parameters,
            measurement=self._measurement,
            base_spec=self._base_spec,
            target_frequency_hz=self._target.value() * 1e6,
            max_adjustment_m=length_to_m(
                self._max_adjustment.value(),
                self._unit_system,
            ),
            cancel_token=self._cancel_token,
        )
        self._thread = QThread(self)
        self._worker = TuningWorker(self._solver, command)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._thread.finished.connect(self._cleanup)
        self._thread.start()

    def _on_progress(self, completed: int, total: int) -> None:
        self._progress.set_progress(
            completed,
            "tuning.progress",
            completed=completed,
            total=total,
        )

    def _on_finished(self, proposal: TuningProposal) -> None:
        self._result = proposal
        self._show_proposal(proposal)
        if proposal.status is TuningStatus.CANCELLED:
            self._progress.cancel("tuning.message.cancelled")
        elif proposal.status is TuningStatus.ERROR:
            self._progress.fail("tuning.failed")
        else:
            self._progress.complete("tuning.progress_done")
        self._restore_controls()
        if self._thread is not None:
            self._thread.quit()

    def _on_failed(self, message: str) -> None:
        self._show_message("tuning.message.error", warning=True)
        self._message.setText(f"{self._translator.t('tuning.message.error')} {message}")
        self._progress.fail("tuning.failed")
        self._restore_controls()
        if self._thread is not None:
            self._thread.quit()

    def _restore_controls(self) -> None:
        self._analyze.setEnabled(True)
        self._cancel.setEnabled(False)
        self._target.setEnabled(True)
        self._max_adjustment.setEnabled(True)

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
        self._progress.mark_cancelling("tuning.cancelling")

    def _format_length(self, value_m: float, *, signed: bool = False) -> str:
        value = length_from_m(value_m, self._unit_system)
        unit = self._translator.t(length_unit_key(self._unit_system))
        return f"{value:+.4f} {unit}" if signed else f"{value:.4f} {unit}"

    def _format_frequency(self, value_hz: float | None) -> str:
        if value_hz is None:
            return "—"
        return f"{value_hz / 1e6:.6f} MHz"

    def _format_swr(self, value: float | None) -> str:
        if value is None:
            return "—"
        return "∞" if math.isinf(value) else f"{value:.3f}"

    def _format_slope(self, value: float | None) -> str:
        if value is None:
            return "—"
        if self._unit_system is UnitSystem.IMPERIAL:
            return f"{value / 1e3 / 3.280839895:+.3f} kHz/ft"
        return f"{value / 1e3:+.3f} kHz/m"

    def _show_proposal(self, proposal: TuningProposal) -> None:
        self._sensitivity.setText(
            self._translator.t(
                "tuning.sensitivity",
                value=self._format_slope(proposal.slope_hz_per_m),
            )
        )
        self._measured_reference.setText(
            self._translator.t(
                "tuning.measured_resonance"
                if proposal.request.measured_kind is TuningReferenceKind.RESONANCE
                else "tuning.measured_min_swr",
                value=self._format_frequency(proposal.request.measured_frequency_hz),
            )
        )
        if proposal.status is not TuningStatus.PROPOSED:
            self._proposal.clear()
            self._prediction.clear()
            self._bounds.clear()
            self._show_message(proposal.message_key, warning=True)
            if proposal.detail:
                self._message.setText(f"{self._message.text()} {proposal.detail}")
            return
        if proposal.proposed_change_m is None or proposal.proposed_dimension_m is None:
            return
        change_key = (
            "tuning.proposed_change_clipped" if proposal.clipped else "tuning.proposed_change"
        )
        self._proposal.setText(
            self._translator.t(
                change_key,
                value=self._format_length(proposal.proposed_change_m, signed=True),
            )
        )
        self._bounds.setText(
            self._translator.t(
                "tuning.bounds",
                lower=self._format_length(proposal.bounds_min_m),
                upper=self._format_length(proposal.bounds_max_m),
            )
        )
        if proposal.predicted_resonance_hz is None:
            self._prediction.setText(
                self._translator.t(
                    "tuning.predicted_no_resonance",
                    swr=self._format_swr(proposal.predicted_swr),
                )
            )
        else:
            self._prediction.setText(
                self._translator.t(
                    "tuning.predicted",
                    resonance=self._format_frequency(proposal.predicted_resonance_hz),
                    swr=self._format_swr(proposal.predicted_swr),
                )
            )
        self._show_message(proposal.message_key)
        self._table.setRowCount(len(proposal.probes))
        probe_labels = (
            "tuning.probe.current",
            "tuning.probe.lower",
            "tuning.probe.higher",
            "tuning.probe.proposed",
        )
        for row, probe in enumerate(proposal.probes):
            label_key = probe_labels[min(row, len(probe_labels) - 1)]
            values = (
                self._translator.t(label_key),
                self._format_length(probe.dimension_m),
                self._format_frequency(probe.resonance_hz),
                self._format_swr(probe.swr_at_target),
            )
            for column, value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(value))
        self._table.resizeColumnsToContents()
        self._result_parameters = with_primary_dimension(
            self._design.parameters,
            proposal.proposed_dimension_m,
        )
        self._apply.setEnabled(self._result_parameters is not None)

    def _apply_result(self) -> None:
        if self._result_parameters is None:
            return
        self.accept()

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
