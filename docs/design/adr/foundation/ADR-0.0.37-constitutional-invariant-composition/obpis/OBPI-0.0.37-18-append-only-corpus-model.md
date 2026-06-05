---
id: OBPI-0.0.37-18-append-only-corpus-model
parent: ADR-0.0.37-constitutional-invariant-composition
item: 18
lane: Heavy
status: Completed
# req_atomic exemption (gz-obpi-specify, 2026-06-04): each REQ is one
# indivisible model/store/conformance/schema contract. Labor does not
# subdivide below a REQ, so one seq=01 TASK per REQ is the honest grain.
req_atomic:
  - REQ-0.0.37-18-01  # CorpusEntry model: one frozen-model contract
  - REQ-0.0.37-18-02  # append-only Corpus store: one append-only-aggregate contract
  - REQ-0.0.37-18-03  # section conformance against AgentContract/Pillar: one conformance contract
  - REQ-0.0.37-18-04  # JSON Schema mirror parity: one schema-mirror contract
---

# OBPI-0.0.37-18-append-only-corpus-model: Append-Only Corpus Model

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #18 — "OBPI-0.0.37-18 — Append-only corpus model + addressed-entry schema (reuse AgentContract/Pillar substrate from prior 11/13; entry = id/surface/section/anchor/tier{invariant|compressible}/classification/witness/text/origin/ts; sections are TEMPLATE-defined, Pydantic enforces conformance; append-only contract)"

**Status:** Completed

## Objective

Deliver the **data layer** for the 2026-06-03 Decision Re-Alignment's part-1 "append-only
corpus (source of truth)": a frozen, schema-bound `CorpusEntry` model carrying the ten
addressed-and-provenanced fields the ADR names, plus an append-only `Corpus` aggregate whose
only mutation is *append* (existing entries are immutable; nothing is hand-edited at the
rendered location), plus a JSON Schema mirror for the entry. Section conformance is enforced
against the existing `AgentContract`/`Pillar` substrate (an entry's `section` MUST resolve to a
real template-defined `Pillar`) — reusing the substrate built under prior 11/13, not a parallel
registry. (Invariant-tier *presence* enforcement is deferred to OBPI-23, which adds the
invariant-tier section designation — `Pillar.tier` is `lite|medium|heavy` today, with no
`invariant` value, so "every invariant section is present" cannot be computed in this scope.)

This OBPI is the **substrate only**. It defines and validates the corpus shape. It does **not**
add the capture surface, the ledger event, the setpoint, the compressor, or the render path —
those are downstream OBPIs (see Denied Paths). The brief is deliberately narrow so the pipeline
has a clean gate-firing boundary before the capture tool (OBPI-19) builds on top of it.

## Lane

**Heavy** — adds a new Pydantic model + a new JSON Schema mirror (schema/runtime-contract
surface). Foundation kind + Heavy lane → Gate 5 human attestation is required
(`assets/HEAVY_LANE_PLAN_TEMPLATE.md`, read before implementation).

## Allowed Paths

