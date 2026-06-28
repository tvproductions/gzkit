"""OBPI pipeline stage execution functions.

Extracted from obpi_cmd.py to stay under the 600-line module cap.
Covers: verification command parsing, pipeline output helpers, and
stage runners (verify, ceremony, sync).
"""

from __future__ import annotations

import json
import shlex
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from gzkit.brief_commands import extract_fenced_commands, is_shell_less_executable
from gzkit.commands.common import GzCliError, _cli_main, console
from gzkit.decomposition import extract_markdown_section
from gzkit.pipeline_runtime import (
    pipeline_command,
    pipeline_git_sync_command,
    refresh_pipeline_markers,
    remove_pipeline_artifacts,
)
from gzkit.quality import QualityResult

# Canonical ARB-wrapped baseline (GHI #317).
# The pipeline's Stage 3 verification must produce receipts at parity with the
# canonical attestation invocations enumerated in AGENTS.md § Attestation, so a
# green Stage 3 result entitles the agent to cite ARB receipt IDs in the
# Stage 4 evidence package without re-running the same checks under ARB.
BASELINE_VERIFICATION = [
    "uv run gz arb ruff",
    "uv run gz arb typecheck",
    "uv run gz arb step --name unittest -- uv run -m unittest -q",
]


# Canonical ARB gates that read disjoint surfaces and emit independent
# receipts (GHI #421). Consecutive parallel-safe commands in the Stage 3
# command list dispatch concurrently; non-matching commands run serially
# in input order to preserve any operator-supplied ordering intent.
_PARALLEL_SAFE_PREFIXES: tuple[str, ...] = (
    "uv run gz arb ruff",
    "uv run gz arb typecheck",
    "uv run gz arb step --name unittest",
    "uv run gz arb step --name mkdocs",
    "uv run gz arb step --name behave",
)


def _is_parallel_safe(command: str) -> bool:
    """Return True if ``command`` is a canonical ARB gate (GHI #421)."""
    return any(command.startswith(prefix) for prefix in _PARALLEL_SAFE_PREFIXES)


def _result_tuple(command: str, result: QualityResult) -> tuple[str, bool, str]:
    """Translate a ``QualityResult`` into the verify-stage result triple."""
    if result.success:
        return command, True, "pass"
    detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
    return command, False, detail


def _dispatch_verification_commands(
    commands: list[str],
    runner: Callable[[str], QualityResult],
) -> list[tuple[str, bool, str]]:
    """Dispatch verification commands, parallelizing canonical ARB gates.

    Consecutive parallel-safe commands run concurrently via a thread pool;
    the rest run serially in input order. Results return in input order
    regardless of completion order. Fail-closed: every command runs even
    when an earlier one fails (no early-exit).
    """
    results: list[tuple[str, bool, str]] = [("", False, "")] * len(commands)
    i = 0
    while i < len(commands):
        if not _is_parallel_safe(commands[i]):
            results[i] = _result_tuple(commands[i], runner(commands[i]))
            i += 1
            continue
        j = i
        while j < len(commands) and _is_parallel_safe(commands[j]):
            j += 1
        if j - i == 1:
            results[i] = _result_tuple(commands[i], runner(commands[i]))
        else:
            with ThreadPoolExecutor(max_workers=j - i) as executor:
                future_to_index = {executor.submit(runner, commands[k]): k for k in range(i, j)}
                for future, idx in future_to_index.items():
                    results[idx] = _result_tuple(commands[idx], future.result())
        i = j
    return results


def _pipeline_behave_command(behave_tags: list[str] | None) -> str | None:
    """Return the Stage 3 heavy-lane behave command, or None to skip.

    GHI #420 scope-discipline resolver:

    * ``behave_tags is None`` — caller has no OBPI scope context. Run
      the full ``features/`` sweep (backward-compat for non-pipeline
      invocations and lite-mode briefs without an OBPI identifier).
    * ``behave_tags == []`` — OBPI has no @REQ-tagged scenarios. Skip
      behave at Stage 3; the full sweep runs at ADR closeout.
    * ``behave_tags`` non-empty — scope the run to ``--tags=<csv>`` so
      cross-OBPI rot in unrelated feature files cannot block this OBPI.
    """
    if behave_tags is None:
        return "uv run gz arb step --name behave -- uv run -m behave features/"
    if not behave_tags:
        return None
    tag_arg = ",".join(behave_tags)
    return f"uv run gz arb step --name behave -- uv run -m behave --tags={tag_arg} features/"


