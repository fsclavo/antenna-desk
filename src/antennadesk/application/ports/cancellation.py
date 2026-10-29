"""Cancellation port."""

from __future__ import annotations

from typing import Protocol


class CancelToken(Protocol):
    """A token that reports whether a long-running operation was cancelled."""

    def is_cancelled(self) -> bool: ...
