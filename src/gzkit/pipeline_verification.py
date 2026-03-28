"""REQ-level parallel verification dispatch models and orchestration.

Extracted from pipeline_runtime.py to keep module sizes under 600 lines.
All public symbols are re-exported from pipeline_runtime for backward compatibility.
"""

from __future__ import annotations

import json
import re
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# REQ-level parallel verification dispatch (OBPI-0.18.0-04)
# ---------------------------------------------------------------------------

MAX_VERIFICATION_FIX_CYCLES = 1

_BRIEF_REQ_RE = re.compile(r"^\d+\.\s+REQUIREMENT:\s*(.*)", re.IGNORECASE)


class VerificationScope(BaseModel):
    """A single requirement scoped for verification dispatch."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_index: int = Field(..., description="1-based requirement index")
    requirement_text: str = Field(..., description="Full requirement text")
    test_paths: list[str] = Field(default_factory=list, description="Test files to run")
    verification_commands: list[str] = Field(
        default_factory=list, description="Commands for verification"
    )
    pass_criteria: str = Field("All tests pass", description="Expected pass criteria")


class VerificationOutcome(StrEnum):
    """Outcome of a single REQ verification."""

    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class VerificationResult(BaseModel):
    """Result from a verification subagent for one or more REQs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_index: int = Field(..., description="1-based requirement index")
    outcome: VerificationOutcome = Field(..., description="Verification outcome")
    detail: str = Field("", description="Human-readable detail")
    commands_run: list[str] = Field(default_factory=list, description="Commands executed")


