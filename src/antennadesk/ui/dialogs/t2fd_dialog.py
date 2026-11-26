# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided terminated folded dipole generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.t2fd import T2FDParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.t2fd_form import T2FDForm


class T2FDDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: T2FDParameters | None = None,
    ) -> None:
        form = T2FDForm(translator, unit_system, parameters, None)
        if parameters is None and frequency_hz is not None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("t2fd.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("t2fd.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("t2fd.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(620, 780),
            parent=parent,
        )
        self._translator = translator
        self._t2fd_form = form
        self._parameters: T2FDParameters | None = None
        self._lowest_frequency = form._lowest_frequency
        self._highest_frequency = form._highest_frequency
        self._length = form._length
        self._spacing = form._spacing
        self._start = form._start
        self._termination = form._termination
        self._transformer = form._transformer
        self._height = form._height
        self._orientation = form._orientation
        self._azimuth = form._azimuth
        self._radius = form._radius
        self._material = form._material
        self._ground = form._ground
        self._permittivity = form._permittivity
        self._conductivity = form._conductivity
        self._geometry = form._geometry
        self._band_warning = form._band_warning
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> T2FDParameters:
        return self._t2fd_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("t2fd.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> T2FDParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
