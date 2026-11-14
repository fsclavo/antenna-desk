# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Resolve the effective matching network for a design and project."""

from __future__ import annotations

from dataclasses import dataclass

from ..antennas.design import AntennaDesignParameters
from ..antennas.endfed import (
    EndFedParameters,
    endfed_design_matching_network,
    endfed_internal_matching_network,
)
from ..antennas.matching_network import MatchingNetwork, MatchingNetworkOrigin


@dataclass(frozen=True, slots=True)
class MatchingNetworkResolution:
    """The internal, project, and effective matching networks.

    ``project`` keeps the configured network even when it is inactive so the UI
    can show its state. ``effective`` is the network the solver should use.
    """

    internal: MatchingNetwork | None
    design: MatchingNetwork | None
    project: MatchingNetwork | None
    effective: MatchingNetwork | None
    override_active: bool
    project_active: bool

    @property
    def design_active(self) -> bool:
        return self.design is not None

    @property
    def origin(self) -> MatchingNetworkOrigin:
        if self.project_active:
            return MatchingNetworkOrigin.PROJECT
        if self.design is not None:
            return MatchingNetworkOrigin.DESIGN_ENDFED
        if self.internal is not None:
            return MatchingNetworkOrigin.INTERNAL_ENDFED
        return MatchingNetworkOrigin.NONE


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
        endfed_internal_matching_network(parameters)
        if isinstance(parameters, EndFedParameters)
        else None
    )
    design = (
        endfed_design_matching_network(parameters)
        if isinstance(parameters, EndFedParameters)
        else None
    )
    family = design if design is not None else internal
    project_active = project_network is not None and project_network.is_active
    override_active = family is not None and project_active
    effective = project_network if project_active else family
    return MatchingNetworkResolution(
        internal=internal,
        design=design,
        project=project_network,
        effective=effective,
        override_active=override_active,
        project_active=project_active,
    )
