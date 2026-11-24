# AntennaDesk 0.10.0 release QA

- **Version:** `0.10.0`
- **Date:** 2026-11-24
- **Tag:** `v0.10.0`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.10.0>
- **Release workflow:** <https://github.com/fsclavo/antenna-desk/actions/runs/45508172449>
- **Tag CI:** <https://github.com/fsclavo/antenna-desk/actions/runs/45508172452>
- **Status:** published with unsigned, checksum-verified artifacts
- **Schema:** 61 (from 52 in 0.9.0)
- **Previous release:** `0.9.0` (2026-11-17)

## Scope

This release consolidates the 1.1 Station work with the 1.2 exploration slices
and the adaptive display-units track:

- Adaptive length display units U1–U6: automatic/fixed metric and imperial
  presentation across scenes, family editors, optimization/synthesis dialogs,
  construction sheets, and reports; CSV and DXF keep canonical units.
- Live tuning (DL3): a coarse preview of managed length, angle, count, and ratio
  dimensions, an optional coarse pattern preview, and **Apply and simulate**
  closing the dialog and starting the full run.
- Uniform radial droop (VR1): one physical-length radial angle with tip
  validation, schema 61, scene/report/live-tuning support, and optimizer
  coverage.
- Bounded cliff/second-medium site ground (DL7): far-field-only `GN`/`RP 2`/
  `RP 3` support with an explicit SWR-unchanged limitation.
- PF1 ZIP project container: deterministic container version 1 with per-entry
  validation, lazy run loading, design-only recovery, and compacted saves.
- Station tools and workflow: Smith chart, tuner matchability, VNA import 2.0,
  decision metrics, convergence study, autosave/recovery, recent projects,
  portable NEC-2 deck export, and the narrowed Yagi mast/guy-wire slice.
- Correctness and optimizer work: frequency-aware bounds, high-frequency
  validity, Moxon gap contract, thin-wire quality gate, multiband HexBeam, and
  deterministic family-optimizer checks.

Release-preparation edits changed only versioning and documentation. The
feature changes and their source-backed or experimental boundaries are in the
changelog, ADRs, and evidence audit.

## Compatibility

- **Breaking project-format change:** 0.9.0 gzip/plain-JSON project files are
  not readable by 0.10.0. Projects must be saved as the current ZIP container.
  Schema 59 and 60 containers migrate on open; schema 58 and older are
  rejected. This is the intentional pre-1.0 PF1 decision in
  [`ADR-0050`](../../ADR/0050-zip-project-container.md).
- Schema 61 adds `radial_droop_deg` with a no-value-rewrite 60→61 migration;
  old vertical designs load at 0° with unchanged geometry.
- The UI keeps PySide6 below 6.12; do not widen the pin without the ADR-0025
  shutdown regression tests.

## Validation

- **Full gate:** **4,325 passed, 1 skipped** with `NEC2C`; the skip is the
  Windows-only console-hiding test on Linux.
- `ruff check`, `ruff format --check`, `mypy`, and
  `mypy --config-file mypy_ui.ini` pass.
- `uv lock --check` and the dependency audit pass.
- Manual U6 desktop QA completed on 2026-11-24: light/dark themes,
  small/normal/large fonts, sketch, forms, construction sheet, and the
  units/CSV/DXF exceptions were checked with no blocking findings.
- Real `nec2c` coverage includes the vertical, phased-vertical, Yagi, HexBeam,
  and drooped-radial cases.
- CI smoke tests passed for the wheel, AppImage, Debian package, Windows
  portable executable, and Windows installer.

## Candidate artifacts