- `src/gzkit/content/models/corpus.py` — **CREATE** (net-new). `CorpusEntry` (frozen `BaseContentModel` subclass; the ten ADR-named fields) and `Corpus` (append-only aggregate + JSONL (de)serialize + `validate_against(AgentContract)` conformance).
- `src/gzkit/content/models/__init__.py` — export `Corpus`, `CorpusEntry` in `__all__`. **OPEN DECISION (resolve in plan):** a corpus entry is a STORE record, not a parseable per-turn surface, so it likely should NOT join the `CONTENT_MODELS` render-dispatch registry — `Pillar` (a store-only sub-model) is exported yet deliberately absent from `CONTENT_MODELS`, and `ConstitutionalInvariant` (the closest store-entry precedent) lives outside it entirely. Default: follow the `Pillar` precedent (export, do not register in `CONTENT_MODELS`).
- `src/gzkit/schemas/corpus_entry.json` — **CREATE** (net-new). JSON Schema mirror of `CorpusEntry` (`additionalProperties: false`, `required` for the non-optional fields, `tier` and `classification` enums), shaped on the `constitutional_invariant.json` precedent.
- `tests/content/test_corpus_model.py` — **CREATE** (net-new). `@covers`-decorated tests for REQ-01..04.
- `features/constitutional_invariants.feature` — Gate 4 BDD scenarios tagged `@REQ-0.0.37-18-01`..`-04`.
- `features/steps/constitutional_invariants_steps.py` — step bindings for the new scenarios (only if existing steps do not already cover them).
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-18-append-only-corpus-model.md` — this brief.
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only).

## Denied Paths

- Paths not listed in Allowed Paths.
- `src/gzkit/events.py` — the `corpus_entry_appended` ledger event family is **OBPI-19** (capture tool emits it on append; this brief defines no event).
- `src/gzkit/commands/content/` and the operator capture CLI it will host — the corpus "remember" capture surface is **OBPI-19**, not this brief (this OBPI defines no CLI verb).
- `data/vendor-manifest.json` (`content_type_temperatures` setpoint map) — the compression setpoint is **OBPI-20**.
- `src/gzkit/governance/compose.py`, `src/gzkit/sync_surfaces.py`, `sync_agents_md`, any deterministic-playback path — the committed-rendition store + playback is **OBPI-22**.
- `AGENTS.md`, `src/gzkit/templates/agents.md`, the rendered surfaces and the monolith template — authoring/playback of the rendered surface is **OBPI-22/27**; this brief touches no rendered surface.
- Any `gz validate --` scope wiring (setpoint/section coherence validator) — **OBPI-20/25**; the conformance proof here is in-model + unit-tested, not a new CLI validator scope.
- The `invariant`-tier section *designation* and its presence-enforcement — **OBPI-23**. `CorpusEntry.tier` carries the `invariant|compressible` value on the entry, but marking which template sections are invariant-bearing (and requiring their presence) is OBPI-23's deliverable; `Pillar` is read-only here and is NOT extended with an invariant marker.
- New runtime dependencies, CI files, lockfiles.
- Speculative model fields beyond the ten the ADR names (simplicity-first; the model grows to the corpus shape, not the imagination).

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `CorpusEntry` MUST be a frozen, `extra="forbid"` model carrying exactly the ten ADR-named fields — `id, surface, section, anchor (optional), tier, classification, witness (optional), text, origin, ts` — with `tier ∈ {invariant, compressible}` and `classification` reusing the `Bullet` `_Classification` enum (`Mechanical | Promotable | Judgment | Ambiguous`). No speculative fields.
2. REQUIREMENT: `Corpus` MUST be append-only — its public mutation surface is a single `append(entry) -> Corpus` returning a NEW aggregate; there is NO method that edits or deletes an existing entry; the entries collection is immutable (e.g. `tuple`). A JSONL round-trip (`load`/`dumps`) MUST reconstruct an equal `Corpus`.
3. REQUIREMENT: `Corpus.validate_against(contract: AgentContract)` MUST fail-closed when any entry's `section` does not resolve to a `Pillar.id` in the contract. Conformance is computed against the template-defined `Pillar` set, never a separate registry. (Invariant-tier *presence* enforcement — "every invariant-bearing section is present" — is DEFERRED to OBPI-23, which introduces the invariant-tier designation; `Pillar.tier` is `lite|medium|heavy` today with no `invariant` value, so presence cannot be computed in this OBPI's scope. Do NOT hardcode a section list to fake it.)
4. REQUIREMENT: `src/gzkit/schemas/corpus_entry.json` MUST mirror `CorpusEntry` — it validates a conformant entry and rejects a malformed one (unknown property via `additionalProperties: false`; out-of-enum `tier`). Model↔schema field parity MUST be asserted by test.
5. NEVER: add the capture CLI, the `corpus_entry_appended` ledger event, the setpoint map, the compressor, or any render/playback wiring in this OBPI — those are OBPIs 19–22 (see Denied Paths). This brief makes the corpus *modeled and validated*, not *captured or rendered*.
6. ALWAYS: reconcile this brief against the parent ADR § Decision Re-Alignment (2026-06-03) part 1 before implementation; quote the Checklist #18 Decision item verbatim into the Implementation Summary.

> STOP-on-BLOCKERS: if `src/gzkit/content/models/agent_contract.py` (Pillar) or `src/gzkit/content/models/base.py` (BaseContentModel) is missing, print a BLOCKERS list and halt — the conformance contract has no substrate without them.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote verbatim into Implementation Summary:** Checklist #18 — "OBPI-0.0.37-18 — Append-only corpus model + addressed-entry schema (reuse AgentContract/Pillar substrate from prior 11/13; entry = id/surface/section/anchor/tier{invariant|compressible}/classification/witness/text/origin/ts; sections are TEMPLATE-defined, Pydantic enforces conformance; append-only contract)."
- [ ] Parent ADR § Decision Re-Alignment (2026-06-03) part 1 — the append-only-corpus design (addressed/provenanced entry; sections template-defined; conformance via AgentContract/Pillar).
- [ ] Parent ADR § Intent — the why-frame (#519 context-economics; corpus as source of truth).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/models/agent_contract.py` exists (`Pillar`, `AgentContract`)
- [ ] `src/gzkit/content/models/base.py` exists (`BaseContentModel` — frozen, extra=forbid, schema_version)
- [ ] `src/gzkit/content/models/bullet.py` exists (`_Classification` enum to reuse)
- [ ] `src/gzkit/schemas/constitutional_invariant.json` exists (schema-mirror precedent)
- [ ] `tests/content/` exists (sibling tests: `test_round_trip_agent_contract.py`, `test_migration_layer.py`)

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/models/agent_contract.py` — `Pillar.id`/`Pillar.tier` are the section keys conformance resolves against.
- [ ] `src/gzkit/content/models/bullet.py` — reuse `_Classification`; do not redefine the enum.
- [ ] `src/gzkit/governance/invariants.py` — the `load_invariants` + `jsonschema.validate` pattern to mirror for schema loading/validation.
- [ ] `src/gzkit/content/models/__init__.py` — the `CONTENT_MODELS` + `__all__` registration pattern to follow.

## Quality Gates

### Gate 1: ADR
- [ ] Checklist #18 Decision item quoted into Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)
- [ ] Tests derived from REQ-01..04, RED before GREEN
- [ ] `uv run gz test` passes

### Code Quality
- [ ] `uv run gz lint` and `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict` clean

### Gate 4: BDD (Heavy)
- [ ] `features/constitutional_invariants.feature` scenarios tagged `@REQ-0.0.37-18-01`..`-04` pass

### Gate 5: Human (Heavy + Foundation)
- [ ] Human attestation recorded

## Verification

```bash
test -f src/gzkit/content/models/corpus.py
test -f src/gzkit/schemas/corpus_entry.json
uv run python -c "from gzkit.content.models import CorpusEntry, Corpus; print('import ok')"
uv run -m unittest tests.content.test_corpus_model -v
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature
```

## Demo

```bash
uv run python -c "
from gzkit.content.models import CorpusEntry, Corpus
e = CorpusEntry(
    id='c-prime-1', surface='AGENTS.md', section='prime-directive', tier='invariant',
    classification='Mechanical', text='YOU OWN THE WORK COMPLETELY.',
    origin='GHI#519', ts='2026-06-05T00:00:00Z',
)
c = Corpus().append(e)
print('entries:', len(c.entries), '| tier:', c.entries[0].tier)
print('round-trip equal:', Corpus.loads(c.dumps()) == c)
"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-18-01 [BEHAVIOR]: `CorpusEntry` is a frozen `extra="forbid"` model with exactly the ten ADR-named fields (`anchor`, `witness` optional), `tier ∈ {invariant, compressible}`, `classification` reusing `Bullet._Classification`; constructing with an unknown field or out-of-enum `tier` raises. Proof: `@covers(REQ-0.0.37-18-01)` test in `tests/content/test_corpus_model.py`.
- [ ] REQ-0.0.37-18-02 [BEHAVIOR]: `Corpus.append(entry)` returns a NEW `Corpus` with the entry appended and the original unchanged; no mutate/delete method exists; entries are immutable; `Corpus.loads(c.dumps()) == c`. Proof: `@covers(REQ-0.0.37-18-02)` test asserting append immutability + JSONL round-trip.
- [ ] REQ-0.0.37-18-03 [BEHAVIOR]: `Corpus.validate_against(contract)` raises when an entry's `section` does not resolve to a `Pillar.id` in `contract`, and passes for a conformant corpus. (Invariant-tier presence is OBPI-23, not asserted here — `Pillar.tier` has no `invariant` value yet.) Proof: `@covers(REQ-0.0.37-18-03)` test exercising the failure path and the success path.
- [ ] REQ-0.0.37-18-04 [BEHAVIOR]: `src/gzkit/schemas/corpus_entry.json` validates a conformant entry and rejects one with an unknown property and one with an out-of-enum `tier`; the test asserts schema↔model field parity. Proof: `@covers(REQ-0.0.37-18-04)` test loading the schema via `jsonschema.validate`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision item quoted
- [ ] **Gate 2 (TDD):** RGR followed; tests derive from REQs
- [ ] **Code Quality:** lint, format, typecheck clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** corpus append + conformance + schema parity
- [ ] **Gate 5:** human attestation recorded

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste test output here
```

### Code Quality
```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)
```text
# Paste docs-build output here
```

