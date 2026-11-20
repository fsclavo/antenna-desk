# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Catalog-to-dialog routing for new projects and template changes.

The module owns the repetitive catalog dispatch. It returns plain selections;
the main window keeps the save prompt, project creation, undo history, and the
application of a changed template.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from typing import Any, cast

from PySide6.QtWidgets import QDialog, QWidget

from ..application.ports.antenna_solver import AntennaSolver
from ..domain.antennas.biquad import BiquadKind
from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.endfed import EndFedPreset
from ..domain.antennas.feed_line import FeedLine
from ..domain.antennas.matching_network import MatchingNetwork
from ..domain.antennas.scv import ScvKind
from ..domain.design.band_plan import BandPlan
from .dialogs.antenna_catalog_dialog import (
    CATALOG_TYPE_BEVERAGE,
    CATALOG_TYPE_BIQUAD,
    CATALOG_TYPE_BOBTAIL_CURTAIN,
    CATALOG_TYPE_CUSTOM,
    CATALOG_TYPE_DELTA_LOOP,
    CATALOG_TYPE_DISCONE,
    CATALOG_TYPE_DOUBLE_BIQUAD,
    CATALOG_TYPE_DOUBLET,
    CATALOG_TYPE_ENDFED,
    CATALOG_TYPE_FAN_DIPOLE,
    CATALOG_TYPE_FOLDED_DIPOLE,
    CATALOG_TYPE_G5RV,
    CATALOG_TYPE_HALF_SQUARE,
    CATALOG_TYPE_HEXBEAM,
    CATALOG_TYPE_INVERTED_L,
    CATALOG_TYPE_INVERTED_V,
    CATALOG_TYPE_J_POLE,
    CATALOG_TYPE_LOADED_DIPOLE,
    CATALOG_TYPE_LOADED_VERTICAL,
    CATALOG_TYPE_LOG_PERIODIC,
    CATALOG_TYPE_LOOP,
    CATALOG_TYPE_MAGNETIC_LOOP,
    CATALOG_TYPE_MOXON,
    CATALOG_TYPE_OCFD,
    CATALOG_TYPE_PHASED_VERTICAL,
    CATALOG_TYPE_QUAD_BEAM,
    CATALOG_TYPE_QUAD_LOOP,
    CATALOG_TYPE_RANDOM_WIRE,
    CATALOG_TYPE_RINGO,
    CATALOG_TYPE_SHORTENED_ENDFED_40_10,
    CATALOG_TYPE_SHORTENED_ENDFED_80_10,
    CATALOG_TYPE_SLIM_JIM,
    CATALOG_TYPE_SLOPER,
    CATALOG_TYPE_T2FD,
    CATALOG_TYPE_TRAP_DIPOLE,
    CATALOG_TYPE_TRAP_YAGI,
    CATALOG_TYPE_VERTICAL,
    CATALOG_TYPE_WIRE_DIPOLE,
    CATALOG_TYPE_YAGI,
    CATALOG_TYPE_ZEPP,
    CATALOG_TYPE_ZS6BKW,
)
from .dialogs.basic_antenna_dialog import BasicAntennaDialog
from .dialogs.beverage_dialog import BeverageDialog
from .dialogs.biquad_dialog import BiquadDialog
from .dialogs.custom_antenna_dialog import CustomAntennaDialog
from .dialogs.discone_dialog import DisconeDialog
from .dialogs.doublet_dialog import DoubletDialog
from .dialogs.endfed_dialog import EndFedDialog
from .dialogs.fan_dipole_dialog import FanDipoleDialog
from .dialogs.g5rv_dialog import G5RVDialog
from .dialogs.hexbeam_dialog import HexbeamDialog
from .dialogs.inverted_l_dialog import InvertedLDialog
from .dialogs.inverted_v_dialog import InvertedVDialog
from .dialogs.j_pole_dialog import JPoleDialog
from .dialogs.loaded_dipole_dialog import LoadedDipoleDialog
from .dialogs.log_periodic_dialog import LogPeriodicDialog
from .dialogs.magnetic_loop_dialog import MagneticLoopDialog
from .dialogs.moxon_dialog import MoxonDialog
from .dialogs.ocfd_dialog import OCFDDialog
from .dialogs.phased_vertical_dialog import PhasedVerticalDialog
from .dialogs.quad_beam_dialog import QuadBeamDialog
from .dialogs.ringo_dialog import RingoDialog
from .dialogs.scv_dialog import ScvDialog
from .dialogs.t2fd_dialog import T2FDDialog
from .dialogs.trap_dipole_dialog import TrapDipoleDialog
from .dialogs.trap_yagi_dialog import TrapYagiDialog
from .dialogs.vertical_dialog import VerticalDialog
from .dialogs.yagi_dialog import YagiDialog
from .dialogs.zepp_dialog import ZeppDialog
from .dialogs.zs6bkw_dialog import ZS6BKWDialog
from .i18n import Translator
from .units import UnitSystem

