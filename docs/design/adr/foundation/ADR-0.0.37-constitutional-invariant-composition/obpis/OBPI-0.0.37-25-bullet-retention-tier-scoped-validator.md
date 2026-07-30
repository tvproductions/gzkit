---
id: OBPI-0.0.37-25-bullet-retention-tier-scoped-validator
parent: ADR-0.0.37-constitutional-invariant-composition
item: 25
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit — one behavior/support
# surface apiece (invariant-verbatim, compressible-receipt, compressible-no-receipt,
# coupled-ADR-amendment, surface-fidelity-wiring, docs); none decomposes into
# parallel seq=02+ sub-tasks (ADR-0.0.64 exemption).
req_atomic:
  - REQ-0.0.37-25-01
  - REQ-0.0.37-25-02
  - REQ-0.0.37-25-03
  - REQ-0.0.37-25-04
  - REQ-0.0.37-25-05
  - REQ-0.0.37-25-06
---

# OBPI-0.0.37-25-bullet-retention-tier-scoped-validator: ADR-0.0.33 Bullet-Retention Tier-Scoped Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #25 - "OBPI-0.0.37-25 — ADR-0.0.33 bullet-retention tier-scoped validator (flip `--bullet-retention` from whole-surface verbatim grep to tier-aware: verbatim on invariant tier; advisor-QC receipt + attestation on compressed tiers; lands in the same commit-window as the coupled ADR-0.0.33 Invariant-1 amendment)"

**Status:** Completed

## Objective

Flip `gz validate --bullet-retention` from a **whole-surface verbatim grep** to **tier-aware enforcement**, realizing the already-authored ADR-0.0.33 § Amendment (2026-06-03):

- **Invariant tier** (`tier: invariant` corpus entries): verbatim-presence contract unchanged and fail-closed — these render verbatim at every setpoint, and the validator asserts their exact presence.
- **Compressible tier**: retention is satisfied by the **advisor-QC information-retention receipt + operator attestation** for the committed rendition (OBPI-24, ADR-pool.llm-as-judge-doctrine, universal Gate 5), **NOT** by verbatim-bullet substring. The invariant preserved is *no binding information is lost* (witnessed by receipt + attestation), not *every byte identical*.