class VerificationPlan(BaseModel):
    """Dispatch plan for Stage 3 REQ-level verification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scopes: list[VerificationScope] = Field(
        default_factory=list, description="All verification scopes"
    )
    independent_groups: list[list[int]] = Field(
        default_factory=list,
        description="Groups of req_index values that can run in parallel",
    )
    strategy: str = Field("sequential", description="'parallel', 'sequential', or 'mixed'")


def extract_verification_scopes(
    brief_content: str,
    test_paths: list[str] | None = None,
) -> list[VerificationScope]:
    """Parse brief requirements into verification scopes.

    Each numbered ``REQUIREMENT:`` line becomes one scope. If explicit
    test_paths are provided, they are attached to every scope. Otherwise
    scopes have empty test_paths (caller must populate or fall back to
    sequential dispatch).
    """
    scopes: list[VerificationScope] = []
    req_index = 0
    for line in brief_content.splitlines():
        match = _BRIEF_REQ_RE.match(line.strip())
        if match:
            req_index += 1
            scopes.append(
                VerificationScope(
                    req_index=req_index,
                    requirement_text=match.group(1).strip(),
                    test_paths=list(test_paths or []),
                )
            )
    return scopes


def compute_path_overlap(scopes: list[VerificationScope]) -> dict[tuple[int, int], list[str]]:
    """Return overlapping test paths between each pair of scopes.

    Keys are ``(req_a, req_b)`` tuples (``a < b``). Values are the shared
    paths. An empty dict means no overlaps exist.
    """
    overlaps: dict[tuple[int, int], list[str]] = {}
    for i, scope_a in enumerate(scopes):
        set_a = set(scope_a.test_paths)
        for scope_b in scopes[i + 1 :]:
            shared = sorted(set_a & set(scope_b.test_paths))
            if shared:
                overlaps[(scope_a.req_index, scope_b.req_index)] = shared
    return overlaps


def partition_independent_groups(
    scopes: list[VerificationScope],
    overlaps: dict[tuple[int, int], list[str]],
) -> list[list[int]]:
    """Partition scopes into groups of non-overlapping requirements.

    Within each group, no two scopes share test paths -- they can be
    dispatched to parallel worktree-isolated subagents. Scopes that
    overlap are placed in the same group and verified sequentially within
    a single subagent.

    Uses a simple union-find to merge overlapping scopes into connected
    components.
    """
    if not scopes:
        return []

    parent: dict[int, int] = {s.req_index: s.req_index for s in scopes}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for req_a, req_b in overlaps:
        union(req_a, req_b)

    groups: dict[int, list[int]] = {}
    for s in scopes:
        root = find(s.req_index)
        groups.setdefault(root, []).append(s.req_index)

    return [sorted(members) for members in sorted(groups.values())]


def build_verification_plan(
    scopes: list[VerificationScope],
) -> VerificationPlan:
    """Create a dispatch plan from extracted verification scopes.

    - Zero scopes -> empty plan, sequential (baseline-only).
    - All scopes lack test_paths -> sequential fallback.
    - Otherwise -> compute overlaps and partition into groups.
    """
    if not scopes:
        return VerificationPlan(strategy="sequential")

    if all(len(s.test_paths) == 0 for s in scopes):
        return VerificationPlan(
            scopes=scopes,
            independent_groups=[[s.req_index for s in scopes]],
            strategy="sequential",
        )

    overlaps = compute_path_overlap(scopes)
    groups = partition_independent_groups(scopes, overlaps)

    if len(groups) <= 1:
        strategy = "sequential"
    elif all(len(g) == 1 for g in groups):
        strategy = "parallel"
    else:
        strategy = "mixed"

    return VerificationPlan(
        scopes=scopes,
        independent_groups=groups,
        strategy=strategy,
    )


def compose_verification_prompt(
    scopes: list[VerificationScope],
    *,
    group_label: str = "",
) -> str:
    """Build the prompt for a verification subagent.

    The subagent receives one or more REQs to verify, runs the specified
    test commands, and returns a JSON result block per REQ.
    """
    lines = [
        "## REQ Verification",
        "",
    ]
    if group_label:
        lines.append(f"**Group:** {group_label}")
        lines.append("")

    lines.append("### Requirements to Verify")
    lines.append("")
    for scope in scopes:
        lines.append(f"**REQ-{scope.req_index}:** {scope.requirement_text}")
        if scope.test_paths:
            lines.append(f"  Test files: {', '.join(f'`{p}`' for p in scope.test_paths)}")
        if scope.verification_commands:
            lines.append(f"  Commands: {', '.join(f'`{c}`' for c in scope.verification_commands)}")
        lines.append(f"  Pass criteria: {scope.pass_criteria}")
        lines.append("")

    lines.extend(
        [
            "### Instructions",
            "",
            "For each requirement above:",
            "1. Read the relevant source and test files.",
            "2. Run the specified test commands (or `uv run -m unittest -q` if none specified).",
            "3. Verify the implementation satisfies the requirement text.",
            "",
            "Return results as a JSON code block with this structure:",
            "",
            "```json",
            "[",
            "  {",
            '    "req_index": 1,',
            '    "outcome": "PASS|FAIL|ERROR",',
            '    "detail": "explanation",',
            '    "commands_run": ["uv run -m unittest ..."]',
            "  }",
            "]",
            "```",
            "",
            "You are read-only -- do NOT modify any files. Only read and run tests.",
            "",
        ]
    )
    return "\n".join(lines)


_VERIFICATION_JSON_RE = re.compile(r"```json\s*(\[.*?\])\s*```", re.DOTALL)


def parse_verification_results(agent_output: str) -> list[VerificationResult]:
    """Extract VerificationResult list from verification subagent output.

    Looks for a JSON code block containing an array of result objects.
    Returns an empty list if no valid result block is found.
    """
    match = _VERIFICATION_JSON_RE.search(agent_output)
    if not match:
        return []
    try:
        data = json.loads(match.group(1))
        if not isinstance(data, list):
            return []
        return [VerificationResult(**item) for item in data]
    except (json.JSONDecodeError, ValueError, KeyError):
        return []


def aggregate_verification_results(
    results: list[VerificationResult],
    expected_req_indices: list[int],
) -> tuple[bool, list[VerificationResult]]:
    """Aggregate results across all REQs.

    Returns ``(all_passed, failures)`` where ``all_passed`` is True only
    when every expected REQ has a PASS outcome. Missing REQs are treated
    as FAIL.
    """
    result_map = {r.req_index: r for r in results}
    failures: list[VerificationResult] = []

    for req_idx in expected_req_indices:
        result = result_map.get(req_idx)
        if result is None:
            failures.append(
                VerificationResult(
                    req_index=req_idx,
                    outcome=VerificationOutcome.FAIL,
                    detail="No result received from verification subagent",
                )
            )
        elif result.outcome != VerificationOutcome.PASS:
            failures.append(result)

    return len(failures) == 0, failures


def should_fallback_to_sequential(plan: VerificationPlan) -> bool:
    """Return True if the plan requires sequential fallback.

    Sequential fallback is required when:
    - Strategy is explicitly "sequential"
    - No scopes have test paths
    - All scopes are in a single group (no parallelism benefit)
    """
    return plan.strategy == "sequential"


# ---------------------------------------------------------------------------
# Stage 3 verification dispatch wiring (OBPI-0.18.0-08)
# ---------------------------------------------------------------------------


class VerificationTimingMetrics(BaseModel):
    """Wall-clock timing metrics for Stage 3 verification dispatch."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    strategy: str = Field(..., description="Dispatch strategy used")
    group_count: int = Field(..., description="Number of independent groups")
    elapsed_seconds: float = Field(..., description="Total wall-clock seconds")
    estimated_sequential_seconds: float = Field(
        0.0, description="Estimated sequential time for comparison"
    )
    time_saved_seconds: float = Field(0.0, description="Estimated time saved by parallelism")


