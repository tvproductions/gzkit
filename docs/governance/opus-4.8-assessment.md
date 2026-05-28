# gzkit — Model-Upgrade Assessment (Claude Opus 4.8)

**Date:** 2026-05-28
**Author:** ahuimanu (summary requested)
**Assessed by:** Claude Opus 4.8 (the model under evaluation — writing about itself)
**Trigger:** Release of Claude Opus 4.8; question of whether it improves gzkit.

---

## 1. Snapshot

- Repo: `tvproductions/gzkit` (created 2026-01-12, public, MIT, Python 3.13+).
- Issues: **557 total**, **28 open** — effectively all operator-authored.
- Cadence: ~557 GHIs in ~4.5 months, often in same-day clusters (#537–#547).
- Recurring labels: `defect`, `runtime`, `tech-debt`, `eval-feedback`.

## 2. What the issues actually say (root-cause categories)

| Category | Representative GHIs | Nature |
|---|---|---|
| Declared-but-never-wired | #545, #543, #544 | Schemas/records exist + are unit-tested but never instantiated in the real path; "proof" is regex, not a query. |
| Verification theater | #540, #562, #541, #539 | Demos hand-authored not executed; tautological tests; no-op string ops; extractor noise. |
| Unenforced doctrine | #537, #538, #556, #552, #551 | Invariants stated in ADRs/AGENTS.md with no `gz validate --<scope>` that fails CI on violation. |
| Runtime brittleness | #534, #550, #539 | UTF-8 / shell-less / heredoc assumptions break in the agent subprocess runtime. |
| ADR/OBPI lifecycle drift | #558, #557, #536, #549, #553 | Demote/promote leave stale state; renamed targets produce invalid paths. |

**Inference:** The dominant failure mode is *doctrine asserted but not promoted to
Mechanical* — exactly the gap the `agents.local.md` scorecard
("Mechanical / Promotable / Judgment / Ambiguous") is designed to close. This is
an enforcement-architecture problem, not a model-reasoning problem.

## 3. Can Opus 4.8 help? — an honest self-assessment

**Where it genuinely moves the needle:**
- **Long-context coherence.** The AGENTS.md + ADR + OBPI + local-rules chain is
  large and budget-pressured (#533, `--instructions-files-budget` GHI #373).
  More of that envelope is held reliably in one session, so fewer invariants are
  dropped mid-task — fewer self-inflicted GHIs.
- **Promotion velocity.** The work in §4.1 (turning Judgment-tier rules into
  `gz validate --<scope>` checks) is precisely the kind of mechanical, spec-bound
  authoring the model does well and fast. That backlog can be cleared materially
  quicker.
- **Multi-file lifecycle fixes.** Demote/promote stale-state bugs (#558, #557,
  #536) span CLI + ledger + projection; holding all three in one coherent patch
  is a strength.
- **Runtime discipline.** UTF-8 / shell-less / heredoc rules (#534, #550, #539,
  and the `agents.local.md` "never prefix PYTHONUTF8=1" rule) are followed more
  consistently.

**Where it will NOT help — and may make it worse:**
- **Un-promoted doctrine stays un-promoted.** No amount of capability makes an
  invariant safe; without a failing gate, any agent can still violate it.
- **Artifacts are generated faster.** Behind un-mechanized rules, a faster agent
  *fills the issue tracker faster*. Capability without gates raises GHI throughput
  in both directions.
- **Theater and dead schemas (#540, #545) are design gaps.** No model closes a
  gate that was never built; it will happily produce more code the same absent
  check fails to catch.
- **Judgment/ambiguity calls (#547 gray zones, #549 re-attestation) are the
  operator's.** Doctrine decisions aren't a capability the model should exercise
  unilaterally — the covenant explicitly reserves final judgment for the human.

**Self-verdict:** Adopt Opus 4.8 as an execution accelerator *after* the gates
exist. Pointed at un-gated doctrine, it yields faster motion in an unverified
direction — the exact thing gzkit was built to prevent.

## 4. Recommendations (priority order)

1. **Promote Judgment-tier rules to Mechanical (highest leverage).**
   For every "not mechanically enforced" GHI (#537, #538, #556, #552), add a
   `gz validate --<scope>` that fails CI, and catalogue it in the doctrine pages
   per the existing scorecard protocol. Treat any doctrine without a failing test
   as *not yet real*. This is the single change most likely to bend the 557 curve.

2. **Ban verification theater structurally.**
   - Execute brief `## Examples` against the claimed REQ rather than trusting prose (#540).
   - Add a tautology/no-op lint to the post-edit hook chain (#562, #541).
   - Make demo extraction execute, not transcribe (#539).

3. **Wire or delete declared schemas.**
   Audit every record "tested but never instantiated" (#545, #543, #544). Wire it
   into the production path or remove it — dead schemas read as coverage and lie.

4. **Harden the agent runtime contract once.**
   Consolidate UTF-8 + shell-less + heredoc handling (#534, #550, #539) so these
   stop recurring as separate GHIs.

5. **THEN bring in Opus 4.8 — as the burndown engine.**
   Pilot it specifically against the *now-gated* backlog. Measure
   GHIs-opened-per-session-day before vs. after. If a stronger model on un-gated
   doctrine raises that rate, that empirically confirms enforcement — not the
   model — is the binding constraint.

6. **Cap the discovery reflex.**
   Same-day batches of 8–11 GHIs (#537–#547) mean discovery is outpacing
   remediation. Add a WIP cap and a "no new doctrine without a gate" rule before
   filing more.

## 5. One line

> Opus 4.8 is a faster, more coherent executor — but gzkit leaks because its
> covenant is *asserted, not yet promoted to Mechanical*. Build the
> `gz validate --<scope>` gates first; then let Opus 4.8 sprint behind them. A
> smarter agent in front of missing gates just fills the tracker faster.
