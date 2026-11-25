> **Dated record, 2026-11-25.** The prompt audit of the Claude Code configuration (session 85e9de78), landed verbatim as the conceptual-model run's test case and as the source the audit's GHIs cite. Line numbers are as read that day. The first "Mechanism map" is superseded by the "Revised mechanism map" and the two sections after it.

# Prompt audit — gzkit Claude Code configuration (2026-11-25)

## Assumptions

- **Scope.** The Claude Code configuration that loads in this project:
  - root `CLAUDE.md` and the `AGENTS.md` it imports;
  - 23 nested `AGENTS.md` files plus the skill-directory copies;
  - `~/.claude/CLAUDE.md` (edits there would affect all projects);
  - `.claude/rules/` (27 files);
  - `.claude/skills/*/SKILL.md` (74 skills plus `.claude/skills/AGENTS.md`);
  - `.claude/agents/` (5 files) and `.claude/commands/` (1 file).
  - About 1.2 MB in total.
- **Plugins, report only.** The plugins that load in this session are `codex` 1.0.6 and `astral` 0.1.0.
- **Skipped.**
  - The `superpowers` and `gz-skills` plugins are installed but absent from this session's skill list.
  - `~/.claude/skills/synced/*` is absent from the session's skill list.
  - No managed-policy `CLAUDE.md` exists.
  - `.claude/worktrees/` (stale agent worktrees) and `.gzkit/renditions/AGENTS.md`, which is a directory.
  - Settings files, `.mcp.json` and `~/.claude.json`, which were not read.
- **Target model.** Claude Opus 5.5 for everything. `codex:codex-rescue` pins `sonnet` and was read as Sonnet 5.5.
- **Non-Anthropic provider.** Codex is an OpenAI integration. Its GPT-facing text was judged only where Claude acts on it.
- **Edit targets.** Most loaded files are generated, so each hunk goes to the canonical source (verified):
  - `.claude/skills/X/` is byte-identical to `.gzkit/skills/X/`;
  - `.claude/rules/X.md` and every nested `AGENTS.md` are generated from `.gzkit/rules/X.md`;
  - root `AGENTS.md` is played back from `.gzkit/corpus/AGENTS.md.jsonl`, so changes to it go through `gz content remember` / `gz content land`.
- **Coupled duties.** Every edit also needs a version bump (`skill-version`/`last_reviewed` for skills, `rule-version` marker plus banner for rules) and then `uv run gz agent sync control-surfaces`.
- **Method.**
  - Five parallel reviewers read the slices whole. The lead read the always-loaded files.
  - The lead re-checked each slice's strongest claims against the code. All held:
    - lock expiry: `events.py`;
    - the merge driver: `.gitattributes`;
    - `tidy` exit codes;
    - ungated validator scopes: `validate_cmd.py` and `data/validator_reachability_grandfather.json`;
    - `gz content land`;
    - the `gz issue file` exit code;
    - the receipt fail-closed condition: `obpi_complete.py:396,708`;
    - the runbook path;
    - the Gate 5 "Heavy only" row.

## Summary

The config has very little model-era cruft. No retired model names, no "think step by step", no update suppressors, no anti-formatting rules, and no thinking or effort prose aimed at older models. The defects are almost all **Group 2**: instruction text the repository has since moved past.

**Three findings matter most.**

1. **"Enforced" scopes that no gate runs.**
   - Root `AGENTS.md:169,209` says `gz check` runs "every registered validator". It lists scopes such as `--cli-alignment`, `--distribution`, `--utf8-prefix` and `--brief-reconcile` as "Mechanical scopes that bind here".
   - `data/validator_reachability_grandfather.json` lists 38 scopes that no gate reaches. 7 of the 16 scopes `AGENTS.md` names are among them.
   - The same false "enforced/live gate" wording sits in `pythonic.md`, `cli.md`, `skill-authoring.md`, `cross-platform.md`, `chores.md` and `tests.md`.
   - As a result, an agent will treat checks that only run when called by name as safety nets.
2. **Gate 5 still described as lane-dependent.**
   - `AGENTS.md` makes Gate 5 universal (ADR-0.0.36).
   - Still wrong:
     - `gz-adr-create/references/govzero-compliance-rules.md:35` ("Heavy only");
     - `gz-obpi-pipeline/SKILL.md:113` ("depends on execution mode");
     - the narrator subagent ("(Normal mode)");
     - outside scope, the pipeline runbook and the OBPI template.
   - An agent can read these as permission to self-close.
3. **Stale mechanics in the lock and pipeline skills.**
   - `gz-obpi-lock` says expired locks are auto-released, and tells agents to add `*.jsonl merge=union`. The code never evicts expired locks, and `.gitattributes` forbids `merge=union`.
   - `gz-obpi-pipeline` names the old `--force` release path.
   - Following these would corrupt the ledger merge or steal a held lock.

**Counts.**

| | High | Medium | Flag/Low |
|---|---|---|---|
| Group 1 (dated text: pressure, migration-relative, choreography) | 0 | 30 | 19 entries in all (S-F7 bundles 15 minor items) |
| Group 2 (stale facts, conflicts, history narratives, trigger text) | 47 | 34 | ↑ |
| Group 3 (tool descriptions) | not applicable in the project; plugins only | | |
| Group 4 (request config) | not applicable: no request-building code in scope | | |
| Plugins (report only) | 0 | 7 | 5 |

## Findings — always-loaded files (lead)