DEFAULT_START_FREQUENCY_HZ = 7_100_000.0


@dataclass(frozen=True, slots=True)
class CatalogContext:
    """Everything the catalog dialogs need from the current window."""

    parent: QWidget
    translator: Translator
    unit_system: UnitSystem
    solver: AntennaSolver | None = None
    matching_network: MatchingNetwork | None = None
    current_frequency_hz: float | None = None
    current_feed_line: FeedLine | None = None


@dataclass(frozen=True, slots=True)
class CatalogSelection:
    """A new-project selection returned by the New Antenna route."""

    parameters: AntennaDesignParameters
    default_name: str
    feed_line: FeedLine | None = None
    band_plan: BandPlan | None = None


@dataclass(frozen=True, slots=True)
class CatalogChange:
    """A Change Template selection returned to the main window."""

    parameters: AntennaDesignParameters
    feed_line: FeedLine | None = None


NewBuilder = Callable[[CatalogContext], CatalogSelection | None]
ChangeBuilder = Callable[[CatalogContext], CatalogChange | None]


def _accepted(dialog: QDialog) -> bool:
    return dialog.exec() == QDialog.DialogCode.Accepted


def _dialog_class(name: str) -> Callable[..., QDialog]:
    dialogs: dict[str, Callable[..., QDialog]] = {
        "BasicAntennaDialog": BasicAntennaDialog,
        "BeverageDialog": BeverageDialog,
        "BiquadDialog": BiquadDialog,
        "CustomAntennaDialog": CustomAntennaDialog,
        "DisconeDialog": DisconeDialog,
        "DoubletDialog": DoubletDialog,
        "EndFedDialog": EndFedDialog,
        "FanDipoleDialog": FanDipoleDialog,
        "G5RVDialog": G5RVDialog,
        "HexbeamDialog": HexbeamDialog,
        "InvertedLDialog": InvertedLDialog,
        "InvertedVDialog": InvertedVDialog,
        "JPoleDialog": JPoleDialog,
        "LoadedDipoleDialog": LoadedDipoleDialog,
        "LogPeriodicDialog": LogPeriodicDialog,
        "MagneticLoopDialog": MagneticLoopDialog,
        "MoxonDialog": MoxonDialog,
        "OCFDDialog": OCFDDialog,
        "PhasedVerticalDialog": PhasedVerticalDialog,
        "QuadBeamDialog": QuadBeamDialog,
        "RingoDialog": RingoDialog,
        "ScvDialog": ScvDialog,
        "T2FDDialog": T2FDDialog,
        "TrapDipoleDialog": TrapDipoleDialog,
        "TrapYagiDialog": TrapYagiDialog,
        "VerticalDialog": VerticalDialog,
        "YagiDialog": YagiDialog,
        "ZeppDialog": ZeppDialog,
        "ZS6BKWDialog": ZS6BKWDialog,
    }
    return dialogs[name]


def _dialog(
    name: str,
    context: CatalogContext,
    *,
    parent_keyword: bool = False,
    **kwargs: object,
) -> QDialog:
    dialog_class = _dialog_class(name)
    if parent_keyword:
        return dialog_class(
            context.translator,
            context.unit_system,
            parent=context.parent,
            **kwargs,
        )
    return dialog_class(context.translator, context.unit_system, context.parent, **kwargs)


def _result(dialog: QDialog, attribute: str | None) -> object:
    getter = getattr(dialog, "result_parameters" if attribute is None else attribute, None)
    if callable(getter):
        return cast(object, getter())
    if attribute == "typed_result_parameters":
        fallback = getattr(dialog, "result_parameters", None)
        if callable(fallback):
            return cast(object, fallback())
    raise AttributeError(f"{type(dialog).__name__} has no {attribute or 'result_parameters'}()")


