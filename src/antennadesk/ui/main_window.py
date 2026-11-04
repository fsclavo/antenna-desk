# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main application window."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from uuid import UUID, uuid4

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QCloseEvent,
    QKeySequence,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStyle,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QWizard,
)

from .. import __version__
from ..application.cancellation import EventCancelToken
from ..application.ports.antenna_solver import AntennaSolver
from ..application.ports.project_repository import ProjectRepository
from ..application.use_cases.add_design_variant import (
    AddDesignVariant,
    AddDesignVariantCommand,
)
from ..application.use_cases.analyze_bands import BandSimulationRequest
from ..application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from ..application.use_cases.delete_design_variant import (
    DeleteDesignVariant,
    DeleteDesignVariantCommand,
)
from ..application.use_cases.open_project import OpenProject
from ..application.use_cases.optimize_elements import ElementOptimizationObjective
from ..application.use_cases.optimize_yagi_elements import resize_yagi
from ..application.use_cases.record_simulation_run import (
    RecordSimulationRun,
    RecordSimulationRunCommand,
)
from ..application.use_cases.rename_design_variant import (
    RenameDesignVariant,
    RenameDesignVariantCommand,
)
from ..application.use_cases.save_project import SaveProject
from ..application.use_cases.update_dipole_design import (
    UpdateDipoleDesign,
    UpdateDipoleDesignCommand,
)
from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.design import (
    AntennaDesignParameters,
    antenna_type_for,
    template_load_ids,
    with_primary_dimension,
)
from ..domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ..domain.antennas.endfed import EndFedParameters, EndFedPreset
from ..domain.antennas.family import antenna_family
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.feed_line import FeedLine
from ..domain.antennas.g5rv import G5RV_DIPOLE_ID
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.load import LumpedLoad
from ..domain.antennas.loop import LoopParameters
from ..domain.antennas.matching_network import MatchingNetwork
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.t2fd import (
    T2FD_DRIVEN_WIRE_ID,
    T2FD_TERMINATED_WIRE_ID,
    T2FDParameters,
)
from ..domain.antennas.transmission_line import TransmissionLine
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import YagiParameters, yagi_element_length_mismatch
from ..domain.common.time import utc_now
from ..domain.common.validation import Diagnostic, Severity
from ..domain.design.band_plan import BandDefault, BandPlan, BandSelection, default_band_plan
from ..domain.design.estimators import supports_estimation
from ..domain.design.formulas import frequency_for_half_wave_length
from ..domain.design.yagi_reference import MAX_YAGI_ELEMENTS, MIN_YAGI_ELEMENTS
from ..domain.measurement import Measurement
from ..domain.projects.project import DesignProvenance, DesignVariant, Project
from ..domain.simulation.band_result import BandAnalysisResult, BandResult
from ..domain.simulation.bands import amateur_band_for, band_snapshot_frequencies
from ..domain.simulation.budget import choose_batch_pattern_step, choose_pattern_step
from ..domain.simulation.far_field import FarFieldRequest
from ..domain.simulation.frequency import FrequencyPlan
from ..domain.simulation.result import SimulationResult, SimulationStatus
from ..domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
)
from ..domain.simulation.spec import SimulationSpec
from ..importers.mmana import parse_mmana_file
from ..importers.nec2_deck import parse_nec2_deck
from ..importers.vna_csv import parse_vna_csv
from ..persistence.constants import MAX_PROJECT_SIZE_BYTES, PROJECT_SIZE_WARNING_BYTES
from ..reporting.csv_export import (
    write_band_analysis_csv,
    write_band_analysis_pattern_csv,
    write_csv,
    write_pattern_csv,
)
from ..reporting.html_report import write_html_report
from ..simulation.nec2.solver import Nec2cSolver
from .dialogs.antenna_catalog_dialog import (
    CATALOG_TYPE_CUSTOM,
    CATALOG_TYPE_DELTA_LOOP,
    CATALOG_TYPE_DOUBLET,
    CATALOG_TYPE_ENDFED,
    CATALOG_TYPE_FAN_DIPOLE,
    CATALOG_TYPE_FOLDED_DIPOLE,
    CATALOG_TYPE_G5RV,
    CATALOG_TYPE_INVERTED_V,
    CATALOG_TYPE_J_POLE,
    CATALOG_TYPE_LOADED_VERTICAL,
    CATALOG_TYPE_LOOP,
    CATALOG_TYPE_MOXON,
    CATALOG_TYPE_OCFD,
    CATALOG_TYPE_QUAD_LOOP,
    CATALOG_TYPE_RANDOM_WIRE,
    CATALOG_TYPE_RINGO,
    CATALOG_TYPE_SLIM_JIM,
    CATALOG_TYPE_SLOPER,
    CATALOG_TYPE_T2FD,
    CATALOG_TYPE_TRAP_DIPOLE,
    CATALOG_TYPE_VERTICAL,
    CATALOG_TYPE_WIRE_DIPOLE,
    CATALOG_TYPE_YAGI,
    AntennaCatalogDialog,
)
from .dialogs.band_analysis_dialog import BandAnalysisDialog
from .dialogs.comparison_dialog import ComparisonDialog
from .dialogs.construction_dialog import ConstructionDialog
from .dialogs.custom_antenna_dialog import CustomAntennaDialog
from .dialogs.design_from_frequency_dialog import DesignFromFrequencyDialog
from .dialogs.doublet_dialog import DoubletDialog
from .dialogs.element_optimization_dialog import (
    ElementOptimizationBand,
    ElementOptimizationDialog,
    ElementOptimizationVariable,
)
from .dialogs.endfed_dialog import EndFedDialog
from .dialogs.fan_dipole_dialog import FanDipoleDialog
from .dialogs.feed_line_dialog import FeedLineDialog
from .dialogs.g5rv_dialog import G5RVDialog
from .dialogs.inverted_v_dialog import InvertedVDialog
from .dialogs.j_pole_dialog import JPoleDialog
from .dialogs.loads_dialog import LoadsDialog
from .dialogs.matching_network_dialog import MatchingNetworkDialog
from .dialogs.measurement_details_dialog import MeasurementDetailsDialog
from .dialogs.moxon_dialog import MoxonDialog
from .dialogs.ocfd_dialog import OCFDDialog
from .dialogs.optimization_dialog import OptimizationDialog
from .dialogs.ringo_dialog import RingoDialog
from .dialogs.synthesis_dialog import SynthesisDialog
from .dialogs.t2fd_dialog import T2FDDialog
from .dialogs.transmission_lines_dialog import TransmissionLinesDialog
from .dialogs.trap_dipole_dialog import TrapDipoleDialog
from .dialogs.vertical_dialog import VerticalDialog
from .dialogs.yagi_dialog import YagiDialog
from .history import ProjectSnapshot, SnapshotCommand, history_action
from .i18n import Language, Translator
from .pattern_resolution import (
    DEFAULT_PATTERN_SNAPSHOT_COUNT,
    DEFAULT_PATTERN_STEP_DEG,
    PATTERN_STEPS_DEG,
    far_field_request,
    pattern_counts,
)
from .report_pdf import write_report_pdf
from .template_identity import catalog_key_for
from .units import UnitSystem, length_from_m, length_unit_key
from .widgets.dipole_form import DipoleForm
from .widgets.endfed_form import EndFedForm
from .widgets.fan_dipole_form import FanDipoleForm
from .widgets.geometry_view import GeometryView, GeometryViewMode
from .widgets.inverted_v_form import InvertedVForm
from .widgets.j_pole_form import JPoleForm
from .widgets.moxon_form import MoxonForm
from .widgets.ocfd_form import OCFDForm
from .widgets.results_view import ResultsView
from .widgets.ringo_form import RingoForm
from .widgets.start_page import StartPage
from .widgets.t2fd_form import T2FDForm
from .widgets.trap_dipole_form import TrapDipoleForm
from .widgets.vertical_form import VerticalForm
from .widgets.yagi_form import YagiForm
from .wizard.dipole_wizard import DipoleWizard
from .workers.band_analysis_worker import BandAnalysisWorker
from .workers.simulation_worker import SimulationWorker

DEFAULT_GENERATED_SWEEP_POINTS = 31
DEFAULT_TWO_BAND_SWEEP_POINTS = 61
YAGI_OPTIMIZATION_MIN_GAP_M = 0.1