Artifacts are built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.10.0`. Native builds ran the bundle
license audit. The local sdist was built before the final documentation edits;
CI rebuilds every artifact from the tag. Windows artifacts are built by CI.

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.10.0-py3-none-any.whl` | 1.2 M | `260af79b6986a8f85e8e808ff9d25f6405370ad237cb5ac94cf6b07035c25241` |
| `antennadesk-0.10.0.tar.gz` | 1.8 M | `fdb9a9cd4dcb1e0f78f494d61cd454a97197b24d0df2be59b4a0232da47c4e3b` |
| `AntennaDesk-0.10.0-x86_64.AppImage` | 121 M | `ad4f52891bf0ac70032ab0edee630edc22be91789f509ffe35c4bdf43d190307` |
| `antennadesk_0.10.0_amd64.deb` | 103 M | `d9a31566e1470c3efefe315003d6c9c3faadb3d4797d9407f29d5b4386db65c7` |
| `AntennaDesk-0.10.0-windows-x86_64.zip` | pending CI | pending CI |
| `AntennaDesk-0.10.0-windows-x86_64-setup.exe` | pending CI | pending CI |

## Smoke tests

| Check | Result |
|---|---|
| Wheel installs in a clean Python 3.12 venv | pass |
| `import antennadesk; print(__version__)` | `0.10.0` |
| `python -m antennadesk.ui.app --version` | `0.10.0` |
| `--check-solver` with `NEC2C` set | found the provided solver |
| AppImage `--version` | `0.10.0` |
| AppImage `--check-solver` | found bundled `nec2c` |
| AppImage `sha256sum -c` | OK |
| AppImage offscreen launch, 10 s timeout | exited 124, no crash |
| Debian `--version` after extraction | `0.10.0` |
| Debian `--check-solver` | found bundled `nec2c` |
| Debian `sha256sum -c` | OK |
| Debian offscreen launch, 10 s timeout | exited 124, no crash |
| Windows portable `--version` / `--check-solver` | pass |
| Windows installer install, launch, and uninstall | pass |

## Published assets

All six artifacts have a companion `.sha256` file. Every published checksum was
verified after downloading the release assets with `sha256sum -c`.

| Asset | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.10.0-py3-none-any.whl` | 1.2 M | `260af79b6986a8f85e8e808ff9d25f6405370ad237cb5ac94cf6b07035c25241` |
| `antennadesk-0.10.0.tar.gz` | 1.8 M | `cd648621c91fce7a45a62cb292ac0f8de4f300b1e70c1bfe78ff653b2f5c04b7` |
| `AntennaDesk-0.10.0-x86_64.AppImage` | 129 M | `5f4ee211b12aed5a67d9185d52cd9902165442388e3858804fca6d1e4fb4c0ba` |
| `antennadesk_0.10.0_amd64.deb` | 110 M | `7f75273795a225f70e21e1e7ec7fdf39e14cde21c2e23cd3681b5fce9753d2a6` |
| `AntennaDesk-0.10.0-windows-x86_64.zip` | 103 M | `3f0d63872661f7da45e26a7e5229ddca097e1cdf315f20e848ca5c7e39e5660c` |
| `AntennaDesk-0.10.0-windows-x86_64-setup.exe` | 71 M | `d7ecd440027254d81ad147cd4c758b023f99375490c5463e3d49e470028ba537` |

The published wheel checksum matches the local candidate. The sdist and native
artifacts were rebuilt independently by CI.

## CI note

The tag CI workflow's Windows jobs did not go green: Python 3.13 and the 3.11
non-UI job failed during collection because the U6 QA pass added a Unix-only
`os.geteuid()` guard to a directory-permission test, and Python 3.12 was
canceled after a long UI stall. The Release workflow independently built,
smoke-tested, and published the Windows artifacts successfully. The guard was
fixed on main after publication and a CI rerun is pending; the 0.10.0
artifacts themselves are unaffected.

## Known limitations

- Native packages are unsigned; verify the SHA-256 checksums. GPG and Windows
  Authenticode signing remain deferred.
- No live VNA/hardware control.
- Experimental and heuristic templates keep their documented evidence levels;
  this release adds no new numerical reference.
- The phased vertical does not share the VR1 droop field.
- PF2 (streaming container write), PF3 (pattern-level lazy loading), and UX45
  (shared Qt worker lifecycle) remain optional maintenance items.
