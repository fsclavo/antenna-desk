# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only, source-backed materials reference."""

from __future__ import annotations

import html
from typing import Protocol

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.feed_line import FeedLine
from ...domain.design.materials_reference import (
    COAX_REFERENCES,
    FERRITE_REFERENCES,
    INSULATOR_REFERENCES,
    WIRE_REFERENCES,
    CoaxReference,
    ReferenceSource,
)
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator


class _ReferenceEntry(Protocol):
    @property
    def key(self) -> str: ...

    @property
    def source(self) -> ReferenceSource: ...


class MaterialsReferenceDialog(QDialog):
    """Show source-backed wire, coax, ferrite, and insulator data.

    The coax tab can initialize the project feed line with a datasheet point.
    Wire, ferrite, and insulator rows are informational and never alter the
    simulation model.
    """

    def __init__(
        self,
        translator: Translator,
        *,
        feed_line: FeedLine | None = None,
        can_apply: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._feed_line = feed_line
        self._can_apply = can_apply
        self._applied_feed_line: FeedLine | None = None
        self.setWindowTitle(translator.t("materials.title"))
        self.resize(*scaled_dialog_size(980, 640))

        self._details = QLabel(self)
        self._details.setWordWrap(True)
        self._details.setTextFormat(Qt.TextFormat.RichText)
        self._details.setOpenExternalLinks(True)
        self._details.setMinimumHeight(72)
        apply_help(self._details, translator, "materials.details")

        self._tabs = QTabWidget(self)
        self._tables: dict[str, QTableWidget] = {}
        self._entries: dict[str, tuple[_ReferenceEntry, ...]] = {}
        self._tab_keys = ("wire", "coax", "ferrite", "insulator")

        self._tabs.addTab(self._build_wire_tab(), translator.t("materials.wire"))
        self._tabs.addTab(self._build_coax_tab(), translator.t("materials.coax"))
        self._tabs.addTab(self._build_ferrite_tab(), translator.t("materials.ferrite"))
        self._tabs.addTab(self._build_insulator_tab(), translator.t("materials.insulator"))
        self._tabs.currentChanged.connect(self._update_details)

        self._reference_note = QLabel(translator.t("materials.reference_only"), self)
        self._reference_note.setWordWrap(True)
        apply_help(self._reference_note, translator, "materials.reference_only")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))

        layout = QVBoxLayout(self)
        layout.addWidget(self._reference_note)
        layout.addWidget(self._tabs, 1)
        layout.addWidget(self._details)
        layout.addWidget(buttons)

        for tab_key in self._tab_keys:
            tab = self._tabs.widget(self._tab_keys.index(tab_key))
            if tab is not None:
                apply_help(tab, translator, f"materials.{tab_key}")
            apply_help(self._tables[tab_key], translator, "materials.table")
        self._update_details()

    def _make_table(self, headers: tuple[str, ...]) -> QTableWidget:
        table = QTableWidget(0, len(headers), self)
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.setWordWrap(False)
        table.itemSelectionChanged.connect(self._update_details)
        return table

    @staticmethod
    def _add_row(table: QTableWidget, values: tuple[str, ...]) -> None:
        row = table.rowCount()
        table.insertRow(row)
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setToolTip(value)
            table.setItem(row, column, item)

    def _finish_table(self, key: str, table: QTableWidget) -> QWidget:
        table.resizeColumnsToContents()
        for column in range(table.columnCount() - 1):
            table.setColumnWidth(column, table.columnWidth(column) + 18)
        table.horizontalHeader().setSectionResizeMode(
            table.columnCount() - 1,
            QHeaderView.ResizeMode.Stretch,
        )
        self._tables[key] = table
        if table.rowCount():
            table.selectRow(0)
        return table

    def _build_wire_tab(self) -> QWidget:
        t = self._translator.t
        table = self._make_table(
            (
                t("materials.column.material"),
                t("materials.column.conductivity"),
                t("materials.column.permeability"),
                t("materials.column.source"),
            )
        )
        self._entries["wire"] = WIRE_REFERENCES
        for entry in WIRE_REFERENCES:
            self._add_row(
                table,
                (
                    t(f"materials.wire.{entry.key}.name"),
                    f"{entry.conductivity_ms_per_m:.1f} MS/m",
                    f"{entry.material.relative_permeability:g}",
                    entry.source.label,
                ),
            )
        return self._finish_table("wire", table)

    def _build_coax_tab(self) -> QWidget:
        t = self._translator.t
        tab = QWidget(self)
        table = self._make_table(
            (
                t("materials.column.type"),
                t("materials.column.impedance"),
                t("materials.column.velocity_factor"),
                t("materials.column.loss"),
                t("materials.column.reference_frequency"),
                t("materials.column.source"),
            )
        )
        self._entries["coax"] = COAX_REFERENCES
        for entry in COAX_REFERENCES:
            self._add_row(
                table,
                (
                    t(f"materials.coax.{entry.key}.name"),
                    f"{entry.characteristic_impedance_ohm:g} Ω",
                    f"{entry.velocity_factor:.2f}",
                    f"{entry.matched_loss_db_per_100m:.2f} dB/100m",
                    f"{entry.reference_frequency_hz / 1_000_000.0:g} MHz",
                    entry.source.label,
                ),
            )
        self._finish_table("coax", table)
        self._apply_button = QPushButton(t("materials.apply"), tab)
        self._apply_button.setEnabled(self._can_apply)
        self._apply_button.clicked.connect(self._apply_coax)
        apply_help(self._apply_button, self._translator, "materials.apply")
        self._apply_hint = QLabel(
            t("materials.apply_hint" if self._can_apply else "materials.apply_unavailable"),
            tab,
        )
        self._apply_hint.setWordWrap(True)
        apply_help(self._apply_hint, self._translator, "materials.apply_hint")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(table, 1)
        layout.addWidget(self._apply_button)
        layout.addWidget(self._apply_hint)
        return tab

    def _build_ferrite_tab(self) -> QWidget:
        t = self._translator.t
        table = self._make_table(
            (
                t("materials.column.mix"),
                t("materials.column.material_type"),
                t("materials.column.initial_permeability"),
                t("materials.column.frequency_range"),
                t("materials.column.source"),
            )
        )
        self._entries["ferrite"] = FERRITE_REFERENCES
        for entry in FERRITE_REFERENCES:
            self._add_row(
                table,
                (
                    t(f"materials.ferrite.{entry.key}.name"),
                    entry.material_type,
                    f"{entry.initial_permeability:g}",
                    f"{entry.frequency_min_mhz:g}-{entry.frequency_max_mhz:g} MHz",
                    entry.source.label,
                ),
            )
        return self._finish_table("ferrite", table)

    def _build_insulator_tab(self) -> QWidget:
        t = self._translator.t
        table = self._make_table(
            (
                t("materials.column.material"),
                t("materials.column.dielectric_strength"),
                t("materials.column.weather"),
                t("materials.column.source"),
            )
        )
        self._entries["insulator"] = INSULATOR_REFERENCES
        for entry in INSULATOR_REFERENCES:
            self._add_row(
                table,
                (
                    t(f"materials.insulator.{entry.key}.name"),
                    entry.dielectric_strength,
                    t(f"materials.weather.{entry.weather_key}"),
                    entry.source.label,
                ),
            )
        return self._finish_table("insulator", table)

    def _update_details(self, *args: object) -> None:
        del args
        index = self._tabs.currentIndex()
        if not 0 <= index < len(self._tab_keys):
            return
        tab_key = self._tab_keys[index]
        table = self._tables.get(tab_key)
        entries = self._entries.get(tab_key)
        if table is None or entries is None:
            return
        row = table.currentRow()
        if row < 0 and table.rowCount():
            row = 0
        if not 0 <= row < len(entries):
            self._details.setText(self._translator.t("materials.details.none"))
            return
        entry = entries[row]
        key = entry.key
        name = self._translator.t(f"materials.{tab_key}.{key}.name")
        note = self._translator.t(f"materials.{tab_key}.{key}.note")
        source = entry.source
        source_label = html.escape(source.label)
        source_html = (
            f'<a href="{html.escape(source.url, quote=True)}">{source_label}</a>'
            if source.url
            else source_label
        )
        self._details.setText(
            f"<b>{html.escape(name)}</b><br>{html.escape(note)}<br>"
            f"{html.escape(self._translator.t('materials.source'))}: {source_html}"
        )

    def _apply_coax(self) -> None:
        table = self._tables["coax"]
        row = table.currentRow()
        if not 0 <= row < len(COAX_REFERENCES):
            return
        entry: CoaxReference = COAX_REFERENCES[row]
        length_m = self._feed_line.length_m if self._feed_line is not None else 10.0
        self._applied_feed_line = entry.feed_line(length_m)
        self.accept()

    def result_feed_line(self) -> FeedLine | None:
        return self._applied_feed_line
