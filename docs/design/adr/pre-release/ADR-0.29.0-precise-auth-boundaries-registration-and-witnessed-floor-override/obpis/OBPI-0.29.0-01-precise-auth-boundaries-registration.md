---
id: OBPI-0.29.0-01-precise-auth-boundaries-registration
parent: ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override
item: 1
lane: heavy
sensitivity: security
status: Draft
---

# OBPI-0.29.0-01-precise-auth-boundaries-registration: Extract `obpi_security_gate.py` from `obpi_complete.py` and re-point `data/security_surfaces.json` `auth_boundaries` so the security floor watches only the surfaces that genuinely decide who-must-attest.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md`
- **Checklist Item:** #1 — "OBPI-0.29.0-01: Extract obpi_security_gate.py from obpi_complete.py and re-point data/security_surfaces.json auth_boundaries (KEEP adr_audit.py, ADD obpi_security_gate.py, DROP obpi_complete.py + obpi_cmd.py); fail-close message names the matched surface + category; verify each de-registered gate genuinely delegates its auth decision to adr_audit.py."

**Status:** Draft

## Objective

Make the `auth_boundaries` security floor PRECISE without making it weaker. Extract the security-scan gate cluster (`_enforce_security_review_gate`, `_security_canonical_slot_filled`, `_load_security_checklist`, `_find_fresh_security_receipt`, `_render_security_walkthrough` plus their module constants) from `src/gzkit/commands/obpi_complete.py` into a new focused module `src/gzkit/commands/obpi_security_gate.py`, imported read-only by `obpi_complete.py`. Re-point `data/security_surfaces.json` `auth_boundaries.globs` to KEEP `adr_audit.py`, ADD `obpi_security_gate.py`, and DROP `obpi_complete.py` and `obpi_cmd.py`. Before de-registering, VERIFY each de-registered gate genuinely delegates its auth decision to `adr_audit.py`; the slot-unfilled fail-close message MUST name the matched surface and category.

## Lane

**Heavy** — This OBPI changes the security-floor registration (a runtime governance contract read by `gz validate --sensitivity`) and carries `sensitivity: security` because its Allowed Paths overlap the registered `auth_boundaries` surface (`obpi_complete.py`) and edit `data/security_surfaces.json` (self-bootstrapping registry).

> Heavy is reserved for command/API/schema/runtime-contract changes. The security-floor registration is a runtime governance contract; this OBPI changes it.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/obpis/OBPI-0.29.0-01-precise-auth-boundaries-registration.md` — this brief (evidence + ceremony updates)
- `src/gzkit/commands/obpi_security_gate.py` — **CREATE** NEW module receiving the extracted security-scan cluster
- `src/gzkit/commands/obpi_complete.py` — remove the moved cluster; import it back read-only
- `data/security_surfaces.json` — re-point the `auth_boundaries` globs
- `tests/commands/` — REQ-derived unittest cases for the extraction and the fail-close message

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/commands/adr_audit.py` — the genuine auth authority STAYS registered and untouched
- Any symbol-level or diff-level detection mechanism (detection stays path-based — ADR-0.0.22)
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The security-scan gate cluster MUST live in `src/gzkit/commands/obpi_security_gate.py` after this OBPI; `obpi_complete.py` MUST import those symbols read-only rather than define them.
2. REQUIREMENT: `data/security_surfaces.json` `auth_boundaries.globs` MUST keep `src/gzkit/commands/adr_audit.py`, add `src/gzkit/commands/obpi_security_gate.py`, and MUST NOT contain `src/gzkit/commands/obpi_complete.py` or `src/gzkit/commands/obpi_cmd.py`.
3. REQUIREMENT: The slot-unfilled fail-close raised by the extracted gate MUST name the matched registered surface and the category that fired (not merely "slot unfilled").
4. REQUIREMENT: Each de-registered gate (receipt-binding, coverage-waiver) MUST be verified to delegate its auth decision to `adr_audit.py`; ANY gate found to make a LOCAL authoritative auth decision MUST have that function moved into `obpi_security_gate.py` (so no authoritative auth symbol is left in a de-registered file).
5. REQUIREMENT: Detection MUST remain path-based on a brief's declared Allowed Paths (ADR-0.0.22); NEVER introduce symbol-level or diff-level detection.
6. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation (`.gzkit/rules/tests.md` § "Tests assert semantics, not strings").

