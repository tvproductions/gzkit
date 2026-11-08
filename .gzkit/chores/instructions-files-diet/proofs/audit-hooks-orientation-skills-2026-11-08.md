# Audit: hooks, session orientation, skill listing (gzkit, 2026-11-08)

Read-only audit. Every hook script registered in `.claude/settings.json` was read in full, plus
`scripts/session_orientation.py` (render path, collectors and budget code) and `scripts/settings_local_backup.py`.
Measurements were taken in this session. Under Anthropic's guidance a hook is for a rule that admits no
exception. A preference-only hook should be deleted and the choice left to Claude.

Live state that changes the picture: `.gzkit/mx.json` has had **safe mode** (`mode: safe`) open since
2026-10-20T22:59Z, which is about 19 days. Measured: `alarms_off()` = True, `checkpoint.is_advisory("pipeline-gate")` = True,
`hangar_demotes()` = True. So verifier-pipe-gate does nothing right now, pipeline-gate only advises, and the
stop hook reports without blocking. All of them still run on every matching call.

Generated-surface note: the `.claude/hooks/*.py` files are generated from templates in `src/gzkit/hooks/scripts/`
(for example `validation.py:391` and `pipeline.py:299,517` hold the same stale strings found below). A fix goes in the
templates and then `gz agent sync control-surfaces`. The skill canon is `.gzkit/skills/`. `.claude/skills/` is a
mirror, and `src/gzkit/skills/` is the wheel copy.

---

## 1. Hooks (21 registered commands)

How Claude Code treats hook output (documented semantics): stdout is added to the model's context
only for **SessionStart** and **UserPromptSubmit**. A PreToolUse/PostToolUse/Stop hook reaches the model
only through **exit 2 + stderr**, a JSON `permissionDecisionReason` / `decision:block` reason, or JSON
`additionalContext`. With **exit 0, stderr or plain stdout goes to the user/transcript, not to Claude**.
With any other non-zero exit, stderr goes to the user only. Several hooks below depend on this. See D4.

