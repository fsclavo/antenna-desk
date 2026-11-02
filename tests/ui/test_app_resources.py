# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PySide6.QtGui import QIcon
from pytestqt.qtbot import QtBot

from antennadesk import __version__
from antennadesk.ui.app import main


def test_application_icon_is_a_loadable_resource(qtbot: QtBot) -> None:
    icon_path = Path("src/antennadesk/ui/resources/antennadesk.svg")
    assert icon_path.is_file()
    assert not QIcon(str(icon_path)).isNull()


def test_desktop_entry_points_to_the_gui_script() -> None:
    desktop = Path("packaging/antennadesk.desktop")
    assert desktop.is_file()
    text = desktop.read_text(encoding="utf-8")
    assert "Exec=antennadesk" in text
    assert "Icon=antennadesk" in text


def test_version_flag_prints_the_package_version(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", ["antennadesk", "--version"])

    assert main() == 0
    assert capsys.readouterr().out.strip() == __version__


def test_check_solver_reports_the_located_executable(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    executable = tmp_path / "nec2c"
    executable.write_text("", encoding="utf-8")
    monkeypatch.setattr("antennadesk.ui.app.find_nec2c", lambda: executable)
    monkeypatch.setattr(sys, "argv", ["antennadesk", "--check-solver"])

    assert main() == 0
    assert capsys.readouterr().out.strip() == str(executable)


def test_check_solver_fails_when_nec2c_is_missing(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("antennadesk.ui.app.find_nec2c", lambda: None)
    monkeypatch.setattr(sys, "argv", ["antennadesk", "--check-solver"])

    assert main() == 1
    assert "nec2c not found" in capsys.readouterr().err


def test_packaging_inputs_are_present() -> None:
    assert Path("packaging/antennadesk.spec").is_file()
    assert Path("packaging/antennadesk.png").is_file()
    assert Path("packaging/antennadesk.ico").is_file()
    assert Path("packaging/build_appimage.sh").is_file()
    assert Path("packaging/build_deb.sh").is_file()
    assert Path("packaging/build_frozen_bundle.sh").is_file()
    assert Path("packaging/build_windows.ps1").is_file()
    assert Path("packaging/clean_artifacts.sh").is_file()
    assert Path("packaging/sign_artifacts.sh").is_file()
    assert Path("packaging/debian/copyright").is_file()
