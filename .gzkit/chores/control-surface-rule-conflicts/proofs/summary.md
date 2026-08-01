# Conflict Matrix Summary — Pass A

> Chore: `control-surface-rule-conflicts` (Lite lane, audit-only)
> Date: **2026-08-01** (prior runs: 2026-05-11, 2026-07-07, 2026-07-16)
> Inputs: `rule-inventory.md`, `conflict-matrix.md`
> Trigger: GHI #743 — the chore's `test -f` acceptance was replaced by a git-commit-date
> freshness gate (`scripts/check_proof_freshness.py`), which failed closed because the
> proofs were frozen at 2026-07-16 while `.gzkit/rules/` last moved 2026-07-29.

Full re-walk: **28 files** (26 canonical rules + `AGENTS.md` + `CLAUDE.md`), **378 unordered
pairs**, fanned across three independent readers plus a first-party verification pass. Every
`file:line` in the matrix's *Mechanical winner* column was opened during this run.

## Counts by severity

| Severity | Definition | 2026-07-16 | **2026-08-01** |
|----------|-----------|------|------|
| `blocking` | Agent hits this monthly or more often; live mid-work surface | 12 | **4** |
| `episodic` | Hit during a specific ADR or change-shape class | 8 | **9** |
| `theoretical` | Pair could disagree on a misread; canonical reading (or an adjacent in-rule disclosure) reconciles | 4 | **4** |
| `refuted` | Prior row's claim verified false; retained out-of-matrix so it is not re-derived | 1 | 1 (unchanged) |
| **Total in matrix** | | **25** | **17** |

Files touched by >=1 row: 19 of 28 -> **16 of 28**.

### Row provenance

