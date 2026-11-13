# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import pytest

from antennadesk.domain.optimization.variables import (
    OptimizationVariable,
    VariableKind,
    variables_at_bounds,
)


def _variable(name: str, *, kind: VariableKind = VariableKind.CONTINUOUS) -> OptimizationVariable:
    if kind is VariableKind.CHOICE:
        return OptimizationVariable(
            name,
            "field.length",
            "optimize.group.geometry",
            1.0,
            10.0,
            kind=kind,
            choices=(1.0, 5.0, 10.0),
        )
    return OptimizationVariable(
        name,
        "field.length",
        "optimize.group.geometry",
        10.0,
        20.0,
        kind=kind,
    )


def test_variables_at_bounds_reports_continuous_unlocked_hits() -> None:
    variables = (
        _variable("low"),
        _variable("center"),
        _variable("high"),
        _variable("locked"),
        _variable("choice", kind=VariableKind.CHOICE),
        _variable("integer", kind=VariableKind.INTEGER),
    )
    values = {
        "low": 10.05,
        "center": 15.0,
        "high": 19.99,
        "locked": 10.0,
        "choice": 1.0,
        "integer": 10.0,
    }

    assert variables_at_bounds(variables, values, locked=frozenset({"locked"})) == (
        "low",
        "high",
    )


def test_variables_at_bounds_rejects_an_invalid_fraction() -> None:
    with pytest.raises(ValueError, match="fraction"):
        variables_at_bounds((), {}, fraction=0.5)
