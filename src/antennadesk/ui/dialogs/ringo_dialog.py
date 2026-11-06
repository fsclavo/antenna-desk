# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided Ringo vertical generator."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.ringo import RingoParameters
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.ringo_form import RingoForm


class RingoDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: RingoParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: RingoParameters | None = None
        self._form = RingoForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        self.setWindowTitle(translator.t("ringo.title"))
        self.resize(*scaled_dialog_size(560, 620))

        self._hint = QLabel(translator.t("ringo.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("ringo.evidence"), self)
        self._evidence.setWordWrap(True)

        self._example = QPushButton(
            translator.t("ringo.ar6_example"),
            self,
        )
        self._example.setToolTip(translator.t("ringo.ar6_example_hint"))
        self._example.clicked.connect(self._form.load_cushcraft_ar6_example)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._form)
        layout.addWidget(self._example)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addStretch(1)
        layout.addWidget(buttons)

    def parameters(self) -> RingoParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("ringo.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> RingoParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
