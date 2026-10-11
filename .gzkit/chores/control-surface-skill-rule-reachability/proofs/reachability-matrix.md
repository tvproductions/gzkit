# Reachability Matrix — Skill ↔ Rule (Pass B)

> Chore: `control-surface-skill-rule-reachability` (Lite lane, audit-only)
> Run: **2026-10-10**, maintenance visit E. Supersedes the 2026-08-09 matrix.
> Surface: **73 skills** under `.gzkit/skills/**` × 26 authored rules plus root `AGENTS.md`.
> Vendor mirrors are derivatives and were not audited.

**Method.** Four independent reviewers (spec-reviewer persona, read-only) each read all 27 files
under `.gzkit/rules/` and root `AGENTS.md` whole, then every skill in one partition whole
(10, 16, 24 and 23 skills). Each gap carries a verbatim quote from the skill and from the rule
with line numbers. The main session checked all 83 quoted lines against the files by text and
by line (83 of 83 verbatim, each within three lines of the cited line) and re-verified first-party
the code claims repeated below. No reviewer ran a command.

**Applicability test** (CHORE.md): a rule applies when (a) its `paths:` cover the skill, (b) the
skill's procedure invokes a CLI verb the rule governs, or (c) the skill modifies files the rule's
`paths:` cover. Root `AGENTS.md` has no `paths:` and applies everywhere.

**Admission bar:** a gap requires a concrete worked example: a step that, followed as written,
breaks a named clause. Silence about a rule is not a gap.

## Counts

| Measure | Value |
|---|---|
| Skills audited | **73** (68 in August; six added, one removed) |
| Authored rules | 26 |
| Applicable pairs by path overlap | **294** (four rules name `.gzkit/skills/**`; `mx-mode.md` and `weaponeering.md` name one skill each) |
| Applicable pairs honored by citation | 5 |
| Rule citations in skill bodies, any form | 28, across 20 skills; **53 of 73 skills cite no rule** |
| Skills naming at least one validator scope | 24 |
| **Gaps with a worked example** | **35**: 6 carried from August, 29 new |
| Confidence of the 29 new gaps | 10 high, 19 medium |

The August count of 624 applicable pairs is not comparable: `task-discovery.md` and others have
since narrowed their `paths:`. The citation rate is not the finding. The 35 rows are.

## Prior rows (August), accounted for

| Row | Verdict | Basis |
|---|---|---|
| N1 `gz-agent-sync` ↛ `skill-surface-sync.md` #6 | **carried** | `:106` still says "Bump the version anyway" with no `last_reviewed` half |
| N2 `gz-obpi-pipeline` ↛ `model-selection.md` claim 4 | closed, premise changed | rule 0.7.0 now says the dispatch call carries `model`; the skill passes a tier alias |
| N3 `gz-obpi-pipeline` ↛ `model-selection.md` claim 5 | closed | Step 4a-v (`gz obpi verify-packet`, `:1014-1025`) replays the packet before presentation; behaviour not observed |
| N4 `gz-obpi-lock` ↛ `token-block-discipline.md` Sub-Invariant 5 | closed | `:119` cites the rule and documents `--abandon` and exit 3 |
| N5 `gz-adr-audit` ↛ `adr-audit.md` step 2 | **carried** | `:164` still runs bare `uv run gz test > …/unittest.txt` where the rule requires ARB-wrapped invocations |
| N6 `gz-adr-audit` ↛ `adr-audit.md` § Rules | closed, premise refuted | the rule's own sequence attests before `gz audit`; the skill's prerequisite is a completed ADR |
| N7 `gz-check` ↛ `gate5-runbook-code-covenant.md` § Do Not | **carried** | `:79-86` lists bare commands under "When deterministic receipts are needed" |
| N8 `gz-check` ↛ `agents-md-map-doctrine.md` § Budget | **carried** (gz-check half) | `:72` still checks "≤ 200" lines; the budget file holds characters. The `gz-tidy` half is closed: it now runs the validator |
| N9 `ghi-close` ↛ `task-discovery.md` § Invariant | **carried** | the skill contains no `Task:` anywhere (grep count 0); `:303` requires only the GHI trailer |
| N10 `gz-obpi-simplify` ↛ `complexity-thresholds.md` § Invariant | **carried** | `:144` flags 50 and 600 lines; `:158` "For each finding: fix it directly." |
| N11 `gz-cli-audit` ↛ `cli.md` Consistency | closed | 0.2.0 added the remediation loop |

## New gaps — high confidence

