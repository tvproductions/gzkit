---
id: OBPI-0.0.74-13-mx-proxy-reality-detector
parent: ADR-0.0.74-mx-mode-maintenance-hangar
item: 13
lane: Heavy
status: Completed
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

**Status:** Completed

## Objective

The proxy-reality distance detector lands at `src/gzkit/mx/proxy_reality.py`: it reads the ledger for the "a gate went green AND reality was later found wrong" signal — the canonical such record is a `gz obpi repudiate --cause model-induced-fabrication` event (a completion cleared a gate, reality was later found wrong) — and produces a record naming the gate that cleared each instance plus a count, turning grader-gaming from a conviction into a number (the north-star instrument). It ships WITH its live negative control: a passing-on-violation test that constructs a known proxy-reality-distance violation, runs the real detection path in production configuration, and asserts it is caught. "Done" = the detector counts the gate-green-but-reality-wrong instances from real ledger signals, the live NC catches a planted violation, and grader-gaming's floor membership (OBPI-03 / BI#3) is no longer a named aspiration but a bound, measured control.

## Lane

**Heavy** - This OBPI ships a runtime-contract surface — the live negative control that keeps `grader-gaming`'s `gate5_invariants` floor membership §5-compliant — so all gates apply.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/req_kind.py` (added by brief reconcile, attestor g0)
- `src/gzkit/mx/__init__.py` (added by brief reconcile, attestor g0)

- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/ADR-0.0.74-mx-mode-maintenance-hangar.md` — parent ADR for intent and scope (§ Decision item 13, § Boundary Invariants #5)
- `src/gzkit/mx/proxy_reality.py` **CREATE** — the detector: reads the ledger for gate-green-but-reality-wrong signals, records the clearing gate, and counts them; the live-NC entry point
- `src/gzkit/enforcement.py` **EDIT** (allowlist amended 2026-06-27, operator-ratified) — wire `_ensure_grader_gaming_registered()` into the single production-discovery seam `_ensure_production_claims_registered()` so `grader-gaming` is LIVE (REQ-13-03). The brief originally deferred this to OBPI-19, but OBPI-19 shipped Completed without wiring the floor sources (the gate5 orphan, same seam); deferring to a closed OBPI is an orphan. The same edit cures OBPI-17's orphaned gate5 sources. Tracked: GHI for the OBPI-17/19 incomplete-implementation miss.
- `tests/mx/test_proxy_reality.py` **CREATE** — unit tests including the passing-on-violation live negative control (plant a known violation, run the real path, assert caught) AND regression tests asserting each floor member is registered by production discovery
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
# Grader-gaming's proxy-reality detector runs as a live negative control inside
# the meta-validator floor step. Pinned by tests/mx/test_proxy_reality.py.
uv run gz validate --qc-binding
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


The detector turns grader-gaming into a number against the real ledger:

```text
$ uv run python3 -c "from gzkit.mx import proxy_reality; r = proxy_reality.scan(); print('proxy-reality distance count:', r.count)"
proxy-reality distance count: 5
```

The §5 live negative control passes on a planted violation (real production path, no stub):

```text
$ uv run -m unittest tests.mx.test_proxy_reality.TestLiveNegativeControl.test_live_nc_catches_planted_violation -v
test_live_nc_catches_planted_violation ... ok
```

grader-gaming's floor membership is now LIVE in production discovery (the REQ-13-03 binding):

```text
$ uv run python3 -c "from gzkit.quality import run_enforcement_floor_audit; from pathlib import Path; r=run_enforcement_floor_audit(Path('.')); print(r.success, r.stdout.strip())"
True Enforcement floor: 41 claims verified.
```

Receipts: `arb-step-unittest-16894dfc4acb4cc18b8fb1cde33c5d24` (6560 tests OK),
`arb-ruff-f091d77627d04421a3641c5a576ed01c`,
`arb-step-typecheck-987b339f62234e11bdf18fd46fa242c3`,
`arb-step-mkdocs-42e28f1fb54c45889d58ddfdcd9f9e55`.

### Implementation Summary


- **Decision item 13 (verbatim):** "The proxy-reality distance detector — grader-gaming's live §5 negative control. A record of *"a gate went green AND reality was later found wrong — here is the gate that cleared it."* It turns grader-gaming from conviction into a count (the north-star instrument) and is the passing-on-violation live control that keeps grader-gaming's floor membership (item 3) §5-compliant rather than a named aspiration."
- Files created: `src/gzkit/mx/proxy_reality.py` (detector `scan()`, `ProxyRealityRecord`/`ProxyRealityScanResult`, live NC fixture/entrypoint, `_ensure_grader_gaming_registered()` with `@enforces("grader-gaming", ...)`); `tests/mx/test_proxy_reality.py` (11 tests).
- Files modified: `src/gzkit/enforcement.py` — wired `_ensure_grader_gaming_registered()` AND the orphaned `_ensure_gate5_claims_registered()` (OBPI-17) into the single production-discovery seam `_ensure_production_claims_registered()`. The brief originally deferred REQ-13-03 to OBPI-19, but OBPI-19 shipped Completed without wiring the floor sources — deferring to a closed OBPI is an orphan (caught by adversarial Stage 4b). REQ-13-03 now resolves `pass` (proven fence) because grader-gaming is live in the registry.
- Tests added: 5 scan-behavior (REQ-13-01), 3 live-NC passing-on-violation (REQ-13-02), 3 production-discovery wiring regression (locks the orphan fix; also asserts both bound gate5 members are live).
- Defects noted: GHI #648 — enforcement floor enrollment-completeness (BI#9) is not implemented; a missing floor member is silently absent rather than caught. Systemic enumeration cure slated for the AIRLOCK system.

## Tracked Defects

- **GHI #648** — `enforcement floor: gate5/grader-gaming claim sources orphaned from production discovery`. Root cause cured at the seam in this OBPI (wiring + regression tests); remaining BI#9 enrollment-completeness enumeration routed to the AIRLOCK system.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — grader-gaming's gate5_invariants floor membership is now a live, measured control: proxy_reality.scan() turns the ledger's repudiation record into a count (5 on the real ledger), the passing-on-violation live NC catches a planted violation through the real production path, and REQ-13-03 resolves as a proven structural fence because grader-gaming is wired into production discovery (run_enforcement_floor_audit: 41 claims verified). Adversarial Stage 4b caught the orphan (deferral to already-Completed OBPI-19); fixed at the single production-discovery seam and locked with regression tests. Receipts: arb-step-unittest-16894dfc4acb4cc18b8fb1cde33c5d24 (6560 tests OK), arb-ruff-f091d77627d04421a3641c5a576ed01c, arb-step-typecheck-987b339f62234e11bdf18fd46fa242c3, arb-step-mkdocs-42e28f1fb54c45889d58ddfdcd9f9e55. Defect GHI #648 filed for the unimplemented BI#9 enrollment enumeration (routed to AIRLOCK).
- Date: 2026-06-27

---

**Date Completed:** 2026-06-27

**Evidence Hash:** -
