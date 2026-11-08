# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every catalog entry must have a New Antenna and Change Template route."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QDialog, QWizard

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import (
    BiquadKind,
    biquad_parameters,
)
from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.endfed import EndFedParameters, EndFedPreset
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.wire import Wire
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.antennas.zepp import zepp_parameters
from antennadesk.domain.antennas.zs6bkw import zs6bkw_parameters
from antennadesk.domain.design import UnsupportedEstimateError
from antennadesk.domain.design.estimators import (
    SUPPORTED_ESTIMATOR_TYPES,
    estimator_type_for,
    supports_estimation,
)
from antennadesk.domain.design.evidence import EVIDENCE, EvidenceLevel
from antennadesk.ui import main_window as main_window_module
from antennadesk.ui.dialogs import antenna_catalog_dialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.template_identity import catalog_key_for
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
        "magnetic_loop": MagneticLoopParameters(
            frequency_hz=7_100_000.0,
            diameter_m=1.0,
        ),
        "ocfd": OCFDParameters(frequency_hz=7_100_000.0, total_length_m=40.0),
        "vertical": VerticalParameters(frequency_hz=7_100_000.0, height_m=10.0),
        "loaded_vertical": VerticalParameters(
            frequency_hz=7_100_000.0,
            height_m=2.0,
            base_height_m=0.25,
            radial_count=4,
            radial_length_m=1.0,
            loading_coil_enabled=True,
            loading_coil_offset_m=1.0,
            loading_coil_inductance_h=10e-6,
        ),
        "inverted_v": InvertedVParameters(
            frequency_hz=7_100_000.0,
            leg_length_m=10.0,
            apex_height_m=12.0,
        ),
        "inverted_l": InvertedLParameters(
            frequency_hz=7_100_000.0,
            vertical_height_m=10.0,
            horizontal_length_m=20.0,
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
            elements=(FanElement(20.0, 120.0), FanElement(10.0, 90.0)),
            apex_height_m=12.0,
        ),
        "t2fd": T2FDParameters(
            frequency_hz=3_500_000.0,
            highest_frequency_hz=30_000_000.0,
            length_m=26.0,
            spacing_m=0.9,
        ),
        "trap_dipole": TrapDipoleParameters(
            frequency_hz=7_100_000.0,
            high_band_frequency_hz=14_100_000.0,
            inner_length_m=10.0,
            outer_length_m=5.0,
            trap_frequency_hz=14_100_000.0,
            trap_inductance_h=10e-6,
        ),
        "endfed": EndFedParameters(frequency_hz=7_100_000.0, length_m=20.0),
        "sloper": EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=20.0,
            feed_height_m=10.0,
            end_height_m=2.0,
            preset=EndFedPreset.SLOPER,
        ),
        "random_wire": EndFedParameters(
            frequency_hz=7_100_000.0,
            length_m=17.0,
            transformer_ratio=9.0,
            counterpoise_length_m=1.0,
            preset=EndFedPreset.RANDOM_WIRE,
        ),
        "doublet": DipoleParameters(
            frequency_hz=7_100_000.0,
            total_length_m=20.0,
            height_m=10.0,
        ),
        "zs6bkw": zs6bkw_parameters(),
        "zepp": zepp_parameters(),
        "g5rv": CustomAntennaParameters(
            frequency_hz=7_100_000.0,
            wires=(
                Wire(
                    "source",
                    Point3D(0.0, 0.0, 1.0),
                    Point3D(0.0, 0.0, 1.1),
                    0.001,
                    COPPER,
                ),
                Wire(
                    "dipole",
                    Point3D(-15.55, 0.0, 10.0),
                    Point3D(15.55, 0.0, 10.0),
                    0.001,
                    COPPER,
                ),
            ),
            feed=FeedPoint("source", 0.05),
            generator_id="g5rv",
            generator_name="G5RV",
        ),
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
            folded=True,
        ),
        "ringo": RingoParameters(
            frequency_hz=29_000_000.0,
            radiator_height_m=5.0,
            ring_diameter_m=0.5,
        ),
        "half_square": scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0),
        "bobtail_curtain": scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0),
        "biquad": biquad_parameters(BiquadKind.SINGLE),
        "double_biquad": biquad_parameters(BiquadKind.DOUBLE),
        "beverage": beverage_parameters(),
        "loaded_dipole": loaded_dipole_parameters(),
        "discone": discone_parameters(),
        "phased_vertical": phased_vertical_parameters(),
        "quad_beam": quad_beam_parameters(),
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
            "ScvDialog",
            "JPoleDialog",
            "EndFedDialog",
            "FanDipoleDialog",
            "TrapDipoleDialog",
            "T2FDDialog",
            "InvertedLDialog",
            "InvertedVDialog",
            "MagneticLoopDialog",
            "OCFDDialog",
            "VerticalDialog",
            "CustomAntennaDialog",
            "DoubletDialog",
            "G5RVDialog",
            "ZS6BKWDialog",
            "ZeppDialog",
            "BiquadDialog",
            "BeverageDialog",
            "LoadedDipoleDialog",
            "DisconeDialog",
            "PhasedVerticalDialog",
            "QuadBeamDialog",
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
        "magnetic_loop": ("magnetic_loop",),
        "ocfd": ("ocfd",),
        "vertical": ("vertical",),
        "loaded_vertical": ("loaded_vertical",),
        "inverted_v": ("inverted_v",),
        "inverted_l": ("inverted_l",),
        "yagi": ("yagi",),
        "moxon": ("moxon",),
        "fan_dipole": ("fan_dipole",),
        "trap_dipole": ("trap_dipole",),
        "t2fd": ("t2fd",),
        "endfed": ("endfed",),
        "sloper": ("sloper",),
        "random_wire": ("random_wire",),
        "doublet": ("doublet",),
        "g5rv": ("g5rv",),
        "zs6bkw": ("zs6bkw",),
        "zepp": ("zepp",),
        "j_pole": ("j_pole", False),
        "slim_jim": ("j_pole", True),
        "ringo": ("ringo",),
        "half_square": ("half_square",),
        "bobtail_curtain": ("bobtail_curtain",),
        "biquad": ("single_biquad",),
        "double_biquad": ("double_biquad",),
        "beverage": ("beverage",),
        "loaded_dipole": ("loaded_dipole",),
        "discone": ("discone",),
        "phased_vertical": ("phased_vertical",),
        "quad_beam": ("quad_beam",),
        "custom": ("custom",),
    }

    catalog_keys = {entry.key for entry in antenna_catalog_dialog.ENTRIES}
    assert set(routes) == catalog_keys, (
        f"New Antenna route table is out of date: {set(routes) ^ catalog_keys}"
    )

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
        new_inverted_l_antenna=record("inverted_l"),
        new_magnetic_loop_antenna=record("magnetic_loop"),
        new_fan_dipole_antenna=record("fan_dipole"),
        new_trap_dipole_antenna=record("trap_dipole"),
        new_t2fd_antenna=record("t2fd"),
        new_endfed_antenna=record("endfed"),
        new_sloper_antenna=record("sloper"),
        new_random_wire_antenna=record("random_wire"),
        new_doublet_antenna=record("doublet"),
        new_g5rv_antenna=record("g5rv"),
        new_zs6bkw_antenna=record("zs6bkw"),
        new_zepp_antenna=record("zepp"),
        new_j_pole_antenna=record("j_pole"),
        new_ringo_antenna=record("ringo"),
        new_half_square_antenna=record("half_square"),
        new_bobtail_curtain_antenna=record("bobtail_curtain"),
        new_single_biquad_antenna=record("single_biquad"),
        new_double_biquad_antenna=record("double_biquad"),
        new_beverage_antenna=record("beverage"),
        new_loaded_dipole_antenna=record("loaded_dipole"),
        new_discone_antenna=record("discone"),
        new_phased_vertical_antenna=record("phased_vertical"),
        new_quad_beam_antenna=record("quad_beam"),
        new_ocfd_antenna=record("ocfd"),
        new_vertical_antenna=record("vertical"),
        new_loaded_vertical_antenna=record("loaded_vertical"),
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


