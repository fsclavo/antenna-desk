# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""A/B comparison of two design variants."""

from __future__ import annotations

import math
from collections.abc import Mapping
from uuid import UUID

import pyqtgraph as pg  # type: ignore  # pyqtgraph ships no type stubs
from PySide6.QtCore import QEvent
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
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
from ...domain.antennas.magnetic_loop import MagneticLoopParameters
from ...domain.antennas.t2fd import T2FDParameters
from ...domain.antennas.trap_dipole import TrapDipoleParameters
from ...domain.projects.project import DesignVariant, Project
from ...domain.simulation.band_result import BandAnalysisResult
from ...domain.simulation.band_summary import summarize_band
from ...domain.simulation.bands import AmateurBand
from ...domain.simulation.result import FrequencyResult, SimulationResult
from ..fonts import apply_plot_fonts, scaled_dialog_size
from ..i18n import Translator
from ..theme import theme_colors
from ..units import (
    UnitSystem,
    diameter_from_m,
    diameter_unit_key,
    length_from_m,
    length_unit_key,
)


class ComparisonDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        project: Project,
        results: Mapping[UUID, SimulationResult],
        parent: QWidget | None = None,
        *,
        band_analyses: Mapping[UUID, BandAnalysisResult] | None = None,
        unit_system: UnitSystem = UnitSystem.METRIC,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._results = results
        self._band_analyses = band_analyses or {}
        self._unit_system = unit_system
        self._colors = theme_colors(self.palette())
        self.setWindowTitle(translator.t("compare.title"))
        self.resize(*scaled_dialog_size(960, 780))

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

        self._band_label = QLabel(translator.t("band.group_title"), self)
        self._band_table = QTableWidget(0, 5, self)
        self._band_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._band_table.setAlternatingRowColors(True)
        self._band_table.verticalHeader().setVisible(False)
        self._band_table.horizontalHeader().setStretchLastSection(True)
        self._band_table.setMaximumHeight(160)
        self._band_label.setVisible(False)
        self._band_table.setVisible(False)

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
        layout.addWidget(self._band_label)
        layout.addWidget(self._band_table)
        layout.addWidget(self._swr_plot, 1)
        layout.addWidget(self._pattern_plot, 1)
        layout.addWidget(self._note)
        layout.addWidget(buttons)

        self._combo_a.currentIndexChanged.connect(self._refresh)
        self._combo_b.currentIndexChanged.connect(self._refresh)
        self._apply_theme()
        self._refresh()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.fontChanged.connect(self._on_application_font_changed)

    def _plots(self) -> tuple[pg.PlotWidget, ...]:
        return (self._swr_plot, self._pattern_plot)

    @staticmethod
    def _make_plot() -> pg.PlotWidget:
        plot = pg.PlotWidget()
        plot.showGrid(x=True, y=True, alpha=0.3)
        return plot

    def _on_application_font_changed(self, font: QFont) -> None:
        del font
        apply_plot_fonts(self._plots())

    def _apply_theme(self) -> None:
        self._colors = theme_colors(self.palette())
        for plot in self._plots():
            plot.setBackground(self._colors.plot_background)
            for axis_name in ("left", "bottom"):
                axis = plot.getAxis(axis_name)
                axis.setPen(self._colors.axis)
                axis.setTextPen(self._colors.axis)
            legend = plot.plotItem.legend
            if legend is not None:
                legend.setLabelTextColor(self._colors.text)
        apply_plot_fonts(self._plots())

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
        max_directivity = result.max_directivity_db if result is not None else None
        max_realized = result.max_realized_gain_db if result is not None else None
        efficiency = (
            frequency.power_budget.efficiency_percent
            if frequency is not None and frequency.power_budget is not None
            else None
        )
        parameters = design.parameters
        length_unit = t(length_unit_key(self._unit_system))
        diameter_unit = t(diameter_unit_key(self._unit_system))

        def length(value_m: float) -> str:
            return f"{length_from_m(value_m, self._unit_system):.3f} {length_unit}"

        if isinstance(parameters, FoldedDipoleParameters):
            primary = length(parameters.total_length_m)
            secondary = length(parameters.spacing_m)
        elif isinstance(parameters, LoopParameters):
            primary = length(parameters.circumference_m)
            secondary = str(parameters.sides)
        elif isinstance(parameters, MagneticLoopParameters):
            primary = length(parameters.diameter_m)
            secondary = f"{parameters.tuning_capacitance_f * 1e12:.3f} pF"
        elif isinstance(parameters, DipoleParameters):
            primary = length(parameters.total_length_m)
            secondary = "—"
        elif isinstance(parameters, TrapDipoleParameters):
            primary = length(parameters.total_length_m)
            secondary = f"{parameters.trap_frequency_hz / 1e6:.3f} MHz"
        elif isinstance(parameters, T2FDParameters):
            primary = length(parameters.length_m)
            secondary = f"{parameters.termination_resistance_ohm:g} Ω"
        else:
            primary = "—"
            secondary = "—"
        height_m = getattr(parameters, "height_m", None)
        azimuth_deg = getattr(parameters, "azimuth_deg", None)
        wire_radius_m = getattr(parameters, "wire_radius_m", None)
        return [
            (
                t("field.antenna_type"),
                t(f"antenna_type.{design.antenna_type}"),
            ),
            (t("field.frequency"), f"{parameters.frequency_hz / 1e6:.6f} MHz"),
            (t("field.primary_dimension"), primary),
            (t("field.secondary_dimension"), secondary),
            (
                t("field.height"),
                length(height_m) if height_m is not None else "—",
            ),
            (t("field.azimuth"), f"{azimuth_deg:.1f}°" if azimuth_deg is not None else "—"),
            (
                t("field.diameter"),
                (
                    f"{diameter_from_m(wire_radius_m * 2.0, self._unit_system):.4f} {diameter_unit}"
                    if wire_radius_m is not None
                    else "—"
                ),
            ),
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
            (
                t("compare.max_directivity"),
                f"{max_directivity:.2f}" if max_directivity is not None else "—",
            ),
            (
                t("compare.max_realized_gain"),
                f"{max_realized:.2f}" if max_realized is not None else "—",
            ),
            (t("compare.efficiency"), (f"{efficiency:.2f}" if efficiency is not None else "—")),
            (
                t("results.solver"),
                (f"{result.solver.name} {result.solver.version}" if result else "—"),
            ),
            (t("results.status"), self._status_text(result)),
            (t("results.frequency_count"), str(len(result.frequencies)) if result else "—"),
        ]

    def _render_band_table(
        self,
        design_a: DesignVariant | None,
        design_b: DesignVariant | None,
    ) -> None:
        analysis_a = self._band_analyses.get(design_a.id) if design_a else None
        analysis_b = self._band_analyses.get(design_b.id) if design_b else None
        if analysis_a is None and analysis_b is None:
            self._band_label.setVisible(False)
            self._band_table.setVisible(False)
            self._band_table.setRowCount(0)
            return
        bands: dict[str, AmateurBand] = {}
        for analysis in (analysis_a, analysis_b):
            if analysis is None:
                continue
            for band_result in analysis.bands:
                bands[band_result.band.name] = band_result.band
        self._band_table.setRowCount(0)
        self._band_table.setColumnCount(5)
        self._band_table.setHorizontalHeaderLabels(
            [
                self._translator.t("band.table.band"),
                f"{design_a.name if design_a else 'A'} {self._translator.t('table.swr')}",
                f"{design_b.name if design_b else 'B'} {self._translator.t('table.swr')}",
                f"{design_a.name if design_a else 'A'} {self._translator.t('band.table.gain')}",
                f"{design_b.name if design_b else 'B'} {self._translator.t('band.table.gain')}",
            ]
        )
        for band_id, band in sorted(
            bands.items(),
            key=lambda item: item[1].start_hz,
        ):
            row = self._band_table.rowCount()
            self._band_table.insertRow(row)
            self._band_table.setItem(row, 0, QTableWidgetItem(band_id))
            for column, analysis in ((1, analysis_a), (2, analysis_b)):
                analysis_result = (
                    analysis.result_for_band(band_id) if analysis is not None else None
                )
                summary = (
                    summarize_band(band, analysis_result.result)
                    if analysis_result is not None
                    else None
                )
                self._band_table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        "—"
                        if summary is None or summary.best_swr is None
                        else f"{summary.best_swr:.3f}"
                    ),
                )
                gain_column = column + 2
                self._band_table.setItem(
                    row,
                    gain_column,
                    QTableWidgetItem(
                        "—"
                        if summary is None or summary.max_gain_db is None
                        else f"{summary.max_gain_db:.2f} dBi"
                    ),
                )
        self._band_label.setVisible(True)
        self._band_table.setVisible(True)
        self._band_table.resizeColumnsToContents()

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
        self._render_band_table(design_a, design_b)
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
