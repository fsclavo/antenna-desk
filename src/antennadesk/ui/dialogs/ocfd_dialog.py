# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided off-center-fed dipole generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.ocfd import OCFDParameters
from ...domain.design.band_plan import BandPlan, default_band_plan
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.ocfd_form import OCFDForm
from .band_analysis_dialog import BandAnalysisDialog


class OCFDDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: OCFDParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: OCFDParameters | None = None
        self._band_plan: BandPlan | None = None
        self._band_plan_edited = False
        self._form = OCFDForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        self._ground = self._form._ground
        self._material = self._form._material

        self.setWindowTitle(translator.t("ocfd.title"))
        self.resize(560, 560)

        self._hint = QLabel(translator.t("ocfd.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("ocfd.evidence"), self)
        self._evidence.setWordWrap(True)
        self._band_plan_label = QLabel(self)
        self._band_plan_label.setWordWrap(True)
        self._band_plan_button = QPushButton(translator.t("band.choose"), self)
        self._band_plan_button.clicked.connect(self._choose_band_plan)
        band_layout = QHBoxLayout()
        band_layout.addWidget(self._band_plan_label, 1)
        band_layout.addWidget(self._band_plan_button)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._form)
        layout.addLayout(band_layout)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addStretch(1)
        layout.addWidget(buttons)
        self._form.changed.connect(self._update_band_plan_label)
        self._update_band_plan_label()

    def parameters(self) -> OCFDParameters:
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
