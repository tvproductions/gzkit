#!/usr/bin/env python3
"""Instruction Auto-Injection Hook.

PreToolUse hook that automatically surfaces relevant domain constraints
when editing files, based on .github/instructions/*.instructions.md
applyTo glob patterns.

Informational only — never blocks operations. Outputs constraint
reminders to stderr so they appear in the agent's context.

Deduplication: tracks surfaced instructions in a state file and
suppresses repeats within a 2-hour window per instruction file.

Exit codes:
  0 - Always (non-blocking; informational only)
"""

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
    """Extract applyTo glob patterns from instruction frontmatter."""
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
    """Extract key constraint sections from an instruction file."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError:
        return []

    lines = text.splitlines()
    result = []
    capturing = False
    capture_level = 0

    for line in lines:
        heading_match = re.match(r"^(#{1,6})\s+(.*)", line)
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
    """Load dedup state from JSON file."""
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state_path, state):
    """Persist dedup state to JSON file."""
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def main():
    """Route file edits to matching instruction constraints."""
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
    print("\n".join(output_parts), file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()

