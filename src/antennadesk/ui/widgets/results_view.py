# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Results tabs: band summary, impedance, SWR, pattern, and diagnostics."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pyqtgraph as pg
from PySide6.QtCore import QEvent, QPoint, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontDatabase, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.feed_line import FeedLine
from ...domain.antennas.flower_pot import FlowerPotParameters
from ...domain.antennas.matching_network import (
    LNetwork,
    MatchingNetwork,
    PiNetwork,
    TNetwork,
)
from ...domain.common.validation import Diagnostic, Severity
from ...domain.design.matching_design import (
    MatchingNetworkDesign,
    matching_network_design_from_frequency,
)
from ...domain.design.smith_chart import (
    MatchingPreviewTopology,
    SmithPlane,
    SmithPoint,
    available_smith_planes,
    design_preview_network,
    smith_points_for_measurement,
    smith_points_for_result,
    transform_with_feed_line,
    transform_with_matching_network,
)
from ...domain.environment.ground import GroundKind
from ...domain.measurement import Measurement, MeasurementPoint, MeasurementSession
from ...domain.measurement_comparison import compare_measurement
from ...domain.measurement_uncertainty import (
    MeasurementDocumentationStatus,
    MeasurementUncertaintyLevel,
    assess_measurement_uncertainty,
)
from ...domain.projects.project import DesignVariant
from ...domain.simulation.band_result import BandAnalysisResult, BandResult
from ...domain.simulation.band_summary import summarize_band
from ...domain.simulation.bands import AMATEUR_BANDS, amateur_band_for
from ...domain.simulation.metrics import decision_metrics
from ...domain.simulation.pattern import (
    PatternGainMetric,
    front_to_back_db,
    max_power_gain_db,
    pattern_gain_offset_db,
)
from ...domain.simulation.resonance import ResonancePoint, find_resonances
from ...domain.simulation.result import (
    CurrentSample,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from ...reporting.design_summary import design_evidence_rows
from ...reporting.result_summary import representative_gain_frequency
from ..fonts import apply_plot_fonts, scaled_font_copy
from ..help import apply_help
from ..i18n import Translator
from ..pattern_orientation import antenna_orientation, forward_axis_azimuth
from ..pattern_overlay import OverlayMode, overlay_from_model
from ..theme import theme_colors
from ..units import DisplayUnits
from .chart_cursor import ChartCursor, CursorSeries
from .form_units import LengthField, LengthFieldSpec
from .polar_pattern_view import PolarPatternView
from .radiation_pattern_3d_view import RadiationPattern3DView
from .smith_chart_view import SmithChartView

DEFAULT_MARKER_LIMIT = 20


def marker_indices(
    count: int,
    *,
    limit: int = DEFAULT_MARKER_LIMIT,
) -> tuple[int, ...]:
    """Return bounded symbol indices spanning the full computed series.

    The line, table, cursor, and exports keep every point. Only the visible
    symbol layer is decimated; endpoints are always represented.
    """

    if count <= 0 or limit <= 0:
        return ()
    if count <= limit:
        return tuple(range(count))
    if limit == 1:
        return (count // 2,)
    return tuple(sorted({round(index * (count - 1) / (limit - 1)) for index in range(limit)}))


CONFIDENCE_TOPICS: tuple[str, ...] = (
    "impedance",
    "swr",
    "efficiency",
    "gain",
    "takeoff",
    "bandwidth",
    "ground",
    "feed_loss",
)


class ResultsView(QWidget):
    measurement_edit_requested = Signal(object)
    measurement_delete_requested = Signal(object)
    measurement_sessions_requested = Signal()
    measurement_compare_requested = Signal(object)
    measurement_tune_requested = Signal(object)
    band_selected = Signal(object)
    matching_network_requested = Signal(object)
    tab_changed = Signal(str)
    pattern_camera_changed = Signal(float, float)

    def __init__(
        self,
        translator: Translator,
        parent: QWidget | None = None,
        *,
        display_units: DisplayUnits | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._display_units = display_units or DisplayUnits()
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
        self._bands_tab.setVisible(False)

        self._table = QTableWidget(0, 5, self._impedance_tab)
        self._configure_table(self._table)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_impedance_context_menu)
        self._impedance_plot = self._make_plot()
        self._impedance_plot.addLegend()
        self._swr_plot = self._make_plot()
        self._impedance_markers: tuple[pg.ScatterPlotItem, ...] = ()
        self._swr_markers: tuple[pg.ScatterPlotItem, ...] = ()
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

        self._impedance_layout = impedance_layout

        self._smith_tab = QWidget(self)
        self._smith_plane = QComboBox(self._smith_tab)
        self._smith_plane_label = QLabel(self._smith_tab)
        self._smith_frequency = QComboBox(self._smith_tab)
        self._smith_frequency_label = QLabel(self._smith_tab)
        self._smith_measurement = QComboBox(self._smith_tab)
        self._smith_measurement.addItem(translator.t("smith.measurement.none"), None)
        self._smith_measurement_label = QLabel(self._smith_tab)
        self._smith_view = SmithChartView(translator, self._smith_tab)
        self._smith_note = QLabel(self._smith_tab)
        self._smith_note.setWordWrap(True)
        self._smith_export_png = QPushButton(self._smith_tab)
        self._smith_export_svg = QPushButton(self._smith_tab)
        self._smith_export_csv = QPushButton(self._smith_tab)
        self._smith_export_png.clicked.connect(lambda: self._export_smith_image(".png"))
        self._smith_export_svg.clicked.connect(lambda: self._export_smith_image(".svg"))
        self._smith_export_csv.clicked.connect(self._export_smith_csv)
        self._smith_plane.currentIndexChanged.connect(self._on_smith_plane_changed)
        self._smith_measurement.currentIndexChanged.connect(self._render_smith)
        self._smith_frequency.currentIndexChanged.connect(self._on_smith_frequency_changed)
        self._smith_preview_network: MatchingNetwork | None = None

        self._smith_feed_group = QGroupBox(self._smith_tab)
        self._smith_feed_group.setCheckable(True)
        self._smith_feed_group.setChecked(False)
        self._smith_feed_length = QDoubleSpinBox(self._smith_feed_group)
        self._smith_feed_length_spec = LengthFieldSpec(
            minimum_m=0.0,
            maximum_m=10_000.0,
            step_m=0.1,
        )
        self._smith_feed_length_field = LengthField(
            self._smith_feed_length,
            self._smith_feed_length_spec,
            translator,
            self._display_units,
        )
        self._smith_feed_length_field.configure(30.0)
        self._smith_feed_z0 = QDoubleSpinBox(self._smith_feed_group)
        self._smith_feed_z0.setRange(1.0, 1_000.0)
        self._smith_feed_z0.setDecimals(1)
        self._smith_feed_z0.setValue(50.0)
        self._smith_feed_z0.setSuffix(" Ω")
        self._smith_feed_vf = QDoubleSpinBox(self._smith_feed_group)
        self._smith_feed_vf.setRange(0.10, 1.0)
        self._smith_feed_vf.setDecimals(3)
        self._smith_feed_vf.setSingleStep(0.01)
        self._smith_feed_vf.setValue(0.66)
        self._smith_feed_length_label = QLabel(self._smith_feed_group)
        self._smith_feed_z0_label = QLabel(self._smith_feed_group)
        self._smith_feed_vf_label = QLabel(self._smith_feed_group)
        self._smith_feed_group.toggled.connect(self._on_smith_feed_toggled)
        self._smith_feed_length.valueChanged.connect(self._on_smith_preview_changed)
        self._smith_feed_z0.valueChanged.connect(self._on_smith_preview_changed)
        self._smith_feed_vf.valueChanged.connect(self._on_smith_preview_changed)
        feed_layout = QHBoxLayout(self._smith_feed_group)
        feed_layout.addWidget(self._smith_feed_length_label)
        feed_layout.addWidget(self._smith_feed_length)
        feed_layout.addWidget(self._smith_feed_z0_label)
        feed_layout.addWidget(self._smith_feed_z0)
        feed_layout.addWidget(self._smith_feed_vf_label)
        feed_layout.addWidget(self._smith_feed_vf)
        feed_layout.addStretch(1)

        self._smith_match_group = QGroupBox(self._smith_tab)
        self._smith_match_group.setCheckable(True)
        self._smith_match_group.setChecked(False)
        self._smith_match_topology = QComboBox(self._smith_match_group)
        for key, value in (
            ("smith.match.l", MatchingPreviewTopology.L.value),
            ("smith.match.pi", MatchingPreviewTopology.PI.value),
            ("smith.match.t", MatchingPreviewTopology.T.value),
        ):
            self._smith_match_topology.addItem(translator.t(key), value)
        self._smith_match_q = QDoubleSpinBox(self._smith_match_group)
        self._smith_match_q.setRange(0.0, 100.0)
        self._smith_match_q.setDecimals(2)
        self._smith_match_q.setSingleStep(0.5)
        self._smith_match_q.setValue(0.0)
        self._smith_match_q.setSuffix(" Q")
        self._smith_match_topology_label = QLabel(self._smith_match_group)
        self._smith_match_q_label = QLabel(self._smith_match_group)
        self._smith_match_status = QLabel(self._smith_match_group)
        self._smith_match_status.setWordWrap(True)
        self._smith_match_group.toggled.connect(self._on_smith_matching_toggled)
        self._smith_match_topology.currentIndexChanged.connect(self._on_smith_matching_changed)
        self._smith_match_q.valueChanged.connect(self._on_smith_matching_changed)
        match_layout = QHBoxLayout(self._smith_match_group)
        match_layout.addWidget(self._smith_match_topology_label)
        match_layout.addWidget(self._smith_match_topology)
        match_layout.addWidget(self._smith_match_q_label)
        match_layout.addWidget(self._smith_match_q)
        match_layout.addWidget(self._smith_match_status, 1)

        smith_controls = QHBoxLayout()
        smith_controls.addWidget(self._smith_plane_label)
        smith_controls.addWidget(self._smith_plane)
        smith_controls.addSpacing(12)
        smith_controls.addWidget(self._smith_frequency_label)
        smith_controls.addWidget(self._smith_frequency)
        smith_controls.addSpacing(12)
        smith_controls.addWidget(self._smith_measurement_label)
        smith_controls.addWidget(self._smith_measurement)
        smith_controls.addStretch(1)
        smith_exports = QHBoxLayout()
        smith_exports.addWidget(self._smith_note, 1)
        smith_exports.addWidget(self._smith_export_png)
        smith_exports.addWidget(self._smith_export_svg)
        smith_exports.addWidget(self._smith_export_csv)
        smith_layout = QVBoxLayout(self._smith_tab)
        smith_layout.setContentsMargins(0, 0, 0, 0)
        smith_layout.addLayout(smith_controls)
        smith_layout.addWidget(self._smith_feed_group)
        smith_layout.addWidget(self._smith_match_group)
        smith_layout.addWidget(self._smith_view, 1)
        smith_layout.addLayout(smith_exports)
        self._set_smith_controls_enabled(False)
        self._update_smith_matching_q_enabled()

        self._sources_tab = QWidget(self)
        self._sources_table = QTableWidget(0, 8, self._sources_tab)
        self._configure_table(self._sources_table)
        self._sources_note = QLabel(self._sources_tab)
        self._sources_note.setWordWrap(True)
        sources_layout = QVBoxLayout(self._sources_tab)
        sources_layout.setContentsMargins(0, 0, 0, 0)
        sources_layout.addWidget(self._sources_note)
        sources_layout.addWidget(self._sources_table)

        self._pattern_frequency = QComboBox(self._pattern_tab)
        self._pattern_frequency_label = QLabel(self._pattern_tab)
        self._azimuth_cut = QComboBox(self._pattern_tab)
        self._azimuth_cut_label = QLabel(self._pattern_tab)
        self._elevation_cut = QComboBox(self._pattern_tab)
        self._elevation_cut_label = QLabel(self._pattern_tab)
        self._pattern_metric = QComboBox(self._pattern_tab)
        for metric in PatternGainMetric:
            self._pattern_metric.addItem("", metric.value)
        self._pattern_metric_label = QLabel(self._pattern_tab)
        self._pattern_metric_summary = QLabel(self._pattern_tab)
        self._pattern_metric_summary.setWordWrap(True)
        self._azimuth_plot = self._make_plot()
        self._elevation_plot = self._make_plot()
        self._azimuth_polar = PolarPatternView(translator, self._pattern_tab)
        self._elevation_polar = PolarPatternView(translator, self._pattern_tab)
        self._pattern_3d = RadiationPattern3DView(translator, self._pattern_tab)
        self._pattern_3d.camera_changed.connect(self.pattern_camera_changed)
        self._pattern_3d_tab = QWidget(self._pattern_tab)
        self._pattern_3d_tab_layout = QVBoxLayout(self._pattern_3d_tab)
        self._pattern_3d_tab_layout.setContentsMargins(0, 0, 0, 0)
        overlay_controls = QHBoxLayout()
        self._pattern_overlay_show = QCheckBox(self._pattern_3d_tab)
        self._pattern_overlay_mode = QComboBox(self._pattern_3d_tab)
        for mode in OverlayMode:
            self._pattern_overlay_mode.addItem("", mode.value)
        self._pattern_overlay_mode.setEnabled(False)
        self._pattern_overlay_show.toggled.connect(self._overlay_visibility_changed)
        self._pattern_overlay_mode.currentIndexChanged.connect(self._overlay_mode_changed)
        overlay_controls.addWidget(self._pattern_overlay_show)
        overlay_controls.addWidget(self._pattern_overlay_mode)
        overlay_controls.addStretch(1)
        self._pattern_3d_tab_layout.addLayout(overlay_controls)
        self._pattern_3d_tab_layout.addWidget(self._pattern_3d)
        pattern_controls = QHBoxLayout()
        pattern_controls.addWidget(self._pattern_frequency_label)
        pattern_controls.addWidget(self._pattern_frequency)
        pattern_controls.addSpacing(12)
        pattern_controls.addWidget(self._azimuth_cut_label)
        pattern_controls.addWidget(self._azimuth_cut)
        pattern_controls.addSpacing(12)
        pattern_controls.addWidget(self._elevation_cut_label)
        pattern_controls.addWidget(self._elevation_cut)
        pattern_controls.addSpacing(12)
        pattern_controls.addWidget(self._pattern_metric_label)
        pattern_controls.addWidget(self._pattern_metric)
        pattern_controls.addStretch(1)
        pattern_layout = QVBoxLayout(self._pattern_tab)
        pattern_layout.setContentsMargins(0, 0, 0, 0)
        pattern_layout.addLayout(pattern_controls)
        pattern_layout.addWidget(self._pattern_metric_summary)
        azimuth_splitter = QSplitter(Qt.Orientation.Vertical, self._pattern_tab)
        azimuth_splitter.addWidget(self._azimuth_plot)
        azimuth_splitter.addWidget(self._azimuth_polar)
        azimuth_splitter.setStretchFactor(0, 1)
        azimuth_splitter.setStretchFactor(1, 1)
        elevation_splitter = QSplitter(Qt.Orientation.Vertical, self._pattern_tab)
        elevation_splitter.addWidget(self._elevation_plot)
        elevation_splitter.addWidget(self._elevation_polar)
        elevation_splitter.setStretchFactor(0, 1)
        elevation_splitter.setStretchFactor(1, 1)
        cuts_splitter = QSplitter(Qt.Orientation.Horizontal, self._pattern_tab)
        cuts_splitter.addWidget(azimuth_splitter)
        cuts_splitter.addWidget(elevation_splitter)
        cuts_splitter.setStretchFactor(0, 1)
        cuts_splitter.setStretchFactor(1, 1)
        self._cut_tab = QWidget(self._pattern_tab)
        cut_layout = QVBoxLayout(self._cut_tab)
        cut_layout.setContentsMargins(0, 0, 0, 0)
        cut_layout.addWidget(cuts_splitter)
        self._pattern_view_tabs = QTabWidget(self._pattern_tab)
        self._pattern_view_tabs.addTab(self._cut_tab, "")
        self._pattern_view_tabs.addTab(self._pattern_3d_tab, "")
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
        self._measurement_session_names: dict[UUID, str] = {}
        self._measurement_session_data: dict[UUID, MeasurementSession] = {}
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
        self._measurement_sessions = QPushButton(
            translator.t("measurement.sessions"), self._measurements_tab
        )
        self._measurement_compare = QPushButton(
            translator.t("measurement.compare"), self._measurements_tab
        )
        self._measurement_tune = QPushButton(
            translator.t("measurement.tune"), self._measurements_tab
        )
        self._measurement_edit.setEnabled(False)
        self._measurement_delete.setEnabled(False)
        self._measurement_compare.setEnabled(False)
        self._measurement_tune.setEnabled(False)
        self._measurement_edit.clicked.connect(self._request_measurement_edit)
        self._measurement_delete.clicked.connect(self._request_measurement_delete)
        self._measurement_sessions.clicked.connect(self.measurement_sessions_requested.emit)
        self._measurement_compare.clicked.connect(self._request_measurement_compare)
        self._measurement_tune.clicked.connect(self._request_measurement_tune)
        self._measurement_table = QTableWidget(0, 8, self._measurements_tab)
        self._configure_table(self._measurement_table)
        self._measurement_plot = self._make_plot()
        self._measurement_plot.addLegend()
        self._measurement_details = QLabel(self._measurements_tab)
        self._measurement_details.setWordWrap(True)
        self._measurement_details.setTextFormat(Qt.TextFormat.PlainText)
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
        measurement_controls.addSpacing(12)
        measurement_controls.addWidget(self._measurement_sessions)
        measurement_controls.addWidget(self._measurement_compare)
        measurement_controls.addWidget(self._measurement_tune)
        measurement_controls.addStretch(1)
        self._uncertainty_group = QGroupBox(self._measurements_tab)
        self._uncertainty_level = QLabel(self._uncertainty_group)
        self._uncertainty_level.setTextFormat(Qt.TextFormat.PlainText)
        self._uncertainty_group.setVisible(False)
        self._uncertainty_factors = QLabel(self._uncertainty_group)
        self._uncertainty_factors.setWordWrap(True)
        self._uncertainty_factors.setTextFormat(Qt.TextFormat.PlainText)
        self._uncertainty_factors.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._uncertainty_warnings = QLabel(self._uncertainty_group)
        self._uncertainty_warnings.setWordWrap(True)
        self._uncertainty_warnings.setTextFormat(Qt.TextFormat.PlainText)
        self._uncertainty_warnings.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._uncertainty_warnings.setStyleSheet(f"color: {self._colors.reactance.name()};")
        self._uncertainty_disclaimer = QLabel(self._uncertainty_group)
        self._uncertainty_disclaimer.setWordWrap(True)
        self._uncertainty_disclaimer.setTextFormat(Qt.TextFormat.PlainText)
        self._uncertainty_disclaimer.setStyleSheet("font-style: italic;")
        uncertainty_layout = QVBoxLayout(self._uncertainty_group)
        uncertainty_layout.addWidget(self._uncertainty_level)
        uncertainty_layout.addWidget(self._uncertainty_factors)
        uncertainty_layout.addWidget(self._uncertainty_warnings)
        uncertainty_layout.addWidget(self._uncertainty_disclaimer)
        apply_help(self._uncertainty_group, self._translator, "measurement.uncertainty.title")
        apply_help(
            self._uncertainty_level,
            self._translator,
            "measurement.uncertainty.level",
        )
        apply_help(
            self._uncertainty_factors,
            self._translator,
            "measurement.uncertainty.factors",
        )
        apply_help(
            self._uncertainty_warnings,
            self._translator,
            "measurement.uncertainty.warnings",
        )
        measurement_layout = QVBoxLayout(self._measurements_tab)
        measurement_layout.setContentsMargins(0, 0, 0, 0)
        measurement_layout.addLayout(measurement_controls)
        measurement_layout.addWidget(self._uncertainty_group)
        measurement_layout.addWidget(self._measurement_details)
        measurement_layout.addWidget(self._measurement_comparison)
        measurement_layout.addWidget(self._measurement_resonance)
        measurement_layout.addWidget(self._measurement_table, 1)
        measurement_layout.addWidget(self._measurement_plot, 2)

        self._decision_group = QGroupBox(self._diagnostics_tab)
        self._decision_table = QTableWidget(0, 2, self._decision_group)
        self._configure_table(self._decision_table)
        self._decision_table.horizontalHeader().setVisible(False)
        decision_layout = QVBoxLayout(self._decision_group)
        decision_layout.addWidget(self._decision_table)
        self._decision_group.setLayout(decision_layout)
        apply_help(self._decision_group, self._translator, "results.decision_metrics")
        apply_help(self._decision_table, self._translator, "results.decision_metrics")

        self._confidence_group = QGroupBox(self._diagnostics_tab)
        self._confidence_evidence = QLabel(self._confidence_group)
        self._confidence_evidence.setWordWrap(True)
        self._confidence_evidence.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._confidence_topic_label = QLabel(self._confidence_group)
        self._confidence_topic = QComboBox(self._confidence_group)
        for topic in CONFIDENCE_TOPICS:
            self._confidence_topic.addItem("", topic)
        self._confidence_topic.currentIndexChanged.connect(self._render_confidence_explanation)
        self._confidence_explanation = QLabel(self._confidence_group)
        self._confidence_explanation.setWordWrap(True)
        self._confidence_explanation.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._confidence_disclaimer = QLabel(self._confidence_group)
        self._confidence_disclaimer.setWordWrap(True)
        self._confidence_disclaimer.setStyleSheet("font-style: italic;")
        confidence_layout = QVBoxLayout(self._confidence_group)
        confidence_layout.addWidget(self._confidence_evidence)
        confidence_layout.addWidget(self._confidence_topic_label)
        confidence_layout.addWidget(self._confidence_topic)
        confidence_layout.addWidget(self._confidence_explanation)
        confidence_layout.addWidget(self._confidence_disclaimer)
        apply_help(self._confidence_group, self._translator, "confidence.title")
        apply_help(self._confidence_topic, self._translator, "confidence.topic")
        apply_help(
            self._confidence_explanation,
            self._translator,
            "confidence.topic",
        )

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
        diagnostics_layout.addWidget(self._decision_group)
        diagnostics_layout.addWidget(self._confidence_group)
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
        self._tabs.addTab(self._smith_tab, "")
        self._tabs.addTab(self._sources_tab, "")
        self._tabs.addTab(self._pattern_tab, "")
        self._tabs.addTab(self._currents_tab, "")
        self._tabs.addTab(self._measurements_tab, "")
        self._tabs.addTab(self._diagnostics_tab, "")
        self._tabs.addTab(self._raw_tab, "")
        self._tabs.setTabVisible(self._tabs.indexOf(self._sources_tab), False)
        self._tabs.currentChanged.connect(self._on_tab_changed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._band_bar)
        layout.addWidget(self._tabs)

        self._impedance_cursor = ChartCursor(self._impedance_plot)
        self._swr_cursor = ChartCursor(self._swr_plot)
        self._azimuth_cursor = ChartCursor(self._azimuth_plot)
        self._elevation_cursor = ChartCursor(self._elevation_plot)
        self._currents_cursor = ChartCursor(self._currents_plot)
        self._measurement_cursor = ChartCursor(self._measurement_plot)

        self._pattern_frequency.currentIndexChanged.connect(self._on_pattern_frequency_changed)
        self._azimuth_cut.currentIndexChanged.connect(self._render_patterns)
        self._elevation_cut.currentIndexChanged.connect(self._render_patterns)
        self._pattern_metric.currentIndexChanged.connect(self._render_patterns)
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
            self._azimuth_plot,
            self._elevation_plot,
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
        for table in (
            self._table,
            self._sources_table,
            self._bands_table,
            self._measurement_table,
            self._diagnostics,
        ):
            table.resizeColumnsToContents()

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
            self._azimuth_cursor,
            self._elevation_cursor,
            self._currents_cursor,
            self._measurement_cursor,
        ):
            cursor.set_colors(
                text=self._colors.text,
                background=self._colors.background,
                line=self._colors.dimension,
            )
        self._azimuth_polar.update()
        self._elevation_polar.update()
        self._pattern_3d.update()
        self._smith_view.update()

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
        widget = self._pattern_3d if self._pattern_view_tabs.currentIndex() == 1 else self._cut_tab
        if widget is self._cut_tab:
            if widget.width() < 100 or widget.height() < 100:
                widget.resize(1_200, 800)
            layout = widget.layout()
            if layout is not None:
                layout.activate()
            pixmap = QPixmap(widget.size())
            pixmap.fill(self._colors.background)
            widget.render(pixmap)
        else:
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
        overlay = overlay_from_model(
            design.antenna if design is not None else None,
            forward_azimuth=(
                forward_axis_azimuth(design.parameters) if design is not None else None
            ),
        )
        if (
            overlay is not None
            and design is not None
            and isinstance(design.parameters, FlowerPotParameters)
        ):
            # The pattern overlay is a physical-construction aid: anchor it at
            # the feed connector, not at the NEC equivalent source at the arm
            # junction. The geometry scene still marks both points separately.
            anchor = (
                0.0,
                0.0,
                design.parameters.physical_feed_height_m,
            )
            overlay = replace(overlay, feed=anchor, center=anchor)
        self._pattern_3d.set_overlay(overlay)
        self._render_patterns()
        self._render_confidence()

    def pattern_camera(self) -> tuple[float, float]:
        """Return the 3D lobe camera yaw and pitch in degrees."""

        return self._pattern_3d.camera_angles()

    def set_pattern_camera(self, yaw_deg: float, pitch_deg: float) -> None:
        """Apply a linked camera without emitting a feedback signal."""

        self._pattern_3d.set_camera(yaw_deg, pitch_deg)

    def _overlay_visibility_changed(self, visible: bool) -> None:
        self._pattern_3d.set_overlay_visible(visible)
        self._pattern_overlay_mode.setEnabled(visible)
        self._pattern_3d.update()

    def _overlay_mode_changed(self, *_args: object) -> None:
        value = self._pattern_overlay_mode.currentData()
        try:
            mode = OverlayMode(str(value))
        except ValueError:
            mode = OverlayMode.AUTO
        self._pattern_3d.set_overlay_mode(mode)

    def _render_confidence(self) -> None:
        t = self._translator.t
        if self._design is None:
            self._confidence_evidence.setText(t("confidence.no_design"))
            self._confidence_topic.setEnabled(False)
        else:
            rows = design_evidence_rows(
                self._design,
                labeler=self._translator.report,
            )
            lines = [
                f"{self._translator.report(label)}: {self._translator.report(value)}"
                for label, value in rows
            ]
            lines.append(t("confidence.modeled"))
            lines.append(t("confidence.uncertainties"))
            self._confidence_evidence.setText("\n".join(lines))
            self._confidence_topic.setEnabled(True)
        self._confidence_disclaimer.setText(t("confidence.disclaimer"))
        self._render_confidence_explanation()

    def _render_confidence_explanation(self, *_args: object) -> None:
        if self._design is None:
            self._confidence_explanation.clear()
            return
        topic = self._confidence_topic.currentData()
        if isinstance(topic, str):
            self._confidence_explanation.setText(self._translator.t(f"confidence.explain.{topic}"))

    def _on_tab_changed(self, _index: int) -> None:
        self.tab_changed.emit(self.current_view())

    def current_view(self) -> str:
        """Return a stable name for the visible result tab."""

        current = self._tabs.currentWidget()
        if current is self._impedance_tab:
            return "impedance"
        if current is self._smith_tab:
            return "smith"
        if current is self._measurements_tab:
            return "measurements"
        if current is self._diagnostics_tab:
            return "diagnostics"
        return "other"

    def show_impedance(self) -> None:
        self._tabs.setCurrentWidget(self._impedance_tab)

    def show_smith(self) -> None:
        self._tabs.setCurrentWidget(self._smith_tab)

    def show_diagnostics(self) -> None:
        self._tabs.setCurrentWidget(self._diagnostics_tab)

    def show_measurements(self) -> None:
        self._tabs.setCurrentWidget(self._measurements_tab)

    def show_bands(self) -> None:
        if self._bands_tab_index >= 0:
            self._tabs.setCurrentWidget(self._bands_tab)

    def set_measurements(
        self,
        measurements: tuple[Measurement, ...],
        session_names: dict[UUID, str] | None = None,
        sessions: tuple[MeasurementSession, ...] = (),
    ) -> None:
        self._measurements = measurements
        self._measurement_session_names = session_names or {}
        self._measurement_session_data = {session.id: session for session in sessions}
        self._measurement_selector.blockSignals(True)
        self._measurement_selector.clear()
        for measurement in measurements:
            session = (
                self._measurement_session_names.get(measurement.session_id)
                if measurement.session_id is not None
                else None
            )
            label = f"{measurement.name} · {session}" if session else measurement.name
            self._measurement_selector.addItem(label)
        self._measurement_selector.blockSignals(False)
        if self._measurement_selector.count():
            self._measurement_selector.setCurrentIndex(0)
        self._measurement_compare.setEnabled(len(measurements) >= 2)
        self._render_measurements()
        self._smith_measurement.blockSignals(True)
        self._smith_measurement.clear()
        self._smith_measurement.addItem(
            self._translator.t("smith.measurement.none"),
            None,
        )
        for measurement in measurements:
            self._smith_measurement.addItem(measurement.name, measurement)
        self._smith_measurement.blockSignals(False)
        self._render_smith()

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
        self._smith_frequency.blockSignals(True)
        self._pattern_frequency.clear()
        self._currents_frequency.clear()
        self._smith_frequency.clear()
        self._pattern_frequencies = ()
        self._pattern_band_results = ()
        if result is not None:
            for frequency in result.frequencies:
                self._currents_frequency.addItem(f"{frequency.frequency_hz / 1e6:g} MHz")
                self._smith_frequency.addItem(
                    f"{frequency.frequency_hz / 1e6:g} MHz",
                    frequency.frequency_hz,
                )
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
        self._smith_frequency.blockSignals(False)
        if self._smith_frequency.count() > 0:
            target_frequency = (
                self._design.parameters.frequency_hz
                if self._design is not None
                else float(self._smith_frequency.itemData(0))
            )
            self._smith_frequency.setCurrentIndex(
                min(
                    range(self._smith_frequency.count()),
                    key=lambda index: abs(
                        float(self._smith_frequency.itemData(index)) - target_frequency
                    ),
                )
            )
        if self._currents_frequency.count() > 0:
            self._currents_frequency.setCurrentIndex(0)
        self._populate_cut_values()
        self._render()
        if self._smith_match_group.isChecked():
            self._on_smith_preview_changed()

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
                self._bands_tab.setVisible(False)
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
        self._tabs.setTabToolTip(
            self._bands_tab_index,
            self._translator.t("help.tab.bands"),
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
        for widget, key, help_key in (
            (self._impedance_tab, "tab.impedance", "help.tab.impedance"),
            (self._smith_tab, "tab.smith", "help.tab.smith"),
            (self._sources_tab, "tab.sources", "help.tab.sources"),
            (self._pattern_tab, "tab.pattern", "help.tab.pattern"),
            (self._currents_tab, "tab.currents", "help.tab.currents"),
            (self._measurements_tab, "tab.measurements", "help.tab.measurements"),
            (self._diagnostics_tab, "tab.diagnostics", "help.tab.diagnostics"),
            (self._raw_tab, "tab.raw", "help.tab.raw"),
        ):
            index = self._tabs.indexOf(widget)
            self._tabs.setTabText(index, self._translator.t(key))
            self._tabs.setTabToolTip(index, self._translator.t(help_key))
        if self._bands_tab_index >= 0:
            self._tabs.setTabText(
                self._bands_tab_index,
                self._translator.t("tab.bands"),
            )
            self._tabs.setTabToolTip(
                self._bands_tab_index,
                self._translator.t("help.tab.bands"),
            )
        self._confidence_group.setTitle(self._translator.t("confidence.title"))
        self._confidence_topic_label.setText(self._translator.t("confidence.topic_label"))
        for index, topic in enumerate(CONFIDENCE_TOPICS):
            self._confidence_topic.setItemText(
                index,
                self._translator.t(f"confidence.topic.{topic}"),
            )
        self._decision_group.setTitle(self._translator.t("results.decision_metrics"))
        apply_help(self._decision_group, self._translator, "results.decision_metrics")
        apply_help(self._decision_table, self._translator, "results.decision_metrics")
        apply_help(self._confidence_group, self._translator, "confidence.title")
        apply_help(self._confidence_topic, self._translator, "confidence.topic")
        apply_help(
            self._confidence_explanation,
            self._translator,
            "confidence.topic",
        )
        self._render_confidence()
        self._render_decision_metrics()
        self._smith_plane_label.setText(self._translator.t("smith.plane"))
        self._smith_frequency_label.setText(self._translator.t("smith.frequency"))
        self._smith_measurement_label.setText(self._translator.t("smith.measurement"))
        self._smith_export_png.setText(self._translator.t("smith.export_png"))
        self._smith_export_svg.setText(self._translator.t("smith.export_svg"))
        self._smith_export_csv.setText(self._translator.t("smith.export_csv"))
        plane_labels = {
            SmithPlane.SIMULATED.value: "smith.plane.simulated",
            SmithPlane.ANTENNA.value: "smith.plane.antenna",
            SmithPlane.FEED_LINE.value: "smith.plane.feed_line",
        }
        for index in range(self._smith_plane.count()):
            data = self._smith_plane.itemData(index)
            if isinstance(data, str) and data in plane_labels:
                self._smith_plane.setItemText(
                    index,
                    self._translator.t(plane_labels[data]),
                )
        if self._smith_measurement.count() > 0:
            self._smith_measurement.setItemText(
                0,
                self._translator.t("smith.measurement.none"),
            )
        self._smith_feed_group.setTitle(self._translator.t("smith.feed_group"))
        self._smith_feed_length_label.setText(self._translator.t("smith.feed_length"))
        self._smith_feed_z0_label.setText(self._translator.t("smith.feed_z0"))
        self._smith_feed_vf_label.setText(self._translator.t("smith.feed_vf"))
        self._smith_match_group.setTitle(self._translator.t("smith.match_group"))
        self._smith_match_topology_label.setText(self._translator.t("smith.match_topology"))
        self._smith_match_q_label.setText(self._translator.t("smith.match_q"))
        for topology, key in (
            (MatchingPreviewTopology.L.value, "smith.match.l"),
            (MatchingPreviewTopology.PI.value, "smith.match.pi"),
            (MatchingPreviewTopology.T.value, "smith.match.t"),
        ):
            index = self._smith_match_topology.findData(topology)
            if index >= 0:
                self._smith_match_topology.setItemText(
                    index,
                    self._translator.t(key),
                )
        self._smith_view.retranslate()
        self._on_smith_preview_changed()
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
        self._pattern_overlay_show.setText(self._translator.t("pattern.overlay_show"))
        self._pattern_overlay_mode.setItemText(
            0,
            self._translator.t("pattern.overlay_mode.auto"),
        )
        self._pattern_overlay_mode.setItemText(
            1,
            self._translator.t("pattern.overlay_mode.full"),
        )
        self._pattern_overlay_mode.setItemText(
            2,
            self._translator.t("pattern.overlay_mode.outline"),
        )
        self._pattern_view_tabs.setTabText(0, self._translator.t("pattern.cut_tab"))
        self._pattern_view_tabs.setTabText(1, self._translator.t("pattern.3d_tab"))
        self._pattern_view_tabs.setTabToolTip(0, self._translator.t("help.tab.pattern"))
        self._pattern_view_tabs.setTabToolTip(1, self._translator.t("help.tab.pattern"))
        self._raw_tabs.setTabToolTip(0, self._translator.t("help.tab.raw"))
        self._raw_tabs.setTabToolTip(1, self._translator.t("help.tab.raw"))
        self._apply_accessibility()
        self._table.setHorizontalHeaderLabels(
            [
                self._translator.t("table.frequency"),
                self._translator.t("table.resistance"),
                self._translator.t("table.reactance"),
                self._translator.t("table.impedance"),
                self._translator.t("table.swr"),
            ]
        )
        self._sources_table.setHorizontalHeaderLabels(
            [
                self._translator.t("table.frequency"),
                self._translator.t("table.source"),
                self._translator.t("table.wire"),
                self._translator.t("table.amplitude"),
                self._translator.t("table.phase"),
                self._translator.t("table.resistance"),
                self._translator.t("table.reactance"),
                self._translator.t("table.power"),
            ]
        )
        self._sources_note.setText(self._translator.t("sources.note"))
        self._diagnostics.setHorizontalHeaderLabels(
            [
                self._translator.t("diagnostic.severity"),
                self._translator.t("diagnostic.code"),
                self._translator.t("diagnostic.message"),
            ]
        )
        self._pattern_frequency_label.setText(self._translator.t("pattern.frequency"))
        self._azimuth_cut_label.setText(self._translator.t("pattern.azimuth_cut"))
        self._elevation_cut_label.setText(self._translator.t("pattern.elevation_cut"))
        self._pattern_metric_label.setText(self._translator.t("pattern.metric"))
        for index, metric in enumerate(PatternGainMetric):
            self._pattern_metric.setItemText(
                index,
                self._translator.t(f"pattern.metric.{metric.value}"),
            )
        self._currents_frequency_label.setText(self._translator.t("currents.frequency"))
        self._measurement_selector_label.setText(self._translator.t("measurement.select"))
        self._measurement_metric_label.setText(self._translator.t("measurement.metric"))
        self._measurement_edit.setText(self._translator.t("measurement.edit"))
        self._measurement_delete.setText(self._translator.t("measurement.delete"))
        self._measurement_sessions.setText(self._translator.t("measurement.sessions"))
        self._measurement_compare.setText(self._translator.t("measurement.compare"))
        self._measurement_tune.setText(self._translator.t("measurement.tune"))
        self._uncertainty_group.setTitle(self._translator.t("measurement.uncertainty.title"))
        self._uncertainty_disclaimer.setText(
            self._translator.t("measurement.uncertainty.disclaimer")
        )
        apply_help(
            self._uncertainty_group,
            self._translator,
            "measurement.uncertainty.title",
        )
        apply_help(
            self._uncertainty_level,
            self._translator,
            "measurement.uncertainty.level",
        )
        apply_help(
            self._uncertainty_factors,
            self._translator,
            "measurement.uncertainty.factors",
        )
        apply_help(
            self._uncertainty_warnings,
            self._translator,
            "measurement.uncertainty.warnings",
        )
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
        for table in (
            self._table,
            self._sources_table,
            self._bands_table,
            self._measurement_table,
            self._diagnostics,
        ):
            table.resizeColumnsToContents()
        self._render()

    def _render(self) -> None:
        self._render_impedance()
        self._render_smith()
        self._render_patterns()
        self._render_currents()
        self._render_measurements()
        self._render_diagnostics()
        self._render_raw()

    def _apply_accessibility(self) -> None:
        for table, key in (
            (self._table, "table.impedance"),
            (self._sources_table, "table.sources"),
            (self._bands_table, "table.bands"),
            (self._measurement_table, "table.measurement"),
            (self._diagnostics, "table.diagnostics"),
        ):
            apply_help(table, self._translator, key)
            text = self._translator.t(f"help.{key}")
            table.horizontalHeader().setToolTip(text)
            table.horizontalHeader().setAccessibleDescription(text)
        for plot, key in (
            (self._impedance_plot, "chart.impedance"),
            (self._swr_plot, "chart.swr"),
            (self._smith_view, "chart.smith"),
            (self._azimuth_plot, "chart.pattern"),
            (self._elevation_plot, "chart.pattern"),
            (self._currents_plot, "chart.currents"),
            (self._measurement_plot, "chart.measurement"),
        ):
            apply_help(plot, self._translator, key)
        apply_help(self._measurement_sessions, self._translator, "measurement.sessions")
        apply_help(self._measurement_compare, self._translator, "measurement.compare")
        apply_help(self._measurement_tune, self._translator, "measurement.tune")
        for button, key in (
            (self._smith_export_png, "smith.export_png"),
            (self._smith_export_svg, "smith.export_svg"),
            (self._smith_export_csv, "smith.export_csv"),
        ):
            apply_help(button, self._translator, key)
        for widget, key in (
            (self._smith_feed_group, "smith.feed_group"),
            (self._smith_feed_length, "smith.feed_length"),
            (self._smith_feed_z0, "smith.feed_z0"),
            (self._smith_feed_vf, "smith.feed_vf"),
            (self._smith_match_group, "smith.match_group"),
            (self._smith_match_topology, "smith.match_topology"),
            (self._smith_match_q, "smith.match_q"),
        ):
            apply_help(widget, self._translator, key)
        for control, key in (
            (self._band_selector, "band.selector"),
            (self._pattern_frequency, "pattern.frequency"),
            (self._azimuth_cut, "pattern.azimuth_cut"),
            (self._elevation_cut, "pattern.elevation_cut"),
            (self._pattern_metric, "pattern.metric"),
            (self._currents_frequency, "currents.frequency"),
            (self._smith_plane, "smith.plane"),
            (self._smith_frequency, "smith.frequency"),
            (self._smith_measurement, "smith.measurement"),
        ):
            apply_help(control, self._translator, key)
        apply_help(self._pattern_metric_summary, self._translator, "pattern.metric_summary")
        apply_help(self._pattern_overlay_show, self._translator, "pattern.overlay_show")
        apply_help(self._pattern_overlay_mode, self._translator, "pattern.overlay_mode")
        self._pattern_view_tabs.setAccessibleDescription(self._translator.t("help.tab.pattern"))
        self._raw_tabs.setAccessibleDescription(self._translator.t("help.tab.raw"))

    def _matching_point_for_row(self, row: int) -> MatchingNetworkDesign | None:
        result = self._result
        if result is None or not 0 <= row < len(result.frequencies):
            return None
        return matching_network_design_from_frequency(
            result.frequencies[row],
            result.spec,
        )

    def _create_impedance_context_menu(self, row: int) -> QMenu:
        point = self._matching_point_for_row(row)
        menu = QMenu(self)
        action = menu.addAction(self._translator.t("results.create_matching_network"))
        action.setEnabled(point is not None)
        action.setToolTip(self._translator.t("help.results.create_matching_network"))
        if point is not None:
            action.triggered.connect(
                lambda _checked=False, point=point: self.matching_network_requested.emit(point)
            )
        else:
            unavailable = menu.addAction(self._translator.t("results.matching_point_unavailable"))
            unavailable.setEnabled(False)
        return menu

    def _show_impedance_context_menu(self, position: QPoint) -> None:
        index = self._table.indexAt(position)
        if not index.isValid():
            return
        menu = self._create_impedance_context_menu(index.row())
        menu.exec(self._table.viewport().mapToGlobal(position))

    def _add_marker_layer(
        self,
        plot: pg.PlotWidget,
        x: Sequence[float],
        y: Sequence[float],
        color: QColor,
    ) -> pg.ScatterPlotItem | None:
        indices = marker_indices(len(x))
        if not indices:
            return None
        marker = pg.ScatterPlotItem(
            x=[x[index] for index in indices],
            y=[y[index] for index in indices],
            size=5,
            pen=pg.mkPen(color, width=1),
            brush=pg.mkBrush(color),
        )
        plot.addItem(marker, ignoreBounds=True)
        return marker

    def _add_band_edges(self, x_values: Sequence[float]) -> None:
        if len(x_values) < 2:
            return
        lower, upper = min(x_values), max(x_values)
        seen: set[float] = set()
        for band in AMATEUR_BANDS:
            if band.stop_hz / 1e6 < lower or band.start_hz / 1e6 > upper:
                continue
            for edge_hz in (band.start_hz, band.stop_hz):
                edge = edge_hz / 1e6
                if lower <= edge <= upper and edge not in seen:
                    seen.add(edge)
                    line = pg.InfiniteLine(
                        pos=edge,
                        angle=90,
                        pen=pg.mkPen(
                            self._colors.grid,
                            style=Qt.PenStyle.DotLine,
                        ),
                    )
                    line.setToolTip(self._translator.t("results.band_edge", band=band.name))
                    self._swr_plot.addItem(line)

    def _render_smith(self) -> None:
        result = self._result
        previous_plane = self._smith_plane.currentData()
        self._smith_plane.blockSignals(True)
        self._smith_plane.clear()
        if result is None or not result.frequencies:
            self._smith_plane.blockSignals(False)
            self._smith_view.clear()
            self._smith_note.clear()
            self._set_smith_controls_enabled(False)
            return
        planes = available_smith_planes(result)
        labels = {
            SmithPlane.SIMULATED: "smith.plane.simulated",
            SmithPlane.ANTENNA: "smith.plane.antenna",
            SmithPlane.FEED_LINE: "smith.plane.feed_line",
        }
        for plane in planes:
            self._smith_plane.addItem(self._translator.t(labels[plane]), plane.value)
        available = {plane.value for plane in planes}
        selected = previous_plane if previous_plane in available else planes[0].value
        index = self._smith_plane.findData(selected)
        self._smith_plane.setCurrentIndex(max(index, 0))
        self._smith_plane.blockSignals(False)
        plane = SmithPlane(self._smith_plane.currentData() or SmithPlane.SIMULATED.value)
        points = smith_points_for_result(result, plane)
        measurement = self._smith_selected_measurement()
        measured = (
            smith_points_for_measurement(measurement, result.spec.reference_impedance_ohm)
            if measurement is not None
            else ()
        )
        measured_note = ""
        if measurement is not None and (
            measurement.reference_impedance_ohm != result.spec.reference_impedance_ohm
        ):
            measured_note = self._translator.t(
                "smith.measured_note",
                z0=f"{result.spec.reference_impedance_ohm:g}",
                measured_z0=f"{measurement.reference_impedance_ohm:g}",
            )
        preview_points: tuple[SmithPoint, ...] = ()
        preview_label = ""
        if self._smith_feed_group.isChecked():
            source_points = points
            if plane is not SmithPlane.ANTENNA and SmithPlane.ANTENNA.value in available:
                source_points = smith_points_for_result(result, SmithPlane.ANTENNA)
            preview_line = FeedLine(
                characteristic_impedance_ohm=self._smith_feed_z0.value(),
                length_m=self._smith_feed_length_field.value_m(),
                velocity_factor=self._smith_feed_vf.value(),
            )
            preview_points = transform_with_feed_line(source_points, preview_line)
            preview_label = self._translator.t("smith.preview.feed_line")
        elif self._smith_match_group.isChecked() and self._smith_preview_network is not None:
            preview_points = transform_with_matching_network(
                points,
                self._smith_preview_network,
            )
            preview_label = self._translator.t("smith.preview.matching")
        self._smith_view.set_data(
            points,
            measured=measured,
            preview=preview_points,
            reference_impedance_ohm=result.spec.reference_impedance_ohm,
            plane_label=self._smith_plane.currentText(),
            preview_label=preview_label,
            measured_note=measured_note,
        )
        selected_frequency = self._smith_frequency.currentData()
        self._smith_view.set_selected_frequency(
            float(selected_frequency) if isinstance(selected_frequency, (int, float)) else None
        )
        note = self._translator.t(f"smith.note.{plane.value}")
        if self._smith_feed_group.isChecked():
            note = f"{note} {self._translator.t('smith.feed_note')}"
        self._smith_note.setText(note)
        self._set_smith_controls_enabled(True)
        has_points = bool(points)
        self._smith_export_png.setEnabled(has_points)
        self._smith_export_svg.setEnabled(has_points)
        self._smith_export_csv.setEnabled(has_points)

    def _set_smith_controls_enabled(self, enabled: bool) -> None:
        for widget in (
            self._smith_plane,
            self._smith_frequency,
            self._smith_measurement,
            self._smith_feed_group,
            self._smith_match_group,
            self._smith_export_png,
            self._smith_export_svg,
            self._smith_export_csv,
        ):
            widget.setEnabled(enabled)

    def _smith_selected_measurement(self) -> Measurement | None:
        measurement = self._smith_measurement.currentData()
        return measurement if isinstance(measurement, Measurement) else None

    def _on_smith_plane_changed(self, _index: int) -> None:
        self._on_smith_preview_changed()

    def _on_smith_frequency_changed(self, _index: int) -> None:
        self._on_smith_preview_changed()

    def _on_smith_feed_toggled(self, checked: bool) -> None:
        if checked and self._smith_match_group.isChecked():
            self._smith_match_group.setChecked(False)
        self._on_smith_preview_changed()

    def _on_smith_matching_toggled(self, checked: bool) -> None:
        if checked and self._smith_feed_group.isChecked():
            self._smith_feed_group.setChecked(False)
        self._update_smith_matching_q_enabled()
        self._on_smith_preview_changed()

    def _on_smith_matching_changed(self, *_args: object) -> None:
        self._update_smith_matching_q_enabled()
        self._on_smith_preview_changed()

    def _on_smith_preview_changed(self, *_args: object) -> None:
        self._design_smith_matching_preview()
        self._render_smith()

    def _update_smith_matching_q_enabled(self) -> None:
        topology = self._smith_match_topology.currentData()
        self._smith_match_q.setEnabled(
            self._smith_match_group.isChecked() and topology != MatchingPreviewTopology.L.value
        )

    def _design_smith_matching_preview(self) -> None:
        self._smith_preview_network = None
        self._smith_match_status.clear()
        if not self._smith_match_group.isChecked():
            return
        result = self._result
        points = self._smith_base_points()
        selected = self._selected_smith_point(points)
        if result is None or selected is None:
            self._smith_match_status.setText(self._translator.t("smith.match.no_data"))
            return
        topology = MatchingPreviewTopology(
            self._smith_match_topology.currentData() or MatchingPreviewTopology.L.value
        )
        loaded_q = self._smith_match_q.value()
        network = design_preview_network(
            selected.impedance_ohm,
            selected.frequency_hz,
            topology,
            source_impedance_ohm=result.spec.reference_impedance_ohm,
            loaded_q=loaded_q if loaded_q > 0.0 else None,
        )
        if (
            network is not None
            and loaded_q > 0.0
            and isinstance(network, (LNetwork, PiNetwork, TNetwork))
        ):
            network = replace(network, q_factor=loaded_q)
        self._smith_preview_network = network
        if network is None:
            self._smith_match_status.setText(self._translator.t("smith.match.no_solution"))
            return
        summary = self._matching_summary(network)
        if loaded_q > 0.0:
            summary = (
                f"{summary} · {self._translator.t('smith.match.q_summary', q=f'{loaded_q:g}')}"
            )
        self._smith_match_status.setText(summary)

    def _smith_base_points(self) -> tuple[SmithPoint, ...]:
        result = self._result
        if result is None or not result.frequencies:
            return ()
        plane = SmithPlane(self._smith_plane.currentData() or SmithPlane.SIMULATED.value)
        return smith_points_for_result(result, plane)

    def _selected_smith_point(
        self,
        points: Sequence[SmithPoint],
    ) -> SmithPoint | None:
        if not points:
            return None
        frequency = self._smith_frequency.currentData()
        if isinstance(frequency, (int, float)):
            return min(
                points,
                key=lambda point: abs(point.frequency_hz - float(frequency)),
            )
        return points[0]

    def _matching_summary(self, network: MatchingNetwork) -> str:
        if isinstance(network, LNetwork):
            side = self._translator.t(
                "smith.match.input" if network.shunt_at_input else "smith.match.output"
            )
            return self._translator.t(
                "smith.match.summary_l",
                series=self._component_label(
                    network.series_inductance_h,
                    network.series_capacitance_f,
                ),
                shunt=self._component_label(
                    network.shunt_inductance_h,
                    network.shunt_capacitance_f,
                ),
                side=side,
            )
        if isinstance(network, PiNetwork):
            return self._translator.t(
                "smith.match.summary_pi",
                input=self._component_label(
                    network.input_shunt_inductance_h,
                    network.input_shunt_capacitance_f,
                ),
                series=self._component_label(
                    network.series_inductance_h,
                    network.series_capacitance_f,
                ),
                output=self._component_label(
                    network.output_shunt_inductance_h,
                    network.output_shunt_capacitance_f,
                ),
            )
        if isinstance(network, TNetwork):
            return self._translator.t(
                "smith.match.summary_t",
                input=self._component_label(
                    network.input_series_inductance_h,
                    network.input_series_capacitance_f,
                ),
                shunt=self._component_label(
                    network.shunt_inductance_h,
                    network.shunt_capacitance_f,
                ),
                output=self._component_label(
                    network.output_series_inductance_h,
                    network.output_series_capacitance_f,
                ),
            )
        return ""

    def _component_label(self, inductance_h: float, capacitance_f: float) -> str:
        if inductance_h > 0.0:
            return f"{inductance_h * 1e6:.3g} {self._translator.t('smith.unit_uh')}"
        if capacitance_f > 0.0:
            return f"{capacitance_f * 1e12:.3g} {self._translator.t('smith.unit_pf')}"
        return self._translator.t("smith.match.none_component")

    def set_display_units(self, display_units: DisplayUnits) -> None:
        value_m = self._smith_feed_length_field.value_m()
        self._display_units = display_units
        self._smith_feed_length_field = LengthField(
            self._smith_feed_length,
            self._smith_feed_length_spec,
            self._translator,
            display_units,
        )
        self._smith_feed_length_field.configure(value_m)
        if self._result is not None:
            self._on_smith_preview_changed()

    def _export_smith_image(self, suffix: str) -> None:
        if not self._smith_view.simulated_points():
            return
        path_text, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("smith.export_title"),
            str(Path.home() / f"smith{suffix}"),
            self._translator.t(
                "smith.export_filter_svg" if suffix == ".svg" else "smith.export_filter_png"
            ),
        )
        if not path_text:
            return
        try:
            self._smith_view.save_image(Path(path_text))
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._translator.t("smith.export_title"),
                str(exc),
            )

    def _export_smith_csv(self) -> None:
        if not self._smith_view.simulated_points():
            return
        path_text, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("smith.export_title"),
            str(Path.home() / "smith.csv"),
            self._translator.t("smith.export_filter_csv"),
        )
        if not path_text:
            return
        try:
            Path(path_text).write_text(self._smith_csv_text(), encoding="utf-8")
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._translator.t("smith.export_title"),
                str(exc),
            )

    def _smith_csv_text(self) -> str:
        lines = [
            "series,frequency_hz,resistance_ohm,reactance_ohm,"
            "gamma_real,gamma_imag,swr,reference_impedance_ohm"
        ]
        for series, points in (
            ("simulated", self._smith_view.simulated_points()),
            ("measured", self._smith_view.measured_points()),
            ("preview", self._smith_view.preview_points()),
        ):
            for point in points:
                lines.append(
                    f"{series},{point.frequency_hz:.6f},"
                    f"{point.impedance_ohm.real:.6f},{point.impedance_ohm.imag:.6f},"
                    f"{point.gamma.real:.9f},{point.gamma.imag:.9f},"
                    f"{point.swr:.6f},{point.reference_impedance_ohm:.3f}"
                )
        return "\n".join(lines) + "\n"

    def _render_impedance(self) -> None:
        self._table.setRowCount(0)
        self._impedance_plot.clear()
        self._swr_plot.clear()
        self._impedance_markers = ()
        self._swr_markers = ()

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
        self._render_sources(frequencies)
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
            name=self._translator.t("table.resistance"),
        )
        self._impedance_plot.plot(
            x,
            reactance,
            pen=pg.mkPen(self._colors.reactance, width=2),
            name=self._translator.t("table.reactance"),
        )
        self._impedance_markers = tuple(
            marker
            for marker in (
                self._add_marker_layer(
                    self._impedance_plot,
                    x,
                    resistance,
                    self._colors.resistance,
                ),
                self._add_marker_layer(
                    self._impedance_plot,
                    x,
                    reactance,
                    self._colors.reactance,
                ),
            )
            if marker is not None
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
            )
            marker = self._add_marker_layer(
                self._swr_plot,
                swr_x,
                swr_y,
                self._colors.swr,
            )
            if marker is not None:
                self._swr_markers = (marker,)
            self._add_band_edges(swr_x)

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

    def _render_sources(self, frequencies: tuple[FrequencyResult, ...]) -> None:
        rows = [
            (frequency, source_index, source)
            for frequency in frequencies
            for source_index, source in enumerate(frequency.source_results, start=1)
        ]
        index = self._tabs.indexOf(self._sources_tab)
        if index >= 0:
            self._tabs.setTabVisible(index, bool(rows))
        self._sources_table.setRowCount(len(rows))
        for row, (frequency, source_index, source) in enumerate(rows):
            values = [
                f"{frequency.frequency_hz / 1e6:.6f}",
                f"S{source_index}",
                source.wire_id,
                f"{source.amplitude:.3f}",
                f"{source.phase_deg:.1f}°",
                f"{source.impedance_ohm.real:.3f}",
                f"{source.impedance_ohm.imag:+.3f}",
                f"{source.power_w:+.6f}",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self._sources_table.setItem(row, column, item)
        self._sources_table.resizeColumnsToContents()

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
        self._render_patterns()
        self._render_decision_metrics()

    def _select_pattern_index(self, index: int) -> None:
        if not 0 <= index < self._pattern_frequency.count():
            return
        self._pattern_frequency.blockSignals(True)
        self._pattern_frequency.setCurrentIndex(index)
        self._pattern_frequency.blockSignals(False)
        self._populate_cut_values()
        self._render_patterns()

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

    def _pattern_metric_value(self) -> PatternGainMetric:
        value = self._pattern_metric.currentData()
        try:
            return PatternGainMetric(str(value))
        except ValueError:
            return PatternGainMetric.POWER

    def _pattern_metric_name(self) -> str:
        return self._translator.t(f"pattern.metric.{self._pattern_metric_value().value}")

    def _selected_pattern_frequency(self) -> FrequencyResult | None:
        index = self._pattern_frequency.currentIndex()
        if 0 <= index < len(self._pattern_frequencies):
            return self._pattern_frequencies[index]
        return None

    @staticmethod
    def _cut_value(combo: QComboBox) -> float | None:
        value = combo.currentData()
        return float(value) if isinstance(value, (int, float)) else None

    @staticmethod
    def _set_cut_values(
        combo: QComboBox,
        values: Sequence[float],
        *,
        default: float | None,
        label: Callable[[float], str],
    ) -> None:
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for value in values:
            combo.addItem(label(value), value)
        combo.blockSignals(False)
        selected = (
            float(current)
            if isinstance(current, (int, float)) and float(current) in values
            else default
        )
        combo.blockSignals(True)
        combo.setCurrentIndex(combo.findData(selected) if selected is not None else -1)
        combo.blockSignals(False)

    def _populate_cut_values(self) -> None:
        frequency = self._selected_pattern_frequency()
        points = (
            [point for point in frequency.far_field if point.gain_total_db is not None]
            if frequency is not None
            else []
        )
        if not points:
            self._set_cut_values(
                self._azimuth_cut,
                (),
                default=None,
                label=lambda value: f"θ={value:g}°",
            )
            self._set_cut_values(
                self._elevation_cut,
                (),
                default=None,
                label=lambda value: f"φ={value:g}°",
            )
            return
        maximum = max(
            points,
            key=lambda point: point.gain_total_db if point.gain_total_db is not None else -math.inf,
        )
        theta_values = tuple(sorted({point.theta_deg for point in points}))
        phi_values = tuple(sorted({point.phi_deg for point in points}))
        self._set_cut_values(
            self._azimuth_cut,
            theta_values,
            default=maximum.theta_deg,
            label=lambda value: f"θ={value:g}°",
        )
        self._set_cut_values(
            self._elevation_cut,
            phi_values,
            default=maximum.phi_deg,
            label=lambda value: f"φ={value:g}°",
        )

    def _render_patterns(self) -> None:
        for plot in (self._azimuth_plot, self._elevation_plot):
            plot.clear()
        for cursor in (self._azimuth_cursor, self._elevation_cursor):
            cursor.clear()
        self._azimuth_polar.set_points(())
        self._elevation_polar.set_points(())
        self._pattern_3d.set_points(())
        self._pattern_metric_summary.setText("")
        if self._result is None or not self._result.frequencies:
            self._set_empty_pattern(self._translator.t("results.none"))
            return
        frequency = self._selected_pattern_frequency()
        if frequency is None:
            title = (
                self._translator.t("pattern.negative_resistance")
                if any(item.impedance_ohm.real <= 0.0 for item in self._result.frequencies)
                else self._translator.t("pattern.none")
            )
            self._set_empty_pattern(title)
            return
        metric = self._pattern_metric_value()
        metric_label = self._pattern_metric_name()
        offset = pattern_gain_offset_db(frequency, metric)
        if offset is None:
            title = (
                self._translator.t("pattern.negative_resistance")
                if frequency.impedance_ohm.real <= 0.0
                else self._translator.t("pattern.metric_unavailable", metric=metric_label)
            )
            self._set_empty_pattern(title)
            self._update_metric_summary(frequency)
            return
        self._azimuth_polar.set_metric_label(metric_label)
        self._elevation_polar.set_metric_label(metric_label)
        self._pattern_3d.set_metric_label(metric_label)
        self._render_azimuth_cut(frequency, metric_label, offset)
        self._render_elevation_cut(frequency, metric_label, offset)
        ground = (
            self._design is not None
            and self._design.antenna.environment.ground.kind is not GroundKind.FREE_SPACE
        )
        parameters = self._design.parameters if self._design is not None else None
        antenna_azimuth, antenna_vertical = antenna_orientation(parameters)
        model = self._design.antenna if self._design is not None else None
        footprint_segments = (
            tuple(
                (wire.start.x_m, wire.start.y_m, wire.end.x_m, wire.end.y_m) for wire in model.wires
            )
            if model is not None
            else ()
        )
        feed_point: tuple[float, float] | None = None
        if model is not None:
            try:
                feed_wire = model.feed_wire
                ratio = min(max(model.feed.offset_m / feed_wire.length_m, 0.0), 1.0)
                feed_point = (
                    feed_wire.start.x_m + (feed_wire.end.x_m - feed_wire.start.x_m) * ratio,
                    feed_wire.start.y_m + (feed_wire.end.y_m - feed_wire.start.y_m) * ratio,
                )
            except (ValueError, AttributeError):
                feed_point = None
        self._pattern_3d.set_points(
            tuple(
                (point.theta_deg, point.phi_deg, point.gain_total_db + offset)
                for point in frequency.far_field
                if point.gain_total_db is not None
            ),
            ground=ground,
            antenna_azimuth=antenna_azimuth,
            antenna_vertical=antenna_vertical,
            forward_azimuth=forward_axis_azimuth(parameters),
            front_to_back_db=front_to_back_db(frequency.far_field),
            footprint_segments=footprint_segments,
            feed_point=feed_point,
        )
        self._update_metric_summary(frequency)

    def _set_empty_pattern(self, title: str) -> None:
        for plot in (self._azimuth_plot, self._elevation_plot):
            plot.setTitle(title, color=self._colors.text)
        for cursor in (self._azimuth_cursor, self._elevation_cursor):
            cursor.clear()
        self._azimuth_polar.set_points(())
        self._elevation_polar.set_points(())
        self._pattern_3d.set_points(())

    def _render_azimuth_cut(
        self,
        frequency: FrequencyResult,
        metric_label: str,
        offset: float,
    ) -> None:
        cut = self._cut_value(self._azimuth_cut)
        points = (
            [
                (point.phi_deg, point.gain_total_db + offset)
                for point in frequency.far_field
                if point.gain_total_db is not None
                and cut is not None
                and abs(point.theta_deg - cut) < 1e-6
            ]
            if cut is not None
            else []
        )
        if not points:
            self._azimuth_plot.setTitle(
                self._translator.t("pattern.none"),
                color=self._colors.text,
            )
            self._azimuth_polar.set_points(())
            return
        points.sort(key=lambda item: item[0])
        angle = [item[0] for item in points]
        gain = [item[1] for item in points]
        self._azimuth_plot.setTitle(
            self._translator.t(
                "pattern.azimuth_title",
                cut=f"{cut:g}",
                metric=metric_label,
            ),
            color=self._colors.text,
        )
        self._azimuth_plot.setLabel(
            "bottom",
            self._translator.t("pattern.azimuth"),
            color=self._colors.text,
        )
        self._azimuth_plot.setLabel(
            "left",
            self._translator.t("pattern.metric_axis", metric=metric_label),
            color=self._colors.text,
        )
        self._azimuth_plot.plot(
            angle,
            gain,
            pen=pg.mkPen(self._colors.pattern, width=2),
            symbol="o",
            symbolSize=4,
        )
        self._azimuth_plot.setXRange(min(angle), max(angle), padding=0.02)
        self._azimuth_cursor.set_series(
            (
                CursorSeries(
                    metric_label,
                    tuple(angle),
                    tuple(gain),
                    self._colors.pattern,
                ),
            ),
            readout_builder=lambda cursor_x, values: self._pattern_readout(cursor_x, "φ", values),
            wrap_period=360.0,
        )
        self._azimuth_polar.set_cut(cut, symbol="θ")
        self._azimuth_polar.set_mirror(False)
        self._azimuth_polar.set_closed(True)
        parameters = self._design.parameters if self._design is not None else None
        azimuth, vertical = antenna_orientation(parameters)
        if azimuth is not None and not vertical:
            self._azimuth_polar.set_antenna(azimuth)
        else:
            self._azimuth_polar.set_antenna(None, vertical=vertical)
        self._azimuth_polar.set_title(
            f"{self._translator.t('pattern.polar_azimuth')} · {metric_label}"
        )
        self._azimuth_polar.set_points(tuple(zip(angle, gain, strict=True)))

    def _render_elevation_cut(
        self,
        frequency: FrequencyResult,
        metric_label: str,
        offset: float,
    ) -> None:
        cut = self._cut_value(self._elevation_cut)
        points = (
            [
                (point.theta_deg, point.gain_total_db + offset)
                for point in frequency.far_field
                if point.gain_total_db is not None
                and cut is not None
                and abs(point.phi_deg - cut) < 1e-6
            ]
            if cut is not None
            else []
        )
        if not points:
            self._elevation_plot.setTitle(
                self._translator.t("pattern.none"),
                color=self._colors.text,
            )
            self._elevation_polar.set_points(())
            return
        points.sort(key=lambda item: item[0])
        angle = [item[0] for item in points]
        gain = [item[1] for item in points]
        self._elevation_plot.setTitle(
            self._translator.t(
                "pattern.elevation_title",
                cut=f"{cut:g}",
                metric=metric_label,
            ),
            color=self._colors.text,
        )
        self._elevation_plot.setLabel(
            "bottom",
            self._translator.t("pattern.elevation"),
            color=self._colors.text,
        )
        self._elevation_plot.setLabel(
            "left",
            self._translator.t("pattern.metric_axis", metric=metric_label),
            color=self._colors.text,
        )
        self._elevation_plot.plot(
            angle,
            gain,
            pen=pg.mkPen(self._colors.pattern, width=2),
            symbol="o",
            symbolSize=4,
        )
        self._elevation_plot.setXRange(min(angle), max(angle), padding=0.02)
        self._elevation_cursor.set_series(
            (
                CursorSeries(
                    metric_label,
                    tuple(angle),
                    tuple(gain),
                    self._colors.pattern,
                ),
            ),
            readout_builder=lambda cursor_x, values: self._pattern_readout(cursor_x, "θ", values),
        )
        self._elevation_polar.set_cut(cut, symbol="φ")
        self._elevation_polar.set_mirror(True)
        self._elevation_polar.set_closed(max(angle) >= 180.0)
        parameters = self._design.parameters if self._design is not None else None
        orientation = getattr(parameters, "orientation", None)
        vertical = getattr(orientation, "value", orientation) == "vertical"
        self._elevation_polar.set_antenna(None, vertical=vertical)
        self._elevation_polar.set_title(
            f"{self._translator.t('pattern.polar_elevation')} · {metric_label}"
        )
        self._elevation_polar.set_points(tuple(zip(angle, gain, strict=True)))

    def _update_metric_summary(self, frequency: FrequencyResult) -> None:
        self._pattern_metric_summary.setText(
            self._translator.t(
                "pattern.metric_summary",
                power=self._metric_value(max_power_gain_db(frequency.far_field)),
                directivity=self._metric_value(frequency.directivity_db),
                realized=self._metric_value(frequency.realized_gain_db),
            )
        )

    def _metric_value(self, value: float | None) -> str:
        if value is None or not math.isfinite(value):
            return self._translator.t("pattern.metric_value_unavailable")
        return f"{value:.2f} dBi"

    def _pattern_readout(
        self,
        angle_deg: float,
        symbol: str,
        values: tuple[tuple[str, float], ...],
    ) -> str:
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
        self._uncertainty_group.setVisible(False)
        index = self._measurement_selector.currentIndex()
        valid = 0 <= index < len(self._measurements)
        self._measurement_edit.setEnabled(valid)
        self._measurement_delete.setEnabled(valid)
        self._measurement_tune.setEnabled(valid)
        if not valid:
            return
        measurement = self._measurements[index]
        self._uncertainty_group.setVisible(True)
        self._render_measurement_uncertainty(measurement)
        self._measurement_compare.setEnabled(len(self._measurements) >= 2)
        details = []
        session = (
            self._measurement_session_names.get(measurement.session_id)
            if measurement.session_id is not None
            else None
        )
        if session:
            details.append(self._translator.t("measurement.session_value", value=session))
        if measurement.source:
            details.append(self._translator.t("measurement.source_value", value=measurement.source))
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

    def _render_measurement_uncertainty(self, measurement: Measurement) -> None:
        session = (
            self._measurement_session_data.get(measurement.session_id)
            if measurement.session_id is not None
            else None
        )
        assessment = assess_measurement_uncertainty(
            measurement,
            session=session,
            simulation=self._result,
        )
        t = self._translator.t
        level = t(f"measurement.uncertainty.level.{assessment.level.value}")
        self._uncertainty_level.setText(t("measurement.uncertainty.level_label", level=level))
        level_color = {
            MeasurementUncertaintyLevel.DOCUMENTED: self._colors.swr,
            MeasurementUncertaintyLevel.PARTIAL: self._colors.reactance,
            MeasurementUncertaintyLevel.LIMITED: self._colors.feed,
        }[assessment.level]
        self._uncertainty_level.setStyleSheet(f"font-weight: bold; color: {level_color.name()};")
        lines = [
            self._documentation_line(
                "calibration",
                assessment.calibration_status,
                assessment.calibration_value,
            ),
            self._documentation_line(
                "reference_plane",
                assessment.reference_plane_status,
                assessment.reference_plane_value,
            ),
            self._documentation_line(
                "feed_line",
                assessment.feed_line_status,
                assessment.feed_line_value,
            ),
        ]
        if assessment.conditions_status is MeasurementDocumentationStatus.DOCUMENTED:
            value = assessment.conditions_value
            if assessment.session_name:
                value = f"{assessment.session_name}: {value}"
            lines.append(t("measurement.uncertainty.conditions_value", value=value))
        else:
            lines.append(t("measurement.uncertainty.conditions_missing"))
        lines.append(
            t(
                "measurement.uncertainty.points_value",
                count=assessment.point_count,
                start=f"{assessment.start_frequency_hz / 1e6:.6f}",
                stop=f"{assessment.stop_frequency_hz / 1e6:.6f}",
                gap=f"{assessment.max_spacing_hz / 1e3:.3f}",
            )
        )
        lines.append(
            t(
                "measurement.uncertainty.reference_impedance_value",
                value=f"{assessment.reference_impedance_ohm:g}",
            )
        )
        if not assessment.resonance_frequencies_hz:
            lines.append(t("measurement.uncertainty.resonance_none"))
        elif len(assessment.resonance_frequencies_hz) == 1:
            lines.append(
                t(
                    "measurement.uncertainty.resonance_one",
                    frequency=f"{assessment.resonance_frequencies_hz[0] / 1e6:.6f}",
                )
            )
        else:
            frequencies = ", ".join(
                f"{frequency / 1e6:.3f}" for frequency in assessment.resonance_frequencies_hz
            )
            lines.append(
                t(
                    "measurement.uncertainty.resonance_multiple",
                    count=len(assessment.resonance_frequencies_hz),
                    frequencies=frequencies,
                )
            )
        if assessment.compared_count is None:
            lines.append(t("measurement.uncertainty.comparison_unavailable"))
        else:
            coverage = assessment.coverage_percent or 0.0
            lines.append(
                t(
                    "measurement.uncertainty.comparison_value",
                    compared=assessment.compared_count,
                    total=assessment.point_count,
                    coverage=f"{coverage:.0f}",
                )
            )
            if assessment.simulated_max_spacing_hz is not None:
                if assessment.simulated_max_spacing_hz > 0.0:
                    lines.append(
                        t(
                            "measurement.uncertainty.simulation_spacing_value",
                            gap=f"{assessment.simulated_max_spacing_hz / 1e3:.3f}",
                        )
                    )
                else:
                    lines.append(t("measurement.uncertainty.simulation_single"))
        self._uncertainty_factors.setText("\n".join(lines))
        warnings = [t(key) for key in assessment.warnings]
        self._uncertainty_warnings.setText(
            "\n".join(warnings) if warnings else t("measurement.uncertainty.warnings_none")
        )
        self._uncertainty_warnings.setStyleSheet(f"color: {self._colors.reactance.name()};")
        self._uncertainty_disclaimer.setText(t("measurement.uncertainty.disclaimer"))

    def _documentation_line(
        self,
        prefix: str,
        status: MeasurementDocumentationStatus,
        value: str,
    ) -> str:
        if status is MeasurementDocumentationStatus.MISSING:
            return self._translator.t(f"measurement.uncertainty.{prefix}_missing")
        if status is MeasurementDocumentationStatus.UNCERTAIN:
            return self._translator.t(
                f"measurement.uncertainty.{prefix}_uncertain",
                value=value,
            )
        return self._translator.t(
            f"measurement.uncertainty.{prefix}_value",
            value=value,
        )

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

    def _request_measurement_compare(self) -> None:
        index = self._measurement_selector.currentIndex()
        measurement = self._measurements[index] if 0 <= index < len(self._measurements) else None
        self.measurement_compare_requested.emit(measurement)

    def _request_measurement_tune(self) -> None:
        index = self._measurement_selector.currentIndex()
        if 0 <= index < len(self._measurements):
            self.measurement_tune_requested.emit(self._measurements[index])

    def _render_diagnostics(self) -> None:
        self._render_decision_metrics()
        self._render_confidence()
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

    def _render_decision_metrics(self) -> None:
        self._decision_table.setRowCount(0)
        if self._result is None or not self._result.frequencies:
            self._decision_group.setVisible(False)
            return
        frequency = self._selected_pattern_frequency()
        if frequency is None:
            target = (
                self._design.parameters.frequency_hz
                if self._design is not None
                else self._result.frequencies[0].frequency_hz
            )
            frequency = min(
                self._result.frequencies,
                key=lambda item: abs(item.frequency_hz - target),
            )
        metrics = decision_metrics(frequency, self._result.frequencies)
        t = self._translator.t
        bandwidth = metrics.swr_bandwidth_2_1
        if bandwidth.bandwidth_hz is not None:
            bandwidth_text = f"{bandwidth.bandwidth_hz / 1e6:.3f} MHz"
        elif bandwidth.lower_hz is not None and bandwidth.upper_hz is not None:
            bandwidth_text = t("results.metric.unbracketed")
        else:
            bandwidth_text = t("results.metric.unavailable")
        rows = (
            ("results.metric.bandwidth", bandwidth_text),
            (
                "results.metric.hpbw_azimuth",
                self._beamwidth_text(
                    metrics.hpbw_azimuth.width_deg,
                    metrics.hpbw_azimuth.bracketed,
                ),
            ),
            (
                "results.metric.hpbw_elevation",
                self._beamwidth_text(
                    metrics.hpbw_elevation.width_deg,
                    metrics.hpbw_elevation.bracketed,
                ),
            ),
            (
                "results.metric.front_to_back",
                self._metric_value_text(metrics.front_to_back_db, "dB"),
            ),
            ("results.metric.sidelobe", self._metric_value_text(metrics.sidelobe_level_db, "dB")),
            ("results.metric.takeoff", self._metric_value_text(metrics.takeoff_deg, "°")),
            (
                "results.metric.efficiency",
                self._metric_value_text(metrics.efficiency_percent, "%"),
            ),
            ("results.metric.directivity", self._metric_value_text(metrics.directivity_db, "dBi")),
            ("results.metric.realized", self._metric_value_text(metrics.realized_gain_db, "dBi")),
            (
                "results.metric.axial_ratio",
                self._metric_value_text(metrics.axial_ratio_db, "dB"),
            ),
            (
                "results.metric.polarization",
                metrics.polarization_sense or t("results.metric.unavailable"),
            ),
            ("results.metric.cp_gain", self._metric_value_text(metrics.cp_gain_db, "dBi")),
            (
                "results.metric.xpd",
                "∞"
                if metrics.cross_polar_discrimination_db == math.inf
                else (
                    t("results.metric.unavailable")
                    if metrics.cross_polar_discrimination_db is None
                    else f"{metrics.cross_polar_discrimination_db:.1f} dB"
                ),
            ),
            (
                "results.metric.resolution",
                self._metric_value_text(metrics.pattern_resolution_deg, "°"),
            ),
        )
        self._decision_table.setRowCount(len(rows))
        for row, (key, value) in enumerate(rows):
            self._decision_table.setItem(row, 0, QTableWidgetItem(t(key)))
            item = QTableWidgetItem(value)
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._decision_table.setItem(row, 1, item)
        self._decision_table.resizeColumnsToContents()
        self._decision_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        self._decision_group.setVisible(True)

    def _beamwidth_text(self, value: float | None, bracketed: bool) -> str:
        if value is not None:
            return f"{value:.1f}°"
        if not bracketed:
            return self._translator.t("results.metric.unbracketed")
        return self._translator.t("results.metric.unavailable")

    def _metric_value_text(self, value: float | None, suffix: str) -> str:
        if value is None:
            return self._translator.t("results.metric.unavailable")
        if math.isinf(value):
            return "∞"
        return f"{value:.2f} {suffix}"

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
                frequency.balun_loss_db,
                frequency.transformer_loss_db,
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
            balun=value(frequency.balun_loss_db, "dB"),
            transformer=value(frequency.transformer_loss_db, "dB"),
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
