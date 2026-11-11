# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Windows installer and release asset integrity (no Windows build required)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
NSIS = ROOT / "packaging" / "windows" / "antennadesk.nsi"
BUILD_WINDOWS = ROOT / "packaging" / "build_windows.ps1"


def test_nsis_installer_script_creates_shortcuts_and_uninstaller() -> None:
    text = NSIS.read_text(encoding="utf-8")

    assert "RequestExecutionLevel admin" in text
    assert 'InstallDir "$PROGRAMFILES64\\${APPNAME}"' in text
    assert "OutFile" in text
    assert "File /r" in text
    assert "CreateShortcut" in text
    assert "WriteUninstaller" in text
    assert 'Section "Uninstall"' in text
    assert "AntennaDesk.exe" in text


def test_windows_build_script_builds_zip_and_installer() -> None:
    text = BUILD_WINDOWS.read_text(encoding="utf-8")

    assert "AntennaDesk-$Version-windows-x86_64.zip" in text
    assert "AntennaDesk-$Version-windows-x86_64-setup.exe" in text
    assert "makensis" in text
    assert "/DSRCDIR=" in text
    assert "/DOUTFILE=" in text
    assert "/DICONFILE=" in text
    assert "collect_bundle_licenses.py" in text
    assert "check_bundle_licenses.py" in text
    assert "Get-FileHash" in text
    assert "Sign-Binary" in text


def test_release_workflow_builds_and_tests_the_installer() -> None:
    text = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")

    assert "choco install nsis" in text
    assert "Build Windows bundle and installer" in text
    assert "Smoke test Windows installer" in text
    assert "Uninstall.exe" in text
    assert "dist/*-setup.exe" in text
    assert "dist/*-setup.exe.sha256" in text
    assert "Generate wheel and sdist checksums" in text
    assert "dist/*.whl.sha256" in text
    assert "dist/*.tar.gz.sha256" in text


def test_clean_artifacts_removes_the_installer() -> None:
    text = (ROOT / "packaging" / "clean_artifacts.sh").read_text(encoding="utf-8")

    assert "AntennaDesk-*-windows-x86_64-setup.exe" in text
    assert "AntennaDesk-*-windows-x86_64-setup.exe.sha256" in text


def test_documentation_lists_the_windows_installer() -> None:
    release = (ROOT / "docs" / "RELEASE.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "windows-x86_64-setup.exe" in release
    assert "Add/Remove Programs" in release
    assert "windows-x86_64-setup.exe" in readme
    assert "Start Menu" in readme
