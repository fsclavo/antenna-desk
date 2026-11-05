# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Collect license texts and third-party notices into a frozen bundle."""

from __future__ import annotations

import shutil
import sys
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = (
    "annotated-types",
    "ezdxf",
    "numpy",
    "packaging",
    "platformdirs",
    "pydantic",
    "pydantic-core",
    "pyparsing",
    "pyqtgraph",
    "typing-extensions",
    "typing-inspection",
)
NEC2C_CACHE = ROOT / "spikes" / "phase0" / ".cache"
NEC2C_PATCH = ROOT / "spikes" / "phase0" / "patches" / "nec2c-windows.patch"
NEC2C_COMMIT = "55be1e0e3fe5ee9dad4ce6050711450d19c562fd"


def _copy_package_licenses(target: Path) -> None:
    for package in PACKAGES:
        try:
            dist = distribution(package)
        except PackageNotFoundError:
            continue
        for file in dist.files or ():
            if "license" not in file.name.lower():
                continue
            source = dist.locate_file(file)
            if not source.is_file():
                continue
            destination = target / f"{package}-{file.name}"
            if not destination.exists():
                shutil.copy2(source, destination)


def _copy_nec2c_source(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    tarballs = sorted(NEC2C_CACHE.glob("nec2c-*.tar.gz"))
    if tarballs:
        shutil.copy2(tarballs[-1], target / tarballs[-1].name)
    else:
        (target / "SOURCE.txt").write_text(
            "nec2c 1.3.3, KJ7LNW fork\n"
            f"Commit: {NEC2C_COMMIT}\n"
            "Source: https://github.com/KJ7LNW/nec2c\n"
            "The release build downloads this tarball before packaging.\n",
            encoding="utf-8",
        )
    if NEC2C_PATCH.is_file():
        shutil.copy2(NEC2C_PATCH, target / NEC2C_PATCH.name)


def collect(bundle: Path) -> list[Path]:
    if not bundle.is_dir():
        raise FileNotFoundError(f"bundle not found: {bundle}")
    licenses = bundle / "licenses"
    licenses.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "LICENSE", bundle / "COPYING")
    for name in ("THIRD_PARTY_NOTICES.md", "LGPL-3.0.txt"):
        shutil.copy2(ROOT / "packaging" / "licenses" / name, licenses / name)
    _copy_package_licenses(licenses)
    _copy_nec2c_source(licenses / "nec2c")
    return sorted(path for path in bundle.rglob("*") if path.is_file())


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("usage: collect_bundle_licenses.py BUNDLE", file=sys.stderr)
        return 2
    try:
        files = collect(Path(arguments[0]))
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"collected {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
