# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided end-fed wire generator."""

from __future__ import annotations

from PySide6.QtCore import QEventLoop, Qt, QThread
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...application.ports.antenna_solver import AntennaSolver
from ...application.use_cases.check_endfed_convergence import (
    CheckEndFedConvergence,
    CheckEndFedConvergenceCommand,
    EndFedConvergenceResult,
)
from ...domain.antennas.endfed import (
    EndFedParameters,
    EndFedPreset,
)
from ...domain.antennas.matching_network import MatchingNetwork
from ...domain.design.band_plan import BandPlan, default_band_plan
from ...domain.design.matching_resolution import resolve_matching_network
from ...domain.simulation.far_field import FarFieldRequest
from ...domain.simulation.frequency import FrequencyPlan
from ...domain.simulation.segmentation import SegmentationPolicy
from ...domain.simulation.spec import SimulationSpec
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.endfed_form import EndFedForm
from ..workers.endfed_convergence_worker import EndFedConvergenceWorker
from .band_analysis_dialog import BandAnalysisDialog


class EndFedDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: EndFedParameters | None = None,
        preset: EndFedPreset = EndFedPreset.STANDARD,
        solver: AntennaSolver | None = None,
        project_matching_network: MatchingNetwork | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: EndFedParameters | None = None
        self._solver = solver
        self._project_matching_network = project_matching_network
        self._band_plan: BandPlan | None = None
        self._band_plan_edited = False
        if parameters is not None:
            preset = parameters.preset
        self._form = EndFedForm(
            translator,
            unit_system,
            parameters,
            self,
            preset=preset,
        )
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        title_key = {
            EndFedPreset.STANDARD: "endfed.title",
            EndFedPreset.SLOPER: "endfed.sloper_title",
            EndFedPreset.RANDOM_WIRE: "endfed.random_wire_title",
            EndFedPreset.SHORTENED_80_10: "endfed.shortened_80_10_title",
            EndFedPreset.SHORTENED_40_10: "endfed.shortened_40_10_title",
        }[preset]
        self.setWindowTitle(translator.t(title_key))
        self.resize(*scaled_dialog_size(620, 780))

        hint_key = {
            EndFedPreset.STANDARD: "endfed.hint",
            EndFedPreset.SLOPER: "endfed.sloper_hint",
            EndFedPreset.RANDOM_WIRE: "endfed.random_wire_hint",
            EndFedPreset.SHORTENED_80_10: "endfed.shortened_80_10_hint",
            EndFedPreset.SHORTENED_40_10: "endfed.shortened_40_10_hint",
        }[preset]
        evidence_key = {
            EndFedPreset.STANDARD: "endfed.evidence",
            EndFedPreset.SLOPER: "endfed.sloper_evidence",
            EndFedPreset.RANDOM_WIRE: "endfed.random_wire_evidence",
            EndFedPreset.SHORTENED_80_10: "endfed.shortened_80_10_evidence",
            EndFedPreset.SHORTENED_40_10: "endfed.shortened_40_10_evidence",
        }[preset]
        self._hint = QLabel(translator.t(hint_key), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t(evidence_key), self)
        self._evidence.setWordWrap(True)
        self._band_plan_label = QLabel(self)
        self._band_plan_label.setWordWrap(True)
        self._band_plan_button = QPushButton(translator.t("band.choose"), self)
        self._band_plan_button.clicked.connect(self._choose_band_plan)
        band_layout = QHBoxLayout()
        band_layout.addWidget(self._band_plan_label, 1)
        band_layout.addWidget(self._band_plan_button)
        self._check_button = QPushButton(translator.t("endfed.convergence_check"), self)
        self._check_button.setEnabled(solver is not None)
        self._check_button.clicked.connect(self._check_convergence)
        self._check_result = QLabel(self)
        self._check_result.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        form_scroll = QScrollArea(self)
        form_scroll.setWidgetResizable(True)
        form_scroll.setWidget(self._form)
        layout.addWidget(form_scroll, 1)
        layout.addLayout(band_layout)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addWidget(self._check_button)
        layout.addWidget(self._check_result)
        layout.addWidget(buttons)
        self._form.changed.connect(self._update_band_plan_label)
        self._update_band_plan_label()

    def _check_convergence(self) -> None:
        if self._solver is None:
            return
        try:
            parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self.windowTitle(), str(exc))
            return
        resolution = resolve_matching_network(
            parameters,
            self._project_matching_network,
        )
        base_spec = SimulationSpec(
            frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
            segmentation=SegmentationPolicy(min_segments_per_wire=1),
            far_field=FarFieldRequest(enabled=False),
            feed_transformer_ratio=parameters.transformer_ratio,
            matching_network=resolution.effective,
            matching_network_override=resolution.override_active,
        )
        command = CheckEndFedConvergenceCommand(
            parameters=parameters,
            base_spec=base_spec,
        )
        progress = QProgressDialog(
            self._translator.t("endfed.convergence_running"),
            "",
            0,
            0,
            self,
        )
        progress.setWindowTitle(self.windowTitle())
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(250)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.setValue(0)
        thread = QThread(self)
        worker = EndFedConvergenceWorker(CheckEndFedConvergence(self._solver), command)
        worker.moveToThread(thread)
        result: dict[str, object] = {}
        loop = QEventLoop()

        def finished(value: object) -> None:
            result["result"] = value
            loop.quit()

        def failed(message: str) -> None:
            result["error"] = message
            loop.quit()

        worker.finished.connect(finished)
        worker.failed.connect(failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.started.connect(worker.run)
        thread.finished.connect(loop.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        try:
            loop.exec()
        finally:
            thread.quit()
            thread.wait()
            progress.close()

        error = result.get("error")
        if isinstance(error, str):
            QMessageBox.critical(self, self.windowTitle(), error)
            return
        convergence = result.get("result")
        if not isinstance(convergence, EndFedConvergenceResult):
            QMessageBox.critical(
                self,
                self.windowTitle(),
                self._translator.t("error.solver"),
            )
            return
        if convergence.error is not None:
            QMessageBox.critical(self, self.windowTitle(), convergence.error)
            return
        points = " · ".join(
            f"{point.segments} seg: R {point.impedance_ohm.real:.1f}, "
            f"X {point.impedance_ohm.imag:+.1f}, SWR {point.swr:.2f}"
            for point in convergence.points
        )
        if convergence.swr_informational:
            status_key = (
                "endfed.convergence_impedance_converged"
                if convergence.converged
                else "endfed.convergence_impedance_unresolved"
            )
            text = self._translator.t(
                "endfed.convergence_result_impedance",
                status=self._translator.t(status_key),
                points=points,
                resistance_spread=convergence.resistance_spread_ohm or 0.0,
                reactance_spread=convergence.reactance_spread_ohm or 0.0,
            )
        else:
            status_key = (
                "endfed.convergence_converged"
                if convergence.converged
                else "endfed.convergence_unresolved"
            )
            text = self._translator.t(
                "endfed.convergence_result",
                status=self._translator.t(status_key),
                points=points,
                swr_spread=convergence.swr_spread or 0.0,
                resistance_spread=convergence.resistance_spread_fraction or 0.0,
                reactance_spread=convergence.reactance_spread_ohm or 0.0,
            )
        self._check_result.setText(text)
        if convergence.swr_informational:
            self._check_result.setText(
                self._check_result.text()
                + "\n"
                + self._translator.t("endfed.convergence_matching_note")
            )

    def parameters(self) -> EndFedParameters:
        return self._form.parameters()

    def _default_band_plan(self) -> BandPlan:
        return default_band_plan(self.parameters()).plan

    def _update_band_plan_label(self) -> None:
        try:
            plan = self._band_plan if self._band_plan_edited else self._default_band_plan()
        except (ValueError, TypeError):
            self._band_plan_label.clear()
            self._band_plan_button.setEnabled(False)
            return
        if plan is None:
            self._band_plan_label.clear()
            self._band_plan_button.setEnabled(False)
            return
        self._band_plan_button.setEnabled(True)
        self._band_plan_label.setText(
            self._translator.t(
                "band.selected",
                bands=", ".join(selection.band.name for selection in plan.selections)
                or self._translator.t("band.no_selection"),
            )
        )

    def _choose_band_plan(self) -> None:
        try:
            parameters = self.parameters()
            default = default_band_plan(parameters)
        except (ValueError, TypeError) as exc:
            QMessageBox.warning(self, self._translator.t("endfed.title"), str(exc))
            return
        dialog = BandAnalysisDialog(
            self._translator,
            default,
            current_frequency_hz=parameters.frequency_hz,
            selected_plan=self._band_plan if self._band_plan_edited else default.plan,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        plan = dialog.plan()
        if not plan:
            QMessageBox.warning(
                self,
                self._translator.t("band.group_title"),
                self._translator.t("band.empty"),
            )
            return
        self._band_plan = plan
        self._band_plan_edited = True
        self._update_band_plan_label()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
            if not self._band_plan_edited:
                self._band_plan = default_band_plan(self._parameters).plan
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("endfed.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> EndFedParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters

    def result_band_plan(self) -> BandPlan:
        if self._band_plan is None:
            raise ValueError("the dialog has not produced a band plan")
        return self._band_plan
