# AntennaDesk 0.7.1 release QA

- **Version:** `0.7.1`
- **Date:** 2026-11-16
- **Status:** release candidate prepared; **not tagged or published**
- **Schema:** 51 (unchanged from 0.7.0)
- **Previous release:** `0.7.0` (2026-11-16)

## Scope

This is a UI-only patch release for the Yagi generator:

- the element table now stretches its columns to the full section width;
- the table keeps a minimum height of 140 px so four rows are visible instead
  of two clipped rows;
- no antenna model, schema, solver, optimizer, persistence, or numerical result
  changes.

The fix is covered by a UI regression test in `tests/ui/test_yagi_dialog.py`.

## Static checks

| Check | Result |
|---|---|
| `uv lock --check` | pass |
| `uv pip check` | all installed packages compatible |
| `uv run ruff check .` | pass |
| `uv run ruff format --check .` | pass, 749 files |
| `uv run mypy` | pass, 198 source files |
| `uv run mypy --config-file mypy_ui.ini` | pass, 147 UI files |
| `uv run pytest -q -W error` | **3,116 passed, 1 skipped** |

The one skip is the Windows-only console-hiding check on Linux.

## Local candidate artifacts

Artifacts were built outside the repository under
`/tmp/user/1000/opencode/antennadesk-0.7.1`. Native builds run the bundle
license audit.

| Artifact | Size | SHA-256 |
|---|---:|---|
| `antennadesk-0.7.1-py3-none-any.whl` | 990 K | `40c8017ac7e5759d0603cdd3fceef62ed69ed8af882751eb06f7229647dd8c74` |
| `antennadesk-0.7.1.tar.gz` | 1.4 M | `9c124a1a0d0404fca313355efe496d2f9049d395c8ad5194aded2252cde71455` |
| `AntennaDesk-0.7.1-x86_64.AppImage` | 121 M | `e2614f4295d96c986ef276ca825db329b093518c66220ffe6acc34923f534327` |
| `antennadesk_0.7.1_amd64.deb` | 103 M | `d17c23c8345d66f1f5d38821b333555446524154de52ce07101fc251c853be50` |

### Wheel and sdist

| Check | Result |
|---|---|
| Clean Python 3.11 venv install | pass |
| `import antennadesk; print(__version__)` | `0.7.1` |
| `python -m antennadesk.ui.app --version` | `0.7.1` |
| `--check-solver` with `NEC2C` set | found the provided solver |
| Wheel built from the sdist | pass |

### AppImage

| Check | Result |
|---|---|
| `--version` | `0.7.1` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

### Debian package

| Check | Result |
|---|---|
| `dpkg-deb --extract` | pass |
| `--version` after extraction | `0.7.1` |
| `--check-solver` | found bundled `nec2c` |
| `sha256sum -c` | OK |
| Offscreen GUI launch, 10 s timeout | exited 124, no crash |

## Windows

The Windows portable zip and NSIS installer must be built and smoke-tested by
the tag-triggered release workflow in CI, as in 0.7.0.

## Known limitations

- This patch changes only the Yagi table layout.
- The manual QA in `QA_PASS_2026-11-15.md` remains valid for the underlying
  features.
- G27, signing, physical validation, and the other limitations from 0.7.0 are
  unchanged.

## Release decision

The `0.7.1` candidate is ready for a tag-triggered CI build and publication
review. It is **not** tagged, pushed, or published by this QA pass.
