# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Empty-state page shown when no project is open."""

from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..fonts import scaled_pixel_font
from ..help import apply_help
from ..i18n import Translator
from ..recent_projects import RecentProject


class StartPage(QWidget):
    """Small start screen with the project entry points."""

    new_requested = Signal()
    open_requested = Signal()
    advise_requested = Signal()
    example_requested = Signal(str)
    reference_requested = Signal()
    recent_requested = Signal(str)
    recent_remove_requested = Signal(str)

    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._translator = translator
        self._recent_entries: tuple[RecentProject, ...] = ()

        self._title = QLabel(self)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setWordWrap(True)
        self._apply_title_font()

        self._description = QLabel(self)
        self._description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._description.setWordWrap(True)

        self._new_button = QPushButton(self)
        self._new_button.setMinimumHeight(40)
        self._new_button.setMinimumWidth(220)
        self._new_button.clicked.connect(self.new_requested)

        self._open_button = QPushButton(self)
        self._open_button.setMinimumHeight(40)
        self._open_button.setMinimumWidth(220)
        self._open_button.clicked.connect(self.open_requested)

        self._advise_button = QPushButton(self)
        self._advise_button.setMinimumHeight(40)
        self._advise_button.setMinimumWidth(220)
        self._advise_button.clicked.connect(self.advise_requested)

        self._recent_label = QLabel(self)
        self._recent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._recent_list = QListWidget(self)
        self._recent_list.setMinimumWidth(360)
        self._recent_list.setMaximumHeight(140)
        self._recent_list.itemActivated.connect(self._recent_activated)
        self._recent_list.currentItemChanged.connect(self._update_remove_button)
        self._recent_empty = QLabel(self)
        self._recent_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._recent_empty.setWordWrap(True)

        self._remove_recent_button = QPushButton(self)
        self._remove_recent_button.clicked.connect(self._remove_selected_recent)

        self._example_button = QToolButton(self)
        self._example_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._example_button.setMinimumHeight(36)
        self._example_button.setMinimumWidth(220)
        self._example_menu = QMenu(self._example_button)
        self._example_actions: dict[str, QAction] = {}
        for kind in ("dipole", "yagi", "vertical"):
            action = self._example_menu.addAction("")
            action.triggered.connect(
                lambda _checked=False, example=kind: self.example_requested.emit(example)
            )
            self._example_actions[kind] = action
        self._example_button.setMenu(self._example_menu)

        self._reference_button = QPushButton(self)
        self._reference_button.setMinimumHeight(36)
        self._reference_button.setMinimumWidth(220)
        self._reference_button.clicked.connect(self.reference_requested)

        self._flow = QLabel(self)
        self._flow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flow.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.addStretch(1)
        layout.addWidget(self._title)
        layout.addSpacing(8)
        layout.addWidget(self._description)
        layout.addSpacing(24)
        layout.addWidget(self._new_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._advise_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._open_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self._recent_label)
        layout.addWidget(self._recent_list)
        layout.addWidget(self._recent_empty)
        layout.addWidget(
            self._remove_recent_button,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        layout.addSpacing(16)
        layout.addWidget(self._example_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._reference_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self._flow)
        layout.addStretch(2)

        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.fontChanged.connect(self._on_application_font_changed)

        self.retranslate()
        self._update_remove_button()

    def _apply_title_font(self) -> None:
        self._title.setFont(
            scaled_pixel_font(
                22,
                QFont.Weight.DemiBold,
                self.font().family(),
            )
        )

    def _on_application_font_changed(self, font: QFont) -> None:
        del font
        self._apply_title_font()

    def set_recent_projects(self, entries: Sequence[RecentProject]) -> None:
        self._recent_entries = tuple(entries)
        self._populate_recent()

    def _populate_recent(self) -> None:
        self._recent_list.clear()
        for entry in self._recent_entries:
            missing = not entry.path.is_file()
            text = entry.display_name
            if missing:
                text = self._translator.t("start.recent_missing", name=text)
            item = QListWidgetItem(text, self._recent_list)
            item.setData(Qt.ItemDataRole.UserRole, str(entry.path))
            item.setToolTip(entry.display_name)
        has_entries = bool(self._recent_entries)
        self._recent_list.setVisible(has_entries)
        self._recent_empty.setVisible(not has_entries)
        self._update_remove_button()

    def _recent_activated(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(path, str) and path:
            self.recent_requested.emit(path)

    def _remove_selected_recent(self) -> None:
        item = self._recent_list.currentItem()
        path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(path, str) and path:
            self.recent_remove_requested.emit(path)

    def _update_remove_button(self, *_args: object) -> None:
        self._remove_recent_button.setEnabled(self._recent_list.currentItem() is not None)

    def retranslate(self) -> None:
        self._title.setText(self._translator.t("start.title"))
        self._description.setText(self._translator.t("start.description"))
        self._new_button.setText(self._translator.t("action.new"))
        self._open_button.setText(self._translator.t("action.open"))
        self._advise_button.setText(self._translator.t("start.advise"))
        self._recent_label.setText(self._translator.t("start.recent"))
        self._recent_empty.setText(self._translator.t("start.no_recent"))
        self._remove_recent_button.setText(self._translator.t("start.remove_recent"))
        self._example_button.setText(self._translator.t("start.examples"))
        self._reference_button.setText(self._translator.t("start.reference_library"))
        self._flow.setText(self._translator.t("start.flow"))
        for kind, action in self._example_actions.items():
            action.setText(self._translator.t(f"start.example.{kind}"))
        apply_help(self._new_button, self._translator, "action.new")
        apply_help(self._open_button, self._translator, "action.open")
        apply_help(self._advise_button, self._translator, "action.antenna_advisor")
        apply_help(self._recent_label, self._translator, "start.recent")
        apply_help(self._recent_list, self._translator, "start.recent")
        apply_help(self._remove_recent_button, self._translator, "start.remove_recent")
        apply_help(self._example_button, self._translator, "start.examples")
        apply_help(self._reference_button, self._translator, "start.reference_library")
        self._populate_recent()
