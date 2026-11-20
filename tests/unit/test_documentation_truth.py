# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Documentation truth checks for claims that have changed in shipped behavior."""

from __future__ import annotations

import re
from pathlib import Path

from antennadesk.persistence.constants import SCHEMA_VERSION

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
DOCS = ROOT / "docs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _markdown_files() -> list[Path]:
    return sorted(
        [
            *DOCS.rglob("*.md"),
            ROOT / "README.md",
            ROOT / "CHANGELOG.md",
            ROOT / "AGENTS.md",
        ]
    )


def _without_fenced_code(text: str) -> str:
    return re.sub(r"(?ms)^```.*?^```\s*$", "", text)


def test_local_markdown_links_resolve() -> None:
    broken: list[str] = []
    for path in _markdown_files():
        text = _without_fenced_code(_read(path))
        for raw_target in re.findall(r"\]\(([^)]+)\)", text):
            target = raw_target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            file_target = target.split("#", 1)[0].strip()
            if not file_target:
                continue
            if file_target.startswith("<") and file_target.endswith(">"):
                file_target = file_target[1:-1]
            if not (path.parent / file_target).resolve().exists():
                broken.append(f"{path.relative_to(ROOT)} -> {raw_target}")

    assert not broken, "Broken local Markdown links:\n" + "\n".join(broken)


def test_changelog_sections_do_not_repeat_entries() -> None:
    text = _read(ROOT / "CHANGELOG.md")
    parts = re.split(r"(?m)^## ", text)

    for part in parts[1:]:
        release = part.splitlines()[0]
        for subsection in re.split(r"(?m)^### ", part)[1:]:
            subheader = subsection.splitlines()[0]
            entries = re.findall(
                r"(?ms)^- \*\*(.+?)\*\*(.*?)(?=^- \*\*|^### |^## |\Z)",
                subsection,
            )
            keys = [(title, " ".join(body.split())) for title, body in entries]
            duplicated = sorted({key[0] for key in keys if keys.count(key) > 1})
            assert not duplicated, f"{release} / {subheader} repeats entries: {duplicated}"


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
    readme = _read(README)
    status = _read(DOCS / "STATUS.md")
    backlog = _read(DOCS / "AUTONOMOUS_BACKLOG.md")

    assert f"Schema version {SCHEMA_VERSION} is" in architecture
    assert f"Current version: `{SCHEMA_VERSION}`" in domain
    assert f"writes version {SCHEMA_VERSION}" in domain
    assert f"current development schema is `{SCHEMA_VERSION}`" in readme
    assert f"**Development schema:** `{SCHEMA_VERSION}`" in status
    assert f"Schema: **{SCHEMA_VERSION}**" in backlog


def test_changelog_does_not_repeat_unreleased_entries_in_release_sections() -> None:
    text = _read(ROOT / "CHANGELOG.md")
    parts = re.split(r"(?m)^## ", text)
    sections = {part.splitlines()[0]: part for part in parts[1:]}
    unreleased = next(
        body for header, body in sections.items() if header.startswith("[Unreleased]")
    )
    titles = set(re.findall(r"(?m)^- \*\*(.+?)\*\*", unreleased))

    assert titles
    for header, body in sections.items():
        if header.startswith("[Unreleased]"):
            continue
        repeated = titles & set(re.findall(r"(?m)^- \*\*(.+?)\*\*", body))
        assert not repeated, f"{header} repeats Unreleased entries: {sorted(repeated)}"


def test_docs_index_lists_every_current_document() -> None:
    index = _read(DOCS / "README.md")
    linked = {
        (DOCS / target.split("#", 1)[0]).resolve()
        for target in re.findall(r"\]\(([^)]+\.md)(?:#[^)]*)?\)", index)
        if not target.startswith(("http://", "https://"))
    }

    for path in DOCS.rglob("*.md"):
        if path.parent == DOCS and path.name == "README.md":
            continue
        if "archive" in path.parts:
            continue
        assert path.resolve() in linked, f"{path.relative_to(ROOT)} is not indexed"
