"""Routing-related Claude hook script generators."""

from textwrap import dedent


def _instruction_router_script() -> str:
    """Return the non-blocking instruction router hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Instruction Auto-Injection Hook.

            PreToolUse hook that automatically surfaces relevant domain constraints
            when editing files, based on .github/instructions/*.instructions.md
            applyTo glob patterns.

            Informational only — never blocks operations. Outputs constraint
            reminders to stderr so they appear in the agent's context.

            Deduplication: tracks surfaced instructions in a state file and
            suppresses repeats within a 2-hour window per instruction file.

            Exit codes:
              0 - Always (non-blocking; informational only)
            \"\"\"

            import fnmatch
            import json
            import re
            import sys
            import time
            from pathlib import Path

            DEDUP_WINDOW_SECONDS = 2 * 60 * 60
            CONSTRAINT_KEYWORDS = (
                "prohibited",
                "must not",
                "must",
                "anti-pattern",
                "covenant",
                "core principles",
                "responsibilities",
            )
            MAX_LINES_PER_FILE = 15
            UNIVERSAL_INSTRUCTION = "cross-platform.instructions.md"


            def parse_apply_to(file_path):
                \"\"\"Extract applyTo glob patterns from instruction frontmatter.\"\"\"
                try:
                    text = file_path.read_text(encoding="utf-8")
                except OSError:
                    return []

                if not text.startswith("---"):
                    return []

                end = text.find("---", 3)
                if end == -1:
                    return []

                frontmatter = text[3:end]
                for line in frontmatter.splitlines():
                    line = line.strip()
                    if line.startswith("applyTo:"):
                        value = line[len("applyTo:") :].strip().strip('"').strip("'")
                        return [pattern.strip() for pattern in value.split(",") if pattern.strip()]
                return []


            def extract_constraint_sections(file_path):
                \"\"\"Extract key constraint sections from an instruction file.\"\"\"
                try:
                    text = file_path.read_text(encoding="utf-8")
                except OSError:
                    return []

                lines = text.splitlines()
                result = []
                capturing = False
                capture_level = 0

                for line in lines:
                    heading_match = re.match(r"^(#{1,6})\\s+(.*)", line)
                    if heading_match:
                        level = len(heading_match.group(1))
                        title = heading_match.group(2).lower()

                        if capturing and level <= capture_level:
                            capturing = False

                        if any(keyword in title for keyword in CONSTRAINT_KEYWORDS):
                            capturing = True
                            capture_level = level
                            result.append(line)
                            continue

                    if capturing and (not result or result[-1].strip() or line.strip()):
                        result.append(line)

                    if len(result) >= MAX_LINES_PER_FILE:
                        break

                return result[:MAX_LINES_PER_FILE]


            def load_state(state_path):
                \"\"\"Load dedup state from JSON file.\"\"\"
                try:
                    return json.loads(state_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    return {}


            def save_state(state_path, state):
                \"\"\"Persist dedup state to JSON file.\"\"\"
                try:
                    state_path.parent.mkdir(parents=True, exist_ok=True)
                    state_path.write_text(json.dumps(state, indent=2) + "\\n", encoding="utf-8")
                except OSError:
                    pass


            def main():
                \"\"\"Route file edits to matching instruction constraints.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                file_path = tool_input.get("file_path", "")
                cwd = input_data.get("cwd", "")

                if not file_path or not cwd:
                    sys.exit(0)

                try:
                    abs_path = Path(file_path).resolve()
                    cwd_path = Path(cwd).resolve()
                    rel_path = abs_path.relative_to(cwd_path)
                    rel_str = rel_path.as_posix()
                except (ValueError, TypeError):
                    sys.exit(0)

                instructions_dir = cwd_path / ".github" / "instructions"
                if not instructions_dir.is_dir():
                    sys.exit(0)

                instruction_files = sorted(instructions_dir.glob("*.instructions.md"))
                if not instruction_files:
                    sys.exit(0)

                matched = []
                is_python_file = rel_str.endswith(".py")

                for inst_file in instruction_files:
                    patterns = parse_apply_to(inst_file)
                    for pattern in patterns:
                        if fnmatch.fnmatch(rel_str, pattern):
                            matched.append(inst_file)
                            break

                if is_python_file:
                    universal = instructions_dir / UNIVERSAL_INSTRUCTION
                    if universal.is_file() and universal not in matched:
                        matched.append(universal)

                if not matched:
                    sys.exit(0)

                state_path = cwd_path / ".claude" / "hooks" / ".instruction-state.json"
                state = load_state(state_path)
                now = time.time()

                to_surface = []
                for inst_file in matched:
                    key = inst_file.name
                    last_surfaced = state.get(key, 0)
                    if (now - last_surfaced) >= DEDUP_WINDOW_SECONDS:
                        to_surface.append(inst_file)

                if not to_surface:
                    sys.exit(0)

                output_parts = []
                output_parts.append("INSTRUCTION CONSTRAINTS (auto-surfaced)")
                output_parts.append("=" * 45)
                output_parts.append(f"Triggered by: {rel_str}")
                output_parts.append("")

                for inst_file in to_surface:
                    sections = extract_constraint_sections(inst_file)
                    if not sections:
                        continue

                    output_parts.append(f"--- {inst_file.name} ---")
                    output_parts.extend(sections)
                    output_parts.append("")
                    state[inst_file.name] = now

                has_content = any(
                    line.startswith("--- ") and line.endswith(" ---") for line in output_parts
                )
                if not has_content:
                    sys.exit(0)

                save_state(state_path, state)
                print("\\n".join(output_parts), file=sys.stderr)
                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _pipeline_router_script() -> str:
    """Return the pipeline router hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Pipeline Router Hook.

            PostToolUse hook on ExitPlanMode that routes the agent to
            `uv run gz obpi pipeline` after plan approval for OBPI work.

            How it works:
              1. Reads `.claude/plans/.plan-audit-receipt.json`
              2. If the receipt exists, names an OBPI, and has verdict `PASS`,
                 emit a routing instruction on stdout directing the agent to
                 invoke the canonical runtime command
              3. If the receipt is absent, invalid, or not `PASS`, exit silently

            Exit codes:
              0 - Always (PostToolUse hooks should not block)
            \"\"\"

            import json
            import os
            import sys
            from pathlib import Path


            def find_project_root(start: Path) -> Path:
                \"\"\"Find the project root by looking for .gzkit or src/gzkit.\"\"\"
                current = start
                while current != current.parent:
                    if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
                        return current
                    current = current.parent
                return start


            def main() -> None:
                \"\"\"Route approved OBPI plans into the pipeline.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
                sys.path.insert(0, str(project_root / "src"))

                try:
                    from gzkit.pipeline_runtime import (
                        load_plan_audit_receipt,
                        pipeline_plans_dir,
                        pipeline_router_message,
                    )
                except Exception:
                    sys.exit(0)

                plans_dir = pipeline_plans_dir(project_root)
                receipt_path = plans_dir / ".plan-audit-receipt.json"
                if not receipt_path.exists():
                    sys.exit(0)

                receipt_state, _warnings, receipt = load_plan_audit_receipt(plans_dir, "")
                if receipt is None or receipt_state != "pass":
                    sys.exit(0)

                obpi_id = str(receipt.get("obpi_id") or "")
                if not obpi_id:
                    sys.exit(0)

                print(pipeline_router_message(obpi_id))
                sys.exit(0)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )


