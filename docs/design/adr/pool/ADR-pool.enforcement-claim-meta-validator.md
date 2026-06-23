---
id: ADR-pool.enforcement-claim-meta-validator
status: Pool
lane: heavy
parent: PRD-GZKIT-1.0.0
---

# ADR-0.0.75-enforcement-claim-meta-validator: Enforcement-Claim Meta-Validator

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware,
whole-file-reasoning, direct. The agent working this ADR treats an enforcement
claim with no live negative control as a defect, never a convenience; "it is
enforced" is a sentence until a known violation has been run through the real
path and observed to fail. No vibe coding: every claim ships with its coupled,
re-runnable proof.

## Why foundation tier?

Without a structural way to prove its own enforcement claims are real, gzkit's
entire governance surface is only as trustworthy as the last unaudited sentence.
By the invariance test — *"without it we wouldn't be doing the project"* —
the meta-validator is the maintenance/inspection port through which the question
*"is this claim actually enforced?"* is answered for every guard. In
ports/adapters terms that points to invariance, not a feature adapter: it shapes
what gzkit IS (a harness whose enforcement claims are facts, not prose), so it is
foundation, not feature.

## Intent

This ADR is the Build-to-1.0 campaign's Movement I item 3 — the
enforcement-claim meta-validator, *"the floor's teeth"*
([`docs/governance/build-to-1.0-campaign-2026-06-20.md`](../../../../governance/build-to-1.0-campaign-2026-06-20.md)
line 222).

Thesis (campaign §5 enforcement-claim rule): **anywhere gzkit asserts that
something is enforced / validated / fail-closed / gated, there MUST be a paired
LIVE negative-control (NC)** that (a) constructs a known violation, (b) runs the
real enforcement path in PRODUCTION configuration, and (c) asserts that it
fails. No live NC means the claim is a facade and is rejected.

This is the structural cure for the **facade failure class** — a mechanism
attested COMPLETED but adopted by nothing. The class was demonstrated live this
session: GHI #637 found that OBPI-0.0.74-12's leveled checkpoint
(`checkpoint.resolve`) was attested COMPLETED with **zero production callers**.
A "gates-as-sensors is done" claim was true at the unit-test layer and false at
the system layer. The meta-validator would have caught it, because a checkpoint
adopted by nothing cannot be made to fail on a violation it does not actually
guard. GHI #623 is the still-open sibling of the same class. The 1.0 definition
(campaign §8) depends on this rule being green.

**Critical constraint (binding):** this **GENERALIZES** the qc_binding system
(ADR-0.0.73), which already runs the run-NC-in-production-and-assert-failure
engine but scoped to `gz check` STEPS only. It does **NOT** stand up a second,
parallel NC system. Two NC frameworks would themselves drift apart — the exact
failure §5 exists to kill.

## Decision

One primitive, one runner, three claim sources, strict no-debt.

1. **One primitive.** `@enforces(claim, fixture=<violation-builder>,
   entrypoint=<production-callable>)`, registered at import time with
   typo / unknown-claim **fail-closed at decoration** (mirrors the `@covers` /
   `@advances` precedent in `src/gzkit/traceability.py` and
   `src/gzkit/tasks.py`). The RUNNER invokes `entrypoint(fixture())` in
   production configuration and asserts that it fails; **the NC NEVER calls the
   validator itself**, so forced-mode counterfactuals (`fail_closed=True` and
   the like) are **impossible by construction, not merely detected**. Genuineness
   of an NC is absolute, not heuristic.

2. **Three claim sources, one claim-type-agnostic registry** (v1 enumerable
   scope):
   - (a) **`gz check` steps / validators** — `@enforces` on the validator
     function; this lifts the 33 existing qc_binding NCs, **re-authored
     un-forced**.
   - (b) **`gate5_invariants` members** — the five in `src/gzkit/mx/invariants.py`,
     one `@enforces` entry per member.
   - (c) **structural-fence REQs that assert enforcement** — `@enforces` on the
     parent-ADR Boundary Invariant, with
     `resolve_fence_proof` (in `src/gzkit/req_kind.py`, consumed by `closeout_proof.py`) requiring a live NC, not just a
     `## Boundary Invariants` anchor.

3. **Strict, no debt.** The meta-validator fail-closes if ANY enrolled claim
   lacks a passing un-forced NC. It does **NOT** inherit qc_binding's
   `_NEGATIVE_CONTROL_DEBT` escape
   (`src/gzkit/governance/trust_audits/qc_binding.py`). Consequently the
   floor-wiring lands **LAST**, only when coverage is complete — the teeth land
   last, accepted deliberately.

