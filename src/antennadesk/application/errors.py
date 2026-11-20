# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Application-level failures shared across adapters."""

from __future__ import annotations


class ProjectPayloadTooLargeError(Exception):
    """A project payload exceeds the configured storage or reopen limit.

    The structured fields let the UI report the real size and limit without
    parsing an adapter-specific message.
    """

    def __init__(
        self,
        message: str,
        *,
        size: int,
        limit: int,
        expanded: bool,
    ) -> None:
        super().__init__(message)
        self.size = size
        self.limit = limit
        self.expanded = expanded
