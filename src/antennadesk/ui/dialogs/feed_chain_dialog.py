# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-frequency feed-chain loss budget for the current result."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.matching_network import MatchingNetworkPosition
from ...domain.projects.project import DesignVariant, Project
from ...domain.simulation.result import SimulationResult
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator
from ..units import UnitSystem


class FeedChainDialog(QDialog):
    """Show the modeled feed-chain stages and their dissipative losses."""

    def __init__(
        self,
        translator: Translator,
        project: Project,
        design: DesignVariant,
        result: SimulationResult,
        unit_system: UnitSystem = UnitSystem.METRIC,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._design = design
        self._result = result
        self._unit_system = unit_system
        self.setWindowTitle(translator.t("feed_chain.title"))
        self.resize(*scaled_dialog_size(980, 640))

        self._path = QLabel(self)
        self._path.setWordWrap(True)
        self._path.setText(self._path_text())
        apply_help(self._path, translator, "feed_chain.path")

        self._power = QDoubleSpinBox(self)
        self._power.setRange(0.001, 10_000.0)
        self._power.setDecimals(2)
        self._power.setSuffix(" W")
        self._power.setValue(100.0)
        self._power.valueChanged.connect(self._populate)
        apply_help(self._power, translator, "feed_chain.power")

        power_form = QFormLayout()
        self._power_label = QLabel(translator.t("feed_chain.power"), self)
        power_form.addRow(self._power_label, self._power)
        apply_help(self._power_label, translator, "feed_chain.power")

        self._table = QTableWidget(0, 9, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setSortingEnabled(False)
        apply_help(self._table, translator, "table.feed_chain")

        self._hint = QLabel(self)
        self._hint.setWordWrap(True)
        self._hint.setText(translator.t("feed_chain.hint"))
        apply_help(self._hint, translator, "feed_chain.hint")

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))

        layout = QVBoxLayout(self)
        layout.addWidget(self._path)
        layout.addLayout(power_form)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._summary)
        layout.addWidget(self._hint)
        layout.addWidget(buttons)
        self.retranslate()
        self._populate()

    def _position(self) -> MatchingNetworkPosition:
        return self._project.matching_network_position

    def _path_text(self) -> str:
        t = self._translator.t
        if self._project.matching_network is None:
            return t("feed_chain.path_direct")
        if self._position() is MatchingNetworkPosition.SHACK:
            return t("feed_chain.path_shack")
        return t("feed_chain.path_feedpoint")

    def retranslate(self) -> None:
        t = self._translator.t
        self.setWindowTitle(t("feed_chain.title"))
        self._power_label.setText(t("feed_chain.power"))
        self._table.setHorizontalHeaderLabels(
            [
                t("feed_chain.frequency"),
                t("feed_chain.swr"),
                t("feed_chain.mismatch"),
                t("feed_chain.line"),
                t("feed_chain.network"),
                t("feed_chain.balun"),
                t("feed_chain.delivered"),
                t("feed_chain.radiated"),
                t("feed_chain.dominant"),
            ]
        )
        self._hint.setText(t("feed_chain.hint"))
        self._path.setText(self._path_text())
        self._populate()

    @staticmethod
    def _value(value: float | None, unit: str = "dB") -> str:
        if value is None:
            return "—"
        if math.isinf(value):
            return "∞"
        return f"{value:.2f} {unit}" if unit else f"{value:.2f}"

    def _power_w(self) -> float:
        return self._power.value()

    def _populate(self, *_args: object) -> None:
        t = self._translator.t
        power = self._power_w()
        rows = self._result.frequencies
        self._table.setRowCount(len(rows))
        worst_line = 0.0
        worst_swr = 0.0
        for row, frequency in enumerate(rows):
            components: tuple[tuple[str, float | None], ...] = (
                (t("feed_chain.mismatch"), frequency.mismatch_loss_db),
                (t("feed_chain.line"), frequency.feed_line_loss_db),
                (t("feed_chain.network"), frequency.network_loss_db),
                (t("feed_chain.balun"), frequency.balun_loss_db),
            )
            known = [(name, value) for name, value in components if value is not None]
            dominant = max(known, key=lambda item: item[1])[0] if known else "—"
            total_loss = sum(value for _name, value in known)
            delivered = power * 10.0 ** (-total_loss / 10.0)
            efficiency = (
                frequency.power_budget.efficiency_percent
                if frequency.power_budget is not None
                else None
            )
            radiated = delivered * efficiency / 100.0 if efficiency is not None else None
            if frequency.feed_line_loss_db is not None:
                worst_line = max(worst_line, frequency.feed_line_loss_db)
            if math.isfinite(frequency.swr):
                worst_swr = max(worst_swr, frequency.swr)
            values = (
                f"{frequency.frequency_hz / 1e6:.6f}",
                self._value(frequency.swr, ""),
                self._value(frequency.mismatch_loss_db),
                self._value(frequency.feed_line_loss_db),
                self._value(frequency.network_loss_db),
                self._value(frequency.balun_loss_db),
                f"{delivered:.2f} W",
                f"{radiated:.2f} W" if radiated is not None else "—",
                dominant,
            )
            for column, value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(value))
        self._table.resizeColumnsToContents()
        self._summary.setText(
            t(
                "feed_chain.summary",
                power=f"{power:.2f}",
                line=f"{worst_line:.2f}",
                swr=("∞" if math.isinf(worst_swr) else f"{worst_swr:.2f}"),
            )
        )
