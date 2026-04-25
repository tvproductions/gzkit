---
id: OBPI-0.0.24-03-doc-updates
parent: ADR-0.0.24-attestation-receipt-binding
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.24-03-doc-updates: AGENTS.md + arb-middleware.md updates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/ADR-0.0.24-attestation-receipt-binding.md`
- **Checklist Item:** #3 — "Update AGENTS.md § Attestation, the attestation rule mirror, and `docs/governance/arb-middleware.md` to reflect the mechanical contract"

**Status:** Draft

## Objective

Update AGENTS.md § Attestation prose to reflect that receipt binding is now mechanical (not advisory) on heavy/foundation, update `docs/governance/arb-middleware.md` to document the new `arb-meta-receipt-bind` family, and update the manpage for `gz validate` to expose `--attestation-receipts`.

## Lane

**Heavy** — Documentation updates accompanying a contract change. Per `.gzkit/rules/gate5-runbook-code-covenant.md`, docs track behavior in the same patch set; this OBPI is the docs side of OBPI-01 and OBPI-02.

## Allowed Paths

- `AGENTS.md` — § Attestation prose updates
- `docs/governance/arb-middleware.md` — receipt-binding section added
- `docs/user/manpages/gz-validate.md` (or wherever manpages live) — `--attestation-receipts` flag documented
- `docs/user/runbook.md` — attestation flow narrative updated if affected
- `docs/governance/governance_runbook.md` — heavy-lane attestation flow updated if affected
- `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/**` — parent ADR package scope

## Denied Paths

- `src/**` — no code changes in this OBPI
- `tests/**` — no test changes in this OBPI
- `features/**` — BDD coverage in OBPI-04
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: AGENTS.md § Attestation replaces "the citing agent must verify the receipt exists and its status matches the claim" with mechanical-gate language naming `gz validate --attestation-receipts` as the enforcement surface.
2. REQUIREMENT: AGENTS.md § Lane behavior table updates: heavy lane "fail-closed" cell explicitly cites the new gate; lite lane "warn" cell remains.
3. REQUIREMENT: `docs/governance/arb-middleware.md` adds a § "Receipt-binding gate" subsection documenting the gate's invocation point, the `arb-meta-receipt-bind` family, and the failure modes (missing / status_mismatch / claim_mismatch).
4. REQUIREMENT: The `gz validate` manpage exposes `--attestation-receipts` with EXAMPLES showing real CLI output (per AGENTS.md § Prime Directive item 2).
5. REQUIREMENT: `uv run gz cli audit` exits 0 — manpage parity is preserved.
6. REQUIREMENT: `uv run mkdocs build --strict` exits 0.
7. REQUIREMENT: NEVER include the operator's personal email anywhere in the doc edits.
8. REQUIREMENT: NEVER leave placeholder output examples in the manpage; paste real CLI output.

> STOP-on-BLOCKERS: if OBPI-01 and OBPI-02 have not landed, STOP — the manpage cannot show real output for an unimplemented surface.

## Discovery Checklist

- [ ] OBPI-0.0.24-01 + OBPI-0.0.24-02 evidence — confirm validator and gate are landed
- [ ] AGENTS.md § Attestation, § Lane behavior, § Canonical invocations
- [ ] `docs/governance/arb-middleware.md` existing structure
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` § Required updates when behavior changes

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] No code change; Gate 2 satisfied via `gz validate --documents` clean run

### Code Quality

- [ ] Lint clean: `uv run gz lint`

### Gate 3: Docs (Heavy)

- [ ] `uv run mkdocs build --strict` exits 0
- [ ] `uv run gz cli audit` exits 0

### Gate 4: BDD (Heavy)

- [ ] BDD scenarios in OBPI-04

### Gate 5: Human (Heavy + Foundation)

- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz cli audit
uv run mkdocs build --strict
uv run gz validate --documents
grep -n "attestation-receipts" AGENTS.md docs/governance/arb-middleware.md docs/user/manpages/gz-validate.md
```

## Acceptance Criteria

- [ ] REQ-0.0.24-03-01: Given AGENTS.md § Attestation, when this OBPI completes, then the prose names `gz validate --attestation-receipts` as the mechanical enforcement surface (not narrative discipline).
- [ ] REQ-0.0.24-03-02: Given `docs/governance/arb-middleware.md`, when this OBPI completes, then a § "Receipt-binding gate" subsection documents invocation point, meta-receipt family, and failure modes.
- [ ] REQ-0.0.24-03-03: Given the `gz validate` manpage, when this OBPI completes, then `--attestation-receipts` is documented with a real CLI EXAMPLES block.
- [ ] REQ-0.0.24-03-04: Given the post-edit repo state, when `gz cli audit` runs, then exit 0 (no manpage drift).
- [ ] REQ-0.0.24-03-05: Given the post-edit repo state, when `mkdocs build --strict` runs, then exit 0.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** validate --documents clean
- [ ] **Code Quality:** Lint clean
- [ ] **Gate 3 (Docs):** mkdocs strict + cli audit pass
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Manpage EXAMPLES section pasted real output
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# validate --documents output
```

### Code Quality

```text
# lint output
```

### Gate 3 (Docs)

```text
# mkdocs build --strict output
# gz cli audit output
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added: n/a (docs)
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
