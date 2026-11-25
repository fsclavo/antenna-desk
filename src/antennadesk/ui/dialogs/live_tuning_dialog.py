# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Live, coarse preview of a managed design dimension."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
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
from ...domain.antennas.design import AntennaDesignParameters
from ...domain.antennas.dimensions import (
    ManagedDimension,
    ManagedValueKind,
    managed_dimensions,
)
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import SimulationResult
from ...domain.simulation.spec import SimulationSpec
from ...presentation.units import DisplayUnits
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from ..widgets.polar_pattern_view import PolarPatternView
from ..workers.simulation_worker import SimulationWorker
from ..workers.task_runner import TaskRunner


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
        dimensions: tuple[ManagedDimension, ...] | None = None,
        display_units: DisplayUnits | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters = parameters
        self._base_spec = base_spec
        self._solver = solver
        self._on_apply = on_apply
        self._display_units = display_units or DisplayUnits()
        self._dimensions = dimensions or managed_dimensions(parameters)
        if not self._dimensions:
            raise ValueError("the family has no managed live-tuning dimension")
        self._dimension = self._dimensions[0]
        self._dimension_m = self._dimension.read(parameters)
        self._request_id = 0
        self._busy = False
        self._pending: float | None = None
        self._token: EventCancelToken | None = None
        self._thread_request_id = 0
        self._runner = TaskRunner(self, close_timeout_ms=500)
        self._runner.succeeded.connect(self._on_worker_finished)
        self._runner.failed.connect(self._on_worker_failed)
        self.setWindowTitle(translator.t("live.title"))
        self.resize(*scaled_dialog_size(640, 620))
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(250)
        self._debounce.timeout.connect(self._start_preview)
        self._dimension_selector_label = QLabel(self)
        self._dimension_combo = QComboBox(self)
        for dimension in self._dimensions:
            self._dimension_combo.addItem(
                translator.t(dimension.label_key),
                dimension.key,
            )
        self._dimension_combo.currentIndexChanged.connect(self._on_dimension_changed)
        self._pattern_preview = QCheckBox(translator.t("live.pattern_preview"), self)
        try:
            supports_pattern = bool(solver.capabilities().supports_far_field)
        except Exception:
            supports_pattern = False
        self._pattern_supported = supports_pattern
        self._pattern_preview.setChecked(supports_pattern)
        self._pattern_preview.setEnabled(supports_pattern)
        self._pattern_preview.toggled.connect(self._on_pattern_preview_toggled)
        self._pattern_view = PolarPatternView(translator, self)
        self._pattern_view.set_title(translator.t("live.pattern_title"))
        self._pattern_view.set_cut(0.0, symbol="φ")
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
        dimension_row = QHBoxLayout()
        dimension_row.addWidget(self._dimension_selector_label)
        dimension_row.addWidget(self._dimension_combo, 1)
        layout = QVBoxLayout(self)
        layout.addLayout(dimension_row)
        layout.addWidget(self._dimension_label)
        layout.addWidget(self._slider)
        layout.addWidget(self._result_label)
        layout.addWidget(self._pattern_preview)
        layout.addWidget(self._pattern_view, 1)
        layout.addWidget(self._progress)
        layout.addWidget(self._preview_label)
        layout.addLayout(controls)
        self._dimension_selector_label.setText(translator.t("live.dimension_selector"))
        apply_help(self._dimension_combo, translator, "live.dimension")
        apply_help(self._pattern_preview, translator, "live.pattern_preview")
        apply_help(self._slider, translator, "live.dimension")
        apply_help(self, translator, "live.title")
        self._update_dimension_label()
        self._update_buttons()
        self._debounce.start()

    def _dimension_for_slider(self, value: int) -> float:
        if self._dimension.kind is ManagedValueKind.COUNT:
            step = max(1, round(self._dimension_m * 0.25))
            candidate = self._dimension_m + (value - 100) / 100.0 * step
        elif self._dimension.kind is ManagedValueKind.ANGLE and abs(self._dimension_m) < 1.0:
            candidate = self._dimension_m + (value - 100) / 100.0 * 30.0
        else:
            candidate = self._dimension_m * (0.80 + 0.40 * value / 200.0)
        return min(max(candidate, self._dimension.minimum), self._dimension.maximum)

    def _format_dimension(self, value: float) -> str:
        if self._dimension.kind is ManagedValueKind.LENGTH:
            return self._display_units.format_length(value)
        if self._dimension.kind is ManagedValueKind.ANGLE:
            return f"{value:.1f}°"
        if self._dimension.kind is ManagedValueKind.COUNT:
            return f"{round(value):d}"
        return f"{value:.3g}"

    def _on_dimension_changed(self, _index: int) -> None:
        key = self._dimension_combo.currentData()
        dimension = next(
            (item for item in self._dimensions if item.key == key),
            None,
        )
        if dimension is None or dimension.key == self._dimension.key:
            return
        self._invalidate_preview()
        self._pending = None
        self._dimension = dimension
        self._dimension_m = dimension.read(self._parameters)
        self._slider.blockSignals(True)
        try:
            self._slider.setValue(100)
        finally:
            self._slider.blockSignals(False)
        self._result_label.clear()
        self._pattern_view.set_points(())
        self._progress.setText(self._translator.t("live.waiting"))
        self._update_dimension_label()
        self._debounce.start()

    def _on_slider(self, _value: int) -> None:
        self._invalidate_preview()
        self._update_dimension_label()
        self._progress.setText(self._translator.t("live.waiting"))
        self._debounce.start()

    def _on_pattern_preview_toggled(self, enabled: bool) -> None:
        if not self._pattern_supported:
            return
        self._invalidate_preview()
        if not enabled:
            self._pattern_view.set_points(())
        self._progress.setText(self._translator.t("live.waiting"))
        self._debounce.start()

    def _invalidate_preview(self) -> None:
        """Discard in-flight results: the requested target has changed."""

        self._request_id += 1
        if self._token is not None:
            self._token.cancel()

    def _update_dimension_label(self) -> None:
        dimension = self._dimension_for_slider(self._slider.value())
        self._dimension_label.setText(
            self._translator.t(
                "live.dimension_value",
                dimension=self._translator.t(self._dimension.label_key),
                value=self._format_dimension(dimension),
            )
        )

    def _current_parameters(self) -> AntennaDesignParameters:
        return self._dimension.write(
            self._parameters,
            self._dimension_for_slider(self._slider.value()),
        )

    def _start_preview(self) -> None:
        if self._busy:
            self._pending = self._dimension_for_slider(self._slider.value())
            if self._token is not None:
                self._token.cancel()
            return
        try:
            parameters = self._current_parameters()
            model = parameters.to_antenna()
            far_field = (
                FarFieldRequest(
                    enabled=True,
                    theta_start_deg=0.0,
                    theta_stop_deg=180.0,
                    theta_count=19,
                    phi_start_deg=0.0,
                    phi_stop_deg=0.0,
                    phi_count=1,
                )
                if self._pattern_preview.isChecked()
                else FarFieldRequest(enabled=False)
            )
            spec = replace(
                self._base_spec,
                frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
                pattern_frequencies_hz=(),
                far_field=far_field,
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
        self._thread_request_id = request_id
        self._busy = True
        self._pending = None
        self._progress.setText(self._translator.t("live.running"))
        self._update_buttons()
        token = EventCancelToken()
        self._token = token
        worker = SimulationWorker(self._solver, model, spec, token)
        self._runner.start(worker, cancel=token)

    @Slot(object)
    def _on_worker_finished(self, result: SimulationResult) -> None:
        self._finished(self._thread_request_id, result)

    @Slot(str)
    def _on_worker_failed(self, message: str) -> None:
        self._failed(self._thread_request_id, message)

    def _finished(self, request_id: int, result: SimulationResult) -> None:
        if request_id != self._request_id:
            self._recover_after_stale_result()
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
        self._update_pattern(result)
        self._progress.setText(self._translator.t("live.preview"))
        self._update_buttons()
        if self._pending is not None:
            self._pending = None
            self._start_preview()

    def _recover_after_stale_result(self) -> None:
        """Release the worker after a result the user has already superseded."""

        self._busy = False
        self._cleanup_thread()
        self._update_buttons()
        if self._pending is not None:
            self._pending = None
            self._start_preview()

    def _update_pattern(self, result: SimulationResult) -> None:
        if not self._pattern_preview.isChecked():
            self._pattern_view.set_points(())
            return
        frequency = result.frequencies[0] if result.frequencies else None
        if frequency is None or not frequency.far_field:
            self._pattern_view.set_points(())
            return
        points = tuple(
            (point.theta_deg, point.gain_total_db)
            for point in frequency.far_field
            if point.gain_total_db is not None
        )
        self._pattern_view.set_points(points)

    def _failed(self, request_id: int, message: str) -> None:
        if request_id != self._request_id:
            self._recover_after_stale_result()
            return
        self._busy = False
        self._cleanup_thread()
        self._progress.setText(message)
        self._pattern_view.set_points(())
        self._update_buttons()

    def _cleanup_thread(self) -> None:
        # The runner keeps the thread alive and detaches a solver that is still
        # stopping; the dialog can close safely.
        self._runner.close(500)

    def _update_buttons(self) -> None:
        self._apply.setEnabled(not self._busy)

    def _apply_clicked(self) -> None:
        if self._busy:
            return
        try:
            self._on_apply(self._current_parameters())
        except Exception as exc:
            self._progress.setText(str(exc))
            return
        self._stop_preview()
        self.accept()

    def _stop_preview(self) -> None:
        """Stop timers and discard any in-flight preview before closing."""

        self._debounce.stop()
        self._invalidate_preview()
        self._pending = None
        self._cleanup_thread()

    def reject(self) -> None:
        self._stop_preview()
        super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._stop_preview()
        event.accept()
