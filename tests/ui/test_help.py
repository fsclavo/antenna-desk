# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Help-resolution and tooltip application tests."""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QWidget
from pytestqt.qtbot import QtBot

from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.dialogs.balun_loss_dialog import BalunLossDialog
from antennadesk.ui.dialogs.feed_line_dialog import FeedLineDialog
from antennadesk.ui.dialogs.loads_dialog import LoadsDialog
from antennadesk.ui.dialogs.matching_network_dialog import MatchingNetworkDialog
from antennadesk.ui.dialogs.measurement_details_dialog import MeasurementDetailsDialog
from antennadesk.ui.help import apply_form_help, apply_help, help_text
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem
from antennadesk.ui.widgets.dipole_form import DipoleForm
from antennadesk.ui.widgets.form_i18n import FormLabels
from antennadesk.ui.widgets.results_view import ResultsView


def test_help_resolution_order_and_missing_keys() -> None:
    translator = Translator(Language.ENGLISH)

    explicit = help_text(
        translator,
        "field.height",
        explicit_key="help.wire_dipole.field.height",
    )
    family = help_text(translator, "field.height", family="wire_dipole")
    shared = help_text(translator, "field.height")
    yagi_height = help_text(translator, "field.height", family="yagi")
    dipole_spacing = help_text(translator, "field.spacing", family="dipole")
    hint = help_text(translator, "yagi.polarization")
    missing = help_text(translator, "field.unknown")

    assert explicit == family
    assert "horizontal wire" in (explicit or "")
    assert "selected ground model" in (shared or "")
    assert "Boom centerline" in (yagi_height or "")
    assert "folded-dipole" in (dipole_spacing or "")
    assert "polarization" in (hint or "").lower()
    assert missing is None


def test_family_specific_labels_resolve_help() -> None:
    translator = Translator(Language.ENGLISH)

    assert "Termination resistor" in (
        help_text(translator, "beverage.termination_resistance") or ""
    )
    assert "Trap resonant" in (help_text(translator, "trap_dipole.trap_frequency") or "")
    assert "Progressive phase" in (help_text(translator, "phased_vertical.phase_step") or "")
    assert "loading-coil" in (help_text(translator, "endfed.loading_coil_inductance") or "")
    assert "matching line" in (help_text(translator, "g5rv.line_impedance") or "")
    assert "Vertical polarization" in (
        help_text(translator, "field.polarization", family="yagi") or ""
    )


def test_apply_form_help_sets_and_retranslates_label_and_control(
    qtbot: QtBot,
) -> None:
    translator = Translator(Language.ENGLISH)
    parent = QWidget()
    qtbot.addWidget(parent)
    form = QFormLayout(parent)
    label = QLabel(parent)
    label.setObjectName("field.height")
    control = QLineEdit(parent)
    form.addRow(label, control)

    apply_form_help(form, translator)

    assert label.toolTip() == control.toolTip()
    assert label.whatsThis() == label.toolTip()
    assert label.accessibleDescription() == label.toolTip()
    assert "selected ground model" in label.toolTip()

    translator.set_language(Language.SPANISH)
    apply_form_help(form, translator)

    assert "modelo de suelo" in label.toolTip()
    assert label.toolTip() == control.toolTip()


