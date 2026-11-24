# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Live, coarse preview of one primary dimension."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ...application.cancellation import EventCancelToken
from ...application.ports.antenna_solver import AntennaSolver
from ...domain.antennas.design import (
    AntennaDesignParameters,
    primary_dimension_m,
    with_primary_dimension,
)
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import SimulationResult
from ...domain.simulation.spec import SimulationSpec
from ...presentation.units import DisplayUnits
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from ..workers.simulation_worker import SimulationWorker


class LiveTuningDialog(QDialog):
    """Debounced coarse preview followed by an explicit apply."""

    def __init__(
        self,
        translator: Translator,
        parameters: AntennaDesignParameters,
        base_spec: SimulationSpec,
        solver: AntennaSolver,
        on_apply: Callable[[AntennaDesignParameters], None],
        *,
        display_units: DisplayUnits | None = None,
        is_simulation_running: Callable[[], bool] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters = parameters
        self._base_spec = base_spec
        self._solver = solver
        self._on_apply = on_apply
        self._display_units = display_units or DisplayUnits()
        self._is_simulation_running = is_simulation_running or (lambda: False)
        self._dimension_m = primary_dimension_m(parameters)
        self._applying = False
        self._request_id = 0
        self._busy = False
        self._pending: float | None = None
        self._token: EventCancelToken | None = None
        self._thread: QThread | None = None
        self._worker: SimulationWorker | None = None
        self.setWindowTitle(translator.t("live.title"))
        self.resize(*scaled_dialog_size(620, 300))
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(250)
        self._debounce.timeout.connect(self._start_preview)
        self._apply_timer = QTimer(self)
        self._apply_timer.setInterval(200)
        self._apply_timer.timeout.connect(self._poll_apply)
        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setRange(0, 200)
        self._slider.setValue(100)
        self._slider.valueChanged.connect(self._on_slider)
        self._dimension_label = QLabel(self)
        self._dimension_label.setTextFormat(Qt.TextFormat.PlainText)
        self._result_label = QLabel(self)
        self._result_label.setTextFormat(Qt.TextFormat.PlainText)
        self._result_label.setMinimumHeight(90)
        self._preview_label = QLabel(translator.t("live.preview_note"), self)
        self._preview_label.setWordWrap(True)
        self._apply = QPushButton(translator.t("live.apply"), self)
        self._apply.clicked.connect(self._apply_clicked)
        self._close = QPushButton(translator.t("live.close"), self)
        self._close.clicked.connect(self.reject)
        self._progress = QLabel(self)
        self._progress.setWordWrap(True)
        controls = QHBoxLayout()
        controls.addWidget(self._apply)
        controls.addWidget(self._close)
        controls.addStretch(1)
        layout = QVBoxLayout(self)
        layout.addWidget(self._dimension_label)
        layout.addWidget(self._slider)
        layout.addWidget(self._result_label, 1)
        layout.addWidget(self._progress)
        layout.addWidget(self._preview_label)
        layout.addLayout(controls)
        apply_help(self._slider, translator, "live.dimension")
        apply_help(self, translator, "live.title")
        self._update_dimension_label()
        self._update_buttons()
        self._debounce.start()

    def _dimension_for_slider(self, value: int) -> float:
        return self._dimension_m * (0.80 + 0.40 * value / 200.0)

    def _on_slider(self, _value: int) -> None:
        self._update_dimension_label()
        self._progress.setText(self._translator.t("live.waiting"))
        self._debounce.start()

    def _update_dimension_label(self) -> None:
        dimension = self._dimension_for_slider(self._slider.value())
        self._dimension_label.setText(
            self._translator.t(
                "live.dimension_label",
                value=self._display_units.format_length(dimension),
            )
        )

    def _current_parameters(self) -> AntennaDesignParameters:
        return with_primary_dimension(
            self._parameters,
            self._dimension_for_slider(self._slider.value()),
        )

    def _start_preview(self) -> None:
        if self._applying:
            return
        if self._busy:
            self._pending = self._dimension_for_slider(self._slider.value())
            if self._token is not None:
                self._token.cancel()
            return
        try:
            parameters = self._current_parameters()
            model = parameters.to_antenna()
            spec = replace(
                self._base_spec,
                frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
                pattern_frequencies_hz=(),
                far_field=FarFieldRequest(enabled=False),
                segmentation=replace(
                    self._base_spec.segmentation,
                    target_segment_length_wavelengths=0.10,
                    min_segments_per_wire=1,
                ),
            )
        except Exception as exc:
            self._progress.setText(str(exc))
            return
        self._request_id += 1
        request_id = self._request_id
        self._busy = True
        self._pending = None
        self._progress.setText(self._translator.t("live.running"))
        self._update_buttons()
        token = EventCancelToken()
        self._token = token
        thread = QThread(self)
        worker = SimulationWorker(self._solver, model, spec, token)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(
            lambda result, request_id=request_id: self._finished(request_id, result)
        )
        worker.failed.connect(
            lambda message, request_id=request_id: self._failed(request_id, message)
        )
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        self._worker = worker
        thread.start()

    def _finished(self, request_id: int, result: SimulationResult) -> None:
        if request_id != self._request_id:
            self._cleanup_thread()
            return
        self._busy = False
        self._cleanup_thread()
        frequency = result.frequencies[0] if result.frequencies else None
        if frequency is None:
            self._result_label.setText(self._translator.t("live.no_result"))
        else:
            self._result_label.setText(
                self._translator.t(
                    "live.result",
                    swr=("∞" if not frequency.swr < float("inf") else f"{frequency.swr:.3f}"),
                    r=f"{frequency.impedance_ohm.real:.2f}",
                    x=f"{frequency.impedance_ohm.imag:+.2f}",
                    z=f"{abs(frequency.impedance_ohm):.2f}",
                )
            )
        self._progress.setText(self._translator.t("live.preview"))
        self._update_buttons()
        if self._pending is not None:
            self._pending = None
            self._start_preview()

    def _failed(self, request_id: int, message: str) -> None:
        if request_id != self._request_id:
            self._cleanup_thread()
            return
        self._busy = False
        self._cleanup_thread()
        self._progress.setText(message)
        self._update_buttons()

    def _cleanup_thread(self) -> None:
        thread = self._thread
        worker = self._worker
        self._thread = None
        self._worker = None
        if worker is not None:
            worker.deleteLater()
        if thread is not None:
            thread.quit()
            thread.wait(100)

    def _update_buttons(self) -> None:
        ready = not self._busy and not self._applying
        self._apply.setEnabled(ready)
        self._slider.setEnabled(not self._applying)

    def _apply_clicked(self) -> None:
        if self._busy or self._applying:
            return
        parameters = self._current_parameters()
        try:
            self._on_apply(parameters)
        except Exception as exc:
            self._progress.setText(str(exc))
            return
        # Keep the dialog open: the operator can keep tuning without reopening.
        self._parameters = parameters
        self._dimension_m = primary_dimension_m(parameters)
        self._slider.blockSignals(True)
        try:
            self._slider.setValue(100)
        finally:
            self._slider.blockSignals(False)
        self._update_dimension_label()
        self._result_label.setText(self._translator.t("live.applied"))
        self._progress.setText(self._translator.t("live.simulation_running"))
        self._debounce.stop()
        self._applying = True
        self._apply_timer.start()
        self._update_buttons()

    def _poll_apply(self) -> None:
        if not self._applying:
            self._apply_timer.stop()
            return
        if self._is_simulation_running():
            return
        self._applying = False
        self._apply_timer.stop()
        self._progress.setText(self._translator.t("live.applied_ready"))
        self._update_buttons()

    def reject(self) -> None:
        self._debounce.stop()
        self._apply_timer.stop()
        if self._token is not None:
            self._token.cancel()
        self._cleanup_thread()
        super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._debounce.stop()
        self._apply_timer.stop()
        if self._token is not None:
            self._token.cancel()
        self._cleanup_thread()
        event.accept()