def prepare_stage3_verification(
    brief_content: str,
    test_paths: list[str] | None = None,
) -> VerificationPlan:
    """Build a Stage 3 verification plan from brief content.

    Composes ``extract_verification_scopes`` and ``build_verification_plan``
    into a single call for Stage 3 orchestration. If no requirements are
    found, returns a sequential plan (baseline-only verification).
    """
    scopes = extract_verification_scopes(brief_content, test_paths)
    return build_verification_plan(scopes)


def compute_verification_timing(
    start_ns: int,
    end_ns: int,
    strategy: str,
    group_count: int,
    per_group_estimate_seconds: float = 30.0,
) -> VerificationTimingMetrics:
    """Compute wall-clock timing metrics for Stage 3 dispatch.

    ``start_ns`` and ``end_ns`` are monotonic nanosecond timestamps
    (from ``time.monotonic_ns()``).  ``per_group_estimate_seconds`` is
    the estimated sequential time per group for savings calculation.
    """
    elapsed = (end_ns - start_ns) / 1e9
    estimated_sequential = group_count * per_group_estimate_seconds
    saved = max(0.0, estimated_sequential - elapsed)
    return VerificationTimingMetrics(
        strategy=strategy,
        group_count=group_count,
        elapsed_seconds=round(elapsed, 2),
        estimated_sequential_seconds=round(estimated_sequential, 2),
        time_saved_seconds=round(saved, 2),
    )


def create_verification_dispatch_records(
    plan: VerificationPlan,
    results: list[VerificationResult],
) -> list[dict[str, Any]]:
    """Bridge Stage 3 verification results to dispatch tracking records.

    Maps each ``VerificationResult`` to a dispatch-compatible dict for
    persistence in the pipeline marker alongside Stage 2 dispatch records.
    """
    result_map = {r.req_index: r for r in results}
    records: list[dict[str, Any]] = []
    for scope in plan.scopes:
        result = result_map.get(scope.req_index)
        records.append(
            {
                "task_id": scope.req_index,
                "role": "Verifier",
                "model": "sonnet",
                "stage": 3,
                "requirement": scope.requirement_text,
                "status": result.outcome if result else "MISSING",
                "detail": result.detail if result else "No result received",
                "commands_run": list(result.commands_run) if result else [],
            }
        )
    return records
