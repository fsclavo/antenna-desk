<!--
SPDX-FileCopyrightText: 2026 Fernando Sclavo
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Third-party notices

AntennaDesk is free software under the GNU General Public License, version 3
or later. The complete text is in `COPYING` next to this file.

The corresponding source for the AntennaDesk release that contains this
notice is available from the same release page:

<https://github.com/fsclavo/antenna-desk/releases>

## AntennaDesk

- License: GPL-3.0-or-later
- Source: <https://github.com/fsclavo/antenna-desk>

## nec2c

- Component: `nec2c` 1.3.3, KJ7LNW fork at commit
  `55be1e0e3fe5ee9dad4ce6050711450d19c562fd`
- License: GPL-3.0
- Upstream: public domain.
- Source: <https://github.com/KJ7LNW/nec2c>
- The source tarball and the Windows portability patch are bundled under
  `licenses/nec2c/`. If the tarball is not present, `licenses/nec2c/SOURCE.txt`
  records the exact source URL and commit.

## Qt, PySide6 and shiboken6

- License: LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only.
- AntennaDesk uses PySide6 under GPL-3.0. The LGPL-3.0 text is included as
  `licenses/LGPL-3.0.txt`.
- Qt source: <https://code.qt.io/cgit/qt/qtbase.git/>
- PySide6 source: <https://code.qt.io/cgit/pyside/pyside-setup.git/>

## Python

- License: PSF-2.0
- <https://docs.python.org/3/license.html>

## NumPy

- License: BSD-3-Clause (with the additional notices in its license file)
- The installed license text is copied under `licenses/numpy-*`.

## pydantic and pydantic-core

- License: MIT
- The installed license texts are copied under `licenses/pydantic-*` and
  `licenses/pydantic_core-*`.

## pyqtgraph

- License: MIT
- The installed license text is copied under `licenses/pyqtgraph-*`.

## ezdxf

- License: MIT
- The installed license text is copied under `licenses/ezdxf-*`.

## Other Python packages

The frozen bundle also contains transitive Python packages. Their installed
license files are copied next to this notice when available:

| Package | License |
|---|---|
| annotated-types | MIT |
| packaging | Apache-2.0 OR BSD-2-Clause |
| platformdirs | MIT |
| pyparsing | MIT |
| typing-extensions | PSF-2.0 |
| typing-inspection | MIT |

## PyInstaller

- License: GPL-2.0-or-later with the bootloader exception.
- <https://pyinstaller.org/en/stable/license.html>
- Only the PyInstaller bootloader is embedded in the frozen executable.
