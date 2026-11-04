# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rewrite the evidence table in docs/VALIDATION_PLAN.md from the registry."""

from __future__ import annotations

from pathlib import Path

from antennadesk.domain.design.evidence import render_markdown_table

START = "<!-- evidence-table:start -->"
END = "<!-- evidence-table:end -->"
PATH = Path(__file__).resolve().parents[1] / "docs" / "VALIDATION_PLAN.md"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    before, rest = text.split(START)
    _, after = rest.split(END)
    PATH.write_text(
        f"{before}{START}\n{render_markdown_table()}\n{END}{after}",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
