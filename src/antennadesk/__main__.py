# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Run AntennaDesk with ``python -m antennadesk``."""

from __future__ import annotations

from .ui.app import main

if __name__ == "__main__":
    raise SystemExit(main())
