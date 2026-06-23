---
mode: CREATE
adr_id: ADR-0.0.74
branch: main
timestamp: "2026-06-23T08:42:56Z"
agent: claude-code
obpi_id:
session_id:
continues_from:
last_commit_sha: 62f6f980
---

<!-- SIZING handoff (not implementation) for the enforcement-claim meta-validator —
     Build-to-1.0 campaign Movement I item 3 (line 222). Anchored to ADR-0.0.74
     because §5 / gate5_invariants / the specific live-NC instance live there, but
     the general meta-validator is OUT of ADR-0.0.74 scope and needs its OWN ADR. -->

## This handoff ADVISES next moves — it is NOT authorization to execute them

A sizing analysis to seed a design session. Present it; obtain operator
authorization before opening an ADR or writing code. You advise; the operator rules.

## Current State Summary

This is a **sizing handoff** for the **enforcement-claim meta-validator** (campaign
`docs/governance/build-to-1.0-campaign-2026-06-20.md` § Movement I item 3, line 222:
"the floor's teeth"). No code was written; this scopes the work.

**What it is (§5 doctrine, campaign lines 177-194):** Any place gzkit asserts
something is **enforced / validated / fail-closed / gated / blocked** — in code, an
ADR, a doc, or an agent's claim — MUST have a paired **live negative control** that
(a) constructs a known violation of that exact claim, (b) runs the real path in its
**production** configuration, and (c) asserts it fails. No live NC ⇒ the claim is
facade ⇒ rejected. Mechanized via an `@enforces(claim=…, neg_control=…)` declaration
and a meta-validator that **runs** every NC against a known violation and fail-closes
if any enforcement claim lacks a passing-on-violation NC, emitting a ledger receipt
so "this is enforced" is a replayable fact, not a sentence. §5: "one primitive, used
in three places: the floor, the MX exit gate, and the antibody repair."

**Why now (root-fix leverage):** this is the structural cure for the exact failure
class demonstrated live this session — mechanisms built and self-certified but
adopted/consumed by nothing: the leveled MX substrate (`checkpoint.resolve` /
`disposition.route` / `levels.*` = 0 production call-sites despite OBPI-0.0.74-11/12
ATTESTED COMPLETED), the rendition gates (formerly staged inert), and
`composition_rendered` (emitted, never consumed). §5 explicitly names the forbidden
shapes this session removed: "forced-mode counterfactuals" and "green tests that
certify enforcement does nothing (`TestStagedWarn`)" — `TestStagedWarn` was deleted
this session.

**Key finding for the sizing:** a **partial implementation already exists** — the
QC-binding system (ADR-0.0.73) is §5's primitive, but scoped to `gz check` STEPS only.
The meta-validator is its **generalization**, not a greenfield build.

## Important Context

**The existing primitive to build on — `gz validate --qc-binding` (ADR-0.0.73):**
- `src/gzkit/qc_binding.py` — `_STEP_CLASSIFICATION` (every step is `bound`/`advisory`/
  `unenforced`); `build_qc_registry()` raises `KeyError` on an unclassified step
  (forces declaration). Registry is DERIVED from `_build_check_steps()`.
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — `_PRODUCTION_NEGATIVE_CONTROLS`,
  **33 live NCs** today. Each constructs a known violation, runs the real path,
  returns 1 (genuine) / 0 (theater). (I added the `invariant-coherence` NC this session.)
- `src/gzkit/governance/trust_audits/qc_binding.py` — the meta-validator: runs each
  bound step's NC, fail-closes on theater (a step that passes its own NC), plus six
  static theater-signatures calibrated on the ADR-0.0.37 facade; `_NEGATIVE_CONTROL_DEBT`
  is the (currently empty) acknowledged-debt escape.
- This IS the enforcement-claim rule — for one surface. The general version lifts the
  NC-execution engine and applies it to every enforcement claim.

**The specific live-NC instance already scoped — OBPI-0.0.74-13 (Draft):**
`src/gzkit/mx/proxy_reality.py` (the proxy-reality distance detector) "ships WITH its
live negative control … runs the real detection path in production configuration, and
asserts it is caught." It is the concrete template the general mechanism abstracts —
grader-gaming's floor membership made "a bound, measured control" rather than a named
aspiration. Recommend landing OBPI-13 first as the proven exemplar, then generalize.

**The gap the meta-validator closes — the facade proof channels that exist today:**
- **Structural-fence REQs** are "proven" by `resolve_fence_proof` in
  `src/gzkit/governance/trust_audits/closeout_proof.py` = **a parent-ADR "## Boundary
  Invariants" anchor is present** (a sentence). No live check. This is the facade
  channel that let OBPI-0.0.74-11/12's adoption fences pass with zero call-sites.
- **`gate5_invariants`** (`src/gzkit/mx/invariants.py`) has 5 members
  `{gate5-attestation, secrets, operator-PII, ledger-integrity, grader-gaming}`; only
  grader-gaming has a live-NC OBPI (13, Draft). The other four are §5 facade claims today.
- **`@enforces` does not exist** anywhere in `src/gzkit/`.

## Decisions Made

Sizing recommendations (operator to ratify in the design session):

- **Decision:** The meta-validator GENERALIZES the qc_binding NC-execution engine; it
  does NOT stand up a second parallel NC system.
  **Rationale:** two NC frameworks would themselves drift; qc_binding already runs 33
  live NCs and fail-closes correctly. Extract the run-NC-in-production-and-assert-failure
  engine; have both `gz check` steps and the new claim surfaces consume it.
