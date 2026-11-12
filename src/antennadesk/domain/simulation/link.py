# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-line, matching-network, and transformer cascade metrics."""

from __future__ import annotations

from dataclasses import dataclass

from ..antennas.matching_network import MatchingNetworkPosition
from ..antennas.two_port import (
    Abcd,
    dissipative_loss_db,
    reflection_loss_db,
    transducer_gain_db,
)
from .spec import SimulationSpec


@dataclass(frozen=True, slots=True)
class LinkBudget:
    """The transmitter-to-antenna link efficiency and its loss components."""

    input_impedance_ohm: complex
    transducer_gain_db: float
    mismatch_loss_db: float
    feed_line_loss_db: float
    network_loss_db: float
    balun_loss_db: float


def link_budget(
    *,
    antenna_impedance_ohm: complex,
    frequency_hz: float,
    spec: SimulationSpec,
) -> LinkBudget:
    """Evaluate the transformer, matching network, and feed line chain.

    The matching network is placed either in the shack, before the feed line,
    or at the feedpoint, after the line. The ideal transformer remains at the
    antenna in both cases. ``feed_line_loss_db`` and ``network_loss_db`` are the
    actual dissipative losses under the modeled impedances, not the matched-line
    loss. ``transducer_gain_db`` is relative to the available power of a source
    at ``spec.reference_impedance_ohm`` and includes transmitter mismatch, line
    loss, network loss, and the residual mismatch at the antenna.
    """

    source_impedance_ohm = spec.reference_impedance_ohm
    load_impedance_ohm = antenna_impedance_ohm / spec.feed_transformer_ratio
    line = spec.feed_line
    line_active = line is not None and line.is_active
    network = spec.matching_network
    network_active = (
        network is not None
        and network.is_active
        and spec.matching_network_position is not MatchingNetworkPosition.NONE
    )
    position = spec.matching_network_position

    cascade = Abcd()
    network_source_ohm = source_impedance_ohm
    network_load_ohm = load_impedance_ohm
    line_source_ohm = source_impedance_ohm
    line_load_ohm = load_impedance_ohm

    if (
        line_active
        and network_active
        and position is MatchingNetworkPosition.SHACK
        and line is not None
        and network is not None
    ):
        line_abcd = line.abcd(frequency_hz)
        network_abcd = network.abcd(frequency_hz)
        line_input_ohm = line_abcd.input_impedance(load_impedance_ohm)
        cascade = network_abcd @ line_abcd
        network_load_ohm = line_input_ohm
        # A shack tuner presents the line with its design impedance. The line
        # still sees the mismatched antenna on its output side.
        line_source_ohm = line.characteristic_impedance_ohm
        line_load_ohm = load_impedance_ohm
    elif line_active and network_active and line is not None and network is not None:
        line_abcd = line.abcd(frequency_hz)
        network_abcd = network.abcd(frequency_hz)
        network_input_ohm = network_abcd.input_impedance(load_impedance_ohm)
        cascade = line_abcd @ network_abcd
        network_source_ohm = line.characteristic_impedance_ohm
        network_load_ohm = load_impedance_ohm
        line_source_ohm = source_impedance_ohm
        line_load_ohm = network_input_ohm
    elif line_active and line is not None:
        cascade = line.abcd(frequency_hz)
        line_source_ohm = source_impedance_ohm
        line_load_ohm = load_impedance_ohm
    elif network_active and network is not None:
        cascade = network.abcd(frequency_hz)
        network_source_ohm = source_impedance_ohm
        network_load_ohm = load_impedance_ohm

    input_impedance_ohm = cascade.input_impedance(load_impedance_ohm)
    mismatch_loss_db = reflection_loss_db(input_impedance_ohm, source_impedance_ohm)
    balun_loss_db = (
        spec.balun_loss.loss_db(frequency_hz)
        if spec.balun_loss is not None and spec.balun_loss.is_active
        else 0.0
    )
    feed_line_loss_db = (
        dissipative_loss_db(
            line.abcd(frequency_hz),
            line_source_ohm,
            line_load_ohm,
        )
        if line_active and line is not None
        else 0.0
    )
    network_loss_db = (
        dissipative_loss_db(
            network.abcd(frequency_hz),
            network_source_ohm,
            network_load_ohm,
        )
        if network_active and network is not None
        else 0.0
    )

    return LinkBudget(
        input_impedance_ohm=input_impedance_ohm,
        transducer_gain_db=(
            transducer_gain_db(
                cascade,
                source_impedance_ohm,
                load_impedance_ohm,
            )
            - balun_loss_db
        ),
        mismatch_loss_db=mismatch_loss_db,
        feed_line_loss_db=feed_line_loss_db,
        network_loss_db=network_loss_db,
        balun_loss_db=balun_loss_db,
    )