def _pipeline_verification_commands(
    obpi_content: str,
    lane: str,
    obpi_id: str | None = None,
    behave_tags: list[str] | None = None,
) -> list[str]:
    """Parse the Verification block into executable shell commands.

    When ``obpi_id`` is provided, ``gz obpi precomplete`` is appended so
    brief-shape audits (behave_req_tags, brief_headings) fire at Stage 3
    BEFORE ``gz obpi complete`` mutates the brief — see GHI #422.

    When ``behave_tags`` is provided (heavy lane, OBPI-scoped pipeline
    invocation), the Stage 3 behave run is scoped to those ``@REQ-...``
    tags so cross-OBPI feature-file rot does not block this OBPI — see
    GHI #420 and ``gz-obpi-pipeline`` SKILL.md § Phase 1 (Scope discipline).
    A non-``None`` empty list means the OBPI has no @REQ-tagged scenarios;
    behave is skipped at Stage 3 in that case (the full ``features/``
    sweep runs at ADR closeout).
    """
    commands: list[str] = list(BASELINE_VERIFICATION)
    section = extract_markdown_section(obpi_content, "Verification") or ""
    # Reuse the shared BI-1 joiner so multi-line constructs (python -c "…"
    # spanning lines) are one logical command, not split per physical line —
    # the same extractor the demo path uses, not a fork (ADR-0.0.63 BI-1, #569).
    for line in extract_fenced_commands(section):
        if not line or line.startswith("#") or line == "command --to --verify":
            continue
        if not is_shell_less_executable(line):
            console.print(
                f"[red]BLOCKED[/red] Non-shell-less Verification command: {line!r}. "
                "Rewrite as separate single-program lines "
                "(no &&, ||, |, ;, $(...), or redirects)."
            )
            raise SystemExit(1)
        commands.append(line)
    if lane == "heavy":
        commands.append("uv run gz arb step --name mkdocs -- uv run mkdocs build --strict")
        behave_cmd = _pipeline_behave_command(behave_tags)
        if behave_cmd is not None:
            commands.append(behave_cmd)
    if obpi_id:
        commands.append(f"uv run gz obpi precomplete {obpi_id}")

    deduped: list[str] = []
    seen: set[str] = set()
    for command in commands:
        if command in seen:
            continue
        seen.add(command)
        deduped.append(command)
    return deduped


# ---------------------------------------------------------------------------
# Pipeline output helpers
# ---------------------------------------------------------------------------


def _print_pipeline_blockers(obpi_id: str, blockers: list[str]) -> None:
    """Render standard pipeline blocker output for one OBPI."""
    console.print(f"[bold]OBPI pipeline:[/bold] {obpi_id}")
    console.print("BLOCKERS:")
    for blocker in blockers:
        console.print(f"- {blocker}")


def _print_pipeline_header(
    *,
    obpi_id: str,
    resolved_parent: str,
    obpi_file: Path,
    project_root: Path,
    lane: str,
    start_from: str | None,
    receipt_state: str,
    stage_labels: list[str],
    per_obpi_marker: Path,
    legacy_marker: Path,
    warnings: list[str],
    receipt: dict[str, Any] | None,
) -> None:
    """Render the shared pipeline header."""
    console.print(f"[bold]OBPI pipeline:[/bold] {obpi_id}")
    console.print(f"  Parent ADR: {resolved_parent}")
    console.print(f"  Brief: {obpi_file.relative_to(project_root).as_posix()}")
    console.print(f"  Lane: {lane}")
    console.print(f"  Entry: {start_from or 'full'}")
    console.print(f"  Receipt: {receipt_state.upper()}")
    console.print("  Stages: " + " -> ".join(stage_labels))
    console.print(f"  Marker: {per_obpi_marker.relative_to(project_root).as_posix()}")
    console.print(f"  Legacy Marker: {legacy_marker.relative_to(project_root).as_posix()}")
    if receipt and receipt.get("plan_file"):
        console.print(f"  Plan File: {receipt['plan_file']}")
    for warning in warnings:
        console.print(f"  Warning: {warning}")


