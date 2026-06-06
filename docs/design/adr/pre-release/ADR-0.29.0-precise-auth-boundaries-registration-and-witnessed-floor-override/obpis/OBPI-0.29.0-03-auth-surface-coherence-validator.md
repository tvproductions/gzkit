---
id: OBPI-0.29.0-03-auth-surface-coherence-validator
parent: ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override
item: 3
lane: heavy
sensitivity: security
status: Draft
---

# OBPI-0.29.0-03-auth-surface-coherence-validator: Add `gz validate --auth-surface-coherence` (drift-back fence asserting no attestation-authority symbols live outside the registered `auth_boundaries` surfaces), plus manpage + runbook docs and an advisory-rules-audit scorecard row.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md`
- **Checklist Item:** #3 — "OBPI-0.29.0-03: Add gz validate --auth-surface-coherence drift-back validator asserting no attestation-authority symbols live outside the registered auth_boundaries surfaces; plus manpage + runbook docs for the precise registration and override event, and an advisory-rules-audit.md scorecard row."

**Status:** Draft

## Objective

Mechanically prevent the narrowed `auth_boundaries` registration from silently eroding. Add a `gz validate --auth-surface-coherence` scope that fails closed (exit 3) when any attestation-authority symbol (`_requires_human_obpi_attestation`, `_enforce_human_attestation_authenticity`, `_enforce_uncovered_acceptance_confirmation`, and the extracted security-scan gate cluster) lives in a module NOT registered under `data/security_surfaces.json` `auth_boundaries`. Wire the scope into the `gz check` default roster. Document the precise registration and the override event in the validate manpage and both runbooks, and add an `advisory-rules-audit.md` scorecard row.

## Lane

**Heavy** — This OBPI adds a new `gz validate` scope (a CLI surface contract) and changes operator-facing docs. It carries `sensitivity: security` because the validator reasons about the registered `auth_boundaries` surfaces and its module lives under the security-floor governance surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. A new `gz validate --<scope>` is a CLI contract change.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/obpis/OBPI-0.29.0-03-auth-surface-coherence-validator.md` — this brief (evidence + ceremony updates)
- `src/gzkit/governance/trust_audits/` — new `--auth-surface-coherence` validator module + registration into `gz check`
- `src/gzkit/commands/validate_cmd.py` — wire the `--auth-surface-coherence` flag into the `validate` CLI surface
- `src/gzkit/cli/` — argparse registration for the `--auth-surface-coherence` flag (validate subparser)
- `docs/user/manpages/validate.md` — document the new scope (Synopsis / Options / Examples / Exit Codes)
- `docs/user/runbook.md` — operator runbook entry for the precise registration + override event
- `docs/governance/governance_runbook.md` — governance-maintainer runbook entry
- `docs/governance/advisory-rules-audit.md` — scorecard row for the new fence
- `tests/` — REQ-derived unittest cases (clean exit 0; drift-back exit 3; check-roster membership)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/commands/adr_audit.py` — untouched (it is the registered authority, not edited here)
- `data/security_surfaces.json` — re-pointing is OBPI-0.29.0-01's scope
- Any symbol-level brief-detection change (the validator audits source symbols against the registry; it does NOT change how briefs declare scope)
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `uv run gz validate --auth-surface-coherence` MUST be a registered scope; `gz validate --help` documents it, and a clean tree exits 0.
2. REQUIREMENT: When an attestation-authority symbol is present in a module NOT registered under `data/security_surfaces.json` `auth_boundaries`, `gz validate --auth-surface-coherence` MUST exit 3 and name the offending symbol and file.
3. REQUIREMENT: The `--auth-surface-coherence` audit MUST be a member of the `gz check` default step roster so drift-back fails the standard quality pipeline.
4. REQUIREMENT: `docs/user/manpages/validate.md`, `docs/user/runbook.md`, and `docs/governance/governance_runbook.md` MUST document the precise registration and the `security_floor_overridden` override event; `docs/governance/advisory-rules-audit.md` MUST carry a scorecard row for the new fence.
5. REQUIREMENT: The drift-back fence MUST enforce parent-ADR `## Boundary Invariants` invariant 1 (no attestation-authority symbol outside a registered `auth_boundaries` surface).
6. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation (`.gzkit/rules/tests.md` § "Tests assert semantics, not strings").

