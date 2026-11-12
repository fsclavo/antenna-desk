# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Curated reference design library."""

from __future__ import annotations

from uuid import uuid4

import pytest

from antennadesk.domain.antennas.dipole import DipoleParameters
from antennadesk.domain.antennas.endfed import EndFedParameters
from antennadesk.domain.antennas.inverted_v import InvertedVParameters
from antennadesk.domain.antennas.moxon import MoxonParameters
from antennadesk.domain.antennas.scv import ScvParameters
from antennadesk.domain.antennas.trap_dipole import TrapDipoleParameters
from antennadesk.domain.antennas.yagi import YagiParameters
from antennadesk.domain.design.evidence import EvidenceLevel
from antennadesk.domain.design.reference_library import (
    REFERENCE_DESIGNS,
    reference_design_by_key,
)
from antennadesk.domain.projects.project import DesignVariant


def test_library_has_a_bounded_set_of_unique_sourced_designs() -> None:
    keys = [design.key for design in REFERENCE_DESIGNS]

    assert len(REFERENCE_DESIGNS) == 12
    assert len(keys) == len(set(keys))
    assert all(design.evidence.source.strip() for design in REFERENCE_DESIGNS)
    assert all(design.evidence.tolerance.strip() for design in REFERENCE_DESIGNS)
    assert all(design.evidence.limitation.strip() for design in REFERENCE_DESIGNS)
    assert {design.evidence.level for design in REFERENCE_DESIGNS} <= {
        EvidenceLevel.REFERENCE,
        EvidenceLevel.PUBLISHED,
    }


def test_reference_design_parameters_match_their_published_examples() -> None:
    dipole = reference_design_by_key("arrl_dipole_40m").parameters
    assert isinstance(dipole, DipoleParameters)
    assert dipole.frequency_hz == pytest.approx(7_100_000.0)
    assert dipole.total_length_m == pytest.approx(20.07, rel=0.01)

    moxon = reference_design_by_key("cebik_moxon_20m").parameters
    assert isinstance(moxon, MoxonParameters)
    assert moxon.width_m == pytest.approx(25.0 * 0.3048)
    assert moxon.depth_m == pytest.approx(9.57 * 0.3048)

    yagi = reference_design_by_key("nbs_yagi_6m").parameters
    assert isinstance(yagi, YagiParameters)
    assert yagi.frequency_hz == pytest.approx(50_100_000.0)
    assert len(yagi.elements) == 5
    assert yagi.driven_index == 1

    trap = reference_design_by_key("w3dzz_trap_dipole").parameters
    assert isinstance(trap, TrapDipoleParameters)
    assert trap.inner_length_m == pytest.approx(2.0 * 33.0 * 0.3048)
    assert trap.outer_length_m == pytest.approx(22.0 * 0.3048)

    half_square = reference_design_by_key("cebik_half_square").parameters
    assert isinstance(half_square, ScvParameters)
    assert half_square.horizontal_length_m == pytest.approx(62.4 * 0.3048)

    bobtail = reference_design_by_key("cebik_bobtail_curtain").parameters
    assert isinstance(bobtail, ScvParameters)
    assert bobtail.horizontal_length_m == pytest.approx(125.0 * 0.3048)

    efhw = reference_design_by_key("arrl_efhw_40m").parameters
    assert isinstance(efhw, EndFedParameters)
    assert efhw.length_m == pytest.approx(66.0 * 0.3048)

    inverted_v = reference_design_by_key("arrl_inverted_v").parameters
    assert isinstance(inverted_v, InvertedVParameters)
    assert inverted_v.leg_length_m * 2.0 == pytest.approx(465.6 / 7.1 * 0.3048)
    assert inverted_v.included_angle_deg == pytest.approx(120.0)


def test_every_reference_builds_a_consistent_design_variant() -> None:
    for design in REFERENCE_DESIGNS:
        variant = DesignVariant(
            id=uuid4(),
            name=design.key,
            antenna_type=design.antenna_type,
            parameters=design.parameters,
            antenna=design.parameters.to_antenna(name=design.key),
        )

        assert variant.parameters == design.parameters
        assert variant.antenna.wires


def test_every_reference_has_presentation_keys_and_search_terms() -> None:
    for design in REFERENCE_DESIGNS:
        assert design.title_key.startswith("reference.")
        assert design.project_name_key.startswith("reference.")
        assert design.summary_key.startswith("reference.")
        assert design.published_key.startswith("reference.")
        assert design.modeled_key.startswith("reference.")
        assert design.antenna_type
        assert design.search_terms
        assert 1_800_000.0 <= design.frequency_hz <= 450_000_000.0
