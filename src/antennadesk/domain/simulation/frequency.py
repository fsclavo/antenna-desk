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
