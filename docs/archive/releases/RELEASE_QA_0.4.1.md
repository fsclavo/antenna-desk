# AntennaDesk 0.4.1 release QA

- **Version:** `0.4.1`
- **Date:** 2026-11-11
- **Tag:** `v0.4.1` at `ca76b1a`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.4.1>
- **Status:** published with unsigned, checksum-verified artifacts

## Scope

This patch release adds the Windows NSIS installer while keeping the portable
Windows zip, and updates the author credit. It does not change the antenna
model, project schema (`35`), or simulation behavior.

## Static checks

| Check | Result |
|---|---|
| `uv lock --check` | pass |
| `uv run ruff check .` | pass |
| `uv run ruff format --check .` | pass, 590 files |
| `uv run mypy` | pass, 165 source files |
| `uv run mypy --config-file mypy_ui.ini` | pass, 118 UI files |
| `uv run pytest` | **2,473 passed, 0 skipped** |
| Example project acceptance flow | 8 passed |

## Local artifact smoke tests

- Wheel installed into a clean Python 3.12 venv: `--version` and
  `--check-solver` passed.
- AppImage: `--version`, `--check-solver`, checksum, and offscreen GUI launch
  passed.
- Debian package: extraction, `--version`, `--check-solver`, checksum, and
  offscreen GUI launch passed.
- Linux bundle license audits passed.

## Windows CI

Candidate run
[`43072323189`](https://github.com/fsclavo/antenna-desk/actions/runs/43072323189)
on branch `release/0.4.1-qa` completed all jobs successfully:

- PyInstaller bundle and `nec2c.exe` built;
- NSIS installed and the `setup.exe` generated;
- installer silently installed;
- Start Menu / Desktop shortcut and uninstaller asserted;
- installed `AntennaDesk.exe --version` and `--check-solver` passed;
- installer silently uninstalled and the installed executable was removed.

The tag-triggered release run
[`43073474869`](https://github.com/fsclavo/antenna-desk/actions/runs/43073474869)
initially failed while Chocolatey fetched NSIS (`504 Gateway Timeout`). The
rerun completed all jobs and published the release. The Linux package job also
passed on this tag, so the 0.4.0 runner DNS issue did not recur.

## Published assets

| Asset | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.4.1-py3-none-any.whl` | 745 K | `da1ffea664ed6db3fb8d40bcc90a7ff3d3b1f83617d6d73078f427a110f3242c` |
| `antennadesk-0.4.1.tar.gz` | 1.1 M | `8e5c17e612f684cfd74467156e25114631b043dbc0b39f5b9eba6d7338cdc9fa` |
| `AntennaDesk-0.4.1-x86_64.AppImage` | 134 M | `f83427fcb2e94e739a94251a37b839fb83d1e8b313f973703bf6d1dc6f4d0a70` |
| `antennadesk_0.4.1_amd64.deb` | 114 M | `bc8d3bb7b6dfa1e4fd57c3f1e8525f5911693f77a6cb6884f4ce4f859ed196e2` |
| `AntennaDesk-0.4.1-windows-x86_64-setup.exe` | 70 M | `3977520e020931c916f7e84874acb2bfa80562cfddfade2c9296b66f76715e22` |
| `AntennaDesk-0.4.1-windows-x86_64.zip` | 103 M | `478c8709279d5014d9454a5d0376bb88ad1e44cfbf45b00b13c74d7a21c74709` |

Every asset has a companion `.sha256` file. The release workflow now generates
wheel and sdist checksums automatically; for 0.4.1 they were generated from the
published wheel/sdist and uploaded after the release job.

## Known limitations

- The native packages are unsigned; verify the SHA-256 checksums. GPG and
  Windows Authenticode signing remain optional and deferred.
- The Windows installer is per-machine and requires elevation.
- The installer installs the application but does not migrate or remove user
  projects and preferences.
- Antenna-model and evidence limitations are unchanged from 0.4.0; see
  `docs/VALIDATION_PLAN.md` and `docs/RELEASE_QA_0.4.0.md`.
