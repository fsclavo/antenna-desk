# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided vertical generator."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QWidget

from ...domain.antennas.vertical import VerticalParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.vertical_form import VerticalForm


class VerticalDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: VerticalParameters | None = None,
        mobile: bool = False,
    ) -> None:
        form = VerticalForm(
            translator,
            unit_system,
            parameters,
            None,
            mobile=mobile,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("vertical.mobile_hint" if mobile else "vertical.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(
            translator.t("vertical.mobile_evidence" if mobile else "vertical.evidence")
        )
        evidence.setWordWrap(True)
        example = QPushButton(translator.t("vertical.mobile_example")) if mobile else None
        if example is not None:
            example.setToolTip(translator.t("vertical.mobile_example_hint"))
            example.clicked.connect(form.load_mobile_example)
        notes = (example, hint, evidence) if example is not None else (hint, evidence)

        super().__init__(
            title=translator.t("vertical.mobile_title" if mobile else "vertical.title"),
            form=form,
            notes=notes,
            initial_size=(560, 700),
            parent=parent,
        )
        self._translator = translator
        self._vertical_form = form
        self._parameters: VerticalParameters | None = None
        self._frequency = form._frequency
        self._height = form._height
        self._base_height = form._base_height
        self._radial_count = form._radial_count
        self._radial_length = form._radial_length
        self._radial_angle = form._radial_angle
        self._radius = form._radius
        self._material = form._material
        self._ground = form._ground
        self._permittivity = form._permittivity
        self._conductivity = form._conductivity
        self._geometry = form._geometry
        self._hint = hint
        self._evidence = evidence
        if example is not None:
            self._example = example

    def parameters(self) -> VerticalParameters:
        return self._vertical_form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("vertical.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> VerticalParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
