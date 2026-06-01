# Implementation Plan — OBPI-0.0.37-13 Reverse-Parse Migration to the Master Model

**OBPI:** OBPI-0.0.37-13-reverse-parse-migration
**Parent ADR:** ADR-0.0.37-constitutional-invariant-composition (Decision Extension 2026-05-30, CIC-1 density-dial)
**Lane:** Heavy (foundation + heavy → Gate-5 human attestation, mandatory)
**Plan authored:** 2026-06-01

## Context

`gz content import AGENTS.md --as AgentContract` today loses 99.84% of the contract.
Mechanism, now confirmed by reading the surfaces: AGENTS.md contains **no** `## Tech Stack`
or `## Rules` heading, yet `_parse_agent_contract` (`markdown_parser.py:153`) reads *only*
those two sections plus name+purpose — so `pillars` is left at its `default_factory=list`
empty and the 32 KB contract collapses to a name+purpose stub.

OBPI-11 already shipped the model spine: `Pillar` (id/title/order/enabled/tier/bullets) and
`Bullet` (text/indent/**classification**/witness/rationale_ref/density_min, with a
Judgment→`lite` floor validator). OBPI-12 shipped the temperature renderer. This brief is the
**reverse-parse migration**: make `import` populate `pillars` from every real `##` section,
join per-bullet `classification` from the advisory scorecard, grow the template so a populated
model renders the full clean contract, dissolve `agents.local.md` into model rows, and assert
the model↔JSON round-trip. It does **not** swap the production sync path (OBPI-14).

## Destination-in-mind (Step 6a disclosure — required)

This plan did not discover its destination; the re-scoped brief and the resume handoff
pre-named it. The approach I had already formed before authoring: *extend the existing
`_parse_agent_contract` to walk all `##` sections via the existing `_sections()` helper,
join classification from `advisory-rules-audit.md`, grow `claude.md.j2`, add a model↔JSON
round-trip test, and remove `agents.local.md`*. My work this session was **feasibility
verification of that pre-formed destination**, not open exploration — disclosed honestly so
the audit is not mistaken for independent rediscovery.

## Rejected alternatives (Step 6a disclosure — required)

1. **Lossless `parse(render(model))` on clean prose** — REJECTED (and is the contradiction
   that FAILed the prior plan-audit). Clean human-readable AGENTS.md cannot carry per-bullet
   classification metadata, so it can never round-trip a classified model. The satisfiable
   lossless contract is model↔canonical-JSON; the prose render is explicitly lossy.
2. **Annotated-markdown render** (embed classification as HTML comments / inline tags so prose
   *could* round-trip) — REJECTED: bloats and uglifies AGENTS.md, defeats the density-dial's
   readability purpose, and re-introduces a hand-edit surface.
3. **A separate OBPI to re-open OBPI-12's template** — REJECTED: model+template+parser are one
   irreducible non-lossy unit; the brief already relaxes Denied-Paths to fold the template here.
4. **Infer classification from prose** (regex "MUST"/"NEVER" → Mechanical) — REJECTED by REQ-02:
   classification is *joined* from the advisory scorecard, the existing
   Mechanical/Promotable/Judgment/Ambiguous source, never re-derived from wording.

## Files (all within brief Allowed Paths)

| File | Change | REQ |
|------|--------|-----|
| `src/gzkit/content/parse/markdown_parser.py` | Extend `_parse_agent_contract`: walk every `##` section via `_sections()`, build one `Pillar` per section (id=kebab(title), order=index, bullets); join classification | 01, 02, 05 |
| `src/gzkit/content/models/agent_contract.py` | Grow **only if** a section cannot be expressed as bullets (block/raw-line fallback). No speculative fields. | 01 |
| `src/gzkit/content/models/bullet.py` | Same bounded-growth clause; field already carries `classification` — likely no change | 02 |
| `src/gzkit/content/templates/agentcontract/claude.md.j2` | Grow so a populated model renders the full clean contract (all pillars/sections), not the stub | 01, 04 |
| `src/gzkit/content/render/pipeline.py` | Render wiring for the fuller template if needed | 01 |
| `src/gzkit/content/migration/registry.py` | Likely **untouched** — adding `Pillar.lines` (optional, default `[]`) needs no schema_version bump | — |
| `src/gzkit/commands/content/import_.py` | `gz content import` surface adjustments if the populate path needs them | 01 |
| `.gzkit/agents.local.md` | **Not edited** — content captured via the AGENTS.md import (already spliced there); physical removal is OBPI-14 (Option A, scope correction) | 03 |
| `tests/content/test_round_trip_agent_contract.py` | model↔JSON round-trip + structural `parse(render(m))` recovery | 04, 05 |
| `tests/content/test_migration_layer.py` | full-corpus import faithfulness; classification join; agents.local dissolve | 01, 02, 03, 06 |
| `tests/content/test_render_pipeline.py` | full-corpus render coverage | 01 |