### Gate 4 (BDD)
```text
# Paste behave output here
```

### Gate 5 (Human)
```text
# Record attestation text here
```

### Value Narrative

Before: contract content lives as hand-authored prose in `AGENTS.md` + the monolith template —
the very shape the 2026-06-03 Re-Alignment names as the root of #519. After: there is a frozen,
schema-validated, append-only `CorpusEntry`/`Corpus` substrate — the single addressable source
of truth that the capture tool (OBPI-19), the compressor (OBPI-21), and deterministic playback
(OBPI-22) build forward from. This OBPI lands the substrate; nothing renders yet.

### Key Proof


Corpus().append(entry) yields a NEW immutable aggregate (no edit/delete surface; entries are a tuple); Corpus.loads(c.dumps()) == c (JSONL round-trip); validate_against(AgentContract) fail-closes on a section resolving to no Pillar; corpus_entry.json accepts a conformant entry and rejects unknown-property / out-of-enum-tier. Observed: 17/17 OBPI-scoped tests pass (receipt arb-step-unittestscoped-a6bbff16e7d14aaf8f21fd131830e52b); full suite 5879/5879 (arb-step-unittest-61a826da0fab4a7bb17b46b670476fdc); 4 BDD scenarios pass (arb-step-behave-de7d0ecefa4a405cb1494db6fc7a2cff).

