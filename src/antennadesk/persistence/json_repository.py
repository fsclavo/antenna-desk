# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Compatibility import for the old JSON repository name.

The native project file is now a ZIP container. New code should import
``ProjectContainerRepository`` from ``container.py``.
"""

from __future__ import annotations

from .container import ProjectContainerRepository

JsonProjectRepository = ProjectContainerRepository

__all__ = ["JsonProjectRepository", "ProjectContainerRepository"]
