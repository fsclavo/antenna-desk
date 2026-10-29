# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Any

import pytest

from antennadesk.persistence.constants import SCHEMA_VERSION
from antennadesk.persistence.errors import ProjectFormatError, UnsupportedSchemaVersion
from antennadesk.persistence.migrations import migrate_document


def _document(version: int) -> dict[str, Any]:
    return {
        "format": "antennadesk-project",
        "schema_version": version,
        "project": {},
    }


def test_current_version_is_an_identity() -> None:
    document = _document(SCHEMA_VERSION)
    assert migrate_document(document) == document


def test_migrations_are_applied_in_order() -> None:
    calls: list[int] = []

    def migrate_1_to_2(data: dict[str, Any]) -> dict[str, Any]:
        calls.append(1)
        migrated = dict(data)
        migrated["from_v1"] = True
        return migrated

    def migrate_2_to_3(data: dict[str, Any]) -> dict[str, Any]:
        calls.append(2)
        migrated = dict(data)
        migrated["from_v2"] = True
        return migrated

    result = migrate_document(
        _document(1),
        target_version=3,
        migrations={1: migrate_1_to_2, 2: migrate_2_to_3},
    )

    assert calls == [1, 2]
    assert result["schema_version"] == 3
    assert result["from_v1"] is True
    assert result["from_v2"] is True


def test_future_version_is_rejected() -> None:
    with pytest.raises(UnsupportedSchemaVersion) as error:
        migrate_document(
            _document(SCHEMA_VERSION + 1),
            target_version=SCHEMA_VERSION,
        )
    assert error.value.found == SCHEMA_VERSION + 1
    assert error.value.supported == SCHEMA_VERSION


def test_missing_migration_is_rejected() -> None:
    with pytest.raises(ProjectFormatError, match="no migration"):
        migrate_document(_document(1), target_version=2, migrations={})


def test_unknown_format_is_rejected() -> None:
    document = _document(1)
    document["format"] = "something-else"
    with pytest.raises(ProjectFormatError, match="format"):
        migrate_document(document)


@pytest.mark.parametrize("version", ["1", True, 0, -1, None])
def test_invalid_schema_versions_are_rejected(version: object) -> None:
    document = _document(1)
    document["schema_version"] = version
    with pytest.raises(ProjectFormatError, match="schema_version"):
        migrate_document(document)


def test_v1_migration_adds_horizontal_orientation() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 1,
        "project": {
            "designs": [
                {
                    "parameters": {
                        "frequency_hz": 7_100_000.0,
                        "total_length_m": 20.0,
                        "height_m": 8.0,
                    }
                }
            ]
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == SCHEMA_VERSION
    assert migrated["project"]["designs"][0]["parameters"]["orientation"] == "horizontal"
    assert migrated["project"]["simulation_runs"] == []
    assert "orientation" not in document["project"]["designs"][0]["parameters"]


def test_v2_migration_adds_simulation_runs() -> None:
    document = {
        "format": "antennadesk-project",
        "schema_version": 2,
        "project": {
            "designs": [],
        },
    }

    migrated = migrate_document(document)

    assert migrated["schema_version"] == 3
    assert migrated["project"]["simulation_runs"] == []
    assert "simulation_runs" not in document["project"]
