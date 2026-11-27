# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Two-phase container writer spool."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from antennadesk.application.project_payload import ProjectLimits
from antennadesk.persistence.container_writer import ContainerSpool
from antennadesk.persistence.errors import ProjectFormatError, ProjectTooLargeError


def _limits(**overrides: int) -> ProjectLimits:
    values = {
        "container_bytes": 64 * 1024 * 1024,
        "expanded_bytes": 256 * 1024 * 1024,
        "manifest_bytes": 1024 * 1024,
        "entry_bytes": 64 * 1024 * 1024,
        "entries": 100,
        "path_bytes": 255,
    }
    values.update(overrides)
    return ProjectLimits(**values)


def _reference_container(path: Path) -> bytes:
    with zipfile.ZipFile(path) as archive:
        manifest = archive.read("manifest.json")
        data = archive.read("runs/large.raw-output.txt")
    buffer = io.BytesIO()
    with zipfile.ZipFile(
        buffer,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:
        for name, payload in (("manifest.json", manifest), ("runs/large.raw-output.txt", data)):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, payload)
    return buffer.getvalue()


def test_streamed_entry_matches_writestr_across_chunk_boundaries() -> None:
    # Larger than the 1 MiB copy chunk, with a mix of text and repetition.
    data = (b"FREQUENCY 7.100000E+06 60 21 0 0 0 0 0\n" * 90_000) + (b"A" * 1024)
    spool = ContainerSpool(_limits())
    try:
        staged = spool.add_stream(
            "runs/large.raw-output.txt",
            "raw-output",
            io.BytesIO(data),
            expected_bytes=len(data),
        )
        assert staged.sha256
        spool.close_stage()
        spool.write_container(b'{"format":"antennadesk.project"}', "manifest.json")

        assert spool.container_path.read_bytes() == _reference_container(spool.container_path)
    finally:
        spool.cleanup()


def test_streamed_entry_limit_is_enforced_without_materializing() -> None:
    spool = ContainerSpool(_limits(entry_bytes=8))
    try:
        with pytest.raises(ProjectTooLargeError, match="too large"):
            spool.add_stream(
                "runs/large.raw-output.txt",
                "raw-output",
                io.BytesIO(b"0123456789"),
            )
    finally:
        spool.cleanup()


def test_streamed_entry_declared_size_must_match() -> None:
    spool = ContainerSpool(_limits())
    try:
        with pytest.raises(ProjectFormatError, match="size mismatch"):
            spool.add_stream(
                "runs/large.raw-output.txt",
                "raw-output",
                io.BytesIO(b"short"),
                expected_bytes=10,
            )
    finally:
        spool.cleanup()


def test_cleanup_removes_the_spool_directory() -> None:
    spool = ContainerSpool(_limits())
    spool.add_bytes("project.json", "metadata", b"{}")
    spool.close_stage()
    spool.write_container(b"{}", "manifest.json")
    directory = spool.container_path.parent
    assert directory.is_dir()

    spool.cleanup()

    assert not directory.exists()
