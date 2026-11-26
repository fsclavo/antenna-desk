# ADR-0056 — Antenna generator dialog layout and height budget

- **Status:** accepted 2026-11-26; implemented and closed by UX50–UX55
- **Date:** 2026-11-26
- **Related:** UX50, UX51, `docs/AUTONOMOUS_BACKLOG.md` §UX50–§UX55

## Context

The Yagi generator exposed the action box below the desktop. Its single-column
form had a measured minimum height of 1087 px: a 920×720 resize was clamped to
the form minimum, the note block and OK/Cancel fell outside the screen, and the
element table was squeezed to its 140 px minimum. The Yagi editor was the
worst case, but the family dialogs were not a system:

- loaded dipole, biquad, Moxon, magnetic loop, Beverage, SCV, J-pole, OCFD,
  fan dipole, Ringo, and inverted V/L had no scroll area;
- twelve other generator dialogs already scrolled through forms between 493
  and 1697 px tall;
- dialog widths ranged from 560 to 940 px;
- notes and the action box moved between dialogs;
- the inline sidebar forms are intentionally narrow and must stay
  single-column.

UX50 fixed the Yagi dialog with a private two-column layout. UX51 turns that
validated shape into a small shared standard and adds a guard so the original
failure cannot return silently.

## Decision

Adopt two small, family-agnostic UI components and a height budget.

### `FormDialogFrame`

`antennadesk.ui.widgets.form_dialog.FormDialogFrame` is a `QDialog` that owns:

- the translated window title and `scaled_dialog_size()` call;
- the form area, optionally inside a `QScrollArea`;
- zero or more note widgets below the form area;
- a `QDialogButtonBox` that is always outside the scroll area;
- the default accept action, with `_accept()` available for validation.

It does not know about antenna families or fields. A subclass that must reject
invalid input overrides `_accept()` and calls `accept()` only after validation.
The frame is also usable with `scroll_form=False` for compact dialogs that fit
the budget.

### `SectionedForm`

`antennadesk.ui.widgets.sectioned_form.SectionedForm` lays out semantic
sections in one or two columns:

- `FormRow` carries a label key, a prebuilt `QLabel`, or no label (widget-only
  rows), plus the control;
- `FormSection` groups rows and may carry a title and an explicit column;
- the label factory lets `FormLabels.bind_form()` keep working for every
  column without duplicating labels or help registration;
- sections are atomic: a section never splits across columns;
- explicit `TWO_COLUMN` is used by the Yagi reference; `AUTO` chooses two
  columns only when the form has at least 12 rows and the target width is at
  least 920 px;
- `tab_order()` returns controls in reading order, left column first, and
  `apply_tab_order()` chains optional trailing widgets.

### Height and width budget

- **Height:** a generator dialog must have `minimumSizeHint().height() <= 640`
  px. A form whose minimum exceeds 640 px must be inside a form scroll area.
  The action box is always outside the scroll area and inside the dialog
  rectangle at 920×640.
- **Width:** the target width is 920 px. English and Spanish must not need a
  horizontal scrollbar at that width; a documented width up to 1000 px is
  allowed only when a family proves it necessary.
- **Compact families:** below 12 visible rows, stay single-column and omit the
  scroll area unless the height budget fails.
- **Sidebar exception:** inline sidebar forms remain single-column at their
  existing 340–520 px widths. The standard applies to generator dialogs, not
  to the main-window sidebar.
- **Responsive rule:** column choice is explicit or threshold-based; it is not
  inferred from family name, wire count, or translated text length.

### Accessibility and tab order

- Every label continues through `FormLabels` and `ui/help.py`, including
  tooltip, What's This, and accessible description.
- Section construction follows reading order. `apply_tab_order()` makes the
  focus chain match the visual left-then-right order and skips hidden controls
  at runtime.
- `WrapLongRows` prevents a long Spanish label from forcing horizontal
  scrolling; the scroll area is the small-screen fallback.
- Light/dark and font-scaling QA remains manual; offscreen tests are not a
  substitute.

### Guard

`tests/ui/test_dialog_layout.py` registers every family generator dialog in
the UX52–UX55 inventory. It checks the height budget, the form scroll when
needed, the action box position, and horizontal scrollbars in English and
Spanish. The registry has no exceptions at the time of this ADR. Two negative
tests prove the guard is not a no-op:

- a deliberately tall 1087 px fake form without a scroll area fails;
- the old single-column Yagi shape in a frame without a scroll area fails.

## UX54 audit: scroll-heavy generator dialogs