| # | Location (edit target) | Evidence | Pattern | Why | Conf. | Action |
|---|---|---|---|---|---|---|
| A1 | `AGENTS.md:169,209` (corpus) | "`uv run gz check` runs every registered validator" / "every validator" | G2 stale fact + conflict | `data/validator_reachability_grandfather.json` lists 38 ungated scopes, 7 of them named in `AGENTS.md`'s own "Mechanical scopes that bind here" list. `tool-skill-runbook-alignment.md` and several nested files say "explicit-only, reachable from no gate". | High | rewrite (hunk A1) |
| A2 | `AGENTS.md:176` (corpus) | "Missing receipts warn on Lite and fail closed on Heavy." | G2 stale fact | `obpi_complete.py:396,708` sets `fail_closed = lane == "heavy" or kind == "foundation"`. The adr-audit and gate5 rules agree with the code. | High | rewrite (hunk A2) |
| A3 | `.claude/agents/narrator.md:39` | "Do NOT proceed past ceremony without human attestation (Normal mode)." | G2 conflict | `AGENTS.md` says Gate 5 is universal (ADR-0.0.36). "(Normal mode)" implies a mode with no attestation. The line dates from 2026-03-20. `docs/governance/GovZero/obpi-pipeline-runbook.md:196,340,433` still describes an "Exception mode — self-close". | High | **flag** — the older text is a prohibition. Recommendation: drop "(Normal mode)", and file a GHI for the runbook. |
| A4 | `.claude/agents/quality-reviewer.md:24` | "Test coverage adequacy (>= 40% floor)" | G2 conflict ("cite the authority, not the value") | The authority is `.gzkit/manifest.json` `coverage_floor`. The value agrees today. | Medium | rewrite (hunk A4) |
| A5 | `.claude/agents/git-sync-repo.md:16,26` | "Guardrails (`gz lint`, `gz test`) pass" / `--apply --lint --test` | G2 conflict | `AGENTS.md` names `gz check` as the per-change gate, run at pre-push. The `git-sync` skill (2026-10) says `--lint --test` "are redundant… Omitting them is not a red flag". The agent text dates from 2026-02. | Medium | **flag** — aligning it would drop explicit gates, so the operator rules |
| A6 | `.claude/commands/git-commit.md:26` | "NEVER use --no-verify (treat it like a forbidden word)" | 1a pressure | The prohibition is real and stays. The emphasis carries no reason, though `AGENTS.md` states it plainly. | Medium | rewrite (hunk A6) |
| A7 | `CLAUDE.md:13` | "On Fable 5.1 additionally… (Fable 5.1 System Card § 8.4)" / "both current cards" | G2 pinned model names / 1d | Fable 5.2 is the current Fable. `data/frontier_model_cards.json` has no 5.2 card, so the repo does not contradict the text, but the conditional will not match a Fable 5.2 session. | Medium | **flag** — operator-ruled paragraph (GHI #943); the card registry needs updating first |
| A8 | `CLAUDE.md:13` | "Start at `medium` effort, Opus 5.5's default" | 1b | The model cannot set its own effort. This is guidance for the operator's settings, and the agent's settings control it. Harmless as context. | Low | flag |
| — | `~/.claude/CLAUDE.md` | — | — | Clean. Its one rule carries its reason. | — | — |

## Findings — rules (`.gzkit/rules/*`; also feeds every nested `AGENTS.md`)

Line numbers are canonical (loaded line = canonical − 1). No mirror drift.

| # | Location | Evidence | Pattern | Why | Conf. | Action |
|---|---|---|---|---|---|---|
| R1 | `pythonic.md:36` | "Classes <=300 … `gz validate --class-size` … **live gate**" | G2 stale | `class_size` is `"explicit"` (`validate_cmd.py:237`) and on the ungated list | High | rewrite |
| R2 | `cli.md:83` | "Seven obligations fire for a new verb, each mechanically checked" | G2 conflict | Obligation 7 (`--skill-alignment`) is explicit-only and ungated. `tool-skill-runbook-alignment.md` (newer) says so. | High | rewrite |
| R3 | `skill-authoring.md:53` | "`--cli-alignment` resolves every `gz <verb>`… `--skill-alignment` holds every verb" | G2 conflict | Both scopes are ungated | High | rewrite |
| R4 | `cross-platform.md:36`, `chores.md:66`, `tests.md:38` | "Enforced by `gz validate --utf8-prefix`" / "`--chores-layout` enforces it" / "`--test-tiers` forbids" | G2 stale | All three scopes are on the ungated list | High | rewrite (3 hunks) |
| R5 | `mx-mode.md:144` | "*every defect trackable* binds through the contract's punch list" | G2 stale term | `safe-mode-doctrine.md` ruled "the punch list becomes the list of discrepancies". The same rule uses the new term at line 100. | High | rewrite |
| R6 | `cli.md` frontmatter | `paths: - "src/gzkit/commands/**"` | G2 path scope | The rule governs parser code in `src/gzkit/cli/`, which the glob misses | Medium | rewrite (add glob) |
| R7 | `hexagonal-architecture.md:55-57` | "5. *Retired 2026-11-12.* The second-adapter threshold is gone" | 1d | Describes a rule the model never saw; the history is in `rule-version-history.md` | Medium | rewrite |
| R8 | `complexity-thresholds.md:68-72` | "rows previously rendered as markdown tables in this file now live in" | 1d | Phrased relative to a migration | Medium | rewrite |
| R9 | `complexity-thresholds.md:78-80, 94-96` | "Radon's seven … retired with Radon" / "`radon_mi` … retired" | 1d / G2 history | Names phantom metrics; the JSON holds exactly 6 | Medium | remove (2 hunks) |
| R10 | `gate5-runbook-code-covenant.md:45` | "The prior 'for heavy/foundation scope' qualifier … is retired." | 1d | Migration-relative | Medium | remove |
| R11 | `gate5-runbook-code-covenant.md:43` | "Measured 2026-08-08 across … **zero** … The eight hits" | G2 history | The measurement is already in `advisory-rules-audit.md` row 49 | Medium | rewrite |
| R12 | `gh-cli.md:44` | "Measured 2026-09-06 (GHI #972): the default form returned `30`…" | G2 history | The rule is already stated in the first sentence | Medium | rewrite |
| R13 | `pythonic.md:44` | "(PLC0415 runs under Ruff `ALL` since 2026-10-23 …) … (138 sites, then unselected)" | G2 history / 1d | Dated, migration-relative | Medium | rewrite |
| R14 | `pythonic.md:54` | "**Mechanized 2026-08-08 by ruff `BLE001`, after running nowhere…**" | G2 history | Enforcement is already stated at line 22 | Medium | remove |
| R15 | `security-sensitivity.md:29` | "What was wrong was the **silence** … It is now named." | 1d / G2 history | Recorded in `rule-version-history.md` | Medium | rewrite |
| R16 | `security-sensitivity.md:33` | "tightened from informational … after 87 pre-existing briefs were found" | G2 history | The current rule is buried in a cutover story | Medium | rewrite |
| R17 | `security-sensitivity.md:37` | "The co-presence proxy gate this walkthrough once named was removed" | 1d | Migration-relative | Medium | remove |
| R18 | `token-block-discipline.md:23` | "Carried verbatim from root `AGENTS.md` § Operator Doctrine on 2026-09-17" | G2 stale pointer | Root `AGENTS.md` no longer carries this ruling; `gz-session-handoff` does | Medium | rewrite |
| R19 | `changelog-release-notes.md:53-55` | "The `gz validate --changelog` structural scope is landed" | 1d | Migration-relative ("is landed") | Medium | rewrite |
| R20 | `brief-heading-conventions.md:36-37` | "Gate 2 (`## Objective`, …) remains H2" | G2 stale | These are top-level sections, not Gate 2 (Gate 2 is Tests) | Medium | rewrite |
| R21 | `guardrail-feedback-prose.md:55-79` | "ADR-0.0.70 § Decision named such a scope a future candidate and deliberately did not ship it…" | G2 history + 1c repetition | 25 lines of archaeology; it also restates § First enforcement consumer | Medium | rewrite |
| R22 | `task-discovery.md:28` | "; `artifact_edited` left the roster under GHI #947" | 1d | Names a removed member inside a closed list | Medium | remove |
| R23 | `chores.md:98` | "2. **Create TODO list** — Exactly one item in-progress at a time" | 1c / 1d | Harness to-do choreography from the oldest line in the file (2026-03-18) | Medium | remove |
| R24 | `mx-mode.md:146` | "The hangar below is unchanged." | 1d | Migration-relative | Medium | rewrite |
| R-F1 | `cli.md:26` vs `pythonic.md:44` | Help-path lazy imports vs "No lazy imports" (two carve-outs only) | G2 conflict | The repo meets `cli.md` with bare `# noqa: PLC0415` | — | **flag** (would loosen a prohibition) |
| R-F2 | `pythonic.md:84`, `brief-heading-conventions.md:42` | "Fail-closed by `--type-ignores`" etc. | G2 | Same class as R4, lower certainty | Low | flag |
| R-F3 | every rule banner (`model-selection.md:14`, `tests.md:12`, …) | "now", "restored after", "corrected" | 1d | `skill-surface-sync.md` requires a one-sentence change rationale, so this is a house pattern | Low | flag (doctrine call) |
| R-F4 | `hexagonal-architecture.md:79,101` | "128 top-level modules (counted 2026-11-08)" (127 today) | G2 volatile | Dated measurement | Low | flag |
| R-F5 | `gate5-runbook-code-covenant.md:37` | bare `gz validate --documents --surfaces` inside the "ARB-wrapped" bundle | G2 | No `CANONICAL_STEP_COMMANDS` entry | Low | flag |
| R-F6 | `model-selection.md:46` | "# or: sonnet, opus" omits `fable` | G2 | Line 53 lists `fable` as valid | Low | flag |
| R-F7 | `agent-failure-modes.md:16`, `weaponeering.md:28`, `tool-skill-runbook-alignment.md:40-66`, `tests.md:68`, `cross-platform.md:44` | roster restatement / measurement narratives / "during migration" / "widens the section above" | G2 / 1d | Agrees with the repo today, or was an operator-directed edit | Low | flag |

## Findings — skills (`.gzkit/skills/*`)

Of 74 skills, 32 are clean: gz-adr-emit-receipt, gz-adr-map, gz-adr-status, gz-agent-sync, gz-big-picture, gz-check-config-paths, gz-chores, gz-cli-audit, gz-competitor-radar, gz-complexity-guide, gz-context, gz-deps-upgrade, gz-flighttest, gz-governance, gz-how, gz-implement, gz-init, gz-manage, gz-migrate-semver, gz-obpi-brief-drift, gz-patch-release, gz-prd, gz-project, gz-pythonic-pattern-apply, gz-pythonic-pattern-detect, gz-quality, gz-skill-review, gz-state, gz-status, gz-validate, gz-workflow and `.claude/skills/AGENTS.md`.

None of the 9 `disable-model-invocation` routers is a stale alias: every target each one routes to exists.

### High

| # | Location | Evidence | Pattern | Why (repo contradiction) | Action |
|---|---|---|---|---|---|
| S1 | `gz-obpi-lock:87,90` | "Claim succeeds if … existing lock is expired" / "locks older than TTL are automatically released" | G2 | Expiry never evicts (`events.py:341,1096`; token-block Sub-Inv 3/4) | rewrite |
| S2 | `gz-obpi-lock:146-148` | "`CLAUDE_CODE` env var … `claude-code`"; "VS Code Copilot … `copilot`" | G2 | `resolve_agent` reads `CLAUDECODE` and returns `claude-code-<sid8>`; it has no Copilot branch | rewrite |
| S3 | `gz-obpi-lock:155` | "is reaped at its TTL" | G2 | Expiry never evicts | rewrite |
| S4 | `gz-obpi-lock:172-187` | "Add to `.gitattributes`: `*.jsonl merge=union`" | G2 conflict | `.gitattributes:17` says "NOT `merge=union`" and uses `gzkit-jsonl` | rewrite |
| S5 | `gz-obpi-lock:196` | `grep -E '(adr_status\|…)'` | G2 | The file is `adr-status.md`; the ledger is missing from the pattern | rewrite |
| S6 | `gz-obpi-pipeline:41` | "the Stage-4 narrator dispatch is declared here:" (nothing follows) | G2 / 1d | The row moved to `references/stage-4-present-evidence.md` | rewrite |
| S7 | `gz-obpi-pipeline:113` | "**Stage 4 behavior depends on execution mode**" | G2 conflict | Gate 5 is universal; the file's own diagram at line 128 says so. The same sentence is in 5 `references/stage-*.md` files, which are rendered from `data/obpi_pipeline_control_inventory.json` and need an inventory row (flag). | rewrite |
| S8 | `gz-obpi-pipeline:215` | "Stage 5 release, abort release (`--force`)" | G2 internal conflict | Lines 135-151 say `complete` surrenders the lock, and an abort uses `--abandon` | rewrite |
| S9 | `gz-plan-audit:303` | "Consumer: `…/gz-obpi-pipeline/SKILL.md` (Stage 1)" | G2 | Stage 1 lives in `references/stage-1-load-context.md` | rewrite |
| S10 | `gz-obpi-simplify:144` | "Functions exceeding 50 lines or modules exceeding 600 lines" | G2 conflict | `pythonic.md`: "cite the table, never a number"; the table's block bands are 37 and 3130 | rewrite |
| S11 | `gz-tech-debt-review:87,117,150` | ">50 LOC, modules >600 LOC" | G2 conflict | Same as S10 | rewrite (3 hunks) |
| S12 | `gz-tech-debt-review:98,118` | ">5y aging policy" / ">2y stale (not yet 5y)" | G2 | The `dependency-currency` CHORE.md says stale is >1y and never grades on age alone | rewrite (2 hunks) |
| S13 | `gz-tidy:123,132` | "Tidy exits 0 whatever it reports." | G2 internal conflict | Lines 38-43 and `tidy.py:104` say it exits 3 on a breach | rewrite (2 hunks) |
| S14 | `gz-rnd:137` | "(AGENTS.md § Operator Economy #7)" | G2 | That section has 5 unnumbered bullets. `docs/governance/rnd-discipline.md:199` has the same citation (coupled). | rewrite |
| S15 | `gz-ontology:73` | `](../../docs/user/manpages/ontology.md)` | G2 | Resolves to `.gzkit/docs/…`; the correct path is `../../../` | rewrite |
| S16 | `gz-check:18-19` | "Replaces the individual … `/gz-arb` skills." | G2 | `gz-arb` was revived 2026-04-14 and is live | rewrite |
| S17 | `gz-check:77-86` | "When deterministic receipts are needed: uv run gz lint / typecheck / test --bdd / check" | G2 conflict | `AGENTS.md`: "Bare lint, test or docs commands produce no receipt" | rewrite |
| S18 | `gz-check:71-75, 136` | "≤ 200 [lines]" CLAUDE.md ceiling | G2 conflict | The authority is the char budget in `data/instructions_files_budget.json` | rewrite |
| S19 | `gz-arb:106` | "`AGENTS.md` § Attestation (em-dash pattern + canonical invocations …)" | G2 | That section holds neither and points to `gz-arb` | rewrite |
| S20 | `gz-airlock:133-134` | `](../../docs/user/manpages/airlock.md)` | G2 | Does not resolve | rewrite |
| S21 | `gz-chore-runner:23` | "(lite, medium, or heavy)" | G2 | `catalog.py:209` is `Literal["lite","heavy"]` | rewrite |
| S22 | `gz-chore-runner:127` | "`gz chores audit` is what records the proof" | G2 | `run` writes the proof; `audit` verifies it | rewrite |
| S23 | `gz-content-remember:55-63` | compose → advise → commit chain, with no `land` | G2 | `gz content land` (2026-09-27) is the advisory's named next step | rewrite |
| S24 | `gz-context-diet:72-75` | "*Lighter ceremony is not a tradeoff axis*" — `AGENTS.md` claim 1 | G2 | The phrase is absent from the rendered `AGENTS.md`; current text is "…lighter ceremony are not reasons to choose" | rewrite |
| S25 | `gz-intent-trace:137-141` | "the active campaign, which is Magna Carta (`AGENTS.md` § Operator Doctrine) … (Behavior Rule 9)" | G2 | `AGENTS.md` names no campaign there, and Behavior Rules are unnumbered | rewrite |
| S26 | `gz-issue-file:47-51` | "≥3 recent `fix(` precedents" | G2 conflict | `AGENTS.md` § Defect-fix routing has no such condition | rewrite |
| S27 | `gz-issue-file:71-73` | "propagates `gh`'s exit code" | G2 | `issue_cmd.py:212` raises `SystemExit(2)` | rewrite |
| S28 | `gz-mx:22-23` | "Two guards NEVER drop: `gate5_invariants` and the PRIME DIRECTIVE" | G2 conflict | `mx-mode.md` pins many `CRITICAL` guards that never demote; the fix tightens | rewrite |
| S29 | `git-sync:141-143` | Related Skills: `lint`, `test`, `format` | G2 | No such skills exist | rewrite |
| S30 | `git-sync:82` | "Pre-commit hook handles lint/test automatically." | G2 | Its own lines 64-68 say otherwise; tests run at pre-push | rewrite |
| S31 | `git-sync:117,120` | "I'll skip `--lint --test` to be quick" → failure mode | G2 internal conflict | Lines 64-74 (newer) say the flags are redundant | remove + rewrite |
| S32 | `git-sync:121` | "I'll commit and sync separately" → don't | G2 internal conflict | § Commit messages (2026-11-08) says commit first, then sync | rewrite |
| S33 | `ghi-author:330` | "Four worked examples —" (five listed) | G2 | `references/examples.md` has five | rewrite |
| S34 | `gz-adr-closeout-ceremony:415` | "`docs/user/operator_runbook.md`" | G2 | Does not exist; the file is `docs/user/runbook.md` | rewrite |
| S35 | `gz-adr-closeout-ceremony:397` | "Run git-sync before `gh release create`" | G2 internal conflict | Step 8 says release ends at the bump and `gz-patch-release` publishes | rewrite |
| S36 | `gz-adr-audit:41` | "file a GHI … and route to a fresh OBPI brief" | G2 conflict | `AGENTS.md`: "Do not create an ADR or OBPI to discharge one" | rewrite |
| S37 | `gz-adr-audit:120` | "`docs/design/audit/**` remains historical only" | G2 / 1d | The path does not exist | remove |
| S38 | `gz-advisor-qc:80` | "advise-rendition CLAUDE.md --consumer claude" | G2 | The only corpus is `AGENTS.md`, with consumers `root` and `codex` | rewrite |
| S39 | `gz-adr-promote:124-128` | "Rule of Three baseline (which the doc sets for heavy-lane ADRs)" | G2 | The matrix was rekeyed 2026-10-28; the lane columns are retired | rewrite |
| S40 | `gz-adr-create/references/govzero-compliance-rules.md:35,39` | "Gate 5 … Heavy only" / "Lite lane: Gates 1-2 only" | G2 conflict | Gate 5 is universal | rewrite |

### Medium

| # | Location | Evidence (abridged) | Pattern | Action |
|---|---|---|---|---|
| S41 | `gz-obpi-pipeline:53` | "No 'stop and summarize' … violating the spirit of this rule is violating the rule." | 1a; also dropped the two legitimate stops | rewrite |
| S42 | `gz-obpi-lock:26` | "An expired lock may mean another agent started work." | G2 (code answers it) | rewrite |
| S43 | `gz-session-handoff:120-121` | `last_lock_event_timestamp` / `last_commit_sha` inputs | G2 (no flag exists; a handoff discharges no lock) | remove |
| S44 | `gz-session-handoff:330-353` | "The gate is RETIRED … Measured lifetime: 9 lifts, 1 block" | G2 history | rewrite (keeps the verbatim quotes) |
| S45 | `gz-session-handoff:388` | "it needed 13 corrections in 29 days" | G2 history | rewrite |
| S46 | `gz-obpi-sync:27-33` | "the table-sync predecessor happened to carry this skill's present slug" | G2 history | rewrite |
| S47 | `gz-obpi-specify:46-53` | "The OBPI-0.0.16-03 brief shipped with fabricated framework paths …" | G2 history | rewrite |
| S48 | `gz-obpi-specify:117,177` | "now pins this order" / "no longer binds" | 1d | rewrite (2 hunks) |
| S49 | `gz-plan:84-86` | "Put up to 20 non-obvious questions to the operator" | G2 conflict ("one decision per question") | rewrite |
| S50 | `gz-wp:4` (description) | "create, attach issues to, move, change, add evidence to or record an issue close" | G2 trigger text / description–body mismatch | rewrite |
| S51 | `gz-airlock:30-33` | "the formerly membrane-less ad-hoc surface now leaves" | 1d | rewrite |
| S52 | `gz-arb:107-109` | the same manpage listed twice | 1c | remove |
| S53 | `gz-chore-runner:4` (description) | "(show, plan, advise, execute, validate)" | G2 description–body mismatch | rewrite |
| S54 | `gz-content-compose:59-60` | "advisor-QC loop (OBPI-24) and operator attestation (OBPI-22)" | G2 (terminal ADR's OBPIs) | rewrite |
| S55 | `gz-content-compose:49`, `gz-content-remember:40,85,89` | `gz content …` without `uv run` | G2 conflict | rewrite |
| S56 | `gz-complexity-distill:149` | "The verb closed the OBPI-0.0.27-06 waiver path" | G2 history | remove |
| S57 | `gz-design:4` (description) | "\"design X\", \"let's design\", \"brainstorm X\"…" | G2 trigger enumeration | rewrite |
| S58 | `gz-design:55-59` | four "**DO NOT**" lines, one with a reason | 1a | rewrite (keeps every prohibition) |
| S59 | `gz-design:126` | "200–300 words for nuanced ones" | 1b/1f numeric cap | rewrite |
| S60 | `gz-foundation-triage:141-148` | "`git status --porcelain … .gzkit/ledger.jsonl` # Expected: empty" | G2 (the ledger is routinely dirty) | rewrite |
| S61 | `gz-insights-remember:20-28` | "was historically hand-appended … This verb **replaces**" | 1d | rewrite |
| S62 | `gz-justify:130` | "3-10 minutes … less than 3 minutes, you probably rationalized" | 1c / 1f | rewrite |
| S63 | `gz-justify:169-172` | "**Closed forward reference:** … no longer need to run" | 1d | remove |
| S64 | `gz-health-audit:164-182` | "The 2026-08-15 run reported … `gz obpi park` verb **that does not exist**" | G2 history | rewrite |
| S65 | `gz-adr-audit:39,171,185` | "is now bound … replaces prose Demonstrate Value … graceful migration" | 1d | rewrite |
| S66 | `gz-adr-closeout-ceremony:176` | "the bound replacement for the old prose 'Demonstrate Value' step" | 1d | rewrite |
| S67 | `gz-adr-closeout-ceremony:36,49` | "**Violating the spirit of this contract is violating it.**" / "Later means never. … NOW." | 1a | remove + rewrite |
| S68 | `gz-adr-closeout-ceremony:313` | "`uv run behave features`" | G2 (manifest: `uv run -m behave features/`) | rewrite |
| S69 | `ghi-triage:32-36` | "MUST execute … There is no Rich table view … full stop." | 1d + 1a; also false (`--format rich` exists) | rewrite |
| S70 | `ghi-triage:79` | "no longer writes them" | 1d | rewrite |
| S71 | `ghi-triage:81-90` | "Measured 2026-09-20 against the 38 members …" | G2 history | rewrite |
| S72 | `git-sync:72-74` | "Defaults were flipped to `False` … (airlineops parity evolution)" | 1d | rewrite |
| S73 | `gz-adr-sync:20,59,63-69` | "Absorbs `gz-adr-autolink` … Archived predecessors" table | G2 history + internal inconsistency | rewrite + remove |
| S74 | `ghi-author:173,175` | "#460 was filed ~17 minutes after #459 …" / "rank 12 … 55%-family skim" | G2 history | rewrite |
| S75 | `ghi-close:234-246` | "Observed instance (GHI #677, 2026-07-21): …" | G2 history | rewrite |
| S76 | `ghi-close:319,342` | "**Canonical regression (GHI #771, arm B).** …" | G2 history | rewrite |
| S77 | `ghi-close:98-100` | "Scenario evaluations sample decisions; … passing sample" | 1c eval vocabulary | rewrite |
| S78 | `ghi-close:106` | "highest-priority constraint … overrides every other instinct" | 1a stacked emphasis | rewrite |
| S79 | `gz-adr-evaluate:73` | "Until GHI #770 … on 2026-08-07 an evaluation of `ADR-0.35.0` ran single-driver" | G2 history | rewrite |
| S80 | `gz-adr-evaluate:153,321` | "`obpis/` (preferred) or `briefs/` (legacy)" | 1d / G2 (no `briefs/` exists) | rewrite |
| S81 | `gz-adr-evaluate:226-227` | "now survives regeneration" | 1d | rewrite |
| S82 | `airlineops-parity-scan:157,170` | "perpetual-catch-up pattern" used for deferring imports | G2 conflict with Boundary 5's meaning | rewrite |
| S83 | `gz-adr-create:88-89,249,292` | "`src/gzkit/templates/adr.md` (canonical …)" | G2 (`.gzkit/templates/` is canonical) | rewrite |

### Flags and Low — no hunk

- **S-F1.** `ghi-author:74-78,319` and `ghi-close:143-148` send a GHI to an agent-authored OBPI brief. This conflicts with `AGENTS.md` ("Never … edit briefs"; "propose OBPI work only as a Feature Checklist item"). **The operator rules.**
- **S-F2.** `gz-adr-create:176` says "Never pre-fill; never propose a default." `AGENTS.md` § Operator Economy says to offer A/B/C with a recommendation. The older text is a prohibition, so this is a flag.
- **S-F3.** Doctrine question: `obpi-decomposition-matrix.md` (2026-10-28) calls ADR checklists and OBPIs "frozen history", while `gz-adr-create`, `gz-adr-promote` and `AGENTS.md` § Gate Covenant still size OBPIs with it. **The operator rules.**
- **S-F4.** `gz-mx:28-29,232` says the PRIME DIRECTIVE binds "in both modes". `mx-mode.md` (2026-10-25) defers *fix immediately* to the safe-mode exit. Aligning the skill would loosen a prohibition, so the operator rules.
- **S-F5.** The opus-tier Self-Escalation block in 7 skills cannot fire on Claude Code, because every one of those skills pins `model: opus`. It may still serve other vendors' mirrors.
- **S-F6.** `gz-obpi-pipeline/AGENTS.md:12` (generated) keeps a relative link that does not resolve from that directory. The fix belongs in the sync generator, which should rebase links.
- **S-F7.** Low findings, each flag only:
  - `gz-obpi-pipeline:119-125`: the "DO NOT STOP HERE" box (1a);
  - `gz-obpi-lock:80`: `"branch": "master"`;
  - `gz-session-handoff`: "no gate" restated about six times, plus a `(v7.9.2)` heading;
  - `gz-rnd:4`: behavioral text inside the description;
  - `gz-tech-debt-review:245`: strategy coaching;
  - `gz-check:126,137`, `gz-adr-audit:54,86,348`: values given without their authority;
  - `gz-justify:56`: cites "6b"/"6e", which `AGENTS.md` no longer carries;
  - `gz-intent-trace:131`: "6h" mis-cited;
  - `gz-complexity-advisor:3`: description misses the body's ceiling-failure case;
  - `gz-flighttest:59-62`: Iron Law caps;
  - `gz-adr-evaluate:4`: description says "or OBPI";
  - `ghi-triage:205`: "1.5 MB … 10–30 s";
  - `ghi-close` "NEVER, EVER, EVER" heading: renaming it needs anchor updates in three skills;
  - rationalization rows that name no observed failure (`skill-authoring.md` Parsimony 5): `git-sync`, `gz-adr-create`, `gz-adr-evaluate`, `gz-adr-audit`;
  - `gz-design:17,39,55`: superpowers prohibitions; the plugin is installed but not loading.
- **S-F8.** `gz-adr-create/references/govzero-compliance-rules.md` also lacks `Validated` in its lifecycle table, and has an `adr-X.Y.x/` layout that matches no directory.

## Plugins — report only, no edits proposed

| # | Location | Finding | Conf. |
|---|---|---|---|
| P1 | `codex/agents/codex-rescue.md:34`, `codex-cli-runtime/SKILL.md:24,39` | Defaults to `--write`. In this repo that means Codex edits the shared tree on `main`, which conflicts with the single-writer / worktree doctrine and bypasses gz-only ledger writes. Pass read-only, or accept the conflict knowingly. | Medium |
| P2 | `codex-rescue.md:3,17` | "Proactively use when Claude Code is stuck" / "Do not wait for the user to explicitly ask". This is a trigger booster in a description that loads every session. It pulls against "delegate only sizeable independent tracks". | Medium |
| P3 | `codex-rescue.md:42`, `codex-cli-runtime:43` vs `codex-result-handling:20`, `commands/rescue.md:48` | "return nothing" on failure, against "include the most actionable stderr lines". | Medium |
| P4 | `codex-rescue.md:23-24` vs `codex-cli-runtime:28` | "prefer background execution", but the background flags are stripped before the forwarder. | Medium |
| P5 | `commands/review.md:60`, `adversarial-review.md:65` | "Do not call `BashOutput`": there is no such tool. | Medium |
| P6 | `codex-result-handling/SKILL.md:19` | "CRITICAL: … STOP … MUST … strictly forbidden" (1a). The constraint is real; the register is the problem. | Medium |
| P7 | `astral/ruff/SKILL.md:25-27` | "Only apply fixes to files you're modifying". This contradicts the PRIME DIRECTIVE ("unrelated lint error found → fix it"). | Medium |
| P8–P12 | various | GPT model names possibly dated; internal skills visible to the model; optional Stop gate returns Codex text as a block reason; bold "Always use" (1a); migration tables restating general knowledge; `pytest` example, which the repo bans. | Low |

## Defects found outside the audit surface (to track)

1. `docs/governance/GovZero/obpi-pipeline-runbook.md:33,186,196,340-342,433` still describes the Exception-mode self-close, which contradicts universal Gate 5.
2. `.gzkit/templates/obpi.md:130` says "### Gate 5: Human (Heavy only)", and `:245` says "when required by parent lane". Same contradiction.
3. `docs/governance/rnd-discipline.md:199` cites "Operator Economy #7", which does not exist.
4. The five `gz-obpi-pipeline/references/stage-*.md` files carry "depends on execution mode". They need a rewording row in `data/obpi_pipeline_control_inventory.json`.
5. `src/gzkit/commands/content/__init__.py:756` help text calls an ARB receipt "Gate 5".
6. `.gitattributes:14` cites "AGENTS.md § Never #2", a section that no longer exists.
7. `data/frontier_model_cards.json` lacks the Fable 5.2 card (see A7).
8. The `sync_nested_agents_md` generator copies rule-relative links without rebasing them (S-F6).

## Mechanism map (superseded by the Revised mechanism map below)

| GHI | Failure mechanism (what changed and was not carried through) | Findings it covers |
|---|---|---|
| M1 | Ungated `gz validate` scopes called gates (extends RP-7 F2) — *ruled: extend F2* | A1, R1–R4 |
| M2 | Gate 5 universality (ADR-0.0.36) not carried into skills/template/agent — *ruled: new GHI, fix now* | S7, S40, narrator:39, `.gzkit/templates/obpi.md:130,245` |
| M3 | Lock lease and surrender semantics (expiry never evicts; `complete` surrenders; `--abandon`; GHI #1167) | S1, S3, S8, S42, S43 |
| M4 | Lock agent identity resolution (`CLAUDECODE`, `-<sid8>`, Copilot dropped) | S2 |
| M5 | JSONL merge driver (`gzkit-jsonl` replaced `merge=union`) | S4 |
| M6 | Pipeline body moved to `references/` at the d47de23c8 cutover | S6, S9, S41 |
| M7 | Size bands rekeyed to the lizard table; 50/600 retired | S10, S11 |
| M8 | Dependency-currency grading (stale >1y, never age alone) restated | S12 |
| M9 | `gz tidy` exits 3 on breach (GHI #1124); older rows kept | S13 |
| M10 | `AGENTS.md` re-rendered; skills cite or restate text it no longer holds | S14 (+ `rnd-discipline.md:199`), S19, S24, S25, S26 |
| M11 | Manpage links one directory level short from a skill dir | S15, S20 |
| M12 | 2026-04-03 consolidation into `gz-check` (lint/test/format retired, `gz-arb` retired then revived) | S16, S17, S29 |
| M13 | Instruction-file budget moved from lines to chars | S18 |
| M14 | Chore model (lane `lite`/`heavy`; `run` writes proof, `audit` verifies) | S21, S22, S53 |
| M15 | `gz content land` added (OBPI-0.35.0-07); chain not updated | S23, S54, S55 |
| M16 | `gz issue file` exits 2 on `gh` failure | S27 |
| M17 | MX floor: guards pinned `CRITICAL` never demote | S28 |
| M18 | *punch list* renamed *list of discrepancies* (safe-mode doctrine) | R5 |
| M19 | `git-sync` flags default off and commit-then-sync (2026-10/11); older rows kept | S30, S31, S32, S72 |
| M20 | `ghi-author` example count (five, not four) | S33 |
| M21 | Renamed or removed paths: `operator_runbook.md`, `docs/design/audit/`, `adr_status` | S34, S37, S5 |
| M22 | Release publication moved to `gz-patch-release` | S35 |
| M23 | Defect-fix routing: a GHI is repaired directly, never via a new OBPI | S36 |
| M24 | Corpus consumers are `root`/`codex` only; no `CLAUDE.md` corpus | S38 |
| M25 | Decomposition matrix rekeyed 2026-10-28; lane columns retired | S39 |
| M26 | Receipt fail-closed condition includes foundation kind (`AGENTS.md`, via corpus) | A2 |

Family reading (not stored): M3–M26 share one cross-GHI pattern — a skill restates a fact from code or canon, the source changes, nothing re-verifies the restatement. No locus tracks it. Evidence that the existing remedy misses it: `gz-check`, `gz-obpi-lock` and `gz-tidy` carry `last_reviewed: 2026-10-17`, `gz-chore-runner` 2026-11-07, `git-sync` 2026-11-08, and each still holds High findings — `gz-skill-review`'s re-verification passed them.

## Revised mechanism map (per source change; ruled 2026-11-25)

Reach = every consumer of the changed fact repo-wide, found at repair. Medium findings sharing a High mechanism ride in its reach; Medium-only mechanisms stay with RP-7 (Split).

| GHI | Source change not carried through | Findings | Event |
|---|---|---|---|
| M1 | ungated scopes called gates (extends RP-7 F2) | A1, R1–R4 | ruled |
| M2 | Gate 5 universal (ADR-0.0.36) | S7, S40, narrator:39, `templates/obpi.md:130,245` | ruled |
| M3 | lock lease/surrender (GHI #1167) | S1, S3, S8, S42, S43, `obpi_complete.py:1511` | verified |
| M4 | lock agent identity (`CLAUDECODE`, `-<sid8>`; Copilot dropped) | S2 | verified (`lock_manager.py:122-143`) |
| M5 | JSONL merge driver `gzkit-jsonl` | S4 | verified (`.gitattributes`) |
| M6 | pipeline body to `references/` (d47de23c8) | S6, S9, S41 | verified |
| M7 | size bands rekeyed to the lizard table | S10, S11 | verified |
| M8 | dependency-currency grading | S12 | verified (CHORE.md:106) |
| M9 | `gz tidy` exits 3 on breach (GHI #1124) | S13 | verified (`tidy.py:104`) |
| M10 | `AGENTS.md` trim 2026-05-07 (`8dbb38c7d`): attestation pattern to `gz-arb`; precedent condition dropped | S19, S26 | verified (git -S) |
| M11 | `AGENTS.md` corpus generation 2026-09-17 (GHI #921) dropped section numbering | S14 (+ `rnd-discipline.md:199`), S25 "Behavior Rule 9", `gz-justify:56`, `gz-intent-trace:131` | verified (git -S) |
| M12 | campaign name left `AGENTS.md` 2026-10-10 (`64f35c53e`) | S25 "Magna Carta" | verified (git -S) |
| M13 | VIBES INERT claim reworded | S24 | event unverified |
| M14 | manpage links written one level short | S15, S20 | wrong at authoring |
| M15 | lint/test/format skills retired into `gz-check` (2026-04-03) | S29 | per subagent; verify at filing |
| M16 | `gz-arb` revived (2026-04-14) | S16, S17 | verified (`revival_note`) |
| M17 | instruction budget lines → chars | S18 | verified (`data/instructions_files_budget.json`) |
| M18 | chore lane enum `lite`/`heavy` | S21 | verified (`catalog.py:209`) |
| M19 | chore `run` writes proof, `audit` verifies | S22, S53 | verified (parser help) |
| M20 | `gz content land` added (OBPI-0.35.0-07) | S23 | verified (`content/__init__.py:631`) |
| M21 | `git-sync` `--lint/--test` default off | S31, S72 | verified (skill's own lines 64-74) |
| M22 | commit first, then `git-sync` (2026-11-08) | S32 | verified (blame) |
| M23 | unit tests moved off pre-commit to pre-push | S30 | verified (`.pre-commit-config.yaml:212-242`) |
| M24 | `ghi-author` example 1a added | S33 | verify at filing |
| M25 | `operator_runbook.md` → `runbook.md` | S34 | verified |
| M26 | `docs/design/audit/` removed | S37 | verified |
| M27 | `adr_status` → `adr-status.md` | S5 | verified |
| M28 | release publication moved to `gz-patch-release` | S35 | verified (Step 8, blame) |
| M29 | Defect-fix routing: a GHI is repaired directly | S36 | verified |
| M30 | corpus consumers `root`/`codex` only | S38 | verified |
| M31 | decomposition matrix rekeyed 2026-10-28 | S39 | verified |
| M32 | receipts fail closed on foundation kind too | A2 | verified (`obpi_complete.py:396,708`) |
| M33 | `gz issue file` exits 2 on `gh` failure | S27 | verified (`issue_cmd.py:212`) |
| M34 | MX floor: `CRITICAL`-pinned guards never demote | S28 | per subagent; verify at filing |
| M35 | *punch list* → *list of discrepancies* | R5 | verified (contract § Records) |

Medium-only, to RP-7 (no High mechanism): S44–S52, S54–S71 except S53, S73–S83.

### Medium stale facts treated as High (ruled 2026-11-25)

| GHI | Source change not carried through | Findings | Event |
|---|---|---|---|
| M36 | one question at a time (operator ruling; `AGENTS.md` § Operator Economy) | S49 | verified |
| M37 | ADR-0.0.37 terminal; cite the successor, never its OBPIs | S54 | per `gz-content-remember:24-27` |
| M38 | `uv run` for every Python command | S55 | wrong at authoring |
| M39 | the ledger is routinely dirty from other work | S60 | observed this session |
| M40 | BDD command is `uv run -m behave features/` (manifest) | S68 | verified (`.gzkit/manifest.json:64`) |
| M41 | `gz-adr-sync` predecessors deleted on retire | S73 | verify at filing |
| M42 | `briefs/` directory retired | S80 | verified (absent) |
| M43 | Architectural Boundary 5: *perpetual catch-up* is gzkit chasing AirlineOps (2026-09-29) | S82 | verified |
| M44 | `.gzkit/templates/` is canonical, `src/gzkit/templates/` its copy | S83 | verified (`skill-surface-sync.md`) |

So the map holds 44 mechanisms. RP-7 keeps the wording and narrative findings: S44–S48, S50–S52, S56–S59, S61–S67, S69–S71, S74–S79, S81, and the rules R7–R24 that are narrative (R6 is RP-7 F12).

### Added by the flag walk (2026-11-25)

| GHI | Source change not carried through | Findings | Ruling |
|---|---|---|---|
| M45 | safe mode defers *fix immediately* to the exit (contract ruling 2026-10-25) | `gz-mx:28-29,232` (S-F4) | canon (newer operator ruling) |
| M46 | help-path deferral is a third lazy-import carve-out | `pythonic.md:44`, `cli.md:26`, 16 parser `# noqa: PLC0415` | "Third carve-out (Recommended)" |
| M47 | `last_reviewed` records a review, never an edit | `skill-surface-sync.md:24` rule 6, `skills_audit.py`, every hunk's bump instruction | "Review-only date (Recommended)" |
| M48 | a build step is never called *Gate 5* (`agents-md-map-doctrine.md`) | `src/gzkit/commands/content/__init__.py:756` help text | canon |

Folded into existing reach: S-F1 (`ghi-author`/`ghi-close` OBPI destination) → M29; S-F2 (`gz-adr-create:176` no default) → M36 ("Economy rule (Recommended)"); A5 (`git-sync-repo` agent) → M21; `.gitattributes:14` "§ Never #2" → M11.
Routed, not repaired here: S-F3 (OBPIs as frozen history) → RP-14; S-F6 (nested-AGENTS.md generator links) → RP-7 F11 (files retired); A7 (`CLAUDE.md:13` Fable 5.1) → `frontier-model-card-currency` chore (Fable 5.2 card unconsumed); runbook Exception mode → GHI #1188.
No action: codex `--write` ("No action"); astral ruff "only fix files you're modifying" (project PRIME DIRECTIVE governs).

Total: 48 GHIs.

### Added when partitioning for RP-7 (2026-11-25, under "Treat as High (Recommended)")

| GHI | Source change not carried through | Findings |
|---|---|---|
| M49 | the three-subjects ruling's carrier moved from root `AGENTS.md` to `gz-session-handoff` | R18 |
| M50 | top-level brief sections are not Gate 2 (Gate 2 is Tests) | R20 |
| M51 | cite the authority, not the value: coverage floor is `.gzkit/manifest.json` `coverage_floor` | A4 |

Total: 51 GHIs.

### Hand-off to RP-7 (stage input, not repaired now)

- GHI #1246 (rules narrative): R7–R17, R19, R21–R24; low flags R-F3, R-F4, R-F7.
- GHI #1250 (skill bodies): S44–S48, S50–S52, S56–S59, S61–S67, S69–S71, S74–S79, S81; low flags S-F5, S-F7.
- GHI #1251 (agent and command definitions): A6, A8.
