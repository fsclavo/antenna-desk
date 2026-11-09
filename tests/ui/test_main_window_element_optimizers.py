# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Element-optimizer entry points for the remaining typed families."""

from __future__ import annotations

import pytest
from main_window_support import use_parameters
from PySide6.QtWidgets import QDialog

from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.zs6bkw import zs6bkw_parameters
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow

ELEMENT_CASES = (
    (
        "optimize_moxon_elements",
        MoxonParameters(
            frequency_hz=28_500_000.0,
            width_m=5.0,
            depth_m=1.5,
            reflector_tip_m=0.3,
            driven_tip_m=0.3,
            height_m=10.0,
        ),
        "element_optimize.moxon_title",
    ),
    (
        "optimize_loop_elements",
        LoopParameters(
            frequency_hz=14_100_000.0,
            circumference_m=21.5,
            height_m=2.0,
        ),
        "element_optimize.loop_title",
    ),
    (
        "optimize_vertical_elements",
        VerticalParameters(frequency_hz=14_100_000.0, height_m=5.0),
        "element_optimize.vertical_title",
    ),
    (
        "optimize_inverted_v_elements",
        InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=10.0,
            apex_height_m=12.0,
        ),
        "element_optimize.inverted_v_title",
    ),
    (
        "optimize_ringo_elements",
        RingoParameters(
            frequency_hz=50_100_000.0,
            radiator_height_m=3.0,
            ring_diameter_m=0.33,
            ring_height_m=0.1,
        ),
        "element_optimize.ringo_title",
    ),
    (
        "optimize_zs6bkw_elements",
        zs6bkw_parameters(),
        "element_optimize.zs6bkw_title",
    ),
)


@pytest.mark.parametrize(
    ("method_name", "parameters", "title_key"),
    ELEMENT_CASES,
    ids=[case[0].removeprefix("optimize_").removesuffix("_elements") for case in ELEMENT_CASES],
)
def test_element_optimizer_updates_the_design_and_starts_a_simulation(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
    method_name: str,
    parameters: object,
    title_key: str,
) -> None:
    use_parameters(window, parameters)
    captured: dict[str, object] = {}

    class FakeElementDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.update(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_parameters(self) -> object:
            return parameters

    monkeypatch.setattr(main_window_module, "ElementOptimizationDialog", FakeElementDialog)
    simulations: list[bool] = []
    monkeypatch.setattr(window, "simulate", lambda: simulations.append(True))

    getattr(window, method_name)()

    assert captured["title_key"] == title_key
    assert captured["build_parameters"]
    assert simulations == [True]
    assert window._project is not None
    assert isinstance(window._project.designs[0].parameters, type(parameters))
    window._dirty = False
