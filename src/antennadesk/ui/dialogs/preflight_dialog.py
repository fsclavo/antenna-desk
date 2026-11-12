# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction pre-flight dialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...domain.common.validation import Severity
from ...domain.design.preflight import (
    PreflightAction,
    PreflightFinding,
    PreflightReport,
    PreflightStatus,
)
from ..fonts import scaled_dialog_size
from ..help import apply_help
from ..i18n import Translator

_SEVERITY_COLORS = {
    Severity.ERROR: QColor("#b42318"),
    Severity.WARNING: QColor("#b54708"),
    Severity.INFO: QColor("#175cd3"),
}
_SEVERITY_GROUP_KEYS = {
    Severity.ERROR: "preflight.group.errors",
    Severity.WARNING: "preflight.group.warnings",
    Severity.INFO: "preflight.group.info",
}
_SEVERITY_ORDER = (Severity.ERROR, Severity.WARNING, Severity.INFO)


class PreflightDialog(QDialog):
    """Read-only construction readiness report with links to the fix."""

    def __init__(
        self,
        translator: Translator,
        report: PreflightReport,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._report = report
        self._selected_action: PreflightAction | None = None
        self.setWindowTitle(translator.t("preflight.title"))
        self.resize(*scaled_dialog_size(900, 640))

        self._intro = QLabel(translator.t("preflight.intro"), self)
        self._intro.setWordWrap(True)
        self._status = QLabel(self)
        self._status.setWordWrap(True)
        apply_help(self._status, translator, "preflight.status")
        self._counts = QLabel(self)
        self._counts.setWordWrap(True)

        self._tree = QTreeWidget(self)
        self._tree.setColumnCount(4)
        self._tree.setRootIsDecorated(True)
        self._tree.setAlternatingRowColors(True)
        self._tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self._tree.itemSelectionChanged.connect(self._update_action_button)
        self._tree.itemDoubleClicked.connect(self._activate_item)
        apply_help(self._tree, translator, "preflight.table")

        self._go_to = QPushButton(translator.t("preflight.go_to"), self)
        self._go_to.setEnabled(False)
        self._go_to.clicked.connect(self._go_to_problem)
        apply_help(self._go_to, translator, "preflight.go_to")
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(translator.t("action.close"))
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.reject)
        buttons.addButton(self._go_to, QDialogButtonBox.ButtonRole.ActionRole)

        layout = QVBoxLayout(self)
        layout.addWidget(self._intro)
        layout.addWidget(self._status)
        layout.addWidget(self._counts)
        layout.addWidget(self._tree, 1)
        layout.addWidget(buttons)

        self.retranslate()

    @property
    def selected_action(self) -> PreflightAction | None:
        return self._selected_action

    def _finding_message(self, finding: PreflightFinding) -> str:
        key = f"diagnostic.{finding.code}"
        translated = self._translator.t(key, **finding.translation_values())
        return finding.message if translated == key else translated

    def _action_text(self, action: PreflightAction) -> str:
        if action is PreflightAction.NONE:
            return ""
        return self._translator.t(f"preflight.action.{action.value}")

    def _where_text(self, finding: PreflightFinding) -> str:
        return finding.subject or finding.field or "—"

    def _category_text(self, finding: PreflightFinding) -> str:
        return self._translator.t(f"preflight.category.{finding.category.value}")

    def _populate(self) -> None:
        self._tree.clear()
        for severity in _SEVERITY_ORDER:
            group_findings = tuple(
                finding
                for finding in self._report.sorted_findings()
                if finding.severity is severity
            )
            if not group_findings:
                continue
            group = QTreeWidgetItem(
                [
                    self._translator.t(_SEVERITY_GROUP_KEYS[severity]),
                    "",
                    "",
                    "",
                ]
            )
            group.setFirstColumnSpanned(True)
            group.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = group.font(0)
            font.setBold(True)
            group.setFont(0, font)
            group.setForeground(0, QBrush(_SEVERITY_COLORS[severity]))
            for finding in group_findings:
                message = self._finding_message(finding)
                item = QTreeWidgetItem(
                    [
                        message,
                        self._category_text(finding),
                        self._where_text(finding),
                        self._action_text(finding.action),
                    ]
                )
                item.setData(0, Qt.ItemDataRole.UserRole, finding)
                item.setToolTip(0, message)
                item.setToolTip(
                    3,
                    (
                        self._translator.t("help.preflight.go_to")
                        if finding.action is not PreflightAction.NONE
                        else ""
                    ),
                )
                group.addChild(item)
            self._tree.addTopLevelItem(group)
            group.setExpanded(True)
        if not self._report.findings:
            item = QTreeWidgetItem([self._translator.t("preflight.no_findings"), "", "", ""])
            item.setFirstColumnSpanned(True)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self._tree.addTopLevelItem(item)

    def _status_text(self) -> str:
        if self._report.status is PreflightStatus.ERROR:
            return self._translator.t(
                "preflight.summary.error",
                errors=len(self._report.errors),
            )
        if self._report.status is PreflightStatus.WARNING:
            return self._translator.t(
                "preflight.summary.warning",
                warnings=len(self._report.warnings),
            )
        if self._report.findings:
            return self._translator.t(
                "preflight.summary.ready_info",
                info=len(self._report.infos),
            )
        return self._translator.t("preflight.summary.ready")

    def _apply_status_style(self) -> None:
        color = {
            PreflightStatus.ERROR: "#b42318",
            PreflightStatus.WARNING: "#b54708",
            PreflightStatus.READY: "#067647",
        }[self._report.status]
        self._status.setStyleSheet(f"color: {color}; font-weight: bold;")

    def retranslate(self) -> None:
        self.setWindowTitle(self._translator.t("preflight.title"))
        self._intro.setText(self._translator.t("preflight.intro"))
        self._status.setText(self._status_text())
        self._counts.setText(
            self._translator.t(
                "preflight.counts",
                errors=len(self._report.errors),
                warnings=len(self._report.warnings),
                info=len(self._report.infos),
            )
        )
        self._apply_status_style()
        self._tree.setHeaderLabels(
            [
                self._translator.t("preflight.column.finding"),
                self._translator.t("preflight.column.category"),
                self._translator.t("preflight.column.where"),
                self._translator.t("preflight.column.action"),
            ]
        )
        self._go_to.setText(self._translator.t("preflight.go_to"))
        apply_help(self._status, self._translator, "preflight.status")
        apply_help(self._go_to, self._translator, "preflight.go_to")
        apply_help(self._tree, self._translator, "preflight.table")
        self._populate()
        self._update_action_button()

    def _selected_finding(self) -> PreflightFinding | None:
        item = self._tree.currentItem()
        if item is None:
            return None
        finding = item.data(0, Qt.ItemDataRole.UserRole)
        return finding if isinstance(finding, PreflightFinding) else None

    def _update_action_button(self) -> None:
        finding = self._selected_finding()
        self._go_to.setEnabled(finding is not None and finding.action is not PreflightAction.NONE)

    def _activate_item(self, item: QTreeWidgetItem, column: int) -> None:
        del column
        finding = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(finding, PreflightFinding) and finding.action is not PreflightAction.NONE:
            self._selected_action = finding.action
            self.accept()

    def _go_to_problem(self) -> None:
        finding = self._selected_finding()
        if finding is None or finding.action is PreflightAction.NONE:
            return
        self._selected_action = finding.action
        self.accept()
