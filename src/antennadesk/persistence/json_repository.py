# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Atomic JSON project repository."""

from __future__ import annotations

import gzip
import json
import os
import tempfile
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from ..domain.projects.project import Project
from .constants import MAX_PROJECT_SIZE_BYTES
from .errors import ProjectFormatError, ProjectTooLargeError
from .migrations import migrate_document
from .schema import ProjectDocument, document_from_project, project_from_document

GZIP_MAGIC = b"\x1f\x8b"
COMPRESSION_LEVEL = 6


class JsonProjectRepository:
    """Read and write versioned, losslessly compressed ``.antennadesk`` files.

    New files are gzip-compressed UTF-8 JSON. Plain JSON files written by older
    versions are still accepted on load.
    """

    @staticmethod
    def _serialize(project: Project) -> str:
        document = document_from_project(project)
        text = json.dumps(
            document.model_dump(mode="json"),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return text + "\n"

    @staticmethod
    def _compress(data: bytes) -> bytes:
        return gzip.compress(data, compresslevel=COMPRESSION_LEVEL, mtime=0)

    @staticmethod
    def _decompress(data: bytes) -> bytes:
        if data.startswith(GZIP_MAGIC):
            return gzip.decompress(data)
        return data

    def prepare_payload(self, project: Project) -> bytes:
        """Serialize and compress a project without writing it to disk."""

        return self._compress(self._serialize(project).encode("utf-8"))

    def write_payload(self, path: Path, payload: bytes) -> None:
        """Write a prepared payload atomically, enforcing the size limit."""

        size = len(payload)
        if size > MAX_PROJECT_SIZE_BYTES:
            raise ProjectTooLargeError(
                f"project is too large ({size} bytes compressed; "
                f"limit is {MAX_PROJECT_SIZE_BYTES} bytes)"
            )
        self._atomic_write(path, payload)

    def serialized_size(self, project: Project) -> int:
        """Return the compressed on-disk size of the project."""

        return len(self.prepare_payload(project))

    def save(self, project: Project, path: Path) -> None:
        self.write_payload(path, self.prepare_payload(project))

    def load(self, path: Path) -> Project:
        if not path.is_file():
            raise ProjectFormatError(f"project file not found: {path}")

        try:
            size = path.stat().st_size
        except OSError as exc:
            raise ProjectFormatError(f"could not read project file: {exc}") from exc
        if size > MAX_PROJECT_SIZE_BYTES:
            raise ProjectTooLargeError(
                f"project file is too large ({size} bytes; limit is {MAX_PROJECT_SIZE_BYTES} bytes)"
            )

        try:
            data = path.read_bytes()
            data = self._decompress(data)
            text = data.decode("utf-8")
        except (OSError, gzip.BadGzipFile, EOFError) as exc:
            raise ProjectFormatError(f"could not read project file: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise ProjectFormatError("project file is not valid UTF-8") from exc

        try:
            raw: Any = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ProjectFormatError(f"invalid project JSON: {exc}") from exc
        if not isinstance(raw, dict):
            raise ProjectFormatError("project file root must be a JSON object")

        try:
            migrated = migrate_document(cast(dict[str, Any], raw))
            document = ProjectDocument.model_validate(migrated)
            return project_from_document(document)
        except ProjectFormatError:
            raise
        except ValidationError as exc:
            raise ProjectFormatError(f"invalid project file: {exc}") from exc
        except ValueError as exc:
            raise ProjectFormatError(f"invalid project file: {exc}") from exc

    @staticmethod
    def _atomic_write(path: Path, payload: bytes) -> None:
        path = Path(path)
        parent = path.parent
        if not parent.is_dir():
            raise ProjectFormatError(f"project directory does not exist: {parent}")

        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=parent,
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise ProjectFormatError(f"could not save project: {exc}") from exc
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
