# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-template conductor-material defaults."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import fields
from pathlib import Path
from typing import Any

import pytest
from pytestqt.qtbot import QtBot

from antennadesk.domain.antennas.beverage import BeverageParameters
from antennadesk.domain.antennas.biquad import BiquadKind, BiquadParameters
from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.discone import DisconeParameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.fan_dipole import FanDipoleParameters
from antennadesk.domain.antennas.flower_pot import FlowerPotParameters
from antennadesk.domain.antennas.folded_dipole import FoldedDipoleParameters
from antennadesk.domain.antennas.hexbeam import HexbeamParameters
from antennadesk.domain.antennas.inverted_l import InvertedLParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.j_pole import JPoleParameters
from antennadesk.domain.antennas.loaded_dipole import LoadedDipoleParameters
from antennadesk.domain.antennas.log_periodic import LogPeriodicParameters
from antennadesk.domain.antennas.loop import LoopParameters
from antennadesk.domain.antennas.magnetic_loop import MagneticLoopParameters
from antennadesk.domain.antennas.material_defaults import (
    TEMPLATE_MATERIAL_DEFAULTS,
    default_material_for_template,
)
from antennadesk.domain.antennas.materials import (
    ALUMINUM,
    COPPER,
    STAINLESS_STEEL_304,
    ConductorMaterial,
)
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.ocfd import OCFDParameters
from antennadesk.domain.antennas.phased_vertical import PhasedVerticalParameters
from antennadesk.domain.antennas.quad_beam import QuadBeamParameters
from antennadesk.domain.antennas.ringo import RingoParameters
from antennadesk.domain.antennas.scv import ScvKind, ScvParameters, scv_parameters
from antennadesk.domain.antennas.t2fd import T2FDParameters
from antennadesk.domain.antennas.transmission_line_doublet import (
    TransmissionLineDoubletParameters,
)
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.trap_yagi import TrapYagiParameters
from antennadesk.domain.antennas.vertical import VerticalParameters
from antennadesk.domain.antennas.yagi import YagiElement, YagiParameters
from antennadesk.domain.antennas.zepp import ZeppParameters
from antennadesk.domain.design.reference_library import REFERENCE_DESIGNS
from antennadesk.domain.projects.project import Project
from antennadesk.persistence.container import ProjectContainerRepository
from antennadesk.ui.dialogs.antenna_catalog_dialog import ENTRIES
from antennadesk.ui.dialogs.biquad_dialog import BiquadDialog
from antennadesk.ui.dialogs.discone_dialog import DisconeDialog
from antennadesk.ui.dialogs.hexbeam_dialog import HexbeamDialog
from antennadesk.ui.dialogs.j_pole_dialog import JPoleDialog
from antennadesk.ui.dialogs.log_periodic_dialog import LogPeriodicDialog
from antennadesk.ui.dialogs.moxon_dialog import MoxonDialog
from antennadesk.ui.dialogs.phased_vertical_dialog import PhasedVerticalDialog
from antennadesk.ui.dialogs.quad_beam_dialog import QuadBeamDialog
from antennadesk.ui.dialogs.ringo_dialog import RingoDialog
from antennadesk.ui.dialogs.scv_dialog import ScvDialog
from antennadesk.ui.dialogs.trap_yagi_dialog import TrapYagiDialog
from antennadesk.ui.dialogs.vertical_dialog import VerticalDialog
from antennadesk.ui.dialogs.yagi_dialog import YagiDialog
from antennadesk.ui.i18n import Language, Translator
from antennadesk.ui.main_window import MainWindow
from antennadesk.ui.units import UnitSystem

_ALUMINUM_CLASSES = (
    YagiParameters,
    TrapYagiParameters,
    VerticalParameters,
    RingoParameters,
    JPoleParameters,
    DisconeParameters,
    PhasedVerticalParameters,
    MoxonParameters,
    HexbeamParameters,
    QuadBeamParameters,
    BiquadParameters,
    LogPeriodicParameters,
)
_COPPER_CLASSES = (
    DipoleParameters,
    FoldedDipoleParameters,
    FlowerPotParameters,
    LoopParameters,
    MagneticLoopParameters,
    OCFDParameters,
    InvertedVParameters,
    InvertedLParameters,
    FanDipoleParameters,
    EndFedParameters,
    LoadedDipoleParameters,
    TrapDipoleParameters,
    T2FDParameters,
    BeverageParameters,
    ZeppParameters,
    TransmissionLineDoubletParameters,
    ScvParameters,
)