**B01 · `gz-obpi-lock` 6.3.1 ↛ root `AGENTS.md` § Operator Doctrine (no branches).**
§ Worktree Isolation tells the agent to run `git worktree add ../gzkit-claude-code -b agent/claude-code/obpi-0.0.25-03` (`:212`) and then `git merge agent/claude-code/obpi-0.0.25-03` (`:219`). Root `:202`: *"its result lands on main through the single writer, never by merging a branch. The no-branches directive is unchanged."*

**B02 · `gz-obpi-pipeline` 6.66.0 ↛ `weaponeering.md` claims 1 to 3.**
Stage 2 opens at "RED — write ONE minimal test" (`:301`) with no constraints sortie, and Stage 3 proceeds on a `working-tree` base whatever the failure class (`:639`). Rule `:33`: *"Do not fold constraints into red; a red that fails on `error` has flown no constraints."* Expected: the rule landed 2026-10-10 as advisory and names this skill in its `paths:`; the departure is a finding for the operator, not a refusal.

**B06 · `gz-adr-closeout-ceremony` 7.19.0 ↛ `gh-cli.md` § Allowed commands.**
`:243` runs `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASE_NOTES.md`. Rule `:31`: *"# never the cumulative RELEASE_NOTES.md (GHI #710)"*.

**B07 · `gz-issue-file` 1.0.3 ↛ `gh-cli.md` § Filing an issue.**
`:46` sends a consumer-owned defect to the "consumer's tracker via plain `gh issue create`." Rule `:20`: *"**`gh issue create` is forbidden as a direct agent invocation**"*.

**B08 · `gz-patch-release` 1.11.1 ↛ `gh-cli.md` § Allowed commands.**
Step 1a.3 runs `gh issue edit <N> --add-label runtime` (`:151`). The rule's block carries no `gh issue edit`, and its 0.7.0 note treats the block as an allowlist (*"this allowlist did not carry the verb"*). `ghi-author` says outright that `gh issue edit` is outside it. Repair is on the rule side or the skill side; the operator rules which.

**B09 · `gz-adr-closeout-ceremony` 7.19.0 ↛ `changelog-release-notes.md` release-notes rule 3.**
`:240` "# Step 9: Update RELEASE_NOTES.md (agent edits the file)". Rule `:41`: *"Authored and updated through the `gz-patch-release` skill, not by hand."*

**B14 · `gz-advisor-qc` 0.2.0 ↛ `agents-md-map-doctrine.md` § Attestation granularity.**
`:58` "Cite the receipt id in the operator's Gate-5" attestation. Rule `:44`: *"Do not call a build step "Gate 5." The content surface's attestation is named CORPUS ATTESTATION."*

**B15 · `gz-deps-upgrade` 1.3.0 ↛ root `AGENTS.md` § Project Identity.**
Step 4 pipes into `python3 -c '…'` (`:85`). Root `:6`: *"always `uv run` for Python commands."* The same clause was breached 40 times by the session that ran this audit (insight scope `session/uv-run-rule`).

**B22 · `gz-pythonic-pattern-detect` 1.1.1 ↛ `chores.md` damaged-slug recovery.**
`:87` prescribes a bare `uv run gz chores doctor` for a "missing or damaged" overlay. Rule `:55` requires `--dry-run` first and a sync of unsynced edits, because a damaged repair rewrites surviving definition files.

**B23 · `gz-tech-debt-review` 1.4.0 ↛ `pythonic.md` § Size Limits.**
`:117` grades "Module >600 LOC, function >50 LOC" as breaking a binding rule. Rule `:56`: *"<=600 as guidance, and cite the table — not this rule — for any threshold claim."* Same class as N10.

## New gaps — medium confidence