4. **Data flow.** Discover all `@enforces` claims (three sources) -> the runner
   builds each violation fixture, runs the real entrypoint, asserts failure ->
   strict fail-close if any claim lacks a passing un-forced NC -> emit an
   `enforcement_claim_verified` ledger receipt per claim. **READ-ONLY on a clean
   run** (no ledger mutation when green). On failure the runner emits per-claim
   guardrail-feedback three-part prose
   ([`.claude/rules/guardrail-feedback-prose.md`](../../../../../.claude/rules/guardrail-feedback-prose.md))
   distinguishing **FACADE** (entrypoint did not fail on the violation) from
   **TEST-BUG** (fixture did not build), naming the **single-NC repro command** —
   not a bare failing count.

**Land order (1:1 with the Checklist, strict-no-debt sequenced):** A -> B ->
C+D -> E. A and B (primitive + runner) stand up first and are runnable manually
to report coverage; C and D enroll the gate5 floor and the fence-proof channel;
E joins the meta-validator to the floor (`gz check` / pre-push) only when
coverage is complete.

**Scope boundary — NOT in this ADR.** Free-prose ADR / doc claim scanning
("enforced / validated / fail-closed" appearing in ADRs and docs must cite a
live NC) is **extension point F**, DEFERRED to a later foundation ADR — it is
unbounded and a prose grader is structurally weaker than a real enforcement
consumer (ADR-0.0.70 precedent). `grader-gaming`'s own live NC (the
proxy-reality detector) is ADR-0.0.74 OBPI-13's work, not this ADR's; this ADR
provides the general `@enforces` surface that channel (c) and OBPI-13 both
express through.

## Consequences

### Positive

1. Every enforcement claim becomes a **replayable fact** (a ledger receipt), not
   a sentence. "Enforced" stops being a word and becomes a re-runnable negative
   control.

2. The facade failure class (GHI #637 fixed this session, GHI #623 the still-open
   sibling) becomes **structurally catchable** rather than caught by luck — a
   claim adopted by nothing fails the meta-validator because its entrypoint
   cannot be made to fail on a violation it does not actually guard.

3. **One primitive, three places:** the floor (`gz check` steps), the MX exit
   gate (`gate5_invariants`), and the antibody / fence-proof repair all express
   enforcement through the same `@enforces` surface — no second NC framework to
   drift.

4. Forcing impossibility is **structural, not heuristic:** because the NC never
   calls the validator, there is no forbidden-kwarg list to enumerate and keep
   current; a forced counterfactual cannot be authored at all.

### Negative

1. **Sequencing / blast-radius.** Strict-no-debt means E (floor wiring) cannot
   land until C+D complete; the teeth do not exist during the migration window.
   Accepted: a partial floor that silently tolerates uncovered claims would
   itself be the facade this ADR exists to kill.

2. **"Production configuration" subtlety.** Each NC must exercise the real path,
   never a mock. Feasibility per `gate5_invariants` member: **secrets** (a
   synthetic planted secret), **operator-pii** (a SYNTHETIC PII-shaped match,
   **NEVER** the operator's real email), **ledger** (a temp ledger with a broken
   hash chain), **gate5-attestation** (the **ABSENCE** case only — a missing
   attestation on a heavy/foundation completion is rejected; **forgery-detection
   is explicitly OUT**, because canon holds the operator's verbatim relayed
   attestation IS Gate 5, so there is no forgery surface to NC). Residual risk: a
   mock creeps into a fixture and the forcing-impossible guarantee leaks at the
   fixture/entrypoint seam. (OBPI-C owns the four floor NCs; OBPI-B owns the
   no-mock discipline in the runner.) **Entrypoint reality (named honestly):**
   of the four members, only `ledger` (`validate_ledger`) and
   `gate5-attestation` (the `_requires_human_obpi_attestation` /
   `_has_human_attestation_content` gate) have a bound production entrypoint
   today; `secrets` has only a handoff-document-scoped `validate_no_secrets`
   regex and `operator-pii` only an insights-scoped `_EMAIL_RE` scrubber — no
   unified gate5 secrets/PII gate is wired. This is itself an instance of this
   ADR's thesis (a floor member named but not generally enforced). OBPI-C must
   either bind to the genuine production gate where one exists or, where it does
   not, surface that member as a named-not-enforced facade and route standing up
   the real gate as named prerequisite work — never bind a narrower proxy
   entrypoint and call the claim proved.

