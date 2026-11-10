# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Report localization stays Qt-free and covers every static label."""

from __future__ import annotations

import ast
import re
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from string import Formatter

from antennadesk.domain.common.validation import Diagnostic, Severity
from antennadesk.domain.design.evidence import EVIDENCE
from antennadesk.domain.projects.project import Project
from antennadesk.domain.simulation.frequency import FrequencyPlan
from antennadesk.domain.simulation.result import (
    FrequencyResult,
    SimulationResult,
    SimulationStatus,
)
from antennadesk.domain.simulation.solver import SolverMetadata
from antennadesk.domain.simulation.spec import SimulationSpec
from antennadesk.reporting.construction_sheet import render_construction_sheet
from antennadesk.reporting.html_report import render_html_report
from antennadesk.reporting.localization import (
    identity_labeler,
    localize_html_labels,
    localize_rows,
)
from antennadesk.ui.evidence_i18n import EVIDENCE_SPANISH
from antennadesk.ui.i18n import _TRANSLATIONS, Language, Translator
from antennadesk.ui.report_i18n import REPORT_SPANISH

REPORTING_ROOT = Path(__file__).resolve().parents[3] / "src" / "antennadesk" / "reporting"


def _result() -> SimulationResult:
    spec = SimulationSpec(frequency_plan=FrequencyPlan.single(7_100_000.0))
    frequency = FrequencyResult(
        frequency_hz=7_100_000.0,
        feed_tag=1,
        feed_segment=11,
        impedance_ohm=complex(50.0, 0.0),
        swr=1.0,
        input_power_w=0.001,
    )
    return SimulationResult(
        status=SimulationStatus.COMPLETED,
        spec=spec,
        model_fingerprint="a" * 64,
        solver=SolverMetadata(name="nec2c", version="1.3.3"),
        frequencies=(frequency,),
        duration_s=0.1,
        started_at=datetime(2026, 10, 29, tzinfo=UTC),
        finished_at=datetime(2026, 10, 29, tzinfo=UTC),
    )


def _fields(text: str) -> set[str]:
    return {name for _, name, _, _ in Formatter().parse(text) if name}


def _catalog_keys() -> list[str]:
    catalog = REPORTING_ROOT.parent / "ui" / "report_i18n.py"
    tree = ast.parse(catalog.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.AnnAssign):
            continue
        target = node.target
        if isinstance(target, ast.Name) and target.id == "REPORT_SPANISH":
            assert isinstance(node.value, ast.Dict)
            return [key.value for key in node.value.keys if isinstance(key, ast.Constant)]
    raise AssertionError("REPORT_SPANISH assignment not found")


def test_report_catalog_has_no_duplicate_or_blank_entries() -> None:
    keys = _catalog_keys()
    assert len(keys) == len(set(keys))
    assert all(value.strip() for value in REPORT_SPANISH.values())


def test_report_catalog_placeholders_match_the_english_source() -> None:
    for source, translation in REPORT_SPANISH.items():
        assert _fields(source) == _fields(translation), source


