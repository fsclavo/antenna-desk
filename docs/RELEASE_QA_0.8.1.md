# AntennaDesk 0.8.1 release QA

- **Version:** `0.8.1`
- **Date:** 2026-11-16
- **Tag:** `v0.8.1` at `3ef4d27`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.8.1>
- **Status:** published with unsigned, checksum-verified artifacts
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

## Published assets

Every asset has a companion `.sha256` file. All six published checksums were
verified with `sha256sum -c` after downloading the release assets.

| Asset | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.8.1-py3-none-any.whl` | 1008 K | `a3d5ccadf8a581ad9a0cd29896063da6ef5972e0dbc60da0d91186f639a3a05e` |
| `antennadesk-0.8.1.tar.gz` | 1.5 M | `a0ae3ff0a82a28063c27c3e1a1376e39115a56731f495ec5688d374ff027be02` |
| `AntennaDesk-0.8.1-x86_64.AppImage` | 129 M | `3683b6cdbedae57f0df71a610336226c76393c66718ca37340efc268e1cc1093` |
| `antennadesk_0.8.1_amd64.deb` | 110 M | `60c689acfeba0f7e5bf21893d09b271f986cc70c3f740a643bf196adee7e1123` |
| `AntennaDesk-0.8.1-windows-x86_64.zip` | 103 M | `f544a94f0175868c78742f7f207879c140d49a4f4f2b58270bdfd15c47b21881` |
| `AntennaDesk-0.8.1-windows-x86_64-setup.exe` | 71 M | `aebefdf28916851b2e50026e952305386193b30e340e78985ae6899505ce7da2` |

The published wheel checksum matches the local candidate; the sdist and native
artifacts were rebuilt independently by CI.

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

The Windows portable zip and NSIS installer were built in GitHub Actions on
`windows-latest`. The workflow ran the frozen executable version/solver checks,
installed the NSIS package silently, checked the desktop shortcut and installed
executable, and completed the silent uninstall. See CI run
[`43946980265`](https://github.com/fsclavo/antenna-desk/actions/runs/43946980265).

## Known limitations

- This is a patch release; the 0.8.0 feature set and limitations are unchanged.
- Native Windows QA and a second Linux display-scaling setting remain manual
  work, as recorded in [`QA_PASS_2026-11-16.md`](QA_PASS_2026-11-16.md).
- G27 remaining ferrite/core-loss and shack-end `Zcm(f)` data, the B4
  coupled-fan measurement, live VNA control, additional engines, and signing
  remain blocked or deferred.

## Release decision

Published as `v0.8.1` on 2026-11-16. The tag-triggered CI run
[`43946980265`](https://github.com/fsclavo/antenna-desk/actions/runs/43946980265)
completed the wheel/sdist, Linux, Windows, and publish jobs successfully. All
six published assets and their companion `.sha256` files were downloaded and
verified after publication.
