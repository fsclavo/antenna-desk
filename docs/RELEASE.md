# Release checklist

AntennaDesk is distributed as a Python wheel/sdist. `nec2c` remains an
external runtime dependency; it is not bundled in the Python package.

## Versioning

The package version is single-sourced from `src/antennadesk/__init__.py`
through Hatchling. Update `__version__` before tagging.

## Build

```bash
uv sync --locked --python 3.12
uv build --out-dir dist
```

Artifacts:

- `dist/antennadesk-<version>.tar.gz`
- `dist/antennadesk-<version>-py3-none-any.whl`

The GUI icon is packaged in `antennadesk/ui/resources/antennadesk.svg`; the
Linux desktop entry is `packaging/antennadesk.desktop`.

## Smoke test

```bash
python -m venv /tmp/antennadesk-release
/tmp/antennadesk-release/bin/pip install dist/antennadesk-*.whl
/tmp/antennadesk-release/bin/python -c "import antennadesk; print(antennadesk.__version__)"
```

For the desktop application, also install a compatible `nec2c` build and
launch the GUI:

```bash
uv run python -m antennadesk
```

Use **Tools → Locate NEC2C...** if the solver is not on `PATH`.

## Supported targets

- Linux with Python 3.11–3.13.
- Windows with Python 3.11–3.13.
- The UI uses PySide6 below 6.10; do not raise that pin without re-running the
  shutdown regression tests.
- `ezdxf` is an optional export dependency but is installed with the package
  for DXF export.

## Release steps

1. Run `uv run ruff check .`.
2. Run `uv run ruff format --check .`.
3. Run `uv run mypy`.
4. Run `NEC2C=... uv run pytest`.
5. Update `CHANGELOG.md` and the version.
6. Build and run the wheel smoke test.
7. Tag the release and attach the wheel/sdist.
8. Record known limitations and experimental templates in the release notes.

## Current limitations

- No native installer or bundled `nec2c` yet.
- No live VNA/hardware control.
- Some template families remain experimental or published/heuristic rather than
  strictly reference-backed. See `docs/VALIDATION_PLAN.md`.
