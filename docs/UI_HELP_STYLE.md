# UI help style guide

Help text explains what a control means when the short label is not enough. It
is not a second user guide.

- Write one or two plain-text sentences, normally 80–180 characters.
- Prioritize model semantics, units, assumptions, and values the user cannot
  infer from the label. Say when a value is a starting point rather than a
  verified measurement.
- Do not use formulas, tables, marketing claims, performance promises, or
  numerical references that are not already documented elsewhere.
- Do not repeat the label. Prefer “Height above the selected ground model; it is
  installation context.” over “This field sets the height.”
- Put shared field help under `help.<key>`, for example
  `help.field.frequency`.
- Put a family-specific override under `help.<family>.<key>`, for example
  `help.wire_dipole.field.height`.
- Keep the existing `<key>_hint` text as the final fallback. Do not rename an
  existing hint just to add a tooltip.
- Keep English and Spanish in sync. A missing translation omits the tooltip;
  never show the raw help key.
- Apply help to both the label and its paired control when the form provides a
  control. Label help must remain available when the control is disabled.
