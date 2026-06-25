---
id: OBPI-0.0.74-17-gate5-invariants-floor-migration
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 17
lane: Heavy
# req_atomic: each REQ is one coherent @enforces-plus-live-NC authoring increment
# for one gate5_invariants member — secrets (01), operator-pii (02), ledger (03),
# gate5-attestation-absence (04) — plus the enrollment-completeness fence (05).
# None decomposes into parallel seq=02+ sub-tasks (ADR-0.0.64 task-envelope
# exemption).
req_atomic:
  - REQ-0.0.74-17-01  # @enforces + live un-forced NC for secrets (synthetic planted secret), or honest named-not-enforced
  - REQ-0.0.74-17-02  # @enforces + live un-forced NC for operator-pii (SYNTHETIC PII match), or honest named-not-enforced
  - REQ-0.0.74-17-03  # @enforces + live un-forced NC for ledger (temp ledger, broken hash chain)
  - REQ-0.0.74-17-04  # @enforces + live un-forced NC for gate5-attestation ABSENCE case (forgery is OUT)
  - REQ-0.0.74-17-05  # STRUCTURAL-FENCE: gate5 floor enrollment completeness enumerated over GATE5_INVARIANTS (BI#9)
status: Completed
---

# OBPI-0.0.74-17-gate5-invariants-floor-migration: Gate5 Invariants Floor Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #17 - "gate5_invariants floor migration — live un-forced negative controls for the four `GATE5_INVARIANTS` members lacking one (secrets, operator-pii, ledger, gate5-attestation-absence), each running its real path against a synthetic violation (grader-gaming is item 13); honest negative — secrets/operator-pii have no bound gate5 entrypoint today, forbid binding a narrower proxy; unit tests"

**Status:** Completed

## Objective