def _print_pipeline_implementation_next_steps(obpi_id: str) -> None:
    """Render Stage 2 guidance after a full launch."""
    console.print("")
    console.print("Next:")
    console.print("- Implement the approved OBPI within the brief allowlist.")
    console.print(f"- When implementation is ready, run: {pipeline_command(obpi_id, 'verify')}")
    console.print("- Keep the active pipeline markers in place during implementation.")


# ---------------------------------------------------------------------------
# Stage runners
# ---------------------------------------------------------------------------


def _run_pipeline_verify_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    obpi_content: str,
    lane: str,
    resolved_parent: str,
    requires_human_attestation: bool,
    attestor: str | None,
    evidence_json: str | None,
) -> None:
    """Run the verify stage, then chain into ceremony and sync."""
    behave_tags: list[str] | None = None
    if lane == "heavy":
        from gzkit.commands.quality import resolve_obpi_behave_tags  # noqa: PLC0415

        behave_tags = resolve_obpi_behave_tags(project_root, obpi_id)
    commands = _pipeline_verification_commands(
        obpi_content, lane, obpi_id=obpi_id, behave_tags=behave_tags
    )
    console.print("")
    console.print("[bold]Stage 3: Verification[/bold]")

    def _runner(command: str) -> QualityResult:
        return _cli_main().run_command(command, cwd=project_root)

    verification_results = _dispatch_verification_commands(commands, _runner)
    failures: list[tuple[str, str]] = []
    for command, passed, detail in verification_results:
        if passed:
            console.print(f"[green]PASS[/green] {command}")
        else:
            failures.append((command, detail))
            console.print(f"[red]FAIL[/red] {command}")
    if failures:
        refresh_pipeline_markers(
            plans_dir,
            obpi_id,
            blockers=[f"{command}: {detail}" for command, detail in failures],
        )
        console.print("BLOCKERS:")
        for command, detail in failures:
            console.print(f"- {command}: {detail}")
        raise SystemExit(1)

    console.print("")
    console.print("Verification passed. Chaining into ceremony.")

    _run_pipeline_ceremony_stage(
        project_root=project_root,
        plans_dir=plans_dir,
        obpi_id=obpi_id,
        obpi_content=obpi_content,
        resolved_parent=resolved_parent,
        requires_human_attestation=requires_human_attestation,
        attestor=attestor,
        evidence_json=evidence_json,
        verification_results=verification_results,
    )


def _run_pipeline_ceremony_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    obpi_content: str,
    resolved_parent: str,
    requires_human_attestation: bool,
    attestor: str | None,
    evidence_json: str | None,
    verification_results: list[tuple[str, bool, str]] | None = None,
) -> None:
    """Render evidence and either pause for human gate or self-close and chain into sync."""
    console.print("")
    console.print("[bold]Stage 4: Ceremony[/bold]")

    if verification_results:
        console.print("")
        console.print("Verification evidence:")
        for command, passed, detail in verification_results:
            tag = "[green]PASS[/green]" if passed else f"[red]FAIL[/red] {detail}"
            console.print(f"  {command}: {tag}")

    if requires_human_attestation:
        console.print("")
        console.print("[bold]Human attestation required.[/bold]")
        console.print("Present verification evidence to the human for attestation.")
        console.print("After receiving attestation, complete the pipeline with:")
        console.print(
            f"  uv run gz obpi pipeline {obpi_id} --from=sync "
            "--attestor <name> --evidence-json '<json>'"
        )
        console.print("")
        console.print(
            "The --evidence-json MUST include: attestation_text (required by "
            "gz obpi complete). Recommended: value_narrative, key_proof, "
            "implementation_summary, attestation_date. For uncovered REQs "
            "add accept_uncovered (list) + accept_uncovered_reason (list, 1:1)."
        )
        return

    console.print("Human attestation not required. Self-closing and chaining into sync.")

    effective_attestor = attestor or "agent:pipeline-autoclose"
    effective_evidence = evidence_json
    if not effective_evidence:
        objective = extract_markdown_section(obpi_content, "Objective") or obpi_id
        passed_commands = [cmd for cmd, passed, _ in (verification_results or []) if passed]
        key_proof = "All verification checks passed: " + ", ".join(passed_commands)
        # GHI #435: auto-close path also flows through `gz obpi complete` and
        # so must include `attestation_text` (required by the inner CLI).
        auto_evidence = {
            "value_narrative": objective.strip()[:500],
            "key_proof": key_proof[:500],
            "attestation_text": (
                f"Pipeline auto-close after Stage 3 verification of {obpi_id}: " + key_proof
            )[:500],
        }
        effective_evidence = json.dumps(auto_evidence)

    _run_pipeline_sync_stage(
        project_root=project_root,
        plans_dir=plans_dir,
        obpi_id=obpi_id,
        resolved_parent=resolved_parent,
        attestor=effective_attestor,
        evidence_json=effective_evidence,
    )


