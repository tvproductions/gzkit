---
id: OBPI-0.0.74-18-structural-fence-proof-upgrade
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 18
lane: Heavy
# req_atomic: each REQ is one coherent increment of the single resolve_fence_proof
# amendment — the enforcement-asserting fence now requires a live NC (01), the
# state-property fence is unchanged (02), and the cross-OBPI fence (03). None
# decomposes into parallel seq=02+ sub-tasks (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.74-18-01  # resolve_fence_proof: a fence REQ asserting enforcement requires a live @enforces NC
  - REQ-0.0.74-18-02  # state-property fences unchanged — still resolve via the Boundary Invariants anchor
  - REQ-0.0.74-18-03  # STRUCTURAL-FENCE: a structural-fence enforcement claim requires a live NC (BI#10)
status: Draft
---

# OBPI-0.0.74-18-structural-fence-proof-upgrade: Structural Fence Proof Upgrade

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #18 - "Structural-fence proof upgrade — `resolve_fence_proof` (in `src/gzkit/req_kind.py`) amended so a `[structural-fence]` REQ that asserts enforcement requires a live `@enforces` NC, not merely a `## Boundary Invariants` anchor, while state-property fences are unchanged; unit tests"

**Status:** Draft

## Objective

Amend `resolve_fence_proof` (in `src/gzkit/req_kind.py`, line ~91 — NOT `closeout_proof.py`, which is its consumer) so that a `[structural-fence]` REQ that asserts *enforcement* (the claim text declares something is enforced / validated / fail-closed / gated) resolves to `"pass"` at closeout ONLY when a live `@enforces` NC for that claim exists, not merely when the parent ADR has a `## Boundary Invariants` anchor. A `[structural-fence]` REQ that asserts a *state-property* (a cross-OBPI integration-state invariant, not an enforcement claim) is UNCHANGED — it still resolves via the `## Boundary Invariants` anchor exactly as today. "Done" = `resolve_fence_proof` distinguishes an enforcement-asserting fence from a state-property fence, requires a live `@enforces` NC for the former (returning an unproven status when absent), leaves the latter's resolution untouched, and unit tests pin both paths. This closes the seam where a structural-fence enforcement claim could ride on a prose anchor alone — the §5 facade in the fence-proof channel.

## Lane

**Heavy** - This OBPI changes a runtime-contract surface — the closeout proof resolver `resolve_fence_proof` that decides whether a `[structural-fence]` REQ resolves — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 18, § Boundary Invariants #10)
- `src/gzkit/req_kind.py` — amend `resolve_fence_proof` so an enforcement-asserting `[structural-fence]` REQ requires a live `@enforces` NC, while state-property fences are unchanged
- `tests/governance/test_fence_proof_live_nc.py` **CREATE** — unit tests for the enforcement-asserting path (requires live NC) and the state-property path (unchanged, anchor-only)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-18-structural-fence-proof-upgrade.md` — this brief (evidence recording)

(Security overlap check: no Allowed Path matches a glob in `data/security_surfaces.json` — `src/gzkit/req_kind.py` is the REQ-kind / fence-proof resolver, not a `*credential*`/`*secret*`/`*hash*` module, not `quality.py`, not a ledger/arb/auth surface. `sensitivity: security` is not declared.)

## Creates These Files

- `tests/governance/test_fence_proof_live_nc.py`

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/governance/trust_audits/closeout_proof.py` — the CONSUMER of `resolve_fence_proof`; this OBPI amends the resolver in `req_kind.py`, not the consumer (if the consumer needs a coupled change, surface it as a coupled-surface finding, do not silently expand)
- The `@enforces` decorator/registry (OBPI-15) and runner (OBPI-16) — this OBPI consumes the registry to check for a live NC, it does not redefine the primitive
- Changing the resolution of state-property (non-enforcement) `[structural-fence]` REQs — they remain anchor-resolved; this is a regression boundary, not a target
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `resolve_fence_proof` MUST resolve a `[structural-fence]` REQ that asserts enforcement to a passing status ONLY when a live `@enforces` NC for that claim exists; absent the live NC it MUST resolve to an unproven status, not merely on a `## Boundary Invariants` anchor (REQ-18-01).
1. REQUIREMENT: `resolve_fence_proof` MUST leave the resolution of state-property (non-enforcement) `[structural-fence]` REQs unchanged — they continue to resolve via the `## Boundary Invariants` anchor (no regression) (REQ-18-02).
1. NEVER: Edit the consumer `closeout_proof.py` to work around the resolver, or weaken state-property fence resolution to make the new enforcement path pass.
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; `resolve_fence_proof` (`src/gzkit/req_kind.py`) and the `@enforces` registry (OBPI-15) MUST exist first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 18 — quoted verbatim:** "Structural-fence proof upgrade — a `[structural-fence]` REQ that asserts *enforcement* requires a live `@enforces` NC, not merely a `## Boundary Invariants` anchor; `resolve_fence_proof` (in `src/gzkit/req_kind.py`) is amended, while state-property fences are unchanged. (OBPI-18)"
- [ ] Parent ADR § Boundary Invariants #10 — "A structural-fence enforcement claim requires a live NC" (the invariant this OBPI implements; the proof channel for REQ-18-03).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `.claude/rules/tests.md` § REQ Scope Discipline — the STRUCTURAL-FENCE proof channel (parent-ADR Boundary Invariants) this resolver implements

