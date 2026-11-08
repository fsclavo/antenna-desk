# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import csv
from pathlib import Path

from antennadesk.domain.optimization.engine import CandidateEvaluation
from antennadesk.reporting.optimizer_csv import (
    optimization_csv_rows,
    write_optimization_csv,
)


def _evaluations() -> tuple[CandidateEvaluation, ...]:
    return (
        CandidateEvaluation(
            index=2,
            values={"height_m": 9.0, "length_m": 20.0},
            score=2.5,
            feasible=True,
            metrics={"swr": 1.4, "max_gain_db": 2.0},
        ),
        CandidateEvaluation(
            index=1,
            values={"height_m": 10.0, "length_m": 20.5},
            score=1.0,
            feasible=True,
            metrics={"swr": 1.1, "max_gain_db": 1.8},
        ),
        CandidateEvaluation(
            index=3,
            values={"height_m": 8.0, "length_m": 19.0},
            score=None,
            feasible=False,
            violation=0.5,
            error="optimize.constraint.height",
        ),
    )


def test_optimization_csv_rows_have_a_stable_schema() -> None:
    header, rows = optimization_csv_rows(
        _evaluations(),
        pareto_indices={2},
        variable_names=("length_m", "height_m"),
    )

    assert header[:7] == (
        "rank",
        "index",
        "score",
        "feasible",
        "violation",
        "error",
        "pareto",
    )
    assert "swr" in header
    assert header[-2:] == ("value_length_m", "value_height_m")
    assert len(rows) == 3
    best = rows[0]
    assert best[1] == "1"
    assert best[2] == "1"
    assert best[3] == "true"
    assert best[6] == "false"


def test_write_optimization_csv_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "optimization.csv"

    write_optimization_csv(
        path,
        _evaluations(),
        pareto_indices={2},
        variable_names=("length_m", "height_m"),
    )

    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 3
    pareto_row = next(row for row in rows if row["index"] == "2")
    assert pareto_row["pareto"] == "true"
    assert pareto_row["value_length_m"] == "20"
    infeasible = next(row for row in rows if row["index"] == "3")
    assert infeasible["feasible"] == "false"
    assert infeasible["error"] == "optimize.constraint.height"
