# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main application window."""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any, Literal, cast
from uuid import UUID

from PySide6.QtCore import Qt, QThread, QTimer
from PySide6.QtGui import (
    QAction,
    QActionGroup,
    QCloseEvent,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QFont,
    QKeySequence,
    QUndoStack,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
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
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWhatsThis,
    QWidget,
)

from .. import __version__
from ..application.cancellation import EventCancelToken
from ..application.discretization import resolve_model_quality
from ..application.pattern_planning import (
    fit_band_specs_to_budget,
    fit_spec_to_budget,
    snapshot_frequencies,
)
from ..application.pattern_resolution import (
    DEFAULT_PATTERN_SNAPSHOT_COUNT,
    DEFAULT_PATTERN_STEP_DEG,
    PATTERN_STEPS_DEG,
)
from ..application.ports.antenna_solver import AntennaSolver
from ..application.ports.nec_export import NecDeckExporter, PreflightRunner
from ..application.ports.project_repository import ProjectRepository
from ..application.project_limits import (
    MAX_PROJECT_SIZE_BYTES,
    PROJECT_SIZE_WARNING_BYTES,
)
from ..application.simulation_specs import (
    DEFAULT_GENERATED_SWEEP_POINTS,
    CustomSweepOptions,
    build_typed_family_simulation_spec,
)
from ..application.use_cases.add_design_variant import (
    AddDesignVariant,
    AddDesignVariantCommand,
)
from ..application.use_cases.analyze_bands import BandSimulationRequest
from ..application.use_cases.compare_designs import (
    CompareDesignsCommand,
    ComparisonOutcome,
    ComparisonRun,
)
from ..application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from ..application.use_cases.delete_design_variant import (
    DeleteDesignVariant,
    DeleteDesignVariantCommand,
)
from ..application.use_cases.project_bundle import (
    BUNDLE_EXTENSION,
    BundleExportResult,
    BundleImportResult,
    ExportProjectBundle,
    ImportProjectBundle,
)
from ..application.use_cases.record_simulation_run import (
    RecordSimulationRun,
    RecordSimulationRunCommand,
)
from ..application.use_cases.rename_design_variant import (
    RenameDesignVariant,
    RenameDesignVariantCommand,
)
from ..application.use_cases.update_dipole_design import (
    UpdateDipoleDesign,
    UpdateDipoleDesignCommand,
)
from ..domain.antennas.antenna import AntennaModel
from ..domain.antennas.balun import BalunLoss
from ..domain.antennas.beverage import BeverageParameters
from ..domain.antennas.biquad import (
    BiquadParameters,
)
from ..domain.antennas.custom import CustomAntennaParameters
from ..domain.antennas.design import (
    AntennaDesignParameters,
    antenna_type_for,
    primary_dimension_m,
    template_load_ids,
    with_primary_dimension,
)
from ..domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ..domain.antennas.discone import DisconeParameters
from ..domain.antennas.endfed import (
    EndFedParameters,
    EndFedPreset,
)
from ..domain.antennas.family import antenna_family
from ..domain.antennas.fan_dipole import FanDipoleParameters
from ..domain.antennas.feed_line import FeedLine
from ..domain.antennas.folded_dipole import FoldedDipoleParameters
from ..domain.antennas.g5rv import G5RV_DIPOLE_ID
from ..domain.antennas.hexbeam import HexbeamParameters
from ..domain.antennas.inverted_l import InvertedLParameters
from ..domain.antennas.inverted_v import InvertedVParameters
from ..domain.antennas.j_pole import JPoleParameters
from ..domain.antennas.load import LumpedLoad, ParallelLoad
from ..domain.antennas.loaded_dipole import LoadedDipoleParameters
from ..domain.antennas.log_periodic import LogPeriodicParameters
from ..domain.antennas.loop import LoopParameters
from ..domain.antennas.magnetic_loop import MagneticLoopParameters
from ..domain.antennas.matching_network import (
    MatchingNetwork,
    MatchingNetworkPosition,
    design_l_network,
    design_pi_network,
    design_t_network,
)
from ..domain.antennas.material_defaults import default_material_for_template
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.ocfd import OCFDParameters
from ..domain.antennas.phased_vertical import PhasedVerticalParameters
from ..domain.antennas.quad_beam import QuadBeamParameters
from ..domain.antennas.ringo import RingoParameters
from ..domain.antennas.scv import ScvParameters
from ..domain.antennas.t2fd import (
    T2FD_DRIVEN_WIRE_ID,
    T2FD_TERMINATED_WIRE_ID,
    T2FDParameters,
)
from ..domain.antennas.transmission_line import TransmissionLine
from ..domain.antennas.transmission_line_doublet import (
    DoubletPreset,
    TransmissionLineDoubletParameters,
)
from ..domain.antennas.trap_dipole import TrapDipoleParameters
from ..domain.antennas.trap_yagi import TrapYagiParameters
from ..domain.antennas.vertical import VerticalParameters
from ..domain.antennas.yagi import (
    YagiParameters,
    nbs_five_element,
    yagi_element_length_mismatch,
)
from ..domain.antennas.zepp import ZeppParameters
from ..domain.antennas.zs6bkw import (
    ZS6BKW_DIPOLE_ID,
)
from ..domain.common.time import utc_now
from ..domain.common.validation import Diagnostic
from ..domain.design.band_plan import (
    BandDefault,
    BandPlan,
    BandSelection,
    default_band_plan,
    operating_frequencies_for,
)
from ..domain.design.comparison import (
    ComparisonBasis,
    apply_comparison_basis,
    native_height_m,
)
from ..domain.design.estimators import supports_estimation
from ..domain.design.feed_connection import feed_connection_detail
from ..domain.design.frequency_scale import (
    UnsupportedFrequencyScaleError,
    scaled_to_frequency,
    supports_frequency_scaling,
)
from ..domain.design.matching_design import (
    MatchingNetworkDesign,
    matching_network_design_from_frequency,
)
from ..domain.design.matching_resolution import resolve_matching_network
from ..domain.design.preflight import PreflightAction, PreflightReport
from ..domain.measurement import Measurement
from ..domain.optimization.registry import optimizer_availability
from ..domain.optimization.summary import OptimizationMode
from ..domain.projects.installation import InstallationSupport
from ..domain.projects.project import DesignProvenance, DesignVariant, Project
from ..domain.simulation.band_result import BandAnalysisResult, BandResult
from ..domain.simulation.bands import (
    amateur_band_for,
)
from ..domain.simulation.budget import (
    PatternBudget,
)
from ..domain.simulation.frequency import FrequencyPlan
from ..domain.simulation.result import SimulationResult, SimulationStatus
from ..domain.simulation.segmentation import (
    SegmentationPolicy,
    aligned_policy_for_model,
    aligned_policy_for_wire_centers,
)
from ..domain.simulation.spec import DEFAULT_TIMEOUT_S, MAX_TIMEOUT_S, SimulationSpec
from ..importers.vna_csv import VnaColumnMapping
from ..reporting.design_summary import installation_profile_rows
from .catalog import CatalogContext, change_template_selection, new_antenna_selection
from .dialogs.antenna_advisor_dialog import AntennaAdvisorDialog
from .dialogs.antenna_catalog_dialog import (
    AntennaCatalogDialog,
)
from .dialogs.balun_loss_dialog import BalunLossDialog
from .dialogs.band_analysis_dialog import BandAnalysisDialog
from .dialogs.bom_costs_dialog import BomCostsDialog
from .dialogs.comparison_dialog import ComparisonDialog
from .dialogs.component_calculator_dialog import (
    CalculatorSeed,
    ComponentCalculatorDialog,
)
from .dialogs.construction_dialog import ConstructionDialog
from .dialogs.construction_record_dialog import ConstructionRecordDialog
from .dialogs.convergence_dialog import ConvergenceDialog
from .dialogs.custom_antenna_dialog import CustomAntennaDialog
from .dialogs.design_from_frequency_dialog import DesignFromFrequencyDialog
from .dialogs.family_optimization_dialog import (
    BandPlanSource,
)
from .dialogs.feed_chain_dialog import FeedChainDialog
from .dialogs.feed_connection_dialog import FeedConnectionDialog
from .dialogs.feed_line_dialog import FeedLineDialog
from .dialogs.guided_experiments_dialog import GuidedExperimentsDialog
from .dialogs.installation_profile_dialog import InstallationProfileDialog
from .dialogs.inverted_l_dialog import InvertedLDialog
from .dialogs.inverted_v_dialog import InvertedVDialog
from .dialogs.journal_dialog import JournalDialog
from .dialogs.live_tuning_dialog import LiveTuningDialog
from .dialogs.loads_dialog import LoadsDialog
from .dialogs.magnetic_loop_dialog import MagneticLoopDialog
from .dialogs.matching_network_dialog import MatchingNetworkDialog
from .dialogs.materials_reference_dialog import MaterialsReferenceDialog
from .dialogs.measurement_comparison_dialog import MeasurementComparisonDialog
from .dialogs.measurement_details_dialog import MeasurementDetailsDialog
from .dialogs.measurement_sessions_dialog import MeasurementSessionsDialog
from .dialogs.ocfd_dialog import OCFDDialog
from .dialogs.parameter_sweep_dialog import ParameterSweepDialog
from .dialogs.preferences_dialog import PreferencesDialog
from .dialogs.preflight_dialog import PreflightDialog
from .dialogs.reference_library_dialog import ReferenceLibraryDialog
from .dialogs.robustness_dialog import RobustnessDialog
from .dialogs.scale_frequency_dialog import ScaleFrequencyDialog
from .dialogs.scv_dialog import ScvDialog
from .dialogs.transmission_lines_dialog import TransmissionLinesDialog
from .dialogs.tuner_match_dialog import TunerMatchDialog
from .dialogs.tuning_assistant_dialog import TuningAssistantDialog
from .dialogs.vertical_dialog import VerticalDialog
from .dialogs.yagi_dialog import YagiDialog
from .element_optimization_actions import (
    optimize_fan_dipole_elements,
    optimize_inverted_v_elements,
    optimize_loop_elements,
    optimize_moxon_elements,
    optimize_ringo_elements,
    optimize_vertical_elements,
    optimize_yagi_elements,
    optimize_zs6bkw_elements,
)
from .exporters import (
    ExportContext,
    ExportFailure,
    export_bom_csv,
    export_frequency_csv,
    export_geometry_dxf,
    export_geometry_pdf,
    export_geometry_png,
    export_geometry_svg,
    export_html_report,
    export_pattern_csv,
    export_pattern_png,
    export_pdf_report,
    export_sources_csv,
    export_touchstone,
    export_wire_schedule_csv,
    save_nec_deck,
)
from .help import apply_help
from .history import ProjectSnapshot, SnapshotCommand, history_action
from .i18n import Language, Translator
from .import_actions import (
    choose_and_import_mmana,
    choose_and_import_nec,
    choose_vna_paths,
)
from .import_actions import (
    import_vna_paths as import_vna_files,
)
from .optimization_actions import (
    run_family_optimization_dialog,
    run_length_optimization_dialog,
    run_synthesis_dialog,
)
from .optimization_adapters import adapter_for
from .preferences import (
    FontSize,
    FontSizeController,
    InMemoryPreferencesStore,
    LanguagePreference,
    PreferencesStore,
    UiPreferences,
    resolve_language,
)
from .project_io import ProjectIO
from .recent_projects import InMemoryRecentProjectsStore, RecentProjectsStore
from .recovery import AutosaveRecovery
from .recovery_actions import RecoveryController
from .template_identity import catalog_key_for, label_key_for
from .theme import ThemeController
from .units import DisplayUnits, UnitSystem, length_from_m, length_unit_key
from .widgets.beverage_form import BeverageForm
from .widgets.biquad_form import BiquadForm
from .widgets.dipole_form import DipoleForm
from .widgets.discone_form import DisconeForm
from .widgets.endfed_form import EndFedForm
from .widgets.fan_dipole_form import FanDipoleForm
from .widgets.feed_matching_summary import FeedMatchingSummary
from .widgets.geometry_view import GeometryView, GeometryViewMode
from .widgets.hexbeam_form import HexbeamForm
from .widgets.inverted_l_form import InvertedLForm
from .widgets.inverted_v_form import InvertedVForm
from .widgets.j_pole_form import JPoleForm
from .widgets.loaded_dipole_form import LoadedDipoleForm
from .widgets.log_periodic_form import LogPeriodicForm
from .widgets.magnetic_loop_form import MagneticLoopForm
from .widgets.moxon_form import MoxonForm
from .widgets.ocfd_form import OCFDForm
from .widgets.phased_vertical_form import PhasedVerticalForm
from .widgets.quad_beam_form import QuadBeamForm
from .widgets.results_view import ResultsView
from .widgets.ringo_form import RingoForm
from .widgets.scv_form import ScvForm
from .widgets.start_page import StartPage
from .widgets.t2fd_form import T2FDForm
from .widgets.task_progress import TaskProgressBar, TaskProgressState
from .widgets.transmission_line_doublet_form import TransmissionLineDoubletForm
from .widgets.trap_dipole_form import TrapDipoleForm
from .widgets.trap_yagi_form import TrapYagiForm
from .widgets.vertical_form import VerticalForm
from .widgets.workflow_panel import NextStepPanel
from .widgets.yagi_form import YagiForm
from .widgets.zepp_form import ZeppForm
from .workers.band_analysis_worker import BandAnalysisWorker
from .workers.comparison_worker import ComparisonWorker
from .workers.project_bundle_worker import (
    ProjectBundleExportWorker,
    ProjectBundleImportWorker,
)
from .workers.simulation_worker import SimulationWorker
from .workflow import NextStepKind, WorkflowContext, WorkflowMode, next_step

VNA_SUFFIXES = frozenset({".csv", ".txt", ".s1p", ".s2p"})


def project_size_action(estimated_bytes: int) -> Literal["ok", "warn", "block"]:
    """Classify an estimated compressed project size before a long run."""

    if estimated_bytes > MAX_PROJECT_SIZE_BYTES:
        return "block"
    if estimated_bytes > PROJECT_SIZE_WARNING_BYTES:
        return "warn"
    return "ok"


