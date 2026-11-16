# AntennaDesk 0.8.1 release QA

- **Version:** `0.8.1`
- **Date:** 2026-11-16
- **Status:** release candidate prepared; **not tagged or published**
- **Schema:** 52 (unchanged from 0.8.0)
- **Previous release:** `0.8.0` (2026-11-16)

## Scope

This is a stabilization patch after 0.8.0. It contains two user-visible fixes:

- **Log-periodic feed classification.** The LPDA design panel now reports a
  balanced center-fed connection with the transposed phase-line note,
  recommends a 1:1 current balun/choke for a direct coax feed, and shows the
  ideal feed transformer when a ratio other than 1:1 is configured. Previously
  the new family appeared as unclassified and unbalanced.
- **Scaled dialog size cap.** Dialog initial sizes are capped to 90 % of the
  available screen, so a large font scale cannot place the title bar or buttons
  off-screen. The content remains scrollable and the dialog stays resizable.
  Discovered during the post-0.8.0 visual QA at 1.5× and 2.0× font scales.

No antenna model, schema, solver, optimizer, persistence, matching, or
numerical result changes are included.

## Validation

- **LPDA feed classification:** tests cover the direct-coax, recorded
  current-balun, and configured transformer-ratio cases.
- **Dialog scaling:** a font-scaling regression test checks that the initial
  dialog size stays inside the available screen geometry.
- **Full gate:** **3,221 passed, 1 skipped** with `NEC2C` and the optional
  `cross-engine` group. The skip is the Windows-only console-hiding test on
  Linux.
- `ruff check`, `ruff format --check`, `mypy`, and
  `mypy --config-file mypy_ui.ini` pass.
- `uv lock --check` and `uv pip check` pass.

## Compatibility

- Schema 52 is unchanged.
- No project file migration is required.
- Existing LPDA projects keep their geometry and results; only the design-panel
  connection summary changes.
- Dialog sizing is a UI-only change; the form layout and scroll behavior are
  unchanged.
- See [`QA_PASS_2026-11-16.md`](QA_PASS_2026-11-16.md) for the original finding
  and the P7/D4 benchmark decision.

## Local candidate artifacts

Artifacts were built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.8.1`. Native builds ran the bundle
license audit and passed the local smoke tests below. The published CI
artifacts are rebuilt independently from the tag.

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.8.1-py3-none-any.whl` | 1008 K | `a3d5ccadf8a581ad9a0cd29896063da6ef5972e0dbc60da0d91186f639a3a05e` |
| `antennadesk-0.8.1.tar.gz` | 1.5 M | `80d04488ba9b505c742de6e425918de84d41c85411dae2022df1c93923ac4bee` |
| `AntennaDesk-0.8.1-x86_64.AppImage` | 121 M | `603249168e9764d65cdda43d2a571f525142c716e7c370988593722b10a8c933` |
| `antennadesk_0.8.1_amd64.deb` | 103 M | `c96e184939977cdcfdae59b3dd6ea98babcae7cce62e088d70ac5d27805f578a` |

Both native artifacts have companion `.sha256` files, verified with
`sha256sum -c`. The wheel and sdist checksums were computed directly from the
built artifacts.

## Smoke tests

### Wheel

| Check | Result |
|---|---|
| Clean Python 3.12 venv install | pass |
| `import antennadesk; print(__version__)` | `0.8.1` |
| `python -m antennadesk.ui.app --version` | `0.8.1` |
| `--check-solver` with `NEC2C` set | found the provided solver |

### AppImage

| Check | Result |
|---|---|
| `--version` | `0.8.1` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

| Check | Result |
|---|---|
| `dpkg-deb --extract` | pass |
| `--version` after extraction | `0.8.1` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

## Windows

The Windows portable zip and NSIS installer are not built locally. The
tag-triggered CI workflow builds them on `windows-latest` and runs the frozen
version/solver, installer, shortcut, and uninstall checks before publishing.

## Known limitations

- This is a patch release; the 0.8.0 feature set and limitations are unchanged.
- Native Windows QA and a second Linux display-scaling setting remain manual
  work, as recorded in [`QA_PASS_2026-11-16.md`](QA_PASS_2026-11-16.md).
- G27 remaining ferrite/core-loss and shack-end `Zcm(f)` data, the B4
  coupled-fan measurement, live VNA control, additional engines, and signing
  remain blocked or deferred.

## Release decision

Pending. Tag `v0.8.1` after publishing this candidate is approved, then verify
that the release workflow attached all six assets and their `.sha256` files.
