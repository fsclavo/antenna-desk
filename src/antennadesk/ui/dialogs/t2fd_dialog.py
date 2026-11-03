# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided terminated folded dipole (T2FD) generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.t2fd import T2FDParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.t2fd_form import T2FDForm


class T2FDDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: T2FDParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: T2FDParameters | None = None
        self._form = T2FDForm(translator, unit_system, parameters, self)
        if parameters is None and frequency_hz is not None:
            self._form.set_frequency_hz(frequency_hz)
        self._lowest_frequency = self._form._lowest_frequency
        self._highest_frequency = self._form._highest_frequency
        self._length = self._form._length
        self._spacing = self._form._spacing
        self._start = self._form._start
        self._termination = self._form._termination
        self._transformer = self._form._transformer
        self._height = self._form._height
        self._orientation = self._form._orientation
        self._azimuth = self._form._azimuth
        self._radius = self._form._radius
        self._material = self._form._material
        self._ground = self._form._ground
        self._permittivity = self._form._permittivity
        self._conductivity = self._form._conductivity
        self._geometry = self._form._geometry
        self._band_warning = self._form._band_warning

        self.setWindowTitle(translator.t("t2fd.title"))
        self.resize(620, 780)

        self._hint = QLabel(translator.t("t2fd.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("t2fd.evidence"), self)
        self._evidence.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._form)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll, 1)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addWidget(buttons)

    def parameters(self) -> T2FDParameters:
        return self._form.parameters()

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
