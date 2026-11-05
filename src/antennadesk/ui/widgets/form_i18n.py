# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Registry for retranslating form-row labels."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtWidgets import QComboBox, QLabel, QWidget

from ..i18n import Translator


def retranslate_combo(
    combo: QComboBox,
    translator: Translator,
    keys: Sequence[str],
) -> None:
    for index, key in enumerate(keys):
        combo.setItemText(index, translator.t(key))


class FormLabels:
    def __init__(self, translator: Translator, parent: QWidget) -> None:
        self._translator = translator
        self._parent = parent
        self._labels: dict[QLabel, str] = {}

    def label(self, key: str) -> QLabel:
        label = QLabel(self._translator.t(key), self._parent)
        self._labels[label] = key
        return label

    def retranslate(self) -> None:
        for label, key in self._labels.items():
            label.setText(self._translator.t(key))