def _translator() -> Translator:
    return Translator(Language.ENGLISH)


def _yagi_parameters(material: ConductorMaterial = COPPER) -> YagiParameters:
    return YagiParameters(
        frequency_hz=14_100_000.0,
        elements=(
            YagiElement(position_m=0.0, length_m=10.0, radius_m=0.001),
            YagiElement(position_m=2.0, length_m=9.5, radius_m=0.001),
        ),
        height_m=10.0,
        material=material,
    )


@pytest.mark.parametrize("parameters_class", _ALUMINUM_CLASSES)
def test_aluminum_family_defaults(parameters_class: type[object]) -> None:
    material = next(field.default for field in fields(parameters_class) if field.name == "material")
    assert material is ALUMINUM


@pytest.mark.parametrize("parameters_class", _COPPER_CLASSES)
def test_copper_family_defaults(parameters_class: type[object]) -> None:
    material = next(field.default for field in fields(parameters_class) if field.name == "material")
    assert material is COPPER


def test_template_mapping_covers_every_catalog_entry() -> None:
    catalog_keys = {entry.key for entry in ENTRIES}

    assert set(TEMPLATE_MATERIAL_DEFAULTS) == catalog_keys
    assert len(TEMPLATE_MATERIAL_DEFAULTS) == 43
    assert default_material_for_template("unknown") is COPPER


@pytest.mark.parametrize(
    ("template_id", "expected"),
    [
        ("yagi", ALUMINUM),
        ("loaded_vertical", STAINLESS_STEEL_304),
        ("wire_dipole", COPPER),
        ("half_square", ALUMINUM),
        ("bobtail_curtain", COPPER),
    ],
)
def test_resolver_examples(template_id: str, expected: object) -> None:
    assert default_material_for_template(template_id) is expected


_ALUMINUM_DIALOGS = (
    ("yagi", lambda t, u: YagiDialog(t, u)),
    ("trap_yagi", lambda t, u: TrapYagiDialog(t, u)),
    ("vertical", lambda t, u: VerticalDialog(t, u)),
    ("ringo", lambda t, u: RingoDialog(t, u)),
    ("j_pole", lambda t, u: JPoleDialog(t, u)),
    ("slim_jim", lambda t, u: JPoleDialog(t, u)),
    ("discone", lambda t, u: DisconeDialog(t, u)),
    ("phased_vertical", lambda t, u: PhasedVerticalDialog(t, u)),
    ("moxon", lambda t, u: MoxonDialog(t, u)),
    ("hexbeam", lambda t, u: HexbeamDialog(t, u)),
    ("quad_beam", lambda t, u: QuadBeamDialog(t, u)),
    ("biquad", lambda t, u: BiquadDialog(t, u)),
    ("double_biquad", lambda t, u: BiquadDialog(t, u, kind=BiquadKind.DOUBLE)),
    ("half_square", lambda t, u: ScvDialog(t, u, kind=ScvKind.HALF_SQUARE)),
    ("log_periodic", lambda t, u: LogPeriodicDialog(t, u)),
)


@pytest.mark.parametrize(("template_id", "factory"), _ALUMINUM_DIALOGS)
def test_new_aluminum_dialogs(
    qtbot: QtBot,
    template_id: str,
    factory: Callable[..., Any],
) -> None:
    del template_id
    dialog = factory(
        _translator(),
        UnitSystem.METRIC,
    )
    qtbot.addWidget(dialog)
    assert dialog.parameters().material is ALUMINUM


def test_new_loaded_vertical_is_stainless(qtbot: QtBot) -> None:
    dialog = VerticalDialog(_translator(), UnitSystem.METRIC, mobile=True)
    qtbot.addWidget(dialog)

    assert dialog.parameters().material is STAINLESS_STEEL_304


