# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolve the constructive feed connection for one design.

The canonical model only stores a feed point. This module adds the physical
wiring detail used by the design panel, the construction sheet, and the
reports. It never feeds the solver.
"""

from __future__ import annotations

from ..antennas.antenna import AntennaModel
from ..antennas.balun import BalunLoss
from ..antennas.biquad import BiquadParameters
from ..antennas.design import AntennaDesignParameters
from ..antennas.dipole import DipoleParameters
from ..antennas.discone import DisconeParameters
from ..antennas.endfed import EndFedParameters
from ..antennas.fan_dipole import FanDipoleParameters
from ..antennas.feed_connection import (
    BalunRequirement,
    FeedBalance,
    FeedConnection,
    FeedConnectionDetail,
    FeedInterface,
    FeedTerminal,
    FeedTopology,
)
from ..antennas.feed_line import FeedLine
from ..antennas.flower_pot import (
    BOTTOM_RADIATOR_ID,
    TOP_RADIATOR_ID,
    FlowerPotParameters,
)
from ..antennas.folded_dipole import FoldedDipoleParameters
from ..antennas.hexbeam import HexbeamParameters
from ..antennas.inverted_l import InvertedLParameters
from ..antennas.inverted_v import InvertedVParameters
from ..antennas.j_pole import JPoleParameters
from ..antennas.loaded_dipole import LoadedDipoleParameters
from ..antennas.log_periodic import LogPeriodicParameters
from ..antennas.loop import LoopParameters
from ..antennas.magnetic_loop import MagneticLoopParameters
from ..antennas.moxon import MoxonParameters
from ..antennas.ocfd import OCFDParameters
from ..antennas.phased_vertical import PhasedVerticalParameters
from ..antennas.quad_beam import QuadBeamParameters
from ..antennas.ringo import RingoParameters
from ..antennas.scv import ScvParameters
from ..antennas.stacked_yagi import (
    StackedYagiFeedMode,
    StackedYagiParameters,
)
from ..antennas.t2fd import T2FDParameters
from ..antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..antennas.trap_dipole import TrapDipoleParameters
from ..antennas.trap_yagi import TrapYagiParameters
from ..antennas.vertical import VerticalParameters
from ..antennas.yagi import YagiMatchType, YagiParameters
from ..antennas.zepp import ZeppParameters
from .feed_balance import feed_balance, requires_current_balun

_CURRENT_BALUN = "1:1 current balun/choke"
_IDEAL_TRANSFORMER = "ideal transformer"
_GAMMA_LIMITATION = "Gamma and delta matches are not modeled."


def _center_terminals(model: AntennaModel) -> tuple[FeedTerminal, FeedTerminal]:
    wire = model.feed_wire
    return (
        FeedTerminal("A", wire.id, model.feed.offset_m, "before"),
        FeedTerminal("B", wire.id, model.feed.offset_m, "after"),
    )


def _base_terminals(model: AntennaModel) -> tuple[FeedTerminal, FeedTerminal]:
    wire = model.feed_wire
    return (
        FeedTerminal("A", wire.id, model.feed.offset_m, "start"),
        FeedTerminal("B", None, None, "ground"),
    )


def _flower_pot_terminals(model: AntennaModel) -> tuple[FeedTerminal, FeedTerminal]:
    top = model.wire_by_id(TOP_RADIATOR_ID)
    bottom = model.wire_by_id(BOTTOM_RADIATOR_ID)
    return (
        FeedTerminal("A", top.id, model.feed.offset_m, "start"),
        FeedTerminal("B", bottom.id, bottom.length_m, "end"),
    )


def _end_terminals(model: AntennaModel) -> tuple[FeedTerminal, FeedTerminal]:
    wire = model.feed_wire
    return (
        FeedTerminal("A", wire.id, model.feed.offset_m, "start"),
        FeedTerminal("B", None, None, "counterpoise"),
    )


def _gap_terminals(model: AntennaModel) -> tuple[FeedTerminal, FeedTerminal]:
    wire = model.feed_wire
    return (
        FeedTerminal("A", wire.id, 0.0, "start"),
        FeedTerminal("B", wire.id, wire.length_m, "end"),
    )


def _connections(
    interface: FeedInterface,
    terminals: tuple[FeedTerminal, FeedTerminal],
) -> tuple[FeedConnection, ...]:
    first, second = terminals
    if interface is FeedInterface.DIRECT_COAX:
        return (
            FeedConnection(first.role, "Coax center", "Direct connection"),
            FeedConnection(second.role, "Coax shield", "Direct connection"),
        )
    if interface is FeedInterface.CURRENT_BALUN:
        return (
            FeedConnection(first.role, "Balun balanced A", "Balanced output"),
            FeedConnection(second.role, "Balun balanced B", "Balanced output"),
            FeedConnection("Coax center", "Balun input center", "Unbalanced input"),
            FeedConnection("Coax shield", "Balun input shield", "Unbalanced input"),
        )
    if interface is FeedInterface.TRANSFORMER:
        return (
            FeedConnection(first.role, "Transformer secondary A", "Balanced output"),
            FeedConnection(second.role, "Transformer secondary B", "Balanced output"),
            FeedConnection("Coax center", "Transformer primary center", "Unbalanced input"),
            FeedConnection("Coax shield", "Transformer primary shield", "Unbalanced input"),
        )
    if interface is FeedInterface.BALANCED_LINE:
        return (
            FeedConnection(first.role, "Balanced line A", "Balanced line"),
            FeedConnection(second.role, "Balanced line B", "Balanced line"),
        )
    if interface is FeedInterface.MULTI_PORT:
        return (
            FeedConnection(first.role, "Primary port", "Primary feed"),
            FeedConnection(second.role, "Ground / radials", "Return path"),
        )
    return (
        FeedConnection(first.role, "Not classified", "Verify before construction"),
        FeedConnection(second.role, "Not classified", "Verify before construction"),
    )


def _ratio(parameters: AntennaDesignParameters) -> float | None:
    value = (
        parameters.feed_transformer_ratio
        if isinstance(parameters, LogPeriodicParameters)
        else getattr(parameters, "transformer_ratio", None)
    )
    if value is None or float(value) == 1.0:
        return None
    return float(value)


def _summary(
    parameters: AntennaDesignParameters,
    topology: FeedTopology,
    interface: FeedInterface,
    balance: FeedBalance,
    ratio: float | None,
) -> str:
    if isinstance(parameters, FlowerPotParameters):
        return (
            "Coax center to the top radiator, shield to the bottom radiator; "
            "integrated resonant choke at the base of the lower radiator; no "
            "separate balun."
        )
    if topology is FeedTopology.LOOP_GAP:
        return "Loop gap: A and B across the gap; verify the coupling or matching method."
    if topology is FeedTopology.APEX_GAP:
        return "Apex gap: A and B across the gap; verify the center/shield assignment."
    if interface is FeedInterface.CURRENT_BALUN:
        return "A and B to a 1:1 current balun; coax center and shield to its input."
    if interface is FeedInterface.TRANSFORMER and ratio is not None:
        return "A and B to a transformer/balun; coax center and shield to its input."
    if interface is FeedInterface.BALANCED_LINE:
        return "A and B to the balanced feed line; the balun location depends on the tuner."
    if interface is FeedInterface.MULTI_PORT:
        return "Primary port plus additional sources; the combining network is not modeled."
    if interface is FeedInterface.UNKNOWN:
        return "Connection not classified; verify the wiring before construction."
    if balance is FeedBalance.BALANCED:
        return (
            "Direct coax: A to the center conductor and B to the shield; "
            "a current balun/choke is recommended."
        )
    return "Direct coax: A to the radiator and B to the ground or return."


def _facts(
    *,
    parameters: AntennaDesignParameters,
    balun_requirement: BalunRequirement,
    interface: FeedInterface,
    ratio: float | None,
    current_balun: bool,
    feed_line: FeedLine | None,
    balun_loss: BalunLoss | None,
    topology: FeedTopology,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    modeled = ["Ideal source at the feed point"]
    if ratio is not None:
        modeled.append("Ideal feed transformer")
    recorded: list[str] = []
    if current_balun:
        recorded.append("Current balun/choke installed")
    if feed_line is not None and feed_line.is_active:
        recorded.append("Feed line configured")
    if balun_loss is not None and balun_loss.is_active:
        recorded.append("Balun/unun loss configured")

    recommended: list[str] = []
    if isinstance(parameters, FlowerPotParameters):
        recommended.append(
            "Use the integrated common-mode choke at the base of the lower radiator; "
            "no separate current balun"
        )
    elif balun_requirement is BalunRequirement.REQUIRED:
        if interface is FeedInterface.TRANSFORMER and ratio is not None:
            recommended.append("Use a current balun/transformer at the modeled ratio")
        else:
            recommended.append("Install a 1:1 current balun/choke at the feed point")
    elif balun_requirement is BalunRequirement.RECOMMENDED:
        recommended.append("A 1:1 current balun/choke is recommended")
    elif balun_requirement is BalunRequirement.NOT_REQUIRED:
        recommended.append("No current balun is required by this family")
        recommended.append("Verify the shield, ground, and return connection")
    else:
        recommended.append("Verify the feed transition; this family is not classified")

    not_modeled = [
        "Common-mode current on the coax shield",
        "Balun balance, frequency response, and power handling",
        "Coax shield radiation and connector loss",
    ]
    if (
        isinstance(parameters, YagiParameters)
        and parameters.match_type is YagiMatchType.NONE
        and not parameters.driven_folded
    ):
        not_modeled.append(_GAMMA_LIMITATION)
    if topology is FeedTopology.UNKNOWN:
        not_modeled.append("The physical center/shield assignment is not classified")
    return tuple(modeled), tuple(recorded), tuple(recommended), tuple(not_modeled)


def _steps(
    parameters: AntennaDesignParameters,
    *,
    topology: FeedTopology,
    interface: FeedInterface,
) -> tuple[str, ...]:
    steps = [
        "Cut or prepare the feed gap and leave clearance for the feed hardware.",
        "Connect terminal A and terminal B to the interface as shown.",
        "Seal the connector, provide strain relief, and form a drip loop.",
    ]
    if interface in (FeedInterface.CURRENT_BALUN, FeedInterface.TRANSFORMER):
        steps.append("Connect the coax center and shield to the balun or transformer input.")
    elif interface is FeedInterface.BALANCED_LINE:
        steps.append("Keep the balanced line pair together and verify the tuner-side balun.")
    elif interface is FeedInterface.MULTI_PORT:
        steps.append("Build the combining network separately; it is not part of the antenna model.")
    if isinstance(parameters, FlowerPotParameters):
        steps.append(
            "Form the common-mode choke below the lower radiator and verify its "
            "resonance with the installed coax."
        )
    elif topology in (
        FeedTopology.BASE_FED_VERTICAL,
        FeedTopology.END_FED,
        FeedTopology.END_FED_STUB,
        FeedTopology.APEX_GAP,
    ):
        steps.append("Verify the shield, ground, radial, or counterpoise return path.")
    return tuple(steps)


def _limitations(
    parameters: AntennaDesignParameters,
    *,
    topology: FeedTopology,
    interface: FeedInterface,
) -> tuple[str, ...]:
    limitations = [
        "This is a construction aid, not a solver result.",
        "The app does not model common-mode current or coax shield radiation.",
        "The feed gap is not modeled; record it as an as-built dimension.",
    ]
    if interface is FeedInterface.TRANSFORMER:
        limitations.append(
            "The transformer is ideal; verify the real balun ratio and power rating."
        )
    if topology is FeedTopology.UNKNOWN:
        limitations.append(
            "The center/shield assignment is not classified; verify it on the build."
        )
    if topology is FeedTopology.BETA_HAIRPIN:
        limitations.append("The hairpin is a matching stub, not a balun.")
    if isinstance(parameters, FlowerPotParameters):
        limitations.append(
            "The integrated choke is ideal; its impedance, self-resonance, and "
            "power handling are not modeled."
        )
    return tuple(limitations)


def _classify(
    parameters: AntennaDesignParameters,
    model: AntennaModel,
    *,
    current_balun: bool,
) -> tuple[
    FeedTopology,
    FeedInterface,
    tuple[FeedTerminal, FeedTerminal],
    str | None,
    float | None,
    float | None,
]:
    ratio = _ratio(parameters)
    gap = getattr(parameters, "feed_gap_m", None) or getattr(parameters, "disc_gap_m", None)

    if isinstance(parameters, YagiParameters):
        if parameters.match_type is YagiMatchType.BETA_HAIRPIN:
            return (
                FeedTopology.BETA_HAIRPIN,
                FeedInterface.CURRENT_BALUN if current_balun else FeedInterface.DIRECT_COAX,
                _gap_terminals(model),
                "Beta/hairpin matching stub; it is not a balun",
                None,
                None,
            )
        if parameters.driven_folded:
            return (
                FeedTopology.FOLDED_DIPOLE,
                (FeedInterface.TRANSFORMER if ratio is not None else FeedInterface.CURRENT_BALUN),
                _center_terminals(model),
                "Conductor B is continuous and connected at both ends; it is not a parasitic",
                ratio,
                None,
            )
        return (
            FeedTopology.CENTER_FED_DIPOLE,
            FeedInterface.CURRENT_BALUN if current_balun else FeedInterface.DIRECT_COAX,
            _center_terminals(model),
            "Tapered driven element" if parameters.is_tapered else None,
            ratio,
            None,
        )

    if isinstance(parameters, LogPeriodicParameters):
        return (
            FeedTopology.CENTER_FED_DIPOLE,
            (
                FeedInterface.TRANSFORMER
                if ratio is not None
                else FeedInterface.CURRENT_BALUN
                if current_balun
                else FeedInterface.DIRECT_COAX
            ),
            _center_terminals(model),
            "Transposed phase line; the rear element terminates the line",
            ratio,
            None,
        )

    if isinstance(
        parameters,
        (
            DipoleParameters,
            InvertedVParameters,
            FanDipoleParameters,
            LoadedDipoleParameters,
            TrapDipoleParameters,
            MoxonParameters,
            TrapYagiParameters,
            HexbeamParameters,
        ),
    ):
        return (
            FeedTopology.CENTER_FED_DIPOLE,
            FeedInterface.CURRENT_BALUN if current_balun else FeedInterface.DIRECT_COAX,
            _center_terminals(model),
            None,
            ratio,
            float(gap) if gap is not None else None,
        )

    if isinstance(parameters, FoldedDipoleParameters):
        return (
            FeedTopology.FOLDED_DIPOLE,
            (FeedInterface.TRANSFORMER if ratio is not None else FeedInterface.CURRENT_BALUN),
            _center_terminals(model),
            "Conductor B is continuous and connected at both ends; it is not a parasitic",
            ratio,
            None,
        )

    if isinstance(parameters, OCFDParameters):
        return (
            FeedTopology.OFF_CENTER_FED_DIPOLE,
            (
                FeedInterface.TRANSFORMER
                if ratio is not None
                else FeedInterface.CURRENT_BALUN
                if current_balun
                else FeedInterface.DIRECT_COAX
            ),
            _center_terminals(model),
            "Off-center feed; verify the actual transformer ratio",
            ratio,
            None,
        )

    if isinstance(
        parameters,
        (
            LoopParameters,
            MagneticLoopParameters,
            BiquadParameters,
            QuadBeamParameters,
            T2FDParameters,
        ),
    ):
        return (
            FeedTopology.LOOP_GAP,
            FeedInterface.TRANSFORMER if ratio is not None else FeedInterface.DIRECT_COAX,
            _center_terminals(model),
            "Loop feed at a gap or matching section" if ratio is None else None,
            ratio,
            float(gap) if gap is not None else None,
        )

    if isinstance(parameters, FlowerPotParameters):
        return (
            FeedTopology.BASE_FED_VERTICAL,
            FeedInterface.DIRECT_COAX,
            _flower_pot_terminals(model),
            "Integrated choke at the base of the lower radiator",
            None,
            None,
        )

    if isinstance(parameters, (VerticalParameters, InvertedLParameters, RingoParameters)):
        return (
            FeedTopology.BASE_FED_VERTICAL,
            FeedInterface.DIRECT_COAX,
            _base_terminals(model),
            None,
            None,
            None,
        )

    if isinstance(parameters, EndFedParameters):
        return (
            FeedTopology.END_FED,
            FeedInterface.TRANSFORMER if ratio is not None else FeedInterface.DIRECT_COAX,
            _end_terminals(model),
            "Counterpoise or installation return is required",
            ratio,
            None,
        )

    if isinstance(parameters, (ZeppParameters, JPoleParameters)):
        return (
            FeedTopology.END_FED_STUB,
            FeedInterface.CURRENT_BALUN if current_balun else FeedInterface.DIRECT_COAX,
            _end_terminals(model),
            "The stub is a matching section, not a balun",
            None,
            None,
        )

    if isinstance(parameters, DisconeParameters):
        return (
            FeedTopology.APEX_GAP,
            FeedInterface.DIRECT_COAX,
            _gap_terminals(model),
            "Verify the center/shield assignment at the apex",
            None,
            float(gap) if gap is not None else None,
        )

    if isinstance(parameters, ScvParameters):
        return (
            FeedTopology.TOP_JUNCTION_FEED,
            FeedInterface.DIRECT_COAX,
            _base_terminals(model),
            "Top-junction feed; matching and ground return are not modeled",
            None,
            None,
        )

    if isinstance(parameters, PhasedVerticalParameters):
        return (
            FeedTopology.MULTI_PORT,
            FeedInterface.MULTI_PORT,
            _center_terminals(model),
            "Primary port plus additional sources; the combining network is ideal",
            None,
            None,
        )

    if isinstance(parameters, StackedYagiParameters):
        return (
            FeedTopology.MULTI_PORT,
            FeedInterface.MULTI_PORT,
            _center_terminals(model),
            (
                "Splitter node is the primary input; lossless TLs feed every level; "
                "matched line loss is applied to gain, but mismatch-dependent loss and "
                "splitter internal mismatch are not modeled"
                if parameters.feed.mode is StackedYagiFeedMode.NETWORK
                else "Level 1 is the primary port; splitter + phase lines, with ideal "
                "sources, no line impedance transformation, and no line loss"
                if parameters.feed.mode is StackedYagiFeedMode.PHASE_LINES
                else (
                    "Level 1 is the primary port; levels 2-N are ideal sources "
                    "and the split is ideal"
                )
            ),
            None,
            None,
        )

    if isinstance(parameters, TransmissionLineDoubletParameters):
        return (
            FeedTopology.CENTER_FED_DIPOLE,
            FeedInterface.BALANCED_LINE,
            _center_terminals(model),
            "Balanced feed line; the balun location depends on the tuner",
            None,
            None,
        )

    return (
        FeedTopology.UNKNOWN,
        FeedInterface.UNKNOWN,
        _center_terminals(model),
        "Custom or unclassified geometry; verify the center/shield assignment",
        None,
        None,
    )


def feed_connection_detail(
    parameters: AntennaDesignParameters,
    model: AntennaModel,
    *,
    current_balun: bool = False,
    feed_line: FeedLine | None = None,
    balun_loss: BalunLoss | None = None,
) -> FeedConnectionDetail:
    """Return the constructive feed detail for ``parameters`` and ``model``."""

    balance = feed_balance(parameters)
    requirement = (
        BalunRequirement.NOT_REQUIRED
        if isinstance(parameters, FlowerPotParameters)
        else BalunRequirement.REQUIRED
        if requires_current_balun(parameters)
        else BalunRequirement.NOT_REQUIRED
        if balance is FeedBalance.UNBALANCED
        else BalunRequirement.UNKNOWN
    )
    topology, interface, terminals, match_hardware, ratio, gap = _classify(
        parameters,
        model,
        current_balun=current_balun,
    )
    modeled, recorded, recommended, not_modeled = _facts(
        parameters=parameters,
        balun_requirement=requirement,
        interface=interface,
        ratio=ratio,
        current_balun=current_balun,
        feed_line=feed_line,
        balun_loss=balun_loss,
        topology=topology,
    )
    return FeedConnectionDetail(
        topology=topology,
        interface=interface,
        balance=balance,
        balun_requirement=requirement,
        terminals=terminals,
        connections=_connections(interface, terminals),
        summary=_summary(parameters, topology, interface, balance, ratio),
        transformer_ratio=ratio,
        match_hardware=match_hardware,
        gap_m=gap,
        modeled=modeled,
        recorded=recorded,
        recommended=recommended,
        not_modeled=not_modeled,
        steps=_steps(parameters, topology=topology, interface=interface),
        limitations=_limitations(parameters, topology=topology, interface=interface),
    )
