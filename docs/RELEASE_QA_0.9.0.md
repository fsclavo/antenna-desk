# AntennaDesk 0.9.0 release QA

- **Version:** `0.9.0`
- **Date:** 2026-11-17
- **Tag:** `v0.9.0` at `075ff9b`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.9.0>
- **Status:** published with unsigned, checksum-verified artifacts
- **Schema:** 52 (unchanged from 0.8.2)
- **Previous release:** `0.8.2` (2026-11-16)

## Scope

This release adds two user-facing features and two correctness fixes:

- **Touchstone `.s1p` round-trip.** VNA import accepts one-port Touchstone RI,
  MA, or DB files with Hz–GHz units, comments, UTF-8 BOM, and the file
  reference impedance. The Export menu writes the simulated sweep as a
  one-port RI file. The export uses the impedance shown in the results table,
  including the configured feed chain, and keeps the simulation reference
  impedance. CSV and Touchstone dispatch by suffix/content.
- **Coaxial feed schematic (UX31).** Direct coax is drawn as a cable with a
  center conductor, outer shield, cutaway, and cross-section, with no middle
  device box. Current balun, transformer, balanced line, multi-port, and
  unknown wiring have distinct drawings. Terminal labels follow
  ground/counterpoise/return. A recommended but unrecorded choke is dashed.
- **Per-template conductor material defaults (UX30).** New designs preselect
  aluminum for Yagi, beam, vertical, and wire-beam templates, stainless 304 for
  the loaded vertical, and copper for dipoles, loops, end-fed wires, and traps.
  Existing designs and source-backed references keep their stored material.
- **Chart cursor teardown.** The reusable chart cursor ignores pending hover and
  leave events after its plot or series starts tearing down.

No schema, solver, persistence, or migration change is included.

## Validation

- **Full gate:** **3,327 passed, 1 skipped** with `NEC2C` and the optional
  `cross-engine` group. The skip is the Windows-only console-hiding test on
  Linux.
- `ruff check`, `ruff format --check`, `mypy`, and
  `mypy --config-file mypy_ui.ini` pass.
- **Touchstone:** parser tests cover RI/MA/DB, Hz–GHz, custom reference
  impedance, comments, BOM, missing angle, `|S11| ≥ 1`, and invalid input.
  Exporter tests cover round-trip, determinism, comments, and invalid input.
  UI tests cover CSV and `.s1p` import, measurement reference impedance, and a
  parseable export.
- **UX31:** semantic SVG tests cover direct coax, no device box, coax and
  cross-section groups, current balun, transformer ratio and ideal label,
  balanced line without coax, multi-port, unknown, ground/counterpoise/return
  labels, dashed choke, determinism, and Spanish labels. The construction sheet
  integration test checks the embedded coaxial figure.
- **UX30:** resolver coverage against all 41 catalog keys; domain defaults for
  aluminum and copper families; dialog defaults for every affected family;
  loaded-vertical 304; Scv half square/bobtail; source-backed reference
  materials; existing-design preservation; Change Template same-key
  preservation; Design from Frequency preservation; project round-trip.
- **Local visual review:** offscreen captures of direct coax, current balun,
  transformer, balanced line, multi-port, unknown, and the feed-connection
  dialog. Manual dark/150 %/PDF/ZIP review remains recommended.

## Compatibility

- Schema 52 is unchanged; no migration is required.
- Existing projects keep their stored wire materials.
- New designs can produce slightly different conductor loss because the
  initial material differs. This is the intended defaults change, not a solver
  change.
- Source-backed reference designs keep explicit copper materials.
- The Windows Python 3.11 UI suite remains excluded per ADR-0025; the dedicated
  non-UI job and the Windows 3.12/3.13 full UI jobs remain.

## Local candidate artifacts

