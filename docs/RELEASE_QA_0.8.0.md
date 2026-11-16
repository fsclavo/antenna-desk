# AntennaDesk 0.8.0 release QA

- **Version:** `0.8.0`
- **Date:** 2026-11-16
- **Status:** release candidate prepared; **not tagged or published**
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

## Local candidate artifacts

Artifacts are built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.8.0`. Native builds run the bundle
license audit.

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.8.0-py3-none-any.whl` | 1007 K | `82d2888c930620c0bfb3eeff54e5527b8f3af233eb4c34a29e5837bd03a47928` |
| `antennadesk-0.8.0.tar.gz` | 1.5 M | `1d99b478d73cfe214e3d2342faa0e4cd75308c99f7e48c44a88cb94396e29451` |
| `AntennaDesk-0.8.0-x86_64.AppImage` | 121 M | `b3d1a26983ee3889d60645d1bc1f115cca5a91406380aa9eed6441ba1d4e2e7c` |
| `antennadesk_0.8.0_amd64.deb` | 103 M | `dc6bc390b5f0d34f261376170f25aae4c1a81bb81e7d51efd9d14839da4d9399` |

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

The `0.8.0` candidate is ready for a tag-triggered CI build and publication
review. It is **not** tagged, pushed, or published by this QA pass.
