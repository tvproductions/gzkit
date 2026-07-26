---
id: OBPI-0.0.52-07-tier2-pipeline-and-promotion-surface
parent: ADR-0.0.52-artifact-staleness-propagation
item: 7
lane: Heavy
status: Draft
allowlist:
- src/gzkit/governance/propagation/tier2.py
- src/gzkit/governance/propagation/tfidf_prefilter.py
- src/gzkit/governance/propagation/judge_call.py
- src/gzkit/governance/propagation/interactive_review.py
- src/gzkit/governance/propagation/anti_theatre.py
- src/gzkit/commands/adr_propagation_cmd.py
- tests/governance/test_propagation_tier2.py
- tests/governance/test_propagation_interactive.py
- tests/governance/test_propagation_anti_theatre.py
- tests/governance/test_propagation_retry_tier2.py
- docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md
reqs:
- REQ-0.0.52-07-01
- REQ-0.0.52-07-02
- REQ-0.0.52-07-03
- REQ-0.0.52-07-04
- REQ-0.0.52-07-05
- REQ-0.0.52-07-06
- REQ-0.0.52-07-07
- REQ-0.0.52-07-08
- REQ-0.0.52-07-09
verification:
- uv run gz lint
- uv run gz typecheck
- uv run -m unittest tests.governance.test_propagation_tier2 tests.governance.test_propagation_interactive tests.governance.test_propagation_anti_theatre tests.governance.test_propagation_retry_tier2 -v
---

# OBPI-0.0.52-07-tier2-pipeline-and-promotion-surface: Tier 2 pipeline and promotion surface (HARD BLOCKED on ADR-0.0.39)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #7 — "HARD BLOCKED on ADR-0.0.39 reaching `Proposed` with named judge-contract surface locked. Tier 2 pipeline — TF-IDF prefilter + LLM-as-judge ranker consuming 0.0.39 framework; batch-table interactive promotion surface with mechanical anti-theatre defenses (refuse identical reasons, require per-candidate identifier references); `propagation_candidates_reviewed` event; graceful degradation on judge unreachability via `judge_unreachable_reason`; `propagation retry-tier2` recovery verb"

**Status:** Draft (HARD BLOCKED — see Prerequisites)

## Objective

Implement the Tier 2 advisory candidate scan that fires at ADR closeout (NOT per-OBPI). TF-IDF prefilter narrows the corpus; LLM-as-judge ranker (consuming ADR-0.0.39's judge contract surface) scores plausibility; operator reviews candidates in a batch-table interactive surface with mechanical anti-theatre defenses; promotions enter the affected-set with operator attestation. Graceful degradation when the judge is unreachable. Add `propagation retry-tier2` for after-the-fact retry. **This OBPI cannot start until ADR-0.0.39 reaches `Proposed` with its named judge-contract subsection locked.**

## Lane

**Heavy** — New stochastic surface added to a fail-closed governance pipeline; new CLI verb (`propagation retry-tier2`); new interactive operator-facing UI.

## Allowed Paths

- `src/gzkit/governance/propagation/tier2.py` — **PRIMARY:** Tier 2 pipeline orchestration (prefilter → judge → promotion)
- `src/gzkit/governance/propagation/tfidf_prefilter.py` — TF-IDF corpus build + top-K candidate narrowing (stdlib-first)
- `src/gzkit/governance/propagation/judge_call.py` — LLM-as-judge call site consuming ADR-0.0.39's judge contract surface
- `src/gzkit/governance/propagation/interactive_review.py` — batch-table promotion UI (Rich-based)
- `src/gzkit/governance/propagation/anti_theatre.py` — copy-paste defense (refuse identical reason strings), per-candidate identifier-reference enforcement
- `src/gzkit/commands/adr_propagation_cmd.py` — new `propagation` parent verb with `retry-tier2` subverb
- `tests/governance/test_propagation_tier2.py` — Tier 2 pipeline unit tests (with judge stubbed)
- `tests/governance/test_propagation_interactive.py` — batch-table UI tests
- `tests/governance/test_propagation_anti_theatre.py` — mechanical anti-theatre defense tests
- `tests/governance/test_propagation_retry_tier2.py` — retry verb tests
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)
- ADR-0.0.39's judge-contract subsection — read-only consumer

## Denied Paths

- Paths not listed in Allowed Paths
- ADR-0.0.39 implementation surfaces (read-only consumer; never modify)
- Tier 1 surfaces (OBPI-03)
- Validator scopes (OBPI-05)

## Creates These Files