> SCOPE BOUNDARY: The extraction + re-point are OBPI-0.29.0-01's scope; the ledger event is OBPI-0.29.0-02's scope. This OBPI assumes both have landed (the validator reads the re-pointed registry and the docs describe the event).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary.
- [ ] Parent ADR § Boundary Invariants — invariant 1 is the contract this validator mechanizes.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/security-sensitivity.md` — the floor contract
- [ ] `docs/governance/advisory-rules-audit.md` — scorecard format
- [ ] `.claude/rules/cli.md` — CLI contract doctrine (new validate scope is heavy lane; `gz cli audit` must pass)
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] An existing `gz validate --<scope>` audit under `src/gzkit/governance/trust_audits/` reviewed as the implementation pattern
- [ ] The `gz check` step-roster builder reviewed for how a new audit is registered

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `data/security_surfaces.json` (re-pointed by OBPI-0.29.0-01)
- [ ] Required path exists: `src/gzkit/commands/validate_cmd.py`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing validate-scope tests adjacent to the Allowed Paths reviewed before implementation
- [ ] `gz cli audit` coverage requirement reviewed (new verb/flag must be covered across manpage + index)

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
- [ ] Manpage + both runbooks + advisory-rules-audit updated; `uv run gz cli audit` exits 0

### Gate 4: BDD (Heavy only)

- [ ] External surface (new validate scope) covered by direct CLI/validator unit tests; no new `.feature` required

### Gate 5: Human (security sensitivity)

- [ ] Human attestation recorded with the extended security walkthrough

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_auth_surface_coherence -v
uv run gz validate --auth-surface-coherence
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

```bash
# Clean tree: the fence passes
uv run gz validate --auth-surface-coherence; echo "exit=$?"

# Drift-back: moving an auth-authority symbol into a de-registered file fails closed
# (demonstrated by the REQ-0.29.0-03-02 test fixture)
uv run gz check 2>&1 | grep -i "auth-surface-coherence"
```

## Acceptance Criteria

- [ ] REQ-0.29.0-03-01 [BEHAVIOR]: Given a clean source tree, when `gz validate --auth-surface-coherence` is invoked, then it exits 0; and `gz validate --help` documents the `--auth-surface-coherence` scope.
- [ ] REQ-0.29.0-03-02 [BEHAVIOR]: Given a fixture where an attestation-authority symbol lives in a module not registered under `data/security_surfaces.json` `auth_boundaries`, when `gz validate --auth-surface-coherence` runs, then it exits 3 and names the offending symbol and its file.
- [ ] REQ-0.29.0-03-03 [BEHAVIOR]: Given the `gz check` default step roster, when it is built, then the `--auth-surface-coherence` audit is a member, so a drift-back fixture causes `gz check` to fail.
- [ ] REQ-0.29.0-03-04 [SUPPORT]: `docs/user/manpages/validate.md`, `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, and `docs/governance/advisory-rules-audit.md` document the precise registration, the `--auth-surface-coherence` scope, and the `security_floor_overridden` override event — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing those docs emitted at OBPI completion.
- [ ] REQ-0.29.0-03-05 [STRUCTURAL-FENCE]: No attestation-authority symbol lives outside a registered `auth_boundaries` surface, per parent ADR `## Boundary Invariants` invariant 1 — this OBPI's validator is the mechanical enforcement of that fence.

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
# Paste docs-build + cli audit output here
```

### Gate 4 (BDD)

```text
# Direct CLI/validator unit tests cover the external surface; no behave run required
```

### Gate 5 (Human)

```text
# Record attestation text here (security-sensitivity walkthrough)
```

### Value Narrative

Before this OBPI, nothing mechanical prevented an agent from later writing an attestation-authority decision into a de-registered file (`obpi_complete.py`, `obpi_cmd.py`). The narrowed `auth_boundaries` registration could silently erode — the floor would pass an edit that genuinely touched auth semantics (a silent security regression). This is the shakiest WWHTBT condition the parent ADR names.

After this OBPI, `gz validate --auth-surface-coherence` fails closed (exit 3) the moment an attestation-authority symbol appears outside a registered surface, and it is wired into `gz check` so the standard quality pipeline catches drift-back. The precise registration and the override event are documented in the manpage and both runbooks, with an advisory-rules-audit scorecard row.

### Key Proof

Smoke run: `uv run gz validate --auth-surface-coherence; echo "exit=$?"` exits 0 on a clean tree; a fixture moving an auth-authority symbol into a de-registered file makes the scope exit 3 and the `gz check` roster fail.

### Implementation Summary

- Files created/modified: validator module under `src/gzkit/governance/trust_audits/`; `src/gzkit/commands/validate_cmd.py` + `src/gzkit/cli/` (flag wiring); `docs/user/manpages/validate.md`; `docs/user/runbook.md`; `docs/governance/governance_runbook.md`; `docs/governance/advisory-rules-audit.md`; `tests/` (REQ-derived cases).
- Tests added: REQ-0.29.0-03-01,02,03 BEHAVIOR cases; REQ-0.29.0-03-04 SUPPORT (docs + ledger proof); REQ-0.29.0-03-05 STRUCTURAL-FENCE audited at ADR closeout.
- Date completed: pending.
- Attestation status: pending (security-sensitivity Gate 5).
- Defects noted: pending.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: pending
- Attestation: pending
- Date: pending

---

**Date Completed:** pending

**Evidence Hash:** -
