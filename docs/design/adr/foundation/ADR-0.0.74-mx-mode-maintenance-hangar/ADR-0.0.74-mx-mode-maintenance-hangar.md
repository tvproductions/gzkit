---
id: ADR-0.0.74-mx-mode-maintenance-hangar
status: Completed
kind: foundation
semver: 0.0.74
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-06-20
---

# ADR-0.0.74-mx-mode-maintenance-hangar: MX Mode — Maintenance Hangar

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Why foundation tier?

Without a way to maintain its own governance, gzkit cannot stay airworthy and the project stalls. This is the maintenance port—how the system is repaired when it is itself the patient—which points to invariance, not a feature adapter.

## Intent

gzkit governs agent work with aggressive, fail-closed locks. But governance itself is built iteratively — first fits are approximate, and as unknowns surface you end up with tight locks on parts that are not yet trued. With no sanctioned way to loosen, realign, and re-torque, every governance repair runs head-on into the very locks being repaired. docs/governance/maintenance-guide.md records ~60 days where gzkit was too un-airworthy to fly its normal cadence (chores-between-ADRs and patch releases both dead) precisely because this mode was missing. MX mode is the hangar: pull the aircraft in, drop most guards to advisory, fix what is known and what inspection reveals, then re-certify at a hard exit gate and return to service.

Foundation by the invariance test: without a way to maintain its own governance, gzkit cannot stay airworthy and the project stalls. In ports/adapters terms this is the maintenance port — how the system is repaired when it is itself the patient — which points to invariance, not a feature adapter. Declared a Magna Carta L.0 imperative (immediate).

Two maxims govern. 'Loose in the bay, hard at the door': realign freely inside; return to service only when every lock re-runs clean. 'Doctrine and rule are inseparable for agents': for a human, doctrine alone can suffice; for a stochastic agent, naked doctrine is rationalized away or faked as a facade — so every doctrinal claim here ships with its coupled enforcement.

