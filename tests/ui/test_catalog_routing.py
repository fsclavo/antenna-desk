# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every catalog entry must have a New Antenna and Change Template route."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QDialog, QWizard

from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.dialogs import antenna_catalog_dialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem


def _catalog_constants() -> dict[str, str]:
    return {
        name: value
        for name, value in vars(antenna_catalog_dialog).items()
        if name.startswith("CATALOG_TYPE_") and isinstance(value, str)
    }


def _parameters_for(key: str) -> object:
    parameters: dict[str, object] = {
        "wire_dipole": DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
        ),
        "folded_dipole": FoldedDipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=8.0,
            spacing_m=0.2,
        ),
        "loop": LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=16,
        ),
        "delta_loop": LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=3,
        ),
        "quad_loop": LoopParameters(
            frequency_hz=7_100_000.0,
            circumference_m=40.0,
            height_m=8.0,
            sides=4,
        ),
        "ocfd": OCFDParameters(frequency_hz=7_100_000.0, total_length_m=40.0),
        "vertical": VerticalParameters(frequency_hz=7_100_000.0, height_m=10.0),
        "inverted_v": InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=10.0,
            apex_height_m=12.0,
        ),
        "yagi": YagiParameters(
            frequency_hz=14_100_000.0,
            elements=(
                YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
                YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
            ),
            height_m=10.0,
        ),
        "moxon": MoxonParameters(
            frequency_hz=14_100_000.0,
            width_m=10.0,
            depth_m=3.0,
            reflector_tip_m=1.0,
            driven_tip_m=1.0,
            height_m=10.0,
        ),
        "fan_dipole": FanDipoleParameters(
            frequency_hz=7_100_000.0,
            elements=(FanElement(20.0, 120.0), FanElement(10.0, 120.0)),
            apex_height_m=12.0,
        ),
        "endfed": EndFedParameters(frequency_hz=7_100_000.0, length_m=20.0),
        "j_pole": JPoleParameters(
            frequency_hz=220_000_000.0,
            radiator_height_m=1.0,
            stub_length_m=0.5,
            spacing_m=0.05,
            feed_offset_m=0.1,
            base_height_m=0.25,
        ),
        "slim_jim": JPoleParameters(
            frequency_hz=220_000_000.0,
            radiator_height_m=1.0,
            stub_length_m=0.5,
            spacing_m=0.05,
            feed_offset_m=0.1,
            base_height_m=0.25,
        ),
        "ringo": RingoParameters(
            frequency_hz=29_000_000.0,
            radiator_height_m=5.0,
            ring_diameter_m=0.5,
        ),
        "custom": CustomAntennaParameters(
            frequency_hz=7_100_000.0,
            wires=(
                Wire(
                    "w1",
                    Point3D(-3.0, 0.0, 5.0),
                    Point3D(3.0, 0.0, 5.0),
                    0.001,
                    COPPER,
                ),
            ),
            feed=FeedPoint("w1", 3.0),
        ),
    }
    return parameters[key]


def test_catalog_constants_and_entries_match() -> None:
    constants = set(_catalog_constants().values())
    entries = {entry.key for entry in antenna_catalog_dialog.ENTRIES}

    assert constants == entries


def test_every_catalog_entry_has_a_change_template_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeDialog:
        def __init__(self, parameters: object) -> None:
            self._parameters = parameters

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def build_parameters(self) -> object:
            return self._parameters

        def result_parameters(self) -> object:
            return self._parameters

    for key in sorted(_catalog_constants().values()):
        parameters = _parameters_for(key)

        def fake_factory(*_args: object, _parameters: object = parameters, **_kwargs: object):
            return FakeDialog(_parameters)

        for class_name in (
            "DipoleWizard",
            "MoxonDialog",
            "YagiDialog",
            "RingoDialog",
            "JPoleDialog",
            "EndFedDialog",
            "FanDipoleDialog",
            "InvertedVDialog",
            "OCFDDialog",
            "VerticalDialog",
            "CustomAntennaDialog",
        ):
            monkeypatch.setattr(main_window_module, class_name, fake_factory)
        fake_self = SimpleNamespace(
            _translator=Translator(Language.ENGLISH),
            _unit_system=UnitSystem.METRIC,
        )

        result = MainWindow._parameters_from_catalog(fake_self, key, 7_100_000.0)

        assert result is not None, f"catalog entry has no parameter route: {key}"


def test_every_catalog_entry_has_a_new_antenna_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    routes: dict[str, object] = {
        "wire_dipole": ("basic", "wire_dipole", None),
        "folded_dipole": ("basic", "folded_dipole", None),
        "loop": ("basic", "loop", None),
        "delta_loop": ("basic", "loop", 3),
        "quad_loop": ("basic", "loop", 4),
        "ocfd": ("ocfd",),
        "vertical": ("vertical",),
        "inverted_v": ("inverted_v",),
        "yagi": ("yagi",),
        "moxon": ("moxon",),
        "fan_dipole": ("fan_dipole",),
        "endfed": ("endfed",),
        "j_pole": ("j_pole", False),
        "slim_jim": ("j_pole", True),
        "ringo": ("ringo",),
        "custom": ("custom",),
    }

    class FakeCatalog:
        selected = "wire_dipole"

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_key(self) -> str:
            return self.selected

    calls: list[tuple[object, ...]] = []

    def record(name: str):
        def handler(*args: object, **kwargs: object) -> None:
            if name == "basic":
                calls.append(("basic", args[0], kwargs.get("initial_sides")))
            elif name == "j_pole":
                calls.append((name, kwargs.get("folded")))
            else:
                calls.append((name, *args))

        return handler

    fake_self = SimpleNamespace(
        _translator=Translator(Language.ENGLISH),
        _unit_system=UnitSystem.METRIC,
        new_custom_antenna=record("custom"),
        new_yagi_antenna=record("yagi"),
        new_moxon_antenna=record("moxon"),
        new_inverted_v_antenna=record("inverted_v"),
        new_fan_dipole_antenna=record("fan_dipole"),
        new_endfed_antenna=record("endfed"),
        new_j_pole_antenna=record("j_pole"),
        new_ringo_antenna=record("ringo"),
        new_ocfd_antenna=record("ocfd"),
        new_vertical_antenna=record("vertical"),
        _new_basic_antenna=record("basic"),
    )
    monkeypatch.setattr(main_window_module, "AntennaCatalogDialog", FakeCatalog)

    for key, expected in routes.items():
        FakeCatalog.selected = key
        calls.clear()
        MainWindow.new_antenna(fake_self)
        assert calls == [expected], f"wrong New Antenna route for {key}: {calls}"


def test_delta_and_quad_change_template_use_the_loop_wizard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[dict[str, object]] = []

    class FakeWizard:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.append(kwargs)

        def exec(self) -> QWizard.DialogCode:
            return QWizard.DialogCode.Accepted

        def build_parameters(self) -> LoopParameters:
            return LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=int(captured[-1].get("initial_sides") or 4),
            )

    monkeypatch.setattr(main_window_module, "DipoleWizard", FakeWizard)
    fake_self = SimpleNamespace(
        _translator=Translator(Language.ENGLISH),
        _unit_system=UnitSystem.METRIC,
    )

    for key, expected_sides in (("delta_loop", 3), ("quad_loop", 4)):
        result = MainWindow._parameters_from_catalog(fake_self, key, 7_100_000.0)
        assert isinstance(result, LoopParameters)
        assert result.sides == expected_sides
        assert captured[-1]["initial_antenna_type"] == "loop"
