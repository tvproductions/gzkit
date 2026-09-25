"""BDD steps for the retention gate inside `gz content commit`.

OBPI-0.35.0-14, ADR-0.35.0 Decision 10. `gz content commit --retention-map <file>`
refuses to promote a candidate that drops a prior block unless every condition of
every removed block is accounted for (`enforce_retention` /
`gzkit.content.retention.validate_retention`).

Shared steps reused from ``gz_steps.py`` (never redefined here, per behave's
AmbiguousStep): ``I run the gz command "{command}"``, ``the command exits with
code {N}``, ``the output contains "{text}"``, ``the file "{path}" exists`` /
``does not exist``. Every CLI invocation in this feature goes through that
shared ``I run the gz command`` step. The candidate-staging step here is
deliberately worded "staged candidate RENDITION" rather than reusing
``rendition_playback_steps.py``'s "staged candidate ... with content" step:
that shared step writes through ``context.root``, populated only by
``content_compose_steps.py``'s "I have initialized a gzkit project" Given,
which this feature never runs -- an identical step TEXT would collide
(behave's AmbiguousStep) while resolving to a step that reads an unset
context attribute.

@covers REQ-0.35.0-14-01
@covers REQ-0.35.0-14-04
@covers REQ-0.35.0-14-05
@covers REQ-0.35.0-14-06
"""

from __future__ import annotations

import json
from pathlib import Path

from behave import given, then

from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import CorpusEntry
from gzkit.content.rendition import candidate_path
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    rendition_fingerprint,
    rendition_path,
    save_fingerprint,
    save_rendition,
)
from gzkit.content.retention import RetentionMap, retention_path

# Verbatim c3582975f:AGENTS.md:234 -- the GHI #1090 replay fixture's prior block,
# reproducible via `git show c3582975f:AGENTS.md | sed -n '234p'`.
_PRIOR_BLOCK_1090 = (
    "**REQ-coverage gate (ADR-0.0.25, ADR-0.0.59).** Every **BEHAVIOR** REQ "
    "must have a covering passing test before `gz obpi complete`; it cannot "
    "be waived — `--accept-uncovered` is refused on every lane, because "
    "BEHAVIOR's only proof channel is a `@covers` test (GHI #537). SUPPORT "
    "and STRUCTURAL-FENCE REQs are exempt by proof channel and never reach "
    "the waiver path. Failing-cover REQs cannot be waived."
)
# The 2026-09-17 compressed bullet that replaced it.
_CANDIDATE_BULLET_1090 = (
    "REQ-coverage gate: every BEHAVIOR REQ needs a passing `@covers` test "
    "before `gz obpi complete`; this cannot be waived. SUPPORT and "
    "STRUCTURAL-FENCE REQs use their declared proof channels."
)
_ACCEPT_UNCOVERED_QUOTE = "`--accept-uncovered` is refused on every lane"


def _seed_entry(surface: str) -> CorpusEntry:
    return CorpusEntry(
        id="e1",
        surface=surface,
        section="behavior-rules",
        tier="compressible",
        classification="Mechanical",
        text="seed",
        origin="bdd",
        ts="2026-06-19T00:00:00+00:00",
    )


def _seed_prior_rendition(surface: str, consumer: str, prior_text: str) -> bytes:
    """Seed a corpus + a PRIOR COMMITTED rendition with provenance; return the sidecar bytes.

    Mirrors ``tests/commands/test_content_commit.py::_seed_prior_rendition`` --
    a prior committed rendition is otherwise created by a first successful `gz
    content commit`, but a fixture needs to pin an exact prior text directly.
    """
    Path(".gzkit").mkdir(exist_ok=True)
    Path(".gzkit", "corpus").mkdir(exist_ok=True)
    root = Path(".")
    append_entry(root, surface, _seed_entry(surface))
    corpus = load_corpus(root, surface)
    fingerprint = corpus_fingerprint(corpus)
    rendition_bytes = prior_text.encode("utf-8")
    save_rendition(root, surface, consumer, rendition_bytes)
    save_fingerprint(
        root,
        surface,
        consumer,
        RenditionProvenance(
            corpus_fingerprint=fingerprint,
            corpus_entry_count=len(corpus.entries),
            rendition_fingerprint=rendition_fingerprint(rendition_bytes),
            committed_ts="2026-09-17T00:00:00+00:00",
            attestor="g0",
            attestation_text="baseline seed",
        ),
    )
    return fingerprint_path(root, surface, consumer).read_bytes()


@given(
    'a prior committed rendition with provenance for "{surface}" consumer "{consumer}" '
    'with text "{text}"'
)
def step_prior_rendition_with_provenance(context, surface: str, consumer: str, text: str) -> None:
    # A literal "\n" survives a Gherkin double-quoted parameter (which cannot
    # itself span lines); unescape it here so a fixture can name a multi-block
    # prior (a blank line separates two paragraph blocks -- Requirement 2).
    prior_text = text.replace("\\n", "\n")
    context.prior_rendition_text = prior_text
    context.prior_provenance_bytes = _seed_prior_rendition(surface, consumer, prior_text)


@given(
    'a staged candidate rendition for "{surface}" consumer "{consumer}" with content "{content}"'
)
def step_staged_candidate(_context, surface: str, consumer: str, content: str) -> None:
    cand = candidate_path(Path("."), surface, consumer)
    cand.parent.mkdir(parents=True, exist_ok=True)
    cand.write_text(content, encoding="utf-8")


