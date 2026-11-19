# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Application preferences dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
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
from ..theme import ThemePreference
from ..units import LengthPolicy, UnitSystem
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
        self.resize(*scaled_dialog_size(460, 420))
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
        for system, policy, key in (
            (UnitSystem.METRIC, LengthPolicy.AUTO, "units.metric_auto"),
            (UnitSystem.METRIC, LengthPolicy.FIXED, "units.metric_fixed"),
            (UnitSystem.IMPERIAL, LengthPolicy.AUTO, "units.imperial_auto"),
            (UnitSystem.IMPERIAL, LengthPolicy.FIXED, "units.imperial_fixed"),
        ):
            self._units.addItem(
                translator.t(key),
                f"{system.value}_{policy.value}",
            )
        self._select(
            self._units,
            f"{preferences.unit_system.value}_{preferences.length_policy.value}",
        )

        self._font_size = QComboBox(self)
        self._font_size.addItem(translator.t("font_size.small"), FontSize.SMALL.value)
        self._font_size.addItem(translator.t("font_size.medium"), FontSize.MEDIUM.value)
        self._font_size.addItem(translator.t("font_size.large"), FontSize.LARGE.value)
        self._select(self._font_size, preferences.font_size.value)

        self._theme = QComboBox(self)
        self._theme.addItem(translator.t("theme.system"), ThemePreference.SYSTEM.value)
        self._theme.addItem(translator.t("theme.light"), ThemePreference.LIGHT.value)
        self._theme.addItem(translator.t("theme.dark"), ThemePreference.DARK.value)
        self._select(self._theme, preferences.theme.value)

        self._workflow_mode = QComboBox(self)
        for mode in WorkflowMode:
            self._workflow_mode.addItem(
                translator.t(f"workflow.mode.{mode.value}"),
                mode.value,
            )
        self._select(self._workflow_mode, preferences.workflow_mode.value)

        self._report_3d = QCheckBox(translator.t("preferences.report_3d"), self)
        self._report_3d.setChecked(preferences.report_include_3d)
        self._report_band_3d = QCheckBox(
            translator.t("preferences.report_band_3d"),
            self,
        )
        self._report_band_3d.setChecked(preferences.report_include_band_3d)
        self._report_3d.toggled.connect(self._update_report_3d_controls)

        form = QFormLayout()
        form.addRow(QLabel(translator.t("preferences.language"), self), self._language)
        form.addRow(QLabel(translator.t("preferences.units"), self), self._units)
        form.addRow(QLabel(translator.t("preferences.font_size"), self), self._font_size)
        form.addRow(QLabel(translator.t("preferences.theme"), self), self._theme)
        form.addRow(
            QLabel(translator.t("preferences.workflow_mode"), self),
            self._workflow_mode,
        )
        form.addRow(
            QLabel(translator.t("preferences.report_options"), self),
            self._report_3d,
        )
        form.addRow(
            QLabel(translator.t("preferences.report_band_sections"), self),
            self._report_band_3d,
        )
        for row, key in enumerate(
            (
                "preferences.language",
                "preferences.units",
                "preferences.font_size",
                "preferences.theme",
                "preferences.workflow_mode",
                "preferences.report_3d",
                "preferences.report_band_3d",
            )
        ):
            apply_row_help(form, row, translator, key)
        self._update_report_3d_controls()

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

    def _update_report_3d_controls(self, *_args: object) -> None:
        self._report_band_3d.setEnabled(self._report_3d.isChecked())

    @staticmethod
    def _select(combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _restore_defaults(self) -> None:
        self._select(self._language, LanguagePreference.SYSTEM.value)
        self._select(
            self._units,
            f"{UnitSystem.METRIC.value}_{LengthPolicy.AUTO.value}",
        )
        self._select(self._font_size, FontSize.MEDIUM.value)
        self._select(self._theme, ThemePreference.SYSTEM.value)
        self._select(self._workflow_mode, WorkflowMode.STANDARD.value)
        self._report_3d.setChecked(True)
        self._report_band_3d.setChecked(False)

    def preferences(self) -> UiPreferences:
        language = self._language.currentData()
        units = self._units.currentData()
        font_size = self._font_size.currentData()
        theme = self._theme.currentData()
        workflow_mode = self._workflow_mode.currentData()
        unit_system = self._initial.unit_system
        length_policy = self._initial.length_policy
        if isinstance(units, str):
            system_value, _, policy_value = units.partition("_")
            try:
                unit_system = UnitSystem(system_value)
                length_policy = LengthPolicy(policy_value)
            except ValueError:
                pass
        return UiPreferences(
            font_size=(
                FontSize(font_size) if isinstance(font_size, str) else self._initial.font_size
            ),
            language=(
                LanguagePreference(language)
                if isinstance(language, str)
                else self._initial.language
            ),
            unit_system=unit_system,
            length_policy=length_policy,
            workflow_mode=(
                WorkflowMode(workflow_mode)
                if isinstance(workflow_mode, str)
                else self._initial.workflow_mode
            ),
            theme=(ThemePreference(theme) if isinstance(theme, str) else self._initial.theme),
            report_include_3d=self._report_3d.isChecked(),
            report_include_band_3d=(
                self._report_3d.isChecked() and self._report_band_3d.isChecked()
            ),
        )
