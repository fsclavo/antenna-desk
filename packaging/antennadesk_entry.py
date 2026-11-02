# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Frozen-application entry point used by PyInstaller."""

from antennadesk.ui.app import main

if __name__ == "__main__":
    raise SystemExit(main())