### Implementation Summary


- Decision item implemented (verbatim): "OBPI-0.0.37-18 — Append-only corpus model + addressed-entry schema (reuse AgentContract/Pillar substrate from prior 11/13; entry = id/surface/section/anchor/tier{invariant|compressible}/classification/witness/text/origin/ts; sections are TEMPLATE-defined, Pydantic enforces conformance; append-only contract)."
- Files created: src/gzkit/content/models/corpus.py (CorpusEntry frozen model + Corpus append-only aggregate), src/gzkit/schemas/corpus_entry.json (JSON Schema mirror), tests/content/test_corpus_model.py (17 @covers tests).
- Files modified: src/gzkit/content/models/__init__.py (export Corpus/CorpusEntry, NOT in CONTENT_MODELS per Pillar precedent), features/constitutional_invariants.feature + steps (4 @REQ-tagged BDD scenarios).
- Tests added: 17 unit tests + 4 BDD scenarios; REQ coverage 100% (4/4).
- Date completed: 2026-06-05
- Attestation status: operator-verbatim "attest completed"
- Defects noted: none.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.37-18 append-only corpus model verified: 17/17 OBPI-scoped tests + 4 BDD scenarios pass (receipts arb-step-unittestscoped-a6bbff16e7d14aaf8f21fd131830e52b, arb-step-behave-de7d0ecefa4a405cb1494db6fc7a2cff), full suite 5879/5879, lint/typecheck/mkdocs clean, REQ coverage 100% (4/4).
- Date: 2026-06-05

---

**Date Completed:** 2026-06-05

**Evidence Hash:** -
