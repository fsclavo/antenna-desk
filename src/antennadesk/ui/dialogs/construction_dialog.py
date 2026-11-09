# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction sheet dialog."""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QImage, QTextDocument
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ...domain.projects.project import DesignVariant, Project
from ...domain.simulation.result import SimulationResult
from ...reporting.construction_sheet import (
    render_construction_sheet,
    write_construction_sheet,
)
from ..construction_pdf import write_construction_pdf
from ..fonts import scaled_dialog_size
from ..i18n import Translator


def _png_data_uri(image: QImage) -> str | None:
    if image.isNull():
        return None
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as handle:
        path = Path(handle.name)
    try:
        if not image.save(str(path)):
            return None
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    finally:
        path.unlink(missing_ok=True)


class ConstructionDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        project: Project,
        design: DesignVariant,
        result: SimulationResult | None,
        parent: QWidget | None = None,
        *,
        figure_image: QImage | None = None,
        auxiliary_image: QImage | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._design = design
        self._result = result
        self._figure_image = figure_image
        self._auxiliary_image = auxiliary_image
        self._figure_data_uri = _png_data_uri(figure_image) if figure_image else None
        self._auxiliary_data_uri = _png_data_uri(auxiliary_image) if auxiliary_image else None
        self.setWindowTitle(translator.t("construction.title"))
        self.resize(*scaled_dialog_size(820, 720))

        self._browser = QTextBrowser(self)
        self._browser.setOpenExternalLinks(False)
        preview_uri = "construction-figure" if figure_image is not None else None
        auxiliary_preview = "installation-view" if auxiliary_image is not None else None
        document = QTextDocument(self._browser)
        if figure_image is not None:
            document.addResource(
                QTextDocument.ResourceType.ImageResource,
                QUrl("construction-figure"),
                figure_image,
            )
        if auxiliary_image is not None:
            document.addResource(
                QTextDocument.ResourceType.ImageResource,
                QUrl("installation-view"),
                auxiliary_image,
            )
        document.setHtml(
            render_construction_sheet(
                project,
                design,
                result,
                figure_png_data_uri=preview_uri,
                auxiliary_png_data_uri=auxiliary_preview,
            )
        )
        self._browser.setDocument(document)

        self._save = QPushButton(translator.t("construction.save"), self)
        self._save_pdf = QPushButton(translator.t("construction.save_pdf"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._save.clicked.connect(self._save_html)
        self._save_pdf.clicked.connect(self._save_pdf_file)
        self._close.clicked.connect(self.accept)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self._save)
        buttons.addWidget(self._save_pdf)
        buttons.addWidget(self._close)

        layout = QVBoxLayout(self)
        layout.addWidget(self._browser, 1)
        layout.addLayout(buttons)

    def _save_html(self) -> None:
        suggested = f"{self._project.name}-{self._design.name}-construction.html".replace(
            "/", "-"
        ).replace("\\", "-")
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.construction_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.html_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() not in {".html", ".htm"}:
            path = path.with_suffix(".html")
        try:
            write_construction_sheet(
                self._project,
                self._design,
                self._result,
                path,
                figure_png_data_uri=self._figure_data_uri,
                auxiliary_png_data_uri=self._auxiliary_data_uri,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._translator.t("construction.title"),
                self._translator.t("error.export", message=str(exc)),
            )
            return
        QMessageBox.information(
            self,
            self._translator.t("construction.title"),
            self._translator.t("status.exported"),
        )

    def _save_pdf_file(self) -> None:
        suggested = f"{self._project.name}-{self._design.name}-construction.pdf".replace(
            "/", "-"
        ).replace("\\", "-")
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self._translator.t("dialog.pdf_title"),
            str(Path.home() / suggested),
            self._translator.t("dialog.pdf_filter"),
        )
        if not filename:
            return
        path = Path(filename)
        if path.suffix.lower() != ".pdf":
            path = path.with_suffix(".pdf")
        try:
            write_construction_pdf(
                self._translator,
                self._project,
                self._design,
                self._result,
                path,
                figure_image=self._figure_image,
                auxiliary_image=self._auxiliary_image,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                self._translator.t("construction.title"),
                self._translator.t("error.export", message=str(exc)),
            )
            return
        QMessageBox.information(
            self,
            self._translator.t("construction.title"),
            self._translator.t("status.exported"),
        )