**Context:**

- [ ] `src/gzkit/req_kind.py` — `resolve_fence_proof` (line ~91), `_BOUNDARY_INVARIANTS_HEADING`, `_REQ_SEMVER_RE`, `_find_parent_adr_file`; the current anchor-only resolution to extend
- [ ] `src/gzkit/governance/trust_audits/closeout_proof.py` — the consumer that calls `resolve_fence_proof` (read to confirm the return-value contract, do not edit)
- [ ] `src/gzkit/enforcement.py` (OBPI-15/16) — the registry the enforcement-asserting path queries for a live NC

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/req_kind.py` exists with `resolve_fence_proof`
- [ ] `src/gzkit/enforcement.py` exists with the `@enforces` registry (OBPI-0.0.74-15 has landed)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/governance/` reviewed for the local fence-proof test convention
- [ ] `resolve_fence_proof` and its `"pass"` / `"unproven-fence"` return values reviewed so the new enforcement path returns a status the consumer already handles

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/req_kind.py
test -f tests/governance/test_fence_proof_live_nc.py
```

## Demo

```bash
# An enforcement-asserting structural-fence REQ no longer resolves on the anchor
# alone — it requires a live @enforces NC; a state-property fence is unchanged.
uv run python -c "from gzkit.req_kind import resolve_fence_proof; from pathlib import Path; print(resolve_fence_proof('REQ-0.0.74-16-05', Path('.')))"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-18-01 [behavior]: Given a `[structural-fence]` REQ whose claim text asserts enforcement, when `resolve_fence_proof` runs, then it resolves to a passing status ONLY if a live `@enforces` NC for that claim exists, and to an unproven status when the NC is absent (not on the `## Boundary Invariants` anchor alone). (@covers test in `tests/governance/test_fence_proof_live_nc.py`)
- [ ] REQ-0.0.74-18-02 [behavior]: Given a `[structural-fence]` REQ that asserts a state-property (non-enforcement) invariant, when `resolve_fence_proof` runs, then it resolves via the `## Boundary Invariants` anchor exactly as before — no regression. (@covers test in `tests/governance/test_fence_proof_live_nc.py`)
- [ ] REQ-0.0.74-18-03 [structural-fence]: A `[structural-fence]` REQ that asserts enforcement resolves at closeout only when `resolve_fence_proof` finds a live `@enforces` NC, not merely a `## Boundary Invariants` anchor (parent ADR § Boundary Invariants #10 — a structural-fence enforcement claim requires a live NC).

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
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

Before: a `[structural-fence]` REQ resolved at closeout as long as the parent ADR carried a `## Boundary Invariants` heading — so a fence REQ that ASSERTS enforcement ("X is fail-closed") passed on a prose anchor alone, with no live proof the enforcement is real: the §5 facade reproduced in the fence-proof channel. Now: `resolve_fence_proof` distinguishes an enforcement-asserting fence from a state-property fence and requires a live `@enforces` NC for the former, while leaving state-property fences anchor-resolved — the fence-proof channel now demands the same live negative control the rest of §5 does.

### Key Proof

### Implementation Summary

- **Decision item 18 (verbatim):** "Structural-fence proof upgrade — a `[structural-fence]` REQ that asserts *enforcement* requires a live `@enforces` NC, not merely a `## Boundary Invariants` anchor; `resolve_fence_proof` (in `src/gzkit/req_kind.py`) is amended, while state-property fences are unchanged. (OBPI-18)"
- Coupled surface (read-only, not edited): `src/gzkit/governance/trust_audits/closeout_proof.py` consumes `resolve_fence_proof`'s return value.
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