def _evidence_json_to_complete_flags(evidence_json: str) -> list[str]:
    """Translate a Stage-5 evidence-json payload into ``gz obpi complete`` flags.

    GHI #435: ``gz obpi complete`` accepts ``--attestation-text`` /
    ``--implementation-summary`` / ``--key-proof`` / ``--accept-uncovered`` /
    ``--accept-uncovered-reason`` as discrete flags — not the ``--evidence-json``
    blob the pipeline parser exposes. The pipeline must do the translation at
    its boundary so an evidence-json payload that lacks the required fields
    fails fast with a message that names the payload (option B remediation),
    instead of letting the inner CLI die on a generic
    ``the following arguments are required: --attestation-text`` that doesn't
    name the user-facing flag at all.
    """
    try:
        payload = json.loads(evidence_json)
    except json.JSONDecodeError as exc:
        msg = f"--evidence-json is not valid JSON: {exc}"
        raise GzCliError(msg) from exc  # noqa: TRY003

    if not isinstance(payload, dict):
        msg = "--evidence-json must decode to a JSON object"
        raise GzCliError(msg)  # noqa: TRY003

    attestation_text = payload.get("attestation_text")
    if not isinstance(attestation_text, str) or not attestation_text.strip():
        msg = (
            "--evidence-json must include a non-empty 'attestation_text' field "
            "(required by gz obpi complete --attestation-text)."
        )
        raise GzCliError(msg)  # noqa: TRY003

    flags: list[str] = ["--attestation-text", shlex.quote(attestation_text)]

    implementation_summary = payload.get("implementation_summary")
    if isinstance(implementation_summary, str) and implementation_summary.strip():
        flags.extend(["--implementation-summary", shlex.quote(implementation_summary)])

    key_proof = payload.get("key_proof")
    if isinstance(key_proof, str) and key_proof.strip():
        flags.extend(["--key-proof", shlex.quote(key_proof)])

    accept_uncovered = payload.get("accept_uncovered") or []
    accept_reasons = payload.get("accept_uncovered_reason") or []
    if not isinstance(accept_uncovered, list) or not isinstance(accept_reasons, list):
        msg = (
            "--evidence-json 'accept_uncovered' and 'accept_uncovered_reason' must be JSON arrays."
        )
        raise GzCliError(msg)  # noqa: TRY003
    if len(accept_uncovered) != len(accept_reasons):
        msg = (
            "--evidence-json 'accept_uncovered' and 'accept_uncovered_reason' "
            f"counts must match ({len(accept_uncovered)} vs {len(accept_reasons)})."
        )
        raise GzCliError(msg)  # noqa: TRY003
    for req_id, reason in zip(accept_uncovered, accept_reasons, strict=True):
        if not isinstance(req_id, str) or not isinstance(reason, str):
            msg = (
                "--evidence-json 'accept_uncovered' and 'accept_uncovered_reason' "
                "entries must be strings."
            )
            raise GzCliError(msg)  # noqa: TRY003
        flags.extend(
            [
                "--accept-uncovered",
                shlex.quote(req_id),
                "--accept-uncovered-reason",
                shlex.quote(reason),
            ]
        )

    return flags


