# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolve the effective matching network for a design and project."""

from __future__ import annotations

from dataclasses import dataclass

from ..antennas.design import AntennaDesignParameters
from ..antennas.endfed import EndFedParameters, endfed_matching_network
from ..antennas.matching_network import MatchingNetwork


@dataclass(frozen=True, slots=True)
class MatchingNetworkResolution:
    """The internal, project, and effective matching networks.

    ``project`` keeps the configured network even when it is inactive so the UI
    can show its state. ``effective`` is the network the solver should use.
    """

    internal: MatchingNetwork | None
    project: MatchingNetwork | None
    effective: MatchingNetwork | None
    override_active: bool
    project_active: bool


def resolve_matching_network(
    parameters: AntennaDesignParameters,
    project_network: MatchingNetwork | None,
) -> MatchingNetworkResolution:
    """Return the effective matching network without persisting a flag.

    A project network replaces the internal EFHW matching network when both are
    active. When the project network is absent or inactive, the internal
    network remains effective. Networks are never cascaded.
    """

    internal = (
        endfed_matching_network(parameters) if isinstance(parameters, EndFedParameters) else None
    )
    project_active = project_network is not None and project_network.is_active
    override_active = internal is not None and project_active
    effective = project_network if project_active else internal
    return MatchingNetworkResolution(
        internal=internal,
        project=project_network,
        effective=effective,
        override_active=override_active,
        project_active=project_active,
    )