This OBPI lands the validator change **in the same commit-window** as the coupled ADR-0.0.33 Invariant-1 amendment, keeping `--bullet-retention` wired into `--surface-fidelity` / `gz check` throughout (ADR-0.0.33 Anti-Pattern #1). Editing a Validated foundation invariant's enforcement is a **real attested amendment**, never a silent validator edit (parent ADR Alternative #18; ADR-0.0.33 is the doctrine-drift guard this respects).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Changing a validator's fail-closed semantics + attesting an amendment to a Validated foundation ADR (ADR-0.0.33, heavy) → Heavy. Gate 5 human attestation is mandatory (foundation/heavy; no self-close) and is the attestation point for the ADR-0.0.33 amendment.

## Allowed Paths

- `src/gzkit/governance/trust_audits/bullet_retention.py` — EDIT: flip from whole-surface verbatim grep to tier-aware enforcement (verbatim for invariant tier; advisor-QC receipt + attestation witness for compressible tier; tier read from the corpus)
- `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md` — EDIT: correct the § Amendment "Mechanical coupling" realizer reference (currently mis-cites OBPI-0.0.37-18 — see § Tracked Defects) to OBPI-0.0.37-25, and record the amendment's Gate-5 attestation in the Attestation Block (the coupled attested amendment)
- `tests/governance/test_bullet_retention.py` — EDIT: add tier-scoped BEHAVIOR tests (invariant-verbatim fail-closed; compressible-with-receipt clean; compressible-without-receipt fail-closed) while preserving the existing ADR-0.0.33-01 coverage
- `docs/user/manpages/validate.md` — EDIT: document the tier-scoped `--bullet-retention` behavior
- `data/behave_coverage_waivers.json` — EDIT: OBPI-level behave-coverage waiver for the SUPPORT doc/amendment REQs (validator behavior is unit-proven; no new CLI verb)
- `src/gzkit/governance/trust_audits/__init__.py` — READ-coupled re-export surface: `validate_bullet_retention` is reached through this package re-export and the preserved REQ-0.0.33-01-04 test imports it from here. Unmodified by this OBPI; declared so the brief-reconcile neighborhood filter (GHI #419) sees the genuine coupled surface the test exercises.
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-25-bullet-retention-tier-scoped-validator.md` — active brief and evidence record
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only, for intent and the 1:1 checklist sync)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/content/models/corpus.py`, `src/gzkit/content/vendors.py` — tier model + setpoint read-only
- `src/gzkit/content/advisor_qc.py`, `src/gzkit/commands/content/advise_rendition.py` — the advisor-QC receipt *producer* is OBPI-24; this validator only *reads* the receipt
- The legal-token enum / other ADR-0.0.33 invariants (surface-weight, pointer-anchors, scenario-reachability) — only Invariant 1 is tier-scoped here
- Silently editing the validator without the coupled ADR-0.0.33 attested amendment — forbidden (parent ADR Alternative #18; doctrine drift)
- `.gzkit/ledger.jsonl` — never hand-edited
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT [BEHAVIOR]: For `tier: invariant` content, `gz validate --bullet-retention` MUST assert verbatim presence in the rendered surface and exit 3 (fail-closed) on any absent/altered invariant text — the Era-1 contract preserved for the invariant tier.
1. REQUIREMENT [BEHAVIOR]: For `tier: compressible` content, `gz validate --bullet-retention` MUST treat retention as satisfied by a present, valid advisor-QC information-retention receipt + operator attestation for the committed rendition — a compressible entry that is reworded/combined (not verbatim) but carries the receipt+attestation MUST NOT fail.
1. REQUIREMENT [BEHAVIOR]: For `tier: compressible` content WITHOUT a valid advisor-QC receipt + attestation, `gz validate --bullet-retention` MUST exit 3 (retention is unwitnessed) — the compressible tier is not an unconditional escape from retention.
1. REQUIREMENT [SUPPORT]: The coupled ADR-0.0.33 Invariant-1 amendment MUST be realized in the same commit-window: the § Amendment "Mechanical coupling" realizer reference is corrected to OBPI-0.0.37-25 and the amendment is recorded as attested in ADR-0.0.33's Attestation Block — proven by `uv run gz validate --documents` plus the `artifact_edited` event for ADR-0.0.33.
1. REQUIREMENT [SUPPORT]: `--bullet-retention` MUST remain wired into `--surface-fidelity` and `gz check` throughout the change (ADR-0.0.33 Anti-Pattern #1) — proven by `uv run gz validate --surface-fidelity` (exit 0 on coherent canon) plus the validator's participation in `gz check`.
1. REQUIREMENT [SUPPORT]: `docs/user/manpages/validate.md` MUST document the tier-scoped `--bullet-retention` behavior and the reference MUST resolve — proven by `uv run gz validate --cli-alignment` plus the `artifact_edited` event for the manpage.
1. NEVER: edit the validator's fail-closed semantics without the coupled ADR-0.0.33 attested amendment; weaken the invariant-tier verbatim contract; or treat the compressible tier as an unconditional retention escape.
1. ALWAYS: reconcile the brief with the parent ADR (`uv run gz validate --brief-reconcile`) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The contract: "ADR-0.0.33 bullet-retention tier-scoped validator (flip `--bullet-retention` from whole-surface verbatim grep to tier-aware: verbatim on invariant tier; advisor-QC receipt + attestation on compressed tiers; lands in the same commit-window as the coupled ADR-0.0.33 Invariant-1 amendment)" (Checklist item #25; § Decision Re-Alignment 2026-06-03 "ADR-0.0.33 reconciliation (coupled attested amendment)").
- [ ] Parent ADR § Decision Re-Alignment "ADR-0.0.33 reconciliation" + Alternative #18 — why a silent validator edit is forbidden and the amendment must be attested.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md` § Amendment (lines ~92-124) — the authored tier-scoped amendment this OBPI realizes + the mis-cited realizer to correct
- [ ] `.gzkit/rules/adr-audit.md` § "Legitimate-authoring exemptions" — the covers-backfill heuristic (avoid cosmetic `@covers`; re-derive assertions)
- [ ] `AGENTS.md` § DO IT RIGHT 1a (coupled-surface coherence) — the validator + ADR amendment must land together

**Context:**

- [ ] OBPI-0.0.37-23 (invariant tier) — the tier-policy / verbatim-survival surface the invariant-tier branch coordinates with
- [ ] OBPI-0.0.37-24 (advisor-QC) — the producer of the advisor-QC receipt the compressible-tier branch reads (sequenced before this OBPI)
- [ ] OBPI-0.0.37-19 (corpus) — the `.gzkit/corpus/` store the validator reads for tier designations (surface-named `.jsonl` files, e.g. `.gzkit/corpus/AGENTS.md.jsonl`)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/governance/trust_audits/bullet_retention.py` exists with `validate_bullet_retention(project_root) -> list[ValidationError]` (the Era-1 whole-surface grep to flip)
- [ ] `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md` exists with § Amendment (2026-06-03) authored
- [ ] `src/gzkit/content/models/corpus.py` exists with `CorpusEntry.tier` (OBPI-18) — the tier source
- [ ] `src/gzkit/governance/trust_audits/attestation_receipts.py` exists — the advisor-QC receipt validation surface the compressible branch reuses
- [ ] `tests/governance/test_bullet_retention.py` exists (the existing ADR-0.0.33-01 coverage to preserve)

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/trust_audits/bullet_retention.py` — the current whole-surface grep (`_parse_scorecard`, `_collect_surface_corpus`, `_normalize`, `_ENFORCED_CLASSES`) — the seam to make tier-aware
- [ ] `src/gzkit/governance/trust_audits/attestation_receipts.py` — `arb-step-*` receipt lookup/validation the compressible branch reuses for the QC witness
- [ ] `src/gzkit/content/corpus_store.py` + `src/gzkit/content/models/corpus.py` — how to read tier per corpus entry
- [ ] `tests/governance/test_bullet_retention.py` + `tests/governance/test_setpoint_coherence.py` — the trust_audits test convention (tempdir, `@covers`, REQ-facet-per-class)
- [ ] `src/gzkit/cli/parser_maintenance.py` (~627-631) + `src/gzkit/commands/validate_cmd.py` (~388) — the existing `--bullet-retention` registration (no flag change needed; behavior change only)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment (RED first for each of REQ-01/02/03)
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/user/manpages/validate.md` documents the tier-scoped behavior; ADR-0.0.33 amendment realizer corrected

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass / waived: REQ-01/02/03 are unit-proven validator behavior; REQ-04/05/06 are SUPPORT. Behave coverage waived per the OBPI-level waiver (no new CLI verb; behavior is validator-internal).

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (mandatory; foundation/heavy; no self-close) — this is the ADR-0.0.33 amendment's attestation point

## Verification

```bash
uv run gz validate --brief-reconcile
uv run gz validate --bullet-retention
uv run gz validate --surface-fidelity
uv run gz validate --documents
uv run gz validate --cli-alignment
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI
uv run -m unittest tests.governance.test_bullet_retention -v
```

## Demo

```bash
# Invariant-tier content must be verbatim — absence fails closed
uv run gz validate --bullet-retention
# -> exit 3 if an invariant-tier entry's text is missing from the rendered surface

# Compressible-tier content with a valid advisor-QC receipt + attestation passes
# even when reworded/combined (not verbatim); without the receipt it fails closed.
uv run gz validate --surface-fidelity   # --bullet-retention stays wired in throughout
```

## Acceptance Criteria

- [ ] REQ-0.0.37-25-01 [BEHAVIOR]: Given an invariant-tier entry absent/altered in the rendered surface, when `gz validate --bullet-retention` runs, then it exits 3 (verbatim contract preserved for the invariant tier). Proof: `@covers`-decorated test in `tests/governance/test_bullet_retention.py`.
- [ ] REQ-0.0.37-25-02 [BEHAVIOR]: Given a compressible-tier entry that is reworded/combined (not verbatim) but carries a valid advisor-QC receipt + operator attestation, when `gz validate --bullet-retention` runs, then it does NOT fail on that entry. Proof: `@covers`-decorated test.
- [ ] REQ-0.0.37-25-03 [BEHAVIOR]: Given a compressible-tier entry with no valid advisor-QC receipt + attestation, when `gz validate --bullet-retention` runs, then it exits 3 (retention unwitnessed). Proof: `@covers`-decorated test.
- [ ] REQ-0.0.37-25-04 [SUPPORT]: Given the coupled amendment, when the OBPI is complete, then ADR-0.0.33's § Amendment realizer reference is corrected to OBPI-0.0.37-25 and the amendment is recorded attested in ADR-0.0.33's Attestation Block — proven by `uv run gz validate --documents` plus the `artifact_edited` event for ADR-0.0.33.
- [ ] REQ-0.0.37-25-05 [SUPPORT]: Given the composite scope, when the OBPI is complete, then `--bullet-retention` remains wired into `--surface-fidelity` and `gz check` — proven by `uv run gz validate --surface-fidelity` (exit 0 on coherent canon) plus the `artifact_edited` event accounting for the validator module's edit within the `--surface-fidelity` composite.
- [ ] REQ-0.0.37-25-06 [SUPPORT]: Given the operator docs, when the OBPI is complete, then `docs/user/manpages/validate.md` documents the tier-scoped behavior and the reference resolves — proven by `uv run gz validate --cli-alignment` plus the `artifact_edited` event for the manpage.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Behave waived for this OBPI — see Gate 4 above and data/behave_coverage_waivers.json
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane — also the ADR-0.0.33 amendment attestation
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


uv run gz validate --bullet-retention exits 0 on live coherent canon (the one compressible corpus entry backs no enforced bullet → all enforced bullets route through the invariant verbatim path; no regression). Behavioral divergence proven by tests: test_compressible_reworded_with_valid_witness_passes (a reworded surface the old grep would fail passes with a valid witness) and test_compressible_without_any_witness_fails_closed (fails closed without one). Full suite 6178/6178 (arb-step-unittest-3c19e2972bda40e39427c559497700e2), lint (arb-ruff-92d5ec92e457494fb938df41d51c76ba), typecheck (arb-step-typecheck-a84e2c556dcf4acfa0e63087102c4ca5), mkdocs --strict (arb-step-mkdocs-46be5634cb064aa8880c773d166884b3) all exit 0; gz covers behavior_uncovered_reqs=0.

### Implementation Summary


- Validator: src/gzkit/governance/trust_audits/bullet_retention.py — flipped whole-surface verbatim grep → tier-aware; tier resolved from .gzkit/corpus/*.jsonl (_resolve_tier; unknown→invariant fallback); invariant tier keeps Era-1 verbatim substring contract; compressible tier witnessed by latest rendition_advisor_verdict event + arb-step-judge-* receipt (exit_status==0, prefix-guarded)
- Tests: tests/governance/test_bullet_retention.py — 10 new tier-scoped tests (3 classes); all 18 ADR-0.0.33-01 tests preserved (28 total)
- Coupled amendment: ADR-0.0.33 § Amendment realizer cite corrected OBPI-0.0.37-18→OBPI-0.0.37-25 + realizer-correction note + tier-scoped amendment row in Attestation Block
- Docs: docs/user/manpages/validate.md tier-scoped behavior (per-tier contract table + exit-code matrix); OBPI-level behave waiver in data/behave_coverage_waivers.json
- Date completed: 2026-06-15
- Attestation status: operator-attested (attest completed); foundation/heavy; ADR-0.0.33 Invariant-1 amendment Gate-5 point
- Defects noted: fixed in-flight insights-schema defect (appended improvement record had evidence as string; InsightRecord requires list[str]) — caught by full unittest sweep, fixed, re-verified green

## Tracked Defects

**ADR-0.0.33 amendment realizer mis-citation (live doctrine drift, this OBPI corrects it).** ADR-0.0.33's § Amendment (2026-06-03) "Mechanical coupling" paragraph states the tier-scoped flip is *"realized by OBPI-0.0.37-18"* and *"attested at OBPI-0.0.37-18's Gate 5."* That is incorrect: OBPI-0.0.37-18 was the append-only corpus **model** (attested-complete) and did NOT flip `--bullet-retention` — the validator on disk is still the Era-1 whole-surface grep. The actual realizer is **this OBPI (OBPI-0.0.37-25)**, per parent ADR Checklist item #25. This OBPI corrects the realizer reference and lands the validator flip + amendment attestation in one commit-window. Surfaced per Behavior Rule Always #9 (name the inconsistency; do not silently resolve); confirm the correction at Stage 1 brief-reconcile and Gate 5.

**24 ↔ 25 receipt-producer dependency.** The compressible-tier branch reads the advisor-QC receipt produced by OBPI-0.0.37-24 (sequenced before this OBPI). If 24 has not landed, 25's compressible-branch tests use receipt fixtures and the real wiring is confirmed at brief-reconcile.

_No further defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.37-25 tier-scoped bullet-retention validator verified: gz validate --bullet-retention flipped from whole-surface verbatim grep to tier-aware enforcement (invariant tier keeps the Era-1 verbatim contract; compressible tier witnessed by the latest rendition_advisor_verdict event + arb-step-judge-* receipt exit_status==0, prefix-guarded; unknown-tier→invariant conservative fallback), realizing the ADR-0.0.33 § Amendment 2026-06-03 and landed in the same commit-window as the coupled amendment (realizer cite corrected OBPI-18→OBPI-25; tier-scoped amendment row recorded in ADR-0.0.33 Attestation Block — this IS that amendment's Gate-5 attestation, foundation/heavy). Live canon stays green (the one compressible corpus entry backs no enforced bullet). 6178/6178 unittest (arb-step-unittest-3c19e2972bda40e39427c559497700e2), lint (arb-ruff-92d5ec92e457494fb938df41d51c76ba), typecheck (arb-step-typecheck-a84e2c556dcf4acfa0e63087102c4ca5), mkdocs --strict (arb-step-mkdocs-46be5634cb064aa8880c773d166884b3) all exit 0; gz covers behavior_uncovered_reqs=0; spec-reviewer PASS + quality-reviewer COHERENT (both-flagged judge-prefix minor fixed + 2 latest-governs tests added).
- Date: 2026-06-15

---

**Date Completed:** 2026-06-15

**Evidence Hash:** -
