#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build the pinned nec2c reference engine for the host platform.
#
# The source is the KJ7LNW/nec2c fork at the commit evaluated during Phase 0.
# Upstream nec2c 1.3.1 is public domain; the fork is distributed under
# GPL-3.0.  The AntennaDesk project is GPL-3.0-or-later, so either is
# compatible.  See docs/ADR/0001-solver-selection.md.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE="$ROOT/.cache"
BUILD="$ROOT/build"
COMMIT="55be1e0e3fe5ee9dad4ce6050711450d19c562fd"
TARBALL="$CACHE/nec2c-$COMMIT.tar.gz"
URL="https://github.com/KJ7LNW/nec2c/archive/$COMMIT.tar.gz"
SHA256="35c9c8cae99d9b95c628e70047352beb458090d1d9682c8529bc7a5bcf33dcfd"
SRC="$CACHE/nec2c-$COMMIT"

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

CC_CMD=(${CC:-cc})
echo "Building nec2c with: ${CC_CMD[*]}"

SOURCE_PATHS=()
for source in "${SOURCES[@]}"; do
  SOURCE_PATHS+=("$SRC/$source")
done

"${CC_CMD[@]}" -O2 -w \
  '-DPACKAGE_STRING="nec2c 1.3.3"' \
  -o "$BUILD/nec2c" \
  "${SOURCE_PATHS[@]}" \
  -lm

"$BUILD/nec2c" -v
echo "Built: $BUILD/nec2c"
