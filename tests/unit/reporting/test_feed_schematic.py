# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Renderer-neutral feed schematic."""

from __future__ import annotations

from antennadesk.domain.antennas.feed_connection import (
    BalunRequirement,
    FeedBalance,
    FeedConnectionDetail,
    FeedInterface,
    FeedTerminal,
    FeedTopology,
)
from antennadesk.reporting.feed_schematic import feed_schematic_svg
from antennadesk.ui.i18n import Language, Translator

_BALANCED_TERMINALS = (
    FeedTerminal("A", "1", 5.0, "before"),
    FeedTerminal("B", "1", 5.0, "after"),
)
_GROUND_TERMINALS = (
    FeedTerminal("A", "1", 0.0, "start"),
    FeedTerminal("B", None, None, "ground"),
)
_COUNTERPOISE_TERMINALS = (
    FeedTerminal("A", "1", 0.0, "start"),
    FeedTerminal("B", None, None, "counterpoise"),
)


def _detail(
    interface: FeedInterface,
    terminals: tuple[FeedTerminal, FeedTerminal] = _BALANCED_TERMINALS,
    *,
    balance: FeedBalance = FeedBalance.BALANCED,
    requirement: BalunRequirement = BalunRequirement.RECOMMENDED,
    ratio: float | None = None,
    topology: FeedTopology = FeedTopology.CENTER_FED_DIPOLE,
) -> FeedConnectionDetail:
    return FeedConnectionDetail(
        topology=topology,
        interface=interface,
        balance=balance,
        balun_requirement=requirement,
        terminals=terminals,
        connections=(),
        summary="Test feed",
        transformer_ratio=ratio,
    )


def test_direct_coax_draws_a_cable_and_no_device_box() -> None:
    svg = feed_schematic_svg(_detail(FeedInterface.DIRECT_COAX))

    assert '<g id="coax">' in svg
    assert '<g id="coax-cross-section">' in svg
    assert '<g id="interface-device">' not in svg
    assert '<g id="balanced-line">' not in svg
    assert "Direct coax" in svg
    assert "Center conductor" in svg
    assert "Shield (braid)" in svg
    assert "Coax center" in svg
    assert "Coax shield" in svg
    assert svg.count("<circle") == 4


def test_direct_coax_shows_a_recommended_choke_dashed() -> None:
    svg = feed_schematic_svg(
        _detail(FeedInterface.DIRECT_COAX, requirement=BalunRequirement.REQUIRED)
    )

    assert '<g id="recommended-choke">' in svg
    assert "Recommended, not recorded" in svg
    assert 'stroke-dasharray="6 4"' in svg


def test_direct_coax_omits_the_choke_when_not_required() -> None:
    svg = feed_schematic_svg(
        _detail(FeedInterface.DIRECT_COAX, requirement=BalunRequirement.NOT_REQUIRED)
    )

    assert '<g id="recommended-choke">' not in svg
    assert "Recommended, not recorded" not in svg


def test_base_fed_vertical_labels_the_ground_return() -> None:
    svg = feed_schematic_svg(
        _detail(
            FeedInterface.DIRECT_COAX,
            _GROUND_TERMINALS,
            balance=FeedBalance.UNBALANCED,
            requirement=BalunRequirement.NOT_REQUIRED,
            topology=FeedTopology.BASE_FED_VERTICAL,
        )
    )

    assert "Ground / radials" in svg
    assert "Antenna terminal B" not in svg


def test_end_fed_labels_the_counterpoise() -> None:
    svg = feed_schematic_svg(
        _detail(
            FeedInterface.DIRECT_COAX,
            _COUNTERPOISE_TERMINALS,
            balance=FeedBalance.UNBALANCED,
            requirement=BalunRequirement.NOT_REQUIRED,
            topology=FeedTopology.END_FED,
        )
    )

    assert "Counterpoise" in svg
    assert "Antenna terminal B" not in svg


def test_current_balun_uses_a_device_block_and_coax() -> None:
    svg = feed_schematic_svg(
        _detail(FeedInterface.CURRENT_BALUN, requirement=BalunRequirement.REQUIRED)
    )

    assert '<g id="interface-device">' in svg
    assert "1:1 current balun" in svg
    assert "Recorded" in svg
    assert '<g id="coax">' in svg
    assert '<g id="coax-cross-section">' in svg


def test_transformer_shows_the_ratio_and_ideal_model() -> None:
    svg = feed_schematic_svg(
        _detail(
            FeedInterface.TRANSFORMER,
            requirement=BalunRequirement.REQUIRED,
            ratio=4.0,
        )
    )

    assert '<g id="interface-device">' in svg
    assert "Transformer / balun" in svg
    assert "4:1" in svg
    assert "Modeled as ideal" in svg
    assert "Primary" in svg
    assert "Secondary" in svg
    assert '<g id="coax">' in svg


def test_balanced_line_has_no_coax() -> None:
    svg = feed_schematic_svg(_detail(FeedInterface.BALANCED_LINE))

    assert '<g id="balanced-line">' in svg
    assert "Balanced line A" in svg
    assert "Balanced line B" in svg
    assert '<g id="coax">' not in svg
    assert "The balun location depends on the tuner; it is not modeled." in svg


def test_multi_port_shows_the_combining_limit() -> None:
    svg = feed_schematic_svg(
        _detail(
            FeedInterface.MULTI_PORT,
            balance=FeedBalance.UNBALANCED,
            requirement=BalunRequirement.NOT_REQUIRED,
            topology=FeedTopology.MULTI_PORT,
        )
    )

    assert '<g id="interface-device">' in svg
    assert "Multi-port combining network" in svg
    assert "Combining network not modeled" in svg
    assert "Primary port" in svg
    assert "Additional sources" in svg


def test_unknown_is_dashed_and_has_no_coax() -> None:
    svg = feed_schematic_svg(
        _detail(
            FeedInterface.UNKNOWN,
            balance=FeedBalance.UNKNOWN,
            requirement=BalunRequirement.UNKNOWN,
            topology=FeedTopology.UNKNOWN,
        )
    )

    assert '<g id="unknown">' in svg
    assert "Verify the wiring" in svg
    assert "Connection not classified" in svg
    assert '<g id="coax">' not in svg
    assert 'stroke-dasharray="6 4"' in svg


def test_feed_schematic_is_deterministic() -> None:
    detail = _detail(FeedInterface.DIRECT_COAX)

    assert feed_schematic_svg(detail) == feed_schematic_svg(detail)


def test_feed_schematic_translates_to_spanish() -> None:
    svg = feed_schematic_svg(
        _detail(FeedInterface.DIRECT_COAX, requirement=BalunRequirement.REQUIRED),
        Translator(Language.SPANISH).report,
    )

    assert "Conexión de alimentación" in svg
    assert "Coaxil directo" in svg
    assert "Conductor central" in svg
    assert "Malla (trenza)" in svg
    assert "Sección del coaxil" in svg
    assert "Centro del coaxil" in svg
    assert "Recomendado, no registrado" in svg
    assert "Center conductor" not in svg
    assert "no a escala" in svg