- **Decision:** It needs its OWN ADR (new foundation capability).
  **Rationale:** the campaign places it as Movement I item 3, explicitly OUT of
  ADR-0.0.74's declared scope ("its own work"; ADR-0.0.74 ships only grader-gaming's
  *specific* live NC, item 13).
- **Decision:** Bound the v1 surface to enumerable claim sites — `gate5_invariants`
  members + structural-fence REQs that assert enforcement + (already-covered) `gz check`
  steps. Defer free-prose ADR/doc scanning to a later increment.
  **Rationale:** "every place gzkit asserts enforced" is unbounded; a prose grader is
  weaker than a real enforcement consumer (ADR-0.0.70 precedent). Start where the claim
  sites are structured and enumerable.

## Immediate Next Steps

*(ADVISORY — for the design session; await operator authorization.)*

1. Run `gz-design` to open a new foundation ADR — "enforcement-claim meta-validator" —
   with the §5 rule (campaign lines 181-194) as its thesis and the qc_binding system as
   the named prior art it generalizes.
2. Propose this OBPI decomposition for that ADR:
   - **A. `@enforces(claim=, neg_control=)` declaration + registry** — import-time
     registration mirroring qc_binding's `_STEP_CLASSIFICATION`; typo/unknown-claim
     fail-closed at decoration time (mirror `@covers`/`@advances` precedent).
   - **B. The meta-validator runner** — discover every `@enforces`, run each NC in
     production config, fail-close if any lacks a passing-on-violation NC; emit an
     additive `enforcement_claim_verified` ledger receipt. (Lift the engine out of
     `audit_qc_binding`.)
   - **C. `gate5_invariants` floor migration** — declare `@enforces` + live NCs for the
     four members lacking one (grader-gaming arrives via OBPI-0.0.74-13).
   - **D. Structural-fence proof upgrade** — a structural-fence REQ that *claims
     enforcement* requires a live NC, not just a Boundary-Invariants anchor; amend
     `closeout_proof.resolve_fence_proof` accordingly.
   - **E. Floor wiring** — join the meta-validator to the `gz check` / pre-push floor
     (campaign: "joins that floor as it lands"). Apply the read-only-gate lesson from
     this session: the validator must not mutate the ledger on a clean run.
   - **F. (stretch) prose/doc claim scanning** — "enforced/validated/fail-closed" in
     ADRs/docs must cite a live NC. Deferred per the v1 scope decision.
3. Decide land-order: OBPI-0.0.74-13 (concrete exemplar) → A → B → C/D → E.

## Pending Work / Open Loops

- **Retroactive blast radius (sequencing risk):** when E lands, the meta-validator WILL
  flag the four unguarded `gate5_invariants` members and any enforcement-claiming
  structural-fence with no live NC (OBPI-0.0.74-11/12's adoption fences). The floor must
  not go red before C/D close those — stage warn→fail (OBPI-0.0.41 precedent) or land
  the migrations first.
- **"Production configuration" subtlety:** §5 forbids forced-mode counterfactuals; each
  NC must exercise the REAL path, not a forced flag. Non-trivial for some claims.
- **Performance:** N live NCs per `gz check` / pre-push (qc_binding already runs 33,
  each spawning tmp dirs/subprocesses). May need memoization or a separate cadence.
- **qc_binding relationship:** absorb-vs-sibling — recommend extract-shared-engine;
  confirm in design.
- **The gates-as-sensors adoption gap (separate but related, campaign line 220):** the
  leveled MX substrate has 0 production call-sites; the meta-validator would expose it.
  Tracked in `.gzkit/insights/agent-insights.jsonl` (2026-06-23 entries).

## Verification Checklist

Confirm the sizing's load-bearing claims before designing:

- [ ] `grep -rn "checkpoint.resolve" src/gzkit --include=*.py | grep -v /mx/ | grep -v def` → 0 (gap is real)
- [ ] `uv run gz validate --qc-binding` passes; `grep -c "_negative_control," src/gzkit/governance/trust_audits/_qc_negative_controls.py` → 33 (primitive exists)
- [ ] `sed -n '225,233p' src/gzkit/governance/trust_audits/closeout_proof.py` shows the structural-fence proof is "add a Boundary Invariants anchor" (facade channel)
- [ ] `grep -rn "@enforces" src/gzkit --include=*.py` → empty (not built)
- [ ] `grep -n GATE5_INVARIANTS src/gzkit/mx/invariants.py` shows 5 members; only grader-gaming has a live-NC OBPI (13)

## Evidence / Artifacts

- `docs/governance/build-to-1.0-campaign-2026-06-20.md` — §5 enforcement-claim rule (lines 177-194); Movement I item 3 (line 222); the anti-hallucination "known-answer evals" framing (line 207)
- `src/gzkit/qc_binding.py` — the existing classification + registry primitive
- `src/gzkit/governance/trust_audits/qc_binding.py` — the existing per-step meta-validator (the engine to generalize)
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — 33 live NCs (the pattern)
- `src/gzkit/governance/trust_audits/closeout_proof.py` — the structural-fence sentence-proof channel to upgrade
- `src/gzkit/mx/invariants.py` — `gate5_invariants` floor members needing live NCs
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-13-mx-proxy-reality-detector.md` — the concrete live-NC exemplar (Draft)
- `.gzkit/insights/agent-insights.jsonl` — this session's entries (gates-as-sensors adoption gap; invariant-coherence read-only fix)

## Environment State

Python 3.13, uv-managed. Sizing only — no dependency or code changes.
