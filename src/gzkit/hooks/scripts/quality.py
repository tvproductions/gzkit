"""Quality-related Claude hook script generators."""

from textwrap import dedent


def _post_edit_ruff_script() -> str:
    """Return the non-blocking post-edit ruff hook script."""
    return dedent(
        """\
            #!/usr/bin/env python3
            \"\"\"Post-Edit Ruff Hook.

            PostToolUse hook that runs ruff check (lint-only, no fix) on edited
            Python files immediately after each Write/Edit operation.

            Reports lint issues without modifying files — avoids the import-removal
            problem where --fix deletes an import before the next Edit adds usage
            (GHI #239). On non-zero exit, the first N lines of ruff output are
            written to stderr so the agent sees the warning in the same turn and
            can correct course before the import colocation window closes.

            Exit codes:
              0 - Always (non-blocking; lint failures do not prevent edits)
            \"\"\"

            import json
            import subprocess
            import sys
            from contextlib import suppress
            from pathlib import Path

            TIMEOUT_SECONDS = 8
            MAX_OUTPUT_LINES = 20


            def main():
                \"\"\"Run ruff on the edited file if it is a Python file.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                file_path = tool_input.get("file_path", "")

                if not file_path.endswith(".py"):
                    sys.exit(0)

                cwd = input_data.get("cwd", "")
                try:
                    target = Path(file_path)
                    if not target.is_absolute() and cwd:
                        target = Path(cwd) / target
                    target = target.resolve()
                except (ValueError, TypeError, OSError):
                    sys.exit(0)

                if not target.is_file():
                    sys.exit(0)

                posix_path = target.as_posix()

                with suppress(FileNotFoundError, subprocess.TimeoutExpired, OSError):
                    result = subprocess.run(
                        ["uv", "run", "ruff", "check", posix_path],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=TIMEOUT_SECONDS,
                    )
                    if result.returncode != 0:
                        combined = (result.stdout or "") + (result.stderr or "")
                        lines = combined.splitlines()[:MAX_OUTPUT_LINES]
                        if lines:
                            sys.stderr.write(
                                f"post-edit-ruff: lint findings on {target.name}\\n"
                            )
                            sys.stderr.write("\\n".join(lines) + "\\n")

                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
    )


def _stop_turn_feedback_script() -> str:
    """Return the blocking stop-turn-feedback Stop hook script (ADR-0.0.70)."""
    return dedent(
        """\
            #!/usr/bin/env python3
            \"\"\"Stop-Turn-Feedback Hook (ADR-0.0.70, OBPI-0.0.70-01).

            Stop hook that runs ruff check (lint-only) over git-dirty Python files
            at agent turn end. On findings it blocks the stop with agent-actionable
            prose — what failed, why it is forbidden, the governed next step
            (.gzkit/rules/guardrail-feedback-prose.md) — so the agent self-corrects
            before declaring done (the Buetow stop-hook mechanism).

            Fail-open contract (ADR-0.0.70 Boundary Invariant 1: a turn can always end):
              - `stop_hook_active` true in the stdin payload -> never block again
              - GZ_STOP_FEEDBACK=off -> disabled without editing settings.json
              - malformed stdin, missing ruff, subprocess timeout, non-git cwd -> allow

            Telemetry: each block appends one JSON line to
            .gzkit/sensors/stop-turn-feedback.jsonl (gitignored). Cap 1 MiB; an
            over-cap log is rewritten keeping only its newest 500 lines.

            Exit codes:
              0 - Allow the stop (default; all failure modes)
              2 - Block the stop; stderr carries the feedback prose
            \"\"\"

            import json
            import os
            import subprocess
            import sys
            import tempfile
            from contextlib import suppress
            from datetime import UTC, datetime
            from pathlib import Path

            TIMEOUT_SECONDS = 2
            MAX_OUTPUT_LINES = 20
            OFF_SWITCH_ENV = "GZ_STOP_FEEDBACK"
            TELEMETRY_PATH = ".gzkit/sensors/stop-turn-feedback.jsonl"
            TELEMETRY_MAX_BYTES = 1_048_576
            TELEMETRY_KEEP_LINES = 500


            def collect_dirty_python_files(cwd: Path) -> list[str]:
                \"\"\"Return git working-tree dirty .py paths that exist on disk.\"\"\"
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    cwd=cwd,
                    timeout=TIMEOUT_SECONDS,
                )
                if result.returncode != 0:
                    return []
                files: list[str] = []
                for line in result.stdout.splitlines():
                    if len(line) < 4:
                        continue
                    path = line[3:].strip().strip('"')
                    if " -> " in path:  # rename entries: keep the destination
                        path = path.split(" -> ", 1)[1].strip('"')
                    if path.endswith(".py") and (cwd / path).is_file():
                        files.append(path)
                return files


            def run_ruff(files: list[str], cwd: Path) -> tuple[int, str]:
                \"\"\"Run ruff check over the files; return (returncode, combined output).\"\"\"
                result = subprocess.run(
                    ["uv", "run", "ruff", "check", *files],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    cwd=cwd,
                    timeout=TIMEOUT_SECONDS,
                )
                return result.returncode, (result.stdout or "") + (result.stderr or "")


            def build_block_message(findings: str, file_count: int) -> str:
                \"\"\"Render the three-part guardrail-feedback-prose bar.\"\"\"
                lines = findings.splitlines()[:MAX_OUTPUT_LINES]
                return (
                    f"stop-turn-feedback: BLOCKED — turn-end lint check failed across "
                    f"{file_count} dirty Python file(s).\\n\\n"
                    "What failed:\\n" + "\\n".join(lines) + "\\n\\n"
                    "Why this is forbidden: gzkit forbids ending a turn while the cheap "
                    "deterministic tier is red (AGENTS.md Behavior Rules — Never #5; "
                    "ADR-0.0.70 turn-end feedback; "
                    ".gzkit/rules/guardrail-feedback-prose.md).\\n\\n"
                    "Governed next step: fix the findings above, verify with "
                    "`uv run ruff check <files>`, then end the turn. One block per turn — "
                    "the next stop proceeds even if findings remain (fail-open)."
                )


            def append_telemetry(cwd: Path, *, files: int, findings_lines: int) -> None:
                \"\"\"Append one JSON line; rewrite an over-cap log keeping the newest lines.\"\"\"
                log = cwd / TELEMETRY_PATH
                log.parent.mkdir(parents=True, exist_ok=True)
                if log.is_file() and log.stat().st_size > TELEMETRY_MAX_BYTES:
                    kept = log.read_text(encoding="utf-8").splitlines()[-TELEMETRY_KEEP_LINES:]
                    log.write_text("\\n".join(kept) + "\\n", encoding="utf-8")
                record = {
                    "ts": datetime.now(UTC).isoformat(),
                    "blocked": True,
                    "files": files,
                    "findings_lines": findings_lines,
                }
                with log.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record) + "\\n")


            def run_demo() -> int:
                \"\"\"Run the check pipeline on a synthetic violation; print the prose.\"\"\"
                with tempfile.TemporaryDirectory() as tmp:
                    sample = Path(tmp) / "demo_violation.py"
                    sample.write_text("import os\\n", encoding="utf-8")
                    try:
                        _, findings = run_ruff([sample.name], Path(tmp))
                    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
                        findings = "demo_violation.py:1:8: F401 [*] `os` imported but unused"
                sys.stdout.write(build_block_message(findings, 1) + "\\n")
                return 0


            def main(argv: list[str]) -> int:
                \"\"\"Run the turn-end check; 0 allows the stop, 2 blocks with feedback.\"\"\"
                if "--demo" in argv:
                    return run_demo()

                if os.environ.get(OFF_SWITCH_ENV, "").lower() == "off":
                    return 0

                try:
                    payload = json.load(sys.stdin)
                except (json.JSONDecodeError, TypeError, ValueError, OSError):
                    return 0

                if payload.get("stop_hook_active"):
                    return 0

                try:
                    cwd = Path(payload.get("cwd") or os.getcwd()).resolve()
                    files = collect_dirty_python_files(cwd)
                    if not files:
                        return 0
                    returncode, findings = run_ruff(files, cwd)
                except (FileNotFoundError, subprocess.TimeoutExpired, OSError, ValueError):
                    return 0

                if returncode == 0:
                    return 0

                with suppress(OSError):
                    findings_lines = len(findings.splitlines())
                    append_telemetry(cwd, files=len(files), findings_lines=findings_lines)
                sys.stderr.write(build_block_message(findings, len(files)) + "\\n")
                return 2


            if __name__ == "__main__":
                sys.exit(main(sys.argv[1:]))
        """
    )
