# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.report_pdf import write_report_pdf


def _result() -> SimulationResult:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.sweep(6_900_000.0, 7_100_000.0, 3))
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(
            FrequencyResult(6_900_000.0, 1, 11, complex(60.0, -10.0), 2.0, 0.001),
            FrequencyResult(7_000_000.0, 1, 11, complex(65.0, 0.0), 1.5, 0.001),
            FrequencyResult(7_100_000.0, 1, 11, complex(70.0, 10.0), 2.0, 0.001),
        ),
    )


def test_report_pdf_is_written(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "report.pdf"

    write_report_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        _result(),
        path,
    )

    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 2_000
