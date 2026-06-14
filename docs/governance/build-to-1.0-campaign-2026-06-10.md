# Build-to-1.0 Campaign, 2026-06-10

Status: **ACTIVE — Magna Carta, the one canonical plan** (operator-ratified
2026-06-10; elevated to Magna Carta same day).

> **Ratification (operator verbatim, 2026-06-10):** "let your new Build-to-1.0
> campaign subsume and supersede all prior plans (emergencies, five-alarm
> fires, restore-health). Also, any plan must address all GHIs and incorporate
> the discipline needed to handle the emergence of new GHI moments."
>
> **Elevation (operator verbatim, 2026-06-10):** "Build-to-1.0 Campaign is now
> Magna Carta, it must rule (and be updated when needed) to get our legs back
> under us."
>
> **Refinement (operator verbatim, 2026-06-10):** "Magna Carta it does not
> invalidate ADR, OBPI, and GHI repair as primary propellants of the work.
> Magna Carta should help refine/facilitate gzkit's governance and build
> facility."
>
> **Amendment (operator verbatim, 2026-06-10):** "we don't direct edit
> AGENTS.md. the CMS system must be prioritized as a near-top priority."
> → CMS completion (ADR-0.0.37 corpus → compress → rendition → playback)
> inserted as Phase B, between in-flight closure and the MOTD build; all
> subsequent phases renumbered.
>
> **Amendment (operator verbatim, 2026-06-12):** "do max improvement from
> Florian Buetow's practices. ensure this becomes aware of this addition:
> docs/governance/build-to-1.0-campaign-2026-06-10.md" → Buetow adoption
> booked as **ADR-0.0.70** (turn-end Stop-hook feedback, session-correction
> mining, guardrail-feedback-prose rule, fourth-source triangulation) and
> inserted as item **B.0**, executed same-day through the governed
> gz-adr-create → OBPI path. Operator closing remark, same exchange: "I guess
> this means that gzkit may end up being worth the effort in the end."
>
> **Amendment (operator verbatim, 2026-06-14):** *"gzkit is a martial art - a
> doctrinal WAY of battle - but each project is the battlefield. The firewall is
> needed to NOT allow the skunkworks to follow the toolset out of the
> lab/factory. The rigging and jigs do not remain attached to the fuselage once
> we open the factory hangar doors for final delivery - we haven't been careful
> about this."* Also: *"some skills go out to the adopter as well (as do other
> harness things)"* and *"the foundation needs to carry both because the are
> inseparable, and with the cms for progressive disclosure, both are mechanical."*
> → A **Firewall foundation ADR** (rooted in GHI #607) is inserted, classifying
> every delivered surface — rules, **skills**, hooks, agent defs, harness — by
> destiny (**wheel-borne / authored-into-battlefield / lab-only-jig**) at
> scaffold-time and validate-time, and carrying **both** a mechanical face
> (jig-escape made structurally impossible) and a communicative face (a
> self-explaining scaffold-boundary surface, rendered mechanically through the
> CMS).
>
> **Resequencing (operator ruling "a", 2026-06-14).** Phase 0 (GHI #615) remains
> the burning emergency, but its *correct* fix — frontmatter-as-projection (see
> the rites amendment) — was found to be the **tail** of a dependency chain, not
> a standalone fix. Propulsion order is therefore: **B.1 CMS (ADR-0.0.37) →
> Firewall foundation ADR → barcode + lifecycle doctrine (the GHI #615 cure) →
> skills-first enforcement (follow-on, prior-art-gated).** Phase 0 still blocks
> the *naive* vocabulary edits it forbids; it no longer blocks the CMS work its
> own cure depends on. The skills-first enforcement follow-on (operator: *"gzkit
> is doing a terrible job of forcing models/agents to use SKILLS FIRST"*) is
> filed as a prior-art-gated successor ADR; prior-art research landed 2026-06-14
> (`docs/governance/prior-art-scaffold-firewall-2026-06-14.md`) and finds the
> only structural skills-first primitive is a scoped `PreToolUse` deny gate.

## Authority and amendment (Magna Carta discipline)

- **It steers; the spine propels.** The governance spine
  (PRD → Constitution → ADR → OBPI → REQ → TASK → Attestation) and GHI repair
  remain the **primary propellants** of the work. Every campaign item
  executes through its governed path — OBPI pipeline, closeout ceremonies,
  defect-fix routing — exactly as before. The campaign refines and
  facilitates that machinery toward 1.0: it sequences ceremony, it never
  substitutes for it, bypasses a gate, or competes with it as a parallel
  work-ordering system.
- **It rules the sequencing.** Every session works this plan's topmost
  unchecked item whose gate is met. Handoffs, triage briefs, and the MOTD
  ADVISE; the campaign governs what is pulled next. No work stream runs
  outside it except `emergency`-labeled interrupts (§ GHI emergence
  discipline rule 3), which the campaign itself defines.
- **It is surfaced mechanically.** `scripts/session_orientation.py` renders
  the campaign as the FIRST section of every SessionStart digest — plan path,
  burn-down count, topmost unchecked items, and the authority note. A session
  that starts without the campaign in view is a defect
  (`collect_campaign` contract, `tests/scripts/test_session_orientation.py`).
- **It is living.** Checking items off with observed command evidence and
  regenerating the GHI register are routine session work. **Amendments** —
  scope changes, phase changes, new overrides — require operator
  ratification, recorded in place with the operator's verbatim words, exactly
  as the rulings above are recorded.
- **It dies only by succession.** Per the MOTD campaign doctrine ("campaigns
  supersede in place"), only a ratified successor campaign retires this plan
  — never silence, never drift.

> **Doctrine (operator verbatim, 2026-06-10):** "I want to build out gzkit, as
> found, as comprehended, and ONLY THEN make reductive decisions. where it is
> redundant, I want to know after it is proven; where it is dead/hollow, let an
> implementation show that; where it works, let working proof speak."
>
> **Completion before reduction.** Every reductive move (cull, retire, merge,
> optimize, straighten) is deferred to the post-1.0 reduction pass (Phase I).
> Mid-campaign course-corrections amend the census; they never change direction.
> This is the structural cure for the named failure mode: partial corrections
> leave seams that ensnare later sessions because no model co-owns the whole.

## Succession

This campaign **subsumes and supersedes all prior plans** (operator ruling,
2026-06-10), per restore-health's own § Session MOTD §5 doctrine ("campaigns
supersede in place"). Operating Rule 1 is preserved: **one active plan; this
file is the plan.** Superseded artifacts (retained on disk for audit, each
carrying a supersession banner pointing here):

| Superseded artifact | Was |
|---|---|
| [`return-to-health-plan-2026-05-30.md`](return-to-health-plan-2026-05-30.md) | Active canonical recovery plan (emergencies, Tier-0 fires, snapshots A–N) |
| [`ultraplan-brief.md`](../../ultraplan-brief.md) | Single planning input for ultraplan (restore-health convergence) |
| [`restore-health-convergence-roadmap.md`](../design/restore-health-convergence-roadmap.md) | Layer-3 sequencing view over the ultraplan brief |

`docs/design/ARCHITECTURE-PLANNING-MEMO.md` is retained as a historical
doctrine source, **not** superseded wholesale — but its Boundaries 1–2 are
overridden below. Per-OBPI plan files under `.claude/plans/` are execution
artifacts of their briefs, not campaign plans; they are untouched.

Restore-health's unfinished threads are carried forward here, not orphaned:

- **#519** (sole open emergency; codex 258K window) → cured inside Phase B
  (CMS completion — near-top by operator amendment, 2026-06-10) by the
  ADR-0.0.37 build-out (<15k registry-projected surface, GHI #533) + Gate 5.
  Closing it fills restore-health's Recovery Closeout retroactively.
- **Phase 3/4 GHI register** (~38 open) → absorbed into the steady-state
  triage cadence (§ Cadence).
- The green floor (ADR-0.0.68, Validated) remains the standing invariant:
  `uv run gz check` green on `main` at every session boundary, enforced by the
  pre-push gate + session-green-gate validator.

Four prior directives are **explicitly overridden by operator ratification of
this campaign** (quoted verbatim per DO IT RIGHT 6h):

1. Definition of Healthy: *"New doctrine, new foundation ADRs, and new
   validators are frozen unless they directly repair a failing gate."* →
   Replaced by: booked-surface completion and promotion/booking ceremonies are
   always in scope; **unbooked** doctrine remains frozen until 1.0.
2. ultraplan-brief P3: *"these are additive — pace by felt need, not
   momentum."* → Replaced by campaign-cadence burn-down (§ Cadence).
3. AGENTS.md § Architectural Boundaries 1: *"Do not promote post-1.0 pool
   ADRs into active work."* → Overridden by the full-pool-build-out ruling
   (Scope decision 1): every live pool item reaches a terminal disposition
   before 1.0.
4. AGENTS.md § Architectural Boundaries 2: *"Do not add more pool ADRs to the
   runtime track."* → Same override. The rendered AGENTS.md is amended through
   the governed corpus path (invariant-coherence byte-compares it; no direct
   edit) — tracked as Phase B.3.

## Scope decisions (booked 2026-06-10, operator dialogue)

| # | Decision | Ruling |
|---|---|---|
| 1 | Pool participation | **Full pool build-out.** All 139 live pool items are processed through the promotion pipeline to a terminal disposition: promoted-and-built, or parked/superseded only when promotion-stage evidence (overlap with a landed surface, absorption shown by implementation) proves it — never by taste. No item left undecided at 1.0. |
| 2 | Canon Foundation workstream | **Booked into 1.0.** Its ADR(s) are authored early in Phase E; build proceeds in increments per the workstream's §12 ("design covers all; build increments"). |
| 3 | Per-ADR done-bar | **Validated or operator-parked.** Every booked ADR reaches Validated (audit ceremony) OR is consciously parked by operator attestation with a named reason. Parking is a completion decision and prime Phase-H evidence. |
| 4 | First-wave sequencing | **In-flight first, then MOTD.** ADR-0.0.69 (02–04) and the ADR-0.0.41 closeout land before the MOTD build opens. *Amended same day (operator): CMS completion inserted between in-flight closure and MOTD — "the CMS system must be prioritized as a near-top priority."* |

Identity sequence (booked earlier same dialogue): **research instrument +
published exemplar → personal toolkit → public product.** 1.0 serves the first
identity; adoption work is not a 1.0 gate.

## Goal state — the 1.0 definition

gzkit is 1.0 when ALL hold:

- **Census reads 100% terminal** — every booked foundation + pre-release ADR
  is Validated or operator-parked; every live pool item has a terminal
  disposition (built or evidence-parked).
- **MOTD shipped** per its exit criteria (restore-health § Session MOTD §8):
  login briefing with 3–5 priority moves, logout continuity, two logrotating
  logs, advisory-only doctrine.
- **Canon Foundation** ADRs Validated (or operator-parked with named reason).
- **Declared surfaces wired**: the 6 manual-only validator scopes
  (`router-tables`, `orphaned-implementation`, `brief-command-shape`,
  `brief-demo-section`, `brief-cross-references`, `scenario-reachability`)
  run on a governed cadence; the 3 provenance-gap scopes
  (`advisor-proof-binding`, `intrinsic-attestation`, `pointer-anchors`) have
  booked origins; the absorbed pool-triage design (ADR-0.0.46/47) has its
  surface.
- **#519 closed**; no open emergency; restore-health Recovery Closeout filled.
- **Green floor holding**; GHI backlog at steady-state triage scale.
- **v1.0.0 released** through the patch-release ceremony.

## Phases

> Green-first is inherited: no phase opens while `uv run gz check` is red.
> Until MOTD ships (Phase C), **this file's checklist is the workplan** —
> sessions work top-down, check items off with observed command evidence.

### Phase 0 — EMERGENCY: The Vocabulary Config-First Exorcism (GHI #615)

> **Badge of shame and despair (operator verbatim, 2026-06-13):** "this goes
> right at the GODDAMNED TOP of the campaign … one GHI only — a badge of shame
> and despair." gzkit has **no central config** for its governance vocabularies
> (`status`, `lane`). The values were copied into ~9 Pydantic models, 2
> mutually-contradictory JSON schemas, 600 brief frontmatters, the ADR corpus,
> authoring tools, skills, validators, and docs — each copy free to drift.
> Nobody plays the same song, in the same key, in the same room. This is
> **V.I.B.E.S. at the canon layer** — the governance surface became the slop it
> exists to prevent. The cure is the Config-First doctrine airlineops already
> proves (their GHI-75): one source of truth, everything derives, AST + drift
> policy tests across every surface.
>
> **This phase blocks every other phase. Rome burns until it is fixed.** One
> GHI carries it — **#615** — the sole badge; no others are filed.

- [ ] 0.1 Ratify the canonical vocabularies — operator gate (§ Open Decisions
      in the rites). Nothing downstream executes until the vocabularies are set.
- [ ] 0.2 Perform the exorcism per the prepared rites:
      [`docs/governance/vocabulary-config-first-exorcism-GHI-615.md`](vocabulary-config-first-exorcism-GHI-615.md)
      — single source of truth (`governance/vocabulary.py` + config + loader +
      frozen fallback) → bind every model / schema / corpus / authoring tool /
      skill / validator / auditor / doc → Config-First AST policy test +
      schema↔source + corpus-conformance drift-guards, mirroring airlineops
      GHI-75. Acceptance: § 8 of the rites; `uv run gz check` green end-to-end.

> **Note (amendment 2026-06-14).** 0.1 partially satisfied: **Q1 ratified**
> (TitleCase frontmatter / snake_case ledger). The cure is reframed as
> **frontmatter-as-projection** (barcode + sidecar + lifecycle state machines for
> all four artifacts) and **resequenced behind the CMS → Firewall chain** (see
> the 2026-06-14 amendment above and the rites amendment). Q2–Q6 demote to
> render-target settings. The single-source-of-truth `governance/vocabulary.py`
> in 0.2 remains the substrate; it now feeds the render path, not strict
> frontmatter parsing.

### Phase A — In-flight closure

- [x] A.1 OBPI-0.0.69-02 (structural-fence channel boundary-invariants
      anchor) — `attested_completed` per `gz adr report ADR-0.0.69`
      (verified 2026-06-10; ADR at 2/4)
- [x] A.2 OBPI-0.0.69-03 (closeout-proof derived view + gate repoint) —
      `attested_completed` per `gz adr report ADR-0.0.69` (verified
      2026-06-10; ADR at 3/4). Active-ceremony freshness gate (24h) added
      per operator ruling; ADR-0.0.41 OBPI-02/03 repointed; pool-ADR
      task-envelope carve-out gap closed
- [x] A.3 OBPI-0.0.69-04 (retire `ln:` surface; supersedes #599) —
      `attested_completed` per `gz adr report ADR-0.0.69` (verified
      2026-06-11; ADR at 4/4); landed in commit `c60c89e4` (retire dead
      `ln:` consumer chain, GHI #601)
- [x] A.4 ADR-0.0.69 closeout ceremony → Validated — `Lifecycle: Validated`
      per `gz adr report ADR-0.0.69` (Phase-2 audit ceremony 2026-06-11;
      operator attestation "accept audit"; `validated` receipt in ledger;
      `audit/AUDIT.md`). Independent spec-reviewer + quality-reviewer both
      GREEN; 3 non-blocking findings routed (F1→GHI #573, F2/F3→ADR
      §Post-Validation Notes)
- [x] A.5 ADR-0.0.41 **Validated** 2026-06-12 — `Lifecycle: Validated` per
      `gz adr report ADR-0.0.41` (closeout ceremony → Completed + operator
      "attest completed"; Phase-2 audit ceremony → Validated + operator
      "accept audit"; `validated` receipt in ledger; `audit/AUDIT.md`).
      OBPI-01/02/03/04 `attested_completed`; **OBPI-05 operator-withdrawn**
      (`obpi_withdrawn`, superseded by ADR-0.0.65 — handoff-surface REQs;
      warn-then-reap lock-lifecycle piece carried to **GHI #603**, Phase E).
      OBPI-0.0.41-04 (lock-handoff coupling validator → `gz validate
      --lock-handoff-coupling`, in the default `gz check` chain) landed
      `3043819b`. In-flight repairs: orphaned 173-min OBPI-03 lock that had
      stalled the OBPI-03 push (failed pre-push Preflight) reaped via
      `gz preflight --apply` (relates to Phase-E #578/#564); `closeout_proof`
      validator gap (didn't honor `obpi_withdrawn`/waived REQs — would block
      ANY ADR closeout with a withdrawn OBPI) fixed with TDD in
      `fix(closeout-proof)` `e1a32cf1`. Non-blocking audit shortfall F2
      (TTL default canon-24h vs CLI-120m) → GHI #604 (Phase E).

> **ADR-0.0.65 (handoff system, in-flight at 1/4) is deliberately NOT
> closed here.** Its terminal disposition lands with the MOTD build (C.4),
> which absorbs it per the ratified MOTD design — completing it standalone
> in Phase A would fork the very system C.4 consolidates. Do not "fix"
> this omission.

Exit gate: 0.0.69 and 0.0.41 terminal; main green, synced.

### Phase B — CMS completion (near-top by operator amendment, 2026-06-10)

The corpus → compress → rendition → playback pipeline (ADR-0.0.37, the
Context-Load CMS) lands end-to-end. This is the system that makes "we don't
direct edit AGENTS.md" workable: contract changes queue in the corpus and
only deterministic playback writes the rendered surface.

- [x] B.0 ADR-0.0.70 Buetow adoption (operator-inserted 2026-06-12; see
      Amendment above) — turn-end Stop-hook feedback (gzkit-owned `Stop`
      phase), `session-correction-mining` chore (third sensor feeding the
      Promotable→Mechanical ladder), `guardrail-feedback-prose` rule,
      fourth-source triangulation in
      `docs/governance/harness-engineering-appraisal.md`. Checks off at
      ADR-0.0.70 terminal (all four OBPIs attested + closeout).
      - **Terminal 2026-06-13: ADR-0.0.70 `Validated`** per
        `gz adr report ADR-0.0.70` — all four OBPIs `attested_completed`,
        Gate-5 audit ceremony accepted ("accept audit", operator g0):
        OBPI-01 stop-hook-turn-end-feedback, OBPI-02 session-correction-mining,
        OBPI-03 guardrail-feedback-prose-rule, OBPI-04
        fourth-source-triangulation. Validation receipts (all exit 0):
        `arb-step-unittest-483ae14c…` (6097 tests), `arb-ruff-ed38ddd7…`,
        `arb-step-typecheck-d83e7132…`, `arb-step-mkdocs-fbec5b2a…`. Audit
        evidence: `…/ADR-0.0.70-…/audit/AUDIT.md`.
- [ ] B.1 ADR-0.0.37 build-out (13/19 verified 2026-06-10 via
      `gz adr report`; → terminal) — the campaign's first marquee.
- [ ] B.2 Registry-projected <15k surface (GHI #533) — closes **#519** (the
      sole open emergency), fills restore-health's Recovery Closeout.
- [ ] B.3 Play back queued corpus entries into the rendered AGENTS.md through
      the pipeline (the two Magna Carta behavior-rules entries, rendered as
      one coherent steering-vs-propulsion rule) and land the
      § Architectural Boundaries 1–2 amendment (full-pool override) the same
      governed way; `invariant-coherence` green throughout.

Exit gate: corpus → rendered-surface round-trip works under the validators;
#519 closed; no open emergency.

### Phase C — MOTD build (the cadence engine)

Per the designed build plan (restore-health § Session MOTD §7), leaf-first,
absorbing ADR-0.0.65 and implementing ADR-0.0.66 (`gz next`):

- [ ] C.1 `.gzkit/work/` store + workplan schema (campaign + daily-brief)
- [ ] C.2 `session_orientation.py` → lightweight auto-triage (the MOTD)
- [ ] C.3 Directed triage skill (`gz next` UX)
- [ ] C.4 Continuity hybrid (subsumes handoff; Stop/clear hook drafts, agent
      finalizes). Includes the terminal disposition of in-flight
      **ADR-0.0.65** (1/4 at amendment time): its remaining OBPIs complete
      inside this build or are operator-parked citing the ratified
      absorption — never left dangling.
- [ ] C.5 Independent logrotation for the two logs
- [ ] C.6 Verb surface folded into ADR-0.0.66; no new top-level verb family

Exit gate: MOTD §8 criteria all observed live.

### Phase D — The Census

- [ ] D.1 Generate the completion census: every booked ADR × lifecycle × OBPI
      × REQ proof channel; every declared surface × wiring state; every live
      pool item × disposition state. Machine-derived from ledger + canon
      (Layer-3 view, regenerable, never hand-maintained); persisted under
      `.gzkit/work/` as the campaign burn-down the MOTD reads at login.
- [ ] D.2 Operator attests the census as the authoritative 1.0 scope.
      Census reconciliation includes the GHI #584 class (233 orphaned
      `obpi_created` ledger events with no on-disk briefs across 24 feature
      ADRs) — every orphan gets a disposition in the census.

Exit gate: census attested; MOTD login brief draws from it.

### Phase E — Booked-canon burn-down (waves)

Dependency-ordered waves over the ~30 booked ADRs short of Validated
(19 Draft + 10 Proposed + stragglers), via MOTD triage. Standing orders:

- [ ] E.1 **Canon Foundation ADRs booked** early in this phase; increments
      build through E/F.
- [ ] E.2 Wire the 6 manual-only validator scopes into a governed cadence
      (chore or check-tier); book origins for the 3 provenance-gap scopes.
- [ ] E.3 Burn Draft/Proposed foundation + pre-release ADRs wave by wave;
      each wave ends in a release (§ Cadence).

Exit gate: all booked ADRs Validated or operator-parked.

### Phase F — Canon Foundation build-out

- [ ] F.1 Complete the Canon Foundation increments to its ADRs' done-bar.

Exit gate: Canon Foundation ADRs terminal.

### Phase G — Pool processing

- [ ] G.0 Pool-machinery repairs first — the promote/demote/evaluate pipeline
      must be sound before 139 items flow through it: GHI #595 (evaluate gate
      errors on pool ADRs), #558 (demote `--on-collision keep-pool` stale
      frontmatter), #536 (promote Target Scope path:line refs).
- [ ] G.1 Every live pool item (139 at baseline; see Appendix B) enters the
      promotion pipeline in MOTD-triaged order (top-signal first).
- [ ] G.2 Terminal disposition per item: promoted → built → Validated, or
      parked/superseded on promotion-stage evidence with operator attestation.
- [ ] G.3 Pool-hygiene defects from the baseline ranking repaired in flight
      (status-drift on `obpi-req-taxonomy-scope-fence`, 11 missing `status:`
      frontmatter, 4 empty Intent sections).

Exit gate: pool index shows zero non-terminal items.

### Phase H — 1.0 declaration

- [ ] H.1 Census 100% terminal; goal-state checklist all true.
- [ ] H.2 v1.0.0 release through the patch-release ceremony.

### Phase I — The reduction pass (post-1.0; out of campaign scope)

Only now: re-run the validator load-bearing audit and pool/surface redundancy
analysis against the finished system; diff against the Appendix A/B baselines;
cull, merge, straighten with working proof speaking. Today's baselines are
inputs, never pre-1.0 action lists.

## GHI Register — all open issues, homed

> **Layer-3 derived view** — regenerated from `gh issue list --state open` at
> every triage pass; never hand-curate the counts. Snapshot 2026-06-10:
> **37 open**. Every open GHI is homed to a phase; an unhomed GHI is itself a
> defect.

| Home | GHIs | Theme |
|---|---|---|
| A (in-flight) | #538 | STRUCTURAL-FENCE parent-shape validator — the substance of OBPI-0.0.69-02 |
| B (CMS) | #519 (emergency), #533, #579, #580 | Codex 258K window; <15k registry-projected surface; imperative-density budget; criticality-ordered renderer |
| C (MOTD) | #585, #574 | Handoff retention → C.5 logrotation; advise-not-execute mechanization → C.4 |
| D (census) | #584 | 233 orphaned `obpi_created` events reconciled by the census |
| E (ceremony mechanization) | #516, #596, #573 | Passive-presenter REQ-evidence; BLOCKED-ADR advance; BI-2 classifier TDD redo |
| E (preflight/locks) | #578, #564 | Reaping-handoff coupling; orphan plan-audit receipts |
| E (task governance) | #563, #553, #561 | Task-envelope completion debt from ADR-0.22.0/0.0.64 |
| E (req-kind/covers hardening) | #537, #544, #545, #546, #547 | BEHAVIOR enforcement; grandfathering cache schema; ReqCoverageRecord; bypass-once; gray-zone doctrine |
| E (documents backfill) | #480, #524, #527 | Schema-convention backfill class (3,536 errors) |
| E (briefs/docs hygiene) | #565, #532, #551 | Shell-less Verification contract; manpage refs; REQ-coverage docs |
| E (quality/infra) | #571, #567, #575, #577, #581, #594, #582 | Test doctrine; skills spike pattern; `gz insights` verb; status projection; reconcile depth; arb retention; subprocess `errors=` class |
| G.0 (pool machinery) | #595, #558, #536 | Promote/demote/evaluate repairs gating pool flow |

## GHI emergence discipline (standing rules)

New GHI moments will keep emerging; the campaign absorbs them without
direction change:

1. **Route at the moment of emergence** per AGENTS.md § Defect-fix routing and
   the direct-fix moratorium: smallest honest fix lands now in one coherent
   commit (TDD, `Task:` trailer); a GHI is filed only when the fix genuinely
   cannot, via `/ghi-author` (never raw `gh issue create`).
2. **Homed at creation.** Every new GHI names its campaign-phase home (or
   "steady-state triage") in the issue body. Unhomed = defect.
3. **`emergency` label = campaign interrupt.** It preempts the current wave
   and the MOTD brief surfaces it at every login until closed (precedent:
   #519). Everything else waits its triaged turn — no five-alarm plan forks;
   the campaign is the fire plan.
4. **Triage at the release drumbeat** via `ghi-triage`; WIP = 1 for
   recovery-class items; closure only with observed command evidence
   (restore-health Phase-4 rule, retained).
5. **The register above is regenerated, never edited** — derived view
   doctrine applies to plans too.

## Cadence (the go-to-market rhythm)

- **Session**: login → MOTD briefing (until C ships: this checklist, top-down)
  → execute the topmost unblocked item via its governed path → logout
  continuity. Operator rules; the MOTD advises.
- **Handoffs are authored relative to the campaign**: a session-end handoff
  is continuity only — its next steps cite campaign item IDs and restate the
  topmost unchecked items; it carries an explicit subordination note that the
  campaign, not the handoff, governs what is pulled next. If handoff and
  campaign disagree, the campaign wins and the variance is reconciled into
  the campaign.
- **Release**: weekly drumbeat through the existing patch-release ceremony;
  every wave that lands capability ships in a named, attested release.
- **Triage**: GHI steady-state via `ghi-triage`; defects route per
  AGENTS.md § Defect-fix routing (direct-fix moratorium stands).
- **Concurrency**: two sessions ref-lock raced in this working directory on
  2026-06-10. Until the lock→branch migration (restore-health §13.7) lands,
  concurrent sessions coordinate via OBPI locks and avoid simultaneous pushes.

## Appendix A — Validator load-bearing baseline (2026-06-10)

Frozen evidence for Phase I. Method: per-scope mining of git history
(fix-commit subjects read and classified), ledger, insights, and wiring
(default set / gz-check / CI / pre-commit / skills / chores).

- 67 scopes total: 11 default, 56 explicit.
- **Proven load-bearing** (multiple recorded catches): defaults +
  `insights-shape`, `task-envelope-coherence`, `instructions-files-budget`,
  `bullet-retention`, `closeout-proof-binding`, `behave-req-tags`,
  `interviews`, `line-endings`, `distribution`, `complexity-thresholds`,
  `surface-fidelity`, `adr-status-fresh`, `doc-surface-parity`,
  `chores-layout`, `decomposition`, `commit-trailers`,
  `orientation-freshness`, `session-green-gate`.
- **Fences with no recorded intrusions** (wired, zero catches):
  `receipt-shape`, `agents-md-map-conformance`, `pointer-anchors`,
  `tautological-test-audit` (1), `unscoped-rules` (1).
- **Manual-only, ~zero fires** (now wired per Phase E.2 instead of retired):
  `router-tables`, `orphaned-implementation`, `brief-command-shape`,
  `brief-demo-section`, `brief-cross-references`, `scenario-reachability`.
- **Validator-was-the-defect cases** (maintenance tail): `req-kind-discipline`
  (GHI #541), `evaluation-justify-binding` (GHI #394), `kind-invariance`
  (GHI #483), `session-green-gate` (GHI #600).
- **Provenance gaps** (no commit ever names them): `advisor-proof-binding`,
  `intrinsic-attestation`, `pointer-anchors`.

## Appendix B — Pool ranking baseline (2026-06-10)

Frozen evidence for Phases G and I. Method: strict full-ID matching;
insights ×3, git ×3, docs cross-refs ×2, ledger ×1 (registration noise
excluded).

- Corpus: 164 pool ADRs on disk; 25 already dead (22 Superseded, 1 Promoted,
  1 archived, 1 supersession with frontmatter drift); **139 live**.
- Classification: live pool ≈ 59% product / 40% governance-meta / 2 unclear.
- Top signal: `airlineops-direct-governance-migration` (153; inflated by one
  parity checklist), `brief-authoring-evidence-checks` (104),
  `obpi-pipeline-dispatch-attestation` (99), `harness-trace-bundles` (91),
  `agentic-security-review` (85), `canonical-vs-runtime-separation` (85),
  `harness-aware-execution-modes` (84), `skill-behavioral-hardening` (71),
  `tdd-receipt-stream` (71), `workflow-specification` (71); then
  `execution-memory-graph` (65), `obpi-authoring-mechanical-floor` (58),
  `agent-execution-intelligence` (52), `adr-amendment-tracking` (49),
  `harness-lab` (48), `contract-surface-mechanical-defenses` (44),
  `solved-problem-pattern-corpus` (43), `session-productivity-metrics` (41),
  `universal-agent-onboarding` (39), `attestation-quality-measurement` (38).
- **24 zero-signal items** — all 10 airlineops/opsdev absorption ADRs among
  them, batch-demoted in commit `a95bba15` (GHI #520) and untouched since.
  The AirlineOps migrate-vs-absorb question is the largest single strategic
  block in the pool; Phase G forces its resolution.
- Signal theme: the corpus demands **proof mechanization** (evidence chains,
  trace bundles, TDD receipts), not new ceremony prose.