UX54 audited the twelve generator dialogs that already had a scroll area.
Every one now uses `FormDialogFrame`, keeps a single semantic column, and keeps
the notes and action box outside the scroll. No dialog required a two-column
split: the primary controls are in the first viewport at the default
1920×1080 size and at the 1366×768 cap; the embedded editor, table, or advanced
groups scroll.

| Dialog | Primary fields | Decision | Offscreen scroll range, 1920×1080 / 1366×768 |
| --- | --- | --- | --- |
| Stacked Yagi | Level count, spacing, max top height, feed mode | One column + scroll; stacked controls promoted above the embedded Yagi editor | 1009 / 1218 |
| End-fed | Design frequency, length, feed section, feed/end height, transformer | One column + scroll; matching, loading-coil, choke, and counterpoise groups stay checkbox-gated | 851 / 940 |
| Vertical | Frequency, height, base height, radial system | One column + scroll; loading coil and top hat stay checkbox-gated groups | 270 / 279 |
| Log-periodic | Low/high frequency, longest element, τ/σ, element count | One column + scroll; the element table and feed line scroll | 71 / 280 |
| HexBeam | Frequency, driver/reflector halves, turning radius, height, feed gap | One column + scroll; the bands group stays a `QGroupBox` | 164 / 293 |
| Trap Yagi | Frequency, element count, driven length, trap values | One column + scroll | 0 / 129 |
| Phased vertical | Frequency, element count, spacing, phase step | One column + scroll | 10 / 139 |
| Quad beam | Frequency, element count, loop side, reflector spacing, height | One column + scroll | 52 / 141 |
| Trap dipole | Low/high band, inner/outer lengths, trap values | One column + scroll | 0 / 29 |
| T2FD | Low/high frequency, length, spacing, termination, transformer | One column + scroll | 0 / 23 |
| Discone | Frequency, cone height/radius, disc radius/gap, wire count | One column + scroll | 0 / 0 |
| Basic antenna | Frequency, length/height, orientation, feed | One column + scroll | 0 / 21 |

The scroll ranges are offscreen reference measurements with the default font
and style. They are not acceptance thresholds. The acceptance is the 640 px
height budget, visible primary fields, visible actions outside the scroll, and
no horizontal scrollbar. The layout guard registers all twelve; there are no
exceptions.

Two columns were rejected for this inventory: each form is a single
geometry/feed reading flow, the advanced `QGroupBox` sections must remain
atomic, and the stacked Yagi embedded editor is a composed-family section that
must not be split. Promoting the stacked controls above that editor is the only
field-order change in UX54.

UX55 migrated fan dipole, Ringo, inverted V, and inverted L without a form
scroll; each keeps its compact single column. The final guard registry has 25
entries and no exceptions. The offscreen closure matrix covered 400
combinations (25 dialogs × light/dark × Medium/Large × English/Spanish ×
1366×768/1920×1080) with no action outside the dialog and no horizontal
scrollbar. The interactive desktop 125%/150% display-scaling check remains a
release-level manual step.

## Rejected alternatives

- **Two columns everywhere.** Compact forms become sparse, and the sidebar
  cannot afford the width. The standard keeps a single-column path.
- **Scroll-only as the sole fix.** Scrolling hides primary fields and leaves
  the action box fragile. The scaffold keeps actions outside the scroll and
  uses two columns only when the form is tall enough.
- **Tabs or collapsible groups by default.** They hide fields and break the
  single reading order; they remain a per-family decision in UX54.
- **Family-specific layout copies.** The original Yagi layout was correct but
  unreusable. The extracted helper keeps the validated behavior and gives the
  guard one contract to test.
- **A global fixed dialog size.** Window managers and font scaling differ.
  Sizing stays layout-based and capped by `scaled_dialog_size()`.

## Consequences

Positive:

- New generator dialogs have one reviewed scaffold and one guard.
- The action box cannot drift outside the scroll area without a failing test.
- The Yagi dialog keeps its UX50 behavior while losing its private layout.
- The sidebar remains untouched.

Costs:

- One more UI abstraction to maintain.
- The guard instantiates every registered dialog, so it is slower than a pure
  unit test.
- `AUTO` layout depends on an explicit target width; callers must pass it.

UX52 later applied the standard to loaded dipole, biquad, Moxon, and magnetic
loop, and UX53 applied it to Beverage, SCV, J-pole, and OCFD without changing
the guard contract, UX54 applied the scaffold audit to the twelve
scroll-heavy dialogs, and UX55 closed the compact-family and matrix work.
Out of scope: the release-level interactive desktop scaling check, changing
`scaled_dialog_size()` semantics, changing the sidebar, and any solver,
domain-model, schema, simulation, report, or numerical-reference change.
