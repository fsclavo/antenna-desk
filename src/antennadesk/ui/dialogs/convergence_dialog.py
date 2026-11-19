# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Self-consistency study dialog for a segmentation-density ladder."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...application.cancellation import EventCancelToken
from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.run_convergence_study import (
    RunConvergenceStudy,
    RunConvergenceStudyCommand,
)
from ...domain.antennas.antenna import AntennaModel
from ...domain.simulation.convergence import ConvergenceResult, convergence_csv
from ...domain.simulation.spec import SimulationSpec
from ..i18n import Translator
from ..workers.convergence_worker import ConvergenceWorker

_COLUMNS = (
    "convergence.column.density",
    "convergence.column.segments",
    "convergence.column.resistance",
    "convergence.column.reactance",
    "convergence.column.magnitude",
    "convergence.column.swr",
    "convergence.column.gain",
    "convergence.column.takeoff",
    "convergence.column.status",
)


class ConvergenceDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        solver: AntennaSolver,
        model: AntennaModel,
        spec: SimulationSpec,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._model = model
        self._spec = spec
        self._solver = solver
        self._result: ConvergenceResult | None = None
        self._cancel_token = EventCancelToken()
        self._thread: QThread | None = None
        self._worker: ConvergenceWorker | None = None

        self.setWindowTitle(translator.t("convergence.title"))
        self.resize(980, 520)

        self._description = QLabel(translator.t("convergence.description"), self)
        self._description.setWordWrap(True)
        self._status = QLabel(translator.t("convergence.running"), self)
        self._status.setWordWrap(True)
        self._progress = QProgressBar(self)
        self._progress.setRange(0, 0)

        self._table = QTableWidget(0, len(_COLUMNS), self)
        self._table.setHorizontalHeaderLabels([translator.t(key) for key in _COLUMNS])
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)

        self._cancel_button = QPushButton(translator.t("action.cancel"), self)
        self._cancel_button.clicked.connect(self._cancel)
        self._export_button = QPushButton(translator.t("convergence.export_csv"), self)
        self._export_button.setEnabled(False)
        self._export_button.clicked.connect(self._export_csv)
        self._close_button = QPushButton(translator.t("action.close"), self)
        self._close_button.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addWidget(self._cancel_button)
        buttons.addStretch(1)
        buttons.addWidget(self._export_button)
        buttons.addWidget(self._close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self._description)
        layout.addWidget(self._status)
        layout.addWidget(self._progress)
        layout.addWidget(self._table, 1)
        layout.addLayout(buttons)

        self._start()

    def _start(self) -> None:
        command = RunConvergenceStudyCommand(
            model=self._model,
            base_spec=self._spec,
            cancel_token=self._cancel_token,
        )
        self._thread = QThread(self)
        self._worker = ConvergenceWorker(
            RunConvergenceStudy(self._solver),
            command,
            self,
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._thread_finished)
        self._thread.start()

    def _thread_finished(self) -> None:
        self._thread = None
        self._worker = None

    def _cancel(self) -> None:
        self._cancel_token.cancel()
        self._cancel_button.setEnabled(False)
        self._status.setText(self._translator.t("convergence.cancelling"))

    def _on_failed(self, message: str) -> None:
        self._progress.setRange(0, 1)
        self._progress.setValue(1)
        self._status.setText(self._translator.t("convergence.failed", message=message))
        self._cancel_button.setEnabled(False)

    def _on_finished(self, result: object) -> None:
        if not isinstance(result, ConvergenceResult):
            self._on_failed(self._translator.t("error.solver"))
            return
        self._result = result
        self._progress.setRange(0, 1)
        self._progress.setValue(1)
        verdict = self._translator.t(f"convergence.verdict.{result.verdict.value}")
        summary = self._translator.t(
            "convergence.summary",
            verdict=verdict,
            points=len(result.valid_points),
            resistance_spread=(result.resistance_spread_fraction or 0.0) * 100.0,
            reactance_spread=result.reactance_spread_ohm or 0.0,
            swr_spread=result.swr_spread or 0.0,
        )
        if result.cancelled:
            summary += "\n" + self._translator.t("convergence.partial")
        if result.error:
            summary += "\n" + self._translator.t("convergence.error", message=result.error)
        self._status.setText(summary)
        self._populate(result)
        self._export_button.setEnabled(True)
        self._cancel_button.setEnabled(False)

    def _populate(self, result: ConvergenceResult) -> None:
        self._table.setRowCount(len(result.points))
        for row, point in enumerate(result.points):
            values = (
                f"{point.density_wavelengths:g}",
                str(point.total_segments),
                f"{point.resistance_ohm:.3f}",
                f"{point.reactance_ohm:+.3f}",
                f"{point.impedance_magnitude_ohm:.3f}",
                f"{point.swr:.3f}",
                "—" if point.max_gain_db is None else f"{point.max_gain_db:.2f}",
                "—" if point.takeoff_deg is None else f"{point.takeoff_deg:.2f}",
                (
                    self._translator.t("convergence.status.valid")
                    if point.valid
                    else self._translator.t("convergence.status.invalid")
                ),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column > 0:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                if point.error or point.diagnostics:
                    item.setToolTip("\n".join((*point.diagnostics, point.error or "")))
                self._table.setItem(row, column, item)
        self._table.resizeColumnsToContents()

    def _export_csv(self) -> None:
        if self._result is None:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("convergence.export_title"),
            str(Path.home() / "convergence.csv"),
            self._translator.t("dialog.csv_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".csv":
            path = path.with_suffix(".csv")
        try:
            path.write_text(convergence_csv(self._result), encoding="utf-8")
        except Exception as exc:
            QMessageBox.critical(
                self,
                self.windowTitle(),
                self._translator.t("error.export", message=str(exc)),
            )

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._thread is not None and self._thread.isRunning():
            self._cancel_token.cancel()
            self._thread.quit()
            self._thread.wait(5_000)
        event.accept()
