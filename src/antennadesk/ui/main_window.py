# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Main application window."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from uuid import UUID

from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QWizard,
)

from ..application.cancellation import EventCancelToken
from ..application.ports.antenna_solver import AntennaSolver
from ..application.ports.project_repository import ProjectRepository
from ..application.use_cases.add_design_variant import (
    AddDesignVariant,
    AddDesignVariantCommand,
)
from ..application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from ..application.use_cases.delete_design_variant import (
    DeleteDesignVariant,
    DeleteDesignVariantCommand,
)
from ..application.use_cases.open_project import OpenProject
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
from ..domain.antennas.design import with_primary_dimension
from ..domain.antennas.dipole import DipoleOrientation, DipoleParameters
from ..domain.antennas.load import LumpedLoad
from ..domain.common.time import utc_now
from ..domain.environment.ground import GroundModel
from ..domain.projects.project import DesignVariant, Project
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
from ..persistence.constants import MAX_PROJECT_SIZE_BYTES, PROJECT_SIZE_WARNING_BYTES
from ..reporting.csv_export import write_csv, write_pattern_csv
from ..reporting.html_report import write_html_report
from ..simulation.nec2.solver import Nec2cSolver
from .dialogs.comparison_dialog import ComparisonDialog
from .dialogs.construction_dialog import ConstructionDialog
from .dialogs.custom_antenna_dialog import CustomAntennaDialog
from .dialogs.loads_dialog import LoadsDialog
from .dialogs.optimization_dialog import OptimizationDialog
from .i18n import Language, Translator
from .report_pdf import write_report_pdf
from .units import UnitSystem
from .widgets.dipole_form import DipoleForm
from .widgets.geometry_view import GeometryView, GeometryViewMode
from .widgets.results_view import ResultsView
from .wizard.dipole_wizard import DipoleWizard
from .workers.simulation_worker import SimulationWorker


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
        self._simulation_design_id: UUID | None = None
        self._loads: tuple[LumpedLoad, ...] = ()
        self._last_status_key = "status.ready"
        self._thread: QThread | None = None
        self._worker: SimulationWorker | None = None
        self._cancel_token: EventCancelToken | None = None

        self._build_actions()
        self._build_ui()
        self.retranslate()
        self._create_default_project()

    def _build_actions(self) -> None:
        self._new_action = QAction(self)
        self._new_action.setShortcut(QKeySequence.StandardKey.New)
        self._new_action.triggered.connect(lambda: self.new_antenna())
        self._new_custom_action = QAction(self)
        self._new_custom_action.triggered.connect(lambda: self.new_custom_antenna())
        self._import_nec_action = QAction(self)
        self._import_nec_action.triggered.connect(lambda: self.import_nec_deck())
        self._import_mmana_action = QAction(self)
        self._import_mmana_action.triggered.connect(lambda: self.import_mmana_file())

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

        self._exit_action = QAction(self)
        self._exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self._exit_action.triggered.connect(self.close)

        self._about_action = QAction(self)
        self._about_action.triggered.connect(lambda: self.show_about())

        self._new_variant_action = QAction(self)
        self._new_variant_action.triggered.connect(lambda: self.new_variant())
        self._rename_variant_action = QAction(self)
        self._rename_variant_action.triggered.connect(lambda: self.rename_variant())
        self._delete_variant_action = QAction(self)
        self._delete_variant_action.triggered.connect(lambda: self.delete_variant())
        self._compare_action = QAction(self)
        self._compare_action.triggered.connect(lambda: self.compare_variants())
        self._optimize_action = QAction(self)
        self._optimize_action.triggered.connect(lambda: self.optimize_length())
        self._construction_action = QAction(self)
        self._construction_action.triggered.connect(lambda: self.show_construction_sheet())
        self._loads_action = QAction(self)
        self._loads_action.triggered.connect(lambda: self.edit_loads())
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
        self._export_html_action = QAction(self)
        self._export_html_action.triggered.connect(lambda: self.export_html_report())
        self._export_pdf_action = QAction(self)
        self._export_pdf_action.triggered.connect(lambda: self.export_pdf_report())
        self._compact_history_action = QAction(self)
        self._compact_history_action.triggered.connect(lambda: self.compact_simulation_history())

        self._simulate_action = QAction(self)
        self._simulate_action.setShortcut(QKeySequence("F5"))
        self._simulate_action.triggered.connect(lambda: self.simulate())

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
        self._form.apply_requested.connect(lambda: self.apply_design())
        self._form.optimize_requested.connect(lambda: self.optimize_length())
        self._form.changed.connect(self._on_form_changed)
        self._form_scroll = QScrollArea(self)
        form_scroll = self._form_scroll
        form_scroll.setWidgetResizable(True)
        form_scroll.setWidget(self._form)
        form_scroll.setMinimumWidth(340)
        form_scroll.setMaximumWidth(480)
        self._custom_panel = QWidget(self)
        custom_layout = QVBoxLayout(self._custom_panel)
        self._custom_title = QLabel(self._custom_panel)
        self._custom_title.setStyleSheet("font-weight: bold;")
        self._custom_summary = QLabel(self._custom_panel)
        self._custom_summary.setWordWrap(True)
        self._custom_edit = QPushButton(self._custom_panel)
        self._custom_edit.clicked.connect(lambda: self.edit_custom_wires())
        custom_layout.addWidget(self._custom_title)
        custom_layout.addWidget(self._custom_summary)
        custom_layout.addWidget(self._custom_edit)
        custom_layout.addStretch(1)
        self._design_stack = QStackedWidget(self)
        self._design_stack.addWidget(form_scroll)
        self._design_stack.addWidget(self._custom_panel)

        self._geometry = GeometryView(self._translator, self._unit_system)
        self._geometry.setMinimumHeight(300)
        self._results = ResultsView(self._translator)

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

        right_splitter = QSplitter(Qt.Orientation.Vertical, self)
        right_splitter.addWidget(geometry_container)
        right_splitter.addWidget(self._results)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 2)
        right_splitter.setSizes([400, 600])

        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_splitter.addWidget(self._design_stack)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([380, 900])
        self.setCentralWidget(main_splitter)

        toolbar = QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        toolbar.addAction(self._new_action)
        toolbar.addAction(self._open_action)
        toolbar.addAction(self._save_action)
        toolbar.addSeparator()
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
        toolbar.addAction(self._simulate_action)
        toolbar.addAction(self._cancel_action)

        self._file_menu = self.menuBar().addMenu("")
        self._file_menu.addAction(self._new_action)
        self._file_menu.addAction(self._new_custom_action)
        self._file_menu.addAction(self._import_nec_action)
        self._file_menu.addAction(self._import_mmana_action)
        self._file_menu.addAction(self._open_action)
        self._file_menu.addAction(self._save_action)
        self._file_menu.addAction(self._save_as_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._new_variant_action)
        self._file_menu.addAction(self._rename_variant_action)
        self._file_menu.addAction(self._delete_variant_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._compare_action)
        self._file_menu.addAction(self._optimize_action)
        self._file_menu.addAction(self._construction_action)
        self._file_menu.addAction(self._loads_action)
        self._file_menu.addAction(self._edit_custom_action)
        self._file_menu.addAction(self._convert_custom_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._export_csv_action)
        self._file_menu.addAction(self._export_pattern_csv_action)
        self._file_menu.addAction(self._export_pattern_png_action)
        self._file_menu.addAction(self._export_geometry_png_action)
        self._file_menu.addAction(self._export_html_action)
        self._file_menu.addAction(self._export_pdf_action)
        self._file_menu.addAction(self._compact_history_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._locate_solver_action)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._exit_action)

        self._language_menu = self.menuBar().addMenu("")
        self._language_menu.addAction(self._english_action)
        self._language_menu.addAction(self._spanish_action)

        self._units_menu = self.menuBar().addMenu("")
        self._units_menu.addAction(self._metric_action)
        self._units_menu.addAction(self._imperial_action)

        self._help_menu = self.menuBar().addMenu("")
        self._help_menu.addAction(self._about_action)

        self._status_label = QLabel(self)
        self._solver_label = QLabel(self)
        self.statusBar().addWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._solver_label)

    def retranslate(self) -> None:
        self._update_title()
        self._new_action.setText(self._translator.t("action.new"))
        self._new_custom_action.setText(self._translator.t("action.new_custom"))
        self._import_nec_action.setText(self._translator.t("action.import_nec"))
        self._import_mmana_action.setText(self._translator.t("action.import_mmana"))
        self._open_action.setText(self._translator.t("action.open"))
        self._save_action.setText(self._translator.t("action.save"))
        self._save_as_action.setText(self._translator.t("action.save_as"))
        self._locate_solver_action.setText(self._translator.t("action.locate_solver"))
        self._exit_action.setText(self._translator.t("action.exit"))
        self._about_action.setText(self._translator.t("action.about"))
        self._new_variant_action.setText(self._translator.t("action.new_variant"))
        self._rename_variant_action.setText(self._translator.t("action.rename_variant"))
        self._delete_variant_action.setText(self._translator.t("action.delete_variant"))
        self._compare_action.setText(self._translator.t("action.compare"))
        self._optimize_action.setText(self._translator.t("action.optimize"))
        self._construction_action.setText(self._translator.t("action.construction"))
        self._loads_action.setText(self._translator.t("action.loads"))
        self._edit_custom_action.setText(self._translator.t("action.edit_custom"))
        self._convert_custom_action.setText(self._translator.t("action.convert_custom"))
        self._custom_title.setText(self._translator.t("custom.panel_title"))
        self._custom_edit.setText(self._translator.t("action.edit_custom"))
        self._export_csv_action.setText(self._translator.t("action.export_csv"))
        self._export_pattern_csv_action.setText(self._translator.t("action.export_pattern_csv"))
        self._export_pattern_png_action.setText(self._translator.t("action.export_pattern_png"))
        self._export_geometry_png_action.setText(self._translator.t("action.export_geometry_png"))
        self._export_html_action.setText(self._translator.t("action.export_html"))
        self._export_pdf_action.setText(self._translator.t("action.export_pdf"))
        self._compact_history_action.setText(self._translator.t("action.compact_history"))
        self._simulate_action.setText(self._translator.t("action.simulate"))
        self._cancel_action.setText(self._translator.t("action.cancel"))
        self._english_action.setText(self._translator.t("action.english"))
        self._spanish_action.setText(self._translator.t("action.spanish"))
        self._metric_action.setText(self._translator.t("units.metric"))
        self._imperial_action.setText(self._translator.t("units.imperial"))
        self._file_menu.setTitle(self._translator.t("menu.file"))
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
        self._form.retranslate()
        self._geometry.retranslate()
        self._results.retranslate()
        self._update_solver_status()
        self._update_status_text()
        self._update_actions()

    def _update_title(self) -> None:
        name = (
            self._project.name if self._project is not None else self._translator.t("app.untitled")
        )
        marker = " *" if self._dirty else ""
        self.setWindowTitle(f"{name}{marker} — AntennaDesk")

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
        self._open_action.setEnabled(idle)
        self._save_action.setEnabled(idle and has_project)
        self._save_as_action.setEnabled(idle and has_project)
        self._locate_solver_action.setEnabled(idle)
        self._exit_action.setEnabled(idle)
        self._new_variant_action.setEnabled(idle and has_designs)
        self._rename_variant_action.setEnabled(idle and has_designs)
        self._delete_variant_action.setEnabled(idle and has_multiple)
        self._compare_action.setEnabled(idle and has_multiple)
        parameters = None
        if self._project is not None and self._design_id is not None:
            parameters = self._project.design_by_id(self._design_id).parameters
        is_custom = isinstance(parameters, CustomAntennaParameters)
        self._optimize_action.setEnabled(
            idle and has_project and not is_custom and self._solver is not None
        )
        self._loads_action.setEnabled(idle and has_project)
        self._edit_custom_action.setEnabled(idle and has_project and is_custom)
        self._convert_custom_action.setEnabled(idle and has_project and not is_custom)
        self._new_custom_action.setEnabled(idle)
        self._import_nec_action.setEnabled(idle)
        self._import_mmana_action.setEnabled(idle)
        self._export_csv_action.setEnabled(idle and has_result)
        self._export_pattern_csv_action.setEnabled(idle and has_result)
        self._export_pattern_png_action.setEnabled(idle and has_result)
        self._export_geometry_png_action.setEnabled(idle and has_project)
        self._export_html_action.setEnabled(idle and has_result)
        self._export_pdf_action.setEnabled(idle and has_result)
        has_history = self._project is not None and len(self._project.simulation_runs) > len(
            self._project.designs
        )
        self._compact_history_action.setEnabled(idle and has_history)
        self._simulate_action.setEnabled(idle and has_project and self._solver is not None)
        self._cancel_action.setEnabled(self._simulating and self._cancel_token is not None)
        self._form.setEnabled(idle and has_project and not is_custom)
        self._design_stack.setEnabled(idle and has_project)
        self._custom_edit.setEnabled(idle and has_project and is_custom)
        self._project_name.setEnabled(idle and has_project)
        self._variant_combo.setEnabled(idle and has_designs)

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

    def _select_design(self, design_id: UUID) -> None:
        if self._project is None:
            return
        design = self._project.design_by_id(design_id)
        self._design_id = design_id
        self._form_dirty = False
        self._loads = design.antenna.loads
        if isinstance(design.parameters, CustomAntennaParameters):
            self._design_stack.setCurrentWidget(self._custom_panel)
            self._custom_summary.setText(
                self._translator.t(
                    "custom.summary",
                    count=len(design.antenna.wires),
                    length=f"{sum(wire.length_m for wire in design.antenna.wires):.3f} m",
                )
            )
        else:
            self._design_stack.setCurrentWidget(self._form_scroll)
            self._form.set_parameters(design.parameters, reset_sweep=True)
        self._results.set_design(design)
        self._geometry.set_model(design.antenna, antenna_type=design.antenna_type)
        self._auto_select_view(design)
        self._set_variant_combo(design_id)
        result = self._simulation_results.get(design_id)
        if result is None and self._project is not None:
            latest_run = self._project.latest_simulation_run(design_id)
            if latest_run is not None:
                result = latest_run.result
                self._simulation_results[design_id] = result
        self._last_result = result
        self._results.set_result(result)
        self._last_status_key = (
            self._result_status_key(result.status) if result is not None else "status.ready"
        )
        self._update_status_text()
        self._update_actions()
        self._update_height_control()

    def _on_variant_changed(self) -> None:
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

    def _create_default_project(self) -> None:
        parameters = DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
            wire_radius_m=0.001,
            ground=GroundModel.finite(
                relative_permittivity=13.0,
                conductivity_s_per_m=0.005,
            ),
        )
        project = CreateDipoleProject().execute(
            CreateDipoleProjectCommand(
                project_name="40 m dipole",
                variant_name="Initial",
                parameters=parameters,
                description="Half-wave dipole for the 40 m band.",
            )
        )
        self._set_project(
            project,
            project.designs[0].id,
            path=None,
            dirty=False,
        )

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
        self._current_path = path
        self._dirty = dirty
        self._form_dirty = False
        self._last_result = None
        self._simulation_results = {}
        for project_design in project.designs:
            latest_run = project.latest_simulation_run(project_design.id)
            if latest_run is not None:
                self._simulation_results[project_design.id] = latest_run.result
        self._simulation_design_id = None
        self._results.set_result(None)
        self._project_name_updating = True
        self._project_name.setText(project.name)
        self._project_name_updating = False
        self._populate_variants(design_id)
        self._select_design(design_id)
        self._update_title()
        self._update_actions()

    def _apply_fields(self) -> Project:
        if self._project is None or self._design_id is None:
            raise ValueError(self._translator.t("error.no_project"))
        project_name = self._project_name.text().strip()
        if not project_name:
            raise ValueError("project name must not be empty")
        previous_design = self._project.design_by_id(self._design_id)
        if isinstance(previous_design.parameters, CustomAntennaParameters):
            design = previous_design
            if design.antenna.loads != self._loads:
                design = design.with_loads(self._loads)
                self._project = self._project.with_design(design, updated_at=utc_now())
            self._project = replace(self._project, name=project_name)
            self._results.set_design(design)
            self._geometry.set_model(design.antenna, antenna_type=design.antenna_type)
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
            )
        )
        updated = replace(updated, name=project_name)
        self._project = updated
        design = updated.design_by_id(self._design_id)
        if design.antenna.loads != self._loads:
            design = design.with_loads(self._loads)
            updated = updated.with_design(design, updated_at=updated.updated_at)
            self._project = updated
        self._results.set_design(design)
        self._geometry.set_model(design.antenna, antenna_type=design.antenna_type)
        self._auto_select_view(design)
        self._project_name_updating = True
        self._project_name.setText(project_name)
        self._project_name_updating = False
        parameters_changed = parameters != previous_design.parameters
        loads_changed = self._loads != previous_design.antenna.loads
        if parameters_changed or loads_changed:
            self._simulation_results.pop(self._design_id, None)
            self._last_result = None
            self._results.set_result(None)
        self._form_dirty = False
        self._dirty = True
        self._update_title()
        self._update_actions()
        self._update_height_control()
        return updated

    def apply_design(self) -> None:
        try:
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._last_status_key = "status.design_changed"
        self._update_status_text()

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
            spec = (
                self._custom_simulation_spec(design.parameters)
                if isinstance(design.parameters, CustomAntennaParameters)
                else self._form.simulation_spec()
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return

        self._last_result = None
        self._results.set_result(None)
        self._simulation_design_id = self._design_id
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

    def _on_simulation_finished(self, result: SimulationResult) -> None:
        self._simulating = False
        self._cancel_token = None
        design_id = self._simulation_design_id
        if design_id is not None:
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

    def _custom_simulation_spec(
        self,
        parameters: CustomAntennaParameters,
    ) -> SimulationSpec:
        model = parameters.to_antenna(name="Custom")
        far_field = FarFieldRequest(
            enabled=True,
            theta_start_deg=0.0,
            theta_stop_deg=(180.0 if parameters.ground.kind.value == "free_space" else 90.0),
            theta_count=19 if parameters.ground.kind.value == "free_space" else 10,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=37,
        )
        return SimulationSpec(
            frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
            segmentation=aligned_policy_for_model(
                model,
                parameters.frequency_hz,
                SegmentationPolicy(min_segments_per_wire=3),
            ),
            far_field=far_field,
        )

    def new_custom_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        name, accepted = QInputDialog.getText(
            self,
            self._translator.t("custom.title"),
            self._translator.t("field.project_name"),
            text="Custom antenna",
        )
        if not accepted:
            return
        dialog = CustomAntennaDialog(self._translator, self._unit_system, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            project = CreateDipoleProject().execute(
                CreateDipoleProjectCommand(
                    project_name=name.strip() or "Custom antenna",
                    variant_name="Initial",
                    parameters=dialog.result_parameters(),
                )
            )
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._set_project(project, project.designs[0].id, path=None, dirty=True)

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
            )
            updated_design = design.with_parameters(parameters)
            self._project = self._project.with_design(updated_design, updated_at=utc_now())
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self._loads = updated_design.antenna.loads
        self._form_dirty = False
        self._dirty = True
        self._simulation_results.pop(self._design_id, None)
        self._results.set_result(None)
        self._results.set_design(updated_design)
        self._geometry.set_model(updated_design.antenna, antenna_type=updated_design.antenna_type)
        self._design_stack.setCurrentWidget(self._custom_panel)
        self._custom_summary.setText(
            self._translator.t(
                "custom.summary",
                count=len(updated_design.antenna.wires),
                length=f"{sum(wire.length_m for wire in updated_design.antenna.wires):.3f} m",
            )
        )
        self._last_status_key = "status.design_changed"
        self._update_title()
        self._update_actions()
        self._update_status_text()

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
        self._simulation_results.pop(self._design_id, None)
        self._results.set_result(None)
        self._results.set_design(updated_design)
        self._geometry.set_model(updated_design.antenna, antenna_type=updated_design.antenna_type)
        self._custom_summary.setText(
            self._translator.t(
                "custom.summary",
                count=len(updated_design.antenna.wires),
                length=f"{sum(wire.length_m for wire in updated_design.antenna.wires):.3f} m",
            )
        )
        self._update_title()
        self._update_actions()

    def new_antenna(self) -> None:
        if not self._maybe_save_changes():
            return
        initial_frequency = 7_100_000.0
        if self._project is not None and self._design_id is not None:
            initial_frequency = self._project.design_by_id(self._design_id).parameters.frequency_hz
        wizard = DipoleWizard(
            self._translator,
            self._unit_system,
            initial_frequency_hz=initial_frequency,
            initial_antenna_type=self._form.antenna_type(),
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
        try:
            project = self._apply_fields()
            size = self._repository.serialized_size(project)
            if size > MAX_PROJECT_SIZE_BYTES:
                self._show_error(
                    self._translator.t(
                        "dialog.project_too_large",
                        size=size / (1024 * 1024),
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
        self._simulation_results.pop(design.id, None)
        self._project = updated
        self._dirty = True
        new_id = updated.designs[0].id
        self._populate_variants(new_id)
        self._select_design(new_id)
        self._update_title()
        self._update_actions()

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
        base_spec = self._form.simulation_spec()
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
            self._form.set_parameters(parameters, reset_sweep=False)
            self._apply_fields()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return
        self.simulate()

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
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._loads = dialog.loads()
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
        try:
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
        try:
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

    def export_pattern_png(self) -> None:
        data = self._current_export_data()
        if data is None:
            return
        project, design, _result = data
        suggested = (
            f"{self._safe_file_name(project.name)}-{self._safe_file_name(design.name)}-pattern.png"
        )
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
        try:
            write_html_report(project, design, result, path)
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
        if len(self._project.simulation_runs) <= len(self._project.designs):
            return
        answer = QMessageBox.question(
            self,
            self._translator.t("app.title"),
            self._translator.t(
                "dialog.compact_history",
                count=len(self._project.simulation_runs),
                keep=len(self._project.designs),
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
        try:
            write_report_pdf(self._translator, project, design, result, path)
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
        if len(design.antenna.wires) > 1:
            index = self._view_combo.findData(GeometryViewMode.PLAN.value)
            if index >= 0 and self._view_combo.currentIndex() != index:
                self._view_combo.setCurrentIndex(index)

    def _update_height_control(self) -> None:
        mode = self._view_combo.currentData()
        vertical = False
        multi_wire = False
        if self._project is not None and self._design_id is not None:
            design = self._project.design_by_id(self._design_id)
            multi_wire = len(design.antenna.wires) > 1
            parameters = design.parameters
            if isinstance(parameters, DipoleParameters):
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
            self._translator.t("app.about"),
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
            event.accept()
        else:
            event.ignore()
