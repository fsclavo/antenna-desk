# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided Yagi generator with an editable element table."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.yagi import YagiParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.yagi_form import YagiForm


class YagiDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: YagiParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: YagiParameters | None = None
        self._form = YagiForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        self._table = self._form._table
        self._driven = self._form._driven
        self._ground = self._form._ground
        self._material = self._form._material
        self._add_element = self._form._add_element
        self._remove_element = self._form._remove_element
        self._load_preset = self._form._load_preset

        self.setWindowTitle(translator.t("yagi.title"))
        self.resize(920, 720)

        self._hint = QLabel(translator.t("yagi.hint"), self)
        self._hint.setWordWrap(True)
        self._evidence = QLabel(translator.t("yagi.evidence"), self)
        self._evidence.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._form, 1)
        layout.addWidget(self._hint)
        layout.addWidget(self._evidence)
        layout.addWidget(buttons)
        layout.addWidget(buttons)

    def parameters(self) -> YagiParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(self, self._translator.t("yagi.title"), str(exc))
            return
        self.accept()

    def result_parameters(self) -> YagiParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
