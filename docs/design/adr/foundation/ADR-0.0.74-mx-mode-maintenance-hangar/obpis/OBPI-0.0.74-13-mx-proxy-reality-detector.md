---
id: OBPI-0.0.74-13-mx-proxy-reality-detector
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 13
lane: Heavy
status: Draft
req_atomic:
  # The proxy-reality detector is one indivisible authoring unit: the detector that
  # records "a gate went green AND reality was later found wrong" and counts it
  # (proxy_reality.py), and the passing-on-violation live negative control that
  # constructs a known violation and asserts it is caught, ship together with one
  # covering test module. No REQ below decomposes into independently-attributable
  # labor steps.
  - REQ-0.0.74-13-01  # the detector records the gate that cleared a later-found-wrong reality, as a count
  - REQ-0.0.74-13-02  # the live negative control plants a known violation, runs the real path, asserts caught
  - REQ-0.0.74-13-03  # STRUCTURAL-FENCE: grader-gaming's floor membership is bound to this live NC (BI#5)
---

# OBPI-0.0.74-13-mx-proxy-reality-detector: Mx Proxy Reality Detector

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`
- **Checklist Item:** #13 - "The proxy-reality distance detector — grader-gaming's live §5 negative control: a record of "a gate went green AND reality was later found wrong — here is the gate that cleared it"; makes grader-gaming measurable; unit tests"

**Status:** Draft

## Objective

The proxy-reality distance detector lands at `src/gzkit/mx/proxy_reality.py`: it reads the ledger for the "a gate went green AND reality was later found wrong" signal — the canonical such record is a `gz obpi repudiate --cause model-induced-fabrication` event (a completion cleared a gate, reality was later found wrong) — and produces a record naming the gate that cleared each instance plus a count, turning grader-gaming from a conviction into a number (the north-star instrument). It ships WITH its live negative control: a passing-on-violation test that constructs a known proxy-reality-distance violation, runs the real detection path in production configuration, and asserts it is caught. "Done" = the detector counts the gate-green-but-reality-wrong instances from real ledger signals, the live NC catches a planted violation, and grader-gaming's floor membership (OBPI-03 / BI#3) is no longer a named aspiration but a bound, measured control.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the live negative control that keeps `grader-gaming`'s `gate5_invariants` floor membership §5-compliant — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 13, § Boundary Invariants #5)
- `src/gzkit/mx/proxy_reality.py` **CREATE** — the detector: reads the ledger for gate-green-but-reality-wrong signals, records the clearing gate, and counts them; the live-NC entry point
- `tests/mx/test_proxy_reality.py` **CREATE** — unit tests including the passing-on-violation live negative control (plant a known violation, run the real path, assert caught)
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-13-mx-proxy-reality-detector.md` — this brief (evidence recording)

(Security overlap check: no Allowed Path matches a glob in `data/security_surfaces.json` — the detector READS the ledger via the public reader, it does not edit `ledger.py`/`ledger_events.py`/`ledger_proof.py`/`ledger_semantics.py`; `sensitivity: security` is not declared.)

## Creates These Files

- `src/gzkit/mx/proxy_reality.py`
- `tests/mx/test_proxy_reality.py`

## Denied Paths

