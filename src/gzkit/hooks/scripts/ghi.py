"""GHI-related Claude hook script generators."""

from textwrap import dedent


def _ghi_triage_chat_silence_script() -> str:
    """Return the ghi-triage chat-silence backstop hook script.

    PreToolUse hook on Bash that fires when a command invokes
    `triage.py --format rank`. Scans the assistant's most recent turn for
    the prose-preamble shape that duplicates the rank renderer's output
    into the chat surface (>=2 distinct GHI tokens each near a severity
    word). Hit -> exit 2, blocking the tool call.

    Authored under GHI #424 round 4 as the structural backstop on the
    chat-text surface; the cache-path requirement on triage.py covers
    the bash-command-line surface independently.
    """
    return dedent(
        '''\
            #!/usr/bin/env python3
            """ghi-triage chat-silence backstop hook.

            PreToolUse hook on Bash. When the command invokes
            `triage.py --format rank`, scan the assistant\'s most recent turn for the
            prose-preamble shape that duplicates the rank renderer\'s deliverable into
            chat. Hit -> exit 2, blocking the tool call.

            Why this hook exists (GHI #424 round 4):
                Three closures (commits 09f89e99, 78314602, 8f1c9212) tried to fix
                chat-prose duplication with doctrine and a schema strip. Doctrine
                fails turn-to-turn; the schema strip plugged the rank-input payload
                but not the assistant text surface. This hook is the structural
                backstop on the chat surface so the duplicate-render shape becomes
                detectable regardless of whether the rule lives in the agent\'s
                short-term memory.

            Detection rule:
                - Tool must be Bash and command must match `triage.py` AND `--format rank`
                - Read `transcript_path` (PreToolUse always provides it)
                - Find last assistant message; concatenate its text content blocks
                - Pattern: at least 2 distinct `#NNN` GHI tokens, each within 200
                  characters of a severity token (blocking|degrading|latent,
                  case-insensitive)
                - Hit -> exit 2 with stderr naming GHI #424 and the offending tokens

            Threshold rationale:
                Single `#NNN` mention near a severity word is allowed (legitimate
                references to the offending GHI itself, e.g. "#424 was blocking the
                pipeline"). The duplication shape this hook targets is a per-GHI
                queue summary, which always involves at least two pairs.

            Exit codes:
                0 - allow (no violation, or invocation does not match triage rank)
                2 - block (chat-prose duplication detected)
            """

            from __future__ import annotations

            import json
            import re
            import sys
            from pathlib import Path

            SEVERITY_RE = re.compile(r"\\b(blocking|degrading|latent)\\b", re.IGNORECASE)
            GHI_RE = re.compile(r"#(\\d+)\\b")
            PROSE_PROXIMITY_CHARS = 200
            MIN_DISTINCT_PAIRS = 2
            TRIAGE_INVOCATION_RE = re.compile(r"triage\\.py[^\\n]*--format\\s+rank", re.DOTALL)


            def _load_input() -> dict | None:
                try:
                    return json.load(sys.stdin)
                except (json.JSONDecodeError, OSError, ValueError):
                    return None


            def _last_assistant_text(transcript_path: Path) -> str:
                """Concatenate text-content blocks of the most recent assistant turn."""
                if not transcript_path.is_file():
                    return ""
                try:
                    lines = transcript_path.read_text(encoding="utf-8").splitlines()
                except OSError:
                    return ""
                for raw in reversed(lines):
                    if not raw.strip():
                        continue
                    try:
                        entry = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if entry.get("type") != "assistant":
                        continue
                    message = entry.get("message", {})
                    content = message.get("content", [])
                    if not isinstance(content, list):
                        continue
                    text_parts: list[str] = []
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") != "text":
                            continue
                        text = block.get("text", "")
                        if isinstance(text, str):
                            text_parts.append(text)
                    return "\\n".join(text_parts)
                return ""


            def find_violation_pairs(text: str) -> list[tuple[str, str]]:
                """Return (ghi_token, severity_token) pairs that violate the proximity rule."""
                pairs: list[tuple[str, str]] = []
                seen_ghis: set[str] = set()
                for ghi_match in GHI_RE.finditer(text):
                    ghi_num = ghi_match.group(1)
                    if ghi_num in seen_ghis:
                        continue
                    start = max(0, ghi_match.start() - PROSE_PROXIMITY_CHARS)
                    end = min(len(text), ghi_match.end() + PROSE_PROXIMITY_CHARS)
                    window = text[start:end]
                    sev = SEVERITY_RE.search(window)
                    if sev:
                        seen_ghis.add(ghi_num)
                        pairs.append((f"#{ghi_num}", sev.group(0)))
                return pairs


            def main() -> int:
                payload = _load_input()
                if not payload:
                    return 0
                if payload.get("tool_name") != "Bash":
                    return 0
                tool_input = payload.get("tool_input", {})
                command = tool_input.get("command", "")
                if not isinstance(command, str) or not TRIAGE_INVOCATION_RE.search(command):
                    return 0
                transcript_path = payload.get("transcript_path")
                if not isinstance(transcript_path, str):
                    return 0
                text = _last_assistant_text(Path(transcript_path))
                if not text:
                    return 0
                pairs = find_violation_pairs(text)
                if len(pairs) < MIN_DISTINCT_PAIRS:
                    return 0
                pair_summary = ", ".join(f"{g} near {s}" for g, s in pairs[:5])
                sys.stderr.write(
                    "ghi-triage chat-silence backstop (GHI #424): "
                    f"detected {len(pairs)} GHI/severity proximity pairs in the same "
                    "assistant turn as the `triage.py --format rank` invocation: "
                    f"{pair_summary}.\\n"
                    "\\n"
                    "The rendered rank list is the deliverable. Per "
                    ".gzkit/skills/ghi-triage/SKILL.md anti-patterns, the agent must "
                    "NOT narrate severity choices in chat before piping to "
                    "--format rank. The Bash tool result already presents the rank "
                    "list; chat-side restatement duplicates the deliverable.\\n"
                    "\\n"
                    "Recovery: drop the per-GHI prose preamble. The agent\'s cognitive "
                    "contribution is selection + ordering + severity, encoded in the "
                    "rank-input JSON. Prose belongs in the renderer\'s output only.\\n"
                )
                return 2


            if __name__ == "__main__":
                sys.exit(main())
            '''
    )
