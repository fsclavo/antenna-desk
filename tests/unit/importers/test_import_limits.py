# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Size guards for untrusted text imports."""

from __future__ import annotations

from pathlib import Path

import pytest

from antennadesk import importers
from antennadesk.importers import read_import_text


def test_small_import_is_read(tmp_path: Path) -> None:
    path = tmp_path / "small.nec"
    path.write_text("CM test\n", encoding="utf-8")

    assert read_import_text(path) == "CM test\n"


def test_oversized_import_is_rejected_before_decode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(importers, "MAX_IMPORT_FILE_BYTES", 8)
    path = tmp_path / "large.nec"
    path.write_bytes(b"x" * 9)

    with pytest.raises(ValueError, match="too large"):
        read_import_text(path)
