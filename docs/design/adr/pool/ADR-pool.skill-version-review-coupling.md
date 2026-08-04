---
id: ADR-pool.skill-version-review-coupling
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.skill-version-review-coupling: Skill-Version / last_reviewed Coupling Validator

## Status

Pool

## Intent

Promote rule #6 of `.gzkit/rules/skill-surface-sync.md` from doctrine-only to
mechanically enforced.

Commit `ab9e33c6` (2026-05-18) bumped `skill-surface-sync.md` to v0.8.0 and
added non-negotiable rule #6:

> **`skill-version` bumps require `last_reviewed` bumps in the same edit
> (skills only).** Any commit that increments `skill-version:` in a skill's
> frontmatter MUST also set `last_reviewed:` to today's date (YYYY-MM-DD). …
> Decoupling the two fields produces fresh code with stale review metadata,
> which silently disables the staleness signal.

The rule is binding but carries **no mechanical backstop**. Nothing in the
validator pipeline checks the coupling: `src/gzkit/skills_audit.py:259-287`
(`_validate_last_reviewed`) and the duplicate path at
`src/gzkit/sync_skill_validation.py:109-125` (`_append_last_reviewed_issues`)
read `last_reviewed` only to enforce the 90-day staleness window
(`DEFAULT_MAX_REVIEW_AGE_DAYS = 90`) — they validate the field in isolation,
never against the surrounding commit's `skill-version` delta.

Per `docs/governance/advisory-rules-audit.md`, an authored binding rule with
no mechanical enforcement path is a **Promotable-class** rule whose promotion
to **Mechanical** is the canonical next step. This ADR is the design home for
that promotion.

**Class of failure addressed:** any skill edit where the author bumps
`skill-version` (because the content changed) but forgets to bump
`last_reviewed` (because the field is procedural muscle memory). The 90-day
staleness audit then runs against a stale date the author never re-asserted —
the staleness signal is defeated by *drift*, not by overt suppression. This is
the exact failure mode rule #6 was authored to prevent; absent mechanical
enforcement the rule degrades to advisory within one or two distracted
commits. GHI #492's own evidence section names three sibling skills patched in
the rule's authoring session (`gz-adr-create` 6.4.1, `gz-adr-promote` 1.4.1,
`gz-plan` 1.3.1) that the proposed validator would have caught had any one of
them decoupled.

## Decision

Author a validator scope — `uv run gz validate --skill-version-review-coupling`
(flag name to be finalized at promotion) — that, given the parent-commit diff,
**refuses to land any skill `SKILL.md` whose `skill-version` differs from the
parent commit's value but whose `last_reviewed` does not also advance to the
commit date.** Wire it into the default `uv run gz check` pipeline so the rule
fails-closed at commit/PR time rather than at human review.

Routing facts carried forward to the promotion's plan/OBPI (advisory, from
GHI #492's scope hint):

- **Estimated diff:** ≤100 lines — new validator function + flag wiring + test
  fixtures.
- **Surfaces touched:** `src/gzkit/skills_audit.py` (natural insertion point,
  alongside `_validate_last_reviewed`), `src/gzkit/cli.py` (flag
  registration), the validator dispatcher, `tests/test_skills_audit.py`.
- **Lane:** heavy — adds a CLI surface (`gz validate` flag) and a
  runtime-contract validator wired into `gz check`.

## Alternatives Considered

1. **Leave rule #6 doctrine-only.** Rejected: an authored binding rule with no
   mechanical witness degrades to advisory within one or two distracted
   commits (advisory-rules-audit Promotable-class definition). The staleness
   signal is defeated by drift the system never sees.
2. **Pre-commit hook only, not a `gz validate` scope.** Rejected: a hook is
   bypassable with `--no-verify`, is not part of the auditable `gz check`
   pipeline, and is inconsistent with how every other Promotable→Mechanical
   promotion has landed (each appears as a `gz validate --<scope>` entry in
   CLAUDE.md § Mechanical scopes).
3. **Fold the check into the existing staleness validator
   (`_validate_last_reviewed`).** Rejected as the *primary* mechanism: the
   staleness check validates `last_reviewed` in isolation against a 90-day
   window and needs no commit context; the coupling check validates
   `last_reviewed` against the surrounding commit's `skill-version` delta and
   requires the parent-commit diff. Different inputs, different trigger. They
   compose but are distinct scopes — conflating them obscures both.
4. **Promote straight to a foundation ADR with no pool stop.** Rejected at
   routing time (GHI #492 close, 2026-05-22): the pool ADR is the
   design-conversation home; promotion to foundation via `gz-adr-promote`
   carries the foundation-tier ceremony (evaluation scorecard, gate covenant)
   at the right time, not retroactively under a closing GHI.

## ADR Relationships

- **`ADR-0.0.52-artifact-staleness-propagation`** — its Intent explicitly
  cites "the `last_reviewed` ↔ skill-version coupling handles the rule level"
  as an assumed-true tier, distinct from the artifact-graph tier 0.0.52 owns.
  GHI #492 reveals that premise is currently **false** (the coupling is
  doctrine-only). This ADR's promotion *makes ADR-0.0.52's three-tier framing
  true* — it is the missing rule-tier mechanical witness, not an increment of
  0.0.52's graph-tier scope.

  > **Correction (2026-08-04, GHI #691).** This ADR's promotion is **necessary
  > but not sufficient** for 0.0.52's three-tier framing. The premise is false
  > twice over: beyond the coupling being doctrine-only, `last_reviewed` does
  > not exist on `.gzkit/rules/**` at all — it governs *skills*, and this
  > ADR's scope is the skill-side edit-time coupling. The rule-surface calendar
  > clock is homed at **`ADR-pool.rule-surface-aging-clock`**; 0.0.52's framing
  > becomes true only when both promote.
- **`ADR-pool.rule-surface-aging-clock`** — sibling, not parent. It adds the
  rule-surface *calendar* clock (does a rule get re-read every 90 days); this
  ADR adds the skill-surface *edit-time* coupling (does a `skill-version` bump
  carry a `last_reviewed` bump). Different surface, different trigger — the
  boundary § Notes already draws against GHI #503's calendar class. **Both edit
  `skill-surface-sync.md` § #6 from opposite directions** — this ADR promotes
  its coupling clause, that one retires its *"skills only"* carve-out. Per
  Invariant 1a, whichever promotes second reconciles against the first's edit.
- **`docs/governance/advisory-rules-audit.md`** — the Promotable→Mechanical
  scorecard pattern this ADR instantiates; the promotion should add the new
  scope to the audit catalogue and to CLAUDE.md § Mechanical scopes.

## Notes — sequencing dependencies (advisory, for the promotion's plan)

- **GHI #493** surfaced that `src/gzkit/skills_audit.py:259-287` and
  `src/gzkit/sync_skill_validation.py:109-125` duplicate the
  `last_reviewed`-validation logic. The coupling validator lands more cleanly
  atop a consolidated validator path; the promotion's plan should sequence the
  #493 option-2 consolidation ahead of, or bundle it with, this scope.
- **GHI #503** is the calendar-staleness *wave* this rule's 90-day audit
  produced — 10 skills sharing `last_reviewed: 2026-02-18` all crossed the
  threshold on the 2026-05-20 tick. #492 (this ADR) enforces the coupling at
  *edit* time; #503 is the symptom when no edit happens for 90 days. A
  scheduled review-cadence / early-warning surface addresses the time-bomb
  class this edit-time validator alone cannot. Treat that as adjacent scope,
  not a blocker for this ADR.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