Migrate the never-relax `gate5_invariants` floor (`src/gzkit/mx/invariants.py`, OBPI-03) onto the `@enforces` surface: declare an `@enforces` entry and author a live UN-FORCED negative control for each of the four members lacking one — `secrets` (a synthetic planted secret), `operator-pii` (a SYNTHETIC PII-shaped match, NEVER the operator's real email), `ledger` (a temp ledger with a broken hash chain run through the real ledger-integrity path), and `gate5-attestation` (the ABSENCE case only — a missing attestation on a heavy/foundation completion rejected through the real `_requires_human_obpi_attestation` gate). `grader-gaming`'s entry + live NC are OBPI-0.0.74-13. **Honest negative (binding):** `secrets` (only a handoff-scoped `validate_no_secrets` regex in `handoff_validation.py`) and `operator-pii` (only an insights-scoped `_EMAIL_RE` scrubber in `correction_mining.py`) have NO bound *gate5* production entrypoint today — bind to the genuine production gate where one exists, or surface the member as a named-not-enforced facade and route standing up the real gate as named prerequisite work; NEVER bind a narrower proxy entrypoint and call the claim proved. "Done" = each of the four members carries an `@enforces` entry whose live un-forced NC runs the real path against a synthetic violation and is caught (or is honestly surfaced as named-not-enforced where no gate5 gate exists), and the enrollment-completeness fence holds.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the `@enforces` enrollment and live negative controls that make the `gate5_invariants` floor §5-compliant — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 17, § Consequences/Negative #7, § Boundary Invariants #9)
- `src/gzkit/mx/invariants.py` — declare the four `@enforces` entries on the `GATE5_INVARIANTS` members (the floor constant + its enrollment)
- `tests/mx/test_gate5_invariants_live_nc.py` **CREATE** — the four live un-forced negative controls (synthetic planted secret, SYNTHETIC PII-shaped match, temp ledger with broken hash chain, missing-attestation absence), each running its real path and asserting the violation is caught
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-17-gate5-invariants-floor-migration.md` — this brief (evidence recording)

(Security overlap check: no Allowed Path matches a glob in `data/security_surfaces.json` — `src/gzkit/mx/invariants.py` is the floor-membership constant module, not a `*secret*`/`*credential*`/`*token*`/ledger/auth surface; the secrets/operator-pii/ledger/attestation production callables are REFERENCED as `@enforces` entrypoints, not edited here (their internals are in the Denied Paths). `sensitivity: security` is not declared. If implementation finds it MUST edit a registered scanner surface to bind a genuine entrypoint, STOP and declare `sensitivity: security` per `.claude/rules/security-sensitivity.md`.)

## Creates These Files

- `tests/mx/test_gate5_invariants_live_nc.py`

## Denied Paths

- Paths not listed in Allowed Paths
- Binding a NARROWER proxy entrypoint to fake coverage where no gate5 production gate exists (secrets, operator-pii) — the honest negative forbids it; surface the member as named-not-enforced and route the real gate as prerequisite work
- Using the operator's REAL email or any real secret/credential in a fixture — the operator-pii NC uses a SYNTHETIC PII-shaped match only (operator-PII prohibition, AGENTS.md)
- `grader-gaming`'s `@enforces` entry + live NC — owned by OBPI-0.0.74-13
- The `@enforces` decorator/registry (OBPI-15) and the runner (OBPI-16) — this OBPI declares claims, it does not redefine the primitive
- Forgery-detection for gate5-attestation — explicitly OUT; canon holds the operator's verbatim relayed attestation IS Gate 5, so there is no forgery surface to NC; only the ABSENCE case is NC-able
- Editing the scanner/gate internals (`src/gzkit/handoff_validation.py`, `src/gzkit/insights/correction_mining.py`, `src/gzkit/ledger.py`, `src/gzkit/commands/obpi_complete.py`) — bound as entrypoints, not modified here
- Relaxing or redefining the `GATE5_INVARIANTS` never-relax list (owned by OBPI-0.0.74-03)
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `secrets` MUST carry an `@enforces` entry whose live un-forced NC plants a synthetic secret and runs the real secrets path, asserting it is caught — OR, if no gate5 secrets production entrypoint exists, the member MUST be surfaced as a named-not-enforced facade with the real gate routed as prerequisite work; a narrower proxy MUST NOT be bound (REQ-17-01).
1. REQUIREMENT: `operator-pii` MUST carry an `@enforces` entry whose live un-forced NC uses a SYNTHETIC PII-shaped match (NEVER the operator's real email) through the real detector, asserting it is caught — OR be honestly surfaced as named-not-enforced with no narrower proxy bound (REQ-17-02).
1. REQUIREMENT: `ledger` MUST carry an `@enforces` entry whose live un-forced NC constructs a temp ledger with a broken hash chain and runs the real ledger-integrity path, asserting it is caught (REQ-17-03).
1. REQUIREMENT: `gate5-attestation` MUST carry an `@enforces` entry whose live un-forced NC exercises the ABSENCE case only — a missing attestation on a heavy/foundation completion rejected through the real `_requires_human_obpi_attestation` gate; forgery-detection is OUT (REQ-17-04).
1. REQUIREMENT: The meta-validator's gate5 claim-source MUST enumerate `GATE5_INVARIANTS` membership and require each member to carry an `@enforces` entry with a passing un-forced NC (or an honest named-not-enforced surfacing); a member with no entry MUST fail the floor (REQ-17-05).
1. NEVER: Bind a narrower proxy entrypoint to manufacture coverage, use a real secret/PII value, or force any NC — D1 genuineness is absolute and the honest-negative is binding (REQ-17-01, REQ-17-02).
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; the `@enforces` registry (OBPI-15), the runner (OBPI-16), and `GATE5_INVARIANTS` (`src/gzkit/mx/invariants.py`, OBPI-03) MUST exist first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 17 — quoted verbatim:** "gate5_invariants floor migration — declare `@enforces` + live un-forced NCs for the four `GATE5_INVARIANTS` members lacking one: secrets (a synthetic planted secret), operator-pii (a SYNTHETIC PII-shaped match, **NEVER** the operator's real email), ledger (a temp ledger with a broken hash chain), gate5-attestation (the **ABSENCE** case only ... forgery-detection is OUT ...). `grader-gaming`'s entry arrives via item 13. **Honest negative:** secrets and operator-pii have NO bound gate5 production entrypoint today — name this in the brief and FORBID binding a narrower proxy to fake it ... (OBPI-17)"
- [ ] Parent ADR § Consequences/Negative #7 — the honest-negative (secrets/operator-pii have no bound gate5 entrypoint today; never bind a narrower proxy).
- [ ] Parent ADR § Boundary Invariants #9 (gate5 floor enrollment completeness enumerated) and § Decision item 3 (the `GATE5_INVARIANTS` never-relax floor this migrates).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract; the operator-PII prohibition (synthetic match only)
- [ ] `.claude/rules/security-sensitivity.md` — the auto-detect sensitivity floor; STOP and declare `sensitivity: security` if a registered scanner surface must be edited
- [ ] `.claude/rules/governance-core.md` § human attestation is sacrosanct — why gate5-attestation forgery is OUT and only the absence case is NC-able

**Context:**

- [ ] `src/gzkit/mx/invariants.py` — `GATE5_INVARIANTS` membership (`secrets`, `operator-pii`, `ledger`, `gate5-attestation`, `grader-gaming`) the `@enforces` entries enroll
- [ ] `src/gzkit/handoff_validation.py` — `validate_no_secrets` (handoff-scoped regex; NOT a unified gate5 secrets gate — the honest-negative case)
- [ ] `src/gzkit/insights/correction_mining.py` — `_EMAIL_RE` (insights-scoped scrubber; NOT a unified gate5 PII gate — the honest-negative case)
- [ ] `src/gzkit/commands/obpi_complete.py` — `_requires_human_obpi_attestation` (the real gate the attestation-absence NC runs through)
- [ ] The ledger-integrity validator (`src/gzkit/validate_pkg/ledger_check.py` / the ledger proof path) — the real path the broken-hash-chain NC runs through

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/enforcement.py` exists with `@enforces` + runner (OBPI-0.0.74-15, -16 have landed)
- [ ] `src/gzkit/mx/invariants.py` exists with `GATE5_INVARIANTS` (OBPI-0.0.74-03 has landed)
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/mx/test_gate5_invariants.py` reviewed for the local test convention before authoring `test_gate5_invariants_live_nc.py`
- [ ] `src/gzkit/governance/trust_audits/_qc_negative_controls.py` reviewed for the construct-violation / run-real-path / assert-caught shape (re-authored un-forced in OBPI-16)
- [ ] The four candidate entrypoints inspected to determine which have a genuine gate5 production path and which must be surfaced as named-not-enforced

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
test -f src/gzkit/mx/invariants.py
test -f tests/mx/test_gate5_invariants_live_nc.py
```

## Demo

```bash
# Each enrolled gate5 floor member runs its real path against a synthetic
# violation; the meta-validator (OBPI-16) reports them as covered, not named.
uv run python -c "from gzkit import enforcement; print('gate5 floor claims:', [c for c in enforcement.registered_claims() if c.startswith('gate5:')])"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-17-01 [behavior]: Given the `secrets` floor member, when its live un-forced NC plants a synthetic secret and runs the real secrets path, then the violation is caught — OR, where no gate5 secrets production entrypoint exists, the member is surfaced as named-not-enforced with no narrower proxy bound. (@covers test in `tests/mx/test_gate5_invariants_live_nc.py`)
- [ ] REQ-0.0.74-17-02 [behavior]: Given the `operator-pii` floor member, when its live un-forced NC runs a SYNTHETIC PII-shaped match (never the operator's real email) through the real detector, then the violation is caught — OR the member is surfaced as named-not-enforced with no narrower proxy bound. (@covers test in `tests/mx/test_gate5_invariants_live_nc.py`)
- [ ] REQ-0.0.74-17-03 [behavior]: Given the `ledger` floor member, when its live un-forced NC builds a temp ledger with a broken hash chain and runs the real ledger-integrity path, then the violation is caught. (@covers test in `tests/mx/test_gate5_invariants_live_nc.py`)
- [ ] REQ-0.0.74-17-04 [behavior]: Given the `gate5-attestation` floor member, when its live un-forced NC presents a missing attestation on a heavy/foundation completion to the real `_requires_human_obpi_attestation` gate, then the absence is rejected (forgery-detection is OUT). (@covers test in `tests/mx/test_gate5_invariants_live_nc.py`)
- [ ] REQ-0.0.74-17-05 [structural-fence]: The meta-validator's gate5 claim-source enumerates `GATE5_INVARIANTS` membership and requires each member to carry an `@enforces` entry with a passing un-forced NC (or honest named-not-enforced surfacing); a member with no entry fails the floor (parent ADR § Boundary Invariants #9 — every gate5 floor member's enforcement is live, enrollment completeness enumerated).

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

Before: the `gate5_invariants` never-relax floor named five members but only `ledger` and `gate5-attestation` had any bound production path; `secrets` and `operator-pii` were floor members with no live enforcement — exactly the facade §5 forbids (a member named but not generally enforced). Now: each member carries an `@enforces` entry whose live un-forced NC runs the real path against a synthetic violation and is caught — and where no gate5 production gate exists, the member is honestly surfaced as named-not-enforced (never a faked narrower proxy), routing the real gate as named prerequisite work.

### Key Proof


Both bound gate5 floor claims PASS through the real meta-validator runner: run_meta_validator(gate5 registry) returns verified=2 facade=0 test_bug=0 with gate5-ledger -> PASS and gate5-attestation-absence -> PASS. Genuineness mutation-verified: gutting any real production path (validate_ledger -> [], _validate_obpi_human_attestation_fields -> no-raise, _requires_human_obpi_attestation -> False) FACADE-fails the corresponding catch-test. Receipts: arb-step-unittest-87fbfb05b85841f894d109c37bb2f5ef (6471/6471 pass), arb-ruff-baaff749264f472598a95d3bf2e19317, arb-step-typecheck-f92749a720b94379969c79485d88bc43, arb-step-mkdocs-f547129b3959452ebc4cea98ea681ef9. Covers parity: behavior_uncovered=0 (REQ-17-05 is structural-fence, proved at ADR closeout via parent ADR Boundary Invariants #9).

### Implementation Summary


- Decision item 17 (verbatim): gate5_invariants floor migration — declare @enforces + live un-forced NCs for the four GATE5_INVARIANTS members lacking one (secrets, operator-pii, ledger, gate5-attestation-absence); honest negative — secrets/operator-pii have no bound gate5 entrypoint today, forbid binding a narrower proxy.
- Bound members: gate5-ledger runs the real validate_ledger integrity path against a schema-corrupted ledger (gzkit ledger has no cryptographic hash chain; the brief's "broken hash chain" is realized as JSONL schema corruption); gate5-attestation-absence runs the real _requires_human_obpi_attestation gate plus _validate_obpi_human_attestation_fields validator against a missing attestation.
- Honest negative: secrets/operator-pii surfaced via _GATE5_NAMED_NOT_ENFORCED — no @enforces entry, no narrower proxy bound (tests enforce the prohibition).
- Files: src/gzkit/mx/invariants.py (modified — gate5 registration); tests/mx/test_gate5_invariants_live_nc.py (created — 12 tests); brief (modified — added REQ-17-05 REQUIREMENT line).
- Tests added: 12 (4 NCs, 4 genuineness guards, 2 named-not-enforced, 2 idempotency/structure).
- Date completed: 2026-06-25
- Attestation status: operator-verbatim ("attest completed"), Gate 5 universal.
- Defects noted: Step-4b adversary weakest-point (attestation NC re-implemented production emptiness check) fixed in-flight by binding the real _validate_obpi_human_attestation_fields; mutation-verified seam-closed.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.74-17 gate5_invariants floor migration verified: gate5-ledger and gate5-attestation-absence carry live un-forced @enforces NCs running the real validate_ledger and _requires_human_obpi_attestation/_validate_obpi_human_attestation_fields production paths (both PASS through run_meta_validator: verified=2 facade=0 test_bug=0); secrets and operator-pii honestly surfaced as named-not-enforced with no narrower proxy bound; 6471/6471 unittests (receipt arb-step-unittest-87fbfb05b85841f894d109c37bb2f5ef), ruff/ty/mkdocs clean (arb-ruff-baaff749264f472598a95d3bf2e19317, arb-step-typecheck-f92749a720b94379969c79485d88bc43, arb-step-mkdocs-f547129b3959452ebc4cea98ea681ef9); independent adversary returned NOT-REFUTED, its one weakest-point seam fixed in-flight and mutation-verified closed. Heavy lane / foundation kind Gate 5 universal.
- Date: 2026-06-25

---

**Date Completed:** 2026-06-25

**Evidence Hash:** -