def _current_frequency(context: CatalogContext) -> float:
    return context.current_frequency_hz or DEFAULT_START_FREQUENCY_HZ


def _new_simple(
    dialog_name: str,
    default_name: str | None,
    *,
    parameters_attr: str | None = None,
    feed_line_attr: str | None = None,
    band_plan_attr: str | None = None,
    parent_keyword: bool = False,
    kwargs: Mapping[str, object] | None = None,
    context_kwargs: Callable[[CatalogContext], dict[str, object]] | None = None,
) -> NewBuilder:
    def build(context: CatalogContext) -> CatalogSelection | None:
        extra = dict(kwargs or {})
        if context_kwargs is not None:
            extra.update(context_kwargs(context))
        dialog = _dialog(
            dialog_name,
            context,
            parent_keyword=parent_keyword,
            **extra,
        )
        if not _accepted(dialog):
            return None
        parameters = cast(AntennaDesignParameters, _result(dialog, parameters_attr))
        name = default_name or str(getattr(parameters, "template_name", "Antenna"))
        return CatalogSelection(
            parameters=parameters,
            default_name=name,
            feed_line=getattr(dialog, feed_line_attr)() if feed_line_attr else None,
            band_plan=getattr(dialog, band_plan_attr)() if band_plan_attr else None,
        )

    return build


def _new_basic(
    antenna_type: str,
    default_name: str,
    *,
    initial_sides: int | None = None,
) -> NewBuilder:
    def build(context: CatalogContext) -> CatalogSelection | None:
        dialog = _dialog_class("BasicAntennaDialog")(
            context.translator,
            context.unit_system,
            context.parent,
            antenna_type=antenna_type,
            frequency_hz=_current_frequency(context),
            initial_sides=initial_sides,
        )
        if not _accepted(dialog):
            return None
        return CatalogSelection(
            cast(AntennaDesignParameters, _result(dialog, None)),
            default_name,
        )

    return build


def _new_endfed(preset: EndFedPreset, default_name: str) -> NewBuilder:
    return _new_simple(
        "EndFedDialog",
        default_name,
        band_plan_attr="result_band_plan",
        kwargs={"preset": preset},
        context_kwargs=lambda context: {
            "solver": context.solver,
            "project_matching_network": context.matching_network,
        },
    )


def _new_j_pole(*, folded: bool) -> NewBuilder:
    def build(context: CatalogContext) -> CatalogSelection | None:
        dialog = _dialog_class("JPoleDialog")(
            context.translator,
            context.unit_system,
            context.parent,
        )
        if not _accepted(dialog):
            return None
        parameters = cast(Any, _result(dialog, None))
        if folded:
            parameters = replace(parameters, folded=True)
        return CatalogSelection(parameters, "Slim Jim" if folded else "J Pole")

    return build


