# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exported decks run in the real engine and reproduce the simulation impedance."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.simulation.far_field import FarFieldRequest
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.segmentation import SegmentationPolicy
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.simulation.nec2.export import NecDeckExportMetadata, render_nec_deck
from antennadesk.simulation.nec2.parser import parse_nec2_output
from antennadesk.simulation.nec2.solver import Nec2cSolver

NEC2C = os.environ.get("NEC2C")
pytestmark = [
    pytest.mark.solver,
    pytest.mark.science,
    pytest.mark.skipif(
        not NEC2C or not Path(NEC2C).is_file(),
        reason="NEC2C must point to a nec2c executable",
    ),
]


def test_exported_deck_reproduces_the_solver_impedance(tmp_path: Path) -> None:
    assert NEC2C is not None
    model = DipoleParameters(
        frequency_hz=7_100_000.0,
        total_length_m=20.0,
        height_m=8.0,
    ).to_antenna(name="40 m dipole")
    spec = SimulationSpec(
        frequency_plan=FrequencyPlan.single(7_100_000.0),
        segmentation=SegmentationPolicy(min_segments_per_wire=5),
        far_field=FarFieldRequest(enabled=False),
    )
    text = render_nec_deck(
        model,
        spec,
        NecDeckExportMetadata(
            project_name="Export test",
            design_name="Dipole",
            antenna_type="wire_dipole",
            app_version="0.9.0",
            solver_name="nec2c",
            solver_version="test",
        ),
    )
    deck_path = tmp_path / "in.nec"
    output_path = tmp_path / "out.out"
    deck_path.write_text(text, encoding="utf-8")

    completed = subprocess.run(  # noqa: S603 - configured test executable, no shell
        [str(Path(NEC2C).resolve()), "-i", deck_path.name, "-o", output_path.name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    parsed = parse_nec2_output(output_path.read_text(encoding="utf-8"))
    expected = Nec2cSolver(Path(NEC2C)).run(model, spec).frequencies[0].impedance_ohm

    assert parsed.frequencies
    actual = parsed.frequencies[0].input_parameters[0].impedance_ohm
    assert actual.real == pytest.approx(expected.real, rel=1e-6)
    assert actual.imag == pytest.approx(expected.imag, rel=1e-6)