class MainWindow(QMainWindow):
    def __init__(
        self,
        repository: ProjectRepository,
        solver: AntennaSolver | None,
        translator: Translator,
        unit_system: UnitSystem = UnitSystem.METRIC,
        parent: QWidget | None = None,
        *,
        preferences: PreferencesStore | None = None,
        recent_projects: RecentProjectsStore | None = None,
        recovery: AutosaveRecovery | None = None,
        font_size_controller: FontSizeController | None = None,
        language_preference: LanguagePreference | None = None,
        theme_controller: ThemeController | None = None,
        solver_factory: Callable[[Path], AntennaSolver] | None = None,
        preflight_runner: PreflightRunner | None = None,
        nec_deck_exporter: NecDeckExporter | None = None,
    ) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._repository = repository
        self._solver = solver
        self._solver_factory = solver_factory
        self._preflight_runner = preflight_runner
        self._nec_deck_exporter = nec_deck_exporter
        self._translator = translator
        self._project_io = ProjectIO(self, translator, repository)
        self._unit_system = unit_system
        self._language_preference = (
            language_preference if language_preference is not None else LanguagePreference.SYSTEM
        )
        self._preferences = preferences if preferences is not None else InMemoryPreferencesStore()
        self._recent_projects = (
            recent_projects if recent_projects is not None else InMemoryRecentProjectsStore()
        )
        self._recovery = recovery
        self._theme_controller = (
            theme_controller if theme_controller is not None else ThemeController()
        )
        loaded_preferences = self._preferences.load()
        self._autosave_enabled = loaded_preferences.autosave_enabled
        self._theme_controller.apply(loaded_preferences.theme)
        self._length_policy = loaded_preferences.length_policy
        self._workflow_mode = loaded_preferences.workflow_mode
        self._report_include_3d = loaded_preferences.report_include_3d
        self._report_include_band_3d = loaded_preferences.report_include_band_3d
        self._restore_last_project_preference = loaded_preferences.restore_last_project
        self._last_applied_workflow_mode: WorkflowMode | None = None
        if font_size_controller is None:
            app = QApplication.instance()
            base_font = app.font() if isinstance(app, QApplication) else QFont()
            font_size_controller = FontSizeController(base_font)
        self._font_size_controller = font_size_controller

        self._project: Project | None = None
        self._design_id: UUID | None = None
        self._current_path: Path | None = None
        self._dirty = False
        self._design_dirty = False
        self._autosave_pending = False
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
        self._workflow_reviewed_swr: set[UUID] = set()
        self._workflow_construction_viewed: set[UUID] = set()
        self._workflow_measurement_compared: set[UUID] = set()
        self._vna_column_mappings: dict[tuple[str, ...], VnaColumnMapping] = {}
        self._loads: tuple[LumpedLoad, ...] = ()
        self._transmission_lines: tuple[TransmissionLine, ...] = ()
        self._feed_line: FeedLine | None = None
        self._matching_network: MatchingNetwork | None = None
        self._matching_network_position = MatchingNetworkPosition.FEEDPOINT
        self._matching_network_design: MatchingNetworkDesign | None = None
        self._balun_loss: BalunLoss | None = None
        self._current_balun = False
        self._custom_pattern_step_deg = DEFAULT_PATTERN_STEP_DEG
        self._custom_run_pattern_step_deg: float | None = None
        self._custom_pattern_frequency_count: int | None = None
        self._sweep_custom_initialized = False
        self._custom_last_budget: PatternBudget | None = None
        self._pending_pattern_diagnostic: Diagnostic | None = None
        self._last_status_key = "status.ready"
        self._thread: QThread | None = None
        self._worker: SimulationWorker | BandAnalysisWorker | ComparisonWorker | None = None
        self._cancel_token: EventCancelToken | None = None
        self._comparison_dialog: ComparisonDialog | None = None
        self._comparison_basis: ComparisonBasis | None = None
        self._comparison_height_mapping: dict[UUID, tuple[bool, tuple[str, ...]]] = {}
        self._progress_started_at: float | None = None
        self._progress_timer = QTimer(self)
        self._progress_timer.setInterval(1000)
        self._progress_timer.timeout.connect(self._update_progress_elapsed)
        self._recovery_controller = RecoveryController(
            self,
            translator,
            lambda: self._recovery,
            self._autosave_now,
        )
        self._undo_stack = QUndoStack(self)
        self._undo_stack.setUndoLimit(50)
        self._history_restoring = False
        self._history_depth = 0
        self._clean_signature: tuple[object, ...] | None = None
        self._clean_run_ids: frozenset[UUID] = frozenset()

        self._build_actions()
        self._build_ui()
        self._sync_workflow_controls()
        self._apply_workflow_mode()
        self._show_empty_state()
        self.retranslate()
        self._refresh_start_page_recents()
        if self._autosave_enabled and self._recovery_controller.available:
            self._recovery_controller.set_enabled(True)
        if self._recovery is not None or self._restore_last_project_preference:
            QTimer.singleShot(0, self._startup_recovery)

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
        self._advisor_action = QAction(self)
        self._advisor_action.triggered.connect(lambda: self.show_antenna_advisor())
        self._reference_library_action = QAction(self)
        self._reference_library_action.triggered.connect(lambda: self.show_reference_library())
        self._import_nec_action = QAction(self)
        self._import_nec_action.triggered.connect(lambda: self.import_nec_deck())
        self._import_mmana_action = QAction(self)
        self._import_mmana_action.triggered.connect(lambda: self.import_mmana_file())
        self._import_vna_action = QAction(self)
        self._import_vna_action.triggered.connect(lambda: self.import_vna_data())

        self._open_action = QAction(self)
        self._open_action.setShortcut(QKeySequence.StandardKey.Open)
        self._open_action.triggered.connect(lambda: self.open_project())

        self._save_action = QAction(self)
        self._save_action.setShortcut(QKeySequence.StandardKey.Save)
        self._save_action.triggered.connect(lambda: self.save_project())

        self._save_as_action = QAction(self)
        self._save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self._save_as_action.triggered.connect(lambda: self.save_project_as())

        self._export_bundle_action = QAction(self)
        self._export_bundle_action.triggered.connect(lambda: self.export_project_bundle())
        self._import_bundle_action = QAction(self)
        self._import_bundle_action.triggered.connect(lambda: self.import_project_bundle())

        self._locate_solver_action = QAction(self)
        self._locate_solver_action.triggered.connect(lambda: self.locate_solver())

        self._preferences_action = QAction(self)
        self._preferences_action.setShortcut(QKeySequence("Ctrl+,"))
        self._preferences_action.triggered.connect(lambda: self.show_preferences())

        self._feed_line_action = QAction(self)
        self._feed_line_action.triggered.connect(lambda: self.configure_feed_line())
        self._matching_network_action = QAction(self)
        self._matching_network_action.triggered.connect(lambda: self.configure_matching_network())
        self._balun_loss_action = QAction(self)
        self._balun_loss_action.triggered.connect(lambda: self.configure_balun_loss())
        self._feed_chain_action = QAction(self)
        self._feed_chain_action.triggered.connect(lambda: self.show_feed_chain_budget())
        self._feed_connection_action = QAction(self)
        self._feed_connection_action.triggered.connect(lambda: self.show_feed_connection())

        self._exit_action = QAction(self)
        self._exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self._exit_action.triggered.connect(self.close)

        self._about_action = QAction(self)
        self._about_action.triggered.connect(lambda: self.show_about())
        self._whats_this_action = QAction(self)
        self._whats_this_action.setShortcut(QKeySequence("Shift+F1"))
        self._whats_this_action.triggered.connect(lambda: QWhatsThis.enterWhatsThisMode())

        self._workflow_guided_action = QAction(self)
        self._workflow_standard_action = QAction(self)
        self._workflow_advanced_action = QAction(self)
        self._workflow_actions = {
            WorkflowMode.GUIDED: self._workflow_guided_action,
            WorkflowMode.STANDARD: self._workflow_standard_action,
            WorkflowMode.ADVANCED: self._workflow_advanced_action,
        }
        self._workflow_action_group = QActionGroup(self)
        self._workflow_action_group.setExclusive(True)
        for mode, action in self._workflow_actions.items():
            action.setCheckable(True)
            action.setData(mode.value)
            action.triggered.connect(lambda checked=False, mode=mode: self._set_workflow_mode(mode))
            self._workflow_action_group.addAction(action)

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
        self._installation_profile_action = QAction(self)
        self._installation_profile_action.triggered.connect(
            lambda: self.edit_installation_profile()
        )
        self._design_from_frequency_action = QAction(self)
        self._design_from_frequency_action.setShortcut(QKeySequence("Ctrl+Shift+E"))
        self._design_from_frequency_action.triggered.connect(lambda: self.design_from_frequency())
        self._scale_frequency_action = QAction(self)
        self._scale_frequency_action.triggered.connect(lambda: self.scale_geometry_to_frequency())
        self._preflight_action = QAction(self)
        self._preflight_action.triggered.connect(lambda: self.show_preflight())
        self._construction_action = QAction(self)
        self._construction_action.triggered.connect(lambda: self.show_construction_sheet())
        self._construction_record_action = QAction(self)
        self._construction_record_action.triggered.connect(lambda: self.edit_construction_record())
        self._bom_costs_action = QAction(self)
        self._bom_costs_action.triggered.connect(lambda: self.edit_bom_costs())
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
        self._export_touchstone_action = QAction(self)
        self._export_touchstone_action.triggered.connect(lambda: self.export_touchstone())
        self._export_nec_action = QAction(self)
        self._export_nec_action.triggered.connect(lambda: self.export_nec_deck())
        self._copy_nec_action = QAction(self)
        self._copy_nec_action.triggered.connect(lambda: self.copy_nec_deck())
        self._export_sources_csv_action = QAction(self)
        self._export_sources_csv_action.triggered.connect(lambda: self.export_sources_csv())
        self._export_wire_schedule_csv_action = QAction(self)
        self._export_wire_schedule_csv_action.triggered.connect(
            lambda: self.export_wire_schedule_csv()
        )
        self._export_bom_csv_action = QAction(self)
        self._export_bom_csv_action.triggered.connect(lambda: self.export_bom_csv())
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
        self._calculator_action = QAction(self)
        self._calculator_action.triggered.connect(lambda: self.show_component_calculators())
        self._materials_action = QAction(self)
        self._materials_action.triggered.connect(lambda: self.show_materials_reference())
        self._tuner_match_action = QAction(self)
        self._tuner_match_action.triggered.connect(lambda: self.show_tuner_matchability())
        self._live_tuning_action = QAction(self)
        self._live_tuning_action.triggered.connect(lambda: self.show_live_tuning())
        self._measurement_sessions_action = QAction(self)
        self._measurement_sessions_action.triggered.connect(
            lambda: self.edit_measurement_sessions()
        )
        self._journal_action = QAction(self)
        self._journal_action.triggered.connect(lambda: self.edit_project_journal())
        self._tuning_action = QAction(self)
        self._tuning_action.triggered.connect(lambda: self.tune_measurement())
        self._sweep_action = QAction(self)
        self._sweep_action.triggered.connect(lambda: self.parameter_sweep())
        self._guided_experiments_action = QAction(self)
        self._guided_experiments_action.triggered.connect(lambda: self.guided_experiments())
        self._robustness_action = QAction(self)
        self._robustness_action.triggered.connect(lambda: self.tolerance_robustness())

        self._simulate_action = QAction(self)
        self._simulate_action.setShortcut(QKeySequence("F5"))
        self._simulate_action.triggered.connect(lambda: self.simulate())

        self._analyze_bands_action = QAction(self)
        self._analyze_bands_action.setShortcut(QKeySequence("Ctrl+Shift+B"))
        self._analyze_bands_action.triggered.connect(lambda: self.analyze_bands())

        self._convergence_action = QAction(self)
        self._convergence_action.triggered.connect(lambda: self.run_convergence_study())

        self._cancel_action = QAction(self)
        self._cancel_action.setShortcut(QKeySequence("Ctrl+."))
        self._cancel_action.triggered.connect(lambda: self.cancel_simulation())

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

        self._inverted_l_form = InvertedLForm(self._translator, self._unit_system, parent=self)
        self._inverted_l_form.changed.connect(self._on_form_changed)
        self._inverted_l_scroll = QScrollArea(self)
        self._inverted_l_scroll.setWidgetResizable(True)
        self._inverted_l_scroll.setWidget(self._inverted_l_form)
        self._inverted_l_scroll.setMinimumWidth(340)
        self._inverted_l_scroll.setMaximumWidth(480)

        self._magnetic_loop_form = MagneticLoopForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._magnetic_loop_form.changed.connect(self._on_form_changed)
        self._magnetic_loop_scroll = QScrollArea(self)
        self._magnetic_loop_scroll.setWidgetResizable(True)
        self._magnetic_loop_scroll.setWidget(self._magnetic_loop_form)
        self._magnetic_loop_scroll.setMinimumWidth(340)
        self._magnetic_loop_scroll.setMaximumWidth(480)

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
        self._endfed_form.matching_network_edit_requested.connect(self.configure_matching_network)
        self._endfed_form.matching_network_remove_requested.connect(self.remove_matching_network)
        self._endfed_form.design_matching_network_requested.connect(
            self._design_endfed_matching_network
        )
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

        self._scv_form = ScvForm(self._translator, self._unit_system, parent=self)
        self._scv_form.changed.connect(self._on_form_changed)
        self._scv_scroll = QScrollArea(self)
        self._scv_scroll.setWidgetResizable(True)
        self._scv_scroll.setWidget(self._scv_form)
        self._scv_scroll.setMinimumWidth(340)
        self._scv_scroll.setMaximumWidth(480)

        self._biquad_form = BiquadForm(self._translator, self._unit_system, parent=self)
        self._biquad_form.changed.connect(self._on_form_changed)
        self._biquad_scroll = QScrollArea(self)
        self._biquad_scroll.setWidgetResizable(True)
        self._biquad_scroll.setWidget(self._biquad_form)
        self._biquad_scroll.setMinimumWidth(340)
        self._biquad_scroll.setMaximumWidth(480)

        self._beverage_form = BeverageForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._beverage_form.changed.connect(self._on_form_changed)
        self._beverage_scroll = QScrollArea(self)
        self._beverage_scroll.setWidgetResizable(True)
        self._beverage_scroll.setWidget(self._beverage_form)
        self._beverage_scroll.setMinimumWidth(340)
        self._beverage_scroll.setMaximumWidth(480)

        self._loaded_dipole_form = LoadedDipoleForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._loaded_dipole_form.changed.connect(self._on_form_changed)
        self._loaded_dipole_scroll = QScrollArea(self)
        self._loaded_dipole_scroll.setWidgetResizable(True)
        self._loaded_dipole_scroll.setWidget(self._loaded_dipole_form)
        self._loaded_dipole_scroll.setMinimumWidth(340)
        self._loaded_dipole_scroll.setMaximumWidth(480)

        self._phased_vertical_form = PhasedVerticalForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._phased_vertical_form.changed.connect(self._on_form_changed)
        self._phased_vertical_scroll = QScrollArea(self)
        self._phased_vertical_scroll.setWidgetResizable(True)
        self._phased_vertical_scroll.setWidget(self._phased_vertical_form)
        self._phased_vertical_scroll.setMinimumWidth(340)
        self._phased_vertical_scroll.setMaximumWidth(480)

        self._quad_beam_form = QuadBeamForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._quad_beam_form.changed.connect(self._on_form_changed)
        self._quad_beam_scroll = QScrollArea(self)
        self._quad_beam_scroll.setWidgetResizable(True)
        self._quad_beam_scroll.setWidget(self._quad_beam_form)
        self._quad_beam_scroll.setMinimumWidth(340)
        self._quad_beam_scroll.setMaximumWidth(480)

        self._log_periodic_form = LogPeriodicForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._log_periodic_form.changed.connect(self._on_form_changed)
        self._log_periodic_scroll = QScrollArea(self)
        self._log_periodic_scroll.setWidgetResizable(True)
        self._log_periodic_scroll.setWidget(self._log_periodic_form)
        self._log_periodic_scroll.setMinimumWidth(340)
        self._log_periodic_scroll.setMaximumWidth(520)

        self._discone_form = DisconeForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._discone_form.changed.connect(self._on_form_changed)
        self._discone_scroll = QScrollArea(self)
        self._discone_scroll.setWidgetResizable(True)
        self._discone_scroll.setWidget(self._discone_form)
        self._discone_scroll.setMinimumWidth(340)
        self._discone_scroll.setMaximumWidth(480)

        self._trap_yagi_form = TrapYagiForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._trap_yagi_form.changed.connect(self._on_form_changed)
        self._trap_yagi_scroll = QScrollArea(self)
        self._trap_yagi_scroll.setWidgetResizable(True)
        self._trap_yagi_scroll.setWidget(self._trap_yagi_form)
        self._trap_yagi_scroll.setMinimumWidth(340)
        self._trap_yagi_scroll.setMaximumWidth(520)

        self._hexbeam_form = HexbeamForm(
            self._translator,
            self._unit_system,
            parent=self,
        )
        self._hexbeam_form.changed.connect(self._on_form_changed)
        self._hexbeam_form.active_band_changed.connect(self._on_hexbeam_active_band_changed)
        self._hexbeam_scroll = QScrollArea(self)
        self._hexbeam_scroll.setWidgetResizable(True)
        self._hexbeam_scroll.setWidget(self._hexbeam_form)
        self._hexbeam_scroll.setMinimumWidth(340)
        self._hexbeam_scroll.setMaximumWidth(520)

        self._doublet_form = TransmissionLineDoubletForm(
            self._translator,
            self._unit_system,
            parent=self,
            preset=DoubletPreset.G5RV,
        )
        self._doublet_form.changed.connect(self._on_form_changed)
        self._doublet_scroll = QScrollArea(self)
        self._doublet_scroll.setWidgetResizable(True)
        self._doublet_scroll.setWidget(self._doublet_form)
        self._doublet_scroll.setMinimumWidth(340)
        self._doublet_scroll.setMaximumWidth(480)

        self._zepp_form = ZeppForm(self._translator, self._unit_system, parent=self)
        self._zepp_form.changed.connect(self._on_form_changed)
        self._zepp_scroll = QScrollArea(self)
        self._zepp_scroll.setWidgetResizable(True)
        self._zepp_scroll.setWidget(self._zepp_form)
        self._zepp_scroll.setMinimumWidth(340)
        self._zepp_scroll.setMaximumWidth(480)

        self._form_panels = (
            (self._form, self._form_scroll, 480),
            (self._ocfd_form, self._ocfd_scroll, 480),
            (self._vertical_form, self._vertical_scroll, 480),
            (self._inverted_v_form, self._inverted_v_scroll, 480),
            (self._inverted_l_form, self._inverted_l_scroll, 480),
            (self._magnetic_loop_form, self._magnetic_loop_scroll, 480),
            (self._yagi_form, self._yagi_scroll, 520),
            (self._moxon_form, self._moxon_scroll, 480),
            (self._fan_dipole_form, self._fan_dipole_scroll, 480),
            (self._trap_dipole_form, self._trap_dipole_scroll, 500),
            (self._t2fd_form, self._t2fd_scroll, 500),
            (self._endfed_form, self._endfed_scroll, 480),
            (self._j_pole_form, self._j_pole_scroll, 480),
            (self._ringo_form, self._ringo_scroll, 480),
            (self._scv_form, self._scv_scroll, 480),
            (self._biquad_form, self._biquad_scroll, 480),
            (self._beverage_form, self._beverage_scroll, 480),
            (self._loaded_dipole_form, self._loaded_dipole_scroll, 480),
            (self._phased_vertical_form, self._phased_vertical_scroll, 480),
            (self._quad_beam_form, self._quad_beam_scroll, 480),
            (self._log_periodic_form, self._log_periodic_scroll, 520),
            (self._discone_form, self._discone_scroll, 480),
            (self._trap_yagi_form, self._trap_yagi_scroll, 520),
            (self._hexbeam_form, self._hexbeam_scroll, 520),
            (self._doublet_form, self._doublet_scroll, 480),
            (self._zepp_form, self._zepp_scroll, 480),
        )
        self._update_form_panel_widths()

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

        self._solver_group = QGroupBox(self)
        self._solver_timeout_label = QLabel(self._solver_group)
        self._solver_timeout = QSpinBox(self._solver_group)
        self._solver_timeout.setRange(10, int(MAX_TIMEOUT_S))
        self._solver_timeout.setSuffix(" s")
        self._solver_timeout.setValue(int(DEFAULT_TIMEOUT_S))
        self._solver_timeout_hint = QLabel(self._solver_group)
        self._solver_timeout_hint.setWordWrap(True)
        solver_layout = QFormLayout(self._solver_group)
        solver_layout.addRow(self._solver_timeout_label, self._solver_timeout)
        solver_layout.addRow(self._solver_timeout_hint)

        self._advanced_body = QWidget(self)
        advanced_layout = QVBoxLayout(self._advanced_body)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        advanced_layout.addWidget(self._solver_group)
        advanced_layout.addWidget(self._sweep_group)
        advanced_layout.addWidget(self._pattern_group)
        advanced_layout.addWidget(self._band_group)
        advanced_layout.addStretch(1)

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
        self._design_stack.addWidget(self._inverted_l_scroll)
        self._design_stack.addWidget(self._magnetic_loop_scroll)
        self._design_stack.addWidget(self._yagi_scroll)
        self._design_stack.addWidget(self._moxon_scroll)
        self._design_stack.addWidget(self._fan_dipole_scroll)
        self._design_stack.addWidget(self._trap_dipole_scroll)
        self._design_stack.addWidget(self._t2fd_scroll)
        self._design_stack.addWidget(self._endfed_scroll)
        self._design_stack.addWidget(self._j_pole_scroll)
        self._design_stack.addWidget(self._ringo_scroll)
        self._design_stack.addWidget(self._scv_scroll)
        self._design_stack.addWidget(self._biquad_scroll)
        self._design_stack.addWidget(self._beverage_scroll)
        self._design_stack.addWidget(self._loaded_dipole_scroll)
        self._design_stack.addWidget(self._phased_vertical_scroll)
        self._design_stack.addWidget(self._quad_beam_scroll)
        self._design_stack.addWidget(self._log_periodic_scroll)
        self._design_stack.addWidget(self._discone_scroll)
        self._design_stack.addWidget(self._trap_yagi_scroll)
        self._design_stack.addWidget(self._hexbeam_scroll)
        self._design_stack.addWidget(self._doublet_scroll)
        self._design_stack.addWidget(self._zepp_scroll)
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
        self._feed_matching_summary = FeedMatchingSummary(
            self._translator,
            self._unit_system,
            self,
        )
        self._feed_matching_summary.edit_network_requested.connect(self.configure_matching_network)
        self._feed_matching_summary.remove_network_requested.connect(self.remove_matching_network)
        self._feed_matching_summary.current_balun_changed.connect(self.set_current_balun)
        self._feed_matching_summary.feed_connection_requested.connect(self.show_feed_connection)
        self._workflow_panel = NextStepPanel(self._translator, self)
        self._workflow_panel.action_requested.connect(self._on_next_step_action)
        self._workflow_panel.advanced_requested.connect(
            lambda: self._set_workflow_mode(WorkflowMode.ADVANCED)
        )
        self._sidebar_tabs = QTabWidget(self)
        self._sidebar_tabs.setDocumentMode(True)
        self._sidebar_tabs.setUsesScrollButtons(False)

        self._design_tab = QWidget(self._sidebar_tabs)
        design_tab_layout = QVBoxLayout(self._design_tab)
        design_tab_layout.setContentsMargins(0, 0, 0, 0)
        design_tab_layout.addWidget(self._workflow_panel)
        design_actions = QHBoxLayout()
        design_actions.addWidget(self._apply_button)
        design_actions.addWidget(self._estimate_button)
        design_actions.addWidget(self._optimize_button)
        design_tab_layout.addLayout(design_actions)
        design_tab_layout.addWidget(self._design_stack, 1)
        design_tab_layout.addWidget(self._feed_matching_summary)
        self._installation_label = QLabel(self)
        self._installation_label.setWordWrap(True)
        self._installation_edit = QPushButton(self)
        self._installation_edit.clicked.connect(lambda: self.edit_installation_profile())
        installation_layout = QHBoxLayout()
        installation_layout.setContentsMargins(0, 0, 0, 0)
        installation_layout.addWidget(self._installation_label, 1)
        installation_layout.addWidget(self._installation_edit)
        design_tab_layout.addLayout(installation_layout)
        design_tab_layout.addWidget(self._provenance_label)

        self._simulation_tab = QWidget(self._sidebar_tabs)
        simulation_tab_layout = QVBoxLayout(self._simulation_tab)
        simulation_tab_layout.setContentsMargins(0, 0, 0, 0)
        self._simulation_scroll = QScrollArea(self._simulation_tab)
        self._simulation_scroll.setWidgetResizable(True)
        self._simulation_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._simulation_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._simulation_scroll.setWidget(self._advanced_body)
        simulation_tab_layout.addWidget(self._simulation_scroll, 1)

        self._design_tab_index = self._sidebar_tabs.addTab(self._design_tab, "")
        self._simulation_tab_index = self._sidebar_tabs.addTab(self._simulation_tab, "")
        design_panel = QWidget(self)
        design_layout = QVBoxLayout(design_panel)
        design_layout.setContentsMargins(0, 0, 0, 0)
        design_layout.addWidget(self._sidebar_tabs)
        self._design_panel = design_panel
        self._update_form_panel_widths()

        self._geometry = GeometryView(
            self._translator,
            self._unit_system,
            display_units=DisplayUnits(self._unit_system, self._length_policy),
        )
        self._geometry.setMinimumHeight(300)
        self._hidden_dimension_texts: tuple[str, ...] = ()
        self._geometry_hidden_label = QLabel(self)
        self._geometry_hidden_label.setWordWrap(True)
        self._geometry_hidden_label.setTextFormat(Qt.TextFormat.PlainText)
        self._geometry_hidden_label.hide()
        self._geometry.hidden_dimensions_changed.connect(self._on_hidden_dimensions_changed)
        self._results = ResultsView(
            self._translator,
            display_units=DisplayUnits(self._unit_system, self._length_policy),
        )
        self._results.measurement_edit_requested.connect(self.edit_measurement)
        self._results.measurement_delete_requested.connect(self.delete_measurement)
        self._results.measurement_sessions_requested.connect(self.edit_measurement_sessions)
        self._results.measurement_compare_requested.connect(self.compare_measurements)
        self._results.measurement_tune_requested.connect(self.tune_measurement)
        self._results.band_selected.connect(self._on_band_selected)
        self._results.matching_network_requested.connect(self.create_matching_network_from_point)
        self._results.tab_changed.connect(self._on_results_tab_changed)

        geometry_container = QWidget(self)
        geometry_layout = QVBoxLayout(geometry_container)
        geometry_layout.setContentsMargins(0, 0, 0, 0)
        geometry_controls = QHBoxLayout()
        self._view_label = QLabel(self)
        self._view_combo = QComboBox(self)
        self._view_combo.addItem("", GeometryViewMode.CONSTRUCTION.value)
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
        geometry_layout.addWidget(self._geometry_hidden_label)
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
        self._main_splitter = main_splitter
        main_splitter.setSizes([self._preferred_form_panel_width(), 900])

        self._start_page = StartPage(self._translator, self)
        self._start_page.new_requested.connect(lambda: self.new_antenna())
        self._start_page.advise_requested.connect(lambda: self.show_antenna_advisor())
        self._start_page.open_requested.connect(lambda: self.open_project())
        self._start_page.example_requested.connect(lambda kind: self.open_example(kind))
        self._start_page.reference_requested.connect(lambda: self.show_reference_library())
        self._start_page.recent_requested.connect(lambda path: self.open_recent_project(path))
        self._start_page.recent_remove_requested.connect(
            lambda path: self.remove_recent_project(path)
        )
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
        toolbar.addSeparator()
        self._workflow_label = QLabel(self)
        toolbar.addWidget(self._workflow_label)
        self._workflow_combo = QComboBox(self)
        for mode in WorkflowMode:
            self._workflow_combo.addItem("", mode.value)
        self._workflow_combo.currentIndexChanged.connect(self._on_workflow_combo_changed)
        toolbar.addWidget(self._workflow_combo)

        self._file_menu = self.menuBar().addMenu("")
        self._file_menu.addAction(self._new_action)
        self._file_menu.addAction(self._advisor_action)
        self._file_menu.addAction(self._reference_library_action)
        self._file_menu.addAction(self._open_action)
        self._file_menu.addAction(self._save_action)
        self._file_menu.addAction(self._save_as_action)
        self._file_menu.addAction(self._export_bundle_action)
        self._file_menu.addAction(self._import_bundle_action)
        self._file_menu.addSeparator()
        self._import_menu = self._file_menu.addMenu("")
        self._import_menu.addAction(self._import_nec_action)
        self._import_menu.addAction(self._import_mmana_action)
        self._import_separator = self._import_menu.addSeparator()
        self._import_menu.addAction(self._import_vna_action)
        self._export_menu = self._file_menu.addMenu("")
        self._export_menu.addAction(self._export_csv_action)
        self._export_menu.addAction(self._export_touchstone_action)
        self._export_menu.addAction(self._export_nec_action)
        self._export_menu.addAction(self._copy_nec_action)
        self._export_menu.addAction(self._export_sources_csv_action)
        self._export_menu.addAction(self._export_wire_schedule_csv_action)
        self._export_menu.addAction(self._export_bom_csv_action)
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
        self._edit_menu.addSeparator()
        self._edit_menu.addAction(self._preferences_action)

        self._view_menu = self.menuBar().addMenu("")
        self._workflow_menu = self._view_menu.addMenu("")
        for mode in WorkflowMode:
            self._workflow_menu.addAction(self._workflow_actions[mode])

        self._design_menu = self.menuBar().addMenu("")
        self._variants_menu = self._design_menu.addMenu("")
        self._variants_menu.addAction(self._new_variant_action)
        self._variants_menu.addAction(self._rename_variant_action)
        self._variants_menu.addAction(self._delete_variant_action)
        self._variants_menu.addSeparator()
        self._variants_menu.addAction(self._compare_action)
        self._design_menu.addSeparator()
        self._design_menu.addAction(self._change_template_action)
        self._design_menu.addAction(self._installation_profile_action)
        self._design_menu.addAction(self._design_from_frequency_action)
        self._design_menu.addAction(self._scale_frequency_action)
        self._design_menu.addAction(self._optimize_action)
        self._design_menu.addSeparator()
        self._design_menu.addAction(self._preflight_action)
        self._design_menu.addAction(self._feed_connection_action)
        self._design_menu.addAction(self._construction_action)
        self._design_menu.addAction(self._construction_record_action)
        self._design_menu.addAction(self._bom_costs_action)
        self._design_menu.addAction(self._loads_action)
        self._design_menu.addAction(self._transmission_lines_action)
        self._custom_menu = self._design_menu.addMenu("")
        self._custom_menu.addAction(self._edit_custom_action)
        self._custom_menu.addAction(self._convert_custom_action)

        self._simulation_menu = self.menuBar().addMenu("")
        self._simulation_menu.addAction(self._simulate_action)
        self._simulation_menu.addAction(self._analyze_bands_action)
        self._simulation_menu.addAction(self._convergence_action)
        self._simulation_menu.addAction(self._cancel_action)
        self._simulation_feed_separator = self._simulation_menu.addSeparator()
        self._simulation_menu.addAction(self._feed_line_action)
        self._simulation_menu.addAction(self._matching_network_action)
        self._simulation_menu.addAction(self._balun_loss_action)
        self._simulation_menu.addAction(self._feed_chain_action)

        self._tools_menu = self.menuBar().addMenu("")
        self._tools_menu.addAction(self._locate_solver_action)
        self._tools_menu.addAction(self._calculator_action)
        self._tools_menu.addAction(self._materials_action)
        self._tools_menu.addAction(self._tuner_match_action)
        self._tools_menu.addAction(self._live_tuning_action)
        self._tools_menu.addAction(self._measurement_sessions_action)
        self._tools_menu.addAction(self._journal_action)
        self._tools_menu.addAction(self._tuning_action)
        self._tools_menu.addAction(self._sweep_action)
        self._tools_menu.addAction(self._guided_experiments_action)
        self._tools_menu.addAction(self._robustness_action)
        self._tools_menu.addAction(self._compact_history_action)

        self._help_menu = self.menuBar().addMenu("")
        self._help_menu.addAction(self._whats_this_action)
        self._help_menu.addAction(self._about_action)

        self._status_label = QLabel(self)
        self._solver_label = QLabel(self)
        self._task_progress = TaskProgressBar(self._translator, self)
        self.statusBar().addWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._task_progress)
        self.statusBar().addPermanentWidget(self._solver_label)

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
        self._advisor_action.setText(self._translator.t("action.antenna_advisor"))
        self._reference_library_action.setText(self._translator.t("action.reference_library"))
        self._reference_library_action.setToolTip(
            self._translator.t("help.action.reference_library")
        )
        self._reference_library_action.setWhatsThis(
            self._translator.t("help.action.reference_library")
        )
        self._advisor_action.setToolTip(self._translator.t("help.action.antenna_advisor"))
        self._advisor_action.setWhatsThis(self._translator.t("help.action.antenna_advisor"))
        self._import_nec_action.setText(self._translator.t("action.import_nec"))
        self._import_mmana_action.setText(self._translator.t("action.import_mmana"))
        self._import_vna_action.setText(self._translator.t("action.import_vna"))
        self._import_vna_action.setToolTip(self._translator.t("help.action.import_vna"))
        self._import_vna_action.setWhatsThis(self._translator.t("help.action.import_vna"))
        self._open_action.setText(self._translator.t("action.open"))
        self._save_action.setText(self._translator.t("action.save"))
        self._save_as_action.setText(self._translator.t("action.save_as"))
        self._export_bundle_action.setText(self._translator.t("action.export_project_bundle"))
        self._export_bundle_action.setToolTip(
            self._translator.t("help.action.export_project_bundle")
        )
        self._export_bundle_action.setWhatsThis(
            self._translator.t("help.action.export_project_bundle")
        )
        self._import_bundle_action.setText(self._translator.t("action.import_project_bundle"))
        self._import_bundle_action.setToolTip(
            self._translator.t("help.action.import_project_bundle")
        )
        self._import_bundle_action.setWhatsThis(
            self._translator.t("help.action.import_project_bundle")
        )
        self._locate_solver_action.setText(self._translator.t("action.locate_solver"))
        self._preferences_action.setText(self._translator.t("action.preferences"))
        self._feed_line_action.setText(self._translator.t("action.feed_line"))
        self._matching_network_action.setText(self._translator.t("action.matching_network"))
        self._balun_loss_action.setText(self._translator.t("action.balun_loss"))
        self._feed_chain_action.setText(self._translator.t("action.feed_chain"))
        self._feed_chain_action.setToolTip(self._translator.t("help.action.feed_chain"))
        self._feed_chain_action.setWhatsThis(self._translator.t("help.action.feed_chain"))
        self._feed_connection_action.setText(self._translator.t("action.feed_connection"))
        self._feed_connection_action.setToolTip(self._translator.t("help.action.feed_connection"))
        self._feed_connection_action.setWhatsThis(self._translator.t("help.action.feed_connection"))
        self._calculator_action.setText(self._translator.t("action.component_calculator"))
        self._calculator_action.setToolTip(self._translator.t("help.action.component_calculator"))
        self._calculator_action.setWhatsThis(self._translator.t("help.action.component_calculator"))
        self._materials_action.setText(self._translator.t("action.materials_reference"))
        self._materials_action.setToolTip(self._translator.t("help.action.materials_reference"))
        self._materials_action.setWhatsThis(self._translator.t("help.action.materials_reference"))
        self._tuner_match_action.setText(self._translator.t("action.tuner_match"))
        self._tuner_match_action.setToolTip(self._translator.t("help.action.tuner_match"))
        self._tuner_match_action.setWhatsThis(self._translator.t("help.action.tuner_match"))
        self._live_tuning_action.setText(self._translator.t("action.live_tuning"))
        self._live_tuning_action.setToolTip(self._translator.t("help.action.live_tuning"))
        self._live_tuning_action.setWhatsThis(self._translator.t("help.action.live_tuning"))
        self._journal_action.setText(self._translator.t("action.project_journal"))
        self._journal_action.setToolTip(self._translator.t("help.action.project_journal"))
        self._journal_action.setWhatsThis(self._translator.t("help.action.project_journal"))
        self._measurement_sessions_action.setText(self._translator.t("action.measurement_sessions"))
        self._measurement_sessions_action.setToolTip(
            self._translator.t("help.action.measurement_sessions")
        )
        self._measurement_sessions_action.setWhatsThis(
            self._translator.t("help.action.measurement_sessions")
        )
        self._tuning_action.setText(self._translator.t("action.tuning_assistant"))
        self._tuning_action.setToolTip(self._translator.t("help.action.tuning_assistant"))
        self._tuning_action.setWhatsThis(self._translator.t("help.action.tuning_assistant"))
        self._sweep_action.setText(self._translator.t("action.parameter_sweep"))
        self._sweep_action.setToolTip(self._translator.t("help.action.parameter_sweep"))
        self._sweep_action.setWhatsThis(self._translator.t("help.action.parameter_sweep"))
        self._guided_experiments_action.setText(self._translator.t("action.guided_experiments"))
        self._guided_experiments_action.setToolTip(
            self._translator.t("help.action.guided_experiments")
        )
        self._guided_experiments_action.setWhatsThis(
            self._translator.t("help.action.guided_experiments")
        )
        self._robustness_action.setText(self._translator.t("action.robustness"))
        self._robustness_action.setToolTip(self._translator.t("help.action.robustness"))
        self._robustness_action.setWhatsThis(self._translator.t("help.action.robustness"))
        self._exit_action.setText(self._translator.t("action.exit"))
        self._about_action.setText(self._translator.t("action.about"))
        self._whats_this_action.setText(self._translator.t("action.whats_this"))
        self._whats_this_action.setToolTip(self._translator.t("action.whats_this.tooltip"))
        self._view_menu.setTitle(self._translator.t("menu.view"))
        self._workflow_menu.setTitle(self._translator.t("menu.workflow_mode"))
        self._workflow_label.setText(self._translator.t("workflow.mode_label"))
        for index, mode in enumerate(WorkflowMode):
            self._workflow_combo.setItemText(
                index,
                self._translator.t(f"workflow.mode.{mode.value}"),
            )
            action = self._workflow_actions[mode]
            action.setText(self._translator.t(f"workflow.mode.{mode.value}"))
            action.setToolTip(self._translator.t(f"help.mode.{mode.value}"))
            action.setWhatsThis(self._translator.t(f"help.mode.{mode.value}"))
        apply_help(self._workflow_label, self._translator, "preferences.workflow_mode")
        apply_help(self._workflow_combo, self._translator, "preferences.workflow_mode")
        self._workflow_panel.retranslate()
        self._new_variant_action.setText(self._translator.t("action.new_variant"))
        self._rename_variant_action.setText(self._translator.t("action.rename_variant"))
        self._delete_variant_action.setText(self._translator.t("action.delete_variant"))
        self._compare_action.setText(self._translator.t("action.compare"))
        self._optimize_action.setText(self._translator.t("action.optimize"))
        self._change_template_action.setText(self._translator.t("action.change_template"))
        self._installation_profile_action.setText(self._translator.t("action.installation_profile"))
        self._installation_profile_action.setToolTip(
            self._translator.t("help.action.installation_profile")
        )
        self._installation_profile_action.setWhatsThis(
            self._translator.t("help.action.installation_profile")
        )
        self._design_from_frequency_action.setText(
            self._translator.t("action.design_from_frequency")
        )
        self._scale_frequency_action.setText(self._translator.t("action.scale_frequency"))
        scale_help = self._translator.t("help.action.scale_frequency")
        self._scale_frequency_action.setToolTip(scale_help)
        self._scale_frequency_action.setWhatsThis(scale_help)
        self._apply_button.setText(self._translator.t("action.apply"))
        self._apply_button.setToolTip(self._translator.t("action.apply.tooltip"))
        self._optimize_button.setText(self._translator.t("action.optimize"))
        self._preflight_action.setText(self._translator.t("action.preflight"))
        self._preflight_action.setToolTip(self._translator.t("help.action.preflight"))
        self._preflight_action.setWhatsThis(self._translator.t("help.action.preflight"))
        self._construction_action.setText(self._translator.t("action.construction"))
        self._construction_record_action.setText(self._translator.t("action.construction_record"))
        self._construction_record_action.setToolTip(
            self._translator.t("help.action.construction_record")
        )
        self._construction_record_action.setWhatsThis(
            self._translator.t("help.action.construction_record")
        )
        self._bom_costs_action.setText(self._translator.t("action.bom_costs"))
        self._bom_costs_action.setToolTip(self._translator.t("help.action.bom_costs"))
        self._bom_costs_action.setWhatsThis(self._translator.t("help.action.bom_costs"))
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
        self._solver_group.setTitle(self._translator.t("solver.group_title"))
        self._solver_timeout_label.setText(self._translator.t("solver.timeout"))
        self._solver_timeout_hint.setText(self._translator.t("solver.timeout_hint"))
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
        self._sidebar_tabs.setTabText(self._design_tab_index, self._translator.t("tab.design"))
        self._sidebar_tabs.setTabText(
            self._simulation_tab_index, self._translator.t("tab.simulation")
        )
        for index, key in (
            (self._design_tab_index, "help.tab.design"),
            (self._simulation_tab_index, "help.tab.simulation"),
        ):
            help_text = self._translator.t(key)
            self._sidebar_tabs.setTabToolTip(index, help_text)
            self._sidebar_tabs.setTabWhatsThis(index, help_text)
        apply_help(self._design_panel, self._translator, "section.design")
        apply_help(self._design_tab, self._translator, "tab.design")
        apply_help(self._simulation_tab, self._translator, "tab.simulation")
        apply_help(self._installation_label, self._translator, "section.installation")
        apply_help(self._installation_edit, self._translator, "action.installation_profile")
        apply_help(self._solver_group, self._translator, "section.solver")
        apply_help(self._sweep_group, self._translator, "section.sweep")
        apply_help(self._pattern_group, self._translator, "section.pattern")
        apply_help(self._band_group, self._translator, "section.band")
        apply_help(self._custom_sweep_group, self._translator, "section.sweep")
        apply_help(self._geometry, self._translator, "section.geometry")
        self._analyze_bands_button.setText(self._translator.t("band.analyze"))
        self._analyze_bands_action.setText(self._translator.t("band.analyze"))
        apply_help(self._analyze_bands_button, self._translator, "action.analyze_bands")
        self._analyze_bands_action.setToolTip(self._translator.t("help.action.analyze_bands"))
        self._analyze_bands_action.setWhatsThis(self._translator.t("help.action.analyze_bands"))
        self._convergence_action.setText(self._translator.t("action.convergence_study"))
        self._convergence_action.setToolTip(self._translator.t("help.action.convergence_study"))
        self._convergence_action.setWhatsThis(self._translator.t("help.action.convergence_study"))
        apply_help(self._apply_button, self._translator, "action.apply_design")
        apply_help(self._optimize_button, self._translator, "action.optimize")
        self._optimize_action.setToolTip(self._translator.t("help.action.optimize"))
        self._optimize_action.setWhatsThis(self._translator.t("help.action.optimize"))
        self._status_label.setAccessibleDescription(self._translator.t("help.status.message"))
        self._status_label.setWhatsThis(self._translator.t("help.status.message"))
        self._solver_label.setAccessibleDescription(self._translator.t("help.status.solver"))
        self._solver_label.setWhatsThis(self._translator.t("help.status.solver"))
        self._cancel_action.setToolTip(self._translator.t("help.action.cancel"))
        self._cancel_action.setWhatsThis(self._translator.t("help.action.cancel"))
        self._update_band_plan_label()
        self._update_workflow_ui()
        self._refresh_installation_summary()
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
        self._export_touchstone_action.setText(self._translator.t("action.export_touchstone"))
        self._export_nec_action.setText(self._translator.t("action.export_nec"))
        self._copy_nec_action.setText(self._translator.t("action.copy_nec"))
        self._export_sources_csv_action.setText(self._translator.t("action.export_sources_csv"))
        self._export_wire_schedule_csv_action.setText(
            self._translator.t("action.export_wire_schedule_csv")
        )
        self._export_bom_csv_action.setText(self._translator.t("action.export_bom_csv"))
        self._export_pattern_csv_action.setText(self._translator.t("action.export_pattern_csv"))
        self._export_pattern_png_action.setText(self._translator.t("action.export_pattern_png"))
        self._export_geometry_png_action.setText(self._translator.t("action.export_geometry_png"))
        self._export_geometry_svg_action.setText(self._translator.t("action.export_geometry_svg"))
        self._export_geometry_pdf_action.setText(self._translator.t("action.export_geometry_pdf"))
        self._export_geometry_dxf_action.setText(self._translator.t("action.export_geometry_dxf"))
        self._export_html_action.setText(self._translator.t("action.export_html"))
        self._export_pdf_action.setText(self._translator.t("action.export_pdf"))
        export_help = self._translator.t("help.action.export")
        for action in (
            self._export_csv_action,
            self._export_sources_csv_action,
            self._export_wire_schedule_csv_action,
            self._export_bom_csv_action,
            self._export_pattern_csv_action,
            self._export_pattern_png_action,
            self._export_geometry_png_action,
            self._export_geometry_svg_action,
            self._export_geometry_pdf_action,
            self._export_geometry_dxf_action,
            self._export_html_action,
            self._export_pdf_action,
        ):
            action.setToolTip(export_help)
            action.setWhatsThis(export_help)
        touchstone_help = self._translator.t("help.action.export_touchstone")
        self._export_touchstone_action.setToolTip(touchstone_help)
        self._export_touchstone_action.setWhatsThis(touchstone_help)
        nec_help = self._translator.t("help.action.export_nec")
        for action in (self._export_nec_action, self._copy_nec_action):
            action.setToolTip(nec_help)
            action.setWhatsThis(nec_help)
        self._compact_history_action.setText(self._translator.t("action.compact_history"))
        self._simulate_action.setText(self._translator.t("action.simulate"))
        self._simulate_action.setToolTip(self._translator.t("action.simulate.tooltip"))
        self._simulate_action.setWhatsThis(self._translator.t("action.simulate.tooltip"))
        self._cancel_action.setText(self._translator.t("action.cancel"))
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
        self._help_menu.setTitle(self._translator.t("menu.help"))
        self._project_name_label.setText(self._translator.t("field.project_name"))
        self._variant_label.setText(self._translator.t("variant.label"))
        self._view_label.setText(self._translator.t("geometry.view"))
        self._view_combo.setItemText(0, self._translator.t("geometry.view_construction"))
        self._view_combo.setItemText(1, self._translator.t("geometry.view_3d"))
        self._height_label.setText(self._translator.t("geometry.vertical_scale"))
        self._zoom_label.setText(self._translator.t("geometry.zoom"))
        self._zoom_combo.setToolTip(self._translator.t("geometry.zoom_hint"))
        self._start_page.retranslate()
        self._form.retranslate()
        self._ocfd_form.retranslate()
        self._vertical_form.retranslate()
        self._inverted_v_form.retranslate()
        self._inverted_l_form.retranslate()
        self._magnetic_loop_form.retranslate()
        self._yagi_form.retranslate()
        self._moxon_form.retranslate()
        self._fan_dipole_form.retranslate()
        self._trap_dipole_form.retranslate()
        self._t2fd_form.retranslate()
        self._endfed_form.retranslate()
        self._feed_matching_summary.retranslate()
        self._j_pole_form.retranslate()
        self._ringo_form.retranslate()
        self._scv_form.retranslate()
        self._biquad_form.retranslate()
        self._beverage_form.retranslate()
        self._loaded_dipole_form.retranslate()
        self._phased_vertical_form.retranslate()
        self._quad_beam_form.retranslate()
        self._log_periodic_form.retranslate()
        self._discone_form.retranslate()
        self._trap_yagi_form.retranslate()
        self._hexbeam_form.retranslate()
        self._doublet_form.retranslate()
        self._zepp_form.retranslate()
        self._geometry.retranslate()
        self._update_hidden_label()
        self._results.retranslate()
        self._task_progress.retranslate()
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
        self._workflow_reviewed_swr.discard(design_id)
        self._workflow_construction_viewed.discard(design_id)
        self._workflow_measurement_compared.discard(design_id)
        if design_id == self._design_id and hasattr(self, "_results"):
            self._results.set_band_analysis(None)

    def _update_status_text(self) -> None:
        running_keys = {"status.simulating", "status.analyzing_bands", "status.cancelling"}
        key = self._last_status_key
        if self._simulating and key not in running_keys:
            key = "status.simulating"
        self._status_label.setText(self._translator.t(key))

    def _start_indeterminate_progress(self, text_key: str) -> None:
        self._progress_started_at = time.monotonic()
        self._task_progress.begin_indeterminate(text_key)
        self._progress_timer.start()

    def _start_determinate_progress(self, maximum: int, text_key: str) -> None:
        self._progress_started_at = time.monotonic()
        self._task_progress.begin_determinate(maximum, text_key)
        self._progress_timer.start()

    def _update_progress_elapsed(self) -> None:
        if self._progress_started_at is None:
            return
        self._task_progress.set_elapsed(int(time.monotonic() - self._progress_started_at))

    def _finish_progress(self) -> None:
        self._progress_timer.stop()
        self._progress_started_at = None
        self._task_progress.reset()

    def _on_simulation_phase(self, phase: str) -> None:
        if self._task_progress.state is not TaskProgressState.RUNNING:
            return
        key = {
            "running": "progress.running_solver",
            "processing": "progress.processing",
        }.get(phase)
        if key is not None:
            self._task_progress.set_text_key(key)

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
        current_result = (
            self._simulation_results.get(self._design_id) if self._design_id is not None else None
        )
        has_sources = current_result is not None and any(
            len(frequency.source_results) > 1 for frequency in current_result.frequencies
        )
        self._new_action.setEnabled(idle)
        self._advisor_action.setEnabled(idle)
        self._reference_library_action.setEnabled(idle)
        self._apply_button.setEnabled(idle and has_project)
        self._open_action.setEnabled(idle)
        self._save_action.setEnabled(idle and has_project)
        self._save_as_action.setEnabled(idle and has_project)
        self._export_bundle_action.setEnabled(idle and has_project)
        self._import_bundle_action.setEnabled(idle)
        self._locate_solver_action.setEnabled(idle)
        self._calculator_action.setEnabled(idle)
        self._materials_action.setEnabled(idle)
        self._tuner_match_action.setEnabled(idle and has_result)
        self._live_tuning_action.setEnabled(idle and has_project and self._solver is not None)
        self._measurement_sessions_action.setEnabled(idle and has_project)
        self._journal_action.setEnabled(idle and has_project)
        self._feed_line_action.setEnabled(idle)
        self._matching_network_action.setEnabled(idle)
        self._balun_loss_action.setEnabled(idle)
        self._feed_chain_action.setEnabled(idle and has_result)
        self._feed_connection_action.setEnabled(idle and has_project)
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
        self._installation_profile_action.setEnabled(idle and has_project)
        self._installation_edit.setEnabled(idle and has_project)
        self._design_from_frequency_action.setEnabled(idle and has_project and estimate_supported)
        self._estimate_button.setEnabled(idle and has_project and estimate_supported)
        estimate_hint = ""
        if parameters is not None and not estimate_supported:
            estimate_hint = self._estimate_unavailable_message(parameters)
        self._estimate_button.setToolTip(estimate_hint)
        self._design_from_frequency_action.setToolTip(estimate_hint)
        scale_supported = parameters is not None and supports_frequency_scaling(parameters)
        self._scale_frequency_action.setEnabled(idle and has_project and scale_supported)
        scale_hint = self._translator.t("help.action.scale_frequency")
        if parameters is not None and not scale_supported:
            scale_hint = self._translator.t("scale_frequency.unsupported")
        self._scale_frequency_action.setToolTip(scale_hint)
        self._scale_frequency_action.setWhatsThis(scale_hint)
        band_enabled = idle and has_project and self._solver is not None
        self._analyze_bands_action.setEnabled(band_enabled)
        self._analyze_bands_button.setEnabled(band_enabled)
        self._convergence_action.setEnabled(band_enabled)
        hexbeam_band = self._optimizer_hexbeam_band(parameters)
        optimizer = (
            optimizer_availability(parameters, hexbeam_band=hexbeam_band)
            if parameters is not None
            else None
        )
        optimize_available = optimizer is not None and optimizer.available
        optimize_enabled = idle and has_project and optimize_available and self._solver is not None
        optimize_hint = self._translator.t("help.action.optimize")
        if optimizer is not None and not optimizer.available and optimizer.reason_key:
            optimize_hint = self._translator.t(
                optimizer.reason_key,
                **optimizer.reason_values,
            )
        self._optimize_action.setEnabled(optimize_enabled)
        self._optimize_button.setEnabled(optimize_enabled)
        self._optimize_action.setToolTip(optimize_hint)
        self._optimize_button.setToolTip(optimize_hint)
        has_measurements = bool(self._project.measurements) if self._project is not None else False
        self._tuning_action.setEnabled(
            idle
            and has_project
            and has_measurements
            and self._tuning_supported(parameters)
            and self._solver is not None
        )
        self._sweep_action.setEnabled(
            idle and has_project and self._sweep_supported(parameters) and self._solver is not None
        )
        self._guided_experiments_action.setEnabled(
            idle and has_project and self._sweep_supported(parameters) and self._solver is not None
        )
        self._robustness_action.setEnabled(
            idle
            and has_project
            and self._robustness_supported(parameters)
            and self._solver is not None
        )
        self._preflight_action.setEnabled(idle and has_project)
        self._construction_action.setEnabled(idle and has_project)
        self._construction_record_action.setEnabled(idle and has_project)
        self._bom_costs_action.setEnabled(idle and has_project)
        self._loads_action.setEnabled(idle and has_project)
        self._transmission_lines_action.setEnabled(idle and has_project)
        self._edit_custom_action.setEnabled(idle and has_project and is_custom)
        self._convert_custom_action.setEnabled(idle and has_project and not is_custom)
        self._import_nec_action.setEnabled(idle)
        self._import_mmana_action.setEnabled(idle)
        self._import_vna_action.setEnabled(idle and has_project)
        self._export_csv_action.setEnabled(idle and has_result)
        self._export_touchstone_action.setEnabled(idle and has_result)
        self._export_nec_action.setEnabled(idle and has_project)
        self._copy_nec_action.setEnabled(idle and has_project)
        self._export_sources_csv_action.setEnabled(idle and has_sources)
        self._export_wire_schedule_csv_action.setEnabled(idle and has_project)
        self._export_bom_csv_action.setEnabled(idle and has_project)
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
        self._solver_group.setEnabled(idle and has_project)
        self._sweep_group.setEnabled(idle and has_project)
        self._toolbar.setVisible(has_project)
        self._update_workflow_ui()

    def _workflow_context(self) -> WorkflowContext:
        if self._project is None or self._design_id is None:
            return WorkflowContext(
                has_project=False,
                has_solver=self._solver is not None,
                has_result=False,
            )
        design = self._project.design_by_id(self._design_id)
        result = self._simulation_results.get(self._design_id)
        design_swr: float | None = None
        if result is not None and result.frequencies:
            target_hz = design.parameters.frequency_hz
            closest = min(
                result.frequencies,
                key=lambda item: abs(item.frequency_hz - target_hz),
            )
            design_swr = closest.swr
        return WorkflowContext(
            has_project=True,
            has_solver=self._solver is not None,
            has_result=result is not None,
            result_status=result.status if result is not None else None,
            design_swr=design_swr,
            reviewed_swr=self._design_id in self._workflow_reviewed_swr,
            construction_viewed=self._design_id in self._workflow_construction_viewed,
            has_measurement=bool(self._project.measurements),
            measurement_compared=self._design_id in self._workflow_measurement_compared,
        )

    def _update_workflow_ui(self) -> None:
        panel = getattr(self, "_workflow_panel", None)
        if panel is None:
            return
        panel.set_guided(self._workflow_mode is WorkflowMode.GUIDED)
        panel.set_step(next_step(self._workflow_context()))
        panel.setVisible(self._workflow_mode is not WorkflowMode.ADVANCED)

    def _set_workflow_mode(self, mode: WorkflowMode, *, save: bool = True) -> None:
        changed = mode is not self._workflow_mode
        self._workflow_mode = mode
        self._sync_workflow_controls()
        self._apply_workflow_mode()
        if changed and save:
            self._save_preferences()

    def _sync_workflow_controls(self) -> None:
        combo = getattr(self, "_workflow_combo", None)
        if combo is not None:
            combo.blockSignals(True)
            index = combo.findData(self._workflow_mode.value)
            if index >= 0:
                combo.setCurrentIndex(index)
            combo.blockSignals(False)
        for mode, action in self._workflow_actions.items():
            action.blockSignals(True)
            action.setChecked(mode is self._workflow_mode)
            action.blockSignals(False)

    def _on_workflow_combo_changed(self, _index: int) -> None:
        value = self._workflow_combo.currentData()
        if not isinstance(value, str):
            return
        try:
            mode = WorkflowMode(value)
        except ValueError:
            return
        self._set_workflow_mode(mode)

    def _apply_workflow_mode(self) -> None:
        guided = self._workflow_mode is WorkflowMode.GUIDED
        advanced = self._workflow_mode is WorkflowMode.ADVANCED
        self._sidebar_tabs.tabBar().setVisible(not guided)
        self._sidebar_tabs.setTabVisible(self._simulation_tab_index, not guided)
        if self._last_applied_workflow_mode is not self._workflow_mode:
            self._sidebar_tabs.setCurrentWidget(
                self._simulation_tab if advanced else self._design_tab
            )
            self._last_applied_workflow_mode = self._workflow_mode
        for action in (
            self._loads_action,
            self._transmission_lines_action,
            self._feed_line_action,
            self._matching_network_action,
            self._balun_loss_action,
            self._feed_chain_action,
            self._feed_connection_action,
            self._optimize_action,
            self._compact_history_action,
            self._calculator_action,
            self._materials_action,
            self._tuner_match_action,
            self._live_tuning_action,
            self._measurement_sessions_action,
            self._journal_action,
            self._tuning_action,
            self._sweep_action,
            self._guided_experiments_action,
            self._robustness_action,
            self._import_nec_action,
            self._import_mmana_action,
        ):
            action.setVisible(not guided)
        self._import_separator.setVisible(not guided)
        self._simulation_feed_separator.setVisible(not guided)
        self._custom_menu.menuAction().setVisible(not guided)
        self._optimize_button.setVisible(not guided)
        self._feed_matching_summary.setVisible(not guided)
        self._workflow_panel.set_guided(guided)
        self._workflow_panel.setVisible(not advanced)
        self._update_workflow_ui()

    def _on_next_step_action(self, kind: object) -> None:
        if not isinstance(kind, NextStepKind):
            return
        if kind is NextStepKind.CREATE_PROJECT:
            self.new_antenna()
        elif kind is NextStepKind.CONFIGURE_SOLVER:
            self.locate_solver()
        elif kind is NextStepKind.SIMULATE:
            self.simulate()
        elif kind is NextStepKind.REVIEW_DIAGNOSTICS:
            self._results.show_diagnostics()
        elif kind is NextStepKind.REVIEW_SWR:
            if self._design_id is not None:
                self._workflow_reviewed_swr.add(self._design_id)
            self._results.show_impedance()
            self._update_workflow_ui()
        elif kind is NextStepKind.BUILD_SHEET:
            self.show_construction_sheet()
        elif kind is NextStepKind.MEASURE:
            self.import_vna_data()
        elif kind is NextStepKind.COMPARE_MEASUREMENT:
            if self._design_id is not None:
                self._workflow_measurement_compared.add(self._design_id)
            self._results.show_measurements()
            self._update_workflow_ui()
        elif kind is NextStepKind.COMPLETE:
            self.export_pdf_report()

    def _on_results_tab_changed(self, view: str) -> None:
        if self._design_id is None:
            return
        if view == "impedance":
            self._workflow_reviewed_swr.add(self._design_id)
        elif view == "measurements":
            self._workflow_measurement_compared.add(self._design_id)
        self._update_workflow_ui()

    def _estimate_unavailable_message(self, parameters: AntennaDesignParameters) -> str:
        if isinstance(parameters, VerticalParameters) and parameters.loading_coil_enabled:
            return self._translator.t("design_from_frequency.unsupported_loaded_vertical")
        if (
            isinstance(parameters, EndFedParameters)
            and parameters.preset is EndFedPreset.RANDOM_WIRE
        ):
            return self._translator.t("design_from_frequency.unsupported_random_wire")
        if isinstance(parameters, EndFedParameters) and parameters.preset in {
            EndFedPreset.SHORTENED_80_10,
            EndFedPreset.SHORTENED_40_10,
        }:
            return self._translator.t("design_from_frequency.unsupported_loaded_endfed")
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
            selected_id: UUID | None
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
            self._matching_network_position = project.matching_network_position
            self._matching_network_design = project.matching_network_design
            self._balun_loss = project.balun_loss
            self._current_balun = project.current_balun
            self._form_dirty = False
            self._simulation_results = {}
            self._band_analysis_results = {}
            self._selected_band_ids = {}
            self._band_plans = {}
            for project_design in project.designs:
                if project_design.band_plan is not None:
                    self._band_plans[project_design.id] = project_design.band_plan
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
            self._refresh_measurements()
            self._project_name_updating = True
            self._project_name.setText(project.name)
            self._project_name_updating = False
            self._populate_variants(selected_id)
            if selected_id is not None:
                self._select_design(selected_id)
            else:
                self._results.set_result(None)
            self._update_dirty_from_signature()
            self._refresh_installation_summary()
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
            parameters.generator_id
            in {
                "inverted_l",
                "inverted_v",
                "magnetic_loop",
                "ocfd",
                "yagi",
                "vertical",
                "half_square",
                "bobtail_curtain",
            }
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
                self._custom_sweep_points.setValue(DEFAULT_GENERATED_SWEEP_POINTS)
            elif parameters.generator_id in {"zs6bkw", "zepp"}:
                self._custom_sweep_start.setValue(7.0)
                self._custom_sweep_stop.setValue(29.7)
                self._custom_sweep_points.setValue(DEFAULT_GENERATED_SWEEP_POINTS)
            else:
                center_mhz = design.parameters.frequency_hz / 1_000_000.0
                self._custom_sweep_start.setValue(center_mhz * 0.95)
                self._custom_sweep_stop.setValue(center_mhz * 1.05)
                self._custom_sweep_points.setValue(100)
            self._custom_sweep.setChecked(True)
        self._update_custom_pattern_status()

    def _on_hexbeam_active_band_changed(self, band: str) -> None:
        if isinstance(self._geometry, GeometryView):
            self._geometry.set_active_band(band)
        self._update_actions()

    def _optimizer_hexbeam_band(self, parameters: AntennaDesignParameters | None) -> str | None:
        """Return the band a multi-band HexBeam optimizer should target."""

        if not isinstance(parameters, HexbeamParameters) or len(parameters.bands) <= 1:
            return None
        active = self._hexbeam_form.active_band()
        labels = {band.label.casefold(): band.label for band in parameters.bands}
        if active is not None and active.casefold() in labels:
            return labels[active.casefold()]
        return parameters.bands[0].label

    def _set_geometry_model(self, design: DesignVariant) -> None:
        display_name = (
            design.parameters.template_name
            if isinstance(design.parameters, JPoleParameters)
            else None
        )
        active_band = (
            self._hexbeam_form.active_band()
            if isinstance(design.parameters, HexbeamParameters)
            else None
        )
        self._geometry.set_model(
            design.antenna,
            antenna_type=design.antenna_type,
            display_name=display_name,
            parameters=design.parameters,
            active_band=active_band,
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
        if design.band_plan is not None:
            self._band_plans[design_id] = design.band_plan
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
        elif isinstance(design.parameters, InvertedLParameters):
            self._design_stack.setCurrentWidget(self._inverted_l_scroll)
            self._inverted_l_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, MagneticLoopParameters):
            self._design_stack.setCurrentWidget(self._magnetic_loop_scroll)
            self._magnetic_loop_form.set_parameters(design.parameters)
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
        elif isinstance(design.parameters, ScvParameters):
            self._design_stack.setCurrentWidget(self._scv_scroll)
            self._scv_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, BiquadParameters):
            self._design_stack.setCurrentWidget(self._biquad_scroll)
            self._biquad_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, BeverageParameters):
            self._design_stack.setCurrentWidget(self._beverage_scroll)
            self._beverage_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, LoadedDipoleParameters):
            self._design_stack.setCurrentWidget(self._loaded_dipole_scroll)
            self._loaded_dipole_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, PhasedVerticalParameters):
            self._design_stack.setCurrentWidget(self._phased_vertical_scroll)
            self._phased_vertical_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, QuadBeamParameters):
            self._design_stack.setCurrentWidget(self._quad_beam_scroll)
            self._quad_beam_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, LogPeriodicParameters):
            self._design_stack.setCurrentWidget(self._log_periodic_scroll)
            self._log_periodic_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, DisconeParameters):
            self._design_stack.setCurrentWidget(self._discone_scroll)
            self._discone_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, TrapYagiParameters):
            self._design_stack.setCurrentWidget(self._trap_yagi_scroll)
            self._trap_yagi_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, HexbeamParameters):
            self._design_stack.setCurrentWidget(self._hexbeam_scroll)
            self._hexbeam_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, TransmissionLineDoubletParameters):
            self._design_stack.setCurrentWidget(self._doublet_scroll)
            self._doublet_form.set_parameters(design.parameters)
        elif isinstance(design.parameters, ZeppParameters):
            self._design_stack.setCurrentWidget(self._zepp_scroll)
            self._zepp_form.set_parameters(design.parameters)
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
        active_band: BandResult | None = None
        if analysis is not None and analysis.bands:
            selected_id = self._selected_band_ids.get(design_id, analysis.bands[0].band.name)
            selected = analysis.result_for_band(selected_id) or analysis.bands[0]
            self._selected_band_ids[design_id] = selected.band.name
            result = selected.result
            active_band = selected
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
        self._results.set_result(result, band=active_band)
        self._last_status_key = (
            self._result_status_key(result.status) if result is not None else "status.ready"
        )
        self._update_status_text()
        self._update_actions()
        self._update_height_control()
        self._update_custom_pattern_status()
        self._refresh_auto_sweep_display()
        self._refresh_feed_matching_summary()

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
        self._matching_network_position = MatchingNetworkPosition.FEEDPOINT
        self._matching_network_design = None
        self._balun_loss = None
        self._current_balun = False
        self._current_path = None
        self._dirty = False
        self._design_dirty = False
        self._autosave_pending = False
        self._form_dirty = False
        self._last_result = None
        self._simulation_results = {}
        self._band_analysis_results = {}
        self._band_plans = {}
        self._selected_band_ids = {}
        self._simulation_design_id = None
        self._band_analysis_design_id = None
        self._workflow_reviewed_swr.clear()
        self._workflow_construction_viewed.clear()
        self._workflow_measurement_compared.clear()
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
        self._refresh_feed_matching_summary()
        self._refresh_installation_summary()
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
        self._recovery_controller.clear()
        self._project = project
        self._design_id = design_id
        self._feed_line = project.feed_line
        self._matching_network = project.matching_network
        self._matching_network_position = project.matching_network_position
        self._matching_network_design = project.matching_network_design
        self._balun_loss = project.balun_loss
        self._current_balun = project.current_balun
        self._current_path = path
        if path is not None:
            self._recent_projects.add(path, project.name)
            self._refresh_start_page_recents()
        self._dirty = dirty
        self._design_dirty = dirty
        self._autosave_pending = dirty
        self._form_dirty = False
        self._last_result = None
        self._simulation_results = {}
        self._band_analysis_results = {}
        self._band_plans = {}
        self._selected_band_ids = {}
        for project_design in project.designs:
            if project_design.band_plan is not None:
                self._band_plans[project_design.id] = project_design.band_plan
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
        self._workflow_reviewed_swr.clear()
        self._workflow_construction_viewed.clear()
        self._workflow_measurement_compared.clear()
        self._results.set_band_analysis(None)
        self._results.set_result(None)
        self._refresh_measurements()
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
        self._design_dirty = dirty
        self._autosave_pending = dirty
        if dirty and self._autosave_enabled and self._recovery is not None:
            self._recovery_controller.schedule()
        self._refresh_installation_summary()
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
        parameters: AntennaDesignParameters
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, InvertedLParameters):
            parameters = self._inverted_l_form.parameters()
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
            self._mark_project_dirty()
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, MagneticLoopParameters):
            parameters = self._magnetic_loop_form.parameters()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(previous_design.parameters, ScvParameters):
            parameters = self._scv_form.parameters()
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
            self._mark_project_dirty()
            self._update_title()
            self._update_actions()
            self._update_height_control()
            return self._project
        if isinstance(
            previous_design.parameters,
            (
                BeverageParameters,
                BiquadParameters,
                LoadedDipoleParameters,
                DisconeParameters,
                PhasedVerticalParameters,
                TrapYagiParameters,
                HexbeamParameters,
                QuadBeamParameters,
                LogPeriodicParameters,
                TransmissionLineDoubletParameters,
                ZeppParameters,
            ),
        ):
            if isinstance(previous_design.parameters, BeverageParameters):
                parameters = self._beverage_form.parameters()
            elif isinstance(previous_design.parameters, BiquadParameters):
                parameters = self._biquad_form.parameters()
            elif isinstance(previous_design.parameters, LoadedDipoleParameters):
                parameters = self._loaded_dipole_form.parameters()
            elif isinstance(previous_design.parameters, PhasedVerticalParameters):
                parameters = self._phased_vertical_form.parameters()
            elif isinstance(previous_design.parameters, QuadBeamParameters):
                parameters = self._quad_beam_form.parameters()
            elif isinstance(previous_design.parameters, LogPeriodicParameters):
                parameters = self._log_periodic_form.parameters()
            elif isinstance(previous_design.parameters, DisconeParameters):
                parameters = self._discone_form.parameters()
            elif isinstance(previous_design.parameters, TrapYagiParameters):
                parameters = self._trap_yagi_form.parameters()
            elif isinstance(previous_design.parameters, HexbeamParameters):
                parameters = self._hexbeam_form.parameters()
            elif isinstance(
                previous_design.parameters,
                TransmissionLineDoubletParameters,
            ):
                parameters = self._doublet_form.parameters()
            else:
                parameters = self._zepp_form.parameters()
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
            self._mark_project_dirty()
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
            self._mark_project_dirty()
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
        self._mark_project_dirty()
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
            self._mark_project_dirty()
            self._update_title()
        self._refresh_feed_matching_summary()

    def _current_matching_network_point(self) -> MatchingNetworkDesign | None:
        result = self._last_result
        if (
            result is None
            or self._project is None
            or self._design_id is None
            or not result.frequencies
        ):
            return None
        design = self._project.design_by_id(self._design_id)
        target_hz = design.parameters.frequency_hz
        frequency = min(
            result.frequencies,
            key=lambda item: abs(item.frequency_hz - target_hz),
        )
        return matching_network_design_from_frequency(frequency, result.spec)

    def _design_endfed_matching_network(self) -> None:
        point = self._current_matching_network_point()
        if point is None:
            QMessageBox.information(
                self,
                self._translator.t("app.title"),
                self._translator.t("endfed.design_matching_no_result"),
            )
            return
        topology = self._endfed_form.design_matching_topology()
        loaded_q = self._endfed_form.design_matching_loaded_q() or None
        network: MatchingNetwork | None
        if topology == "pi":
            network = design_pi_network(
                point.load_impedance_ohm,
                point.frequency_hz,
                source_impedance_ohm=point.source_impedance_ohm,
                loaded_q=loaded_q,
            )
        elif topology == "t":
            network = design_t_network(
                point.load_impedance_ohm,
                point.frequency_hz,
                source_impedance_ohm=point.source_impedance_ohm,
                loaded_q=loaded_q,
            )
        else:
            network = design_l_network(
                point.load_impedance_ohm,
                point.frequency_hz,
                source_impedance_ohm=point.source_impedance_ohm,
            )
        if network is None:
            QMessageBox.information(
                self,
                self._translator.t("app.title"),
                self._translator.t("endfed.design_matching_no_solution"),
            )
            return
        self._endfed_form.set_design_matching_network(network)
        QMessageBox.information(
            self,
            self._translator.t("app.title"),
            self._translator.t("endfed.design_matching_populated"),
        )

    @history_action("history.matching_network")
    def configure_matching_network(self) -> None:
        frequency_hz = 14_100_000.0
        parameters = None
        if self._project is not None and self._design_id is not None:
            parameters = self._project.design_by_id(self._design_id).parameters
            frequency_hz = parameters.frequency_hz
        internal_matching_active = False
        if parameters is not None:
            internal_matching_active = (
                resolve_matching_network(parameters, self._matching_network).internal is not None
            )
        dialog = MatchingNetworkDialog(
            self._translator,
            self._matching_network,
            self,
            frequency_hz=frequency_hz,
            internal_matching_active=internal_matching_active,
            design=self._matching_network_design,
            current_point=self._current_matching_network_point(),
            position=self._matching_network_position,
        )
        result = dialog.exec()
        if self._design_id is not None:
            self._workflow_reviewed_swr.add(self._design_id)
            self._update_workflow_ui()
        if result != QDialog.DialogCode.Accepted:
            return
        network = dialog.result_network()
        position = getattr(
            dialog,
            "position",
            lambda: self._matching_network_position,
        )()
        self._set_matching_network(
            network,
            dialog.result_design() if network is not None else None,
            position,
        )

    @history_action("history.matching_network")
    def create_matching_network_from_point(self, point: object) -> None:
        if not isinstance(point, MatchingNetworkDesign):
            return
        if self._matching_network is not None:
            answer = QMessageBox.question(
                self,
                self._translator.t("matching_network.replace_title"),
                self._translator.t("matching_network.replace_question"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        parameters = None
        if self._project is not None and self._design_id is not None:
            parameters = self._project.design_by_id(self._design_id).parameters
        internal_matching_active = False
        if parameters is not None:
            internal_matching_active = (
                resolve_matching_network(parameters, self._matching_network).internal is not None
            )
        if internal_matching_active:
            answer = QMessageBox.question(
                self,
                self._translator.t("matching_network.efhw_override_title"),
                self._translator.t("matching_network.efhw_override_question"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        dialog = MatchingNetworkDialog(
            self._translator,
            self._matching_network,
            self,
            frequency_hz=point.frequency_hz,
            internal_matching_active=internal_matching_active,
            design=point,
            current_point=point,
            position=self._matching_network_position,
        )
        result = dialog.exec()
        if self._design_id is not None:
            self._workflow_reviewed_swr.add(self._design_id)
            self._update_workflow_ui()
        if result != QDialog.DialogCode.Accepted:
            return
        network = dialog.result_network()
        position = getattr(
            dialog,
            "position",
            lambda: self._matching_network_position,
        )()
        self._set_matching_network(
            network,
            dialog.result_design() if network is not None else None,
            position,
        )

    @history_action("history.matching_network")
    def remove_matching_network(self) -> None:
        if self._matching_network is None:
            return
        answer = QMessageBox.question(
            self,
            self._translator.t("feed_matching.remove_title"),
            self._translator.t("feed_matching.remove_question"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._set_matching_network(None, None)

    def _set_matching_network(
        self,
        network: MatchingNetwork | None,
        design: MatchingNetworkDesign | None,
        position: MatchingNetworkPosition | None = None,
    ) -> None:
        self._matching_network = network
        if position is not None:
            self._matching_network_position = MatchingNetworkPosition(position)
        self._matching_network_design = design if network is not None else None
        if self._project is not None:
            timestamp = utc_now()
            self._project = self._project.with_matching_network(
                network,
                position=self._matching_network_position,
                updated_at=timestamp,
            ).with_matching_network_design(
                self._matching_network_design,
                updated_at=timestamp,
            )
            self._mark_project_dirty()
            self._update_title()
        self._refresh_feed_matching_summary()

    @history_action("history.balun_loss")
    def configure_balun_loss(self) -> None:
        dialog = BalunLossDialog(
            self._translator,
            self,
            balun_loss=self._balun_loss,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._balun_loss = dialog.result_balun_loss()
        if self._project is not None:
            self._project = self._project.with_balun_loss(
                self._balun_loss,
                updated_at=utc_now(),
            )
            self._mark_project_dirty()
            self._update_title()
        self._refresh_feed_matching_summary()

    @history_action("history.current_balun")
    def set_current_balun(self, installed: bool) -> None:
        installed = bool(installed)
        if installed == self._current_balun:
            return
        self._current_balun = installed
        if self._project is not None:
            self._project = self._project.with_current_balun(
                installed,
                updated_at=utc_now(),
            )
            self._mark_project_dirty()
            self._update_title()
        self._refresh_feed_matching_summary()

    def show_component_calculators(self) -> None:
        seed = CalculatorSeed()
        if self._project is not None and self._design_id is not None:
            design = self._project.design_by_id(self._design_id)
            loads = design.antenna.loads
            if loads:
                load = loads[0]
                seed = CalculatorSeed(
                    tab=("trap" if isinstance(load, ParallelLoad) else "coil"),
                    inductance_h=load.inductance_h or None,
                    capacitance_f=load.capacitance_f or None,
                    frequency_hz=design.parameters.frequency_hz,
                )
        dialog = ComponentCalculatorDialog(
            self._translator,
            self._unit_system,
            seed=seed,
            parent=self,
        )
        dialog.exec()

    @history_action("history.feed_line")
    def show_materials_reference(self) -> None:
        dialog = MaterialsReferenceDialog(
            self._translator,
            feed_line=self._feed_line,
            can_apply=self._project is not None,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        feed_line = dialog.result_feed_line()
        if feed_line is None:
            return
        self._feed_line = feed_line
        if self._project is not None:
            self._project = self._project.with_feed_line(
                feed_line,
                updated_at=utc_now(),
            )
            self._mark_project_dirty()
            self._update_title()
        self._refresh_feed_matching_summary()

    def show_feed_chain_budget(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        result = self._simulation_results.get(self._design_id)
        if result is None:
            self._show_error(self._translator.t("error.no_result"))
            return
        dialog = FeedChainDialog(
            self._translator,
            self._project,
            design,
            result,
            self._unit_system,
            self,
        )
        dialog.exec()

    def show_feed_connection(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        design = self._project.design_by_id(self._design_id)
        detail = feed_connection_detail(
            design.parameters,
            design.antenna,
            current_balun=self._current_balun,
            feed_line=self._feed_line,
            balun_loss=self._balun_loss,
        )
        FeedConnectionDialog(self._translator, detail, self).exec()

    def _refresh_feed_matching_summary(self) -> None:
        parameters = None
        detail = None
        if self._project is not None and self._design_id is not None:
            design = self._project.design_by_id(self._design_id)
            parameters = design.parameters
            detail = feed_connection_detail(
                parameters,
                design.antenna,
                current_balun=self._current_balun,
                feed_line=self._feed_line,
                balun_loss=self._balun_loss,
            )
        self._endfed_form.set_project_matching_network(self._matching_network)
        self._feed_matching_summary.set_state(
            parameters,
            self._matching_network,
            self._feed_line,
            self._balun_loss,
            position=self._matching_network_position,
            current_balun=self._current_balun,
            feed_detail=detail,
        )

    @history_action("history.installation_profile")
    def edit_installation_profile(self) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        dialog = InstallationProfileDialog(
            self._translator,
            self._unit_system,
            self._project.installation_profiles,
            self._project.active_installation_profile_id,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._project = self._project.with_installation_state(
            dialog.profiles(),
            dialog.active_profile_id(),
            updated_at=utc_now(),
        )
        self._mark_project_dirty()
        self._refresh_installation_summary()
        self._update_title()
        self._update_actions()
        self._last_status_key = "status.installation_profile"
        self._update_status_text()

    def _refresh_installation_summary(self) -> None:
        label = getattr(self, "_installation_label", None)
        button = getattr(self, "_installation_edit", None)
        if label is None or button is None:
            return
        profile = self._project.active_installation_profile if self._project is not None else None
        button.setText(
            self._translator.t("installation.edit" if profile is not None else "installation.add")
        )
        if profile is None:
            label.setText(self._translator.t("installation.none"))
            label.setToolTip(self._translator.t("installation.none_hint"))
            return
        rows = [
            row
            for row in installation_profile_rows(profile, labeler=self._translator.report)
            if row[0] != "Profile notes"
        ]
        text = " · ".join(f"{name}: {value}" for name, value in rows)
        label.setText(text)
        label.setToolTip(f"{text}\n\n{self._translator.t('help.section.installation')}")

    def _base_simulation_spec(self, design: DesignVariant) -> SimulationSpec:
        spec = replace(
            self._family_simulation_spec(design),
            timeout_s=float(self._solver_timeout.value()),
        )
        return self._with_model_quality(design.antenna, spec)

    def _supports_extended_thin_wire_kernel(self) -> bool:
        if self._solver is None:
            return False
        try:
            return bool(self._solver.capabilities().supports_extended_thin_wire_kernel)
        except Exception:
            return False

    def _with_model_quality(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> SimulationSpec:
        return resolve_model_quality(
            model,
            spec,
            supports_extended_kernel=self._supports_extended_thin_wire_kernel(),
        ).spec

    def _with_project_chain(
        self,
        parameters: AntennaDesignParameters,
        spec: SimulationSpec,
    ) -> SimulationSpec:
        resolution = resolve_matching_network(parameters, self._matching_network)
        return replace(
            spec,
            feed_line=self._feed_line,
            matching_network=resolution.effective,
            matching_network_position=self._matching_network_position,
            matching_network_override=resolution.override_active,
            matching_network_origin=resolution.origin,
            balun_loss=self._balun_loss,
        )

    def _family_simulation_spec(self, design: DesignVariant) -> SimulationSpec:
        parameters = design.parameters
        if isinstance(parameters, (DipoleParameters, FoldedDipoleParameters, LoopParameters)):
            return self._form.simulation_spec()
        return self._typed_simulation_spec(parameters)

    def _typed_simulation_spec(
        self,
        parameters: AntennaDesignParameters,
        *,
        active_hexbeam_band: str | None = None,
    ) -> SimulationSpec:
        return build_typed_family_simulation_spec(
            parameters,
            pattern_step_deg=self._custom_pattern_step_deg,
            custom_sweep=self._custom_sweep_options(),
            active_hexbeam_band=active_hexbeam_band,
        )

    def _custom_sweep_options(self) -> CustomSweepOptions:
        return CustomSweepOptions(
            enabled=self._custom_sweep.isChecked(),
            start_hz=self._custom_sweep_start.value() * 1_000_000.0,
            stop_hz=self._custom_sweep_stop.value() * 1_000_000.0,
            points=self._custom_sweep_points.value(),
        )

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
            design.parameters.generator_id in {"g5rv", "zs6bkw"}
        ):
            dipole_id = (
                G5RV_DIPOLE_ID if design.parameters.generator_id == "g5rv" else ZS6BKW_DIPOLE_ID
            )
            dipole = model.wire_by_id(dipole_id)
            count = segmentation.segments_for(dipole, frequency_plan.stop_hz)
            if count % 2 == 0:
                count += 1
            segmentation = SegmentationPolicy(
                min_segments_per_wire=3,
                wire_segments=((dipole_id, count),),
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
        if isinstance(design.parameters, LogPeriodicParameters):
            segmentation = aligned_policy_for_wire_centers(
                model,
                frequency_plan.stop_hz,
                segmentation,
            )
        else:
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
        design_dirty_before = self._design_dirty
        autosave_pending_before = self._autosave_pending
        try:
            project = self._apply_fields()
            self._design_dirty = design_dirty_before
            self._autosave_pending = autosave_pending_before
            if not design_dirty_before:
                self._recovery_controller.stop_debounce()
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
        spec = self._with_project_chain(design.parameters, spec)
        self._cancel_token = EventCancelToken()
        self._simulating = True
        self._last_status_key = "status.simulating"
        self._update_actions()
        self._update_status_text()
        self._start_indeterminate_progress("progress.preparing")

        thread = QThread(self)
        worker = SimulationWorker(
            self._solver,
            design.antenna,
            spec,
            self._cancel_token,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.phase.connect(self._on_simulation_phase)
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

    def run_convergence_study(self) -> None:
        if self._simulating:
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
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
        spec = self._with_project_chain(
            design.parameters,
            self._base_simulation_spec(design),
        )
        dialog = ConvergenceDialog(
            self._translator,
            self._solver,
            design.antenna,
            spec,
            self,
        )
        dialog.exec()

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
        self._start_band_analysis(design, plan, dialog.workers())

    def _start_band_analysis(
        self,
        design: DesignVariant,
        plan: BandPlan,
        parallel_workers: int = 1,
    ) -> None:
        if not plan or self._solver is None:
            return
        self._band_plans[design.id] = plan
        if self._project is not None:
            current = self._project.design_by_id(design.id)
            if current.band_plan != plan:
                self._project = self._project.with_design(
                    current.with_band_plan(plan),
                    updated_at=utc_now(),
                )
                self._mark_project_dirty()
                self._update_title()
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
            )
            spec = self._with_project_chain(design.parameters, spec)
            model = design.antenna
            if isinstance(design.parameters, HexbeamParameters):
                model = design.parameters.to_antenna(active_band=selection.band.name)
            spec = resolve_model_quality(
                model,
                spec,
                supports_extended_kernel=self._supports_extended_thin_wire_kernel(),
            ).spec
            requests.append(BandSimulationRequest(selection.band, spec, model=model))

        fitted, budget = self._fit_band_specs_to_budget(
            design.antenna,
            tuple(request.spec for request in requests),
        )
        requests = [
            BandSimulationRequest(request.band, spec)
            for request, spec in zip(requests, fitted, strict=True)
        ]
        if budget is not None:
            size_mb = budget.estimated_project_bytes / (1024.0 * 1024.0)
            action = project_size_action(budget.estimated_project_bytes)
            if action == "block":
                self._show_error(
                    self._translator.t(
                        "band.size_too_large",
                        size=size_mb,
                        limit=MAX_PROJECT_SIZE_BYTES / (1024.0 * 1024.0),
                    )
                )
                return
            if action == "warn":
                answer = QMessageBox.warning(
                    self,
                    self._translator.t("app.title"),
                    self._translator.t(
                        "band.size_warning",
                        size=size_mb,
                        limit=PROJECT_SIZE_WARNING_BYTES / (1024.0 * 1024.0),
                    ),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return

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
        self._start_determinate_progress(len(requests), "progress.analyzing_bands")

        thread = QThread(self)
        worker = BandAnalysisWorker(
            self._solver,
            design.id,
            design.antenna,
            tuple(requests),
            self._cancel_token,
            parallel_workers=parallel_workers,
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
        self._task_progress.set_progress(
            index,
            "status.bands_progress",
            index=index,
            total=total,
            band=band,
        )
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
        self._finish_progress()
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
                self._mark_project_dirty(design=False)
                self._update_title()
        self._results.set_band_analysis(analysis)
        if analysis.bands:
            self._results.set_result(analysis.bands[0].result, band=analysis.bands[0])
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
        self._finish_progress()
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
            self._workflow_reviewed_swr.discard(design_id)
            self._workflow_measurement_compared.discard(design_id)
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
                self._mark_project_dirty(design=False)
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
        self._finish_progress()
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
        self._task_progress.mark_cancelling("status.cancelling")
        self._progress_timer.stop()
        self._progress_started_at = None
        self._cancel_action.setEnabled(False)

    def _fit_spec_to_budget(self, model: object, spec: SimulationSpec) -> SimulationSpec:
        """Choose pattern snapshots and the finest pattern step that fits."""

        from ..domain.antennas.antenna import AntennaModel

        if not isinstance(model, AntennaModel):
            self._pending_pattern_diagnostic = None
            return replace(spec, pattern_frequencies_hz=())
        plan = fit_spec_to_budget(
            model,
            spec,
            requested_step_deg=self._custom_run_pattern_step_deg,
            pattern_frequency_count=self._custom_pattern_frequency_count,
        )
        if plan.budget is not None:
            self._custom_last_budget = plan.budget
            self._show_custom_pattern_budget(plan.budget)
        self._pending_pattern_diagnostic = plan.diagnostic
        return plan.spec

    def _fit_band_specs_to_budget(
        self,
        model: object,
        specs: tuple[SimulationSpec, ...],
    ) -> tuple[tuple[SimulationSpec, ...], PatternBudget | None]:
        from ..domain.antennas.antenna import AntennaModel

        if not isinstance(model, AntennaModel):
            return specs, None
        fitted, budget = fit_band_specs_to_budget(
            model,
            specs,
            requested_step_deg=self._custom_run_pattern_step_deg,
        )
        if budget is not None:
            self._custom_last_budget = budget
            self._show_custom_pattern_budget(budget)
        return fitted, budget

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
        return snapshot_frequencies(
            frequency_plan,
            preferred_frequency_hz=preferred_frequency_hz,
            count=self._custom_pattern_frequency_count,
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
        band_plan: BandPlan | None = None,
        description: str = "",
        ask_name: bool = True,
    ) -> bool:
        suggested = self._suggested_project_name(parameters, default_name)
        if ask_name:
            name = self._ask_project_name(suggested)
            if name is None:
                return False
        else:
            name = suggested
        try:
            project = CreateDipoleProject().execute(
                CreateDipoleProjectCommand(
                    project_name=name,
                    variant_name="Initial",
                    parameters=parameters,
                    description=description,
                    band_plan=band_plan,
                )
            )
            if feed_line is not None:
                project = project.with_feed_line(
                    feed_line,
                    updated_at=project.updated_at,
                )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return False
        self._set_project(project, project.designs[0].id, path=None, dirty=True)
        self._sidebar_tabs.setCurrentWidget(self._design_tab)
        self._mark_starting_dimensions_pristine(parameters)
        return True

    def _mark_starting_dimensions_pristine(
        self,
        parameters: AntennaDesignParameters,
    ) -> None:
        """Mark a newly generated design as eligible for automatic resizing."""

        if isinstance(parameters, QuadBeamParameters):
            self._quad_beam_form.mark_starting_dimensions_pristine()
        elif isinstance(parameters, HexbeamParameters):
            self._hexbeam_form.mark_starting_dimensions_pristine()
        elif isinstance(parameters, DisconeParameters):
            self._discone_form.mark_starting_dimensions_pristine()
        elif isinstance(parameters, TrapYagiParameters):
            self._trap_yagi_form.mark_starting_dimensions_pristine()
        elif isinstance(parameters, PhasedVerticalParameters):
            self._phased_vertical_form.mark_starting_dimensions_pristine()
        elif isinstance(parameters, YagiParameters):
            self._yagi_form.mark_starting_dimensions_pristine()
        elif isinstance(parameters, MoxonParameters):
            self._moxon_form.mark_starting_dimensions_pristine()

    @history_action("history.measurement_sessions")
    def edit_measurement_sessions(self) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        dialog = MeasurementSessionsDialog(
            self._translator,
            self._project,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        updated = dialog.result_project()
        if updated == self._project:
            return
        self._project = updated
        self._mark_project_dirty()
        self._refresh_measurements()
        self._tabs_select_measurements()
        self._last_status_key = "status.measurement_sessions"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    @history_action("history.project_journal")
    def edit_project_journal(self) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        dialog = JournalDialog(
            self._translator,
            self._project,
            self,
            default_design_id=self._design_id,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        updated = dialog.result_project()
        if updated == self._project:
            return
        self._project = updated
        self._mark_project_dirty()
        self._last_status_key = "status.project_journal"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    def compare_measurements(self, measurement: Measurement | None = None) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if len(self._project.measurements) < 2:
            QMessageBox.information(
                self,
                self._translator.t("measurement.before_after_title"),
                self._translator.t("measurement.comparison_need_two"),
            )
            return
        measurements = tuple(sorted(self._project.measurements, key=lambda item: item.created_at))
        before_id = measurements[-2].id
        after_id = measurements[-1].id
        if measurement is not None and any(item.id == measurement.id for item in measurements):
            index = next(
                index for index, item in enumerate(measurements) if item.id == measurement.id
            )
            if index == 0:
                before_id = measurements[0].id
                after_id = measurements[1].id
            else:
                before_id = measurements[index - 1].id
                after_id = measurements[index].id
        dialog = MeasurementComparisonDialog(
            self._translator,
            measurements,
            self,
            session_names=self._measurement_session_names(),
            initial_before_id=before_id,
            initial_after_id=after_id,
        )
        dialog.exec()
        if self._design_id is not None:
            self._workflow_measurement_compared.add(self._design_id)
        self._update_workflow_ui()

    def tolerance_robustness(self) -> None:
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
        availability = optimizer_availability(design.parameters)
        descriptor = availability.descriptor
        if descriptor is None:
            self._show_error(self._translator.t("robustness.unavailable_family"))
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._base_simulation_spec(design),
        )
        dialog = RobustnessDialog(
            self._translator,
            self._unit_system,
            self._solver,
            descriptor,
            design,
            base_spec,
            self,
        )
        dialog.exec()

    @history_action("history.parameter_sweep")
    def parameter_sweep(self) -> None:
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
        availability = optimizer_availability(design.parameters)
        descriptor = availability.descriptor
        adapter = adapter_for(design.parameters)
        if descriptor is None or adapter is None:
            self._show_error(self._translator.t("sweep.unavailable_family"))
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._base_simulation_spec(design),
        )
        dialog = ParameterSweepDialog(
            self._translator,
            self._unit_system,
            self._solver,
            descriptor,
            design,
            base_spec,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_parameters()
        if selected is None:
            return
        try:
            adapter.apply_parameters(self, selected)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._last_status_key = "status.parameter_sweep_applied"
        self._update_status_text()
        self.simulate()

    @history_action("history.guided_experiment")
    def guided_experiments(self) -> None:
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
        availability = optimizer_availability(design.parameters)
        descriptor = availability.descriptor
        adapter = adapter_for(design.parameters)
        if descriptor is None or adapter is None:
            self._show_error(self._translator.t("guided.unavailable_family"))
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._base_simulation_spec(design),
        )
        dialog = GuidedExperimentsDialog(
            self._translator,
            self._unit_system,
            self._solver,
            descriptor,
            design,
            base_spec,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_parameters()
        if selected is None:
            return
        try:
            adapter.apply_parameters(self, selected)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._last_status_key = "status.guided_experiment_applied"
        self._update_status_text()
        self.simulate()

    @history_action("history.tuning")
    def tune_measurement(self, measurement: Measurement | None = None) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return
        if measurement is None:
            if not self._project.measurements:
                QMessageBox.information(
                    self,
                    self._translator.t("tuning.title"),
                    self._translator.t("tuning.need_measurement"),
                )
                return
            measurement = max(
                self._project.measurements,
                key=lambda item: item.created_at,
            )
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        design = self._project.design_by_id(self._design_id)
        adapter = adapter_for(design.parameters)
        if not self._tuning_supported(design.parameters) or adapter is None:
            self._show_error(self._translator.t("tuning.unavailable_family"))
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._base_simulation_spec(design),
        )
        dialog = TuningAssistantDialog(
            self._translator,
            self._unit_system,
            self._solver,
            design,
            measurement,
            base_spec,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.result_parameters()
        if selected is None:
            return
        try:
            adapter.apply_parameters(self, selected)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._last_status_key = "status.tuning_applied"
        self._update_status_text()
        self.simulate()

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
            sessions=self._project.measurement_sessions,
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
                session_id=dialog.session_id(),
            )
            self._project = self._project.with_updated_measurement(
                updated,
                updated_at=utc_now(),
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.measurement", message=str(exc)))
            return
        self._mark_project_dirty()
        self._refresh_measurements()
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
        self._mark_project_dirty()
        self._refresh_measurements()
        self._tabs_select_measurements()
        self._last_status_key = "status.measurement_deleted"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    @history_action("history.measurement_import")
    def import_vna_data(self) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        paths = choose_vna_paths(self, self._translator)
        if paths:
            self.import_vna_paths(paths)

    def import_vna_paths(self, paths: Sequence[Path]) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        result = import_vna_files(
            parent=self,
            translator=self._translator,
            project=self._project,
            paths=paths,
            mappings=self._vna_column_mappings,
            show_error=self._show_error,
        )
        if result is None:
            return
        self._project = result.project
        if self._design_id is not None:
            self._workflow_measurement_compared.discard(self._design_id)
        self._mark_project_dirty()
        self._refresh_measurements()
        self._tabs_select_measurements()
        self._last_status_key = "status.vna_imported"
        self._update_title()
        self._update_actions()
        self._update_status_text()
        if result.warnings:
            QMessageBox.warning(
                self,
                self._translator.t("dialog.vna_title"),
                self._translator.t(
                    "dialog.vna_warnings",
                    count=len(result.warnings),
                    details="\n".join(result.warnings[:12]),
                ),
            )

    def import_nec_deck(self) -> None:
        if not self._maybe_save_changes():
            return
        try:
            imported = choose_and_import_nec(self, self._translator)
        except Exception as exc:
            self._show_error(self._translator.t("error.import_nec", message=str(exc)))
            return
        if imported is None:
            return
        self._set_project(
            imported.project,
            imported.project.designs[0].id,
            path=None,
            dirty=True,
        )
        if imported.warnings:
            QMessageBox.warning(
                self,
                self._translator.t("dialog.nec_title"),
                self._translator.t(
                    "dialog.nec_warnings",
                    count=len(imported.warnings),
                    details="\n".join(imported.warnings[:12]),
                ),
            )

    def import_mmana_file(self) -> None:
        if not self._maybe_save_changes():
            return
        try:
            imported = choose_and_import_mmana(self, self._translator)
        except Exception as exc:
            self._show_error(self._translator.t("error.import_mmana", message=str(exc)))
            return
        if imported is None:
            return
        self._set_project(
            imported.project,
            imported.project.designs[0].id,
            path=None,
            dirty=True,
        )
        if imported.warnings:
            QMessageBox.warning(
                self,
                self._translator.t("dialog.mmana_title"),
                self._translator.t(
                    "dialog.mmana_warnings",
                    count=len(imported.warnings),
                    details="\n".join(imported.warnings[:12]),
                ),
            )

    def _tuning_supported(self, parameters: AntennaDesignParameters | None) -> bool:
        if parameters is None or adapter_for(parameters) is None:
            return False
        try:
            primary_dimension_m(parameters)
        except TypeError:
            return False
        return True

    def _sweep_supported(self, parameters: AntennaDesignParameters | None) -> bool:
        if parameters is None or adapter_for(parameters) is None:
            return False
        return optimizer_availability(parameters).descriptor is not None

    def _robustness_supported(
        self,
        parameters: AntennaDesignParameters | None,
    ) -> bool:
        if parameters is None:
            return False
        return optimizer_availability(parameters).descriptor is not None

    def _measurement_session_names(self) -> dict[UUID, str]:
        if self._project is None:
            return {}
        return {session.id: session.name for session in self._project.measurement_sessions}

    def _refresh_measurements(self) -> None:
        if self._project is None:
            self._results.set_measurements(())
            return
        self._results.set_measurements(
            self._project.measurements,
            self._measurement_session_names(),
            self._project.measurement_sessions,
        )

    def _tabs_select_measurements(self) -> None:
        self._results.show_measurements()

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
        self._mark_project_dirty()
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
            dialog: Any = InvertedVDialog(
                self._translator,
                self._unit_system,
                self,
                parameters=InvertedVParameters.from_custom_parameters(parameters),
            )
        elif parameters.generator_id == "inverted_l":
            dialog = InvertedLDialog(
                self._translator,
                self._unit_system,
                self,
                parameters=InvertedLParameters.from_custom_parameters(parameters),
            )
        elif parameters.generator_id == "magnetic_loop":
            dialog = MagneticLoopDialog(
                self._translator,
                self._unit_system,
                self,
                parameters=MagneticLoopParameters.from_custom_parameters(parameters),
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
        elif parameters.generator_id in {"half_square", "bobtail_curtain"}:
            dialog = ScvDialog(
                self._translator,
                self._unit_system,
                self,
                parameters=ScvParameters.from_custom_parameters(parameters),
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
        self._mark_project_dirty()
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
        self._mark_project_dirty()
        self._invalidate_design_result(self._design_id)
        self._results.set_result(None)
        self._results.set_design(updated_design)
        self._set_geometry_model(updated_design)
        self._update_custom_panel(updated_design)
        self._update_title()
        self._update_actions()

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
        try:
            change = change_template_selection(self._catalog_context(), selected)
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        if change is None:
            return
        parameters = change.parameters
        feed_line = change.feed_line
        if (
            selected == catalog_key_for(design.parameters)
            and type(parameters) is type(design.parameters)
            and hasattr(parameters, "material")
            and cast(Any, parameters).material == default_material_for_template(selected)
        ):
            parameters = replace(
                parameters,
                material=cast(Any, design.parameters).material,
            )
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
            band_line = feed_line if feed_line is not None else self._feed_line
            band_default = default_band_plan(
                parameters,
                high_impedance_feed_line=(
                    band_line is not None and band_line.characteristic_impedance_ohm >= 300.0
                ),
            )
            updated_design = design.with_parameters(parameters).with_band_plan(band_default.plan)
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
        self._mark_project_dirty()
        self._select_design(self._design_id)
        self._mark_starting_dimensions_pristine(parameters)
        self._last_status_key = "status.design_changed"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    def show_reference_library(self) -> None:
        if not self._maybe_save_changes():
            return
        dialog = ReferenceLibraryDialog(self._translator, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        reference = dialog.selected_reference()
        if reference is None:
            return
        try:
            band_default = default_band_plan(reference.parameters)
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        created = self._create_project_from_parameters(
            reference.parameters,
            default_name=self._translator.t(reference.project_name_key),
            band_plan=band_default.plan,
            description=self._translator.t(
                "reference.library.project_description",
                published=self._translator.t(reference.published_key),
            ),
        )
        if not created:
            return
        self._last_status_key = "status.reference_opened"
        self._update_status_text()
        if dialog.simulate_after_open() and self._solver is not None:
            self.simulate()

    def show_antenna_advisor(self) -> None:
        if not self._maybe_save_changes():
            return
        profile = self._project.active_installation_profile if self._project is not None else None
        dialog = AntennaAdvisorDialog(
            self._translator,
            self._unit_system,
            initial_height_m=(profile.available_height_m if profile is not None else None),
            initial_width_m=(profile.available_width_m if profile is not None else None),
            portable=(profile is not None and profile.support is InstallationSupport.PORTABLE),
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_catalog_key()
        if selected is not None:
            self.new_antenna_from_key(selected)

    def _catalog_context(self) -> CatalogContext:
        frequency_hz = None
        if self._project is not None and self._design_id is not None:
            frequency_hz = self._project.design_by_id(self._design_id).parameters.frequency_hz
        return CatalogContext(
            parent=self,
            translator=self._translator,
            unit_system=self._unit_system,
            solver=self._solver,
            matching_network=self._matching_network,
            current_frequency_hz=frequency_hz,
            current_feed_line=self._feed_line,
        )

    def new_antenna_from_key(self, key: str) -> None:
        if not self._maybe_save_changes():
            return
        try:
            selection = new_antenna_selection(self._catalog_context(), key)
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        if selection is None:
            return
        self._create_project_from_parameters(
            selection.parameters,
            default_name=selection.default_name,
            feed_line=selection.feed_line,
            band_plan=selection.band_plan,
        )

    def new_antenna(self) -> None:
        dialog = AntennaCatalogDialog(self._translator, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_key()
        if selected is not None:
            self.new_antenna_from_key(selected)

    def new_dipole(self) -> None:
        self.new_antenna()

    def _refresh_start_page_recents(self) -> None:
        self._start_page.set_recent_projects(self._recent_projects.load())

    def _open_project_path(self, path: Path, *, show_error: bool = True) -> bool:
        try:
            project = self._project_io.load(path)
            if not project.designs:
                raise ValueError("project has no designs")
        except Exception as exc:
            if show_error:
                self._show_error(self._translator.t("error.open", message=str(exc)))
            return False
        self._set_project(
            project,
            project.designs[0].id,
            path=path,
            dirty=False,
        )
        self._last_status_key = "status.opened"
        self._update_status_text()
        return True

    def open_project(self) -> None:
        if not self._maybe_save_changes():
            return
        start = self._current_path.parent if self._current_path is not None else Path.home()
        path = self._project_io.choose_open_path(start)
        if path is not None:
            self._open_project_path(path)

    def open_recent_project(self, path: str) -> None:
        if not self._maybe_save_changes():
            return
        target = Path(path)
        if not target.is_file():
            self._show_error(
                self._translator.t(
                    "error.open",
                    message=self._translator.t("error.file_missing", name=target.name),
                )
            )
            self._recent_projects.remove(target)
            self._refresh_start_page_recents()
            return
        self._open_project_path(target)

    def remove_recent_project(self, path: str) -> None:
        self._recent_projects.remove(Path(path))
        self._refresh_start_page_recents()
        self._last_status_key = "status.recent_removed"
        self._update_status_text()

    def _restore_last_project(self) -> None:
        if self._project is not None:
            return
        entries = self._recent_projects.load()
        if not entries:
            return
        path = entries[0].path
        if not path.is_file():
            self._recent_projects.remove(path)
            self._refresh_start_page_recents()
            self._last_status_key = "status.recent_missing"
            self._update_status_text()
            return
        if not self._open_project_path(path, show_error=False):
            self._recent_projects.remove(path)
            self._refresh_start_page_recents()
            self._last_status_key = "status.recent_missing"
            self._update_status_text()

    def _autosave_now(self) -> bool:
        if (
            not self._autosave_enabled
            or not self._recovery_controller.available
            or self._project is None
            or not self._design_dirty
            or not self._autosave_pending
            or self._simulating
        ):
            return False
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception:
                return False
        if not self._recovery_controller.save(self._project, self._current_path):
            return False
        self._autosave_pending = False
        return True

    def _startup_recovery(self) -> None:
        if self._project is not None:
            return
        if self._recovery is not None and self._autosave_enabled:
            snapshot = self._recovery_controller.load()
            if snapshot is not None:
                decision = self._recovery_controller.offer(snapshot)
                if decision.restore:
                    self._set_project(
                        snapshot.project,
                        snapshot.project.designs[0].id,
                        path=decision.path,
                        dirty=True,
                    )
                    self._last_status_key = "status.recovered"
                    self._update_status_text()
        elif self._recovery is not None:
            self._recovery_controller.clear()
        if self._project is None and self._restore_last_project_preference:
            self._restore_last_project()

    def open_example(self, kind: str) -> None:
        if not self._maybe_save_changes():
            return
        if kind == "dipole":
            parameters: AntennaDesignParameters = DipoleParameters(
                frequency_hz=7_100_000.0,
                total_length_m=20.0,
                height_m=8.0,
            )
            default_name = "Wire dipole"
        elif kind == "yagi":
            parameters = nbs_five_element(
                frequency_hz=14_100_000.0,
                height_m=10.0,
            )
            default_name = "Yagi"
        elif kind == "vertical":
            parameters = VerticalParameters(
                frequency_hz=14_100_000.0,
                height_m=5.0,
                base_height_m=0.25,
                radial_count=4,
                radial_length_m=2.5,
            )
            default_name = "Vertical"
        else:
            raise ValueError(f"unknown example: {kind}")
        self._create_project_from_parameters(
            parameters,
            default_name=default_name,
            ask_name=False,
        )

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
        path = self._project_io.choose_save_path(self._project.name)
        if path is None:
            return False
        return self._save_to(path)

    def _bundle_suggested_path(self) -> Path:
        name = self._project.name if self._project is not None else "project"
        safe_name = name.replace("/", "-").replace("\\", "-")
        parent = self._current_path.parent if self._current_path is not None else Path.home()
        return parent / f"{safe_name}{BUNDLE_EXTENSION}"

    @history_action("history.export_bundle")
    def export_project_bundle(self) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.export_bundle_title"),
            str(self._bundle_suggested_path()),
            self._translator.t("dialog.project_bundle_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != BUNDLE_EXTENSION:
            path = path.with_suffix(BUNDLE_EXTENSION)
        try:
            result = self._run_export_bundle(path)
        except Exception as exc:
            self._show_error(self._translator.t("error.export_bundle", message=str(exc)))
            return
        self._last_status_key = "status.bundle_exported"
        self._update_status_text()
        if result.missing_assets:
            self._show_bundle_missing_assets(result.missing_assets)

    def import_project_bundle(self) -> None:
        if not self._maybe_save_changes():
            return
        start = (
            str(self._current_path.parent) if self._current_path is not None else str(Path.home())
        )
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self._translator.t("dialog.import_bundle_title"),
            start,
            self._translator.t("dialog.project_bundle_filter"),
        )
        if not filename:
            return
        destination = QFileDialog.getExistingDirectory(
            self,
            self._translator.t("dialog.import_bundle_destination"),
            start,
        )
        if not destination:
            return
        try:
            result = self._run_import_bundle(Path(filename), Path(destination))
        except Exception as exc:
            self._show_error(self._translator.t("error.import_bundle", message=str(exc)))
            return
        if not result.project.designs:
            self._show_error(
                self._translator.t(
                    "error.import_bundle",
                    message=self._translator.t("error.bundle_no_designs"),
                )
            )
            return
        self._set_project(
            result.project,
            result.project.designs[0].id,
            path=result.project_path,
            dirty=False,
        )
        self._last_status_key = "status.bundle_imported"
        self._update_status_text()
        if result.missing_assets:
            self._show_bundle_missing_assets(result.missing_assets)

    def _run_export_bundle(self, path: Path) -> BundleExportResult:
        if self._project is None:
            raise RuntimeError("no project to export")
        worker = ProjectBundleExportWorker(
            ExportProjectBundle(self._repository),
            self._project,
            path,
            base_dir=self._current_path.parent if self._current_path is not None else None,
        )
        result = self._project_io.run_bundle_worker(worker, "status.exporting_bundle")
        if not isinstance(result, BundleExportResult):
            raise RuntimeError("bundle export worker produced no result")
        return result

    def _run_import_bundle(
        self,
        bundle_path: Path,
        destination_parent: Path,
    ) -> BundleImportResult:
        worker = ProjectBundleImportWorker(
            ImportProjectBundle(self._repository),
            bundle_path,
            destination_parent,
        )
        result = self._project_io.run_bundle_worker(worker, "status.importing_bundle")
        if not isinstance(result, BundleImportResult):
            raise RuntimeError("bundle import worker produced no result")
        return result

    def _show_bundle_missing_assets(self, assets: tuple[str, ...]) -> None:
        shown = "\n".join(assets[:10])
        if len(assets) > 10:
            shown += "\n…"
        QMessageBox.warning(
            self,
            self._translator.t("dialog.bundle_missing_title"),
            self._translator.t(
                "dialog.bundle_missing",
                count=len(assets),
                assets=shown,
            ),
        )

    def _save_to(self, path: Path) -> bool:
        before = self._history_snapshot()
        try:
            project = self._apply_fields()
            after = self._history_snapshot()
            self._record_history("history.save", before, after)
            payload = self._project_io.prepare_payload(project)
            size = len(payload)
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
            self._project_io.write(path, payload)
        except Exception as exc:
            self._show_error(self._translator.t("error.save", message=str(exc)))
            return False
        self._current_path = path
        if self._project is not None:
            self._recent_projects.add(path, self._project.name)
            self._refresh_start_page_recents()
        self._recovery_controller.clear()
        self._dirty = False
        self._design_dirty = False
        self._autosave_pending = False
        self._form_dirty = False
        self._recovery_controller.stop_debounce()
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
        self._mark_project_dirty()
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
        self._mark_project_dirty()
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
        self._mark_project_dirty()
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
        optimizer_available = optimizer_availability(design.parameters).available
        dialog = DesignFromFrequencyDialog(
            self._translator,
            self._unit_system,
            initial_parameters=design.parameters,
            can_refine=self._solver is not None and optimizer_available,
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
        self._mark_project_dirty()
        self._select_design(self._design_id)
        self._mark_starting_dimensions_pristine(parameters)
        self._last_status_key = "status.design_estimated"
        self._update_title()
        self._update_actions()
        self._update_status_text()
        refine_requested = getattr(dialog, "refine_requested", lambda: False)()
        if refine_requested and self._solver is not None and optimizer_available:
            self._open_refinement_for_current_design()

    @history_action("history.scale_frequency")
    def scale_geometry_to_frequency(self) -> None:
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
        if not supports_frequency_scaling(design.parameters):
            self._show_error(self._translator.t("scale_frequency.unsupported"))
            return
        dialog = ScaleFrequencyDialog(
            self._translator,
            design.parameters.frequency_hz,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            parameters = scaled_to_frequency(
                design.parameters,
                dialog.target_frequency_hz(),
            )
            updated_design = design.with_parameters(parameters)
            self._project = self._project.with_design(updated_design, updated_at=utc_now())
        except (UnsupportedFrequencyScaleError, ValueError, TypeError) as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._invalidate_design_result(self._design_id)
        self._mark_project_dirty()
        self._select_design(self._design_id)
        self._last_status_key = "status.frequency_scaled"
        self._update_title()
        self._update_actions()
        self._update_status_text()

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
        if isinstance(previous, T2FDParameters) and isinstance(estimated, T2FDParameters):
            updates.update(
                termination_resistance_ohm=previous.termination_resistance_ohm,
                transformer_ratio=previous.transformer_ratio,
            )
        elif isinstance(previous, EndFedParameters) and isinstance(estimated, EndFedParameters):
            updates.update(
                preset=previous.preset,
                transformer_ratio=previous.transformer_ratio,
                transformer_loss_model=previous.transformer_loss_model,
                return_path=previous.return_path,
                installation_return_length_m=previous.installation_return_length_m,
                counterpoise_length_m=previous.counterpoise_length_m,
                counterpoise_height_m=previous.counterpoise_height_m,
                counterpoise_azimuth_deg=previous.counterpoise_azimuth_deg,
            )
        elif isinstance(previous, OCFDParameters) and isinstance(estimated, OCFDParameters):
            updates.update(
                feed_ratio=previous.feed_ratio,
                transformer_ratio=previous.transformer_ratio,
            )
        elif (
            isinstance(previous, FoldedDipoleParameters)
            and isinstance(estimated, FoldedDipoleParameters)
        ) or (isinstance(previous, LoopParameters) and isinstance(estimated, LoopParameters)):
            updates["transformer_ratio"] = previous.transformer_ratio
        elif isinstance(previous, JPoleParameters) and isinstance(estimated, JPoleParameters):
            updates.update(folded=previous.folded, gap_m=previous.gap_m)
        elif isinstance(previous, RingoParameters) and isinstance(estimated, RingoParameters):
            updates["ring_sides"] = previous.ring_sides
        elif isinstance(previous, QuadBeamParameters) and isinstance(estimated, QuadBeamParameters):
            updates.update(
                reflector_scale=previous.reflector_scale,
                director_scale=previous.director_scale,
                transformer_ratio=previous.transformer_ratio,
            )
        elif isinstance(previous, YagiParameters) and isinstance(estimated, YagiParameters):
            updates["driven_index"] = previous.driven_index
            updates["driven_folded"] = previous.driven_folded
            updates["driven_fold_spacing_m"] = previous.driven_fold_spacing_m
            updates["match_type"] = previous.match_type
            updates["match_length_m"] = previous.match_length_m
            updates["match_spacing_m"] = previous.match_spacing_m
            updates["transformer_ratio"] = previous.transformer_ratio
            if previous.elements and estimated.elements:
                radius_m = previous.elements[0].radius_m
                estimated = replace(
                    estimated,
                    elements=tuple(
                        replace(element, radius_m=radius_m) for element in estimated.elements
                    ),
                )
        return replace(cast(Any, estimated), **updates)

    def _prepare_optimization(
        self,
        *,
        apply_form: bool = True,
    ) -> tuple[DesignVariant, AntennaSolver] | None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return None
        if self._solver is None:
            self._show_error(self._translator.t("error.solver"))
            return None
        if apply_form and self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return None
        return self._project.design_by_id(self._design_id), self._solver

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
        design = self._project.design_by_id(self._design_id)
        band_plan = self._current_band_plan(design)
        operating_frequencies = operating_frequencies_for(design.parameters, band_plan)
        hexbeam_band = self._optimizer_hexbeam_band(design.parameters)
        availability = optimizer_availability(design.parameters, hexbeam_band=hexbeam_band)
        if availability.descriptor is None:
            self._show_error(
                self._translator.t(
                    availability.reason_key or "optimize.unavailable.unsupported",
                    **availability.reason_values,
                )
            )
            return
        adapter = adapter_for(design.parameters)
        if adapter is None:
            self._show_error(self._translator.t("optimize.unavailable.unsupported"))
            return
        target_band_label: str | None = None
        band_edges_hz = self._optimizer_band_edges(design)
        band_plan_source = BandPlanSource.CURRENT_PLAN if band_edges_hz else BandPlanSource.FALLBACK
        band_plan_bands = len(band_plan.selections)
        target_model = design.antenna
        if isinstance(design.parameters, HexbeamParameters) and hexbeam_band is not None:
            target = next(
                (
                    band
                    for band in design.parameters.bands
                    if band.label.casefold() == hexbeam_band.casefold()
                ),
                None,
            )
            if target is not None:
                base_spec = self._typed_simulation_spec(
                    design.parameters,
                    active_hexbeam_band=hexbeam_band,
                )
                target_model = design.parameters.to_antenna(active_band=hexbeam_band)
                operating_frequencies = (target.frequency_hz,)
                band_edges_hz = ()
                band_plan_source = BandPlanSource.FALLBACK
                band_plan_bands = 0
                target_band_label = self._translator.t(f"hexbeam.band.{hexbeam_band}")
            else:
                base_spec = adapter.simulation_spec(self, design.parameters)
        else:
            base_spec = adapter.simulation_spec(self, design.parameters)
        base_spec = replace(
            base_spec,
            timeout_s=float(self._solver_timeout.value()),
        )
        base_spec = self._with_model_quality(target_model, base_spec)
        base_spec = self._with_project_chain(design.parameters, base_spec)
        choice = run_family_optimization_dialog(
            self,
            self._translator,
            self._unit_system,
            self._solver,
            availability.descriptor,
            base_spec,
            topology_label=self._translator.t(label_key_for(design.parameters)),
            target_band_label=target_band_label,
            band_edges_hz=band_edges_hz,
            band_plan_source=band_plan_source,
            band_plan_bands=band_plan_bands,
            operating_frequencies_hz=operating_frequencies,
            last_summary=design.optimization_summary,
        )
        if choice is None:
            return
        selected, result = choice
        try:
            adapter.apply_parameters(self, selected)
            self._form_dirty = True
            self._apply_fields()
            if result is not None and result.summary is not None:
                current = self._project.design_by_id(self._design_id)
                self._project = self._project.with_design(
                    current.with_optimization_summary(result.summary),
                    updated_at=utc_now(),
                )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        updated_design = self._project.design_by_id(self._design_id)
        summary = result.summary if result is not None else None
        if (
            summary is not None
            and summary.mode in {OptimizationMode.BAND_AWARE, OptimizationMode.ROBUST}
            and band_plan
        ):
            self._start_band_analysis(updated_design, band_plan)
        else:
            self.simulate()

    def _optimizer_band_edges(self, design: DesignVariant) -> tuple[float, ...]:
        plan = self._current_band_plan(design)
        edges: list[float] = []
        for selection in plan.selections:
            edges.extend(
                (
                    selection.band.start_hz,
                    selection.band.center_hz,
                    selection.band.stop_hz,
                )
            )
        return tuple(dict.fromkeys(edges))

    @history_action("history.optimize")
    def optimize_length(self) -> None:
        prepared = self._prepare_optimization()
        if prepared is None:
            return
        design, solver = prepared
        if isinstance(
            design.parameters,
            (DipoleParameters, FoldedDipoleParameters, LoopParameters),
        ):
            base_spec = self._form.simulation_spec()
        else:
            base_spec = self._typed_simulation_spec(design.parameters)
        base_spec = replace(
            base_spec,
            timeout_s=float(self._solver_timeout.value()),
        )
        base_spec = self._with_project_chain(design.parameters, base_spec)
        dimension = run_length_optimization_dialog(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            base_spec,
        )
        if dimension is None:
            return
        try:
            parameters = with_primary_dimension(design.parameters, dimension)
            adapter = adapter_for(parameters)
            if adapter is not None:
                adapter.apply_parameters(self, parameters)
            else:
                self._form.set_parameters(parameters, reset_sweep=False)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    @history_action("history.optimize")
    def synthesize_dimensions(self) -> None:
        prepared = self._prepare_optimization()
        if prepared is None:
            return
        design, solver = prepared
        if not isinstance(design.parameters, (OCFDParameters, JPoleParameters)):
            return
        synthesis_spec = replace(
            self._typed_simulation_spec(design.parameters),
            timeout_s=float(self._solver_timeout.value()),
        )
        synthesis_spec = self._with_project_chain(design.parameters, synthesis_spec)
        selected = run_synthesis_dialog(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            synthesis_spec,
        )
        if selected is None:
            return
        adapter = adapter_for(selected)
        if adapter is None:
            return
        try:
            adapter.apply_parameters(self, selected)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    @history_action("history.optimize")
    def optimize_yagi_elements(self) -> None:
        prepared = self._prepare_optimization()
        if prepared is None:
            return
        design, solver = prepared
        if not isinstance(design.parameters, YagiParameters):
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._typed_simulation_spec(design.parameters),
        )
        selected = optimize_yagi_elements(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            base_spec,
        )
        if selected is None:
            return
        try:
            self._yagi_form.set_parameters(selected)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    def optimize_fan_dipole_elements(self) -> None:
        prepared = self._prepare_optimization()
        if prepared is None:
            return
        design, solver = prepared
        if not isinstance(design.parameters, FanDipoleParameters):
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._typed_simulation_spec(design.parameters),
        )
        selected = optimize_fan_dipole_elements(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            base_spec,
            selected_band_id=self._selected_band_ids.get(design.id),
        )
        if selected is None:
            return
        try:
            self._fan_dipole_form.set_parameters(selected)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    def optimize_moxon_elements(self) -> None:
        prepared = self._prepare_optimization()
        if prepared is None:
            return
        design, solver = prepared
        if not isinstance(design.parameters, MoxonParameters):
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._typed_simulation_spec(design.parameters),
        )
        selected = optimize_moxon_elements(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            base_spec,
        )
        if selected is None:
            return
        try:
            self._moxon_form.set_parameters(selected)
            self._form_dirty = True
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

    def optimize_loop_elements(self) -> None:
        prepared = self._prepare_optimization(apply_form=False)
        if prepared is None:
            return
        design, solver = prepared
        if not isinstance(design.parameters, LoopParameters):
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._form.simulation_spec(),
        )
        selected = optimize_loop_elements(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            base_spec,
        )
        if selected is None:
            return
        self._form.set_parameters(selected, reset_sweep=False)
        self._form_dirty = True
        self._apply_fields()
        self.simulate()

    def optimize_vertical_elements(self) -> None:
        prepared = self._prepare_optimization(apply_form=False)
        if prepared is None:
            return
        design, solver = prepared
        if not isinstance(design.parameters, VerticalParameters):
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._typed_simulation_spec(design.parameters),
        )
        selected = optimize_vertical_elements(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            base_spec,
        )
        if selected is None:
            return
        self._vertical_form.set_parameters(selected)
        self._form_dirty = True
        self._apply_fields()
        self.simulate()

    def optimize_inverted_v_elements(self) -> None:
        prepared = self._prepare_optimization(apply_form=False)
        if prepared is None:
            return
        design, solver = prepared
        if not isinstance(design.parameters, InvertedVParameters):
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._typed_simulation_spec(design.parameters),
        )
        selected = optimize_inverted_v_elements(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            base_spec,
        )
        if selected is None:
            return
        self._inverted_v_form.set_parameters(selected)
        self._form_dirty = True
        self._apply_fields()
        self.simulate()

    def optimize_ringo_elements(self) -> None:
        prepared = self._prepare_optimization(apply_form=False)
        if prepared is None:
            return
        design, solver = prepared
        if not isinstance(design.parameters, RingoParameters):
            return
        base_spec = self._with_project_chain(
            design.parameters,
            self._typed_simulation_spec(design.parameters),
        )
        selected = optimize_ringo_elements(
            self,
            self._translator,
            self._unit_system,
            solver,
            design.parameters,
            base_spec,
        )
        if selected is None:
            return
        self._ringo_form.set_parameters(selected)
        self._form_dirty = True
        self._apply_fields()
        self.simulate()

    def optimize_zs6bkw_elements(self) -> None:
        prepared = self._prepare_optimization(apply_form=False)
        if prepared is None:
            return
        design, solver = prepared
        parameters = design.parameters
        if (
            not isinstance(parameters, CustomAntennaParameters)
            or parameters.generator_id != "zs6bkw"
        ):
            return
        base_spec = self._with_project_chain(
            parameters,
            self._typed_simulation_spec(parameters),
        )
        selected = optimize_zs6bkw_elements(
            self,
            self._translator,
            self._unit_system,
            solver,
            parameters,
            base_spec,
        )
        if selected is None:
            return
        if self._project is None:
            return
        updated = design.with_parameters(selected)
        self._project = self._project.with_design(updated, updated_at=utc_now())
        self._loads = updated.antenna.loads
        self._form_dirty = False
        self._mark_project_dirty()
        self._invalidate_design_result(self._design_id)
        self._results.set_result(None)
        self._results.set_design(updated)
        self._set_geometry_model(updated)
        self._design_stack.setCurrentWidget(self._custom_panel)
        self._update_custom_panel(updated)
        self._auto_select_view(updated)
        self._update_title()
        self._update_actions()
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
        self._mark_project_dirty()
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
        self._mark_project_dirty()
        self.apply_design()
        self._last_status_key = "status.design_changed"
        self._update_status_text()

    def _preflight_report_for_current_design(self) -> PreflightReport | None:
        if self._preflight_runner is None:
            return None
        if self._project is None or self._design_id is None:
            return None
        design = self._project.design_by_id(self._design_id)
        spec = self._with_project_chain(
            design.parameters,
            self._base_simulation_spec(design),
        )
        return self._preflight_runner(
            self._project,
            design,
            spec,
            result=self._simulation_results.get(self._design_id),
        )

    def show_preflight(self) -> None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        if self._form_dirty:
            try:
                self._apply_fields()
            except Exception as exc:
                self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
                return
        report = self._preflight_report_for_current_design()
        if report is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        dialog = PreflightDialog(self._translator, report, self)
        dialog.exec()
        action = dialog.selected_action
        if action is not None:
            self._handle_preflight_action(action)

    def _handle_preflight_action(self, action: PreflightAction) -> None:
        if action is PreflightAction.EDIT_LOADS:
            self.edit_loads()
            return
        if action is PreflightAction.EDIT_LINES:
            self.edit_transmission_lines()
            return
        if action is PreflightAction.EDIT_SUPPORTS:
            self.edit_installation_profile()
            return
        if action is PreflightAction.EDIT_CONSTRUCTION:
            self.edit_construction_record()
            return
        if action is PreflightAction.RUN_SIMULATION:
            self.simulate()
            return
        if action is PreflightAction.NONE:
            return
        if action is PreflightAction.EDIT_GEOMETRY:
            design = (
                self._project.design_by_id(self._design_id)
                if self._project is not None and self._design_id is not None
                else None
            )
            if design is not None and isinstance(design.parameters, CustomAntennaParameters):
                self.edit_custom_wires()
                return
        self._design_panel.setFocus()
        current = self._design_stack.currentWidget()
        if current is not None:
            current.setFocus()

    @history_action("history.construction_record")
    def edit_construction_record(self) -> None:
        if self._project is None:
            self._show_error(self._translator.t("error.no_project"))
            return
        dialog = ConstructionRecordDialog(
            self._translator,
            self._unit_system,
            self._project.construction_record,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._project = self._project.with_construction_record(
            dialog.record(),
            updated_at=utc_now(),
        )
        self._mark_project_dirty()
        self._last_status_key = "status.construction_record"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    @history_action("history.bom_costs")
    def edit_bom_costs(self) -> None:
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
        dialog = BomCostsDialog(
            self._translator,
            self._project,
            design,
            self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        record = dialog.result_bom_costs()
        if record == self._project.bom_costs:
            return
        self._project = self._project.with_bom_costs(
            record,
            updated_at=utc_now(),
        )
        self._mark_project_dirty()
        self._last_status_key = "status.bom_costs_saved"
        self._update_title()
        self._update_actions()
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
        try:
            figure_image = self._geometry.construction_image()
            auxiliary_image = self._geometry.auxiliary_image()
            isometric_image = self._geometry.three_d_image()
            auxiliary_kind = self._geometry.auxiliary_view_kind()
        except OSError:
            figure_image = None
            auxiliary_image = None
            isometric_image = None
            auxiliary_kind = None
        try:
            figure_svg = self._geometry.construction_svg()
            auxiliary_svg = self._geometry.auxiliary_svg()
            isometric_svg = self._geometry.three_d_svg()
        except OSError:
            figure_svg = None
            auxiliary_svg = None
            isometric_svg = None
        dialog = ConstructionDialog(
            self._translator,
            self._project,
            design,
            result,
            self,
            figure_image=figure_image,
            auxiliary_image=auxiliary_image,
            isometric_image=isometric_image,
            figure_svg=figure_svg,
            auxiliary_svg=auxiliary_svg,
            isometric_svg=isometric_svg,
            auxiliary_kind=auxiliary_kind,
            preflight=self._preflight_report_for_current_design(),
            display_units=DisplayUnits(self._unit_system, self._length_policy),
        )
        dialog.exec()
        self._workflow_construction_viewed.add(self._design_id)
        self._update_workflow_ui()

    def compare_variants(self) -> None:
        if self._project is None or len(self._project.designs) < 2:
            return
        current = self._design_id or self._project.designs[0].id
        initial_ids = [current]
        for design in self._project.designs:
            if design.id != current and len(initial_ids) < 4:
                initial_ids.append(design.id)
        dialog = ComparisonDialog(
            self._translator,
            self._project,
            self._simulation_results,
            self,
            band_analyses=self._band_analysis_results,
            unit_system=self._unit_system,
            initial_basis=self._default_comparison_basis(),
            initial_design_ids=initial_ids,
            height_mapping=self._comparison_height_mapping,
        )
        dialog.recompute_requested.connect(
            lambda basis, design_ids: self._start_comparison(
                dialog,
                basis,
                design_ids,
            )
        )
        dialog.rejected.connect(self._cancel_comparison_if_running)
        self._comparison_dialog = dialog
        try:
            dialog.exec()
        finally:
            self._comparison_dialog = None
            self._comparison_basis = None
            self._comparison_height_mapping = {}

    def _default_comparison_basis(self) -> ComparisonBasis:
        if self._project is None:
            raise ValueError(self._translator.t("error.no_project"))
        design = (
            self._project.design_by_id(self._design_id)
            if self._design_id is not None
            else self._project.designs[0]
        )
        spec = self._apply_sweep_override(design, self._base_simulation_spec(design))
        plan = spec.frequency_plan
        reference_hz = design.parameters.frequency_hz
        if not plan.start_hz <= reference_hz <= plan.stop_hz:
            reference_hz = plan.start_hz + (plan.stop_hz - plan.start_hz) / 2.0
        height = native_height_m(design.parameters)
        return ComparisonBasis(
            frequency_plan=plan,
            ground=design.parameters.ground,
            reference_height_m=height,
            reference_frequency_hz=reference_hz,
        )

    def _build_comparison_runs(
        self,
        basis: ComparisonBasis,
        design_ids: object,
    ) -> tuple[tuple[ComparisonRun, ...], dict[UUID, tuple[bool, tuple[str, ...]]]]:
        if self._project is None:
            raise ValueError(self._translator.t("error.no_project"))
        runs: list[ComparisonRun] = []
        height_mapping: dict[UUID, tuple[bool, tuple[str, ...]]] = {}
        if not isinstance(design_ids, (tuple, list)):
            return (), {}
        for value in design_ids:
            if not isinstance(value, UUID):
                continue
            design = self._project.design_by_id(value)
            application = apply_comparison_basis(design, basis)
            height_mapping[value] = (
                application.height_mapped,
                application.warnings,
            )
            spec = replace(
                self._base_simulation_spec(application.design),
                frequency_plan=basis.frequency_plan,
                pattern_frequencies_hz=(basis.reference_frequency_hz,),
            )
            spec = self._fit_spec_to_budget(application.design.antenna, spec)
            spec = self._with_project_chain(application.design.parameters, spec)
            runs.append(
                ComparisonRun(
                    design_id=value,
                    name=design.name,
                    model=application.design.antenna,
                    spec=spec,
                )
            )
        return tuple(runs), height_mapping

    def _start_comparison(
        self,
        dialog: ComparisonDialog,
        basis: ComparisonBasis,
        design_ids: object,
    ) -> None:
        if self._simulating or self._solver is None or self._project is None:
            if self._solver is None:
                dialog.set_error(self._translator.t("error.solver"))
            return
        if not isinstance(design_ids, (tuple, list)) or len(design_ids) < 2:
            return
        try:
            runs, height_mapping = self._build_comparison_runs(basis, design_ids)
        except Exception as exc:
            dialog.set_error(str(exc))
            return
        if len(runs) < 2:
            return
        self._comparison_dialog = dialog
        self._comparison_basis = basis
        self._comparison_height_mapping = height_mapping
        dialog.set_recomputing(True)
        self._cancel_token = EventCancelToken()
        self._simulating = True
        self._last_status_key = "status.comparing"
        self._update_actions()
        self._update_status_text()
        self._start_determinate_progress(len(runs), "status.comparing")
        thread = QThread(self)
        worker = ComparisonWorker(
            self._solver,
            CompareDesignsCommand(
                runs=tuple(runs),
                cancel_token=self._cancel_token,
            ),
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self._on_comparison_progress)
        worker.finished.connect(self._on_comparison_finished)
        worker.failed.connect(self._on_comparison_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_worker_thread_finished)
        self._thread = thread
        self._worker = worker
        thread.start()

    def _on_comparison_progress(self, index: int, total: int, name: str) -> None:
        self._task_progress.set_progress(
            index,
            "status.comparing_progress",
            index=index,
            total=total,
            name=name,
        )
        self._status_label.setText(
            self._translator.t(
                "status.comparing_progress",
                index=index,
                total=total,
                name=name,
            )
        )

    def _on_comparison_finished(self, outcome: object) -> None:
        self._simulating = False
        self._cancel_token = None
        self._finish_progress()
        if not isinstance(outcome, ComparisonOutcome):
            return
        dialog = self._comparison_dialog
        results = {
            item.design_id: item.result for item in outcome.results if item.result is not None
        }
        if dialog is not None:
            dialog.set_results(
                results,
                basis=self._comparison_basis,
                band_analyses={},
                height_mapping=self._comparison_height_mapping,
            )
        self._last_status_key = (
            "status.comparison_cancelled" if outcome.cancelled else "status.comparison_done"
        )
        self._update_actions()
        self._update_status_text()

    def _on_comparison_failed(self, message: str) -> None:
        self._simulating = False
        self._cancel_token = None
        self._finish_progress()
        dialog = self._comparison_dialog
        if dialog is not None:
            dialog.set_error(message)
        self._last_status_key = "status.error"
        self._update_actions()
        self._status_label.setText(self._translator.t("status.error"))
        self._show_error(self._translator.t("error.simulation", message=message))

    def _cancel_comparison_if_running(self) -> None:
        if self._simulating and isinstance(self._worker, ComparisonWorker):
            self.cancel_simulation()

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

    def _design_export_context(self) -> ExportContext | None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return None
        return ExportContext(
            parent=self,
            translator=self._translator,
            project=self._project,
            design=self._project.design_by_id(self._design_id),
            display_units=DisplayUnits(self._unit_system, self._length_policy),
            include_3d=self._report_include_3d,
            include_band_3d=self._report_include_band_3d,
        )

    def _result_export_context(self) -> ExportContext | None:
        data = self._current_export_data()
        if data is None:
            return None
        project, design, result = data
        return ExportContext(
            parent=self,
            translator=self._translator,
            project=project,
            design=design,
            display_units=DisplayUnits(self._unit_system, self._length_policy),
            result=result,
            band_analysis=(
                self._band_analysis_results.get(self._design_id)
                if self._design_id is not None
                else None
            ),
            include_3d=self._report_include_3d,
            include_band_3d=self._report_include_band_3d,
        )

    def _run_export(self, action: Callable[..., Path | None], *args: object) -> None:
        try:
            if action(*args) is None:
                return
        except ExportFailure as exc:
            self._show_error(
                self._translator.t(exc.message_key, message=exc.detail),
            )
            return
        except Exception as exc:
            self._show_error(self._translator.t("error.export", message=str(exc)))
            return
        self._last_status_key = "status.exported"
        self._update_status_text()

    def export_csv(self) -> None:
        context = self._result_export_context()
        if context is not None:
            self._run_export(export_frequency_csv, context)

    def export_touchstone(self) -> None:
        context = self._result_export_context()
        if context is not None:
            self._run_export(export_touchstone, context)

    def export_sources_csv(self) -> None:
        context = self._result_export_context()
        if context is not None:
            self._run_export(export_sources_csv, context)

    def export_pattern_csv(self) -> None:
        context = self._result_export_context()
        if context is not None:
            self._run_export(export_pattern_csv, context)

    def export_pattern_png(self) -> None:
        context = self._result_export_context()
        if context is not None:
            self._run_export(export_pattern_png, context, self._results)

    def export_html_report(self) -> None:
        context = self._result_export_context()
        if context is not None:
            self._run_export(export_html_report, context)

    def export_pdf_report(self) -> None:
        context = self._result_export_context()
        if context is not None:
            self._run_export(export_pdf_report, context)

    def export_wire_schedule_csv(self) -> None:
        context = self._design_export_context()
        if context is not None:
            self._run_export(export_wire_schedule_csv, context)

    def export_bom_csv(self) -> None:
        context = self._design_export_context()
        if context is not None:
            self._run_export(export_bom_csv, context)

    def export_geometry_png(self) -> None:
        context = self._design_export_context()
        if context is not None:
            self._run_export(export_geometry_png, context, self._geometry)

    def export_geometry_svg(self) -> None:
        context = self._design_export_context()
        if context is not None:
            self._run_export(export_geometry_svg, context, self._geometry)

    def export_geometry_pdf(self) -> None:
        context = self._design_export_context()
        if context is not None:
            self._run_export(export_geometry_pdf, context, self._geometry)

    def export_geometry_dxf(self) -> None:
        context = self._design_export_context()
        if context is not None:
            self._run_export(export_geometry_dxf, context, self._geometry)

    def export_nec_deck(self) -> None:
        data = self._current_nec_deck()
        if data is None:
            return
        project, design, text = data
        context = ExportContext(
            parent=self,
            translator=self._translator,
            project=project,
            design=design,
            display_units=DisplayUnits(self._unit_system, self._length_policy),
        )
        self._run_export(save_nec_deck, context, text)

    def _current_nec_deck(self) -> tuple[Project, DesignVariant, str] | None:
        if self._project is None or self._design_id is None:
            self._show_error(self._translator.t("error.no_project"))
            return None
        try:
            project = self._apply_fields() if self._form_dirty else self._project
            design = project.design_by_id(self._design_id)
            spec = self._apply_sweep_override(design, self._base_simulation_spec(design))
            spec = self._with_project_chain(design.parameters, spec)
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return None
        solver_metadata = None
        if self._solver is not None:
            try:
                solver_metadata = self._solver.version()
            except Exception:
                solver_metadata = None
        if self._nec_deck_exporter is None:
            self._show_error(
                self._translator.t(
                    "error.export",
                    message="NEC deck export is not configured",
                )
            )
            return None
        return (
            project,
            design,
            self._nec_deck_exporter(project, design, spec, solver_metadata),
        )

    def copy_nec_deck(self) -> None:
        data = self._current_nec_deck()
        if data is None:
            return
        _project, _design, text = data
        QApplication.clipboard().setText(text)
        self._last_status_key = "status.copied"
        self._update_status_text()

    def _unique_variant_name(self, base: str) -> str:
        if self._project is None:
            raise ValueError(self._translator.t("error.no_project"))
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
        self._mark_project_dirty(design=False)
        self._last_status_key = "status.compacted"
        self._update_title()
        self._update_actions()
        self._update_status_text()

    def locate_solver(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self._translator.t("dialog.solver_title"),
            str(Path.home()),
            self._translator.t("dialog.all_files"),
        )
        if not filename:
            return
        if self._solver_factory is None:
            self._show_error(
                self._translator.t(
                    "error.solver_start",
                    message="solver factory is not configured",
                )
            )
            return
        try:
            solver = self._solver_factory(Path(filename))
            solver.version()
        except Exception as exc:
            self._show_error(self._translator.t("error.solver_start", message=str(exc)))
            return
        self._solver = solver
        self._update_solver_status()
        self._update_actions()

    def _current_preferences(self) -> UiPreferences:
        return UiPreferences(
            font_size=self._font_size_controller.size,
            language=self._language_preference,
            unit_system=self._unit_system,
            length_policy=self._length_policy,
            workflow_mode=self._workflow_mode,
            theme=self._theme_controller.preference,
            report_include_3d=self._report_include_3d,
            report_include_band_3d=self._report_include_band_3d,
            restore_last_project=self._restore_last_project_preference,
            autosave_enabled=self._autosave_enabled,
        )

    def _save_preferences(self) -> None:
        self._preferences.save(self._current_preferences())

    def _preferred_form_panel_width(self) -> int:
        widest = max(
            form.minimumSizeHint().width() for form, _scroll, _base_max_width in self._form_panels
        )
        # Font metrics differ across platforms. Let the panel grow to the
        # widest form instead of clipping large-font layouts; each form still
        # lives in a QScrollArea for narrow windows.
        return max(380, widest + 24)

    def _update_form_panel_widths(self) -> None:
        for form, scroll, base_max_width in self._form_panels:
            needed = form.minimumSizeHint().width() + 24
            scroll.setMinimumWidth(340)
            scroll.setMaximumWidth(max(base_max_width, needed))
        design_panel = getattr(self, "_design_panel", None)
        if design_panel is not None:
            required = self._preferred_form_panel_width()
            design_panel.setMinimumWidth(required)
            splitter = getattr(self, "_main_splitter", None)
            if splitter is not None:
                sizes = splitter.sizes()
                total = sum(sizes)
                if len(sizes) == 2 and total > required and sizes[0] < required:
                    splitter.setSizes([required, total - required])

    def show_preferences(self) -> None:
        dialog = PreferencesDialog(
            self._translator,
            self._current_preferences(),
            self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_preferences(dialog.preferences())

    def _apply_preferences(self, preferences: UiPreferences) -> None:
        self._theme_controller.apply(preferences.theme)
        self._language_preference = preferences.language
        self._translator.set_language(resolve_language(preferences.language))
        self._font_size_controller.apply(preferences.font_size)
        self._unit_system = preferences.unit_system
        self._length_policy = preferences.length_policy
        self._workflow_mode = preferences.workflow_mode
        self._report_include_3d = preferences.report_include_3d
        self._report_include_band_3d = preferences.report_include_band_3d
        self._restore_last_project_preference = preferences.restore_last_project
        self._autosave_enabled = preferences.autosave_enabled
        if self._autosave_enabled:
            if self._design_dirty:
                self._autosave_pending = True
            self._recovery_controller.set_enabled(True, pending=self._design_dirty)
        else:
            self._recovery_controller.stop()
            self._autosave_pending = False
            self._recovery_controller.clear()
        self._sync_workflow_controls()
        self._apply_workflow_mode()
        self._apply_unit_system_to_forms(preferences.unit_system)
        self.retranslate()
        self._update_form_panel_widths()
        self._save_preferences()

    def _set_language(self, language: Language) -> None:
        self._language_preference = LanguagePreference(language.value)
        self._translator.set_language(language)
        self.retranslate()
        self._update_form_panel_widths()
        self._save_preferences()

    def _set_font_size(self, size: FontSize) -> None:
        self._font_size_controller.apply(size)
        self._update_form_panel_widths()
        self._save_preferences()

    def _apply_unit_system_to_forms(self, unit_system: UnitSystem) -> None:
        for form in (
            self._form,
            self._ocfd_form,
            self._vertical_form,
            self._inverted_v_form,
            self._inverted_l_form,
            self._magnetic_loop_form,
            self._yagi_form,
            self._moxon_form,
            self._fan_dipole_form,
            self._trap_dipole_form,
            self._t2fd_form,
            self._endfed_form,
            self._j_pole_form,
            self._ringo_form,
            self._scv_form,
            self._biquad_form,
            self._beverage_form,
            self._loaded_dipole_form,
            self._phased_vertical_form,
            self._quad_beam_form,
            self._log_periodic_form,
            self._discone_form,
            self._trap_yagi_form,
            self._hexbeam_form,
            self._doublet_form,
            self._zepp_form,
        ):
            form.set_unit_system(unit_system)
        self._geometry.set_unit_system(unit_system)
        self._geometry.set_display_units(DisplayUnits(unit_system, self._length_policy))
        self._results.set_display_units(DisplayUnits(unit_system, self._length_policy))
        self._refresh_installation_summary()

    def _set_unit_system(self, unit_system: UnitSystem) -> None:
        self._unit_system = unit_system
        self._apply_unit_system_to_forms(unit_system)
        self._update_form_panel_widths()
        self._save_preferences()

    def _on_view_mode_changed(self) -> None:
        value = self._view_combo.currentData()
        if not isinstance(value, str):
            return
        mode = GeometryViewMode(value)
        self._geometry.set_view_mode(mode)
        self._update_height_control()

    def _on_hidden_dimensions_changed(self, values: object) -> None:
        if isinstance(values, (tuple, list)):
            self._hidden_dimension_texts = tuple(str(value) for value in values)
        else:
            self._hidden_dimension_texts = ()
        self._update_hidden_label()

    def _update_hidden_label(self) -> None:
        if not self._hidden_dimension_texts:
            self._geometry_hidden_label.clear()
            self._geometry_hidden_label.hide()
            return
        self._geometry_hidden_label.setText(
            self._translator.t(
                "geometry.hidden_values",
                values=", ".join(self._hidden_dimension_texts),
            )
        )
        self._geometry_hidden_label.show()

    def _auto_select_view(self, design: DesignVariant) -> None:
        del design
        self._geometry.set_view_mode(GeometryViewMode.CONSTRUCTION)
        index = self._view_combo.findData(GeometryViewMode.CONSTRUCTION.value)
        if index >= 0 and self._view_combo.currentIndex() != index:
            self._view_combo.blockSignals(True)
            self._view_combo.setCurrentIndex(index)
            self._view_combo.blockSignals(False)
        self._update_height_control()

    def _update_height_control(self) -> None:
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
            self._geometry.resolved_mode() is GeometryViewMode.ELEVATION
            and not vertical
            and not multi_wire
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

    def _mark_project_dirty(self, *, design: bool = True) -> None:
        self._dirty = True
        if design:
            self._design_dirty = True
            self._autosave_pending = True
            if self._autosave_enabled:
                self._recovery_controller.schedule()

    def _on_form_changed(self) -> None:
        if self._project is None or self._simulating:
            return
        self._form_dirty = True
        self._mark_project_dirty()
        self._update_title()
        self._update_actions()
        self._refresh_auto_sweep_display()

    def _project_name_changed(self, _text: str) -> None:
        if self._project_name_updating or self._project is None:
            return
        self._mark_project_dirty()
        self._update_title()
        self._update_actions()

    def show_live_tuning(self) -> None:
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
        try:
            primary_dimension_m(design.parameters)
        except TypeError:
            self._show_error(self._translator.t("live.unsupported"))
            return
        dialog = LiveTuningDialog(
            self._translator,
            design.parameters,
            self._base_simulation_spec(design),
            self._solver,
            lambda parameters: self._apply_live_tuning(design, parameters),
            display_units=DisplayUnits(self._unit_system, self._length_policy),
            parent=self,
        )
        dialog.exec()

    def _apply_live_tuning(
        self,
        design: DesignVariant,
        parameters: AntennaDesignParameters,
    ) -> None:
        if self._project is None or self._design_id is None:
            raise ValueError(self._translator.t("error.no_project"))
        updated = design.with_parameters(parameters)
        self._project = self._project.with_design(updated, updated_at=utc_now())
        self._invalidate_design_result(self._design_id)
        self._mark_project_dirty()
        self._select_design(self._design_id)
        self._last_status_key = "status.design_changed"
        self._update_title()
        self._update_actions()
        self.simulate()

    def show_tuner_matchability(self) -> None:
        if self._last_result is None:
            self._show_error(self._translator.t("error.no_result"))
            return
        dialog = TunerMatchDialog(self._translator, self._last_result, self)
        dialog.exec()

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

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if self._project is not None and any(
            Path(url.toLocalFile()).suffix.lower() in VNA_SUFFIXES
            for url in event.mimeData().urls()
            if url.isLocalFile()
        ):
            event.acceptProposedAction()
            return
        event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if self._project is not None and any(
            Path(url.toLocalFile()).suffix.lower() in VNA_SUFFIXES
            for url in event.mimeData().urls()
            if url.isLocalFile()
        ):
            event.acceptProposedAction()
            return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [
            Path(url.toLocalFile())
            for url in event.mimeData().urls()
            if url.isLocalFile() and Path(url.toLocalFile()).suffix.lower() in VNA_SUFFIXES
        ]
        if paths:
            event.acceptProposedAction()
            self.import_vna_paths(paths)
            return
        event.ignore()

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
            self._recovery_controller.stop()
            self._recovery_controller.clear()
            self._undo_stack.clear()
            event.accept()
        else:
            event.ignore()
