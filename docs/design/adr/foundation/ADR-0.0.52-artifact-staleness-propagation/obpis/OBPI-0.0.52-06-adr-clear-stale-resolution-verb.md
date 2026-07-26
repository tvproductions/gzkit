---
id: OBPI-0.0.52-06-adr-clear-stale-resolution-verb
parent: ADR-0.0.52-artifact-staleness-propagation
item: 6
lane: Heavy
status: Draft
allowlist:
- src/gzkit/commands/adr_clear_stale_cmd.py
- src/gzkit/cli/adr_subcommands.py
- src/gzkit/governance/propagation/resolution.py
- tests/governance/test_adr_clear_stale.py
- tests/governance/test_propagation_composition.py
- docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md
reqs:
- REQ-0.0.52-06-01
- REQ-0.0.52-06-02
- REQ-0.0.52-06-03
- REQ-0.0.52-06-04
- REQ-0.0.52-06-05
- REQ-0.0.52-06-06
- REQ-0.0.52-06-07
verification:
- uv run gz lint
- uv run gz typecheck
- uv run -m unittest tests.governance.test_adr_clear_stale tests.governance.test_propagation_composition -v
---

# OBPI-0.0.52-06-adr-clear-stale-resolution-verb: gz adr clear-stale resolution verb

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #6 — "`clear-stale` resolution verb + `gz-adr-evaluate` invocation + `artifact_staleness_cleared` event emission with operator attestation + composition with ADR-0.0.26's `--evaluation-justify-binding` validated end-to-end"

**Status:** Draft

## Objective

Implement `clear-stale` — the resolution verb that clears an `evaluation_stale` flag via confirm-or-amend re-evaluation with operator attestation. The verb invokes `gz-adr-evaluate` against the flagged artifact (producing the canonical `adr-evaluation` event ADR-0.0.26 consumes), emits `artifact_staleness_cleared` with operator attestation, and removes the frontmatter entry atomically (via `tx_id` paired with OBPI-04 semantics).

## Lane

**Heavy** — New CLI verb (changes `gz adr` subcommand surface).

## Allowed Paths

- `src/gzkit/commands/adr_clear_stale_cmd.py` — **PRIMARY:** new resolution verb
- `src/gzkit/cli/adr_subcommands.py` — register `clear-stale` subcommand
- `src/gzkit/governance/propagation/resolution.py` — clearance pipeline (re-evaluate + emit + remove entry)
- `tests/governance/test_adr_clear_stale.py` — clearance verb tests (confirmed_unchanged path; amended path; rejection of unattested clearance)
- `tests/governance/test_propagation_composition.py` — end-to-end test with ADR-0.0.26's `--evaluation-justify-binding`
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Tier 2 surfaces (OBPI-07)
- Status surfaces (OBPI-08)
- ADR-0.0.26 implementation surfaces (read-only consumption only)

## Creates These Files

- `src/gzkit/commands/adr_clear_stale_cmd.py` — **CREATE** new resolution verb command module
- `src/gzkit/cli/adr_subcommands.py` — **CREATE** (or extend existing parser_governance.py) ADR subcommand registration
- `src/gzkit/governance/propagation/resolution.py` — **CREATE** clearance pipeline (re-evaluate + emit + remove entry)
- `tests/governance/test_adr_clear_stale.py` — **CREATE** clearance verb tests
- `tests/governance/test_propagation_composition.py` — **CREATE** end-to-end test with ADR-0.0.26's `--evaluation-justify-binding`

## Requirements (FAIL-CLOSED)

<!-- gz-validate-skip: command-shape -->
1. REQUIREMENT: `clear-stale <flagged-id> --upstream <upstream-id> --kind {confirmed_unchanged|amended} --reason "..." --attest "..."` MUST be implemented as a new subcommand under `gz adr`.
2. REQUIREMENT: The verb MUST invoke `gz-adr-evaluate <flagged-id>` which produces a fresh `adr-evaluation` ledger event (the orthogonal composition surface with ADR-0.0.26 Decision 1).
3. REQUIREMENT: On `--kind confirmed_unchanged`: emit `artifact_staleness_cleared` with `clearance_kind: confirmed_unchanged`, `reason`, `attestation`, `fresh_evaluation_event_id`, paired by `tx_id`; remove the corresponding frontmatter entry atomically.
4. REQUIREMENT: On `--kind amended`: require `--amendment-ref <ref>` (accepts commit SHA as transitional handle until ADR-pool.adr-amendment-tracking promotes). Emit `artifact_staleness_cleared` with `clearance_kind: amended`, `amendment_ref`, plus the same fields as `confirmed_unchanged`.
5. REQUIREMENT: Operator attestation MUST be non-empty; an empty `--attest` value MUST exit 1 with a clear error (clearance is operator-attested by design, never automatic).
6. REQUIREMENT: If the specified `--upstream <upstream-id>` is not present in the flagged artifact's frontmatter `evaluation_stale` entries, exit 1 with a clear "nothing to clear" message.
7. REQUIREMENT: Composition with ADR-0.0.26's `--evaluation-justify-binding` MUST be exercised end-to-end: when the fresh evaluation score is < 3.0, the next validator invocation MUST fire `--evaluation-justify-binding` (no special handling in this verb — the validators compose through the shared `adr-evaluation` event family).
8. REQUIREMENT: The clearance ledger event AND the frontmatter entry removal MUST be paired by `tx_id` per OBPI-04 atomic-transaction semantics.

