"""nec2c process adapter."""

from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

from ...application.ports.antenna_solver import ProgressCallback
from ...application.ports.cancellation import CancelToken
from ...domain.antennas.antenna import AntennaModel
from ...domain.common.time import utc_now
from ...domain.common.validation import (
    Diagnostic,
    Severity,
    has_errors,
)
from ...domain.environment.ground import GroundKind
from ...domain.simulation.result import SimulationResult, SimulationStatus
from ...domain.simulation.solver import SolverCapabilities, SolverMetadata
from ...domain.simulation.spec import SimulationSpec
from ..discretization import validate_segmentation
from ..fingerprint import model_fingerprint
from .capabilities import NEC2C_CAPABILITIES
from .errors import SolverExecutionError, SolverNotAvailable
from .input_writer import write_nec2_input
from .normalization import normalize_nec2_result
from .parser import Nec2ParseError, parse_nec2_output

DEFAULT_MAX_OUTPUT_BYTES = 50 * 1024 * 1024
DEFAULT_VERSION_TIMEOUT_S = 10.0


class Nec2cSolver:
    """Run nec2c as a controlled external process."""

    def __init__(
        self,
        executable: Path,
        *,
        max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
        version_timeout_s: float = DEFAULT_VERSION_TIMEOUT_S,
    ) -> None:
        if max_output_bytes <= 0:
            raise ValueError("max_output_bytes must be positive")
        if version_timeout_s <= 0:
            raise ValueError("version_timeout_s must be positive")
        self._executable = Path(executable).expanduser().resolve()
        self._max_output_bytes = max_output_bytes
        self._version_timeout_s = version_timeout_s
        self._metadata: SolverMetadata | None = None

    def capabilities(self) -> SolverCapabilities:
        return NEC2C_CAPABILITIES

    def version(self) -> SolverMetadata:
        if self._metadata is not None:
            return self._metadata
        if not self._executable.is_file():
            raise SolverNotAvailable(f"nec2c executable not found: {self._executable}")

        try:
            completed = subprocess.run(
                [str(self._executable), "-v"],
                capture_output=True,
                text=True,
                timeout=self._version_timeout_s,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SolverNotAvailable(f"could not run nec2c: {exc}") from exc

        output = (completed.stdout or completed.stderr or "").strip()
        if completed.returncode != 0 or not output:
            raise SolverNotAvailable(f"nec2c -v failed with exit code {completed.returncode}")

        parts = output.split()
        version = parts[-1] if parts else "unknown"
        self._metadata = SolverMetadata(
            name="nec2c",
            version=version,
            executable=str(self._executable),
        )
        return self._metadata

    def validate(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
    ) -> tuple[Diagnostic, ...]:
        diagnostics = list(validate_segmentation(model, spec))

        if spec.include_conductor_losses:
            for wire in model.wires:
                if not math.isclose(
                    wire.material.relative_permeability,
                    1.0,
                    rel_tol=1e-9,
                    abs_tol=1e-9,
                ):
                    diagnostics.append(
                        Diagnostic(
                            code="solver.permeability_unsupported",
                            severity=Severity.WARNING,
                            message=(
                                "relative permeability is not emitted to NEC; "
                                "the adapter models conductor conductivity only"
                            ),
                            field="material.relative_permeability",
                        )
                    )

        if (
            model.environment.ground.kind is not GroundKind.FREE_SPACE
            and spec.far_field.enabled
            and spec.far_field.theta_stop_deg > 90.0
        ):
            diagnostics.append(
                Diagnostic(
                    code="far_field.below_ground",
                    severity=Severity.WARNING,
                    message=(
                        "far-field points below the ground plane were requested; "
                        "use theta <= 90 degrees for ground models"
                    ),
                    field="far_field",
                )
            )

        return tuple(diagnostics)

    def run(
        self,
        model: AntennaModel,
        spec: SimulationSpec,
        *,
        progress_callback: ProgressCallback | None = None,
        cancel_token: CancelToken | None = None,
    ) -> SimulationResult:
        del progress_callback
        started_at = utc_now()
        diagnostics = list(self.validate(model, spec))
        if has_errors(diagnostics):
            return self._empty_result(
                model=model,
                spec=spec,
                solver=self._unavailable_metadata(),
                status=SimulationStatus.ERROR,
                diagnostics=diagnostics,
                started_at=started_at,
            )

        if cancel_token is not None and cancel_token.is_cancelled():
            return self._empty_result(
                model=model,
                spec=spec,
                solver=self._unavailable_metadata(),
                status=SimulationStatus.CANCELLED,
                diagnostics=[
                    Diagnostic(
                        code="solver.cancelled",
                        severity=Severity.WARNING,
                        message="simulation cancelled before execution",
                    )
                ],
                started_at=started_at,
            )

        try:
            metadata = self.version()
        except SolverNotAvailable as exc:
            return self._empty_result(
                model=model,
                spec=spec,
                solver=self._unavailable_metadata(),
                status=SimulationStatus.ERROR,
                diagnostics=[
                    Diagnostic(
                        code="solver.not_available",
                        severity=Severity.ERROR,
                        message=str(exc),
                        field="solver",
                    )
                ],
                started_at=started_at,
            )

        try:
            deck = write_nec2_input(model, spec)
        except ValueError as exc:
            return self._empty_result(
                model=model,
                spec=spec,
                solver=metadata,
                status=SimulationStatus.ERROR,
                diagnostics=[
                    Diagnostic(
                        code="solver.input_error",
                        severity=Severity.ERROR,
                        message=str(exc),
                        field="solver",
                    )
                ],
                started_at=started_at,
            )

        workdir = Path(tempfile.mkdtemp(prefix="adnec2-"))
        input_path = workdir / "in.nec"
        output_path = workdir / "out.out"
        input_text = deck.text
        output_text = ""
        stderr = ""

        try:
            input_path.write_text(input_text, encoding="utf-8", newline="\n")
            process: subprocess.Popen[str] = subprocess.Popen(
                [
                    str(self._executable),
                    "-i",
                    input_path.name,
                    "-o",
                    output_path.name,
                ],
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            deadline = time.monotonic() + spec.timeout_s
            while True:
                if process.poll() is not None:
                    break
                if cancel_token is not None and cancel_token.is_cancelled():
                    self._terminate(process)
                    _, process_stderr = process.communicate(timeout=5)
                    stderr = process_stderr or ""
                    return self._empty_result(
                        model=model,
                        spec=spec,
                        solver=metadata,
                        status=SimulationStatus.CANCELLED,
                        diagnostics=[
                            Diagnostic(
                                code="solver.cancelled",
                                severity=Severity.WARNING,
                                message="simulation cancelled",
                            )
                        ],
                        started_at=started_at,
                        raw_input=input_text,
                        stderr=stderr,
                    )
                if time.monotonic() > deadline:
                    self._terminate(process)
                    _, process_stderr = process.communicate(timeout=5)
                    stderr = process_stderr or ""
                    return self._empty_result(
                        model=model,
                        spec=spec,
                        solver=metadata,
                        status=SimulationStatus.ERROR,
                        diagnostics=[
                            Diagnostic(
                                code="solver.timeout",
                                severity=Severity.ERROR,
                                message=(f"nec2c did not finish within {spec.timeout_s:g} seconds"),
                            )
                        ],
                        started_at=started_at,
                        raw_input=input_text,
                        stderr=stderr,
                    )
                time.sleep(0.05)

            _, process_stderr = process.communicate(timeout=5)
            stderr = process_stderr or ""
            return_code = process.returncode if process.returncode is not None else -1

            if return_code != 0:
                output_text = self._read_output_or_empty(output_path)
                return self._empty_result(
                    model=model,
                    spec=spec,
                    solver=metadata,
                    status=SimulationStatus.ERROR,
                    diagnostics=[
                        Diagnostic(
                            code="solver.exit_code",
                            severity=Severity.ERROR,
                            message=f"nec2c exited with code {return_code}",
                        )
                    ],
                    started_at=started_at,
                    raw_input=input_text,
                    raw_output=output_text,
                    stderr=stderr,
                )

            output_text = self._read_output(output_path)
            parsed = parse_nec2_output(output_text)
            finished_at = utc_now()
            return normalize_nec2_result(
                model=model,
                spec=spec,
                deck=deck,
                parsed=parsed,
                solver=metadata,
                diagnostics=diagnostics,
                raw_input=input_text,
                raw_output=output_text,
                stderr=stderr,
                started_at=started_at,
                finished_at=finished_at,
            )
        except (
            OSError,
            subprocess.TimeoutExpired,
            SolverExecutionError,
            Nec2ParseError,
            ValueError,
        ) as exc:
            if not output_text:
                output_text = self._read_output_or_empty(output_path)
            return self._empty_result(
                model=model,
                spec=spec,
                solver=metadata,
                status=SimulationStatus.ERROR,
                diagnostics=[
                    Diagnostic(
                        code="solver.execution_error",
                        severity=Severity.ERROR,
                        message=str(exc),
                    )
                ],
                started_at=started_at,
                raw_input=input_text,
                raw_output=output_text,
                stderr=stderr,
            )
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    def _unavailable_metadata(self) -> SolverMetadata:
        return SolverMetadata(
            name="nec2c",
            version="unavailable",
            executable=str(self._executable),
        )

    def _empty_result(
        self,
        *,
        model: AntennaModel,
        spec: SimulationSpec,
        solver: SolverMetadata,
        status: SimulationStatus,
        diagnostics: list[Diagnostic],
        started_at: datetime,
        raw_input: str = "",
        raw_output: str = "",
        stderr: str = "",
    ) -> SimulationResult:
        finished_at = utc_now()
        return SimulationResult(
            status=status,
            spec=spec,
            model_fingerprint=model_fingerprint(model, spec),
            solver=solver,
            frequencies=(),
            diagnostics=tuple(diagnostics),
            raw_input=raw_input,
            raw_output=raw_output,
            stderr=stderr,
            duration_s=(finished_at - started_at).total_seconds(),
            started_at=started_at,
            finished_at=finished_at,
        )

    def _read_output(self, path: Path) -> str:
        if not path.is_file():
            raise SolverExecutionError("nec2c produced no output file")
        size = path.stat().st_size
        if size > self._max_output_bytes:
            raise SolverExecutionError(
                f"nec2c output is too large ({size} bytes; limit is {self._max_output_bytes})"
            )
        return path.read_text(encoding="utf-8", errors="replace")

    def _read_output_or_empty(self, path: Path) -> str:
        try:
            return self._read_output(path)
        except (OSError, SolverExecutionError):
            return ""

    @staticmethod
    def _terminate(process: subprocess.Popen[str]) -> None:
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        except OSError:
            pass
