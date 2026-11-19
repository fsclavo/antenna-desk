# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FarFieldPoint,
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.reporting.localization import Labeler
from antennadesk.reporting.pattern_lobe import PatternLobe
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


def _pattern_result() -> SimulationResult:
    points = (
        FarFieldPoint(0.0, 0.0, 2.1, None, 2.1, 0.0, 0.0, "LINEAR", None, None, None, None),
        FarFieldPoint(0.0, 90.0, 1.8, None, 1.8, 0.0, 0.0, "LINEAR", None, None, None, None),
        FarFieldPoint(90.0, 0.0, -4.0, None, -4.0, 0.0, 0.0, None, None, None, None, None),
        FarFieldPoint(90.0, 90.0, -6.0, None, -6.0, 0.0, 0.0, None, None, None, None, None),
    )
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(
            FrequencyResult(
                7_100_000.0,
                1,
                11,
                complex(70.0, 10.0),
                2.0,
                0.001,
                far_field=points,
            ),
        ),
    )


def test_report_pdf_includes_geometry_and_pattern_cuts(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "pattern-report.pdf"
    geometry_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<line x1="0" y1="0" x2="10" y2="10"/></svg>'
    )

    write_report_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        _pattern_result(),
        path,
        geometry_svg=geometry_svg,
    )

    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert b"/Subtype /Image" not in data


def test_report_pdf_includes_the_3d_pattern_figure(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.ui import report_pdf

    calls: list[bool] = []
    real = report_pdf.pattern_lobe

    def spy(
        frequency: FrequencyResult,
        tr: Labeler,
        *,
        ground: bool,
    ) -> PatternLobe:
        calls.append(ground)
        return real(frequency, tr, ground=ground)

    monkeypatch.setattr(report_pdf, "pattern_lobe", spy)
    path = tmp_path / "pattern-3d-report.pdf"

    write_report_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        _pattern_result(),
        path,
    )

    data = path.read_bytes()
    assert calls
    assert data.startswith(b"%PDF")
    assert b"/Subtype /Image" not in data


def test_report_pdf_can_omit_the_3d_pattern_figure(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.ui import report_pdf

    calls: list[bool] = []

    def spy(
        frequency: FrequencyResult,
        tr: Labeler,
        *,
        ground: bool,
    ) -> PatternLobe:
        calls.append(ground)
        return report_pdf.pattern_lobe(frequency, tr, ground=ground)

    monkeypatch.setattr(report_pdf, "pattern_lobe", spy)
    path = tmp_path / "pattern-3d-off.pdf"

    write_report_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        _pattern_result(),
        path,
        include_pattern_lobe=False,
    )

    data = path.read_bytes()
    assert calls == []
    assert data.startswith(b"%PDF")
    assert b"/Subtype /Image" not in data


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


def test_report_pdf_charts_are_vector(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "vector-report.pdf"

    write_report_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        _result(),
        path,
    )

    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert b"/Subtype /Image" not in data


def test_report_pdf_is_written_in_spanish(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    path = tmp_path / "informe.pdf"

    write_report_pdf(
        Translator(Language.SPANISH),
        sample_project,
        sample_project.designs[0],
        _result(),
        path,
    )

    data = path.read_bytes()
    assert data.startswith(b"%PDF")
    assert len(data) > 2_000


def test_report_pdf_includes_a_band_summary(
    qtbot: QtBot,
    sample_project: Project,
    tmp_path: Path,
) -> None:
    from datetime import UTC, datetime
    from uuid import uuid4

    from antennadesk.domain.simulation.band_result import BandAnalysisResult, BandResult
    from antennadesk.domain.simulation.bands import amateur_band_by_id

    band = amateur_band_by_id("40m")
    assert band is not None
    analysis = BandAnalysisResult(
        design_id=sample_project.designs[0].id,
        batch_id=uuid4(),
        created_at=datetime(2026, 11, 3, tzinfo=UTC),
        bands=(BandResult(band=band, result=_result()),),
    )
    path = tmp_path / "band-report.pdf"

    write_report_pdf(
        Translator(Language.ENGLISH),
        sample_project,
        sample_project.designs[0],
        _result(),
        path,
        band_analysis=analysis,
    )

    assert path.read_bytes().startswith(b"%PDF")