- `src/gzkit/governance/propagation/tier2.py` — **CREATE** Tier 2 pipeline orchestration
- `src/gzkit/governance/propagation/tfidf_prefilter.py` — **CREATE** TF-IDF corpus build + top-K narrowing
- `src/gzkit/governance/propagation/judge_call.py` — **CREATE** LLM-as-judge call site consuming ADR-0.0.39's judge contract
- `src/gzkit/governance/propagation/interactive_review.py` — **CREATE** batch-table promotion UI
- `src/gzkit/governance/propagation/anti_theatre.py` — **CREATE** copy-paste defense + per-candidate identifier-reference enforcement
- `src/gzkit/commands/adr_propagation_cmd.py` — **CREATE** new `propagation` parent verb with `retry-tier2` subverb
- `tests/governance/test_propagation_tier2.py` — **CREATE** Tier 2 pipeline unit tests
- `tests/governance/test_propagation_interactive.py` — **CREATE** batch-table UI tests
- `tests/governance/test_propagation_anti_theatre.py` — **CREATE** mechanical anti-theatre defense tests
- `tests/governance/test_propagation_retry_tier2.py` — **CREATE** retry verb tests

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Tier 2 fires ONLY on ADR-closeout triggers (NOT per-OBPI). OBPI-04's trigger wiring already gates this; this OBPI MUST NOT add per-OBPI Tier 2 invocation.
2. REQUIREMENT: TF-IDF prefilter MUST build the corpus from all active artifacts' Decision and Intent sections at trigger time; cosine similarity narrows to top-K (K from `data/staleness_propagation_thresholds.json`).
3. REQUIREMENT: LLM-as-judge call MUST consume ADR-0.0.39's named judge-contract surface (input shape, output shape, error semantics defined entirely by 0.0.39).
4. REQUIREMENT: Judge output MUST be `(plausibility_score: float ∈ [0,1], reasoning: str, impact_summary: str)` per candidate, validated against the Tier2Candidate Pydantic model from OBPI-02.
5. REQUIREMENT: Batch-table interactive surface MUST present all candidates above the display floor at once; operator promotes/rejects per candidate; `commit <attestation>` finalizes the review.
6. REQUIREMENT: Anti-theatre — `commit` MUST be refused if all promote/reject reasons are identical (copy-paste defense); MUST require rejection reasons to reference specific upstream or candidate identifiers.
7. REQUIREMENT: Promoted candidates MUST enter the affected-set with `source: semantic_scan`, `attested_by: <operator>`; promotion writes frontmatter `evaluation_stale` entry and emits `artifact_staleness_flagged` (per OBPI-04 atomic-transaction semantics).
8. REQUIREMENT: Always emit `propagation_candidates_reviewed` even when zero candidates were promoted — provenance discipline (the review happened, the ledger records what was considered).
9. REQUIREMENT: On judge unreachability (timeout, schema-invalid response, network error): emit `propagation_candidates_reviewed` with `reviews: []`, `judge_unreachable_reason: <reason>`, `operator_attestation: ""` (mechanical fallback, NOT operator-attested). Closeout proceeds with Tier 1 only.
<!-- gz-validate-skip: command-shape -->
10. REQUIREMENT: `propagation retry-tier2 <ADR-id>` MUST exist as a recovery verb that re-runs Tier 2 against the original trigger event; emits a new `propagation_candidates_reviewed` event (does NOT modify the prior one).

> STOP-on-BLOCKERS: ADR-0.0.39 MUST be at `Proposed` status with its named "judge contract surface" subsection locked. If 0.0.39 is still in pre-`Proposed` status, halt this OBPI and surface the prerequisite to the operator. Mock judges and stubs are explicitly forbidden by parent ADR § Alternatives Considered #8.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"HARD BLOCKED on ADR-0.0.39 reaching `Proposed` with named judge-contract surface locked. Tier 2 pipeline — TF-IDF prefilter + LLM-as-judge ranker consuming 0.0.39 framework; batch-table interactive promotion surface with mechanical anti-theatre defenses"*.
- [ ] Parent ADR § Decision / "Tier 2 — Advisory candidate scan" — full spec.
- [ ] Parent ADR § Decision / "Tier 2 anti-theatre defenses" — copy-paste defense, per-candidate identifier-reference rule, tripwire receipt.
- [ ] Parent ADR § Decision / "2am operational discipline" — judge graceful-degradation contract.
- [ ] Parent ADR § Consequences/Negative items 3, 4 — Tier 2 stochastic-input risk and theatre failure mode.

**Governance:**

- [ ] ADR-0.0.39 § Decision / judge-contract-surface subsection — input/output shape, error semantics, rate-limit discipline.
- [ ] `.gzkit/rules/cli.md` — Heavy-Lane Trigger; new subcommand registration ceremony.

**Prerequisites:**

- [ ] **ADR-0.0.39 MUST be `Proposed` with named judge-contract surface subsection locked.** Check status before proceeding.
- [ ] OBPI-0.0.52-02 (Pydantic models including `Tier2Candidate`, `CandidateReview`, `PropagationCandidatesReviewedEvent`) has landed.
- [ ] OBPI-0.0.52-04 (trigger wiring + `tx_id` semantics) has landed.

