# Project instructions

AntennaDesk is a local-first antenna design and simulation application for
amateur radio. The project is GPL-3.0-or-later.

## Read first

- `docs/antennadesk-development-blueprint.md`
- `docs/PROJECT_DECISIONS.md`
- Relevant files in `docs/ADR/`

## Architecture

- Preserve the boundaries between domain, application, solver adapters,
  persistence, and UI.
- Domain code must not import PySide6, SciPy, or concrete solver libraries.
- Never put electromagnetic calculations in widgets or view models.
- The application depends on ports, not concrete adapters.
- The solver adapter translates the canonical model to the engine format and
  normalizes the output.
- A simulation is an immutable snapshot, never a live reference to a mutable
  model.

## UI

- Use PySide6 for the desktop UI and PyQtGraph for charts.
- Route user-visible strings through `ui/i18n.py`; keep English and Spanish in
  sync. UI strings are English by default, with Spanish translations.
- Keep metric/imperial conversion at the presentation boundary. Domain and
  project files use canonical meters.
- Run simulations in a worker thread; never block the Qt event loop.
- UI tests use `pytest-qt` with the offscreen platform.
- PySide6 is pinned below 6.10 because 6.12 triggered a shutdown refcount crash
  with pyqtgraph. Re-evaluate the pin deliberately.

## Correctness and science

- Do not invent numerical reference values.
- Reference values must come from a traceable independent source.
- New domain rules require unit tests.
- Solver behavior changes require integration and regression tests.
- Keep units and result conventions explicit.
- Distinguish gain, realized gain, and directivity.
- Do not silently discard unsupported imported elements.
- Approximations and limitations must be visible to the user.

## Implementation discipline

- Implement one coherent milestone at a time; do not scaffold the whole
  roadmap.
- Do not add a dependency without justifying its cost, license, and benefit.
- Do not use `pickle` for project files.
- Project files are versioned JSON with explicit migrations and atomic saves.
- Keep the UI responsive during long operations.
- Do not run shell commands built by concatenating untrusted input.
- Treat imported files as untrusted data.
- Documentation and README are in English. Code identifiers are in English.
  The UI supports Spanish and English.
- Add short SPDX headers to source files.

## Tooling

Use `uv` for the environment and dependency management.

Before declaring a task complete, run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```

Add tests for every new domain rule and every persistence or adapter behavior.

## Workflow

1. Read the blueprint and existing code.
2. Identify affected domains and dependencies.
3. Propose a short plan and the files to modify.
4. Implement the minimum scope.
5. Add tests.
6. Run the checks above.
7. Review architectural boundaries.
8. Update documentation and `CHANGELOG.md` when behavior or schema changes.
9. Report changes, decisions, tests, and remaining limitations.

Do not commit or push unless the user explicitly asks.
