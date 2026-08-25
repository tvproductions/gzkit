"""BDD steps for gz content retire — OBPI-0.35.0-02 corpus attestation.

CLI invocation, exit-code, output, and ledger-event assertions reuse the shared steps
in ``gz_steps.py``. Local steps exist only where the shared ones cannot express the
scenario:

- the seeded entry's id is minted at runtime, so a literal command string cannot name it;
- ``shlex.split`` collapses a whitespace-only ``--attestor``, which is the exact value
  one scenario needs to send.

@covers REQ-0.35.0-02-01
@covers REQ-0.35.0-02-02
@covers REQ-0.35.0-02-03
@covers REQ-0.35.0-02-04
@covers REQ-0.35.0-02-05
@covers REQ-0.35.0-02-07
"""

from __future__ import annotations

import io
import json
import re
import shlex
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when

from gzkit.cli.main import main
from gzkit.content.models import Corpus
from gzkit.content.models.corpus import effective_corpus


def _invoke(args: list[str]) -> tuple[int, str]:
    """In-process CLI driver (mirrors gz_steps.py:_invoke).

    Behave exec()s step files without package semantics, so a relative import of
    the shared helper fails at load time; every other step module that needs a
    driver defines its own for the same reason.
    """
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


_CORPUS = Path(".gzkit") / "corpus" / "AGENTS.md.jsonl"


def _load() -> Corpus:
    return Corpus.loads(_CORPUS.read_text(encoding="utf-8"))


@given('a corpus entry "{text}" at tier "{tier}"')
def step_seed_entry(context, text: str, tier: str) -> None:
    code, output = _invoke(
        [
            "content",
            "remember",
            "AGENTS.md",
            "--section",
            "Prime Directive",
            "--text",
            text,
            "--tier",
            tier,
        ]
    )
    assert code == 0, output
    entry = _load().entries[-1]
    context.seeded_entry_id = entry.id
    context.seeded_entry_text = entry.text
    context.corpus_before = _CORPUS.read_bytes()
    context.rows_before = len(_load().entries)


@when('I retire the seeded entry with args "{args}"')
def step_retire_with_args(context, args: str) -> None:
    argv = ["content", "retire", "AGENTS.md", "--entry", context.seeded_entry_id]
    context.exit_code, context.output = _invoke(argv + shlex.split(args))


@when("I retire the seeded entry with a whitespace-only attestor")
def step_retire_whitespace_attestor(context) -> None:
    # Passed as an argv element rather than through a parsed command string: the
    # shared step's shlex.split would collapse the spaces this scenario is about.
    context.exit_code, context.output = _invoke(
        [
            "content",
            "retire",
            "AGENTS.md",
            "--entry",
            context.seeded_entry_id,
            "--reason",
            "superseded",
            "--attestor",
            "   ",
        ]
    )


@then('the corpus for "{surface}" is byte-unchanged')
def step_corpus_unchanged(context, surface: str) -> None:
    assert _CORPUS.read_bytes() == context.corpus_before, (
        f"corpus for {surface} changed on a refusal: {context.output}"
    )


@then('the corpus for "{surface}" grew by exactly {n:d} row')
def step_corpus_grew(context, surface: str, n: int) -> None:
    after = len(_load().entries)
    assert after == context.rows_before + n, (
        f"{surface}: expected {context.rows_before + n} rows, found {after}"
    )


@then("the retired entry is still present verbatim in the raw corpus log")
def step_retired_row_survives(context) -> None:
    raw = _load()
    match = [e for e in raw.entries if e.id == context.seeded_entry_id]
    assert match, "the retired row vanished from the raw log — retirement must never delete"
    assert match[0].text == context.seeded_entry_text, "the retired row's text was altered"


@then("the retired entry is absent from the effective corpus")
def step_retired_row_folded(context) -> None:
    live = {e.id for e in effective_corpus(_load()).entries}
    assert context.seeded_entry_id not in live, (
        "the retired entry is still live in the effective corpus"
    )


@then('no ledger event "{event}" was emitted')
def step_no_ledger_event(_context, event: str) -> None:
    path = Path(".gzkit") / "ledger.jsonl"
    if not path.exists():
        return
    rows = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    assert not [r for r in rows if r.get("event") == event], (
        f"a {event} event was written on a path that must write nothing"
    )


@then("every gz command named in the recovery prose actually runs")
def step_recovery_commands_run(context) -> None:
    """A recommended command must RUN, not merely appear.

    A substring assertion passes for any string, including a verb that does not
    exist — which is how `gz content list <surface>` shipped in this prose once.
    Placeholder operands are substituted rather than stripped, so the whole command
    is parsed; a dummy value may fail at runtime, which is fine — this asserts the
    command's SHAPE.
    """
    commands = re.findall(r"`(gz [^`]+)`", context.output)
    assert commands, f"recovery prose named no runnable command: {context.output}"
    for cmd in commands:
        argv = ["_probe_" if a.startswith("<") else a for a in shlex.split(cmd)[1:]]
        _, out = _invoke(argv)
        assert "unrecognized arguments" not in out, f"does not parse: {cmd}"
        assert "invalid choice" not in out, f"unregistered verb: {cmd}"
