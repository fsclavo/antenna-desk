from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest

from antennadesk.domain.common.ids import new_id, parse_id
from antennadesk.domain.common.time import ensure_utc, utc_now
from antennadesk.domain.common.validation import (
    Diagnostic,
    DomainValidationError,
    Severity,
    has_errors,
    raise_if_errors,
)


def test_parse_id_round_trip() -> None:
    identifier = new_id()
    assert parse_id(str(identifier)) == identifier


def test_parse_id_rejects_invalid_text() -> None:
    with pytest.raises(ValueError, match="invalid UUID"):
        parse_id("not-a-uuid")


def test_diagnostic_requires_code_and_message() -> None:
    with pytest.raises(ValueError, match="code"):
        Diagnostic(code=" ", severity=Severity.ERROR, message="message")
    with pytest.raises(ValueError, match="message"):
        Diagnostic(code="code", severity=Severity.ERROR, message=" ")


def test_has_errors_and_raise_if_errors() -> None:
    warning = Diagnostic(code="w", severity=Severity.WARNING, message="warning")
    error = Diagnostic(code="e", severity=Severity.ERROR, message="error")

    assert has_errors([warning]) is False
    assert has_errors([warning, error]) is True
    raise_if_errors([warning])

    with pytest.raises(DomainValidationError, match="e: error"):
        raise_if_errors([warning, error])


def test_domain_validation_error_requires_an_error() -> None:
    warning = Diagnostic(code="w", severity=Severity.WARNING, message="warning")
    with pytest.raises(ValueError, match="at least one error"):
        DomainValidationError([warning])


def test_utc_now_is_timezone_aware() -> None:
    now = utc_now()
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)


def test_ensure_utc_converts_offsets() -> None:
    value = datetime(2026, 10, 29, 12, 0, 0, tzinfo=timezone(timedelta(hours=-3)))
    converted = ensure_utc(value, name="timestamp")
    assert converted.tzinfo is UTC
    assert converted.hour == 15


def test_ensure_utc_rejects_naive_values() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ensure_utc(datetime(2026, 10, 29, 12, 0, 0), name="timestamp")
