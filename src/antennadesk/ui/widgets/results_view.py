# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Results tabs: band summary, impedance, SWR, pattern, and diagnostics."""

from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path

import pyqtgraph as pg  # type: ignore  # pyqtgraph ships no type stubs
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ...domain.common.validation import Diagnostic, Severity
from ...domain.environment.ground import GroundKind
from ...domain.measurement import Measurement, MeasurementPoint
from ...domain.measurement_comparison import compare_measurement
from ...domain.projects.project import DesignVariant
from ...domain.simulation.band_result import BandAnalysisResult, BandResult
from ...domain.simulation.band_summary import summarize_band
from ...domain.simulation.bands import amateur_band_for
from ...domain.simulation.pattern import PatternGainMetric, pattern_gain_offset_db
from ...domain.simulation.resonance import ResonancePoint, find_resonances
from ...domain.simulation.result import (
    CurrentSample,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from ...reporting.result_summary import representative_gain_frequency
from ..fonts import apply_plot_fonts, scaled_font_copy
from ..i18n import Translator
from ..theme import theme_colors
from .chart_cursor import ChartCursor, CursorSeries
from .polar_pattern_view import PolarPatternView
from .radiation_pattern_3d_view import RadiationPattern3DView


class ResultsView(QWidget):
    measurement_edit_requested = Signal(object)
    measurement_delete_requested = Signal(object)
    band_selected = Signal(object)

    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._colors = theme_colors(self.palette())
        self._result: SimulationResult | None = None
        self._design: DesignVariant | None = None
        self._pattern_frequencies: tuple[FrequencyResult, ...] = ()
        self._pattern_band_results: tuple[BandResult | None, ...] = ()
        self._band_analysis: BandAnalysisResult | None = None
        self._active_band: BandResult | None = None
        self._bands_tab_index = -1

        self._band_bar = QWidget(self)
        self._band_label = QLabel(self._band_bar)
        self._band_selector = QComboBox(self._band_bar)
        self._band_selector.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._band_selector.currentIndexChanged.connect(self._on_band_selector_changed)
        band_bar_layout = QHBoxLayout(self._band_bar)
        band_bar_layout.setContentsMargins(0, 0, 0, 4)
        band_bar_layout.setSpacing(6)
        band_bar_layout.addWidget(self._band_label)
        band_bar_layout.addWidget(self._band_selector)
        band_bar_layout.addStretch(1)
        self._band_bar.setVisible(False)

        self._tabs = QTabWidget(self)
        self._impedance_tab = QWidget(self)
        self._pattern_tab = QWidget(self)
        self._currents_tab = QWidget(self)
        self._measurements_tab = QWidget(self)
        self._diagnostics_tab = QWidget(self)
        self._raw_tab = QWidget(self)
        self._bands_tab = QWidget(self)
        self._bands_table = QTableWidget(0, 8, self._bands_tab)
        self._configure_table(self._bands_table)
        bands_layout = QVBoxLayout(self._bands_tab)
        bands_layout.setContentsMargins(0, 0, 0, 0)
        bands_layout.addWidget(self._bands_table)

        self._table = QTableWidget(0, 5, self._impedance_tab)
        self._configure_table(self._table)
        self._impedance_plot = self._make_plot()
        self._impedance_plot.addLegend()
        self._swr_plot = self._make_plot()
        self._resonance_label = QLabel(self._impedance_tab)
        self._resonance_label.setWordWrap(True)

        self._impedance_charts_splitter = QSplitter(
            Qt.Orientation.Horizontal,
            self._impedance_tab,
        )
        self._impedance_charts_splitter.addWidget(self._impedance_plot)
        self._impedance_charts_splitter.addWidget(self._swr_plot)
        self._impedance_charts_splitter.setStretchFactor(0, 1)
        self._impedance_charts_splitter.setStretchFactor(1, 1)

        impedance_splitter = QSplitter(Qt.Orientation.Vertical, self._impedance_tab)
        impedance_splitter.addWidget(self._table)
        impedance_splitter.addWidget(self._impedance_charts_splitter)
        impedance_splitter.setStretchFactor(0, 1)
        impedance_splitter.setStretchFactor(1, 3)
        impedance_layout = QVBoxLayout(self._impedance_tab)
        impedance_layout.setContentsMargins(0, 0, 0, 0)
        impedance_layout.addWidget(self._resonance_label)
        impedance_layout.addWidget(impedance_splitter)

        self._pattern_frequency = QComboBox(self._pattern_tab)
        self._pattern_frequency_label = QLabel(self._pattern_tab)
        self._pattern_mode = QComboBox(self._pattern_tab)
        self._pattern_mode.addItem("", "azimuth")
        self._pattern_mode.addItem("", "elevation")
        self._pattern_mode_label = QLabel(self._pattern_tab)
        self._pattern_cut = QComboBox(self._pattern_tab)
        self._pattern_cut_label = QLabel(self._pattern_tab)
        self._pattern_metric = QComboBox(self._pattern_tab)
        for metric in PatternGainMetric:
            self._pattern_metric.addItem("", metric.value)
        self._pattern_metric_label = QLabel(self._pattern_tab)
        self._pattern_plot = self._make_plot()
        self._polar_pattern = PolarPatternView(translator, self._pattern_tab)
        self._pattern_3d = RadiationPattern3DView(translator, self._pattern_tab)
        pattern_controls = QHBoxLayout()
        pattern_controls.addWidget(self._pattern_frequency_label)
        pattern_controls.addWidget(self._pattern_frequency)
        pattern_controls.addSpacing(12)
        pattern_controls.addWidget(self._pattern_mode_label)
        pattern_controls.addWidget(self._pattern_mode)
        pattern_controls.addSpacing(12)
        pattern_controls.addWidget(self._pattern_cut_label)
        pattern_controls.addWidget(self._pattern_cut)
        pattern_controls.addSpacing(12)
        pattern_controls.addWidget(self._pattern_metric_label)
        pattern_controls.addWidget(self._pattern_metric)
        pattern_controls.addStretch(1)
        pattern_layout = QVBoxLayout(self._pattern_tab)
        pattern_layout.setContentsMargins(0, 0, 0, 0)
        pattern_layout.addLayout(pattern_controls)
        pattern_splitter = QSplitter(Qt.Orientation.Vertical, self._pattern_tab)
        pattern_splitter.addWidget(self._pattern_plot)
        pattern_splitter.addWidget(self._polar_pattern)
        pattern_splitter.setStretchFactor(0, 1)
        pattern_splitter.setStretchFactor(1, 1)
        cut_tab = QWidget(self._pattern_tab)
        cut_layout = QVBoxLayout(cut_tab)
        cut_layout.setContentsMargins(0, 0, 0, 0)
        cut_layout.addWidget(pattern_splitter)
        self._pattern_view_tabs = QTabWidget(self._pattern_tab)
        self._pattern_view_tabs.addTab(cut_tab, "")
        self._pattern_view_tabs.addTab(self._pattern_3d, "")
        pattern_layout.addWidget(self._pattern_view_tabs)

        self._currents_frequency = QComboBox(self._currents_tab)
        self._currents_frequency_label = QLabel(self._currents_tab)
        self._currents_plot = self._make_plot()
        currents_controls = QHBoxLayout()
        currents_controls.addWidget(self._currents_frequency_label)
        currents_controls.addWidget(self._currents_frequency)
        currents_controls.addStretch(1)
        currents_layout = QVBoxLayout(self._currents_tab)
        currents_layout.setContentsMargins(0, 0, 0, 0)
        currents_layout.addLayout(currents_controls)
        currents_layout.addWidget(self._currents_plot)

        self._measurements: tuple[Measurement, ...] = ()
        self._measurement_selector = QComboBox(self._measurements_tab)
        self._measurement_selector_label = QLabel(self._measurements_tab)
        self._measurement_selector.currentIndexChanged.connect(self._render_measurements)
        self._measurement_metric = QComboBox(self._measurements_tab)
        self._measurement_metric.addItem("", "swr")
        self._measurement_metric.addItem("", "resistance")
        self._measurement_metric.addItem("", "reactance")
        self._measurement_metric.addItem("", "magnitude")
        self._measurement_metric.currentIndexChanged.connect(self._render_measurements)
        self._measurement_metric_label = QLabel(self._measurements_tab)
        self._measurement_edit = QPushButton(
            translator.t("measurement.edit"), self._measurements_tab
        )
        self._measurement_delete = QPushButton(
            translator.t("measurement.delete"), self._measurements_tab
        )
        self._measurement_edit.setEnabled(False)
        self._measurement_delete.setEnabled(False)
        self._measurement_edit.clicked.connect(self._request_measurement_edit)
        self._measurement_delete.clicked.connect(self._request_measurement_delete)
        self._measurement_table = QTableWidget(0, 8, self._measurements_tab)
        self._configure_table(self._measurement_table)
        self._measurement_plot = self._make_plot()
        self._measurement_plot.addLegend()
        self._measurement_details = QLabel(self._measurements_tab)
        self._measurement_details.setWordWrap(True)
        self._measurement_comparison = QLabel(self._measurements_tab)
        self._measurement_comparison.setWordWrap(True)
        self._measurement_resonance = QLabel(self._measurements_tab)
        self._measurement_resonance.setWordWrap(True)
        measurement_controls = QHBoxLayout()
        measurement_controls.addWidget(self._measurement_selector_label)
        measurement_controls.addWidget(self._measurement_selector)
        measurement_controls.addSpacing(12)
        measurement_controls.addWidget(self._measurement_metric_label)
        measurement_controls.addWidget(self._measurement_metric)
        measurement_controls.addSpacing(12)
        measurement_controls.addWidget(self._measurement_edit)
        measurement_controls.addWidget(self._measurement_delete)
        measurement_controls.addStretch(1)
        measurement_layout = QVBoxLayout(self._measurements_tab)
        measurement_layout.setContentsMargins(0, 0, 0, 0)
        measurement_layout.addLayout(measurement_controls)
        measurement_layout.addWidget(self._measurement_details)
        measurement_layout.addWidget(self._measurement_comparison)
        measurement_layout.addWidget(self._measurement_resonance)
        measurement_layout.addWidget(self._measurement_table, 1)
        measurement_layout.addWidget(self._measurement_plot, 2)

        self._summary = QLabel(self._diagnostics_tab)
        self._summary.setWordWrap(True)
        self._summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._gain_summary = QLabel(self._diagnostics_tab)
        self._gain_summary.setWordWrap(True)
        self._gain_summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._gain_summary.setVisible(False)
        self._diagnostics = QTableWidget(0, 3, self._diagnostics_tab)
        self._configure_table(self._diagnostics)
        self._diagnostics_empty = QLabel(self._diagnostics_tab)
        diagnostics_layout = QVBoxLayout(self._diagnostics_tab)
        diagnostics_layout.setContentsMargins(0, 0, 0, 0)
        diagnostics_layout.addWidget(self._summary)
        diagnostics_layout.addWidget(self._gain_summary)
        diagnostics_layout.addWidget(self._diagnostics)
        diagnostics_layout.addWidget(self._diagnostics_empty)

        self._raw_tabs = QTabWidget(self._raw_tab)
        self._raw_input = self._make_text_view()
        self._raw_output = self._make_text_view()
        self._raw_tabs.addTab(self._raw_input, "")
        self._raw_tabs.addTab(self._raw_output, "")
        raw_layout = QVBoxLayout(self._raw_tab)
        raw_layout.setContentsMargins(0, 0, 0, 0)
        raw_layout.addWidget(self._raw_tabs)

        self._tabs.addTab(self._impedance_tab, "")
        self._tabs.addTab(self._pattern_tab, "")
        self._tabs.addTab(self._currents_tab, "")
        self._tabs.addTab(self._measurements_tab, "")
        self._tabs.addTab(self._diagnostics_tab, "")
        self._tabs.addTab(self._raw_tab, "")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._band_bar)
        layout.addWidget(self._tabs)

        self._impedance_cursor = ChartCursor(self._impedance_plot)
        self._swr_cursor = ChartCursor(self._swr_plot)
        self._pattern_cursor = ChartCursor(self._pattern_plot)
        self._currents_cursor = ChartCursor(self._currents_plot)
        self._measurement_cursor = ChartCursor(self._measurement_plot)

        self._pattern_frequency.currentIndexChanged.connect(self._on_pattern_frequency_changed)
        self._pattern_mode.currentIndexChanged.connect(self._on_pattern_mode_changed)
        self._pattern_cut.currentIndexChanged.connect(self._render_pattern)
        self._pattern_metric.currentIndexChanged.connect(self._render_pattern)
        self._currents_frequency.currentIndexChanged.connect(self._render_currents)
        self._bands_table.itemSelectionChanged.connect(self._on_band_selected)
        self._bands_table.itemDoubleClicked.connect(self._on_band_double_clicked)
        self._apply_theme()
        self.retranslate()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.fontChanged.connect(self._on_application_font_changed)

    def _plots(self) -> tuple[pg.PlotWidget, ...]:
        return (
            self._impedance_plot,
            self._swr_plot,
            self._pattern_plot,
            self._currents_plot,
            self._measurement_plot,
        )

    @staticmethod
    def _make_plot() -> pg.PlotWidget:
        plot = pg.PlotWidget()
        plot.showGrid(x=True, y=True, alpha=0.3)
        return plot

    def _on_application_font_changed(self, font: QFont) -> None:
        del font
        apply_plot_fonts(self._plots())
        self._apply_raw_fonts()

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
        for cursor in (
            self._impedance_cursor,
            self._swr_cursor,
            self._pattern_cursor,
            self._currents_cursor,
            self._measurement_cursor,
        ):
            cursor.set_colors(
                text=self._colors.text,
                background=self._colors.background,
                line=self._colors.dimension,
            )
        self._polar_pattern.update()
        self._pattern_3d.update()

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.PaletteChange:
            self._apply_theme()
            self._render()
        super().changeEvent(event)

    @staticmethod
    def _configure_table(table: QTableWidget) -> None:
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)

    def _make_text_view(self) -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        view.setFont(scaled_font_copy(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)))
        return view

    def _apply_raw_fonts(self) -> None:
        for view in (self._raw_input, self._raw_output):
            view.setFont(
                scaled_font_copy(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
            )

    def save_pattern_image(self, path: Path) -> None:
        widget = (
            self._pattern_3d if self._pattern_view_tabs.currentIndex() == 1 else self._polar_pattern
        )
        pixmap = widget.grab()
        if pixmap.isNull() or not pixmap.save(str(path), "PNG"):
            raise OSError(f"could not write pattern image: {path}")

    def save_band_pattern_images(self, paths: Sequence[Path]) -> tuple[Path, ...]:
        """Save one current pattern view per band, then restore the selection."""

        analysis = self._band_analysis
        if analysis is None:
            raise ValueError("no band analysis is active")
        if len(paths) != len(analysis.bands):
            raise ValueError("one path is required per band")
        current_result = self._result
        current_band = self._active_band
        current_pattern_index = self._pattern_frequency.currentIndex()
        saved: list[Path] = []
        try:
            for band_result, path in zip(analysis.bands, paths, strict=True):
                if not any(frequency.far_field for frequency in band_result.result.frequencies):
                    continue
                self.set_result(band_result.result, band=band_result)
                self.save_pattern_image(path)
                saved.append(path)
        finally:
            self.set_result(current_result, band=current_band)
            if 0 <= current_pattern_index < self._pattern_frequency.count():
                self._pattern_frequency.setCurrentIndex(current_pattern_index)
        return tuple(saved)

    def set_design(self, design: DesignVariant | None) -> None:
        self._design = design
        self._render_pattern()

    def show_measurements(self) -> None:
        self._tabs.setCurrentWidget(self._measurements_tab)

    def show_bands(self) -> None:
        if self._bands_tab_index >= 0:
            self._tabs.setCurrentWidget(self._bands_tab)

    def set_measurements(self, measurements: tuple[Measurement, ...]) -> None:
        self._measurements = measurements
        self._measurement_selector.blockSignals(True)
        self._measurement_selector.clear()
        for measurement in measurements:
            self._measurement_selector.addItem(measurement.name)
        self._measurement_selector.blockSignals(False)
        if self._measurement_selector.count():
            self._measurement_selector.setCurrentIndex(0)
        self._render_measurements()

    def set_result(
        self,
        result: SimulationResult | None,
        *,
        band: BandResult | None = None,
    ) -> None:
        self._result = result
        self._active_band = band if band is not None else self._band_for_result(result)
        if band is not None:
            self._sync_band_selector(band)
        self._pattern_frequency.blockSignals(True)
        self._currents_frequency.blockSignals(True)
        self._pattern_frequency.clear()
        self._currents_frequency.clear()
        self._pattern_frequencies = ()
        self._pattern_band_results = ()
        if result is not None:
            for frequency in result.frequencies:
                self._currents_frequency.addItem(f"{frequency.frequency_hz / 1e6:g} MHz")
            entries = self._pattern_entries(result)
            self._pattern_frequencies = tuple(frequency for _band, frequency in entries)
            self._pattern_band_results = tuple(band for band, _frequency in entries)
            for band_result, frequency in entries:
                band_name = (
                    band_result.band.name
                    if band_result is not None
                    else getattr(amateur_band_for(frequency.frequency_hz), "name", None)
                )
                label = f"{frequency.frequency_hz / 1e6:g} MHz"
                if band_name is not None:
                    label += f" ({band_name})"
                self._pattern_frequency.addItem(label)
        if self._pattern_frequencies:
            target = (
                self._design.parameters.frequency_hz
                if self._design is not None
                else self._pattern_frequencies[0].frequency_hz
            )
            candidate_indices = [
                index
                for index, band_result in enumerate(self._pattern_band_results)
                if band_result is None or band_result.result is result
            ]
            if not candidate_indices:
                candidate_indices = list(range(len(self._pattern_frequencies)))
            self._pattern_frequency.setCurrentIndex(
                min(
                    candidate_indices,
                    key=lambda index: abs(self._pattern_frequencies[index].frequency_hz - target),
                )
            )
        self._pattern_frequency.blockSignals(False)
        self._currents_frequency.blockSignals(False)
        if self._currents_frequency.count() > 0:
            self._currents_frequency.setCurrentIndex(0)
        self._populate_cut_values()
        self._render()

    def _pattern_entries(
        self,
        result: SimulationResult,
    ) -> tuple[tuple[BandResult | None, FrequencyResult], ...]:
        if self._band_analysis is not None and self._band_analysis.bands:
            return tuple(
                (band_result, frequency)
                for band_result in self._band_analysis.bands
                for frequency in band_result.result.frequencies
                if frequency.far_field
            )
        return tuple((None, frequency) for frequency in result.frequencies if frequency.far_field)

    def _band_for_result(self, result: SimulationResult | None) -> BandResult | None:
        if result is None or self._band_analysis is None:
            return None
        return next(
            (band for band in self._band_analysis.bands if band.result is result),
            None,
        )

    def _chart_title(self, key: str) -> str:
        title = self._translator.t(key)
        if self._active_band is None:
            return title
        return f"{title} — {self._active_band.band.name}"

    def set_band_analysis(self, analysis: BandAnalysisResult | None) -> None:
        self._band_analysis = analysis
        self._active_band = None
        self._band_selector.blockSignals(True)
        self._band_selector.clear()
        self._band_selector.blockSignals(False)
        self._band_bar.setVisible(False)
        self._bands_table.blockSignals(True)
        self._bands_table.setRowCount(0)
        if analysis is None or not analysis.bands:
            if self._bands_tab_index >= 0:
                if self._tabs.currentWidget() is self._bands_tab:
                    self._tabs.setCurrentWidget(self._impedance_tab)
                self._tabs.removeTab(self._bands_tab_index)
                self._bands_tab_index = -1
            self._bands_table.blockSignals(False)
            if self._result is not None:
                self._render_impedance()
            return
        if self._bands_tab_index < 0:
            self._bands_tab_index = 0
            self._tabs.insertTab(
                self._bands_tab_index,
                self._bands_tab,
                self._translator.t("tab.bands"),
            )
        self._tabs.setTabText(
            self._bands_tab_index,
            self._translator.t("tab.bands"),
        )
        self._band_selector.blockSignals(True)
        for band_result in analysis.bands:
            self._band_selector.addItem(band_result.band.name)
        self._band_selector.setCurrentIndex(0)
        self._band_selector.blockSignals(False)
        self._band_bar.setVisible(True)
        self._render_bands()
        if self._bands_table.rowCount():
            self._bands_table.selectRow(0)
        self._bands_table.blockSignals(False)

    def _render_bands(self) -> None:
        self._bands_table.setRowCount(0)
        analysis = self._band_analysis
        if analysis is None:
            return
        for band_result in analysis.bands:
            summary = summarize_band(band_result.band, band_result.result)
            row = self._bands_table.rowCount()
            self._bands_table.insertRow(row)
            band_item = QTableWidgetItem(band_result.band.name)
            band_item.setData(Qt.ItemDataRole.UserRole, band_result)
            self._bands_table.setItem(row, 0, band_item)
            values = (
                f"{band_result.band.start_hz / 1e6:.3f} - {band_result.band.stop_hz / 1e6:.3f}",
                "—" if summary.best_swr is None else f"{summary.best_swr:.3f}",
                "—" if summary.best_swr_hz is None else f"{summary.best_swr_hz / 1e6:.6f} MHz",
                "—" if summary.max_gain_db is None else f"{summary.max_gain_db:.2f} dBi",
                "—" if summary.takeoff_deg is None else f"{summary.takeoff_deg:.1f}°",
                "—"
                if summary.efficiency_percent is None
                else f"{summary.efficiency_percent:.1f} %",
                self._translator.t(f"status.{summary.status.value}"),
            )
            for column, value in enumerate(values, start=1):
                self._bands_table.setItem(row, column, QTableWidgetItem(value))

    def _on_band_selected(self) -> None:
        row = self._bands_table.currentRow()
        if row < 0:
            return
        item = self._bands_table.item(row, 0)
        if item is None:
            return
        band_result = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(band_result, BandResult):
            return
        self.set_result(band_result.result, band=band_result)
        self.band_selected.emit(band_result)

    def _on_band_double_clicked(self, item: QTableWidgetItem) -> None:
        if item.row() < 0:
            return
        self._bands_table.selectRow(item.row())
        self._tabs.setCurrentWidget(self._impedance_tab)

    def _on_band_selector_changed(self, index: int) -> None:
        analysis = self._band_analysis
        if analysis is None or not 0 <= index < len(analysis.bands):
            return
        if index >= self._bands_table.rowCount():
            return
        current = self._bands_table.currentRow()
        self._bands_table.selectRow(index)
        if current == index and self._active_band is not analysis.bands[index]:
            self._on_band_selected()

    def retranslate(self) -> None:
        for widget, key in (
            (self._impedance_tab, "tab.impedance"),
            (self._pattern_tab, "tab.pattern"),
            (self._currents_tab, "tab.currents"),
            (self._measurements_tab, "tab.measurements"),
            (self._diagnostics_tab, "tab.diagnostics"),
            (self._raw_tab, "tab.raw"),
        ):
            self._tabs.setTabText(self._tabs.indexOf(widget), self._translator.t(key))
        if self._bands_tab_index >= 0:
            self._tabs.setTabText(
                self._bands_tab_index,
                self._translator.t("tab.bands"),
            )
        self._band_label.setText(self._translator.t("band.table.band"))
        self._bands_table.setHorizontalHeaderLabels(
            [
                self._translator.t("band.table.band"),
                self._translator.t("band.table.range"),
                self._translator.t("band.table.best_swr"),
                self._translator.t("band.table.at_frequency"),
                self._translator.t("band.table.gain"),
                self._translator.t("band.table.takeoff"),
                self._translator.t("band.table.efficiency"),
                self._translator.t("band.table.status"),
            ]
        )
        if self._band_analysis is not None:
            self._render_bands()
        self._pattern_view_tabs.setTabText(0, self._translator.t("pattern.cut_tab"))
        self._pattern_view_tabs.setTabText(1, self._translator.t("pattern.3d_tab"))
        self._table.setHorizontalHeaderLabels(
            [
                self._translator.t("table.frequency"),
                self._translator.t("table.resistance"),
                self._translator.t("table.reactance"),
                self._translator.t("table.impedance"),
                self._translator.t("table.swr"),
            ]
        )
        self._diagnostics.setHorizontalHeaderLabels(
            [
                self._translator.t("diagnostic.severity"),
                self._translator.t("diagnostic.code"),
                self._translator.t("diagnostic.message"),
            ]
        )
        self._pattern_frequency_label.setText(self._translator.t("pattern.frequency"))
        self._pattern_mode_label.setText(self._translator.t("pattern.mode"))
        self._pattern_mode.setItemText(0, self._translator.t("pattern.mode_azimuth"))
        self._pattern_mode.setItemText(1, self._translator.t("pattern.mode_elevation"))
        self._pattern_metric_label.setText(self._translator.t("pattern.metric"))
        for index, metric in enumerate(PatternGainMetric):
            self._pattern_metric.setItemText(
                index,
                self._translator.t(f"pattern.metric.{metric.value}"),
            )
        self._update_cut_label()
        self._currents_frequency_label.setText(self._translator.t("currents.frequency"))
        self._measurement_selector_label.setText(self._translator.t("measurement.select"))
        self._measurement_metric_label.setText(self._translator.t("measurement.metric"))
        self._measurement_edit.setText(self._translator.t("measurement.edit"))
        self._measurement_delete.setText(self._translator.t("measurement.delete"))
        self._measurement_metric.setItemText(0, self._translator.t("table.swr"))
        self._measurement_metric.setItemText(1, self._translator.t("table.resistance"))
        self._measurement_metric.setItemText(2, self._translator.t("table.reactance"))
        self._measurement_metric.setItemText(3, self._translator.t("table.impedance"))
        self._measurement_table.setHorizontalHeaderLabels(
            [
                self._translator.t("table.frequency"),
                self._translator.t("measurement.measured_r"),
                self._translator.t("measurement.measured_x"),
                self._translator.t("measurement.measured_z"),
                self._translator.t("measurement.measured_swr"),
                self._translator.t("measurement.simulated_r"),
                self._translator.t("measurement.simulated_x"),
                self._translator.t("measurement.impedance_error"),
            ]
        )
        self._raw_tabs.setTabText(0, self._translator.t("raw.input"))
        self._raw_tabs.setTabText(1, self._translator.t("raw.output"))
        self._render()

    def _render(self) -> None:
        self._render_impedance()
        self._render_pattern()
        self._render_currents()
        self._render_measurements()
        self._render_diagnostics()
        self._render_raw()

    def _render_impedance(self) -> None:
        self._table.setRowCount(0)
        self._impedance_plot.clear()
        self._swr_plot.clear()

        if self._result is None or not self._result.frequencies:
            self._impedance_cursor.clear()
            self._swr_cursor.clear()
            self._table.setRowCount(0)
            self._resonance_label.setText("")
            self._resonance_label.setVisible(False)
            self._impedance_plot.setTitle(
                self._translator.t("results.none"), color=self._colors.text
            )
            self._swr_plot.setTitle(self._translator.t("results.none"), color=self._colors.text)
            return

        frequencies = self._result.frequencies
        self._table.setRowCount(len(frequencies))
        for row, frequency in enumerate(frequencies):
            values = [
                f"{frequency.frequency_hz / 1e6:.6f}",
                f"{frequency.impedance_ohm.real:.3f}",
                f"{frequency.impedance_ohm.imag:+.3f}",
                f"{abs(frequency.impedance_ohm):.3f}",
                "∞" if math.isinf(frequency.swr) else f"{frequency.swr:.3f}",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._table.setItem(row, column, item)
        self._table.resizeColumnsToContents()

        x = [frequency.frequency_hz / 1e6 for frequency in frequencies]
        resistance = [frequency.impedance_ohm.real for frequency in frequencies]
        reactance = [frequency.impedance_ohm.imag for frequency in frequencies]
        self._impedance_plot.setTitle(self._chart_title("plot.impedance"), color=self._colors.text)
        self._impedance_plot.setLabel(
            "bottom", self._translator.t("table.frequency"), color=self._colors.text
        )
        self._impedance_plot.setLabel(
            "left", self._translator.t("plot.impedance_axis"), color=self._colors.text
        )
        self._impedance_plot.plot(
            x,
            resistance,
            pen=pg.mkPen(self._colors.resistance, width=2),
            symbol="o",
            symbolSize=5,
            name=self._translator.t("table.resistance"),
        )
        self._impedance_plot.plot(
            x,
            reactance,
            pen=pg.mkPen(self._colors.reactance, width=2),
            symbol="o",
            symbolSize=5,
            name=self._translator.t("table.reactance"),
        )

        swr_x: list[float] = []
        swr_y: list[float] = []
        for frequency in frequencies:
            if math.isfinite(frequency.swr):
                swr_x.append(frequency.frequency_hz / 1e6)
                swr_y.append(frequency.swr)
        self._swr_plot.setTitle(self._chart_title("plot.swr"), color=self._colors.text)
        self._swr_plot.setLabel(
            "bottom", self._translator.t("table.frequency"), color=self._colors.text
        )
        self._swr_plot.setLabel("left", self._translator.t("table.swr"), color=self._colors.text)
        if swr_x:
            self._swr_plot.plot(
                swr_x,
                swr_y,
                pen=pg.mkPen(self._colors.swr, width=2),
                symbol="o",
                symbolSize=5,
            )

        if len(frequencies) < 2:
            resonances: tuple[ResonancePoint, ...] = ()
            self._resonance_label.setText("")
            self._resonance_label.setVisible(False)
        else:
            resonances = find_resonances(
                [frequency.frequency_hz for frequency in frequencies],
                [frequency.impedance_ohm for frequency in frequencies],
            )
            self._resonance_label.setVisible(True)
        if resonances:
            self._resonance_label.setText(
                " · ".join(
                    self._translator.t(
                        "resonance.label",
                        frequency=f"{point.frequency_hz / 1e6:.3f}",
                        resistance=f"{point.impedance_ohm.real:.2f}",
                    )
                    for point in resonances
                )
            )
            for point in resonances:
                self._impedance_plot.addItem(
                    pg.InfiniteLine(
                        pos=point.frequency_hz / 1e6,
                        angle=90,
                        pen=pg.mkPen(self._colors.grid, style=Qt.PenStyle.DashLine),
                        label=f"{point.frequency_hz / 1e6:.3f} MHz",
                        labelOpts={"position": 0.96, "color": self._colors.secondary_text},
                    )
                )
                self._swr_plot.addItem(
                    pg.InfiniteLine(
                        pos=point.frequency_hz / 1e6,
                        angle=90,
                        pen=pg.mkPen(self._colors.grid, style=Qt.PenStyle.DashLine),
                    )
                )
        else:
            self._resonance_label.setText(self._translator.t("resonance.none"))

        energy = CursorSeries(
            self._translator.t("table.resistance"),
            tuple(x),
            tuple(resistance),
            self._colors.resistance,
        )
        reactance_series = CursorSeries(
            self._translator.t("table.reactance"),
            tuple(x),
            tuple(reactance),
            self._colors.reactance,
        )
        self._impedance_cursor.set_series(
            (energy, reactance_series),
            readout_builder=lambda cursor_x, _values: self._impedance_readout(
                cursor_x, frequencies
            ),
        )
        self._swr_cursor.set_series(
            (
                CursorSeries(
                    self._translator.t("table.swr"),
                    tuple(swr_x),
                    tuple(swr_y),
                    self._colors.swr,
                ),
            ),
            readout_builder=lambda cursor_x, _values: self._swr_readout(cursor_x, frequencies),
        )

    def _impedance_readout(self, x_mhz: float, frequencies: tuple[FrequencyResult, ...]) -> str:
        frequency = min(
            frequencies,
            key=lambda item: abs(item.frequency_hz / 1e6 - x_mhz),
        )
        swr = "∞" if math.isinf(frequency.swr) else f"{frequency.swr:.3f}"
        return self._translator.t(
            "cursor.impedance_readout",
            frequency=f"{frequency.frequency_hz / 1e6:.6f} MHz",
            resistance=f"{frequency.impedance_ohm.real:.3f} Ω",
            reactance=f"{frequency.impedance_ohm.imag:+.3f} Ω",
            magnitude=f"{abs(frequency.impedance_ohm):.3f} Ω",
            swr=swr,
        )

    def _swr_readout(self, x_mhz: float, frequencies: tuple[FrequencyResult, ...]) -> str:
        frequency = min(
            frequencies,
            key=lambda item: abs(item.frequency_hz / 1e6 - x_mhz),
        )
        swr = "∞" if math.isinf(frequency.swr) else f"{frequency.swr:.3f}"
        return self._translator.t(
            "cursor.swr_readout",
            frequency=f"{frequency.frequency_hz / 1e6:.6f} MHz",
            swr=swr,
        )

    def _render_currents(self) -> None:
        self._currents_plot.clear()
        self._currents_cursor.clear()
        if self._result is None or not self._result.frequencies:
            self._currents_plot.setTitle(
                self._translator.t("results.none"), color=self._colors.text
            )
            return
        index = self._currents_frequency.currentIndex()
        if index < 0 or index >= len(self._result.frequencies):
            return
        frequency = self._result.frequencies[index]
        currents = frequency.currents
        if not currents:
            self._currents_plot.setTitle(
                self._translator.t("currents.none"), color=self._colors.text
            )
            return

        segments = [current.segment for current in currents]
        magnitudes = [current.magnitude_a for current in currents]
        self._currents_plot.setTitle(self._translator.t("plot.currents"), color=self._colors.text)
        self._currents_plot.setLabel(
            "bottom", self._translator.t("currents.segment"), color=self._colors.text
        )
        self._currents_plot.setLabel(
            "left", self._translator.t("currents.magnitude"), color=self._colors.text
        )
        self._currents_plot.plot(
            segments,
            magnitudes,
            pen=pg.mkPen(self._colors.resistance, width=2),
            symbol="o",
            symbolSize=4,
        )
        self._currents_plot.addItem(
            pg.InfiniteLine(
                pos=frequency.feed_segment,
                angle=90,
                pen=pg.mkPen(self._colors.feed, style=Qt.PenStyle.DashLine),
                label=self._translator.t("geometry.feed"),
                labelOpts={"position": 0.95, "color": self._colors.feed},
            )
        )
        self._currents_cursor.set_series(
            (
                CursorSeries(
                    self._translator.t("currents.magnitude"),
                    tuple(float(value) for value in segments),
                    tuple(magnitudes),
                    self._colors.resistance,
                ),
            ),
            readout_builder=lambda cursor_x, _values: self._currents_readout(
                cursor_x, frequency, currents
            ),
        )

    def _currents_readout(
        self,
        segment_x: float,
        frequency: FrequencyResult,
        currents: tuple[CurrentSample, ...],
    ) -> str:
        current = min(
            currents,
            key=lambda item: abs(item.segment - segment_x),
        )
        return self._translator.t(
            "cursor.current_readout",
            frequency=f"{frequency.frequency_hz / 1e6:.6f} MHz",
            segment=current.segment,
            current=f"{current.magnitude_a:.4f} A",
        )

    def _on_pattern_frequency_changed(self, index: int) -> None:
        if 0 <= index < len(self._pattern_band_results):
            band_result = self._pattern_band_results[index]
            if band_result is not None and band_result.result is not self._result:
                self.set_result(band_result.result, band=band_result)
                self._select_pattern_index(index)
                self._select_bands_row(band_result)
                self.band_selected.emit(band_result)
                return
        self._populate_cut_values()
        self._render_pattern()

    def _select_pattern_index(self, index: int) -> None:
        if not 0 <= index < self._pattern_frequency.count():
            return
        self._pattern_frequency.blockSignals(True)
        self._pattern_frequency.setCurrentIndex(index)
        self._pattern_frequency.blockSignals(False)
        self._populate_cut_values()
        self._render_pattern()

    def _select_bands_row(self, band_result: BandResult) -> None:
        if self._band_analysis is None:
            return
        row = next(
            (
                index
                for index, candidate in enumerate(self._band_analysis.bands)
                if candidate is band_result
            ),
            -1,
        )
        if row < 0:
            return
        self._bands_table.blockSignals(True)
        self._bands_table.selectRow(row)
        self._bands_table.blockSignals(False)
        self._sync_band_selector(band_result)

    def _sync_band_selector(self, band_result: BandResult) -> None:
        analysis = self._band_analysis
        if analysis is None:
            return
        index = next(
            (
                candidate_index
                for candidate_index, candidate in enumerate(analysis.bands)
                if candidate is band_result
            ),
            -1,
        )
        if index < 0 or index >= self._band_selector.count():
            return
        self._band_selector.blockSignals(True)
        self._band_selector.setCurrentIndex(index)
        self._band_selector.blockSignals(False)

    def _on_pattern_mode_changed(self) -> None:
        self._populate_cut_values()
        self._render_pattern()

    def _pattern_mode_value(self) -> str:
        value = self._pattern_mode.currentData()
        return value if isinstance(value, str) else "azimuth"

    def _pattern_metric_value(self) -> PatternGainMetric:
        value = self._pattern_metric.currentData()
        try:
            return PatternGainMetric(str(value))
        except ValueError:
            return PatternGainMetric.POWER

    def _pattern_metric_name(self) -> str:
        return self._translator.t(f"pattern.metric.{self._pattern_metric_value().value}")

    def _update_cut_label(self) -> None:
        key = (
            "pattern.cut_phi" if self._pattern_mode_value() == "elevation" else "pattern.cut_theta"
        )
        self._pattern_cut_label.setText(self._translator.t(key))

    def _selected_pattern_frequency(self) -> FrequencyResult | None:
        index = self._pattern_frequency.currentIndex()
        if 0 <= index < len(self._pattern_frequencies):
            return self._pattern_frequencies[index]
        return None

    def _populate_cut_values(self) -> None:
        points = []
        frequency = self._selected_pattern_frequency()
        if frequency is not None:
            points = [point for point in frequency.far_field if point.gain_total_db is not None]
        mode = self._pattern_mode_value()
        current = self._pattern_cut.currentData()
        candidates: dict[float, list[float]] = {}
        for point in points:
            key = point.phi_deg if mode == "elevation" else point.theta_deg
            candidates.setdefault(key, []).append(
                point.gain_total_db if point.gain_total_db is not None else -999.0
            )
        self._pattern_cut.blockSignals(True)
        self._pattern_cut.clear()
        for value in sorted(candidates):
            label = f"φ={value:g}°" if mode == "elevation" else f"θ={value:g}°"
            self._pattern_cut.addItem(label, value)
        self._pattern_cut.blockSignals(False)
        self._update_cut_label()
        if not candidates:
            return
        if isinstance(current, (int, float)) and float(current) in candidates:
            default = float(current)
        elif mode == "elevation":
            default = max(
                candidates,
                key=lambda value: max(candidates[value]) - min(candidates[value]),
            )
        else:
            default = max(candidates, key=lambda value: max(candidates[value]))
        self._pattern_cut.blockSignals(True)
        self._pattern_cut.setCurrentIndex(self._pattern_cut.findData(default))
        self._pattern_cut.blockSignals(False)

    def _render_pattern(self) -> None:
        self._pattern_plot.clear()
        if self._result is None or not self._result.frequencies:
            self._pattern_cursor.clear()
            self._pattern_plot.setTitle(self._translator.t("results.none"), color=self._colors.text)
            self._polar_pattern.set_points(())
            self._pattern_3d.set_points(())
            return
        frequency = self._selected_pattern_frequency()
        if frequency is None:
            self._pattern_cursor.clear()
            title = (
                self._translator.t("pattern.negative_resistance")
                if any(item.impedance_ohm.real <= 0.0 for item in self._result.frequencies)
                else self._translator.t("pattern.none")
            )
            self._pattern_plot.setTitle(title, color=self._colors.text)
            self._polar_pattern.set_points(())
            self._pattern_3d.set_points(())
            return
        mode = self._pattern_mode_value()
        metric = self._pattern_metric_value()
        metric_label = self._pattern_metric_name()
        offset = pattern_gain_offset_db(frequency, metric)
        if offset is None:
            self._pattern_cursor.clear()
            title = (
                self._translator.t("pattern.negative_resistance")
                if frequency.impedance_ohm.real <= 0.0
                else self._translator.t("pattern.metric_unavailable", metric=metric_label)
            )
            self._pattern_plot.setTitle(title, color=self._colors.text)
            self._polar_pattern.set_points(())
            self._pattern_3d.set_points(())
            return
        selected_cut = self._pattern_cut.currentData()
        selected = float(selected_cut) if isinstance(selected_cut, (int, float)) else None
        points = []
        for point in frequency.far_field:
            if point.gain_total_db is None or selected is None:
                continue
            cut_value = point.phi_deg if mode == "elevation" else point.theta_deg
            if abs(cut_value - selected) >= 1e-6:
                continue
            points.append(
                (
                    point.theta_deg if mode == "elevation" else point.phi_deg,
                    point.gain_total_db + offset,
                )
            )
        if not points:
            self._pattern_cursor.clear()
            title = (
                self._translator.t("pattern.negative_resistance")
                if frequency.impedance_ohm.real <= 0.0
                else self._translator.t("pattern.none")
            )
            self._pattern_plot.setTitle(title, color=self._colors.text)
            self._polar_pattern.set_points(())
            self._pattern_3d.set_points(())
            return
        theta = [value[0] for value in points]
        gain = [value[1] for value in points]
        axis_label = (
            self._translator.t("pattern.elevation")
            if mode == "elevation"
            else self._translator.t("pattern.azimuth")
        )
        cut_symbol = "φ" if mode == "elevation" else "θ"
        cut_title = self._translator.t("plot.pattern")
        if selected is not None:
            cut_title = f"{cut_title} · {cut_symbol}={selected:g}°"
        self._pattern_plot.setTitle(cut_title, color=self._colors.text)
        self._pattern_plot.setLabel("bottom", axis_label, color=self._colors.text)
        self._pattern_plot.setLabel(
            "left",
            self._translator.t("pattern.metric_axis", metric=metric_label),
            color=self._colors.text,
        )
        self._pattern_plot.plot(
            theta,
            gain,
            pen=pg.mkPen(self._colors.pattern, width=2),
            symbol="o",
            symbolSize=4,
        )
        self._pattern_plot.setXRange(min(theta), max(theta), padding=0.02)
        self._pattern_cursor.set_series(
            (
                CursorSeries(
                    metric_label,
                    tuple(theta),
                    tuple(gain),
                    self._colors.pattern,
                ),
            ),
            readout_builder=lambda cursor_x, values: self._pattern_readout(cursor_x, mode, values),
            wrap_period=360.0 if mode == "azimuth" else None,
        )
        self._polar_pattern.set_cut(
            selected,
            symbol="φ" if mode == "elevation" else "θ",
        )
        self._polar_pattern.set_mirror(mode == "elevation")
        self._polar_pattern.set_closed(mode == "azimuth" or max(theta) >= 180.0)
        parameters = self._design.parameters if self._design is not None else None
        azimuth = getattr(parameters, "azimuth_deg", None)
        orientation = getattr(parameters, "orientation", None)
        vertical = getattr(orientation, "value", orientation) == "vertical"
        if mode == "azimuth" and azimuth is not None and not vertical:
            self._polar_pattern.set_antenna(float(azimuth))
        else:
            self._polar_pattern.set_antenna(None, vertical=vertical)
        polar_title = self._translator.t(
            "pattern.polar_elevation" if mode == "elevation" else "pattern.polar_azimuth"
        )
        self._polar_pattern.set_title(f"{polar_title} · {metric_label}")
        self._polar_pattern.set_points(tuple(zip(theta, gain, strict=True)))
        ground = (
            self._design is not None
            and self._design.antenna.environment.ground.kind is not GroundKind.FREE_SPACE
        )
        self._pattern_3d.set_points(
            tuple(
                (point.theta_deg, point.phi_deg, point.gain_total_db + offset)
                for point in frequency.far_field
                if point.gain_total_db is not None
            ),
            ground=ground,
        )

    def _pattern_readout(
        self,
        angle_deg: float,
        mode: str,
        values: tuple[tuple[str, float], ...],
    ) -> str:
        symbol = "φ" if mode == "elevation" else "θ"
        gain = f"{values[0][0]}: {values[0][1]:.3f} dBi" if values else "—"
        return self._translator.t(
            "cursor.gain_readout",
            angle=f"{symbol}={angle_deg:g}°",
            gain=gain,
        )

    def _render_measurements(self) -> None:
        self._measurement_table.setRowCount(0)
        self._measurement_plot.clear()
        self._measurement_cursor.clear()
        self._measurement_plot.setTitle(
            self._translator.t("measurement.none"), color=self._colors.text
        )
        self._measurement_resonance.setText("")
        self._measurement_resonance.setVisible(False)
        index = self._measurement_selector.currentIndex()
        valid = 0 <= index < len(self._measurements)
        self._measurement_edit.setEnabled(valid)
        self._measurement_delete.setEnabled(valid)
        if not valid:
            return
        measurement = self._measurements[index]
        details = []
        if measurement.calibration:
            details.append(
                self._translator.t("measurement.calibration_value", value=measurement.calibration)
            )
        if measurement.reference_plane:
            details.append(
                self._translator.t(
                    "measurement.reference_plane_value",
                    value=measurement.reference_plane,
                )
            )
        if measurement.feed_line:
            details.append(
                self._translator.t("measurement.feed_line_value", value=measurement.feed_line)
            )
        if measurement.notes:
            details.append(self._translator.t("measurement.notes_value", value=measurement.notes))
        self._measurement_details.setText(" · ".join(details))
        comparison = (
            compare_measurement(
                measurement,
                [frequency.frequency_hz for frequency in self._result.frequencies],
                [frequency.impedance_ohm for frequency in self._result.frequencies],
            )
            if self._result is not None and self._result.frequencies
            else None
        )
        self._measurement_table.setRowCount(
            len(comparison.points) if comparison is not None else len(measurement.points)
        )
        for row, point in enumerate(measurement.points):
            measured = point.impedance_ohm
            simulated = comparison.points[row].simulated_ohm if comparison is not None else None
            error = comparison.points[row].error_ohm if comparison is not None else None
            swr = point.swr(measurement.reference_impedance_ohm)
            values = [
                f"{point.frequency_hz / 1e6:.6f}",
                f"{measured.real:.3f}",
                f"{measured.imag:+.3f}",
                f"{abs(measured):.3f}",
                "∞" if math.isinf(swr) else f"{swr:.3f}",
                f"{simulated.real:.3f}" if simulated is not None else "—",
                f"{simulated.imag:+.3f}" if simulated is not None else "—",
                f"{error:.3f}" if error is not None else "—",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._measurement_table.setItem(row, column, item)
        self._measurement_table.resizeColumnsToContents()
        if comparison is None:
            self._measurement_comparison.setText("")
            self._measurement_comparison.setVisible(False)
        elif comparison.compared_count:
            self._measurement_comparison.setText(
                self._translator.t(
                    "measurement.comparison_summary",
                    count=comparison.compared_count,
                    mean=f"{comparison.mean_error_ohm:.3f}",
                    maximum=f"{comparison.max_error_ohm:.3f}",
                )
            )
            self._measurement_comparison.setVisible(True)
        else:
            self._measurement_comparison.setText(self._translator.t("measurement.comparison_none"))
            self._measurement_comparison.setVisible(True)

        metric = str(self._measurement_metric.currentData() or "swr")
        metric_label = self._measurement_metric.currentText()
        metric_colors = {
            "swr": self._colors.swr,
            "resistance": self._colors.resistance,
            "reactance": self._colors.reactance,
            "magnitude": self._colors.pattern,
        }

        def measured_value(point: MeasurementPoint) -> float:
            if metric == "resistance":
                return point.impedance_ohm.real
            if metric == "reactance":
                return point.impedance_ohm.imag
            if metric == "magnitude":
                return abs(point.impedance_ohm)
            return point.swr(measurement.reference_impedance_ohm)

        measured_series = [
            (point.frequency_hz / 1e6, measured_value(point)) for point in measurement.points
        ]
        measured_series = [
            (frequency, value) for frequency, value in measured_series if math.isfinite(value)
        ]
        simulated_series: list[tuple[float, float]] = []
        if self._result is not None and self._result.frequencies:
            for frequency in self._result.frequencies:
                if metric == "resistance":
                    metric_value = frequency.impedance_ohm.real
                elif metric == "reactance":
                    metric_value = frequency.impedance_ohm.imag
                elif metric == "magnitude":
                    metric_value = abs(frequency.impedance_ohm)
                else:
                    metric_value = frequency.swr
                if math.isfinite(metric_value):
                    simulated_series.append((frequency.frequency_hz / 1e6, metric_value))

        title_key = (
            "measurement.comparison_title" if simulated_series else "measurement.measured_title"
        )
        self._measurement_plot.setTitle(
            self._translator.t(title_key, metric=metric_label),
            color=self._colors.text,
        )
        self._measurement_plot.setLabel(
            "bottom", self._translator.t("table.frequency"), color=self._colors.text
        )
        self._measurement_plot.setLabel("left", metric_label, color=self._colors.text)
        if measured_series:
            self._measurement_plot.plot(
                [point[0] for point in measured_series],
                [point[1] for point in measured_series],
                pen=pg.mkPen(metric_colors[metric], width=2),
                name=self._translator.t("measurement.measured"),
            )
        if simulated_series:
            self._measurement_plot.plot(
                [point[0] for point in simulated_series],
                [point[1] for point in simulated_series],
                pen=pg.mkPen(self._colors.pattern, width=2, style=Qt.PenStyle.DashLine),
                name=self._translator.t("measurement.simulated"),
            )

        cursor_series: list[CursorSeries] = []
        if measured_series:
            cursor_series.append(
                CursorSeries(
                    self._translator.t("measurement.measured"),
                    tuple(point[0] for point in measured_series),
                    tuple(point[1] for point in measured_series),
                    metric_colors[metric],
                    metric_label,
                )
            )
        if simulated_series:
            cursor_series.append(
                CursorSeries(
                    self._translator.t("measurement.simulated"),
                    tuple(point[0] for point in simulated_series),
                    tuple(point[1] for point in simulated_series),
                    self._colors.pattern,
                    metric_label,
                )
            )
        if cursor_series:
            self._measurement_cursor.set_series(
                cursor_series,
                readout_builder=lambda cursor_x, values: self._measurement_readout(
                    cursor_x, values
                ),
            )

        measured_resonances = find_resonances(
            [point.frequency_hz for point in measurement.points],
            [point.impedance_ohm for point in measurement.points],
        )
        simulated_resonances = (
            find_resonances(
                [frequency.frequency_hz for frequency in self._result.frequencies],
                [frequency.impedance_ohm for frequency in self._result.frequencies],
            )
            if self._result is not None and self._result.frequencies
            else ()
        )
        resonance_parts: list[str] = []
        if measured_resonances:
            resonance_parts.append(
                " · ".join(
                    self._translator.t(
                        "measurement.resonance_measured",
                        frequency=f"{point.frequency_hz / 1e6:.3f}",
                        resistance=f"{point.impedance_ohm.real:.2f}",
                    )
                    for point in measured_resonances
                )
            )
        else:
            resonance_parts.append(self._translator.t("measurement.resonance_none"))
        if simulated_resonances:
            resonance_parts.append(
                " · ".join(
                    self._translator.t(
                        "measurement.resonance_simulated",
                        frequency=f"{point.frequency_hz / 1e6:.3f}",
                        resistance=f"{point.impedance_ohm.real:.2f}",
                    )
                    for point in simulated_resonances
                )
            )
        if len(measured_resonances) == 1 and len(simulated_resonances) == 1:
            delta = (
                measured_resonances[0].frequency_hz - simulated_resonances[0].frequency_hz
            ) / 1e6
            resonance_parts.append(
                self._translator.t("measurement.resonance_delta", delta=f"{delta:+.3f}")
            )
        self._measurement_resonance.setText(" · ".join(resonance_parts))
        self._measurement_resonance.setVisible(bool(resonance_parts))

    def _measurement_readout(
        self,
        frequency_mhz: float,
        values: tuple[tuple[str, float], ...],
    ) -> str:
        parts = [f"{frequency_mhz:.6f} MHz"]
        parts.extend(f"{label}: {value:.3f}" for label, value in values)
        return " · ".join(parts)

    def _request_measurement_edit(self) -> None:
        index = self._measurement_selector.currentIndex()
        if 0 <= index < len(self._measurements):
            self.measurement_edit_requested.emit(self._measurements[index])

    def _request_measurement_delete(self) -> None:
        index = self._measurement_selector.currentIndex()
        if 0 <= index < len(self._measurements):
            self.measurement_delete_requested.emit(self._measurements[index])

    def _render_diagnostics(self) -> None:
        self._diagnostics.setRowCount(0)
        if self._result is None:
            self._summary.setText(self._translator.t("results.none"))
            self._gain_summary.setText("")
            self._gain_summary.setVisible(False)
            self._diagnostics_empty.setText("")
            self._diagnostics_empty.setVisible(False)
            return

        status = self._status_text(self._result.status)
        self._summary.setText(
            self._translator.t(
                "results.summary",
                status=status,
                solver=self._result.solver.name,
                version=self._result.solver.version,
                frequencies=len(self._result.frequencies),
                duration=self._result.duration_s,
                fingerprint=self._result.model_fingerprint[:12],
            )
        )
        gain_summary = self._gain_summary_text()
        self._gain_summary.setText(gain_summary)
        self._gain_summary.setVisible(bool(gain_summary))
        diagnostics = self._result.diagnostics
        self._diagnostics.setRowCount(len(diagnostics))
        for row, diagnostic in enumerate(diagnostics):
            self._diagnostics.setItem(
                row,
                0,
                QTableWidgetItem(self._severity_text(diagnostic.severity)),
            )
            self._diagnostics.setItem(row, 1, QTableWidgetItem(diagnostic.code))
            message = QTableWidgetItem(self._diagnostic_message(diagnostic))
            message.setToolTip(diagnostic.message)
            self._diagnostics.setItem(row, 2, message)
        self._diagnostics.resizeColumnsToContents()
        self._diagnostics.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._diagnostics_empty.setText(self._translator.t("diagnostic.none"))
        self._diagnostics_empty.setVisible(not diagnostics)

    def _gain_summary_text(self) -> str:
        if self._result is None:
            return ""
        metrics: tuple[float | None, ...] = (
            self._result.max_total_gain_db,
            self._result.max_directivity_db,
            self._result.max_realized_gain_db,
        )
        frequency = representative_gain_frequency(self._result)
        if frequency is not None:
            metrics = (
                *metrics,
                frequency.mismatch_loss_db,
                frequency.feed_line_loss_db,
                frequency.network_loss_db,
            )
        if all(metric is None for metric in metrics):
            return ""
        t = self._translator.t

        def value(value: float | None, suffix: str) -> str:
            return f"{value:.2f} {suffix}" if value is not None else "—"

        first = t(
            "results.gain_summary",
            gain=value(self._result.max_total_gain_db, "dBi"),
            directivity=value(self._result.max_directivity_db, "dBi"),
            realized=value(self._result.max_realized_gain_db, "dBi"),
        )
        if frequency is None:
            return first
        second = t(
            "results.link_summary",
            frequency=f"{frequency.frequency_hz / 1e6:.3f}",
            mismatch=value(frequency.mismatch_loss_db, "dB"),
            line=value(frequency.feed_line_loss_db, "dB"),
            network=value(frequency.network_loss_db, "dB"),
        )
        return f"{first} · {second}"

    def _render_raw(self) -> None:
        if self._result is None:
            self._raw_input.setPlainText("")
            self._raw_output.setPlainText("")
            return
        self._raw_input.setPlainText(self._result.raw_input)
        self._raw_output.setPlainText(self._result.raw_output)

    def _status_text(self, status: SimulationStatus) -> str:
        return self._translator.t(f"status_value.{status.value}")

    def _severity_text(self, severity: Severity) -> str:
        return self._translator.t(f"severity.{severity.value}")

    def _diagnostic_message(self, diagnostic: Diagnostic) -> str:
        key = f"diagnostic.{diagnostic.code}"
        translated = self._translator.t(key)
        return diagnostic.message if translated == key else translated
