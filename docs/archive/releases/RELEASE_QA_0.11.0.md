# AntennaDesk 0.11.0 release QA

- **Version:** `0.11.0`
- **Date:** 2026-11-27
- **Tag:** `v0.11.0`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.11.0>
- **Status:** release candidate; tag and asset publication pending
- **Schema:** 73
- **Previous release:** `0.10.1` (2026-11-24)

## Scope

This minor release packages the unreleased work since 0.10.1:

- **UX46–UX49:** 3D pattern orientation, max-gain/back rays, plan mini-map,
  schematic antenna overlay, linked geometry/pattern cameras, and the shared
  antenna/feed visual language.
- **UX50–UX55:** the generator-dialog layout standard, wide and complex-family
  migrations, the compact-family closure, and the cross-family automated layout
  matrix.
- **UX56–UX57:** beam-symmetry-plane overlay centering and the rear-gain back
  ray.
- **DL6:** the extended stacked-Yagi slice with per-level sources, splitter and
  phase-line feed specification, the co-simulated network mode, Wilkinson
  divider with matching and tolerance analysis, isolation-resistor parasitics,
  per-level transformer ratios, folded driven elements, and the bounded
  spacing/phase optimizer inside the top-height envelope.
- **FP1:** the half-wave Flower Pot family, including the schema 73 physical
  feed/choke correction, the construction-only 45/63 mm choke heights, the
  physical-versus-NEC-equivalent split, the estimator, optimizer, scene,
  reports/BOM, and the physical-feed-anchored pattern overlay.

## Schema and compatibility

- **Current schema:** 73.
- Schema 72 added the Flower Pot payload; schema 73 added the construction-only
  choke height and the feed-height semantics with an additive 72→73 migration.
- Existing 72 Flower Pot payloads load with a zero choke and unchanged
  lower-cut geometry.
- The accepted migration path remains 59 through 72; older or newer schemas are
  rejected.
- No solver or electromagnetic-model change is included in the FP1 correction;
  the two-wire center-fed NEC equivalent and the 1.087 scale remain.

## Validation

- **Full gate:** **4,787 passed, 1 skipped** with the Windows-only console-hiding
  check skipped on Linux.
- `uv run ruff check .` — pass.
- `uv run ruff format --check .` — pass.
- `uv run mypy` — pass.
- `uv run mypy --config-file mypy_ui.ini` — pass.
- `NEC2C=spikes/phase0/build/nec2c uv run pytest tests/integration/simulation`
  — **186 passed**.
- Flower Pot domain, persistence, estimator, optimizer, catalog, form, scene,
  report, help, and pattern-overlay regressions pass.
- UX56/UX57 pure overlay/back-ray tests and scene snapshots pass.
- The full documentation-truth and changelog-structure checks pass.
- The wheel/sdist build is recorded below.

## Packaging

- `uv build --out-dir …` produced `antennadesk-0.11.0-py3-none-any.whl`
  (1.3 MiB) and `antennadesk-0.11.0.tar.gz` (2.1 MiB).
- Wheel metadata reports version `0.11.0`.
- `python -m antennadesk.ui.app --version` reports `0.11.0`.
- `uv lock --check` passes.

The tag workflow builds the Linux AppImage and Debian package, and the Windows
installer and portable zip with bundled `nec2c`, then verifies the checksums.
Native package publication and the tag CI matrix are pending.

## Known limitations

- The measured broadband splitter/isolation model remains unavailable until
  measured S3P/S4P data and an embedded-data ADR exist.
- The Flower Pot choke remains ideal; common-mode current, choke impedance,
  coax dielectric loss, and the conduit body are not modeled.
- No 50 Ω, gain, bandwidth, or validated choke claim is made for the Flower Pot.
- The FP1 5/8, double 5/8, dual-band sleeve, and high-gain variants remain out
  of scope until their own spikes and ADRs exist.
- DL8 terrain modeling remains blocked until a validated terrain model or a
  second engine exists.
- Native packages are unsigned; verify the published checksums.
- Windows Python 3.11 continues to run the non-UI suite only; the full UI suite
  runs on Windows 3.12/3.13 and Linux.