**Existing Code:**

- [ ] Existing Rich-based interactive surfaces in the codebase reviewed for batch-table conventions.
- [ ] Any existing LLM-call site under ADR-0.0.39 framework reviewed for call-site patterns.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests derived from brief acceptance criteria
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] BDD scenarios pass (full coverage in OBPI-09)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded — REQUIRED (stochastic surface in governance pipeline)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_propagation_tier2 tests.governance.test_propagation_interactive tests.governance.test_propagation_anti_theatre tests.governance.test_propagation_retry_tier2 -v
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# Closeout with Tier 2 fire (requires ADR-0.0.39 Proposed)
uv run gz closeout ADR-0.0.X
# Interactive batch-table surfaces; operator promotes/rejects per candidate
# Expected ledger entry: propagation_candidates_reviewed

# Anti-theatre defense: identical reason strings rejected
# (in interactive: all promote/reject reasons match → [commit] refused)

# Graceful degradation: simulate judge unreachable
GZ_TIER2_FORCE_JUDGE_UNREACHABLE=1 uv run gz closeout ADR-0.0.Y
# Expected: propagation_candidates_reviewed with judge_unreachable_reason set;
#           closeout proceeds with Tier 1 only

# Retry after degraded run
uv run gz adr propagation retry-tier2 ADR-0.0.Y
# Expected: new propagation_candidates_reviewed event emitted
```

## Acceptance Criteria

- [ ] REQ-0.0.52-07-01: Given an ADR closeout, when Tier 2 fires, then the TF-IDF prefilter narrows the corpus to top-K candidates (K from threshold config) before any judge call.
- [ ] REQ-0.0.52-07-02: Given the LLM-as-judge call, when it executes, then it consumes ADR-0.0.39's named judge-contract surface (no stub, no mock; fail-closed at OBPI-start if 0.0.39 is not Proposed).
- [ ] REQ-0.0.52-07-03: Given an interactive review with N candidates above display floor, when the operator promotes some and rejects others, then `propagation_candidates_reviewed` is emitted with full promote/reject decisions on `commit <attestation>`.
- [ ] REQ-0.0.52-07-04: Given operator input with identical reason strings across all candidates, when `[commit]` is invoked, then the anti-theatre defense refuses commit with a clear message.
- [ ] REQ-0.0.52-07-05: Given a rejection reason that is generic ("no impact", "irrelevant") without referencing specific upstream or candidate identifiers, when commit is invoked, then the defense refuses the commit.
- [ ] REQ-0.0.52-07-06: Given promoted candidates, when commit completes, then each promoted artifact gets a frontmatter `evaluation_stale` entry with `source: semantic_scan`, `attested_by: <operator>`, paired by `tx_id` per OBPI-04 semantics.
- [ ] REQ-0.0.52-07-07: Given judge unreachability (timeout/schema-invalid/network), when Tier 2 fires, then `propagation_candidates_reviewed` is emitted with `reviews: []`, `judge_unreachable_reason: <reason>`, `operator_attestation: ""`; closeout proceeds.
- [ ] REQ-0.0.52-07-08: Given a degraded Tier 2 run, when `propagation retry-tier2 <ADR-id>` runs, then a NEW `propagation_candidates_reviewed` event is emitted (the prior one is preserved on the append-only ledger).
- [ ] REQ-0.0.52-07-09: Given the new subcommand registration, when `propagation --help` runs, then `retry-tier2` is listed with a canonical example.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle followed
- [ ] **Code Quality:** Lint, type checks clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** included
- [ ] **ADR-0.0.39 prereq:** Confirmed Proposed before starting

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

Before: silent-cross-conceptual-impact had no detection surface — declared edges and path overlap could not reach design-coupling that lived only in shared intent text. Now: every ADR closeout produces ranked candidates for operator review with mechanical anti-theatre defenses, attestation-gated promotion, and in-protocol graceful degradation when the judge is unreachable.

### Key Proof

<!-- gz-validate-skip: command-shape -->
```bash
$ uv run gz closeout ADR-0.0.X
Tier 2 candidate review — ADR-0.0.X closeout
  [batch-table with 3 candidates ranked by judge plausibility]
> P 1
> R 2 superseded last week (OBPI-0.0.F-02 no longer active)
> R 3 different concern (ADR-0.0.G's persona surface)
> commit "reviewed 3 candidates; promoted ADR-0.0.E (taxonomy overlap), rejected by specific identifier"
[OK] Candidate review complete. Promoted: 1. Rejected: 2.
Ledger: propagation_candidates_reviewed 9h0i1j2k... (tx_id 1l2m3n4o...)
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
