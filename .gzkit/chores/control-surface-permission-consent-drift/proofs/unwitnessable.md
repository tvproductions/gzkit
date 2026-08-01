# Unwitnessable Ledger — Pass D run 2026-08-01

**Read this before reading `consent-drift.md`.** That ledger reported **6 live rows**. This
artifact is why 6 is a floor, not a measurement.

Required by `acceptance.json` and CHORE.md § Acceptance Criteria: a run producing a drift
ledger without this file fails its own criteria (GHI #690). CHORE.md § Workflow step 4 states
the reason plainly — *"This artifact is the point of the chore as much as the drift ledger."*

## UW-1 — Context-dependent prohibitions (4 of 14 command-shaped rules)

The drift walk covers only prohibitions where a forbidden command is forbidden
*unconditionally*. Where doctrine forbids an action **in a context**, no permission rule can
express it: the sanctioned and forbidden invocations are byte-identical strings, and the
permission matcher sees a flat string with no caller context.

| ID | Citation | Verbatim | Why invisible |
|---|---|---|---|
| CD-1 | `AGENTS.md:127` § Always #13; `.gzkit/rules/gh-cli.md:26-30` | *"Author GHIs through `/ghi-author` — never call `gh issue create` directly"* | The rule itself declares the unwitnessability at `gh-cli.md:30`: *"The prohibition is on the **caller**, not the string: `/ghi-author` itself invokes `gh issue create` at `SKILL.md:199` as its own final step … Nothing mechanical can tell them apart — the discipline is yours to keep."* `Bash(gh issue:*)` is **load-bearing, not drift** — denying it breaks the only sanctioned path for filing a GHI. Canonical false positive: the Pass D prototype flagged exactly this rule and was wrong. |
| CD-2 | `AGENTS.md:142` § Never #6 | *"Do not work around hook blocks."* | "Working around" is an intent. No token distinguishes a legitimate retry from a workaround. |
| CD-3 | `AGENTS.md:62` § SKILLS FIRST | *"Matching skill first. No convenience exception."* | The same command is sanctioned or forbidden depending on whether a skill covers the task. Context, not string. |
| CD-4 | `AGENTS.md:38` § PRIME DIRECTIVE 6 | *"file a GHI via `/ghi-author` (never `gh issue create` directly …)"* | Second citation site for CD-1's string. Recorded so a future run does not mistake the duplicate for an unmapped rule. |

**Four in fourteen command-shaped prohibitions are structurally invisible to this pass.** This
is a ceiling, not a backlog item — it does not shrink with better patterns.

## UW-2 — Broad-rule blindness (re-verified this run, not carried forward)

A drift row can only be raised against an allow rule that *names* the prohibited token or
whose glob *contains* the prohibited path. A broad rule permits the same forbidden action
while naming nothing. Each row below was re-tested this run by asking whether the rule permits
the concrete command (never by substring match against the rule text):

| Prohibition | Forbidden command | Permitted by | Named in the rule? | New this run? |
|---|---|---|---|---|
| CF-6 — `AGENTS.md:344`, operator canon *"never create feature branches"* | `git checkout -b feature/foo` | `Bash(git *)` | **No** | no |
| CF-3 — `AGENTS.md:94` § STDLIB-FIRST, *"`unittest` over pytest"* | `uv run pytest tests/` | `Bash(uv run *)` | **No** | no |
| CF-5 — `AGENTS.md:137` § Never #2, *"NEVER: Modify the ledger directly"* | `sed -i '' 's/x/y/' .gzkit/ledger.jsonl` | `Bash(sed:*)` | **No** | no |
| CF-5 — same | `perl -i -pe 's/x/y/' .gzkit/ledger.jsonl` | `Bash(perl -i -pe ' *)` | **No** | **YES** — second shell writer reaching the ledger; the wildcard follows the opening quote, so every in-place perl program is granted |
| CF-10 — `AGENTS.md:125` § Always #11, *"never hand-append the jsonl"* | `sed -i '' '$a\{...}' .gzkit/insights/agent-insights.jsonl` | `Bash(sed:*)`, `Bash(perl -i -pe ' *)` | **No** | **YES** — CF-10 was not mapped before |
| CF-7 — `.gzkit/rules/skill-surface-sync.md:30`, *"Never edit vendor mirrors directly"* | `sed -i '' 's/x/y/' .claude/skills/gz-check/SKILL.md` | `Bash(sed:*)`, `Bash(perl -i -pe ' *)` | **No** | **YES** — the `Edit(...)` path to `.claude/**` is closed (no glob reaches it); the shell reopens it |
| CF-8 — `.gzkit/rules/skill-surface-sync.md:31`, *"Never edit `src/gzkit/<surface>/` directly"* | `sed -i '' 's/x/y/' src/gzkit/rules/tests.md` | `Bash(sed:*)`, `Bash(perl -i -pe ' *)` | **No** | **YES** — a second, unnamed path to the same surface `Edit(src/**)` reaches by containment (D-7) |
| CF-9 — `deprecations.py:41`, `gz gates` retired | `uv run gz gates --adr ADR-0.1.0` | `Bash(uv run *)` | **No** | **YES** |

All eight are **live** in the sense that matters — the action is permitted and no deny covers
it — yet none appears in `consent-drift.md`, because the ledger can only see rules that name
the token or contain the path. **The drift walk's 6 live rows and these 8 verified gaps
coexist.** That is the honest summary of this pass's coverage.

The sharpest structural fact, unchanged from the prior run and now confirmed on four more
prohibitions: **permission surfaces are per-tool; these prohibitions are per-artifact.** The
`Edit(...)` grants correctly do not reach `.gzkit/ledger.jsonl`, `.gzkit/insights/`, or
`.claude/skills/` — and `Bash(sed:*)` plus `Bash(perl -i -pe ' *)` reopen every one of them
through the shell. Closing the file-tool path without closing the shell path closes nothing.

### Probe hygiene note (carried forward, still binding)

The prior run's loose probe (substring match on rule prefixes) reported 18 rules permitting a
ledger write; re-testing each rule against the actual command reduced that to 1. This run
applied the command-permission test from the start and found 2 (`sed`, `perl -i`). A future
run must test *permission of the command*, never *substring of the rule* — the loose form
manufactured false positives at ~18:1 here.

## UW-3 — CI-blindness (narrowed, not eliminated)

```
$ git check-ignore -v .claude/settings.local.json
.gitignore:54:.claude/settings.local.json	.claude/settings.local.json
```

This run walked **180 allow rules from `settings.local.json` and 0 from `settings.json`** —
every settings-surface allow rule audited exists only on one operator's machine. On a fresh
clone this pass sees an empty allow list and reports a clean surface, vacuously. **Never wire
this chore to a CI gate.** Its settings findings (D-1 … D-7) are not reproducible off the
authoring machine.

**Narrowed this run:** the extended `_PERMITTED_BASH` surface *is* committed
(`src/gzkit/handoff_resume_gate.py`, last commit `44f7aac2e` 2026-08-01), so D-8, D-9, U-1 and
U-2 are reproducible in any clone. That is a real asymmetry worth naming: the standing-consent
surface that ships with the wheel is auditable; the one that accretes from "always allow"
clicks is not. The chore's structural limit is a property of *where consent is stored*, not of
consent auditing as such.

## UW-4 — Curated-list drift (this run's near-miss, recorded)

`doctrine-map.md` was re-derived from `AGENTS.md` + `.gzkit/rules/**` this run rather than
loaded from the prior run, per CHORE.md § Known coverage limits #4. **That is not a formality
this time.** Four of the ten context-free prohibitions (CF-7, CF-8, CF-9, CF-10) were absent
from the 2026-07-16 map, and three of the six live drift rows trace to them. A run that
trusted the cached map would have re-reported "0 live" against an unchanged permission surface
and been wrong.

The residual risk stands: the derivation is an agent reading prose, not a mechanical
extraction from `.gzkit/corpus/AGENTS.md.jsonl`. CF-7 and CF-8 have been in
`.gzkit/rules/skill-surface-sync.md` since 2026-04-07 (`7dbe5c15e`) — they were missed by the
first run and caught by the second. **A prohibition added between runs is caught only if the
next run's reader notices it, and the first run demonstrated that readers miss them.**

## UW-5 — An internal doctrine tension this pass cannot adjudicate

`AGENTS.md:38` § PRIME DIRECTIVE 6 lists, as a sanctioned route for an out-of-scope defect:
*"append to `.gzkit/insights/agent-insights.jsonl`"*. `AGENTS.md:125` § Always #11 says of the
same file: *"(**never** hand-append the jsonl)"*, and `.gzkit/rules/governance-core.md:50`
repeats it: *"**never** hand-append `.gzkit/insights/agent-insights.jsonl`"*.

Both readings are defensible (#38 may mean "append via the CLI"), and resolving it is a rule
edit — outside this chore's audit-only lane and outside its `proofs/` write boundary. It is
recorded here because CF-10's drift row depends on which reading binds, and because a
permission-surface pass is where the ambiguity becomes operational: a permission rule cannot
encode "append, but only through `gz insights remember`". This is a **Pass A (rule-conflict)
finding surfaced by a Pass D walk**; routed to `summary.md` § Routing list, not resolved here.

## Standing conclusion

This pass is an **advisory sweep with a known ceiling**, not a gate:

- 10 of 14 command-shaped prohibitions auditable; 4 structurally invisible (UW-1)
- 8 verified live gaps invisible to the drift ledger by construction (UW-2), up from 3
- 180 of 216 audited grants invisible to CI (UW-3); the 36 committed ones are visible
- 4 of 10 mapped prohibitions were absent from the prior run's map (UW-4)

The 6 live rows from this run are **consistent with a surface that permits at least 14
forbidden actions right now** (6 named + 8 unnamed). Anyone reading `consent-drift.md` without
this file will draw the wrong conclusion — which is the precise failure GHI #690 named and
this artifact exists to prevent.
