# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify the local reference corpus against its committed manifest.

The corpus is copyrighted and gitignored. This script never downloads it; it
checks that the files the tests depend on are present and unchanged. Use
``--write`` after curating the list to regenerate the manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reference_data.manifest.json"
CORPUS = ROOT / "reference_data"
SOURCE = "MMANA-GAL sample models supplied by the project owner; not redistributed."

CURATED_FILES = (
    "mmana/HF simple/Dipole/3.5and3.8 dipole -1.maa",
    "mmana/HF simple/Dipole/FD20_1.maa",
    "mmana/HF simple/Dipole/InvV40.maa",
    "mmana/HF simple/Dipole/0.5 dipole+short radial.maa",
    "mmana/HF simple/Vertical/offcenter GP1.maa",
    "mmana/HF simple/Vertical/Vert20s_75+rad.maa",
    "mmana/HF simple/Loop/LOOP20r.maa",
    "mmana/HF beams/Db54m.maa",
    "mmana/HF beams/w2eey.maa",
    "mmana/VHF/J-ant144.maa",
    "mmana/VHF/144omni.maa",
    "mmana/Short/Magnetic loops/Multiturnloop.maa",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(corpus: Path) -> None:
    files = []
    for relative in CURATED_FILES:
        path = corpus / relative
        if not path.is_file():
            raise SystemExit(f"missing corpus file: {path}")
        files.append(
            {
                "path": relative,
                "size": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    document = {"source": SOURCE, "files": files}
    MANIFEST.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST} with {len(files)} files")


def check_manifest(corpus: Path) -> int:
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = 0
    for entry in document["files"]:
        path = corpus / entry["path"]
        if not path.is_file():
            print(f"MISSING {entry['path']}")
            failures += 1
            continue
        if path.stat().st_size != entry["size"]:
            print(f"SIZE    {entry['path']}")
            failures += 1
            continue
        if _sha256(path) != entry["sha256"]:
            print(f"HASH    {entry['path']}")
            failures += 1
    total = len(document["files"])
    print(f"{total - failures}/{total} reference files verified")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=CORPUS)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_manifest(args.corpus)
        return 0
    return check_manifest(args.corpus)


if __name__ == "__main__":
    raise SystemExit(main())
