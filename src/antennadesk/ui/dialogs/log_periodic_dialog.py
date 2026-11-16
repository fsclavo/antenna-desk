# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided log-periodic dipole array generator."""

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

from ...domain.antennas.log_periodic import LogPeriodicParameters
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.log_periodic_form import LogPeriodicForm


class LogPeriodicDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: LogPeriodicParameters | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._parameters: LogPeriodicParameters | None = None
        self._form = LogPeriodicForm(translator, unit_system, parameters, self)
        if frequency_hz is not None and parameters is None:
            self._form.set_frequency_hz(frequency_hz)
        self.setWindowTitle(translator.t("log_periodic.title"))
        self.resize(*scaled_dialog_size(640, 900))

        self._hint = QLabel(translator.t("log_periodic.hint"), self)
        self._hint.setWordWrap(True)

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
        layout.addWidget(buttons)

    def parameters(self) -> LogPeriodicParameters:
        return self._form.parameters()

    def _accept(self) -> None:
        try:
            self._parameters = self.parameters()
        except (ValueError, TypeError) as exc:
            QMessageBox.critical(
                self,
                self._translator.t("log_periodic.title"),
                str(exc),
            )
            return
        self.accept()

    def result_parameters(self) -> LogPeriodicParameters:
        if self._parameters is None:
            raise ValueError("the dialog has not produced parameters")
        return self._parameters