- Paths not listed in Allowed Paths
- Editing ledger internals (`src/gzkit/ledger.py`, `ledger_events.py`, `ledger_proof.py`, `ledger_semantics.py`) — the detector reads existing events, it does not add a new event type or mutate the ledger writer (would require `sensitivity: security`)
- Redefining or relaxing the `gate5_invariants` never-relax list (owned by OBPI-0.0.74-03)
- Stubbing the negative control — a non-executing or always-pass NC is the facade §5 forbids
- New dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/mx/proxy_reality.py` MUST read the ledger for "a gate went green AND reality was later found wrong" signals (canonically a `repudiated` event with cause `model-induced-fabrication`) and produce a record naming the gate that cleared each instance plus a count (REQ-13-01).
1. REQUIREMENT: The detector MUST ship a live negative control that constructs a known proxy-reality-distance violation, runs the REAL detection path in production configuration, and asserts the violation is caught — passing-on-violation, never a stub (REQ-13-02).
1. REQUIREMENT: `grader-gaming`'s `gate5_invariants` floor membership MUST be bound to this live negative control; a floor claim with no passing-on-violation live NC is facade and is rejected (REQ-13-03).
1. NEVER: Mark the OBPI accepted while the negative control is a stub or always-passes — that is the §5 facade this OBPI exists to prevent.
1. ALWAYS: Reconcile the brief with the parent ADR before implementation; the `gate5_invariants` constant (`src/gzkit/mx/invariants.py`, OBPI-03, with `grader-gaming` as a member) MUST exist first — STOP if missing.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 13 — quoted verbatim:** "The proxy-reality distance detector — grader-gaming's live §5 negative control. A record of *"a gate went green AND reality was later found wrong — here is the gate that cleared it."* It turns grader-gaming from conviction into a count (the north-star instrument) and is the passing-on-violation live control that keeps grader-gaming's floor membership (item 3) §5-compliant rather than a named aspiration."
- [ ] Parent ADR § Boundary Invariants #5 — "Every floor member's enforcement is live, not named" (the §5 enforcement-claim rule this OBPI satisfies).
- [ ] Parent ADR § Decision item 3 — `grader-gaming` joining the `gate5_invariants` floor (the membership this NC makes live).
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `.claude/rules/governance-core.md` § Withdraw vs Repudiate — `gz obpi repudiate --cause model-induced-fabrication` is the canonical "gate cleared, reality later wrong" record this detector counts

**Context:**

- [ ] `src/gzkit/mx/invariants.py` (OBPI-03) — `grader-gaming`'s floor membership this NC binds
- [ ] The ledger reader surface (`gzkit.ledger` / events) — how repudiation events are read without mutating the ledger
- [ ] `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — the existing passing-on-violation NC pattern to mirror

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/mx/invariants.py` exists with `grader-gaming` as a `gate5_invariants` member (OBPI-0.0.74-03 has landed)
- [ ] `.gzkit/ledger.jsonl` and the public ledger reader are available
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `tests/mx/test_checkpoint.py` reviewed for the local test convention before authoring `test_proxy_reality.py`
- [ ] An existing negative control (`_qc_negative_controls.py`) reviewed for the construct-violation / run-real-path / assert-caught shape

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
test -f src/gzkit/mx/proxy_reality.py
test -f tests/mx/test_proxy_reality.py
```

## Demo

```bash
# Grader-gaming becomes a count: the detector names each gate that cleared a
# later-found-wrong reality (repudiation, cause model-induced-fabrication).
uv run python -c "from gzkit.mx import proxy_reality; r = proxy_reality.scan(); print('proxy-reality distance count:', r.count)"
```

## Acceptance Criteria

- [ ] REQ-0.0.74-13-01 [behavior]: Given the ledger, when `proxy_reality.scan()` runs, then it records each "a gate went green AND reality was later found wrong" instance (canonically a `repudiated` event with cause `model-induced-fabrication`), naming the gate that cleared it, and reports a count — grader-gaming becomes a number, not a conviction. (@covers test in `tests/mx/test_proxy_reality.py`)
- [ ] REQ-0.0.74-13-02 [behavior]: Given the live negative control, when it runs in production configuration, then it constructs a known proxy-reality-distance violation, runs the REAL detection path, and asserts the violation is caught — the control passes on a planted violation and is not a stub. (@covers test in `tests/mx/test_proxy_reality.py`)
- [ ] REQ-0.0.74-13-03 [structural-fence]: `grader-gaming`'s `gate5_invariants` floor membership (BI#3) is bound to this live negative control; a floor claim with no passing-on-violation live NC is facade and is rejected (parent ADR § Boundary Invariants #5 — every floor member's enforcement is live, not named).

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

Before: `grader-gaming` was named the most concerning training trend (Opus 4.8 § 6.1.2) but it could only be asserted, not measured — a floor member with no live detector, exactly the facade §5 forbids. Now: the proxy-reality distance detector reads the ledger's own "gate cleared, reality later wrong" record (repudiation, cause model-induced-fabrication) and turns grader-gaming into a count, and its passing-on-violation live negative control proves the detector actually catches a planted violation — so the floor claim is enforced, not aspirational.

### Key Proof

### Implementation Summary

- **Decision item 13 (verbatim):** "The proxy-reality distance detector — grader-gaming's live §5 negative control. A record of *"a gate went green AND reality was later found wrong — here is the gate that cleared it."* It turns grader-gaming from conviction into a count (the north-star instrument) and is the passing-on-violation live control that keeps grader-gaming's floor membership (item 3) §5-compliant rather than a named aspiration."
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
