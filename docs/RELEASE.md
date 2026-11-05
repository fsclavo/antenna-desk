# Release checklist

AntennaDesk is distributed as a Python wheel/sdist, a Linux AppImage, a Debian
package, and a Windows onedir zip. `nec2c` is bundled in the native packages and
remains an external runtime dependency for the wheel. The initial release is
unsigned; signing is optional and deferred until project keys are configured.

## Versioning

The package version is single-sourced from `src/antennadesk/__init__.py`
through Hatchling. Update `__version__` before tagging. The release workflow is
triggered by a `v*` tag and publishes the artifacts to the GitHub release.

## Build the Python package

```bash
uv sync --locked --python 3.12
uv build --out-dir dist
```

Artifacts:

- `dist/antennadesk-<version>.tar.gz`
- `dist/antennadesk-<version>-py3-none-any.whl`

## Build the Linux AppImage

Requirements:

- `uv`
- `appimagetool` on `PATH`, or `APPIMAGETOOL=/path/to/appimagetool`
- a built `nec2c` at `spikes/phase0/build/nec2c`, or `NEC2C=/path/to/nec2c`
- PyInstaller, installed by `uv run --group packaging`
- optionally `APPIMAGE_RUNTIME_FILE=/path/to/runtime-x86_64` to pin the AppImage
  runtime instead of letting `appimagetool` download the current one

```bash
bash spikes/phase0/scripts/build_nec2c.sh
packaging/build_appimage.sh
```

The result is `dist/AntennaDesk-<version>-x86_64.AppImage` plus a `.sha256`
file. PyInstaller is a packaging-only dependency; its license (GPL-2.0-or-later
with the bootloader exception) is compatible with this project.

## Build the Debian package

Requirements:

- `uv`
- `dpkg-deb`
- a built `nec2c` at `spikes/phase0/build/nec2c`, or `NEC2C=/path/to/nec2c`
- PyInstaller, installed by `uv run --group packaging`

```bash
bash spikes/phase0/scripts/build_nec2c.sh
packaging/build_deb.sh
```

The result is `dist/antennadesk_<version>_<arch>.deb` plus a `.sha256` file.
Development versions are normalized with `~` (for example
`0.2.0.dev0` becomes `0.2.0~dev0`) so they sort before the final release. The
package installs the frozen bundle under `/opt/antennadesk`, with
`/usr/bin/antennadesk` as the launcher, the desktop entry, icons, copyright,
and a generated Debian changelog.

## License notices

Every native artifact includes:

- `COPYING`, the GPL-3.0 text;
- `licenses/THIRD_PARTY_NOTICES.md`;
- `licenses/LGPL-3.0.txt`;
- the installed license files for the bundled Python dependencies;
- `licenses/nec2c/` with the pinned source tarball and Windows patch, or a
  `SOURCE.txt` with the exact URL and commit.

`packaging/collect_bundle_licenses.py` collects them and
`packaging/check_bundle_licenses.py` fails the build if a required notice is
missing. The Debian package also installs the notices under
`/usr/share/doc/antennadesk`.

## Build the Windows bundle

Requirements:

- `uv`
- MSYS2/UCRT64 for `nec2c.exe`
- PyInstaller, installed by `uv run --group packaging`

```powershell
bash spikes/phase0/scripts/build_nec2c_windows.sh
packaging\build_windows.ps1
```

The result is `dist/AntennaDesk-<version>-windows-x86_64.zip` plus a `.sha256`
file. The zip contains `AntennaDesk.exe`, its `_internal` directory, and
`nec2c.exe` next to the executable.

## Smoke tests

Wheel:

```bash
python -m venv /tmp/antennadesk-release
/tmp/antennadesk-release/bin/pip install dist/*.whl
/tmp/antennadesk-release/bin/python -c "import antennadesk; print(antennadesk.__version__)"
/tmp/antennadesk-release/bin/python -m antennadesk.ui.app --version
```

AppImage:

```bash
APPIMAGE_EXTRACT_AND_RUN=1 dist/AntennaDesk-*.AppImage --version
APPIMAGE_EXTRACT_AND_RUN=1 dist/AntennaDesk-*.AppImage --check-solver
(cd dist && sha256sum -c *.AppImage.sha256)
```

For a headless launch check, run the GUI offscreen for a few seconds and
expect `timeout` to terminate it (exit code 124, not a crash):

```bash
QT_QPA_PLATFORM=offscreen APPIMAGE_EXTRACT_AND_RUN=1 \
  timeout 10s dist/AntennaDesk-*.AppImage
```

Debian package:

```bash
dpkg-deb --info dist/antennadesk_*.deb
dpkg-deb --contents dist/antennadesk_*.deb | less
rm -rf /tmp/antennadesk-deb
dpkg-deb --extract dist/antennadesk_*.deb /tmp/antennadesk-deb
/tmp/antennadesk-deb/opt/antennadesk/AntennaDesk --version
/tmp/antennadesk-deb/opt/antennadesk/AntennaDesk --check-solver
(cd dist && sha256sum -c *.deb.sha256)
```

