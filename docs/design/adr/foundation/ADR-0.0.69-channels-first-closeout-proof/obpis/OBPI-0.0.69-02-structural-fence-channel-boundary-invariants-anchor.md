---
id: OBPI-0.0.69-02-structural-fence-channel-boundary-invariants-anchor
parent: ADR-0.0.69-channels-first-closeout-proof
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.69-02-structural-fence-channel-boundary-invariants-anchor: STRUCTURAL-FENCE Channel Boundary-Invariants Anchor

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md`
- **Checklist Item:** #2 - "OBPI-0.0.69-02: STRUCTURAL-FENCE channel — Boundary-Invariants anchor assertion + add the `## Boundary Invariants` heading to ADR-0.0.59 itself (closes #538) (Heavy)"

**Status:** Draft

## Objective

The STRUCTURAL-FENCE proof arm stops reporting `"grandfathered"`: it asserts that a
parent-ADR `## Boundary Invariants` anchor is present for the FENCE REQ and reports
unproven when absent. ADR-0.0.59 itself gains a `## Boundary Invariants` heading so its
own FENCE REQs stay provable. Closes #538.

## Lane

**Heavy** - Changes the runtime semantics of the STRUCTURAL-FENCE proof channel (a
runtime-contract surface) from advisory/grandfathered to a real Boundary-Invariants-anchor
assertion.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? -->

- `src/gzkit/req_kind.py` — the STRUCTURAL-FENCE arm (today reporting `"grandfathered"`): assert a parent-ADR `## Boundary Invariants` anchor is present for the FENCE REQ; absent anchor → unproven
- `tests/` — fail-close regression tests (anchor present → proven; anchor absent → unproven)
- `docs/design/adr/foundation/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine/ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine.md` — add the `## Boundary Invariants` heading anchoring ADR-0.0.59's own FENCE REQs (coupled-surface fix so ADR-0.0.59 stays provable under the new arm)
- `docs/user/manpages/validate.md` — document the STRUCTURAL-FENCE proof semantics
- `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md` — parent ADR (read-only reference) and the home of REQ-0.0.69-02-04's Boundary-Invariants entry
- `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/obpis/OBPI-0.0.69-02-structural-fence-channel-boundary-invariants-anchor.md` — this brief

> Confirm the real on-disk path of ADR-0.0.59's package before editing; if it has moved,
> note the divergence rather than authoring against a stale path.

## Denied Paths

<!-- What is OUT OF SCOPE? -->

- The SUPPORT branch (`_check_support_req`) — OBPI-01's scope
- The derived `--closeout-proof` view — OBPI-03's scope
- The `ln:` closeout-proof-binding surface — OBPI-04's scope
- New runtime dependencies; lockfiles; CI files

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The STRUCTURAL-FENCE arm MUST report proven only when a parent-ADR `## Boundary Invariants` anchor is present for the FENCE REQ; a missing anchor MUST report unproven — never `"grandfathered"` or advisory.
1. REQUIREMENT: ADR-0.0.59 MUST gain a `## Boundary Invariants` heading anchoring its own STRUCTURAL-FENCE REQs so it stays provable under the new arm.
1. REQUIREMENT: `docs/user/manpages/validate.md` MUST document the STRUCTURAL-FENCE proof semantics; `mkdocs build --strict` and `gz validate --documents` MUST stay green.
1. NEVER: touch the SUPPORT branch, the derived view, or the `ln:` surface — those are OBPI-01/03/04 scopes.
1. ALWAYS: reconcile this brief against the parent ADR § Decision item (2) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (2)** — quote it verbatim into this brief's Implementation Summary.
- [ ] Parent ADR § Intent and § Boundary Invariants (REQ-0.0.69-02-04 entry).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.69-channels-first-closeout-proof/ADR-0.0.69-channels-first-closeout-proof.md`

> **STOP:** If you cannot quote the parent ADR § Decision item (2) that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR (OBPI-01 SUPPORT arm, OBPI-03 derived view)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/req_kind.py` exists and the FENCE arm's `"grandfathered"` status is present
- [ ] ADR-0.0.59's package exists on disk and its FENCE REQs are identifiable
- [ ] `docs/user/manpages/validate.md` exists

**Existing Code (understand current state):**

- [ ] `req_kind.py` FENCE arm read whole; how a parent-ADR Boundary-Invariants anchor is (or is not) currently located
- [ ] ADR-0.0.68's `## Boundary Invariants` section reviewed as the anchor-shape precedent
- [ ] Existing `req_kind` tests reviewed for the fail-close test fixture shape

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

<!-- Single-program, shell-less invocations only (GHI #415). -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz cli audit
```

## Demo

```bash
# A STRUCTURAL-FENCE REQ whose parent ADR carries a matching `## Boundary Invariants`
# anchor now resolves to proven; one without an anchor reports unproven (no longer
# "grandfathered"):
uv run gz validate --req-kind-discipline
```

## Acceptance Criteria

<!-- Each REQ carries exactly one inline [kind] tag (ADR-0.0.59). -->

- [ ] REQ-0.0.69-02-01 [behavior]: Given a STRUCTURAL-FENCE REQ whose parent ADR has NO matching `## Boundary Invariants` anchor, when the FENCE arm resolves proof, then `proof_status` is unproven (fail-close) — never `grandfathered`. (@covers test)
- [ ] REQ-0.0.69-02-02 [behavior]: Given a STRUCTURAL-FENCE REQ whose parent ADR carries a matching `## Boundary Invariants` anchor, when the FENCE arm resolves proof, then `proof_status` is proven. (@covers test)
- [ ] REQ-0.0.69-02-03 [support]: ADR-0.0.59 gains a `## Boundary Invariants` heading anchoring its own STRUCTURAL-FENCE REQs (coupled-surface fix so ADR-0.0.59 stays provable). Proof: `artifact_edited` ledger event + `gz validate --documents` + `mkdocs build --strict` green.
- [ ] REQ-0.0.69-02-04 [structural-fence]: The STRUCTURAL-FENCE proof arm MUST assert a real parent-ADR `## Boundary Invariants` anchor and MUST NOT report `grandfathered`/advisory. Verified at ADR-0.0.69 closeout via the parent ADR `## Boundary Invariants` (Invariant 1).

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

<!-- What problem existed before this OBPI, and what capability exists now? -->

Before: the STRUCTURAL-FENCE proof arm reported `"grandfathered"`, waving through any FENCE
REQ regardless of whether its parent ADR actually declared the fence in a
`## Boundary Invariants` section (#538). Now: the arm asserts a real anchor and fail-closes
when it is absent, making the FENCE channel load-bearing.

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- Closes #538 — STRUCTURAL-FENCE arm reported `grandfathered` instead of asserting a real anchor.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
