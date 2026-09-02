# Plan — OBPI-0.35.0-04-section-ownership-and-ratchet

**Parent ADR:** ADR-0.35.0-canon-entry-corpus-landing (§ Decision item 3)
**Brief:** docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md
**Lane:** Heavy

## Context

ADR § Decision item 3, quoted verbatim:

> SECTION OWNERSHIP + DECREASE-ONLY RATCHET. Sections declare `corpus-owned` or
> `unowned`. The generator materializes owned sections from the corpus and carries
> unowned sections forward verbatim. The unowned byte total is recorded in a
> decrease-only ratchet. Un-owning a section (which raises the ratchet) requires an
> attested raise-path, corpus-attested, the same shape as the retire path -- an
> undefined reversal path is the one agents invent.

This OBPI ships the declaration and the ratchet. It does NOT ship materialization
(OBPI-0.35.0-05) or the `--rendition-lineage` gate (OBPI-0.35.0-06).

**Unit ruled 2026-09-02 (operator):** *"span-based, consistent with REQ-05"*.
Unowned bytes = summed byte span of sections declared `unowned`.

Baseline re-measured 2026-09-02 with the canonical `gzkit.content.parse.section_id`:
22 H1/H2 sections, 46,876 B total; 10 corpus-addressed sections spanning 38,239 B;
12 unowned sections spanning 8,637 B; coverage 81.6%. Derived at run time, never stored.

## Step 6a Disclosures (plan-before-exploration, advisory)

**Destination-in-mind.** Before writing this plan I had already formed the approach it
proposes: a Pydantic declaration model plus a JSON schema, byte spans computed by
reusing the existing `section_id` vocabulary, and a decrease-only guard in the store's
update path. That destination came from reading the brief's Allowed Paths, which name
`ownership.py`, `unown.py`, and `section_ownership.json` as CREATE targets — the brief
largely fixes the shape, so the plan is closer to a decomposition than a free design.

**Rejected alternatives.**

1. A fresh slugifier local to `ownership.py`. Rejected on reading
   `markdown_parser.py:183` — `section_id` is documented as "the single section-id
   vocabulary shared by every surface that names a section ... a second slugifier would
   let those surfaces disagree." Inventing one would also have silently failed REQ-06.
2. Storing the baseline figures in the declaration as authoritative. Rejected: REQ-07
   requires derivation at run time, and `.claude/rules/governance-core.md` makes a
   written value illustrative. The declaration stores the FLOOR (a ratchet needs
   durable state) but recomputes the coverage figure.
3. Reusing `surface_delivery_witness._rendered_sections` for spans. Rejected: it scans
   H2 only and returns heading offsets, not spans; AGENTS.md carries two H1s that the
   brief's "22 H1/H2 sections" counts. A shared helper is the right eventual home but
   widening that private function is outside this brief's allowlist.
4. Folding the raise-path into the existing `content retire` verb. Rejected: retire
   acts on corpus ENTRIES, un-own acts on SECTIONS. The brief names `unown.py` as a
   CREATE target and the ADR calls for "the same shape", not the same verb.

## Files

- `src/gzkit/schemas/section_ownership.json` — CREATE, declaration schema
- `src/gzkit/content/ownership.py` — CREATE, model, store, span measurement, ratchet
- `.gzkit/ownership/AGENTS.md.json` — CREATE, day-one declaration and floor
- `src/gzkit/commands/content/unown.py` — CREATE, attested raise-path command
- `src/gzkit/commands/content/__init__.py`, `src/gzkit/cli/**` — MODIFY, register verb only
- `src/gzkit/governance/events.py` — MODIFY, ownership and ratchet events
- `tests/content/test_ownership.py` — CREATE, covering tests
- `tests/commands/test_content_unown.py` — CREATE, covering tests
- `features/**` — ADD, Gate 4 scenarios for the raise-path
- `docs/user/manpages/content.md` — MODIFY, raise-path section

## Steps

1. Schema and model. `section_ownership.json`: `surface`, `sections` (map of section id
   to the closed enum `corpus-owned` / `unowned`), `unowned_byte_floor` (int >= 0),
   `measured_at`. Pydantic `OwnershipDeclaration` mirrors it. The closed enum satisfies
   REQ-01's "no third value". (REQ-01)
2. Span measurement. `measure_section_spans(surface)` returns a mapping of section id to
   byte span over H1/H2 headings, keyed by `section_id(title)` imported from
   `gzkit.content.parse`. (REQ-06)
3. Fail-closed load. `load_declaration(path, surface)` cross-checks declared keys against
   measured ids: an undeclared present section, a declared-but-absent id, or a value
   outside the enum raises, naming the offending section id. Three-part recovery prose.
   (REQ-01, REQ-09)
4. Baseline computation. `compute_baseline(surface, corpus)` returns owned count, unowned
   span, total span, coverage pct, and the per-section entry-count histogram — all
   derived, none stored. (REQ-07, REQ-08)
5. Decrease-only ratchet. `record_unowned_total(decl, total)` — a total less than or equal
   to the floor updates it and emits a ratchet event carrying prior and new values; a
   greater total is REFUSED with recovery prose and no write. (REQ-02, REQ-03, REQ-09)
6. Ledger events. Add the ownership-transition and ratchet-floor-change events to
   `events.py`, following the existing emit-helper pattern. (REQ-05)
7. Attested raise-path. `gz content unown <surface> --section <id> --attestor --reason`,
   mirroring the FAIL-CLOSED arm of `commands/content/commit.py:88-117`: an empty or
   whitespace-only attestor or reason exits non-zero, writes nothing, emits nothing. On
   success the section flips to `unowned`, the floor RISES by that section's span, and the
   event records the section id, both floor values, the attestor, and the reason.
   (REQ-04, REQ-05, REQ-09)
8. Day-one declaration. Generate `.gzkit/ownership/AGENTS.md.json` from the measured
   baseline. (REQ-08)
9. Parser registration in `commands/content/__init__.py` and `cli/**`. Verb only.
10. Docs and BDD. Manpage section for `content unown`; behave scenarios tagged
    `@REQ-0.35.0-04-04` and `@REQ-0.35.0-04-05` for the attested raise-path.

Each step follows Red-Green-Refactor: one minimal test, watched to fail on its own
assertion (never an import error), then the simplest code that passes.

## Verification

```
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run mkdocs build --strict
```

## Notes

- Denied: `AGENTS.md` itself, `composer.py`, `trust_audits/**`, `models/corpus.py`.
- REQ-08 is [support] — proven by the `artifact_edited` ledger event citing
  `.gzkit/ownership/AGENTS.md.json` plus `gz validate --documents`, never by a unit test
  authored to fill the cell (ADR-0.0.59).
- Scope collisions reported by `gz plan audit` are all against TERMINAL briefs on shared
  infrastructure files; none is a live brief owning this work.
