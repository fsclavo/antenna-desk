# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fixtures shared by the nec2c integration modules."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from antennadesk.simulation.nec2.solver import Nec2cSolver


@pytest.fixture
def solver() -> Nec2cSolver:
    nec2c = os.environ.get("NEC2C")
    assert nec2c is not None
    return Nec2cSolver(Path(nec2c))