@given(
    'a retention map "{filename}" for "{surface}" consumer "{consumer}" dropping condition '
    '"{cond_id}" for removed block "{block_text}" with reason "{reason}"'
)
def step_retention_map_single_dropped_condition(
    _context, filename: str, surface: str, consumer: str, cond_id: str, block_text: str, reason: str
) -> None:
    retention_map = {
        "surface": surface,
        "consumer": consumer,
        "extracted_by": "reviewer-agent",
        "mapped_by": "author-agent",
        "blocks": [
            {
                "removed": block_text,
                "conditions": [
                    {
                        "id": cond_id,
                        "quote": block_text,
                        "disposition": "dropped",
                        "reason": reason,
                    }
                ],
                "non_binding": [],
            }
        ],
    }
    Path(filename).write_text(json.dumps(retention_map), encoding="utf-8")


@given('the GHI #1090 replay is staged for "{surface}" consumer "{consumer}"')
def step_seed_1090_replay(context, surface: str, consumer: str) -> None:
    prior = "# AGENTS.md\n\n" + _PRIOR_BLOCK_1090 + "\n"
    context.prior_rendition_text = prior
    context.prior_provenance_bytes = _seed_prior_rendition(surface, consumer, prior)
    cand = candidate_path(Path("."), surface, consumer)
    cand.parent.mkdir(parents=True, exist_ok=True)
    cand.write_text("# AGENTS.md\n\n" + _CANDIDATE_BULLET_1090 + "\n", encoding="utf-8")


@given(
    'a retention map "{filename}" for the GHI #1090 replay marking the '
    "accept-uncovered condition KEPT"
)
def step_1090_all_kept_map(context, filename: str) -> None:
    """The exact fixture from `TestContentCommitRetentionGateGHI1090Replay._all_kept_map`.

    One condition (the accept-uncovered clause) is wrongly marked KEPT at a
    span absent from the candidate; a `non_binding` declaration stubs the rest
    of the block so the ONLY violation under test is that KEPT span.
    """
    retention_map = {
        "surface": "AGENTS.md",
        "consumer": "codex",
        "extracted_by": "reviewer-agent",
        "mapped_by": "author-agent",
        "blocks": [
            {
                "removed": _PRIOR_BLOCK_1090,
                "conditions": [
                    {
                        "id": "C1",
                        "quote": _ACCEPT_UNCOVERED_QUOTE,
                        "disposition": "kept",
                        "span": _ACCEPT_UNCOVERED_QUOTE,
                    }
                ],
                "non_binding": [
                    {
                        "quote": _PRIOR_BLOCK_1090,
                        "reason": "fixture stub -- only C1's disposition is under test here",
                    }
                ],
            }
        ],
    }
    Path(filename).write_text(json.dumps(retention_map), encoding="utf-8")
    context.retention_map_1090 = retention_map


@given(
    'the same retention map "{filename}" with the accept-uncovered condition '
    "DROPPED and its id attested"
)
def step_1090_drop_and_reattest(context, filename: str) -> None:
    retention_map = json.loads(Path(filename).read_text(encoding="utf-8"))
    retention_map["blocks"][0]["conditions"][0] = {
        "id": "C1",
        "quote": _ACCEPT_UNCOVERED_QUOTE,
        "disposition": "dropped",
        "reason": "2026-09-17 compression dropped this condition; disclosed here",
    }
    Path(filename).write_text(json.dumps(retention_map), encoding="utf-8")
    context.retention_map_1090 = retention_map


@then('the committed rendition for "{surface}" consumer "{consumer}" equals the prior text')
def step_rendition_equals_prior(context, surface: str, consumer: str) -> None:
    actual = rendition_path(Path("."), surface, consumer).read_text(encoding="utf-8")
    assert actual == context.prior_rendition_text, (
        f"the committed rendition was overwritten on refusal: {actual!r}"
    )


@then('the provenance sidecar for "{surface}" consumer "{consumer}" is unchanged since seeding')
def step_provenance_unchanged(context, surface: str, consumer: str) -> None:
    actual = fingerprint_path(Path("."), surface, consumer).read_bytes()
    assert actual == context.prior_provenance_bytes, (
        "the provenance sidecar was overwritten on a retention-gate refusal"
    )


@then('no "{event}" ledger event was written')
def step_no_ledger_event(_context, event: str) -> None:
    ledger = Path(".gzkit", "ledger.jsonl")
    lines = ledger.read_text(encoding="utf-8").splitlines() if ledger.exists() else []
    written = [line for line in lines if line.strip() and json.loads(line).get("event") == event]
    assert not written, f"a {event!r} ledger event was written on refusal: {written}"


@then('the retention sidecar for "{surface}" consumer "{consumer}" holds the map "{filename}"')
def step_sidecar_holds_map(_context, surface: str, consumer: str, filename: str) -> None:
    sidecar = retention_path(Path("."), surface, consumer)
    assert sidecar.exists(), f"no retention sidecar at {sidecar}"
    expected = RetentionMap.model_validate_json(Path(filename).read_text(encoding="utf-8"))
    actual = RetentionMap.model_validate_json(sidecar.read_text(encoding="utf-8"))
    assert actual == expected, f"the sidecar does not hold the validated map: {actual!r}"