def test_new_bobtail_is_copper(qtbot: QtBot) -> None:
    dialog = ScvDialog(_translator(), UnitSystem.METRIC, kind=ScvKind.BOBTAIL_CURTAIN)
    qtbot.addWidget(dialog)

    assert dialog.parameters().material is COPPER


def test_existing_yagi_material_is_preserved(qtbot: QtBot) -> None:
    dialog = YagiDialog(_translator(), UnitSystem.METRIC, parameters=_yagi_parameters(COPPER))
    qtbot.addWidget(dialog)

    assert dialog.parameters().material is COPPER


def test_scv_factory_chooses_by_kind_and_respects_an_override() -> None:
    assert scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0).material is ALUMINUM
    assert scv_parameters(ScvKind.BOBTAIL_CURTAIN, 7_150_000.0).material is COPPER
    assert scv_parameters(ScvKind.HALF_SQUARE, 7_150_000.0, material=COPPER).material is COPPER


@pytest.mark.parametrize(
    "key",
    [
        "cebik_moxon_20m",
        "g3txq_hexbeam_20m",
        "cebik_half_square",
        "cebik_bobtail_curtain",
        "nbs_yagi_6m",
    ],
)
def test_source_backed_references_keep_copper(key: str) -> None:
    design = next(item for item in REFERENCE_DESIGNS if item.key == key)

    assert design.parameters.material is COPPER


def test_custom_dialog_stays_copper() -> None:
    from antennadesk.ui.dialogs.custom_antenna_dialog import CustomAntennaDialog

    dialog = CustomAntennaDialog(_translator(), UnitSystem.METRIC)
    try:
        materials = {wire.material for wire in dialog.parameters().wires}
        assert materials == {COPPER}
    finally:
        dialog.close()


def test_design_from_frequency_preserves_the_current_material(qtbot: QtBot) -> None:
    from antennadesk.ui.dialogs.design_from_frequency_dialog import (
        DesignFromFrequencyDialog,
    )

    dialog = DesignFromFrequencyDialog(
        _translator(),
        UnitSystem.METRIC,
        initial_parameters=_yagi_parameters(STAINLESS_STEEL_304),
    )
    qtbot.addWidget(dialog)

    dialog._run_estimate()

    assert dialog.estimated_parameters().material is STAINLESS_STEEL_304


def test_change_template_same_key_preserves_a_copper_yagi(
    window: MainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from PySide6.QtWidgets import QDialog, QMessageBox

    from antennadesk.ui import catalog as catalog_module
    from antennadesk.ui import main_window as main_window_module
    from antennadesk.ui.dialogs.antenna_catalog_dialog import (
        CATALOG_TYPE_YAGI,
    )

    project = window._project
    assert project is not None
    design = project.designs[0].with_parameters(_yagi_parameters(COPPER))
    project = project.with_design(design, updated_at=project.updated_at)
    window._set_project(project, design.id, path=None, dirty=False)

    class FakeCatalog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def selected_key(self) -> str:
            return CATALOG_TYPE_YAGI

    class FakeYagiDialog:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def exec(self) -> QDialog.DialogCode:
            return QDialog.DialogCode.Accepted

        def result_parameters(self) -> YagiParameters:
            return _yagi_parameters(ALUMINUM)

    monkeypatch.setattr(main_window_module, "AntennaCatalogDialog", FakeCatalog)
    monkeypatch.setattr(catalog_module, "YagiDialog", FakeYagiDialog)
    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
    )

    window.change_template()

    updated = window._project.designs[0].parameters
    assert isinstance(updated, YagiParameters)
    assert updated.material is COPPER


def test_material_survives_a_project_round_trip(
    tmp_path: Path,
    sample_project: Project,
) -> None:
    design = sample_project.designs[0].with_parameters(_yagi_parameters(ALUMINUM))
    project = sample_project.with_design(design, updated_at=sample_project.updated_at)
    repository = ProjectContainerRepository()
    path = tmp_path / "material.antennadesk"

    repository.save(project, path)
    loaded = repository.load(path)

    parameters = loaded.designs[0].parameters
    assert isinstance(parameters, YagiParameters)
    assert parameters.material == ALUMINUM
