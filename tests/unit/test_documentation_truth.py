# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Documentation truth checks for claims that have changed in shipped behavior."""

from __future__ import annotations

from pathlib import Path

from antennadesk.persistence.constants import SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
DOCS = ROOT / "docs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readme_status_and_gain_claims_match_the_shipped_application() -> None:
    text = _read(README)

    normalized = " ".join(text.lower().split())

    assert "pre-alpha" not in text
    assert "Realized gain and directivity are not" not in text
    assert "pattern charts can display power gain, directivity, or realized gain" in normalized
    assert "EVIDENCE_AUDIT.md" in text
    assert "docs/ADR" in text


def test_solver_adapter_does_not_claim_results_and_progress_are_missing() -> None:
    text = _read(DOCS / "SOLVER_ADAPTER.md")

    assert "Results are not persisted in the project file yet." not in text
    assert "No progress reporting, because nec2c does not provide real progress" not in text
    assert "schema 30 and later" in text


def test_user_guide_limitations_match_shipped_optimizer_and_feed_line() -> None:
    text = _read(DOCS / "USER_GUIDE.md")

    assert "There are no boom-length or turning-radius constraints." not in text
    assert "does not add line loss to the pattern gain or" not in text
    assert "maximum turning-radius" in text
    assert "its loss is included in the transmitter-side" in text
    assert "EVIDENCE_AUDIT.md" in text
    assert "[ADR](ADR/)" in text


def test_schema_documents_name_the_current_version() -> None:
    architecture = _read(DOCS / "ARCHITECTURE.md")
    domain = _read(DOCS / "DOMAIN_MODEL.md")

    assert f"Schema version {SCHEMA_VERSION} is" in architecture
    assert f"Current version: `{SCHEMA_VERSION}`" in domain
    assert "Version 56 adds the Beverage feed-transformer ratio" in domain
