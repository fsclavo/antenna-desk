# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Before/after measurement comparison dialog."""

from __future__ import annotations

import math
from uuid import UUID

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.measurement import Measurement
from ...domain.measurement_comparison import (
    MeasurementPairComparison,
    compare_measurement_pair,
)
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator


def _swr_text(value: float | None) -> str:
    if value is None:
        return "—"
    return "∞" if math.isinf(value) else f"{value:.3f}"


class MeasurementComparisonDialog(QDialog):
    """Compare two measurements on their overlapping frequency range."""

    def __init__(
        self,
        translator: Translator,
        measurements: tuple[Measurement, ...],
        parent: QWidget | None = None,
        *,
        session_names: dict[UUID, str] | None = None,
        initial_before_id: UUID | None = None,
        initial_after_id: UUID | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._measurements = measurements
        self._session_names = session_names or {}
        self._comparison: MeasurementPairComparison | None = None
        self.setWindowTitle(translator.t("measurement.before_after_title"))
        self.resize(*scaled_dialog_size(980, 720))

        self._before = QComboBox(self)
        self._after = QComboBox(self)
        for measurement in measurements:
            session = (
                self._session_names.get(measurement.session_id)
                if measurement.session_id is not None
                else None
            )
            label = measurement.name
            if session:
                label = f"{label} · {session}"
            self._before.addItem(label, measurement.id)
            self._after.addItem(label, measurement.id)
        self._set_initial(self._before, initial_before_id, fallback=0)
        self._set_initial(
            self._after,
            initial_after_id,
            fallback=min(1, max(len(measurements) - 1, 0)),
        )
        self._before.currentIndexChanged.connect(self._render)
        self._after.currentIndexChanged.connect(self._render)

        self._reference = QDoubleSpinBox(self)
        self._reference.setRange(1.0, 10_000.0)
        self._reference.setDecimals(1)
        self._reference.setValue(50.0)
        self._reference.setSuffix(" Ω")
        self._reference.valueChanged.connect(self._render)
        apply_help(self._reference, translator, "measurement.comparison.reference")
        self._reference_label = QLabel(translator.t("measurement.comparison_reference"), self)

        self._before_label = QLabel(translator.t("measurement.comparison_before"), self)
        self._after_label = QLabel(translator.t("measurement.comparison_after"), self)
        form = QFormLayout()
        form.addRow(self._before_label, self._before)
        form.addRow(self._after_label, self._after)
        form.addRow(self._reference_label, self._reference)
        apply_help(self._before, translator, "measurement.comparison.before")
        apply_help(self._after, translator, "measurement.comparison.after")

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._summary.setTextFormat(Qt.TextFormat.PlainText)
        self._resonance = QLabel(self)
        self._resonance.setWordWrap(True)
        self._resonance.setTextFormat(Qt.TextFormat.PlainText)
        self._conditions = QLabel(self)
        self._conditions.setWordWrap(True)
        self._conditions.setTextFormat(Qt.TextFormat.PlainText)
        self._conditions.setStyleSheet("color: #8a5a00;")
        apply_help(self._summary, translator, "measurement.comparison.summary")

        self._table = QTableWidget(0, 9, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        for column in range(9):
            self._table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        self._table.horizontalHeader().setStretchLastSection(True)
        apply_help(self._table, translator, "measurement.comparison.table")

        self._plot = pg.PlotWidget(self)
        self._plot.addLegend()
        self._plot.setLabel("bottom", translator.t("measurement.frequency_mhz"))
        self._plot.setLabel("left", "SWR")
        apply_help(self._plot, translator, "measurement.comparison.plot")

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._summary)
        layout.addWidget(self._resonance)
        layout.addWidget(self._conditions)
        layout.addWidget(self._table, 2)
        layout.addWidget(self._plot, 3)
        layout.addWidget(buttons)

        self.retranslate()

    def _set_initial(
        self,
        combo: QComboBox,
        target: UUID | None,
        *,
        fallback: int,
    ) -> None:
        if target is not None:
            index = combo.findData(target)
            if index >= 0:
                combo.setCurrentIndex(index)
                return
        if combo.count():
            combo.setCurrentIndex(min(fallback, combo.count() - 1))

    def _measurement(self, combo: QComboBox) -> Measurement | None:
        value = combo.currentData()
        if not isinstance(value, UUID):
            return None
        return next(
            (measurement for measurement in self._measurements if measurement.id == value),
            None,
        )

    def comparison(self) -> MeasurementPairComparison | None:
        return self._comparison

    def _condition_warning(self, before: Measurement, after: Measurement) -> str:
        changed: list[str] = []
        if before.calibration != after.calibration:
            changed.append(self._translator.t("measurement.calibration"))
        if before.reference_plane != after.reference_plane:
            changed.append(self._translator.t("measurement.reference_plane"))
        if before.feed_line != after.feed_line:
            changed.append(self._translator.t("measurement.feed_line"))
        if not math.isclose(
            before.reference_impedance_ohm,
            after.reference_impedance_ohm,
            rel_tol=1e-9,
            abs_tol=1e-9,
        ):
            changed.append(self._translator.t("measurement.reference"))
        if not changed:
            return ""
        return self._translator.t(
            "measurement.comparison_conditions",
            fields=", ".join(changed),
        )

    def _resonance_text(self, comparison: MeasurementPairComparison) -> str:
        before = " · ".join(
            f"{point.frequency_hz / 1e6:.3f} MHz ({point.impedance_ohm.real:.2f} Ω)"
            for point in comparison.before_resonances
        ) or self._translator.t("measurement.resonance_none")
        after = " · ".join(
            f"{point.frequency_hz / 1e6:.3f} MHz ({point.impedance_ohm.real:.2f} Ω)"
            for point in comparison.after_resonances
        ) or self._translator.t("measurement.resonance_none")
        parts = [
            self._translator.t("measurement.comparison_resonance_before", value=before),
            self._translator.t("measurement.comparison_resonance_after", value=after),
        ]
        if comparison.resonance_shift_hz is not None:
            parts.append(
                self._translator.t(
                    "measurement.comparison_resonance_shift",
                    value=f"{comparison.resonance_shift_hz / 1e3:+.3f}",
                )
            )
        return " · ".join(parts)

    def _render(self, *_args: object) -> None:
        before = self._measurement(self._before)
        after = self._measurement(self._after)
        self._table.setRowCount(0)
        self._plot.clear()
        self._conditions.clear()
        self._resonance.clear()
        if before is None or after is None:
            self._comparison = None
            self._summary.setText(self._translator.t("measurement.comparison_unavailable"))
            return
        comparison = compare_measurement_pair(
            before,
            after,
            reference_impedance_ohm=self._reference.value(),
        )
        self._comparison = comparison
        if not comparison.points:
            self._summary.setText(self._translator.t("measurement.before_after_no_overlap"))
        else:
            mean = comparison.mean_impedance_delta_ohm
            maximum = comparison.max_impedance_delta_ohm
            self._summary.setText(
                self._translator.t(
                    "measurement.before_after_summary",
                    count=comparison.compared_count,
                    mean=f"{mean:.3f}" if mean is not None else "—",
                    maximum=f"{maximum:.3f}" if maximum is not None else "—",
                    before=_swr_text(comparison.mean_swr_before),
                    after=_swr_text(comparison.mean_swr_after),
                )
            )
        self._resonance.setText(self._resonance_text(comparison))
        self._conditions.setText(self._condition_warning(before, after))
        self._table.setRowCount(len(comparison.points))
        for row, point in enumerate(comparison.points):
            values = (
                f"{point.frequency_hz / 1e6:.6f}",
                f"{point.before_ohm.real:.3f}",
                f"{point.before_ohm.imag:+.3f}",
                _swr_text(point.before_swr),
                f"{point.after_ohm.real:.3f}",
                f"{point.after_ohm.imag:+.3f}",
                _swr_text(point.after_swr),
                f"{point.impedance_delta_ohm:.3f}",
                _swr_text(point.swr_delta) if point.swr_delta is not None else "—",
            )
            for column, value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(value))

        frequencies = [
            point.frequency_hz / 1e6
            for point in comparison.points
            if math.isfinite(point.before_swr) and math.isfinite(point.after_swr)
        ]
        if frequencies:
            self._plot.plot(
                frequencies,
                [
                    point.before_swr
                    for point in comparison.points
                    if math.isfinite(point.before_swr) and math.isfinite(point.after_swr)
                ],
                pen=pg.mkPen("#175cd3", width=2),
                name=self._translator.t("measurement.comparison_before"),
            )
            self._plot.plot(
                frequencies,
                [
                    point.after_swr
                    for point in comparison.points
                    if math.isfinite(point.before_swr) and math.isfinite(point.after_swr)
                ],
                pen=pg.mkPen("#b54708", width=2),
                name=self._translator.t("measurement.comparison_after"),
            )

    def retranslate(self) -> None:
        t = self._translator.t
        self.setWindowTitle(t("measurement.before_after_title"))
        self._before_label.setText(t("measurement.comparison_before"))
        self._after_label.setText(t("measurement.comparison_after"))
        self._reference_label.setText(t("measurement.comparison_reference"))
        self._table.setHorizontalHeaderLabels(
            [
                t("measurement.frequency_mhz"),
                t("measurement.comparison_before_r"),
                t("measurement.comparison_before_x"),
                t("measurement.comparison_before_swr"),
                t("measurement.comparison_after_r"),
                t("measurement.comparison_after_x"),
                t("measurement.comparison_after_swr"),
                t("measurement.comparison_delta_z"),
                t("measurement.comparison_delta_swr"),
            ]
        )
        self._plot.setLabel("bottom", t("measurement.frequency_mhz"))
        self._plot.setLabel("left", "SWR")
        apply_help(self._summary, self._translator, "measurement.comparison.summary")
        apply_help(self._table, self._translator, "measurement.comparison.table")
        apply_help(self._plot, self._translator, "measurement.comparison.plot")
        self._render()