Windows:

```powershell
build\pyinstaller-dist\AntennaDesk\AntennaDesk.exe --version
build\pyinstaller-dist\AntennaDesk\AntennaDesk.exe --check-solver
Get-FileHash dist\AntennaDesk-*-windows-x86_64.zip -Algorithm SHA256
```

## Clean local build artifacts

For clean-room validation, build outside the repository:

```bash
rm -rf /tmp/antennadesk-build /tmp/antennadesk-dist
BUILD_DIR=/tmp/antennadesk-build DIST_DIR=/tmp/antennadesk-dist \
  packaging/build_deb.sh
# ...run the smoke tests...
rm -rf /tmp/antennadesk-build /tmp/antennadesk-dist
```

To remove artifacts produced in the repository, including orphan `.deb`,
AppImage, Windows zip, wheel, sdist, and `build/` files, run:

```bash
packaging/clean_artifacts.sh
```

This leaves `spikes/phase0/build/nec2c` in place because the test suite and
local builds use it.

The GUI uses `nec2c` from `NEC2C`, `PATH`, or the directory next to the
application executable. The native bundles place `nec2c` next to the
executable; the wheel installer must provide it separately. Use
**Tools → Locate NEC2C...** if automatic discovery fails.

## Signing (optional, deferred)

Signing is optional, is not required for the initial release, and requires
project-owned keys. Unsigned releases still publish SHA-256 checksums for
integrity verification.

### GPG-signed release artifacts

The release workflow can import a GPG key and create detached ASCII-armored
signatures for the wheel, sdist, AppImage, `.deb`, and Windows zip:

- `GPG_PRIVATE_KEY`: ASCII-armored private key.
- `GPG_KEY_ID`: fingerprint or email of the signing key.
- `GPG_PASSPHRASE`: optional passphrase.

When `GPG_PRIVATE_KEY` is configured, the workflow runs
`packaging/sign_artifacts.sh` before publishing and uploads the `.asc` files.
To sign locally:

```bash
GPG_KEY_ID=<fingerprint> packaging/sign_artifacts.sh
gpg --verify dist/AntennaDesk-*.AppImage.asc dist/AntennaDesk-*.AppImage
```

### AppImage embedded signature

Set `APPIMAGE_SIGN_KEY=<gpg-key-id>` when running
`packaging/build_appimage.sh` to also sign the AppImage with `appimagetool`.
This is independent of the detached `.asc` signatures.

### Windows Authenticode

Set `WINDOWS_SIGN_CERT` to a `.pfx` path, `WINDOWS_SIGN_PASSWORD`, and
optionally `WINDOWS_TIMESTAMP_URL` before running
`packaging/build_windows.ps1`. The script signs both `AntennaDesk.exe` and
`nec2c.exe` with SHA-256 and a timestamp server.

In the release workflow, set `WINDOWS_SIGN_CERT_BASE64` to the base64-encoded
`.pfx`; the job decodes it to a temporary file, signs the binaries, and removes
the certificate file.

### Debian repository signing

Individual `.deb` signing is not automated. Sign the repository `Release`
metadata for APT, or use `debsigs` if detached package signatures are required.
The detached GPG signatures from `packaging/sign_artifacts.sh` provide
artifact-level verification.

The release workflow builds unsigned artifacts when the corresponding secrets
are absent.

## Supported targets

- Linux with Python 3.11–3.13; the AppImage and `.deb` bundle their own Python
  runtime.
- Debian/Ubuntu systems with `libc6 >= 2.35` for the `.deb`.
- Windows with Python 3.11–3.13; the zip bundles its own Python runtime.
- The UI uses PySide6 below 6.12; do not raise that pin without re-running the
  shutdown regression tests in ADR-0025.
- `ezdxf` is an optional export dependency but is installed with the package
  for DXF export.

## Release steps

1. Run `uv run ruff check .`.
2. Run `uv run ruff format --check .`.
3. Run `uv run mypy`.
4. Run `uv run mypy --config-file mypy_ui.ini`.
5. Run `NEC2C=... uv run pytest`.
6. Update `CHANGELOG.md` and `__version__`.
7. Build and test the wheel, AppImage, Debian package, and Windows zip.
8. Tag `v<version>` and push the tag.
9. Verify the release workflow attached all artifacts and checksums.
10. Record known limitations and experimental templates in the release notes.
11. For the initial release, signing may be skipped; keep the SHA-256 checksums
    and note that signatures are deferred.

## Current limitations

- The initial native packages are unsigned. Verify the published SHA-256
  checksums. GPG and Windows Authenticode signing remain available as an
  optional later step when project-owned keys are configured.
- No live VNA/hardware control.
- Some template families remain experimental or published/heuristic rather than
  strictly reference-backed. See `docs/VALIDATION_PLAN.md`.
