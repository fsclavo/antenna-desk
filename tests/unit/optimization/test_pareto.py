# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from antennadesk.domain.optimization.multi_variable import BoundedEvaluation
from antennadesk.domain.optimization.pareto import ParetoObjectives, pareto_ranks


def _evaluation(index: int, gain: float, fb: float, swr: float) -> BoundedEvaluation:
    return BoundedEvaluation(
        index,
        {"x": float(index)},
        0.0,
        metrics={
            "max_gain_db": gain,
            "front_to_back_db": fb,
            "swr": swr,
        },
    )


def test_pareto_ranks_put_non_dominated_points_first() -> None:
    evaluations = (
        _evaluation(1, 10.0, 20.0, 1.5),
        _evaluation(2, 9.0, 25.0, 1.2),
        _evaluation(3, 8.0, 15.0, 2.0),
    )

    ranks = pareto_ranks(evaluations, ParetoObjectives())

    assert ranks[1] == 1
    assert ranks[2] == 1
    assert ranks[3] == 2


def test_pareto_ignores_incomplete_metrics() -> None:
    incomplete = BoundedEvaluation(1, {"x": 1.0}, 0.0, metrics={"max_gain_db": 10.0})
    complete = _evaluation(2, 9.0, 20.0, 1.5)

    ranks = pareto_ranks((incomplete, complete), ParetoObjectives())

    assert ranks == {2: 1}