NEW_BUILDERS: dict[str, NewBuilder] = {
    CATALOG_TYPE_WIRE_DIPOLE: _new_basic(CATALOG_TYPE_WIRE_DIPOLE, "Wire dipole"),
    CATALOG_TYPE_FOLDED_DIPOLE: _new_basic(
        CATALOG_TYPE_FOLDED_DIPOLE,
        "Folded dipole",
    ),
    CATALOG_TYPE_LOOP: _new_basic(CATALOG_TYPE_LOOP, "Loop"),
    CATALOG_TYPE_DELTA_LOOP: _new_basic(
        CATALOG_TYPE_LOOP,
        "Delta loop",
        initial_sides=3,
    ),
    CATALOG_TYPE_QUAD_LOOP: _new_basic(
        CATALOG_TYPE_LOOP,
        "Quad loop",
        initial_sides=4,
    ),
    CATALOG_TYPE_CUSTOM: _new_simple(
        "CustomAntennaDialog",
        "Custom antenna",
        parent_keyword=True,
    ),
    CATALOG_TYPE_YAGI: _new_simple("YagiDialog", "Yagi"),
    CATALOG_TYPE_MOXON: _new_simple("MoxonDialog", "Moxon"),
    CATALOG_TYPE_RINGO: _new_simple("RingoDialog", "Ringo"),
    CATALOG_TYPE_MAGNETIC_LOOP: _new_simple("MagneticLoopDialog", "Magnetic loop"),
    CATALOG_TYPE_OCFD: _new_simple(
        "OCFDDialog",
        "OCFD",
        band_plan_attr="result_band_plan",
    ),
    CATALOG_TYPE_VERTICAL: _new_simple("VerticalDialog", "Vertical"),
    CATALOG_TYPE_LOADED_VERTICAL: _new_simple(
        "VerticalDialog",
        "Loaded vertical",
        kwargs={"mobile": True},
    ),
    CATALOG_TYPE_INVERTED_V: _new_simple("InvertedVDialog", "Inverted V"),
    CATALOG_TYPE_INVERTED_L: _new_simple("InvertedLDialog", "Inverted L"),
    CATALOG_TYPE_FAN_DIPOLE: _new_simple("FanDipoleDialog", "Fan dipole"),
    CATALOG_TYPE_TRAP_DIPOLE: _new_simple("TrapDipoleDialog", "Trap dipole"),
    CATALOG_TYPE_T2FD: _new_simple("T2FDDialog", "T2FD"),
    CATALOG_TYPE_ENDFED: _new_endfed(EndFedPreset.STANDARD, "End-fed"),
    CATALOG_TYPE_SLOPER: _new_endfed(EndFedPreset.SLOPER, "Sloper"),
    CATALOG_TYPE_RANDOM_WIRE: _new_endfed(EndFedPreset.RANDOM_WIRE, "Random wire"),
    CATALOG_TYPE_SHORTENED_ENDFED_80_10: _new_endfed(
        EndFedPreset.SHORTENED_80_10,
        "Shortened EFHW 80-10 m",
    ),
    CATALOG_TYPE_SHORTENED_ENDFED_40_10: _new_endfed(
        EndFedPreset.SHORTENED_40_10,
        "Shortened EFHW 40-20-10 m",
    ),
    CATALOG_TYPE_DOUBLET: _new_simple(
        "DoubletDialog",
        "Doublet",
        feed_line_attr="result_feed_line",
    ),
    CATALOG_TYPE_G5RV: _new_simple(
        "G5RVDialog",
        "G5RV",
        parameters_attr="typed_result_parameters",
    ),
    CATALOG_TYPE_ZS6BKW: _new_simple(
        "ZS6BKWDialog",
        "ZS6BKW",
        parameters_attr="typed_result_parameters",
    ),
    CATALOG_TYPE_ZEPP: _new_simple(
        "ZeppDialog",
        "Zepp",
        parameters_attr="typed_result_parameters",
    ),
    CATALOG_TYPE_J_POLE: _new_j_pole(folded=False),
    CATALOG_TYPE_SLIM_JIM: _new_j_pole(folded=True),
    CATALOG_TYPE_HALF_SQUARE: _new_simple(
        "ScvDialog",
        ScvKind.HALF_SQUARE.template_name,
        kwargs={"kind": ScvKind.HALF_SQUARE},
    ),
    CATALOG_TYPE_BOBTAIL_CURTAIN: _new_simple(
        "ScvDialog",
        ScvKind.BOBTAIL_CURTAIN.template_name,
        kwargs={"kind": ScvKind.BOBTAIL_CURTAIN},
    ),
    CATALOG_TYPE_BIQUAD: _new_simple(
        "BiquadDialog",
        BiquadKind.SINGLE.template_name,
        kwargs={"kind": BiquadKind.SINGLE},
    ),
    CATALOG_TYPE_DOUBLE_BIQUAD: _new_simple(
        "BiquadDialog",
        BiquadKind.DOUBLE.template_name,
        kwargs={"kind": BiquadKind.DOUBLE},
    ),
    CATALOG_TYPE_BEVERAGE: _new_simple("BeverageDialog", "Beverage"),
    CATALOG_TYPE_LOADED_DIPOLE: _new_simple("LoadedDipoleDialog", None),
    CATALOG_TYPE_PHASED_VERTICAL: _new_simple("PhasedVerticalDialog", None),
    CATALOG_TYPE_QUAD_BEAM: _new_simple(
        "QuadBeamDialog",
        None,
        context_kwargs=lambda context: {"frequency_hz": context.current_frequency_hz},
    ),
    CATALOG_TYPE_LOG_PERIODIC: _new_simple("LogPeriodicDialog", None),
    CATALOG_TYPE_DISCONE: _new_simple("DisconeDialog", None),
    CATALOG_TYPE_TRAP_YAGI: _new_simple("TrapYagiDialog", None),
    CATALOG_TYPE_HEXBEAM: _new_simple("HexbeamDialog", None),
}


