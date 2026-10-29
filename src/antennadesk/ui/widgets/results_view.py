# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Results tabs: impedance, SWR, pattern, diagnostics, and raw data."""

from __future__ import annotations

import math

import pyqtgraph as pg
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ...domain.common.validation import Diagnostic, Severity
from ...domain.simulation.resonance import find_resonances
from ...domain.simulation.result import SimulationResult, SimulationStatus
from ..i18n import Translator
from ..theme import theme_colors
from .polar_pattern_view import PolarPatternView


class ResultsView(QWidget):
    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._colors = theme_colors(self.palette())
        self._result: SimulationResult | None = None

        self._tabs = QTabWidget(self)
        self._impedance_tab = QWidget(self)
        self._pattern_tab = QWidget(self)
        self._currents_tab = QWidget(self)
        self._diagnostics_tab = QWidget(self)
        self._raw_tab = QWidget(self)

        self._table = QTableWidget(0, 5, self._impedance_tab)
        self._configure_table(self._table)
        self._impedance_plot = self._make_plot()
        self._impedance_plot.addLegend()
        self._swr_plot = self._make_plot()
        self._resonance_label = QLabel(self._impedance_tab)
        self._resonance_label.setWordWrap(True)

        impedance_splitter = QSplitter(Qt.Orientation.Vertical, self._impedance_tab)
        impedance_splitter.addWidget(self._table)
        impedance_splitter.addWidget(self._impedance_plot)
        impedance_splitter.addWidget(self._swr_plot)
        impedance_splitter.setStretchFactor(0, 1)
        impedance_splitter.setStretchFactor(1, 2)
        impedance_splitter.setStretchFactor(2, 2)
        impedance_layout = QVBoxLayout(self._impedance_tab)
        impedance_layout.setContentsMargins(0, 0, 0, 0)
        impedance_layout.addWidget(self._resonance_label)
        impedance_layout.addWidget(impedance_splitter)

        self._pattern_frequency = QComboBox(self._pattern_tab)
        self._pattern_frequency_label = QLabel(self._pattern_tab)
        self._pattern_plot = self._make_plot()
        self._polar_pattern = PolarPatternView(translator, self._pattern_tab)
        pattern_controls = QHBoxLayout()
        pattern_controls.addWidget(self._pattern_frequency_label)
        pattern_controls.addWidget(self._pattern_frequency)
        pattern_controls.addStretch(1)
        pattern_layout = QVBoxLayout(self._pattern_tab)
        pattern_layout.setContentsMargins(0, 0, 0, 0)
        pattern_layout.addLayout(pattern_controls)
        pattern_splitter = QSplitter(Qt.Orientation.Vertical, self._pattern_tab)
        pattern_splitter.addWidget(self._pattern_plot)
        pattern_splitter.addWidget(self._polar_pattern)
        pattern_splitter.setStretchFactor(0, 1)
        pattern_splitter.setStretchFactor(1, 1)
        pattern_layout.addWidget(pattern_splitter)

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

        self._summary = QLabel(self._diagnostics_tab)
        self._summary.setWordWrap(True)
        self._summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._diagnostics = QTableWidget(0, 3, self._diagnostics_tab)
        self._configure_table(self._diagnostics)
        self._diagnostics_empty = QLabel(self._diagnostics_tab)
        diagnostics_layout = QVBoxLayout(self._diagnostics_tab)
        diagnostics_layout.setContentsMargins(0, 0, 0, 0)
        diagnostics_layout.addWidget(self._summary)
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
        self._tabs.addTab(self._diagnostics_tab, "")
        self._tabs.addTab(self._raw_tab, "")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tabs)

        self._pattern_frequency.currentIndexChanged.connect(self._render_pattern)
        self._currents_frequency.currentIndexChanged.connect(self._render_currents)
        self._apply_theme()
        self.retranslate()

    @staticmethod
    def _make_plot() -> pg.PlotWidget:
        plot = pg.PlotWidget()
        plot.showGrid(x=True, y=True, alpha=0.3)
        return plot

    def _apply_theme(self) -> None:
        self._colors = theme_colors(self.palette())
        for plot in (
            self._impedance_plot,
            self._swr_plot,
            self._pattern_plot,
            self._currents_plot,
        ):
            plot.setBackground(self._colors.plot_background)
            for axis_name in ("left", "bottom"):
                axis = plot.getAxis(axis_name)
                axis.setPen(self._colors.axis)
                axis.setTextPen(self._colors.axis)
            legend = plot.plotItem.legend
            if legend is not None:
                legend.setLabelTextColor(self._colors.text)
        self._polar_pattern.update()

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

    @staticmethod
    def _make_text_view() -> QPlainTextEdit:
        view = QPlainTextEdit()
        view.setReadOnly(True)
        view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        view.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        return view

    def set_result(self, result: SimulationResult | None) -> None:
        self._result = result
        for combo in (self._pattern_frequency, self._currents_frequency):
            combo.blockSignals(True)
            combo.clear()
            if result is not None:
                for frequency in result.frequencies:
                    combo.addItem(f"{frequency.frequency_hz / 1e6:g} MHz")
            combo.blockSignals(False)
            if combo.count() > 0:
                combo.setCurrentIndex(0)
        self._render()

    def retranslate(self) -> None:
        self._tabs.setTabText(0, self._translator.t("tab.impedance"))
        self._tabs.setTabText(1, self._translator.t("tab.pattern"))
        self._tabs.setTabText(2, self._translator.t("tab.currents"))
        self._tabs.setTabText(3, self._translator.t("tab.diagnostics"))
        self._tabs.setTabText(4, self._translator.t("tab.raw"))
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
        self._currents_frequency_label.setText(self._translator.t("currents.frequency"))
        self._raw_tabs.setTabText(0, self._translator.t("raw.input"))
        self._raw_tabs.setTabText(1, self._translator.t("raw.output"))
        self._render()

    def _render(self) -> None:
        self._render_impedance()
        self._render_pattern()
        self._render_currents()
        self._render_diagnostics()
        self._render_raw()

    def _render_impedance(self) -> None:
        self._table.setRowCount(0)
        self._impedance_plot.clear()
        self._swr_plot.clear()

        if self._result is None or not self._result.frequencies:
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
        self._impedance_plot.setTitle(self._translator.t("plot.impedance"), color=self._colors.text)
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
        self._swr_plot.setTitle(self._translator.t("plot.swr"), color=self._colors.text)
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
            resonances = ()
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

    def _render_currents(self) -> None:
        self._currents_plot.clear()
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

    def _render_pattern(self) -> None:
        self._pattern_plot.clear()
        if self._result is None or not self._result.frequencies:
            self._pattern_plot.setTitle(self._translator.t("results.none"), color=self._colors.text)
            self._polar_pattern.set_points(())
            return
        index = self._pattern_frequency.currentIndex()
        if index < 0 or index >= len(self._result.frequencies):
            return
        frequency = self._result.frequencies[index]
        points = [
            (point.theta_deg, point.gain_total_db)
            for point in frequency.far_field
            if point.gain_total_db is not None
        ]
        if not points:
            self._pattern_plot.setTitle(self._translator.t("pattern.none"), color=self._colors.text)
            self._polar_pattern.set_points(())
            return
        theta = [value[0] for value in points]
        gain = [value[1] for value in points]
        self._pattern_plot.setTitle(self._translator.t("plot.pattern"), color=self._colors.text)
        self._pattern_plot.setLabel(
            "bottom", self._translator.t("pattern.elevation"), color=self._colors.text
        )
        self._pattern_plot.setLabel(
            "left", self._translator.t("pattern.gain"), color=self._colors.text
        )
        self._pattern_plot.plot(
            theta,
            gain,
            pen=pg.mkPen(self._colors.pattern, width=2),
            symbol="o",
            symbolSize=4,
        )
        self._pattern_plot.setXRange(min(theta), max(theta), padding=0.02)
        self._polar_pattern.set_points(tuple(zip(theta, gain, strict=True)))

    def _render_diagnostics(self) -> None:
        self._diagnostics.setRowCount(0)
        if self._result is None:
            self._summary.setText(self._translator.t("results.none"))
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
