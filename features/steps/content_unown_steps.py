"""BDD steps for gz content unown -- attested ratchet-raise path (OBPI-0.35.0-04 Task 4).

Un-owning a section is the ONE move that raises the decrease-only unowned-byte
ratchet (`gzkit.content.ownership.record_unowned_total` refuses every other
attempt). Same corpus-attestation shape as `gz content retire`, with one
deliberate difference: un-owning a section is a canon change EVERY time, so
`--attestor`/`--reason` are unconditionally required (REQ-0.35.0-04-04),
never conditional on what moved. A successful raise flips the named section
to `unowned`, raises the floor by exactly that section's measured byte span,
and emits one `section_ownership_unowned` ledger event (REQ-0.35.0-04-05).

The REQ-04 scenarios' `no ledger event "..." was emitted` step is NOT defined
in this module -- it lives in `features/steps/content_retire_steps.py` and is
reached here through behave's global step registry (tracked debt; see this
OBPI brief's `## Tracked Defects`).

@covers REQ-0.35.0-04-04
@covers REQ-0.35.0-04-05
"""

from __future__ import annotations

import io
import json
import shlex
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when

from gzkit.cli.main import main
from gzkit.content.ownership import measure_section_spans, sections_digest
from gzkit.governance.events import emit_section_ownership_genesis

_SURFACE_TEXT = (
    "# Doc Title\n"
    "preamble text under the H1\n"
    "## Alpha Section\n"
    "alpha body line one\n"
    "alpha body line two\n"
    "## Beta Section\n"
    "beta body\n"
)


def _invoke(args: list[str]) -> tuple[int, str]:
    """In-process CLI driver (mirrors content_retire_steps.py:_invoke).

    Behave exec()s step files without package semantics, so a relative import of
    the shared helper fails at load time; every step module that needs a driver
    defines its own for the same reason.
    """
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


def _declaration_path(surface: str) -> Path:
    return Path(".gzkit") / "ownership" / f"{surface}.json"


@given('a control surface "{surface}" with an ownership declaration')
def step_seed_surface_and_declaration(context, surface: str) -> None:
    """Seed a small surface AND a declaration covering EVERY measured section id.

    `load_declaration` fails closed on any undeclared section (REQ-0.35.0-04-01),
    so the declared `sections` map is built by calling `measure_section_spans`
    against the same text just written, never by hand-typing ids.

    The surface is written as BYTES. `write_text` opens in text mode with
    `newline=None`, which translates every `\n` to `os.linesep` -- so on Windows
    the file gains a byte per line while `measure_section_spans` below still
    measures the untranslated in-memory string, and the seeded floor undercounts
    the file it is supposed to describe (GHI #958). The production reader is
    already hardened against exactly this: `_surface_digest` decodes raw bytes
    rather than using `read_text`, "because the floor this digest protects is a
    count of PHYSICAL BYTES" (Step-4b round-8 finding 2). The fixture must
    produce the bytes that reader measures.
    """
    Path(surface).write_bytes(_SURFACE_TEXT.encode("utf-8"))
    spans = measure_section_spans(_SURFACE_TEXT)
    sections = dict.fromkeys(spans, "unowned")
    sections["doc-title"] = "corpus-owned"
    sections["alpha-section"] = "corpus-owned"

    # The floor is derived from the same measure_section_spans call above, never
    # hardcoded, so it stays coherent regardless of _SURFACE_TEXT's byte layout.
    seed_floor = sum(span for sid, span in spans.items() if sections[sid] == "unowned")

    declaration_path = _declaration_path(surface)
    declaration_path.parent.mkdir(parents=True, exist_ok=True)
    # Mint the genesis witness id FIRST and embed it, because the emitter's
    # contract is caller-minted ids: Layer-1 (the declaration) and Layer-2 (the
    # ledger) must agree on which event proves the day-one floor. A null
    # `floor_event_id` is fail-closed since `0488f8f4` -- a floor that merely
    # agrees with its own summed span is what an attacker recomputes after a
    # hand edit (GHI #957).
    genesis_event_id = f"section-ownership-genesis-{surface}-{seed_floor}"
    declaration_path.write_text(
        json.dumps(
            {
                "surface": surface,
                "sections": sections,
                "unowned_byte_floor": seed_floor,
                "measured_at": "2026-09-02T00:00:00Z",
                "floor_event_id": genesis_event_id,
            }
        ),
        encoding="utf-8",
    )
    emit_section_ownership_genesis(
        Path("."), genesis_event_id, surface, sections_digest(sections), seed_floor
    )

    context.surface = surface
    context.spans = spans
    context.prior_floor = seed_floor
    context.declaration_before = declaration_path.read_bytes()


