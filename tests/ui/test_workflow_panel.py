# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Guided workflow mode and next-step panel integration."""

from __future__ import annotations

from dataclasses import replace

from main_window_support import FakeSolver
from pytestqt.qtbot import QtBot

from antennadesk.persistence.json_repository import JsonProjectRepository
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.workflow import NextStepKind, WorkflowMode


def test_next_step_starts_with_a_simulation(window: MainWindow) -> None:
    step = window._workflow_panel.step

    assert step is not None
    assert step.kind is NextStepKind.SIMULATE


def test_guided_mode_hides_advanced_actions(window: MainWindow) -> None:
    window._set_workflow_mode(WorkflowMode.GUIDED)

    assert window._advanced_toggle.isHidden()
    assert window._advanced_body.isHidden()
    assert window._optimize_button.isHidden()
    assert not window._optimize_action.isVisible()
    assert not window._loads_action.isVisible()
    assert not window._feed_line_action.isVisible()
    assert not window._matching_network_action.isVisible()
    assert window._feed_matching_summary.isHidden()
    assert not window._import_nec_action.isVisible()
    assert not window._import_separator.isVisible()
    assert not window._simulation_feed_separator.isVisible()
    assert not window._workflow_panel.isHidden()


def test_standard_mode_restores_the_full_editor(window: MainWindow) -> None:
    window._set_workflow_mode(WorkflowMode.STANDARD)

    assert not window._advanced_toggle.isHidden()
    assert window._advanced_body.isHidden()
    assert not window._optimize_button.isHidden()
    assert window._loads_action.isVisible()
    assert window._feed_line_action.isVisible()
    assert not window._feed_matching_summary.isHidden()
    assert not window._workflow_panel.isHidden()


def test_advanced_mode_expands_the_advanced_panel(window: MainWindow) -> None:
    window._set_workflow_mode(WorkflowMode.ADVANCED)

    assert window._advanced_toggle.isChecked()
    assert not window._advanced_body.isHidden()
    assert window._workflow_panel.isHidden()


def test_workflow_mode_persists_across_windows(qtbot: QtBot, window: MainWindow) -> None:
    store = window._preferences
    window._set_workflow_mode(WorkflowMode.GUIDED)

    assert store.load().workflow_mode is WorkflowMode.GUIDED

    reopened = MainWindow(
        JsonProjectRepository(),
        FakeSolver(),
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        preferences=store,
    )
    qtbot.addWidget(reopened)

    assert reopened._workflow_mode is WorkflowMode.GUIDED
    reopened.close()


def test_next_step_panel_retranslates(window: MainWindow) -> None:
    window._set_language(Language.SPANISH)

    spanish = Translator(Language.SPANISH)
    assert window._workflow_panel._title.text() == spanish.t("workflow.panel_title")
    assert window._workflow_panel._body.text() == spanish.t("workflow.next.simulate.body")
    assert window._workflow_panel._action.text() == spanish.t("workflow.next.simulate.action")

    window._set_language(Language.ENGLISH)

    english = Translator(Language.ENGLISH)
    assert window._workflow_panel._title.text() == english.t("workflow.panel_title")
    assert window._workflow_panel._action.text() == english.t("workflow.next.simulate.action")


def test_high_swr_review_advances_the_coach(window: MainWindow) -> None:
    assert window._project is not None
    assert window._design_id is not None
    design = window._project.design_by_id(window._design_id)
    result = FakeSolver().run(design.antenna, window._base_simulation_spec(design))
    high_swr = replace(
        result,
        frequencies=(replace(result.frequencies[0], swr=3.0),),
    )
    window._simulation_results[window._design_id] = high_swr
    window._last_result = high_swr
    window._results.set_result(high_swr)
    window._update_workflow_ui()

    assert window._workflow_panel.step is not None
    assert window._workflow_panel.step.kind is NextStepKind.REVIEW_SWR

    window._on_next_step_action(NextStepKind.REVIEW_SWR)

    assert window._workflow_panel.step is not None
    assert window._workflow_panel.step.kind is NextStepKind.BUILD_SHEET


def test_settings_persist_workflow_mode(qtbot: QtBot, window: MainWindow) -> None:
    window._set_workflow_mode(WorkflowMode.ADVANCED)

    saved = window._current_preferences()

    assert saved.workflow_mode is WorkflowMode.ADVANCED
    assert window._preferences.load() == saved