| # | Event / matcher | Script | Enforces / injects | Can block | Prose to model (bytes, frequency) | Class | Duplicates |
|---|---|---|---|---|---|---|---|
| 1 | SessionStart `*` | scripts/session_orientation.py | State digest (§2) | No | 3985 B today (4.4 KB earlier) per start and again after each compaction (SessionStart source=compact). **20.6 s wall time** measured | Preference/advisory | See §2 |
| 2 | SessionStart `*` | scripts/settings_local_backup.py | Snapshots gitignored settings.local.json to ~/.claude/backups | No | 0 B (a restore hint only when the file is missing) | Operator safety, not an agent rule | none |
| 3 | PreCompact `*` | session_orientation.py (again) | Same digest | No | **0 B reach the model** (PreCompact stdout is not injected). It still costs ~20 s and repeats the side effects (git fetch, lock reaping, ledger TTL rows, lease bookings) | Redundant | SessionStart `*` already re-fires on source=compact |
| 4 | PreToolUse ExitPlanMode | plan-audit-gate.py | Blocks plan exit for an OBPI plan without a fresh plan-audit receipt. Self-runs `gz plan audit` (60 s cap) | Yes (exit 2) | ~400–900 B on a block. Rare | Zero-exception (governed gate) | Prior-art reminder points to a nonexistent `/prior-art` skill (D5) |
| 5 | PreToolUse Bash | verifier-pipe-gate.py | Refuses verifier piped into another process (exit-code masking) | Yes (exit 2) | 1059 B on a block. Rare | **Zero-exception**, a model hook | `.gzkit/rules/tests.md` § exit-code integrity (the hook mechanizes it, which is correct). Inert under safe mode |
| 6 | PreToolUse Bash | pipeline-completion-reminder.py | Reminder before git commit/push when a pipeline marker is live and brief incomplete | No (exit 0) | **0 B to model** (stderr on exit 0) | Preference/reminder | gz-obpi-pipeline skill |
| 7 | PreToolUse Bash | ghi-triage-chat-silence.py | Blocks `triage.py --format rank` if last turn narrated ≥2 GHI/severity pairs | Yes (exit 2) | ~700 B on a block. Only on triage | **Preference** (chat style) | ghi-triage SKILL.md § Step 3 |
| 8 | PreToolUse Bash | dispatch-stamp.py | Rewrites a subagent's gz command with its dispatch root (updatedInput) | Rewrites; denies subagent PowerShell gz | 0 B normally | Zero-exception (wrong-root write prevention) | none |
| 9 | PreToolUse Grep\|Bash\|PowerShell | prefer-lsp.py | Denies the first text search per "Python-looking" token per session. An identical retry passes | Yes (deny), **bypassed by repeating** | 510 B reason + one wasted round trip per new token. Frequent (≈180 tokens recorded across 9 recent session files) | **Preference by its own design** (nudge, never trap) | CLAUDE.md line "Python symbol lookups … go through the LSP tool" |
| 10 | PreToolUse Write\|Edit\|NotebookEdit | session-staleness-check.py | Warns about stale legacy pipeline marker/receipt | No | **0 B to model** (stderr exit 0) | Preference | none |
| 11 | PreToolUse Write\|Edit\|NotebookEdit | pipeline-gate.py | Blocks src/ and tests/ writes for a governed OBPI without an active pipeline. Fences work-package trees | Yes (exit 2) | 381 B on a block | Zero-exception (governance) | AGENTS.md OBPI Acceptance Protocol. Advisory under safe mode |
| 12 | PreToolUse Write\|Edit\|NotebookEdit | obpi-completion-validator.py | Blocks an edit that sets an OBPI brief to Completed without evidence/attestation | Yes (exit 2) | ~300–600 B on a block. Rare | Zero-exception (advisory fast path; the commit guard is the binding arm) | Its lane logic contradicts AGENTS.md Gate 5 (D6) |
| 13 | PostToolUse ExitPlanMode | pipeline-router.py | Prints "run gz obpi pipeline" after a PASS receipt | No | **0 B to model** (plain stdout, exit 0, PostToolUse) | Preference/routing | gz-obpi-pipeline |
| 14 | PostToolUse Edit\|Write | post-edit-ruff.py | `gz lint` on the edited .py. Prints up to 20 lines | No | **0 B to model** (stderr exit 0), although its docstring says "so the agent sees the warning in the same turn" | Preference (fast feedback) | stop-turn-feedback lint arm. AGENTS.md says this hook "strips unused imports", which is stale (D7) |
| 15 | PostToolUse Edit\|Write | ledger-writer.py | Records governance-artifact edits through record_artifact_edit | No (prints "[GOVERNANCE BLOCK]" with exit 1, which cannot block and goes to the user only) | 0 B to model | Bookkeeping (zero-exception record) | commit-locus backstop gzkit.hooks.commit_ledger |
| 16 | PostToolUse Agent | dispatch-stamp.py | Books the subagent's dispatch claim | No | 0 B | Zero-exception bookkeeping | none |
| 17 | PreToolUse PowerShell | dispatch-stamp.py | See row 8 | Deny | 0 B normally | Zero-exception | none |
| 18 | Stop `*` | stop-turn-feedback.py | (a) gz lint over **all git-dirty .py**, (b) "claim-grounding": state claims without a nearby citation token | Yes (exit 2, once per turn) | ~700–1100 B per block. 73 blocks logged (10 claim-grounding) in .gzkit/sensors | (a) deterministic, close to zero-exception. (b) **heuristic preference**: any backtick span satisfies it | AGENTS.md "Completion evidence is the ledger" |
| 19 | Stop `*` | settings_local_backup.py | Same as row 2 | No | 0 B | Operator safety | running at every turn end is excessive; SessionStart alone covers recovery |
| 20 | UserPromptSubmit `*` | mx-awareness.py | MX/safe-mode banner on every prompt while the marker exists | No | **359 B every prompt** (19 days running). Stdlib fallback reads the whole 28 MB ledger | Zero-exception *state* banner (justified as awareness) but verbose | Orientation "MX hangar" section. `.claude/rules/mx-mode.md` |
| 21 | SessionEnd `*` | session-exit-bookmark.py | Writes a CHECKPOINT handoff on exit/clear | No | 0 B now. Next session's orientation adds ~340 B "bookmarks awaiting sensemaking" + ~390 B "Account" | Bookkeeping | Feeds §2 sections that recur every session |

