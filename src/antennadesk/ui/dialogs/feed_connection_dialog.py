# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Read-only constructive feed-connection detail."""

from __future__ import annotations

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.antennas.feed_connection import FeedConnectionDetail
from ...reporting.feed_schematic import feed_schematic_svg
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator


class FeedConnectionDialog(QDialog):
    """Show the physical feed wiring without changing the design."""

    def __init__(
        self,
        translator: Translator,
        detail: FeedConnectionDetail,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._detail = detail
        self.resize(*scaled_dialog_size(920, 720))

        self._summary = QLabel(self)
        self._summary.setWordWrap(True)
        self._summary.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._schematic = QSvgWidget(self)
        self._schematic.setMinimumHeight(280)

        self._table = QTableWidget(0, 3, self)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        apply_help(self._table, translator, "feed_connection.table")

        self._modeled = self._state_group()
        self._recorded = self._state_group()
        self._recommended = self._state_group()
        self._not_modeled = self._state_group()

        self._steps = QLabel(self)
        self._steps.setWordWrap(True)
        self._steps.setTextFormat(Qt.TextFormat.PlainText)
        self._limitations = QLabel(self)
        self._limitations.setWordWrap(True)
        self._limitations.setTextFormat(Qt.TextFormat.PlainText)

        self._hardware = QLabel(self)
        self._hardware.setWordWrap(True)

        content = QWidget(self)
        content_layout = QVBoxLayout(content)
        content_layout.addWidget(self._summary)
        content_layout.addWidget(self._schematic)
        content_layout.addWidget(self._table)
        for group in (
            self._modeled,
            self._recorded,
            self._recommended,
            self._not_modeled,
        ):
            content_layout.addWidget(group)
        content_layout.addWidget(self._hardware)
        content_layout.addWidget(self._steps)
        content_layout.addWidget(self._limitations)
        content_layout.addStretch(1)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            parent=self,
        )
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))

        layout = QVBoxLayout(self)
        layout.addWidget(scroll, 1)
        layout.addWidget(buttons)
        self.retranslate()

    def _state_group(self) -> QGroupBox:
        group = QGroupBox(self)
        group_layout = QVBoxLayout(group)
        label = QLabel(group)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.PlainText)
        group_layout.addWidget(label)
        return group

    @staticmethod
    def _bullets(values: tuple[str, ...]) -> str:
        return "\n".join(f"• {value}" for value in values) if values else "—"

    def _set_group(self, group: QGroupBox, values: tuple[str, ...]) -> None:
        label = group.findChild(QLabel)
        if label is not None:
            label.setText(self._bullets(tuple(self._translator.report(value) for value in values)))

    def retranslate(self) -> None:
        t = self._translator.t
        self.setWindowTitle(t("feed_connection.title"))
        self._summary.setText(self._translator.report(self._detail.summary))
        self._schematic.load(
            QByteArray(feed_schematic_svg(self._detail, self._translator.report).encode("utf-8"))
        )
        self._table.setHorizontalHeaderLabels(
            [t("feed_connection.from"), t("feed_connection.to"), t("feed_connection.notes")]
        )
        self._table.setRowCount(len(self._detail.connections))
        for row, connection in enumerate(self._detail.connections):
            values = (
                self._translator.report(connection.source),
                self._translator.report(connection.target),
                self._translator.report(connection.note) if connection.note else "",
            )
            for column, value in enumerate(values):
                self._table.setItem(row, column, QTableWidgetItem(value))
        self._table.resizeColumnsToContents()

        for group, title, state_values in (
            (self._modeled, t("feed_connection.modeled"), self._detail.modeled),
            (self._recorded, t("feed_connection.recorded"), self._detail.recorded),
            (self._recommended, t("feed_connection.recommended"), self._detail.recommended),
            (self._not_modeled, t("feed_connection.not_modeled"), self._detail.not_modeled),
        ):
            group.setTitle(title)
            self._set_group(group, state_values)

        if self._detail.match_hardware:
            self._hardware.setText(
                t(
                    "feed_connection.hardware",
                    value=self._translator.report(self._detail.match_hardware),
                )
            )
            self._hardware.show()
        else:
            self._hardware.hide()
        self._steps.setText(
            t(
                "feed_connection.steps_value",
                value="\n".join(
                    f"{index}. {self._translator.report(step)}"
                    for index, step in enumerate(self._detail.steps, start=1)
                ),
            )
        )
        self._limitations.setText(
            t(
                "feed_connection.limitations_value",
                value=self._bullets(
                    tuple(self._translator.report(item) for item in self._detail.limitations)
                ),
            )
        )
        apply_help(self, self._translator, "section.feed_connection")
        apply_help(self._summary, self._translator, "feed_connection.summary")
        apply_help(self._schematic, self._translator, "feed_connection.schematic")
        apply_help(self._table, self._translator, "feed_connection.table")
        apply_help(self._steps, self._translator, "feed_connection.steps")
        apply_help(self._limitations, self._translator, "feed_connection.limitations")
