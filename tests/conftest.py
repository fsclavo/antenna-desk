# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import gc
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from datetime import UTC, datetime
from uuid import UUID

import pytest

from antennadesk.application.use_cases.create_dipole_project import (
    CreateDipoleProject,
    CreateDipoleProjectCommand,
)
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.environment.ground import GroundModel
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.json_repository import JsonProjectRepository

# Make the local Phase 0 build discoverable without an explicit environment
# variable, so `uv run pytest` exercises the solver tests instead of silently
# skipping them.  CI still sets NEC2C explicitly.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_LOCAL_SOLVER_CANDIDATES = (
    _REPO_ROOT / "spikes" / "phase0" / "build" / "nec2c",
    _REPO_ROOT / "spikes" / "phase0" / "build" / "nec2c.exe",
)
if not os.environ.get("NEC2C"):
    for _candidate in _LOCAL_SOLVER_CANDIDATES:
        if _candidate.is_file():
            os.environ["NEC2C"] = str(_candidate)
            break

PROJECT_ID = UUID("00000000-0000-0000-0000-000000000001")
DESIGN_ID = UUID("00000000-0000-0000-0000-000000000002")
FIXED_NOW = datetime(2026, 10, 29, 12, 0, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def _collect_garbage_after_each_test(request):
    yield
    if "/ui/" not in str(request.node.path):
        return
    from PySide6.QtCore import QEvent
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is not None:
        app.closeAllWindows()
        # ``deleteLater`` only schedules the deletion; it runs when the
        # deferred-delete events are dispatched.  Without this, widgets left
        # behind by a test stay alive and the next test pays for their paint
        # and palette events.
        app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
    gc.collect()


@pytest.fixture
def dipole_parameters() -> DipoleParameters:
    return DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
        azimuth_deg=0.0,
        wire_radius_m=0.001,
        ground=GroundModel.finite(
            relative_permittivity=13.0,
            conductivity_s_per_m=0.005,
        ),
    )


@pytest.fixture
def sample_project(dipole_parameters: DipoleParameters) -> Project:
    return CreateDipoleProject().execute(
        CreateDipoleProjectCommand(
            project_name="40 m dipole",
            variant_name="Initial",
            parameters=dipole_parameters,
            description="Half-wave dipole for the 40 m band.",
        ),
        project_id=PROJECT_ID,
        design_id=DESIGN_ID,
        now=FIXED_NOW,
    )


@pytest.fixture
def repository() -> JsonProjectRepository:
    return JsonProjectRepository()


def pytest_report_header(config: pytest.Config) -> str:
    """Report whether the solver tests will run or skip."""
    solver = os.environ.get("NEC2C")
    if solver and Path(solver).is_file():
        return f"nec2c: {solver}"
    return "nec2c: not found; solver integration tests will skip"
