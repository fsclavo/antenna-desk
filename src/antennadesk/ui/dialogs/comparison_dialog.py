# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Multi-design comparison under an explicit common basis."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from uuid import UUID

import pyqtgraph as pg
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
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
from ...domain.design.comparison import ComparisonBasis, native_height_m
from ...domain.design.suitability import PROFILES_BY_KEY
from ...domain.environment.ground import GroundModel
from ...domain.projects.project import DesignVariant, Project
from ...domain.simulation.band_result import BandAnalysisResult
from ...domain.simulation.band_summary import summarize_band
from ...domain.simulation.bands import AmateurBand
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.result import FrequencyResult, SimulationResult
from ..fonts import apply_plot_fonts, scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator
from ..template_identity import catalog_key_for
from ..theme import theme_colors
from ..units import (
    UnitSystem,
    diameter_from_m,
    diameter_unit_key,
    length_from_m,
    length_to_m,
    length_unit_key,
)
from ..widgets.ground_presets import SOIL_PRESETS

MAX_COMPARISON_DESIGNS = 4
DEFAULT_POINTS = 31


class ComparisonDialog(QDialog):
    """Compare two to four designs and request a common-basis recompute."""

    recompute_requested = Signal(object, object)

    def __init__(
        self,
        translator: Translator,
        project: Project,
        results: Mapping[UUID, SimulationResult],
        parent: QWidget | None = None,
        *,
        band_analyses: Mapping[UUID, BandAnalysisResult] | None = None,
        unit_system: UnitSystem = UnitSystem.METRIC,
        initial_basis: ComparisonBasis | None = None,
        initial_design_ids: Sequence[UUID] | None = None,
        height_mapping: Mapping[UUID, tuple[bool, tuple[str, ...]]] | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._results = dict(results)
        self._band_analyses = dict(band_analyses or {})
        self._unit_system = unit_system
        self._height_mapping = dict(height_mapping or {})
        self._basis = initial_basis or self._default_basis(project)
        self._recomputing = False
        self._colors = theme_colors(self.palette())
        self.setWindowTitle(translator.t("compare.title"))
        self.resize(*scaled_dialog_size(1_080, 840))

        self._build_ui()
        self._populate_designs(initial_design_ids)
        self._load_basis(self._basis)
        self._apply_theme()
        self._refresh()
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.fontChanged.connect(self._on_application_font_changed)

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        t = self._translator.t
        self._design_group = QGroupBox(t("compare.designs"), self)
        design_layout = QVBoxLayout(self._design_group)
        self._design_list = QListWidget(self._design_group)
        self._design_list.itemChanged.connect(self._on_design_changed)
        apply_help(self._design_list, self._translator, "compare.designs")
        design_layout.addWidget(self._design_list)

        self._basis_group = QGroupBox(t("compare.basis"), self)
        basis_form = QFormLayout(self._basis_group)
        self._start = QDoubleSpinBox(self._basis_group)
        self._stop = QDoubleSpinBox(self._basis_group)
        for spin in (self._start, self._stop):
            spin.setRange(0.1, 100_000.0)
            spin.setDecimals(6)
            spin.setSuffix(" MHz")
        self._points = QSpinBox(self._basis_group)
        self._points.setRange(2, 1_000)
        self._points.setValue(DEFAULT_POINTS)
        self._ground = QComboBox(self._basis_group)
        self._ground.addItem(t("compare.ground_free_space"), GroundModel.free_space())
        self._ground.addItem(t("compare.ground_perfect"), GroundModel.perfect())
        for preset in SOIL_PRESETS:
            self._ground.addItem(
                t(preset.label_key),
                GroundModel.finite(
                    relative_permittivity=preset.relative_permittivity,
                    conductivity_s_per_m=preset.conductivity_s_per_m,
                ),
            )
        self._reference_height = QDoubleSpinBox(self._basis_group)
        self._reference_height.setRange(0.0, 10_000.0)
        self._reference_height.setDecimals(2)
        self._reference_height.setSpecialValueText(t("compare.height_native"))
        self._reference_height.setSuffix(f" {t(length_unit_key(self._unit_system))}")
        self._reference_frequency = QDoubleSpinBox(self._basis_group)
        self._reference_frequency.setRange(0.1, 100_000.0)
        self._reference_frequency.setDecimals(6)
        self._reference_frequency.setSuffix(" MHz")
        self._recompute = QPushButton(t("compare.recompute"), self._basis_group)
        self._recompute.clicked.connect(self._request_recompute)
        apply_help(self._recompute, self._translator, "compare.recompute")

        basis_rows: list[tuple[str, QWidget]] = [
            (t("compare.start"), self._start),
            (t("compare.stop"), self._stop),
            (t("compare.points"), self._points),
            (t("compare.ground"), self._ground),
            (t("compare.reference_height"), self._reference_height),
            (t("compare.reference_frequency"), self._reference_frequency),
        ]
        for row, (label_text, widget) in enumerate(basis_rows):
            label = QLabel(label_text, self._basis_group)
            basis_form.addRow(label, widget)
            apply_row_help(
                basis_form,
                row,
                self._translator,
                f"compare.{self._basis_help_key(row)}",
            )
        basis_form.addRow(self._recompute)

        self._basis_label = QLabel(self)
        self._basis_label.setWordWrap(True)
        self._basis_label.setStyleSheet("font-style: italic;")

        self._table = QTableWidget(0, 1, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setMinimumHeight(240)
        apply_help(self._table, self._translator, "table.comparison")

        self._band_label = QLabel(t("band.group_title"), self)
        self._band_table = QTableWidget(0, 1, self)
        self._band_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._band_table.setAlternatingRowColors(True)
        self._band_table.verticalHeader().setVisible(False)
        self._band_table.horizontalHeader().setStretchLastSection(True)
        self._band_table.setMaximumHeight(150)
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
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(t("action.close"))

        top = QHBoxLayout()
        top.addWidget(self._design_group, 1)
        top.addWidget(self._basis_group, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self._basis_label)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._band_label)
        layout.addWidget(self._band_table)
        layout.addWidget(self._swr_plot, 1)
        layout.addWidget(self._pattern_plot, 1)
        layout.addWidget(self._note)
        layout.addWidget(buttons)
        self._update_recompute_enabled()

    @staticmethod
    def _basis_help_key(row: int) -> str:
        return (
            "start",
            "stop",
            "points",
            "ground",
            "reference_height",
            "reference_frequency",
        )[row]

    @staticmethod
    def _make_plot() -> pg.PlotWidget:
        plot = pg.PlotWidget()
        plot.showGrid(x=True, y=True, alpha=0.3)
        return plot

    def _plots(self) -> tuple[pg.PlotWidget, ...]:
        return (self._swr_plot, self._pattern_plot)

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

    def _on_application_font_changed(self, font: QFont) -> None:
        del font
        apply_plot_fonts(self._plots())

    # ---------------------------------------------------------------- basis

    def _default_basis(self, project: Project) -> ComparisonBasis:
        design = project.designs[0]
        frequency_hz = design.parameters.frequency_hz
        return ComparisonBasis(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_POINTS,
            ),
            ground=design.parameters.ground,
            reference_height_m=native_height_m(design.parameters),
            reference_frequency_hz=frequency_hz,
        )

    def _load_basis(self, basis: ComparisonBasis) -> None:
        self._start.setValue(basis.frequency_plan.start_hz / 1_000_000.0)
        self._stop.setValue(basis.frequency_plan.stop_hz / 1_000_000.0)
        self._points.setValue(basis.frequency_plan.count)
        index = self._ground_index(basis.ground)
        self._ground.setCurrentIndex(index if index >= 0 else 0)
        self._reference_height.setValue(
            length_from_m(basis.reference_height_m, self._unit_system)
            if basis.reference_height_m is not None
            else 0.0
        )
        self._reference_frequency.setValue(basis.reference_frequency_hz / 1_000_000.0)
        self._basis_label.setText(self._basis_text(basis))
        self._update_recompute_enabled()

    def _basis_from_form(self) -> ComparisonBasis:
        start = self._start.value() * 1_000_000.0
        stop = self._stop.value() * 1_000_000.0
        if stop <= start:
            raise ValueError(self._translator.t("compare.invalid_range"))
        height = self._reference_height.value()
        return ComparisonBasis(
            frequency_plan=FrequencyPlan.sweep(start, stop, self._points.value()),
            ground=self._ground.currentData(),
            reference_height_m=(length_to_m(height, self._unit_system) if height > 0.0 else None),
            reference_frequency_hz=self._reference_frequency.value() * 1_000_000.0,
        )

    def _ground_index(self, ground: GroundModel) -> int:
        for index in range(self._ground.count()):
            data = self._ground.itemData(index)
            if isinstance(data, GroundModel) and data == ground:
                return index
        return -1

    def _basis_text(self, basis: ComparisonBasis) -> str:
        t = self._translator.t
        height = (
            t("compare.height_native")
            if basis.reference_height_m is None
            else f"{length_from_m(basis.reference_height_m, self._unit_system):.1f} "
            f"{t(length_unit_key(self._unit_system))}"
        )
        return t(
            "compare.basis_text",
            start=f"{basis.frequency_plan.start_hz / 1e6:.3f}",
            stop=f"{basis.frequency_plan.stop_hz / 1e6:.3f}",
            points=basis.frequency_plan.count,
            height=height,
            frequency=f"{basis.reference_frequency_hz / 1e6:.3f}",
        )

    def _request_recompute(self) -> None:
        try:
            basis = self._basis_from_form()
        except ValueError as exc:
            self._set_note(str(exc), visible=True)
            return
        ids = self._selected_ids()
        if len(ids) < 2:
            self._set_note(self._translator.t("compare.select_two"), visible=True)
            return
        self.recompute_requested.emit(basis, tuple(ids))

    def _update_recompute_enabled(self) -> None:
        enabled = not self._recomputing and len(self._selected_ids()) >= 2
        self._recompute.setEnabled(enabled)
        for widget in (
            self._start,
            self._stop,
            self._points,
            self._ground,
            self._reference_height,
            self._reference_frequency,
        ):
            widget.setEnabled(not self._recomputing)
        self._design_list.setEnabled(not self._recomputing)

    # --------------------------------------------------------------- designs

    def _populate_designs(self, initial_ids: Sequence[UUID] | None) -> None:
        selected = set(initial_ids or ())
        if not selected:
            selected = {design.id for design in self._project.designs[:2]}
        self._design_list.blockSignals(True)
        for design in self._project.designs:
            item = QListWidgetItem(design.name)
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setCheckState(
                Qt.CheckState.Checked if design.id in selected else Qt.CheckState.Unchecked
            )
            item.setData(Qt.ItemDataRole.UserRole, str(design.id))
            self._design_list.addItem(item)
        self._design_list.blockSignals(False)
        self._on_design_changed()

    def _selected_ids(self) -> tuple[UUID, ...]:
        ids: list[UUID] = []
        for row in range(self._design_list.count()):
            item = self._design_list.item(row)
            if item.checkState() is Qt.CheckState.Checked:
                try:
                    ids.append(UUID(str(item.data(Qt.ItemDataRole.UserRole))))
                except ValueError:
                    continue
        return tuple(ids)

    def _on_design_changed(self, _item: QListWidgetItem | None = None) -> None:
        selected = self._selected_ids()
        if len(selected) > MAX_COMPARISON_DESIGNS:
            self._design_list.blockSignals(True)
            item = self._design_list.currentItem()
            if item is not None:
                item.setCheckState(Qt.CheckState.Unchecked)
            self._design_list.blockSignals(False)
            self._set_note(self._translator.t("compare.max_four"), visible=True)
        self._update_recompute_enabled()
        self._refresh()

    def _design_by_id(self, design_id: UUID) -> DesignVariant | None:
        try:
            return self._project.design_by_id(design_id)
        except KeyError:
            return None

    # --------------------------------------------------------------- results

    def set_recomputing(self, recomputing: bool) -> None:
        self._recomputing = recomputing
        if recomputing:
            self._set_note(self._translator.t("compare.recomputing"), visible=True)
        else:
            self._set_note("", visible=False)
        self._update_recompute_enabled()

    def set_results(
        self,
        results: Mapping[UUID, SimulationResult],
        *,
        basis: ComparisonBasis | None = None,
        band_analyses: Mapping[UUID, BandAnalysisResult] | None = None,
        height_mapping: Mapping[UUID, tuple[bool, tuple[str, ...]]] | None = None,
    ) -> None:
        self._results = dict(results)
        if band_analyses is not None:
            self._band_analyses = dict(band_analyses)
        if height_mapping is not None:
            self._height_mapping = dict(height_mapping)
        if basis is not None:
            self._basis = basis
            self._load_basis(basis)
        self._recomputing = False
        self._update_recompute_enabled()
        self._refresh()

    def set_error(self, message: str) -> None:
        self._recomputing = False
        self._update_recompute_enabled()
        self._set_note(
            self._translator.t("compare.recompute_error", message=message),
            visible=True,
        )

    def _set_note(self, text: str, *, visible: bool) -> None:
        self._note.setText(text)
        self._note.setVisible(visible)

    # --------------------------------------------------------------- refresh

    def _refresh(self) -> None:
        designs: list[DesignVariant] = []
        for design_id in self._selected_ids():
            design = self._design_by_id(design_id)
            if design is not None:
                designs.append(design)
        if not designs:
            self._table.setRowCount(0)
            self._table.setColumnCount(1)
            self._band_label.setVisible(False)
            self._band_table.setVisible(False)
            self._swr_plot.clear()
            self._pattern_plot.clear()
            return

        rows = self._rows(designs[0], self._results.get(designs[0].id))
        self._table.setColumnCount(1 + len(designs))
        self._table.setRowCount(len(rows))
        self._table.setHorizontalHeaderLabels(
            [self._translator.t("compare.metric"), *(design.name for design in designs)]
        )
        for row, (label, _value) in enumerate(rows):
            self._table.setItem(row, 0, QTableWidgetItem(label))
            for column, design in enumerate(designs, start=1):
                values = self._rows(design, self._results.get(design.id))
                value = values[row][1] if row < len(values) else "—"
                self._table.setItem(row, column, QTableWidgetItem(value))
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setStretchLastSection(True)

        missing = any(self._results.get(design.id) is None for design in designs)
        self._render_band_table(designs)
        self._render_charts(designs)
        notes: list[str] = []
        if missing:
            notes.append(self._translator.t("compare.no_result"))
        for design in designs:
            _mapped, warnings = self._height_mapping.get(design.id, (False, ()))
            for warning in warnings:
                notes.append(
                    self._translator.t(
                        f"compare.height_warning.{warning}",
                        name=design.name,
                    )
                )
        self._set_note("\n".join(notes), visible=bool(notes))

    def _frequency_for(
        self,
        result: SimulationResult | None,
        target_hz: float,
    ) -> FrequencyResult | None:
        if result is None or not result.frequencies:
            return None
        return min(
            result.frequencies,
            key=lambda item: abs(item.frequency_hz - target_hz),
        )

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
        design: DesignVariant,
        result: SimulationResult | None,
    ) -> list[tuple[str, str]]:
        t = self._translator.t
        frequency = self._frequency_for(result, self._basis.reference_frequency_hz)
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
        height_m = native_height_m(parameters)
        azimuth_deg = getattr(parameters, "azimuth_deg", None)
        wire_radius_m = getattr(parameters, "wire_radius_m", None)
        wires = design.antenna.wires
        xs = [point.x_m for wire in wires for point in (wire.start, wire.end)]
        ys = [point.y_m for wire in wires for point in (wire.start, wire.end)]
        zs = [point.z_m for wire in wires for point in (wire.start, wire.end)]
        footprint = max(max(xs) - min(xs), max(ys) - min(ys)) if wires else 0.0
        conductor_length = sum(wire.length_m for wire in wires)
        suitability = PROFILES_BY_KEY.get(catalog_key_for(parameters))
        build_effort = (
            t(f"advisor.complexity.{suitability.complexity.value}")
            if suitability is not None
            else "—"
        )
        return [
            (
                t("field.antenna_type"),
                t(f"antenna_type.{design.antenna_type}"),
            ),
            (t("field.frequency"), f"{parameters.frequency_hz / 1e6:.6f} MHz"),
            (
                t("compare.reference_frequency"),
                f"{self._basis.reference_frequency_hz / 1e6:.6f} MHz",
            ),
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
            (t("compare.footprint"), length(footprint)),
            (
                t("compare.max_height"),
                length(max(zs)) if zs else "—",
            ),
            (t("compare.conductor_length"), length(conductor_length)),
            (t("compare.wires"), str(len(wires))),
            (t("compare.loads"), str(len(design.antenna.loads))),
            (t("compare.lines"), str(len(design.antenna.transmission_lines))),
            (t("compare.build_effort"), build_effort),
            (
                t("results.solver"),
                (f"{result.solver.name} {result.solver.version}" if result else "—"),
            ),
            (t("results.status"), self._status_text(result)),
        ]

    def _render_band_table(self, designs: Sequence[DesignVariant]) -> None:
        analyses = [(design, self._band_analyses.get(design.id)) for design in designs]
        if not any(analysis is not None for _design, analysis in analyses):
            self._band_label.setVisible(False)
            self._band_table.setVisible(False)
            self._band_table.setRowCount(0)
            return
        bands: dict[str, AmateurBand] = {}
        for _design, analysis in analyses:
            if analysis is None:
                continue
            for band_result in analysis.bands:
                bands[band_result.band.name] = band_result.band
        self._band_table.setRowCount(0)
        self._band_table.setColumnCount(1 + len(designs))
        self._band_table.setHorizontalHeaderLabels(
            [
                self._translator.t("band.table.band"),
                *(f"{design.name} {self._translator.t('table.swr')}" for design in designs),
            ]
        )
        for band_id, band in sorted(
            bands.items(),
            key=lambda item: item[1].start_hz,
        ):
            row = self._band_table.rowCount()
            self._band_table.insertRow(row)
            self._band_table.setItem(row, 0, QTableWidgetItem(band_id))
            for column, (_design, analysis) in enumerate(analyses, start=1):
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
        self._band_label.setVisible(True)
        self._band_table.setVisible(True)
        self._band_table.resizeColumnsToContents()

    def _series_colors(self) -> tuple:
        return (
            self._colors.series_a,
            self._colors.series_b,
            self._colors.swr,
            self._colors.pattern,
        )

    def _render_charts(self, designs: Sequence[DesignVariant]) -> None:
        self._swr_plot.clear()
        self._pattern_plot.clear()
        self._swr_plot.setTitle(self._translator.t("compare.swr"), color=self._colors.text)
        self._swr_plot.setLabel(
            "bottom",
            self._translator.t("table.frequency"),
            color=self._colors.text,
        )
        self._swr_plot.setLabel(
            "left",
            self._translator.t("table.swr"),
            color=self._colors.text,
        )
        self._pattern_plot.setTitle(
            self._translator.t("compare.pattern"),
            color=self._colors.text,
        )
        self._pattern_plot.setLabel(
            "bottom",
            self._translator.t("pattern.elevation"),
            color=self._colors.text,
        )
        self._pattern_plot.setLabel(
            "left",
            self._translator.t("pattern.gain"),
            color=self._colors.text,
        )
        colors = self._series_colors()
        for index, design in enumerate(designs):
            result = self._results.get(design.id)
            if result is None:
                continue
            color = colors[index % len(colors)]
            swr_points = [
                (frequency.frequency_hz / 1e6, frequency.swr)
                for frequency in result.frequencies
                if math.isfinite(frequency.swr)
            ]
            if swr_points:
                self._swr_plot.plot(
                    [point[0] for point in swr_points],
                    [point[1] for point in swr_points],
                    pen=pg.mkPen(color, width=2),
                    symbol="o",
                    symbolSize=4,
                    name=design.name,
                )
            frequency = self._frequency_for(
                result,
                self._basis.reference_frequency_hz,
            )
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
                    name=design.name,
                )
