# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided inverted-L generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.inverted_l import InvertedLParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.inverted_l_form import InvertedLForm


class InvertedLDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: InvertedLParameters | None = None,
    ) -> None:
        form = InvertedLForm(translator, unit_system, parameters, None)
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("inverted_l.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("inverted_l.evidence"))
        evidence.setWordWrap(True)

        super().__init__(
            title=translator.t("inverted_l.title"),
            form=form,
            notes=(hint, evidence),
            initial_size=(560, 600),
            scroll_form=False,
            parent=parent,
        )
        self._translator = translator
        self._inverted_l_form = form
        self._parameters: InvertedLParameters | None = None
        self._frequency = form._frequency
        self._vertical_height = form._vertical_height
        self._horizontal_length = form._horizontal_length
        self._base_height = form._base_height
        self._azimuth = form._azimuth
        self._radius = form._radius
        self._material = form._material
        self._ground = form._ground
        self._permittivity = form._permittivity
        self._conductivity = form._conductivity
        self._geometry = form._geometry
        self._hint = hint
        self._evidence = evidence

    def parameters(self) -> InvertedLParameters:
        return self._inverted_l_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("inverted_l.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> InvertedLParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
