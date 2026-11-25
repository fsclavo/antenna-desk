# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Every catalog entry must have a New Antenna and Change Template route."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QDialog

from antennadesk.domain.antennas.beverage import beverage_parameters
from antennadesk.domain.antennas.biquad import (
    BiquadKind,
    biquad_parameters,
)
from antennadesk.domain.antennas.custom import CustomAntennaParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import discone_parameters
from antennadesk.domain.antennas.endfed import (
    EndFedParameters,
    EndFedPreset,
    shortened_efhw_40_10_parameters,
    shortened_efhw_80_10_parameters,
)
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters, FanElement
from antennadesk.domain.antennas.feed import FeedPoint
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.geometry import Point3D
from antennadesk.domain.antennas.hexbeam import published_hexbeam_parameters
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loaded_dipole import loaded_dipole_parameters
from antennadesk.domain.antennas.log_periodic import log_periodic_parameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.antennas.materials import COPPER
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.phased_vertical import phased_vertical_parameters
from antennadesk.domain.antennas.quad_beam import quad_beam_parameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.scv import ScvKind, scv_parameters
from antennadesk.domain.antennas.stacked_yagi import StackedYagiParameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.trap_yagi import trap_yagi_parameters
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
from antennadesk.ui import catalog as catalog_module
from antennadesk.ui.catalog import (
    CHANGE_BUILDERS,
    NEW_BUILDERS,
    CatalogContext,
    change_template_selection,
    new_antenna_selection,
)
from antennadesk.ui.dialogs import antenna_catalog_dialog
from antennadesk.ui.i18n import Language, Translator
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
        "stacked_yagi": StackedYagiParameters(
            yagi=YagiParameters(
                frequency_hz=14_100_000.0,
                elements=(
                    YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
                    YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
                ),
                height_m=10.0,
            ),
            count=2,
            spacing_m=10.6,
            phase_step_deg=180.0,
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
        "shortened_endfed_80_10": shortened_efhw_80_10_parameters(),
        "shortened_endfed_40_10": shortened_efhw_40_10_parameters(),
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
        "log_periodic": log_periodic_parameters(),
        "discone": discone_parameters(),
        "trap_yagi": trap_yagi_parameters(),
        "hexbeam": published_hexbeam_parameters(),
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


def _context() -> CatalogContext:
    return CatalogContext(
        parent=None,  # type: ignore[arg-type]
        translator=Translator(Language.ENGLISH),
        unit_system=UnitSystem.METRIC,
        current_frequency_hz=7_100_000.0,
        current_feed_line=None,
    )


def _fake_dialog_class(parameters: object) -> type:
    class FakeDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> object:
            return parameters

        def typed_result_parameters(self) -> object:
            return parameters

        def parameters(self) -> object:
            return parameters

        def result_feed_line(self) -> None:
            return None

        def feed_line(self) -> None:
            return None

        def result_band_plan(self) -> None:
            return None

    return FakeDialog


def test_every_catalog_entry_has_a_change_template_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    keys = set(_catalog_constants().values())

    assert set(CHANGE_BUILDERS) == keys
    for key in sorted(keys):
        parameters = _parameters_for(key)
        monkeypatch.setattr(
            catalog_module,
            "_dialog_class",
            lambda _name, parameters=parameters: _fake_dialog_class(parameters),
        )
        change = change_template_selection(_context(), key)

        assert change is not None, f"catalog entry has no parameter route: {key}"
        assert change.parameters is not None


def test_every_catalog_entry_has_a_new_antenna_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    keys = set(_catalog_constants().values())

    assert set(NEW_BUILDERS) == keys
    for key in sorted(keys):
        parameters = _parameters_for(key)
        monkeypatch.setattr(
            catalog_module,
            "_dialog_class",
            lambda _name, parameters=parameters: _fake_dialog_class(parameters),
        )
        selection = new_antenna_selection(_context(), key)

        assert selection is not None, f"catalog entry has no New Antenna route: {key}"
        assert selection.default_name


def test_delta_and_quad_change_template_use_the_loop_dialog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[dict[str, object]] = []

    class FakeBasicDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            captured.append(kwargs)

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> LoopParameters:
            return LoopParameters(
                frequency_hz=7_100_000.0,
                circumference_m=40.0,
                height_m=8.0,
                sides=int(captured[-1].get("initial_sides") or 4),
            )

    monkeypatch.setattr(catalog_module, "_dialog_class", lambda _name: FakeBasicDialog)

    for key, expected_sides in (("delta_loop", 3), ("quad_loop", 4)):
        change = change_template_selection(_context(), key)

        assert isinstance(change.parameters, LoopParameters)
        assert change.parameters.sides == expected_sides
        assert captured[-1]["antenna_type"] == "loop"


ESTIMATORLESS_CATALOG_KEYS = frozenset(
    {
        "custom",
        "g5rv",
        "inverted_l",
        "loaded_vertical",
        "magnetic_loop",
        "random_wire",
        "shortened_endfed_80_10",
        "shortened_endfed_40_10",
        "half_square",
        "bobtail_curtain",
        "biquad",
        "double_biquad",
        "beverage",
        "loaded_dipole",
        "log_periodic",
        "discone",
        "trap_yagi",
        "phased_vertical",
        "stacked_yagi",
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
