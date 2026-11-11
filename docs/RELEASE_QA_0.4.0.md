# AntennaDesk 0.4.0 release-candidate QA

- **Candidate:** `0.4.0`
- **Date:** 2026-11-11
- **Source commit:** `d082631` (`docs(release): record 0.4.0 candidate QA`);
  local artifacts were built from the code-identical `32e7b3e` release-prep tree
- **Status:** release candidate prepared locally and Windows CI validated;
  **not tagged or published**

## Scope

This checkpoint covers the changes since `v0.3.1`:

- matching-network precedence, override visibility, persisted design target,
  and impedance-point network creation (M1–M5, ADR-0028);
- optional shortened-EFHW inverted-L bend (G26, schema 35);
- UI help, accessibility, task-progress, optimizer, and project-loading work
  accumulated since the previous release.

## Static checks

| Check | Result |
|---|---|
| `uv lock --check` | pass |
| `uv run ruff check .` | pass |
| `uv run ruff format --check .` | pass, 587 files |
| `uv run mypy` | pass, 165 source files |
| `uv run mypy --config-file mypy_ui.ini` | pass, 118 UI files |
| `uv run pytest` | **2,468 passed, 0 skipped** |
| Example project acceptance flow | 8 passed |

The full suite ran with the local `spikes/phase0/build/nec2c` solver; the pytest
header reported the solver path. No solver tests were skipped.

## Visual QA

Offscreen screenshots were generated from `examples/dipole_40m.antennadesk` in
English, metric units:

- light theme, medium font;
- light theme, large font;
- dark palette, medium font.

Two presentation defects were found and fixed before rebuilding the artifacts:

1. The **Feed & matching** group title displayed the `&` as a Qt mnemonic,
   producing `Feed_matching`. The title now escapes the ampersand.
2. Result-table headers were clipped at the large font size when no result was
   loaded. Table columns are now resized on retranslation and application-font
   changes.

Remaining manual QA: inspect on a real display with the platform light/dark
theme and the supported font-size settings. The offscreen captures do not
replace that check.

## Artifact smoke tests

### Wheel and sdist

Built with `uv build --out-dir dist`, installed into a fresh Python 3.12 venv.

| Check | Result |
|---|---|
| `import antennadesk; print(__version__)` | `0.4.0` |
| `python -m antennadesk.ui.app --version` | `0.4.0` |
| `--check-solver` with `NEC2C` set | found the provided solver |
| Wheel installation | pass |

### AppImage

Built clean-room with `BUILD_DIR` and `DIST_DIR` outside the repository. Bundle
license audit passed.

| Check | Result |
|---|---|
| `--version` | `0.4.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

Built clean-room from the same frozen bundle. Bundle license audit passed.

| Check | Result |
|---|---|
| `dpkg-deb --info` | `Version: 0.4.0`, `amd64` |
| `--version` after extraction | `0.4.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Windows

Built by GitHub Actions run
[`43042974734`](https://github.com/fsclavo/antenna-desk/actions/runs/43042974734)
on `windows-latest` from branch `release/0.4.0-qa`:

| Check | Result |
|---|---|
| `Build nec2c for Windows` | pass |
| `Build Windows bundle` | pass |
| `AntennaDesk.exe --version` | pass in the Windows smoke step |
| `AntennaDesk.exe --check-solver` | pass in the Windows smoke step |
| Artifact download and `sha256sum -c` | OK |
| Zip contents | `AntennaDesk.exe`, `nec2c.exe`, `COPYING`, and `licenses/` present |
| License audit inside the Windows build | pass |

The same workflow run's Linux package job failed before building because the
GitHub runner could not resolve `azure.archive.ubuntu.com` for `apt-get`
(`Temporary failure resolving`). A rerun failed with the same infrastructure
error. This is not a code failure: the Linux AppImage and `.deb` were built and
smoke-tested locally as recorded above.

## Local artifacts

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.4.0-py3-none-any.whl` | 745 K | `67ad32710e971e3d5c9d7d257ed84272c6818abfc6d3201e50679b276d1aaa3e` |
| `antennadesk-0.4.0.tar.gz` | 1.1 M | `7c2e7a719de878d14c04a06105689310f446d2cf142952fa2f4a7c4acfc9e4e0` |
| `AntennaDesk-0.4.0-x86_64.AppImage` | 120 M | `05925edce790894cf6d0059ccd2dfe64f0e5ce7ddeed30aefaff8e86dec9e4fc` |
| `antennadesk_0.4.0_amd64.deb` | 102 M | `947648eaeb078d24bcddd09050ec5978e4b7be176e5ea1458d00b2fa8c024d1f` |
| `AntennaDesk-0.4.0-windows-x86_64.zip` | 103 M | `2f3b3421ec2e1329ea6a56d9c82a8ed2d5a0e4a6cd1a426b95d1e913b65582a2` |

The AppImage, `.deb`, and Windows zip have companion `.sha256` files. The wheel
and sdist do not have companion checksum files yet; the release workflow
currently publishes the native checksums and the wheel/sdist artifacts.

## Signing

Signing remains deferred. No GPG key or Windows Authenticode certificate was
configured for this checkpoint. The local artifacts are unsigned and verified
only by SHA-256.

## Known limitations

- Some antenna templates remain experimental or published/heuristic rather
  than numerically validated; see `docs/VALIDATION_PLAN.md`.
- Matching networks remain ideal post-processing models. The EFHW internal
  matching unit and the project network are never cascaded; see ADR-0028.
- The shortened-EFHW inverted-L bend is a sharp 90° corner and has no
  independent numerical validation.
- No live VNA/hardware control and no additional full-wave engine.
- GPG and Windows Authenticode signing are not configured.

## Release decision

Windows build and smoke tests are complete. Do not tag or publish until:

1. the platform light/dark and font-scaling QA is completed on a real display;
2. the maintainer approves the tag `v0.4.0`;
3. the tag-triggered workflow completes its Linux package job (the candidate
   branch run was blocked by a GitHub runner DNS failure, while the local Linux
   artifacts passed the same build and smoke checks).
