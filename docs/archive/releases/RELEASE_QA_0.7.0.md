# AntennaDesk 0.7.0 release QA

- **Version:** `0.7.0`
- **Date:** 2026-11-16
- **Tag:** `v0.7.0` at `c3dc3a6`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.7.0>
- **Status:** published with unsigned, checksum-verified artifacts
- **Schema:** 51
- **Previous release:** `0.6.0` (2026-11-13)

## Scope

This release covers the accumulated work after `0.6.0`:

- optional measured 49:1 transformer reactive preset (EF7a);
- measured 49:1 transformer loss table and separate `transformer_loss_db`
  (EF7b);
- selectable end-fed return path: automatic, installation proxy, counterpoise,
  or coax shield (EF8a);
- bounded feedpoint common-mode choke with measured series R/X (EF8);
- design-specific matching network with L, Pi, and T topologies (EF9);
- L-network synthesis from the current primary-side impedance (EF9 amendment);
- source-backed frequency-dependent coax attenuation for RG-58A/U and RG-213/U
  (G27 / ADR-0039);
- feed-chain loss audit and total-loss report row (ADR-0040).

Schema migrations cover v46→v47 (return path), v47→v48 (transformer loss),
v48→v49 (common-mode choke), v49→v50 (design matching network), and v50→v51
(feed-line attenuation table).

## Static checks

| Check | Result |
|---|---|
| `uv lock --check` | pass |
| `uv pip check` | all installed packages compatible |
| `uv run ruff check .` | pass |
| `uv run ruff format --check .` | pass, 747 files |
| `uv run mypy` | pass, 198 source files |
| `uv run mypy --config-file mypy_ui.ini` | pass, 147 UI files |
| `uv run pytest -q -W error` | **3,115 passed, 1 skipped** |
| Help coverage manifest | pass in the pytest suite |

The one skip is the Windows-only console-hiding check on Linux. The full suite
ran with the local `NEC2C` solver and no Python warning was promoted to an
error.

## Manual QA

The user performed a manual pass over the end-fed editor (L/Pi/T, return path,
feedpoint choke, transformer and loss selectors), the feed-line catalog and
attenuation hints, matching precedence, reports, and light/dark plus normal text
scaling. The pass was reported successful with no blocking issue. Details are in
[`QA_PASS_2026-11-15.md`](../qa/QA_PASS_2026-11-15.md).

A real-display Windows pass and a second Linux display-scaling pass remain
recommended as follow-up QA; they did not block publication.

## Local candidate artifacts

Artifacts were built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.7.0`. Native builds ran the bundle
license audit and passed the local smoke tests below. The published CI artifacts
were rebuilt independently; their hashes are in the next section.

## Published assets

Every asset has a companion `.sha256` file. All six published checksums were
verified with `sha256sum -c` after downloading the release assets.

| Asset | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.7.0-py3-none-any.whl` | 990 K | `49b142c216d3f99cea82f3aac8612082bd9a46053c8a828ba1619a7c10867fe9` |
| `antennadesk-0.7.0.tar.gz` | 1.4 M | `58d4eefbfcdd1d361b44dd69f3d752db3ee48ba0d8186cc9700cd6ef620abe85` |
| `AntennaDesk-0.7.0-x86_64.AppImage` | 129 M | `838467025eba76272beecd9a2c5627ed45c28b5fa69c14c402c6cf635d11ae22` |
| `antennadesk_0.7.0_amd64.deb` | 110 M | `a74f328ee0af9d57433d3f6e3f73e8195f9d7633fa359fcfd1437ada8a85b2e8` |
| `AntennaDesk-0.7.0-windows-x86_64.zip` | 103 M | `91381478382e077c919f5cee28a223f57409caec8963b514063490afceb9cf85` |
| `AntennaDesk-0.7.0-windows-x86_64-setup.exe` | 71 M | `99723a4b14ed17c06a9192d0161763a1510f4ed3bd95dd3e7159ea10e4541ac8` |

### Wheel and sdist

| Check | Result |
|---|---|
| Clean Python 3.11 venv install | pass |
| `import antennadesk; print(__version__)` | `0.7.0` |
| `python -m antennadesk.ui.app --version` | `0.7.0` |
| `--check-solver` with `NEC2C` set | found the provided solver |
| Wheel built from the sdist | pass |

### AppImage

| Check | Result |
|---|---|
| `--version` | `0.7.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

| Check | Result |
|---|---|
| `dpkg-deb --info` | `Version: 0.7.0`, `amd64` |
| Package contents | launcher, frozen app, `nec2c`, desktop entry, copyright |
| `--version` after extraction | `0.7.0` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

## Windows

The Windows portable zip and NSIS installer were built in GitHub Actions on
`windows-latest`. The workflow ran the frozen executable version/solver checks,
installed the NSIS package silently, checked the desktop shortcut and installed
executable, and completed the silent uninstall. See CI run
[`43787804618`](https://github.com/fsclavo/antenna-desk/actions/runs/43787804618).

## Signing

Signing remains deferred. No GPG key or Windows Authenticode certificate is
configured for this release. The published artifacts are unsigned and verified
by SHA-256.

## Known limitations

- G27 is split and partially complete: measured transformer loss, feedpoint
  choke, coax attenuation, and the loss audit are in; analytical ferrite core
  loss and interpolated shack-end `Zcm(f)` still require measurements.
- The feedpoint choke is a bounded model at the feedpoint; shack-end placement
  and shield transfer impedance are not modeled.
- Coax attenuation tables are nominal datasheet data. Values are interpolated
  inside the documented range; outside it the endpoint values are used and
  preflight warns.
- Pi/T matching networks are manual. Automatic synthesis is L-only.
- The design-specific matching network is ideal L/C; component Q, ESR, and
  balun imbalance remain separate or unmodeled.
- Absolute end-fed SWR remains informational for the shortened presets.
- Physical antenna validation and live VNA control remain blocked without
  measurements or hardware.

## Release decision

Published as `v0.7.0` on 2026-11-16. The tag-triggered CI run
[`43787804618`](https://github.com/fsclavo/antenna-desk/actions/runs/43787804618)
completed the wheel/sdist, Linux, Windows, and publish jobs successfully. All
six published assets and their companion `.sha256` files were downloaded and
verified after publication.
