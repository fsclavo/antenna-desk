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
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QSplitter,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
    QWizard,
)

from ..application.cancellation import EventCancelToken
from ..application.ports.antenna_solver import AntennaSolver
from ..application.ports.project_repository import ProjectRepository
from ..application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from ..application.use_cases.open_project import OpenProject
from ..application.use_cases.save_project import SaveProject
from ..application.use_cases.update_dipole_design import (
    UpdateDipoleDesign,
    UpdateDipoleDesignCommand,
)
from ..domain.antennas.dipole import DipoleParameters
from ..domain.environment.ground import GroundModel
from ..domain.projects.project import Project
from ..domain.simulation.result import SimulationResult, SimulationStatus
from ..simulation.nec2.solver import Nec2cSolver
from .i18n import Language, Translator
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
        self._project_name_updating = False
        self._simulating = False
        self._last_result: SimulationResult | None = None
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
        self._new_action.triggered.connect(lambda: self.new_dipole())

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
        self._form.changed.connect(self._on_form_changed)
        form_scroll = QScrollArea(self)
        form_scroll.setWidgetResizable(True)
        form_scroll.setWidget(self._form)
        form_scroll.setMinimumWidth(340)
        form_scroll.setMaximumWidth(480)

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
        self._height_label = QLabel(self)
        self._height_combo = QComboBox(self)
        for factor in (1.0, 1.5, 2.0, 3.0):
            self._height_combo.addItem(f"{factor:g}x", factor)
        geometry_controls.addStretch(1)
        geometry_controls.addWidget(self._view_label)
        geometry_controls.addWidget(self._view_combo)
        geometry_controls.addWidget(self._height_label)
        geometry_controls.addWidget(self._height_combo)
        geometry_layout.addLayout(geometry_controls)
        geometry_layout.addWidget(self._geometry, 1)
        geometry_container.setMinimumHeight(330)
        self._view_combo.currentIndexChanged.connect(self._on_view_mode_changed)
        self._height_combo.currentIndexChanged.connect(self._on_height_scale_changed)

        right_splitter = QSplitter(Qt.Orientation.Vertical, self)
        right_splitter.addWidget(geometry_container)
        right_splitter.addWidget(self._results)
        right_splitter.setStretchFactor(0, 1)
        right_splitter.setStretchFactor(1, 2)
        right_splitter.setSizes([400, 600])

        main_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_splitter.addWidget(form_scroll)
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
        toolbar.addAction(self._simulate_action)
        toolbar.addAction(self._cancel_action)

        self._file_menu = self.menuBar().addMenu("")
        self._file_menu.addAction(self._new_action)
        self._file_menu.addAction(self._open_action)
        self._file_menu.addAction(self._save_action)
        self._file_menu.addAction(self._save_as_action)
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
        self._open_action.setText(self._translator.t("action.open"))
        self._save_action.setText(self._translator.t("action.save"))
        self._save_as_action.setText(self._translator.t("action.save_as"))
        self._locate_solver_action.setText(self._translator.t("action.locate_solver"))
        self._exit_action.setText(self._translator.t("action.exit"))
        self._about_action.setText(self._translator.t("action.about"))
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
        self._view_label.setText(self._translator.t("geometry.view"))
        self._view_combo.setItemText(0, self._translator.t("geometry.view_elevation"))
        self._view_combo.setItemText(1, self._translator.t("geometry.view_plan"))
        self._height_label.setText(self._translator.t("geometry.vertical_scale"))
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
        if self._simulating:
            self._status_label.setText(self._translator.t("status.simulating"))
        elif self._last_result is not None:
            self._status_label.setText(self._result_status_text(self._last_result.status))
        else:
            self._status_label.setText(self._translator.t("status.ready"))

    def _result_status_text(self, status: SimulationStatus) -> str:
        key = {
            SimulationStatus.COMPLETED: "status.completed",
            SimulationStatus.CANCELLED: "status.cancelled",
            SimulationStatus.PARTIAL: "status.partial",
            SimulationStatus.ERROR: "status.error",
        }[status]
        return self._translator.t(key)

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
        self._new_action.setEnabled(idle)
        self._open_action.setEnabled(idle)
        self._save_action.setEnabled(idle and has_project)
        self._save_as_action.setEnabled(idle and has_project)
        self._locate_solver_action.setEnabled(idle)
        self._exit_action.setEnabled(idle)
        self._simulate_action.setEnabled(idle and has_project and self._solver is not None)
        self._cancel_action.setEnabled(self._simulating and self._cancel_token is not None)
        self._form.setEnabled(idle and has_project)
        self._project_name.setEnabled(idle and has_project)

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
        self._last_result = None
        self._results.set_result(None)
        design = project.design_by_id(design_id)
        self._form.set_parameters(design.parameters, reset_sweep=True)
        self._geometry.set_model(design.antenna)
        self._project_name_updating = True
        self._project_name.setText(project.name)
        self._project_name_updating = False
        self._update_title()
        self._update_actions()
        self._last_status_key = "status.ready"
        self._update_status_text()

    def _apply_fields(self) -> Project:
        if self._project is None or self._design_id is None:
            raise ValueError(self._translator.t("error.no_project"))
        project_name = self._project_name.text().strip()
        if not project_name:
            raise ValueError("project name must not be empty")
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
        self._geometry.set_model(design.antenna)
        self._project_name_updating = True
        self._project_name.setText(project_name)
        self._project_name_updating = False
        self._dirty = True
        self._last_result = None
        self._results.set_result(None)
        self._update_title()
        self._update_actions()
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
            spec = self._form.simulation_spec()
        except Exception as exc:
            self._show_error(self._translator.t("error.invalid_design", message=str(exc)))
            return

        self._last_result = None
        self._results.set_result(None)
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
        self._last_result = result
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
        self._update_status_text()
        self._cancel_action.setEnabled(False)

    def new_dipole(self) -> None:
        if not self._maybe_save_changes():
            return
        initial_frequency = 7_100_000.0
        if self._project is not None and self._design_id is not None:
            initial_frequency = self._project.design_by_id(self._design_id).parameters.frequency_hz
        wizard = DipoleWizard(
            self._translator,
            self._unit_system,
            initial_frequency_hz=initial_frequency,
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
        self._height_combo.setEnabled(mode is GeometryViewMode.ELEVATION)

    def _on_height_scale_changed(self) -> None:
        value = self._height_combo.currentData()
        if isinstance(value, (int, float)):
            self._geometry.set_height_exaggeration(float(value))

    def _on_form_changed(self) -> None:
        if self._project is None or self._simulating:
            return
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
