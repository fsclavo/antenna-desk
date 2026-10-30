# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Antenna type catalog used by New Antenna."""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..i18n import Translator

CATALOG_TYPE_WIRE_DIPOLE = "wire_dipole"
CATALOG_TYPE_FOLDED_DIPOLE = "folded_dipole"
CATALOG_TYPE_LOOP = "loop"
CATALOG_TYPE_VERTICAL = "vertical"
CATALOG_TYPE_YAGI = "yagi"
CATALOG_TYPE_INVERTED_V = "inverted_v"
CATALOG_TYPE_CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    key: str
    label_key: str
    family_key: str
    description_key: str
    evidence_key: str


ENTRIES: tuple[CatalogEntry, ...] = (
    CatalogEntry(
        key=CATALOG_TYPE_WIRE_DIPOLE,
        label_key="antenna_type.wire_dipole",
        family_key="catalog.family.dipole",
        description_key="catalog.wire_dipole.description",
        evidence_key="catalog.evidence.builtin",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_FOLDED_DIPOLE,
        label_key="antenna_type.folded_dipole",
        family_key="catalog.family.dipole",
        description_key="catalog.folded_dipole.description",
        evidence_key="catalog.evidence.builtin",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_INVERTED_V,
        label_key="catalog.inverted_v",
        family_key="catalog.family.dipole",
        description_key="catalog.inverted_v.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_YAGI,
        label_key="catalog.yagi",
        family_key="catalog.family.yagi",
        description_key="catalog.yagi.description",
        evidence_key="catalog.evidence.yagi",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_LOOP,
        label_key="antenna_type.loop",
        family_key="catalog.family.loop",
        description_key="catalog.loop.description",
        evidence_key="catalog.evidence.builtin",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_VERTICAL,
        label_key="catalog.vertical",
        family_key="catalog.family.vertical",
        description_key="catalog.vertical.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_CUSTOM,
        label_key="catalog.custom",
        family_key="catalog.family.custom",
        description_key="catalog.custom.description",
        evidence_key="catalog.evidence.custom",
    ),
)


class AntennaCatalogDialog(QDialog):
    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self.setWindowTitle(translator.t("catalog.title"))
        self.resize(680, 500)

        self._search = QLineEdit(self)
        self._search.setPlaceholderText(translator.t("catalog.search"))
        self._search.textChanged.connect(self._filter)

        self._list = QListWidget(self)
        self._list.currentItemChanged.connect(self._selection_changed)
        self._list.itemDoubleClicked.connect(lambda _item: self.accept())

        self._detail = QLabel(self)
        self._detail.setWordWrap(True)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(translator.t("catalog.type"), self))
        layout.addWidget(self._search)
        layout.addWidget(self._list, 1)
        layout.addWidget(self._detail)
        layout.addWidget(self._buttons)

        for entry in ENTRIES:
            item = QListWidgetItem(
                f"{translator.t(entry.family_key)} · {translator.t(entry.label_key)}"
            )
            item.setData(1, entry.key)
            item.setData(2, entry.description_key)
            item.setData(3, entry.evidence_key)
            self._list.addItem(item)
        if self._list.count():
            self._list.setCurrentRow(0)

    def _filter(self, text: str) -> None:
        needle = text.strip().casefold()
        for row in range(self._list.count()):
            item = self._list.item(row)
            searchable = " ".join(
                [
                    item.text(),
                    self._translator.t(str(item.data(2))),
                    self._translator.t(str(item.data(3))),
                ]
            ).casefold()
            item.setHidden(bool(needle) and needle not in searchable)
        current = self._list.currentItem()
        if current is not None and current.isHidden():
            for row in range(self._list.count()):
                candidate = self._list.item(row)
                if not candidate.isHidden():
                    self._list.setCurrentItem(candidate)
                    break

    def _selection_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(current is not None)
        if current is None:
            self._detail.clear()
            return
        self._detail.setText(
            f"{self._translator.t(str(current.data(2)))}\n\n"
            f"{self._translator.t('catalog.evidence')}: "
            f"{self._translator.t(str(current.data(3)))}"
        )

    def selected_key(self) -> str | None:
        item = self._list.currentItem()
        if item is None:
            return None
        value = item.data(1)
        return value if isinstance(value, str) else None
