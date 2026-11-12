# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-balance classification for construction guidance.

The simulator models ideal transformers but not common-mode current.  This
module identifies the families whose physical feed is balanced and therefore
normally needs a current balun or choke.  It is a construction note, not an
electromagnetic model.
"""

from __future__ import annotations

from enum import StrEnum

from ..antennas.biquad import BiquadParameters
from ..antennas.custom import CustomAntennaParameters
from ..antennas.design import AntennaDesignParameters
from ..antennas.dipole import DipoleParameters
from ..antennas.folded_dipole import FoldedDipoleParameters
from ..antennas.hexbeam import HexbeamParameters
from ..antennas.inverted_v import InvertedVParameters
from ..antennas.loaded_dipole import LoadedDipoleParameters
from ..antennas.loop import LoopParameters
from ..antennas.magnetic_loop import MagneticLoopParameters
from ..antennas.moxon import MoxonParameters
from ..antennas.ocfd import OCFDParameters
from ..antennas.quad_beam import QuadBeamParameters
from ..antennas.scv import ScvParameters
from ..antennas.t2fd import T2FDParameters
from ..antennas.transmission_line_doublet import TransmissionLineDoubletParameters
from ..antennas.trap_dipole import TrapDipoleParameters
from ..antennas.trap_yagi import TrapYagiParameters
from ..antennas.yagi import YagiParameters
from ..antennas.zepp import ZeppParameters


class FeedBalance(StrEnum):
    BALANCED = "balanced"
    UNBALANCED = "unbalanced"
    UNKNOWN = "unknown"


_BALANCED_TYPES = (
    BiquadParameters,
    DipoleParameters,
    FoldedDipoleParameters,
    HexbeamParameters,
    InvertedVParameters,
    LoadedDipoleParameters,
    LoopParameters,
    MoxonParameters,
    OCFDParameters,
    QuadBeamParameters,
    ScvParameters,
    T2FDParameters,
    TransmissionLineDoubletParameters,
    TrapDipoleParameters,
    TrapYagiParameters,
    YagiParameters,
    ZeppParameters,
)


def feed_balance(parameters: AntennaDesignParameters) -> FeedBalance:
    """Classify the feed as balanced, unbalanced, or unknown."""

    if isinstance(parameters, _BALANCED_TYPES):
        return FeedBalance.BALANCED
    if isinstance(parameters, (CustomAntennaParameters, MagneticLoopParameters)):
        return FeedBalance.UNKNOWN
    return FeedBalance.UNBALANCED


def requires_current_balun(parameters: AntennaDesignParameters) -> bool:
    """Return True when the family normally needs a current balun or choke."""

    return feed_balance(parameters) is FeedBalance.BALANCED