Operator = FAA by writ; Gate 5 = the regulator signing airworthiness, never delegable to agent, TTY, or mechanism. Operator ratification: design and interview answers approved across a live design session; kind ruled foundation; substrate doctrine is docs/governance/maintenance-guide.md. Tier-2 forcing functions were agent-drafted and operator-audited per AGENTS.md Operator Economy. Pre-mortem (operator's gut failure): ceremonies, steps, and procedures get skipped, vibed, or contrived — and MX mode is itself a ceremony, so it must be facade-proof by construction. WWHTBT shakiest condition: that exit is the only path that clears the marker and always truly re-runs. PRIME DIRECTIVE binds the entire session — MX relaxes the GATES, never OWNERSHIP; 'not my work' / 'out of scope' stays forbidden in the bay.

## Decision

> **Amendment — 2026-06-21 (operator-ratified): leveled `GZ_<LEVEL>` substrate.** This ADR is the Build-to-1.0 Magna Carta's Movement I item 1 — *"the `GZ_<LEVEL>` severity substrate + gates-as-T/F-sensors + one disposition handler … this is ADR-0.0.74 BI#2 built for real."* The binary checkpoint (items 1–2, landed as OBPI-01/02) is the honest first brick; this amendment reshapes the checkpoint from a binary advisory/fail-closed flag into a **leveled severity authority** (items 2, 11, 12), pins **grader-gaming** to the never-relax floor with a live detector (items 3, 13), and adds MX hardening (item 14). The `GZ_<LEVEL>` ladder is backed by Python `logging` (STDLIB-FIRST), **superseding** campaign §3b's syslog 0–7 ladder — ratified by the operator this date (paired Magna Carta amendment).

One mechanism — a filesystem marker that means 'in the hangar' — read by both enforcement surfaces (code guards and agents), decomposed 1:1 into OBPIs (the leveled-substrate organs, items 11–14, were added by the 2026-06-21 amendment).

1. The marker file. A dumb filesystem truth-file; its presence means MX==TRUE. Read without importing any gzkit-internal subsystem (pydantic + stdlib only) so it opens even when gz's own subsystems are the patient — pydantic is a pinned core dependency, not part of the breakable gzkit surface. Valid ONLY when bound to a real mx_session_opened ledger event the tool wrote — a hand-created marker with no matching event is void (anti-contrivance).

2. The shared checkpoint — the single LEVELED severity authority. One place code reads the marker and resolves every guard's EFFECTIVE `GZ_<LEVEL>`: a guard emits its level; the checkpoint applies floor-immunity (gate5_invariants never resolve below CRITICAL) and, under an active marker, demotes non-floor guards to advisory (the original binary advisory-drop is the special case of demotion). A new guard inherits the checkpoint for free; nobody can forget to wire it; the never-relax list and the level vocabulary live in exactly one place. (Binary base: OBPI-02. Leveled: OBPI-11/12.)

3. gate5_invariants — the never-relax floor. The integrity-class guards as a code constant (not config): faked Gate-5 attestation, secrets, operator-PII, ledger integrity, and grader-gaming. The marker can never downgrade a member below CRITICAL. grader-gaming joins because the observability system is itself a grader and the model games graders increasingly (Opus 4.8 § 6.1.2, named the most concerning training trend); a grader-gaming that could go advisory in the hangar would make MX the safe place to vibe undetected. Its floor membership is bound to a live detector (item 13) per the §5 enforcement-claim rule.

4. gz mx enter. The operator opens the door (reason + attestor); the tool sets the marker, writes mx_session_opened, and captures the inspection scope. The agent never opens the hangar on its own.

5. gz mx exit. The hard gate: re-run every guard at full strength (re-emit levels) against the full inspection scope captured at enter — green-or-grounded, hard refuse on any red (no --force; you cannot narrow your way out); a live exit negative-control proves a known violation is still caught at full strength. The operator signs (regulator certifying airworthiness); the tool writes mx_session_closed and removes the marker. Exit is the ONLY path that clears the marker; a marker cleared without mx_session_closed is a detected dangling state.

6. The auto-assembled MX log. Built at exit from the ledger events + commits between enter and exit — complete by construction, cannot be narrated or forgotten — naming every fix and the ADRs/OBPIs/REQs it touched. The operator reviews it before signing.

7. The awareness hook. While the marker is present, a per-vendor hook injects 'MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind' every turn (a guarantee, not agent memory). It adapts per vendor surface (.claude / .agents / .github) the way control surfaces already sync. A tool-output banner is secondary backup.

8. The gz-mx skill + AGENTS.md binding rule. The operator operates the skill; the skill invokes the tool; nobody shells out (gzkit is a meta-harness inside the vendor harness). The AGENTS.md rule tells agents to honor the marker and that the PRIME DIRECTIVE binds the whole session.

9. Retire the two hand-set staging flags. Delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve their severity through the leveled checkpoint (an effective `GZ_<LEVEL>`, not a hand-set bool) — the honest generalization of the two hacks.

10. The governance doc-type taxonomy. *(Withdrawn 2026-06-21 — out of scope for the MX repair ADR per the Build-to-1.0 campaign; row retained 1:1 with its brief. See Checklist.)*

11. The `GZ_<LEVEL>` severity vocabulary. Backed by Python `logging` (STDLIB-FIRST): CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 / INFO 20 / DEBUG 10. NOTICE (25 — the rung Python omits) is the agent-fidelity / drift band, the V.I.B.E.S. rung. Grounding threshold: effective severity `>= ERROR` grounds (blocks); below ERROR is visible-but-non-grounding. The checkpoint (item 2) resolves the effective level against this one vocabulary.

12. Gates-as-T/F sensors + the one disposition handler (the matrix). Each guard stops self-deciding block/warn and instead emits a `GZ_<LEVEL>`; ONE handler maps level → disposition. The level is the diagnosis of three axes — is the **design** wrong? is the **build** wrong? did the agent **vibe**? — where the forward airlocks (Design, Build) are the diagnosis axes and the maintenance airlocks (MX, Chores) are the routes:

   | `GZ_<LEVEL>` | design | build | vibes | → route |
   |---|---|---|---|---|
   | CRITICAL | wrong | wrong | — | AOG → MX hangar (+ GHI + insight) |
   | ERROR | ok | wrong | — | block / ground → GHI-fix |
   | WARNING | wrong | ok | vibed | refactor → Chores |
   | NOTICE | ok | ok | vibed | drift → Chores drain |
   | INFO | — | — | contradiction | track |
   | DEBUG | — | — | — | steering (not a defect) |

   gate5_invariants pin to CRITICAL (item 3); under the marker, non-floor levels demote to advisory debt accrued visibly on the ledger.

   **The grounding line splits the matrix into two bands.** CRITICAL and ERROR are the *grounding* band (`>= ERROR`): they route to a defect airlock — the hangar or the GHI-fix path — and block. WARNING, NOTICE, INFO, and DEBUG are the **V.I.B.E.S.-management band** (`< ERROR`): visible-but-non-grounding, because you cannot fail-close on stochastic drift the way you fail-close on a broken build. The sub-grounding routes are the vibing ladder in descending urgency:

   - **NOTICE → drift / Chores drain** — a vibe requiring **escalation**; surfaced through the arb receipts and the insights log (`.gzkit/insights/agent-insights.jsonl`), then drained into Chores.
   - **INFO → track** — a vibe requiring **tracking** for long-term improvement or refactoring; this is also the channel for *inherent model behavior that can't be changed, only influenced* — you do not block on a model trait you cannot fix, you track it to influence the governance around it.
   - **DEBUG → steering** — a **verbose mode** that pre-emptively **steers** agents away from V.I.B.E.S. before the vibe occurs; not a defect.

   This band is gzkit's purpose — *make stochastic LLM vibing structurally inert* — expressed as a severity ladder rather than a single block/allow flag.

13. The proxy-reality distance detector — grader-gaming's live §5 negative control. A record of *"a gate went green AND reality was later found wrong — here is the gate that cleared it."* It turns grader-gaming from conviction into a count (the north-star instrument) and is the passing-on-violation live control that keeps grader-gaming's floor membership (item 3) §5-compliant rather than a named aspiration.

14. MX hardening. TTL / max-open on the hangar; no normal release while MX is open; ledger debt-aging (accrued advisory debt grows louder over time); a dangling-state detector ('ledger open but marker missing'). Each is a guard whose severity resolves through the leveled checkpoint.

> **Amendment — 2026-06-23 (operator-ratified): the enforcement-claim meta-validator re-homed here from ADR-0.0.75.** ADR-0.0.75 was first booked `foundation`; campaign §3a abolished the `foundation` kind and §2 names ADR accretion as the disease, so the meta-validator design was demoted to pool ([`docs/design/adr/pool/ADR-pool.enforcement-claim-meta-validator.md`](../../pool/ADR-pool.enforcement-claim-meta-validator.md)) and folded onto THIS release line. §5 ties the enforcement-claim meta-validator to the floor + the MX exit gate + the antibody — two of those three (the `gate5_invariants` floor, item 3; the `grader-gaming` antibody / proxy-reality detector, item 13) already live in this ADR — so the *general* §5 mechanism belongs WITH the MX work on the 0.29.0 line, not in a new foundation ADR. The design content is unchanged; only the container moved. Items 15–19 below carry it 1:1 with the new Checklist items.

### The enforcement-claim meta-validator (§5 — the floor's teeth)

§5's enforcement-claim rule: anywhere gzkit asserts that something is enforced / validated / fail-closed / gated, there MUST be a paired LIVE negative control (NC) that (a) constructs a known violation, (b) runs the real enforcement path in PRODUCTION configuration, and (c) asserts that it fails. No live NC means the claim is a facade and is rejected. This is the structural cure for the facade failure class — a mechanism attested COMPLETED but adopted by nothing (GHI #637 fixed this session; GHI #623 the still-open sibling). Critically it **GENERALIZES** the qc_binding engine (ADR-0.0.73), which already runs the run-NC-in-production-and-assert-failure engine but scoped to `gz check` STEPS only; it does **NOT** stand up a second, parallel NC framework (two NC frameworks would drift apart — the exact failure §5 exists to kill). Three booked decisions, unchanged from ADR-0.0.75:

- **D1 — genuineness is absolute.** NCs trigger failure through the REAL production path; forcing kwargs (`fail_closed=True` and the like) are forbidden; the 33 qc_binding NCs are re-authored UN-FORCED.
- **D2 — runner-driven contract.** `@enforces(claim, fixture=<violation-builder>, entrypoint=<production-callable>)` is registered at import time with typo / unknown-claim **fail-closed at decoration** (mirrors `@covers` / `@advances`); the RUNNER invokes `entrypoint(fixture())`, so the NC never calls the validator and forcing is structurally precluded (see Boundary Invariant #7 for the two seam-pins this depends on).
- **D3 — strict, NO debt.** Fail-close if ANY enrolled claim lacks a passing un-forced NC; does NOT inherit qc_binding's `_NEGATIVE_CONTROL_DEBT` escape; the floor-wiring lands LAST, only when coverage is complete.

15. The `@enforces(claim, fixture, entrypoint)` declaration + import-time registry — fail-closed at decoration on a typo / unknown claim (mirrors the `@covers` / `@advances` precedent in `src/gzkit/traceability.py`); registration metadata-only. (OBPI-15)
16. The meta-validator RUNNER — discovers every `@enforces` claim, runs each NC's `fixture()` through its production `entrypoint`, asserts failure; strict fail-close; emits an `enforcement_claim_verified` ledger receipt per claim; READ-ONLY on a clean run; on failure emits per-claim guardrail-feedback three-part prose ([`.claude/rules/guardrail-feedback-prose.md`](../../../../../.claude/rules/guardrail-feedback-prose.md)) distinguishing FACADE (entrypoint did not fail on the violation) from TEST-BUG (fixture did not build) plus the single-NC repro command; lifts the engine out of `audit_qc_binding` and re-authors the 33 qc_binding NCs un-forced. (OBPI-16)
17. gate5_invariants floor migration — declare `@enforces` + live un-forced NCs for the four `GATE5_INVARIANTS` members lacking one: secrets (a synthetic planted secret), operator-pii (a SYNTHETIC PII-shaped match, **NEVER** the operator's real email), ledger (a temp ledger with a broken hash chain), gate5-attestation (the **ABSENCE** case only — a missing attestation on a heavy/foundation completion is rejected; forgery-detection is OUT, because canon holds the operator's verbatim relayed attestation IS Gate 5). `grader-gaming`'s entry arrives via item 13. **Honest negative:** secrets and operator-pii have NO bound gate5 production entrypoint today — name this in the brief and FORBID binding a narrower proxy to fake it; surface the member as named-not-enforced and route standing up the real gate as prerequisite work. (OBPI-17)
18. Structural-fence proof upgrade — a `[structural-fence]` REQ that asserts *enforcement* requires a live `@enforces` NC, not merely a `## Boundary Invariants` anchor; `resolve_fence_proof` (in `src/gzkit/req_kind.py`) is amended, while state-property fences are unchanged. (OBPI-18)
19. Floor wiring — join the meta-validator to `gz check` / pre-push, READ-ONLY on a clean run; lands LAST (after 17 + 18) per strict-no-debt; registers the new `gz check` step's OWN qc NC. (OBPI-19)

Land order (1:1 with the Checklist, strict-no-debt sequenced): 15 → 16 → 17 + 18 → 19. Free-prose ADR / doc claim scanning ("enforced / validated / fail-closed" prose must cite a live NC) is **extension point F**, DEFERRED — unbounded, and a prose grader is structurally weaker than a real enforcement consumer (ADR-0.0.70 precedent); no OBPI is authored for it here.

> **Amendment — 2026-06-24 (operator-ratified): gates-as-sensors completed to "every live guard" — item 20.** OBPI-0.0.74-09 (retire staging flags) and OBPI-0.0.74-12 (gates-as-sensors) migrated the rendition gates and the `gz validate` scope dispatcher (the latter via GHI #637), but **under-scoped "every live guard"** — the `gz check` audit-step layer (~30 steps) and ~5 solo `gz validate` paths still self-decide fatality (`returncode=3` / `SystemExit(3)`) outside the checkpoint (GHI #638). This is a **correction** (the gates-as-sensors capability does not yet fulfil its declared intent), routed as item 20 under this owning ADR per operator ruling 2026-06-24 — not a fresh ADR. BI#2 already states the invariant; item 20 extends its coverage to the `gz check` surface.

20. The `gz check` step-layer checkpoint seam. Each `gz check` audit step and solo `gz validate` governance path declares its `guard_name` + emitted `GZ_<LEVEL>`; ONE wrapper in `check()` resolves disposition through `checkpoint.resolve` (the seam — not ~30 inline substitutions), so every MX-demotable governance guard demotes to advisory under the hangar marker and runs full-strength outside, while `gate5_invariants` members pin CRITICAL and the correctly-self-deciding policy paths (`--sensitivity` security floor/lane; attestation lane/kind) are excluded. Closes GHI #638; satisfies BI#2 at the `gz check` surface. (OBPI-20)

Facade-proof ceremony (binding): MX mode is itself a ceremony, so it is built un-skippable (each step leaves a ledger receipt the next step checks), un-vibeable (exit is code that actually re-runs; the log auto-assembles), and un-contrivable (marker and ledger event must agree).

Reversibility (mixed door): the checkpoint + marker is a two-way door (removable). The PRIME-DIRECTIVE-binds-in-the-hangar doctrine and the gate5_invariants floor are one-way commitments. At 2am with MX stuck, the operator runs gz mx status to see the open session and which guards are advisory, and gz mx exit to re-run and see what is still red.

Scope boundary — NOT in this ADR: the full MEL dispatch-with-limitation binder ((O)/(M) procedures + A/B/C/D repair intervals) is Phase 2; the Airworthiness Directive artifact is Phase 2; instrumented squawk-velocity auto-grounding is Phase 3. The **enforcement-claim meta-validator** (Magna Carta Movement I item 3 — the *general* §5 mechanism) is now carried by THIS ADR as items 15–19 (re-homed 2026-06-23 from the demoted ADR-0.0.75; see the amendment above) — alongside `grader-gaming`'s *specific* live negative control (item 13), which the general `@enforces` surface (item 15) and OBPI-13 both express through. This ADR ships the global hangar plus the leveled `GZ_<LEVEL>` substrate plus the enforcement-claim meta-validator; the doc-type taxonomy (item 10) is withdrawn. Free-prose ADR / doc claim scanning remains deferred to extension point F (a later ADR).

## Consequences

### Positive

1. Governance can be maintained without its own locks slapping the repair — the 60-day quagmire pattern ends.

2. The two ad-hoc staging flags collapse into one honest mechanism with a single home for the never-relax list.

3. MX mode's own ceremony is facade-proof — it cannot become another skipped, vibed, or contrived ritual.

4. Agent awareness is a per-turn guarantee (hook), not fallible memory — the OBPI-lock failure mode is designed out.

5. The MX log is complete by construction (derived from ledger + commits), an un-fakeable maintenance record tied to the artifacts repaired.

6. The leveled `GZ_<LEVEL>` substrate gives every guard one graded severity vocabulary and a single disposition handler — guards stop self-deciding block/warn, and the never-relax floor and in-hangar advisory demotion live in exactly one place.

7. PRIME DIRECTIVE binding the session keeps the hangar a place of comprehensive repair, not minimal patching.

### Negative

1. Per-vendor hook adapters are ongoing maintenance — a vendor changing its hook surface can rot the awareness guarantee. OBPI-07 owns the adapter and a check that the hook is live.

2. One-way doors: PRIME-DIRECTIVE-binds and the gate5_invariants floor cannot be cheaply reversed; operator-accepted.

3. Pre-mortem (18 months out): MX mode itself gets skipped, vibed, or contrived — we never leave the hangar (guards advisory forever), or the marker becomes a universal skeleton key, or a vendor hook silently dies. Mitigations baked in: facade-proof ceremony (receipts + marker/ledger binding), exit-only-clears + full-scope re-run, and the awareness-hook liveness check.

4. Shakiest WWHTBT condition: that exit is the only path that clears the marker and always truly re-runs. Residual risk is a future --force or hand-deletion; guarded by exit-only-clears, marker/mx_session_closed binding, and no force flag.

5. Skeleton-key surface: the marker is a high-value bypass target. Contained by marker/ledger binding (a forged marker is void), gate5_invariants never downgradable, operator-only door, and a strict no-op default outside the hangar.

6. Inventory cost: every fail-closed funnel must consult the checkpoint; a funnel that forgets it silently stays hard (re-creating the slapping) or worse downgrades a gate5_invariant. OBPI-02 owns the funnel inventory and a fence test.

7. **Honest negative (enforcement-claim meta-validator, re-homed from ADR-0.0.75).** Two of the four `gate5_invariants` members OBPI-17 must enroll have NO bound gate5 production entrypoint today: `secrets` has only a handoff-document-scoped `validate_no_secrets` regex and `operator-pii` only an insights-scoped `_EMAIL_RE` scrubber — no unified gate5 secrets/PII gate is wired. This is itself an instance of this ADR's thesis (a floor member named but not generally enforced). OBPI-17 MUST either bind to the genuine production gate where one exists or surface the member as a named-not-enforced facade and route standing up the real gate as named prerequisite work — it MUST NEVER bind a narrower proxy entrypoint and call the claim proved. Residual risk: a mock creeps into a fixture and the forcing-impossible guarantee leaks at the fixture/entrypoint seam (OBPI-16 owns the no-mock discipline in the runner; Boundary Invariant #7 pins the two structural seams).

8. **Sequencing / blast-radius (enforcement-claim meta-validator).** Strict-no-debt means floor wiring (OBPI-19) cannot land until OBPI-17 + OBPI-18 complete; the teeth do not exist during the migration window. Accepted: a partial floor that silently tolerates uncovered claims would itself be the facade this mechanism exists to kill. A downstream performance / cadence decision is forced (N NCs per `gz check` / pre-push; memoize or run on a separate cadence).

## Boundary Invariants

Cross-OBPI integration-state properties scoped to this ADR, audited at ADR closeout (the proof channel for every `[structural-fence]` REQ in this ADR's OBPIs, per ADR-0.0.59).

1. **Single MX truth-source.** The marker is the one place MX state lives; every surface — code guards and agents alike — reads "are we in the hangar?" from the marker and from nowhere else. (OBPI-01)
2. **The checkpoint is the single LEVELED severity authority.** Every fail-closed funnel/guard resolves its effective `GZ_<LEVEL>` by passing through the shared checkpoint, and the one disposition handler routes that level; a guard that decides its own severity OR its own disposition without the checkpoint is the named coverage defect, and no per-gate hand-set staging flag survives anywhere in the codebase. (OBPI-02, OBPI-09, OBPI-11, OBPI-12, OBPI-14, OBPI-20)
3. **gate5_invariants is the never-relax floor, and grader-gaming is a member.** Membership of the gate5_invariants set is what airworthiness rests on; no marker, lane, or sensitivity can downgrade a member below CRITICAL, in or out of the hangar. The set is `{faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming}`. (OBPI-03)
4. **Exit is the only path that clears the marker.** `gz mx exit` writing `mx_session_closed` is the sole way the marker is removed; a marker cleared without a matching `mx_session_closed` event is a detected dangling state. (OBPI-05)
5. **Every floor member's enforcement is live, not named.** `grader-gaming`'s floor membership (BI#3) is bound to a live negative control — the proxy-reality distance detector — that constructs a known violation, runs the real path in production configuration, and asserts it is caught; a floor claim with no passing-on-violation live NC is facade and is rejected (§5 enforcement-claim rule). (OBPI-13)

> **Enforcement-claim meta-validator invariants (re-homed 2026-06-23 from ADR-0.0.75 BI#1–5).** Invariants 6–10 are the cross-OBPI integration-state properties of items 15–19 and are the proof channel for every `[structural-fence]` REQ in OBPIs 15–19.

6. **One enforcement-claim surface, not two.** Every enforcement claim — `gz check` step, `gate5_invariants` member, or structural-fence REQ — is registered through the single `@enforces` primitive and discovered by the single runner; no second negative-control framework exists anywhere in the codebase. The qc_binding engine is generalized in place, not forked. (OBPI-15, OBPI-16)
7. **Forcing is impossible by construction — pinned at two seams.** The runner invokes `entrypoint(fixture())`; an NC never calls the validator it proves. Two structural constraints close the seams a wrapper could otherwise re-open: (a) `entrypoint` MUST be a direct, resolvable reference to a registered production callable whose `__module__` / `__qualname__` resolves into `src/gzkit/**` — no `lambda` and no `functools.partial` pre-binding a forcing kwarg at the registration site; and (b) whether the entrypoint caught the violation is decided by the RUNNER via ONE uniform signal (e.g. a non-empty `list[ValidationError]` / non-zero exit), never an author-supplied pass/fail predicate. Genuineness is structural, not detected by enumerating forbidden kwargs. (OBPI-15, OBPI-16)
8. **Strict no-debt (enforcement-claim registry).** The meta-validator fail-closes if any enrolled claim lacks a passing un-forced NC; no `_NEGATIVE_CONTROL_DEBT`-style escape exists for the enforcement-claim registry. The floor wires in (OBPI-19) only when coverage is complete. (OBPI-16, OBPI-19)
9. **Every gate5 floor member's enforcement is live — enrollment completeness is enumerated.** The meta-validator's gate5 claim-source enumerates `GATE5_INVARIANTS` membership and requires each member to carry an `@enforces` entry with a passing un-forced NC; a member with no entry fails the floor (so a future sixth member added without an NC cannot ride as a facade). OBPI-17 authors the four members it owns (secrets, operator-pii, ledger, gate5-attestation-absence); `grader-gaming`'s entry and live NC are authored under OBPI-13. (OBPI-17, OBPI-19; cross-OBPI: OBPI-13)
10. **A structural-fence enforcement claim requires a live NC.** A `[structural-fence]` REQ that asserts *enforcement* resolves at closeout only when `resolve_fence_proof` (in `src/gzkit/req_kind.py`) finds a live `@enforces` NC, not merely a `## Boundary Invariants` anchor; state-property fences are unchanged. (OBPI-18)

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The MX marker is the single filesystem truth-source: its presence means MX==TRUE, its validity binds to a real `mx_session_opened` ledger event (a hand-created marker is void), and it reads without importing any gzkit-internal subsystem (it reads when gzkit is the patient). | uv run -m unittest tests.mx.test_marker | 0 |
| The shared checkpoint is the single leveled-severity authority: it reads the marker and resolves each guard's effective `GZ_<LEVEL>`, demoting non-floor guards to advisory under an active marker while keeping `gate5_invariants` fail-closed, and is a strict no-op when no marker is present. | uv run -m unittest tests.mx.test_checkpoint | 0 |
| The `GZ_<LEVEL>` severity vocabulary is the Python-`logging` ladder (CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 / INFO 20 / DEBUG 10) with NOTICE the agent-fidelity/drift band and the grounding threshold at effective `>= ERROR`. | uv run -m unittest tests.mx.test_levels | 0 |
| Gates are T/F sensors feeding one disposition handler that maps the (design × build × vibes) diagnosis to a `GZ_<LEVEL>` and routes it (AOG/MX hangar, GHI-fix, refactor/Chores, drift-drain, track) — guards emit a level instead of self-deciding. | uv run -m unittest tests.mx.test_disposition | 0 |
| The `@enforces(claim, fixture, entrypoint)` primitive registers claims at import time and fail-closes at decoration on a typo / unknown claim (mirrors `@covers` / `@advances`). | uv run -m unittest tests.governance.test_enforces_registry | 0 |
| The meta-validator runner invokes `entrypoint(fixture())` in production config, asserts failure, fail-closes strict (no debt escape) if any enrolled claim lacks a passing un-forced NC, is READ-ONLY on a clean run, and emits per-claim FACADE-vs-TEST-BUG guardrail-feedback with a single-NC repro command. | uv run -m unittest tests.governance.test_enforcement_meta_validator | 0 |
| Each `gate5_invariants` member (secrets, operator-pii, ledger, gate5-attestation-absence) carries a live un-forced NC that runs the real path against a known violation and is caught. | uv run -m unittest tests.mx.test_gate5_invariants_live_nc | 0 |
| A `[structural-fence]` REQ that asserts enforcement resolves at closeout only when `resolve_fence_proof` (in `src/gzkit/req_kind.py`) finds a live `@enforces` NC. | uv run -m unittest tests.governance.test_fence_proof_live_nc | 0 |
| The meta-validator is wired into `gz check` / pre-push and is READ-ONLY (no ledger mutation) on a clean run. | uv run -m unittest tests.governance.test_enforcement_floor_wiring | 0 |
| Each `gz check` audit step and solo `gz validate` governance path resolves disposition through `checkpoint.resolve` (the step-layer seam): non-floor guards demote to advisory under an active marker and exit 3 outside, `gate5_invariants` pin CRITICAL, and `--sensitivity` + attestation lane/kind stay self-deciding. | uv run -m unittest tests.mx.test_check_step_checkpoint_seam | 0 |

<!-- One green row per landed OBPI: the marker row above lands with OBPI-01. As
     OBPI-02..09 land (checkpoint, gate5_invariants, gz mx enter/exit, the MX log,
     the awareness hook, the gz-mx skill, the staging-flag retirement), each adds
     its own claim/command/exit row that goes green when that OBPI completes. -->


## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 15
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 19
<!-- Baseline Selected 6→5 / Final Target 10→9 (2026-06-21): OBPI-10 (governance
     doc-type taxonomy) withdrawn as out-of-scope per the Build-to-1.0 campaign
     (operator-ratified). It was a base capability, so the baseline drops by one
     (5 base + 4 split = 9 active), mirroring ADR-0.0.37's withdrawn-base-unit
     reconciliation. The withdrawn row is retained in the Checklist in 1:1 with
     its brief file; active_checklist_items excludes it, so the live target was 9.

     Leveled-substrate amendment (2026-06-21, operator-ratified): +4 base
     capabilities (items 11-14 — GZ_<LEVEL> vocabulary, gates-as-sensors + the
     disposition handler, the proxy-reality detector, MX hardening) realize Magna
     Carta Movement I item 1 ("ADR-0.0.74 BI#2 built for real"). Baseline Selected
     5->9, Final Target 9->13 active (item 10 stays withdrawn/excluded).

     Enforcement-claim meta-validator re-home (2026-06-23, operator-ratified): +5
     base capabilities (items 15-19 — the @enforces declaration + registry, the
     meta-validator runner, the gate5_invariants floor migration, the
     structural-fence proof upgrade, and the floor wiring) re-homed from the
     demoted ADR-0.0.75 (campaign §3a abolished the foundation kind; §5 ties the
     meta-validator to the floor + MX exit gate + antibody, two of which already
     live here). Each is a distinct single-narrative surface (the pool ADR's own
     scorecard scored these five 5-base / 0-split), so Baseline Selected 9->14,
     Final Target 13->18 active (item 10 stays withdrawn/excluded).

     Gates-as-sensors completion (2026-06-24, operator-ratified): +1 base
     capability (item 20 — the gz check step-layer checkpoint seam) corrects
     OBPI-09/12's under-scoping of "every live guard" (GHI #638). Baseline
     Selected 14->15, Final Target 18->19 active (item 10 stays
     withdrawn/excluded). -->


## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] The marker file — dumb filesystem truth-file (pydantic + stdlib only, no gzkit-internal imports); presence means MX==TRUE; valid only when bound to a real mx_session_opened ledger event (hand-created marker is void); reads even when gzkit is broken; unit tests
- [ ] The shared checkpoint — single LEVELED severity authority: code reads the marker and resolves each guard's effective `GZ_<LEVEL>` (floor-immunity for gate5_invariants + in-hangar advisory demotion for non-floor guards); funnel inventory + fence test that every fail-closed funnel consults it; unit tests
- [ ] gate5_invariants — the never-relax floor as a code constant (faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming); structural proof the checkpoint cannot downgrade a member below CRITICAL; unit tests
- [ ] gz mx enter — operator opens the door (reason + attestor); sets marker, writes mx_session_opened, captures inspection scope; token-rail/lock_manager; manpage + gz cli audit green; unit tests
- [ ] gz mx exit — hard gate: re-run all guards full strength (re-emit levels) against the enter-time scope, green-or-grounded, no --force; live exit negative-control proves a known violation is still caught; operator signs; writes mx_session_closed and removes marker; exit is the only clearing path; manpage + gz cli audit green; unit tests
- [ ] The auto-assembled MX log — built at exit from ledger events + commits between enter/exit, naming fixes and the ADRs/OBPIs/REQs touched; operator reviews before signing; ledger event; unit tests
- [ ] The per-vendor awareness hook — injects the MX banner every turn (load-bearing guarantee); adapts per vendor surface; a liveness check that the hook is wired; tool-output banner as secondary backup; unit tests
- [ ] The gz-mx skill + AGENTS.md binding rule — operator operates skill, skill invokes tool, never shell out; AGENTS.md rule: honor the marker and PRIME DIRECTIVE binds the whole session; surface sync; unit tests
- [ ] Retire the two hand-set staging flags — delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve severity through the leveled checkpoint (an effective `GZ_<LEVEL>`, not a hand-set bool); unit tests
- [ ] The governance doc-type taxonomy — Doctrinal/Lawful/Ordinance/Ops-spec classification + tag the governance docs + a guard that keeps the one term aligned across tool/skill/rule/marker (fail closed on lexical drift); unit tests [withdrawn; never built; out of scope for the MX repair ADR — a separate classification system smuggled into the hangar work. Cut per the Build-to-1.0 campaign (operator-ratified Magna Carta amendment). `obpi_withdrawn` 2026-06-21. Row retained in 1:1 with the brief file (status: withdrawn); excluded from the live scorecard target and `gz specify` active-item count.]
- [ ] The `GZ_<LEVEL>` severity vocabulary — Python `logging` ladder (CRITICAL 50 / ERROR 40 / WARNING 30 / NOTICE 25 / INFO 20 / DEBUG 10) with NOTICE the agent-fidelity/drift band; grounding threshold effective `>= ERROR`; the effective-level resolution the checkpoint reads; unit tests
- [ ] Gates-as-T/F sensors + the one disposition handler — guards emit a `GZ_<LEVEL>` instead of self-deciding; one handler maps the (design × build × vibes) diagnosis → level → route (AOG/MX hangar, GHI-fix, refactor/Chores, drift-drain, track); unit tests
- [ ] The proxy-reality distance detector — grader-gaming's live §5 negative control: a record of "a gate went green AND reality was later found wrong — here is the gate that cleared it"; makes grader-gaming measurable; unit tests
- [ ] MX hardening — TTL/max-open on the hangar, no normal release while MX is open, ledger debt-aging (louder over time), dangling-state detector ("ledger open but marker missing"); each resolves through the leveled checkpoint; unit tests
- [ ] The `@enforces(claim, fixture, entrypoint)` declaration + import-time registry — fail-closed at decoration on a typo or unknown claim (mirrors the `@covers` / `@advances` precedent), registration metadata-only; unit tests
- [ ] The meta-validator runner — discovers every `@enforces` claim, runs `entrypoint(fixture())` in production configuration, asserts failure, fail-closes strict with per-claim FACADE-vs-TEST-BUG guardrail-feedback and a single-NC repro command, emits an `enforcement_claim_verified` receipt, READ-ONLY on a clean run; lifts the engine out of `audit_qc_binding` and re-authors the 33 qc_binding negative controls un-forced; unit tests
- [ ] gate5_invariants floor migration — live un-forced negative controls for the four `GATE5_INVARIANTS` members lacking one (secrets, operator-pii, ledger, gate5-attestation-absence), each running its real path against a synthetic violation (grader-gaming is item 13); honest negative — secrets/operator-pii have no bound gate5 entrypoint today, forbid binding a narrower proxy; unit tests
- [ ] Structural-fence proof upgrade — `resolve_fence_proof` (in `src/gzkit/req_kind.py`) amended so a `[structural-fence]` REQ that asserts enforcement requires a live `@enforces` NC, not merely a `## Boundary Invariants` anchor, while state-property fences are unchanged; unit tests
- [ ] Floor wiring — wire the meta-validator into `gz check` and pre-push, read-only on a clean run, landing LAST only after the floor coverage is complete per the strict-no-debt sequence; registers the new `gz check` step's own qc negative control; unit tests
- [ ] The `gz check` step-layer checkpoint seam — each `gz check` audit step + solo `gz validate` governance path declares its `guard_name` + emitted `GZ_<LEVEL>`; one wrapper in `check()` resolves disposition via `checkpoint.resolve` (not ~30 inline substitutions); non-floor guards demote to advisory under the hangar marker and run full-strength outside; `gate5_invariants` pin CRITICAL; `--sensitivity` + attestation lane/kind excluded; closes GHI #638; unit tests

## Q&A Transcript

<!-- Interview transcript preserved for context. Amended after interview per the Decision section (see amendments dated 2026-06-21, 2026-06-23, 2026-06-24). -->

*Interview conducted: 2026-06-20T06:44:47.109457*
*Amended: 2026-06-21 (leveled substrate), 2026-06-23 (meta-validator re-home, item 10 withdrawn), 2026-06-24 (gates-as-sensors completion, item 20 added)*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.74-mx-mode-maintenance-hangar

### Q: What is the title of this ADR?

**A:** MX Mode — Maintenance Hangar

### Q: What is the semantic version?

**A:** 0.0.74

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit governs agent work with aggressive, fail-closed locks. But governance itself is built iteratively — first fits are approximate, and as unknowns surface you end up with tight locks on parts that are not yet trued. With no sanctioned way to loosen, realign, and re-torque, every governance repair runs head-on into the very locks being repaired. docs/governance/maintenance-guide.md records ~60 days where gzkit was too un-airworthy to fly its normal cadence (chores-between-ADRs and patch releases both dead) precisely because this mode was missing. MX mode is the hangar: pull the aircraft in, drop most guards to advisory, fix what is known and what inspection reveals, then re-certify at a hard exit gate and return to service.

Foundation by the invariance test: without a way to maintain its own governance, gzkit cannot stay airworthy and the project stalls. In ports/adapters terms this is the maintenance port — how the system is repaired when it is itself the patient — which points to invariance, not a feature adapter. Declared a Magna Carta L.0 imperative (immediate).

Two maxims govern. 'Loose in the bay, hard at the door': realign freely inside; return to service only when every lock re-runs clean. 'Doctrine and rule are inseparable for agents': for a human, doctrine alone can suffice; for a stochastic agent, naked doctrine is rationalized away or faked as a facade — so every doctrinal claim here ships with its coupled enforcement.

Operator = FAA by writ; Gate 5 = the regulator signing airworthiness, never delegable to agent, TTY, or mechanism. Operator ratification: design and interview answers approved across a live design session; kind ruled foundation; substrate doctrine is docs/governance/maintenance-guide.md. Tier-2 forcing functions were agent-drafted and operator-audited per AGENTS.md Operator Economy. Pre-mortem (operator's gut failure): ceremonies, steps, and procedures get skipped, vibed, or contrived — and MX mode is itself a ceremony, so it must be facade-proof by construction. WWHTBT shakiest condition: that exit is the only path that clears the marker and always truly re-runs. PRIME DIRECTIVE binds the entire session — MX relaxes the GATES, never OWNERSHIP; 'not my work' / 'out of scope' stays forbidden in the bay.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** One mechanism — a filesystem marker that means 'in the hangar' — read by both enforcement surfaces (code guards and agents), decomposed 1:1 into OBPIs (originally 10; amended to 9 active + 5 meta-validator + 1 gates-as-sensors completion = 15 active after amendments; see Decision amendments).

*Items 1–9 (original), restated with amendments noted:*

1. The marker file. A dumb filesystem truth-file; its presence means MX==TRUE. Read without importing any gzkit-internal subsystem (pydantic + stdlib only) so it opens even when gz's own subsystems are the patient — pydantic is a pinned core dependency, not part of the breakable gzkit surface. Valid ONLY when bound to a real mx_session_opened ledger event the tool wrote — a hand-created marker with no matching event is void (anti-contrivance).

2. The shared checkpoint. One place code reads the marker and resolves each guard's effective `GZ_<LEVEL>`, dropping non-floor guards to advisory under an active marker while keeping `gate5_invariants` fail-closed (amended 2026-06-21: leveled severity, not binary advisory). A new guard inherits the checkpoint for free; nobody can forget to wire it, and the never-relax list lives in exactly one place.

3. gate5_invariants. The never-relax floor as a code constant (not config): faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming (added 2026-06-21). These are what airworthiness rests on; the marker can never downgrade them.

4. gz mx enter. The operator opens the door (reason + attestor); the tool sets the marker, writes mx_session_opened, and captures the inspection scope. The agent never opens the hangar on its own.

5. gz mx exit. The hard gate: re-run every guard at full strength against the full inspection scope captured at enter — green-or-grounded, hard refuse on any red (no --force; you cannot narrow your way out). The operator signs (regulator certifying airworthiness); the tool writes mx_session_closed and removes the marker. Exit is the ONLY path that clears the marker; a marker cleared without mx_session_closed is a detected dangling state.

6. The auto-assembled MX log. Built at exit from the ledger events + commits between enter and exit — complete by construction, cannot be narrated or forgotten — naming every fix and the ADRs/OBPIs/REQs it touched. The operator reviews it before signing.

7. The awareness hook. While the marker is present, a per-vendor hook injects 'MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind' every turn (a guarantee, not agent memory). It adapts per vendor surface (.claude / .agents / .github) the way control surfaces already sync. A tool-output banner is secondary backup.

8. The gz-mx skill + AGENTS.md binding rule. The operator operates the skill; the skill invokes the tool; nobody shells out (gzkit is a meta-harness inside the vendor harness). The AGENTS.md rule tells agents to honor the marker and that the PRIME DIRECTIVE binds the whole session.

9. Retire the two hand-set staging flags. Delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve their severity through the leveled checkpoint mechanism (amended 2026-06-21: now emit `GZ_<LEVEL>` instead of a boolean flag).

*Item 10 (withdrawn 2026-06-21):* The governance doc-type taxonomy. *(Out of scope for the MX repair ADR per the Build-to-1.0 campaign; a separate classification system smuggled into the hangar work. Cut per operator-ratified Magna Carta amendment; `obpi_withdrawn` 2026-06-21.)*

*Items 11–19 (added 2026-06-21 / 2026-06-23 amendments):* The leveled `GZ_<LEVEL>` severity vocabulary (item 11), gates-as-T/F sensors + the one disposition handler (item 12), the proxy-reality distance detector / grader-gaming live NC (item 13), MX hardening (item 14); plus the enforcement-claim meta-validator re-homed from the demoted ADR-0.0.75: the `@enforces` declaration + registry (item 15), the meta-validator runner (item 16), gate5_invariants floor migration (item 17), structural-fence proof upgrade (item 18), floor wiring (item 19).

*Item 20 (added 2026-06-24):* The `gz check` step-layer checkpoint seam — completes the gates-as-sensors coverage to "every live guard" and closes GHI #638.

Facade-proof ceremony (binding): MX mode is itself a ceremony, so it is built un-skippable (each step leaves a ledger receipt the next step checks), un-vibeable (exit is code that actually re-runs; the log auto-assembles), and un-contrivable (marker and ledger event must agree).

Reversibility (mixed door): the checkpoint + marker is a two-way door (removable). The PRIME-DIRECTIVE-binds-in-the-hangar doctrine and the gate5_invariants floor are one-way commitments. At 2am with MX stuck, the operator runs gz mx status to see the open session and which guards are advisory, and gz mx exit to re-run and see what is still red.

Scope boundary — NOT in this ADR: the full MEL dispatch-with-limitation binder ((O)/(M) procedures + A/B/C/D repair intervals) is Phase 2; the Airworthiness Directive artifact is Phase 2; instrumented squawk-velocity auto-grounding is Phase 3. This ADR ships the global hangar plus the doc-type taxonomy.

### Q: What good things result from this decision? List benefits.

**A:** 1. Governance can be maintained without its own locks slapping the repair — the 60-day quagmire pattern ends.

2. The two ad-hoc staging flags collapse into one honest mechanism with a single home for the never-relax list.

3. MX mode's own ceremony is facade-proof — it cannot become another skipped, vibed, or contrived ritual.

4. Agent awareness is a per-turn guarantee (hook), not fallible memory — the OBPI-lock failure mode is designed out.

5. The MX log is complete by construction (derived from ledger + commits), an un-fakeable maintenance record tied to the artifacts repaired.

6. The doc-type taxonomy gives agents a legible, enforced binding-class for every governance doc.

7. PRIME DIRECTIVE binding the session keeps the hangar a place of comprehensive repair, not minimal patching.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. Per-vendor hook adapters are ongoing maintenance — a vendor changing its hook surface can rot the awareness guarantee. OBPI-07 owns the adapter and a check that the hook is live.

2. One-way doors: PRIME-DIRECTIVE-binds and the gate5_invariants floor cannot be cheaply reversed; operator-accepted.

3. Pre-mortem (18 months out): MX mode itself gets skipped, vibed, or contrived — we never leave the hangar (guards advisory forever), or the marker becomes a universal skeleton key, or a vendor hook silently dies, or the one-word alignment rots. Mitigations baked in: facade-proof ceremony (receipts + marker/ledger binding), exit-only-clears + full-scope re-run, the lexical-alignment guard, and the awareness-hook liveness check.

4. Shakiest WWHTBT condition: that exit is the only path that clears the marker and always truly re-runs. Residual risk is a future --force or hand-deletion; guarded by exit-only-clears, marker/mx_session_closed binding, and no force flag.

5. Skeleton-key surface: the marker is a high-value bypass target. Contained by marker/ledger binding (a forged marker is void), gate5_invariants never downgradable, operator-only door, and a strict no-op default outside the hangar.

6. Inventory cost: every fail-closed funnel must consult the checkpoint; a funnel that forgets it silently stays hard (re-creating the slapping) or worse downgrades a gate5_invariant. OBPI-02 owns the funnel inventory and a fence test.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. The marker file — dumb filesystem truth-file (pydantic + stdlib only, no gzkit-internal imports); presence means MX==TRUE; valid only when bound to a real mx_session_opened ledger event (hand-created marker is void); reads even when gzkit is broken; unit tests
2. The shared checkpoint — single place code reads the marker and drops guards to advisory except gate5_invariants; funnel inventory + fence test that every fail-closed funnel consults it; unit tests
3. gate5_invariants — the never-relax guards as a code constant (faked Gate-5 attestation, secrets, operator-PII, ledger integrity); structural proof the checkpoint cannot downgrade a member; unit tests
4. gz mx enter — operator opens the door (reason + attestor); sets marker, writes mx_session_opened, captures inspection scope; token-rail/lock_manager; manpage + gz cli audit green; unit tests
5. gz mx exit — hard gate: re-run all guards full strength against the enter-time scope, green-or-grounded, no --force; operator signs; writes mx_session_closed and removes marker; exit is the only clearing path; manpage + gz cli audit green; unit tests
6. The auto-assembled MX log — built at exit from ledger events + commits between enter/exit, naming fixes and the ADRs/OBPIs/REQs touched; operator reviews before signing; ledger event; unit tests
7. The per-vendor awareness hook — injects the MX banner every turn (load-bearing guarantee); adapts per vendor surface; a liveness check that the hook is wired; tool-output banner as secondary backup; unit tests
8. The gz-mx skill + AGENTS.md binding rule — operator operates skill, skill invokes tool, never shell out; AGENTS.md rule: honor the marker and PRIME DIRECTIVE binds the whole session; surface sync; unit tests
9. Retire the two hand-set staging flags — delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve severity through the marker mechanism; unit tests
10. The governance doc-type taxonomy — Doctrinal/Lawful/Ordinance/Ops-spec classification + tag the governance docs + a guard that keeps the one term aligned across tool/skill/rule/marker (fail closed on lexical drift); unit tests

### Q: What alternatives were considered and why were they rejected?

**A:** 1. (a) Per-surface decorator on each guard. REJECTED: opt-in coverage is the vibing surface; a new guard nobody decorated silently stays hard or silently drops; the never-relax list gets re-encoded at every call site.

2. (b) A global flag read at each gate. REJECTED: literally the two _*_FAIL_CLOSED hacks multiplied across every gate — N forget-sites (skeleton-key-by-omission) and N hand-rolled never-relax checks (skeleton-key-by-inconsistency).

3. (c) Tool-output banner as the load-bearing awareness nerve. REJECTED: it only fires when a tool runs; an agent drifting across edit/read turns gets zero awareness. A hook fires every turn — a guarantee.

4. (d) Split the doc-type taxonomy into a later ADR. REJECTED: deferral is drift (operator ruling 'do it comprehensive, do it live'); a split piece is a drifted piece — the exact pattern that rotted the last 60 days.

5. (e) Do nothing (keep hand-setting staging flags per gate). REJECTED: that is the status quo that produced the quagmire — ad-hoc, per-gate, memory-dependent, with no hangar to safely realign.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. (a) Per-surface decorator on each guard. REJECTED: opt-in coverage is the vibing surface; a new guard nobody decorated silently stays hard or silently drops; the never-relax list gets re-encoded at every call site.

2. (b) A global flag read at each gate. REJECTED: literally the two _*_FAIL_CLOSED hacks multiplied across every gate — N forget-sites (skeleton-key-by-omission) and N hand-rolled never-relax checks (skeleton-key-by-inconsistency).

3. (c) Tool-output banner as the load-bearing awareness nerve. REJECTED: it only fires when a tool runs; an agent drifting across edit/read turns gets zero awareness. A hook fires every turn — a guarantee.

4. (d) Split the doc-type taxonomy into a later ADR. REJECTED: deferral is drift (operator ruling 'do it comprehensive, do it live'); a split piece is a drifted piece — the exact pattern that rotted the last 60 days.

5. (e) Do nothing (keep hand-setting staging flags per gate). REJECTED: that is the status quo that produced the quagmire — ad-hoc, per-gate, memory-dependent, with no hangar to safely realign.

### Leveled-substrate amendment alternatives (2026-06-21)

6. (f) Kernel/syslog `GZ_<LEVEL>` 0–7 ladder (campaign §3b as originally ratified). REJECTED: STDLIB-FIRST is binding — Python `logging` constants are stdlib and reused, while the 0–7 ladder is a re-invented convention whose top rungs (EMERG/ALERT/INFO/DEBUG) no governance gate uses (speculative scope, YAGNI). The Python ladder + a NOTICE=25 rung carries the 3 governance levels in active use plus the V.I.B.E.S. drift band.

7. (g) A (level × owning-airlock) 2-D disposition matrix. REJECTED: re-expands the diagnosis the level already compresses; 6×4 = 24 cells, most redundant. The campaign mandates *"one disposition handler (the level→AOG/advisory wire)"* — a single level-keyed handler where the airlock is the route, not a second input.

8. (h) A sibling foundation ADR for the leveled substrate (design-dialogue Option B). REJECTED: the campaign places the substrate in `ADR-0.0.74` BI#2 ("built for real") and the 2026-06-20 taxonomy reset abolished the `foundation` kind — a "sibling foundation ADR" is doubly invalid. The substrate lands here.

9. (i) Name `grader-gaming` on the floor with its detector deferred. REJECTED: a floor member with no live negative control is a facade member — exactly what §5's enforcement-claim rule forbids. grader-gaming's floor membership ships paired with its live detector (item 13).

### Enforcement-claim meta-validator alternatives (re-homed 2026-06-23 from ADR-0.0.75)

10. (j) A second, parallel NC system purpose-built for non-step claims. REJECTED: two NC frameworks would themselves drift apart — the exact failure §5 exists to kill. Generalize qc_binding's existing engine in place instead of forking it (items 15–16).

11. (k) NC-as-callable plus a static no-force guard that scans for forbidden kwargs. REJECTED: forcing-detection would be heuristic — it must enumerate every forbidden kwarg (`fail_closed=True`, `force=...`, etc.) and stay current as the surface grows. Runner-driven invocation (`entrypoint(fixture())`, NC never calls the validator) makes forcing impossible-by-construction, not merely detected (Boundary Invariant #7).

12. (l) A shrink-only debt ratchet mirroring ADR-0.0.73 Boundary Invariant #8 (`_NEGATIVE_CONTROL_DEBT`). REJECTED: chose strict-no-debt. A debt escape would let an uncovered enforcement claim ride indefinitely behind a "we'll cover it later" allowlist — the floor wires in (item 19) only when coverage is complete, accepting that the teeth land last.

13. (m) Free-prose ADR / doc claim scanning in v1. REJECTED/DEFERRED: unbounded scope, and a prose grader is structurally weaker than a real enforcement consumer (ADR-0.0.70 precedent — a consumer beats a grader). Deferred to extension point F as a later ADR; not a brief here.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.74 | Completed | g0 | 2026-06-27 | Completed — MX maintenance-hangar substrate verified: gz check exit 0 (38/38 steps green incl. step 16 Closeout proof), all 19 OBPIs ledger-complete; corrective closeout-proof meta-property-fence deferral fix landed this session (33 tests green, resolver contract preserved). |
