# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from antennadesk.ui import solver_locator


def test_configured_solver_wins(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    name = solver_locator._executable_name()
    configured = tmp_path / "configured-nec2c"
    bundled = tmp_path / "bundle" / name
    on_path = tmp_path / f"path-{name}"
    bundled.parent.mkdir()
    for executable in (configured, bundled, on_path):
        executable.write_text("", encoding="utf-8")
    monkeypatch.setenv("NEC2C", str(configured))
    monkeypatch.setattr(sys, "executable", str(tmp_path / "bundle" / "python"))
    monkeypatch.setattr(solver_locator.shutil, "which", lambda name: str(on_path))

    assert solver_locator.find_nec2c() == configured.resolve()


def test_bundled_solver_wins_over_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    name = solver_locator._executable_name()
    bundled = tmp_path / "bundle" / name
    on_path = tmp_path / f"path-{name}"
    bundled.parent.mkdir()
    bundled.write_text("", encoding="utf-8")
    on_path.write_text("", encoding="utf-8")
    monkeypatch.delenv("NEC2C", raising=False)
    monkeypatch.setattr(sys, "executable", str(bundled.parent / "python"))
    monkeypatch.setattr(solver_locator.shutil, "which", lambda name: str(on_path))

    assert solver_locator.find_nec2c() == bundled


def test_path_solver_is_used_when_nothing_is_bundled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    name = solver_locator._executable_name()
    on_path = tmp_path / f"path-{name}"
    on_path.write_text("", encoding="utf-8")
    monkeypatch.delenv("NEC2C", raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "bundle" / "python"))
    monkeypatch.setattr(solver_locator.shutil, "which", lambda name: str(on_path))

    assert solver_locator.find_nec2c() == on_path.resolve()


def test_missing_configured_solver_falls_through_to_none(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fake_module = tmp_path / "repo" / "src" / "antennadesk" / "ui" / "solver_locator.py"
    monkeypatch.setenv("NEC2C", str(tmp_path / "missing-nec2c"))
    monkeypatch.setattr(sys, "executable", str(tmp_path / "bundle" / "python"))
    monkeypatch.setattr(solver_locator.shutil, "which", lambda name: None)
    monkeypatch.setattr(solver_locator, "__file__", str(fake_module))
    monkeypatch.chdir(tmp_path)

    assert solver_locator.find_nec2c() is None


def test_repo_root_solver_is_used_as_a_last_resort(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    name = solver_locator._executable_name()
    repo = tmp_path / "repo"
    fake_module = repo / "src" / "antennadesk" / "ui" / "solver_locator.py"
    expected = repo / "spikes" / "phase0" / "build" / name
    expected.parent.mkdir(parents=True)
    expected.write_text("", encoding="utf-8")
    monkeypatch.delenv("NEC2C", raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "bundle" / "python"))
    monkeypatch.setattr(solver_locator.shutil, "which", lambda name: None)
    monkeypatch.setattr(solver_locator, "__file__", str(fake_module))
    monkeypatch.chdir(tmp_path)

    assert solver_locator.find_nec2c() == expected


def test_working_directory_solver_is_used_as_a_last_resort(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    name = solver_locator._executable_name()
    workdir = tmp_path / "work"
    expected = workdir / "spikes" / "phase0" / "build" / name
    expected.parent.mkdir(parents=True)
    expected.write_text("", encoding="utf-8")
    fake_module = tmp_path / "repo" / "src" / "antennadesk" / "ui" / "solver_locator.py"
    monkeypatch.delenv("NEC2C", raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "bundle" / "python"))
    monkeypatch.setattr(solver_locator.shutil, "which", lambda name: None)
    monkeypatch.setattr(solver_locator, "__file__", str(fake_module))
    monkeypatch.chdir(workdir)

    assert solver_locator.find_nec2c() == expected
