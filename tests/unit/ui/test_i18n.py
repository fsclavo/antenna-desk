# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Consistency checks for the English/Spanish translation tables.

The UI is maintained in two languages by hand, so these tests guard the
invariants that a missing or malformed entry breaks: every key has both
languages, no entry is blank, placeholders match, and the literal has no
duplicate keys that would silently overwrite a translation.
"""

from __future__ import annotations

import ast
from pathlib import Path
from string import Formatter

from antennadesk.ui import i18n
from antennadesk.ui.i18n import _TRANSLATIONS, Language, Translator


def _fields(formatter: Formatter, text: str) -> set[str]:
    return {name for _, name, _, _ in formatter.parse(text) if name}


def _translation_dict_node() -> ast.Dict:
    tree = ast.parse(Path(i18n.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.AnnAssign):
            continue
        target = node.target
        if isinstance(target, ast.Name) and target.id == "_TRANSLATIONS":
            assert isinstance(node.value, ast.Dict)
            return node.value
    raise AssertionError("_TRANSLATIONS assignment not found")


def test_every_key_has_every_language() -> None:
    expected = set(Language)
    for key, translations in _TRANSLATIONS.items():
        assert set(translations) == expected, key


def test_no_translation_is_blank() -> None:
    for key, translations in _TRANSLATIONS.items():
        for language, text in translations.items():
            assert text.strip(), f"{key} is blank in {language.value}"


def test_placeholders_match_across_languages() -> None:
    formatter = Formatter()
    for key, translations in _TRANSLATIONS.items():
        reference = _fields(formatter, translations[Language.ENGLISH])
        for language, text in translations.items():
            assert _fields(formatter, text) == reference, f"{key} in {language.value}"


def test_translation_literal_has_no_duplicate_keys() -> None:
    node = _translation_dict_node()
    keys = [key.value for key in node.keys if isinstance(key, ast.Constant)]
    duplicates = {key for key in keys if keys.count(key) > 1}
    assert not duplicates, f"duplicate translation keys: {sorted(duplicates)}"


def test_unknown_key_falls_back_to_the_key() -> None:
    assert Translator(Language.SPANISH).t("missing.key") == "missing.key"


def test_optional_returns_none_instead_of_a_raw_key() -> None:
    translator = Translator(Language.SPANISH)

    assert translator.optional("missing.key") is None
    assert translator.optional("help.field.frequency") is not None


def test_every_shared_field_has_english_and_spanish_help() -> None:
    field_keys = {
        "field.antenna_type",
        "field.azimuth",
        "field.base_height",
        "field.circumference",
        "field.conductivity",
        "field.design_frequency",
        "field.diameter",
        "field.element_length",
        "field.family",
        "field.frequency",
        "field.fundamental_frequency",
        "field.ground",
        "field.height",
        "field.length",
        "field.material",
        "field.orientation",
        "field.permittivity",
        "field.polarization",
        "field.primary_dimension",
        "field.project_name",
        "field.reference_impedance",
        "field.sag",
        "field.secondary_dimension",
        "field.sides",
        "field.soil_preset",
        "field.spacing",
        "field.transformer_ratio",
        "field.sweep",
        "field.sweep_enabled",
        "field.sweep_points",
        "field.sweep_start",
        "field.sweep_stop",
        "field.template",
        "field.wire_radius",
    }
    expected = set(Language)

    for key in field_keys:
        translations = _TRANSLATIONS.get(f"help.{key}", {})
        assert set(translations) == expected, key
        assert all(text.strip() for text in translations.values()), key


HELP_MANIFEST = frozenset(
    {
        "help.section.design",
        "help.section.workflow",
        "help.section.installation",
        "help.section.advisor",
        "help.section.solver",
        "help.section.sweep",
        "help.section.pattern",
        "help.section.band",
        "help.section.geometry",
        "help.section.feed_matching",
        "help.tab.design",
        "help.tab.simulation",
        "help.matching_network.position",
        "help.matching_network.source_impedance",
        "help.matching_network.use_current_point",
        "help.mode.guided",
        "help.mode.standard",
        "help.mode.advanced",
        "help.preferences.workflow_mode",
        "help.preferences.theme",
        "help.dipole.field.transformer_ratio",
        "help.yagi.field.transformer_ratio",
        "help.endfed.bend_enabled",
        "help.endfed.bend_vertical",
        "help.results.create_matching_network",
        "help.action.simulate",
        "help.action.next_step",
        "help.action.show_advanced",
        "help.action.installation_profile",
        "help.action.antenna_advisor",
        "help.action.reference_library",
        "help.reference.library.search",
        "help.reference.library.list",
        "help.reference.library.details",
        "help.reference.library.open",
        "help.reference.library.simulate",
        "help.action.feed_chain",
        "help.action.component_calculator",
        "help.component_calculator.coil",
        "help.component_calculator.trap",
        "help.component_calculator.balun",
        "help.component_calculator.conductor",
        "help.component_calculator.choke",
        "help.component_calculator.inductance",
        "help.component_calculator.diameter",
        "help.component_calculator.winding_length",
        "help.component_calculator.turns",
        "help.component_calculator.frequency",
        "help.component_calculator.capacitance",
        "help.component_calculator.turns_ratio",
        "help.component_calculator.impedance_ratio",
        "help.component_calculator.material",
        "help.component_calculator.use",
        "help.component_calculator.calculate",
        "help.loads.calculator",
        "help.action.preflight",
        "help.action.measurement_sessions",
        "help.action.tuning_assistant",
        "help.action.parameter_sweep",
        "help.action.guided_experiments",
        "help.guided.list",
        "help.guided.details",
        "help.guided.start",
        "help.guided.guide",
        "help.action.robustness",
        "help.action.project_journal",
        "help.robustness.variables",
        "help.robustness.tolerance",
        "help.robustness.corners",
        "help.robustness.samples",
        "help.robustness.seed",
        "help.robustness.swr_limit",
        "help.robustness.target",
        "help.robustness.run",
        "help.robustness.cancel",
        "help.robustness.plot",
        "help.robustness.table",
        "help.sweep.axes",
        "help.sweep.variable",
        "help.sweep.metric",
        "help.sweep.target",
        "help.sweep.run",
        "help.sweep.cancel",
        "help.sweep.apply_selected",
        "help.sweep.apply_best",
        "help.sweep.plot",
        "help.sweep.table",
        "help.tuning.measurement",
        "help.tuning.target",
        "help.tuning.current_dimension",
        "help.tuning.max_adjustment",
        "help.tuning.analyze",
        "help.tuning.cancel",
        "help.tuning.apply",
        "help.tuning.table",
        "help.tuning.assumptions",
        "help.measurement.session",
        "help.measurement.uncertainty.title",
        "help.measurement.uncertainty.level",
        "help.measurement.uncertainty.factors",
        "help.measurement.uncertainty.warnings",
        "help.measurement.sessions",
        "help.measurement.compare",
        "help.measurement.tune",
        "help.measurement.session.name",
        "help.measurement.session.date",
        "help.measurement.session.design",
        "help.measurement.session.location",
        "help.measurement.session.conditions",
        "help.measurement.session.notes",
        "help.measurement.sessions.timeline",
        "help.measurement.sessions.details",
        "help.measurement.sessions.table",
        "help.measurement.sessions.new",
        "help.measurement.sessions.edit",
        "help.measurement.sessions.delete",
        "help.measurement.sessions.edit_measurement",
        "help.measurement.sessions.compare",
        "help.measurement.comparison.reference",
        "help.measurement.comparison.before",
        "help.measurement.comparison.after",
        "help.measurement.comparison.summary",
        "help.measurement.comparison.table",
        "help.measurement.comparison.plot",
        "help.preflight.table",
        "help.preflight.status",
        "help.preflight.go_to",
        "help.action.construction_record",
        "help.construction_record.notes",
        "help.construction_record.dimensions",
        "help.construction_record.checklist",
        "help.construction_record.add",
        "help.construction_record.remove",
        "help.feed_chain.path",
        "help.feed_chain.power",
        "help.feed_chain.hint",
        "help.table.feed_chain",
        "help.action.new",
        "help.action.open",
        "help.advisor.bands",
        "help.advisor.height",
        "help.advisor.width",
        "help.advisor.installation",
        "help.advisor.intent",
        "help.advisor.complexity",
        "help.advisor.directionality",
        "help.advisor.tuner",
        "help.advisor.multiband",
        "help.advisor.find",
        "help.advisor.open",
        "help.table.advisor",
        "help.compare.designs",
        "help.compare.start",
        "help.compare.stop",
        "help.compare.points",
        "help.compare.ground",
        "help.compare.reference_height",
        "help.compare.reference_frequency",
        "help.compare.recompute",
        "help.table.comparison",
        "help.confidence.title",
        "help.confidence.topic",
        "help.installation.profiles",
        "help.installation.name",
        "help.installation.available_height",
        "help.installation.available_width",
        "help.installation.orientation",
        "help.installation.support",
        "help.installation.ground",
        "help.installation.notes",
        "help.installation.image_reference",
        "help.installation.add",
        "help.installation.duplicate",
        "help.installation.remove",
        "help.action.analyze_bands",
        "help.action.apply_design",
        "help.action.optimize",
        "help.action.cancel",
        "help.action.export",
        "action.whats_this.tooltip",
        "help.tab.impedance",
        "help.tab.sources",
        "help.tab.pattern",
        "help.tab.currents",
        "help.tab.measurements",
        "help.tab.diagnostics",
        "help.tab.raw",
        "help.tab.bands",
        "help.chart.impedance",
        "help.chart.swr",
        "help.chart.pattern",
        "help.chart.currents",
        "help.chart.measurement",
        "help.table.impedance",
        "help.table.sources",
        "help.table.bands",
        "help.table.measurement",
        "help.table.diagnostics",
        "help.status.progress",
        "help.status.solver",
        "help.status.message",
        "help.band.selector",
        "help.pattern.frequency",
        "help.pattern.mode",
        "help.pattern.cut",
        "help.pattern.metric",
        "help.currents.frequency",
        "help.feed_line.characteristic_impedance",
        "help.balun_loss.reference_frequency",
        "help.loads.offset",
        "help.matching_network.topology",
        "help.transmission_lines.z0",
        "help.optimize.objective",
        "help.synthesis.target_frequency",
        "help.custom.feed_offset",
        "help.measurement.notes",
        "help.yagi.match_type",
        "help.trap_yagi.trap_frequency",
        "help.vertical.radial_system",
        "help.journal.timeline",
        "help.journal.table",
        "help.journal.details",
        "help.journal.new",
        "help.journal.edit",
        "help.journal.delete",
        "help.journal.compare",
        "help.journal.title",
        "help.journal.date",
        "help.journal.kind",
        "help.journal.design",
        "help.journal.body",
        "help.journal.snapshot",
        "help.journal.images",
        "help.journal.image_add",
        "help.journal.image_remove",
        "help.journal.image_open",
        "help.journal.preview",
        "help.journal.comparison.left",
        "help.journal.comparison.right",
        "help.journal.comparison.table",
    }
)


def test_help_coverage_manifest_is_bilingual_and_short() -> None:
    expected = set(Language)

    for key in HELP_MANIFEST:
        translations = _TRANSLATIONS.get(key, {})
        assert set(translations) == expected, key
        for text in translations.values():
            assert text.strip(), key
            assert len(text) <= 240, key


def test_every_help_entry_is_bilingual_and_short() -> None:
    expected = set(Language)

    for key, translations in _TRANSLATIONS.items():
        if not key.startswith("help."):
            continue
        assert set(translations) == expected, key
        for text in translations.values():
            assert text.strip(), key
            assert len(text) <= 240, key
            assert text != key, key


def test_translator_formats_placeholders() -> None:
    text = Translator(Language.ENGLISH).t("app.about", version="1.2.3")
    assert "AntennaDesk 1.2.3" in text
