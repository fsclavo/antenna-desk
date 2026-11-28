# UX61 layout closure checklist — 2026-11-27

- **Status:** complete 2026-11-27; automated closure and manual desktop
  confirmation reported OK by the project owner.
- **Scope:** UX58–UX61 generator-dialog layout track
- **Automated baseline:** UX58 (96 DPI, 1× scale, 9–10 pt test font)
- **Windows CI:** [run 46081455154](https://github.com/fsclavo/antenna-desk/actions/runs/46081455154), green on 3.12 and 3.13

## Automated result

- Local layout batch: **356 passed** in 30 s.
- Windows 3.12/3.13 layout batch: **330 passed** on both jobs, well under the
  180 s timeout.
- Windows baseline: `Segoe UI 9.00pt / 96 DPI / DPR 1.00 / fusion`.
- Full gate: **4,967 passed, 1 skipped**; the skip is the Windows-only
  console-hiding test.
- README `tests` badge: passing on `main`.
- Guard matrix: 26 dialogs × English/Spanish × Medium/Large × (920×640 and the
  documented initial size). No horizontal scrollbar, action box visible and
  outside the scroll.
- Yagi: default height without vertical scroll at Medium; Large Spanish has no
  horizontal scrollbar; the table grows with extra height.
- Flower Pot: Medium/Large English/Spanish at the 600 px initial width; actions
  visible and no horizontal scrollbar.

## Pending manual checks

Run once on a Linux desktop and once on a Windows desktop, with the current
build:

- [x] English and Spanish.
- [x] Light and dark themes.
- [x] Medium and Large font presets.
- [x] Windows display scaling at 125% and 150%; Linux equivalent if used.
- [x] All 26 family generator dialogs: OK/Cancel visible, no clipped primary
      field, no horizontal scrollbar.
- [x] Yagi at the 920 px target: no vertical scroll at Medium; vertical allowed
      at Large; element table grows when the dialog is taller.
- [x] Basic Antenna at 560 px and Large: template/family row stays compact and
      its full text is available in the tooltip.
- [x] Compact families (fan dipole, Ringo, inverted V/L) keep actions visible
      without a form scroll.

## Manual confirmation (2026-11-27)

The project owner reported the checklist passed on the Linux and Windows
desktops for the build at UX61 closure, covering English/Spanish, light/dark,
Medium/Large, and 125%/150%. Exact OS build and Qt/PySide6 version strings were
not supplied separately; the green CI baseline for this build is
`Segoe UI 9.00pt / 96 DPI / DPR 1.00 / fusion`.

## Closure

All three conditions are met:

1. Windows 3.12 and 3.13 pass the real layout batch without `skip`/`xfail` or a
   platform exclusion.
2. The manual checklist above is recorded for both desktops.
3. The README `tests` badge is green on `main`.