def _change_simple(
    dialog_name: str,
    *,
    parameters_attr: str | None = None,
    feed_line_attr: str | None = None,
    parent_keyword: bool = False,
    kwargs: Mapping[str, object] | None = None,
    omit_frequency: bool = False,
    context_kwargs: Callable[[CatalogContext], dict[str, object]] | None = None,
) -> ChangeBuilder:
    def build(context: CatalogContext) -> CatalogChange | None:
        extra = dict(kwargs or {})
        if not omit_frequency:
            extra["frequency_hz"] = context.current_frequency_hz
        if context_kwargs is not None:
            extra.update(context_kwargs(context))
        dialog = _dialog(
            dialog_name,
            context,
            parent_keyword=parent_keyword,
            **extra,
        )
        if not _accepted(dialog):
            return None
        return CatalogChange(
            parameters=cast(AntennaDesignParameters, _result(dialog, parameters_attr)),
            feed_line=getattr(dialog, feed_line_attr)() if feed_line_attr else None,
        )

    return build


def _change_basic(
    antenna_type: str,
    *,
    initial_sides: int | None = None,
) -> ChangeBuilder:
    def build(context: CatalogContext) -> CatalogChange | None:
        dialog = _dialog_class("BasicAntennaDialog")(
            context.translator,
            context.unit_system,
            context.parent,
            antenna_type=antenna_type,
            frequency_hz=_current_frequency(context),
            initial_sides=initial_sides,
        )
        if not _accepted(dialog):
            return None
        return CatalogChange(cast(AntennaDesignParameters, _result(dialog, None)))

    return build


def _change_endfed(
    *,
    preset: EndFedPreset | None = None,
    omit_frequency: bool = False,
) -> ChangeBuilder:
    def context_kwargs(context: CatalogContext) -> dict[str, object]:
        extra: dict[str, object] = {
            "solver": context.solver,
            "project_matching_network": context.matching_network,
        }
        if preset is not None:
            extra["preset"] = preset
        return extra

    return _change_simple(
        "EndFedDialog",
        omit_frequency=omit_frequency,
        context_kwargs=context_kwargs,
    )


def _change_j_pole(*, folded: bool) -> ChangeBuilder:
    def build(context: CatalogContext) -> CatalogChange | None:
        dialog = _dialog_class("JPoleDialog")(
            context.translator,
            context.unit_system,
            context.parent,
            frequency_hz=context.current_frequency_hz,
        )
        if not _accepted(dialog):
            return None
        parameters = cast(Any, _result(dialog, None))
        if folded:
            parameters = replace(parameters, folded=True)
        return CatalogChange(parameters)

    return build


