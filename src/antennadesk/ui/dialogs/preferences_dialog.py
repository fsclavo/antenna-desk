# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Application preferences dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..fonts import scaled_dialog_size
from ..help import apply_row_help
from ..i18n import Translator
from ..preferences import FontSize, LanguagePreference, UiPreferences
from ..units import UnitSystem
from ..workflow import WorkflowMode


class PreferencesDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        preferences: UiPreferences,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._initial = preferences

        self.setWindowTitle(translator.t("preferences.title"))
        self.resize(*scaled_dialog_size(460, 340))
        self.setSizeGripEnabled(True)

        self._language = QComboBox(self)
        self._language.addItem(
            translator.t("preferences.language_system"),
            LanguagePreference.SYSTEM.value,
        )
        self._language.addItem(
            translator.t("action.english"),
            LanguagePreference.ENGLISH.value,
        )
        self._language.addItem(
            translator.t("action.spanish"),
            LanguagePreference.SPANISH.value,
        )
        self._select(self._language, preferences.language.value)

        self._units = QComboBox(self)
        self._units.addItem(translator.t("units.metric"), UnitSystem.METRIC.value)
        self._units.addItem(translator.t("units.imperial"), UnitSystem.IMPERIAL.value)
        self._select(self._units, preferences.unit_system.value)

        self._font_size = QComboBox(self)
        self._font_size.addItem(translator.t("font_size.small"), FontSize.SMALL.value)
        self._font_size.addItem(translator.t("font_size.medium"), FontSize.MEDIUM.value)
        self._font_size.addItem(translator.t("font_size.large"), FontSize.LARGE.value)
        self._select(self._font_size, preferences.font_size.value)

        self._workflow_mode = QComboBox(self)
        for mode in WorkflowMode:
            self._workflow_mode.addItem(
                translator.t(f"workflow.mode.{mode.value}"),
                mode.value,
            )
        self._select(self._workflow_mode, preferences.workflow_mode.value)

        form = QFormLayout()
        form.addRow(QLabel(translator.t("preferences.language"), self), self._language)
        form.addRow(QLabel(translator.t("preferences.units"), self), self._units)
        form.addRow(QLabel(translator.t("preferences.font_size"), self), self._font_size)
        form.addRow(
            QLabel(translator.t("preferences.workflow_mode"), self),
            self._workflow_mode,
        )
        for row, key in enumerate(
            (
                "preferences.language",
                "preferences.units",
                "preferences.font_size",
                "preferences.workflow_mode",
            )
        ):
            apply_row_help(form, row, translator, key)

        hint = QLabel(translator.t("preferences.hint"), self)
        hint.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        restore = buttons.addButton(
            translator.t("preferences.restore_defaults"),
            QDialogButtonBox.ButtonRole.ResetRole,
        )
        restore.clicked.connect(self._restore_defaults)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(translator.t("action.ok"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(
            translator.t("action.cancel")
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(hint)
        layout.addStretch(1)
        layout.addWidget(buttons)

    @staticmethod
    def _select(combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _restore_defaults(self) -> None:
        self._select(self._language, LanguagePreference.SYSTEM.value)
        self._select(self._units, UnitSystem.METRIC.value)
        self._select(self._font_size, FontSize.MEDIUM.value)
        self._select(self._workflow_mode, WorkflowMode.STANDARD.value)

    def preferences(self) -> UiPreferences:
        language = self._language.currentData()
        unit_system = self._units.currentData()
        font_size = self._font_size.currentData()
        workflow_mode = self._workflow_mode.currentData()
        return UiPreferences(
            font_size=(
                FontSize(font_size) if isinstance(font_size, str) else self._initial.font_size
            ),
            language=(
                LanguagePreference(language)
                if isinstance(language, str)
                else self._initial.language
            ),
            unit_system=(
                UnitSystem(unit_system)
                if isinstance(unit_system, str)
                else self._initial.unit_system
            ),
            workflow_mode=(
                WorkflowMode(workflow_mode)
                if isinstance(workflow_mode, str)
                else self._initial.workflow_mode
            ),
        )
