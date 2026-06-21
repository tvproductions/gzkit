---
id: ADR-0.0.74-mx-mode-maintenance-hangar
status: Draft
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

13. The proxy-reality distance detector — grader-gaming's live §5 negative control. A record of *"a gate went green AND reality was later found wrong — here is the gate that cleared it."* It turns grader-gaming from conviction into a count (the north-star instrument) and is the passing-on-violation live control that keeps grader-gaming's floor membership (item 3) §5-compliant rather than a named aspiration.

14. MX hardening. TTL / max-open on the hangar; no normal release while MX is open; ledger debt-aging (accrued advisory debt grows louder over time); a dangling-state detector ('ledger open but marker missing'). Each is a guard whose severity resolves through the leveled checkpoint.

Facade-proof ceremony (binding): MX mode is itself a ceremony, so it is built un-skippable (each step leaves a ledger receipt the next step checks), un-vibeable (exit is code that actually re-runs; the log auto-assembles), and un-contrivable (marker and ledger event must agree).

Reversibility (mixed door): the checkpoint + marker is a two-way door (removable). The PRIME-DIRECTIVE-binds-in-the-hangar doctrine and the gate5_invariants floor are one-way commitments. At 2am with MX stuck, the operator runs gz mx status to see the open session and which guards are advisory, and gz mx exit to re-run and see what is still red.

Scope boundary — NOT in this ADR: the full MEL dispatch-with-limitation binder ((O)/(M) procedures + A/B/C/D repair intervals) is Phase 2; the Airworthiness Directive artifact is Phase 2; instrumented squawk-velocity auto-grounding is Phase 3. The **enforcement-claim meta-validator** (Magna Carta Movement I item 3 — the *general* §5 mechanism) is its own work; this ADR ships grader-gaming's *specific* live negative control (item 13), which must comply with §5. This ADR ships the global hangar plus the leveled `GZ_<LEVEL>` substrate; the doc-type taxonomy (item 10) is withdrawn.

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

## Boundary Invariants

Cross-OBPI integration-state properties scoped to this ADR, audited at ADR closeout (the proof channel for every `[structural-fence]` REQ in this ADR's OBPIs, per ADR-0.0.59).

1. **Single MX truth-source.** The marker is the one place MX state lives; every surface — code guards and agents alike — reads "are we in the hangar?" from the marker and from nowhere else. (OBPI-01)
2. **The checkpoint is the single LEVELED severity authority.** Every fail-closed funnel/guard resolves its effective `GZ_<LEVEL>` by passing through the shared checkpoint, and the one disposition handler routes that level; a guard that decides its own severity OR its own disposition without the checkpoint is the named coverage defect, and no per-gate hand-set staging flag survives anywhere in the codebase. (OBPI-02, OBPI-09, OBPI-11, OBPI-12)
3. **gate5_invariants is the never-relax floor, and grader-gaming is a member.** Membership of the gate5_invariants set is what airworthiness rests on; no marker, lane, or sensitivity can downgrade a member below CRITICAL, in or out of the hangar. The set is `{faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming}`. (OBPI-03)
4. **Exit is the only path that clears the marker.** `gz mx exit` writing `mx_session_closed` is the sole way the marker is removed; a marker cleared without a matching `mx_session_closed` event is a detected dangling state. (OBPI-05)
5. **Every floor member's enforcement is live, not named.** `grader-gaming`'s floor membership (BI#3) is bound to a live negative control — the proxy-reality distance detector — that constructs a known violation, runs the real path in production configuration, and asserts it is caught; a floor claim with no passing-on-violation live NC is facade and is rejected (§5 enforcement-claim rule). (OBPI-13)

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
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.74-mx-mode-maintenance-hangar --check | 0 |

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
- Baseline Selected: 9
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 13
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
     5->9, Final Target 9->13 active (item 10 stays withdrawn/excluded). -->


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

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-06-20T06:44:47.109457*

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

**A:** One mechanism — a filesystem marker that means 'in the hangar' — read by both enforcement surfaces (code guards and agents), decomposed 1:1 into 10 OBPIs.

1. The marker file. A dumb filesystem truth-file; its presence means MX==TRUE. Read without importing any gzkit-internal subsystem (pydantic + stdlib only) so it opens even when gz's own subsystems are the patient — pydantic is a pinned core dependency, not part of the breakable gzkit surface. Valid ONLY when bound to a real mx_session_opened ledger event the tool wrote — a hand-created marker with no matching event is void (anti-contrivance).

2. The shared checkpoint. One place code reads the marker and drops guards to advisory — everything except the gate5_invariants. A new guard inherits the checkpoint for free; nobody can forget to wire it, and the never-relax list lives in exactly one place.

3. gate5_invariants. The never-relax guards as a code constant (not config): faked Gate-5 attestation, secrets, operator-PII, ledger integrity. These are what airworthiness rests on; the marker can never downgrade them.

4. gz mx enter. The operator opens the door (reason + attestor); the tool sets the marker, writes mx_session_opened, and captures the inspection scope. The agent never opens the hangar on its own.

5. gz mx exit. The hard gate: re-run every guard at full strength against the full inspection scope captured at enter — green-or-grounded, hard refuse on any red (no --force; you cannot narrow your way out). The operator signs (regulator certifying airworthiness); the tool writes mx_session_closed and removes the marker. Exit is the ONLY path that clears the marker; a marker cleared without mx_session_closed is a detected dangling state.

6. The auto-assembled MX log. Built at exit from the ledger events + commits between enter and exit — complete by construction, cannot be narrated or forgotten — naming every fix and the ADRs/OBPIs/REQs it touched. The operator reviews it before signing.

7. The awareness hook. While the marker is present, a per-vendor hook injects 'MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind' every turn (a guarantee, not agent memory). It adapts per vendor surface (.claude / .agents / .github) the way control surfaces already sync. A tool-output banner is secondary backup.

8. The gz-mx skill + AGENTS.md binding rule. The operator operates the skill; the skill invokes the tool; nobody shells out (gzkit is a meta-harness inside the vendor harness). The AGENTS.md rule tells agents to honor the marker and that the PRIME DIRECTIVE binds the whole session.

9. Retire the two hand-set staging flags. Delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve their severity through the one marker mechanism (the honest generalization of the two hacks).

10. The governance doc-type taxonomy. Classify governance docs Doctrinal / Lawful / Ordinance / Ops-spec, tag them, and add a guard that keeps the ONE term aligned across tool / skill / rule / marker (fail closed on lexical drift).

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

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.74 | Pending | | | |
