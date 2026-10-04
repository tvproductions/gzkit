"""Where the context of an agent session grew, and what grew it.

Read-only. Stdlib only. Reads Claude Code transcripts (JSONL) and writes a JSON
results file and CSV files beside this script.

Method, kept consistent with
docs/governance/obpi-run-cost-2026-10-03-evidence/session_token_cost.py:
one usage record per API call, de-duplicated by message id (first appearance fixes
the order, the last row for an id supplies the usage), and

    context = input_tokens + cache_read_input_tokens + cache_creation_input_tokens

Measured: everything taken from a `usage` record (context, cache-read, output).
Estimated: every figure derived from a character count (tokens ~ chars / 4).
Projected: section `projection`, which is arithmetic on the measured curve.

Run from the repository root:

    uv run python docs/governance/context-phase-review-2026-10-04-evidence/context_analysis.py
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parent
# Transcripts live outside the repository, under a directory named for the checkout path.
PROJECTS = Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd()))
SESSIONS = {
    "baseline_OBPI-0.35.0-08": "553e5afb-48e8-4cae-be4a-db046a3690ba",
    "trial_OBPI-0.35.0-10": "a0f543a5-5dc2-41ff-949b-f036f79ce0a1",
}
# Sibling window for the baseline, copied from the evidence README.
BASELINE_SIBLING_WINDOW = ("2026-10-03T06:55:00+00:00", "2026-10-03T11:35:00+00:00")
EXPECTED_BASELINE = {
    "calls": 260,
    "cache_read_input_tokens": 118_627_618,
    "first_context": 55_206,
    "peak_context": 743_855,
}
EXPECTED_BASELINE_SUBAGENTS = {
    "calls": 145,
    "cache_read_input_tokens": 13_390_717,
    "peak_context": 232_736,
}
EXPECTED_BASELINE_SIBLINGS = {
    "files": 12,
    "calls": 152,
    "cache_read_input_tokens": 21_910_398,
    "peak_context": 269_644,
}
CTX_KEYS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
SAVE_POINT_TOKENS = 20_000
CHARS_PER_TOKEN = 4  # estimate, not a measurement

# A marker is an invocation, not a mention: it needs the `uv run gz` prefix and
# must not be a --help call. Prose inside --summary text does not carry the prefix.
GZ = r"uv run gz "
NOHELP = r"(?![^;&|\n]*--help)"
MARKERS: dict[str, str] = {
    "pipeline_launch": GZ + r"obpi pipeline\b" + NOHELP,
    "single_driver_dispatch": GZ + r"obpi dispatch\b[^;&|\n]*--single-driver",
    "reviewer_dispatch": r"claude\s+--agent\s+(?:spec|quality)-reviewer",
    "s3_arb_ruff": GZ + r"arb ruff\b" + NOHELP,
    "s3_arb_typecheck": GZ + r"arb typecheck\b" + NOHELP,
    "s3_arb_unittest": GZ + r"arb step --name unittest\b",
    "s3_covers": GZ + r"covers\b" + NOHELP,
    "s3_arb_red": GZ + r"arb red\b" + NOHELP,
    "s4_present_evidence": GZ + r"obpi present-evidence\b" + NOHELP,
    "s4_verify_packet": GZ + r"obpi verify-packet\b" + NOHELP,
    "s4_codex_companion": r"codex-companion\S*\s+task\b",
    "s4_acceptance_review": GZ + r"obpi acceptance\b[^;&|\n]*\breview\b",
    "s4_acceptance_stage4_status": GZ + r"obpi acceptance\b[^;&|\n]*--stage stage4",
    "s5_precomplete": GZ + r"obpi precomplete\b" + NOHELP,
    "s5_complete": GZ + r"obpi complete\b" + NOHELP,
    "s5_git_sync": GZ + r"git-sync\b" + NOHELP,
}
S3 = ("s3_arb_ruff", "s3_arb_typecheck", "s3_arb_unittest", "s3_covers", "s3_arb_red")
S4 = (
    "s4_present_evidence",
    "s4_verify_packet",
    "s4_codex_companion",
    "s4_acceptance_review",
    "s4_acceptance_stage4_status",
)

# Bash families, first match wins, so a compound command is counted once.
BASH_FAMILIES: tuple[tuple[str, str], ...] = (
    ("gz arb", r"uv run gz arb\b"),
    ("gz obpi acceptance", r"uv run gz obpi acceptance\b"),
    ("gz obpi other", r"uv run gz obpi\b"),
    ("unittest", r"\bunittest(?:-parallel)?\b"),
    ("gz other", r"uv run gz\b"),
    ("git", r"(?:^|[;&|(\s])git\s"),
)


def load_rows(path: Path) -> list[dict]:
    """Return the parsed rows of a transcript, skipping lines that are not JSON."""
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def context_of(usage: dict) -> int:
    """Return the tokens the model read for one call."""
    return sum(usage.get(key) or 0 for key in CTX_KEYS)


def text_len(content: object) -> int:
    """Return the character count of a message content value."""
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        total = 0
        for block in content:
            if isinstance(block, dict):
                total += len(block.get("text") or "")
                if block.get("type") not in ("text", None) and "text" not in block:
                    total += len(json.dumps(block))
            else:
                total += len(str(block))
        return total
    return 0


def bash_family(command: str) -> str:
    """Return the first Bash family a command matches."""
    for name, pattern in BASH_FAMILIES:
        if re.search(pattern, command):
            return name
    if "/scratchpad" in command or "$S/" in command or "$S " in command:
        return "other: reads the run's own logs in the scratchpad"
    return "other: repo inspection (grep, sed, cat, python, gh)"


def rendered_len(row: dict) -> int | None:
    """Return the characters an attachment rendered into the prompt, None if none."""
    rendered = row.get("rendered")
    if rendered is None:
        rendered = row.get("renderedInHumanTurn")
    if not rendered:
        return None
    return sum(len(part.get("content") or "") for part in rendered if isinstance(part, dict))


def classify_attachment(row: dict, calls_seen: int) -> tuple[str, str]:
    """Return (category, sub-key) for an attachment row."""
    att = row["attachment"]
    kind = att.get("type") or "?"
    if kind == "nested_memory":
        path = att.get("path") or ""
        if "/.claude/rules/" in path:
            return "rule_injections", path.rsplit("/", 1)[-1]
        return "other_harness_reminders", "nested_memory:" + path.rsplit("/", 1)[-1]
    if kind.startswith("hook_"):
        return "hook_outputs", f"{kind}:{att.get('hookName')}"
    if kind == "queued_command":
        origin = (att.get("origin") or {}).get("kind")
        if origin in ("peer", "task-notification"):
            return "agent_results", f"queued {origin}"
        return "operator_prompts", "queued prompt"
    if calls_seen == 0:
        return "session_start_attachments", kind
    return "other_harness_reminders", kind


def analyze(path: Path) -> dict:
    """Return calls, user-side items and assistant output sizes for one transcript."""
    rows = load_rows(path)
    calls: dict[str, dict] = {}
    tool_uses: dict[str, dict] = {}
    items: list[dict] = []
    not_rendered: Counter[str] = Counter()
    pipeline_trigger_calls: list[int] = []
    pending_pipeline_trigger = False

    def add(category: str, sub: str, chars: int, stamp: str | None) -> None:
        items.append(
            {
                "enters_at_call": len(calls),  # read first by the next API call
                "timestamp": stamp,
                "category": category,
                "sub": sub,
                "chars": chars,
            }
        )

    for row in rows:
        kind = row.get("type")
        message = row.get("message") or {}
        stamp = row.get("timestamp")
        if kind == "assistant" and message.get("id") and message.get("usage"):
            mid = message["id"]
            call: dict[str, Any] | None = calls.get(mid)
            if call is None:
                call = calls[mid] = {
                    "index": len(calls),
                    "timestamp": stamp,
                    "model": message.get("model"),
                    "tools": [],
                    "markers": [],
                    "text_chars": 0,
                    "thinking_chars": 0,
                    "thinking_signature_chars": 0,
                    "tool_arg_chars": 0,
                    "tool_arg_chars_by_tool": {},
                }
                if pending_pipeline_trigger:
                    pipeline_trigger_calls.append(call["index"])
                    pending_pipeline_trigger = False
            call["usage"] = message["usage"]
            for block in message.get("content") or []:
                btype = block.get("type")
                if btype == "text":
                    call["text_chars"] += len(block.get("text") or "")
                elif btype == "thinking":
                    call["thinking_chars"] += len(block.get("thinking") or "")
                    call["thinking_signature_chars"] += len(block.get("signature") or "")
                elif btype == "tool_use":
                    args = block.get("input") or {}
                    arg_chars = len(json.dumps(args, ensure_ascii=False))
                    call["tool_arg_chars"] += arg_chars
                    name = block.get("name") or "?"
                    by_tool = call["tool_arg_chars_by_tool"]
                    by_tool[name] = by_tool.get(name, 0) + arg_chars
                    tool_uses[block["id"]] = {"name": name, "input": args, "call": call["index"]}
                    call["tools"].append(name)
                    if name == "Bash":
                        command = args.get("command") or ""
                        for marker, pattern in MARKERS.items():
                            if re.search(pattern, command) and marker not in call["markers"]:
                                call["markers"].append(marker)
                    elif name == "Agent":
                        call["markers"].append(f"agent_dispatch:{args.get('subagent_type')}")
                    elif name == "Skill":
                        call["markers"].append(f"skill:{args.get('skill')}")
                    elif name == "SendMessage":
                        call["markers"].append("send_message_to_subagent")
        elif kind == "user":
            content = message.get("content")
            origin = (row.get("origin") or {}).get("kind")
            if isinstance(content, str):
                if "<command-name>/gz-obpi-pipeline</command-name>" in content:
                    pending_pipeline_trigger = True
                if origin in ("peer", "task-notification") or "<task-notification>" in content:
                    add(
                        "agent_results",
                        f"user-row {origin or 'task-notification'}",
                        len(content),
                        stamp,
                    )
                elif content.startswith("Stop hook feedback"):
                    add("hook_outputs", "stop hook feedback (user row)", len(content), stamp)
                elif origin == "human":
                    add("operator_prompts", "prompt", len(content), stamp)
                else:
                    add("everything_else", "harness user row", len(content), stamp)
                continue
            for block in content or []:
                btype = block.get("type")
                if btype == "text":
                    text = block.get("text") or ""
                    found = re.match(r"Base directory for this skill: \S*/skills/(\S+)", text)
                    if found:
                        add("skill_bodies", found.group(1), len(text), stamp)
                    else:
                        add("everything_else", "user text block", len(text), stamp)
                elif btype == "tool_result":
                    use = tool_uses.get(block.get("tool_use_id")) or {"name": "?", "input": {}}
                    chars = text_len(block.get("content"))
                    name, args = use["name"], use["input"]
                    if name == "Skill":
                        add(
                            "skill_bodies", f"{args.get('skill')} (Skill tool result)", chars, stamp
                        )
                    elif name == "Read":
                        add("file_reads", args.get("file_path") or "?", chars, stamp)
                    elif name == "Bash":
                        add("bash_outputs", bash_family(args.get("command") or ""), chars, stamp)
                    elif name in ("Agent", "SendMessage"):
                        add("agent_results", f"{name} tool result", chars, stamp)
                    elif name in ("Edit", "Write"):
                        add("edit_write_results", name, chars, stamp)
                    else:
                        add("everything_else", f"{name} tool result", chars, stamp)
        elif kind == "attachment":
            category, sub = classify_attachment(row, len(calls))
            chars = rendered_len(row)
            if chars is None:
                not_rendered[f"{category}|{sub}"] += 1
                continue
            add(category, sub, chars, stamp)

    ordered = sorted(calls.values(), key=lambda c: c["index"])
    for call in ordered:
        usage = call.pop("usage")
        call["input_tokens"] = usage.get("input_tokens") or 0
        call["cache_read"] = usage.get("cache_read_input_tokens") or 0
        call["cache_creation"] = usage.get("cache_creation_input_tokens") or 0
        call["output_tokens"] = usage.get("output_tokens") or 0
        call["context"] = context_of(usage)
    return {
        "calls": ordered,
        "items": items,
        "not_rendered": dict(not_rendered),
        "pipeline_trigger_calls": pipeline_trigger_calls,
        "row_types": dict(Counter(r.get("type") or "?" for r in rows)),
    }


def totals(calls: list[dict]) -> dict:
    """Return the figures the evidence script reports, for comparison."""
    if not calls:
        return {"calls": 0}
    return {
        "calls": len(calls),
        "cache_read_input_tokens": sum(c["cache_read"] for c in calls),
        "cache_creation_input_tokens": sum(c["cache_creation"] for c in calls),
        "input_tokens": sum(c["input_tokens"] for c in calls),
        "output_tokens": sum(c["output_tokens"] for c in calls),
        "first_context": calls[0]["context"],
        "peak_context": max(c["context"] for c in calls),
        "peak_context_call": max(calls, key=lambda c: c["context"])["index"],
        "last_context": calls[-1]["context"],
        "context_decreases": sum(
            1 for a, b in zip(calls, calls[1:], strict=False) if b["context"] < a["context"]
        ),
        "calls_growing_less_than_previous_output": sum(
            1
            for a, b in zip(calls, calls[1:], strict=False)
            if b["context"] - a["context"] < a["output_tokens"]
        ),
        "models": dict(Counter(c["model"] for c in calls)),
        "cache_read_by_model": dict(_sum_by(calls, "model", "cache_read")),
    }


def _sum_by(calls: list[dict], key: str, field: str) -> Counter:
    out: Counter[str] = Counter()
    for call in calls:
        out[str(call[key])] += call[field]
    return out


def first_at(
    calls: list[dict], start: int, wanted: tuple[str, ...], end: int | None = None
) -> int | None:
    """Return the index of the first call at or after `start` carrying a wanted marker."""
    for call in calls[start:end]:
        if any(marker in call["markers"] for marker in wanted):
            return call["index"]
    return None


def boundaries(data: dict) -> list[dict]:
    """Locate stage boundaries from tool calls; every boundary is a call index.

    Rule: boundaries are found in order, each searched only after the one before
    it, and each is the FIRST call carrying one of the stage's markers. Later
    re-entries (review rounds, repeated baselines) stay in the segment they fall in
    and are listed under `marker_hits`.
    """
    calls = data["calls"]
    found: list[dict] = [{"name": "0 pre-pipeline work", "start": 0, "located_by": "session start"}]

    launch_candidates = list(data["pipeline_trigger_calls"])
    for call in calls:
        if "skill:gz-obpi-pipeline" in call["markers"] or "pipeline_launch" in call["markers"]:
            launch_candidates.append(call["index"])
    if not launch_candidates:
        return found
    launch = min(launch_candidates)
    how = (
        "first call after the /gz-obpi-pipeline skill load"
        if launch in data["pipeline_trigger_calls"]
        else "first `gz obpi pipeline` invocation or Skill load"
    )
    found.append(
        {"name": "1 pipeline launch to first dispatch", "start": launch, "located_by": how}
    )

    cursor = launch
    impl = first_at(calls, cursor, ("agent_dispatch:implementer",))
    if impl is not None:
        found.append(
            {
                "name": "2a implementation (implementer dispatched)",
                "start": impl,
                "located_by": "first Agent call with subagent_type=implementer",
            }
        )
        cursor = impl
    else:
        single = first_at(calls, cursor, ("single_driver_dispatch",))
        if single is not None:
            found.append(
                {
                    "name": "2a implementation (single driver, no Agent dispatch)",
                    "start": single,
                    "located_by": "`gz obpi dispatch --single-driver` declaration",
                }
            )
            cursor = single
    review = first_at(calls, cursor, ("reviewer_dispatch",))
    if review is not None:
        found.append(
            {
                "name": "2b review and fix cycles",
                "start": review,
                "located_by": "first `claude --agent spec-reviewer|quality-reviewer`",
            }
        )
        cursor = review
    stage3 = first_at(calls, cursor + 1, S3)
    if stage3 is not None:
        found.append(
            {
                "name": "3 verification baseline",
                "start": stage3,
                "located_by": "first of gz arb ruff/typecheck/step unittest, gz covers, gz arb red",
            }
        )
        cursor = stage3
    stage4 = first_at(calls, cursor + 1, S4)
    if stage4 is not None:
        found.append(
            {
                "name": "4 evidence and adversarial review",
                "start": stage4,
                "located_by": "first of present-evidence, verify-packet, codex-companion task, "
                "acceptance review, acceptance --stage stage4",
            }
        )
        cursor = stage4
    complete = first_at(calls, cursor + 1, ("s5_complete",))
    stage5, how5 = None, ""
    if complete is not None:
        stage5, how5 = complete, "first `gz obpi complete`"
        for call in calls[cursor + 1 : complete + 1]:
            if "s5_precomplete" in call["markers"]:
                stage5, how5 = (
                    call["index"],
                    "the `gz obpi precomplete` nearest before the first `gz obpi complete`",
                )
    else:
        sync = first_at(calls, cursor + 1, ("s5_git_sync",))
        if sync is not None:
            stage5, how5 = (
                sync,
                "first `gz git-sync` (no `gz obpi complete` was run in this session)",
            )
    if stage5 is not None:
        found.append({"name": "5 completion and sync", "start": stage5, "located_by": how5})
    return found


def segments(data: dict) -> list[dict]:
    """Return per-segment call counts, context at entry and exit, and cache-read."""
    calls = data["calls"]
    marks = boundaries(data)
    by_segment_category: dict[int, Counter] = defaultdict(Counter)
    starts = [m["start"] for m in marks]
    for item in data["items"]:
        index = min(item["enters_at_call"], len(calls) - 1)
        seg = max(i for i, start in enumerate(starts) if start <= index)
        by_segment_category[seg][item["category"]] += item["chars"]
    out: list[dict] = []
    for i, mark in enumerate(marks):
        end = marks[i + 1]["start"] if i + 1 < len(marks) else len(calls)
        chunk = calls[mark["start"] : end]
        if not chunk:
            continue
        entry, exit_ = chunk[0]["context"], chunk[-1]["context"]
        next_entry = calls[end]["context"] if end < len(calls) else None
        before = calls[mark["start"] - 1]["context"] if mark["start"] > 0 else None
        out.append(
            {
                "segment": mark["name"],
                "located_by": mark["located_by"],
                "first_call": chunk[0]["index"],
                "last_call": chunk[-1]["index"],
                "start_time": chunk[0]["timestamp"],
                "end_time": chunk[-1]["timestamp"],
                "calls": len(chunk),
                "context_at_entry": entry,
                "context_at_exit": exit_,
                "context_growth": exit_ - entry,
                "context_before_entry": before,
                "step_at_entry": entry - before if before is not None else None,
                "growth_including_entry_step": exit_ - (before if before is not None else entry),
                "context_at_next_entry": next_entry,
                "peak_context": max(c["context"] for c in chunk),
                "cache_read_tokens": sum(c["cache_read"] for c in chunk),
                "cache_creation_tokens": sum(c["cache_creation"] for c in chunk),
                "output_tokens": sum(c["output_tokens"] for c in chunk),
                "models": dict(Counter(c["model"] for c in chunk)),
                "est_tokens_arriving_by_category": {
                    k: round(v / CHARS_PER_TOKEN) for k, v in by_segment_category[i].most_common()
                },
            }
        )
    return out


def growth_sources(data: dict) -> dict:
    """Aggregate user-side content by category; tokens are chars/4 estimates."""
    items = data["items"]
    calls = data["calls"]
    by_cat: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    by_sub: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for item in items:
        by_cat[item["category"]][0] += 1
        by_cat[item["category"]][1] += item["chars"]
        slot = by_sub[item["category"]][item["sub"]]
        slot[0] += 1
        slot[1] += item["chars"]

    def table(category: str, top: int | None = None) -> list[dict]:
        rows = sorted(by_sub[category].items(), key=lambda kv: -kv[1][1])
        return [
            {"key": k, "count": v[0], "chars": v[1], "est_tokens": round(v[1] / CHARS_PER_TOKEN)}
            for k, v in rows[:top]
        ]

    after_first = sum(i["chars"] for i in items if i["enters_at_call"] > 0)
    before_first = sum(i["chars"] for i in items if i["enters_at_call"] == 0)
    out_tokens_before_last = sum(c["output_tokens"] for c in calls[:-1])
    measured_growth = calls[-1]["context"] - calls[0]["context"]
    assistant: dict[str, Any] = {
        "text_chars": sum(c["text_chars"] for c in calls),
        "thinking_text_chars": sum(c["thinking_chars"] for c in calls),
        "thinking_signature_chars": sum(c["thinking_signature_chars"] for c in calls),
        "tool_call_argument_chars": sum(c["tool_arg_chars"] for c in calls),
        "output_tokens_measured": sum(c["output_tokens"] for c in calls),
    }
    arg_by_tool: Counter[str] = Counter()
    for call in calls:
        arg_by_tool.update(call["tool_arg_chars_by_tool"])
    assistant["tool_call_argument_chars_by_tool"] = dict(arg_by_tool.most_common())
    assistant["visible_chars_total"] = (
        assistant["text_chars"]
        + assistant["thinking_text_chars"]
        + assistant["tool_call_argument_chars"]
    )
    assistant["visible_est_tokens"] = round(assistant["visible_chars_total"] / CHARS_PER_TOKEN)
    non_output_growth = measured_growth - out_tokens_before_last
    return {
        "categories": [
            {
                "category": k,
                "items": v[0],
                "chars": v[1],
                "est_tokens": round(v[1] / CHARS_PER_TOKEN),
            }
            for k, v in sorted(by_cat.items(), key=lambda kv: -kv[1][1])
        ],
        "skill_bodies": table("skill_bodies"),
        "file_reads_top20": table("file_reads", 20),
        "file_reads_repeated": [r for r in table("file_reads") if r["count"] > 1],
        "file_reads_distinct_files": len(by_sub["file_reads"]),
        "bash_outputs_by_family": table("bash_outputs"),
        "agent_results": table("agent_results"),
        "rule_injections": table("rule_injections"),
        "hook_outputs": table("hook_outputs"),
        "session_start_attachments": table("session_start_attachments"),
        "other_harness_reminders": table("other_harness_reminders"),
        "operator_prompts": table("operator_prompts"),
        "edit_write_results": table("edit_write_results"),
        "everything_else": table("everything_else"),
        "attachments_recorded_but_not_rendered": data["not_rendered"],
        "assistant_output": assistant,
        "calibration": {
            "note": "Checks the chars/4 estimate against the measured curve. Assumes every "
            "earlier assistant output (thinking included) stays in context.",
            "measured_context_growth_first_to_last_call": measured_growth,
            "measured_output_tokens_before_last_call": out_tokens_before_last,
            "implied_user_side_tokens": non_output_growth,
            "est_user_side_tokens_after_first_call": round(after_first / CHARS_PER_TOKEN),
            "implied_chars_per_token": round(after_first / non_output_growth, 2)
            if non_output_growth
            else None,
            "user_side_chars_before_first_call": before_first,
            "first_call_context_measured": calls[0]["context"],
        },
    }


def cache_events(calls: list[dict]) -> list[dict]:
    """Return calls where most of the context was rewritten to cache, not read."""
    out = []
    for prev, call in zip(calls, calls[1:], strict=False):
        if call["cache_read"] < 0.5 * prev["context"]:
            gap = (
                datetime.fromisoformat(call["timestamp"].replace("Z", "+00:00"))
                - datetime.fromisoformat(prev["timestamp"].replace("Z", "+00:00"))
            ).total_seconds()
            out.append(
                {
                    "call": call["index"],
                    "timestamp": call["timestamp"],
                    "context": call["context"],
                    "cache_read": call["cache_read"],
                    "cache_creation": call["cache_creation"],
                    "previous_model": prev["model"],
                    "model": call["model"],
                    "seconds_since_previous_call": round(gap),
                }
            )
    return out


def projection(
    calls: list[dict],
    segs: list[dict],
    fixed_load: int | None = None,
    fixed_read: int | None = None,
) -> dict:
    """Arithmetic, not measurement: reset context at each stage boundary.

    `fixed_load` is the context a fresh agent starts with (default: this session's
    first-call context); `fixed_read` is how much of it the first call after a reset
    reads from cache (default: what this session's first call read).
    """
    first_context = calls[0]["context"] if fixed_load is None else fixed_load
    first_read = calls[0]["cache_read"] if fixed_read is None else fixed_read
    base = first_context + SAVE_POINT_TOKENS
    rows = []
    for number, seg in enumerate(segs):
        chunk = calls[seg["first_call"] : seg["last_call"] + 1]
        entry = seg["context_at_entry"]
        reset = number > 0 and entry > base
        read = write = 0
        peak = 0
        for position, call in enumerate(chunk):
            if not reset:
                p_ctx, p_read = call["context"], call["cache_read"]
            else:
                p_ctx = call["context"] - entry + base
                if position == 0:
                    p_read = min(call["cache_read"], first_read)
                else:
                    # A hit keeps its offset above the dropped history; a miss
                    # (cache_read no larger than a cold call reads) stays a miss.
                    p_read = max(
                        min(call["cache_read"], first_read),
                        call["cache_read"] - (entry - base),
                    )
            p_write = max(0, p_ctx - p_read - call["input_tokens"])
            read += p_read
            write += p_write
            peak = max(peak, p_ctx)
        rows.append(
            {
                "segment": seg["segment"],
                "calls": len(chunk),
                "reset_applied": reset,
                "actual_cache_read": seg["cache_read_tokens"],
                "projected_cache_read": read,
                "actual_cache_creation": seg["cache_creation_tokens"],
                "projected_cache_creation": write,
                "actual_peak_context": seg["peak_context"],
                "projected_peak_context": peak,
            }
        )
    actual_read = sum(r["actual_cache_read"] for r in rows)
    projected_read = sum(r["projected_cache_read"] for r in rows)
    return {
        "label": "PROJECTION - arithmetic on the measured curve, not a measurement",
        "save_point_tokens": SAVE_POINT_TOKENS,
        "reset_context_tokens": base,
        "resets": sum(1 for r in rows if r["reset_applied"]),
        "segments": rows,
        "actual_cache_read": actual_read,
        "projected_cache_read": projected_read,
        "cache_read_reduction_pct": round(100 * (1 - projected_read / actual_read), 1),
        "actual_cache_creation": sum(r["actual_cache_creation"] for r in rows),
        "projected_cache_creation": sum(r["projected_cache_creation"] for r in rows),
        "projected_peak_context": max(r["projected_peak_context"] for r in rows),
        "assumptions": [
            "Same API calls, in the same order, with the same per-call output.",
            "Within a segment each call keeps its measured offset above the segment's entry "
            "context.",
            f"At each boundary the context becomes a fixed load ({first_context}) + a "
            f"{SAVE_POINT_TOKENS}-token save point = {base}; the pre-pipeline segment is not "
            "reset.",
            "The save point carries everything the next stage needs: no file is re-read, no skill "
            "is re-loaded, no extra call is spent writing or reading the save point.",
            f"The first call after a reset reads {first_read} tokens from cache; the rest of the "
            "reset context is a cache write.",
            "Later calls in a segment read from cache what they read in the run, less the dropped "
            "history. A call that missed the cache in the run still misses it.",
            "Model switches and idle gaps fall where they fell in the run.",
            "Subagent and reviewer sessions are unchanged and not included.",
        ],
    }


def subagent_loads(session_id: str) -> list[dict]:
    """Return first-call context and peak for each in-process subagent transcript."""
    folder = PROJECTS / session_id / "subagents"
    out = []
    for path in sorted(folder.glob("*.jsonl")):
        calls = analyze(path)["calls"]
        if not calls:
            continue
        meta_path = path.with_suffix("").with_suffix(".meta.json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        out.append(
            {
                "transcript": path.name,
                "agent_type": meta.get("agentType"),
                "description": meta.get("description"),
                "models": dict(Counter(c["model"] for c in calls)),
                "calls": len(calls),
                "first_call_context": calls[0]["context"],
                "first_call_cache_read": calls[0]["cache_read"],
                "first_call_cache_creation": calls[0]["cache_creation"],
                "peak_context": max(c["context"] for c in calls),
                "last_context": calls[-1]["context"],
                "cache_read_tokens": sum(c["cache_read"] for c in calls),
                "cache_creation_tokens": sum(c["cache_creation"] for c in calls),
                "output_tokens": sum(c["output_tokens"] for c in calls),
                "first_call_time": calls[0]["timestamp"],
                "last_call_time": calls[-1]["timestamp"],
            }
        )
    return out


def sibling_loads(session_id: str, window: tuple[str, str]) -> list[dict]:
    """Return first-call context and peak for sibling sessions (README heuristic).

    A sibling is a transcript whose every timestamped row falls inside the window.
    """
    start, end = (datetime.fromisoformat(v) for v in window)
    out = []
    for path in sorted(PROJECTS.glob("*.jsonl")):
        if path.stem == session_id:
            continue
        rows = load_rows(path)
        stamps = [
            datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00"))
            for r in rows
            if isinstance(r.get("timestamp"), str)
        ]
        if not stamps or not (start <= min(stamps) and max(stamps) <= end):
            continue
        calls = analyze(path)["calls"]
        if not calls:
            continue
        agent = next(
            (
                r.get("agentSetting") or r.get("agentName")
                for r in rows
                if r.get("agentSetting") or r.get("agentName")
            ),
            None,
        )
        out.append(
            {
                "transcript": path.name,
                "agent": agent,
                "models": dict(Counter(c["model"] for c in calls)),
                "calls": len(calls),
                "first_call_context": calls[0]["context"],
                "peak_context": max(c["context"] for c in calls),
                "cache_read_tokens": sum(c["cache_read"] for c in calls),
                "first_call_time": calls[0]["timestamp"],
            }
        )
    return out


def write_curve(name: str, data: dict, segs: list[dict]) -> Path:
    """Write the per-call context curve as CSV."""
    path = OUT_DIR / f"context_curve_{name}.csv"
    seg_of = {}
    for seg in segs:
        for index in range(seg["first_call"], seg["last_call"] + 1):
            seg_of[index] = seg["segment"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "call",
                "timestamp",
                "model",
                "context",
                "input_tokens",
                "cache_read",
                "cache_creation",
                "output_tokens",
                "segment",
                "tools",
                "markers",
            ]
        )
        for call in data["calls"]:
            writer.writerow(
                [
                    call["index"],
                    call["timestamp"],
                    call["model"],
                    call["context"],
                    call["input_tokens"],
                    call["cache_read"],
                    call["cache_creation"],
                    call["output_tokens"],
                    seg_of.get(call["index"], ""),
                    " ".join(call["tools"]),
                    " ".join(call["markers"]),
                ]
            )
    return path


def portable(text: str) -> str:
    """Strip the machine-local checkout and home prefixes from a recorded path."""
    local = text.replace(str(PROJECTS), "<transcripts>").replace(f"{Path.cwd()}/", "")
    return local.replace(str(Path.home()), "~")


def write_items(name: str, data: dict) -> Path:
    """Write every user-side item (sizes only, no content) as CSV."""
    path = OUT_DIR / f"context_inputs_{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["enters_at_call", "timestamp", "category", "sub", "chars", "est_tokens"])
        for item in data["items"]:
            writer.writerow(
                [
                    item["enters_at_call"],
                    item["timestamp"],
                    item["category"],
                    portable(str(item["sub"])),
                    item["chars"],
                    round(item["chars"] / CHARS_PER_TOKEN),
                ]
            )
    return path


def marker_hits(calls: list[dict]) -> dict[str, list[int]]:
    """Return every call index at which each marker was seen."""
    hits: dict[str, list[int]] = defaultdict(list)
    for call in calls:
        for marker in call["markers"]:
            hits[marker].append(call["index"])
    return dict(hits)


def main() -> None:
    """Analyze both sessions and write results.json and the CSV files."""
    results: dict = {
        "method": __doc__,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "sessions": {},
    }
    for name, session_id in SESSIONS.items():
        data = analyze(PROJECTS / f"{session_id}.jsonl")
        segs = segments(data)
        session = {
            "session_id": session_id,
            "totals": totals(data["calls"]),
            "boundaries": boundaries(data),
            "segments": segs,
            "marker_hits": marker_hits(data["calls"]),
            "cache_rewrite_events": cache_events(data["calls"]),
            "growth_sources": growth_sources(data),
            "context_curve": [
                {
                    "call": c["index"],
                    "timestamp": c["timestamp"],
                    "context": c["context"],
                    "output_tokens": c["output_tokens"],
                }
                for c in data["calls"]
            ],
            "projection": projection(data["calls"], segs),
            "files": {
                "curve_csv": str(write_curve(name, data, segs)),
                "inputs_csv": str(write_items(name, data)),
            },
        }
        results["sessions"][name] = session

    baseline_id = SESSIONS["baseline_OBPI-0.35.0-08"]
    base_totals = results["sessions"]["baseline_OBPI-0.35.0-08"]["totals"]
    subagents = subagent_loads(baseline_id)
    sub_totals = {
        "calls": sum(s["calls"] for s in subagents),
        "cache_read_input_tokens": sum(s["cache_read_tokens"] for s in subagents),
        "peak_context": max(s["peak_context"] for s in subagents),
    }
    results["sanity_check"] = {
        "orchestrator": {
            key: {"expected": want, "measured": base_totals[key], "match": base_totals[key] == want}
            for key, want in EXPECTED_BASELINE.items()
        },
        "in_process_subagents": {
            key: {"expected": want, "measured": sub_totals[key], "match": sub_totals[key] == want}
            for key, want in EXPECTED_BASELINE_SUBAGENTS.items()
        },
        "never_compacted": {
            "compaction_rows_found": sum(
                1
                for r in load_rows(PROJECTS / f"{baseline_id}.jsonl")
                if r.get("subtype") == "compact_boundary" or r.get("isCompactSummary")
            ),
            "context_decreases_between_calls": base_totals["context_decreases"],
        },
    }
    results["baseline_subagents"] = subagents
    base_session = results["sessions"]["baseline_OBPI-0.35.0-08"]
    base_calls = analyze(PROJECTS / f"{baseline_id}.jsonl")["calls"]
    lightest = min(s["first_call_context"] for s in subagents if s["agent_type"] == "implementer")
    sensitivity = projection(
        base_calls, base_session["segments"], fixed_load=lightest, fixed_read=0
    )
    sensitivity["label"] = (
        "PROJECTION, sensitivity - same arithmetic with the fixed load of a fresh in-process "
        "implementer subagent instead of the orchestrator's first-call context; assumes each "
        "stage could run in such an agent, which nothing here measures"
    )
    base_session["projection_sensitivity_subagent_load"] = sensitivity
    siblings = sibling_loads(baseline_id, BASELINE_SIBLING_WINDOW)
    results["baseline_sibling_sessions"] = {
        "window": BASELINE_SIBLING_WINDOW,
        "heuristic": "transcripts whose every timestamped row falls inside the window",
        "sessions": siblings,
    }
    sib_totals = {
        "files": len(siblings),
        "calls": sum(s["calls"] for s in siblings),
        "cache_read_input_tokens": sum(s["cache_read_tokens"] for s in siblings),
        "peak_context": max((s["peak_context"] for s in siblings), default=0),
    }
    results["sanity_check"]["sibling_reviewer_sessions"] = {
        key: {"expected": want, "measured": sib_totals[key], "match": sib_totals[key] == want}
        for key, want in EXPECTED_BASELINE_SIBLINGS.items()
    }
    out = OUT_DIR / "results.json"
    rendered = portable(json.dumps(results, indent=2, ensure_ascii=False))
    out.write_text(rendered + "\n", encoding="utf-8")
    print(json.dumps(results["sanity_check"], indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