| Class | Count | Rows |
|---|---|---|
| **New this run** | 5 | R02, R03, R04, R16, R17 |
| **Carried forward — still live** | 12 | R01 (was 12), R05 (2), R06 (9), R07 (11), R08 (24), R09 (6), R10 (7), R11 (8), R12 (5), R13 (4), R14 (22), R15 (23) |
| **Retired — conflict no longer exists** | 12 | prior rows 1, 3, 13, 14, 15, 16, 17, 18, 19, 20, 21, 25 |
| **Refuted, kept out of matrix** | 1 | prior row 10 (Never #1 vs Universal OBPI Attestation) |

## The headline: the prior audit was actioned the same day and the matrix never recorded it

The 2026-07-16 proofs were committed at **13:11**. `3a4aacf32`
(*"reconcile 3 rules that contradicted AGENTS.md (Pass A rows 13-16, 19)"*) landed at
**14:48** and `1ddb407d7` (*"reconcile remaining Pass A rows; mechanize the version-marker
invariant"*) at **16:22** — the same afternoon, between them remediating rows 11, 13-23 and
25. **Twelve of the prior matrix's twenty-five rows were dead before the day ended, and the
matrix said nothing.**

That is exactly the failure mode GHI #743 names. Under the old `test -f` acceptance the
chore reported `All criteria pass` for sixteen days while its central artifact described a
surface that had been repaired within three hours of the artifact being written. The
freshness gate is the correct fix and it fired correctly.

**Secondary observation worth carrying:** the remediation was faithful. Spot-checking all
twelve retired rows against current canon found no case where a rule was reworded to *look*
fixed. Each carries a rule-version bump, a header sentence naming the row it closed, and a
body change that matches. Two rows (prior 22, 23) were deliberately *not* closed and were
instead disclosed in-rule with the reason — `security-sensitivity.md` `0.5.0` states the MX
demotion is *"deliberate, not a defect"* and warns against the obvious fix because GHI #682
is undischarged. Naming a conflict you have decided not to close is a legitimate outcome and
is scored here as a severity downgrade, not a retirement.

## Top blocking rows

Only four rows scored `blocking` this run (down from twelve). The fifth entry below is the
highest-leverage `episodic` row, included because the top-5 slot is more useful filled than
padded.

1. **R02 — `governance-core.md` § Required workflow order vs `AGENTS.md` § OBPI Acceptance
   Protocol (pipeline mandate).** *New.* The highest-leverage row in the matrix, for the same
   structural reason prior row 14 was: `governance-core.md` frontmatter is `paths: "**/*"`,
   so it loads on every edit in every session. Its six-step manual sequence carves out defect
   fixes but not contract-bearing OBPI work, and its step 3 (*"Implement one OBPI increment"*)
   trips `.claude/hooks/pipeline-gate.py:160` at exit 2 — while `AGENTS.md:228` calls freeform
   implementation of such an OBPI *"a process defect"* and Never #6 forbids working around a
   hook block. The rule routes the agent into the block. The hook's scope is also **wider**
   than the mandate it enforces: it fires for every governed OBPI, not only contract-bearing
   ones, so `AGENTS.md` under-describes its own gate.

2. **R01 — `chores.md` vs `skill-surface-sync.md`, the canonical chore surface.** The only
   2026-07-16 blocking row left entirely unaddressed — neither remediation commit touched it,
   and both files have since moved for unrelated reasons (`322f07473`, `a58d01126`). Not
   merely disagreeing prose: two live code paths run in opposite directions
   (`sync_surfaces.py:771-781` `.gzkit -> src/`; `chores.py:501` package -> `.gzkit`), so
   whichever surface the agent edits, the other rule's prescribed command silently reverts it.
   `gz validate --chores-layout` and `--distribution` both exit 0; the drift is invisible.

3. **R05 — `AGENTS.md` § PRIME DIRECTIVE 4 vs § Defect-fix routing.** Unchanged since the
   prior run; the one-line qualifier was never added. `grep -in "allowed.paths" AGENTS.md`
   returns zero hits, so an agent expanding scope mid-OBPI has nothing in the PRIME DIRECTIVE
   pointing it at the routing thresholds 250 lines away. Resolved *against* the PRIME
   DIRECTIVE in code (`orphaned_implementation.py:59`).

4. **R06 — `model-selection.md` vs `CLAUDE.md` § Opus tuning.** Unchanged, and now widened.
   `medium` is still absent from model-selection's four-value enum; `model-selection.md`'s
   `paths:` still exclude general sessions, so the rule that would resolve the conflict is the
   one that does not load when subagents are dispatched. **New this run:** both surfaces are
   pinned to a superseded model generation — the `CLAUDE.md` heading still reads *"Opus 4.7
   tuning"* (untouched since `8deb53b1b`) and `model-selection.md:72` still uses
   `claude-opus-4-7` as its worked example of a forbidden hardcoded id.

5. **R04 (episodic) — `task-discovery.md`'s GHI #731 auto-stamp vs its own § Layer-drift
   fail-close.** The only row in this matrix **created by a fix**. Closing prior rows 20/21
   exposed a producer-side gap; the producer-side patch (`4b9db7592`, the newest change to
   the whole audited surface) stamps `Task:` trailers from runtime state, so the commit-trailer
   channel now agrees with the runtime TASK set *by construction* — erasing the divergence
   signal § Layer-drift declares load-bearing. The rule concedes it in four words
   (*"Witness status unruled"*) and **GHI #731 is still open**.

## The pattern under this run's rows

The 2026-07-16 run's diagnosis was *"prose describing code that no longer exists."* Twelve of
those rows were fixed by making the prose match. This run's residue is a different shape:

**Rules asserting an enforcement that was never built, or that was deliberately removed.**

- R16 — `agents-md-map-doctrine.md` says growth past 32,768 B *"fails the default gate closed"*;
  the witness docstring says *"Never fail-closed (2026-07-06 ruling)"* and the enforced budget
  is 50,000.
- R09 — `tool-skill-runbook-alignment.md` Invariant 3 binds a skill Output Contract enum that
  does not exist: `.gzkit/schemas/skill.schema.json` has no `output_contract` property at all.
- R11 — `skill-surface-sync.md` #2 binds *"every edit"* under `.gzkit/rules/**`, and its
  mechanical arm (`rule_version_markers.py:78-80`) iterates `.md` only, so the `.json` sibling
  escapes entirely.
- R15 — `security-sensitivity.md` § Do Not forbids an edit whose only mandated path
  (`AGENTS.md` operator canon direct-fix) has no declaration channel; the nominated
  `Sensitivity:` trailer is unimplemented.
- R07 — `pythonic.md`'s function/module limits are enforced by nothing, and the canonical
  table's length bands have no consumer (`complexity_advise.py:126`, `metrics_checked = 1`).

Three of these five were *authored* as binding claims about mechanisms, not as rules about
behavior. A rule that describes a gate is a rule that goes stale silently, because nothing
re-reads it when the gate moves. **The generalizable fix is to stop writing enforcement
claims into rule bodies and instead point at the validator by flag name** — a pointer breaks
loudly (`--cli-alignment` would fail), a paraphrase does not.

## Off-matrix defects found on the audited surface

These are defects, not rule-pair contradictions, so they were deliberately kept out of the
matrix rather than padding it. All are trackable per `AGENTS.md` PRIME DIRECTIVE 6.

1. **`gz validate` exits 1 today on `.gzkit/rules/mx-mode.md`** — `marker=1.0.1 disagrees
   with block quote=1.0.0`. Introduced by `e2d38c3c0` (2026-07-24), whose own commit body
   claims *"mx-mode.md (rule 1.0.0 -> 1.0.1)"*; the HTML marker was bumped, the visible block
   quote was not, and no rationale sentence was written. This breaks `skill-surface-sync.md`
   § Conflict resolution, which makes the version *"the primary signal"* — the same file now
   answers `1.0.0` and `1.0.1` to that question. **Highest-priority follow-up: this is a red
   gate, right now.**
2. **`gz check` cannot see defect 1.** `rule_version_markers` is registered as a `"default"`-
   mode scope (`validate_cmd.py:366-368`), i.e. it fires on a bare `uv run gz validate` — but
   `gz check` never runs a bare `gz validate`; every `run_command("uv run gz validate --...")`
   in `src/gzkit/quality.py` passes an explicit flag, and the step list at
   `src/gzkit/commands/quality.py:438-490` has no rule-version-markers step. So `gz check` is
   green on a rule file `gz validate` exits 3 on. This is `control-surface-rule-vs-check-drift`
   territory but is recorded here because it is why defect 1 survived eight days.
3. **Root-relative doc links that do not resolve from the rule's own directory.**
   `.gzkit/rules/AGENTS.md:27`, `agent-failure-modes.md:29`, and `complexity-thresholds.md:93`
   and `:99` write `](docs/governance/...)`, which resolves to `.gzkit/rules/docs/...`. Sibling
   rules correctly use `](../../docs/...)`. The link targets all exist at the repo root; the
   references are simply mis-rooted.
4. **`allowNetwork` is declared and read by nobody.** `src/gzkit/chores/registry.json:11-13`
   carries `"allowNetwork": false` for the lite lane; `grep -rn "allowNetwork" src/gzkit
   --include=*.py` returns zero readers. `chores.md` § Core Principles states the prohibition
   as binding.
5. **`tests.md` overstates the smoke gate to adopters.** § General Rules says `gz smoke` is
   *"Enforced by that verb (exit 3 on breach or on an empty tier)"* unconditionally;
   `src/gzkit/commands/smoke_cmd.py:38-48` returns `_EXIT_OK` unless `.gzkit.json` declares
   `smoke.required`, whose default is `False` (`src/gzkit/config.py:161-168`, deliberately —
   the dogfooding-leak reasoning at GHI #607). Invisible in-tree because this repo declares
   `"required": true`. An adopter reading the shipped rule believes a gate is armed that is
   not. Related: `smoke_cmd.py:76-77` tells the operator the full unit tier *"has its own,
   larger budget"*, which `tests.md` § General Rules explicitly denies (*"Full unit tier: no
   fixed ceiling"*).
6. **`cli.md`'s rule-version marker sits after the H1**, not *"immediately after the
   frontmatter"* as `skill-surface-sync.md` #2 requires. `_MARKER_RE` is a bare `search()`
   with no positional constraint, so the sub-clause has no mechanical arm. Cosmetic.
7. **`.claude/settings.local.json` permits `Bash(gh issue:*)`** — the permission surface
   allows the invocation `AGENTS.md` Always #13 forbids as a direct agent call, and no hook
   intercepts it (`grep -rn "gh issue" .claude/hooks/` -> zero hits across 15 hooks). This
   belongs to `control-surface-permission-consent-drift`; noted here for cross-chore routing.

## Prioritized follow-up

Operator canon: a GHI-tracked repair routes to direct fix; never spin up an ADR/OBPI to
discharge one. Sizes are measured against `AGENTS.md` § Defect-fix routing thresholds.

| # | Route | Target | Edit summary | Rows | Size |
|---|---|---|---|---|---|
| 1 | direct-fix | `.gzkit/rules/mx-mode.md` | Align the visible block quote to `1.0.1` and write the missing rationale sentence. **Turns a currently-red `gz validate` green.** | off-matrix 1 | 2 lines, 1 file |
| 2 | direct-fix | `.gzkit/rules/governance-core.md` § Required workflow order | Add the contract-bearing branch pointing at `gz obpi pipeline` before step 1 | R02 | <=6 lines, 1 file |
| 3 | direct-fix | `.gzkit/rules/chores.md` + `src/gzkit/chores/README.md` + `commands/chores.py` | Delete the two surface tables -> pointer to `skill-surface-sync.md` § Surface layout; fix or rename `_repair_damaged_doctor_slug`'s direction | R01 | ~100 lines, 3 files |
| 4 | direct-fix | `AGENTS.md` § PRIME DIRECTIVE 4 | One-line Allowed-Paths qualifier routing cross-boundary fixes to § Defect-fix routing | R05 | 1 line, 1 file |
| 5 | direct-fix | `CLAUDE.md` + `.gzkit/rules/model-selection.md` | Split scopes (main-session effort vs dispatched-subagent effort); reconcile `medium`; retire the `Opus 4.7` / `claude-opus-4-7` generation pins | R06 | <=10 lines, 2 files |
| 6 | direct-fix | `.gzkit/rules/agents-md-map-doctrine.md` § Budget + § Shape enforcement | Drop the false fail-close claim and the hard-coded `32768`; delete *"forthcoming"*; state the actual template/rendered audit split | R16, R17 | <=10 lines, 1 file |
| 7 | direct-fix + mech-promotion | `.gzkit/rules/chores.md:141` + `trust_audits/cli.py` | Drop the `gz-` prefix; add `.gzkit/rules/**/*.md` to `_manpage_alignment_sources` so the rule surface is inside its own binding | R03 | <=5 lines, 2 files |
| 8 | direct-fix | `src/gzkit/commands/quality.py` step list | Add a rule-version-markers step so `gz check` sees what `gz validate` already catches | off-matrix 2 | <=5 lines, 1 file |
| 9 | resolve-then-fix | `.gzkit/rules/task-discovery.md` under **open GHI #731** | Rule the witness status: mark stamped trailers distinguishably, or scope § Layer-drift off the producer-coupled channel pair | R04 | <=10 lines |
| 10 | direct-fix | `.gzkit/rules/tests.md` § General Rules | Qualify the smoke arm with `smoke.required`; drop the "larger budget" claim from `smoke_cmd.py` | off-matrix 5 | <=6 lines, 2 files |
| 11 | mech-promotion | `.gzkit/schemas/skill.schema.json` | Add `output_contract` with enum `{table, tree, plain, prose}` so Invariant 3 has an arm | R09 | schema + validator |
| 12 | direct-fix | `.gzkit/rules/models.md`, `.gzkit/rules/complexity-thresholds.md`, `AGENTS.md` § Lane Rules | The three one-line cross-reference/scope sentences carried unapplied since 2026-05-11 | R13, R11, R10 | <=3 lines each |
| 13 | escalate | `pythonic.md` / `complexity-thresholds.md` / xenon hook | One threshold authority. Needs a class-size corpus band that does not exist — a `gz-complexity-distill` pass, not a prose edit. Surface routing facts to the operator | R07 | larger |
| 14 | direct-fix | `.gzkit/rules/complexity-thresholds.json` | Null the `corpus_percentile` on the six bootstrap rows so the data stops asserting a corpus fact GHI #404 denies | R08 | 6 lines, 1 file |
| 15 | housekeeping | 4 rule files | Re-root the `](docs/...)` links to `](../../docs/...)` | off-matrix 3 | 4 lines |

## Stability commitment (replacing the retired +/-2 band)

The 2026-07-16 run retired the prior *"+/-2 rows absent a doctrinal shift"* commitment on the
grounds that the matrix measures *reader thoroughness against a moving surface*, not a stable
population, and that a tight expected-variance band creates pressure to under-report. That
retirement stands.

**The replacement commitment is directional, not numeric:** a re-run must account for every
prior row as `retired` (naming the commit that closed it), `carried` (with a re-opened
`file:line`), or `refuted` (with the verification that falsifies it). A row that silently
disappears between runs is a defect in the run, regardless of the total. This run accounts
for all 25 prior rows: 12 retired, 12 carried, 1 refuted.

## Audit posture

- **Lane:** Lite — audit-only. **This run edited exactly four files, all under
  `.gzkit/chores/control-surface-rule-conflicts/proofs/`:** `rule-inventory.md`,
  `conflict-matrix.md`, `summary.md`, `rule-line-counts.txt`. (`rule-surface-listing.txt` was
  regenerated and came out byte-identical.) No rule, skill, schema, hook, or source file was
  touched; every command run against the repository was a read verb (`git log`, `git show`,
  `grep`, `gh issue view`, `uv run gz validate --*`).
  **Working-tree note for whoever commits this:** other paths show as modified in
  `git status` — the three sibling `control-surface-*` chores' proofs, and two
  `handoff_resume_authorized` lines in `.gzkit/ledger.jsonl` written by the session-start
  hook. Neither came from this run. Stage this chore's four files deliberately; do not
  `git add -A`.
- **Scope discipline:** only pairs with a concrete worked example were admitted. Five
  candidates were dropped for failing that bar — including one (`mx-mode.md` *"do not exit
  the hangar while any detectable defect remains"* vs `AGENTS.md` PRIME DIRECTIVE 6) where no
  reader could construct a case in which the two prescribe opposites, and one
  (`tests.md`'s smoke claim) whose counterparty is the code rather than another rule, which
  routes it to § Off-matrix defects instead.
- **Convergence:** R03 was found independently by two readers, which is the confidence signal
  the fan-out exists to produce. Single-reader rows carry correspondingly less.
- **Mirror control:** all 25 mirrored rules were diffed against `.claude/rules/`; every
  difference is the expected frontmatter transform plus the generated-file banner. No mirror
  was audited as a source, per CHORE.md § Policy and Guardrails.
- **Evidence resolution:** every row carries a GHI number, a SHA, or both, each verified this
  run (`gh issue view`, `git log -1`). The mechanical witness is
  `check_evidence.py --offline` -> `matrix valid: 17 row(s), all evidence resolves`.
