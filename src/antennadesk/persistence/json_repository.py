"""Atomic JSON project repository."""

from __future__ import annotations

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


class JsonProjectRepository:
    """Read and write versioned ``.antennadesk`` project files."""

    def save(self, project: Project, path: Path) -> None:
        document = document_from_project(project)
        text = json.dumps(
            document.model_dump(mode="json"),
            indent=2,
            ensure_ascii=False,
        )
        text += "\n"
        size = len(text.encode("utf-8"))
        if size > MAX_PROJECT_SIZE_BYTES:
            raise ProjectTooLargeError(
                f"project is too large ({size} bytes; limit is {MAX_PROJECT_SIZE_BYTES} bytes)"
            )
        self._atomic_write(path, text)

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
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ProjectFormatError("project file is not valid UTF-8") from exc
        except OSError as exc:
            raise ProjectFormatError(f"could not read project file: {exc}") from exc

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
    def _atomic_write(path: Path, text: str) -> None:
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
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise ProjectFormatError(f"could not save project: {exc}") from exc
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
