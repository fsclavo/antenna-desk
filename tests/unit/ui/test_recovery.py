# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Autosave recovery store behavior."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from antennadesk.domain.projects.project import Project
from antennadesk.persistence.errors import ProjectFormatError
from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.recovery import AutosaveRecovery


def test_recovery_round_trip_and_clear(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())

    recovery.save(
        sample_project,
        original_path=tmp_path / "source.antennadesk",
        dirty=True,
    )

    assert recovery.project_path.is_file()
    assert recovery.metadata_path.is_file()
    snapshot = recovery.load()
    assert snapshot is not None
    assert snapshot.project == sample_project
    assert snapshot.original_path == tmp_path / "source.antennadesk"
    assert snapshot.dirty is True
    assert snapshot.saved_at

    recovery.clear()
    assert recovery.load() is None
    assert not recovery.project_path.exists()
    assert not recovery.metadata_path.exists()


def test_corrupt_metadata_falls_back_to_safe_defaults(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())
    recovery.save(sample_project, original_path=None, dirty=True)
    recovery.metadata_path.write_text("{bad json", encoding="utf-8")

    snapshot = recovery.load()

    assert snapshot is not None
    assert snapshot.project == sample_project
    assert snapshot.original_path is None
    assert snapshot.dirty is True


def test_corrupt_project_payload_raises(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    recovery = AutosaveRecovery(tmp_path / "recovery", JsonProjectRepository())
    recovery.save(sample_project, original_path=None, dirty=True)
    recovery.project_path.write_bytes(b"not a project")

    with pytest.raises(ProjectFormatError):
        recovery.load()


@pytest.mark.skipif(os.geteuid() == 0, reason="root bypasses directory permissions")
def test_read_only_recovery_directory_is_reported(
    sample_project: Project,
    tmp_path: Path,
) -> None:
    directory = tmp_path / "recovery"
    directory.mkdir()
    directory.chmod(0o500)
    recovery = AutosaveRecovery(directory, JsonProjectRepository())
    try:
        with pytest.raises((OSError, ProjectFormatError)):
            recovery.save(sample_project, original_path=None, dirty=True)
    finally:
        directory.chmod(0o700)
