"""gz arb CLI — ARB (Agent Self-Reporting) middleware dispatcher.

Wraps QA commands (ruff, ty, unittest, coverage, etc.) and emits validated
JSON receipts for attestation evidence. See `AGENTS.md` § Attestation for the
binding rule contract, `docs/governance/arb-middleware.md` for the middleware
deep-dive, and `src/gzkit/arb/` for the implementation.

@covers REQ-0.25.0-33-01
@covers REQ-0.25.0-33-02
@covers REQ-0.25.0-33-03
@covers REQ-0.25.0-33-05
"""

from __future__ import annotations

import sys
from pathlib import Path

from gzkit.arb.advisor import collect_arb_advice, render_arb_advice_text
from gzkit.arb.patterns import collect_patterns, render_patterns_compact, render_patterns_markdown
from gzkit.arb.ruff_reporter import run_ruff_via_arb
from gzkit.arb.step_reporter import run_step_via_arb
from gzkit.arb.validator import (
    CANONICAL_STEP_COMMANDS,
    render_validation_text,
    validate_receipts,
)

_INTERNAL_ERROR = 2


def arb_ruff_cmd(
    *,
    paths: list[str] | None = None,
    fix: bool = False,
    quiet: bool = False,
    soft_fail: bool = False,
) -> int:
    """Run ruff via ARB and emit a lint receipt."""
    try:
        exit_status, _ = run_ruff_via_arb(
            paths=paths,
            fix=fix,
            quiet=quiet,
            soft_fail=soft_fail,
        )
    except OSError as exc:
        print(f"arb: internal error: {exc}", file=sys.stderr)
        return _INTERNAL_ERROR
    return exit_status


def arb_red_cmd(
    *,
    req: str,
    base: str | None = None,
    obpi: str | None = None,
    quiet: bool = False,
) -> int:
    """Witness a BEHAVIOR REQ's test failing against the base tree (GHI #642).

    Exit 0 means a RED was witnessed (``assertion`` or the weaker ``error``). Exit 1
    means the test PASSED with the production hunks withheld — it cannot fail, so it
    proves nothing, and that is the defect this command exists to surface.
    """
    from gzkit.arb.red_reporter import run_red_via_arb
    from gzkit.commands.common import get_project_root
    from gzkit.ledger import Ledger
    from gzkit.ledger_events import red_receipt_emitted_event
    from gzkit.red_witness import resolve_covering_test_names

    project_root = get_project_root()
    test_names = resolve_covering_test_names(project_root, req)
    if not test_names:
        print(
            f"arb red: no @covers test found for {req}. A BEHAVIOR REQ with no covering "
            "test is a coverage defect, not a falsifiability one — run `uv run gz covers` "
            "and author the covering test first.",
            file=sys.stderr,
        )
        return 1

    try:
        witness, receipt_path = run_red_via_arb(
            project_root=project_root,
            req_id=req,
            test_names=test_names,
            base_commit=base,
            obpi_id=obpi,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"arb red: cannot run base-tree witness: {exc}", file=sys.stderr)
        return _INTERNAL_ERROR

    Ledger(project_root / ".gzkit" / "ledger.jsonl").append(
        red_receipt_emitted_event(
            req_id=req,
            receipt_id=str(receipt_path.stem),
            failure_class=witness.failure_class,
            base_commit=witness.base_commit,
            base_provenance=witness.base_provenance,
            obpi_id=obpi,
            test_names=witness.test_names,
        )
    )

    if not quiet:
        print(
            f"arb red req={req} base={witness.base_commit[:12]} "
            f"failure_class={witness.failure_class} receipt={receipt_path}"
        )

    if witness.failure_class == "not-applicable":
        print(
            f"RED WITNESS DID NOT RUN: no production hunks were withheld against base "
            f"{witness.base_commit[:12]}, and no earlier tree could be reconstructed for "
            f"{req} — its `@covers` string is absent from the test tree's history, or the "
            "commit that introduced it has no parent. So the base tree already carries "
            f"{req}'s implementation and its covering test would pass there no matter what "
            "it asserts. This is NOT a finding about the test — do NOT rewrite it "
            "(GHI #839, #849).",
            file=sys.stderr,
        )
        return 0
    if not witness.is_conclusive:
        print(
            f"RED WITNESS INCONCLUSIVE: {req}'s test failed with an ERROR against the "
            f"RECONSTRUCTED base {witness.base_commit[:12]} (the parent of the commit that "
            "introduced the test). On that tree an error is as likely to be unrelated "
            "drift as the missing implementation, so it witnesses nothing either way — "
            "and counting it would let a hollow test in old code clear this gate. This is "
            "NOT a finding about the test. To get a real verdict, run the witness while "
            "the production change is still in the working tree (GHI #849).",
            file=sys.stderr,
        )
        return 0
    if witness.failure_class == "none":
        print(
            f"RED WITNESS FAILED: {req}'s covering test PASSED against base commit "
            f"{witness.base_commit[:12]} with the production hunks withheld. A test that "
            "passes without its implementation cannot fail when the business logic "
            "changes (AGENTS.md § DO IT RIGHT Rule 6), so it witnesses nothing. Rewrite "
            "the test to assert the REQ's semantics, then re-run `uv run gz arb red "
            f"--req {req}`.",
            file=sys.stderr,
        )
        return 1
    if witness.failure_class == "error" and not quiet:  # working-tree only: see above
        print(
            f"weak RED: {req}'s test failed with an error, not an assertion — it failed "
            "for the wrong reason (usually a not-yet-existing symbol). Recorded as "
            "failure_class=error; never equate this with an assertion RED.",
            file=sys.stderr,
        )
    return 0


