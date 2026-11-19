# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Manual column mapping fallback for unrecognized VNA CSV exports."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ...importers.vna_csv import VnaColumnMapping
from ..fonts import scaled_dialog_size
from ..help import apply_row_help
from ..i18n import Translator


class VnaMappingDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        headers: Sequence[str],
        parent: QWidget | None = None,
        *,
        initial: VnaColumnMapping | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._headers = tuple(headers)
        self.setWindowTitle(translator.t("vna.mapping_title"))
        self.resize(*scaled_dialog_size(520, 300))

        self._frequency = QComboBox(self)
        self._mode = QComboBox(self)
        for mode, key in (
            ("rx", "vna.mapping_rx"),
            ("complex", "vna.mapping_complex"),
            ("polar", "vna.mapping_polar"),
        ):
            self._mode.addItem(translator.t(key), mode)
        self._first = QComboBox(self)
        self._second = QComboBox(self)
        for combo in (self._frequency, self._first, self._second):
            combo.addItems(self._headers)
        self._reference = QDoubleSpinBox(self)
        self._reference.setRange(1.0, 10_000.0)
        self._reference.setDecimals(3)
        self._reference.setValue(50.0)
        self._reference.setSuffix(" Ω")

        if initial is not None:
            self._select(self._frequency, initial.frequency)
            self._select(self._mode, initial.mode)
            self._select(self._first, initial.first)
            self._select(self._second, initial.second)
            self._reference.setValue(initial.reference_impedance_ohm)
        elif len(self._headers) >= 3:
            self._first.setCurrentIndex(1)
            self._second.setCurrentIndex(2)

        form = QFormLayout()
        form.addRow(QLabel(translator.t("vna.mapping_frequency"), self), self._frequency)
        form.addRow(QLabel(translator.t("vna.mapping_mode"), self), self._mode)
        form.addRow(QLabel(translator.t("vna.mapping_first"), self), self._first)
        form.addRow(QLabel(translator.t("vna.mapping_second"), self), self._second)
        form.addRow(QLabel(translator.t("vna.mapping_reference"), self), self._reference)
        for row, key in enumerate(
            (
                "vna.mapping_frequency",
                "vna.mapping_mode",
                "vna.mapping_first",
                "vna.mapping_second",
                "vna.mapping_reference",
            )
        ):
            apply_row_help(form, row, translator, key)
        hint = QLabel(translator.t("vna.mapping_hint"), self)
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
        layout.addWidget(buttons)

    @staticmethod
    def _select(combo: QComboBox, value: str) -> None:
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def mapping(self) -> VnaColumnMapping:
        mode = self._mode.currentData()
        return VnaColumnMapping(
            frequency=self._frequency.currentText(),
            mode=mode if isinstance(mode, str) else "rx",
            first=self._first.currentText(),
            second=self._second.currentText(),
            reference_impedance_ohm=self._reference.value(),
        )