ESTIMATORLESS_CATALOG_KEYS = frozenset(
    {
        "custom",
        "g5rv",
        "inverted_l",
        "loaded_vertical",
        "magnetic_loop",
        "random_wire",
        "half_square",
        "bobtail_curtain",
        "biquad",
        "double_biquad",
        "beverage",
        "loaded_dipole",
        "discone",
        "phased_vertical",
        "quad_beam",
        "trap_dipole",
        "zepp",
        "zs6bkw",
    }
)


def test_every_catalog_entry_has_the_expected_estimator_support() -> None:
    covered: set[str] = set()

    for entry in antenna_catalog_dialog.ENTRIES:
        parameters = _parameters_for(entry.key)
        if entry.key in ESTIMATORLESS_CATALOG_KEYS:
            assert supports_estimation(parameters) is False, entry.key
            with pytest.raises(UnsupportedEstimateError):
                estimator_type_for(parameters)
            continue
        estimator = estimator_type_for(parameters)
        assert estimator in SUPPORTED_ESTIMATOR_TYPES, entry.key
        covered.add(estimator)

    assert covered == SUPPORTED_ESTIMATOR_TYPES


def test_catalog_identity_maps_every_template_except_the_doublet_alias() -> None:
    for entry in antenna_catalog_dialog.ENTRIES:
        parameters = _parameters_for(entry.key)
        if entry.key == "doublet":
            # The doublet is a dipole plus a project feed line; the canonical
            # parameters cannot distinguish it from a wire dipole.
            assert catalog_key_for(parameters) == "wire_dipole"
        else:
            assert catalog_key_for(parameters) == entry.key


def test_catalog_evidence_label_matches_the_registry_level() -> None:
    for entry in antenna_catalog_dialog.ENTRIES:
        level = EVIDENCE[entry.key].level
        if entry.evidence_key == "catalog.evidence.experimental":
            assert level is EvidenceLevel.EXPERIMENTAL, entry.key
        if entry.evidence_key == "catalog.evidence.published":
            assert level is EvidenceLevel.PUBLISHED, entry.key


def test_catalog_entry_strings_exist_in_both_languages() -> None:
    for entry in antenna_catalog_dialog.ENTRIES:
        for key in (
            entry.label_key,
            entry.family_key,
            entry.description_key,
            entry.evidence_key,
        ):
            for language in (Language.ENGLISH, Language.SPANISH):
                assert Translator(language).t(key) != key, f"missing {key!r} in {language.value}"
