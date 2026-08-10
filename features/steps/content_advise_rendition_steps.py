"""BDD steps for gz content advise-rendition — OBPI-0.0.37-24.

Reuses the globally-registered steps from content_compose_steps.py:
``the command exits 0``, ``the command exits non-zero``, and
``the ledger contains a "{event_type}" event for surface "{surface}"``. This
module defines only the advise-rendition-specific steps.

@covers REQ-0.0.37-24-01
@covers REQ-0.0.37-24-02
@covers REQ-0.0.37-24-03
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import then, when

from gzkit.cli import main


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


def _receipts() -> list[Path]:
    return sorted((Path(".") / "artifacts" / "receipts").glob("arb-step-judge-*.json"))


def _advise_args(surface: str, consumer: str, score: str, explanation: str) -> list[str]:
    return [
        "content",
        "advise-rendition",
        surface,
        "--consumer",
        consumer,
        "--score",
        score,
        "--explanation",
        explanation,
    ]


@when(
    'I run advise-rendition for "{surface}" consumer "{consumer}" '
    'score "{score}" explanation "{explanation}"'
)
def step_run_advise(context, surface, consumer, score, explanation) -> None:
    # The project-init step (shared with compose) created .gzkit/; the ledger
    # append target exists. Receipts land under cwd/artifacts/receipts.
    code, output = _invoke(_advise_args(surface, consumer, score, explanation))
    context.exit_code = code
    context.output = output


@when(
    'I run advise-rendition twice for "{surface}" consumer "{consumer}" '
    'score "{score}" explanation "{explanation}"'
)
def step_run_advise_twice(context, surface, consumer, score, explanation) -> None:
    args = _advise_args(surface, consumer, score, explanation)
    code1, _ = _invoke(args)
    code2, _ = _invoke(args)
    context.exit_code = code2
    context.first_exit_code = code1


@then("an advisor-QC receipt is written")
def step_receipt_written(_context) -> None:
    receipts = _receipts()
    assert receipts, "expected an arb-step-judge-*.json receipt but none was written"


@then("no advisor-QC receipt is written")
def step_no_receipt(_context) -> None:
    receipts = _receipts()
    assert not receipts, f"expected no receipt but found: {[p.name for p in receipts]}"


@then('the ledger has no "{event_type}" event')
def step_ledger_no_event(_context, event_type) -> None:
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    if not ledger_path.exists():
        return
    events = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matching = [e for e in events if e.get("event") == event_type]
    assert not matching, f"expected no {event_type!r} event but found {len(matching)}"


@then("both advise-rendition runs exit 0")
def step_both_advise_runs_exit_0(context) -> None:
    assert context.first_exit_code == 0, f"first run exit {context.first_exit_code}"
    assert context.exit_code == 0, f"second run exit {context.exit_code}"


@then("the two advisor-QC receipts are byte-identical")
def step_two_receipts_identical(_context) -> None:
    receipts = _receipts()
    assert len(receipts) == 2, f"expected exactly two receipts, got {len(receipts)}"
    # Each receipt carries a deliberately-unique run_id + timestamp_utc (the
    # unique-seam fields). Determinism is proven by the receipt body being
    # identical once those two seams are normalized out — nothing else varies
    # between runs (no LLM/network influence).
    bodies = []
    for path in receipts:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.pop("run_id", None)
        data.pop("timestamp_utc", None)
        bodies.append(json.dumps(data, sort_keys=True))
    assert bodies[0] == bodies[1], (
        f"receipt bodies differ once unique seams are removed:\n{bodies[0]}\n{bodies[1]}"
    )
