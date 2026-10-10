# The chore board — advice for admission

> **What this is.** Row 3 of R&D run `renewing-vows` (`../renewing-vows.md`): "chore — advise
> only; the operator directs admission." Drafted 2026-10-10 on the operator's go ('go on row
> 3'), after the run's sign-off, which the operator's ruling of 2026-10-09 ('let's do chores
> after rnd') made the condition. It runs no chore and admits nothing. Measured with
> `uv run gz chores status --json` and `.gzkit/chores/registry.json` on 2026-10-10.

## The board as measured

| Band | Chores |
|---|---|
| overdue | 35 |
| unmeasured | 3 (the accumulated-work signal reads `unmeasured`, GHI #1009) |
| current | 2 |

By signal: 29 `content-delta`, 8 `elapsed-time`, 3 `accumulated-work`. By class: 24
conformance, 6 coherence, 4 mining, 3 curation, 2 currency. Thirty-three of the 35 overdue
last ran on or before 2026-08-09; three never ran.

**The signature.** A `content-delta` chore comes due whenever the content it watches changes.
In a repository that changes every session, that is every session, so an interval board
holding 29 of them reads "overdue" as its resting state and tells the operator nothing. The
operator named this on 2026-10-05 ('chore is level A-D airframe checks (still mx)'): the
distinction the board lacks is between a check flown before every flight and a task done at
a visit.

## Advice 1 — take the per-flight checks off the board

A content-delta chore whose check already runs in `gz check` on every change is a
per-flight check, and its board entry is a second clock on the same thing. For these, the
chore's last-run should derive from the gate step's receipt (`chore-class-system.md`
§ Derive last-run from the artifact), which makes the board read `current` whenever the gate
is green and removes the entry from the overdue count without running anything by hand.

| Chore | Per-change twin in `gz check` | Advice |
|---|---|---|
| `quality-check` | the gate itself | derive; the chore is the gate's name on the board |
| `ledger-vocabulary-inertness` | step "Ledger vocabulary inertness" | derive |
| `control-surface-validator-reachability` | step "Validator reachability" | derive |
| `module-sloc-cap-radon` | step "Module size" | derive |
| `complexity-reduction-xenon` | pre-commit xenon; step "Complexity-thresholds" | derive |
| `hardcoded-root-eradication` | step "Wheel path literals" | derive, if the chore's scope is the delivered surfaces; else keep |
| `skill-authoring-quality` | step "Skill audit" | derive |
| `skill-command-doc-parity` | step "Parity check" | derive |
| `test-manpage-examples`, `doc-coverage` | step "CLI audit"; "Docs build" | derive where the chore's check is the step's; keep the remainder |
| `frontmatter-ledger-coherence` | `gz validate --frontmatter` (default scopes) | derive |
| `config-paths-remediation` | step "Config registry"; `gz check-config-paths` | derive |
| `cli-contract-governance` | step "CLI audit"; `--cli-alignment` | derive |
| `control-surface-rule-vs-check-drift` | step "Advisory scorecard coverage" | derive |
| `coverage-40pct` | the unit tier's coverage floor | derive |

Fourteen entries. The derivation is a registry change per chore (its `staleness` reads the
gate receipt), and the chore body stays for the remainder the step does not cover. This is
the "sort per-flight conformance checks off the interval board into `gz check`" of the
disposition map, made concrete.

## Advice 2 — package what remains into named visits

What remains is work done at a visit, not before every flight. Under the rhythm ratified
2026-10-10, a visit is a scheduled work package (FAA AC 120-16G § 6-1) that comes due on the
board's announcement; "letter check" is the operator's own name for it and is used here as
the operator's label, not as a term with a source.

| Visit | Chores | Why together | Due |
|---|---|---|---|
| **A — the light check** (curation and currency) | `instructions-files-diet`, `pool-triage`, `memory-hygiene`, `dependency-currency`, `frontier-model-card-currency`, `ghi-cross-reference-staleness` | each reads a surface that grows between republishes and feeds the republish | **now**: `AGENTS.md` is 25,473 chars against a 20,000 budget (advisory until 1.0); the pool holds 224 entries after this run's five; the republish signal has fired |
| **B — the debt check** | `decommission-tautological-tests` | the one chore with a date: the debt ceiling steps to 222 on 2026-10-14 UTC and the check breaches then unless ops are retired (debt 223 on 2026-10-07) | **before 2026-10-14** |
| **C — the mining visit** | `arb-pattern-extraction`, `eval-feedback-cluster`, `failure-class-index`, `session-correction-mining` | all four read the ledger and the insights for patterns; each is propose-rung and writes a report, not a fix; last run 2026-07-31 or never | on the elapsed-time signal, all overdue |
| **D — the conformance sweep** | `pythonic-refactoring`, `pythonic-design-pattern-detection` then `-application`, `exceptions-and-logging-rationalization`, `pep257-docstring-compliance`, `test-isolation-compliance`, `cross-platform-test-cleanup`, `test-consolidation-subtest-sweep`, `repository-structure-normalization`, `evidence-integrity-audit` | repair-rung code hygiene with no per-change twin; share one setup (a green tree, the complexity and test tooling) | on content-delta; packaged so they run once per visit, not per change |
| **E — control-surface coherence** | `control-surface-rule-conflicts`, `control-surface-skill-rule-reachability`, `control-surface-permission-consent-drift`, `skill-trigger-testing` | project-local coherence reads over the same surfaces; two are operator-only-repair | on content-delta of the control surfaces |

Visits A and B are due now by their own signals; C, D and E are overdue only because the
board's clock is wrong for them (Advice 1) or because nothing announced them (Advice 3).

## Advice 3 — the two announcements, for admission to the estate

Ruled 2026-10-07 ('Two slower tiers, signal-triggered'); both announce and gate nothing.

1. **Republish due.** Signal: the count of dated amendments on the active campaign edition
   (47 today). Where it lives: a line in the session orientation hook's output, and an
   advisory `gz validate` scope that reports the count against a threshold the operator
   sets in data, not prose. What it announces: "a new edition is due; the fold carries or
   withdraws every ruling explicitly." The edition is the operator's to cut.
2. **Maintenance visit due.** Signal: a visit's chores past their band on the board.
   Where it lives: the same orientation line, naming the visit (A to E) rather than 35
   slugs. What it announces: "visit A is due" and nothing more. Admission is the operator's.

Both are chores of class `coherence`, rung `propose`, with the board as their artifact;
they are candidates for the registry, not entries in it.

## What this advice does not do

It admits nothing: the operator directs admission (`chore-class-system.md` § Consultation
points, the in-the-loop point). It changes no registry entry. It does not make a chore run a
ledger event; that is `ADR-pool.maintenance-record-entry` (row 1). The accumulated-work
signal stays `unmeasured` until GHI #1009 lands, so visit A's `pool-triage` and
`instructions-files-diet` are due by their own numbers above, not by the board.
