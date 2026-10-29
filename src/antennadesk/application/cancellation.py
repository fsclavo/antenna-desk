"""Thread-safe cancellation helpers."""

from __future__ import annotations

import threading


class EventCancelToken:
    """A cancellation token backed by ``threading.Event``."""

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()
