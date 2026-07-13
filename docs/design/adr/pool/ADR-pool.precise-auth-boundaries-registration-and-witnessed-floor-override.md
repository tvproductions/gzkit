---
id: ADR-pool.precise-auth-boundaries-registration-and-witnessed-floor-override
status: Pool
lane: heavy
sensitivity: security
parent: PRD-GZKIT-1.0.0
---

# ADR-pool.precise-auth-boundaries-registration-and-witnessed-floor-override: Precise auth_boundaries registration and witnessed floor override

## Persona

Craftsperson with surgical-precision instincts: treats the security floor not as
overhead but as the discipline that keeps attestation honest. Knows that a floor
that over-fires trains reflexive overrides and goes inert — so precision is a
security property, not a convenience. Narrows the registration by MOVING the
auth-bearing code into its own registered home, never by weakening detection.
Refuses to de-register a surface until it has verified that no real human-presence
decision is left behind.

## Agent Context Frame — MANDATORY

This section establishes the mental model agents must carry through all OBPI execution.

**Role:** Refactoring architect + governance-surface precision. This is a surgical
re-registration of a security floor plus an additive ledger event and a fence
validator — NOT new behavior in the completion pipeline. The auth-decision LOGIC
does not change; only WHICH surfaces the floor watches, and whether the override is
witnessed.

**Purpose:** The `auth_boundaries` floor watches exactly the surfaces that genuinely
decide who-must-attest (`adr_audit.py` and the extracted `obpi_security_gate.py`),
no more; every `--accept-security-floor` override leaves a queryable
`security_floor_overridden` ledger record; and no attestation-authority symbol can
silently drift back into a de-registered file without a fail-close.

**Goals:**

- An additive, structural edit to `obpi_complete.py` (e.g. a reconciliation gate) no
  longer auto-classifies the editing brief `sensitivity:security` (the GHI #583
  deadlock is gone).
- Every `--accept-security-floor` override emits a `security_floor_overridden` ledger
  event queryable by `brief_id` / `parent_adr`.
- `gz validate --auth-surface-coherence` exits 3 if any attestation-authority symbol
  lives outside the registered `auth_boundaries` surfaces.

**Critical Constraint:** Implementations MUST keep detection PATH-BASED on a brief's
declared Allowed Paths (ADR-0.0.22). Precision is achieved by MOVING the auth-bearing
code into its own registered module, NEVER by introducing symbol-level or diff-level
detection. Implementations MUST NOT de-register `obpi_complete.py` until each
de-registered gate is verified to delegate its auth decision to `adr_audit.py` (or the
local-authority function is moved into `obpi_security_gate.py`).

**Anti-Pattern Warning:** A FAILED implementation narrows the registration but leaves
a real human-presence decision behind in the de-registered `obpi_complete.py` body —
the floor now passes edits that genuinely touch auth semantics (a silent security
regression that still passes every test). Equally failed: re-coarsening by piling
unrelated gates into `obpi_security_gate.py` until it is "the whole completion
pipeline" again, or letting `security_floor_overridden` become
witnessed-but-never-reviewed theater.

**Integration Points:** `src/gzkit/commands/obpi_complete.py` (source of the extracted
cluster; imports it back read-only); `src/gzkit/commands/adr_audit.py`
(`_requires_human_obpi_attestation`, `_enforce_human_attestation_authenticity`,
`_enforce_uncovered_acceptance_confirmation` — the genuine auth authority; stays
registered, untouched); `data/security_surfaces.json` (`auth_boundaries` re-pointed);
`src/gzkit/events.py`, `src/gzkit/ledger_events.py`,
`.gzkit/schemas/ledger_events.json`, `src/gzkit/schemas/ledger.json`,
`src/gzkit/governance/trust_audits/events.py` (the five-surface ledger-event pattern,
mirrored from `brief_reconcile_drift_overridden`); the new `--auth-surface-coherence`
validator scope under `src/gzkit/governance/trust_audits/`.

## Tidy First Plan

Behavior-preserving tidyings before any behavior change; tests stay green throughout.