def test_form_labels_sets_family_help_and_refreshes(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    parent = QWidget()
    qtbot.addWidget(parent)
    control = QLineEdit(parent)
    labels = FormLabels(translator, parent, family="wire_dipole")

    label = labels.label("field.height", control)

    assert "horizontal wire" in label.toolTip()
    assert control.toolTip() == label.toolTip()

    translator.set_language(Language.SPANISH)
    labels.retranslate()

    assert "hilo horizontal" in label.toolTip()
    assert control.toolTip() == label.toolTip()


def test_form_labels_binds_controls_from_a_form(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    parent = QWidget()
    qtbot.addWidget(parent)
    form = QFormLayout(parent)
    labels = FormLabels(translator, parent)
    label = labels.label("field.height")
    control = QLineEdit(parent)
    form.addRow(label, control)

    labels.bind_form(form)

    assert "selected ground model" in label.toolTip()
    assert control.toolTip() == label.toolTip()

    control.setEnabled(False)
    labels.retranslate()

    assert "selected ground model" in label.toolTip()


def test_yagi_form_applies_help_to_shared_fields(qtbot: QtBot) -> None:
    from antennadesk.ui.widgets.yagi_form import YagiForm

    form = YagiForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.retranslate()

    labels = {
        label.objectName(): label
        for label in form.findChildren(QLabel)
        if label.objectName().startswith("field.")
    }

    assert "Boom centerline" in labels["field.height"].toolTip()
    assert form._height.toolTip() == labels["field.height"].toolTip()
    assert "Vertical polarization" in form._polarization.toolTip()
    assert "Design frequency" in labels["field.frequency"].toolTip()
    assert form._frequency.toolTip() == labels["field.frequency"].toolTip()


def test_apply_help_clears_a_missing_key_instead_of_showing_it(
    qtbot: QtBot,
) -> None:
    parent = QWidget()
    qtbot.addWidget(parent)
    label = QLabel(parent)
    label.setToolTip("stale")

    apply_help(label, Translator(Language.ENGLISH), "field.unknown")

    assert label.toolTip() == ""
    assert label.whatsThis() == ""
    assert label.accessibleDescription() == ""


def test_main_window_sections_actions_and_tabs_have_help(window) -> None:  # type: ignore[no-untyped-def]
    assert "Antenna type" in window._design_panel.toolTip()
    assert "solver timeout" in window._solver_group.toolTip()
    assert "Frequency range" in window._sweep_group.toolTip()
    assert "Far-field" in window._pattern_group.toolTip()
    assert "amateur bands" in window._band_group.toolTip()
    assert "Dimensioned construction" in window._geometry.toolTip()
    assert "EFHW" in window._feed_matching_summary.toolTip()
    assert "amateur bands" in window._analyze_bands_action.toolTip()
    assert "form values" in window._apply_button.toolTip()
    assert "family optimizer" in window._optimize_button.toolTip()
    assert "recommendation" in window._workflow_panel.toolTip()
    assert "Advanced" in window._workflow_combo.toolTip()
    assert "profile" in window._installation_label.toolTip()
    assert "installation profile" in window._installation_edit.toolTip().lower()
    assert "shortlist" in window._advisor_action.toolTip()
    assert "feed-chain" in window._feed_chain_action.toolTip()
    assert "as-built" in window._construction_record_action.toolTip().lower()
    assert "calculators" in window._calculator_action.toolTip().lower()

    tabs = window._results._tabs
    impedance = tabs.indexOf(window._results._impedance_tab)
    pattern = tabs.indexOf(window._results._pattern_tab)
    assert "Impedance" in tabs.tabToolTip(impedance)
    assert "radiation" in tabs.tabToolTip(pattern)

    window._set_language(Language.SPANISH)
    assert "Tiempo límite" in window._solver_group.toolTip()
    assert "bandas" in window._analyze_bands_action.toolTip()
    assert "Recomendación" in window._workflow_panel.toolTip()
    assert "perfil" in window._installation_label.toolTip().lower()
    assert "preselección" in window._advisor_action.toolTip()
    assert "cadena" in window._feed_chain_action.toolTip()
    assert "as-built" in window._construction_record_action.toolTip().lower()
    assert "calculadoras" in window._calculator_action.toolTip().lower()


def test_feed_line_dialog_applies_row_help(qtbot: QtBot) -> None:
    dialog = FeedLineDialog(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(dialog)

    assert "Characteristic impedance" in dialog._label_impedance.toolTip()
    assert dialog._impedance.toolTip() == dialog._label_impedance.toolTip()
    assert "feed-line length" in dialog._length.toolTip()


def test_balun_loss_dialog_applies_row_help(qtbot: QtBot) -> None:
    dialog = BalunLossDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)

    assert "reference insertion loss" in dialog._reference_frequency.toolTip()
    assert "insertion loss" in dialog._reference_loss.toolTip()
    assert "exponent" in dialog._exponent.toolTip()


def test_loads_dialog_applies_row_help(qtbot: QtBot) -> None:
    dialog = LoadsDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        {"radiator": 20.0},
        (),
    )
    qtbot.addWidget(dialog)

    assert "Distance" in dialog._offset.toolTip()
    assert "resistance" in dialog._resistance.toolTip()
    assert "trap" in dialog._trap_frequency.toolTip()


def test_matching_network_dialog_applies_row_help(qtbot: QtBot) -> None:
    dialog = MatchingNetworkDialog(Translator(Language.ENGLISH))
    qtbot.addWidget(dialog)

    assert "topology" in dialog._topology.toolTip().lower()
    assert "reactance" in dialog._load_x.toolTip().lower()
    assert "Shunt" in dialog._input_shunt_l.toolTip()
    assert "source impedance" in dialog._source_impedance.toolTip().lower()
    assert "simulation" in dialog._use_current_point.toolTip().lower()


def test_measurement_details_dialog_applies_help(qtbot: QtBot) -> None:
    dialog = MeasurementDetailsDialog(Translator(Language.ENGLISH), "run")
    qtbot.addWidget(dialog)

    assert "Calibration" in dialog._calibration.toolTip()
    assert "reference plane" in dialog._reference_plane.toolTip().lower()
    assert "notes" in dialog._notes.toolTip().lower()


def test_whats_this_action_enters_qt_mode(
    window,  # type: ignore[no-untyped-def]
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    calls: list[bool] = []
    monkeypatch.setattr(
        main_window_module.QWhatsThis,
        "enterWhatsThisMode",
        lambda: calls.append(True),
    )

    window._whats_this_action.trigger()

    assert calls == [True]
    assert window._whats_this_action.shortcut().toString() == "Shift+F1"


def test_results_view_exposes_help_and_accessibility(qtbot: QtBot) -> None:
    translator = Translator(Language.ENGLISH)
    view = ResultsView(translator)
    qtbot.addWidget(view)

    assert "Resistance" in view._impedance_plot.toolTip()
    assert view._impedance_plot.whatsThis() == view._impedance_plot.toolTip()
    assert view._impedance_plot.accessibleDescription() == view._impedance_plot.toolTip()
    assert "Frequency" in view._table.horizontalHeader().toolTip()
    assert "band" in view._band_selector.toolTip().lower()
    assert "Evidence" in view._confidence_group.toolTip()
    assert "topic" in view._confidence_topic.toolTip().lower()
    assert view._pattern_view_tabs.accessibleDescription()
    assert view._raw_tabs.accessibleDescription()

    translator.set_language(Language.SPANISH)
    view.retranslate()

    assert "Resistencia" in view._impedance_plot.toolTip()
    assert "Evidencia" in view._confidence_group.toolTip()


def test_dipole_form_applies_help_to_its_labels_and_controls(qtbot: QtBot) -> None:
    form = DipoleForm(Translator(Language.ENGLISH), UnitSystem.METRIC)
    qtbot.addWidget(form)
    form.retranslate()

    labels = {
        label.objectName(): label
        for label in form.findChildren(QLabel)
        if label.objectName().startswith("field.")
    }

    assert "Design frequency" in labels["field.frequency"].toolTip()
    assert form._frequency.toolTip() == labels["field.frequency"].toolTip()
    assert "selected ground model" in labels["field.height"].toolTip()
    assert form._height.toolTip() == labels["field.height"].toolTip()
    assert "folded-dipole" in form._spacing.toolTip()
    assert "frequency sweep" in form._sweep.toolTip()
    assert "custom sweep" in form._sweep_start.toolTip()
    assert "custom sweep" in form._sweep_stop.toolTip()