| Row | Skill (version) | Rule clause | Step, in one line |
|---|---|---|---|
| B03 | `gz-obpi-lock` (6.3.1) | root `AGENTS.md:146`, never independently claim or release OBPI locks | `:25` "Lock first, always" extends claiming to an agent's own quick fix |
| B04 | `gz-obpi-pipeline` (6.66.0) | `model-selection.md:18`, tier by decision complexity, not task size | `:356` classifies by allowed file count and maps it to a tier |
| B05 | `gz-obpi-pipeline` (6.66.0) | root `AGENTS.md:108`, never hand-write markers | `:222` "Hand-author fallback" writes the pipeline-active marker, and `:236` says it unblocks the gate hook |
| B10 | `ghi-author` (1.11.0) | root `AGENTS.md:177`, do not create an ADR or OBPI to discharge a GHI | `:317` routes a finding to a new OBPI brief and closes the GHI `superseded` |
| B11 | `gz-issue-file` (1.0.3) | root `AGENTS.md:181`, defect-fix routing | `:49` attributes a "≥3 recent `fix(` precedents" test the section does not hold and omits its covering-test condition |
| B12 | `gz-adr-closeout-ceremony` (7.19.0) | `model-selection.md:22`, a subagent's claim is not evidence | `:60` synthesizes attestation evidence from three subagent reads with no re-derivation step |
| B13 | `gz-patch-release` (1.11.1) | `model-selection.md:34`, release notes on the Opus tier | `:17` declares `model: sonnet` for a skill whose core act is writing release notes |
| B16 | `gz-chore-runner` (1.5.2) | root `AGENTS.md:90`, author GHIs through `ghi-author` | `:87` routes tracking to `gz chores propose-ghi`, which calls `gh issue create` with no prior-art lookup (`chores_propose_ghi_cmd.py:94-104`) |
| B17 | `airlineops-parity-scan` (1.2.0) | root `AGENTS.md:238`, gzkit leads and AirlineOps adopts | `:27` triggers a scan on any AirlineOps change and requires a same-cycle tranche |
| B18 | `gz-chore-runner` (1.5.2) | `chores.md:21`, edit `.gzkit/chores/` only | `:61` calls the package copy "canonical"; `gz-context-diet:86` and `gz-obpi-specify:51` carry the same inverted label |
| B19 | `gz-complexity-advisor` (0.2.3) | root `AGENTS.md:94`, commit through the configured hooks | `:77` offers `SKIP=complexity-advisor-auto-chain git commit`; the hook is not installed here |
| B20 | `gz-foundation-triage` (1.0.3) | root `AGENTS.md:133`, foundation is closed to new authoring | `:74` emits candidates for reclassification to foundation |
| B21 | `gz-complexity-distill` (0.3.2) | root `AGENTS.md:172`, Gate 5 names completed OBPI or ADR work only | `:66` has the operator attest a distillation "at Gate 5" |
| B24 | `gz-pythonic-pattern-detect` (1.1.1) | `chores.md:62`, plan before any run | `:80` runs the chore with no `gz chores plan` or `advise`; `gz-pythonic-pattern-apply` and `gz-tech-debt-review` do the same (grep count 0 in all three) |
| B25 | `gz-skill-review` (1.0.0) | `gh-cli.md` § Allowed commands | `:53` uses `gh issue view <N>`, which the block does not list; `gz-status:41`, `ghi-close` and this chore's own evidence gate use it too |
| B26 | `gz-how` (1.0.1), `references/skill-maintenance.md` | `skill-surface-sync.md:20`, bump the version on every edit | `:10` has the agent add rows to two skills with no version or review-date bump |
| B27 | `gz-state` (0.2.0) | root `AGENTS.md:146`, never independently edit briefs | `:44` tells the operator, then runs `gz state --repair`, which rewrites brief status with no dry run and no wait |
| B28 | `gz-migrate-semver` (0.2.0) | root `AGENTS.md:108`, write the ledger only through `gz` commands | `:31` routes a slug correction to `python -m gzkit.governance.obpi_slug_rename`, which appends to the ledger (`obpi_slug_rename.py:130`) and calls itself "Not a ``gz`` verb" (`:22`) |
| B29 | `gz-skill-review` (1.0.0) | `skill-authoring.md:53`, a repair that touches a skill is operator-only | `:4` lets an audit warning trigger a rewrite, version bump, sync, commit and push |

## Below the bar, verified

- `gz-tidy:123` says "Tidy exits 0 whatever it reports." `src/gzkit/commands/tidy.py:171` raises `SystemExit(3)`. Stale since GHI #1124; no rule clause is broken by following it.
- `gz-deps-upgrade` frontmatter is not valid YAML under a strict parser: its `description:` contains an unquoted `: ` ("in one pass: uv itself"). gzkit's own reader accepts it. Whether every consumer of skill frontmatter does was not tested.
- `ghi-close:404` cites `.claude/rules/arb.md` inside an example; no `arb.md` exists in either rules directory. `ghi-triage:118` and `gz-obpi-pipeline:1706` cite mirror paths where a canonical path exists.
- `gz-insights-remember` declares `gz_command: gz insights remember`; siblings omit the `gz ` prefix.
- Numbered references that no longer resolve in the unnumbered root contract: `gz-obpi-pipeline` ("Always #18", "#9", "#6", "#11"), `gz-intent-trace:141` ("Behavior Rule 9"), `gz-justify:56` ("6b", "6e"). `skill-authoring.md` Parsimony clause 2 requires text attributed to `AGENTS.md` to be quoted from the current file.

## Unverified references (reviewers could not run commands)

