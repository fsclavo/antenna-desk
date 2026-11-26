# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided Yagi generator with an editable element table."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QMessageBox, QWidget

from ...domain.antennas.yagi import YagiParameters
from ..i18n import Translator
from ..units import UnitSystem
from ..widgets.form_dialog import FormDialogFrame
from ..widgets.yagi_form import YagiForm


class YagiDialog(FormDialogFrame):
    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        parent: QWidget | None = None,
        *,
        frequency_hz: float | None = None,
        parameters: YagiParameters | None = None,
    ) -> None:
        form = YagiForm(
            translator,
            unit_system,
            parameters,
            None,
            wide_layout=True,
        )
        if frequency_hz is not None and parameters is None:
            form.set_frequency_hz(frequency_hz)
        hint = QLabel(translator.t("yagi.hint"))
        hint.setWordWrap(True)
        evidence = QLabel(translator.t("yagi.evidence"))
        evidence.setWordWrap(True)
        boom_note = QLabel(translator.t("yagi.boom_note"))
        boom_note.setWordWrap(True)

        super().__init__(
            title=translator.t("yagi.title"),
            form=form,
            notes=(hint, evidence, boom_note),
            initial_size=(920, 860),
            parent=parent,
        )
        self._translator = translator
        self._yagi_form = form
        self._parameters: YagiParameters | None = None
        self._hint = hint
        self._evidence = evidence
        self._boom_note = boom_note
        self._table = form._table
        self._driven = form._driven
        self._driven_folded = form._driven_folded
        self._driven_fold_spacing = form._driven_fold_spacing
        self._match_type = form._match_type
        self._match_length = form._match_length
        self._match_spacing = form._match_spacing
        self._ground = form._ground
        self._material = form._material
        self._add_element = form._add_element
        self._remove_element = form._remove_element
        self._load_preset = form._load_preset

    def parameters(self) -> YagiParameters:
        return self._yagi_form.parameters()

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
