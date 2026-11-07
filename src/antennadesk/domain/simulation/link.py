# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Feed-line, matching-network, and transformer cascade metrics."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..antennas.two_port import Abcd, reflection_loss_db, transducer_gain_db
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

    The cascade order from the transmitter is feed line, matching network, and
    ideal transformer.  ``transducer_gain_db`` is relative to the available
    power of a source at ``spec.reference_impedance_ohm``; it therefore includes
    transmitter mismatch, line loss, network loss, and any residual mismatch at
    the antenna.
    """

    source_impedance_ohm = spec.reference_impedance_ohm
    load_impedance_ohm = antenna_impedance_ohm / spec.feed_transformer_ratio
    line = spec.feed_line
    network = spec.matching_network

    cascade = Abcd()
    if line is not None and line.is_active:
        cascade = cascade @ line.abcd(frequency_hz)
    if network is not None and network.is_active:
        cascade = cascade @ network.abcd(frequency_hz)

    input_impedance_ohm = cascade.input_impedance(load_impedance_ohm)
    mismatch_loss_db = reflection_loss_db(input_impedance_ohm, source_impedance_ohm)
    balun_loss_db = (
        spec.balun_loss.loss_db(frequency_hz)
        if spec.balun_loss is not None and spec.balun_loss.is_active
        else 0.0
    )
    feed_line_loss_db = (
        line.matched_loss_db_per_100m * line.length_m / 100.0
        if line is not None and line.is_active
        else 0.0
    )

    network_loss_db = 0.0
    if network is not None and network.is_active:
        network_source_ohm = (
            line.characteristic_impedance_ohm
            if line is not None and line.is_active
            else source_impedance_ohm
        )
        network_abcd = network.abcd(frequency_hz)
        network_input_ohm = network_abcd.input_impedance(load_impedance_ohm)
        network_gain_db = transducer_gain_db(
            network_abcd,
            network_source_ohm,
            load_impedance_ohm,
        )
        network_mismatch_db = reflection_loss_db(
            network_input_ohm,
            network_source_ohm,
        )
        if math.isfinite(network_gain_db) and math.isfinite(network_mismatch_db):
            network_loss_db = max(0.0, -(network_gain_db + network_mismatch_db))

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
