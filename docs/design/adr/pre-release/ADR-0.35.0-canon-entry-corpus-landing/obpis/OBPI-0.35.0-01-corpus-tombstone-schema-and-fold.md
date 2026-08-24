---
id: OBPI-0.35.0-01-corpus-tombstone-schema-and-fold
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 1
lane: Heavy
status: Completed
allowlist:
- src/gzkit/content/models/corpus.py
- src/gzkit/content/tier_policy.py
- src/gzkit/content/corpus_store.py
- src/gzkit/content/rendition_store.py
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
req_atomic:
# Declared 2026-08-24 at Stage 2, where the labor happened (GHI #590). REQ-01, -03
# and -08 are ABSENT from this list on purpose: each carried genuinely multi-step
# labor and was subdivided via `gz task start --seq next` instead.
#   REQ-01 -> seq 01/02/03: field+schema+identity, then the red-suite fix cycle,
#             then the hollow-fingerprint-test repair.
#   REQ-03 -> seq 01/02/03: the Algebra 8 projection; then the default-direction
#             witness added after task 2's review flipped `live.get(t, False)` to
#             `True`; then the refusal that REPLACED that default outright after the
#             Step-4b Codex adversary showed a `True` default does not merely fail
#             safe, it INVENTS an answer the algebra does not give. No default
#             survives -- `_liveness` now raises on an unresolved tombstone. Read the
#             first two entries as a record of labor, never as a description of
#             current behavior.
#   REQ-08 -> seq 01/02: the three D3 consumer repoints, then the direct
#             un-retirement witnesses for `retired_ids`/`live_entry_with_text`.
# The six below are one indivisible unit each -- one behavior, one covering test,
# authored in a single implementer cycle with no follow-on labor.
- REQ-0.35.0-01-02  # Algebra 2+3 load-time refusal: one validator branch set, one negative-test class.
- REQ-0.35.0-01-04  # Algebra 5+6 un-retirement: one reverse-pass assertion over one three-row fixture.
- REQ-0.35.0-01-05  # Algebra 4 role asymmetry: one projection filter, one fixture pair.
- REQ-0.35.0-01-06  # Algebra 7 double-retire refusal: one liveness-gated branch plus its legal-case contrast.
- REQ-0.35.0-01-07  # Algebra 8+9 idempotence and order: pure assertions over the fold already built for -03..-06.
- REQ-0.35.0-01-09  # STRUCTURAL-FENCE: zero labor in this OBPI by construction; proven by parent-ADR BI-01 at closeout.
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run gz validate --documents
- uv run gz validate --req-kind-discipline
- uv run gz validate --rendition-freshness
- uv run gz validate --rendition-floor-coherence
tasks:
  - TASK-0.35.0-01-01-01
  - TASK-0.35.0-01-02-01
  - TASK-0.35.0-01-03-01
  - TASK-0.35.0-01-04-01
  - TASK-0.35.0-01-05-01
  - TASK-0.35.0-01-06-01
  - TASK-0.35.0-01-07-01
  - TASK-0.35.0-01-08-01
  - TASK-0.35.0-01-09-01
  - TASK-0.35.0-01-01-02
  - TASK-0.35.0-01-01-03
  - TASK-0.35.0-01-03-02
  - TASK-0.35.0-01-08-02
  - TASK-0.35.0-01-03-03
---

# OBPI-0.35.0-01-corpus-tombstone-schema-and-fold: Corpus Tombstone Schema And Fold

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #1 - "`CorpusEntry.supersedes` / `.retires` fields + `effective_corpus()` fold (algebra specified, including retire-the-tombstone) + `tier_policy.invariant_entries()` reads the effective view"

**Status:** Completed

## Objective

Add two optional tombstone fields to `CorpusEntry` and ship `effective_corpus()` — a fold whose algebra is pinned in this brief, including retire-the-tombstone (un-retirement) — so retirement becomes an appended row rather than a deletion, and route `tier_policy.invariant_entries()` through the effective view so the invariant floor stops counting retired canon.

