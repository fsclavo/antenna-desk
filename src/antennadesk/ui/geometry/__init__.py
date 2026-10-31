# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Presentation-neutral geometry scene used by the construction sketch."""

from .builder import SUPPORTED_PRESENTATION_TYPES
from .scene import (
    AngularDimension,
    Dimension,
    GeometryScene,
    SceneInset,
    SceneMarker,
    ScenePoint,
    ScenePolyline,
)
from .views import GeometryViewMode, recommended_view

__all__ = [
    "SUPPORTED_PRESENTATION_TYPES",
    "AngularDimension",
    "Dimension",
    "GeometryScene",
    "GeometryViewMode",
    "SceneInset",
    "SceneMarker",
    "ScenePoint",
    "ScenePolyline",
    "recommended_view",
]
