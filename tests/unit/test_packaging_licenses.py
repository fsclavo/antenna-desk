# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""The binary packaging must carry the license texts and third-party notices."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLLECT = ROOT / "packaging" / "collect_bundle_licenses.py"
CHECK = ROOT / "packaging" / "check_bundle_licenses.py"
NOTICES = ROOT / "packaging" / "licenses" / "THIRD_PARTY_NOTICES.md"
LGPL = ROOT / "packaging" / "licenses" / "LGPL-3.0.txt"


def _run(script: Path, bundle: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - runs a repository script with this interpreter
        [sys.executable, str(script), str(bundle)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_license_notices_exist_and_name_the_bundled_components() -> None:
    notices = NOTICES.read_text(encoding="utf-8")
    assert "nec2c" in notices
    assert "PySide6" in notices
    assert "Qt" in notices
    assert "GPL-3.0" in notices
    assert "LGPL-3.0" in notices
    assert "GNU LESSER GENERAL PUBLIC LICENSE" in LGPL.read_text(encoding="utf-8")


def test_packaging_scripts_run_the_license_audit() -> None:
    for relative in (
        "packaging/build_frozen_bundle.sh",
        "packaging/build_windows.ps1",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "collect_bundle_licenses.py" in text, relative
        assert "check_bundle_licenses.py" in text, relative

    for relative in ("packaging/build_appimage.sh", "packaging/build_deb.sh"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "THIRD_PARTY_NOTICES.md" in text, relative
        assert "COPYING" in text, relative


def test_collected_bundle_passes_and_a_missing_notice_fails(tmp_path: Path) -> None:
    bundle = tmp_path / "AntennaDesk"
    bundle.mkdir()

    collected = _run(COLLECT, bundle)
    assert collected.returncode == 0, collected.stderr
    assert (bundle / "COPYING").is_file()
    assert (bundle / "licenses" / "THIRD_PARTY_NOTICES.md").is_file()
    assert (bundle / "licenses" / "LGPL-3.0.txt").is_file()
    assert (bundle / "licenses" / "nec2c").is_dir()

    checked = _run(CHECK, bundle)
    assert checked.returncode == 0, checked.stderr

    (bundle / "licenses" / "THIRD_PARTY_NOTICES.md").unlink()
    checked = _run(CHECK, bundle)
    assert checked.returncode == 1
    assert "THIRD_PARTY_NOTICES.md" in checked.stderr
