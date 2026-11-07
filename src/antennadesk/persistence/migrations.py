# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit project schema migrations."""

from __future__ import annotations

import copy
import math
from collections.abc import Callable, Mapping
from typing import Any

from .constants import PROJECT_FORMAT, SCHEMA_VERSION
from .errors import ProjectFormatError, UnsupportedSchemaVersion

Migration = Callable[[dict[str, Any]], dict[str, Any]]


def _migrate_v1_to_v2(document: dict[str, Any]) -> dict[str, Any]:
    """Add the dipole orientation field to schema version 1 designs."""

    migrated = copy.deepcopy(document)
    project = migrated.get("project")
    if isinstance(project, dict):
        designs = project.get("designs")
        if isinstance(designs, list):
            for design in designs:
                if not isinstance(design, dict):
                    continue
                parameters = design.get("parameters")
                if isinstance(parameters, dict) and "orientation" not in parameters:
                    parameters["orientation"] = "horizontal"
    return migrated


def _migrate_v2_to_v3(document: dict[str, Any]) -> dict[str, Any]:
    """Add the simulation-run list to schema version 2 projects."""

    migrated = copy.deepcopy(document)
    project = migrated.get("project")
    if isinstance(project, dict) and "simulation_runs" not in project:
        project["simulation_runs"] = []
    return migrated


def _migrate_v3_to_v4(document: dict[str, Any]) -> dict[str, Any]:
    """Add optional band/batch metadata to simulation runs."""

    migrated = copy.deepcopy(document)
    project = migrated.get("project")
    if isinstance(project, dict):
        runs = project.get("simulation_runs")
        if isinstance(runs, list):
            for run in runs:
                if not isinstance(run, dict):
                    continue
                run.setdefault("band_id", None)
                run.setdefault("batch_id", None)
    return migrated


def _migrate_v4_to_v5(document: dict[str, Any]) -> dict[str, Any]:
    """Add optional feed-transformer ratios to OCFD and custom designs."""

    migrated = copy.deepcopy(document)
    project = migrated.get("project")
    if not isinstance(project, dict):
        return migrated
    designs = project.get("designs")
    if not isinstance(designs, list):
        return migrated
    for design in designs:
        if not isinstance(design, dict):
            continue
        parameters = design.get("parameters")
        if not isinstance(parameters, dict):
            continue
        if design.get("antenna_type") == "ocfd":
            parameters.setdefault("transformer_ratio", 1.0)
        elif design.get("antenna_type") == "custom":
            parameters.setdefault("feed_transformer_ratio", 1.0)
    return migrated


def _migrate_v5_to_v6(document: dict[str, Any]) -> dict[str, Any]:
    """Add optional persisted band-intent metadata to designs."""

    migrated = copy.deepcopy(document)
    project = migrated.get("project")
    if not isinstance(project, dict):
        return migrated
    designs = project.get("designs")
    if isinstance(designs, list):
        for design in designs:
            if isinstance(design, dict):
                design.setdefault("band_plan", None)
    return migrated


def _migrate_v6_to_v7(document: dict[str, Any]) -> dict[str, Any]:
    """Add the default horizontal polarization to Yagi and Moxon designs."""

    migrated = copy.deepcopy(document)
    project = migrated.get("project")
    if not isinstance(project, dict):
        return migrated
    designs = project.get("designs")
    if not isinstance(designs, list):
        return migrated
    for design in designs:
        if not isinstance(design, dict):
            continue
        if design.get("antenna_type") not in {"yagi", "moxon"}:
            continue
        parameters = design.get("parameters")
        if isinstance(parameters, dict):
            parameters.setdefault("polarization", "horizontal")
    return migrated


def _add_negative_resistance_diagnostics(project: dict[str, Any]) -> None:
    runs = project.get("simulation_runs")
    if not isinstance(runs, list):
        return
    for run in runs:
        if not isinstance(run, dict):
            continue
        result = run.get("result")
        if not isinstance(result, dict):
            continue
        frequencies = result.get("frequencies")
        if not isinstance(frequencies, list) or not frequencies:
            continue
        negative = [
            frequency
            for frequency in frequencies
            if isinstance(frequency, dict)
            and isinstance(frequency.get("impedance_real_ohm"), (int, float))
            and frequency["impedance_real_ohm"] <= 0.0
        ]
        if not negative:
            continue
        diagnostics = result.setdefault("diagnostics", [])
        if not isinstance(diagnostics, list):
            continue
        if any(
            isinstance(diagnostic, dict)
            and diagnostic.get("code") == "normalization.negative_resistance"
            for diagnostic in diagnostics
        ):
            continue
        all_negative = len(negative) == len(frequencies)
        diagnostics.append(
            {
                "code": "normalization.negative_resistance",
                "severity": "error" if all_negative else "warning",
                "message": (
                    "negative input resistance: the passive antenna model is invalid; "
                    "check the radial height and ground model. Far-field gains are unavailable."
                ),
                "field": "impedance",
            }
        )
        result["status"] = "error" if all_negative else "partial"


def _migrate_v7_to_v8(document: dict[str, Any]) -> dict[str, Any]:
    """Add top-hat fields and negative-resistance diagnostics."""

    migrated = copy.deepcopy(document)
    project = migrated.get("project")
    if not isinstance(project, dict):
        return migrated
    _add_negative_resistance_diagnostics(project)
    designs = project.get("designs")
    if not isinstance(designs, list):
        return migrated
    for design in designs:
        if not isinstance(design, dict) or design.get("antenna_type") != "vertical":
            continue
        parameters = design.get("parameters")
        if not isinstance(parameters, dict):
            continue
        antenna = design.get("antenna")
        wires = antenna.get("wires") if isinstance(antenna, dict) else None
        hat_wires = (
            [
                wire
                for wire in wires
                if isinstance(wire, dict) and str(wire.get("id", "")).startswith("top-hat-")
            ]
            if isinstance(wires, list)
            else []
        )
        lengths: list[float] = []
        for wire in hat_wires:
            start = wire.get("start")
            end = wire.get("end")
            if not isinstance(start, dict) or not isinstance(end, dict):
                continue
            try:
                lengths.append(
                    math.hypot(
                        float(end["x_m"]) - float(start["x_m"]),
                        float(end["y_m"]) - float(start["y_m"]),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
        parameters.setdefault("top_hat_enabled", bool(hat_wires))
        parameters.setdefault("top_hat_wire_count", len(hat_wires))
        parameters.setdefault(
            "top_hat_radius_m",
            (sum(lengths) / len(lengths)) if lengths else 0.0,
        )
    return migrated


def _migrate_v8_to_v9(document: dict[str, Any]) -> dict[str, Any]:
    """Introduce the inverted-L design type; existing designs are unchanged."""

    return copy.deepcopy(document)


MIGRATIONS: dict[int, Migration] = {
    1: _migrate_v1_to_v2,
    2: _migrate_v2_to_v3,
    3: _migrate_v3_to_v4,
    4: _migrate_v4_to_v5,
    5: _migrate_v5_to_v6,
    6: _migrate_v6_to_v7,
    7: _migrate_v7_to_v8,
    8: _migrate_v8_to_v9,
}


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
