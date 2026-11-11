#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build a Debian package from the shared PyInstaller onedir bundle.
#
# Requirements:
#   - uv
#   - dpkg-deb
#   - a nec2c build in spikes/phase0/build/ or NEC2C pointing to it
#
# Usage:
#   packaging/build_deb.sh
#   NEC2C=/path/to/nec2c packaging/build_deb.sh
#   BUILD_DIR=/tmp/build DIST_DIR=/tmp/dist packaging/build_deb.sh
#
# BUILD_DIR and DIST_DIR can point outside the repository for clean-room
# validation; both are removed/replaced by the build.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APP_NAME="AntennaDesk"
BUILD_DIR="${BUILD_DIR:-$ROOT/build}"
DIST_DIR="${DIST_DIR:-$ROOT/dist}"
VERSION="$(uv run python -c 'import antennadesk; print(antennadesk.__version__)')"
DEB_VERSION="${VERSION/.dev/~dev}"
BUNDLE="$BUILD_DIR/pyinstaller-dist/$APP_NAME"

case "$(uname -m)" in
  x86_64) DEFAULT_DEB_ARCH="amd64" ;;
  aarch64) DEFAULT_DEB_ARCH="arm64" ;;
  *) DEFAULT_DEB_ARCH="" ;;
esac
DEB_ARCH="${DEB_ARCH:-$DEFAULT_DEB_ARCH}"
if [[ -z "$DEB_ARCH" ]]; then
  DEB_ARCH="$(dpkg --print-architecture)"
fi

OUTPUT="$DIST_DIR/antennadesk_${DEB_VERSION}_${DEB_ARCH}.deb"
STAGE="$BUILD_DIR/deb/antennadesk_${DEB_VERSION}_${DEB_ARCH}"

if ! command -v dpkg-deb >/dev/null 2>&1; then
  echo "dpkg-deb not found; this script requires a Debian-based system." >&2
  exit 1
fi

echo "Building $APP_NAME $DEB_VERSION for $DEB_ARCH"
rm -rf "$STAGE"
mkdir -p "$DIST_DIR"
packaging/build_frozen_bundle.sh

if [[ ! -x "$BUNDLE/$APP_NAME" ]]; then
  echo "PyInstaller bundle missing at $BUNDLE/$APP_NAME" >&2
  exit 1
fi

install -d \
  "$STAGE/DEBIAN" \
  "$STAGE/opt" \
  "$STAGE/usr/bin" \
  "$STAGE/usr/share/applications" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps" \
  "$STAGE/usr/share/icons/hicolor/256x256/apps" \
  "$STAGE/usr/share/doc/antennadesk"

cp -a "$BUNDLE" "$STAGE/opt/antennadesk"
ln -s "/opt/antennadesk/$APP_NAME" "$STAGE/usr/bin/antennadesk"
install -m 644 "$ROOT/packaging/antennadesk.desktop" \
  "$STAGE/usr/share/applications/antennadesk.desktop"
install -m 644 "$ROOT/src/antennadesk/ui/resources/antennadesk.svg" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps/antennadesk.svg"
install -m 644 "$ROOT/packaging/antennadesk.png" \
  "$STAGE/usr/share/icons/hicolor/256x256/apps/antennadesk.png"
install -m 644 "$ROOT/packaging/debian/copyright" \
  "$STAGE/usr/share/doc/antennadesk/copyright"
install -m 644 "$ROOT/LICENSE" "$STAGE/usr/share/doc/antennadesk/COPYING"
install -m 644 "$ROOT/packaging/licenses/THIRD_PARTY_NOTICES.md" \
  "$STAGE/usr/share/doc/antennadesk/THIRD_PARTY_NOTICES.md"
install -m 644 "$ROOT/packaging/licenses/LGPL-3.0.txt" \
  "$STAGE/usr/share/doc/antennadesk/LGPL-3.0.txt"

cat > "$STAGE/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if [ "$1" = "configure" ]; then
  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
  fi
  if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
  fi
fi
exit 0
EOF

cat > "$STAGE/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e
if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
  fi
  if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
  fi
fi
exit 0
EOF
chmod 755 "$STAGE/DEBIAN/postinst" "$STAGE/DEBIAN/postrm"

{
  echo "antennadesk ($DEB_VERSION) unstable; urgency=medium"
  echo
  echo "  * Local package build."
  echo
  echo " -- Fernando Sclavo (LU2EFI) <fernando.sclavo@ingenia.la>  $(date -Ru)"
} | gzip -9n > "$STAGE/usr/share/doc/antennadesk/changelog.Debian.gz"

INSTALLED_SIZE="$(du -sk "$STAGE/opt" "$STAGE/usr" | awk '{total += $1} END {print total}')"
cat > "$STAGE/DEBIAN/control" <<EOF
Package: antennadesk
Version: $DEB_VERSION
Section: science
Priority: optional
Architecture: $DEB_ARCH
Maintainer: Fernando Sclavo (LU2EFI) <fernando.sclavo@ingenia.la>
Installed-Size: $INSTALLED_SIZE
Depends: libc6 (>= 2.35), libgl1, libegl1, libxkbcommon-x11-0, libxcb-cursor0, libxcb-icccm4, libxcb-keysyms1, libxcb-shape0, libxcb-xinerama0, libxcb-randr0, libxcb-render-util0, libxcb-xfixes0, libdbus-1-3, libfontconfig1, libglib2.0-0
Homepage: https://github.com/fsclavo/antenna-desk
Description: Antenna design, simulation, and construction for amateur radio
 AntennaDesk is a local-first desktop application for designing, simulating,
 and building antennas. This package bundles the NEC-2 engine and the Python
 runtime.
EOF
chmod 644 "$STAGE/DEBIAN/control"

dpkg-deb --build --root-owner-group "$STAGE" "$OUTPUT"

(
  cd "$DIST_DIR"
  sha256sum "$(basename "$OUTPUT")" > "$(basename "$OUTPUT").sha256"
)
echo "Created $OUTPUT"