Latency per Bash call: 5 hooks (verifier 0.14 s, others ~0.035–0.04 s). Edit: 3 pre + 2 post.

**Zero-exception (keep):** verifier-pipe-gate, dispatch-stamp (×3), pipeline-gate, obpi-completion-validator,
plan-audit-gate, ledger-writer, stop-turn-feedback lint arm, mx-awareness (as a short state banner),
session-exit-bookmark (bookkeeping), settings_local_backup (operator safety).

**Preference (delete, or move to prose/skill):** prefer-lsp, ghi-triage-chat-silence,
pipeline-completion-reminder, session-staleness-check, pipeline-router, post-edit-ruff (as wired),
stop-turn-feedback claim-grounding arm, the PreCompact orientation registration.

### Defects

- **D1 prefer-lsp false positives (reproduced).** Each of these was denied:
  `find . -name "*.md" | grep -v node_modules` ('node_modules'),
  `git log --oneline | grep -i fix_ci`, `ps aux | grep MY_ENV_VAR`, `grep -rn GZKIT_DISPATCH_ROOT docs/`.
  Causes in `prefer-lsp.py`: (1) `covers_python([])` returns True when there is **no** file operand, so a grep
  that filters stdin in a pipeline counts as a search over Python files. (2) `-v` (inverted match) is treated as a
  lookup. (3) a directory operand with no suffix (`docs/`) produces no filter and so "covers Python". (4) any
  token with an underscore or in UpperCamel case qualifies (recorded blocks include `Raises`, `ruff_baseline`, `trust_audits`,
  `node_modules`). An identical retry always passes, so each false positive costs a round trip and 510 B of
  prose and enforces nothing. The hook is a preference by its own docstring ("nudges and never traps").
- **D2 orientation is not read-only, and runs twice per compaction.** `collect_obpi_locks` reaps and appends
  `obpi_lock_ttl_warning` ledger rows, `collect_mx_hangar` books lease expiries, `probe_remote_divergence`
  fetches. On PreCompact this all happens again with no context benefit. (My run appended no rows today.)
- **D3 orientation latency 20.6 s** per session start (gh issue list, git fetch, `gz adr status` ×≤3,
  `gz chores status --json`, a full 28 MB ledger parse in `_events_since`, mx_hardening_findings).
- **D4 four advisory hooks are unseen by the model.** pipeline-completion-reminder, session-staleness-check,
  post-edit-ruff (stderr, exit 0) and pipeline-router (stdout, exit 0, PostToolUse) never reach Claude under the
  documented semantics, so they cost latency and deliver nothing to the agent. ledger-writer's
  "[GOVERNANCE BLOCK]" uses exit 1, which neither blocks nor reaches the model. *Verify by reproduction
  before acting*: these semantics come from the hooks docs, not from an observed run here.
- **D5 stale skill references in hook prose:** plan-audit-gate tells the agent to run `/prior-art`, and
  obpi-completion-validator tells it to run `/gz-obpi-audit`. **Neither skill exists** in `.gzkit/skills` or `.claude/skills`.
  The prior-art regex also accepts the word "grep" or "registry", so it is close to always satisfied. Same strings in
  `src/gzkit/hooks/scripts/validation.py:391` and `pipeline.py:299,517`.
- **D6 obpi-completion-validator contradicts Gate 5 doctrine.** It requires human attestation only when
  `is_foundation or parent_lane == "Heavy"` and prints "OBPIs under Heavy/Foundation ADRs inherit attestation
  rigor". AGENTS.md says Gate 5 is universal (ADR-0.0.36, GHI #342). The commit guard is the binding arm, but the
  prose teaches retired doctrine.
