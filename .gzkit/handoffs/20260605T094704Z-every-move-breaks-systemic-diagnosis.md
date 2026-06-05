---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-05T09:47:04Z"
agent: claude-code
obpi_id: OBPI-0.0.37-19
session_id: corpus-capture-2026-06-05
continues_from:
---

<!-- Handoff for ADR-0.0.37 — created by claude-code at 2026-06-05T09:47:04Z -->

## This handoff ADVISES next moves — it is NOT authorization to execute them

A resuming agent MUST present the advised steps to the operator and obtain explicit
authorization before executing any of them — no file mutation, no `gz` ceremony, no
deletion until the operator says go. This handoff hands off a **diagnosis**, not
in-flight work. You advise; the operator rules.

## The Short Answer — Why Every Move Breaks

Said plainly, the way it was said to the operator:

It is real and measurable, not a feeling. 30% of commits in the last 30 days (141 of 478)
are `fix(` — roughly five fix-commits a day, for weeks. That is the experience quantified.

The root cause is that **enforcement outgrew scaffolding, and gzkit breaks its own rule
inward.** There are 26 `gz check` gates, 78 validator scopes, 66 foundation ADRs — a
comprehensive *enforcement* surface. But the *generation* side is thin. gzkit's whole
doctrine is "single source of truth, derive views, no hand-maintained duplicates." Yet
adding one ledger event this session meant hand-syncing 6 parallel registries; adding one
CLI verb tripped 8 more hand-maintained lists. None is derived. So every primitive carries
a large manual blast radius, and you find the missing pieces **one gate-failure at a time.**
That serial discovery *is* the "everything breaks" feeling.

The deeper signal, and the real headline: **`main` is not green.** Two gates are red on
`main` right now and have been long enough that this session hit them by accident. When
`main` is chronically half-red, a new red alarms no one — so the gates have stopped
*preventing* and started just *taxing*. That is the actual disease.

The trap to avoid: the instinct is to fix this with more tooling — a code generator, a
smarter reconcile engine. That is answering a too-much-machinery problem with more
machinery, during a return-to-health emergency that forbids exactly that. **The cure is
subtraction.** Lead with deletions and one safe criterion: any gate red on `main` that
nobody is acting on is not protecting anything — fix it this week or retire it.

And the part owed honestly: completing OBPI-19 made the pile slightly *worse* — a new
event, command, skill, two waivers, a baseline regen. And a few stumbles this session were
execution, not architecture (a flag set then corrected, truncated receipt IDs, a wrong
skill category). The systemic share dominates, but it was not all the system.

## Current State Summary

OBPI-0.0.37-19 (corpus capture tool + skill, `gz content remember`) is **Completed** —
attested by g0, reconcile PASS, two git-syncs landed on `main`, lock released.
That work is done; nothing about it is in-flight.

The reason this handoff exists is the operator's standing question: **"why does nearly
every move break something — this has been constant for weeks."** That experience is real
and measurable. In the last 30 days: **141 of 478 commits (30%) are `fix(`** — roughly
five fix-commits a day. This session is a clean worked example of the cause, so the
diagnosis below is grounded in what was directly observed landing one small feature.

## Important Context

**The shape of the problem (systemic, not a quality problem).** Landing one small
feature — a single CLI subcommand plus a store plus a skill — required touching ~22 files
and clearing a serial cascade of fail-closed gates. The work was correct; it just cost
roughly 10x because coherence is achieved by manual labor plus gate-failure discovery,
not by construction.

**Root cause: enforcement has outgrown scaffolding, and gzkit violates its own doctrine
inward.** The governance surface is comprehensive on the enforcement side — 26 `gz check`
steps, 78 `gz validate` scopes, 66 foundation ADRs — but thin on the generation side.
gzkit's core doctrine is "single source of truth, derive Layer-3 views, no hand-maintained
duplicates, compose from a registry." Its own internals break that exact rule:

- Adding ONE ledger event requires hand-editing **6 parallel registries** that must stay in
  sync: the typed model in `src/gzkit/events.py`, the `TypedLedgerEvent` union, the factory
  in `src/gzkit/ledger_events.py`, the schema in `src/gzkit/schemas/ledger.json`, the
  `_NO_GRAPH_IMPACT` waiver, and the `_EVENT_MODELS` map in `tests/test_schemas.py`. None is
  derived. An omission in any one is invisible until a gate fails.
- Adding ONE CLI verb tripped a doc-coverage manifest, a skill manpage, a skill index, a
  router table, a distribution baseline, a `cli audit` triple, a subcommand fence, and a
  help-width check — each discovered one failure at a time (reactive triage).
- The brief itself pointed at a **dead schema file** (`.gzkit/schemas/ledger_events.json`,
  **0 consumers** in `src/`) and the wrong manpage path, and omitted 9 coupled surfaces —
  and `gz validate --brief-reconcile` (the CIC-2 "structural witness" meant to catch exactly
  this) **passed it clean**. The reconcile engine has a resolution gap: it does not know
  code-convention couplings.

**The headline finding: `main` is not green, and that is the whole story.** Two gates are
red on `main` and have been long enough that this session hit them by accident:
`gz validate --ledger` (out-of-enum `disposition` on committed `chore_decommission_processed`
events) and `gz check` step 23/26 Task-envelope-coherence (OBPI-0.0.37-26 closed seq=01-only
without `req_atomic`). When `main` is chronically half-red, a new red alarms no one — so the
gate system has lost its signal and shifted from preventing breakage to taxing every change.

