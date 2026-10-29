# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""A/B comparison of two design variants."""

from __future__ import annotations

import math
from collections.abc import Mapping
from uuid import UUID

import pyqtgraph as pg
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.dipole import DipoleParameters
from ...domain.antennas.folded_dipole import FoldedDipoleParameters
from ...domain.antennas.loop import LoopParameters
from ...domain.projects.project import DesignVariant, Project
from ...domain.simulation.result import FrequencyResult, SimulationResult
from ..i18n import Translator
from ..theme import theme_colors


class ComparisonDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        project: Project,
        results: Mapping[UUID, SimulationResult],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._results = results
        self._colors = theme_colors(self.palette())
        self.setWindowTitle(translator.t("compare.title"))
        self.resize(960, 780)

        self._combo_a = QComboBox(self)
        self._combo_b = QComboBox(self)
        for design in project.designs:
            self._combo_a.addItem(design.name, str(design.id))
            self._combo_b.addItem(design.name, str(design.id))
        if self._combo_b.count() > 1:
            self._combo_b.setCurrentIndex(1)

        self._label_a = QLabel(translator.t("compare.variant_a"), self)
        self._label_b = QLabel(translator.t("compare.variant_b"), self)
        controls = QHBoxLayout()
        controls.addWidget(self._label_a)
        controls.addWidget(self._combo_a)
        controls.addWidget(self._label_b)
        controls.addWidget(self._combo_b)
        controls.addStretch(1)

        self._table = QTableWidget(0, 3, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setMinimumHeight(260)

        self._swr_plot = self._make_plot()
        self._swr_plot.addLegend()
        self._pattern_plot = self._make_plot()
        self._pattern_plot.addLegend()

        self._note = QLabel(self)
        self._note.setWordWrap(True)
        self._note.setVisible(False)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.rejected.connect(self.accept)
        buttons.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self._table)
        layout.addWidget(self._swr_plot, 1)
        layout.addWidget(self._pattern_plot, 1)
        layout.addWidget(self._note)
        layout.addWidget(buttons)

        self._combo_a.currentIndexChanged.connect(self._refresh)
        self._combo_b.currentIndexChanged.connect(self._refresh)
        self._apply_theme()
        self._refresh()

    @staticmethod
    def _make_plot() -> pg.PlotWidget:
        plot = pg.PlotWidget()
        plot.showGrid(x=True, y=True, alpha=0.3)
        return plot

    def _apply_theme(self) -> None:
        self._colors = theme_colors(self.palette())
        for plot in (self._swr_plot, self._pattern_plot):
            plot.setBackground(self._colors.plot_background)
            for axis_name in ("left", "bottom"):
                axis = plot.getAxis(axis_name)
                axis.setPen(self._colors.axis)
                axis.setTextPen(self._colors.axis)
            legend = plot.plotItem.legend
            if legend is not None:
                legend.setLabelTextColor(self._colors.text)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.PaletteChange:
            self._apply_theme()
            self._refresh()
        super().changeEvent(event)

    def _design_for(self, combo: QComboBox) -> DesignVariant | None:
        value = combo.currentData()
        if not isinstance(value, str):
            return None
        try:
            return self._project.design_by_id(UUID(value))
        except (KeyError, ValueError):
            return None

    @staticmethod
    def _closest_frequency(
        result: SimulationResult | None,
        target_hz: float,
    ) -> FrequencyResult | None:
        if result is None or not result.frequencies:
            return None
        return min(result.frequencies, key=lambda item: abs(item.frequency_hz - target_hz))

    @staticmethod
    def _max_gain(result: SimulationResult | None) -> float | None:
        if result is None:
            return None
        gains = [
            point.gain_total_db
            for frequency in result.frequencies
            for point in frequency.far_field
            if point.gain_total_db is not None
        ]
        return max(gains) if gains else None

    def _status_text(self, result: SimulationResult | None) -> str:
        if result is None:
            return "—"
        return self._translator.t(f"status_value.{result.status.value}")

    def _rows(
        self,
        design: DesignVariant | None,
        result: SimulationResult | None,
    ) -> list[tuple[str, str]]:
        t = self._translator.t
        if design is None:
            return [(t("compare.metric"), "—")]
        frequency = self._closest_frequency(result, design.parameters.frequency_hz)
        max_gain = self._max_gain(result)
        efficiency = (
            frequency.power_budget.efficiency_percent
            if frequency is not None and frequency.power_budget is not None
            else None
        )
        parameters = design.parameters
        if isinstance(parameters, FoldedDipoleParameters):
            primary = f"{parameters.total_length_m:.3f} m"
            secondary = f"{parameters.spacing_m:.3f} m"
        elif isinstance(parameters, LoopParameters):
            primary = f"{parameters.circumference_m:.3f} m"
            secondary = str(parameters.sides)
        elif isinstance(parameters, DipoleParameters):
            primary = f"{parameters.total_length_m:.3f} m"
            secondary = "—"
        else:
            primary = "—"
            secondary = "—"
        return [
            (
                t("field.antenna_type"),
                t(f"antenna_type.{design.antenna_type}"),
            ),
            (t("field.frequency"), f"{parameters.frequency_hz / 1e6:.6f} MHz"),
            (t("field.primary_dimension"), primary),
            (t("field.secondary_dimension"), secondary),
            (t("field.height"), f"{parameters.height_m:.3f} m"),
            (t("field.azimuth"), f"{parameters.azimuth_deg:.1f}°"),
            (t("field.diameter"), f"{parameters.wire_radius_m * 2000.0:.3f} mm"),
            (t("table.resistance"), f"{frequency.impedance_ohm.real:.3f}" if frequency else "—"),
            (t("table.reactance"), f"{frequency.impedance_ohm.imag:+.3f}" if frequency else "—"),
            (t("table.impedance"), f"{abs(frequency.impedance_ohm):.3f}" if frequency else "—"),
            (
                t("table.swr"),
                (
                    "∞"
                    if frequency and math.isinf(frequency.swr)
                    else (f"{frequency.swr:.3f}" if frequency else "—")
                ),
            ),
            (t("compare.max_gain"), f"{max_gain:.2f}" if max_gain is not None else "—"),
            (t("compare.efficiency"), (f"{efficiency:.2f}" if efficiency is not None else "—")),
            (
                t("results.solver"),
                (f"{result.solver.name} {result.solver.version}" if result else "—"),
            ),
            (t("results.status"), self._status_text(result)),
            (t("results.frequency_count"), str(len(result.frequencies)) if result else "—"),
        ]

    def _refresh(self) -> None:
        design_a = self._design_for(self._combo_a)
        design_b = self._design_for(self._combo_b)
        result_a = self._results.get(design_a.id) if design_a else None
        result_b = self._results.get(design_b.id) if design_b else None

        rows_a = self._rows(design_a, result_a)
        rows_b = self._rows(design_b, result_b)
        self._table.setColumnCount(3)
        self._table.setRowCount(len(rows_a))
        self._table.setHorizontalHeaderLabels(
            [
                self._translator.t("compare.metric"),
                design_a.name if design_a else "A",
                design_b.name if design_b else "B",
            ]
        )
        for index, (label, value_a) in enumerate(rows_a):
            value_b = rows_b[index][1] if index < len(rows_b) else "—"
            self._table.setItem(index, 0, QTableWidgetItem(label))
            self._table.setItem(index, 1, QTableWidgetItem(value_a))
            self._table.setItem(index, 2, QTableWidgetItem(value_b))
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setStretchLastSection(True)

        self._note.setText(self._translator.t("compare.no_result"))
        self._note.setVisible(result_a is None or result_b is None)
        self._render_charts(design_a, design_b, result_a, result_b)

    def _render_charts(
        self,
        design_a: DesignVariant | None,
        design_b: DesignVariant | None,
        result_a: SimulationResult | None,
        result_b: SimulationResult | None,
    ) -> None:
        self._swr_plot.clear()
        self._pattern_plot.clear()
        self._swr_plot.setTitle(self._translator.t("compare.swr"), color=self._colors.text)
        self._swr_plot.setLabel(
            "bottom", self._translator.t("table.frequency"), color=self._colors.text
        )
        self._swr_plot.setLabel("left", self._translator.t("table.swr"), color=self._colors.text)
        self._pattern_plot.setTitle(self._translator.t("compare.pattern"), color=self._colors.text)
        self._pattern_plot.setLabel(
            "bottom", self._translator.t("pattern.elevation"), color=self._colors.text
        )
        self._pattern_plot.setLabel(
            "left", self._translator.t("pattern.gain"), color=self._colors.text
        )

        for label, result, color in (
            ("A", result_a, self._colors.series_a),
            ("B", result_b, self._colors.series_b),
        ):
            if result is None:
                continue
            swr_points = [
                (frequency.frequency_hz / 1e6, frequency.swr)
                for frequency in result.frequencies
                if math.isfinite(frequency.swr)
            ]
            design = design_a if label == "A" else design_b
            legend = design.name if design is not None else label
            if swr_points:
                self._swr_plot.plot(
                    [point[0] for point in swr_points],
                    [point[1] for point in swr_points],
                    pen=pg.mkPen(color, width=2),
                    symbol="o",
                    symbolSize=4,
                    name=legend,
                )
            if design is None:
                continue
            frequency = self._closest_frequency(result, design.parameters.frequency_hz)
            if frequency is None:
                continue
            pattern = [
                (point.theta_deg, point.gain_total_db)
                for point in frequency.far_field
                if point.gain_total_db is not None
            ]
            if pattern:
                self._pattern_plot.plot(
                    [point[0] for point in pattern],
                    [point[1] for point in pattern],
                    pen=pg.mkPen(color, width=2),
                    symbol="o",
                    symbolSize=4,
                    name=legend,
                )
