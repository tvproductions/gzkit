---
id: OBPI-0.0.24-03-doc-updates
parent: ADR-0.0.24-attestation-receipt-binding
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.24-03-doc-updates: AGENTS.md + arb-middleware.md updates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/ADR-0.0.24-attestation-receipt-binding.md`
- **Checklist Item:** #3 — "Update AGENTS.md § Attestation, the attestation rule mirror, and `docs/governance/arb-middleware.md` to reflect the mechanical contract"

**Status:** Draft

## Objective

Update AGENTS.md § Attestation prose to reflect that receipt binding is now mechanical (not advisory) on heavy/foundation, update `docs/governance/arb-middleware.md` to document the new `arb-meta-receipt-bind` family, and update the manpage for `gz validate` to expose `--attestation-receipts`.

## Lane

**Heavy** — Although AGENTS.md § Lane Rules treats documentation/process/template-only changes as Lite by default, this OBPI inherits the parent ADR's foundation-kind rigor regardless of its own surface (per AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix — foundation-kind brief-level attestation fires on every OBPI's `Completed` transition, including doc-only OBPIs, because doctrine drift is invariant drift). Per `.gzkit/rules/gate5-runbook-code-covenant.md`, docs track behavior in the same patch set; this OBPI is the docs side of OBPI-01 and OBPI-02.

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

**Prerequisites**

- OBPI-0.0.24-01 (validator scope) is `attested_completed` per `gz adr status ADR-0.0.24` — confirms `gz validate --attestation-receipts` exists and parses inline `arb-(ruff|step-<name>)-[a-f0-9]{32}` IDs against `artifacts/receipts/`.
- OBPI-0.0.24-02 (wire-into-completion) is `attested_completed` per `gz adr status ADR-0.0.24` — confirms the gate fires pre-emission inside `gz obpi complete` and `gz adr emit-receipt` with lane/kind-conditional fail/warn behavior and emits the `arb-meta-receipt-bind-…` self-attesting receipt family.
- Real ARB receipts exist in `artifacts/receipts/` for the EXAMPLES block — `arb-ruff-008dda0e47384e89bea69e3b8b5cb6d4.json` confirmed present via session probe; suitable for the heavy/foundation PASS example.
- `gz cli audit` baseline is currently green (90/90 commands fully covered) so the manpage edit can be verified non-regressing.
- `mkdocs build --strict` baseline is currently green so the doc edits can be verified non-regressing.

**Existing Code**

- `AGENTS.md` § Attestation — current Lane behavior block (~line 356) still uses pre-mechanical narrative-trust language ("Citing agent must verify the receipt exists and status matches the claim"); the surface to rewrite per REQ-01/02 lives in two places: the Lane behavior bullets and the Receipt IDs sentence directly above § Anti-patterns.
- `docs/governance/arb-middleware.md` — current structure (Core Concept → Available commands → Receipt schema and storage → Exit codes → Rationale) has no Receipt-binding gate section; insertion point for REQ-03 is between `## Receipt schema and storage` and `## Exit codes` — preserves the schema → storage → enforcement → consumption flow.
- `docs/user/commands/validate.md` — current `### --attestation-receipts` section (lines 26-44) carries a placeholder ("full operator prose lands in OBPI-03") and no EXAMPLES block; this is the surface to expand per REQ-04 — the canonical home for `gz validate` documentation in this repo (no `docs/user/manpages/gz-validate.md` exists).
- `docs/user/runbook.md` step 4b heavy-lane ARB receipts block (~line 163) — names `AGENTS.md` § Attestation but not the new mechanical gate; targeted one-line note insertion.
- `.claude/rules/gate5-runbook-code-covenant.md` — already binding doctrine that documentation tracks behavior in the same patch set; consulted for coverage scope, no edits required.

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


Heavy/foundation gate accepts a real receipt citation:

```
$ uv run gz validate --attestation-receipts \
    "Tests pass — full unittest sweep clean (lint: receipt arb-ruff-008dda0e47384e89bea69e3b8b5cb6d4)" \
    --lane heavy --kind foundation
✓ 1 attestation receipt(s) resolved.
$ echo $?
0
```

Heavy/foundation gate rejects narrative-only attestation (fail-closed):

```
$ uv run gz validate --attestation-receipts \
    "Implementation complete; all checks green." \
    --lane heavy --kind foundation
❌ No ARB receipt IDs cited (heavy or foundation: fail-closed).
$ echo $?
3
```

These are the two EXAMPLES now pasted verbatim into `docs/user/commands/validate.md` § `--attestation-receipts` § Examples. Heavy-lane ARB evidence for this OBPI: lint receipt `arb-ruff-7b1d21ab042d4c0d90097e8c6ba88fa9` (exit 0); docs strict build receipt `arb-step-mkdocs-01fb9557cf9f4e31a6f221f4fdcb06ff` (exit 0); `gz cli audit` clean (90/90); `gz validate --documents` clean.

### Implementation Summary


- Files modified: `AGENTS.md` (§ Attestation Lane behavior block + Receipt IDs sentence rewritten to cite the mechanical `gz validate --attestation-receipts` gate and the `arb-meta-receipt-bind-…` family); `docs/governance/arb-middleware.md` (new `## Receipt-binding gate` subsection with invocation point, meta-receipt family, failure-mode table, lane/kind matrix, ADR-0.0.24 cross-link); `docs/user/commands/validate.md` (`--attestation-receipts` section expanded with failure-mode table and `#### Examples` block carrying two real session-captured PASS/FAIL invocations); `docs/user/runbook.md` (step 4b note that citation is mechanically verified inside `gz obpi complete` / `gz adr emit-receipt`).
- Files created: `.claude/plans/OBPI-0.0.24-03-doc-updates.md` (approved plan, plan-audit verdict PASS).
- Tests added: n/a (docs-only OBPI; BDD coverage deferred to OBPI-0.0.24-04 per parent ADR checklist item #4).
- Date completed: 2026-05-02.
- Attestation status: operator attested in Stage 4 ("attest completed"); foundation+heavy attestation rigor satisfied via `--attestor-present` co-presence proxy (active pipeline marker present per GHI #292).
- Defects noted: none.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — OBPI-0.0.24-03 doc-updates closes the docs-side gap of ADR-0.0.24's mechanical receipt-binding contract: AGENTS.md § Attestation now cites `gz validate --attestation-receipts` as the mechanical gate (no longer narrative discipline), `docs/governance/arb-middleware.md` carries the new § Receipt-binding gate subsection with invocation point + `arb-meta-receipt-bind-…` family + missing/status_mismatch/claim_mismatch failure modes, `docs/user/commands/validate.md` carries two real session-captured PASS/FAIL EXAMPLES (no placeholders, REQ-08), and `docs/user/runbook.md` step 4b notes the gate is mechanically enforced inside `gz obpi complete` / `gz adr emit-receipt`. Heavy-lane ARB evidence: lint clean (lint: receipt arb-ruff-7b1d21ab042d4c0d90097e8c6ba88fa9), docs strict build clean (mkdocs: receipt arb-step-mkdocs-01fb9557cf9f4e31a6f221f4fdcb06ff). `gz cli audit` clean (90/90 commands fully covered, REQ-05); `gz validate --documents` clean (REQ-06); PII grep clean across all four edited files (REQ-07). 4 files modified, 1 plan file created, 0 tests (docs-only; BDD deferred to OBPI-04 per parent ADR checklist).
- Date: 2026-05-02

---

**Brief Status:** Completed

**Date Completed:** 2026-05-02

**Evidence Hash:** -
