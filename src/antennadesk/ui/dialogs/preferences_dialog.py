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
from ..i18n import Language, Translator
from ..preferences import FontSize, UiPreferences
from ..units import UnitSystem


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
        self.resize(*scaled_dialog_size(460, 300))
        self.setSizeGripEnabled(True)

        self._language = QComboBox(self)
        self._language.addItem(translator.t("action.english"), Language.ENGLISH.value)
        self._language.addItem(translator.t("action.spanish"), Language.SPANISH.value)
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

        form = QFormLayout()
        form.addRow(QLabel(translator.t("menu.language"), self), self._language)
        form.addRow(QLabel(translator.t("menu.units"), self), self._units)
        form.addRow(QLabel(translator.t("menu.font_size"), self), self._font_size)

        hint = QLabel(translator.t("preferences.hint"), self)
        hint.setWordWrap(True)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
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

    def preferences(self) -> UiPreferences:
        language = self._language.currentData()
        unit_system = self._units.currentData()
        font_size = self._font_size.currentData()
        return UiPreferences(
            font_size=(
                FontSize(font_size) if isinstance(font_size, str) else self._initial.font_size
            ),
            language=(Language(language) if isinstance(language, str) else self._initial.language),
            unit_system=(
                UnitSystem(unit_system)
                if isinstance(unit_system, str)
                else self._initial.unit_system
            ),
        )
