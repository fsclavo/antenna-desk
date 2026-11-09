# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Band selection dialog for multiband analysis."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.design.band_plan import BandDefault, BandPlan, BandSelection
from ...domain.simulation.bands import AMATEUR_BANDS, amateur_band_by_id, amateur_band_for
from ..fonts import scaled_dialog_size
from ..i18n import Translator
from ..parallelism import MAX_UI_PARALLEL_WORKERS, default_parallel_workers

PRESET_DEFAULT = "default"
PRESET_CURRENT = "current"
PRESET_40_20_10 = "40_20_10"
PRESET_80_10 = "80_10"
PRESET_ALL = "all"
PRESET_CUSTOM = "custom"

_PRESET_BANDS: dict[str, tuple[str, ...]] = {
    PRESET_40_20_10: ("40m", "20m", "10m"),
    PRESET_80_10: ("80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m"),
}


class BandAnalysisDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        default: BandDefault,
        *,
        current_frequency_hz: float,
        selected_plan: BandPlan | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._default = default
        self._current_frequency_hz = current_frequency_hz
        self._applying = False

        self.setWindowTitle(translator.t("band.dialog_title"))
        self.resize(*scaled_dialog_size(560, 620))

        self._preset = QComboBox(self)
        for key in (
            PRESET_DEFAULT,
            PRESET_CURRENT,
            PRESET_40_20_10,
            PRESET_80_10,
            PRESET_ALL,
            PRESET_CUSTOM,
        ):
            self._preset.addItem(translator.t(f"band.preset.{key}"), key)
        self._preset.currentIndexChanged.connect(self._apply_preset)

        self._workers = QSpinBox(self)
        self._workers.setRange(1, MAX_UI_PARALLEL_WORKERS)
        self._workers.setValue(default_parallel_workers())
        self._workers.setToolTip(translator.t("band.workers_hint"))

        self._table = QTableWidget(0, 3, self)
        self._table.setHorizontalHeaderLabels(
            [
                translator.t("band.table.band"),
                translator.t("band.table.range"),
                translator.t("band.table.points"),
            ]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setColumnWidth(0, 130)
        self._table.setColumnWidth(1, 220)

        for band in AMATEUR_BANDS:
            row = self._table.rowCount()
            self._table.insertRow(row)
            band_item = QTableWidgetItem(band.name)
            band_item.setData(Qt.ItemDataRole.UserRole, band.name)
            band_item.setFlags(
                band_item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled
            )
            band_item.setCheckState(Qt.CheckState.Unchecked)
            self._table.setItem(row, 0, band_item)
            range_item = QTableWidgetItem(f"{band.start_hz / 1e6:.3f} - {band.stop_hz / 1e6:.3f}")
            range_item.setFlags(range_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, 1, range_item)
            points = QSpinBox(self._table)
            points.setRange(3, 201)
            points.setValue(
                selected_plan.selections[0].points
                if selected_plan is not None and selected_plan.selections
                else 15
            )
            self._table.setCellWidget(row, 2, points)

        self._evidence = QLabel(translator.t(f"band.evidence.{default.evidence.value}"), self)
        self._evidence.setWordWrap(True)
        self._note = QLabel(translator.t(default.note_key), self)
        self._note.setWordWrap(True)

        form = QFormLayout()
        form.addRow(translator.t("band.preset"), self._preset)
        form.addRow(translator.t("band.workers"), self._workers)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._evidence)
        layout.addWidget(self._note)
        layout.addWidget(buttons)

        self._set_plan(selected_plan or default.plan)
        self._preset.setCurrentIndex(
            self._preset.findData(PRESET_CUSTOM if selected_plan is not None else PRESET_DEFAULT)
        )

    def _set_plan(self, plan: BandPlan) -> None:
        self._applying = True
        selected = {selection.band_id: selection for selection in plan.selections}
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            spin = self._table.cellWidget(row, 2)
            if item is None or not isinstance(spin, QSpinBox):
                continue
            band_id = item.data(Qt.ItemDataRole.UserRole)
            selection = selected.get(band_id)
            item.setCheckState(
                Qt.CheckState.Checked if selection is not None else Qt.CheckState.Unchecked
            )
            if selection is not None:
                spin.setValue(selection.points)
        self._applying = False

    def _apply_preset(self) -> None:
        if self._applying:
            return
        key = self._preset.currentData()
        if not isinstance(key, str) or key == PRESET_CUSTOM:
            return
        if key == PRESET_DEFAULT:
            self._set_plan(self._default.plan)
            return
        if key == PRESET_CURRENT:
            band = amateur_band_for(self._current_frequency_hz, tolerance_fraction=0.0)
            if band is None:
                self._set_plan(BandPlan(()))
            else:
                self._set_plan(BandPlan((BandSelection(band),)))
            return
        if key == PRESET_ALL:
            self._check_ids(tuple(band.name for band in AMATEUR_BANDS))
            return
        self._check_ids(_PRESET_BANDS.get(key, ()))

    def _check_ids(self, band_ids: tuple[str, ...]) -> None:
        wanted = set(band_ids)
        self._applying = True
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item is None:
                continue
            band_id = item.data(Qt.ItemDataRole.UserRole)
            item.setCheckState(
                Qt.CheckState.Checked if band_id in wanted else Qt.CheckState.Unchecked
            )
        self._applying = False

    def plan(self) -> BandPlan:
        selections: list[BandSelection] = []
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            spin = self._table.cellWidget(row, 2)
            if item is None or not isinstance(spin, QSpinBox):
                continue
            if item.checkState() is not Qt.CheckState.Checked:
                continue
            band_id = item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(band_id, str):
                continue
            band = amateur_band_by_id(band_id)
            if band is not None:
                selections.append(BandSelection(band, spin.value()))
        return BandPlan(tuple(selections))

    def workers(self) -> int:
        return self._workers.value()

    def _accept(self) -> None:
        if not self.plan():
            QMessageBox.warning(
                self,
                self._translator.t("band.dialog_title"),
                self._translator.t("band.none_selected"),
            )
            return
        self.accept()