def arb_step_cmd(
    *,
    name: str,
    argv: list[str],
    quiet: bool = False,
    soft_fail: bool = False,
) -> int:
    """Run an arbitrary command via ARB and emit a step receipt."""
    try:
        exit_status, _ = run_step_via_arb(
            name=name,
            cmd=argv,
            quiet=quiet,
            soft_fail=soft_fail,
        )
    except ValueError as exc:
        print(f"arb: invalid step invocation: {exc}", file=sys.stderr)
        return _INTERNAL_ERROR
    except OSError as exc:
        print(f"arb: internal error: {exc}", file=sys.stderr)
        return _INTERNAL_ERROR
    return exit_status


def arb_ty_cmd(*, argv: list[str], quiet: bool = False) -> int:
    """Run `uvx ty` via ARB step wrapper."""
    return arb_step_cmd(name="ty", argv=["uvx", "ty", *argv], quiet=quiet)


def arb_typecheck_cmd(*, quiet: bool = False) -> int:
    """Run the canonical ``gz typecheck`` command via ARB step wrapper.

    This is the Heavy-lane attestation receipt form for type checks: it wraps
    the exact command ``gz typecheck`` (and therefore ``gz closeout``) runs,
    so ARB receipts cannot claim "types clean" against a scope that diverges
    from the governance gate. See GHI #199.

    The argv is READ from ``CANONICAL_STEP_COMMANDS`` for the same reason
    ``quality.run_typecheck`` reads it: a third hand-spelled copy of the command
    is a third place the #199 divergence can re-enter.
    """
    return arb_step_cmd(
        name="typecheck", argv=list(CANONICAL_STEP_COMMANDS["typecheck"]), quiet=quiet
    )


def arb_coverage_cmd(*, argv: list[str], quiet: bool = False) -> int:
    """Run coverage via ARB step wrapper."""
    return arb_step_cmd(name="coverage", argv=["coverage", *argv], quiet=quiet)


