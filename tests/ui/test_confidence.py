# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Result confidence card and contextual explanations."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.projects.project import Project
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.widgets.results_view import CONFIDENCE_TOPICS, ResultsView


def test_confidence_card_shows_evidence_and_limitations(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_design(sample_project.designs[0])

    text = view._confidence_evidence.text()
    assert "Evidence level" in text
    assert "Modeled:" in text
    assert "Dominant uncertainties:" in text
    assert view._confidence_topic.isEnabled() is True


def test_shortened_endfed_confidence_marks_swr_informational(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_40_10_parameters

    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    design = sample_project.designs[0].with_parameters(shortened_efhw_40_10_parameters())
    view.set_design(design)

    text = view._confidence_evidence.text()
    assert "Model confidence" in text
    assert "Absolute SWR is informational" in text
    assert "installation return" in text


def test_confidence_topic_switches_the_explanation(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)
    view.set_design(sample_project.designs[0])

    index = CONFIDENCE_TOPICS.index("impedance")
    view._confidence_topic.setCurrentIndex(index)

    assert "resistive part" in view._confidence_explanation.text()


def test_confidence_card_handles_no_design(qtbot: QtBot) -> None:
    view = ResultsView(Translator(Language.ENGLISH))
    qtbot.addWidget(view)

    view.set_design(None)

    assert "Select a design" in view._confidence_evidence.text()
    assert view._confidence_topic.isEnabled() is False
    assert view._confidence_explanation.text() == ""


def test_confidence_card_retranslates(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    view = ResultsView(Translator(Language.SPANISH))
    qtbot.addWidget(view)
    view.set_design(sample_project.designs[0])

    assert "Nivel de evidencia" in view._confidence_evidence.text()
    assert view._confidence_group.title() == "Confianza del resultado"
    assert view._confidence_topic.itemText(0) == "Impedancia"


def test_shortened_endfed_confidence_retranslates(
    qtbot: QtBot,
    sample_project: Project,
) -> None:
    from antennadesk.domain.antennas.endfed import shortened_efhw_40_10_parameters

    view = ResultsView(Translator(Language.SPANISH))
    qtbot.addWidget(view)
    design = sample_project.designs[0].with_parameters(shortened_efhw_40_10_parameters())
    view.set_design(design)

    text = view._confidence_evidence.text()
    assert "Confianza del modelo" in text
    assert "ROE absoluta es informativa" in text
    assert "contrapeso físico" in text
