#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Cross-build or native-build nec2c for Windows.
#
# On MSYS2/MinGW use the default gcc.  On Linux, either use a MinGW
# cross-compiler or Zig:
#
#   CC="zig cc -target x86_64-windows-gnu" \
#     bash spikes/phase0/scripts/build_nec2c_windows.sh
#
# The patch adds a small getopt() replacement and replaces POSIX-only
# signal/timing calls.  It is maintained in patches/nec2c-windows.patch.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE="$ROOT/.cache"
BUILD="$ROOT/build"
COMMIT="55be1e0e3fe5ee9dad4ce6050711450d19c562fd"
TARBALL="$CACHE/nec2c-$COMMIT.tar.gz"
URL="https://github.com/KJ7LNW/nec2c/archive/$COMMIT.tar.gz"
SHA256="35c9c8cae99d9b95c628e70047352beb458090d1d9682c8529bc7a5bcf33dcfd"
SRC="$CACHE/nec2c-$COMMIT"
SRC_WIN="$CACHE/nec2c-$COMMIT-win"
PATCH_FILE="$ROOT/patches/nec2c-windows.patch"

SOURCES=(
  calculations.c
  geometry.c
  input.c
  matrix.c
  network.c
  shared.c
  fields.c
  ground.c
  main.c
  misc.c
  radiation.c
  somnec.c
)

mkdir -p "$CACHE" "$BUILD"

if [[ ! -f "$TARBALL" ]]; then
  echo "Downloading nec2c source..."
  curl -L --fail --retry 3 --output "$TARBALL.tmp" "$URL"
  mv "$TARBALL.tmp" "$TARBALL"
fi

echo "$SHA256  $TARBALL" | sha256sum -c -

if [[ ! -d "$SRC" ]]; then
  tar -xzf "$TARBALL" -C "$CACHE"
fi

if [[ ! -d "$SRC_WIN" ]]; then
  cp -a "$SRC" "$SRC_WIN"
fi

if ! grep -q "_WIN32" "$SRC_WIN/nec2c.h"; then
  echo "Applying Windows compatibility patch..."
  patch -p1 -d "$SRC_WIN" < "$PATCH_FILE"
fi

if [[ -n "${CC:-}" ]]; then
  CC_CMD=($CC)
elif command -v x86_64-w64-mingw32-gcc >/dev/null 2>&1; then
  CC_CMD=(x86_64-w64-mingw32-gcc)
elif command -v zig >/dev/null 2>&1; then
  CC_CMD=(zig cc -target x86_64-windows-gnu)
else
  echo "error: no Windows C compiler found; set CC" >&2
  exit 1
fi

echo "Building nec2c.exe with: ${CC_CMD[*]}"

SOURCE_PATHS=()
for source in "${SOURCES[@]}"; do
  SOURCE_PATHS+=("$SRC_WIN/$source")
done

"${CC_CMD[@]}" -O2 -w \
  '-DPACKAGE_STRING="nec2c 1.3.3"' \
  -o "$BUILD/nec2c.exe" \
  "${SOURCE_PATHS[@]}" \
  -lm

echo "Built: $BUILD/nec2c.exe"
