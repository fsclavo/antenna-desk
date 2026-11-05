# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fail a packaging build when the required license notices are missing."""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_FILES = (
    ("COPYING", "GNU GENERAL PUBLIC LICENSE"),
    ("licenses/THIRD_PARTY_NOTICES.md", "nec2c"),
    ("licenses/THIRD_PARTY_NOTICES.md", "PySide6"),
    ("licenses/THIRD_PARTY_NOTICES.md", "Qt"),
    ("licenses/LGPL-3.0.txt", "GNU LESSER GENERAL PUBLIC LICENSE"),
)


def check(bundle: Path) -> list[str]:
    missing: list[str] = []
    for relative, marker in REQUIRED_FILES:
        path = bundle / relative
        if not path.is_file():
            missing.append(f"missing {relative}")
            continue
        if marker not in path.read_text(encoding="utf-8"):
            missing.append(f"{relative} does not contain {marker!r}")

    nec2c_source = bundle / "licenses" / "nec2c"
    if not nec2c_source.is_dir():
        missing.append("missing licenses/nec2c/")
    elif (
        not any(nec2c_source.glob("nec2c-*.tar.gz")) and not (nec2c_source / "SOURCE.txt").is_file()
    ):
        missing.append("missing licenses/nec2c/ source tarball or SOURCE.txt")
    return missing


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("usage: check_bundle_licenses.py BUNDLE", file=sys.stderr)
        return 2
    bundle = Path(arguments[0])
    if not bundle.is_dir():
        print(f"bundle not found: {bundle}", file=sys.stderr)
        return 2
    missing = check(bundle)
    if missing:
        print("license audit failed:", file=sys.stderr)
        for item in missing:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print(f"license audit passed: {bundle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