## Steps (TDD per REQ — RED then GREEN, commit each GREEN)

1. **REQ-01 — populate pillars (RED→GREEN).** Test in `test_migration_layer.py`: import the live
   AGENTS.md, assert `len(pillars)` ≈ the section count and that a known section
   (e.g. `PRIME DIRECTIVE (OWNERSHIP)`) appears as a `Pillar` with non-empty bullets — and that
   the imported model's serialized size is within a bounded ratio of the source (regression floor:
   beat the 161-byte stub). Implement by walking `_sections()`; reuse `_parse_bullets()` for
   bullet lines. **Primary risk lives here** — see Notes (tables / numbered lists / `###`).
2. **REQ-02 — join classification (RED→GREEN).** Test: a bullet whose scorecard row scores
   `Judgment` (e.g. "Read AGENTS.md before implementation work") imports with
   `classification="Judgment"`. Implement a scorecard parser (read `advisory-rules-audit.md`
   tables → {rule-text → Score}) and a match step joining each bullet to its score.
3. **REQ-05 — conservative default (RED→GREEN).** Test: a bullet with no scorecard match imports
   as `classification="Ambiguous"`, never `Mechanical`. Implement as the join's fallback.
4. **REQ-03 — capture agents.local.md as model rows (RED→GREEN).** Test: importing AGENTS.md
   yields a model in which a known Local-Agent-Rules line (e.g. the UTF-8-prefix rule) appears as a
   model row — the content is spliced into AGENTS.md, so the import captures it. Physical file
   removal + sync rewire are OBPI-14 (Option A); OBPI-13 does **not** delete the file or edit the
   sync path.
5. **REQ-04 — round-trip (RED→GREEN).** Test: `AgentContract.model_validate_json(m.model_dump_json()) == m`
   (lossless), and `parse(render(m))` recovers sections/bullets/text/order (structure-only,
   explicitly NOT classification metadata). Grow `claude.md.j2` until the structural recovery holds.
6. **REQ-06 — record the migration (SUPPORT).** `gz validate --documents` passes after the
   model+parser+template changes (no regression); `artifact_edited` events are emitted for the
   edited OBPI-13 surfaces. The removed-agents.local.md proof is OBPI-14 (Option A).

## Verification (from brief)

```
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.test_round_trip_agent_contract -v
uv run -m unittest tests.content.test_migration_layer -v
uv run mkdocs build --strict        # Gate 3 (Heavy)
```

Gate 4 (Heavy/BDD): `features/constitutional_invariants.feature` scenario tagged `@REQ-0.0.37-13-*`.
Gate 5 (Heavy + Foundation): human attestation — pipeline cannot self-close.

## Notes / Risks

- **Primary implementation risk — model expressiveness (handoff-flagged).** `Pillar.bullets` is a
  flat `list[Bullet]` (text + indent). AGENTS.md sections carry markdown **tables** (Gate Covenant,
  Kinds), numbered lists, prose paragraphs, and `###` sub-headings. A naive bullet-only capture
  loses that structure and breaks REQ-04's structural recovery. Bounded escape (brief-permitted):
  capture non-bullet lines per section as full-fidelity `text` (raw-line bullets) or add a minimal
  block/raw representation **only as far as round-trip recovery requires** — grow the model to fit
  the corpus, never speculation. The round-trip test is the forcing function.
- **Classification join is by paraphrase, not verbatim text.** Scorecard "Rule" cells are
  summaries, not the exact AGENTS.md bullet wording. Expect imperfect matches; REQ-05's `Ambiguous`
  fallback is the designed safety net (and is the *correct* outcome — never silently `Mechanical`).
- **`tech_stack`/`rules` legacy fields.** AGENTS.md has neither `## Tech Stack` nor `## Rules`, so
  populating `pillars` does not double-render. Leave the two legacy fields for back-compat; the
  full-contract render walks `pillars`.
- **Denied (OBPI-14, not here):** `sync_agents_md`, `get_project_context` literals, the monolith
  template `src/gzkit/templates/AGENTS.md`, and the rendered `AGENTS.md` output. This brief makes
  the model *populated and renderable*; OBPI-14 makes it the production source.
- **Scope-collision advisory:** 18 sibling-ADR path overlaps (`src/gzkit/commands/content/`,
  `markdown_parser.py` shared with ADR-0.0.34-03 which this brief *extends*) are expected
  shared-directory noise, not a blocker.
