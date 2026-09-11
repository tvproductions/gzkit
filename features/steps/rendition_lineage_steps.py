"""BDD steps for gz validate --rendition-lineage — OBPI-0.35.0-06.

Fixture shape mirrors `tests/governance/test_rendition_lineage.py` and the
negative-control fixture `_build_rendition_lineage` in
`_qc_negative_controls.py`: a two-section surface (one section the ownership
declaration marks corpus-owned, one it marks unowned), a corpus entry for the
owned section, a committed rendition, an ownership declaration backed by a
real ledger genesis event, and a committed lineage sidecar.

@covers REQ-0.35.0-06-01
@covers REQ-0.35.0-06-02
@covers REQ-0.35.0-06-03
"""

from __future__ import annotations

import json
from pathlib import Path

from behave import given, then

from gzkit.content.corpus_store import append_entry
from gzkit.content.lineage import lineage_path
from gzkit.content.models import CorpusEntry
from gzkit.content.ownership import declaration_path, sections_digest
from gzkit.content.rendition_store import rendition_path
from gzkit.governance.events import emit_section_ownership_genesis

_SURFACE = "NCSurface.md"
_OWNER = "NCType"
_CONSUMER = "root"

_MANIFEST = {
    "content_type_routes": {_OWNER: [_CONSUMER]},
    "content_type_temperatures": {_OWNER: {_CONSUMER: "lite"}},
    "surface_content_types": {_SURFACE: _OWNER},
}

#: `generate_candidate` materializes an owned section as the heading line, a
#: blank line, the body, then a trailing newline — this chunk is byte-for-byte
#: what that derivation produces, so the "matches the corpus" scenario needs no
#: separate derivation step to prove equality against.
_CANON_TEXT = "Canon body line the corpus owns."
_MATCHING_OWNED_CHUNK = f"## Owned Section\n\n{_CANON_TEXT}\n"
_DRIFTED_OWNED_CHUNK = "## Owned Section\n\nHand-authored prose the corpus never said.\n"
_UNOWNED_CHUNK = "## Unowned Section\nHand-authored prose nobody claims.\n"

_SECTIONS = {"owned-section": "corpus-owned", "unowned-section": "unowned"}


@given("I have initialized a gzkit project with a rendition surface")
def step_init_project(context) -> None:
    root = Path.cwd()
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "vendor-manifest.json").write_text(json.dumps(_MANIFEST), encoding="utf-8")
    (root / ".gzkit").mkdir(exist_ok=True)
    context.root = root
    context.exit_code = None
    context.output = ""


@given("the corpus for the surface contains a canon entry for the owned section")
def step_corpus_canon_entry(context) -> None:
    append_entry(
        context.root,
        _SURFACE,
        CorpusEntry(
            id="e-canon",
            surface=_SURFACE,
            section="owned-section",
            tier="compressible",
            classification="Ambiguous",
            text=_CANON_TEXT,
            origin="bdd-test",
            ts="2026-09-11T00:00:00+00:00",
        ),
    )


def _write_rendition(context, owned_chunk: str) -> None:
    text = owned_chunk + _UNOWNED_CHUNK
    context.committed_text = text
    context.owned_chunk = owned_chunk
    path = rendition_path(context.root, _SURFACE, _CONSUMER)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


@given("a committed rendition whose owned section matches the corpus")
def step_rendition_matching(context) -> None:
    _write_rendition(context, _MATCHING_OWNED_CHUNK)


@given(
    "a committed rendition whose owned section carries hand-authored prose the corpus never said"
)
def step_rendition_drifted(context) -> None:
    _write_rendition(context, _DRIFTED_OWNED_CHUNK)


@given("a valid ownership declaration and committed lineage exist for it")
def step_ownership_and_lineage(context) -> None:
    digest = sections_digest(_SECTIONS)
    unowned_floor = len(_UNOWNED_CHUNK.encode("utf-8"))
    event_id = f"section-ownership-genesis-{_SURFACE}-{digest[:12]}"
    emit_section_ownership_genesis(context.root, event_id, _SURFACE, digest, unowned_floor)
    declaration_path(context.root, _SURFACE).parent.mkdir(parents=True, exist_ok=True)
    declaration_path(context.root, _SURFACE).write_text(
        json.dumps(
            {
                "surface": _SURFACE,
                "sections": _SECTIONS,
                "unowned_byte_floor": unowned_floor,
                "measured_at": "2026-09-11T00:00:00Z",
                "floor_event_id": event_id,
            }
        ),
        encoding="utf-8",
    )

    owned_span = len(context.owned_chunk.encode("utf-8"))
    unowned_span = len(_UNOWNED_CHUNK.encode("utf-8"))
    document = {
        "owned-section": {
            "owned": True,
            "entry_ids": ["e-canon"],
            "byte_span": [0, owned_span],
        },
        "unowned-section": {
            "owned": False,
            "entry_ids": [],
            "byte_span": [owned_span, owned_span + unowned_span],
        },
    }
    path = lineage_path(context.root, _SURFACE, _CONSUMER)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2), encoding="utf-8")


#: The "I run \"{command}\"" @when and the "the command exits 0" / "the command
#: exits non-zero" / "the output includes" @then steps are deliberately NOT
#: redefined here — `features/steps/obpi_lock_steps.py`, `content_compose_steps.py`,
#: and `gz_steps.py` already register those exact step texts, and behave's
#: registry is global across all loaded step modules (`AmbiguousStep` on
#: redefinition). Only the section-naming assertion below is unique to this file.


@then('the output names the section "{section_id}"')
def step_output_names_section(context, section_id: str) -> None:
    assert section_id in context.output, (
        f"Expected section id {section_id!r} in output. Got: {context.output}"
    )