3. **Performance.** N NCs per `gz check` / pre-push (qc_binding already runs 33,
   each spawning tmp dirs / subprocesses) may need memoization or a separate
   cadence; a quietly-too-slow floor gets moved off pre-push and §5 decays. A
   cadence decision is forced downstream (see § Subsequent decisions forced).

### Extension point F (DEFERRED — not a v1 brief)

Free-prose ADR / doc claim scanning: "enforced / validated / fail-closed"
appearing in ADRs and docs must cite a live NC. Deferred to a later foundation
ADR because the scope is unbounded and a prose grader is weaker than a real
enforcement consumer. Recorded here so the boundary is explicit and the
follow-on ADR has a named home; **no OBPI brief is authored for F in this ADR.**

### Subsequent decisions forced

1. The free-prose ADR/doc claim-scanning **extension F** as a later foundation
   ADR.
2. Refactoring ADR-0.0.74's MX exit gate + the antibody repair onto `@enforces`.
3. A **performance / cadence** decision: memoize, or run the floor on a separate
   cadence than every pre-push.

## Boundary Invariants

Cross-OBPI integration-state properties scoped to this ADR, audited at ADR
closeout (the proof channel for every `[structural-fence]` REQ in this ADR's
OBPIs, per ADR-0.0.59).

1. **One enforcement-claim surface, not two.** Every enforcement claim — `gz
   check` step, `gate5_invariants` member, or structural-fence REQ — is
   registered through the single `@enforces` primitive and discovered by the
   single runner; no second negative-control framework exists anywhere in the
   codebase. The qc_binding engine is generalized in place, not forked. (OBPI-01,
   OBPI-02)
2. **Forcing is impossible by construction — pinned at two seams.** The runner
   invokes `entrypoint(fixture())`; an NC never calls the validator it proves.
   Two structural constraints close the seams a wrapper could otherwise re-open:
   (a) `entrypoint` MUST be a direct, resolvable reference to a registered
   production callable whose `__module__` / `__qualname__` resolves into
   `src/gzkit/**` — no `lambda` and no `functools.partial` pre-binding a forcing
   kwarg at the registration site; and (b) whether the entrypoint caught the
   violation is decided by the runner via ONE uniform signal (e.g. a non-empty
   `list[ValidationError]` / non-zero exit), never an author-supplied pass/fail
   predicate. Genuineness is structural, not detected by enumerating forbidden
   kwargs. (OBPI-01, OBPI-02)
3. **Strict no-debt.** The meta-validator fail-closes if any enrolled claim lacks
   a passing un-forced NC; no `_NEGATIVE_CONTROL_DEBT`-style escape exists for
   the enforcement-claim registry. The floor wires in (OBPI-05) only when
   coverage is complete. (OBPI-02, OBPI-05)
4. **Every floor member's enforcement is live, not named — enrollment
   completeness is enumerated.** The meta-validator's gate5 claim-source
   enumerates `GATE5_INVARIANTS` membership and requires each member to carry an
   `@enforces` entry with a passing un-forced NC; a member with no entry fails
   the floor (so a future sixth member added without an NC cannot ride as a
   facade). OBPI-03 authors the four members it owns (secrets, operator-pii,
   ledger, gate5-attestation-absence); `grader-gaming`'s `@enforces` entry and
   live NC are authored under **ADR-0.0.74 OBPI-13** (the proxy-reality
   detector) — a declared cross-ADR dependency of this floor's completeness.
   (OBPI-03, OBPI-05; cross-ADR: ADR-0.0.74 OBPI-13)
5. **A structural-fence enforcement claim requires a live NC.** A
   `[structural-fence]` REQ that asserts *enforcement* resolves at closeout only
   when `resolve_fence_proof` (in `src/gzkit/req_kind.py`, consumed by `closeout_proof.py`) finds a live `@enforces` NC, not
   merely a `## Boundary Invariants` anchor. (OBPI-04)

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Each row becomes green as its owning OBPI lands. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The `@enforces(claim, fixture, entrypoint)` primitive registers claims at import time and fail-closes at decoration on a typo / unknown claim (mirrors `@covers` / `@advances`). | uv run -m unittest tests.governance.test_enforces_registry | 0 |
| The meta-validator runner invokes `entrypoint(fixture())` in production config, asserts failure, fail-closes strict (no debt escape) if any enrolled claim lacks a passing un-forced NC, is READ-ONLY on a clean run, and emits per-claim FACADE-vs-TEST-BUG guardrail-feedback with a single-NC repro command. | uv run -m unittest tests.governance.test_enforcement_meta_validator | 0 |
| Each `gate5_invariants` member (secrets, operator-pii, ledger, gate5-attestation-absence) carries a live un-forced NC that runs the real path against a known violation and is caught. | uv run -m unittest tests.mx.test_gate5_invariants_live_nc | 0 |
| A `[structural-fence]` REQ that asserts enforcement resolves at closeout only when `resolve_fence_proof` (in `src/gzkit/req_kind.py`, consumed by `closeout_proof.py`) finds a live `@enforces` NC. | uv run -m unittest tests.governance.test_fence_proof_live_nc | 0 |
| The meta-validator is wired into `gz check` / pre-push and is READ-ONLY (no ledger mutation) on a clean run. | uv run -m unittest tests.governance.test_enforcement_floor_wiring | 0 |

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 1
- Observability: 2
- Lineage: 2
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

