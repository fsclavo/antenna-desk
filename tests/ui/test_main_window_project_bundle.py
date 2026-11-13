# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable project bundle actions in the main window."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox

from antennadesk.application.use_cases.project_bundle import (
    BundleExportResult,
    BundleImportResult,
)
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.i18n import Language
from antennadesk.ui.main_window import MainWindow


class _FakeExportBundle:
    captured: ClassVar[dict[str, object]] = {}
    result: ClassVar[BundleExportResult | None] = None

    def __init__(self, repository: object) -> None:
        del repository

    def execute(self, project: object, bundle_path: Path, *, base_dir: Path | None = None):
        type(self).captured = {
            "project": project,
            "bundle_path": bundle_path,
            "base_dir": base_dir,
        }
        assert type(self).result is not None
        return type(self).result


class _FakeImportBundle:
    captured: ClassVar[dict[str, object]] = {}
    result: ClassVar[BundleImportResult | None] = None
    error: ClassVar[str | None] = None

    def __init__(self, repository: object) -> None:
        del repository

    def execute(self, bundle_path: Path, destination_parent: Path):
        type(self).captured = {
            "bundle_path": bundle_path,
            "destination_parent": destination_parent,
        }
        if type(self).error is not None:
            raise ValueError(type(self).error)
        assert type(self).result is not None
        return type(self).result


def test_bundle_actions_are_in_the_file_menu_and_retranslate(window: MainWindow) -> None:
    assert window._export_bundle_action in window._file_menu.actions()
    assert window._import_bundle_action in window._file_menu.actions()
    assert window._export_bundle_action.text() == "Export Project Bundle..."
    assert window._import_bundle_action.text() == "Import Project Bundle..."
    assert window._export_bundle_action.toolTip()
    assert window._import_bundle_action.toolTip()

    window._set_language(Language.SPANISH)

    assert window._export_bundle_action.text() == "Exportar bundle del proyecto..."
    assert window._import_bundle_action.text() == "Importar bundle del proyecto..."
    window._set_language(Language.ENGLISH)


def test_export_bundle_writes_the_normalized_path(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert window._project is not None
    window._dirty = False
    _FakeExportBundle.captured = {}
    _FakeExportBundle.result = BundleExportResult(
        bundle_path=tmp_path / "project.antennadesk-bundle",
        asset_count=2,
        missing_assets=(),
        bundle_size=1234,
    )
    monkeypatch.setattr(
        main_window_module,
        "ExportProjectBundle",
        _FakeExportBundle,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(tmp_path / "project"), ""),
    )

    window.export_project_bundle()

    assert _FakeExportBundle.captured["bundle_path"] == (tmp_path / "project.antennadesk-bundle")
    assert _FakeExportBundle.captured["base_dir"] is None
    assert window._last_status_key == "status.bundle_exported"


def test_export_bundle_warns_about_missing_images(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window._dirty = False
    _FakeExportBundle.result = BundleExportResult(
        bundle_path=tmp_path / "project.antennadesk-bundle",
        asset_count=1,
        missing_assets=(str(tmp_path / "missing.jpg"),),
        bundle_size=1234,
    )
    warnings: list[str] = []
    monkeypatch.setattr(
        main_window_module,
        "ExportProjectBundle",
        _FakeExportBundle,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(tmp_path / "project"), ""),
    )
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: warnings.append(args[2]) or QMessageBox.StandardButton.Ok,
    )

    window.export_project_bundle()

    assert warnings
    assert "missing.jpg" in warnings[0]


def test_import_bundle_replaces_the_current_project(
    window: MainWindow,
    sample_project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window._dirty = False
    destination = tmp_path / "imported"
    destination.mkdir()
    project_path = destination / "project.antennadesk"
    _FakeImportBundle.error = None
    _FakeImportBundle.captured = {}
    _FakeImportBundle.result = BundleImportResult(
        project=sample_project,
        project_path=project_path,
        destination=destination,
        asset_count=1,
        missing_assets=(),
    )
    monkeypatch.setattr(
        main_window_module,
        "ImportProjectBundle",
        _FakeImportBundle,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(tmp_path / "bundle.antennadesk-bundle"), ""),
    )
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(destination),
    )

    window.import_project_bundle()

    assert _FakeImportBundle.captured["bundle_path"] == (tmp_path / "bundle.antennadesk-bundle")
    assert _FakeImportBundle.captured["destination_parent"] == destination
    assert window._current_path == project_path
    assert window._project == sample_project
    assert window._last_status_key == "status.bundle_imported"


def test_import_bundle_error_is_reported(
    window: MainWindow,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window._dirty = False
    _FakeImportBundle.error = "invalid bundle"
    errors: list[str] = []
    monkeypatch.setattr(
        main_window_module,
        "ImportProjectBundle",
        _FakeImportBundle,
    )
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: (str(tmp_path / "bad.antennadesk-bundle"), ""),
    )
    monkeypatch.setattr(
        QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(tmp_path),
    )
    monkeypatch.setattr(
        QMessageBox,
        "critical",
        lambda *args, **kwargs: errors.append(args[2]) or QMessageBox.StandardButton.Ok,
    )

    window.import_project_bundle()

    assert errors
    assert "invalid bundle" in errors[0]
    _FakeImportBundle.error = None


def test_import_bundle_cancel_keeps_the_current_project(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window._dirty = False
    previous = window._project
    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        lambda *args, **kwargs: ("", ""),
    )

    window.import_project_bundle()

    assert window._project is previous
