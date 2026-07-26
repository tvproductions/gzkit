---
id: OBPI-0.0.52-05-adr-eval-fresh-and-coherence-validators
parent: ADR-0.0.52-artifact-staleness-propagation
item: 5
lane: Heavy
status: Draft
allowlist:
- src/gzkit/governance/trust_audits/staleness_freshness.py
- src/gzkit/governance/trust_audits/staleness_coherence.py
- src/gzkit/governance/trust_audits/__init__.py
- src/gzkit/commands/validate_cmd.py
- src/gzkit/commands/quality.py
- src/gzkit/commands/adr_audit.py
- tests/governance/test_adr_eval_fresh.py
- tests/governance/test_staleness_coherence.py
- tests/governance/test_adr_audit_check_staleness.py
- docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md
reqs:
- REQ-0.0.52-05-01
- REQ-0.0.52-05-02
- REQ-0.0.52-05-03
- REQ-0.0.52-05-04
- REQ-0.0.52-05-05
- REQ-0.0.52-05-06
- REQ-0.0.52-05-07
verification:
- uv run gz lint
- uv run gz typecheck
- uv run gz validate --adr-eval-fresh
- uv run gz validate --staleness-coherence
- uv run gz check
- uv run -m unittest tests.governance.test_adr_eval_fresh tests.governance.test_staleness_coherence tests.governance.test_adr_audit_check_staleness -v
---

# OBPI-0.0.52-05-adr-eval-fresh-and-coherence-validators: adr-eval-fresh and staleness-coherence validators

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #5 — "`gz validate --adr-eval-fresh` validator + `gz validate --staleness-coherence` validator; default `gz check` bundle integration; `gz adr audit-check` augmentation to refuse `Completed` claim if any child OBPI carries unresolved flag"

**Status:** Draft

## Objective

Add two fail-closed validator scopes: `gz validate --adr-eval-fresh` (lifecycle-advance gate) and `gz validate --staleness-coherence` (Layer 1 vs Layer 2 drift detector). Integrate both into the default `gz check` bundle. Augment `gz adr audit-check` to refuse `Completed` claims when any child OBPI carries an unresolved `evaluation_stale` flag.

## Lane

**Heavy** — New CLI validator scopes and modifies `gz adr audit-check` semantics.

## Allowed Paths

- `src/gzkit/governance/trust_audits/staleness_freshness.py` — **PRIMARY:** `--adr-eval-fresh` implementation
- `src/gzkit/governance/trust_audits/staleness_coherence.py` — **PRIMARY:** `--staleness-coherence` implementation
- `src/gzkit/governance/trust_audits/__init__.py` — register both scopes
- `src/gzkit/commands/validate_cmd.py` — CLI flag wiring
- `src/gzkit/commands/quality.py` — `gz check` default bundle inclusion (the `check()` handler lives here)
- `src/gzkit/commands/adr_audit.py` — refuse Completed on stale child OBPI (the `audit-check` handler lives here)
- `tests/governance/test_adr_eval_fresh.py` — fail-close tests
- `tests/governance/test_staleness_coherence.py` — drift-detection tests
- `tests/governance/test_adr_audit_check_staleness.py` — completion-refusal tests
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Resolution verb (OBPI-06)
- Tier 2 surfaces (OBPI-07)
- Status surfaces (OBPI-08)

## Creates These Files

- `src/gzkit/governance/trust_audits/staleness_freshness.py` — **CREATE** `--adr-eval-fresh` implementation
- `src/gzkit/governance/trust_audits/staleness_coherence.py` — **CREATE** `--staleness-coherence` implementation
- `tests/governance/test_adr_eval_fresh.py` — **CREATE** fail-close tests
- `tests/governance/test_staleness_coherence.py` — **CREATE** drift-detection tests
- `tests/governance/test_adr_audit_check_staleness.py` — **CREATE** completion-refusal tests

Existing files modified: `src/gzkit/governance/trust_audits/__init__.py`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/commands/quality.py`, `src/gzkit/commands/adr_audit.py`.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz validate --adr-eval-fresh` MUST exit 3 when an artifact carries an unresolved `evaluation_stale` entry AND is the subject of an advancing action (closeout, attest, OBPI complete, audit-check); exit 0 otherwise.
2. REQUIREMENT: The validator MUST detect the advancing action from call-chain context; pure read commands (`gz status`, `gz state --json`) MUST NOT cause exit 3 (they surface flags via OBPI-08).
3. REQUIREMENT: Error messages MUST include the copy-paste-ready resolution command.
   <!-- gz-validate-skip: command-shape -->
   Example: `uv run gz adr clear-stale <flagged-id> --upstream <upstream-id> --kind {confirmed_unchanged|amended} --reason "..." --attest "..."`.
