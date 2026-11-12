# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Curated reference design library dialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.design.evidence import EvidenceEntry, EvidenceLevel
from ...domain.design.reference_library import REFERENCE_DESIGNS, ReferenceDesign
from ...domain.simulation.bands import amateur_band_for
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator


class ReferenceLibraryDialog(QDialog):
    """Browse source-backed designs and open one as a new project."""

    def __init__(
        self,
        translator: Translator,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._references = REFERENCE_DESIGNS
        self.setWindowTitle(translator.t("reference.library.title"))
        self.resize(*scaled_dialog_size(980, 680))

        self._intro = QLabel(translator.t("reference.library.intro"), self)
        self._intro.setWordWrap(True)
        apply_help(self._intro, translator, "reference.library.details")

        self._search = QLineEdit(self)
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._filter)
        apply_help(self._search, translator, "reference.library.search")

        self._list = QListWidget(self)
        self._list.setAlternatingRowColors(True)
        self._list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._list.currentRowChanged.connect(self._selection_changed)
        apply_help(self._list, translator, "reference.library.list")

        self._details = QLabel(self)
        self._details.setWordWrap(True)
        self._details.setTextFormat(Qt.TextFormat.PlainText)
        self._details.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        apply_help(self._details, translator, "reference.library.details")

        self._simulate = QCheckBox(translator.t("reference.library.simulate_after"), self)
        self._simulate.setChecked(True)
        apply_help(self._simulate, translator, "reference.library.simulate")

        self._open = QPushButton(translator.t("reference.library.open"), self)
        self._open.clicked.connect(self.accept)
        apply_help(self._open, translator, "reference.library.open")
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))
        buttons.rejected.connect(self.reject)

        actions = QHBoxLayout()
        actions.addWidget(self._simulate)
        actions.addStretch(1)
        actions.addWidget(self._open)
        actions.addWidget(buttons)

        content = QHBoxLayout()
        content.addWidget(self._list, 2)
        content.addWidget(self._details, 3)

        layout = QVBoxLayout(self)
        layout.addWidget(self._intro)
        layout.addWidget(self._search)
        layout.addLayout(content, 1)
        layout.addLayout(actions)

        self.retranslate()
        self._select_initial()

    def selected_reference(self) -> ReferenceDesign | None:
        row = self._list.currentRow()
        if 0 <= row < len(self._references) and not self._list.item(row).isHidden():
            return self._references[row]
        return None

    def simulate_after_open(self) -> bool:
        return self._simulate.isChecked()

    def _select_initial(self) -> None:
        for row in range(self._list.count()):
            if not self._list.item(row).isHidden():
                self._list.setCurrentRow(row)
                return
        self._selection_changed()

    def _filter(self, *_args: object) -> None:
        query = self._search.text().strip().lower()
        first_visible: int | None = None
        for row, design in enumerate(self._references):
            item = self._list.item(row)
            haystack = " ".join(
                (
                    self._translator.t(design.title_key),
                    self._translator.t(design.summary_key),
                    *design.search_terms,
                )
            ).lower()
            visible = not query or query in haystack
            item.setHidden(not visible)
            if visible and first_visible is None:
                first_visible = row
        current = self._list.currentRow()
        if first_visible is None:
            self._details.setText(self._translator.t("reference.library.no_match"))
            self._open.setEnabled(False)
            return
        if current < 0 or self._list.item(current).isHidden():
            self._list.setCurrentRow(first_visible)
        else:
            self._selection_changed()

    def _selection_changed(self, *_args: object) -> None:
        design = self.selected_reference()
        if design is None:
            self._details.setText(self._translator.t("reference.library.no_match"))
            self._open.setEnabled(False)
            return
        self._details.setText(self._details_text(design))
        self._open.setEnabled(True)

    def _details_text(self, design: ReferenceDesign) -> str:
        t = self._translator.t
        band = amateur_band_for(design.frequency_hz)
        band_text = band.name if band is not None else f"{design.frequency_hz / 1e6:.4f} MHz"
        evidence = design.evidence
        return "\n".join(
            (
                t(design.title_key),
                t(design.summary_key),
                "",
                f"{t('reference.library.band')}: {band_text}",
                (f"{t('reference.library.evidence')}: {self._evidence_level_text(evidence)}"),
                "",
                f"{t('reference.library.published')}: {t(design.published_key)}",
                f"{t('reference.library.modeled')}: {t(design.modeled_key)}",
                "",
                (
                    f"{t('reference.library.source')}: "
                    f"{self._evidence_text(design, 'source', evidence.source)}"
                ),
                (
                    f"{t('reference.library.tolerance')}: "
                    f"{self._evidence_text(design, 'tolerance', evidence.tolerance)}"
                ),
                (
                    f"{t('reference.library.limitation')}: "
                    f"{self._evidence_text(design, 'limitation', evidence.limitation)}"
                ),
            )
        )

    def _evidence_text(self, design: ReferenceDesign, field: str, fallback: str) -> str:
        key = f"evidence.{design.evidence_template}.{field}"
        translated = self._translator.report(key)
        return fallback if translated == key else translated

    def _evidence_level_text(self, evidence: EvidenceEntry) -> str:
        key = {
            EvidenceLevel.REFERENCE: "reference.library.evidence.reference",
            EvidenceLevel.PUBLISHED: "reference.library.evidence.published",
            EvidenceLevel.EXPERIMENTAL: "reference.library.evidence.experimental",
        }[evidence.level]
        return self._translator.t(key)

    def retranslate(self) -> None:
        t = self._translator.t
        self.setWindowTitle(t("reference.library.title"))
        self._intro.setText(t("reference.library.intro"))
        self._search.setPlaceholderText(t("reference.library.search_placeholder"))
        self._simulate.setText(t("reference.library.simulate_after"))
        self._open.setText(t("reference.library.open"))
        self._list.clear()
        for design in self._references:
            band = amateur_band_for(design.frequency_hz)
            band_text = band.name if band is not None else "—"
            item = QListWidgetItem(
                t(
                    "reference.library.item",
                    title=t(design.title_key),
                    band=band_text,
                    level=design.evidence.level.value,
                )
            )
            item.setToolTip(t(design.summary_key))
            self._list.addItem(item)
        if self._list.count() > 0:
            self._list.setCurrentRow(0)
        self._filter()
        self._selection_changed()
