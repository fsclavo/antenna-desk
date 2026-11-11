# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic antenna advisor constraints and ordering."""

from __future__ import annotations

import pytest

from antennadesk.domain.design.advisor import (
    AdvisorBlocker,
    AdvisorRequest,
    Directionality,
    FitStatus,
    recommend,
)
from antennadesk.domain.design.suitability import (
    PROFILES_BY_KEY,
    Complexity,
    OperatingIntent,
)


def _request(**overrides: object) -> AdvisorRequest:
    values: dict[str, object] = {
        "bands": frozenset({"40m"}),
        "multiband_required": False,
        "intent": OperatingIntent.REGIONAL,
        "tuner_available": False,
        "max_complexity": Complexity.MODERATE,
    }
    values.update(overrides)
    return AdvisorRequest(**values)  # type: ignore[arg-type]


def _keys(request: AdvisorRequest) -> list[str]:
    return [candidate.profile.catalog_key for candidate in recommend(request).candidates]


def test_single_band_prefers_a_simple_dipole() -> None:
    keys = _keys(_request())

    assert keys[0] == "wire_dipole"
    assert "vertical" in keys


def test_multiband_request_excludes_monoband_families() -> None:
    keys = _keys(
        _request(
            bands=frozenset({"40m", "20m", "10m"}),
            multiband_required=True,
        )
    )

    assert "wire_dipole" not in keys
    assert "inverted_v" not in keys
    assert "endfed" in keys


def test_space_constraint_excludes_long_designs() -> None:
    result = recommend(
        _request(
            bands=frozenset({"40m", "20m", "10m"}),
            multiband_required=True,
            available_width_m=19.0,
        )
    )

    keys = [candidate.profile.catalog_key for candidate in result.candidates]
    assert all(candidate.footprint_m <= 19.0 for candidate in result.candidates)
    assert "endfed" not in keys
    assert "ocfd" not in keys
    assert "fan_dipole" not in keys
    assert "trap_dipole" in keys


def test_height_constraint_excludes_tall_designs() -> None:
    result = recommend(_request(available_height_m=6.0))

    keys = [candidate.profile.catalog_key for candidate in result.candidates]
    assert "wire_dipole" in keys
    assert "inverted_v" not in keys
    assert "endfed" not in keys


def test_required_tuner_is_excluded_without_a_tuner() -> None:
    result = recommend(
        _request(
            bands=frozenset({"80m", "40m", "20m", "15m", "10m"}),
            multiband_required=True,
            tuner_available=False,
        )
    )

    keys = [candidate.profile.catalog_key for candidate in result.candidates]
    assert "g5rv" not in keys
    assert "random_wire" not in keys
    assert "endfed" in keys
    assert AdvisorBlocker.TUNER in result.blockers


def test_portable_request_excludes_fixed_installations() -> None:
    keys = _keys(
        _request(
            bands=frozenset({"40m", "20m", "10m"}),
            multiband_required=True,
            portable=True,
        )
    )

    assert "g5rv" not in keys
    assert "fan_dipole" not in keys
    assert "trap_dipole" not in keys
    assert "endfed" in keys


def test_directional_request_keeps_beams() -> None:
    result = recommend(
        _request(
            intent=OperatingIntent.DX,
            directionality=Directionality.DIRECTIONAL,
            max_complexity=Complexity.ADVANCED,
        )
    )

    keys = [candidate.profile.catalog_key for candidate in result.candidates]
    assert "yagi" in keys or "moxon" in keys
    assert all(candidate.profile.directional for candidate in result.candidates)


def test_intent_and_height_warnings_change_the_fit_status() -> None:
    result = recommend(
        _request(
            intent=OperatingIntent.NVIS,
            available_height_m=9.0,
        )
    )

    candidate = next(
        item for item in result.candidates if item.profile.catalog_key == "wire_dipole"
    )
    assert candidate.warnings == ("height_below_recommended",)
    assert candidate.status is FitStatus.GOOD


def test_experimental_family_gets_a_warning() -> None:
    result = recommend(
        _request(
            bands=frozenset({"40m", "20m", "10m"}),
            multiband_required=True,
            portable=True,
            tuner_available=True,
            max_complexity=Complexity.SIMPLE,
        )
    )

    candidate = next(
        item for item in result.candidates if item.profile.catalog_key == "random_wire"
    )
    assert "experimental_starting_point" in candidate.warnings


def test_no_match_reports_blockers() -> None:
    result = recommend(
        _request(
            bands=frozenset({"80m", "40m", "20m", "15m", "10m"}),
            multiband_required=True,
            available_width_m=5.0,
        )
    )

    assert result.candidates == ()
    assert AdvisorBlocker.SPACE in result.blockers


def test_footprint_scales_with_the_lowest_band() -> None:
    profile = PROFILES_BY_KEY["ocfd"]

    assert profile.footprint_at(3_500_000.0) == pytest.approx(41.0)
    assert profile.footprint_at(7_000_000.0) == pytest.approx(20.5)


def test_request_rejects_unknown_or_empty_bands() -> None:
    with pytest.raises(ValueError, match="band"):
        _request(bands=frozenset())
    with pytest.raises(ValueError, match="unknown"):
        _request(bands=frozenset({"11m"}))


def test_ordering_is_deterministic() -> None:
    request = _request(
        bands=frozenset({"40m", "20m", "10m"}),
        multiband_required=True,
        tuner_available=True,
    )

    first = _keys(request)
    second = _keys(request)

    assert first == second