4. REQUIREMENT: `gz validate --staleness-coherence` MUST cross-check every frontmatter `evaluation_stale` entry has a matching ledger `artifact_staleness_flagged` event without a matching `artifact_staleness_cleared`, and vice versa. Exit 3 on drift, 0 on coherence.
5. REQUIREMENT: Both validator scopes MUST join the default `gz check` bundle.
6. REQUIREMENT: `gz adr audit-check ADR-X.Y.Z` MUST refuse a `Completed` claim if any child OBPI carries an unresolved `evaluation_stale` flag; exit 3 with prescriptive error naming the child OBPI and upstream.
7. REQUIREMENT: Anti-pattern enforced at validator entry points: neither validator may early-return based on the other's state (named in parent ADR composition table).
8. REQUIREMENT: Validator implementations MUST be pure functions of (canon, ledger, command-context) — no global mutable state, no caching surviving invocation.

> STOP-on-BLOCKERS: read existing trust_audits scope for registration pattern before authoring.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"`gz validate --adr-eval-fresh` validator + `gz validate --staleness-coherence` validator; default `gz check` bundle integration; `gz adr audit-check` augmentation"*.
- [ ] Parent ADR § Decision / "Validators" — exact fail-close semantics.
- [ ] Parent ADR § Decision / "Composition with ADR-0.0.26" — orthogonal validator table; anti-pattern naming.

**Governance:**

- [ ] `.gzkit/rules/governance-core.md` § Proof commands — pattern for new scopes.

**Prerequisites:**

- [ ] OBPI-0.0.52-02 (Pydantic models, frontmatter schema delta) has landed.
- [ ] OBPI-0.0.52-04 (trigger wiring + tx_id) has landed; ledger events emittable for tests.

**Existing Code:**

- [ ] Existing validator scope (e.g., `cli_alignment.py`) reviewed for scope registration and exit-code conventions.
- [ ] `validate_cmd.py` reviewed for flag-registration pattern.

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

- [ ] Human attestation recorded

## Verification

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz lint
uv run gz typecheck
uv run gz validate --adr-eval-fresh
uv run gz validate --staleness-coherence
uv run gz check
uv run -m unittest tests.governance.test_adr_eval_fresh tests.governance.test_staleness_coherence tests.governance.test_adr_audit_check_staleness -v
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
echo "ADR-0.0.B carries evaluation_stale: ADR-0.0.A"
uv run gz closeout ADR-0.0.B
# Expected: exit 3 from --adr-eval-fresh with copy-paste resolution command

uv run gz validate --staleness-coherence
# Expected: exit 3 on drift, naming orphan tx_id + recovery message

uv run gz adr audit-check ADR-0.0.X
# Expected: exit 3 if any child OBPI has unresolved evaluation_stale
```

## Acceptance Criteria

- [ ] REQ-0.0.52-05-01: Given an artifact with unresolved `evaluation_stale`, when `gz closeout` runs, then `--adr-eval-fresh` fires and exits 3 with the copy-paste resolution command.
- [ ] REQ-0.0.52-05-02: Given the same stale artifact, when `gz status` or `gz state --json` runs, then `--adr-eval-fresh` does NOT fire.
- [ ] REQ-0.0.52-05-03: Given a ledger `artifact_staleness_flagged` without matching frontmatter entry, when `--staleness-coherence` runs, then it exits 3 naming the orphan `tx_id`.
- [ ] REQ-0.0.52-05-04: Given a frontmatter entry without matching ledger event, when `--staleness-coherence` runs, then symmetric orphan detection exits 3.
- [ ] REQ-0.0.52-05-05: Given a matched flag+clear pair, when `--staleness-coherence` runs, then it exits 0.
- [ ] REQ-0.0.52-05-06: Given `uv run gz check`, when it runs, then both scopes contribute to the overall exit code.
- [ ] REQ-0.0.52-05-07: Given `gz adr audit-check` on an ADR whose child OBPI carries unresolved `evaluation_stale`, when invoked, then audit-check refuses Completed and exits 3.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle followed
- [ ] **Code Quality:** Lint, type checks clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** included

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

Before: propagation flags could land in the void; flagged artifacts could still advance, and Layer 1 vs Layer 2 drift had no validator. Now: `--adr-eval-fresh` mechanically refuses lifecycle advance on flagged artifacts; `--staleness-coherence` catches any drift; `gz adr audit-check` cannot certify Completed on an ADR whose children carry unresolved flags.

### Key Proof

<!-- gz-validate-skip: command-shape -->
```bash
$ uv run gz closeout ADR-0.0.B
[FAIL] ADR-0.0.B carries unresolved evaluation_stale flags during advancing action.
Resolution:
  uv run gz adr clear-stale ADR-0.0.B --upstream ADR-0.0.A \
    --kind confirmed_unchanged --reason "..." --attest "..."
Exit 3.
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
