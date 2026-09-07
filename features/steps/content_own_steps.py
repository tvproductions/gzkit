"""BDD steps for gz content own -- the governed `unowned -> corpus-owned` transition (GHI #974).

Owning a section is the lowering move that CHANGES THE MAP: once the live
corpus carries every content line of an unowned section, the section becomes
`corpus-owned` and the decrease-only unowned-byte floor falls to the summed
span of the sections that remain unowned, as the surface measures them. Same
corpus-attestation shape as `gz content unown`: a blank `--attestor` or
`--reason` exits 1 and writes nothing.

The `no ledger event "..." was emitted`, `the command exits with code N`,
`section ... is declared ...`, `ledger event ... has field ...` and
`the ownership declaration ... is byte-unchanged` steps are shared through
behave's global registry with `content_retire_steps.py` and
`content_unown_steps.py`; only the steps this feature adds live here.
"""

from __future__ import annotations

import io
import json
import shlex
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when

from gzkit.cli.main import main
from gzkit.content.models.corpus import Corpus, CorpusEntry
from gzkit.content.ownership import load_declaration, measure_section_spans, sections_digest
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

_ALPHA_LINES = ("alpha body line one", "alpha body line two")


def _invoke(args: list[str]) -> tuple[int, str]:
    """In-process CLI driver (mirrors content_unown_steps.py:_invoke)."""
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


def _seed(context, surface: str, corpus_texts: tuple[str, ...]) -> None:
    Path(surface).write_bytes(_SURFACE_TEXT.encode("utf-8"))
    spans = measure_section_spans(_SURFACE_TEXT)
    sections = dict.fromkeys(spans, "unowned")
    sections["doc-title"] = "corpus-owned"
    seed_floor = sum(span for sid, span in spans.items() if sections[sid] == "unowned")

    declaration_path = _declaration_path(surface)
    declaration_path.parent.mkdir(parents=True, exist_ok=True)
    genesis_event_id = f"section-ownership-genesis-{surface}-own-{seed_floor}"
    declaration_path.write_text(
        json.dumps(
            {
                "surface": surface,
                "sections": sections,
                "unowned_byte_floor": seed_floor,
                "measured_at": "2026-09-07T00:00:00Z",
                "floor_event_id": genesis_event_id,
            }
        ),
        encoding="utf-8",
    )
    emit_section_ownership_genesis(
        Path("."), genesis_event_id, surface, sections_digest(sections), seed_floor
    )

    entries = tuple(
        CorpusEntry(
            id=f"corpus-alpha-section-{index:02d}",
            surface=surface,
            section="alpha-section",
            tier="invariant",
            classification="Judgment",
            text=text,
            origin="bdd",
            ts="2026-09-07T00:00:00Z",
        )
        for index, text in enumerate(corpus_texts)
    )
    corpus_path = Path(".gzkit") / "corpus" / f"{surface}.jsonl"
    corpus_path.parent.mkdir(parents=True, exist_ok=True)
    corpus_path.write_text(Corpus(entries=entries).dumps() + "\n", encoding="utf-8")

    context.surface = surface
    context.spans = spans
    context.prior_floor = seed_floor
    context.declaration_before = declaration_path.read_bytes()


@given('a control surface "{surface}" with an unowned section the corpus fully carries')
def step_seed_fully_carried(context, surface: str) -> None:
    _seed(context, surface, _ALPHA_LINES)


@given('a control surface "{surface}" with an unowned section the corpus only partly carries')
def step_seed_partly_carried(context, surface: str) -> None:
    _seed(context, surface, _ALPHA_LINES[:1])


@when('I own section "{section}" with args "{args}"')
def step_own_with_args(context, section: str, args: str) -> None:
    context.section = section
    argv = ["content", "own", context.surface, "--section", section]
    context.exit_code, context.output = _invoke(argv + shlex.split(args))


@then('the unowned-byte floor for "{surface}" equals the measured remaining unowned span')
def step_floor_is_measured_remainder(context, surface: str) -> None:
    declaration = json.loads(_declaration_path(surface).read_text(encoding="utf-8"))
    live_spans = measure_section_spans(Path(surface).read_bytes().decode("utf-8"))
    expected = sum(
        span for sid, span in live_spans.items() if declaration["sections"][sid] == "unowned"
    )
    assert declaration["unowned_byte_floor"] == expected, (
        f"expected the measured remainder {expected}, got {declaration['unowned_byte_floor']}"
    )


@then('the ownership declaration for "{surface}" reloads through the real loader')
def step_reloads(context, surface: str) -> None:
    loaded = load_declaration(
        _declaration_path(surface), Path(surface).read_bytes().decode("utf-8"), Path(".")
    )
    assert loaded.sections[context.section] == "corpus-owned", loaded.sections
