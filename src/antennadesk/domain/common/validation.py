# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validation primitives shared by domain objects."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A structured validation message."""

    code: str
    severity: Severity
    message: str
    field: str | None = None

    def __post_init__(self) -> None:
        if not self.code.strip():
            raise ValueError("diagnostic code must not be empty")
        if not self.message.strip():
            raise ValueError("diagnostic message must not be empty")


def has_errors(diagnostics: Sequence[Diagnostic]) -> bool:
    return any(diagnostic.severity is Severity.ERROR for diagnostic in diagnostics)


class DomainValidationError(ValueError):
    """Raised when an object would violate a domain invariant."""

    def __init__(self, diagnostics: Sequence[Diagnostic]) -> None:
        self.diagnostics = tuple(diagnostics)
        errors = [
            diagnostic for diagnostic in self.diagnostics if diagnostic.severity is Severity.ERROR
        ]
        if not errors:
            raise ValueError("DomainValidationError requires at least one error diagnostic")
        details = "; ".join(f"{diagnostic.code}: {diagnostic.message}" for diagnostic in errors)
        super().__init__(details)


def raise_if_errors(diagnostics: Sequence[Diagnostic]) -> None:
    if has_errors(diagnostics):
        raise DomainValidationError(diagnostics)