Artifacts are built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.9.0`. Native builds run the bundle
license audit.

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.9.0-py3-none-any.whl` | 1016 K | `5115d5926f685de0e5c97b3515c9317e982cc6708a744d4a928ff1226f54adc6` |
| `antennadesk-0.9.0.tar.gz` | 1.5 M | `afec0edee0bbfd60f1d3c3c9b54f86668dfb851b99dfa3b17ce45f7a968798f2` |
| `AntennaDesk-0.9.0-x86_64.AppImage` | 121 M | `210a0cc5d5524e1de3267f46bfcc29bb8ea44678522d50caca1f7c9a5eab5107` |
| `antennadesk_0.9.0_amd64.deb` | 103 M | `ae5792f148b96ab66aab2b2e199a59c1cefdc8270962f039dfa7e3ab22b36972` |

Both native artifacts have companion `.sha256` files, verified with
`sha256sum -c`. The wheel and sdist checksums were computed directly from the
built artifacts.

## Published assets

Every asset has a companion `.sha256` file. All six published checksums were
verified with `sha256sum -c` after downloading the release assets.

| Asset | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.9.0-py3-none-any.whl` | 1016 K | `5115d5926f685de0e5c97b3515c9317e982cc6708a744d4a928ff1226f54adc6` |
| `antennadesk-0.9.0.tar.gz` | 1.5 M | `5fffdec656f2a66aaa0c1ff4d7a7ffb902d8b1320c2e25f602c7ebbabd83b942` |
| `AntennaDesk-0.9.0-x86_64.AppImage` | 129 M | `be5397ca1ef2011d335bb85f43e600937f6c76b842e42ca3c35f0f6aa456cf45` |
| `antennadesk_0.9.0_amd64.deb` | 110 M | `0f013506c01c93c710fe547acca90b57a2aa04effc8666f48fa128bb95bccb3f` |
| `AntennaDesk-0.9.0-windows-x86_64.zip` | 103 M | `977eba31a2fd4db9e66a969be21625d0e6847d8e64f3dc4ab05843f528eca2e3` |
| `AntennaDesk-0.9.0-windows-x86_64-setup.exe` | 71 M | `ac1cb712e885b56cfc7609af580ac1c0de96bb88c6d3ac6eed30de7e75fc3e88` |

The published wheel checksum matches the local candidate; the sdist and native
artifacts were rebuilt independently by CI.

## Smoke tests

### Wheel

| Check | Result |
|---|---|
| Clean Python 3.12 venv install | pass |
| `import antennadesk; print(__version__)` | `0.9.0` |
| `python -m antennadesk.ui.app --version` | `0.9.0` |
| `--check-solver` with `NEC2C` set | found the provided solver |

### AppImage

| Check | Result |
|---|---|
| `--version` | `0.9.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

| Check | Result |
|---|---|
| `dpkg-deb --extract` | pass |
| `--version` after extraction | `0.9.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

## Windows

The Windows portable zip and NSIS installer are built in GitHub Actions on
`windows-latest`; the workflow runs the frozen version/solver, installer,
shortcut, and uninstall checks before publishing. See CI run
[`44103244393`](https://github.com/fsclavo/antenna-desk/actions/runs/44103244393).

## Known limitations

- Touchstone support is one-port `.s1p` only. Two-port and mixed-mode data are
  not supported.
- The export reflects the result-table impedance, including the configured feed
  chain. Disable the feed line/matching network to export the antenna-terminal
  impedance.
- The feed schematic is a construction aid, not a solver result. It does not
  model common-mode current, shield radiation, connector loss, or a real balun.
- Material defaults are conductor-loss presets, not structural or tubing
  models. Per-wire material mixing is not added.
- Native Windows and second-scaling visual QA remains manual.
- G27 remaining ferrite/core-loss and shack-end `Zcm(f)` data, the B4
  coupled-fan measurement, live VNA control, additional engines, and signing
  remain blocked or deferred.

## Release decision

Published as `v0.9.0` on 2026-11-17. The tag-triggered CI run
[`44103244393`](https://github.com/fsclavo/antenna-desk/actions/runs/44103244393)
completed the wheel/sdist, Linux, Windows, and publish jobs successfully. All
six published assets and their companion `.sha256` files were downloaded and
verified after publication.
