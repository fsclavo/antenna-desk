# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Pristine-state and feedback for frequency-first starting dimensions."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from ..i18n import Translator


class StartingDimensionsState:
    """Track whether a form still holds generated starting geometry.

    The state is intentionally conservative: a managed-field edit locks the
    geometry until the user reloads the starting dimensions. Installation and
    matching fields that the starting helper preserves do not lock it.
    """

    def __init__(self, translator: Translator, label: QLabel) -> None:
        self._translator = translator
        self._label = label
        self._pristine = False
        self._message: str | None = None
        self._frequency_mhz: float | None = None

    @property
    def pristine(self) -> bool:
        return self._pristine

    def mark_pristine(self, *, frequency_mhz: float | None = None) -> None:
        """Mark the managed geometry as generated and optionally show feedback."""

        self._pristine = True
        if frequency_mhz is None:
            self.clear()
            return
        self._message = "updated"
        self._frequency_mhz = frequency_mhz
        self._render()

    def mark_non_pristine(self) -> None:
        """Lock automatic regeneration and clear transient feedback."""

        self._pristine = False
        self.clear()

    def show_stale(self, frequency_mhz: float) -> None:
        """Explain that the frequency changed but the geometry was preserved."""

        self._pristine = False
        self._message = "stale"
        self._frequency_mhz = frequency_mhz
        self._render()

    def clear(self) -> None:
        self._message = None
        self._frequency_mhz = None
        self._label.clear()
        self._label.setVisible(False)

    def retranslate(self) -> None:
        if self._message is not None:
            self._render()

    def _render(self) -> None:
        if self._message is None or self._frequency_mhz is None:
            self.clear()
            return
        key = f"starting_dimensions.{self._message}"
        self._label.setText(
            self._translator.t(
                key,
                frequency=f"{self._frequency_mhz:.6f}",
            )
        )
        self._label.setVisible(True)
