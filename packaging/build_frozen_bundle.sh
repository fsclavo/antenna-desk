#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build the shared PyInstaller onedir bundle used by the AppImage and .deb
# packages. The bundle is written to:
#
#   ${BUILD_DIR:-<repo>/build}/pyinstaller-dist/AntennaDesk
#
# nec2c is copied next to the frozen executable so find_nec2c() discovers it.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BUILD_DIR="${BUILD_DIR:-$ROOT/build}"
PYINSTALLER_DIST="$BUILD_DIR/pyinstaller-dist"
PYINSTALLER_WORK="$BUILD_DIR/pyinstaller"
NEC2C_BINARY="${NEC2C:-$ROOT/spikes/phase0/build/nec2c}"

if [[ ! -f "$NEC2C_BINARY" ]]; then
  echo "nec2c not found at $NEC2C_BINARY" >&2
  echo "Build it with spikes/phase0/scripts/build_nec2c.sh or set NEC2C." >&2
  exit 1
fi

rm -rf "$PYINSTALLER_DIST" "$PYINSTALLER_WORK"
mkdir -p "$PYINSTALLER_DIST"

uv run --group packaging pyinstaller \
  packaging/antennadesk.spec \
  --noconfirm \
  --clean \
  --distpath "$PYINSTALLER_DIST" \
  --workpath "$PYINSTALLER_WORK"

BUNDLE="$PYINSTALLER_DIST/AntennaDesk"
if [[ ! -x "$BUNDLE/AntennaDesk" ]]; then
  echo "PyInstaller did not produce $BUNDLE/AntennaDesk" >&2
  exit 1
fi

install -m 755 "$NEC2C_BINARY" "$BUNDLE/nec2c"
