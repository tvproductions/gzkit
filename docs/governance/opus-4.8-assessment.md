# gzkit — Model-Upgrade Assessment (Claude Opus 4.8)

**Date:** 2026-05-28
**Author:** ahuimanu (summary requested)
**Assessed by:** Claude Opus 4.8 (the model under evaluation — writing about itself)
**Trigger:** Release of Claude Opus 4.8; question of whether it improves gzkit.

> **Operator framing (2026-05-28, verbatim — do not soften):** *"GzKit is sick
> and in poor health. I hope Opus 4.8 can save the day."* This revision folds in
> the two durable emergency records the operator pointed at: the **5-alarm fire**
> (GHI [#517](https://github.com/tvproductions/gzkit/issues/517)) and the
> **get-out-of-jail recovery plan**
> (`docs/governance/get-out-of-jail-plan-2026-05-23.md`). Read §1.5 before §3 —
> the prognosis only makes sense against the diagnosis.

---

## 1. Snapshot

- Repo: `tvproductions/gzkit` (created 2026-01-12, public, MIT, Python 3.13+).
- Issues: **557 total**, **28 open** — effectively all operator-authored.
- Cadence: ~557 GHIs in ~4.5 months, often in same-day clusters (#537–#547).
- Recurring labels: `defect`, `runtime`, `tech-debt`, `eval-feedback`, `emergency`.

## 1.5 The 5-alarm fire and the get-out-of-jail plan (the binding context)

Two operator-authored documents define the health emergency this assessment
answers. They are not background — they are the diagnosis and the prescription.

### The 5-alarm fire — GHI #517 (`emergency`)

> *"adr authoring, obpi authoring, adr authoring evaluation, obpi execution, adr
> closeout, and adr audit are the HEART AND SOUL of gzkit. If any of these are
> shitty, then GZKIT is shitty. … This is a 5-alarm fire."*
> *"5 ALARM FIRE! THE DEGRADATION CANNOT BE OVERSTATED."*
> *"Det her er et klovneshow!"*

A single ADR-0.0.57 closeout walkthrough surfaced **five distinct structural
defects in the ceremony surface** — the work was sound, the *validation machine
used to close it was not*:

| # | Failure | Root cause |
|---|---|---|
| 1 | Demo-anchor drift — 3 of 5 doctrine-read demos produced empty output | No preflight validating brief-authored demo commands yield non-empty output; zero fail-close. |
| 2 | GHI #427's "fix" did not structurally land | A unit test ran as a product demo; the "fix" was prose in a SKILL.md, **not a mechanical filter** in `ceremony_data.py`. |
| 3 | Multi-line command fragment-split | `ceremony_data.py` split a heredoc on newlines; 5 unrunnable fragments presented as 5 demos. |
| 4 | Substantive REQ failure passed the REQ-coverage gate | An **AND-clause REQ passed coverage with only one conjunct satisfied** (ADR-0.0.25 gate has no AND-clause semantics). |
| 5 | Gate 5 bypass via `--next` | `--next` advanced past Step 6 ATTESTATION; `attestation: None` in final state. Gate 5 has no enforcement teeth in the ceremony state machine. |

**The existential claim of #517:** ceremony correctness is enforced by *prose in
SKILL.md files* (Layer 1 authored text), with **no Layer 2 runtime enforcement**
and the **operator as the verification layer**. One pillar (`gz-obpi-pipeline`)
is built correctly with staged mechanical gates; the other five are unaudited
against that standard. If they share the closeout class-of-failure, gzkit "is
providing a governance-branded wrapper around unverified agent output. That is
worse than no governance at all — it creates false confidence." GHI #517 closed
`not_planned` (superseded), routing remediation into pool ADRs.

### The get-out-of-jail plan (recovery, 2026-05-23)

Written the day #517, GHI #519 (Codex 258K window collapse), and the
model-regression deep-dive all landed. Its thesis: **the bottleneck is promotion
velocity, not insight — gzkit's best ideas already sit in
`docs/design/adr/pool/`; move five of them to shipped.** Posture: *"Sobriety. No
new doctrine. No new foundation ADRs. No three-model review."*

**Definition of "out of jail" (all seven must hold):** root `AGENTS.md` ≤ 5 KB
router; `gz context <ADR-ID>` exists; a namespace-router skill layer exists; ≥ 4
skills declare `inputs:`/`outputs:` validated by `gz validate --skill-contracts`;
closeout reads structured `REQ → Evidence` from a `CeremonyStore` port; ≥ 50 of
61 Validated ADRs harvested to `Completed`; a normal session carries an ADR
plan→implement→verify→closeout within a 200K budget.

| Move | Days | Action | Cites prior art |
|---|---|---|---|
| Prequel (Day 0) | — | Demote the 25-deep `0.27.0`–`0.51.0` `Pending` feature queue to pool; build `gz adr demote` | GHI #520 / #521 |
| Move 1 | 1–2 | Promote the namespace router (six router skills) | `ADR-pool.namespace-router-product-surface` |
| Move 2 | 3–5 | Ship `gz context <ADR-ID>` focused-context loader | `ADR-pool.focused-context-loader` |
| Move 3 | 6–8 | Shrink AGENTS.md to ≤ 5 KB router boot manifest | `ADR-0.0.54-agents-md-map-not-encyclopedia` |
| Move 4 | 9–11 | Typed skill contracts (`inputs:`/`outputs:` + `--skill-contracts`) | `ADR-pool.intent-stage-skill-composition` |
| Move 5 | 12–14 | Closeout ceremony on the hexagonal spine (`CeremonyStore` + `ReqEvidence`) | `ADR-0.0.3-hexagonal-architecture-tune-up` |
| Move 6 | inserted 2026-05-25 | Categorical test-shape doctrine (~3,404 filesystem-shaped ops / 32% of the tree) | GHI #531 → `ADR-0.0.59` |

The plan's single sentence to remember: *"gzkit's best ideas are already in
`docs/design/adr/pool/`. Move five of them to shipped … and you have GSD's
footing on your own foundation. Stop authoring new ones until those five ship."*

## 2. What the issues actually say (root-cause categories)

| Category | Representative GHIs | Nature |
|---|---|---|
| Declared-but-never-wired | #545, #543, #544 | Schemas/records exist + are unit-tested but never instantiated in the real path; "proof" is regex, not a query. |
| Verification theater | #540, #562, #541, #539, **#517** | Demos hand-authored not executed; tautological tests; no-op string ops; extractor noise. **#517 is the canonical case: 5 such failures in one ceremony.** |
| Unenforced doctrine | #537, #538, #556, #552, #551 | Invariants stated in ADRs/AGENTS.md with no `gz validate --<scope>` that fails CI on violation. |
| Runtime brittleness | #534, #550, #539 | UTF-8 / shell-less / heredoc assumptions break in the agent subprocess runtime. |
| ADR/OBPI lifecycle drift | #558, #557, #536, #549, #553, **#520** | Demote/promote leave stale state; renamed targets produce invalid paths; **a 25-deep `Pending` feature queue blocked the recovery semver.** |

**Inference:** The dominant failure mode is *doctrine asserted but not promoted to
Mechanical* — exactly the gap the `agents.local.md` scorecard
("Mechanical / Promotable / Judgment / Ambiguous") is designed to close, and
exactly what the 5-alarm fire proved with five concrete failures and the
get-out-of-jail plan proposes to close with five mechanical moves. This is an
enforcement-architecture problem, not a model-reasoning problem.

## 3. Can Opus 4.8 help? — an honest self-assessment

**Where it genuinely moves the needle:**
- **Long-context coherence.** The AGENTS.md + ADR + OBPI + local-rules chain is
  large and budget-pressured (#533, `--instructions-files-budget` GHI #373; GHI
  #519's Codex 258K window collapse is the failure mode). More of that envelope
  is held reliably in one session, so fewer invariants are dropped mid-task —
  fewer self-inflicted GHIs. This directly serves the recovery plan's seventh
  exit criterion (a full plan→closeout cycle inside a 200K budget).
- **Promotion velocity — the recovery plan's named bottleneck.** Moves 1–5 are
  *"move what's already authored from pool to shipped,"* and §4.1 (turning
  Judgment-tier rules into `gz validate --<scope>` checks) is precisely the
  mechanical, spec-bound authoring the model does well and fast. This is the
  single capability most aligned with "out of jail."
- **Multi-file lifecycle fixes.** Demote/promote stale-state bugs (#558, #557,
  #536) and the Day-0 prequel sweep (#520/#521) span CLI + ledger + projection;
  holding all three in one coherent patch is a strength.
- **Runtime discipline.** UTF-8 / shell-less / heredoc rules (#534, #550, #539,
  and the `agents.local.md` "never prefix PYTHONUTF8=1" rule) are followed more
  consistently — the same brittleness class behind #517 Failure 3 (heredoc
  fragment-split).

**Where it will NOT help — and may make it worse:**
- **Un-promoted doctrine stays un-promoted.** No amount of capability makes an
  invariant safe; without a failing gate, any agent can still violate it. #517
  Failure 2 is the proof: GHI #427's prose-level "fix" did not land because it
  was never mechanized. A smarter model writing better prose changes nothing.
- **Artifacts are generated faster.** Behind un-mechanized rules, a faster agent
  *fills the issue tracker faster* — the recovery plan's anti-temptation
  tripwires (no new foundation ADRs, no new doctrine pages, WIP discipline) exist
  precisely to stop a capable agent from accelerating discovery past remediation.
- **Theater and dead schemas (#540, #545, and all five #517 failures) are design
  gaps.** No model closes a gate that was never built; it will happily produce
  more code the same absent check fails to catch. #517 Failure 4 (AND-clause REQ
  passing coverage) is a missing semantic in the gate, not a model deficiency.
- **Judgment/ambiguity calls are the operator's.** #517 explicitly reserves
  cross-analyst tie-breaking and pool-ADR routing for the human; #547 gray zones
  and #549 re-attestation are doctrine decisions the model must not exercise
  unilaterally. The covenant reserves final judgment for the human.

**Self-verdict:** Adopt Opus 4.8 as an execution accelerator *after* the gates
exist — i.e., **as the burndown engine for the get-out-of-jail moves, not as a
substitute for them.** Pointed at un-gated doctrine, it yields faster motion in
an unverified direction — the exact thing the 5-alarm fire showed gzkit already
does to itself, and the exact thing gzkit was built to prevent. Opus 4.8 does not
"save the day"; it sprints the recovery plan once the spine is laid.

## 4. Recommendations (priority order)

> These map onto the get-out-of-jail moves. Where a recommendation advances a
> specific move, it is named.

1. **Lay the mechanical spine first — execute the get-out-of-jail moves.**
   Moves 1–5 (router → context loader → AGENTS.md shrink → typed skill contracts
   → closeout-on-spine) are the load-bearing remediation. Move 5 specifically
   answers all five #517 failures: structured `ReqEvidence` instead of extracted
   shell, `--next` blocked at the Gate 5 boundary, AND-clause REQs rejected at
   brief-authoring time. Do not skip the spine to chase model velocity.

2. **Promote Judgment-tier rules to Mechanical (highest leverage).**
   For every "not mechanically enforced" GHI (#537, #538, #556, #552), add a
   `gz validate --<scope>` that fails CI, and catalogue it per the existing
   scorecard protocol. Treat any doctrine without a failing test as *not yet
   real* — the literal lesson of #517 Failure 2.

3. **Ban verification theater structurally (close the #517 class).**
   - Execute brief `## Examples`/`## Demo` against the claimed REQ rather than
     trusting prose (#540; #517 Failures 1 & 3).
   - Give the REQ-coverage gate AND-clause semantics (#517 Failure 4).
   - Add Gate 5 enforcement teeth to the ceremony state machine — `--next` must
     not bypass attestation (#517 Failure 5).
   - Add a tautology/no-op lint to the post-edit hook chain (#562, #541); make
     demo extraction execute, not transcribe (#539); land Move 6 / ADR-0.0.59 to
     retire the ~3,404 filesystem-shaped test operations.

4. **Wire or delete declared schemas.**
   Audit every record "tested but never instantiated" (#545, #543, #544). Wire it
   into the production path or remove it — dead schemas read as coverage and lie.

5. **Harden the agent runtime contract once.**
   Consolidate UTF-8 + shell-less + heredoc handling (#534, #550, #539) so these
   stop recurring as separate GHIs — the substrate behind #517 Failure 3.

6. **THEN bring in Opus 4.8 — as the burndown engine.**
   Pilot it specifically against the *now-gated* backlog once Moves 1–5 close.
   Measure GHIs-opened-per-session-day before vs. after. If a stronger model on
   un-gated doctrine raises that rate, that empirically confirms enforcement —
   not the model — is the binding constraint.

7. **Cap the discovery reflex (honor the recovery tripwires).**
   Same-day batches of 8–11 GHIs (#537–#547) mean discovery is outpacing
   remediation. The get-out-of-jail plan already bans new foundation ADRs, new
   doctrine pages, and "fix X while we're here" mid-recovery. Add a WIP cap and a
   "no new doctrine without a gate" rule before filing more.

## 5. One line

> Opus 4.8 is a faster, more coherent executor — but gzkit is sick because its
> covenant is *asserted, not yet promoted to Mechanical*: the 5-alarm fire (GHI
> #517) proved it with five failures in a single ceremony. Execute the
> get-out-of-jail spine first (router, context-loader, skill-contracts,
> closeout-on-spine, test-shape doctrine); **then** let Opus 4.8 sprint behind
> the gates. A smarter agent in front of missing gates just fills the tracker
> faster — and the model cannot save the day the recovery plan was written to win.
