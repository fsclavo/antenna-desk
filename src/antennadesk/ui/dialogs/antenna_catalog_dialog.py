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

from ..fonts import scaled_dialog_size
from ..i18n import Translator

CATALOG_TYPE_WIRE_DIPOLE = "wire_dipole"
CATALOG_TYPE_FOLDED_DIPOLE = "folded_dipole"
CATALOG_TYPE_LOOP = "loop"
CATALOG_TYPE_DELTA_LOOP = "delta_loop"
CATALOG_TYPE_QUAD_LOOP = "quad_loop"
CATALOG_TYPE_MAGNETIC_LOOP = "magnetic_loop"
CATALOG_TYPE_VERTICAL = "vertical"
CATALOG_TYPE_LOADED_VERTICAL = "loaded_vertical"
CATALOG_TYPE_DISCONE = "discone"
CATALOG_TYPE_YAGI = "yagi"
CATALOG_TYPE_MOXON = "moxon"
CATALOG_TYPE_FAN_DIPOLE = "fan_dipole"
CATALOG_TYPE_TRAP_DIPOLE = "trap_dipole"
CATALOG_TYPE_T2FD = "t2fd"
CATALOG_TYPE_ENDFED = "endfed"
CATALOG_TYPE_SLOPER = "sloper"
CATALOG_TYPE_RANDOM_WIRE = "random_wire"
CATALOG_TYPE_DOUBLET = "doublet"
CATALOG_TYPE_G5RV = "g5rv"
CATALOG_TYPE_ZS6BKW = "zs6bkw"
CATALOG_TYPE_ZEPP = "zepp"
CATALOG_TYPE_J_POLE = "j_pole"
CATALOG_TYPE_RINGO = "ringo"
CATALOG_TYPE_HALF_SQUARE = "half_square"
CATALOG_TYPE_BOBTAIL_CURTAIN = "bobtail_curtain"
CATALOG_TYPE_BIQUAD = "biquad"
CATALOG_TYPE_DOUBLE_BIQUAD = "double_biquad"
CATALOG_TYPE_BEVERAGE = "beverage"
CATALOG_TYPE_LOADED_DIPOLE = "loaded_dipole"
CATALOG_TYPE_PHASED_VERTICAL = "phased_vertical"
CATALOG_TYPE_QUAD_BEAM = "quad_beam"
CATALOG_TYPE_SLIM_JIM = "slim_jim"
CATALOG_TYPE_INVERTED_V = "inverted_v"
CATALOG_TYPE_INVERTED_L = "inverted_l"
CATALOG_TYPE_OCFD = "ocfd"
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
        key=CATALOG_TYPE_RINGO,
        label_key="catalog.ringo",
        family_key="catalog.family.vertical",
        description_key="catalog.ringo.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_J_POLE,
        label_key="catalog.j_pole",
        family_key="catalog.family.vertical",
        description_key="catalog.j_pole.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_HALF_SQUARE,
        label_key="catalog.half_square",
        family_key="catalog.family.vertical",
        description_key="catalog.half_square.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_BOBTAIL_CURTAIN,
        label_key="catalog.bobtail_curtain",
        family_key="catalog.family.vertical",
        description_key="catalog.bobtail_curtain.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_SLIM_JIM,
        label_key="catalog.slim_jim",
        family_key="catalog.family.vertical",
        description_key="catalog.slim_jim.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_BIQUAD,
        label_key="catalog.biquad",
        family_key="catalog.family.loop",
        description_key="catalog.biquad.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_DOUBLE_BIQUAD,
        label_key="catalog.double_biquad",
        family_key="catalog.family.loop",
        description_key="catalog.double_biquad.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_BEVERAGE,
        label_key="catalog.beverage",
        family_key="catalog.family.wire",
        description_key="catalog.beverage.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_LOADED_DIPOLE,
        label_key="catalog.loaded_dipole",
        family_key="catalog.family.dipole",
        description_key="catalog.loaded_dipole.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_PHASED_VERTICAL,
        label_key="catalog.phased_vertical",
        family_key="catalog.family.vertical",
        description_key="catalog.phased_vertical.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_QUAD_BEAM,
        label_key="catalog.quad_beam",
        family_key="catalog.family.loop",
        description_key="catalog.quad_beam.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_DISCONE,
        label_key="catalog.discone",
        family_key="catalog.family.vertical",
        description_key="catalog.discone.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_ENDFED,
        label_key="catalog.endfed",
        family_key="catalog.family.dipole",
        description_key="catalog.endfed.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_SLOPER,
        label_key="catalog.sloper",
        family_key="catalog.family.dipole",
        description_key="catalog.sloper.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_RANDOM_WIRE,
        label_key="catalog.random_wire",
        family_key="catalog.family.dipole",
        description_key="catalog.random_wire.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_G5RV,
        label_key="catalog.g5rv",
        family_key="catalog.family.dipole",
        description_key="catalog.g5rv.description",
        evidence_key="catalog.evidence.g5rv",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_ZS6BKW,
        label_key="catalog.zs6bkw",
        family_key="catalog.family.dipole",
        description_key="catalog.zs6bkw.description",
        evidence_key="catalog.evidence.zs6bkw",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_ZEPP,
        label_key="catalog.zepp",
        family_key="catalog.family.dipole",
        description_key="catalog.zepp.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_DOUBLET,
        label_key="catalog.doublet",
        family_key="catalog.family.dipole",
        description_key="catalog.doublet.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_FAN_DIPOLE,
        label_key="catalog.fan_dipole",
        family_key="catalog.family.dipole",
        description_key="catalog.fan_dipole.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_TRAP_DIPOLE,
        label_key="catalog.trap_dipole",
        family_key="catalog.family.dipole",
        description_key="catalog.trap_dipole.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_T2FD,
        label_key="catalog.t2fd",
        family_key="catalog.family.dipole",
        description_key="catalog.t2fd.description",
        evidence_key="catalog.evidence.t2fd",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_INVERTED_V,
        label_key="catalog.inverted_v",
        family_key="catalog.family.dipole",
        description_key="catalog.inverted_v.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_INVERTED_L,
        label_key="catalog.inverted_l",
        family_key="catalog.family.vertical",
        description_key="catalog.inverted_l.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_OCFD,
        label_key="catalog.ocfd",
        family_key="catalog.family.dipole",
        description_key="catalog.ocfd.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_MOXON,
        label_key="catalog.moxon",
        family_key="catalog.family.yagi",
        description_key="catalog.moxon.description",
        evidence_key="catalog.evidence.moxon",
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
        key=CATALOG_TYPE_DELTA_LOOP,
        label_key="catalog.delta_loop",
        family_key="catalog.family.loop",
        description_key="catalog.delta_loop.description",
        evidence_key="catalog.evidence.builtin",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_QUAD_LOOP,
        label_key="catalog.quad_loop",
        family_key="catalog.family.loop",
        description_key="catalog.quad_loop.description",
        evidence_key="catalog.evidence.builtin",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_MAGNETIC_LOOP,
        label_key="catalog.magnetic_loop",
        family_key="catalog.family.loop",
        description_key="catalog.magnetic_loop.description",
        evidence_key="catalog.evidence.experimental",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_VERTICAL,
        label_key="catalog.vertical",
        family_key="catalog.family.vertical",
        description_key="catalog.vertical.description",
        evidence_key="catalog.evidence.published",
    ),
    CatalogEntry(
        key=CATALOG_TYPE_LOADED_VERTICAL,
        label_key="catalog.loaded_vertical",
        family_key="catalog.family.vertical",
        description_key="catalog.loaded_vertical.description",
        evidence_key="catalog.evidence.published",
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
    def __init__(
        self,
        translator: Translator,
        parent: QWidget | None = None,
        *,
        initial_key: str | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self.setWindowTitle(translator.t("catalog.title"))
        self.resize(*scaled_dialog_size(680, 500))

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
            initial_row = 0
            if initial_key is not None:
                for row in range(self._list.count()):
                    if self._list.item(row).data(1) == initial_key:
                        initial_row = row
                        break
            self._list.setCurrentRow(initial_row)

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