def _build_sync_stage_steps(
    *,
    obpi_id: str,
    resolved_parent: str,
    attestor: str,
    evidence_json: str,
) -> list[tuple[str, str]]:
    """Return the ``(command, label)`` list executed at Stage 5.

    GHI #422 fix #1: ``gz obpi complete`` runs first to mutate the brief and
    write the completion receipt atomically (the previous runtime jumped
    straight to ``git-sync``, leaving the brief stuck in ``pending`` and the
    operator running ``complete`` manually after the fact).

    GHI #422 fix #3: ``--attestor-present`` is passed automatically because
    Stage 5 runs only when the active pipeline marker exists — the runtime IS
    the active session and has already enforced the attestation gate at
    Stage 4.

    GHI #36 anchor cleanness is preserved: ``gz obpi complete`` captures the
    parent ADR anchor (clean — the parent ADR isn't being mutated). The
    standalone ``gz obpi emit-receipt`` step that previously ran after sync is
    removed because ``complete`` emits the same ``obpi_receipt_emitted_event``
    internally; keeping both produced duplicate ledger events.

    GHI #435: the pipeline's ``--evidence-json`` payload is translated into the
    discrete flags ``gz obpi complete`` actually consumes. A missing
    ``attestation_text`` (or a malformed payload) fails closed at this boundary
    with a message that names ``--evidence-json``, rather than at the inner CLI
    with a flag the agent's command line never mentioned.
    """
    complete_flags = _evidence_json_to_complete_flags(evidence_json)
    complete_cmd = " ".join(
        [
            f"uv run gz obpi complete {obpi_id}",
            "--attestor-present",
            "--attestor",
            shlex.quote(attestor),
            *complete_flags,
        ]
    )
    return [
        (complete_cmd, "Complete OBPI atomically"),
        (pipeline_git_sync_command(), "Guarded repository sync"),
        (f"uv run gz obpi reconcile {obpi_id}", "Reconcile OBPI"),
        (f"uv run gz adr status {resolved_parent} --json", "Refresh parent ADR view"),
    ]


def _run_pipeline_sync_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    resolved_parent: str,
    attestor: str,
    evidence_json: str,
) -> None:
    """Run Stage 5: sync and account deterministically, then clear markers."""
    console.print("")
    console.print("[bold]Stage 5: Sync And Account[/bold]")

    steps = _build_sync_stage_steps(
        obpi_id=obpi_id,
        resolved_parent=resolved_parent,
        attestor=attestor,
        evidence_json=evidence_json,
    )

    for command, label in steps:
        console.print(f"  {label}...")
        result = _cli_main().run_command(command, cwd=project_root)
        if result.success:
            console.print(f"  [green]PASS[/green] {label}")
        else:
            detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
            console.print(f"  [red]FAIL[/red] {label}")
            if detail:
                for line in detail.splitlines()[:10]:
                    console.print(f"    {line}")
            console.print(f"Stage 5 failed at: {label}")
            raise SystemExit(1)

    # Lightweight accounting commit — ledger + frontmatter only, no lint/test.
    # Failure is non-fatal: the receipt is sealed and implementation is synced.
    accounting_steps: list[tuple[str, str]] = [
        ("git add -A", "Stage accounting changes"),
        (
            f'git commit -m "chore: record {obpi_id} completion receipt (gz pipeline)"',
            "Commit accounting changes",
        ),
        ("git push", "Push accounting changes"),
    ]
    for command, label in accounting_steps:
        result = _cli_main().run_command(command, cwd=project_root)
        if result.success:
            console.print(f"  [green]PASS[/green] {label}")
        else:
            detail = (result.stderr or result.stdout or "").strip()
            console.print(f"  [yellow]WARN[/yellow] {label}: {detail[:200]}")

    remove_pipeline_artifacts(plans_dir, obpi_id)
    console.print("")
    console.print(
        f"Pipeline complete. {obpi_id} synced. The work lock was surrendered "
        f"mechanically at completion (register-entry handoff written, lock "
        f"released); no manual 'gz obpi lock release' is required (GHI #619)."
    )
