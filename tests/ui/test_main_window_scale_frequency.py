# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit scale-to-frequency action."""

from __future__ import annotations

import pytest
from main_window_support import use_parameters
from PySide6.QtWidgets import QDialog

from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.main_window import MainWindow


def test_scale_geometry_to_frequency_preserves_family_fields(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from antennadesk.domain.antennas.quad_beam import (
        QuadBeamParameters,
        quad_beam_parameters,
    )

    current = quad_beam_parameters(
        frequency_hz=144_000_000.0,
        element_count=3,
        loop_side_m=0.50,
        reflector_spacing_m=0.45,
        director_spacing_m=0.45,
        height_m=8.0,
        reflector_scale=1.1,
        director_scale=0.9,
        transformer_ratio=6.0,
    )
    use_parameters(window, current)
    assert window._scale_frequency_action.isEnabled() is True

    class FakeScaleDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def target_frequency_hz(self) -> float:
            return 288_000_000.0

    monkeypatch.setattr(main_window_module, "ScaleFrequencyDialog", FakeScaleDialog)
    window._dirty = False

    window.scale_geometry_to_frequency()

    assert window._project is not None
    design = window._project.designs[0]
    assert isinstance(design.parameters, QuadBeamParameters)
    assert design.parameters.frequency_hz == pytest.approx(288_000_000.0)
    assert design.parameters.loop_side_m == pytest.approx(0.25)
    assert design.parameters.reflector_spacing_m == pytest.approx(0.225)
    assert design.parameters.director_spacing_m == pytest.approx(0.225)
    assert design.parameters.height_m == pytest.approx(8.0)
    assert design.parameters.element_count == 3
    assert design.parameters.reflector_scale == pytest.approx(1.1)
    assert design.parameters.director_scale == pytest.approx(0.9)
    assert design.parameters.transformer_ratio == pytest.approx(6.0)

    assert window._undo_stack.canUndo() is True
    window._undo_project()
    design = window._project.designs[0]
    assert design.parameters.frequency_hz == pytest.approx(144_000_000.0)
    window._dirty = False


def test_scale_frequency_action_is_disabled_for_unsupported_templates(
    window: MainWindow,
) -> None:
    from antennadesk.domain.antennas.yagi import nbs_five_element

    use_parameters(window, nbs_five_element(frequency_hz=145_000_000.0, height_m=10.0))
    window._update_actions()

    assert window._scale_frequency_action.isEnabled() is False
    assert "no reliable frequency-scaling rule" in window._scale_frequency_action.toolTip()
    window._dirty = False
