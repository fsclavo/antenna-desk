# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import replace

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.design import AntennaDesignParameters, antenna_type_for
from antennadesk.domain.antennas.dipole import (
    DipoleOrientation,
    DipoleParameters,
)
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiParameters
from antennadesk.domain.design import DesignIntent, VerticalForm
from antennadesk.domain.design.estimators import estimate_intent
from antennadesk.ui.dialogs.design_from_frequency_dialog import (
    DesignFromFrequencyDialog,
)
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.units import UnitSystem


def _dialog(
    qtbot: QtBot,
    parameters: AntennaDesignParameters,
) -> DesignFromFrequencyDialog:
    dialog = DesignFromFrequencyDialog(
        Translator(Language.ENGLISH),
        UnitSystem.METRIC,
        initial_parameters=parameters,
    )
    qtbot.addWidget(dialog)
    return dialog


def _estimated_parameters(family: str) -> AntennaDesignParameters:
    if family == "t2fd":
        return estimate_intent(
            DesignIntent(
                frequency_hz=7_100_000.0,
                highest_frequency_hz=30_000_000.0,
                antenna_type=family,
            )
        ).parameters
    return estimate_intent(
        DesignIntent(
            frequency_hz=146_000_000.0,
            antenna_type=family,
            fan_bands_hz=(146_000_000.0,),
        )
    ).parameters


def test_dialog_estimates_the_current_dipole_template(qtbot: QtBot) -> None:
    dialog = _dialog(
        qtbot,
        DipoleParameters(
            frequency_hz=146_000_000.0,
            total_length_m=1.0,
            height_m=12.0,
        ),
    )

    dialog._run_estimate()

    assert dialog._results.rowCount() >= 2
    assert dialog._apply.isEnabled()
    assert dialog._estimator_type == "wire_dipole"
    assert dialog._template_value.text() == "Wire dipole"
    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, DipoleParameters)
    assert parameters.total_length_m > 0.0
    assert parameters.height_m == pytest.approx(12.0)


def test_dialog_preloads_the_current_template_and_parameters(qtbot: QtBot) -> None:
    dialog = _dialog(
        qtbot,
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=9.0,
            orientation=DipoleOrientation.VERTICAL,
        ),
    )

    assert not hasattr(dialog, "_family")
    assert dialog._template_value.text() == "Wire dipole"
    assert dialog._frequency.value() == pytest.approx(7.1)
    assert dialog._height.value() == pytest.approx(9.0)
    assert dialog._orientation.currentData() == DipoleOrientation.VERTICAL.value
    assert "current template" in dialog._template_hint.text().lower()


def test_dialog_estimates_a_vertical_with_subtype(qtbot: QtBot) -> None:
    dialog = _dialog(
        qtbot,
        VerticalParameters(
            frequency_hz=146_000_000.0,
            height_m=1.4,
            base_height_m=0.3,
            radial_count=8,
            radial_length_m=0.5,
        ),
    )

    dialog._vertical_form.setCurrentIndex(
        dialog._vertical_form.findData(VerticalForm.HALF_WAVE.value)
    )
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, VerticalParameters)
    assert parameters.radial_count == 8
    assert parameters.base_height_m == pytest.approx(0.3)
    assert parameters.height_m > 0.9


def test_dialog_preselects_the_ringo_template(qtbot: QtBot) -> None:
    dialog = _dialog(
        qtbot,
        RingoParameters(
            frequency_hz=7_100_000.0,
            radiator_height_m=5.0,
            ring_diameter_m=1.0,
        ),
    )

    assert dialog._template_value.text() == "Ringo"
    assert dialog._estimator_type == "ringo"
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, RingoParameters)
    assert parameters.frequency_hz == pytest.approx(7_100_000.0)


def test_dialog_estimates_a_delta_loop_without_changing_the_family(
    qtbot: QtBot,
) -> None:
    dialog = _dialog(
        qtbot,
        LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=42.0,
            height_m=8.0,
            sides=3,
        ),
    )

    assert dialog._template_value.text() == "Delta loop"
    assert dialog._loop_shape.currentData() == "delta"
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, LoopParameters)
    assert parameters.sides == 3


