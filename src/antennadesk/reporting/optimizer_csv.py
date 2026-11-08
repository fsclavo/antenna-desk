# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Deterministic CSV export for family-optimizer evaluations."""

from __future__ import annotations

import csv
import math
from collections.abc import Iterable, Sequence
from pathlib import Path

from ..domain.optimization.engine import CandidateEvaluation, rank_evaluations

_FIXED_METRICS: tuple[str, ...] = (
    "resistance_ohm",
    "reactance_ohm",
    "swr",
    "target_error_ohm",
    "target_swr",
    "max_gain_db",
    "front_to_back_db",
    "efficiency_percent",
    "bandwidth_hz",
    "boom_length_m",
    "turning_radius_m",
    "swr_spread",
    "worst_frequency_hz",
    "multi_point_count",
    "optimization_score_spread",
)


def _number(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return ""
    return f"{value:.12g}"


def optimization_csv_rows(
    evaluations: Sequence[CandidateEvaluation],
    *,
    pareto_indices: Iterable[int] = (),
    variable_names: Sequence[str] = (),
) -> tuple[tuple[str, ...], list[tuple[str, ...]]]:
    """Return ``(header, rows)`` with a stable column schema."""

    ranked = rank_evaluations(evaluations)
    metric_names = list(_FIXED_METRICS)
    extra_metrics = sorted(
        {
            name
            for evaluation in evaluations
            for name in evaluation.metrics
            if name not in metric_names
        }
    )
    metric_names.extend(extra_metrics)
    all_variables = list(variable_names)
    extra_variables = sorted(
        {
            name
            for evaluation in evaluations
            for name in evaluation.values
            if name not in all_variables
        }
    )
    all_variables.extend(extra_variables)
    pareto = set(pareto_indices)
    header = (
        "rank",
        "index",
        "score",
        "feasible",
        "violation",
        "error",
        "pareto",
        *metric_names,
        *(f"value_{name}" for name in all_variables),
    )
    rows: list[tuple[str, ...]] = []
    for rank, evaluation in enumerate(ranked, start=1):
        rows.append(
            (
                str(rank),
                str(evaluation.index),
                _number(evaluation.score),
                "true" if evaluation.feasible else "false",
                _number(evaluation.violation),
                evaluation.error or "",
                "true" if evaluation.index in pareto else "false",
                *(_number(evaluation.metrics.get(name)) for name in metric_names),
                *(_number(evaluation.values.get(name)) for name in all_variables),
            )
        )
    return header, rows


def write_optimization_csv(
    path: str | Path,
    evaluations: Sequence[CandidateEvaluation],
    *,
    pareto_indices: Iterable[int] = (),
    variable_names: Sequence[str] = (),
) -> None:
    """Write the ranked evaluation log and Pareto flags as UTF-8 CSV."""

    header, rows = optimization_csv_rows(
        evaluations,
        pareto_indices=pareto_indices,
        variable_names=variable_names,
    )
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
