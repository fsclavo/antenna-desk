# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided antenna advisor dialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.design.advisor import (
    AdvisorBlocker,
    AdvisorCandidate,
    AdvisorRequest,
    Directionality,
    recommend,
)
from ...domain.design.suitability import Complexity, OperatingIntent
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator
from ..units import UnitSystem, length_from_m, length_to_m, length_unit_key
from .antenna_catalog_dialog import ENTRIES

ADVISOR_BANDS: tuple[str, ...] = (
    "80m",
    "40m",
    "30m",
    "20m",
    "17m",
    "15m",
    "12m",
    "10m",
)

DEFAULT_BANDS: frozenset[str] = frozenset({"40m", "20m", "10m"})
ENTRY_BY_KEY = {entry.key: entry for entry in ENTRIES}


class AntennaAdvisorDialog(QDialog):
    """Collect practical constraints and show up to three catalog matches."""

    def __init__(
        self,
        translator: Translator,
        unit_system: UnitSystem,
        *,
        initial_height_m: float | None = None,
        initial_width_m: float | None = None,
        portable: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._unit_system = unit_system
        self._candidates: tuple[AdvisorCandidate, ...] = ()
        self._request: AdvisorRequest | None = None
        self._blockers: tuple[AdvisorBlocker, ...] = ()
        self._selected_key: str | None = None

        self.setWindowTitle(translator.t("advisor.title"))
        self.resize(*scaled_dialog_size(1000, 700))
        self._build_ui()
        self._apply_initial_values(
            initial_height_m=initial_height_m,
            initial_width_m=initial_width_m,
            portable=portable,
        )

    def _build_ui(self) -> None:
        t = self._translator.t
        hint = QLabel(t("advisor.hint"), self)
        hint.setWordWrap(True)

        criteria = QGroupBox(t("advisor.criteria"), self)
        form = QFormLayout(criteria)
        self._bands = QListWidget(criteria)
        self._bands.setMinimumHeight(150)
        for band in ADVISOR_BANDS:
            item = QListWidgetItem(band)
            item.setFlags(
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setCheckState(
                Qt.CheckState.Checked if band in DEFAULT_BANDS else Qt.CheckState.Unchecked
            )
            item.setData(Qt.ItemDataRole.UserRole, band)
            self._bands.addItem(item)
        apply_help(self._bands, self._translator, "advisor.bands")

        self._height = QDoubleSpinBox(criteria)
        self._height.setRange(0.0, 10_000.0)
        self._height.setDecimals(2)
        self._height.setSpecialValueText(t("advisor.not_set"))
        self._height.setSuffix(f" {t(length_unit_key(self._unit_system))}")
        self._width = QDoubleSpinBox(criteria)
        self._width.setRange(0.0, 10_000.0)
        self._width.setDecimals(2)
        self._width.setSpecialValueText(t("advisor.not_set"))
        self._width.setSuffix(f" {t(length_unit_key(self._unit_system))}")

        self._installation = QComboBox(criteria)
        self._installation.addItem(t("advisor.permanent"), False)
        self._installation.addItem(t("advisor.portable"), True)

        self._intent = QComboBox(criteria)
        for intent in OperatingIntent:
            self._intent.addItem(t(f"advisor.intent.{intent.value}"), intent.value)

        self._tuner = QCheckBox(t("advisor.tuner"), criteria)

        self._complexity = QComboBox(criteria)
        for complexity in Complexity:
            self._complexity.addItem(
                t(f"advisor.complexity.{complexity.value}"),
                complexity.value,
            )
        self._complexity.setCurrentIndex(self._complexity.findData(Complexity.MODERATE.value))

        self._directionality = QComboBox(criteria)
        self._directionality.addItem(t("advisor.directionality.any"), None)
        self._directionality.addItem(
            t("advisor.directionality.omni"),
            Directionality.OMNI.value,
        )
        self._directionality.addItem(
            t("advisor.directionality.directional"),
            Directionality.DIRECTIONAL.value,
        )

        self._multiband = QCheckBox(t("advisor.multiband"), criteria)
        self._multiband.setChecked(True)

        rows: list[tuple[str, QWidget]] = [
            (t("advisor.bands"), self._bands),
            (t("advisor.height"), self._height),
            (t("advisor.width"), self._width),
            (t("advisor.installation"), self._installation),
            (t("advisor.intent"), self._intent),
            (t("advisor.complexity"), self._complexity),
            (t("advisor.directionality"), self._directionality),
        ]
        for row, (label_text, widget) in enumerate(rows):
            label = QLabel(label_text, criteria)
            form.addRow(label, widget)
            apply_row_help(form, row, self._translator, f"advisor.{self._help_key(row)}")
        form.addRow(self._tuner)
        form.addRow(self._multiband)
        apply_help(self._tuner, self._translator, "advisor.tuner")
        apply_help(self._multiband, self._translator, "advisor.multiband")

        self._find = QPushButton(t("advisor.find"), criteria)
        self._find.clicked.connect(self._find_candidates)
        apply_help(self._find, self._translator, "advisor.find")
        form.addRow(self._find)

        results = QGroupBox(t("advisor.results"), self)
        results_layout = QVBoxLayout(results)
        self._table = QTableWidget(0, 7, results)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.itemSelectionChanged.connect(self._selection_changed)
        apply_help(self._table, self._translator, "advisor.results")
        self._details = QLabel(results)
        self._details.setWordWrap(True)
        self._details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._details.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        results_layout.addWidget(self._table, 1)
        results_layout.addWidget(self._details, 1)

        body = QHBoxLayout()
        body.addWidget(criteria, 0)
        body.addWidget(results, 1)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setText(t("advisor.open"))
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self._buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(t("action.cancel"))
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        apply_help(
            self._buttons.button(QDialogButtonBox.StandardButton.Ok),
            self._translator,
            "advisor.open",
        )

        layout = QVBoxLayout(self)
        layout.addWidget(hint)
        layout.addLayout(body, 1)
        layout.addWidget(self._buttons)

    @staticmethod
    def _help_key(row: int) -> str:
        return (
            "bands",
            "height",
            "width",
            "installation",
            "intent",
            "complexity",
            "directionality",
        )[row]

    def _apply_initial_values(
        self,
        *,
        initial_height_m: float | None,
        initial_width_m: float | None,
        portable: bool,
    ) -> None:
        if initial_height_m is not None:
            self._height.setValue(length_from_m(initial_height_m, self._unit_system))
        if initial_width_m is not None:
            self._width.setValue(length_from_m(initial_width_m, self._unit_system))
        self._installation.setCurrentIndex(self._installation.findData(bool(portable)))

    def _selected_bands(self) -> frozenset[str]:
        bands: set[str] = set()
        for row in range(self._bands.count()):
            item = self._bands.item(row)
            if item.checkState() is Qt.CheckState.Checked:
                data = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(data, str):
                    bands.add(data)
        return frozenset(bands)

    def _request_from_form(self) -> AdvisorRequest:
        height = self._height.value()
        width = self._width.value()
        direction = self._directionality.currentData()
        return AdvisorRequest(
            bands=self._selected_bands(),
            multiband_required=self._multiband.isChecked(),
            available_height_m=(length_to_m(height, self._unit_system) if height > 0.0 else None),
            available_width_m=(length_to_m(width, self._unit_system) if width > 0.0 else None),
            portable=bool(self._installation.currentData()),
            intent=OperatingIntent(self._intent.currentData()),
            tuner_available=self._tuner.isChecked(),
            max_complexity=Complexity(self._complexity.currentData()),
            directionality=(Directionality(direction) if isinstance(direction, str) else None),
        )

    def _find_candidates(self) -> None:
        if not self._selected_bands():
            self._details.setText(self._translator.t("advisor.no_bands"))
            return
        try:
            request = self._request_from_form()
        except ValueError as exc:
            self._details.setText(str(exc))
            return
        result = recommend(request)
        self._request = request
        self._candidates = result.candidates
        self._blockers = result.blockers
        self._selected_key = None
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self._populate_table()
        if self._candidates:
            self._table.selectRow(0)
        else:
            self._details.setText(self._no_match_text())

    def _populate_table(self) -> None:
        t = self._translator.t
        self._table.setRowCount(len(self._candidates))
        headers = (
            "advisor.table.antenna",
            "advisor.table.fit",
            "advisor.table.bands",
            "advisor.table.space",
            "advisor.table.height",
            "advisor.table.feed",
            "advisor.table.complexity",
        )
        self._table.setHorizontalHeaderLabels([t(key) for key in headers])
        request = self._request
        if request is None:
            return
        for row, candidate in enumerate(self._candidates):
            profile = candidate.profile
            entry = ENTRY_BY_KEY.get(profile.catalog_key)
            label = t(entry.label_key) if entry is not None else profile.catalog_key
            covered = ", ".join(sorted(profile.bands & request.bands))
            values = (
                label,
                t(f"advisor.fit.{candidate.status.value}"),
                covered or "—",
                self._length_text(candidate.footprint_m),
                self._length_text(profile.min_height_m),
                t(f"advisor.feed.{profile.feed.value}"),
                t(f"advisor.complexity.{profile.complexity.value}"),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, profile.catalog_key)
                self._table.setItem(row, column, item)
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setStretchLastSection(True)

    def _length_text(self, value_m: float) -> str:
        value = length_from_m(value_m, self._unit_system)
        return f"{value:.1f} {self._translator.t(length_unit_key(self._unit_system))}"

    def _no_match_text(self) -> str:
        t = self._translator.t
        lines = [t("advisor.no_match")]
        if self._blockers:
            lines.append("")
            lines.append(t("advisor.blockers"))
            for blocker in self._blockers:
                lines.append(f"• {t(f'advisor.blocker.{blocker.value}')}")
        return "\n".join(lines)

    def _selection_changed(self) -> None:
        row = self._table.currentRow()
        if not 0 <= row < len(self._candidates):
            self._selected_key = None
            self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            return
        candidate = self._candidates[row]
        self._selected_key = candidate.profile.catalog_key
        self._buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        self._details.setText(self._details_text(candidate))

    def _details_text(self, candidate: AdvisorCandidate) -> str:
        t = self._translator.t
        profile = candidate.profile
        entry = ENTRY_BY_KEY.get(profile.catalog_key)
        description = t(entry.description_key) if entry is not None else ""
        evidence = t(entry.evidence_key) if entry is not None else profile.evidence_level
        lines = [description, ""]
        lines.append(
            t(
                "advisor.details.typical",
                gain=t(f"advisor.gain.{profile.gain_class.value}"),
                takeoff=t(f"advisor.takeoff.{profile.takeoff_class.value}"),
                bandwidth=t(f"advisor.bandwidth.{profile.bandwidth_class.value}"),
            )
        )
        lines.append(t("advisor.details.evidence", value=evidence))
        lines.append("")
        lines.append(t(f"advisor.profile.{profile.catalog_key}.tradeoff"))
        lines.append("")
        lines.append(t("advisor.details.reasons"))
        for reason in candidate.reasons:
            lines.append(f"• {t(f'advisor.reason.{reason}')}")
        if candidate.warnings:
            lines.append("")
            lines.append(t("advisor.details.warnings"))
            for warning in candidate.warnings:
                lines.append(f"• {t(f'advisor.warning.{warning}')}")
        lines.append("")
        lines.append(t("advisor.open_hint"))
        lines.append(t("advisor.disclaimer"))
        return "\n".join(lines)

    def selected_catalog_key(self) -> str | None:
        return self._selected_key

    def accept(self) -> None:
        if self._selected_key is None:
            return
        super().accept()
