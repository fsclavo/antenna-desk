# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""End-fed editor override state and project-network actions."""

from __future__ import annotations

from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.endfed import shortened_efhw_80_10_parameters
from antennadesk.domain.antennas.matching_network import LNetwork
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.endfed_form import EndFedForm


def _project_network() -> LNetwork:
    return LNetwork(series_inductance_h=1e-6, shunt_capacitance_f=100e-12)


def test_endfed_form_marks_internal_matching_inactive_under_override(
    qtbot: QtBot,
) -> None:
    form = EndFedForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.set_parameters(shortened_efhw_80_10_parameters())
    form.set_project_matching_network(_project_network())

    assert form._matching_override_widget.isHidden() is False
    assert "retained but inactive" in form._matching_override.text()
    assert form._matching_capacitance.isEnabled() is False
    assert form._transformer_leakage.isEnabled() is False
    assert form._matching_override_actions.isHidden() is False


def test_endfed_form_restores_internal_matching_when_the_override_is_removed(
    qtbot: QtBot,
) -> None:
    form = EndFedForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.set_parameters(shortened_efhw_80_10_parameters())
    form.set_project_matching_network(_project_network())
    form.set_project_matching_network(None)

    assert form._matching_override_widget.isHidden() is True
    assert form._matching_capacitance.isEnabled() is True
    assert form._transformer_leakage.isEnabled() is True


def test_endfed_form_emits_project_network_actions(qtbot: QtBot) -> None:
    form = EndFedForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.set_parameters(shortened_efhw_80_10_parameters())
    form.set_project_matching_network(_project_network())
    emitted: list[str] = []
    form.matching_network_edit_requested.connect(lambda: emitted.append("edit"))
    form.matching_network_remove_requested.connect(lambda: emitted.append("remove"))

    form._matching_override_edit.click()
    form._matching_override_remove.click()

    assert emitted == ["edit", "remove"]


def test_endfed_form_can_hide_the_project_network_actions(qtbot: QtBot) -> None:
    form = EndFedForm(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        show_override_actions=False,
    )
    qtbot.addWidget(form)
    form.set_parameters(shortened_efhw_80_10_parameters())
    form.set_project_matching_network(_project_network())

    assert form._matching_override_widget.isHidden() is False
    assert form._matching_override_actions.isHidden() is True


def test_endfed_form_retranslates_the_override_note(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    form = EndFedForm(translator, UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.set_parameters(shortened_efhw_80_10_parameters())
    form.set_project_matching_network(_project_network())

    assert "retained but inactive" in form._matching_override.text()

    translator.set_language(Language.SPANISH)
    form.retranslate()

    assert "se retienen pero están inactivos" in form._matching_override.text()
    assert form._matching_override_edit.text() == "Editar red del proyecto..."
    assert form._matching_override_remove.text() == "Quitar red del proyecto"