> **AMENDED 2026-08-18 (operator-ruled, GHI #822): this brief's content-surface
> attestation is renamed from "Gate 5" to CORPUS ATTESTATION.** Gate 5 names
> OBPI/ADR completion attestation (`ADR-0.0.36`) and nothing else; a build step
> wearing that name is the collision the transit/exchange/handoff fence forbids
> (operator ruling 2026-08-17, `AGENTS.md` § Operator Doctrine). The noun is
> `corpus`, not `rendition`, because the same ruling puts the attestable subject on
> the corpus and holds a rendition to be a Layer-3 derived view, "never the thing
> attested." Parent ADR § Decision carries the governing amendment. This brief's own
> `### Gate 5 (Human)` gate-covenant sections are UNCHANGED — those are the genuine
> Gate 5, on this OBPI's completion. Naming only; no REQ semantics change.

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
- `src/gzkit/content/corpus_store.py` — **read-only coupled surface** (AMENDED 2026-08-24, operator-approved).
  Not edited by this OBPI. Declared because REQ-0.35.0-01-01's covering test must load the real
  on-disk corpus through the production `load_corpus`, and `gz validate --brief-reconcile`'s
  neighborhood filter (`brief_reconcile.py:536-588`) correctly reports an undeclared import from
  `src/gzkit/content/` as `missing_in_brief`.
- `src/gzkit/content/rendition_store.py` — **read-only coupled surface** (AMENDED 2026-08-24, operator-approved).
  Not edited by this OBPI. REQ-2 names `corpus_fingerprint()` by name and the Discovery Checklist
  already required reading it at `:56-64`; the allowlist simply never declared it. Declaring it is
  what lets the covering test assert against the PRODUCTION function instead of a local
  reimplementation of its hash — the hollow-test defect the Stage-2 two-stage review caught.
- `src/gzkit/schemas/corpus_entry.json` — additive schema for the two optional fields
- `tests/content/test_corpus_model.py` — fold-algebra and additive-load tests
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-01-corpus-tombstone-schema-and-fold.md` — this brief's evidence sections

## Denied Paths

- `src/gzkit/commands/content/**` — the `retire` CLI surface (its corpus-attestation extension) is OBPI-0.35.0-02
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

### Step 4b — Independent Adversarial Validation

**Adversary:** Codex (OpenAI) — tier 1, cross-vendor. Run under ARB so the tier is
proven, not declared: `uv run gz arb step --name codexadversary -- codex exec ...`.
Tier-1 availability was checked first (`codex:setup` -> `ready: true`,
`loggedIn: true`), so tiers 2 and 3 were forbidden.

**Pass 1 — receipt `arb-step-codexadversary-fa5592c0de384832b028e97abbc2e89a`
(`exit_status: 0`). Verdict: REFUTED-WITH-CAVEATS.** Three findings:

1. **`_liveness()` was not semantically total over the domain it claimed.** The
   `live.get(t, True)` default did not merely fail safe — it INVENTED an answer the
   pinned algebra does not give. On `[T1(retires=X), X, T2(retires=T1)]` the recurrence
   gives `live(x) = True`, but the implementation returned `x` retired and folded to
   `[]`. Two prior same-vendor reviewers had examined this exact line and PASSED it,
   having verified only that the default fails safe on the one shape the test covered.
   **RESOLVED IN FLIGHT** — the default was removed outright; `_liveness` now raises
   `ValueError` naming the unresolved tombstone and the entry it targets. No fallback
   survives (`live[t]`, never `.get`).
2. **`corpus_store.append_entry` persists before validating**, so an invalid corpus
   reaches disk and is refused only on the next load. **ROUTED, not fixed** — GHI #875.
   `corpus_store.py` is a READ-ONLY coupled surface in this brief's operator-approved
   allowlist amendment; editing it would exceed that approval.
3. **The parent ADR pins the algebra in SEVEN bullets, not nine clauses.** The nine
   numbered clauses are this BRIEF's enumeration. **ACCEPTED** — an orchestrator
   framing error, corrected; no code implication.

**Pass 2 (re-validation of the fix) — receipt
`arb-step-codexadversary-30f8bbf371d44ff7a131f4ddcac44629` (`exit_status: 0`).
Verdict: NOT-REFUTED.** Evidence it produced:

- Algebra 9 intact under the refusal — the risk a wrongly-keyed fix would have created.
  An exhaustive small-state sweep: **1069 enumerated unique-id logs, 561 load-accepted,
  508 refused by Algebra 7, 0 idempotence failures, 0 caller crashes on load-accepted
  logs.**
- Refusal keyed correctly: an absent edge KEY is legitimate projection residue and is
  ignored; an unresolved edge-list VALUE raises. Both cases exercised.
- Test honesty: against an in-memory reconstruction of the pre-fix helper, 2 of the 3
  added tests FAIL (genuine witnesses) and the third passes by design as the
  preservation fence. The removed test "encoded the now-rejected invented fallback and
  was genuinely obsolete; its exact shape is retained with the stronger `ValueError`
  assertion."
- No regression: 79 -> 55, floor 54, fingerprint unchanged, full suite `Ran 8803 tests
  ... OK`, process exit 0.
- Repository preservation: before/after `git status` snapshots byte-identical
  (`8b496100...`). Independently confirmed by the orchestrator — the working-tree diff
  SHA-256 was `77157c51...` before and after the run.

**Adversary's Weakest point (recorded, not dismissed):** *"`Corpus` still represents
both validated logs and dangling projected views, so correctness depends on preserving
the subtle distinction between an absent edge key and an unresolved edge-list value;
the new contrast test is the main fence against that distinction drifting."* That fence
is `test_a_dangling_supersedes_target_is_not_an_unresolved_tombstone`.

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


Un-retirement — the behavior that did not work before this OBPI and fails silently under the flat form:

    uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.models.corpus import effective_corpus; c = load_corpus(Path('.'), 'AGENTS.md'); print('raw', len(c.entries), 'effective', len(effective_corpus(c).entries))"
    raw 79 effective 55

    uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.tier_policy import invariant_entries; print('invariant on the floor:', len(invariant_entries(load_corpus(Path('.'), 'AGENTS.md'))))"
    invariant on the floor: 54

    uv run python -c "from pathlib import Path; from gzkit.content.corpus_store import load_corpus; from gzkit.content.rendition_store import corpus_fingerprint; print(corpus_fingerprint(load_corpus(Path('.'), 'AGENTS.md')))"
    8459d30b0fbacc8e5e33da8dd391f9355daef6ac1912d5c175f53888bd3f92de

On the synthetic chain `[X, T1(retires=X), T2(retires=T1)]` the fold returns `['x']` — X is LIVE again while all three rows remain in the raw log. The flat `retired_ids()` returned `{X, T1}` and left X retired forever.

Attestation receipts: arb-step-unittest-fce01219ac674796b47ac6fb157ec3be (8803/8803, exit_status 0), arb-ruff-2a3a3ac6999948719a5ae9da75f53c5e, arb-step-typecheck-171fe83e0aa54fbb831bf308c0f72fca, arb-step-mkdocs-bad10d75145b4d84bafdd5820c485e72, arb-step-codexadversary-30f8bbf371d44ff7a131f4ddcac44629 (NOT-REFUTED).

### Implementation Summary


- Additive schema: `CorpusEntry.supersedes: str | None = None`, appended to `POST_BASELINE_IDENTITY_FIELDS` so unset tombstone fields are omitted from `Corpus.dumps()`. The corpus fingerprint is unchanged at 8459d30b0fbacc8e5e33da8dd391f9355daef6ac1912d5c175f53888bd3f92de and `gz validate --rendition-freshness` stays green on the landing commit, which brief REQ-2 named as the trap.
- Load-time algebra: `validate_tombstone_algebra` enforces Algebra 2 (target strictly earlier), Algebra 3 (exclusivity) and Algebra 7 (at most one LIVE tombstone per target) inside `Corpus.loads`. Deliberately NOT a Pydantic model validator — that shape makes Algebra 9 unsatisfiable, because a folded view legitimately carries a `supersedes` row whose target the fold removed.
- The fold: `_tombstones_by_target` registers an edge for BOTH pointers; `_liveness` resolves `live(e) = not any(live(t) for t in tombstones targeting e)` in ONE `reversed(entries)` pass — no fixpoint, no recursion; `effective_corpus` projects every row where `live(e)` and `e.retires is None`, in append order.
- Refusal over invention: `_liveness` has NO default. An unresolved tombstone raises `ValueError` naming both ids. This replaced a `live.get(t, True)` fallback after the Step-4b adversary showed the fallback invents an answer the algebra does not give.
- Consumer repoint (D3): `tier_policy.invariant_entries()`, `Corpus.retired_ids()` and `Corpus.live_entry_with_text()` all read the fold. `retired_ids()` was redefined in place rather than deleted, which repoints `commands/content/retire.py`'s guard without editing that denied path.
- Allowlist amended (operator-approved): `corpus_store.py` and `rendition_store.py` declared READ-ONLY coupled surfaces so REQ-01's covering test asserts against the PRODUCTION `corpus_fingerprint` instead of a local re-implementation.
- Labor attribution: REQ-01, -03 and -08 subdivided (seq 02/03) because their labor was genuinely multi-step; the other six declared `req_atomic:` with per-REQ rationale.
- Tests added: 84 -> 98 in the scoped set; full suite 8794 -> 8803.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.35.0-01 lands the corpus tombstone fold. `supersedes` added additively with the corpus fingerprint unchanged at 8459d30b0fbacc8e5e33da8dd391f9355daef6ac1912d5c175f53888bd3f92de; 8803/8803 tests pass (receipt arb-step-unittest-fce01219ac674796b47ac6fb157ec3be), lint clean (arb-ruff-2a3a3ac6999948719a5ae9da75f53c5e), typecheck clean (arb-step-typecheck-171fe83e0aa54fbb831bf308c0f72fca), docs clean (arb-step-mkdocs-bad10d75145b4d84bafdd5820c485e72). The algebra is implemented as a single reverse pass with Algebra 2/3/7 failing closed at Corpus.loads; all three liveness consumers repointed off the flat form; the real corpus folds 79 raw -> 55 effective with the invariant floor unchanged at 54. A tier-1 cross-vendor adversary (Codex, ARB-proven) refuted the `live.get(t, True)` default as inventing an answer the pinned algebra does not give (receipt arb-step-codexadversary-fa5592c0de384832b028e97abbc2e89a); the default was removed in flight and re-validation returned NOT-REFUTED over an exhaustive 1069-log sweep with 0 idempotence failures (receipt arb-step-codexadversary-30f8bbf371d44ff7a131f4ddcac44629). Three findings routed rather than excused: GHI #873, #874, #875.
- Date: 2026-08-24

---

**Date Completed:** 2026-08-24

**Evidence Hash:** -