<!-- Five distinct surfaces: the primitive (A), the runner (B), the gate5 floor
     migration (C), the fence-proof upgrade (D), the floor wiring (E). Each is a
     single-narrative unit with its own surface boundary and testability
     ceiling; no further split is warranted. Extension F is deferred and is NOT
     a checklist item. -->

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.75-01 — the `@enforces(claim, fixture, entrypoint)` decorator and one claim-type-agnostic registry populated at import time, fail-closed at decoration on a typo or unknown claim (mirrors the `@covers` / `@advances` precedent), registration metadata-only; unit tests
- [ ] OBPI-0.0.75-02 — the meta-validator runner discovers every claim, runs `entrypoint(fixture())` in production configuration, asserts failure, fail-closes strict with per-claim guardrail-feedback, lifting the engine and re-authoring the 33 qc_binding negative controls un-forced; unit tests
- [ ] OBPI-0.0.75-03 — live un-forced negative controls for the four `gate5_invariants` members lacking one (secrets, operator-pii, ledger, gate5-attestation-absence), each running its real scanner against a synthetic violation (grader-gaming is OBPI-0.0.74-13); unit tests
- [ ] OBPI-0.0.75-04 — `resolve_fence_proof` (in `src/gzkit/req_kind.py`, consumed by `closeout_proof.py`) amended so a `[structural-fence]` REQ that asserts enforcement requires a live `@enforces` NC, not merely a `## Boundary Invariants` anchor, while state-property fences are unchanged; unit tests
- [ ] OBPI-0.0.75-05 — wire the meta-validator into `gz check` and pre-push, read-only on a clean run, landing LAST only after the floor coverage is complete per the strict-no-debt sequence; unit tests

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Design interview conducted live with the operator; answers recorded in
`adr-interview.json` alongside this ADR. Tier-2 forcing functions were
agent-drafted against session evidence and operator-audited per AGENTS.md
§ Operator Economy of Effort.*

### Q: What kind of ADR is this?

**A:** Foundation. By the invariance test, without a structural way to prove its
own enforcement claims are real, gzkit's governance surface is only as
trustworthy as its last unaudited sentence. This is the inspection port — *is
this claim enforced?* — which points to invariance, not a feature adapter.

### Q: What problem are we solving?

**A:** The facade failure class — a mechanism attested COMPLETED but adopted by
nothing. Demonstrated live this session by GHI #637 (OBPI-0.0.74-12's leveled
checkpoint was attested COMPLETED with zero production callers). Campaign §5's
enforcement-claim rule is the cure: any claim that something is enforced /
validated / fail-closed / gated must have a paired live negative control that
constructs a violation, runs the real path in production config, and asserts
failure. The 1.0 definition (campaign §8) depends on this being green.

### Q: What did we decide?

**A:** One primitive (`@enforces(claim, fixture, entrypoint)`, import-time
registry, fail-closed at decoration), one runner (invokes
`entrypoint(fixture())` in production config and asserts failure — the NC never
calls the validator, so forcing is impossible by construction), three claim
sources into one claim-type-agnostic registry (`gz check` steps lifting the 33
qc_binding NCs un-forced, the five gate5_invariants members, and
structural-fence REQs), strict no-debt (fail-close if any claim lacks a passing
un-forced NC; floor wiring lands last). Generalizes ADR-0.0.73's qc_binding
engine — does NOT fork a second NC system.

### Q: What alternatives were considered and why rejected?

**A:** (a) A second parallel NC system — rejected: two frameworks drift, the
exact §5 failure. (b) NC-as-callable + a static no-force guard — rejected:
forcing-detection would be heuristic (enumerate forbidden kwargs); runner-driven
makes forcing impossible. (c) A shrink-only debt ratchet mirroring ADR-0.0.73
BI#8 — rejected: chose strict-no-debt; the floor wires in only when coverage is
complete. (d) Free-prose ADR/doc claim scanning in v1 — rejected: unbounded; a
prose grader is weaker than a real enforcement consumer (ADR-0.0.70 precedent);
deferred to extension F.

