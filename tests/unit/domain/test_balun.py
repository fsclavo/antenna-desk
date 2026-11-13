# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import math

import pytest

from antennadesk.domain.antennas.balun import (
    SQUASH_PRACTICE_49_1_LOSS,
    BalunLoss,
    LossPoint,
)


def test_squash_practice_loss_preset_uses_the_published_band_values() -> None:
    for frequency_hz, expected_db in (
        (3_750_000.0, 0.43),
        (7_150_000.0, 0.33),
        (14_175_000.0, 0.30),
        (28_500_000.0, 0.32),
    ):
        assert SQUASH_PRACTICE_49_1_LOSS.loss_db(frequency_hz) == pytest.approx(expected_db)

    assert SQUASH_PRACTICE_49_1_LOSS.table_range_hz == pytest.approx((3_750_000.0, 28_500_000.0))
    assert "Squash Practice" in SQUASH_PRACTICE_49_1_LOSS.source


def test_loss_table_interpolates_in_log_frequency() -> None:
    model = BalunLoss(
        reference_loss_db=0.0,
        points=(
            LossPoint(1_000_000.0, 0.2),
            LossPoint(4_000_000.0, 0.6),
        ),
        source="test",
    )

    geometric_midpoint = 2_000_000.0
    assert model.loss_db(geometric_midpoint) == pytest.approx(0.4)


def test_loss_table_clamps_outside_the_measured_range() -> None:
    model = BalunLoss(
        reference_loss_db=0.0,
        points=(
            LossPoint(3_750_000.0, 0.43),
            LossPoint(28_500_000.0, 0.32),
        ),
        source="test",
    )

    assert model.loss_db(1_800_000.0) == pytest.approx(0.43)
    assert model.loss_db(50_000_000.0) == pytest.approx(0.32)
    assert model.is_within_table_range(14_000_000.0)
    assert not model.is_within_table_range(1_800_000.0)


def test_loss_table_requires_a_source_and_increasing_frequencies() -> None:
    with pytest.raises(ValueError, match="source"):
        BalunLoss(
            reference_loss_db=0.0,
            points=(
                LossPoint(7_000_000.0, 0.3),
                LossPoint(14_000_000.0, 0.4),
            ),
        )

    with pytest.raises(ValueError, match="strictly increasing"):
        BalunLoss(
            reference_loss_db=0.0,
            points=(
                LossPoint(14_000_000.0, 0.3),
                LossPoint(7_000_000.0, 0.4),
            ),
            source="test",
        )


def test_power_law_loss_is_unchanged_without_a_table() -> None:
    model = BalunLoss(
        reference_frequency_hz=7_000_000.0,
        reference_loss_db=0.5,
        exponent=0.5,
    )

    assert model.loss_db(28_000_000.0) == pytest.approx(0.5 * math.sqrt(4.0))
    assert model.table_range_hz is None
