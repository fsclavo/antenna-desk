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
    configured = tmp_path / "configured-nec2c"
    bundled = tmp_path / "bundle" / "nec2c"
    on_path = tmp_path / "path-nec2c"
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
    bundled = tmp_path / "bundle" / "nec2c"
    on_path = tmp_path / "path-nec2c"
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
    on_path = tmp_path / "path-nec2c"
    on_path.write_text("", encoding="utf-8")
    monkeypatch.delenv("NEC2C", raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "bundle" / "python"))
    monkeypatch.setattr(solver_locator.shutil, "which", lambda name: str(on_path))

    assert solver_locator.find_nec2c() == on_path.resolve()