`gz-obpi-lock:239` "`AGENTS.md` § Agent Profiles"; `gz-adr-closeout-ceremony:418` `docs/user/operator_runbook.md`; `git-sync:128-130` related skills `lint`, `test`, `format`; `gz-airlock:138` and `gz-ontology:73` relative manpage links one level short; `gz-intent-trace:138` "Magna Carta (`AGENTS.md` § Operator Doctrine)"; `gz-obpi-pipeline:543` `TempDBMixin`; `gz-obpi-pipeline:1490` `ghi-close` pinned at v2.4.0 (it is 2.12.0); `ghi-author:134` BSD-only `date -v-30d` in the mandatory Step 0 query. Each is a reference a reviewer could not find stated where it points; none was asserted absent.

## Limits

No command was run by any reviewer, so no verb, flag or exit code was observed. The honors test credits a citation by filename, which says the skill names the rule, not that it follows it. A gap is a reading of two texts; whether an agent in practice takes the step is not measured here.

## After the run: the sweep of 2026-10-11

Operator g0 ordered the repair of the ten rows of summary headline 1 ("do the skill sweep").
Evidence: commit `04fda99d3`. One independent reviewer (spec-reviewer persona, read-only) read the
edits against the rules before the commit. It returned seven rows closed and three partly
closed; the main session checked each finding it acted on against the files, and the
states below are after those corrections.

| Row | State | What the skill says now |
|---|---|---|
| B01 | closed | `gz-obpi-lock` 6.4.0 teaches a detached worktree and a patch the single writer applies; no branch, no merge. The sequence was run in a throwaway repository first |
| B06 | closed | `gz-adr-closeout-ceremony` 7.20.0 Step 10 publishes the newest version block only, by `gz-patch-release` Step 4d |
| B14 | closed | `gz-advisor-qc` 0.2.1 names the corpus attestation |
| B18 | closed | `gz-chore-runner` 1.5.3, `gz-context-diet` 1.1.3 and `gz-obpi-specify` 1.9.3 name `.gzkit/chores/` the authoring source |
| B20 | closed | `gz-foundation-triage` 1.1.0 keeps the check (REQ-0.0.57-03-05) and leaves the list empty where the kind is closed |
| B22 | closed | `gz-pythonic-pattern-detect` 1.2.0 runs the doctor's dry run and a sync before a repair |
| B02 | open, narrowed | `gz-obpi-pipeline` 6.67.0 cites the rule at the weak-red row of Phase 1c. No stage flies the constraints sortie; the rule gives that to the runtime (claim 6), so the skill does not place it |
| B09 | open, narrowed | Step 9 follows `gz-patch-release` Steps 2, 3 and 4b. `gz-patch-release:56` still sends minor releases to the closeout ceremony, so the two skills point at each other. One ruling: which surface owns a minor release's notes |
| B17 | open, narrowed | `airlineops-parity-scan` 1.3.0 states the direction and drops the trigger on an AirlineOps change. Step 13's same-cycle tranche is unchanged: the skill reads "perpetual catch-up" as a reason for it, the reviewer reads it as the chase. One ruling |
| B21 | open, withdrawn | `gz-complexity-distill` is unchanged at 0.3.2. REQ-0.0.27-04-07, attested, reads "operator-attested at Gate 5", and `ADR-0.0.27` calls the pass a "foundation-kind ceremony at every recurrence"; `AGENTS.md` § Attestation reads "Gate 5 names completed OBPI/ADR work only". A REQ that literally asserts a retired claim goes to the operator (`AGENTS.md` § OBPI Acceptance Protocol) |

**Ruling on B21, 2026-10-11.** Operator g0 ruled, verbatim "B", on the option worded "Gate 5, kept
literal. Each recurring pass runs as an OBPI you initiate under a feature ADR." Commit `a87603775`:
`gz-complexity-distill` 0.4.0 says a cadence trigger makes a pass due and the operator initiates
the pass as OBPI work, so the Gate 5 it names is an OBPI's completion attestation. **B21 is closed.**
The REQ, the ADR and the naming rule keep their text. Recorded as worked example 5 of
`docs/governance/attested-req-subject-retirement.md`.

**Open gaps after the sweep and the ruling: 28 of 35** (seven closed). The unverified reference
`gz-obpi-lock:239` ("`AGENTS.md` § Agent Profiles") was confirmed absent by grep and removed.

Same class, outside the skills and corrected in the same commit: six skill manpages, the
`frontmatter-reconcile` manpage, two runbook lines, and the manual-finish hint of
`gz patch release`, which printed the cumulative notes file as the release body.

Limits of this addendum. The reviewer read the edited hunks and the cited clauses, not the
63 unedited skills, and ran no command. The session that wrote the edits also wrote this
table. Two findings stay open as insights: the closeout CLI's Step 9 text
(`closeout/ceremony-step-9-release-notes`) and the mirror roster in 38 skill manpages
(`docs/skill-manpages-stale-mirror-roster`).
