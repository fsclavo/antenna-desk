#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Remove local packaging artifacts produced by the bundle scripts.
# This does not touch spikes/phase0/build/ (the nec2c build used for tests).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

rm -rf "$ROOT/build"
rm -f "$ROOT"/dist/AntennaDesk-*.AppImage \
  "$ROOT"/dist/AntennaDesk-*.AppImage.sha256 \
  "$ROOT"/dist/antennadesk_*.deb \
  "$ROOT"/dist/antennadesk_*.deb.sha256 \
  "$ROOT"/dist/AntennaDesk-*-windows-x86_64.zip \
  "$ROOT"/dist/AntennaDesk-*-windows-x86_64.zip.sha256 \
  "$ROOT"/dist/AntennaDesk-*-windows-x86_64-setup.exe \
  "$ROOT"/dist/AntennaDesk-*-windows-x86_64-setup.exe.sha256 \
  "$ROOT"/dist/antennadesk-*.whl \
  "$ROOT"/dist/antennadesk-*.tar.gz
rmdir "$ROOT/dist" 2>/dev/null || true

echo "Removed local packaging artifacts."