def _pipeline_gate_script() -> str:
    """Return the pipeline gate hook script."""
    return (
        dedent(
            """\
            #!/usr/bin/env python3
            \"\"\"Pipeline Gate Hook.

            PreToolUse hook on Write|Edit that blocks implementation file writes
            under `src/` and `tests/` when an OBPI plan-audit receipt exists but
            the governance pipeline has not been activated.

            Exit codes:
              0 - Allow operation
              2 - Block operation (pipeline not invoked)
            \"\"\"

            import json
            import os
            import re
            import sys
            from pathlib import Path


            def resolve_repo_path(cwd: str, file_path: str) -> str | None:
                \"\"\"Resolve a tool file path into a repo-relative POSIX path.\"\"\"
                if not cwd or not file_path:
                    return None

                try:
                    cwd_path = Path(cwd).resolve()
                    target = Path(file_path)
                    if not target.is_absolute():
                        target = cwd_path / target
                    rel_path = target.resolve().relative_to(cwd_path)
                except (OSError, TypeError, ValueError):
                    return None

                return rel_path.as_posix()


            def find_project_root(start: Path) -> Path:
                \"\"\"Find the project root by looking for .gzkit or src/gzkit.\"\"\"
                current = start
                while current != current.parent:
                    if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
                        return current
                    current = current.parent
                return start


            def _is_path_within_scope(rel_path: str, allowed_paths: list[str]) -> bool:
                \"\"\"Check if rel_path falls within any of the OBPI's allowed paths (#127).\"\"\"
                for allowed in allowed_paths:
                    clean = allowed.rstrip("/").replace("/**", "")
                    if rel_path == clean or rel_path.startswith(clean + "/"):
                        return True
                return False


            def _extract_allowed_paths_from_brief(brief_path: Path) -> list[str]:
                \"\"\"Extract allowed paths from an OBPI brief file (#127).\"\"\"
                try:
                    content = brief_path.read_text(encoding="utf-8")
                except OSError:
                    return []
                match = re.search(
                    r"^## Allowed Paths\\s*$([\\s\\S]*?)(?:^## |\\Z)",
                    content,
                    flags=re.MULTILINE,
                )
                if not match:
                    return []
                paths: list[str] = []
                for line in match.group(1).splitlines():
                    stripped = line.strip()
                    if not stripped.startswith("-"):
                        continue
                    backticked = re.findall(r"`([^`]+)`", stripped)
                    candidates = backticked or [re.sub(r"^-+\\s*", "", stripped).split(" - ", 1)[0]]
                    for candidate in candidates:
                        normalized = candidate.strip().replace("\\\\", "/")
                        if normalized and " " not in normalized:
                            paths.append(normalized)
                return paths


            def main() -> None:
                \"\"\"Gate implementation writes until the pipeline is active.\"\"\"
                try:
                    input_data = json.load(sys.stdin)
                except json.JSONDecodeError:
                    sys.exit(0)

                tool_input = input_data.get("tool_input", {})
                rel_path = resolve_repo_path(
                    input_data.get("cwd", os.getcwd()),
                    tool_input.get("file_path", ""),
                )
                if rel_path is None or not rel_path.startswith(("src/", "tests/")):
                    sys.exit(0)

                project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
                sys.path.insert(0, str(project_root / "src"))

                try:
                    from gzkit.pipeline_runtime import (
                        extract_brief_status,
                        find_obpi_brief,
                        load_plan_audit_receipt,
                        marker_matches,
                        pipeline_gate_message,
                        pipeline_marker_paths,
                        pipeline_plans_dir,
                    )
                except Exception:
                    sys.exit(0)

                plans_dir = pipeline_plans_dir(project_root)
                receipt_path = plans_dir / ".plan-audit-receipt.json"
                if not receipt_path.exists():
                    sys.exit(0)

                receipt_state, _warnings, receipt = load_plan_audit_receipt(plans_dir, "")
                if receipt is None or receipt_state != "pass":
                    sys.exit(0)

                obpi_id = str(receipt.get("obpi_id") or "")
                if not obpi_id:
                    sys.exit(0)

                # GHI-127: Skip gate if the OBPI brief is already Completed (stale receipt).
                docs_root = project_root / "docs"
                brief_path = find_obpi_brief(docs_root, obpi_id)
                if brief_path is not None:
                    brief_status = extract_brief_status(brief_path)
                    if brief_status and brief_status.lower() == "completed":
                        sys.exit(0)

                    # GHI-127: Scope enforcement to the OBPI's allowed paths.
                    allowed_paths = _extract_allowed_paths_from_brief(brief_path)
                    if allowed_paths and not _is_path_within_scope(rel_path, allowed_paths):
                        sys.exit(0)

                obpi_marker, legacy_marker = pipeline_marker_paths(plans_dir, obpi_id)
                if marker_matches(obpi_marker, obpi_id):
                    sys.exit(0)

                if marker_matches(legacy_marker, obpi_id):
                    sys.exit(0)

                print(pipeline_gate_message(obpi_id), file=sys.stderr)
                sys.exit(2)


            if __name__ == "__main__":
                main()
            """
        )
        + "\n"
    )
