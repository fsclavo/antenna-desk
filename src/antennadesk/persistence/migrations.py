# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit project schema migrations."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .constants import PROJECT_FORMAT, SCHEMA_VERSION
from .errors import ProjectFormatError, UnsupportedSchemaVersion

Migration = Callable[[dict[str, Any]], dict[str, Any]]
MIGRATIONS: dict[int, Migration] = {}


def migrate_document(
    data: Mapping[str, Any],
    *,
    target_version: int = SCHEMA_VERSION,
    migrations: Mapping[int, Migration] | None = None,
) -> dict[str, Any]:
    """Validate the format/version envelope and apply migrations in order."""

    document = dict(data)

    if document.get("format") != PROJECT_FORMAT:
        raise ProjectFormatError(f"unsupported project format: {document.get('format')!r}")

    version = document.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int):
        raise ProjectFormatError("schema_version must be an integer")
    if version < 1:
        raise ProjectFormatError("schema_version must be greater than or equal to 1")
    if version > target_version:
        raise UnsupportedSchemaVersion(found=version, supported=target_version)

    active_migrations = migrations if migrations is not None else MIGRATIONS
    while version < target_version:
        migration = active_migrations.get(version)
        if migration is None:
            raise ProjectFormatError(f"no migration from schema version {version} to {version + 1}")
        document = migration(document)
        version += 1
        document["schema_version"] = version

    return document