- Prep tidyings (behavior-preserving):
  1. Extract the security-scan gate cluster (`_enforce_security_review_gate`,
     `_security_canonical_slot_filled`, `_load_security_checklist`,
     `_find_fresh_security_receipt`, `_render_security_walkthrough` plus their module
     constants) from `obpi_complete.py` into `obpi_security_gate.py`; `obpi_complete.py`
     imports them read-only. A pure move — no call-site semantics change.
  2. Before moving each function, verify it carries no LOCAL authoritative auth
     decision (it must delegate human-presence / who-must-attest decisions to
     `adr_audit.py`).

Separation of prep → change → polish: the extraction (prep, behavior-preserving) lands
first under OBPI-0.29.0-01; the registration re-point and the witnessed ledger event
(behavior change) land next; the drift-back validator and docs (polish/fence) land
last. STOP/BLOCKERS: if any de-registered gate is found to make a local authoritative
auth decision, that function MUST move into `obpi_security_gate.py` before the
registration is narrowed.

## Intent

**Current state (today).** The `auth_boundaries` security floor in the existing
`data/security_surfaces.json` globs three WHOLE command modules (`adr_audit.py`,
`obpi_complete.py`, `obpi_cmd.py`), so ANY edit to any of them auto-classifies the
editing brief `sensitivity:security` and forces `--accept-security-floor`. Before this
ADR, during OBPI-0.0.37-08, an additive reconciliation-gate edit to `obpi_complete.py`
tripped the floor though it touched no auth semantics (GHI #583). The floor currently
over-fires (false positives that train reflexive overrides and erode the anti-vibe
signal the floor exists to carry), AND the override is console-only at
`obpi_complete.py:201-205` (un-witnessed, leaving no auditable record).

**Target state (after this ADR).** The registration WILL be PRECISE — it should match
only the surfaces that genuinely decide who-must-attest — and every override WILL be
WITNESSED as a queryable ledger event rather than an ephemeral console line. The
durable outcome is a security floor that no longer cries wolf, an override that leaves a
permanent audit trail, and a mechanical fence that should fail closed if the narrowed
registration ever erodes. This is the lasting contract this ADR establishes.

## Decision

Decision items (each observable via CLI/config/artifact):

1. **Extract** the security-scan gate cluster into `src/gzkit/commands/obpi_security_gate.py`, imported read-only by `obpi_complete.py` (module-extraction, NOT symbol-detection).
2. **Re-point** `data/security_surfaces.json` `auth_boundaries`: KEEP `adr_audit.py`, ADD `obpi_security_gate.py`, DROP `obpi_complete.py` + `obpi_cmd.py`.
3. **Keep detection path-based** on a brief's declared Allowed Paths (ADR-0.0.22); the fail-close names the matched surface + category.
4. **Witness the override**: emit a `security_floor_overridden` ledger event on `--accept-security-floor`, replacing the console-only print, mirroring the `brief_reconcile_drift_overridden` five-surface pattern.
5. **Fence drift-back**: add `gz validate --auth-surface-coherence` asserting no attestation-authority symbol lives outside the registered surfaces.

Extract the security-scan gate cluster from src/gzkit/commands/obpi_complete.py into a new focused module src/gzkit/commands/obpi_security_gate.py (the functions _enforce_security_review_gate, _security_canonical_slot_filled, _load_security_checklist, _find_fresh_security_receipt, _render_security_walkthrough plus their module constants); obpi_complete.py imports them read-only. Then re-point the data/security_surfaces.json auth_boundaries globs: KEEP src/gzkit/commands/adr_audit.py (the genuine who-must-attest / authenticity authority), ADD src/gzkit/commands/obpi_security_gate.py, DROP src/gzkit/commands/obpi_complete.py and src/gzkit/commands/obpi_cmd.py. The authoritative human-presence / who-must-attest decisions already live in adr_audit.py (_requires_human_obpi_attestation, _enforce_human_attestation_authenticity, _enforce_uncovered_acceptance_confirmation), which stays registered; obpi_complete.py's other gates (receipt-binding, coverage-waiver) merely wrap those adr_audit calls, so de-registering loses no real protection. Detection is module-extraction, NOT symbol-detection: it stays path-based on a brief's declared Allowed Paths (ADR-0.0.22). Fold in dimension C: emit a security_floor_overridden ledger event (brief_id, parent_adr, override_ts, attestor, reason, detected_categories) when --accept-security-floor fires, replacing the console-only print (which moves into obpi_security_gate.py); mirror the brief_reconcile_drift_overridden event pattern across all surfaces. Add a drift-back validator (gz validate --auth-surface-coherence) asserting no attestation-authority symbols live outside the registered auth_boundaries surfaces, so de-registered files cannot silently re-accrete auth logic.

## Interfaces

- **CLI (external contract):** `uv run gz validate --auth-surface-coherence` — new
  validator scope (OBPI-0.29.0-03). Exit 0 clean; exit 3 on any attestation-authority
  symbol outside the registered surfaces.
- **Config / data surfaces:** `data/security_surfaces.json` `auth_boundaries.globs`
  re-pointed (read by `gz validate --sensitivity`).
- **Ledger event:** `security_floor_overridden` — new event type registered in the
  discriminated union and both schemas; emitted by the override path in
  `obpi_security_gate.py`.
- **Module surface:** `src/gzkit/commands/obpi_security_gate.py` (new; holds the
  extracted security-scan cluster), imported read-only by `obpi_complete.py`.

## Boundary Invariants

These are the structural fences this ADR establishes. They are audited at ADR closeout
(STRUCTURAL-FENCE proof channel), not by per-OBPI behavior tests.

1. **No attestation-authority symbol may live outside a registered `auth_boundaries`
   surface.** Attestation-authority symbols — the human-presence / who-must-attest /
   authenticity decisions (`_requires_human_obpi_attestation`,
   `_enforce_human_attestation_authenticity`, `_enforce_uncovered_acceptance_confirmation`,
   and the extracted security-scan gate cluster) — MUST reside only in the modules
   registered under `data/security_surfaces.json` `auth_boundaries` (`adr_audit.py`,
   `obpi_security_gate.py`). A symbol of this class appearing in any de-registered file
   (`obpi_complete.py`, `obpi_cmd.py`) is a fail-close drift-back signal, enforced by
   `gz validate --auth-surface-coherence` (OBPI-0.29.0-03).
2. **Detection stays path-based.** No surface introduced by this ADR may detect
   security sensitivity by SYMBOL or by DIFF; detection remains path-based on a brief's
   declared Allowed Paths (ADR-0.0.22). This fence is why module-extraction was chosen
   over symbol-detection.
3. **`obpi_security_gate.py` holds only auth-bearing security-scan gating.** The
   extracted module is not a dumping ground; gates without a who-must-attest /
   human-presence justification do not belong in it (re-coarsening guard).

## Rationale

The security floor exists to carry an anti-vibe signal: an edit that touches
who-must-attest semantics should trip heightened review. Globbing whole modules inverts
that purpose — `obpi_complete.py` is a large module whose body is mostly wrapper
plumbing around `adr_audit.py`'s authority decisions, so the floor fires on edits that
carry no auth meaning. Each false positive trains the operator to reflexively reach for
`--accept-security-floor`, eroding the very signal the floor protects (a floor that
cries wolf becomes inert).

The authoritative human-presence / who-must-attest decisions already live in
`adr_audit.py`, which stays registered. `obpi_complete.py`'s other gates
(receipt-binding, coverage-waiver) merely WRAP those `adr_audit` calls, so
de-registering them loses no real protection — provided OBPI-0.29.0-01 VERIFIES the
delegation (assumption-surfacing REQ): if any wrapper makes a LOCAL authoritative auth
decision, that function must move into `obpi_security_gate.py` too.

**Why module-extraction beats symbol-detection (rejected alternative).** The
natural-looking alternative is to detect the specific attestation-authority SYMBOLS and
trip the floor only when a brief touches them. This was REJECTED. gzkit's security-floor
detection is PATH-BASED on a brief's declared Allowed Paths (ADR-0.0.22) — that
constraint is real and load-bearing, not inherited convention. Symbol-level detection
would require briefs to declare allowed SYMBOLS rather than allowed paths,
re-architecting the brief contract itself — a disproportionate blast radius for a
precision problem. Module-extraction solves it directly: move the auth-bearing cluster
into its own file, and path-based detection becomes precise for free, with no change to
the brief contract. This aligns with the Smallest-Vibing-Surface frame: precise
registration + witnessed override + drift-back fence each close a leak without widening
any other surface.

**Precedent / exemplar.** The witnessed-override design follows an established exemplar:
the `security_floor_overridden` event mirrors the existing `brief_reconcile_drift_overridden`
escape-hatch-receipt pattern (the precedent landed under OBPI-0.0.37-08), reusing the same
five-surface registration shape (factory in `ledger_events.py`, Pydantic model +
discriminated-union member in `events.py`, schema entries in both ledger schemas, and a
`_NO_GRAPH_IMPACT` waiver). The drift-back validator follows the existing
`gz validate --<scope>` audit pattern under `src/gzkit/governance/trust_audits/`. No novel
mechanism is introduced where a precedent exists.

### Pre-Mortem (Gary Klein — "18 months out, this failed spectacularly. Why?")

1. **Narrow extraction under-protected.** An auth decision drifted into the
   de-registered `obpi_complete.py` body after the fact; the floor passed an edit that
   genuinely touched auth semantics. → Mitigated by OBPI-0.29.0-03's
   `gz validate --auth-surface-coherence` drift-back validator, wired into `gz check`.
   This is the single mechanical guard, so its symbol-coverage must be real, not
   cosmetic.
2. **`obpi_security_gate.py` became a dumping ground**, re-coarsening back into "the
   whole completion pipeline" and reintroducing the original false-positive problem. →
   Boundary Invariant 3 and the re-coarsening guard in the Anti-Pattern Warning.
3. **The override became theater** — `security_floor_overridden` events emitted
   faithfully but never reviewed. → Forces a subsequent decision: a review cadence for
   `security_floor_overridden` events.

### What Would Have to Be True (Roger Martin)

For module-extraction to be the right call, the auth-authority logic must STAY PUT in
the registered surfaces. Nothing mechanical prevents an agent from later writing an auth
decision into a de-registered file — this is the SHAKIEST condition, and it is exactly
what OBPI-0.29.0-03's drift-back validator exists to mechanize. For symbol-detection
(Alternative B) to have been better, briefs would have to declare allowed symbols —
which they do not and should not (ADR-0.0.22).

### Constraint Archaeology

Detection is path-based on Allowed Paths — REAL and load-bearing (ADR-0.0.22), exercised
every time `gz validate --sensitivity` runs. It is the reason module-extraction beats
symbol-detection; it is not inherited convention nobody re-examined.

### Assumption Surfacing

The de-registration rests on the assumption that `obpi_complete.py`'s receipt-binding /
coverage gates are mere wrappers delegating to `adr_audit.py`. If the opposite were true
— a wrapper makes a local authoritative auth decision — de-registering would silently
drop real protection. OBPI-0.29.0-01 MUST verify this and move any local-authority
function into `obpi_security_gate.py`.

### The 2am Operator Question

At 2am the operator needs the fail-close to name WHICH matched surface and WHICH
category fired (not just "slot unfilled"), and needs every override to be QUERYABLE after
the fact (`security_floor_overridden` by `brief_id` / `parent_adr`). Both are folded into
the briefs.

### Reversibility Assessment

Two-way door. Re-coarsening the registration is a one-line revert of
`data/security_surfaces.json`; the extracted module and the ledger event are additive and
harmless if the registration is widened again. Low reversal cost supports proceeding now.

### Scope Minimization

OBPI-0.29.0-01 alone fixes the false-positive deadlock (the MVP). OBPI-0.29.0-02
(witnessing) and OBPI-0.29.0-03 (drift-defense + docs) add the audit trail and the
mechanical guard. If time were halved, 01 ships first; 02 and 03 are the durability
layer.

### Subsequent decisions forced

- Promote `pool.agentic-security-review` (dimension A) — the floor is now precise but the
  toolchain is still INCAPABLE of an actual agentic security review (the canonical slot
  stays unfilled).
- Define a review cadence for `security_floor_overridden` events so witnessing does not
  become theater.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: this ADR's enforcement is not yet landed (no obpi_security_gate.py module, no security_floor_overridden event, no --auth-surface-coherence validator; auth_boundaries still globs the pre-ADR modules). The security-surfaces registry this ADR re-points validates against its schema as the closest green proxy. | uv run -m unittest tests.governance.test_security_surfaces_registry | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override --check | 0 |

## Consequences

> The design forcing functions that stress-test these consequences — Pre-Mortem,
> What-Would-Have-to-Be-True, Constraint Archaeology, Assumption Surfacing, the 2am
> Operator Question, Reversibility, and Scope Minimization — are recorded under
> `## Rationale` above (the Pre-Mortem subsection enumerates the three failure scenarios
> and their mitigations).

### Positive

1. The false-positive deadlock disappears: additive/structural edits to obpi_complete.py no longer force --accept-security-floor, so the security floor stops training reflexive overrides and recovers its anti-vibe signal.
2. The floor becomes PRECISE without becoming weaker: adr_audit.py (the genuine who-must-attest authority) and the extracted obpi_security_gate.py remain registered, so every real human-presence decision still trips the floor.
3. Overrides become witnessed and queryable: the security_floor_overridden ledger event replaces the ephemeral console print, giving a permanent audit trail (attestor, reason, detected_categories) for every floor override.
4. Drift-back is mechanically prevented: gz validate --auth-surface-coherence fails-close if attestation-authority symbols ever appear outside the registered surfaces, so the narrowed registration cannot silently erode.
5. Module-extraction keeps detection path-based on Allowed Paths (ADR-0.0.22) — no re-architecting of the brief contract.

### Negative

1. Narrow extraction under-protects IF an auth decision later drifts into the de-registered obpi_complete.py body — mitigated by the OBPI-03 drift-back validator, but the validator is the only mechanical guard, so its coverage must be real.
2. obpi_security_gate.py could become a dumping ground that re-coarsens the surface if future gates are added to it without auth justification — a maintenance discipline risk.
3. The security_floor_overridden event could become the new reflexive ritual: witnessed-but-never-reviewed theater. A review cadence for these events is a forced subsequent decision.
4. The de-registration rests on the assumption that obpi_complete.py's receipt-binding/coverage gates are mere wrappers delegating to adr_audit.py — OBPI-01 must VERIFY this; if any gate makes a LOCAL authoritative auth decision, that function must move into obpi_security_gate.py too.
5. The floor is now precise but the toolchain is still INCAPABLE of an actual agentic security review (the canonical slot stays unfilled until pool.agentic-security-review promotes — dimension A, out of scope here but forced next).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 5
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.29.0-01: Extract obpi_security_gate.py from obpi_complete.py and re-point data/security_surfaces.json auth_boundaries (KEEP adr_audit.py, ADD obpi_security_gate.py, DROP obpi_complete.py + obpi_cmd.py); fail-close message names the matched surface + category; verify each de-registered gate genuinely delegates its auth decision to adr_audit.py.
- [ ] OBPI-0.29.0-02: Add the security_floor_overridden ledger event across all surfaces (schemas, Pydantic model, factory, no-graph-impact waiver), emit it on --accept-security-floor override (replacing the console-only print), and make it queryable.
- [ ] OBPI-0.29.0-03: Add gz validate --auth-surface-coherence drift-back validator asserting no attestation-authority symbols live outside the registered auth_boundaries surfaces; plus manpage + runbook docs for the precise registration and override event, and an advisory-rules-audit.md scorecard row.

## OBPI Briefs

The Checklist above is decomposed 1:1 into OBPI briefs under `obpis/`. Every Feature
Checklist item maps to exactly one brief (1:1 Synchronization Mandate). All three are
Heavy lane and carry `sensitivity: security` (each overlaps a registered
`auth_boundaries` surface).

| # | OBPI | Specification Summary | Lane | Sensitivity | Status |
|---|------|----------------------|------|-------------|--------|
| 1 | OBPI-0.29.0-01 | Extract `obpi_security_gate.py`; re-point `auth_boundaries` (keep `adr_audit.py`, add `obpi_security_gate.py`, drop `obpi_complete.py` + `obpi_cmd.py`); fail-close names surface+category; verify delegation. | Heavy | security | Pending |
| 2 | OBPI-0.29.0-02 | `security_floor_overridden` ledger event across all five surfaces; emit on override (replaces console-only print); make queryable. | Heavy | security | Pending |
| 3 | OBPI-0.29.0-03 | `gz validate --auth-surface-coherence` drift-back validator; manpage + runbook docs; advisory-rules-audit scorecard row. | Heavy | security | Pending |

**Briefs location:** `obpis/OBPI-0.29.0-*.md`. Every row above has exactly one brief file.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-06-06T05:31:07.037631*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.29.0-precise-auth-boundaries-registration-and-witnessed-floor-override

### Q: What is the title of this ADR?

**A:** Precise auth_boundaries registration and witnessed floor override

### Q: What is the semantic version?

**A:** 0.29.0

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** The auth_boundaries security floor in data/security_surfaces.json globs three WHOLE command modules (adr_audit.py, obpi_complete.py, obpi_cmd.py), so ANY edit to any of them auto-classifies the editing brief sensitivity:security and forces --accept-security-floor. During OBPI-0.0.37-08 an additive reconciliation-gate edit to obpi_complete.py tripped the floor though it touched no auth semantics (GHI #583). The floor over-fires (false positives that train reflexive overrides and erode the anti-vibe signal the floor exists to carry) AND the override is console-only at obpi_complete.py:201-205 (un-witnessed, leaving no auditable record). We need the registration to be PRECISE (matching only the surfaces that genuinely decide who-must-attest) and the override to be WITNESSED (a queryable ledger event, not an ephemeral console line).

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Extract the security-scan gate cluster from src/gzkit/commands/obpi_complete.py into a new focused module src/gzkit/commands/obpi_security_gate.py (the functions _enforce_security_review_gate, _security_canonical_slot_filled, _load_security_checklist, _find_fresh_security_receipt, _render_security_walkthrough plus their module constants); obpi_complete.py imports them read-only. Then re-point the data/security_surfaces.json auth_boundaries globs: KEEP src/gzkit/commands/adr_audit.py (the genuine who-must-attest / authenticity authority), ADD src/gzkit/commands/obpi_security_gate.py, DROP src/gzkit/commands/obpi_complete.py and src/gzkit/commands/obpi_cmd.py. The authoritative human-presence / who-must-attest decisions already live in adr_audit.py (_requires_human_obpi_attestation, _enforce_human_attestation_authenticity, _enforce_uncovered_acceptance_confirmation), which stays registered; obpi_complete.py's other gates (receipt-binding, coverage-waiver) merely wrap those adr_audit calls, so de-registering loses no real protection. Detection is module-extraction, NOT symbol-detection: it stays path-based on a brief's declared Allowed Paths (ADR-0.0.22). Fold in dimension C: emit a security_floor_overridden ledger event (brief_id, parent_adr, override_ts, attestor, reason, detected_categories) when --accept-security-floor fires, replacing the console-only print (which moves into obpi_security_gate.py); mirror the brief_reconcile_drift_overridden event pattern across all surfaces. Add a drift-back validator (gz validate --auth-surface-coherence) asserting no attestation-authority symbols live outside the registered auth_boundaries surfaces, so de-registered files cannot silently re-accrete auth logic.

### Q: What good things result from this decision? List benefits.

**A:** 1. The false-positive deadlock disappears: additive/structural edits to obpi_complete.py no longer force --accept-security-floor, so the security floor stops training reflexive overrides and recovers its anti-vibe signal.
2. The floor becomes PRECISE without becoming weaker: adr_audit.py (the genuine who-must-attest authority) and the extracted obpi_security_gate.py remain registered, so every real human-presence decision still trips the floor.
3. Overrides become witnessed and queryable: the security_floor_overridden ledger event replaces the ephemeral console print, giving a permanent audit trail (attestor, reason, detected_categories) for every floor override.
4. Drift-back is mechanically prevented: gz validate --auth-surface-coherence fails-close if attestation-authority symbols ever appear outside the registered surfaces, so the narrowed registration cannot silently erode.
5. Module-extraction keeps detection path-based on Allowed Paths (ADR-0.0.22) — no re-architecting of the brief contract.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. Narrow extraction under-protects IF an auth decision later drifts into the de-registered obpi_complete.py body — mitigated by the OBPI-03 drift-back validator, but the validator is the only mechanical guard, so its coverage must be real.
2. obpi_security_gate.py could become a dumping ground that re-coarsens the surface if future gates are added to it without auth justification — a maintenance discipline risk.
3. The security_floor_overridden event could become the new reflexive ritual: witnessed-but-never-reviewed theater. A review cadence for these events is a forced subsequent decision.
4. The de-registration rests on the assumption that obpi_complete.py's receipt-binding/coverage gates are mere wrappers delegating to adr_audit.py — OBPI-01 must VERIFY this; if any gate makes a LOCAL authoritative auth decision, that function must move into obpi_security_gate.py too.
5. The floor is now precise but the toolchain is still INCAPABLE of an actual agentic security review (the canonical slot stays unfilled until pool.agentic-security-review promotes — dimension A, out of scope here but forced next).

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. OBPI-0.29.0-01: Extract obpi_security_gate.py from obpi_complete.py and re-point data/security_surfaces.json auth_boundaries (KEEP adr_audit.py, ADD obpi_security_gate.py, DROP obpi_complete.py + obpi_cmd.py); fail-close message names the matched surface + category; verify each de-registered gate genuinely delegates its auth decision to adr_audit.py.
2. OBPI-0.29.0-02: Add the security_floor_overridden ledger event across all surfaces (schemas, Pydantic model, factory, no-graph-impact waiver), emit it on --accept-security-floor override (replacing the console-only print), and make it queryable.
3. OBPI-0.29.0-03: Add gz validate --auth-surface-coherence drift-back validator asserting no attestation-authority symbols live outside the registered auth_boundaries surfaces; plus manpage + runbook docs for the precise registration and override event, and an advisory-rules-audit.md scorecard row.

### Q: What alternatives were considered and why were they rejected?

**A:** Symbol-detection / AST-level auth-surface detection (REJECTED): instead of registering whole modules or extracted modules, detect the specific attestation-authority SYMBOLS (functions like _requires_human_obpi_attestation) and only trip the floor when a brief touches those symbols. Rejected because gzkit's security-floor detection is PATH-BASED on a brief's declared Allowed Paths (ADR-0.0.22) — symbol-level detection would require briefs to declare allowed SYMBOLS rather than allowed paths, re-architecting the brief contract itself. That is a disproportionate blast radius for a precision problem that module-extraction solves directly: extract the auth-bearing cluster into its own file, and path-based detection becomes precise for free. Status-quo (do nothing) also rejected: the over-classification deadlock is live (GHI #583) and the un-witnessed override is an audit gap.


## Evidence

Four-Gate evidence (filled at OBPI closeout):

- **Gate 1 (ADR):** this document.
- **Gate 2 (TDD):** `tests/commands/test_obpi_security_gate.py` (extraction + fail-close
  message names surface+category); ledger-event round-trip tests for
  `security_floor_overridden` under `tests/`; `tests/governance/` coverage for
  `gz validate --auth-surface-coherence`.
- **Gate 3 (Docs):** `docs/user/manpages/validate.md` (new `--auth-surface-coherence`
  scope), `docs/user/runbook.md` + `docs/governance/governance_runbook.md` (precise
  registration + override event), `docs/governance/advisory-rules-audit.md` (scorecard
  row).
- **Gate 4 (BDD):** no new `.feature` file — the external surfaces (one new validator
  scope; one new ledger event type) are covered by direct CLI/validator unit tests at
  Gate 2. Documented in OBPI-0.29.0-03.
- **Gate 5 (Human):** brief-level human attestation is universal (ADR-0.0.36); all three
  briefs carry `sensitivity: security` and fire the extended Gate-5 walkthrough.

## Alternatives Considered

Symbol-detection / AST-level auth-surface detection (REJECTED): instead of registering whole modules or extracted modules, detect the specific attestation-authority SYMBOLS (functions like _requires_human_obpi_attestation) and only trip the floor when a brief touches those symbols. Rejected because gzkit's security-floor detection is PATH-BASED on a brief's declared Allowed Paths (ADR-0.0.22) — symbol-level detection would require briefs to declare allowed SYMBOLS rather than allowed paths, re-architecting the brief contract itself. That is a disproportionate blast radius for a precision problem that module-extraction solves directly: extract the auth-bearing cluster into its own file, and path-based detection becomes precise for free. Status-quo (do nothing) also rejected: the over-classification deadlock is live (GHI #583) and the un-witnessed override is an audit gap.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.29.0 | Pending | | | |
