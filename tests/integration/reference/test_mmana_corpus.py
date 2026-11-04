# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Structural and simulation checks over the curated MMANA reference corpus.

The corpus is copyrighted and gitignored; the committed manifest lists the
curated files and their checksums. These tests skip when the corpus is absent,
so CI runs them only where the data has been provisioned. They are structural
regression evidence, not an independent numerical validation.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pytest

from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import SimulationStatus
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.importers.mmana import parse_mmana_file
from antennadesk.simulation.nec2.solver import Nec2cSolver

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = REPO_ROOT / "reference_data.manifest.json"
CORPUS = REPO_ROOT / "reference_data"

if not MANIFEST.is_file() or not CORPUS.is_dir():
    pytest.skip("reference corpus is not available", allow_module_level=True)

ENTRIES = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
CASES = [pytest.param(entry["path"], id=Path(entry["path"]).stem) for entry in ENTRIES]

NEC2C = os.environ.get("NEC2C")
requires_solver = pytest.mark.skipif(
    not NEC2C or not Path(NEC2C).is_file(),
    reason="NEC2C must point to a nec2c executable",
)


def _parameters(relative_path: str):
    path = CORPUS / relative_path
    text = path.read_text(encoding="cp1251", errors="replace")
    return parse_mmana_file(text).parameters


@pytest.mark.parametrize("relative_path", CASES)
def test_reference_model_imports(relative_path: str) -> None:
    parameters = _parameters(relative_path)

    assert parameters.wires
    assert parameters.frequency_hz > 0.0
    assert any(wire.id == parameters.feed.wire_id for wire in parameters.wires)


@pytest.mark.parametrize("relative_path", CASES)
@pytest.mark.solver
@pytest.mark.science
@requires_solver
def test_reference_model_simulates(relative_path: str) -> None:
    assert NEC2C is not None
    parameters = _parameters(relative_path)
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(parameters.frequency_hz),
        segmentation=SegmentationPolicy(target_segment_length_wavelengths=0.05),
        far_field=FarFieldRequest(
            enabled=True,
            theta_count=19,
            phi_start_deg=0.0,
            phi_stop_deg=360.0,
            phi_count=37,
        ),
    )

    result = Nec2cSolver(Path(NEC2C)).run(parameters.to_antenna(), spec)

    assert result.status is SimulationStatus.COMPLETED
    impedance = result.frequencies[0].impedance_ohm
    assert math.isfinite(impedance.real) and impedance.real > 0.0
    assert result.max_total_gain_db is not None
    assert math.isfinite(result.max_total_gain_db)