**Honest mirror (two parts, both load-bearing):**
1. **This session made the pile slightly worse.** Completing OBPI-19 added a new event, a new
   command, a new skill, a security-surface touch, two new waivers, and a baseline regen. The
   coupling being diagnosed grew during the very act of diagnosing it. That is the recursion to
   watch: more surface is the disease, so the cure cannot be "more surface."
2. **Not all friction was the system.** A few stumbles were execution, not architecture: a
   doc-coverage `manpage` flag set true then corrected to false, truncated receipt IDs rejected
   by the binding gate, and a wrong skill `category` caught by `--surfaces`. The systemic share
   dominates, but the work was not blameless.

## Decisions Made

- **Decision:** Frame the cure as **subtraction-first**, not new tooling.
  **Rationale:** The operator has drowned for weeks in too much machinery; answering that with
  more machinery (codegen, more derivation layers, smarter validators) deepens the hole,
  especially under the return-to-health posture (#519) that forbids new foundation work.
  **Alternatives rejected:** "Build a `gz <primitive> new` generator that scaffolds all
  registrations" — correct in the abstract, but it is a 7th system supervising the other 6 and
  net-adds surface during a recovery.

- **Decision:** Adopt a single, safe subtraction criterion: **any gate currently red on `main`
  with no one acting on it is not protecting anything — fix it this week or retire it.**
  **Rationale:** This discriminates load-bearing gates from noise far better than "26 feels like
  a lot," and it strips no real protection.
  **Alternatives rejected:** A blanket "cut the gate count" target — risks removing gates that
  do earn their keep.

- **Decision:** Spawn **one** tracked follow-up at most, operator's call (the brief-reconcile
  code-coupling gap against the OBPI-0.0.37-05 reconcile engine).
  **Rationale:** Proliferating GHIs/ADRs is the disease; prescribing a slate of them as the
  treatment repeats it.
  **Alternatives rejected:** Filing GHIs for each of the three awareness items.

## Immediate Next Steps

ADVISORY ONLY — present these to the operator and wait for authorization. They are
deliberately small and subtraction-biased.

1. **Get `main` actually green before any new feature OBPI.** Fix-or-retire the two standing
   reds: the `chore_decommission_processed` `disposition` enum (`src/gzkit/schemas/ledger.json`
   vs the committed events — either widen the enum or correct the events via a governed path) and
   OBPI-0.0.37-26's missing `req_atomic`. Both are logged in `.gzkit/insights/agent-insights.jsonl`.
2. **Delete the dead `.gzkit/schemas/ledger_events.json`** (0 consumers in `src/`). One concrete
   redundant surface removed; confirm nothing reads it first (`grep -rl ledger_events.json src/`).
3. **Run the red-on-main-unattended test across the 26 gates / 78 validators** and produce a
   short retire-or-fix list. No new fail-closed gate lands during recovery without scaffolding
   that makes its coherence the default.
4. **Operator decides on one tracked follow-up:** the brief-reconcile resolution gap (CIC-2 /
   OBPI-0.0.37-05) — teach it the code-convention couplings (this event-kind needs these
   registries; this verb trips these gates) so the blast radius is front-loaded into the brief.
5. **Defer, do not start, the big subtraction:** collapsing the 6 event registries toward 1
   derived source. It is the right long-term move but it is new machinery; it waits until `main`
   is green and the recovery posture lifts.

## Pending Work / Open Loops

- Two pre-existing reds on `main` (ledger disposition enum; OBPI-0.0.37-26 task-envelope) — not
  introduced by OBPI-19, not fixable within it; insights logged.
- Security-floor override recorded to the ledger for operator review: OBPI-19's correction-A edit
  to `src/gzkit/ledger_events.py` (a registered `ledger_integrity` surface) triggered the floor
  because the project-wide security-scan toolchain is unlanded (GHI #462). Brief now carries
  `sensitivity: security`.
- The brief-reconcile code-coupling gap (the diagnosis's most leveraged single fix) — untracked
  until the operator rules on step 4.
- The 6-registry event-coupling collapse — deferred subtraction, named so it is not forgotten.

## Verification Checklist

- [ ] OBPI-19 is Completed and synced: `uv run gz obpi reconcile OBPI-0.0.37-19-corpus-capture-tool-skill`
- [ ] Branch and sync state: `git branch --show-current` (expect `main`), tree clean
- [ ] Reproduce the standing reds (confirm they are pre-existing, not new):
      `uv run gz validate --ledger` and `uv run gz validate --task-envelope-coherence`
- [ ] Confirm the dead schema file has no consumers before any deletion: `grep -rl ledger_events.json src/`
- [ ] Re-read the fix-commit ratio for trend: `git log --since='30 days ago' --oneline --grep='^fix(' | wc -l`

## Evidence / Artifacts

- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-19-corpus-capture-tool-skill.md` — the completed brief; its § Tracked Defects enumerates the 11 drift dimensions and the coupled-surface amendment
- `.gzkit/insights/agent-insights.jsonl` — the two pre-existing-red defect insights (ledger disposition enum; OBPI-26 task-envelope)
- `.gzkit/schemas/ledger_events.json` — the dead schema file (0 consumers in `src/`; deletion candidate, step 2)
- `src/gzkit/events.py`, `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json`, `src/gzkit/governance/trust_audits/events.py`, `tests/test_schemas.py` — the 6 hand-maintained event registries that must be synced per new event
- `src/gzkit/commands/content/remember.py`, `src/gzkit/content/corpus_store.py`, `.gzkit/skills/gz-content-remember/SKILL.md` — what OBPI-19 actually shipped

## Environment State

Python 3.13 / uv. `main` synced with `origin` (ahead=0 behind=0). Working tree clean at
handoff time. Return-to-health posture active (#519): no new foundation ADRs; subtraction
preferred over addition.
