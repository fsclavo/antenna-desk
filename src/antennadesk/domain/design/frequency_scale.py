# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit, allowlisted scaling of a tuned design to another frequency."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, cast

from ..antennas.biquad import BiquadParameters
from ..antennas.design import (
    AntennaDesignParameters,
    primary_dimension_m,
    with_primary_dimension,
)
from ..antennas.dipole import DipoleParameters
from ..antennas.discone import DisconeParameters
from ..antennas.folded_dipole import FoldedDipoleParameters
from ..antennas.hexbeam import HexbeamParameters
from ..antennas.loop import LoopParameters
from ..antennas.quad_beam import QuadBeamParameters


class UnsupportedFrequencyScaleError(ValueError):
    """The current template has no reliable frequency-scaling rule."""


# These families have a single primary electrical dimension and a deterministic
# derived geometry. Multi-band HexBeams are excluded dynamically below until a
# family-specific band-scaling rule exists. Do not add loaded, trapped,
# Yagi/Moxon, fan, or transmission-line families without a family-specific rule.
_SCALABLE_TYPES = (
    DipoleParameters,
    FoldedDipoleParameters,
    LoopParameters,
    QuadBeamParameters,
    BiquadParameters,
    DisconeParameters,
    HexbeamParameters,
)


def supports_frequency_scaling(parameters: AntennaDesignParameters) -> bool:
    if isinstance(parameters, HexbeamParameters) and parameters.bands:
        return False
    return isinstance(parameters, _SCALABLE_TYPES)


def scaled_to_frequency(
    parameters: AntennaDesignParameters,
    frequency_hz: float,
) -> AntennaDesignParameters:
    """Scale the primary electrical geometry to a new design frequency.

    The current primary dimension is assumed to represent the current design
    frequency. The new dimension is ``primary * f_old / f_new``. Installation
    and matching fields are preserved by the family adapter.
    """

    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive")
    if not supports_frequency_scaling(parameters):
        raise UnsupportedFrequencyScaleError(
            "the current template has no reliable frequency-scaling rule"
        )
    old_frequency_hz = parameters.frequency_hz
    if old_frequency_hz <= 0.0:
        raise ValueError("the current design frequency must be positive")
    primary_m = primary_dimension_m(parameters)
    target_m = primary_m * old_frequency_hz / frequency_hz
    scaled: AntennaDesignParameters
    if isinstance(parameters, FoldedDipoleParameters):
        ratio = target_m / parameters.total_length_m
        scaled = replace(
            parameters,
            total_length_m=target_m,
            spacing_m=parameters.spacing_m * ratio,
        )
    else:
        scaled = with_primary_dimension(parameters, target_m)
    return cast(
        AntennaDesignParameters,
        replace(cast(Any, scaled), frequency_hz=frequency_hz),
    )
