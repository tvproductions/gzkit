# Unwitnessable Ledger — Pass D run 2026-07-16

**Read this before reading `consent-drift.md`.** That ledger reported **0 live rows**. This artifact is why that number does not mean "the permission surface honors doctrine."

Required by `acceptance.json`: a run producing a drift ledger without this file fails its own criteria (GHI #690).

## UW-1 — Context-dependent prohibitions (3 of 9 command-shaped rules)

The drift walk covers only prohibitions where a forbidden command is forbidden *unconditionally*. Where doctrine forbids an action **in a context**, no permission rule can express it: the sanctioned and forbidden invocations are byte-identical strings, and the permission matcher sees a flat string with no caller context.

| ID | Citation | Verbatim | Why invisible |
|---|---|---|---|
| CD-1 | `AGENTS.md:127` § Always #13 | *"Author GHIs through `/ghi-author` — never call `gh issue create` directly"* | `/ghi-author` invokes `gh issue create` at `SKILL.md:199` as its own final step. `Bash(gh issue:*)` is **load-bearing, not drift** — denying it breaks the only sanctioned path for filing a GHI. Canonical false positive: the Pass D prototype flagged exactly this rule and was wrong. |
| CD-2 | `AGENTS.md:142` § Never #6 | *"Do not work around hook blocks."* | "Working around" is an intent. No token distinguishes a legitimate retry from a workaround. |
| CD-3 | `AGENTS.md` § SKILLS FIRST | *"Matching skill first. No convenience exception."* | The same command is sanctioned or forbidden depending on whether a skill covers the task. Context, not string. |

**One in three command-shaped prohibitions in AGENTS.md is structurally invisible to this pass.** This is a ceiling, not a backlog item — it does not shrink with better patterns.

## UW-2 — Broad-rule blindness (verified, not hypothesised)

A drift row can only be raised against an allow rule that *mentions* the prohibited token. A broad rule permits the same forbidden action while naming nothing. Verified this run by testing whether each rule actually permits the command:

| Prohibition | Forbidden command | Permitted by | Named in the rule? |
|---|---|---|---|
| CF-6 — `AGENTS.md:342`, operator canon *"never create feature branches"* | `git checkout -b feature/foo` | `Bash(git *)` | **No** |
| CF-3 — `AGENTS.md:94` § STDLIB-FIRST, *"unittest over pytest"* | `uv run pytest tests/` | `Bash(uv run *)` | **No** |
| CF-5 — `AGENTS.md:137` § Never #2, *"NEVER: Modify the ledger directly"* | `sed -i '' 's/x/y/' .gzkit/ledger.jsonl` | `Bash(sed:*)` | **No** |

All three are **live** in the sense that matters — the action is permitted and no deny covers it — yet all three are absent from `consent-drift.md`, because the ledger can only see rules that name the token. **The drift walk's 0-live result and these 3 verified gaps coexist.** That is the honest summary of this pass's coverage.

CF-5 is the sharpest: `Edit(...)` rules correctly do not reach `.gzkit/ledger.jsonl`, so the *file-tool* path is closed — but `Bash(sed:*)` reopens it through the shell. Permission surfaces are per-tool; the prohibition is per-artifact.

### Probe hygiene note

An initial loose probe (substring match on rule prefixes) reported 18 rules permitting a ledger write. Re-testing each rule against the actual command reduced that to **1** (`Bash(sed:*)`): the `Bash(tee <path>)` rules are pinned to exact paths and `Bash(cat)` cannot write. A future run must test *permission of the command*, never *substring of the rule* — the loose form manufactures false positives at ~18:1 here.

## UW-3 — CI-blindness

```
$ git check-ignore -v .claude/settings.local.json
.gitignore:54:.claude/settings.local.json	.claude/settings.local.json
```

This run walked **180 allow rules from `settings.local.json` and 0 from `settings.json`** — every allow rule audited exists only on one operator's machine. On a fresh clone this pass sees an empty allow list and reports a clean surface, vacuously. **Never wire this chore to a CI gate.** Its findings are not reproducible off the authoring machine.

## UW-4 — Curated-list drift

`doctrine-map.md` was re-derived from `AGENTS.md` + `.gzkit/rules/**` this run rather than loaded from a prior run, per CHORE.md § Known coverage limits #4. That mitigates but does not eliminate the risk: the derivation is an agent reading prose, not a mechanical extraction from `.gzkit/corpus/AGENTS.md.jsonl`. A prohibition added to AGENTS.md between runs is caught only if the next run's reader notices it.

## Standing conclusion

This pass is an **advisory sweep with a known ceiling**, not a gate:

- 6 of 9 command-shaped prohibitions auditable; 3 structurally invisible (UW-1)
- 3 verified live gaps invisible to the drift ledger by construction (UW-2)
- 0 of 180 audited rules visible to CI (UW-3)

The 0-live drift ledger from this run is **consistent with a surface that permits three forbidden actions right now**. Anyone reading `consent-drift.md` without this file will draw the wrong conclusion — which is the precise failure GHI #690 named and this artifact exists to prevent.
