"""gz arb CLI — ARB (Agent Self-Reporting) middleware dispatcher.

Wraps QA commands (ruff, ty, unittest, coverage, etc.) and emits validated
JSON receipts for attestation evidence. See `.gzkit/rules/arb.md` for the
rule contract and `src/gzkit/arb/` for the implementation.

@covers REQ-0.25.0-33-01
@covers REQ-0.25.0-33-02
@covers REQ-0.25.0-33-03
@covers REQ-0.25.0-33-05
"""

from __future__ import annotations

import sys

from gzkit.arb.advisor import collect_arb_advice, render_arb_advice_text
from gzkit.arb.patterns import collect_patterns, render_patterns_compact, render_patterns_markdown
from gzkit.arb.ruff_reporter import run_ruff_via_arb
from gzkit.arb.step_reporter import run_step_via_arb
from gzkit.arb.validator import render_validation_text, validate_receipts

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
    """
    return arb_step_cmd(name="typecheck", argv=["uv", "run", "ty", "check", "src"], quiet=quiet)


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


__all__ = [
    "arb_advise_cmd",
    "arb_coverage_cmd",
    "arb_patterns_cmd",
    "arb_ruff_cmd",
    "arb_step_cmd",
    "arb_ty_cmd",
    "arb_typecheck_cmd",
    "arb_validate_cmd",
]
