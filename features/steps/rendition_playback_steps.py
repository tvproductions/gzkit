"""BDD steps for committed-rendition store + deterministic playback + freshness gate.

@covers REQ-0.0.37-22-01
@covers REQ-0.0.37-22-02
@covers REQ-0.0.37-22-03
@covers REQ-0.0.37-22-04
@covers REQ-0.0.37-22-07
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from behave import given, then, when

from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models.corpus import Corpus, CorpusEntry
from gzkit.content.rendition import candidate_path
from gzkit.content.rendition_store import (
    RenditionProvenance,
    corpus_fingerprint,
    fingerprint_path,
    load_rendition,
    rendition_fingerprint,
    rendition_path,
    save_fingerprint,
    save_rendition,
)


def _entry(surface: str, entry_id: str, text: str) -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface=surface,
        section="behavior-rules",
        tier="compressible",
        classification="Mechanical",
        text=text,
        origin="bdd",
        ts="2026-06-19T00:00:00+00:00",
    )


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------


@given('a committed rendition for "{surface}" consumer "{consumer}" with content "{content}"')
def step_given_committed_rendition(context, surface, consumer, content):
    root = Path(context.root)
    save_rendition(root, surface, consumer, content.encode())
    context.rendition_surface = surface
    context.rendition_consumer = consumer
    context.rendition_content = content


@given('no committed rendition exists for "{surface}" consumer "{consumer}"')
def step_given_no_rendition(context, surface, consumer):
    context.rendition_surface = surface
    context.rendition_consumer = consumer


@given('a corpus for "{surface}" with one entry')
def step_given_corpus_one_entry(context, surface):
    root = Path(context.root)
    corpus = Corpus(entries=(_entry(surface, "e0", "seed entry"),))
    corpus_dir = root / ".gzkit" / "corpus"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    (corpus_dir / f"{surface}.jsonl").write_text(corpus.dumps() + "\n", encoding="utf-8")


@given('a committed rendition with provenance for "{surface}" consumer "{consumer}"')
def step_given_committed_rendition_with_provenance(context, surface, consumer):
    root = Path(context.root)
    corpus = load_corpus(root, surface)
    rendition_bytes = b"# Rendition\n"
    save_rendition(root, surface, consumer, rendition_bytes)
    save_fingerprint(
        root,
        surface,
        consumer,
        RenditionProvenance(
            corpus_fingerprint=corpus_fingerprint(corpus),
            corpus_entry_count=len(corpus.entries),
            rendition_fingerprint=rendition_fingerprint(rendition_bytes),
            committed_ts="2026-06-19T00:00:00+00:00",
            attestor="bdd",
            attestation_text="done",
        ),
    )


@given('the corpus for "{surface}" gains a new entry')
def step_given_corpus_gains_entry(context, surface):
    root = Path(context.root)
    append_entry(root, surface, _entry(surface, "e1", "newly captured rule"))


@given('a staged candidate for "{surface}" consumer "{consumer}" with content "{content}"')
def step_given_staged_candidate(context, surface, consumer, content):
    root = Path(context.root)
    cand = candidate_path(root, surface, consumer)
    cand.parent.mkdir(parents=True, exist_ok=True)
    cand.write_text(content, encoding="utf-8")


@given('AGENTS.md contains "{content}"')
def step_given_agents_md_content(context, content):
    root = Path(context.root)
    (root / "AGENTS.md").write_bytes(content.encode())


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------


@when('I load the rendition for "{surface}" consumer "{consumer}"')
def step_when_load_rendition(context, surface, consumer):
    root = Path(context.root)
    try:
        context.loaded_bytes = load_rendition(root, surface, consumer)
        context.load_error = None
        context.loaded_bytes_second = load_rendition(root, surface, consumer)
    except FileNotFoundError as exc:
        context.load_error = exc


@when('I attempt to load the rendition for "{surface}" consumer "{consumer}"')
def step_when_attempt_load_rendition(context, surface, consumer):
    root = Path(context.root)
    try:
        load_rendition(root, surface, consumer)
        context.load_error = None
    except FileNotFoundError as exc:
        context.load_error = exc


@when("I run sync_agents_md")
def step_when_sync_agents_md(context):
    import gzkit.sync_surfaces as ss
    from gzkit.config import GzkitConfig

    root = Path(context.root)
    config = GzkitConfig.load(root / ".gzkit.json")
    context.render_was_called = False

    def _track(*args, **kwargs):
        context.render_was_called = True
        return b""

    with patch.object(ss, "render_content_model", side_effect=_track):
        ss.sync_agents_md(root, config)

    context.agents_md_first = (root / "AGENTS.md").read_bytes()

    with patch.object(ss, "render_content_model", side_effect=_track):
        ss.sync_agents_md(root, config)

    context.agents_md_second = (root / "AGENTS.md").read_bytes()


# Note: "When I run the gz command "..."" is handled by the generic step
# in features/steps/gz_steps.py (which captures stdout+stderr into context.output).


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------


@then('the loaded bytes equal "{expected}"')
def step_then_loaded_bytes_equal(context, expected):
    assert context.load_error is None, f"Expected no error, got: {context.load_error}"
    assert context.loaded_bytes == expected.encode(), (
        f"Expected {expected!r}, got {context.loaded_bytes!r}"
    )


@then("loading again returns the same bytes")
def step_then_loading_again_same_bytes(context):
    assert context.loaded_bytes == context.loaded_bytes_second, (
        "Second load returned different bytes"
    )


@then("a FileNotFoundError is raised")
def step_then_file_not_found(context):
    assert isinstance(context.load_error, FileNotFoundError), (
        f"Expected FileNotFoundError, got: {context.load_error!r}"
    )


@then('AGENTS.md contains exactly "{expected}"')
def step_then_agents_md_contains(context, expected):
    root = Path(context.root)
    actual = (root / "AGENTS.md").read_bytes()
    assert actual == expected.encode(), f"Expected {expected!r}, got {actual!r}"


@then("running sync_agents_md again produces the same AGENTS.md bytes")
def step_then_sync_deterministic(context):
    assert context.agents_md_first == context.agents_md_second, (
        "sync_agents_md is not deterministic: second run produced different bytes"
    )


@then("the model render pipeline was not invoked")
def step_then_render_not_invoked(context):
    assert not context.render_was_called, (
        "render_content_model was called despite committed rendition"
    )


@then('a committed rendition exists for "{surface}" consumer "{consumer}"')
def step_then_committed_rendition_exists(context, surface, consumer):
    root = Path(context.root)
    path = rendition_path(root, surface, consumer)
    assert path.exists(), f"Expected committed rendition at {path}"


@then('a provenance sidecar exists for "{surface}" consumer "{consumer}"')
def step_then_provenance_sidecar_exists(context, surface, consumer):
    root = Path(context.root)
    path = fingerprint_path(root, surface, consumer)
    assert path.exists(), f"Expected provenance sidecar at {path}"


@then('the ledger contains a "{event_type}" event')
def step_then_ledger_event(context, event_type):
    root = Path(context.root)
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    assert ledger_path.exists(), "Ledger file not found"
    events = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matching = [e for e in events if e.get("event") == event_type]
    assert matching, (
        f"No '{event_type}' event found in ledger. Events: {[e.get('event') for e in events]}"
    )