def test_dialog_preloads_a_fan_dipole_element_count(qtbot: QtBot) -> None:
    dialog = _dialog(
        qtbot,
        FanDipoleParameters(
            frequency_hz=7_100_000.0,
            elements=(
                FanElement(length_m=20.2, included_angle_deg=120.0),
                FanElement(length_m=10.1, included_angle_deg=100.0),
            ),
            apex_height_m=12.0,
        ),
    )

    assert len(dialog._fan_bands.text().split(",")) == 2
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, FanDipoleParameters)
    assert len(parameters.elements) == 2


def test_dialog_preloads_the_yagi_element_count(qtbot: QtBot) -> None:
    initial = _estimated_parameters("yagi")
    assert isinstance(initial, YagiParameters)
    dialog = _dialog(qtbot, initial)

    assert dialog._yagi_elements.value() == len(initial.elements)
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, YagiParameters)
    assert len(parameters.elements) == len(initial.elements)


def test_dialog_preloads_and_applies_yagi_polarization(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.polarization import Polarization

    initial = _estimated_parameters("yagi")
    assert isinstance(initial, YagiParameters)
    initial = replace(initial, height_m=8.0, polarization=Polarization.VERTICAL)
    dialog = _dialog(qtbot, initial)

    assert dialog._polarization.currentData() == "vertical"
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, YagiParameters)
    assert parameters.polarization is Polarization.VERTICAL


def test_dialog_preloads_and_applies_moxon_polarization(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.polarization import Polarization

    initial = _estimated_parameters("moxon")
    assert isinstance(initial, MoxonParameters)
    initial = replace(initial, height_m=10.0, polarization=Polarization.VERTICAL)
    dialog = _dialog(qtbot, initial)

    assert dialog._polarization.currentData() == "vertical"
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, MoxonParameters)
    assert parameters.polarization is Polarization.VERTICAL


def test_dialog_preloads_the_t2fd_band_and_estimates_it(qtbot: QtBot) -> None:
    from antennadesk.domain.antennas.t2fd import T2FDParameters

    dialog = _dialog(
        qtbot,
        T2FDParameters(
            frequency_hz=3_500_000.0,
            highest_frequency_hz=30_000_000.0,
            length_m=26.13,
            spacing_m=0.87,
        ),
    )

    assert dialog._estimator_type == "t2fd"
    assert dialog._highest_frequency.value() == pytest.approx(30.0)
    dialog._run_estimate()

    parameters = dialog.estimated_parameters()
    assert isinstance(parameters, T2FDParameters)
    assert parameters.highest_frequency_hz == pytest.approx(30_000_000.0)


def test_dialog_shows_estimator_sources(qtbot: QtBot) -> None:
    dialog = _dialog(
        qtbot,
        _estimated_parameters("moxon"),
    )
    dialog._run_estimate()

    assert "Cebik" in dialog._sources.text()
    assert "Table 1" in dialog._sources.text()


def test_changing_an_input_invalidates_the_estimate(qtbot: QtBot) -> None:
    dialog = _dialog(
        qtbot,
        DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
    )
    dialog._run_estimate()
    assert dialog._apply.isEnabled()

    dialog._frequency.setValue(dialog._frequency.value() * 1.01)

    assert dialog._apply.isEnabled() is False
    assert dialog._results.rowCount() == 0


@pytest.mark.parametrize(
    "family",
    (
        "wire_dipole",
        "folded_dipole",
        "loop",
        "vertical",
        "inverted_v",
        "fan_dipole",
        "endfed",
        "ocfd",
        "j_pole",
        "ringo",
        "yagi",
        "moxon",
        "t2fd",
    ),
)
def test_dialog_estimates_every_supported_family(
    qtbot: QtBot,
    family: str,
) -> None:
    initial = _estimated_parameters(family)
    dialog = _dialog(qtbot, initial)
    dialog._run_estimate()

    assert dialog._results.rowCount() > 0
    assert dialog._apply.isEnabled() is True
    assert antenna_type_for(dialog.estimated_parameters()) == family
