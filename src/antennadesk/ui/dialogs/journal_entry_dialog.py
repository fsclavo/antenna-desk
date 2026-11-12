# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create or edit one project journal entry."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from PySide6.QtCore import QDateTime, Qt, QTimeZone, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ...domain.projects.journal import (
    MAX_JOURNAL_IMAGE_REFERENCES,
    JournalEntry,
    JournalEntryKind,
)
from ...domain.projects.project import Project
from ...reporting.journal_snapshot import journal_design_snapshot
from ..fonts import scaled_dialog_size
from ..help import apply_help, apply_row_help
from ..i18n import Translator


class JournalEntryDialog(QDialog):
    """Edit the metadata, notes, images, and design link of one entry."""

    def __init__(
        self,
        translator: Translator,
        project: Project,
        parent: QWidget | None = None,
        *,
        entry: JournalEntry | None = None,
        default_design_id: UUID | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._existing_entry = entry
        self._now = now or (lambda: datetime.now(UTC))
        self._result: JournalEntry | None = None
        self.setWindowTitle(translator.t("journal.entry_title"))
        self.resize(*scaled_dialog_size(680, 720))

        self._title = QLineEdit(self)
        if entry is not None:
            self._title.setText(entry.title)
        self._date = QDateTimeEdit(self)
        self._date.setCalendarPopup(True)
        self._date.setDisplayFormat("yyyy-MM-dd HH:mm")
        self._date.setDateTime(
            QDateTime.fromSecsSinceEpoch(
                int((entry.created_at if entry is not None else self._now()).timestamp()),
                QTimeZone.utc(),
            )
        )
        self._kind = QComboBox(self)
        for kind in JournalEntryKind:
            self._kind.addItem(translator.t(f"journal.kind.{kind.value}"), kind)
        if entry is not None:
            index = self._kind.findData(entry.kind)
            if index >= 0:
                self._kind.setCurrentIndex(index)
        self._design = QComboBox(self)
        self._design.addItem(translator.t("journal.no_design"), None)
        for design in project.designs:
            self._design.addItem(design.name, design.id)
        initial_design = entry.design_id if entry is not None else default_design_id
        if initial_design is not None:
            for index in range(self._design.count()):
                if self._design.itemData(index) == initial_design:
                    self._design.setCurrentIndex(index)
                    break
        self._design.currentIndexChanged.connect(self._update_snapshot_controls)

        self._body = QPlainTextEdit(self)
        if entry is not None:
            self._body.setPlainText(entry.body)

        self._capture = QCheckBox(translator.t("journal.capture_snapshot"), self)
        self._capture.setChecked(entry is None and self._design.currentData() is not None)
        self._snapshot_info = QLabel(self)
        self._snapshot_info.setWordWrap(True)
        self._snapshot_info.setTextFormat(Qt.TextFormat.PlainText)
        self._snapshot_info.hide()

        self._images = QListWidget(self)
        if entry is not None:
            for reference in entry.image_references:
                self._images.addItem(QListWidgetItem(reference))
        self._images.currentRowChanged.connect(self._update_preview)
        self._add_image = QPushButton(translator.t("journal.image_add"), self)
        self._remove_image = QPushButton(translator.t("journal.image_remove"), self)
        self._open_image = QPushButton(translator.t("journal.image_open"), self)
        self._add_image.clicked.connect(self._choose_images)
        self._remove_image.clicked.connect(self._remove_selected_image)
        self._open_image.clicked.connect(self._open_selected_image)
        self._preview = QLabel(self)
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setMinimumSize(240, 150)
        self._preview.setWordWrap(True)

        self._validation = QLabel(self)
        self._validation.setWordWrap(True)
        self._validation.setStyleSheet("color: #a33a2b;")
        self._validation.hide()

        form = QFormLayout()
        form.addRow(translator.t("journal.field.title"), self._title)
        form.addRow(translator.t("journal.field.date"), self._date)
        form.addRow(translator.t("journal.field.kind"), self._kind)
        form.addRow(translator.t("journal.field.design"), self._design)
        for row, key in enumerate(
            (
                "journal.title",
                "journal.date",
                "journal.kind",
                "journal.design",
            )
        ):
            apply_row_help(form, row, translator, key)

        self._body_label = QLabel(translator.t("journal.field.body"), self)
        self._images_label = QLabel(translator.t("journal.field.images"), self)
        for widget, key in (
            (self._body_label, "journal.body"),
            (self._body, "journal.body"),
            (self._capture, "journal.snapshot"),
            (self._snapshot_info, "journal.snapshot"),
            (self._images_label, "journal.images"),
            (self._images, "journal.images"),
            (self._add_image, "journal.image_add"),
            (self._remove_image, "journal.image_remove"),
            (self._open_image, "journal.image_open"),
            (self._preview, "journal.preview"),
        ):
            apply_help(widget, translator, key)

        image_buttons = QHBoxLayout()
        image_buttons.addWidget(self._add_image)
        image_buttons.addWidget(self._remove_image)
        image_buttons.addWidget(self._open_image)
        image_buttons.addStretch(1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(translator.t("action.ok"))
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(
            translator.t("action.cancel")
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._body_label)
        layout.addWidget(self._body, 1)
        layout.addWidget(self._capture)
        layout.addWidget(self._snapshot_info)
        layout.addWidget(self._images_label)
        layout.addWidget(self._images, 1)
        layout.addLayout(image_buttons)
        layout.addWidget(self._preview)
        layout.addWidget(self._validation)
        layout.addWidget(buttons)

        self._update_snapshot_controls()
        self._update_preview()

    def entry(self) -> JournalEntry | None:
        return self._build_entry()

    def _build_entry(self) -> JournalEntry | None:
        title = self._title.text().strip()
        if not title:
            self._show_validation(self._translator.t("journal.title_required"))
            self._title.setFocus()
            return None
        references = self._image_references()
        if len(references) > MAX_JOURNAL_IMAGE_REFERENCES:
            self._show_validation(
                self._translator.t(
                    "journal.images_limit",
                    maximum=MAX_JOURNAL_IMAGE_REFERENCES,
                )
            )
            return None
        design_id = self._design.currentData()
        if not isinstance(design_id, UUID):
            design_id = None
        snapshot = (
            self._existing_entry.snapshot
            if self._existing_entry is not None and self._existing_entry.snapshot is not None
            else None
        )
        if snapshot is None and self._capture.isChecked() and design_id is not None:
            snapshot = journal_design_snapshot(self._project, self._project.design_by_id(design_id))
        return JournalEntry(
            id=self._existing_entry.id if self._existing_entry is not None else uuid4(),
            created_at=datetime.fromtimestamp(self._date.dateTime().toSecsSinceEpoch(), UTC),
            title=title,
            kind=self._kind.currentData() or JournalEntryKind.NOTE,
            body=self._body.toPlainText(),
            design_id=design_id,
            snapshot=snapshot,
            image_references=references,
        )

    def accept(self) -> None:
        result = self._build_entry()
        if result is None:
            return
        self._result = result
        super().accept()

    def _show_validation(self, message: str) -> None:
        self._validation.setText(message)
        self._validation.show()

    def _update_snapshot_controls(self, *_args: object) -> None:
        design_id = self._design.currentData()
        if self._existing_entry is not None and self._existing_entry.snapshot is not None:
            snapshot = self._existing_entry.snapshot
            self._capture.setChecked(False)
            self._capture.hide()
            self._snapshot_info.setText(
                self._translator.t(
                    "journal.snapshot_stored",
                    name=snapshot.design_name,
                    rows=len(snapshot.rows),
                )
            )
            self._snapshot_info.show()
            return
        self._snapshot_info.hide()
        self._capture.show()
        self._capture.setEnabled(isinstance(design_id, UUID))
        if not isinstance(design_id, UUID):
            self._capture.setChecked(False)

    def _image_references(self) -> tuple[str, ...]:
        return tuple(self._images.item(row).text() for row in range(self._images.count()))

    def _choose_images(self) -> None:
        paths, _selected_filter = QFileDialog.getOpenFileNames(
            self,
            self._translator.t("journal.image_choose"),
            "",
            self._translator.t("journal.image_filter"),
        )
        self._append_image_paths(tuple(paths))

    def _append_image_paths(self, paths: tuple[str, ...]) -> None:
        current = self._image_references()
        room = MAX_JOURNAL_IMAGE_REFERENCES - len(current)
        for path in paths[: max(room, 0)]:
            item = QListWidgetItem(path)
            item.setToolTip(path)
            self._images.addItem(item)
        if len(paths) > max(room, 0):
            self._show_validation(
                self._translator.t(
                    "journal.images_limit",
                    maximum=MAX_JOURNAL_IMAGE_REFERENCES,
                )
            )
        if paths and self._images.currentRow() < 0 and self._images.count() > 0:
            self._images.setCurrentRow(0)

    def _remove_selected_image(self) -> None:
        row = self._images.currentRow()
        if row < 0:
            return
        self._images.takeItem(row)
        self._update_preview()

    def _open_selected_image(self) -> None:
        path = self._selected_image_path()
        if path is None:
            return
        if not Path(path).is_file():
            self._show_validation(self._translator.t("journal.image_missing", path=path))
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def _selected_image_path(self) -> str | None:
        item = self._images.currentItem()
        return item.text() if item is not None else None

    def _update_preview(self, *_args: object) -> None:
        path = self._selected_image_path()
        if path is None:
            self._preview.clear()
            self._preview.setText(self._translator.t("journal.preview_hint"))
            return
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._preview.clear()
            self._preview.setText(self._translator.t("journal.preview_unavailable"))
            return
        self._preview.setPixmap(
            pixmap.scaled(
                320,
                200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
