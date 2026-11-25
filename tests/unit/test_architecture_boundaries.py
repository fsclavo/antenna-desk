# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Dependency-direction guards for the ports-and-adapters layers."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "antennadesk"

THIRD_PARTY = (
    "PySide6",
    "pyqtgraph",
    "pydantic",
    "ezdxf",
    "numpy",
    "scipy",
    "matplotlib",
)

FORBIDDEN = {
    "domain": (
        "antennadesk.application",
        "antennadesk.persistence",
        "antennadesk.simulation",
        "antennadesk.reporting",
        "antennadesk.ui",
        "antennadesk.presentation",
        *THIRD_PARTY,
    ),
    "application": (
        "antennadesk.persistence",
        "antennadesk.simulation",
        "antennadesk.reporting",
        "antennadesk.ui",
        "antennadesk.presentation",
        *THIRD_PARTY,
    ),
    "importers": (
        "antennadesk.persistence",
        "antennadesk.simulation",
        "antennadesk.reporting",
        "antennadesk.ui",
        "antennadesk.presentation",
        *THIRD_PARTY,
    ),
    "persistence": (
        "antennadesk.simulation",
        "antennadesk.reporting",
        "antennadesk.ui",
        "antennadesk.presentation",
        "PySide6",
        "pyqtgraph",
        "ezdxf",
        "numpy",
        "scipy",
        "matplotlib",
    ),
    "simulation": (
        "antennadesk.persistence",
        "antennadesk.reporting",
        "antennadesk.ui",
        "antennadesk.presentation",
        *THIRD_PARTY,
    ),
    "reporting": (
        "antennadesk.persistence",
        "antennadesk.ui",
        *THIRD_PARTY,
    ),
    "presentation": (
        "antennadesk.persistence",
        "antennadesk.simulation",
        "antennadesk.reporting",
        "antennadesk.ui",
        *THIRD_PARTY,
    ),
}


def _package_for(path: Path) -> str:
    parts = path.relative_to(SOURCE).with_suffix("").parts[:-1]
    return ".".join(("antennadesk", *parts))


def _absolute_from(node: ast.ImportFrom, package: str) -> str:
    if node.level == 0:
        return node.module or ""
    base = package.split(".")
    trim = node.level - 1
    if trim:
        base = base[: len(base) - trim]
    if node.module:
        base.extend(node.module.split("."))
    return ".".join(base)


def _matches(module: str, prefix: str) -> bool:
    return module == prefix or module.startswith(f"{prefix}.")


def _imported_modules(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    package = _package_for(path)
    modules: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = _absolute_from(node, package)
            modules.append((node.lineno, module))
            if module == "antennadesk":
                modules.extend((node.lineno, f"antennadesk.{alias.name}") for alias in node.names)
    return modules


def test_layer_imports_follow_the_declared_direction() -> None:
    violations: list[str] = []
    for layer, prefixes in FORBIDDEN.items():
        layer_root = SOURCE / layer
        for path in sorted(layer_root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            for line, module in _imported_modules(path):
                for prefix in prefixes:
                    if _matches(module, prefix):
                        violations.append(
                            f"{path.relative_to(ROOT)}:{line}: {layer} imports {module}"
                        )

    assert not violations, "\n".join(violations)


# The UI is a ratchet: app.py is the composition root and may build concrete
# adapters. The main-window entries are known debt; remove an entry when the
# corresponding use case or port replaces the direct adapter import.
ALLOWED_UI_ADAPTER_IMPORTS = {
    ("app.py", "antennadesk.persistence.container"),
    ("app.py", "antennadesk.simulation.nec2.export"),
    ("app.py", "antennadesk.simulation.nec2.solver"),
    ("app.py", "antennadesk.simulation.preflight"),
}


def test_ui_adapter_imports_are_allowlisted() -> None:
    found: set[tuple[str, str]] = set()
    for path in sorted((SOURCE / "ui").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        for _, module in _imported_modules(path):
            if _matches(module, "antennadesk.persistence") or _matches(
                module, "antennadesk.simulation"
            ):
                found.add((path.name, module))

    assert found == ALLOWED_UI_ADAPTER_IMPORTS, (
        f"new UI adapter imports: {sorted(found - ALLOWED_UI_ADAPTER_IMPORTS)}; "
        f"stale allowlist entries: {sorted(ALLOWED_UI_ADAPTER_IMPORTS - found)}"
    )


def test_qthread_lifecycle_is_owned_by_the_task_runner() -> None:
    """UI code must not copy the QThread create/cleanup sequence."""

    violations: list[str] = []
    controller = SOURCE / "ui" / "workers" / "task_runner.py"
    for path in sorted((SOURCE / "ui").rglob("*.py")):
        if path == controller or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for marker in ("QThread(", ".moveToThread("):
            if marker in text:
                violations.append(f"{path.relative_to(ROOT)}: {marker}")

    assert not violations, "\n".join(violations)
