#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build a Linux AppImage from the shared PyInstaller onedir bundle.
#
# Requirements:
#   - uv
#   - appimagetool on PATH (or APPIMAGETOOL pointing to it)
#   - a nec2c build in spikes/phase0/build/ or NEC2C pointing to it
#
# Usage:
#   packaging/build_appimage.sh
#   NEC2C=/path/to/nec2c packaging/build_appimage.sh
#   APPIMAGE_SIGN_KEY=<gpg-key-id> packaging/build_appimage.sh
#
# BUILD_DIR and DIST_DIR can point outside the repository for clean-room
# validation; both are removed/replaced by the build.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APP_NAME="AntennaDesk"
ARCH="${ARCH:-x86_64}"
APPIMAGETOOL="${APPIMAGETOOL:-appimagetool}"
BUILD_DIR="${BUILD_DIR:-$ROOT/build}"
DIST_DIR="${DIST_DIR:-$ROOT/dist}"
APP_DIR="$BUILD_DIR/$APP_NAME.AppDir"
BUNDLE="$BUILD_DIR/pyinstaller-dist/$APP_NAME"
VERSION="$(uv run python -c 'import antennadesk; print(antennadesk.__version__)')"
OUTPUT="$DIST_DIR/$APP_NAME-$VERSION-$ARCH.AppImage"

if ! command -v "$APPIMAGETOOL" >/dev/null 2>&1; then
  echo "appimagetool not found; set APPIMAGETOOL or install it." >&2
  exit 1
fi

echo "Building $APP_NAME $VERSION for $ARCH"
rm -rf "$APP_DIR"
mkdir -p "$DIST_DIR"
packaging/build_frozen_bundle.sh

if [[ ! -x "$BUNDLE/$APP_NAME" ]]; then
  echo "PyInstaller bundle missing at $BUNDLE/$APP_NAME" >&2
  exit 1
fi

install -d "$APP_DIR/usr/bin" \
  "$APP_DIR/usr/share/applications" \
  "$APP_DIR/usr/share/icons/hicolor/scalable/apps"
cp -a "$BUNDLE" "$APP_DIR/usr/bin/$APP_NAME"
install -m 644 "$ROOT/src/antennadesk/ui/resources/antennadesk.svg" "$APP_DIR/antennadesk.svg"
install -m 644 "$ROOT/src/antennadesk/ui/resources/antennadesk.svg" \
  "$APP_DIR/usr/share/icons/hicolor/scalable/apps/antennadesk.svg"

cat > "$APP_DIR/antennadesk.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Comment=Antenna design, simulation, and construction for amateur radio
Exec=$APP_NAME
Icon=antennadesk
Terminal=false
Categories=Science;Engineering;
StartupWMClass=$APP_NAME
EOF
install -m 644 "$APP_DIR/antennadesk.desktop" \
  "$APP_DIR/usr/share/applications/antennadesk.desktop"

cat > "$APP_DIR/AppRun" <<'EOF'
#!/bin/sh
set -e
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/AntennaDesk/AntennaDesk" "$@"
EOF
chmod 755 "$APP_DIR/AppRun"

APPIMAGE_ARGS=(--no-appstream)
if [[ -n "${APPIMAGE_RUNTIME_FILE:-}" ]]; then
  APPIMAGE_ARGS+=(--runtime-file "$APPIMAGE_RUNTIME_FILE")
fi
if [[ -n "${APPIMAGE_SIGN_KEY:-}" ]]; then
  APPIMAGE_ARGS+=(--sign --sign-key "$APPIMAGE_SIGN_KEY")
fi

APPIMAGE_EXTRACT_AND_RUN=1 ARCH="$ARCH" "$APPIMAGETOOL" \
  "${APPIMAGE_ARGS[@]}" "$APP_DIR" "$OUTPUT"

(
  cd "$DIST_DIR"
  sha256sum "$(basename "$OUTPUT")" > "$(basename "$OUTPUT").sha256"
)
echo "Created $OUTPUT"
