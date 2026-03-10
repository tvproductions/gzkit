import io
import os
import tempfile
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CliResult:
    """Simple CLI invocation result."""

    exit_code: int
    output: str


class CliRunner:
    """Minimal stdlib-only CLI test runner."""

    @contextmanager
    def isolated_filesystem(self):
        cwd = Path.cwd()
        old_no_color = os.environ.get("NO_COLOR")
        os.environ["NO_COLOR"] = "1"
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            try:
                yield
            finally:
                os.chdir(cwd)
                if old_no_color is None:
                    del os.environ["NO_COLOR"]
                else:
                    os.environ["NO_COLOR"] = old_no_color

    def invoke(self, command, args):
        output = io.StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            try:
                exit_code = command(args)
            except SystemExit as exc:
                code = exc.code
                exit_code = code if isinstance(code, int) else 1
        return CliResult(
            exit_code=0 if exit_code is None else int(exit_code),
            output=output.getvalue(),
        )


def _write_obpi(
    path: Path,
    status: str,
    brief_status: str,
    implementation_line: str,
    *,
    lane: str = "Lite",
    key_proof: str = "uv run gz adr status ADR-0.1.0 --json",
    human_attestation: tuple[str, str, str] | None = None,
) -> None:
    lines = [
        "---",
        "id: OBPI-0.1.0-01-demo",
        "parent: ADR-0.1.0",
        "item: 1",
        f"lane: {lane}",
        f"status: {status}",
        "---",
        "",
        "# OBPI-0.1.0-01-demo: Demo",
        "",
        f"**Brief Status:** {brief_status}",
        "",
        "## Evidence",
        "",
        "### Implementation Summary",
        f"- Files created/modified: {implementation_line}",
        "- Validation commands run: uv run -m unittest discover tests",
        "- Date completed: 2026-02-14",
        "",
        "## Key Proof",
        key_proof,
        "",
    ]
    if human_attestation is not None:
        attestor, attestation, attestation_date = human_attestation
        lines.extend(
            [
                "## Human Attestation",
                f"- Attestor: {attestor}",
                f"- Attestation: {attestation}",
                f"- Date: {attestation_date}",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n")