def test_every_static_report_label_has_a_spanish_translation() -> None:
    missing: list[tuple[str, str]] = []
    for path in sorted(REPORTING_ROOT.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            index = {"tr": 0, "_note": 1}.get(node.func.id)
            if index is None or len(node.args) <= index:
                continue
            argument = node.args[index]
            if (
                isinstance(argument, ast.Constant)
                and isinstance(argument.value, str)
                and argument.value not in REPORT_SPANISH
            ):
                missing.append((path.name, argument.value))
    assert not missing, missing


def test_every_diagnostic_code_has_a_translation() -> None:
    codes: set[str] = set()
    for path in REPORTING_ROOT.parent.rglob("*.py"):
        codes.update(
            match.group(1)
            for match in re.finditer(r'code="([^"]+)"', path.read_text(encoding="utf-8"))
        )
    missing = sorted(code for code in codes if f"diagnostic.{code}" not in _TRANSLATIONS)
    assert not missing, missing


def test_every_evidence_field_has_a_spanish_translation() -> None:
    missing: list[str] = []
    for template in EVIDENCE:
        translation = EVIDENCE_SPANISH.get(template)
        if translation is None:
            missing.append(template)
            continue
        for field in ("source", "tolerance", "limitation"):
            if not translation.get(field, "").strip():
                missing.append(f"{template}.{field}")
    assert not missing, missing


def test_translator_report_translates_diagnostic_and_evidence_keys() -> None:
    spanish = Translator(Language.SPANISH)
    english = Translator(Language.ENGLISH)

    assert spanish.report("diagnostic.solver.timeout") == "El solver agotó el tiempo de espera."
    assert english.report("diagnostic.solver.timeout") == "diagnostic.solver.timeout"
    assert "Solo espacio libre" in spanish.report("evidence.wire_dipole.limitation")
    assert english.report("evidence.wire_dipole.limitation") == "evidence.wire_dipole.limitation"


def test_translator_report_translates_and_falls_back() -> None:
    spanish = Translator(Language.SPANISH)
    english = Translator(Language.ENGLISH)

    assert spanish.report("Wire schedule") == "Lista de hilos"
    assert english.report("Wire schedule") == "Wire schedule"
    assert spanish.report("not a catalog label") == "not a catalog label"
    assert spanish.report("Load {index} ({kind})", index=2, kind="serie") == "Carga 2 (serie)"


def test_localize_rows_translates_labels_and_values() -> None:
    rows = (("Type", "custom wires"), ("Length", "10.0000 m"))
    localized = localize_rows(rows, Translator(Language.SPANISH).report)

    assert localized == (("Tipo", "hilos personalizados"), ("Longitud", "10.0000 m"))


def test_localize_html_labels_only_touches_structural_text() -> None:
    markup = (
        "<h2>Wire schedule</h2><table><tr><th>Wire</th><td>driven</td></tr></table>"
        "<figcaption>Construction view</figcaption>"
    )
    localized = localize_html_labels(markup, Translator(Language.SPANISH).report)

    assert "<h2>Lista de hilos</h2>" in localized
    assert "<th>Hilo</th>" in localized
    assert "<td>driven</td>" in localized
    assert "<figcaption>Vista de construcción</figcaption>" in localized


def test_identity_labeler_formats_placeholders() -> None:
    assert identity_labeler("{count} segments", count=3) == "3 segments"


def test_spanish_construction_sheet_translates_structure_and_notes(
    sample_project: Project,
) -> None:
    design = sample_project.designs[0]
    sheet = render_construction_sheet(
        sample_project,
        design,
        None,
        labeler=Translator(Language.SPANISH).report,
        language="es",
    )

    assert '<html lang="es">' in sheet
    assert "<h2>Dimensiones</h2>" in sheet
    assert "<h2>Lista de hilos</h2>" in sheet
    assert "<h2>Lista de materiales</h2>" in sheet
    assert "<h2>Evidencia y limitaciones</h2>" in sheet
    assert "<h2>Notas de construcción</h2>" in sheet
    assert "<th>Longitud total del hilo</th>" in sheet
    assert "Cortá los dos tramos" in sheet
    assert "Recortá y volvé a medir" in sheet
    assert "Solo espacio libre y los casos de suelo publicados." in sheet
    assert "Free-space and the published ground cases only." not in sheet
    assert "Wire schedule" not in sheet
    assert "Construction notes" not in sheet
    # User data and canonical identifiers are not translated.
    assert sample_project.name in sheet
    assert design.antenna.wires[0].id in sheet


def test_spanish_construction_sheet_translates_view_captions(
    sample_project: Project,
) -> None:
    sheet = render_construction_sheet(
        sample_project,
        sample_project.designs[0],
        None,
        figure_png_data_uri="data:image/png;base64,AAAA",
        auxiliary_png_data_uri="data:image/png;base64,BBBB",
        isometric_png_data_uri="data:image/png;base64,CCCC",
        labeler=Translator(Language.SPANISH).report,
        language="es",
    )

    assert "Vista de construcción" in sheet
    assert "Vista de instalación (frontal)" in sheet
    assert "Vista isométrica" in sheet


def test_english_construction_sheet_stays_english(sample_project: Project) -> None:
    sheet = render_construction_sheet(
        sample_project,
        sample_project.designs[0],
        None,
        labeler=Translator(Language.ENGLISH).report,
        language="en",
    )

    assert '<html lang="en">' in sheet
    assert "<h2>Wire schedule</h2>" in sheet
    assert "Cut the two legs" in sheet


def test_spanish_html_report_translates_diagnostics(
    sample_project: Project,
) -> None:
    result = replace(
        _result(),
        diagnostics=(
            Diagnostic(
                code="solver.timeout",
                severity=Severity.ERROR,
                message="NEC2C timed out after 180 s",
            ),
        ),
    )
    report = render_html_report(
        sample_project,
        sample_project.designs[0],
        result,
        labeler=Translator(Language.SPANISH).report,
        language="es",
    )

    assert "El solver agotó el tiempo de espera." in report
    assert "NEC2C timed out after 180 s" not in report


def test_unknown_diagnostic_falls_back_to_the_domain_message(
    sample_project: Project,
) -> None:
    result = replace(
        _result(),
        diagnostics=(
            Diagnostic(
                code="custom.unknown",
                severity=Severity.WARNING,
                message="preserve this technical detail",
            ),
        ),
    )
    report = render_html_report(
        sample_project,
        sample_project.designs[0],
        result,
        labeler=Translator(Language.SPANISH).report,
        language="es",
    )

    assert "preserve this technical detail" in report


def test_spanish_html_report_translates_headings_and_headers(
    sample_project: Project,
) -> None:
    report = render_html_report(
        sample_project,
        sample_project.designs[0],
        _result(),
        labeler=Translator(Language.SPANISH).report,
        language="es",
    )

    assert '<html lang="es">' in report
    assert "<h2>Diseño</h2>" in report
    assert "<h2>Configuración de la simulación</h2>" in report
    assert "<h2>Impedancia</h2>" in report
    assert "<h2>Diagnósticos</h2>" in report
    assert "<th>Frecuencia (MHz)</th>" in report
    assert "<th>ROE</th>" in report
    assert "Segmentación" in report
    assert "habilitado" in report
    assert "Informe de simulación de AntennaDesk" in report
    assert sample_project.name in report
