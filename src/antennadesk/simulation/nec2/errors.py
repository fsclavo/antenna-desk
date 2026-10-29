"""NEC-2 adapter errors."""

from __future__ import annotations


class SolverNotAvailable(RuntimeError):
    """The configured solver executable cannot be executed."""


class SolverExecutionError(RuntimeError):
    """The solver failed to produce usable output."""
