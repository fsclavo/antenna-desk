# AntennaDesk 0.8.0 release QA

- **Version:** `0.8.0`
- **Date:** 2026-11-16
- **Tag:** `v0.8.0` at `c400c4f`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.8.0>
- **Status:** published with unsigned, checksum-verified artifacts
- **Schema:** 52 (from 51)
- **Previous release:** `0.7.1` (2026-11-16)

## Scope

- **Log-periodic dipole array (LPDA).** A straight-element family with a
  transposed phase line built from the existing `TransmissionLine` primitive.
  The generic `phase_reversal` flag is persisted and maps to a negative NEC TL
  characteristic impedance. The Cebik 10 m 1.0 in, 75 Ω reference reproduces
  the published NEC-4 gain and front-to-back ratio at 29 MHz, with
  segmentation-stable element currents.
- **Automatic Pi/T matching synthesis.** The project matching dialog and the
  design-specific end-fed action synthesize L, Pi, or T networks from the
  current load. Pi/T use a visible total design Q; a Q below the physical
  minimum returns no solution. The synthesis is lossless and the component-Q
  loss model remains separate.
- Documentation, EN/ES help, scene contract, reports, construction notes,
  schema migration, and tests.

## Validation

- **C3 evidence:** level **B**. The Cebik 10 m reference is a published NEC-4
  model, not a measurement. The 0.5 in and #12 rows in the same table use
  different optimization geometry, so the 1.0 in row is the exact match.
- **C3 reference results at 29 MHz:**

  | Metric | Published | NEC2C |
  |---|---:|---:|
  | Gain, 75 Ω | 7.36 dBi | 7.37 dBi |
  | Front-to-back, 75 Ω | 22.01 dB | 22.01 dB |
  | Gain, 200 Ω | 7.04 dBi | 7.05 dBi |
  | Front-to-back, 200 Ω | 24.56 dB | 24.56 dB |
  | Input impedance, 75 Ω | — | 52.38 − j1.39 Ω |
  | Element phases | 10.6/−79.1/−168.1/109.6° | 12.1/−77.6/−166.5/111.2° |

  Segmentation 43/41/39/37, 21/21/21/21, 31/29/27/25, and 51/49/47/45 changes R
  by less than 0.15 %, X by 0.28 Ω, gain by 0.01 dB, and F/B by 0.12 dB.
- **Pi/T synthesis:** exact input-impedance match for real and complex loads
  across 2, 3, 8, and 10 design Q values; minimum-Q rejection and component
  variation are covered by unit tests.
- **Full gate:** **3,219 passed, 1 skipped** with `NEC2C` and the optional
  `cross-engine` group. The skip is the Windows-only console-hiding test on
  Linux.
- `ruff check`, `ruff format --check`, `mypy`, and `mypy --config-file
  mypy_ui.ini` pass.

## Compatibility

- Schema 52 is additive. Version 51 projects migrate transmission lines with
  `phase_reversal: false`, preserving their previous behavior.
- Existing L-network synthesis and all other antenna families are numerically
  unchanged.
- The new LPDA family is a normal `AntennaModel`; no solver or persistence
  subsystem was added.
- Pi/T synthesis is lossless. Component loss remains the separate
  `q_factor` model.

## Published assets

Every asset has a companion `.sha256` file. All six published checksums were
verified with `sha256sum -c` after downloading the release assets. The local
candidate builds were verified before tagging; CI rebuilt the artifacts
independently.

| Asset | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.8.0-py3-none-any.whl` | 1006 K | `82d2888c930620c0bfb3eeff54e5527b8f3af233eb4c34a29e5837bd03a47928` |
| `antennadesk-0.8.0.tar.gz` | 1.4 M | `ec3d54717f999740eff6d7a9df61387f4131f97b6b1087a5304622156dd2f99b` |
| `AntennaDesk-0.8.0-x86_64.AppImage` | 129 M | `afe5578f9a5dcca76bcef146b47155c218ce22aa4910b8edff9f4cba06af2a91` |
| `antennadesk_0.8.0_amd64.deb` | 109 M | `8fdd9bf3e1daf0c2af8335918ff17f9a49362aa1da4c12720d1db98ff002253a` |
| `AntennaDesk-0.8.0-windows-x86_64.zip` | 103 M | `be1b7151c819b9afc64eb3fb068b98d362f076d050f2b00eada8a1792ab90caa` |
| `AntennaDesk-0.8.0-windows-x86_64-setup.exe` | 71 M | `aae32bce458c187df7f1507c8438b8b09a11c426b9510f6cf1b3738e9debb375` |

## Smoke tests

- **Wheel:** clean virtual environment, import version, `--version`, and
  `--check-solver` with the packaged `nec2c` or a configured path.
- **AppImage:** `--version`, `--check-solver`, checksum verification, and a
  headless offscreen launch that exits only by timeout.
- **Debian:** package metadata, extraction, bundled `--version`,
  `--check-solver`, and checksum verification.
- **Windows:** the tag-triggered CI workflow builds the portable zip and NSIS
  installer, runs the frozen executable checks, installs silently, verifies the
  shortcut and installed app, and uninstalls silently.

### Local result

- Wheel installed in a clean Python 3.11 virtual environment:
  `antennadesk.__version__` and `python -m antennadesk.ui.app --version` printed
  **0.8.0**; `--check-solver` found the reference `nec2c`.
- AppImage: `--version` printed **0.8.0**, `--check-solver` found the bundled
  `nec2c`, and the offscreen launch exited only through the 10 s timeout
  (exit code 124, not a crash).
- Debian: package metadata reports **0.8.0**; the extracted bundle printed
  **0.8.0** and found its bundled `nec2c`.
- `sha256sum -c` passed for the wheel, sdist, AppImage, and Debian package.

## Windows

The Windows portable zip and NSIS installer were built in GitHub Actions on
`windows-latest`. The workflow ran the frozen executable version/solver checks,
installed the NSIS package silently, checked the desktop shortcut and installed
executable, and completed the silent uninstall. See CI run
[`43931919975`](https://github.com/fsclavo/antenna-desk/actions/runs/43931919975).

## Known limitations

- LPDA evidence is **B**: the reference is a published NEC-4 model, not a
  measured prototype. The model is lossless and omits the balun, feed-line
  loss, rear stub, boom, mast, and construction tolerances.
- The ARRL/Cebik 7 MHz swept-element wire design is not reproduced by the
  straight-element family; it remains a future V-array variant.
- There is no full LPDA τ/σ optimizer; the registry returns an explicit
  unavailable reason.
- Pi/T synthesis has no separate matching-network optimizer objective. The
  design Q is a total loaded Q and selects one of many possible networks.
- G27 remaining ferrite/choke data, B4 fan-dipole coupling, live VNA control,
  additional engines, and signing remain blocked or deferred as documented in
  the backlog.

## Release decision

Published as `v0.8.0` on 2026-11-16. The tag-triggered CI run
[`43931919975`](https://github.com/fsclavo/antenna-desk/actions/runs/43931919975)
completed the wheel/sdist, Linux, Windows, and publish jobs successfully. All
six published assets and their companion `.sha256` files were downloaded and
verified after publication.
