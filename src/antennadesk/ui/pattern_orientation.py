# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Presentation-only antenna orientation helpers for the 3D pattern view."""

from __future__ import annotations

from ..domain.antennas.design import AntennaDesignParameters
from ..domain.antennas.hexbeam import HexbeamParameters
from ..domain.antennas.log_periodic import LogPeriodicParameters
from ..domain.antennas.moxon import MoxonParameters
from ..domain.antennas.quad_beam import QuadBeamParameters
from ..domain.antennas.stacked_yagi import StackedYagiParameters
from ..domain.antennas.trap_yagi import TrapYagiParameters
from ..domain.antennas.yagi import YagiParameters

_FORWARD_AXIS_TYPES = (
    YagiParameters,
    MoxonParameters,
    QuadBeamParameters,
    HexbeamParameters,
    LogPeriodicParameters,
    StackedYagiParameters,
    TrapYagiParameters,
)


def antenna_orientation(
    parameters: AntennaDesignParameters | None,
) -> tuple[float | None, bool]:
    """Return the antenna azimuth and whether it is a vertical orientation."""

    if parameters is None:
        return None, False
    azimuth = getattr(parameters, "azimuth_deg", None)
    orientation = getattr(parameters, "orientation", None)
    vertical = getattr(orientation, "value", orientation) == "vertical"
    return (float(azimuth) if isinstance(azimuth, (int, float)) else None, vertical)


def forward_axis_azimuth(parameters: AntennaDesignParameters | None) -> float | None:
    """Return a forward azimuth only for families with an explicit boom axis."""

    if not isinstance(parameters, _FORWARD_AXIS_TYPES):
        return None
    azimuth = getattr(parameters, "azimuth_deg", None)
    return float(azimuth) if isinstance(azimuth, (int, float)) else None