class MainWindow(QMainWindow):
    def __init__(
        self,
        repository: ProjectRepository,
        solver: AntennaSolver | None,
        translator: Translator,
        unit_system: UnitSystem = UnitSystem.METRIC,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._repository = repository
        self._solver = solver
        self._translator = translator
        self._unit_system = unit_system

        self._project: Project | None = None
        self._design_id: UUID | None = None
        self._current_path: Path | None = None
        self._dirty = False
        self._form_dirty = False
        self._project_name_updating = False
        self._updating_variants = False
        self._simulating = False
        self._last_result: SimulationResult | None = None
        self._simulation_results: dict[UUID, SimulationResult] = {}
        self._band_analysis_results: dict[UUID, BandAnalysisResult] = {}
        self._band_plans: dict[UUID, BandPlan] = {}
        self._selected_band_ids: dict[UUID, str] = {}
        self._simulation_design_id: UUID | None = None
        self._band_analysis_design_id: UUID | None = None
        self._loads: tuple[LumpedLoad, ...] = ()
        self._transmission_lines: tuple[TransmissionLine, ...] = ()
        self._feed_line: FeedLine | None = None
        self._matching_network: MatchingNetwork | None = None
        self._custom_pattern_step_deg = DEFAULT_PATTERN_STEP_DEG
        self._custom_run_pattern_step_deg: float | None = None
        self._custom_pattern_frequency_count: int | None = None
        self._sweep_custom_initialized = False
        self._custom_last_budget = None
        self._pending_pattern_diagnostic: Diagnostic | None = None
        self._last_status_key = "status.ready"
        self._thread: QThread | None = None
        self._worker: SimulationWorker | BandAnalysisWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._undo_stack = QUndoStack(self)
        self._undo_stack.setUndoLimit(50)
        self._history_restoring = False
        self._history_depth = 0
        self._clean_signature: tuple[object, ...] | None = None
        self._clean_run_ids: frozenset[UUID] = frozenset()

        self._build_actions()
        self._build_ui()
        self._show_empty_state()
        self.retranslate()

    def _build_actions(self) -> None:
        self._undo_action = QAction(self)
        self._undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self._undo_action.triggered.connect(self._undo_project)
        self._redo_action = QAction(self)
        self._redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self._redo_action.triggered.connect(self._redo_project)
        self._undo_stack.indexChanged.connect(lambda _index: self._refresh_history_actions())

        self._new_action = QAction(self)
        self._new_action.setShortcut(QKeySequence.StandardKey.New)
        self._new_action.triggered.connect(lambda: self.new_antenna())
        self._import_nec_action = QAction(self)
        self._import_nec_action.triggered.connect(lambda: self.import_nec_deck())
        self._import_mmana_action = QAction(self)
        self._import_mmana_action.triggered.connect(lambda: self.import_mmana_file())
        self._import_vna_action = QAction(self)
        self._import_vna_action.triggered.connect(lambda: self.import_vna_csv())

        self._open_action = QAction(self)
        self._open_action.setShortcut(QKeySequence.StandardKey.Open)
        self._open_action.triggered.connect(lambda: self.open_project())

        self._save_action = QAction(self)
        self._save_action.setShortcut(QKeySequence.StandardKey.Save)
        self._save_action.triggered.connect(lambda: self.save_project())

        self._save_as_action = QAction(self)
        self._save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self._save_as_action.triggered.connect(lambda: self.save_project_as())

        self._locate_solver_action = QAction(self)
        self._locate_solver_action.triggered.connect(lambda: self.locate_solver())

        self._feed_line_action = QAction(self)
        self._feed_line_action.triggered.connect(lambda: self.configure_feed_line())
        self._matching_network_action = QAction(self)
        self._matching_network_action.triggered.connect(lambda: self.configure_matching_network())

        self._exit_action = QAction(self)
        self._exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self._exit_action.triggered.connect(self.close)

        self._about_action = QAction(self)
        self._about_action.triggered.connect(lambda: self.show_about())

        self._new_variant_action = QAction(self)
        self._new_variant_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        self._new_variant_action.triggered.connect(lambda: self.new_variant())
        self._rename_variant_action = QAction(self)
        self._rename_variant_action.triggered.connect(lambda: self.rename_variant())
        self._delete_variant_action = QAction(self)
        self._delete_variant_action.triggered.connect(lambda: self.delete_variant())
        self._compare_action = QAction(self)
        self._compare_action.triggered.connect(lambda: self.compare_variants())
        self._optimize_action = QAction(self)
        self._optimize_action.triggered.connect(lambda: self.optimize_current_design())
        self._change_template_action = QAction(self)
        self._change_template_action.setShortcut(QKeySequence("Ctrl+Shift+T"))
        self._change_template_action.triggered.connect(lambda: self.change_template())
        self._design_from_frequency_action = QAction(self)
        self._design_from_frequency_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self._design_from_frequency_action.triggered.connect(lambda: self.design_from_frequency())
        self._construction_action = QAction(self)
        self._construction_action.triggered.connect(lambda: self.show_construction_sheet())
        self._loads_action = QAction(self)
        self._loads_action.triggered.connect(lambda: self.edit_loads())
        self._transmission_lines_action = QAction(self)
        self._transmission_lines_action.triggered.connect(lambda: self.edit_transmission_lines())
        self._edit_custom_action = QAction(self)
        self._edit_custom_action.triggered.connect(lambda: self.edit_custom_wires())
        self._convert_custom_action = QAction(self)
        self._convert_custom_action.triggered.connect(lambda: self.convert_to_custom_wires())
        self._export_csv_action = QAction(self)
        self._export_csv_action.triggered.connect(lambda: self.export_csv())
        self._export_pattern_csv_action = QAction(self)
        self._export_pattern_csv_action.triggered.connect(lambda: self.export_pattern_csv())
        self._export_pattern_png_action = QAction(self)
        self._export_pattern_png_action.triggered.connect(lambda: self.export_pattern_png())
        self._export_geometry_png_action = QAction(self)
        self._export_geometry_png_action.triggered.connect(lambda: self.export_geometry_png())
        self._export_geometry_svg_action = QAction(self)
        self._export_geometry_svg_action.triggered.connect(lambda: self.export_geometry_svg())
        self._export_geometry_pdf_action = QAction(self)
        self._export_geometry_pdf_action.triggered.connect(lambda: self.export_geometry_pdf())
        self._export_geometry_dxf_action = QAction(self)
        self._export_geometry_dxf_action.triggered.connect(lambda: self.export_geometry_dxf())
        self._export_html_action = QAction(self)
        self._export_html_action.triggered.connect(lambda: self.export_html_report())
        self._export_pdf_action = QAction(self)
        self._export_pdf_action.triggered.connect(lambda: self.export_pdf_report())
        self._compact_history_action = QAction(self)
        self._compact_history_action.triggered.connect(lambda: self.compact_simulation_history())

        self._simulate_action = QAction(self)
        self._simulate_action.setShortcut(QKeySequence("F5"))
        self._simulate_action.triggered.connect(lambda: self.simulate())

        self._analyze_bands_action = QAction(self)
        self._analyze_bands_action.setShortcut(QKeySequence("Ctrl+Shift+B"))
        self._analyze_bands_action.triggered.connect(lambda: self.analyze_bands())

        self._cancel_action = QAction(self)
        self._cancel_action.setShortcut(QKeySequence("Ctrl+."))
        self._cancel_action.triggered.connect(lambda: self.cancel_simulation())

        self._language_group = QActionGroup(self)
        self._language_group.setExclusive(True)
        self._english_action = QAction(self)
        self._english_action.setCheckable(True)
        self._english_action.triggered.connect(lambda: self._set_language(Language.ENGLISH))
        self._spanish_action = QAction(self)
        self._spanish_action.setCheckable(True)
        self._spanish_action.triggered.connect(lambda: self._set_language(Language.SPANISH))
        self._language_group.addAction(self._english_action)
        self._language_group.addAction(self._spanish_action)
        self._english_action.setChecked(self._translator.language is Language.ENGLISH)
        self._spanish_action.setChecked(self._translator.language is Language.SPANISH)

        self._units_group = QActionGroup(self)
        self._units_group.setExclusive(True)
        self._metric_action = QAction(self)
        self._metric_action.setCheckable(True)
        self._metric_action.triggered.connect(lambda: self._set_unit_system(UnitSystem.METRIC))
        self._imperial_action = QAction(self)
        self._imperial_action.setCheckable(True)
        self._imperial_action.triggered.connect(lambda: self._set_unit_system(UnitSystem.IMPERIAL))
        self._units_group.addAction(self._metric_action)
        self._units_group.addAction(self._imperial_action)
        self._metric_action.setChecked(self._unit_system is UnitSystem.METRIC)
        self._imperial_action.setChecked(self._unit_system is UnitSystem.IMPERIAL)

        style = self.style()
        self._new_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self._open_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        self._save_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self._simulate_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self._cancel_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_BrowserStop))
        self._locate_solver_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))

    def _build_ui(self) -> None:
        self.setMinimumSize(1_100, 800)

        self._form = DipoleForm(self._translator, self._unit_system)
        self._form.changed.connect(self._on_form_changed)
        self._form.change_template_requested.connect(lambda: self.change_template())
        self._form_scroll = QScrollArea(self)
        form_scroll = self._form_scroll
        form_scroll.setWidgetResizable(True)
        form_scroll.setWidget(self._form)
        form_scroll.setMinimumWidth(340)
        form_scroll.setMaximumWidth(480)
        self._ocfd_form = OCFDForm(self._translator, self._unit_system, parent=self)
        self._ocfd_form.changed.connect(self._on_form_changed)
        self._ocfd_scroll = QScrollArea(self)
        self._ocfd_scroll.setWidgetResizable(True)
        self._ocfd_scroll.setWidget(self._ocfd_form)
        self._ocfd_scroll.setMinimumWidth(340)
        self._ocfd_scroll.setMaximumWidth(480)

        self._vertical_form = VerticalForm(self._translator, self._unit_system, parent=self)
        self._vertical_form.changed.connect(self._on_form_changed)
        self._vertical_scroll = QScrollArea(self)
        self._vertical_scroll.setWidgetResizable(True)
        self._vertical_scroll.setWidget(self._vertical_form)
        self._vertical_scroll.setMinimumWidth(340)
        self._vertical_scroll.setMaximumWidth(480)

        self._inverted_v_form = InvertedVForm(self._translator, self._unit_system, parent=self)
        self._inverted_v_form.changed.connect(self._on_form_changed)
        self._inverted_v_scroll = QScrollArea(self)
        self._inverted_v_scroll.setWidgetResizable(True)
        self._inverted_v_scroll.setWidget(self._inverted_v_form)
        self._inverted_v_scroll.setMinimumWidth(340)
        self._inverted_v_scroll.setMaximumWidth(480)

        self._yagi_form = YagiForm(self._translator, self._unit_system, parent=self)
        self._yagi_form.changed.connect(self._on_form_changed)
        self._yagi_scroll = QScrollArea(self)
        self._yagi_scroll.setWidgetResizable(True)
        self._yagi_scroll.setWidget(self._yagi_form)
        self._yagi_scroll.setMinimumWidth(340)
        self._yagi_scroll.setMaximumWidth(520)

        self._moxon_form = MoxonForm(self._translator, self._unit_system, parent=self)
        self._moxon_form.changed.connect(self._on_form_changed)
        self._moxon_scroll = QScrollArea(self)
        self._moxon_scroll.setWidgetResizable(True)
        self._moxon_scroll.setWidget(self._moxon_form)
        self._moxon_scroll.setMinimumWidth(340)
        self._moxon_scroll.setMaximumWidth(480)

        self._fan_dipole_form = FanDipoleForm(self._translator, self._unit_system, parent=self)
        self._fan_dipole_form.changed.connect(self._on_form_changed)
        self._fan_dipole_scroll = QScrollArea(self)
        self._fan_dipole_scroll.setWidgetResizable(True)
        self._fan_dipole_scroll.setWidget(self._fan_dipole_form)
        self._fan_dipole_scroll.setMinimumWidth(340)
        self._fan_dipole_scroll.setMaximumWidth(480)

        self._trap_dipole_form = TrapDipoleForm(self._translator, self._unit_system, parent=self)
        self._trap_dipole_form.changed.connect(self._on_form_changed)
        self._trap_dipole_scroll = QScrollArea(self)
        self._trap_dipole_scroll.setWidgetResizable(True)
        self._trap_dipole_scroll.setWidget(self._trap_dipole_form)
        self._trap_dipole_scroll.setMinimumWidth(340)
        self._trap_dipole_scroll.setMaximumWidth(500)

        self._t2fd_form = T2FDForm(self._translator, self._unit_system, parent=self)
        self._t2fd_form.changed.connect(self._on_form_changed)
        self._t2fd_scroll = QScrollArea(self)
        self._t2fd_scroll.setWidgetResizable(True)
        self._t2fd_scroll.setWidget(self._t2fd_form)
        self._t2fd_scroll.setMinimumWidth(340)
        self._t2fd_scroll.setMaximumWidth(500)

        self._endfed_form = EndFedForm(self._translator, self._unit_system, parent=self)
        self._endfed_form.changed.connect(self._on_form_changed)
        self._endfed_scroll = QScrollArea(self)
        self._endfed_scroll.setWidgetResizable(True)
        self._endfed_scroll.setWidget(self._endfed_form)
        self._endfed_scroll.setMinimumWidth(340)
        self._endfed_scroll.setMaximumWidth(480)

        self._j_pole_form = JPoleForm(self._translator, self._unit_system, parent=self)
        self._j_pole_form.changed.connect(self._on_form_changed)
        self._j_pole_scroll = QScrollArea(self)
        self._j_pole_scroll.setWidgetResizable(True)
        self._j_pole_scroll.setWidget(self._j_pole_form)
        self._j_pole_scroll.setMinimumWidth(340)
        self._j_pole_scroll.setMaximumWidth(480)

        self._ringo_form = RingoForm(self._translator, self._unit_system, parent=self)
        self._ringo_form.changed.connect(self._on_form_changed)
        self._ringo_scroll = QScrollArea(self)
        self._ringo_scroll.setWidgetResizable(True)
        self._ringo_scroll.setWidget(self._ringo_form)
        self._ringo_scroll.setMinimumWidth(340)
        self._ringo_scroll.setMaximumWidth(480)

        self._sweep_group = QGroupBox(self)
        self._sweep_group.setTitle(self._translator.t("sweep.group_title"))
        self._sweep_mode_label = QLabel(self._sweep_group)
        self._sweep_mode = QComboBox(self._sweep_group)
        self._sweep_mode.addItem(self._translator.t("sweep.auto"), None)
        self._sweep_mode.addItem(self._translator.t("sweep.custom"), "custom")
        self._sweep_mode.currentIndexChanged.connect(self._on_sweep_mode_changed)
        self._sweep_start_label = QLabel(self._sweep_group)
        self._sweep_start = QDoubleSpinBox(self._sweep_group)
        self._sweep_start.setRange(0.1, 100_000.0)
        self._sweep_start.setDecimals(6)
        self._sweep_start.setSuffix(" MHz")
        self._sweep_start.setValue(7.0)
        self._sweep_stop_label = QLabel(self._sweep_group)
        self._sweep_stop = QDoubleSpinBox(self._sweep_group)
        self._sweep_stop.setRange(0.1, 100_000.0)
        self._sweep_stop.setDecimals(6)
        self._sweep_stop.setSuffix(" MHz")
        self._sweep_stop.setValue(7.3)
        self._sweep_points_label = QLabel(self._sweep_group)
        self._sweep_points = QSpinBox(self._sweep_group)
        self._sweep_points.setRange(2, 10_000)
        self._sweep_points.setValue(DEFAULT_GENERATED_SWEEP_POINTS)
        sweep_layout = QFormLayout(self._sweep_group)
        sweep_layout.addRow(self._sweep_mode_label, self._sweep_mode)
        sweep_layout.addRow(self._sweep_start_label, self._sweep_start)
        sweep_layout.addRow(self._sweep_stop_label, self._sweep_stop)
        sweep_layout.addRow(self._sweep_points_label, self._sweep_points)
        self._sweep_hint = QLabel(self._sweep_group)
        self._sweep_hint.setWordWrap(True)
        self._sweep_hint.setStyleSheet("font-style: italic;")
        sweep_layout.addRow(self._sweep_hint)
        self._update_sweep_controls()

        self._pattern_group = QGroupBox(self)
        self._pattern_group.setTitle(self._translator.t("pattern.settings_title"))
        self._custom_pattern_label = QLabel(
            self._translator.t("custom.pattern_resolution"),
            self._pattern_group,
        )
        self._custom_pattern_resolution = QComboBox(self._pattern_group)
        self._custom_pattern_resolution.addItem(self._translator.t("custom.pattern_auto"), None)
        for step in PATTERN_STEPS_DEG:
            self._custom_pattern_resolution.addItem(f"{step:g}°", step)
        self._custom_pattern_resolution.setCurrentIndex(
            self._custom_pattern_resolution.findData(self._custom_run_pattern_step_deg)
        )
        self._custom_pattern_resolution.currentIndexChanged.connect(self._custom_pattern_changed)
        self._custom_pattern_frequency_label = QLabel(
            self._translator.t("custom.pattern_frequencies"),
            self._pattern_group,
        )
        self._custom_pattern_frequency_mode = QComboBox(self._pattern_group)
        self._custom_pattern_frequency_mode.addItem(
            self._translator.t("custom.pattern_frequencies_auto"),
            None,
        )
        for count in (5, 9, 13, 17, 21):
            self._custom_pattern_frequency_mode.addItem(
                self._translator.t("custom.pattern_frequencies_option", count=count),
                count,
            )
        self._custom_pattern_frequency_mode.setCurrentIndex(
            self._custom_pattern_frequency_mode.findData(self._custom_pattern_frequency_count)
        )
        self._custom_pattern_frequency_mode.currentIndexChanged.connect(
            self._custom_pattern_frequency_changed
        )
        self._custom_pattern_status = QLabel(self._pattern_group)
        self._custom_pattern_status.setWordWrap(True)
        pattern_layout = QFormLayout(self._pattern_group)
        pattern_layout.addRow(
            self._custom_pattern_label,
            self._custom_pattern_resolution,
        )
        pattern_layout.addRow(
            self._custom_pattern_frequency_label,
            self._custom_pattern_frequency_mode,
        )
        pattern_layout.addRow(self._custom_pattern_status)

        self._band_group = QGroupBox(self)
        self._band_group.setTitle(self._translator.t("band.group_title"))
        self._band_plan_label = QLabel(self._band_group)
        self._band_plan_label.setWordWrap(True)
        self._analyze_bands_button = QPushButton(self._band_group)
        self._analyze_bands_button.clicked.connect(lambda: self.analyze_bands())
        band_layout = QHBoxLayout(self._band_group)
        band_layout.addWidget(self._band_plan_label, 1)
        band_layout.addWidget(self._analyze_bands_button)

        self._advanced_toggle = QToolButton(self)
        self._advanced_toggle.setCheckable(True)
        self._advanced_toggle.setChecked(False)
        self._advanced_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self._advanced_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._advanced_toggle.toggled.connect(self._on_advanced_toggled)
        self._advanced_body = QWidget(self)
        advanced_layout = QVBoxLayout(self._advanced_body)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        advanced_layout.addWidget(self._sweep_group)
        advanced_layout.addWidget(self._pattern_group)
        advanced_layout.addWidget(self._band_group)
        self._advanced_body.setVisible(False)

        self._custom_panel = QWidget(self)
        custom_layout = QVBoxLayout(self._custom_panel)
        self._custom_title = QLabel(self._custom_panel)
        self._custom_title.setStyleSheet("font-weight: bold;")
        self._custom_summary = QLabel(self._custom_panel)
        self._custom_summary.setWordWrap(True)
        self._custom_family = QLabel(self._custom_panel)
        self._custom_family.setWordWrap(True)
        self._custom_generator = QLabel(self._custom_panel)
        self._custom_generator.setWordWrap(True)
        self._custom_generator.setStyleSheet("font-style: italic;")
        self._custom_edit = QPushButton(self._custom_panel)
        self._custom_edit.clicked.connect(lambda: self.edit_custom_wires())
        self._custom_generator_edit = QPushButton(self._custom_panel)
        self._custom_generator_edit.clicked.connect(lambda: self.edit_generator())
        self._custom_sweep_group = QGroupBox(self._custom_panel)
        self._custom_sweep = QCheckBox(self._custom_sweep_group)
        self._custom_sweep.setChecked(True)
        self._custom_sweep.toggled.connect(self._update_custom_sweep_controls)
        self._custom_sweep_start = QDoubleSpinBox(self._custom_sweep_group)
        self._custom_sweep_stop = QDoubleSpinBox(self._custom_sweep_group)
        for spin in (self._custom_sweep_start, self._custom_sweep_stop):
            spin.setRange(0.1, 100_000.0)
            spin.setDecimals(6)
            spin.setSuffix(" MHz")
        self._custom_sweep_points = QSpinBox(self._custom_sweep_group)
        self._custom_sweep_points.setRange(2, 10_000)
        self._custom_sweep_points.setValue(100)
        self._custom_sweep_center_hz: float | None = None
        custom_sweep_layout = QFormLayout(self._custom_sweep_group)
        custom_sweep_layout.addRow(self._custom_sweep)
        custom_sweep_layout.addRow(
            self._translator.t("field.sweep_start"), self._custom_sweep_start
        )
        custom_sweep_layout.addRow(self._translator.t("field.sweep_stop"), self._custom_sweep_stop)
        custom_sweep_layout.addRow(
            self._translator.t("field.sweep_points"), self._custom_sweep_points
        )
        custom_layout.addWidget(self._custom_title)
        custom_layout.addWidget(self._custom_family)
        custom_layout.addWidget(self._custom_generator)
        custom_layout.addWidget(self._custom_summary)
        custom_layout.addWidget(self._custom_generator_edit)
        custom_layout.addWidget(self._custom_edit)
        custom_layout.addWidget(self._custom_sweep_group)
        custom_layout.addStretch(1)
        self._design_stack = QStackedWidget(self)
        self._design_stack.addWidget(form_scroll)
        self._design_stack.addWidget(self._ocfd_scroll)
        self._design_stack.addWidget(self._vertical_scroll)
        self._design_stack.addWidget(self._inverted_v_scroll)
        self._design_stack.addWidget(self._yagi_scroll)
        self._design_stack.addWidget(self._moxon_scroll)
        self._design_stack.addWidget(self._fan_dipole_scroll)
        self._design_stack.addWidget(self._trap_dipole_scroll)
        self._design_stack.addWidget(self._t2fd_scroll)
        self._design_stack.addWidget(self._endfed_scroll)
        self._design_stack.addWidget(self._j_pole_scroll)
        self._design_stack.addWidget(self._ringo_scroll)
        self._design_stack.addWidget(self._custom_panel)
        self._apply_button = QPushButton(self)
        self._apply_button.clicked.connect(lambda: self.apply_design())
        self._estimate_button = QPushButton(self)
        self._estimate_button.clicked.connect(lambda: self.design_from_frequency())
        self._optimize_button = QPushButton(self)
        self._optimize_button.clicked.connect(lambda: self.optimize_current_design())
        self._provenance_label = QLabel(self)
        self._provenance_label.setWordWrap(True)
        self._provenance_label.setVisible(False)
        design_panel = QWidget(self)
        design_layout = QVBoxLayout(design_panel)
        design_layout.setContentsMargins(0, 0, 0, 0)
        design_actions = QHBoxLayout()
        design_actions.addWidget(self._apply_button)
        design_actions.addWidget(self._estimate_button)
        design_actions.addWidget(self._optimize_button)
        design_layout.addLayout(design_actions)
        design_layout.addWidget(self._design_stack, 1)
        design_layout.addWidget(self._provenance_label)
        design_layout.addWidget(self._advanced_toggle)
        design_layout.addWidget(self._advanced_body)

        self._geometry = GeometryView(self._translator, self._unit_system)
        self._geometry.setMinimumHeight(300)
        self._results = ResultsView(self._translator)
        self._results.measurement_edit_requested.connect(self.edit_measurement)
        self._results.measurement_delete_requested.connect(self.delete_measurement)
        self._results.band_selected.connect(self._on_band_selected)

        geometry_container = QWidget(self)
        geometry_layout = QVBoxLayout(geometry_container)
        geometry_layout.setContentsMargins(0, 0, 0, 0)
        geometry_controls = QHBoxLayout()
        self._view_label = QLabel(self)
        self._view_combo = QComboBox(self)
        self._view_combo.addItem("", GeometryViewMode.ELEVATION.value)
        self._view_combo.addItem("", GeometryViewMode.PLAN.value)
        self._view_combo.addItem("", GeometryViewMode.THREE_D.value)
        self._height_label = QLabel(self)
        self._height_combo = QComboBox(self)
        for factor in (1.0, 1.5, 2.0, 3.0):
            self._height_combo.addItem(f"{factor:g}x", factor)
        self._zoom_label = QLabel(self)
        self._zoom_combo = QComboBox(self)
        for factor in (0.5, 1.0, 2.0, 4.0, 8.0):
            self._zoom_combo.addItem(f"{factor:g}x", factor)
        self._zoom_combo.setCurrentIndex(1)
        self._zoom_combo.setToolTip(self._translator.t("geometry.zoom_hint"))
        geometry_controls.addStretch(1)
        geometry_controls.addWidget(self._view_label)
        geometry_controls.addWidget(self._view_combo)
        geometry_controls.addWidget(self._height_label)
        geometry_controls.addWidget(self._height_combo)
        geometry_controls.addWidget(self._zoom_label)
        geometry_controls.addWidget(self._zoom_combo)
        geometry_layout.addLayout(geometry_controls)
        geometry_layout.addWidget(self._geometry, 1)
        geometry_container.setMinimumHeight(330)
        self._view_combo.currentIndexChanged.connect(self._on_view_mode_changed)
        self._height_combo.currentIndexChanged.connect(self._on_height_scale_changed)
        self._zoom_combo.currentIndexChanged.connect(self._on_zoom_changed)
        self._geometry.zoom_changed.connect(self._sync_zoom_combo)

        self._right_splitter = QSplitter(Qt.Orientation.Vertical, self)
        right_splitter = self._right_splitter
        right_splitter.addWidget(geometry_container)
        right_splitter.addWidget(self._results)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 2)
        right_splitter.setSizes([350, 650])

        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_splitter.addWidget(design_panel)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([380, 900])

        self._start_page = StartPage(self._translator, self)
        self._start_page.new_requested.connect(lambda: self.new_antenna())
        self._start_page.open_requested.connect(lambda: self.open_project())
        self._editor_panel = main_splitter
        self._main_stack = QStackedWidget(self)
        self._main_stack.addWidget(self._start_page)
        self._main_stack.addWidget(self._editor_panel)
        self.setCentralWidget(self._main_stack)

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toolbar = toolbar
        self.addToolBar(toolbar)
        self._project_name_label = QLabel(self)
        toolbar.addWidget(self._project_name_label)
        self._project_name = QLineEdit(self)
        self._project_name.setMinimumWidth(220)
        self._project_name.textChanged.connect(self._project_name_changed)
        toolbar.addWidget(self._project_name)
        toolbar.addSeparator()
        self._variant_label = QLabel(self)
        toolbar.addWidget(self._variant_label)
        self._variant_combo = QComboBox(self)
        self._variant_combo.setMinimumWidth(170)
        self._variant_combo.currentIndexChanged.connect(self._on_variant_changed)
        toolbar.addWidget(self._variant_combo)
        toolbar.addAction(self._new_variant_action)
        toolbar.addSeparator()
        toolbar.addAction(self._undo_action)
        toolbar.addAction(self._redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self._simulate_action)
        toolbar.addAction(self._cancel_action)

        self._file_menu = self.menuBar().addMenu("")
        self._file_menu.addAction(self._new_action)
        self._file_menu.addAction(self._open_action)
        self._file_menu.addAction(self._save_action)
        self._file_menu.addAction(self._save_as_action)
        self._file_menu.addSeparator()
        self._import_menu = self._file_menu.addMenu("")
        self._import_menu.addAction(self._import_nec_action)
        self._import_menu.addAction(self._import_mmana_action)
        self._import_menu.addSeparator()
        self._import_menu.addAction(self._import_vna_action)
        self._export_menu = self._file_menu.addMenu("")
        self._export_menu.addAction(self._export_csv_action)
        self._export_menu.addAction(self._export_pattern_csv_action)
        self._export_menu.addSeparator()
        self._export_menu.addAction(self._export_pattern_png_action)
        self._export_menu.addAction(self._export_geometry_png_action)
        self._export_menu.addAction(self._export_geometry_svg_action)
        self._export_menu.addAction(self._export_geometry_pdf_action)
        self._export_menu.addAction(self._export_geometry_dxf_action)
        self._export_menu.addSeparator()
        self._export_menu.addAction(self._export_html_action)
        self._export_menu.addAction(self._export_pdf_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._exit_action)

        self._edit_menu = self.menuBar().addMenu("")
        self._edit_menu.addAction(self._undo_action)
        self._edit_menu.addAction(self._redo_action)

        self._design_menu = self.menuBar().addMenu("")
        self._variants_menu = self._design_menu.addMenu("")
        self._variants_menu.addAction(self._new_variant_action)
        self._variants_menu.addAction(self._rename_variant_action)
        self._variants_menu.addAction(self._delete_variant_action)
        self._variants_menu.addSeparator()
        self._variants_menu.addAction(self._compare_action)
        self._design_menu.addSeparator()
        self._design_menu.addAction(self._change_template_action)
        self._design_menu.addAction(self._design_from_frequency_action)
        self._design_menu.addAction(self._optimize_action)
        self._design_menu.addSeparator()
        self._design_menu.addAction(self._construction_action)
        self._design_menu.addAction(self._loads_action)
        self._design_menu.addAction(self._transmission_lines_action)
        self._custom_menu = self._design_menu.addMenu("")
        self._custom_menu.addAction(self._edit_custom_action)
        self._custom_menu.addAction(self._convert_custom_action)

        self._simulation_menu = self.menuBar().addMenu("")
        self._simulation_menu.addAction(self._simulate_action)
        self._simulation_menu.addAction(self._analyze_bands_action)
        self._simulation_menu.addAction(self._cancel_action)
        self._simulation_menu.addSeparator()
        self._simulation_menu.addAction(self._feed_line_action)
        self._simulation_menu.addAction(self._matching_network_action)

        self._tools_menu = self.menuBar().addMenu("")
        self._tools_menu.addAction(self._locate_solver_action)
        self._tools_menu.addAction(self._compact_history_action)
        self._tools_menu.addSeparator()
        self._language_menu = self._tools_menu.addMenu("")
        self._language_menu.addAction(self._english_action)
        self._language_menu.addAction(self._spanish_action)
        self._units_menu = self._tools_menu.addMenu("")
        self._units_menu.addAction(self._metric_action)
        self._units_menu.addAction(self._imperial_action)

        self._help_menu = self.menuBar().addMenu("")
        self._help_menu.addAction(self._about_action)

        self._status_label = QLabel(self)
        self._solver_label = QLabel(self)
        self.statusBar().addWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._solver_label)

    def _on_advanced_toggled(self, expanded: bool) -> None:
        self._advanced_body.setVisible(expanded)
        self._advanced_toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )

    def _on_sweep_mode_changed(self, _index: int) -> None:
        custom = self._sweep_mode.currentData() == "custom"
        if custom and not self._sweep_custom_initialized:
            self._initialize_sweep_from_template()
            self._sweep_custom_initialized = True
        self._update_sweep_controls()

    def _update_sweep_controls(self) -> None:
        custom = self._sweep_mode.currentData() == "custom"
        for widget in (self._sweep_start, self._sweep_stop, self._sweep_points):
            widget.setEnabled(custom)

    def _initialize_sweep_from_template(self) -> None:
        self._refresh_auto_sweep_display(force=True)

    def _refresh_auto_sweep_display(self, *, force: bool = False) -> None:
        if not force and self._sweep_mode.currentData() == "custom":
            return
        if self._project is None or self._design_id is None:
            return
        try:
            design = self._project.design_by_id(self._design_id)
            spec = self._base_simulation_spec(design)
        except Exception:
            return
        plan = spec.frequency_plan
        self._sweep_start.setValue(plan.start_hz / 1_000_000.0)
        self._sweep_stop.setValue(plan.stop_hz / 1_000_000.0)
        self._sweep_points.setValue(plan.count)

    def retranslate(self) -> None:
        self._update_title()
        self._new_action.setText(self._translator.t("action.new"))
        self._import_nec_action.setText(self._translator.t("action.import_nec"))
        self._import_mmana_action.setText(self._translator.t("action.import_mmana"))
        self._import_vna_action.setText(self._translator.t("action.import_vna"))
        self._open_action.setText(self._translator.t("action.open"))
        self._save_action.setText(self._translator.t("action.save"))
        self._save_as_action.setText(self._translator.t("action.save_as"))
        self._locate_solver_action.setText(self._translator.t("action.locate_solver"))
        self._feed_line_action.setText(self._translator.t("action.feed_line"))
        self._matching_network_action.setText(self._translator.t("action.matching_network"))
        self._exit_action.setText(self._translator.t("action.exit"))
        self._about_action.setText(self._translator.t("action.about"))
        self._new_variant_action.setText(self._translator.t("action.new_variant"))
        self._rename_variant_action.setText(self._translator.t("action.rename_variant"))
        self._delete_variant_action.setText(self._translator.t("action.delete_variant"))
        self._compare_action.setText(self._translator.t("action.compare"))
        self._optimize_action.setText(self._translator.t("action.optimize"))
        self._change_template_action.setText(self._translator.t("action.change_template"))
        self._design_from_frequency_action.setText(
            self._translator.t("action.design_from_frequency")
        )
        self._apply_button.setText(self._translator.t("action.apply"))
        self._apply_button.setToolTip(self._translator.t("action.apply.tooltip"))
        self._optimize_button.setText(self._translator.t("action.optimize"))
        self._construction_action.setText(self._translator.t("action.construction"))
        self._loads_action.setText(self._translator.t("action.loads"))
        self._transmission_lines_action.setText(self._translator.t("action.transmission_lines"))
        self._edit_custom_action.setText(self._translator.t("action.edit_custom"))
        self._convert_custom_action.setText(self._translator.t("action.convert_custom"))
        self._custom_title.setText(self._translator.t("custom.panel_title"))
        self._custom_edit.setText(self._translator.t("action.edit_custom"))
        self._estimate_button.setText(self._translator.t("action.design_from_frequency"))
        self._custom_generator_edit.setText(self._translator.t("action.edit_generator"))
        self._custom_sweep_group.setTitle(self._translator.t("field.sweep"))
        self._custom_sweep.setText(self._translator.t("field.sweep_enabled"))
        self._sweep_group.setTitle(self._translator.t("sweep.group_title"))
        self._sweep_mode_label.setText(self._translator.t("sweep.mode"))
        self._sweep_mode.setItemText(0, self._translator.t("sweep.auto"))
        self._sweep_mode.setItemText(1, self._translator.t("sweep.custom"))
        self._sweep_start_label.setText(self._translator.t("field.sweep_start"))
        self._sweep_stop_label.setText(self._translator.t("field.sweep_stop"))
        self._sweep_points_label.setText(self._translator.t("field.sweep_points"))
        self._sweep_hint.setText(self._translator.t("sweep.hint"))
        self._pattern_group.setTitle(self._translator.t("pattern.settings_title"))
        self._band_group.setTitle(self._translator.t("band.group_title"))
        self._advanced_toggle.setText(self._translator.t("advanced.title"))
        self._analyze_bands_button.setText(self._translator.t("band.analyze"))
        self._analyze_bands_action.setText(self._translator.t("band.analyze"))
        self._update_band_plan_label()
        self._custom_pattern_label.setText(self._translator.t("custom.pattern_resolution"))
        self._custom_pattern_resolution.setItemText(
            0,
            self._translator.t("custom.pattern_auto"),
        )
        self._custom_pattern_frequency_label.setText(
            self._translator.t("custom.pattern_frequencies")
        )
        self._custom_pattern_frequency_mode.setItemText(
            0,
            self._translator.t("custom.pattern_frequencies_auto"),
        )
        for index, count in enumerate((5, 9, 13), start=1):
            self._custom_pattern_frequency_mode.setItemText(
                index,
                self._translator.t("custom.pattern_frequencies_option", count=count),
            )
        self._update_custom_pattern_status()
        self._export_csv_action.setText(self._translator.t("action.export_csv"))
        self._export_pattern_csv_action.setText(self._translator.t("action.export_pattern_csv"))
        self._export_pattern_png_action.setText(self._translator.t("action.export_pattern_png"))
        self._export_geometry_png_action.setText(self._translator.t("action.export_geometry_png"))
        self._export_geometry_svg_action.setText(self._translator.t("action.export_geometry_svg"))
        self._export_geometry_pdf_action.setText(self._translator.t("action.export_geometry_pdf"))
        self._export_geometry_dxf_action.setText(self._translator.t("action.export_geometry_dxf"))
        self._export_html_action.setText(self._translator.t("action.export_html"))
        self._export_pdf_action.setText(self._translator.t("action.export_pdf"))
        self._compact_history_action.setText(self._translator.t("action.compact_history"))
        self._simulate_action.setText(self._translator.t("action.simulate"))
        self._simulate_action.setToolTip(self._translator.t("action.simulate.tooltip"))
        self._cancel_action.setText(self._translator.t("action.cancel"))
        self._english_action.setText(self._translator.t("action.english"))
        self._spanish_action.setText(self._translator.t("action.spanish"))
        self._metric_action.setText(self._translator.t("units.metric"))
        self._imperial_action.setText(self._translator.t("units.imperial"))
        self._edit_menu.setTitle(self._translator.t("menu.edit"))
        self._refresh_history_actions()
        self._file_menu.setTitle(self._translator.t("menu.file"))
        self._import_menu.setTitle(self._translator.t("menu.import"))
        self._export_menu.setTitle(self._translator.t("menu.export"))
        self._design_menu.setTitle(self._translator.t("menu.design"))
        self._variants_menu.setTitle(self._translator.t("menu.variants"))
        self._custom_menu.setTitle(self._translator.t("menu.custom_wires"))
        self._simulation_menu.setTitle(self._translator.t("menu.simulation"))
        self._tools_menu.setTitle(self._translator.t("menu.tools"))
        self._language_menu.setTitle(self._translator.t("menu.language"))
        self._units_menu.setTitle(self._translator.t("menu.units"))
        self._help_menu.setTitle(self._translator.t("menu.help"))
        self._project_name_label.setText(self._translator.t("field.project_name"))
        self._variant_label.setText(self._translator.t("variant.label"))
        self._view_label.setText(self._translator.t("geometry.view"))
        self._view_combo.setItemText(0, self._translator.t("geometry.view_elevation"))
        self._view_combo.setItemText(1, self._translator.t("geometry.view_plan"))
        self._view_combo.setItemText(2, self._translator.t("geometry.view_3d"))
        self._height_label.setText(self._translator.t("geometry.vertical_scale"))
        self._zoom_label.setText(self._translator.t("geometry.zoom"))
        self._zoom_combo.setToolTip(self._translator.t("geometry.zoom_hint"))
        self._start_page.retranslate()
        self._form.retranslate()
        self._geometry.retranslate()
        self._results.retranslate()
        if self._project is not None and self._design_id is not None:
            design = self._project.design_by_id(self._design_id)
            if isinstance(design.parameters, CustomAntennaParameters):
                self._update_custom_panel(design)
        self._update_solver_status()
        self._update_status_text()
        self._update_actions()

    def _update_title(self) -> None:
        if self._project is None:
            self.setWindowTitle(self._translator.t("app.title"))
            return
        marker = " *" if self._dirty else ""
        self.setWindowTitle(f"{self._project.name}{marker} — AntennaDesk")

    def _update_provenance_label(self, design: DesignVariant | None) -> None:
        provenance = design.provenance if design is not None else None
        if provenance is None:
            self._provenance_label.clear()
            self._provenance_label.setVisible(False)
            return
        tolerance = length_from_m(provenance.tolerance_m, self._unit_system)
        unit = self._translator.t(length_unit_key(self._unit_system))
        self._provenance_label.setText(
            self._translator.t(
                "design.provenance",
                method=provenance.method_id,
                confidence=provenance.confidence,
                tolerance=f"{tolerance:.3f} {unit}",
            )
        )
        self._provenance_label.setVisible(True)

    def _latest_band_analysis_for(
        self,
        project: Project,
        design_id: UUID,
    ) -> BandAnalysisResult | None:
        analysis = project.latest_band_analysis(design_id)
        if analysis is None:
            return None
        latest_single = project.latest_simulation_run(design_id)
        if latest_single is not None and latest_single.created_at > analysis.created_at:
            return None
        return analysis

    def _remember_band_plan(self, analysis: BandAnalysisResult) -> None:
        selections = tuple(
            BandSelection(
                band.band,
                max(2, band.result.spec.frequency_plan.count),
            )
            for band in analysis.bands
        )
        if selections:
            self._band_plans[analysis.design_id] = BandPlan(selections)

    def _default_band_default(self, design: DesignVariant) -> BandDefault:
        return default_band_plan(
            design.parameters,
            high_impedance_feed_line=(
                self._feed_line is not None
                and self._feed_line.characteristic_impedance_ohm >= 300.0
            ),
        )

    def _default_band_for(self, design: DesignVariant) -> BandPlan:
        return self._default_band_default(design).plan

    def _current_band_plan(self, design: DesignVariant) -> BandPlan:
        plan = self._band_plans.get(design.id)
        if plan is not None:
            return plan
        return self._default_band_for(design)

    def _update_band_plan_label(self) -> None:
        if self._project is None or self._design_id is None:
            self._band_plan_label.setText("")
            return
        try:
            design = self._project.design_by_id(self._design_id)
        except KeyError:
            self._band_plan_label.setText("")
            return
        plan = self._current_band_plan(design)
        if plan:
            bands = ", ".join(selection.band.name for selection in plan.selections)
            self._band_plan_label.setText(self._translator.t("band.selected", bands=bands))
        else:
            self._band_plan_label.setText(self._translator.t("band.no_selection"))

    def _invalidate_design_result(self, design_id: UUID | None) -> None:
        if design_id is None:
            return
        self._simulation_results.pop(design_id, None)
        self._band_analysis_results.pop(design_id, None)
        self._selected_band_ids.pop(design_id, None)
        if design_id == self._design_id and hasattr(self, "_results"):
            self._results.set_band_analysis(None)

    def _update_status_text(self) -> None:
        key = "status.simulating" if self._simulating else self._last_status_key
        self._status_label.setText(self._translator.t(key))

    def _result_status_key(self, status: SimulationStatus) -> str:
        return {
            SimulationStatus.COMPLETED: "status.completed",
            SimulationStatus.CANCELLED: "status.cancelled",
            SimulationStatus.PARTIAL: "status.partial",
            SimulationStatus.ERROR: "status.error",
        }[status]

    def _update_solver_status(self) -> None:
        if self._solver is None:
            self._solver_label.setText(self._translator.t("status.no_solver"))
            self._solver_label.setToolTip(self._translator.t("status.solver_missing"))
            return
        try:
            metadata = self._solver.version()
        except Exception:
            self._solver_label.setText(self._translator.t("status.no_solver"))
            self._solver_label.setToolTip(self._translator.t("status.solver_missing"))
            return
        self._solver_label.setText(
            self._translator.t(
                "status.solver",
                name=metadata.name,
                version=metadata.version,
            )
        )
        self._solver_label.setToolTip(metadata.executable or "")

    def _update_actions(self) -> None:
        idle = not self._simulating
        has_project = self._project is not None and self._design_id is not None
        has_designs = self._project is not None and len(self._project.designs) > 0
        has_multiple = self._project is not None and len(self._project.designs) > 1
        has_result = self._design_id is not None and self._design_id in self._simulation_results
        self._new_action.setEnabled(idle)
        self._apply_button.setEnabled(idle and has_project)
        self._open_action.setEnabled(idle)
        self._save_action.setEnabled(idle and has_project)
        self._save_as_action.setEnabled(idle and has_project)
        self._locate_solver_action.setEnabled(idle)
        self._feed_line_action.setEnabled(idle)
        self._matching_network_action.setEnabled(idle)
        self._exit_action.setEnabled(idle)
        self._new_variant_action.setEnabled(idle and has_designs)
        self._rename_variant_action.setEnabled(idle and has_designs)
        self._delete_variant_action.setEnabled(idle and has_multiple)
        self._compare_action.setEnabled(idle and has_multiple)
        design = None
        parameters = None
        if self._project is not None and self._design_id is not None:
            design = self._project.design_by_id(self._design_id)
            parameters = design.parameters
        self._update_provenance_label(design)
        is_custom = isinstance(parameters, CustomAntennaParameters)
        estimate_supported = parameters is not None and supports_estimation(parameters)
        self._change_template_action.setEnabled(idle and has_project)
        self._design_from_frequency_action.setEnabled(idle and has_project and estimate_supported)
        self._estimate_button.setEnabled(idle and has_project and estimate_supported)
        estimate_hint = ""
        if parameters is not None and not estimate_supported:
            estimate_hint = self._estimate_unavailable_message(parameters)
        self._estimate_button.setToolTip(estimate_hint)
        self._design_from_frequency_action.setToolTip(estimate_hint)
        band_enabled = idle and has_project and self._solver is not None
        self._analyze_bands_action.setEnabled(band_enabled)
        self._analyze_bands_button.setEnabled(band_enabled)
        optimize_enabled = idle and has_project and not is_custom and self._solver is not None
        self._optimize_action.setEnabled(optimize_enabled)
        self._optimize_button.setEnabled(optimize_enabled)
        self._loads_action.setEnabled(idle and has_project)
        self._transmission_lines_action.setEnabled(idle and has_project)
        self._edit_custom_action.setEnabled(idle and has_project and is_custom)
        self._convert_custom_action.setEnabled(idle and has_project and not is_custom)
        self._import_nec_action.setEnabled(idle)
        self._import_mmana_action.setEnabled(idle)
        self._import_vna_action.setEnabled(idle and has_project)
        self._export_csv_action.setEnabled(idle and has_result)
        self._export_pattern_csv_action.setEnabled(idle and has_result)
        self._export_pattern_png_action.setEnabled(idle and has_result)
        self._export_geometry_png_action.setEnabled(idle and has_project)
        self._export_geometry_svg_action.setEnabled(idle and has_project)
        self._export_geometry_pdf_action.setEnabled(idle and has_project)
        self._export_geometry_dxf_action.setEnabled(idle and has_project)
        self._export_html_action.setEnabled(idle and has_result)
        self._export_pdf_action.setEnabled(idle and has_result)
        has_history = (
            self._project is not None and self._project.has_compactable_simulation_history()
        )
        self._compact_history_action.setEnabled(idle and has_history)
        self._simulate_action.setEnabled(idle and has_project and self._solver is not None)
        self._cancel_action.setEnabled(self._simulating and self._cancel_token is not None)
        self._form.setEnabled(idle and has_project and not is_custom)
        self._design_stack.setEnabled(idle and has_project)
        self._custom_edit.setEnabled(idle and has_project and is_custom)
        self._project_name.setEnabled(idle and has_project)
        self._variant_combo.setEnabled(idle and has_designs)
        self._advanced_toggle.setEnabled(idle and has_project)
        self._sweep_group.setEnabled(idle and has_project)
        self._toolbar.setVisible(has_project)

    def _estimate_unavailable_message(self, parameters: AntennaDesignParameters) -> str:
        if isinstance(parameters, VerticalParameters) and parameters.loading_coil_enabled:
            return self._translator.t("design_from_frequency.unsupported_loaded_vertical")
        if (
            isinstance(parameters, EndFedParameters)
            and parameters.preset is EndFedPreset.RANDOM_WIRE
        ):
            return self._translator.t("design_from_frequency.unsupported_random_wire")
        return self._translator.t("design_from_frequency.unsupported")

    def _discard_form_changes_for_history(self, *, redo: bool) -> bool:
        if not self._form_dirty:
            return True
        key = "dialog.redo_dirty_message" if redo else "dialog.undo_dirty_message"
        answer = QMessageBox.question(
            self,
            self._translator.t("dialog.undo_dirty_title"),
            self._translator.t(key),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes

    def _undo_project(self) -> None:
        if self._simulating or not self._undo_stack.canUndo():
            return
        if not self._discard_form_changes_for_history(redo=False):
            return
        self._undo_stack.undo()

    def _redo_project(self) -> None:
        if self._simulating or not self._redo_stack_can_redo():
            return
        if not self._discard_form_changes_for_history(redo=True):
            return
        self._undo_stack.redo()

    def _redo_stack_can_redo(self) -> bool:
        try:
            return self._undo_stack.canRedo()
        except RuntimeError:
            return False

    def _refresh_history_actions(self) -> None:
        try:
            undo_text = self._undo_stack.undoText()
            redo_text = self._undo_stack.redoText()
            can_undo = self._undo_stack.canUndo()
            can_redo = self._undo_stack.canRedo()
        except RuntimeError:
            return
        self._undo_action.setEnabled(can_undo and not self._simulating)
        self._redo_action.setEnabled(can_redo and not self._simulating)
        self._undo_action.setText(
            self._translator.t("action.undo") + (f" {undo_text}" if undo_text else "")
        )
        self._redo_action.setText(
            self._translator.t("action.redo") + (f" {redo_text}" if redo_text else "")
        )

    def _history_snapshot(self) -> ProjectSnapshot:
        return ProjectSnapshot(self._project, self._design_id)

    def _current_project_signature(self) -> tuple[object, ...] | None:
        return self._history_snapshot().signature()

    def _current_run_ids(self) -> frozenset[UUID]:
        if self._project is None:
            return frozenset()
        return frozenset(run.id for run in self._project.simulation_runs)

    def _update_dirty_from_signature(self) -> None:
        self._dirty = (
            self._current_project_signature() != self._clean_signature
            or self._current_run_ids() != self._clean_run_ids
            or self._form_dirty
        )

    def _record_history(
        self,
        label_key: str,
        before: ProjectSnapshot,
        after: ProjectSnapshot,
    ) -> None:
        if self._history_depth or self._history_restoring:
            return
        if before.signature() == after.signature():
            return
        self._undo_stack.push(
            SnapshotCommand(
                self._restore_project_snapshot,
                before,
                after,
                self._translator.t(label_key),
            )
        )
        self._update_dirty_from_signature()
        self._update_title()
        self._refresh_history_actions()

    def _restore_project_snapshot(self, snapshot: ProjectSnapshot) -> None:
        if snapshot.project is None or self._history_restoring:
            return
        self._history_restoring = True
        try:
            current_runs = self._project.simulation_runs if self._project is not None else ()
            valid_design_ids = {design.id for design in snapshot.project.designs}
            merged_runs = tuple(run for run in current_runs if run.design_id in valid_design_ids)
            project = replace(
                snapshot.project,
                simulation_runs=merged_runs,
                updated_at=utc_now(),
            )
            self._project = project
            if snapshot.design_id is not None:
                try:
                    project.design_by_id(snapshot.design_id)
                    selected_id = snapshot.design_id
                except ValueError:
                    selected_id = project.designs[0].id if project.designs else None
            else:
                selected_id = project.designs[0].id if project.designs else None
            self._design_id = selected_id
            self._feed_line = project.feed_line
            self._matching_network = project.matching_network
            self._form_dirty = False
            self._simulation_results = {}
            self._band_analysis_results = {}
            self._selected_band_ids = {}
            self._band_plans = {}
            for project_design in project.designs:
                analysis = self._latest_band_analysis_for(project, project_design.id)
                if analysis is not None and analysis.bands:
                    self._band_analysis_results[project_design.id] = analysis
                    self._remember_band_plan(analysis)
                    self._simulation_results[project_design.id] = analysis.bands[0].result
                    continue
                latest_run = project.latest_simulation_run(project_design.id)
                if latest_run is not None:
                    self._simulation_results[project_design.id] = latest_run.result
            self._results.set_band_analysis(None)
            self._results.set_measurements(project.measurements)
            self._project_name_updating = True
            self._project_name.setText(project.name)
            self._project_name_updating = False
            self._populate_variants(selected_id)
            if selected_id is not None:
                self._select_design(selected_id)
            else:
                self._results.set_result(None)
            self._update_dirty_from_signature()
            self._update_title()
            self._update_actions()
            self._update_status_text()
        finally:
            self._history_restoring = False

    def _populate_variants(self, target_id: UUID | None = None) -> None:
        if self._project is None:
            return
        target = target_id if target_id is not None else self._design_id
        self._updating_variants = True
        self._variant_combo.blockSignals(True)
        self._variant_combo.clear()
        for design in self._project.designs:
            self._variant_combo.addItem(design.name, str(design.id))
        self._variant_combo.blockSignals(False)
        self._updating_variants = False
        if target is not None:
            self._set_variant_combo(target)

    def _set_variant_combo(self, design_id: UUID) -> None:
        index = self._variant_combo.findData(str(design_id))
        if index < 0:
            return
        previous = self._updating_variants
        self._updating_variants = True
        self._variant_combo.blockSignals(True)
        self._variant_combo.setCurrentIndex(index)
        self._variant_combo.blockSignals(False)
        self._updating_variants = previous

    def _update_custom_panel(self, design: DesignVariant) -> None:
        parameters = design.parameters
        if not isinstance(parameters, CustomAntennaParameters):
            return
        family = antenna_family(parameters)
        template = parameters.generator_name or self._translator.t("catalog.custom")
        self._custom_family.setText(
            self._translator.t("custom.family", value=self._translator.t(f"family.{family.value}"))
        )
        self._custom_generator.setText(self._translator.t("custom.template", value=template))
        self._custom_summary.setText(
            self._translator.t(
                "custom.summary",
                count=len(design.antenna.wires),
                length=f"{sum(wire.length_m for wire in design.antenna.wires):.3f} m",
            )
        )
        self._custom_generator_edit.setVisible(
            parameters.generator_id in {"inverted_v", "ocfd", "yagi", "vertical"}
        )
        index = (
            0
            if self._custom_run_pattern_step_deg is None
            else self._custom_pattern_resolution.findData(self._custom_run_pattern_step_deg)
        )
        if index >= 0:
            self._custom_pattern_resolution.blockSignals(True)
            self._custom_pattern_resolution.setCurrentIndex(index)
            self._custom_pattern_resolution.blockSignals(False)
        if self._custom_sweep_center_hz != design.parameters.frequency_hz:
            self._custom_sweep_center_hz = design.parameters.frequency_hz
            if parameters.generator_id == "g5rv":
                self._custom_sweep_start.setValue(3.5)
                self._custom_sweep_stop.setValue(30.0)
                self._custom_sweep_points.setValue(41)
            else:
                center_mhz = design.parameters.frequency_hz / 1_000_000.0
                self._custom_sweep_start.setValue(center_mhz * 0.95)
                self._custom_sweep_stop.setValue(center_mhz * 1.05)
                self._custom_sweep_points.setValue(100)
            self._custom_sweep.setChecked(True)
        self._update_custom_pattern_status()

    def _set_geometry_model(self, design: DesignVariant) -> None:
        display_name = (
            design.parameters.template_name
            if isinstance(design.parameters, JPoleParameters)
            else None
        )
        self._geometry.set_model(
            design.antenna,
            antenna_type=design.antenna_type,
            display_name=display_name,
            parameters=design.parameters,
        )
        self._height_combo.blockSignals(True)
        self._height_combo.setCurrentIndex(0)
        self._height_combo.blockSignals(False)

    def _select_design(self, design_id: UUID) -> None:
        if self._project is None:
            return
        design = self._project.design_by_id(design_id)
        self._design_id = design_id
        self._form_dirty = False
        self._sweep_custom_initialized = False
        self._update_provenance_label(design)
        self._loads = design.antenna.loads
        self._transmission_lines = design.antenna.transmission_lines
        if isinstance(design.parameters, CustomAntennaParameters):
            self._design_stack.setCurrentWidget(self._custom_panel)
            self._update_custom_panel(design)
        elif isinstance(design.parameters, OCFDParameters):
            self._design_stack.setCurrentWidget(self._ocfd_scroll)
            self._ocfd_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, VerticalParameters):
            self._design_stack.setCurrentWidget(self._vertical_scroll)
            self._vertical_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, InvertedVParameters):
            self._design_stack.setCurrentWidget(self._inverted_v_scroll)
            self._inverted_v_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, YagiParameters):
            self._design_stack.setCurrentWidget(self._yagi_scroll)
            self._yagi_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, MoxonParameters):
            self._design_stack.setCurrentWidget(self._moxon_scroll)
            self._moxon_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, FanDipoleParameters):
            self._design_stack.setCurrentWidget(self._fan_dipole_scroll)
            self._fan_dipole_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, TrapDipoleParameters):
            self._design_stack.setCurrentWidget(self._trap_dipole_scroll)
            self._trap_dipole_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, T2FDParameters):
            self._design_stack.setCurrentWidget(self._t2fd_scroll)
            self._t2fd_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, EndFedParameters):
            self._design_stack.setCurrentWidget(self._endfed_scroll)
            self._endfed_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, JPoleParameters):
            self._design_stack.setCurrentWidget(self._j_pole_scroll)
            self._j_pole_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, RingoParameters):
            self._design_stack.setCurrentWidget(self._ringo_scroll)
            self._ringo_form.set_parameters(design.parameters)
        else:
            self._design_stack.setCurrentWidget(self._form_scroll)
            self._form.set_parameters(design.parameters, reset_sweep=True)
        self._results.set_design(design)
        self._set_geometry_model(design)
        self._auto_select_view(design)
        self._set_variant_combo(design_id)
        analysis = self._band_analysis_results.get(design_id)
        if analysis is None and self._project is not None:
            analysis = self._latest_band_analysis_for(self._project, design_id)
            if analysis is not None:
                self._band_analysis_results[design_id] = analysis
                self._remember_band_plan(analysis)
        result = self._simulation_results.get(design_id)
        if analysis is not None and analysis.bands:
            selected_id = self._selected_band_ids.get(design_id, analysis.bands[0].band.name)
            selected = analysis.result_for_band(selected_id) or analysis.bands[0]
            self._selected_band_ids[design_id] = selected.band.name
            result = selected.result
            self._simulation_results[design_id] = result
            self._results.set_band_analysis(analysis)
        else:
            self._results.set_band_analysis(None)
            if result is None and self._project is not None:
                latest_run = self._project.latest_simulation_run(design_id)
                if latest_run is not None:
                    result = latest_run.result
                    self._simulation_results[design_id] = result
        self._last_result = result
        self._update_band_plan_label()
        self._results.set_result(result)
        self._last_status_key = (
            self._result_status_key(result.status) if result is not None else "status.ready"
        )
        self._update_status_text()
        self._update_actions()
        self._update_height_control()
        self._update_custom_pattern_status()
        self._refresh_auto_sweep_display()

    @history_action("history.apply_design")
    def _on_variant_changed(self, *_args: object) -> None:
        if self._updating_variants or self._project is None:
            return
        value = self._variant_combo.currentData()
        if not isinstance(value, str):
            return
        try:
            design_id = UUID(value)
        except ValueError:
            return
        if design_id == self._design_id:
            return
        previous_id = self._design_id
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                if previous_id is not None:
                    self._set_variant_combo(previous_id)
                return
        self._select_design(design_id)

    def _show_empty_state(self) -> None:
        self._project = None
        self._design_id = None
        self._feed_line = None
        self._matching_network = None
        self._current_path = None
        self._dirty = False
        self._form_dirty = False
        self._last_result = None
        self._simulation_results = {}
        self._band_analysis_results = {}
        self._band_plans = {}
        self._selected_band_ids = {}
        self._simulation_design_id = None
        self._band_analysis_design_id = None
        self._loads = ()
        self._transmission_lines = ()
        self._undo_stack.clear()
        self._clean_signature = None
        self._clean_run_ids = frozenset()
        self._project_name_updating = True
        self._project_name.clear()
        self._project_name_updating = False
        self._variant_combo.clear()
        self._results.set_band_analysis(None)
        self._results.set_result(None)
        self._results.set_design(None)
        self._results.set_measurements(())
        self._geometry.clear_model()
        self._main_stack.setCurrentWidget(self._start_page)
        self._last_status_key = "status.ready"
        self._update_title()
        self._update_status_text()
        self._update_actions()

    def _set_project(
        self,
        project: Project,
        design_id: UUID,
        *,
        path: Path | None,
        dirty: bool,
    ) -> None:
        self._project = project
        self._design_id = design_id
        self._feed_line = project.feed_line
        self._matching_network = project.matching_network
        self._current_path = path
        self._dirty = dirty
        self._form_dirty = False
        self._last_result = None
        self._simulation_results = {}
        self._band_analysis_results = {}
        self._band_plans = {}
        self._selected_band_ids = {}
        for project_design in project.designs:
            analysis = self._latest_band_analysis_for(project, project_design.id)
            if analysis is not None and analysis.bands:
                self._band_analysis_results[project_design.id] = analysis
                self._remember_band_plan(analysis)
                self._simulation_results[project_design.id] = analysis.bands[0].result
                continue
            latest_run = project.latest_simulation_run(project_design.id)
            if latest_run is not None:
                self._simulation_results[project_design.id] = latest_run.result
        self._simulation_design_id = None
        self._band_analysis_design_id = None
        self._results.set_band_analysis(None)
        self._results.set_result(None)
        self._results.set_measurements(project.measurements)
        self._project_name_updating = True
        self._project_name.setText(project.name)
        self._project_name_updating = False
        self._main_stack.setCurrentWidget(self._editor_panel)
        self._populate_variants(design_id)
        self._select_design(design_id)
        self._undo_stack.clear()
        self._history_depth = 0
        self._history_restoring = False
        if not dirty:
            self._clean_signature = self._current_project_signature()
            self._clean_run_ids = self._current_run_ids()
        self._dirty = dirty
        self._update_title()
        self._update_actions()
        self._refresh_history_actions()

    def _apply_fields(self) -> Project:
        if self._project is None or self._design_id is None:
            raise ValueError(self._translator.t("error.no_project"))
        project_name = self._project_name.text().strip()
        if not project_name:
            raise ValueError("project name must not be empty")
        previous_design = self._project.design_by_id(self._design_id)
        loads_override = self._loads if self._loads != previous_design.antenna.loads else None
        transmission_lines_override = (
            self._transmission_lines
            if self._transmission_lines != previous_design.antenna.transmission_lines
            else None
        )
        attachments_changed = loads_override is not None or transmission_lines_override is not None
        if isinstance(previous_design.parameters, OCFDParameters):
            parameters = self._ocfd_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, VerticalParameters):
            parameters = self._vertical_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, InvertedVParameters):
            parameters = self._inverted_v_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, YagiParameters):
            parameters = self._yagi_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, MoxonParameters):
            parameters = self._moxon_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, FanDipoleParameters):
            parameters = self._fan_dipole_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, TrapDipoleParameters):
            parameters = self._trap_dipole_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, T2FDParameters):
            parameters = self._t2fd_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, EndFedParameters):
            parameters = self._endfed_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, JPoleParameters):
            parameters = self._j_pole_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, RingoParameters):
            parameters = self._ringo_form.parameters()
            updated = UpdateDipoleDesign().execute(
                UpdateDipoleDesignCommand(
                    project=self._project,
                    design_id=self._design_id,
                    parameters=parameters,
                    loads=loads_override,
                    transmission_lines=transmission_lines_override,
                )
            )
            updated = replace(updated, name=project_name)
            self._project = updated
            design = updated.design_by_id(self._design_id)
            if parameters != previous_design.parameters or attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._loads = design.antenna.loads
            self._transmission_lines = design.antenna.transmission_lines
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._project_name_updating = True
            self._project_name.setText(project_name)
            self._project_name_updating = False
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, CustomAntennaParameters):
            design = previous_design
            if (
                design.antenna.loads != self._loads
                or design.antenna.transmission_lines != self._transmission_lines
            ):
                design = design.with_loads(self._loads).with_transmission_lines(
                    self._transmission_lines
                )
                self._project = self._project.with_design(design, updated_at=utc_now())
            self._project = replace(self._project, name=project_name)
            if attachments_changed:
                self._invalidate_design_result(self._design_id)
                self._results.set_result(None)
            self._results.set_design(design)
            self._set_geometry_model(design)
            self._auto_select_view(design)
            self._form_dirty = False
            self._dirty = True
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        parameters = self._form.parameters()
        updated = UpdateDipoleDesign().execute(
            UpdateDipoleDesignCommand(
                project=self._project,
                design_id=self._design_id,
                parameters=parameters,
                loads=loads_override,
                transmission_lines=transmission_lines_override,
            )
        )
        updated = replace(updated, name=project_name)
        self._project = updated
        design = updated.design_by_id(self._design_id)
        self._results.set_design(design)
        self._set_geometry_model(design)
        self._auto_select_view(design)
        self._project_name_updating = True
        self._project_name.setText(project_name)
        self._project_name_updating = False
        if parameters != previous_design.parameters or attachments_changed:
            self._invalidate_design_result(self._design_id)
            self._last_result = None
            self._results.set_result(None)
        self._form_dirty = False
        self._dirty = True
        self._update_title()
        self._update_actions()
        self._update_height_control()
        return updated

    @history_action("history.apply_design")
    def apply_design(self) -> None:
        try:
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._last_status_key = "status.design_changed"
        self._update_status_text()

    @history_action("history.feed_line")
    def configure_feed_line(self) -> None:
        dialog = FeedLineDialog(
            self._translator,
            self._unit_system,
            self._feed_line,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._feed_line = dialog.result_feed_line()
        if self._project is not None:
            self._project = self._project.with_feed_line(
                self._feed_line,
                updated_at=utc_now(),
            )
            self._dirty = True
            self._update_title()

    @history_action("history.matching_network")
    def configure_matching_network(self) -> None:
        frequency_hz = 14_100_000.0
        if self._project is not None and self._design_id is not None:
            frequency_hz = self._project.design_by_id(self._design_id).parameters.frequency_hz
        dialog = MatchingNetworkDialog(
            self._translator,
            self._matching_network,
            self,
            frequency_hz=frequency_hz,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._matching_network = dialog.result_network()
        if self._project is not None:
            self._project = self._project.with_matching_network(
                self._matching_network,
                updated_at=utc_now(),
            )
            self._dirty = True
            self._update_title()

    def _base_simulation_spec(self, design: DesignVariant) -> SimulationSpec:
        parameters = design.parameters
        if isinstance(parameters, CustomAntennaParameters):
            return self._custom_simulation_spec(parameters)
        if isinstance(parameters, OCFDParameters):
            return self._ocfd_simulation_spec(parameters)
        if isinstance(parameters, VerticalParameters):
            return self._vertical_simulation_spec(parameters)
        if isinstance(parameters, InvertedVParameters):
            return self._inverted_v_simulation_spec(parameters)
        if isinstance(parameters, YagiParameters):
            return self._yagi_simulation_spec(parameters)
        if isinstance(parameters, MoxonParameters):
            return self._moxon_simulation_spec(parameters)
        if isinstance(parameters, FanDipoleParameters):
            return self._fan_dipole_simulation_spec(parameters)
        if isinstance(parameters, TrapDipoleParameters):
            return self._trap_dipole_simulation_spec(parameters)
        if isinstance(parameters, T2FDParameters):
            return self._t2fd_simulation_spec(parameters)
        if isinstance(parameters, EndFedParameters):
            return self._endfed_simulation_spec(parameters)
        if isinstance(parameters, JPoleParameters):
            return self._j_pole_simulation_spec(parameters)
        if isinstance(parameters, RingoParameters):
            return self._ringo_simulation_spec(parameters)
        return self._form.simulation_spec()

    def _apply_sweep_override(
        self,
        design: DesignVariant,
        spec: SimulationSpec,
    ) -> SimulationSpec:
        if self._sweep_mode.currentData() != "custom":
            return spec
        start_hz = self._sweep_start.value() * 1_000_000.0
        stop_hz = self._sweep_stop.value() * 1_000_000.0
        if start_hz >= stop_hz:
            raise ValueError(self._translator.t("error.invalid_sweep"))
        plan = FrequencyPlan.sweep(start_hz, stop_hz, self._sweep_points.value())
        return self._replanned_spec(design, spec, plan)

    def _replanned_spec(
        self,
        design: DesignVariant,
        spec: SimulationSpec,
        frequency_plan: FrequencyPlan,
    ) -> SimulationSpec:
        """Rebuild segmentation for a different band plan."""

        model = design.antenna
        segmentation = SegmentationPolicy(min_segments_per_wire=3)
        if isinstance(design.parameters, CustomAntennaParameters) and (
            design.parameters.generator_id == "g5rv"
        ):
            dipole = model.wire_by_id(G5RV_DIPOLE_ID)
            count = segmentation.segments_for(dipole, frequency_plan.stop_hz)
            if count % 2 == 0:
                count += 1
            segmentation = SegmentationPolicy(
                min_segments_per_wire=3,
                wire_segments=((G5RV_DIPOLE_ID, count),),
            )
        elif isinstance(design.parameters, T2FDParameters):
            base = aligned_policy_for_model(
                model,
                frequency_plan.stop_hz,
                SegmentationPolicy(min_segments_per_wire=3),
            )
            driven_count = base.segments_for(
                model.wire_by_id(T2FD_DRIVEN_WIRE_ID),
                frequency_plan.stop_hz,
            )
            if driven_count % 2 == 0:
                driven_count += 1
            segmentation = SegmentationPolicy(
                min_segments_per_wire=3,
                wire_segments=tuple(
                    (
                        wire.id,
                        driven_count
                        if wire.id in {T2FD_DRIVEN_WIRE_ID, T2FD_TERMINATED_WIRE_ID}
                        else base.segments_for(wire, frequency_plan.stop_hz),
                    )
                    for wire in model.wires
                ),
            )
        segmentation = aligned_policy_for_model(
            model,
            frequency_plan.stop_hz,
            segmentation,
        )
        return replace(
            spec,
            frequency_plan=frequency_plan,
            segmentation=segmentation,
            pattern_frequencies_hz=(),
        )

    @history_action("history.simulate")
    def simulate(self) -> None:
        if self._simulating:
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        try:
            project = self._apply_fields()
            if self._design_id is None:
                raise ValueError(self._translator.t("error.no_project"))
            design = project.design_by_id(self._design_id)
            if isinstance(design.parameters, YagiParameters) and yagi_element_length_mismatch(
                design.parameters
            ):
                answer = QMessageBox.question(
                    self,
                    self._translator.t("dialog.yagi_mismatch_title"),
                    self._translator.t("dialog.yagi_mismatch_message"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
            if (
                isinstance(design.parameters, FanDipoleParameters)
                and self._sweep_mode.currentData() != "custom"
            ):
                fan_plan = default_band_plan(design.parameters).plan
                if len(fan_plan) > 1:
                    self._start_band_analysis(design, fan_plan)
                    return
            spec = self._apply_sweep_override(design, self._base_simulation_spec(design))
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return

        self._last_result = None
        self._results.set_result(None)
        self._simulation_design_id = self._design_id
        spec = self._fit_spec_to_budget(design.antenna, spec)
        spec = replace(spec, feed_line=self._feed_line, matching_network=self._matching_network)
        self._cancel_token = EventCancelToken()
        self._simulating = True
        self._last_status_key = "status.simulating"
        self._update_actions()
        self._update_status_text()

        thread = QThread(self)
        worker = SimulationWorker(
            self._solver,
            design.antenna,
            spec,
            self._cancel_token,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_simulation_finished)
        worker.failed.connect(self._on_simulation_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_worker_thread_finished)
        self._thread = thread
        self._worker = worker
        thread.start()

    def analyze_bands(self) -> None:
        if self._simulating:
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        try:
            project = self._apply_fields()
            if self._design_id is None:
                raise ValueError(self._translator.t("error.no_project"))
            design = project.design_by_id(self._design_id)
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return

        default = self._default_band_default(design)
        saved_plan = self._band_plans.get(design.id)
        dialog = BandAnalysisDialog(
            self._translator,
            default,
            current_frequency_hz=design.parameters.frequency_hz,
            selected_plan=saved_plan,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        plan = dialog.plan()
        if not plan:
            return
        self._start_band_analysis(design, plan)

    def _start_band_analysis(self, design: DesignVariant, plan: BandPlan) -> None:
        if not plan or self._solver is None:
            return
        self._band_plans[design.id] = plan
        self._update_band_plan_label()

        requests: list[BandSimulationRequest] = []
        for selection in plan.selections:
            spec = self._replanned_spec(
                design,
                self._base_simulation_spec(design),
                selection.frequency_plan,
            )
            target_hz = (
                design.parameters.frequency_hz
                if selection.band.start_hz
                <= design.parameters.frequency_hz
                <= selection.band.stop_hz
                else selection.center_hz
            )
            spec = replace(
                spec,
                pattern_frequencies_hz=self._custom_pattern_frequencies(
                    spec.frequency_plan,
                    target_hz,
                ),
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            )
            requests.append(BandSimulationRequest(selection.band, spec))

        fitted = self._fit_band_specs_to_budget(
            design.antenna,
            tuple(request.spec for request in requests),
        )
        requests = [
            BandSimulationRequest(request.band, spec)
            for request, spec in zip(requests, fitted, strict=True)
        ]

        self._last_result = None
        self._pending_pattern_diagnostic = None
        self._results.set_band_analysis(None)
        self._results.set_result(None)
        self._band_analysis_design_id = design.id
        self._cancel_token = EventCancelToken()
        self._simulating = True
        self._last_status_key = "status.analyzing_bands"
        self._update_actions()
        self._update_status_text()

        thread = QThread(self)
        worker = BandAnalysisWorker(
            self._solver,
            design.id,
            design.antenna,
            tuple(requests),
            self._cancel_token,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_band_analysis_progress)
        worker.finished.connect(self._on_band_analysis_finished)
        worker.failed.connect(self._on_simulation_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_worker_thread_finished)
        self._thread = thread
        self._worker = worker
        thread.start()

    def _on_band_analysis_progress(self, index: int, total: int, band: str) -> None:
        self._status_label.setText(
            self._translator.t(
                "status.bands_progress",
                index=index,
                total=total,
                band=band,
            )
        )

    def _on_band_analysis_finished(self, analysis: BandAnalysisResult) -> None:
        self._simulating = False
        self._cancel_token = None
        self._pending_pattern_diagnostic = None
        design_id = self._band_analysis_design_id or analysis.design_id
        self._band_analysis_design_id = None
        self._band_analysis_results[design_id] = analysis
        self._remember_band_plan(analysis)
        if analysis.bands:
            selected = analysis.bands[0]
            self._selected_band_ids[design_id] = selected.band.name
            self._simulation_results[design_id] = selected.result
            self._last_result = selected.result
        self._simulation_design_id = None
        self._last_status_key = (
            "status.bands_done"
            if analysis.status is SimulationStatus.COMPLETED
            else self._result_status_key(analysis.status)
        )
        if self._project is not None:
            recorded = False
            for band_result in analysis.bands:
                if band_result.result.status not in {
                    SimulationStatus.COMPLETED,
                    SimulationStatus.PARTIAL,
                }:
                    continue
                self._project = RecordSimulationRun().execute(
                    RecordSimulationRunCommand(
                        project=self._project,
                        design_id=design_id,
                        result=band_result.result,
                        band_id=band_result.band.name,
                        batch_id=analysis.batch_id,
                    )
                )
                recorded = True
            if recorded:
                self._dirty = True
                self._update_title()
        self._results.set_band_analysis(analysis)
        if analysis.bands:
            self._results.set_result(analysis.bands[0].result)
        self._results.show_bands()
        self._update_actions()
        self._update_status_text()
        if analysis.status is SimulationStatus.ERROR:
            self._show_error(self._translator.t("status.error"))

    def _on_band_selected(self, band_result: object) -> None:
        if not isinstance(band_result, BandResult):
            return
        if self._design_id is None:
            return
        self._selected_band_ids[self._design_id] = band_result.band.name
        self._simulation_results[self._design_id] = band_result.result
        self._last_result = band_result.result
        self._update_actions()

    def _on_simulation_finished(self, result: SimulationResult) -> None:
        self._simulating = False
        self._cancel_token = None
        if self._pending_pattern_diagnostic is not None:
            result = replace(
                result,
                diagnostics=(
                    *result.diagnostics,
                    self._pending_pattern_diagnostic,
                ),
            )
            self._pending_pattern_diagnostic = None
        design_id = self._simulation_design_id
        if design_id is not None:
            self._band_analysis_results.pop(design_id, None)
            self._selected_band_ids.pop(design_id, None)
            self._results.set_band_analysis(None)
            self._simulation_results[design_id] = result
            if self._project is not None and result.status in {
                SimulationStatus.COMPLETED,
                SimulationStatus.PARTIAL,
            }:
                self._project = RecordSimulationRun().execute(
                    RecordSimulationRunCommand(
                        project=self._project,
                        design_id=design_id,
                        result=result,
                    )
                )
                self._dirty = True
                self._update_title()
        self._simulation_design_id = None
        self._last_result = result
        self._last_status_key = self._result_status_key(result.status)
        self._results.set_result(result)
        self._update_actions()
        self._update_status_text()
        if result.status is SimulationStatus.ERROR:
            error = next(
                (
                    diagnostic.message
                    for diagnostic in result.diagnostics
                    if diagnostic.severity.value == "error"
                ),
                self._translator.t("status.error"),
            )
            self._show_error(self._translator.t("error.simulation", message=error))

    def _on_simulation_failed(self, message: str) -> None:
        self._simulating = False
        self._cancel_token = None
        self._simulation_design_id = None
        self._band_analysis_design_id = None
        self._pending_pattern_diagnostic = None
        self._last_status_key = "status.error"
        self._update_actions()
        self._status_label.setText(self._translator.t("status.error"))
        self._show_error(self._translator.t("error.simulation", message=message))

    def _on_worker_thread_finished(self) -> None:
        self._thread = None
        self._worker = None

    def cancel_simulation(self) -> None:
        if not self._simulating or self._cancel_token is None:
            return
        self._cancel_token.cancel()
        self._last_status_key = "status.cancelling"
        self._status_label.setText(self._translator.t("status.cancelling"))
        self._cancel_action.setEnabled(False)

    def _fit_spec_to_budget(self, model: object, spec: SimulationSpec) -> SimulationSpec:
        """Choose pattern snapshots and the finest pattern step that fits storage."""

        from ..domain.antennas.antenna import AntennaModel

        if not isinstance(model, AntennaModel) or not spec.far_field.enabled:
            self._pending_pattern_diagnostic = None
            return replace(spec, pattern_frequencies_hz=())
        ground = model.environment.ground
        requested_step = self._custom_run_pattern_step_deg
        pattern_frequencies = spec.pattern_frequencies_hz
        if not pattern_frequencies:
            if self._custom_pattern_frequency_count is None:
                pattern_frequencies = band_snapshot_frequencies(
                    spec.frequency_plan,
                    preferred_frequency_hz=model.design_frequency_hz,
                )
            else:
                pattern_frequencies = spec.frequency_plan.snapshot_frequencies(
                    self._custom_pattern_frequency_count,
                    preferred_frequency_hz=model.design_frequency_hz,
                )
        pattern_count = (
            len(pattern_frequencies) if pattern_frequencies else spec.frequency_plan.count
        )
        segment_count = sum(
            spec.segmentation.segments_for(wire, spec.frequency_plan.stop_hz)
            for wire in model.wires
        )
        budget = choose_pattern_step(
            frequency_count=spec.frequency_plan.count,
            pattern_frequency_count=pattern_count,
            segment_count=segment_count,
            candidate_steps=tuple(reversed(PATTERN_STEPS_DEG)),
            counts_for_step=lambda step: pattern_counts(step, ground),
            requested_step_deg=requested_step,
        )
        self._custom_last_budget = budget
        self._show_custom_pattern_budget(budget)
        if budget.far_field_enabled:
            if requested_step is None or budget.pattern_step_deg == requested_step:
                self._pending_pattern_diagnostic = None
            else:
                self._pending_pattern_diagnostic = Diagnostic(
                    code="solver.pattern_resolution_reduced",
                    severity=Severity.INFO,
                    message=(
                        "far-field pattern resolution reduced from "
                        f"{requested_step:g}° to {budget.pattern_step_deg:g}° "
                        "to fit the project storage limit"
                    ),
                    field="far_field",
                )
            return replace(
                spec,
                far_field=far_field_request(budget.pattern_step_deg, ground),
                pattern_frequencies_hz=pattern_frequencies,
            )
        self._pending_pattern_diagnostic = Diagnostic(
            code="solver.pattern_disabled",
            severity=Severity.WARNING,
            message=(
                "far-field pattern disabled: the sweep is too large for the project storage limit"
            ),
            field="far_field",
        )
        return replace(
            spec,
            far_field=FarFieldRequest(enabled=False),
            pattern_frequencies_hz=(),
        )

    def _fit_band_specs_to_budget(
        self,
        model: object,
        specs: tuple[SimulationSpec, ...],
    ) -> tuple[SimulationSpec, ...]:
        from ..domain.antennas.antenna import AntennaModel

        if not specs or not isinstance(model, AntennaModel):
            return specs
        ground = model.environment.ground
        budget = choose_batch_pattern_step(
            frequency_counts=tuple(spec.frequency_plan.count for spec in specs),
            segment_counts=tuple(
                sum(
                    spec.segmentation.segments_for(wire, spec.frequency_plan.stop_hz)
                    for wire in model.wires
                )
                for spec in specs
            ),
            candidate_steps=tuple(reversed(PATTERN_STEPS_DEG)),
            counts_for_step=lambda step: pattern_counts(step, ground),
            requested_step_deg=self._custom_run_pattern_step_deg,
            pattern_frequency_counts=tuple(
                max(1, len(spec.pattern_frequencies_hz)) for spec in specs
            ),
        )
        self._custom_last_budget = budget
        self._show_custom_pattern_budget(budget)
        if not budget.far_field_enabled:
            return tuple(
                replace(
                    spec,
                    far_field=FarFieldRequest(enabled=False),
                    pattern_frequencies_hz=(),
                )
                for spec in specs
            )
        if budget.pattern_step_deg is None:
            return specs
        request = far_field_request(budget.pattern_step_deg, ground)
        return tuple(replace(spec, far_field=request) for spec in specs)

    def _update_custom_sweep_controls(self) -> None:
        enabled = self._custom_sweep.isChecked()
        self._custom_sweep_start.setEnabled(enabled)
        self._custom_sweep_stop.setEnabled(enabled)
        self._custom_sweep_points.setEnabled(enabled)
        self._update_custom_pattern_status()

    def _custom_pattern_changed(self, _index: int) -> None:
        value = self._custom_pattern_resolution.currentData()
        self._custom_run_pattern_step_deg = (
            float(value) if isinstance(value, (int, float)) else None
        )
        self._update_custom_pattern_status()

    def _custom_pattern_frequency_changed(self, _index: int) -> None:
        value = self._custom_pattern_frequency_mode.currentData()
        self._custom_pattern_frequency_count = int(value) if isinstance(value, int) else None
        self._update_custom_pattern_status()

    def _custom_pattern_frequencies(
        self,
        frequency_plan: FrequencyPlan,
        preferred_frequency_hz: float,
    ) -> tuple[float, ...]:
        if self._custom_pattern_frequency_count is None:
            return band_snapshot_frequencies(
                frequency_plan,
                preferred_frequency_hz=preferred_frequency_hz,
            )
        return frequency_plan.snapshot_frequencies(
            self._custom_pattern_frequency_count,
            preferred_frequency_hz=preferred_frequency_hz,
        )

    def _update_custom_pattern_status(self) -> None:
        if self._project is None or self._design_id is None:
            self._custom_pattern_status.setText("")
            return
        design = self._project.design_by_id(self._design_id)
        requested = (
            self._translator.t("custom.pattern_auto")
            if self._custom_run_pattern_step_deg is None
            else f"{self._custom_run_pattern_step_deg:g}°"
        )
        if not isinstance(design.parameters, CustomAntennaParameters):
            self._custom_pattern_status.setText("")
            return
        sweep_count = self._custom_sweep_points.value() if self._custom_sweep.isChecked() else 1
        pattern_count = 1
        if (
            self._custom_sweep.isChecked()
            and self._custom_sweep_start.value() < self._custom_sweep_stop.value()
            and sweep_count >= 2
        ):
            try:
                plan = FrequencyPlan.sweep(
                    self._custom_sweep_start.value() * 1_000_000.0,
                    self._custom_sweep_stop.value() * 1_000_000.0,
                    sweep_count,
                )
                pattern_count = len(
                    self._custom_pattern_frequencies(
                        plan,
                        design.parameters.frequency_hz,
                    )
                )
            except ValueError:
                pattern_count = min(DEFAULT_PATTERN_SNAPSHOT_COUNT, sweep_count)
        self._custom_pattern_status.setText(
            self._translator.t(
                "custom.pattern_requested",
                value=requested,
                count=pattern_count,
                sweep=sweep_count,
            )
        )

    def _show_custom_pattern_budget(self, budget: object) -> None:
        from ..domain.simulation.budget import PatternBudget

        if not isinstance(budget, PatternBudget):
            return
        size = budget.estimated_project_bytes / (1024.0 * 1024.0)
        if not budget.far_field_enabled:
            self._custom_pattern_status.setText(self._translator.t("custom.pattern_disabled"))
            return
        value = f"{budget.pattern_step_deg:g}°"
        if budget.reduced:
            requested = (
                self._translator.t("custom.pattern_auto")
                if self._custom_run_pattern_step_deg is None
                else f"{budget.requested_step_deg:g}°"
            )
            text = self._translator.t(
                "custom.pattern_reduced",
                value=value,
                requested=requested,
                patterns=budget.pattern_frequency_count,
                size=size,
            )
        else:
            text = self._translator.t(
                "custom.pattern_effective",
                value=value,
                patterns=budget.pattern_frequency_count,
                size=size,
            )
        self._custom_pattern_status.setText(text)

    def _ocfd_simulation_spec(self, parameters: OCFDParameters) -> SimulationSpec:
        model = parameters.to_antenna(name="OCFD")
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
            feed_transformer_ratio=parameters.transformer_ratio,
        )

    def _vertical_simulation_spec(self, parameters: VerticalParameters) -> SimulationSpec:
        model = parameters.to_antenna(name="Vertical")
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
        )

    def _inverted_v_simulation_spec(self, parameters: InvertedVParameters) -> SimulationSpec:
        model = parameters.to_antenna(name="Inverted V")
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
        )

    def _yagi_simulation_spec(self, parameters: YagiParameters) -> SimulationSpec:
        model = parameters.to_antenna(name="Yagi")
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
        )

    def _moxon_simulation_spec(self, parameters: MoxonParameters) -> SimulationSpec:
        model = parameters.to_antenna(name="Moxon")
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
        )

    def _fan_dipole_simulation_spec(
        self,
        parameters: FanDipoleParameters,
    ) -> SimulationSpec:
        model = parameters.to_antenna(name="Fan dipole")
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
        )

    def _trap_dipole_simulation_spec(
        self,
        parameters: TrapDipoleParameters,
    ) -> SimulationSpec:
        model = parameters.to_antenna(name="Trap dipole")
        low_band_hz = parameters.frequency_hz
        high_band_hz = parameters.high_band_frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                low_band_hz * 0.95,
                high_band_hz * 1.05,
                DEFAULT_TWO_BAND_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                high_band_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
        )

    def _t2fd_simulation_spec(self, parameters: T2FDParameters) -> SimulationSpec:
        model = parameters.to_antenna(name="T2FD")
        stop_hz = parameters.highest_frequency_hz
        base = aligned_policy_for_model(
            model,
            stop_hz,
            SegmentationPolicy(min_segments_per_wire=3),
        )
        driven_count = base.segments_for(
            model.wire_by_id(T2FD_DRIVEN_WIRE_ID),
            stop_hz,
        )
        if driven_count % 2 == 0:
            driven_count += 1
        wire_segments = tuple(
            (
                wire.id,
                driven_count
                if wire.id in {T2FD_DRIVEN_WIRE_ID, T2FD_TERMINATED_WIRE_ID}
                else base.segments_for(wire, stop_hz),
            )
            for wire in model.wires
        )
        segmentation = SegmentationPolicy(
            min_segments_per_wire=3,
            wire_segments=wire_segments,
        )
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                parameters.frequency_hz,
                parameters.highest_frequency_hz,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=segmentation,
            far_field=far_field_request(
                self._custom_pattern_step_deg,
                parameters.ground,
            ),
            feed_transformer_ratio=parameters.transformer_ratio,
        )

    def _endfed_simulation_spec(self, parameters: EndFedParameters) -> SimulationSpec:
        model = parameters.to_antenna(name="End-fed")
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
            feed_transformer_ratio=parameters.transformer_ratio,
        )

    def _j_pole_simulation_spec(self, parameters: JPoleParameters) -> SimulationSpec:
        model = parameters.to_antenna()
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
        )

    def _ringo_simulation_spec(self, parameters: RingoParameters) -> SimulationSpec:
        model = parameters.to_antenna()
        frequency_hz = parameters.frequency_hz
        return SimulationSpec(
            frequency_plan=FrequencyPlan.sweep(
                frequency_hz * 0.95,
                frequency_hz * 1.05,
                DEFAULT_GENERATED_SWEEP_POINTS,
            ),
            segmentation=aligned_policy_for_model(
                model,
                frequency_hz * 1.05,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
        )

    def _custom_simulation_spec(
        self,
        parameters: CustomAntennaParameters,
    ) -> SimulationSpec:
        model = parameters.to_antenna(name="Custom")
        if self._custom_sweep.isChecked():
            frequency_plan = FrequencyPlan.sweep(
                self._custom_sweep_start.value() * 1_000_000.0,
                self._custom_sweep_stop.value() * 1_000_000.0,
                self._custom_sweep_points.value(),
            )
        else:
            frequency_plan = FrequencyPlan.single(parameters.frequency_hz)
        segmentation = SegmentationPolicy(min_segments_per_wire=3)
        if parameters.generator_id == "g5rv":
            dipole = model.wire_by_id(G5RV_DIPOLE_ID)
            count = segmentation.segments_for(dipole, frequency_plan.stop_hz)
            if count % 2 == 0:
                count += 1
            segmentation = SegmentationPolicy(
                min_segments_per_wire=3,
                wire_segments=((G5RV_DIPOLE_ID, count),),
            )
        segmentation = aligned_policy_for_model(
            model,
            frequency_plan.stop_hz,
            segmentation,
        )
        return SimulationSpec(
            frequency_plan=frequency_plan,
            segmentation=segmentation,
            far_field=far_field_request(self._custom_pattern_step_deg, parameters.ground),
            feed_transformer_ratio=parameters.feed_transformer_ratio,
        )

    def _suggested_project_name(
        self,
        parameters: AntennaDesignParameters,
        default_name: str,
    ) -> str:
        band = amateur_band_for(parameters.frequency_hz)
        return f"{band.name} {default_name}" if band is not None else default_name

    def _ask_project_name(self, default_name: str) -> str | None:
        name, accepted = QInputDialog.getText(
            self,
            self._translator.t("catalog.title"),
            self._translator.t("field.project_name"),
            text=default_name,
        )
        if not accepted:
            return None
        return name.strip() or default_name

    def _create_project_from_parameters(
        self,
        parameters: AntennaDesignParameters,
        *,
        default_name: str,
        feed_line: FeedLine | None = None,
    ) -> None:
        name = self._ask_project_name(self._suggested_project_name(parameters, default_name))
        if name is None:
            return
        try:
            project = CreateDipoleProject().execute(
                CreateDipoleProjectCommand(
                    project_name=name,
                    variant_name="Initial",
                    parameters=parameters,
                )
            )
            if feed_line is not None:
                project = project.with_feed_line(
                    feed_line,
                    updated_at=project.updated_at,
                )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._set_project(project, project.designs[0].id, path=None, dirty=True)

    def new_custom_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = CustomAntennaDialog(
            self._translator,
            self._unit_system,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Custom antenna",
        )

    def new_moxon_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = MoxonDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Moxon",
        )

    def new_yagi_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = YagiDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Yagi",
        )

    def new_ringo_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = RingoDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Ringo",
        )

    def new_j_pole_antenna(self, *, folded: bool) -> None:
        if not self._maybe_save_changes():
            return
        default_name = "Slim Jim" if folded else "J Pole"
        dialog = JPoleDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        parameters = dialog.result_parameters()
        if folded:
            parameters = replace(parameters, folded=True)
        self._create_project_from_parameters(
            parameters,
            default_name=default_name,
        )

    def new_endfed_antenna(
        self,
        *,
        preset: EndFedPreset = EndFedPreset.STANDARD,
    ) -> None:
        if not self._maybe_save_changes():
            return
        default_name = {
            EndFedPreset.STANDARD: "End-fed",
            EndFedPreset.SLOPER: "Sloper",
            EndFedPreset.RANDOM_WIRE: "Random wire",
        }[preset]
        dialog = EndFedDialog(
            self._translator,
            self._unit_system,
            self,
            preset=preset,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name=default_name,
        )

    def new_sloper_antenna(self) -> None:
        self.new_endfed_antenna(preset=EndFedPreset.SLOPER)

    def new_random_wire_antenna(self) -> None:
        self.new_endfed_antenna(preset=EndFedPreset.RANDOM_WIRE)

    def new_g5rv_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = G5RVDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="G5RV",
        )

    def new_doublet_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = DoubletDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Doublet",
            feed_line=dialog.result_feed_line(),
        )

    def new_fan_dipole_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = FanDipoleDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Fan dipole",
        )

    def new_trap_dipole_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = TrapDipoleDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Trap dipole",
        )

    def new_t2fd_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = T2FDDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="T2FD",
        )

    def new_inverted_v_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = InvertedVDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Inverted V",
        )

    def new_vertical_antenna(self, *, mobile: bool = False) -> None:
        if not self._maybe_save_changes():
            return
        dialog = VerticalDialog(
            self._translator,
            self._unit_system,
            self,
            mobile=mobile,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="Loaded vertical" if mobile else "Vertical",
        )

    def new_loaded_vertical_antenna(self) -> None:
        self.new_vertical_antenna(mobile=True)

    def new_ocfd_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = OCFDDialog(self._translator, self._unit_system, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._create_project_from_parameters(
            dialog.result_parameters(),
            default_name="OCFD",
        )

    @history_action("history.measurement_edit")
    def edit_measurement(self, measurement: Measurement) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        dialog = MeasurementDetailsDialog(
            self._translator,
            measurement.name,
            self,
            measurement=measurement,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            updated = replace(
                measurement,
                name=dialog.name() or measurement.name,
                calibration=dialog.calibration(),
                reference_plane=dialog.reference_plane(),
                feed_line=dialog.feed_line(),
                notes=dialog.notes(),
            )
            self._project = self._project.with_updated_measurement(
                updated,
                updated_at=utc_now(),
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.measurement", message=str(exc)))
            return
        self._dirty = True
        self._results.set_measurements(self._project.measurements)
        self._tabs_select_measurements()
        self._last_status_key = "status.measurement_updated"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    @history_action("history.measurement_delete")
    def delete_measurement(self, measurement: Measurement) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        answer = QMessageBox.question(
            self,
            self._translator.t("measurement.delete_title"),
            self._translator.t("measurement.delete_confirm", name=measurement.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self._project = self._project.without_measurement(
                measurement.id,
                updated_at=utc_now(),
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.measurement", message=str(exc)))
            return
        self._dirty = True
        self._results.set_measurements(self._project.measurements)
        self._tabs_select_measurements()
        self._last_status_key = "status.measurement_deleted"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    @history_action("history.measurement_import")
    def import_vna_csv(self) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self._translator.t("dialog.vna_title"),
            str(Path.home()),
            self._translator.t("dialog.vna_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        try:
            parsed = parse_vna_csv(path.read_text(encoding="utf-8", errors="replace"))
            details = MeasurementDetailsDialog(self._translator, path.stem, self)
            if details.exec() != QDialog.DialogCode.Accepted:
                return
            measurement = Measurement(
                id=uuid4(),
                name=details.name() or path.stem,
                created_at=utc_now(),
                reference_impedance_ohm=parsed.reference_impedance_ohm,
                points=parsed.points,
                source=str(path),
                calibration=details.calibration(),
                reference_plane=details.reference_plane(),
                feed_line=details.feed_line(),
                notes=details.notes(),
            )
            self._project = self._project.with_measurement(
                measurement,
                updated_at=utc_now(),
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.import_vna", message=str(exc)))
            return
        self._dirty = True
        self._results.set_measurements(self._project.measurements)
        self._tabs_select_measurements()
        self._update_title()
        self._update_actions()
        self._update_status_text()
        if parsed.warnings:
            QMessageBox.warning(
                self,
                self._translator.t("dialog.vna_title"),
                self._translator.t(
                    "dialog.vna_warnings",
                    count=len(parsed.warnings),
                    details="\n".join(parsed.warnings[:12]),
                ),
            )

    def _tabs_select_measurements(self) -> None:
        self._results.show_measurements()

    def import_nec_deck(self) -> None:
        if not self._maybe_save_changes():
            return
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self._translator.t("dialog.nec_title"),
            str(Path.home()),
            self._translator.t("dialog.nec_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        try:
            result = parse_nec2_deck(path.read_text(encoding="utf-8", errors="strict"))
            project = CreateDipoleProject().execute(
                CreateDipoleProjectCommand(
                    project_name=path.stem,
                    variant_name="Imported",
                    parameters=result.parameters,
                )
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.import_nec", message=str(exc)))
            return
        self._set_project(project, project.designs[0].id, path=None, dirty=True)
        if result.warnings:
            QMessageBox.warning(
                self,
                self._translator.t("dialog.nec_title"),
                self._translator.t(
                    "dialog.nec_warnings",
                    count=len(result.warnings),
                    details="\n".join(result.warnings[:12]),
                ),
            )

    def import_mmana_file(self) -> None:
        if not self._maybe_save_changes():
            return
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self._translator.t("dialog.mmana_title"),
            str(Path.home()),
            self._translator.t("dialog.mmana_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        try:
            result = parse_mmana_file(path.read_text(encoding="utf-8", errors="strict"))
            project = CreateDipoleProject().execute(
                CreateDipoleProjectCommand(
                    project_name=path.stem,
                    variant_name="Imported",
                    parameters=result.parameters,
                )
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.import_mmana", message=str(exc)))
            return
        self._set_project(project, project.designs[0].id, path=None, dirty=True)
        if result.warnings:
            QMessageBox.warning(
                self,
                self._translator.t("dialog.mmana_title"),
                self._translator.t(
                    "dialog.mmana_warnings",
                    count=len(result.warnings),
                    details="\n".join(result.warnings[:12]),
                ),
            )

    @history_action("history.convert_custom")
    def convert_to_custom_wires(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        if isinstance(design.parameters, CustomAntennaParameters):
            return
        try:
            parameters = CustomAntennaParameters(
                frequency_hz=design.parameters.frequency_hz,
                wires=design.antenna.wires,
                feed=design.antenna.feed,
                ground=design.antenna.environment.ground,
                loads=design.antenna.loads,
                transmission_lines=design.antenna.transmission_lines,
            )
            updated_design = design.with_parameters(parameters)
            self._project = self._project.with_design(updated_design, updated_at=utc_now())
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._loads = updated_design.antenna.loads
        self._form_dirty = False
        self._dirty = True
        self._invalidate_design_result(self._design_id)
        self._results.set_result(None)
        self._results.set_design(updated_design)
        self._set_geometry_model(updated_design)
        self._design_stack.setCurrentWidget(self._custom_panel)
        self._update_custom_panel(updated_design)
        self._last_status_key = "status.design_changed"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    @history_action("history.edit_generator")
    def edit_generator(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        parameters = design.parameters
        if not isinstance(parameters, CustomAntennaParameters):
            return
        if parameters.generator_id == "inverted_v":
            dialog: QDialog = InvertedVDialog(
                self._translator,
                self._unit_system,
                self,
                parameters=InvertedVParameters.from_custom_parameters(parameters),
            )
        elif parameters.generator_id == "ocfd":
            dialog = OCFDDialog(
                self._translator,
                self._unit_system,
                self,
                parameters=OCFDParameters.from_custom_parameters(parameters),
            )
        elif parameters.generator_id == "yagi":
            dialog = YagiDialog(
                self._translator,
                self._unit_system,
                self,
                parameters=YagiParameters.from_custom_parameters(parameters),
            )
        elif parameters.generator_id == "vertical":
            dialog = VerticalDialog(
                self._translator,
                self._unit_system,
                self,
                parameters=VerticalParameters.from_custom_parameters(parameters),
            )
        else:
            return
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            updated_design = design.with_parameters(dialog.result_parameters())
            self._project = self._project.with_design(updated_design, updated_at=utc_now())
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._loads = updated_design.antenna.loads
        self._form_dirty = False
        self._dirty = True
        self._invalidate_design_result(self._design_id)
        self._results.set_result(None)
        self._results.set_design(updated_design)
        self._set_geometry_model(updated_design)
        self._design_stack.setCurrentWidget(self._custom_panel)
        self._update_custom_panel(updated_design)
        self._auto_select_view(updated_design)
        self._last_status_key = "status.design_changed"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    @history_action("history.edit_custom")
    def edit_custom_wires(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        if not isinstance(design.parameters, CustomAntennaParameters):
            self._show_error(
                self._translator.t("error.invalid_design", message="not a custom antenna")
            )
            return
        dialog = CustomAntennaDialog(
            self._translator,
            self._unit_system,
            design.parameters,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            updated_design = design.with_parameters(dialog.result_parameters())
            self._project = self._project.with_design(updated_design, updated_at=utc_now())
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._loads = updated_design.antenna.loads
        self._form_dirty = False
        self._dirty = True
        self._invalidate_design_result(self._design_id)
        self._results.set_result(None)
        self._results.set_design(updated_design)
        self._set_geometry_model(updated_design)
        self._update_custom_panel(updated_design)
        self._update_title()
        self._update_actions()

    def _parameters_from_catalog(
        self,
        selected: str,
        frequency_hz: float,
    ) -> AntennaDesignParameters | None:
        if selected in {
            CATALOG_TYPE_WIRE_DIPOLE,
            CATALOG_TYPE_FOLDED_DIPOLE,
            CATALOG_TYPE_LOOP,
            CATALOG_TYPE_DELTA_LOOP,
            CATALOG_TYPE_QUAD_LOOP,
        }:
            antenna_type = (
                CATALOG_TYPE_LOOP
                if selected in {CATALOG_TYPE_DELTA_LOOP, CATALOG_TYPE_QUAD_LOOP}
                else selected
            )
            initial_sides = {
                CATALOG_TYPE_DELTA_LOOP: 3,
                CATALOG_TYPE_QUAD_LOOP: 4,
            }.get(selected)
            wizard = DipoleWizard(
                self._translator,
                self._unit_system,
                initial_frequency_hz=frequency_hz,
                initial_antenna_type=antenna_type,
                initial_sides=initial_sides,
                parent=self,
            )
            if wizard.exec() != QWizard.DialogCode.Accepted:
                return None
            return wizard.build_parameters()
        if selected == CATALOG_TYPE_MOXON:
            dialog = MoxonDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected == CATALOG_TYPE_YAGI:
            dialog = YagiDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            return (
                dialog.result_parameters() if dialog.exec() == QDialog.DialogCode.Accepted else None
            )
        if selected == CATALOG_TYPE_RINGO:
            dialog = RingoDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected in {CATALOG_TYPE_J_POLE, CATALOG_TYPE_SLIM_JIM}:
            dialog = JPoleDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            parameters = dialog.result_parameters()
            if selected == CATALOG_TYPE_SLIM_JIM:
                parameters = replace(parameters, folded=True)
            return parameters
        if selected == CATALOG_TYPE_ENDFED:
            dialog = EndFedDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected in {CATALOG_TYPE_SLOPER, CATALOG_TYPE_RANDOM_WIRE}:
            preset = (
                EndFedPreset.SLOPER if selected == CATALOG_TYPE_SLOPER else EndFedPreset.RANDOM_WIRE
            )
            dialog = EndFedDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
                preset=preset,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected == CATALOG_TYPE_G5RV:
            dialog = G5RVDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected == CATALOG_TYPE_DOUBLET:
            dialog = DoubletDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected == CATALOG_TYPE_FAN_DIPOLE:
            dialog = FanDipoleDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected == CATALOG_TYPE_TRAP_DIPOLE:
            dialog = TrapDipoleDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected == CATALOG_TYPE_T2FD:
            dialog = T2FDDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected == CATALOG_TYPE_INVERTED_V:
            dialog = InvertedVDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            return (
                dialog.result_parameters() if dialog.exec() == QDialog.DialogCode.Accepted else None
            )
        if selected == CATALOG_TYPE_OCFD:
            dialog = OCFDDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return None
            return dialog.result_parameters()
        if selected in {CATALOG_TYPE_VERTICAL, CATALOG_TYPE_LOADED_VERTICAL}:
            dialog = VerticalDialog(
                self._translator,
                self._unit_system,
                self,
                frequency_hz=frequency_hz,
                mobile=selected == CATALOG_TYPE_LOADED_VERTICAL,
            )
            return (
                dialog.result_parameters() if dialog.exec() == QDialog.DialogCode.Accepted else None
            )
        if selected == CATALOG_TYPE_CUSTOM:
            dialog = CustomAntennaDialog(
                self._translator,
                self._unit_system,
                parent=self,
                frequency_hz=frequency_hz,
            )
            return (
                dialog.result_parameters() if dialog.exec() == QDialog.DialogCode.Accepted else None
            )
        return None

    @history_action("history.change_template")
    def change_template(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if not self._maybe_save_changes():
            return
        design = self._project.design_by_id(self._design_id)
        catalog = AntennaCatalogDialog(
            self._translator,
            self,
            initial_key=catalog_key_for(design.parameters),
        )
        if catalog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = catalog.selected_key()
        if selected is None:
            return
        feed_line = None
        try:
            if selected == CATALOG_TYPE_DOUBLET:
                dialog = DoubletDialog(
                    self._translator,
                    self._unit_system,
                    self,
                    frequency_hz=design.parameters.frequency_hz,
                    feed_line=self._feed_line,
                )
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    return
                parameters = dialog.parameters()
                feed_line = dialog.feed_line()
            else:
                parameters = self._parameters_from_catalog(
                    selected,
                    design.parameters.frequency_hz,
                )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        if parameters is None:
            return
        answer = QMessageBox.question(
            self,
            self._translator.t("dialog.change_template_title"),
            self._translator.t("dialog.change_template_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            updated_design = design.with_parameters(parameters)
            timestamp = utc_now()
            self._project = self._project.with_design(updated_design, updated_at=timestamp)
            if feed_line is not None:
                self._project = self._project.with_feed_line(
                    feed_line,
                    updated_at=timestamp,
                )
                self._feed_line = feed_line
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._invalidate_design_result(self._design_id)
        self._dirty = True
        self._select_design(self._design_id)
        self._last_status_key = "status.design_changed"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    def new_antenna(self) -> None:
        dialog = AntennaCatalogDialog(self._translator, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_key()
        if selected == CATALOG_TYPE_CUSTOM:
            self.new_custom_antenna()
        elif selected == CATALOG_TYPE_YAGI:
            self.new_yagi_antenna()
        elif selected == CATALOG_TYPE_MOXON:
            self.new_moxon_antenna()
        elif selected == CATALOG_TYPE_INVERTED_V:
            self.new_inverted_v_antenna()
        elif selected == CATALOG_TYPE_FAN_DIPOLE:
            self.new_fan_dipole_antenna()
        elif selected == CATALOG_TYPE_TRAP_DIPOLE:
            self.new_trap_dipole_antenna()
        elif selected == CATALOG_TYPE_T2FD:
            self.new_t2fd_antenna()
        elif selected == CATALOG_TYPE_ENDFED:
            self.new_endfed_antenna()
        elif selected == CATALOG_TYPE_SLOPER:
            self.new_sloper_antenna()
        elif selected == CATALOG_TYPE_RANDOM_WIRE:
            self.new_random_wire_antenna()
        elif selected == CATALOG_TYPE_DOUBLET:
            self.new_doublet_antenna()
        elif selected == CATALOG_TYPE_G5RV:
            self.new_g5rv_antenna()
        elif selected == CATALOG_TYPE_J_POLE:
            self.new_j_pole_antenna(folded=False)
        elif selected == CATALOG_TYPE_SLIM_JIM:
            self.new_j_pole_antenna(folded=True)
        elif selected == CATALOG_TYPE_RINGO:
            self.new_ringo_antenna()
        elif selected == CATALOG_TYPE_OCFD:
            self.new_ocfd_antenna()
        elif selected == CATALOG_TYPE_DELTA_LOOP:
            self._new_basic_antenna(CATALOG_TYPE_LOOP, initial_sides=3)
        elif selected == CATALOG_TYPE_QUAD_LOOP:
            self._new_basic_antenna(CATALOG_TYPE_LOOP, initial_sides=4)
        elif selected == CATALOG_TYPE_VERTICAL:
            self.new_vertical_antenna()
        elif selected == CATALOG_TYPE_LOADED_VERTICAL:
            self.new_loaded_vertical_antenna()
        elif selected in {
            CATALOG_TYPE_WIRE_DIPOLE,
            CATALOG_TYPE_FOLDED_DIPOLE,
            CATALOG_TYPE_LOOP,
        }:
            self._new_basic_antenna(selected)

    def _new_basic_antenna(
        self,
        antenna_type: str,
        *,
        initial_sides: int | None = None,
    ) -> None:
        if not self._maybe_save_changes():
            return
        initial_frequency = 7_100_000.0
        if self._project is not None and self._design_id is not None:
            initial_frequency = self._project.design_by_id(self._design_id).parameters.frequency_hz
        wizard = DipoleWizard(
            self._translator,
            self._unit_system,
            initial_frequency_hz=initial_frequency,
            initial_antenna_type=antenna_type,
            initial_sides=initial_sides,
            parent=self,
        )
        if wizard.exec() != QWizard.DialogCode.Accepted:
            return
        try:
            parameters = wizard.build_parameters()
            project = CreateDipoleProject().execute(
                CreateDipoleProjectCommand(
                    project_name=wizard.project_name(),
                    variant_name="Initial",
                    parameters=parameters,
                )
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._set_project(
            project,
            project.designs[0].id,
            path=None,
            dirty=True,
        )

    def new_dipole(self) -> None:
        self.new_antenna()

    def open_project(self) -> None:
        if not self._maybe_save_changes():
            return
        start = (
            str(self._current_path.parent) if self._current_path is not None else str(Path.home())
        )
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self._translator.t("dialog.open_title"),
            start,
            self._translator.t("dialog.project_filter"),
        )
        if not filename:
            return
        try:
            project = OpenProject(self._repository).execute(Path(filename))
            if not project.designs:
                raise ValueError("project has no designs")
        except Exception as exc:
            self._show_error(self._translator.t("error.open", message=str(exc)))
            return
        self._set_project(
            project,
            project.designs[0].id,
            path=Path(filename),
            dirty=False,
        )
        self._last_status_key = "status.opened"
        self._update_status_text()

    def save_project(self) -> bool:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return False
        if self._current_path is None:
            return self.save_project_as()
        return self._save_to(self._current_path)

    def save_project_as(self) -> bool:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return False
        safe_name = self._project.name.replace("/", "-").replace("\\", "-")
        suggested = f"{safe_name}.antennadesk"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.save_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.project_filter"),
        )
        if not filename:
            return False
        path = Path(filename)
        if path.suffix.lower() != ".antennadesk":
            path = path.with_suffix(".antennadesk")
        return self._save_to(path)

    def _save_to(self, path: Path) -> bool:
        before = self._history_snapshot()
        try:
            project = self._apply_fields()
            after = self._history_snapshot()
            self._record_history("history.save", before, after)
            size = self._repository.serialized_size(project)
            if size > MAX_PROJECT_SIZE_BYTES:
                self._show_error(
                    self._translator.t(
                        "dialog.project_too_large",
                        size=size / (1024 * 1024),
                        limit=MAX_PROJECT_SIZE_BYTES / (1024 * 1024),
                    )
                )
                return False
            if size > PROJECT_SIZE_WARNING_BYTES:
                answer = QMessageBox.warning(
                    self,
                    self._translator.t("app.title"),
                    self._translator.t(
                        "dialog.large_project",
                        size=size / (1024 * 1024),
                    ),
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Save,
                )
                if answer != QMessageBox.StandardButton.Save:
                    return False
            SaveProject(self._repository).execute(project, path)
        except Exception as exc:
            self._show_error(self._translator.t("error.save", message=str(exc)))
            return False
        self._current_path = path
        self._dirty = False
        self._form_dirty = False
        self._clean_signature = self._current_project_signature()
        self._clean_run_ids = self._current_run_ids()
        self._undo_stack.setClean()
        self._update_title()
        self._update_actions()
        self._last_status_key = "status.saved"
        self._update_status_text()
        return True

    def _maybe_save_changes(self) -> bool:
        if not self._dirty:
            return True
        answer = QMessageBox.question(
            self,
            self._translator.t("app.title"),
            self._translator.t("dialog.save_changes"),
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Save:
            return self.save_project()
        return answer == QMessageBox.StandardButton.Discard

    @history_action("history.new_variant")
    def new_variant(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        source = self._project.design_by_id(self._design_id)
        default_name = self._unique_variant_name(
            self._translator.t("variant.copy_name", name=source.name)
        )
        name, accepted = QInputDialog.getText(
            self,
            self._translator.t("variant.new_title"),
            self._translator.t("variant.name"),
            text=default_name,
        )
        if not accepted:
            return
        try:
            updated = AddDesignVariant().execute(
                AddDesignVariantCommand(
                    project=self._project,
                    source_design_id=source.id,
                    name=name,
                )
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        new_id = updated.designs[-1].id
        self._project = updated
        self._dirty = True
        self._populate_variants(new_id)
        self._select_design(new_id)
        self._update_title()
        self._update_actions()

    @history_action("history.rename_variant")
    def rename_variant(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        name, accepted = QInputDialog.getText(
            self,
            self._translator.t("variant.rename_title"),
            self._translator.t("variant.name"),
            text=design.name,
        )
        if not accepted:
            return
        try:
            updated = RenameDesignVariant().execute(
                RenameDesignVariantCommand(
                    project=self._project,
                    design_id=design.id,
                    name=name,
                )
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._project = updated
        self._dirty = True
        self._populate_variants(self._design_id)
        self._update_title()
        self._update_actions()

    @history_action("history.delete_variant")
    def delete_variant(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if len(self._project.designs) <= 1:
            self._show_error(self._translator.t("variant.last_cannot_delete"))
            return
        design = self._project.design_by_id(self._design_id)
        answer = QMessageBox.question(
            self,
            self._translator.t("variant.delete_title"),
            self._translator.t("variant.delete_confirm", name=design.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            updated = DeleteDesignVariant().execute(
                DeleteDesignVariantCommand(
                    project=self._project,
                    design_id=design.id,
                )
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._invalidate_design_result(design.id)
        self._project = updated
        self._dirty = True
        new_id = updated.designs[0].id
        self._populate_variants(new_id)
        self._select_design(new_id)
        self._update_title()
        self._update_actions()

    @history_action("history.design_from_frequency")
    def design_from_frequency(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        if not supports_estimation(design.parameters):
            self._show_error(self._estimate_unavailable_message(design.parameters))
            return
        dialog = DesignFromFrequencyDialog(
            self._translator,
            self._unit_system,
            initial_parameters=design.parameters,
            can_refine=self._solver is not None,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            estimate = dialog.estimated_estimate()
            parameters = self._preserve_estimate_context(
                design.parameters,
                estimate.parameters,
            )
            provenance = DesignProvenance(
                method_id=estimate.method_id,
                confidence=estimate.confidence.value,
                assumptions=estimate.assumptions,
                warnings=estimate.warnings,
                tolerance_m=estimate.tolerance_m,
                source_ids=estimate.source_ids,
            )
            updated_design = design.with_parameters(parameters, provenance=provenance)
            self._project = self._project.with_design(updated_design, updated_at=utc_now())
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._invalidate_design_result(self._design_id)
        self._dirty = True
        self._select_design(self._design_id)
        self._last_status_key = "status.design_estimated"
        self._update_title()
        self._update_actions()
        self._update_status_text()
        refine_requested = getattr(dialog, "refine_requested", lambda: False)()
        if refine_requested and self._solver is not None:
            self._open_refinement_for_current_design()

    def _preserve_estimate_context(
        self,
        previous: AntennaDesignParameters,
        estimated: AntennaDesignParameters,
    ) -> AntennaDesignParameters:
        """Keep fields that identify the current template or its matching."""

        if antenna_type_for(previous) != antenna_type_for(estimated):
            raise ValueError(self._translator.t("error.estimate_changes_template"))
        updates: dict[str, object] = {}
        for name in (
            "azimuth_deg",
            "radial_angle_deg",
            "material",
            "ground",
            "wire_radius_m",
            "orientation",
        ):
            if hasattr(previous, name) and hasattr(estimated, name):
                updates[name] = getattr(previous, name)
        if isinstance(previous, EndFedParameters) and isinstance(estimated, EndFedParameters):
            updates.update(
                preset=previous.preset,
                transformer_ratio=previous.transformer_ratio,
                counterpoise_length_m=previous.counterpoise_length_m,
                counterpoise_height_m=previous.counterpoise_height_m,
                counterpoise_azimuth_deg=previous.counterpoise_azimuth_deg,
            )
        elif isinstance(previous, OCFDParameters) and isinstance(estimated, OCFDParameters):
            updates.update(
                feed_ratio=previous.feed_ratio,
                transformer_ratio=previous.transformer_ratio,
            )
        elif isinstance(previous, JPoleParameters) and isinstance(estimated, JPoleParameters):
            updates.update(folded=previous.folded, gap_m=previous.gap_m)
        elif isinstance(previous, RingoParameters) and isinstance(estimated, RingoParameters):
            updates["ring_sides"] = previous.ring_sides
        elif isinstance(previous, YagiParameters) and isinstance(estimated, YagiParameters):
            updates["driven_index"] = previous.driven_index
            if previous.elements and estimated.elements:
                radius_m = previous.elements[0].radius_m
                estimated = replace(
                    estimated,
                    elements=tuple(
                        replace(element, radius_m=radius_m) for element in estimated.elements
                    ),
                )
        return replace(estimated, **updates)

    def _open_refinement_for_current_design(self) -> None:
        self.optimize_current_design()

    @history_action("history.optimize")
    def optimize_current_design(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        parameters = self._project.design_by_id(self._design_id).parameters
        if isinstance(parameters, (OCFDParameters, JPoleParameters)):
            self.synthesize_dimensions()
        elif isinstance(parameters, YagiParameters):
            self.optimize_yagi_elements()
        elif isinstance(parameters, FanDipoleParameters):
            self.optimize_fan_dipole_elements()
        elif isinstance(parameters, MoxonParameters):
            self.optimize_moxon_elements()
        elif isinstance(parameters, VerticalParameters):
            self.optimize_vertical_elements()
        elif isinstance(parameters, InvertedVParameters):
            self.optimize_inverted_v_elements()
        elif isinstance(parameters, RingoParameters):
            self.optimize_ringo_elements()
        elif isinstance(parameters, LoopParameters):
            self.optimize_loop_elements()
        elif isinstance(parameters, CustomAntennaParameters):
            self._show_error(self._translator.t("error.optimize_custom"))
        else:
            self.optimize_length()

    @history_action("history.optimize")
    def optimize_length(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        if isinstance(design.parameters, OCFDParameters):
            base_spec = self._ocfd_simulation_spec(design.parameters)
        elif isinstance(design.parameters, EndFedParameters):
            base_spec = self._endfed_simulation_spec(design.parameters)
        elif isinstance(design.parameters, TrapDipoleParameters):
            base_spec = self._trap_dipole_simulation_spec(design.parameters)
        elif isinstance(design.parameters, T2FDParameters):
            base_spec = self._t2fd_simulation_spec(design.parameters)
        else:
            base_spec = self._form.simulation_spec()
        base_spec = replace(
            base_spec,
            feed_line=self._feed_line,
            matching_network=self._matching_network,
        )
        dialog = OptimizationDialog(
            self._translator,
            self._unit_system,
            self._solver,
            design.parameters,
            base_spec,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        dimension = dialog.selected_dimension_m()
        if dimension is None:
            return
        try:
            parameters = with_primary_dimension(design.parameters, dimension)
            if isinstance(parameters, OCFDParameters):
                self._ocfd_form.set_parameters(parameters)
            elif isinstance(parameters, EndFedParameters):
                self._endfed_form.set_parameters(parameters)
            elif isinstance(parameters, TrapDipoleParameters):
                self._trap_dipole_form.set_parameters(parameters)
            elif isinstance(parameters, T2FDParameters):
                self._t2fd_form.set_parameters(parameters)
            else:
                self._form.set_parameters(parameters, reset_sweep=False)
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    @history_action("history.optimize")
    def synthesize_dimensions(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        if isinstance(design.parameters, OCFDParameters):
            base_spec = self._ocfd_simulation_spec(design.parameters)
        elif isinstance(design.parameters, JPoleParameters):
            base_spec = self._j_pole_simulation_spec(design.parameters)
        else:
            return
        dialog = SynthesisDialog(
            self._translator,
            self._unit_system,
            self._solver,
            design.parameters,
            replace(
                base_spec,
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            ),
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        parameters = dialog.selected_parameters()
        if parameters is None:
            return
        try:
            if isinstance(parameters, OCFDParameters):
                self._ocfd_form.set_parameters(parameters)
            elif isinstance(parameters, JPoleParameters):
                self._j_pole_form.set_parameters(parameters)
            else:
                return
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    @history_action("history.optimize")
    def optimize_yagi_elements(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        if not isinstance(design.parameters, YagiParameters):
            return
        parameters = design.parameters
        elements = parameters.elements
        minimum_elements = max(MIN_YAGI_ELEMENTS, parameters.driven_index + 1)
        maximum_elements = max(len(elements), MAX_YAGI_ELEMENTS)
        variables = []
        if maximum_elements > minimum_elements:
            variables.append(
                ElementOptimizationVariable(
                    "element_count",
                    self._translator.t("yagi.element_count"),
                    float(len(elements)),
                    integer=True,
                    minimum=float(minimum_elements),
                    maximum=float(maximum_elements),
                )
            )
        for index, element in enumerate(elements):
            variables.append(
                ElementOptimizationVariable(
                    f"length_{index}",
                    f"{self._translator.t('yagi.element')} {index + 1} · "
                    f"{self._translator.t('yagi.length')}",
                    element.length_m,
                )
            )
        for index in range(1, len(elements)):
            variables.append(
                ElementOptimizationVariable(
                    f"gap_{index}",
                    f"{self._translator.t('yagi.element')} {index + 1} · "
                    f"{self._translator.t('yagi_optimize.current_gap')}",
                    elements[index].position_m - elements[index - 1].position_m,
                    minimum=YAGI_OPTIMIZATION_MIN_GAP_M,
                )
            )

        def build(values: dict[str, float]) -> YagiParameters:
            frequency_hz = values.get("__frequency_hz", parameters.frequency_hz)
            count = round(values.get("element_count", len(elements)))
            resized = resize_yagi(
                replace(parameters, frequency_hz=frequency_hz),
                count,
            )
            updated = list(resized.elements)
            for index in range(min(len(updated), len(elements))):
                if (name := f"length_{index}") in values:
                    updated[index] = replace(updated[index], length_m=values[name])
            positions = [updated[0].position_m]
            for index in range(1, len(updated)):
                default_gap = updated[index].position_m - updated[index - 1].position_m
                positions.append(positions[-1] + values.get(f"gap_{index}", default_gap))
            updated = [
                replace(element, position_m=positions[index])
                for index, element in enumerate(updated)
            ]
            return replace(resized, elements=tuple(updated))

        dialog = ElementOptimizationDialog(
            self._translator,
            self._unit_system,
            self._solver,
            replace(
                self._yagi_simulation_spec(parameters),
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            ),
            title_key="element_optimize.yagi_title",
            hint_key="element_optimize.yagi_hint",
            variables=tuple(variables),
            build_parameters=build,
            objectives=(
                ElementOptimizationObjective.TARGET_IMPEDANCE,
                ElementOptimizationObjective.MAX_GAIN,
                ElementOptimizationObjective.MAX_FRONT_TO_BACK,
                ElementOptimizationObjective.MULTI_OBJECTIVE,
            ),
            default_frequency_hz=parameters.frequency_hz,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        parameters = dialog.selected_parameters()
        if parameters is None:
            return
        try:
            self._yagi_form.set_parameters(parameters)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    @history_action("history.optimize")
    def optimize_fan_dipole_elements(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        if not isinstance(design.parameters, FanDipoleParameters):
            return
        parameters = design.parameters
        elements = parameters.elements
        bands: dict[str, ElementOptimizationBand] = {}
        variables: list[ElementOptimizationVariable] = []
        for index, element in enumerate(elements):
            frequency_hz = frequency_for_half_wave_length(element.length_m)
            band = amateur_band_for(frequency_hz, tolerance_fraction=0.01)
            band_id = band.name if band is not None else None
            if band is not None:
                bands[band.name] = ElementOptimizationBand(
                    band_id=band.name,
                    label=band.name,
                    frequency_hz=frequency_hz,
                )
            variables.append(
                ElementOptimizationVariable(
                    f"length_{index}",
                    f"{self._translator.t('yagi.element')} {index + 1} · "
                    f"{self._translator.t('yagi.length')}",
                    element.length_m,
                    band_id=band_id,
                )
            )

        selected_band_id = self._selected_band_ids.get(design.id)
        if selected_band_id not in bands:
            selected_band_id = None
        if selected_band_id is not None:
            default_frequency_hz = bands[selected_band_id].frequency_hz
        elif bands:
            default_frequency_hz = min(
                bands.values(),
                key=lambda band: band.frequency_hz,
            ).frequency_hz
        else:
            default_frequency_hz = parameters.frequency_hz

        def build(values: dict[str, float]) -> FanDipoleParameters:
            updated = list(elements)
            for index in range(len(updated)):
                if (name := f"length_{index}") in values:
                    updated[index] = replace(updated[index], length_m=values[name])
            return replace(
                parameters,
                frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
                elements=tuple(updated),
            )

        dialog = ElementOptimizationDialog(
            self._translator,
            self._unit_system,
            self._solver,
            replace(
                self._fan_dipole_simulation_spec(parameters),
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            ),
            title_key="element_optimize.fan_title",
            variables=tuple(variables),
            build_parameters=build,
            objectives=(
                ElementOptimizationObjective.TARGET_IMPEDANCE,
                ElementOptimizationObjective.MAX_GAIN,
                ElementOptimizationObjective.MAX_FRONT_TO_BACK,
                ElementOptimizationObjective.MULTI_OBJECTIVE,
            ),
            default_frequency_hz=default_frequency_hz,
            bands=tuple(sorted(bands.values(), key=lambda band: band.frequency_hz)),
            default_band_id=selected_band_id,
            hint_key="element_optimize.fan_hint",
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        parameters = dialog.selected_parameters()
        if parameters is None:
            return
        try:
            self._fan_dipole_form.set_parameters(parameters)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    @history_action("history.optimize")
    def optimize_moxon_elements(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        if not isinstance(design.parameters, MoxonParameters):
            return
        parameters = design.parameters
        variables = (
            ElementOptimizationVariable(
                "width_m", self._translator.t("moxon.width"), parameters.width_m
            ),
            ElementOptimizationVariable(
                "depth_m", self._translator.t("moxon.depth"), parameters.depth_m
            ),
            ElementOptimizationVariable(
                "reflector_tip_m",
                self._translator.t("moxon.reflector_tip"),
                parameters.reflector_tip_m,
            ),
            ElementOptimizationVariable(
                "driven_tip_m",
                self._translator.t("moxon.driven_tip"),
                parameters.driven_tip_m,
            ),
        )

        def build(values: dict[str, float]) -> MoxonParameters:
            return replace(
                parameters,
                frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
                width_m=values.get("width_m", parameters.width_m),
                depth_m=values.get("depth_m", parameters.depth_m),
                reflector_tip_m=values.get("reflector_tip_m", parameters.reflector_tip_m),
                driven_tip_m=values.get("driven_tip_m", parameters.driven_tip_m),
            )

        dialog = ElementOptimizationDialog(
            self._translator,
            self._unit_system,
            self._solver,
            replace(
                self._moxon_simulation_spec(parameters),
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            ),
            title_key="element_optimize.moxon_title",
            variables=variables,
            build_parameters=build,
            objectives=(
                ElementOptimizationObjective.TARGET_IMPEDANCE,
                ElementOptimizationObjective.MAX_GAIN,
                ElementOptimizationObjective.MAX_FRONT_TO_BACK,
                ElementOptimizationObjective.MULTI_OBJECTIVE,
            ),
            default_frequency_hz=parameters.frequency_hz,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        parameters = dialog.selected_parameters()
        if parameters is None:
            return
        try:
            self._moxon_form.set_parameters(parameters)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    @history_action("history.optimize")
    def optimize_loop_elements(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        design = self._project.design_by_id(self._design_id)
        if not isinstance(design.parameters, LoopParameters):
            return
        parameters = design.parameters
        variables = (
            ElementOptimizationVariable(
                "circumference_m",
                self._translator.t("field.circumference"),
                parameters.circumference_m,
            ),
        )

        def build(values: dict[str, float]) -> LoopParameters:
            return replace(
                parameters,
                frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
                circumference_m=values.get("circumference_m", parameters.circumference_m),
            )

        dialog = ElementOptimizationDialog(
            self._translator,
            self._unit_system,
            self._solver,
            replace(
                self._form.simulation_spec(),
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            ),
            title_key="element_optimize.loop_title",
            hint_key="element_optimize.loop_hint",
            variables=variables,
            build_parameters=build,
            objectives=(
                ElementOptimizationObjective.TARGET_IMPEDANCE,
                ElementOptimizationObjective.MAX_GAIN,
                ElementOptimizationObjective.MAX_FRONT_TO_BACK,
                ElementOptimizationObjective.MULTI_OBJECTIVE,
            ),
            default_frequency_hz=parameters.frequency_hz,
            default_target_resistance_ohm=100.0,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_parameters()
        if selected is None:
            return
        self._form.set_parameters(selected, reset_sweep=False)
        self._form_dirty = True
        self._apply_fields()
        self.simulate()

    @history_action("history.optimize")
    def optimize_vertical_elements(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        design = self._project.design_by_id(self._design_id)
        if not isinstance(design.parameters, VerticalParameters):
            return
        parameters = design.parameters
        variables = [
            ElementOptimizationVariable(
                "height_m", self._translator.t("field.height"), parameters.height_m
            )
        ]
        if parameters.radial_count > 0:
            variables.append(
                ElementOptimizationVariable(
                    "radial_length_m",
                    self._translator.t("vertical.radial_length"),
                    parameters.radial_length_m,
                )
            )
            variables.append(
                ElementOptimizationVariable(
                    "radial_count",
                    self._translator.t("vertical.radial_count"),
                    float(parameters.radial_count),
                    integer=True,
                )
            )

        def build(values: dict[str, float]) -> VerticalParameters:
            return replace(
                parameters,
                frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
                height_m=values.get("height_m", parameters.height_m),
                radial_length_m=values.get("radial_length_m", parameters.radial_length_m),
                radial_count=round(values.get("radial_count", parameters.radial_count)),
            )

        dialog = ElementOptimizationDialog(
            self._translator,
            self._unit_system,
            self._solver,
            replace(
                self._vertical_simulation_spec(parameters),
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            ),
            title_key="element_optimize.vertical_title",
            variables=tuple(variables),
            build_parameters=build,
            objectives=(
                ElementOptimizationObjective.TARGET_IMPEDANCE,
                ElementOptimizationObjective.MAX_GAIN,
                ElementOptimizationObjective.MAX_FRONT_TO_BACK,
                ElementOptimizationObjective.MULTI_OBJECTIVE,
            ),
            default_frequency_hz=parameters.frequency_hz,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_parameters()
        if selected is None:
            return
        self._vertical_form.set_parameters(selected)
        self._form_dirty = True
        self._apply_fields()
        self.simulate()

    @history_action("history.optimize")
    def optimize_inverted_v_elements(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        design = self._project.design_by_id(self._design_id)
        if not isinstance(design.parameters, InvertedVParameters):
            return
        parameters = design.parameters

        def build(values: dict[str, float]) -> InvertedVParameters:
            return replace(
                parameters,
                frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
                leg_length_m=values.get("leg_length_m", parameters.leg_length_m),
            )

        dialog = ElementOptimizationDialog(
            self._translator,
            self._unit_system,
            self._solver,
            replace(
                self._inverted_v_simulation_spec(parameters),
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            ),
            title_key="element_optimize.inverted_v_title",
            variables=(
                ElementOptimizationVariable(
                    "leg_length_m",
                    self._translator.t("inverted_v.leg_length"),
                    parameters.leg_length_m,
                ),
            ),
            build_parameters=build,
            objectives=(
                ElementOptimizationObjective.TARGET_IMPEDANCE,
                ElementOptimizationObjective.MAX_GAIN,
                ElementOptimizationObjective.MAX_FRONT_TO_BACK,
                ElementOptimizationObjective.MULTI_OBJECTIVE,
            ),
            default_frequency_hz=parameters.frequency_hz,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_parameters()
        if selected is None:
            return
        self._inverted_v_form.set_parameters(selected)
        self._form_dirty = True
        self._apply_fields()
        self.simulate()

    @history_action("history.optimize")
    def optimize_ringo_elements(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        design = self._project.design_by_id(self._design_id)
        if not isinstance(design.parameters, RingoParameters):
            return
        parameters = design.parameters
        variables = (
            ElementOptimizationVariable(
                "radiator_height_m",
                self._translator.t("ringo.radiator_height"),
                parameters.radiator_height_m,
            ),
            ElementOptimizationVariable(
                "ring_diameter_m",
                self._translator.t("ringo.ring_diameter"),
                parameters.ring_diameter_m,
            ),
            ElementOptimizationVariable(
                "ring_sides",
                self._translator.t("ringo.ring_sides"),
                float(parameters.ring_sides),
                integer=True,
            ),
        )

        def build(values: dict[str, float]) -> RingoParameters:
            return replace(
                parameters,
                frequency_hz=values.get("__frequency_hz", parameters.frequency_hz),
                radiator_height_m=values.get("radiator_height_m", parameters.radiator_height_m),
                ring_diameter_m=values.get("ring_diameter_m", parameters.ring_diameter_m),
                ring_sides=round(values.get("ring_sides", parameters.ring_sides)),
            )

        dialog = ElementOptimizationDialog(
            self._translator,
            self._unit_system,
            self._solver,
            replace(
                self._ringo_simulation_spec(parameters),
                feed_line=self._feed_line,
                matching_network=self._matching_network,
            ),
            title_key="element_optimize.ringo_title",
            variables=variables,
            build_parameters=build,
            objectives=(
                ElementOptimizationObjective.TARGET_IMPEDANCE,
                ElementOptimizationObjective.MAX_GAIN,
                ElementOptimizationObjective.MAX_FRONT_TO_BACK,
                ElementOptimizationObjective.MULTI_OBJECTIVE,
            ),
            default_frequency_hz=parameters.frequency_hz,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_parameters()
        if selected is None:
            return
        self._ringo_form.set_parameters(selected)
        self._form_dirty = True
        self._apply_fields()
        self.simulate()

    @history_action("history.loads")
    def edit_loads(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        dialog = LoadsDialog(
            self._translator,
            self._unit_system,
            {wire.id: wire.length_m for wire in design.antenna.wires},
            design.antenna.loads,
            self,
            protected_load_ids=template_load_ids(design.parameters),
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._loads = dialog.loads()
        self._form_dirty = True
        self._dirty = True
        self.apply_design()
        self._last_status_key = "status.design_changed"
        self._update_status_text()

    @history_action("history.transmission_lines")
    def edit_transmission_lines(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        dialog = TransmissionLinesDialog(
            self._translator,
            self._unit_system,
            {wire.id: wire for wire in design.antenna.wires},
            design.antenna.transmission_lines,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._transmission_lines = dialog.transmission_lines()
        self._form_dirty = True
        self._dirty = True
        self.apply_design()
        self._last_status_key = "status.design_changed"
        self._update_status_text()

    def show_construction_sheet(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        result = self._simulation_results.get(self._design_id)
        dialog = ConstructionDialog(
            self._translator,
            self._project,
            design,
            result,
            self,
        )
        dialog.exec()

    def compare_variants(self) -> None:
        if self._project is None or len(self._project.designs) < 2:
            return
        dialog = ComparisonDialog(
            self._translator,
            self._project,
            self._simulation_results,
            self,
            band_analyses=self._band_analysis_results,
        )
        dialog.exec()

    def _current_export_data(
        self,
    ) -> tuple[Project, DesignVariant, SimulationResult] | None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return None
        result = self._simulation_results.get(self._design_id)
        if result is None:
            self._show_error(self._translator.t("error.no_result"))
            return None
        return self._project, self._project.design_by_id(self._design_id), result

    def export_csv(self) -> None:
        data = self._current_export_data()
        if data is None:
            return
        project, design, result = data
        suggested = f"{self._safe_file_name(project.name)}-{self._safe_file_name(design.name)}.csv"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.csv_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.csv_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".csv":
            path = path.with_suffix(".csv")
        analysis = (
            self._band_analysis_results.get(self._design_id)
            if self._design_id is not None
            else None
        )
        try:
            if analysis is not None:
                write_band_analysis_csv(analysis, path)
            else:
                write_csv(result, path)
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def export_pattern_csv(self) -> None:
        data = self._current_export_data()
        if data is None:
            return
        project, design, result = data
        suggested = (
            f"{self._safe_file_name(project.name)}-{self._safe_file_name(design.name)}-pattern.csv"
        )
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.pattern_csv_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.csv_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".csv":
            path = path.with_suffix(".csv")
        analysis = (
            self._band_analysis_results.get(self._design_id)
            if self._design_id is not None
            else None
        )
        try:
            if analysis is not None:
                write_band_analysis_pattern_csv(analysis, path)
            else:
                write_pattern_csv(result, path)
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def export_geometry_png(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        suggested = (
            f"{self._safe_file_name(self._project.name)}-"
            f"{self._safe_file_name(design.name)}-geometry.png"
        )
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.geometry_png_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.png_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".png":
            path = path.with_suffix(".png")
        try:
            self._geometry.save_image(path)
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def export_geometry_svg(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        suggested = (
            f"{self._safe_file_name(self._project.name)}-"
            f"{self._safe_file_name(design.name)}-geometry.svg"
        )
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.geometry_svg_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.svg_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".svg":
            path = path.with_suffix(".svg")
        try:
            self._geometry.save_svg(path)
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def export_geometry_pdf(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        suggested = (
            f"{self._safe_file_name(self._project.name)}-"
            f"{self._safe_file_name(design.name)}-geometry.pdf"
        )
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.geometry_pdf_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.pdf_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".pdf":
            path = path.with_suffix(".pdf")
        try:
            self._geometry.save_pdf(path)
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def export_geometry_dxf(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        suggested = (
            f"{self._safe_file_name(self._project.name)}-"
            f"{self._safe_file_name(design.name)}-geometry.dxf"
        )
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.geometry_dxf_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.dxf_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".dxf":
            path = path.with_suffix(".dxf")
        try:
            self._geometry.save_dxf(path)
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def export_pattern_png(self) -> None:
        data = self._current_export_data()
        if data is None:
            return
        project, design, _result = data
        stem = f"{self._safe_file_name(project.name)}-{self._safe_file_name(design.name)}"
        analysis = (
            self._band_analysis_results.get(self._design_id)
            if self._design_id is not None
            else None
        )
        if analysis is not None and analysis.bands:
            directory = QFileDialog.getExistingDirectory(
                self,
                self._translator.t("dialog.band_pattern_png_title"),
                str(Path.home()),
            )
            if not directory:
                return
            paths = tuple(
                Path(directory) / f"{stem}-{self._safe_file_name(band.band.name)}-pattern.png"
                for band in analysis.bands
            )
            try:
                saved = self._results.save_band_pattern_images(paths)
            except Exception as exc:
                self._show_error(self._translator.t("error.export", message=str(exc)))
                return
            if not saved:
                self._show_error(self._translator.t("error.no_result"))
                return
            self._last_status_key = "status.exported"
            self._update_status_text()
            return

        suggested = f"{stem}-pattern.png"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.pattern_png_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.png_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".png":
            path = path.with_suffix(".png")
        try:
            self._results.save_pattern_image(path)
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def export_html_report(self) -> None:
        data = self._current_export_data()
        if data is None:
            return
        project, design, result = data
        suggested = f"{self._safe_file_name(project.name)}-{self._safe_file_name(design.name)}.html"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.html_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.html_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() not in {".html", ".htm"}:
            path = path.with_suffix(".html")
        analysis = (
            self._band_analysis_results.get(self._design_id)
            if self._design_id is not None
            else None
        )
        try:
            write_html_report(project, design, result, path, band_analysis=analysis)
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def _unique_variant_name(self, base: str) -> str:
        assert self._project is not None
        names = {design.name for design in self._project.designs}
        if base not in names:
            return base
        index = 2
        while f"{base} {index}" in names:
            index += 1
        return f"{base} {index}"

    def compact_simulation_history(self) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if not self._project.has_compactable_simulation_history():
            return
        answer = QMessageBox.question(
            self,
            self._translator.t("app.title"),
            self._translator.t(
                "dialog.compact_history",
                count=len(self._project.simulation_runs),
                keep=self._project.retained_simulation_run_count(),
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._project = self._project.with_latest_simulation_runs_only(updated_at=utc_now())
        self._dirty = True
        self._last_status_key = "status.compacted"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    def export_pdf_report(self) -> None:
        data = self._current_export_data()
        if data is None:
            return
        project, design, result = data
        suggested = f"{self._safe_file_name(project.name)}-{self._safe_file_name(design.name)}.pdf"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.pdf_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.pdf_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".pdf":
            path = path.with_suffix(".pdf")
        analysis = (
            self._band_analysis_results.get(self._design_id)
            if self._design_id is not None
            else None
        )
        try:
            write_report_pdf(
                self._translator,
                project,
                design,
                result,
                path,
                band_analysis=analysis,
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    @staticmethod
    def _safe_file_name(value: str) -> str:
        return value.replace("/", "-").replace("\\", "-").replace(":", "-")

    def locate_solver(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self._translator.t("dialog.solver_title"),
            str(Path.home()),
            self._translator.t("dialog.all_files"),
        )
        if not filename:
            return
        try:
            solver = Nec2cSolver(Path(filename))
            solver.version()
        except Exception as exc:
            self._show_error(self._translator.t("error.solver_start", message=str(exc)))
            return
        self._solver = solver
        self._update_solver_status()
        self._update_actions()

    def _set_language(self, language: Language) -> None:
        self._translator.set_language(language)
        self._english_action.setChecked(language is Language.ENGLISH)
        self._spanish_action.setChecked(language is Language.SPANISH)
        self.retranslate()

    def _set_unit_system(self, unit_system: UnitSystem) -> None:
        self._unit_system = unit_system
        self._metric_action.setChecked(unit_system is UnitSystem.METRIC)
        self._imperial_action.setChecked(unit_system is UnitSystem.IMPERIAL)
        self._form.set_unit_system(unit_system)
        self._geometry.set_unit_system(unit_system)

    def _on_view_mode_changed(self) -> None:
        value = self._view_combo.currentData()
        if not isinstance(value, str):
            return
        mode = GeometryViewMode(value)
        self._geometry.set_view_mode(mode)
        self._update_height_control()

    def _auto_select_view(self, design: DesignVariant) -> None:
        del design
        mode = self._geometry.recommended_mode()
        self._geometry.set_view_mode(mode)
        index = self._view_combo.findData(mode.value)
        if index >= 0 and self._view_combo.currentIndex() != index:
            self._view_combo.blockSignals(True)
            self._view_combo.setCurrentIndex(index)
            self._view_combo.blockSignals(False)
        self._update_height_control()

    def _update_height_control(self) -> None:
        mode = self._view_combo.currentData()
        vertical = False
        multi_wire = False
        if self._project is not None and self._design_id is not None:
            design = self._project.design_by_id(self._design_id)
            multi_wire = len(design.antenna.wires) > 1
            parameters = design.parameters
            if isinstance(
                parameters,
                (DipoleParameters, TrapDipoleParameters, T2FDParameters),
            ):
                vertical = parameters.orientation is DipoleOrientation.VERTICAL
        self._height_combo.setEnabled(
            mode == GeometryViewMode.ELEVATION.value and not vertical and not multi_wire
        )

    def _on_height_scale_changed(self) -> None:
        value = self._height_combo.currentData()
        if isinstance(value, (int, float)):
            self._geometry.set_height_exaggeration(float(value))

    def _on_zoom_changed(self) -> None:
        value = self._zoom_combo.currentData()
        if isinstance(value, (int, float)):
            self._geometry.set_zoom(float(value))

    def _sync_zoom_combo(self, factor: float) -> None:
        index = min(
            range(self._zoom_combo.count()),
            key=lambda item: abs(float(self._zoom_combo.itemData(item)) - factor),
        )
        if index == self._zoom_combo.currentIndex():
            return
        self._zoom_combo.blockSignals(True)
        self._zoom_combo.setCurrentIndex(index)
        self._zoom_combo.blockSignals(False)

    def _on_form_changed(self) -> None:
        if self._project is None or self._simulating:
            return
        self._form_dirty = True
        self._dirty = True
        self._update_title()
        self._update_actions()
        self._refresh_auto_sweep_display()

    def _project_name_changed(self, _text: str) -> None:
        if self._project_name_updating or self._project is None:
            return
        self._dirty = True
        self._update_title()
        self._update_actions()

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            self._translator.t("app.title"),
            self._translator.t("app.about", version=__version__),
        )

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(
            self,
            self._translator.t("app.title"),
            message,
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._simulating:
            QMessageBox.information(
                self,
                self._translator.t("app.title"),
                self._translator.t("dialog.close_simulation"),
            )
            event.ignore()
            return
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait(5_000)
            self._thread = None
            self._worker = None
        if self._maybe_save_changes():
            self._undo_stack.clear()
            event.accept()
        else:
            event.ignore()