### Tier-2 — Pre-Mortem

**A:** 18 months out, §5 decayed three ways: (a) runner NCs grew too expensive,
the floor was quietly moved off pre-push, uncovered claims crept back; (b)
"production configuration" was reinterpreted loosely — a mock crept into a
fixture and the forcing-impossible guarantee leaked at the fixture/entrypoint
seam; (c) strict-no-debt deadlocked on one genuinely hard claim and a quiet
per-claim exemption was added, reintroducing the debt escape under a new name.

### Tier-2 — What Would Have to Be True

**A:** Right iff every enforcement claim expresses as (fixture builds a known
violation, real production entrypoint runs against it, it fails). Shakiest
conditions: the operator-pii NC (synthetic PII-shaped match, never the real
address, while still exercising the real detector) and the gate5-attestation NC
(only the ABSENCE case is NC-able; forgery is not, because canon holds the
operator's relayed verbatim attestation IS Gate 5).

### Tier-2 — Constraint Archaeology

**A:** "No forced-mode counterfactual" is real and freshly re-tested:
ADR-0.0.73's antibody was defeated by a forced NC, and GHI #637 this session
showed a checkpoint attested COMPLETED with zero production callers. The
constraint is load-bearing, not inherited convention.

### Tier-2 — Assumption Surfacing

**A:** Core assumption: the qc_binding engine generalizes from `gz check` STEPS
to non-step claims (gate5 members, fence-proof REQs) with one
claim-type-agnostic registry. If false — if non-step claims need fundamentally
different invocation — the design needs per-type runners, re-opening the
"two frameworks drift" risk that alternative (a) was rejected to avoid.

### Tier-2 — The 2am Operator

**A:** At 2am the floor is red. The operator needs WHICH claim failed, WHY
(facade — entrypoint did not fail on the violation — vs test-bug — fixture did
not build), and the single-NC repro command to re-run that one claim in
isolation. This drove OBPI-B's per-claim guardrail-feedback three-part prose
requirement — a bare failing count is not enough.

### Tier-2 — Reversibility

**A:** Two-way door at the mechanism (the `@enforces` primitive and runner are
removable code). One-way door at the doctrine: once 1.0 is defined as "every
enforcement claim has a live NC", un-adopting redefines what 1.0 means.

### Tier-2 — Scope Minimization

**A:** Smallest valuable version: A (`@enforces` + registry) + B (runner) + the
rendition NC, runnable MANUALLY to report coverage without yet being wired into
the floor. That is exactly the booked land-order — A, B, then C+D, then E (the
floor join) last.

### Closing — What subsequent decisions does this force?

**A:** (1) The free-prose ADR/doc claim-scanning extension F as a later
foundation ADR; (2) refactoring ADR-0.0.74's MX exit gate + antibody repair onto
`@enforces`; (3) a performance / cadence decision (memoize, or run the floor on a
separate cadence than every pre-push).

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. (a) **A second, parallel NC system** purpose-built for non-step claims.
   REJECTED: two NC frameworks would themselves drift apart — the exact failure
   §5 exists to kill. Generalize qc_binding's existing engine instead of forking
   it.

2. (b) **NC-as-callable plus a static no-force guard** that scans for forbidden
   kwargs. REJECTED: forcing-detection would be heuristic — it must enumerate
   every forbidden kwarg (`fail_closed=True`, `force=...`, etc.) and stay current
   as the surface grows. Runner-driven invocation (`entrypoint(fixture())`, NC
   never calls the validator) makes forcing IMPOSSIBLE, not merely detected.

3. (c) **A shrink-only debt ratchet** mirroring ADR-0.0.73 Boundary Invariant #8
   (`_NEGATIVE_CONTROL_DEBT`). REJECTED: chose strict-no-debt. A debt escape would
   let an uncovered enforcement claim ride indefinitely behind a "we'll cover it
   later" allowlist — the floor wires in only when coverage is complete,
   accepting that the teeth land last.

4. (d) **Free-prose ADR / doc claim scanning in v1.** REJECTED: unbounded scope;
   a prose grader is structurally weaker than a real enforcement consumer
   (ADR-0.0.70 precedent — a consumer beats a grader). Deferred to extension
   point F as a later foundation ADR.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.75 | Pending | | | |