@when('I unown section "{section}" with args "{args}"')
def step_unown_with_args(context, section: str, args: str) -> None:
    context.section = section
    argv = ["content", "unown", context.surface, "--section", section]
    context.exit_code, context.output = _invoke(argv + shlex.split(args))


@when('I unown section "{section}" with a whitespace-only attestor')
def step_unown_whitespace_attestor(context, section: str) -> None:
    # Passed as an argv element rather than through a parsed command string:
    # shlex.split would collapse the whitespace-only value this scenario is about.
    context.section = section
    context.exit_code, context.output = _invoke(
        [
            "content",
            "unown",
            context.surface,
            "--section",
            section,
            "--reason",
            "a real reason",
            "--attestor",
            "   ",
        ]
    )


@when('I unown section "{section}" with a whitespace-only reason')
def step_unown_whitespace_reason(context, section: str) -> None:
    context.section = section
    context.exit_code, context.output = _invoke(
        [
            "content",
            "unown",
            context.surface,
            "--section",
            section,
            "--attestor",
            "g0",
            "--reason",
            "   ",
        ]
    )


@then('the ownership declaration for "{surface}" is byte-unchanged')
def step_declaration_unchanged(context, surface: str) -> None:
    path = _declaration_path(surface)
    assert path.read_bytes() == context.declaration_before, (
        f"declaration for {surface} changed on a refusal: {context.output}"
    )


@then('section "{section}" of "{surface}" is declared "{state}"')
def step_section_state(context, section: str, surface: str, state: str) -> None:
    declaration = json.loads(_declaration_path(surface).read_text(encoding="utf-8"))
    assert declaration["sections"][section] == state, declaration


@then('the unowned-byte floor for "{surface}" rose by exactly that section\'s measured span')
def step_floor_rose_by_span(context, surface: str) -> None:
    declaration = json.loads(_declaration_path(surface).read_text(encoding="utf-8"))
    expected = context.prior_floor + context.spans[context.section]
    assert declaration["unowned_byte_floor"] == expected, (
        f"expected floor {expected} (seed {context.prior_floor} + measured span "
        f"{context.spans[context.section]}), got {declaration['unowned_byte_floor']}"
    )


def _ledger_events() -> list[dict]:
    path = Path(".gzkit") / "ledger.jsonl"
    if not path.exists():
        return []
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


@then("the ledger event's prior and new floor fields match the seed floor and its measured rise")
def step_ledger_event_floor_fields(context) -> None:
    """Asserts the EVENT's own floor fields, not the declaration's.

    Distinct from `step_floor_rose_by_span` above, which reads the on-disk
    declaration -- a regression that writes the right floor to the
    declaration but the wrong pair into the ledger event would pass that step
    and still be caught here (REQ-0.35.0-04-05: the event carries "both floor
    values").
    """
    events = [e for e in _ledger_events() if e.get("event") == "section_ownership_unowned"]
    assert events, f"no section_ownership_unowned event found: {_ledger_events()}"
    event = events[-1]
    expected_prior = context.prior_floor
    expected_new = context.prior_floor + context.spans[context.section]
    assert event["prior_unowned_byte_floor"] == expected_prior, (
        f"expected prior_unowned_byte_floor {expected_prior}, "
        f"got {event['prior_unowned_byte_floor']}"
    )
    assert event["new_unowned_byte_floor"] == expected_new, (
        f"expected new_unowned_byte_floor {expected_new}, got {event['new_unowned_byte_floor']}"
    )
