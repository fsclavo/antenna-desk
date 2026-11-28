# AntennaDesk 0.11.2 release QA

- **Version:** `0.11.2`
- **Date:** 2026-11-27 (published 2026-11-28 UTC)
- **Tag:** `v0.11.2`
- **Release:** <https://github.com/fsclavo/antenna-desk/releases/tag/v0.11.2>
- **Status:** published 2026-11-27
- **Schema:** 73 (unchanged from 0.11.1)
- **Previous release:** `0.11.1` (2026-11-27)

## Scope

This patch release packages:

- the UX58–UX61 generator-dialog layout track: deterministic offscreen test
  baseline, `WrapLongRows` across family forms, layout-based initial sizing,
  the Medium/Large EN/ES guard, and the resolved Windows offscreen font;
- PF2 streaming container writes: bounded temporary spool, byte-identical
  manifest-first output, and streamed copied runs;
- the DL3 follow-up exposing Flower Pot feed/choke heights and the trapped-Yagi
  trap inset in live tuning.

No solver, electromagnetic model, project schema, or project-format change is
included.

## Validation

- **Full gate:** **4,967 passed, 1 skipped** (Windows-only console check
  skipped on Linux).
- `uv run ruff check .` — pass.
- `uv run ruff format --check .` — pass.
- `uv run mypy` — pass.
- `uv run mypy --config-file mypy_ui.ini` — pass.
- `NEC2C=spikes/phase0/build/nec2c uv run pytest tests/integration/simulation`
  — **186 passed**.
- Windows CI run
  [`46081455154`](https://github.com/fsclavo/antenna-desk/actions/runs/46081455154)
  — all jobs green, including Windows 3.12/3.13.
- Windows layout batch: **330 passed** on both 3.12 and 3.13; baseline
  `Segoe UI 9.00pt / 96 DPI / DPR 1.00 / fusion`.
- README `tests` badge: passing.
- Manual Linux/Windows light-dark and 125%/150% checklist: passed; see
  [`QA_CHECKLIST_2026-11-27_ux61.md`](../qa/QA_CHECKLIST_2026-11-27_ux61.md).

## Packaging

- `uv build` produced `antennadesk-0.11.2-py3-none-any.whl` and
  `antennadesk-0.11.2.tar.gz`; wheel metadata reports `0.11.2`.
- The tag workflow built the AppImage, Debian package, Windows installer, and
  portable Windows zip.
- The AppImage and the extracted Debian launcher report `0.11.2`; the Debian
  control metadata reports `0.11.2`.
- The Windows portable zip contains `AntennaDesk.exe` and the bundled
  `nec2c.exe`.

## Publication verification (2026-11-27)

- Tag workflow
  [`46085721824`](https://github.com/fsclavo/antenna-desk/actions/runs/46085721824)
  completed successfully; all build and publish jobs passed.
- The GitHub release is public and contains **12 assets** (six packages and six
  checksum files).
- All six published checksums verify with `sha256sum -c`.
- The Windows installer, portable zip, AppImage, Debian package, wheel, and
  sdist carry the `0.11.2` version or filename.

## Known limitations

- The 0.11.1 and 0.11.0 feature limitations remain; see
  [`RELEASE_QA_0.11.1.md`](RELEASE_QA_0.11.1.md) and
  [`RELEASE_QA_0.11.0.md`](RELEASE_QA_0.11.0.md).
- Native packages are unsigned; verify the published checksums.
- The Windows installer was built and checksum-verified by the release
  workflow; it was not installed on a separate Windows desktop in this
  verification pass.
