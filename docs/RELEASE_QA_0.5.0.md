# AntennaDesk 0.5.0 release-candidate QA

- **Candidate:** `0.5.0`
- **Date:** 2026-11-12
- **Tag:** none yet; candidate on `release/0.5.0-qa` after the release-prep
  merge and CI QA
- **Status:** local static checks, Linux/Python artifact smoke tests, and CI
  Windows bundle/installer QA passed; ready to tag

## Scope

This candidate covers the accumulated work since `v0.4.2` and moves the project
schema from 35 to 44. The release-facing changes are:

- folded-dipole **4:1**, full-wave loop **2:1**, and Yagi folded-driven **4:1**
  ideal feed-transformer defaults, with the Yagi ratio preserved through
  **Estimate**;
- the project-level current-balun/balanced-feed construction record (schema 44);
- side-by-side azimuth/elevation pattern cuts with independent selectors and a
  shared metric;
- metric-aware pattern titles, axis labels, polar scale footers, 3D label, cursor
  readout, and a power/directivity/realized-gain summary;
- the accumulated project, measurement, construction, workflow, and reporting
  work delivered between `v0.4.2` and this candidate, including the project
  journal, reference design library, guided experiments, workflow modes,
  installation profiles, antenna advisor, comparison 2.0, confidence card,
  parameter sweeps, tolerance analysis, measurement sessions, preflight checks,
  component calculators, as-built records, and feed-line loss budget.

No antenna geometry, solver convention, or gain definition changed for the
pattern work. The feed transformers are ideal link-budget models, not
common-mode or transformer-loss models.

## Static checks

| Check | Result |
|---|---|
| `uv lock --check` | pass |
| `uv run ruff check .` | pass |
| `uv run ruff format --check .` | pass, 702 files |
| `uv run mypy` | pass, 189 source files |
| `uv run mypy --config-file mypy_ui.ini` | pass, 142 UI files |
| `uv run pytest` | **2,866 passed, 1 skipped** |
| Example project acceptance flow | 8 passed |
| Help coverage manifest | pass in the pytest suite |

The full suite runs with the local `spikes/phase0/build/nec2c` solver. The one
skip is the Windows-only console-hiding check, which does not run on Linux.

## Visual QA

Offscreen screenshots were generated at 1280 × 860 in English with metric units
from a synthetic far-field **display fixture**, not from a validated reference
pattern:

- light theme, medium font;
- dark theme, medium font;
- light theme, large font;
- dark theme, large font;
- the **3D lobe** tab in light/medium.

The four-pane **Cuts** view, independent θ/φ selectors, metric summary, cursor
targets, polar scale footers, and the 3D metric label remained legible in both
themes and both font sizes. At 900 × 600 the Cuts tab measured 892 × 484, with
444 × 260 line charts and 444 × 220 polar views; no control or label overlapped.

One presentation defect was found and fixed before rebuilding the artifacts:

1. The polar footer showed the rounded scale ceiling as `Power gain: 5 dBi`
   while the peak marker showed `2.47 dBi`, which could be read as a peak value.
   The footer now says **`Power gain scale · 5 dBi`** in English and
   **`Escala de … · 5 dBi`** in Spanish.

The pattern PNG export saved the whole 2 × 2 Cuts view (1272 × 744 in the
offscreen capture), while the **3D lobe** tab saved the 3D view. Remaining
manual QA: inspect on a real display with the platform light/dark theme, display
scaling, and all supported font sizes. The offscreen captures do not replace
that check.

## Artifact smoke tests

Artifacts were built outside the repository with `BUILD_DIR` and `DIST_DIR` in
`/tmp/user/1000/opencode`. Both native builds ran the bundle license audit and
passed it.

### Wheel and sdist

| Check | Result |
|---|---|
| `import antennadesk; print(__version__)` in a clean Python 3.12 venv | `0.5.0` |
| `python -m antennadesk.ui.app --version` | `0.5.0` |
| `--check-solver` with `NEC2C` set | found the provided solver |
| Wheel installation | pass |

### AppImage

| Check | Result |
|---|---|
| `--version` | `0.5.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

| Check | Result |
|---|---|
| `dpkg-deb --info` | `Version: 0.5.0`, `amd64` |
| Package contents | launcher symlink, `AntennaDesk`, `nec2c`, desktop entry, copyright |
| `--version` after extraction | `0.5.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Windows

Not built locally because `makensis` is unavailable on this machine. GitHub
Actions run
[`43310098954`](https://github.com/fsclavo/antenna-desk/actions/runs/43310098954)
on `release/0.5.0-qa` completed all build jobs successfully:

| Check | Result |
|---|---|
| Wheel and sdist job | pass |
| Windows bundle, `nec2c.exe`, and NSIS installer | pass |
| Frozen `AntennaDesk.exe --version` / `--check-solver` | pass |
| Installer install, desktop shortcut, and uninstaller | pass |
| Installed `AntennaDesk.exe --version` / `--check-solver` | pass |
| Silent uninstall | pass |
| Linux AppImage and `.deb` jobs | pass |
| Publish GitHub release | skipped, because the run was not a tag |

## Local artifacts

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.5.0-py3-none-any.whl` | 924 K | `c8b03bda867d903d08e154a5c7a8eb210216fb4e516b1a1ce058c11c8cdfe0d0` |
| `antennadesk-0.5.0.tar.gz` | 1.3 M | `e31fdd3a4aac9ea358f03617debfb94c1b2ebead28fd87310b1fe6fb3868c737` |
| `AntennaDesk-0.5.0-x86_64.AppImage` | 120 M | `f42a7feb87c210b58ac004020f45ae8f6cc19e522a497225eccca64485ebca48` |
| `antennadesk_0.5.0_amd64.deb` | 102 M | `188997bbda1f8e513a7334c4b1917d405bfc87630363e6a97eea3c0aab8fe146` |

These are local candidate artifacts. They are unsigned and are not the published
release assets.

## Signing

Signing remains deferred. No GPG key or Windows Authenticode certificate was
configured for this candidate. Verify the SHA-256 checksums.

## Known limitations

- The Windows bundle and installer were built and smoke-tested in CI rather
  than locally because `makensis` is unavailable on this machine.
- Visual QA is offscreen only; real-display themes, platform scaling, and
  font-size settings still need a manual pass.
- The native packages are unsigned.
- Feed transformers and matching networks are ideal post-processing models. The
  current-balun checkbox is a construction record and does not model common-mode
  current, SWR, or gain.
- The folded-dipole 4:1 and loop 2:1 defaults still leave a residual mismatch;
  a matching network may be needed for an exact 50 Ω match.
- Antenna-model and evidence limitations are unchanged; see
  `docs/VALIDATION_PLAN.md` and `docs/RELEASE_QA_0.4.0.md`.

## Release decision

The 0.5.0 candidate is ready to tag and publish. The code and documentation
passed the static gate, the local Linux/Python smoke tests, and the CI Windows
bundle and installer QA. Tag `v0.5.0` on this candidate and push the tag; the
tag-triggered workflow will rebuild, sign if configured, and publish the
checksum-verified artifacts.
