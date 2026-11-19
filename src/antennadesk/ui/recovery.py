# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Atomic autosave and crash-recovery files outside the project schema."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ..application.ports.project_repository import ProjectRepository
from ..domain.projects.project import Project

RECOVERY_FORMAT = "antennadesk-recovery"
RECOVERY_VERSION = 1
RECOVERY_PROJECT_NAME = "autosave.antennadesk"
RECOVERY_METADATA_NAME = "autosave.json"


@dataclass(frozen=True, slots=True)
class RecoverySnapshot:
    project: Project
    original_path: Path | None
    dirty: bool
    saved_at: str


class AutosaveRecovery:
    """Write one atomic recovery snapshot per running window."""

    def __init__(self, directory: Path, repository: ProjectRepository) -> None:
        self._directory = Path(directory).expanduser()
        self._repository = repository

    @property
    def directory(self) -> Path:
        return self._directory

    @property
    def project_path(self) -> Path:
        return self._directory / RECOVERY_PROJECT_NAME

    @property
    def metadata_path(self) -> Path:
        return self._directory / RECOVERY_METADATA_NAME

    def save(
        self,
        project: Project,
        *,
        original_path: Path | None,
        dirty: bool,
    ) -> None:
        """Write the project payload first, then its recovery metadata."""

        self._directory.mkdir(parents=True, exist_ok=True)
        payload = self._repository.prepare_payload(project)
        self._repository.write_payload(self.project_path, payload)
        metadata = {
            "format": RECOVERY_FORMAT,
            "version": RECOVERY_VERSION,
            "original_path": str(original_path) if original_path is not None else None,
            "dirty": dirty,
            "saved_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "project_name": project.name,
        }
        self._atomic_write_text(
            self.metadata_path,
            json.dumps(metadata, ensure_ascii=False, separators=(",", ":")),
        )

    def load(self) -> RecoverySnapshot | None:
        """Return the recovery snapshot, or None when no payload exists."""

        if not self.project_path.is_file():
            return None
        metadata = self._read_metadata()
        project = self._repository.load(self.project_path)
        raw_path = metadata.get("original_path")
        original_path = (
            Path(raw_path).expanduser() if isinstance(raw_path, str) and raw_path.strip() else None
        )
        raw_saved_at = metadata.get("saved_at")
        return RecoverySnapshot(
            project=project,
            original_path=original_path,
            dirty=metadata.get("dirty") is not False,
            saved_at=raw_saved_at if isinstance(raw_saved_at, str) else "",
        )

    def clear(self) -> None:
        for path in (self.project_path, self.metadata_path):
            try:
                path.unlink()
            except FileNotFoundError:
                continue

    def _read_metadata(self) -> dict[str, object]:
        try:
            text = self.metadata_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return {}
        try:
            value = json.loads(text)
        except (TypeError, ValueError):
            return {}
        return value if isinstance(value, dict) else {}

    def _atomic_write_text(self, path: Path, text: str) -> None:
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
