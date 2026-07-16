# Summary — Pass D run 2026-07-16

First run of `control-surface-permission-consent-drift`. Baseline established.

## Counts

| Severity | Count |
|---|---|
| live (drift ledger) | **1** |
| neutralized | 0 |
| clean (no allow rule grants the prohibition) | 6 |
| **verified gaps invisible to the ledger** (`unwitnessable.md` UW-2) | **3** |

## The headline is not the zero

`consent-drift.md` reports **0 live rows**. That is *not* a clean surface. Three forbidden
actions are permitted right now and are invisible to the walk by construction:

| Prohibition | Permitted by | Named in the rule? |
|---|---|---|
| never create feature branches (`AGENTS.md:342`) | `Bash(git *)` | No |
| unittest over pytest (`AGENTS.md:94`) | `Bash(uv run *)` | No |
| never modify the ledger directly (`AGENTS.md:137`) | `Bash(sed:*)` | No |

The 0 is real: the concrete drift this chore was authored for (`Bash(python3:*)`, GHI #690)
was remediated in `d330b2de` / `cd75f6fd` / `6ecd29d8` before this first run. CF-1 through
CF-6 all report clean because that repair landed, not because nothing was ever wrong.

## Known coverage limits (restated verbatim per CHORE.md — required)

1. **Context-dependence — the hard ceiling.** Much of `AGENTS.md` forbids an action *in a context*: "never call `gh issue create` **outside this skill**" (Always #13), "never X directly", "never X without ceremony". Permission rules are context-free string matches. The sanctioned and forbidden invocations are byte-identical. `Bash(gh issue:*)` is **load-bearing, not drift**.
2. **Broad-rule blindness.** A drift row can only be raised against a rule that *mentions* the prohibited token. `Bash(git *)` permits `git checkout -b feature/foo` but contains no matching substring. Broad rules are the more dangerous class and this pass cannot see them.
3. **CI-blindness.** This chore is local-run only; its findings are not reproducible in CI. Never wire it to a CI gate.
4. **Curated-list drift.** The doctrine→pattern mapping is hand-maintained and can itself drift from `AGENTS.md`. Step 1 re-derives it each run rather than trusting the prior run's map.

## Routing list

**No `live` drift rows → no direct-fix GHI from this run.**

The 3 UW-2 gaps are **not** routed as drift GHIs. Each would require narrowing a broad allow
rule (`Bash(git *)`, `Bash(uv run *)`, `Bash(sed:*)`) — a real permission change with workflow
cost, and the operator ruled 2026-07-16 that broad allows are acceptable on a local dev box
where the hook chain, ledger, and Gate 5 are the actual enforcement. Recorded here as standing
known-gaps, not as defects awaiting a fix.

**Next run should check:** whether `.claude/settings.json` has accumulated allow rules (it had
0 this run — deny-only, by design: policy travels, convenience does not). Allow rules appearing
in the committed surface would be the first thing worth a second look.
