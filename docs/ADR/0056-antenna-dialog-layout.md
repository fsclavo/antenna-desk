# ADR-0056 — Antenna generator dialog layout and height budget

- **Status:** accepted 2026-11-26; implemented by UX50 and UX51
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

Out of scope: migrating the remaining families (UX52–UX55), changing
`scaled_dialog_size()` semantics, changing the sidebar, and any solver,
domain-model, schema, simulation, report, or numerical-reference change.
