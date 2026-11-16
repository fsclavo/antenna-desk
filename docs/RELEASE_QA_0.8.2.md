# AntennaDesk 0.8.2 release QA

- **Version:** `0.8.2`
- **Date:** 2026-11-16
- **Status:** release candidate prepared; **not tagged or published**
- **Schema:** 52 (unchanged from 0.8.0)
- **Previous release:** `0.8.1` (2026-11-16)

## Scope

This is a stabilization patch for the element tables in the Yagi and
log-periodic editors:

- each table now keeps a minimum column width based on its widest header
  label, so a capped dialog or a large font scale cannot clip labels such as
  “Posición en el boom”;
- the tables scroll horizontally when the columns do not fit;
- the shared helper is applied after construction and after retranslation, so
  English and Spanish labels both size correctly.

No antenna model, schema, solver, optimizer, persistence, matching, or
numerical result changes are included.

## Why this patch exists

The 0.8.1 release capped scaled dialog sizes to 90 % of the available screen.
On a small CI screen, the Yagi table became narrower than its header labels and
`test_element_tables_fit_their_headers_at_large` failed on Linux. The same test
was already failing on Windows because the Yagi table used stretch-only columns.
This patch fixes both cases instead of weakening the test.

## Validation

- **Header sizing:** a narrow-dialog regression test resizes the Spanish Yagi
  editor to 520 px and checks every header section against its label width.
- **Existing font-scaling test:** the full English/Spanish header check now
  passes at the capped dialog size.
- **Full gate:** **3,222 passed, 1 skipped** with `NEC2C` and the optional
  `cross-engine` group. The skip is the Windows-only console-hiding test on
  Linux.
- `ruff check`, `ruff format --check`, `mypy`, and
  `mypy --config-file mypy_ui.ini` pass.
- `uv lock --check` and `uv pip check` pass.

## Compatibility

- Schema 52 is unchanged; no project migration is required.
- Table content, values, and row behavior are unchanged.
- Wide dialogs keep the previous full-width stretch layout; only the minimum
  width changes when labels would otherwise be clipped.
- See [`RELEASE_QA_0.8.1.md`](RELEASE_QA_0.8.1.md) for the dialog-size cap and
  LPDA feed-classification fixes.

## Local candidate artifacts

Artifacts were built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.8.2`. Native builds ran the bundle
license audit and passed the local smoke tests below. The published CI
artifacts are rebuilt independently from the tag.

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.8.2-py3-none-any.whl` | 1008 K | `ebd0e7ff5f651f4633b1c425982373dad4020578540b81f7df85e1ea4d2dd6b5` |
| `antennadesk-0.8.2.tar.gz` | 1.5 M | `8a9acdb188b6d85b1760bcaf73e8abb90c45355eb3ebec1138deeb477850f3ff` |
| `AntennaDesk-0.8.2-x86_64.AppImage` | 121 M | `3bfd0ccf51e1955e4d5be75fec315d0f04ef827b1229c67dceae59b779942db6` |
| `antennadesk_0.8.2_amd64.deb` | 103 M | `47326a7fc25e1d1d842491c5c8581c27bd2898ced138a5d2343bdfc5149b563e` |

Both native artifacts have companion `.sha256` files, verified with
`sha256sum -c`. The wheel and sdist checksums were computed directly from the
built artifacts.

## Smoke tests

### Wheel

| Check | Result |
|---|---|
| Clean Python 3.12 venv install | pass |
| `import antennadesk; print(__version__)` | `0.8.2` |
| `python -m antennadesk.ui.app --version` | `0.8.2` |
| `--check-solver` with `NEC2C` set | found the provided solver |

### AppImage

| Check | Result |
|---|---|
| `--version` | `0.8.2` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

| Check | Result |
|---|---|
| `dpkg-deb --extract` | pass |
| `--version` after extraction | `0.8.2` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

## Windows

The Windows portable zip and NSIS installer are not built locally. The
tag-triggered CI workflow builds them on `windows-latest` and runs the frozen
version/solver, installer, shortcut, and uninstall checks before publishing.

## Known limitations

- This is a patch release; the 0.8.1 feature set and limitations are unchanged.
- Native Windows QA and a second Linux display-scaling setting remain manual
  work, as recorded in [`QA_PASS_2026-11-16.md`](QA_PASS_2026-11-16.md).
- G27 remaining ferrite/core-loss and shack-end `Zcm(f)` data, the B4
  coupled-fan measurement, live VNA control, additional engines, and signing
  remain blocked or deferred.

## Release decision

Pending. Tag `v0.8.2` after this candidate is approved, then verify that the
release workflow attached all six assets and their `.sha256` files.
