# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""PyInstaller specification for the AntennaDesk desktop bundle."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent

datas = [
    (
        str(ROOT / "src" / "antennadesk" / "ui" / "resources" / "antennadesk.svg"),
        "antennadesk/ui/resources",
    ),
]

analysis = Analysis(
    [str(ROOT / "packaging" / "antennadesk_entry.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="AntennaDesk",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "packaging" / "antennadesk.ico") if sys.platform == "win32" else None,
)

collect = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AntennaDesk",
)
