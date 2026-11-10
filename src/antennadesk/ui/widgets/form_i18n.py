# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Registry for retranslating form-row labels."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtWidgets import QComboBox, QLabel, QWidget

from ..help import apply_help
from ..i18n import Translator


def retranslate_combo(
    combo: QComboBox,
    translator: Translator,
    keys: Sequence[str],
) -> None:
    for index, key in enumerate(keys):
        combo.setItemText(index, translator.t(key))


class FormLabels:
    def __init__(
        self,
        translator: Translator,
        parent: QWidget,
        *,
        family: str | None = None,
    ) -> None:
        self._translator = translator
        self._parent = parent
        self._family = family
        self._labels: dict[QLabel, str] = {}
        self._controls: dict[QLabel, QWidget] = {}

    def label(self, key: str, control: QWidget | None = None) -> QLabel:
        label = QLabel(self._translator.t(key), self._parent)
        label.setObjectName(key)
        self._labels[label] = key
        if control is not None:
            self._controls[label] = control
        self._apply_help(label, key, control)
        return label

    def retranslate(self) -> None:
        for label, key in self._labels.items():
            label.setText(self._translator.t(key))
            self._apply_help(label, key, self._controls.get(label))

    def _apply_help(
        self,
        label: QLabel,
        key: str,
        control: QWidget | None,
    ) -> None:
        apply_help(
            label,
            self._translator,
            key,
            family=self._family,
        )
        if control is not None:
            apply_help(
                control,
                self._translator,
                key,
                family=self._family,
            )
