#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Create detached ASCII-armored GPG signatures for release artifacts.
#
# Usage:
#   GPG_KEY_ID=<fingerprint-or-email> packaging/sign_artifacts.sh
#   GPG_KEY_ID=... GPG_PASSPHRASE=... packaging/sign_artifacts.sh
#   DIST_DIR=/tmp/dist GPG_KEY_ID=... packaging/sign_artifacts.sh
#
# The private key must already be present in the active GPG keyring. In CI,
# import it from a protected secret before running this script.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${DIST_DIR:-$ROOT/dist}"
GPG_KEY_ID="${GPG_KEY_ID:-}"

if ! command -v gpg >/dev/null 2>&1; then
  echo "gpg not found." >&2
  exit 1
fi
if [[ -z "$GPG_KEY_ID" ]]; then
  echo "GPG_KEY_ID must identify the signing key." >&2
  exit 1
fi

GPG_ARGS=(
  --batch
  --yes
  --armor
  --detach-sign
  --local-user "$GPG_KEY_ID"
)
if [[ -n "${GPG_PASSPHRASE:-}" ]]; then
  GPG_ARGS+=(--pinentry-mode loopback --passphrase "$GPG_PASSPHRASE")
fi

shopt -s nullglob
artifacts=(
  "$DIST_DIR"/*.whl
  "$DIST_DIR"/*.tar.gz
  "$DIST_DIR"/*.AppImage
  "$DIST_DIR"/*.deb
  "$DIST_DIR"/*.zip
)
if (( ${#artifacts[@]} == 0 )); then
  echo "No release artifacts found in $DIST_DIR" >&2
  exit 1
fi

for artifact in "${artifacts[@]}"; do
  signature="$artifact.asc"
  rm -f "$signature"
  gpg "${GPG_ARGS[@]}" --output "$signature" "$artifact"
  gpg --verify "$signature" "$artifact" >/dev/null 2>&1
  echo "Signed $artifact"
done

echo "Created ${#artifacts[@]} detached signature(s)."
