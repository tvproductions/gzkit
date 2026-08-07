---
id: OBPI-0.35.0-01-corpus-tombstone-schema-and-fold
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 1
lane: Heavy
status: Draft
allowlist:
- src/gzkit/content/models/corpus.py
- src/gzkit/content/tier_policy.py
- src/gzkit/schemas/corpus_entry.json
- tests/content/test_corpus_model.py
- docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-01-corpus-tombstone-schema-and-fold.md
reqs:
- REQ-0.35.0-01-01
- REQ-0.35.0-01-02
- REQ-0.35.0-01-03
- REQ-0.35.0-01-04
- REQ-0.35.0-01-05
- REQ-0.35.0-01-06
- REQ-0.35.0-01-07
- REQ-0.35.0-01-08
- REQ-0.35.0-01-09
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz validate --rendition-freshness
- uv run gz validate --rendition-floor-coherence
---

# OBPI-0.35.0-01-corpus-tombstone-schema-and-fold: Corpus Tombstone Schema And Fold

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #1 - "`CorpusEntry.supersedes` / `.retires` fields + `effective_corpus()` fold (algebra specified, including retire-the-tombstone) + `tier_policy.invariant_entries()` reads the effective view"

**Status:** Draft

## Objective

Add two optional tombstone fields to `CorpusEntry` and ship `effective_corpus()` — a fold whose algebra is pinned in this brief, including retire-the-tombstone (un-retirement) — so retirement becomes an appended row rather than a deletion, and route `tier_policy.invariant_entries()` through the effective view so the invariant floor stops counting retired canon.

**Dependency order (ADR-0.35.0 § Scope Minimization):** 01 is the head of the 01 -> 02 -> 03 prerequisite chain and the minimum shippable slice. Nothing else in ADR-0.35.0 may land first: alternative H is rejected precisely because shipping the OBPI-05 generator before retirement ships a regression by construction.