CHANGE_BUILDERS: dict[str, ChangeBuilder] = {
    CATALOG_TYPE_WIRE_DIPOLE: _change_basic(CATALOG_TYPE_WIRE_DIPOLE),
    CATALOG_TYPE_FOLDED_DIPOLE: _change_basic(CATALOG_TYPE_FOLDED_DIPOLE),
    CATALOG_TYPE_LOOP: _change_basic(CATALOG_TYPE_LOOP),
    CATALOG_TYPE_DELTA_LOOP: _change_basic(CATALOG_TYPE_LOOP, initial_sides=3),
    CATALOG_TYPE_QUAD_LOOP: _change_basic(CATALOG_TYPE_LOOP, initial_sides=4),
    CATALOG_TYPE_CUSTOM: _change_simple(
        "CustomAntennaDialog",
        parent_keyword=True,
    ),
    CATALOG_TYPE_YAGI: _change_simple("YagiDialog"),
    CATALOG_TYPE_MOXON: _change_simple("MoxonDialog"),
    CATALOG_TYPE_RINGO: _change_simple("RingoDialog"),
    CATALOG_TYPE_MAGNETIC_LOOP: _change_simple("MagneticLoopDialog"),
    CATALOG_TYPE_OCFD: _change_simple("OCFDDialog"),
    CATALOG_TYPE_VERTICAL: _change_simple("VerticalDialog"),
    CATALOG_TYPE_LOADED_VERTICAL: _change_simple(
        "VerticalDialog",
        kwargs={"mobile": True},
    ),
    CATALOG_TYPE_INVERTED_V: _change_simple("InvertedVDialog"),
    CATALOG_TYPE_INVERTED_L: _change_simple("InvertedLDialog"),
    CATALOG_TYPE_FAN_DIPOLE: _change_simple("FanDipoleDialog"),
    CATALOG_TYPE_TRAP_DIPOLE: _change_simple("TrapDipoleDialog"),
    CATALOG_TYPE_T2FD: _change_simple("T2FDDialog"),
    CATALOG_TYPE_ENDFED: _change_endfed(),
    CATALOG_TYPE_SLOPER: _change_endfed(preset=EndFedPreset.SLOPER),
    CATALOG_TYPE_RANDOM_WIRE: _change_endfed(preset=EndFedPreset.RANDOM_WIRE),
    CATALOG_TYPE_SHORTENED_ENDFED_80_10: _change_endfed(
        preset=EndFedPreset.SHORTENED_80_10,
        omit_frequency=True,
    ),
    CATALOG_TYPE_SHORTENED_ENDFED_40_10: _change_endfed(
        preset=EndFedPreset.SHORTENED_40_10,
        omit_frequency=True,
    ),
    CATALOG_TYPE_DOUBLET: _change_simple(
        "DoubletDialog",
        parameters_attr="parameters",
        feed_line_attr="feed_line",
        context_kwargs=lambda context: {"feed_line": context.current_feed_line},
    ),
    CATALOG_TYPE_G5RV: _change_simple(
        "G5RVDialog",
        parameters_attr="typed_result_parameters",
    ),
    CATALOG_TYPE_ZS6BKW: _change_simple(
        "ZS6BKWDialog",
        parameters_attr="typed_result_parameters",
    ),
    CATALOG_TYPE_ZEPP: _change_simple(
        "ZeppDialog",
        parameters_attr="typed_result_parameters",
    ),
    CATALOG_TYPE_J_POLE: _change_j_pole(folded=False),
    CATALOG_TYPE_SLIM_JIM: _change_j_pole(folded=True),
    CATALOG_TYPE_HALF_SQUARE: _change_simple(
        "ScvDialog",
        kwargs={"kind": ScvKind.HALF_SQUARE},
    ),
    CATALOG_TYPE_BOBTAIL_CURTAIN: _change_simple(
        "ScvDialog",
        kwargs={"kind": ScvKind.BOBTAIL_CURTAIN},
    ),
    CATALOG_TYPE_BIQUAD: _change_simple(
        "BiquadDialog",
        kwargs={"kind": BiquadKind.SINGLE},
    ),
    CATALOG_TYPE_DOUBLE_BIQUAD: _change_simple(
        "BiquadDialog",
        kwargs={"kind": BiquadKind.DOUBLE},
    ),
    CATALOG_TYPE_BEVERAGE: _change_simple("BeverageDialog"),
    CATALOG_TYPE_LOADED_DIPOLE: _change_simple("LoadedDipoleDialog"),
    CATALOG_TYPE_PHASED_VERTICAL: _change_simple("PhasedVerticalDialog"),
    CATALOG_TYPE_QUAD_BEAM: _change_simple("QuadBeamDialog"),
    CATALOG_TYPE_LOG_PERIODIC: _change_simple("LogPeriodicDialog"),
    CATALOG_TYPE_DISCONE: _change_simple("DisconeDialog"),
    CATALOG_TYPE_TRAP_YAGI: _change_simple("TrapYagiDialog"),
    CATALOG_TYPE_HEXBEAM: _change_simple("HexbeamDialog"),
}


def new_antenna_selection(
    context: CatalogContext,
    key: str,
) -> CatalogSelection | None:
    """Return the New Antenna selection for ``key``, or None on cancel."""

    builder = NEW_BUILDERS.get(key)
    if builder is None:
        return None
    return builder(context)


def change_template_selection(
    context: CatalogContext,
    key: str,
) -> CatalogChange | None:
    """Return the Change Template selection for ``key``, or None on cancel."""

    builder = CHANGE_BUILDERS.get(key)
    if builder is None:
        return None
    return builder(context)
