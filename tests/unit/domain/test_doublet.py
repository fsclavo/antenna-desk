# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.antennas.doublet import (
    doublet_feed_line,
    doublet_parameters,
)


def test_doublet_reference_matches_the_published_94_foot_design() -> None:
    parameters = doublet_parameters()
    line = doublet_feed_line()

    assert parameters.total_length_m == pytest.approx(94.0 * 0.3048, rel=0.01)
    assert line.characteristic_impedance_ohm == pytest.approx(450.0)
    assert line.length_m == pytest.approx(41.0 * 0.3048, rel=0.01)
    assert line.velocity_factor == pytest.approx(0.9)
    assert line.matched_loss_db_per_100m == pytest.approx(0.2)
