# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Construction sheet dialog."""

from __future__ import annotations

from pathlib import Path

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
from ..i18n import Translator


class ConstructionDialog(QDialog):
    def __init__(
        self,
        translator: Translator,
        project: Project,
        design: DesignVariant,
        result: SimulationResult | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._project = project
        self._design = design
        self._result = result
        self.setWindowTitle(translator.t("construction.title"))
        self.resize(820, 720)

        self._browser = QTextBrowser(self)
        self._browser.setOpenExternalLinks(False)
        self._browser.setHtml(render_construction_sheet(project, design, result))

        self._save = QPushButton(translator.t("construction.save"), self)
        self._close = QPushButton(translator.t("action.close"), self)
        self._save.clicked.connect(self._save_html)
        self._close.clicked.connect(self.accept)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self._save)
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
            write_construction_sheet(self._project, self._design, self._result, path)
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
