# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided off-center-fed dipole generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QWidget,
)

from ...domain.antennas.ocfd import OCFDParameters
from ...domain.design.band_plan import BandPlan, default_band_plan
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.ocfd_form import OCFDForm
from .band_analysis_dialog import BandAnalysisDialog


class OCFDDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: OCFDParameters | None = None,
    ) -> None:
        form = OCFDForm(
            translator,
            unit_system,
            parameters,
            None,
            wide_layout=True,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("ocfd.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("ocfd.evidence"))
        evidence.setWordWrap(True)
        band_plan_label = QLabel()
        band_plan_label.setWordWrap(True)
        band_plan_button = QPushButton(translator.t("band.choose"))
        band_plan_button.clicked.connect(self._choose_band_plan)
        band_container = QWidget()
        band_layout = QHBoxLayout(band_container)
        band_layout.setContentsMargins(0, 0, 0, 0)
        band_layout.addWidget(band_plan_label, 1)
        band_layout.addWidget(band_plan_button)

        super().__init__(
            title=translator.t("ocfd.title"),
            form=form,
            notes=(band_container, hint, evidence),
            initial_size=(920, 640),
            parent=parent,
        )
        self._translator = translator
        self._ocfd_form = form
        self._parameters: OCFDParameters | None = None
        self._band_plan: BandPlan | None = None
        self._band_plan_edited = False
        self._ground = form._ground
        self._material = form._material
        self._hint = hint
        self._evidence = evidence
        self._band_plan_label = band_plan_label
        self._band_plan_button = band_plan_button
        form.changed.connect(self._update_band_plan_label)
        self._update_band_plan_label()

    def parameters(self) -> OCFDParameters:
        return self._ocfd_form.parameters()

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
            QMessageBox.warning(self, self._translator.t("ocfd.title"), str(exc))
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
            QMessageBox.critical(self, self._translator.t("ocfd.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> OCFDParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters

    def result_band_plan(self) -> BandPlan:
        if self._band_plan is None:
            raise ValueError("the dialog has not produced a band plan")
        return self._band_plan