> **PARTIALLY PRE-LANDED — read before implementing (reconciled 2026-08-07).**
> Roughly half of this brief landed ahead of the chain as the GHI #635 direct fix
> (`852e8a25`, `42ba6c250`) on 2026-07-22 — ONE DAY after this brief was authored,
> and nobody reconciled it. Measured at HEAD `6863f0555`:
>
> | Requirement | Target | Observed | State |
> |-------------|--------|----------|-------|
> | 1 — additive fields | `retires` + `supersedes`, both `str \| None = None` | `retires` only (`models/corpus.py:100`) | **half landed** |
> | 1 — regression fixture | 51 rows: 50 invariant, 1 compressible | **53 rows: 51 invariant, 2 compressible** (1 retired, so 50 live invariant) | **stale — re-measure** |
> | 2 — omit unset tombstone fields | must never emit `"retires":null` | **solved and fenced** — `POST_BASELINE_IDENTITY_FIELDS` + `_inert_fields` (`corpus.py:66-115`); fence is `test_every_field_is_classified` | **landed** |
> | 3-12 — the nine-clause fold | `effective_corpus()` | **absent** — a flat `Corpus.retired_ids()` stands in (`corpus.py:129-131`) | **open** |
> | 14 — `tier_policy` reads the effective view | route through the fold | **already routed, in the flat form** (`tier_policy.py:20`) | **landed; needs repoint** |
>
> **What this changes about the work.** REQ-2 is no longer something to invent.
> The identity-serialization mechanism exists and GENERALIZES: adding `supersedes`
> means appending it to `POST_BASELINE_IDENTITY_FIELDS`, and
> `test_every_field_is_classified` fails closed if you forget. REQ-14's consumer is
> already wired; it must be REPOINTED from `retired_ids()` to the fold, not newly
> connected — and per BI-01 the repoint must reach every consumer, since a leftover
> flat reader is the green-gate-over-omitted-canon failure this ADR ranks worst
> (§ Consequences Negative #5).
>
> **Latent defect the flat stand-in carries — Algebra 6 does not hold today.**
> `retired_ids()` is `frozenset(e.retires for e in entries if e.retires is not None)`:
> flat, with no liveness pass. Append `T2` retiring `T1` and the set becomes
> `{X, T1}` — `X` stays retired forever. **Un-retirement does not work today, and
> fails silently.** The nine-clause fold is not decoration over the shipped
> mechanism; it is what makes retirement reversible at all.
>
> **Why this note is authored rather than computed.**
> `uv run gz obpi brief-drift OBPI-0.35.0-01-corpus-tombstone-schema-and-fold`
> reports **clean across all five dimensions** (allowlist, discovery, verification,
> req_count, citation). Every dimension is an existence check, so none can see a
> surface this brief plans to CREATE that already exists — the inverse of the
> exists-but-dead class GHI #581 names, and invisible to the same engine.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/content/models/corpus.py` — `CorpusEntry` tombstone fields, `Corpus` fold
- `src/gzkit/content/tier_policy.py` — `invariant_entries()` reads the effective view
- `src/gzkit/schemas/corpus_entry.json` — additive schema for the two optional fields
- `tests/content/test_corpus_model.py` — fold-algebra and additive-load tests
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-01-corpus-tombstone-schema-and-fold.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/commands/content/**` — the `withdraw` CLI surface is OBPI-0.35.0-02
- `.gzkit/corpus/AGENTS.md.jsonl` — appending the eight tombstones is OBPI-0.35.0-03
- `src/gzkit/content/composer.py` — generator and `ByteEvidence` work is OBPI-0.35.0-05
- `src/gzkit/governance/trust_audits/**` — validator scopes are OBPI-0.35.0-06
- New dependencies, CI files, lockfiles
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. ALWAYS additive: `CorpusEntry` is `frozen=True, extra="forbid"`. Both new fields MUST be `str | None = None`. Every one of the 51 rows already on disk in `.gzkit/corpus/AGENTS.md.jsonl` MUST still load unchanged.
2. NEVER change the serialized bytes of a tombstone-free entry. `corpus_fingerprint()` hashes `Corpus.dumps()` (`rendition_store.py:56-64`), and `model_dump_json()` would emit `"supersedes":null,"retires":null` on every row — silently re-fingerprinting the whole corpus and flipping `gz validate --rendition-freshness` to drift on the very commit that lands this OBPI. Serialization MUST omit unset tombstone fields.
3. THE FOLD ALGEBRA IS PINNED HERE, NOT CHOSEN AT IMPLEMENTATION TIME. Implement exactly the nine clauses below; a naive last-write-wins toggle is explicitly refused because it renders retirement history ambiguous (ADR § Reversibility).
4. ALGEBRA 1 — ORDER. The total order over entries is position in the append log. There is no timestamp tiebreak; `ts` is provenance, never sequence.
5. ALGEBRA 2 — TARGETS. `retires` and `supersedes` each name exactly one entry id that appears STRICTLY EARLIER in the log. A forward reference, a self reference, or an unknown id is a load-time `ValueError`.
6. ALGEBRA 3 — EXCLUSIVITY. An entry MUST NOT populate both `retires` and `supersedes`. Populating both is a load-time `ValueError`.
7. ALGEBRA 4 — ROLES. `retires` marks a pure tombstone row: it contributes NO text to the effective view. `supersedes` marks a replacement row: it retires its target AND is itself a content row in the effective view.
8. ALGEBRA 5 — LIVENESS BY REVERSE PASS. `live(e) = not any(live(t) for t in tombstones targeting e)`. Because every tombstone strictly follows its target (Algebra 2), evaluating entries from LAST to FIRST resolves every dependency before it is read. This is a single reverse pass — NEVER a fixpoint iteration and NEVER unbounded recursion.
9. ALGEBRA 6 — UN-RETIREMENT IS RETIRING THE TOMBSTONE. Appending `T2` with `retires = <id of T1>` makes `live(T1)` false, which by Algebra 5 makes `live(X)` true again. All three rows remain in the raw log; retirement history is preserved, not overwritten.
10. ALGEBRA 7 — NO SILENT DOUBLE-RETIRE. At most one LIVE tombstone may target a given entry. A second live tombstone targeting the same entry is a load-time `ValueError`, so "retire twice" can never be silently read as "un-retire".
11. ALGEBRA 8 — PROJECTION. `effective_corpus(corpus)` returns, in append order, every entry where `live(e)` is true AND `e.retires is None`.
12. ALGEBRA 9 — IDEMPOTENCE. `effective_corpus(effective_corpus(c)) == effective_corpus(c)` for every corpus `c`.
13. NEVER mutate the raw log. `Corpus.append` returns a new corpus and `corpus_store.py` has no delete path; `effective_corpus()` is a pure projection over the loaded corpus (alternatives E and F are rejected).
14. ALWAYS route `tier_policy.invariant_entries()` through the effective view, so a retired invariant entry stops being on the 0-Kelvin floor.
15. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- [ ] `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md` — pre-mortem, WWHTBT, constraint archaeology, 2am-operator, reversibility, scope minimization.

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] `.gzkit/rules/tests.md` § REQ Scope Discipline — the three-kind proof-channel matrix this brief's Acceptance Criteria are tagged against

**Context:**

- [ ] ADR § Decision item 1 and § Consequences (Negative) #5 — `effective_corpus()` becoming a second source of truth is the failure with the WORST detection latency, because the symptom is a GREEN gate.
- [ ] `DESIGN_FORCING_FUNCTIONS.md` § 6 Reversibility — the tombstone row is the one genuinely one-way commitment in ADR-0.35.0.
- [ ] ADR § Alternatives E and F — hard-delete and in-place tier mutation, both rejected; do not re-litigate.
- [ ] `.gzkit/rules/models.md` — frozen Pydantic + `extra="forbid"` discipline for the additive fields.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/models/corpus.py` exists and declares `CorpusEntry` with `ConfigDict(frozen=True, extra="forbid")`
- [ ] `src/gzkit/content/tier_policy.py` exists and exposes `invariant_entries` / `assert_invariant_verbatim`
- [ ] `src/gzkit/schemas/corpus_entry.json` exists
- [ ] `.gzkit/corpus/AGENTS.md.jsonl` exists and loads (51 rows: 50 invariant, 1 compressible) — the additive-load regression fixture
- [ ] `tests/content/test_corpus_model.py` exists

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/corpus_store.py:26-45` — `load_corpus` returns the RAW corpus today; every consumer of it is a candidate one-line omission (pre-mortem #3)
- [ ] `src/gzkit/content/rendition_store.py:56-64` — `corpus_fingerprint` hashes `Corpus.dumps()`; read before touching serialization
- [ ] `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:66` — a raw-corpus consumer that OBPI-0.35.0-06 will repoint
- [ ] `src/gzkit/content/composer.py:59-60` — a raw-corpus consumer that OBPI-0.35.0-05 will repoint

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. -->

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --rendition-freshness
uv run gz validate --rendition-floor-coherence
```

## Demo

```bash
uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.models.corpus import effective_corpus; c = load_corpus(Path('.'), 'AGENTS.md'); print('raw', len(c.entries), 'effective', len(effective_corpus(c).entries))"
uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.models.corpus import effective_corpus; from gzkit.content.tier_policy import invariant_entries; print('invariant on the floor:', len(invariant_entries(load_corpus(Path('.'), 'AGENTS.md'))))"
uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.rendition_store import corpus_fingerprint; print(corpus_fingerprint(load_corpus(Path('.'), 'AGENTS.md')))"
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID and exactly one kind tag
(ADR-0.0.59; `gz validate --req-kind-discipline`):
  [behavior]         -> proven ONLY by an @covers test in tests/**
  [support]          -> proven ONLY by a path-citing ledger event + structural validator
  [structural-fence] -> proven ONLY by a parent-ADR ## Boundary Invariants entry
-->

- [ ] REQ-0.35.0-01-01 [behavior]: Given a `CorpusEntry` JSONL line carrying neither `supersedes` nor `retires` (the shape of all 51 rows on disk today), when it is loaded through `Corpus.loads` and re-serialized through `Corpus.dumps`, then it round-trips BYTE-IDENTICALLY and `corpus_fingerprint()` is unchanged from its pre-OBPI value.
- [ ] REQ-0.35.0-01-02 [behavior]: Given a corpus whose entry populates `retires` with a forward id, its own id, an unknown id, or populates both `retires` and `supersedes`, when the corpus is loaded, then a `ValueError` is raised naming the offending entry id (Algebra 2 and 3).
- [ ] REQ-0.35.0-01-03 [behavior]: Given a corpus `[X, T1(retires=X)]`, when `effective_corpus()` folds it, then the result contains neither `X` nor `T1` — `X` because it is retired, `T1` because a pure tombstone contributes no text (Algebra 4 and 8).
- [ ] REQ-0.35.0-01-04 [behavior]: Given a corpus `[X, T1(retires=X), T2(retires=T1)]`, when `effective_corpus()` folds it, then `X` is LIVE again and neither tombstone appears — un-retirement is retiring the tombstone, resolved by the single reverse pass, and all three rows remain in the raw log (Algebra 5 and 6).
- [ ] REQ-0.35.0-01-05 [behavior]: Given a corpus `[X, S1(supersedes=X)]`, when `effective_corpus()` folds it, then `S1` IS present in the effective view and `X` is not — a replacement row is a content row, unlike a pure tombstone (Algebra 4).
- [ ] REQ-0.35.0-01-06 [behavior]: Given a corpus containing two LIVE tombstones targeting the same entry, when it is loaded, then a `ValueError` is raised — a double-retire is never silently folded into an un-retirement (Algebra 7).
- [ ] REQ-0.35.0-01-07 [behavior]: Given any corpus `c`, when `effective_corpus()` is applied twice, then the result equals applying it once, and entry order is preserved as append order (Algebra 8 and 9).
- [ ] REQ-0.35.0-01-08 [behavior]: Given a corpus in which an `invariant`-tier entry has been retired by an appended tombstone, when `tier_policy.invariant_entries()` is called, then the retired entry is ABSENT from the returned floor and `assert_invariant_verbatim()` no longer demands its text in a rendition.
- [ ] REQ-0.35.0-01-09 [structural-fence]: Every corpus consumer in the repository reads the EFFECTIVE view, never the raw log — `tier_policy.invariant_entries()` (this OBPI), `rendition_floor_coherence.py` (OBPI-0.35.0-06), and `composer.py` (OBPI-0.35.0-05). A consumer left on the raw log resurrects retired canon behind a GREEN gate; the fence audits the complete consumer set at ADR closeout, after every OBPI that adds one has landed.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