> SCOPE BOUNDARY: The `security_floor_overridden` ledger event and its emission are OBPI-0.29.0-02's scope; the `--auth-surface-coherence` validator and docs are OBPI-0.29.0-03's scope. The extraction here moves the console-only print verbatim into `obpi_security_gate.py`; replacing it with the event is OBPI-02.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary. The Decision item is the contract.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override/ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/security-sensitivity.md` — the floor contract and self-bootstrapping registry rule
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] `src/gzkit/commands/obpi_complete.py:72-254` — the cluster being moved
- [ ] `src/gzkit/commands/adr_audit.py` — `_requires_human_obpi_attestation`, `_enforce_human_attestation_authenticity`, `_enforce_uncovered_acceptance_confirmation` (the auth authority that stays registered)

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `src/gzkit/commands/obpi_complete.py`
- [ ] Required path exists: `data/security_surfaces.json`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing security-gate tests adjacent to the Allowed Paths reviewed before extraction
- [ ] Delegation verification (REQ-04) completed before any de-registration

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
- [ ] Relevant docs updated (registration change noted where consumed)

### Gate 4: BDD (Heavy only)

- [ ] External surface (registration + fail-close message) covered by direct unit tests; no new `.feature` required

### Gate 5: Human (security sensitivity)

- [ ] Human attestation recorded with the extended security walkthrough

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.commands.test_obpi_security_gate -v
uv run gz validate --sensitivity
```

## Demo

```bash
# The extracted cluster lives in its own module, imported read-only by obpi_complete.py
uv run python -c "from gzkit.commands.obpi_security_gate import _enforce_security_review_gate; print('extracted OK')"

# auth_boundaries no longer globs obpi_complete.py / obpi_cmd.py
uv run python -c "import json; g=[c for c in json.load(open('data/security_surfaces.json')) if c['category']=='auth_boundaries'][0]['globs']; print(g)"
```

## Acceptance Criteria

- [ ] REQ-0.29.0-01-01 [BEHAVIOR]: Given the post-extraction source tree, when `from gzkit.commands.obpi_security_gate import _enforce_security_review_gate, _security_canonical_slot_filled, _load_security_checklist, _find_fresh_security_receipt, _render_security_walkthrough` is executed, then all five symbols resolve from `obpi_security_gate.py` and `obpi_complete.py` references them via import (not local definition).
- [ ] REQ-0.29.0-01-02 [BEHAVIOR]: Given `data/security_surfaces.json`, when the `auth_boundaries` category globs are read, then they contain `src/gzkit/commands/adr_audit.py` and `src/gzkit/commands/obpi_security_gate.py` and do NOT contain `src/gzkit/commands/obpi_complete.py` or `src/gzkit/commands/obpi_cmd.py`.
- [ ] REQ-0.29.0-01-03 [BEHAVIOR]: Given a `sensitivity:security` brief and an unfilled canonical security slot, when the extracted gate fails closed, then the error message names the matched registered surface and the category (`auth_boundaries`) that fired, not merely "slot unfilled".
- [ ] REQ-0.29.0-01-04 [BEHAVIOR]: Given each de-registered gate (receipt-binding, coverage-waiver) in `obpi_complete.py`, when its auth-decision path is inspected by a test asserting delegation, then it calls into `adr_audit.py` for the human-presence / who-must-attest decision (no LOCAL authoritative auth decision remains in a de-registered file); any local-authority function is instead defined in `obpi_security_gate.py`.
- [ ] REQ-0.29.0-01-05 [STRUCTURAL-FENCE]: The detection mechanism remains path-based on a brief's declared Allowed Paths — no symbol-level or diff-level detection is introduced — per parent ADR `## Boundary Invariants` invariant 2.

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
# Direct unit tests cover the external surface; no behave run required
```

### Gate 5 (Human)

```text
# Record attestation text here (security-sensitivity walkthrough)
```

### Value Narrative

Before this OBPI, the `auth_boundaries` floor globbed three whole command modules, so any edit to `obpi_complete.py` — even an additive, structural reconciliation gate that touched no auth semantics — auto-classified the editing brief `sensitivity:security` and forced `--accept-security-floor` (the GHI #583 deadlock). The floor cried wolf, training reflexive overrides and eroding its own anti-vibe signal.

After this OBPI, the auth-bearing security-scan cluster lives in its own registered module (`obpi_security_gate.py`), `adr_audit.py` stays registered as the genuine who-must-attest authority, and `obpi_complete.py` / `obpi_cmd.py` are de-registered. Edits to `obpi_complete.py`'s non-auth body no longer trip the floor, while every real human-presence decision still does. Delegation is verified before de-registration, so no protection is silently dropped.

### Key Proof

Smoke run: `from gzkit.commands.obpi_security_gate import _enforce_security_review_gate` resolves; the `auth_boundaries` globs read `[src/gzkit/commands/adr_audit.py, src/gzkit/commands/obpi_security_gate.py]`.

### Implementation Summary

- Files created/modified: `src/gzkit/commands/obpi_security_gate.py` (new); `src/gzkit/commands/obpi_complete.py` (cluster removed, imported read-only); `data/security_surfaces.json` (`auth_boundaries` re-pointed); `tests/commands/test_obpi_security_gate.py` (REQ-derived cases).
- Tests added: REQ-0.29.0-01-01..04 BEHAVIOR cases; REQ-0.29.0-01-05 audited as a structural fence at ADR closeout.
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