> STOP-on-BLOCKERS: if `gz-adr-evaluate` is not yet emitting canonical `adr-evaluation` events (ADR-0.0.26 Decision 1), pause and confirm 0.0.26 surface availability.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"`clear-stale` resolution verb + `gz-adr-evaluate` invocation + `artifact_staleness_cleared` event emission with operator attestation + composition with ADR-0.0.26's `--evaluation-justify-binding` validated end-to-end"*.
- [ ] Parent ADR § Decision / "Resolution ceremony (confirm-or-amend)" — exact verb shape, attestation contract.
- [ ] Parent ADR § Decision / "Composition with ADR-0.0.26" — orthogonal validator table.

**Governance:**

- [ ] `AGENTS.md` § Attestation — canonical invocation patterns; attestation enrichment rules.
- [ ] `AGENTS.md` § Local Agent Rules — operator PII boundary on attestation fields (no personal email).
- [ ] ADR-0.0.26 § Decision item 1 — `adr-evaluation` event shape (consumed by this verb's re-evaluation pass).

**Prerequisites:**

- [ ] OBPI-0.0.52-02 (Pydantic models including `ArtifactStalenessClearedEvent`) has landed.
- [ ] OBPI-0.0.52-04 (`tx_id` atomic-transaction semantics) has landed.
- [ ] OBPI-0.0.52-05 (`--adr-eval-fresh` validator) has landed — the verb's output clears flags that validator gates on.

**Existing Code:**

- [ ] Existing `gz adr <subcommand>` verb reviewed for subcommand registration pattern.
- [ ] ADR-0.0.26 `gz-adr-evaluate` implementation reviewed for the `adr-evaluation` event-emit hook this verb invokes.

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

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_adr_clear_stale tests.governance.test_propagation_composition -v
```

## Demo

<!-- gz-validate-skip: command-shape -->
```bash
# Confirm-unchanged path
uv run gz adr clear-stale ADR-0.0.B --upstream ADR-0.0.A \
  --kind confirmed_unchanged \
  --reason "ADR-0.0.A's Decision item 3 affects only src/gzkit/render/; ADR-0.0.B's surface is src/gzkit/validate/ (independent)" \
  --attest "g0 — confirmed downstream design unchanged"

# Amended path (requires --amendment-ref)
uv run gz adr clear-stale OBPI-0.0.B-04 --upstream ADR-0.0.A \
  --kind amended \
  --amendment-ref a1b2c3d4 \
  --reason "Amended REQ-0.0.B-04-02 to track A's new enum value" \
  --attest "g0 — amended per commit a1b2c3d4"

# Composition with ADR-0.0.26: if fresh evaluation < 3.0, next gz check fires --evaluation-justify-binding
uv run gz check
# Expected: --evaluation-justify-binding fires naturally on the new low score
```

## Acceptance Criteria

- [ ] REQ-0.0.52-06-01: Given a flagged artifact, when `clear-stale --kind confirmed_unchanged` runs with valid attestation, then `gz-adr-evaluate` is invoked, `artifact_staleness_cleared` is emitted, and the frontmatter entry is removed atomically.
- [ ] REQ-0.0.52-06-02: Given `--kind amended` without `--amendment-ref`, when invoked, then the verb exits 1 with a prescriptive error.
- [ ] REQ-0.0.52-06-03: Given an empty `--attest`, when invoked, then exit 1 (operator attestation mandatory; no automatic clearance).
- [ ] REQ-0.0.52-06-04: Given an `--upstream` not present in the artifact's `evaluation_stale` entries, when invoked, then exit 1 with "nothing to clear".
- [ ] REQ-0.0.52-06-05: Given a fresh evaluation that scores < 3.0 after clearance, when the next `gz check` runs, then ADR-0.0.26's `--evaluation-justify-binding` fires naturally (orthogonal composition validated).
- [ ] REQ-0.0.52-06-06: Given the clearance ledger event and the frontmatter entry removal, when both complete, then they share the same `tx_id` (per OBPI-04 semantics).
- [ ] REQ-0.0.52-06-07: Given the verb registration, when `gz adr --help` runs, then `clear-stale` appears in the subcommand list with help text including the canonical example.

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

Before: a flagged artifact had no resolution surface — operator could not legitimately clear an `evaluation_stale` flag, and the validator gating lifecycle advance would block indefinitely. Now: the confirm-or-amend ceremony is a single CLI verb invocation, mechanically attested, with re-evaluation that composes naturally into ADR-0.0.26's score-threshold validator.

### Key Proof

<!-- gz-validate-skip: command-shape -->
```bash
$ uv run gz adr clear-stale ADR-0.0.B --upstream ADR-0.0.A \
    --kind confirmed_unchanged --reason "..." --attest "..."
Running gz-adr-evaluate ADR-0.0.B...
[OK] Fresh evaluation: 3.45/4.0 weighted (GO). Ledger: adr-evaluation 5e6f7g8h...
Clearance recorded.
  fresh_evaluation_event_id: 5e6f7g8h...
  Ledger: artifact_staleness_cleared 9i0j1k2l... (tx_id 7m8n9o0p...)
evaluation_stale entry removed from ADR-0.0.B frontmatter.
Exit 0.
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
