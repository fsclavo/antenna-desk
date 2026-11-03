# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frequency plans."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.units import ensure_positive

MAX_FREQUENCIES = 10_000


@dataclass(frozen=True, slots=True)
class FrequencyPlan:
    """A single frequency or a uniformly spaced frequency sweep."""

    start_hz: float
    stop_hz: float
    count: int = 1

    def __post_init__(self) -> None:
        ensure_positive(self.start_hz, name="frequency start_hz")
        ensure_positive(self.stop_hz, name="frequency stop_hz")
        if self.stop_hz < self.start_hz:
            raise ValueError("frequency stop_hz must be greater than or equal to start_hz")
        if self.count < 1:
            raise ValueError("frequency count must be at least 1")
        if self.count > MAX_FREQUENCIES:
            raise ValueError(f"frequency count must not exceed {MAX_FREQUENCIES}")
        if self.count == 1 and self.stop_hz != self.start_hz:
            raise ValueError("a single-frequency plan requires start_hz == stop_hz")

    @classmethod
    def single(cls, frequency_hz: float) -> FrequencyPlan:
        return cls(start_hz=frequency_hz, stop_hz=frequency_hz, count=1)

    @classmethod
    def sweep(cls, start_hz: float, stop_hz: float, count: int) -> FrequencyPlan:
        if count < 2:
            raise ValueError("a sweep requires at least two frequencies")
        return cls(start_hz=start_hz, stop_hz=stop_hz, count=count)

    @property
    def is_single(self) -> bool:
        return self.count == 1

    @property
    def step_hz(self) -> float:
        if self.count == 1:
            return 0.0
        return (self.stop_hz - self.start_hz) / (self.count - 1)

    @property
    def frequencies_hz(self) -> tuple[float, ...]:
        if self.count == 1:
            return (self.start_hz,)
        step = self.step_hz
        return tuple(self.start_hz + index * step for index in range(self.count))

    def snapshot_frequencies(
        self,
        max_count: int,
        *,
        preferred_frequency_hz: float | None = None,
    ) -> tuple[float, ...]:
        """Return up to ``max_count`` representative frequencies from the plan.

        The first and last plan frequencies are always included. When
        ``preferred_frequency_hz`` is inside the plan and ``max_count >= 3``,
        the evenly spaced index closest to it is replaced by the nearest plan
        frequency, so the design frequency normally has a pattern snapshot.

        This is used to compute far-field patterns at a small number of
        frequencies while keeping the full impedance sweep.
        """

        if max_count < 1:
            raise ValueError("max_count must be at least 1")
        if self.count <= max_count:
            return self.frequencies_hz
        preferred_index = self._plan_index(preferred_frequency_hz)
        if max_count == 1:
            if preferred_index is None:
                return (self.start_hz,)
            return (self.start_hz + preferred_index * self.step_hz,)
        last_index = self.count - 1
        indices = sorted(
            {round(index * last_index / (max_count - 1)) for index in range(max_count)}
        )
        if preferred_index is not None and preferred_index not in indices:
            interior = [index for index in indices if 0 < index < last_index]
            if interior:
                closest = min(interior, key=lambda index: abs(index - preferred_index))
                indices = sorted({*indices, preferred_index} - {closest})
        step = self.step_hz
        return tuple(self.start_hz + index * step for index in indices)

    def _plan_index(self, frequency_hz: float | None) -> int | None:
        if frequency_hz is None:
            return None
        index = round((frequency_hz - self.start_hz) / self.step_hz)
        if 0 <= index < self.count:
            return index
        return None

    def nearest_frequency(self, frequency_hz: float) -> float:
        """Return the plan frequency closest to ``frequency_hz``."""

        if self.count == 1:
            return self.start_hz
        index = round((frequency_hz - self.start_hz) / self.step_hz)
        index = min(max(index, 0), self.count - 1)
        return self.start_hz + index * self.step_hz