- **D7 AGENTS.md § Execution Rules is stale:** it says "the post-edit ruff hook strips unused imports immediately".
  post-edit-ruff.py is lint-only, no fix (GHI #239). The rule's reason no longer holds, though the advice
  (put the import and its use in one edit) is harmless.
- **D8 plan-audit-gate reads the global `~/.claude/plans/`.** The newest plan from *any* project, if it names an OBPI id,
  can gate ExitPlanMode here.
- **D9 stop-turn-feedback lints every git-dirty .py**, not only files this session touched. Pre-existing findings
  in a dirty tree (61 files on 2026-11-07) block a turn the agent did not cause. TIMEOUT_SECONDS=2 for
  `uv run gz lint` over many files risks a silent fail-open.
- **D10 the agent-definition budget measures the wrong thing.** `.claude/agents/*.md` totals 10,814 B against a 6000-B budget,
  but only the 5 `description` fields (~650 B) enter the main session. Bodies load only inside the subagent.

---

## 2. Session orientation (3985 B today, budget 4000)

| Section | Bytes | Actionable each session? | Duplicates |
|---|---|---|---|
| Title line | 69 | no | — |
| Active campaign — Magna Carta | 916 | partly: plan path + topmost pointer are useful. The 3 truncated checkbox heads ("document order, NOT the pull order") are by its own label not the pull order | CAMPAIGN_AUTHORITY_NOTE (~230 B) restates rulings carried verbatim by gz-obpi-pipeline. Workflow fronts list repeats the plan |
| Git remote state | 62 | yes, but only when diverged | `gz status` |
| Most-recent handoff (advisement + 5 advised steps) | 1249 | **yes**, the main payload | the handoff file itself. The "ADVISES, never authorizes… book with gz handoff decide" sentence repeats gz-session-handoff |
| Account since last authored handoff | 393 | sometimes (VERDICT line) | derived from git + ledger. Recurs whenever a bookmark exists |
| Session-exit bookmarks awaiting sensemaking | 341 | rarely: produced mechanically by row 21 on every exit/clear, so it appears almost every session | GHI #759 instruction repeated each time |
| Open session-handoff GHIs | 44 | no: "(none open)" | costs a `gh` network call |
| Active OBPI claims | 70 | no: lists `mx-session`, the hangar's session lock, as an "OBPI claim" (misleading) | MX banner |
| Active ADR pipeline state | 61 | no: "(no active pipeline markers)" | `gz obpi status` |
| Chores due or overdue | 228 | no: "32 overdue" every session, "announces, never gates". Constant noise trains the reader to skip it | `gz chores status` |
| MX hangar | 341 | already known | **duplicates the per-prompt mx-awareness banner** (row 20) |
| Skill-awareness re-injection | 211 | no | "consult gz-how" line is **verbatim AGENTS.md § SKILLS FIRST**. The "below 50% context" note means nothing at session start |

Trim candidates (~1.2–1.4 KB, about 35%): drop Skill-awareness (211), the empty GHI and pipeline sections (105),
the MX hangar section while mx-awareness runs (341), chores reduced to one count line or dropped (≈150–228),
CAMPAIGN_AUTHORITY_NOTE and the checkbox heads (≈350), and the repeated handoff boilerplate sentence (≈200).
Show the git section only when diverged. Remove the PreCompact registration (D2/D3). Result ≈2.6 KB.

---

## 3. Skill listing and agent definitions

- 75 skills in `.claude/skills` (`.gzkit/skills` holds the same 75 names). 11 already carry `disable-model-invocation: true`
  (git-sync, gz-big-picture, gz-chores, gz-context, gz-governance, gz-health-audit, gz-manage, gz-project,
  gz-quality, gz-workflow). The validator skips them. **64 model-invocable descriptions = 6736 chars**
  (budget 6000), plus per-entry name/format overhead (~1.5 KB) every session.
- Largest description: **gz-rnd 661 chars** (10% of the budget on its own). Trim to ~150. Its "offer it when signals fit" clause
  keeps it model-invocable.
- Canon already says to do this: `src/gzkit/rules/skill-authoring.md:18` ("A skill that wraps one command and adds no
  judgment is an alias: make it user-invoked … or remove it") and `agents-md-map-doctrine.md:62`.

**Operator-initiated or side-effecting, candidates for DMI** (1075 chars): gz-patch-release (publishes),
gz-deps-upgrade, gz-competitor-radar (monthly), gz-complexity-distill, airlineops-parity-scan, gz-flighttest
(human Go/No-Go), gz-migrate-semver (ledger events), gz-init, gz-constitute, gz-prd, gz-adr-closeout-ceremony,
gz-mx (opens safe mode). Also consider gz-obpi-pipeline and gz-obpi-lock, since AGENTS.md says only the operator initiates
OBPI work and claims locks. **Caution:** DMI also blocks the model from loading the skill when another skill chains to it.
Cross-references measured: gz-obpi-pipeline is named by 14 other skills, closeout by 9, ghi-close by 8,
patch-release by 5. Check each chain before flipping.

**Thin wrappers (alias rule), candidates for DMI or merge** (495 chars): gz-adr-map (1.5 KB body), gz-check-config-paths
(1.4 KB), gz-implement (1.8 KB), gz-cli-audit (2.0 KB), gz-validate (2.1 KB), gz-adr-emit-receipt (2.5 KB),
gz-state (3.0 KB).

**Overlap clusters** (the cause of the `gz-how` disambiguation crutch):
- Status/lineage: gz-status, gz-adr-status, gz-state, gz-adr-map, gz-ontology (plus DMI gz-big-picture).
- Sync: gz-adr-sync, gz-obpi-sync, gz-agent-sync, git-sync (skill) **and** the git-sync-repo agent (same trigger phrases).
- Audit/check: gz-adr-audit, gz-plan-audit, gz-cli-audit, gz-check-config-paths, gz-validate, gz-check, gz-tidy,
  gz-tech-debt-review (plus DMI gz-health-audit).
- Complexity: gz-complexity-advisor / -distill / -guide. Pythonic: -detect / -apply. Content: compose / remember / advisor-qc.
- Triage: ghi-triage, gz-foundation-triage. Design entry: gz-design, gz-plan, gz-adr-create, gz-rnd, gz-justify.

Estimated result: 6736 − 1075 − 495 − ~500 (gz-rnd trim) ≈ **4.7K chars**, under budget.

Agents: 5 files, 10,814 B. Main-session cost is only the descriptions (~650 B). git-sync-repo duplicates the
git-sync skill. Fix the budget validator to measure descriptions, or accept that the 6000-B line measures subagent prompts (D10).

---

## Adjacent finding (outside the three sources, same bloat)

Path-scoped rules load on the first **Read** of a matching file. Reading any `.py` loads `pythonic.md` (8.9 KB) and
`hexagonal-architecture.md` (6.5 KB), both `paths: "**/*.py"`. Reading `scripts/session_orientation.py` also loads
`token-block-discipline.md` (8.3 KB). That was about 23.7 KB in this audit session, with no edits made. hexagonal-architecture is
design doctrine, not per-file guidance: narrowing it to `src/gzkit/**/*.py` would keep it out of hook/script/test reads.
(`cat` through Bash does not trigger rule loading. Read does.)

## Per-session injected bytes (summary)

| Source | Bytes |
|---|---|
| Orientation | ~4.0 KB at start, and again after each compaction |
| mx-awareness | 359 B × prompts (e.g. 50 prompts ≈ 18 KB). The largest cumulative item while safe mode stays open |
| Hook block prose | event-driven. prefer-lsp ≈ 510 B per new token (most frequent). stop-feedback ≈ 0.7–1.1 KB per block |
| Skill listing | 6.7K chars of descriptions + ~1.5 KB overhead |
| Agent descriptions | ~650 B |
| (Path rules, on first .py Read) | ~15–24 KB |