def arb_validate_cmd(*, limit: int = 50, as_json: bool = False) -> int:
    """Validate recent ARB receipts against their JSON schemas."""
    try:
        result = validate_receipts(limit=limit)
    except OSError as exc:
        print(f"arb: internal error: {exc}", file=sys.stderr)
        return _INTERNAL_ERROR

    if as_json:
        sys.stdout.write(result.model_dump_json(indent=2) + "\n")
    else:
        sys.stdout.write(render_validation_text(result))

    return 1 if result.invalid > 0 else 0


def arb_advise_cmd(*, limit: int = 50, as_json: bool = False) -> int:
    """Summarize recent ARB receipts into actionable recommendations."""
    try:
        advice = collect_arb_advice(limit=limit)
    except OSError as exc:
        print(f"arb: internal error: {exc}", file=sys.stderr)
        return _INTERNAL_ERROR

    if as_json:
        sys.stdout.write(advice.model_dump_json(indent=2) + "\n")
    else:
        sys.stdout.write(render_arb_advice_text(advice))

    return 0


def arb_patterns_cmd(
    *,
    limit: int = 500,
    as_json: bool = False,
    compact: bool = False,
) -> int:
    """Extract recurring anti-patterns from ARB receipts."""
    try:
        report = collect_patterns(limit=limit)
    except OSError as exc:
        print(f"arb: internal error: {exc}", file=sys.stderr)
        return _INTERNAL_ERROR

    if as_json:
        sys.stdout.write(report.model_dump_json(indent=2) + "\n")
    elif compact:
        sys.stdout.write(render_patterns_compact(report))
    else:
        sys.stdout.write(render_patterns_markdown(report))

    return 0


def arb_archive_cmd(
    *,
    older_than: str = "30d",
    dry_run: bool = False,
    as_json: bool = False,
) -> int:
    """Relocate aged, uncited ARB receipts into artifacts/receipts/archive/."""
    from datetime import UTC, datetime

    from gzkit.arb.archive import execute_receipt_archive, plan_receipt_archive
    from gzkit.arb.paths import receipts_root
    from gzkit.cli.helpers.durations import parse_older_than_days

    older_than_days = parse_older_than_days(older_than)
    try:
        root = receipts_root()
        plan = plan_receipt_archive(
            root=root,
            base_path=Path.cwd(),
            older_than_days=older_than_days,
            now=datetime.now(UTC),
        )
        result = None if dry_run else execute_receipt_archive(plan, root=root)
    except OSError as exc:
        print(f"arb: internal error: {exc}", file=sys.stderr)
        return _INTERNAL_ERROR

    payload = result if result is not None else plan
    if as_json:
        sys.stdout.write(payload.model_dump_json(indent=2) + "\n")
        return 0

    header = "Receipt archive plan (dry-run)" if dry_run else "Receipt archive"
    lines = [
        header,
        f"  Root: {root}",
        f"  Older than: {older_than_days}d",
        f"  Eligible: {len(plan.eligible)}",
        f"  Skipped (cited in ledger): {len(plan.skipped_cited)}",
        f"  Skipped (newer than threshold): {len(plan.skipped_recent)}",
        f"  Skipped (undatable): {len(plan.skipped_undatable)}",
        f"  Skipped (name conflict in archive/): {len(plan.skipped_conflict)}",
        f"  Skipped (not ARB-emitted): {len(plan.skipped_foreign)}",
    ]
    if result is None:
        lines.append("  Use without --dry-run to relocate.")
    else:
        lines.append(f"  Moved: {len(result.moved)}")
        if result.skipped_conflict:
            lines.append(f"  Skipped at execution (race): {len(result.skipped_conflict)}")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


__all__ = [
    "arb_advise_cmd",
    "arb_archive_cmd",
    "arb_coverage_cmd",
    "arb_patterns_cmd",
    "arb_ruff_cmd",
    "arb_step_cmd",
    "arb_ty_cmd",
    "arb_typecheck_cmd",
    "arb_validate_cmd",
]
