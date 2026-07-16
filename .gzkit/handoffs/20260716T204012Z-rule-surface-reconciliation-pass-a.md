---
mode: CREATE
adr_id: ADR-0.0.20
branch: main
timestamp: '2026-07-16T20:40:12Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260716T003622Z-session-end-adr-0.0.65-validated.md
---

## Current State Summary

Session scope: the agent permission surface, then the rule surface it exposed. No OBPI was open; all work routed as GHI-tracked defect repair and chore runs per operator canon (a GHI is the work order and the receipt).

ADR anchor note: this session was not ADR-scoped. ADR-0.0.20 is the honest anchor because it owns the canonical-rule-surface invariant family — the validator landed here (`src/gzkit/validators/rule_version_markers.py`) sits in the same package as ADR-0.0.20's `unscoped_rules.py`, with the same shape and the same subject. The handoff schema requires an `ADR-X.Y.Z`; the Pass A chore's actual parent is `ADR-pool.control-surface-rule-pair-conflict-audit`, which the frontmatter validator rejects (pool ids are not semver-shaped).

FINAL STATE: tree clean, main synced with origin, `gz check` exit 0 (41 checks), `uv run -m unittest -q` exit 0 (7087 tests). Six commits landed: d330b2de, cd75f6fd, 6ecd29d8, 28449b3e, 3a4aacf3, 1ddb407d (plus sync commits 4ebb800d, dce3bd4b).

1. PERMISSION SURFACE. `.claude/settings.local.json` went 259 to 180 allow rules with no coverage lost (verified by a transitive-coverage check that caught a real bug mid-flight: two rules pointed at a parent that was itself being removed). Removed 3 inert `Write(...)` rules (only `Edit(path)` rules are consulted by the file-permission matcher), 73 subsumed or dead-in-practice rules, and 6 bare-Python grants that violated AGENTS.md section Execution Rules. Added 6 probe-verified deny rules to the COMMITTED `.claude/settings.json`: policy travels with the repo, convenience stays local. Every deny was proven by firing the command it forbids, including a `git -C <path> commit --no-verify` bypass that the first draft did NOT catch and would have shipped broken.

2. GHI #690 (CLOSED, fixed by 28449b3e). Permission allow rules can contradict AGENTS.md with no witness. Operator ruled the route: chore, not validator. Landed `control-surface-permission-consent-drift` as Pass D of the control-surface audit family. First run PASSED. It reports 0 live drift rows, and `proofs/unwitnessable.md` is a REQUIRED acceptance artifact recording 3 verified gaps the ledger structurally cannot see: `Bash(git *)` permits `git checkout -b feature/foo` against operator canon, `Bash(uv run *)` permits `uv run pytest`, `Bash(sed:*)` permits a direct ledger write against Never #2. The zero and the three coexist; the summary says so in as many words.

3. PASS A RE-RUN (4ebb800d, dce3bd4b). Full re-walk: 28 files, 214 section headings, 378 unordered pairs, fanned across 4 independent Explore agents each covering the whole surface from a disjoint focus set. 11 rows became 25 (12 blocking, 8 episodic, 4 theoretical, 1 refuted). Three rows found independently by 2+ readers.

4. RULE RECONCILIATIONS (3a4aacf3, 1ddb407d). Nine rules bumped: governance-core 0.5.0, gate5-runbook-code-covenant 0.2.0, gh-cli 0.3.0, adr-audit 0.2.0, cli 0.2.0, task-discovery 0.4.0, security-sensitivity 0.5.0, pythonic 0.2.0, brief-heading-conventions 0.1.0. All 25 Pass A rows discharged.

5. CLASS FIX. `gz validate --rule-version-markers` now enforces skill-surface-sync section Non-negotiable rules #2, which was binding and unchecked. 25/25 canonical rules carry an agreeing marker plus block quote. Verified failing closed on both violation types with real exit codes (not pipe-masked).

## Important Context

**The one thing to carry forward:** every layer inspected this session trusted a *description* instead of checking the *thing*, and every one of them looked green. Permission rules described commands they did not match (`Write(docs/**)` was inert; only `Edit(path)` rules are consulted). Rules described code that was deleted (ADR-0.0.36 collapsed attestation branching; three rule surfaces still described the branches). The Pass A audit described enforcement it never read (three mechanical-winner cells were wrong; one was dangerously wrong). The audit's own gate described a matrix it had stopped parsing at row 9 (`break` on a cell-count mismatch, reporting "8 rows, all evidence resolves" about a 25-row matrix). The handoff gate that wrote this document checks that sections are PRESENT, not populated — five of seven were empty headings and passed. Expect this shape; it is the house failure mode.

**Do not re-derive Pass A row 10.** It is retained in the matrix in `refuted` state specifically so a future reader does not re-discover the claim from the same misreading. There is no "Lane x Kind x Sensitivity matrix". `_requires_human_obpi_attestation` (`src/gzkit/commands/adr_audit.py:393-406`) is `return True`, unconditional. Its remediation was queued as a ready-to-apply direct fix that would have edited AGENTS.md Never #1 to make Gate 5 conditional.

**Non-obvious constraint — GHI #682 blocks the obvious fix for Pass A row 22.** `sensitivity` is absent from `GATE5_INVARIANTS`, so the sensitivity floor silently demotes to advisory inside the MX hangar. Promoting it looks correct and is a trap: #682 has two briefs currently failing that floor, and they are exactly what an operator enters the hangar to repair. The rule now says this out loud, including the "do not do this without first discharging #682" fence.

**Non-obvious constraint — the canonical threshold table has no class-size metric.** So "make `pythonic.md` cite the table" (the natural reading of `complexity-thresholds.md` § Invariant) would delete `--class-size`, the only enforced size gate in the repo. Three authorities disagree — pythonic (50/600/300), the table (`lizard_nloc` 37.0, `radon_raw_nloc` 1031.9), and the xenon hook (CC 11-20, matching neither). Resolving needs a corpus band that does not exist yet.

**`gh issue create` is load-bearing, not drift.** It is forbidden as a *direct agent invocation* (Always #13) but `/ghi-author` runs it at `SKILL.md:199`. The sanctioned and forbidden invocations are byte-identical strings. A prototype scan flagged `Bash(gh issue:*)` as a contradiction and was wrong; denying it would break the only sanctioned path for filing a GHI. `gh-cli.md` 0.3.0 now states that the prohibition is on the caller, not the string.

**Surface-editing discipline (hit live this session).** `.gzkit/rules/` is canonical; `.claude/rules/`, `.github/instructions/`, and `src/gzkit/rules/` are generated. Edit canonical, then `uv run gz agent sync control-surfaces`. Note `.claude/rules/chores.md` and `.claude/rules/skill-surface-sync.md` DISAGREE about which chores surface is canonical (Pass A row 12) — `sync_pkg_surfaces` (`src/gzkit/sync_surfaces.py:699`) reads only `.gzkit/ -> src/`, so skill-surface-sync is right and an edit made in `src/gzkit/chores/` is destroyed on the next sync. The prose is corrected; `_repair_damaged_doctor_slug` still runs the opposite direction.

**Verification discipline.** Never pipe a verifier through `tail`/`head`/`grep` — the shell reports the filter's exit, always 0 (tests.md § Verification exit-code integrity, GHI #589). This was violated in-session while verifying the new validator's exit codes; the deny rules read as exit 0 when they were exit 1. Capture to a file and read the real code.

## Decisions Made

DECISION 1: Deny rules go in the COMMITTED settings.json; allow rules stay local. Rationale: policy binds every clone, convenience is one machine's accumulated consent. Committing the allow list would export operator paths and session history to everyone. Rejected: leaving deny in settings.local.json, which enforced project doctrine (Never #10) from a gitignored file that no other machine or CI ever sees.

DECISION 2: Anchor the deny patterns on the dangerous FLAG, not the command shape. Rationale: `Bash(git commit *--no-verify*)` was proven broken by probe — `git -C <path> commit --no-verify` executed with hooks skipped, saved only by an empty staging area. `git` permits arbitrary global options before the subcommand, so prefix-anchoring cannot hold. `Bash(git *--no-verify*)` survives. Rejected: the subcommand-anchored form I originally shipped.

DECISION 3: `-n` stays narrow (`git *commit -n *`); do not broaden to `git *-n *`. Rationale: a broad form denies `git log -n 5` and `git tag -n`. Accepted gap: `git -C <path> commit -n` is not caught. A deny is a refusal, not a prompt — over-denial obstructs real work, and the asymmetry favors narrowness.

DECISION 4: Split `git *hooksPath*` into `git *hooksPath=*` plus `git *config *hooksPath *`. Rationale: the blunt form denied `git config --unset core.hooksPath` — the one command that REMOVES a bypass. A rule that blocks its own recovery path is worse than the hole it plugs. The discriminator is that dangerous forms carry a VALUE; reads do not.

DECISION 5 (operator ruling): route GHI #690 to a chore, not a `gz validate` scope. Rationale: validate carries 90 flags against an open campaign checkbox to collapse that surface (#618 residual), and the prototype's own result argued against gating — it produced exactly one finding and it was a FALSE POSITIVE. `Bash(gh issue:*)` is load-bearing: `/ghi-author` invokes `gh issue create` at SKILL.md:199, and Always #13 forbids it only OUTSIDE the skill. Sanctioned and forbidden are byte-identical strings.

DECISION 6: `proofs/unwitnessable.md` is a REQUIRED acceptance criterion, not documentation. Rationale: a run producing a drift ledger without a coverage-limits ledger advertises coverage it does not have. Documentation gets skipped; a failing acceptance criterion does not. This converts an honest caveat into a structural obligation.

DECISION 7: prior Pass A row 10 is REFUTED and its remediation MUST NOT be applied. Rationale: it asserted a "Lane x Kind x Sensitivity matrix [that] permits self-close for feature x lite x absent", citing `_requires_human_obpi_attestation` as that matrix. Verified at `src/gzkit/commands/adr_audit.py:393-406`: the function is `return True`, unconditional, docstring "the foundation/lane/security branching logic has been collapsed" (ADR-0.0.36). The row's remediation sat as item #3 in the prior run's prioritized follow-up list, marked direct-fix, ready to apply: reword AGENTS.md Never #1 to "when the matrix requires it". Applying it would have weakened Gate 5 to match deleted code, against ADR-0.0.36 and operator canon ("human attestation is sacrosanct and gold"). Its stated acceptance check ("the predicate is unchanged") was true and irrelevant. Row retained in refuted state so a future run does not re-derive the claim.

DECISION 8: `file:line` citation is now BINDING on the mechanical-winner cell. Rationale: rows 9, 10 and 11 all determined the winner by reading what a rule CLAIMS about enforcement rather than reading the enforcement. That is the exact failure the matrix exists to catch, occurring inside the matrix.

DECISION 9: retire the prior run's plus-or-minus-2 stability commitment. Rationale: the swing was plus 14 (11 to 25), seven times tolerance, which by the commitment's own terms is a finding. It presumes the matrix measures a stable population; it measures reader thoroughness against a moving surface, and a tight variance band pressures a re-run toward under-reporting rather than looking harder.

DECISION 10: do NOT promote `sensitivity` into `GATE5_INVARIANTS` (Pass A row 22). Rationale: GHI #682 is OPEN with two briefs currently failing the sensitivity floor. Fail-closing the scope would lock the MX hangar against the briefs an operator enters it to repair. The demotion is deliberate; the SILENCE was the defect. Named it in security-sensitivity.md instead, with an explicit "do not do this without first discharging #682".

DECISION 11: change NO number in pythonic.md (Pass A row 11). Rationale: three authorities disagree — pythonic (functions <=50, modules <=600, classes <=300), the canonical table (lizard_nloc blocks at 37.0, radon_raw_nloc at 1031.9), and the xenon hook (CC 11-20, matching neither). The table has NO class-size metric, so "just cite the table" would delete the only enforced size gate (`--class-size`, limit=300 hardcoded). Resolution needs a corpus band that does not exist. Named the conflict, routed the fix, guessed nothing.

DECISION 12: annotate `gh issue create` in gh-cli.md rather than delete it (Pass A row 13). Rationale: the invocation is load-bearing inside `/ghi-author`. The right answer was not to make the rule enforceable but to make it HONEST about being unenforceable — it now states that the prohibition is on the caller, not the string, and that nothing mechanical can tell them apart.

DECISION 13: the class fix belongs in a structural validator, NOT a governance test. Rationale: I first built it in `tests/governance/` specifically to avoid validate scope #91, and `gz validate --tautological-test-audit` flagged all three of its methods. tests.md section The discriminator is explicit — a test that greps a production doc proves content, not behavior; route it to the SUPPORT channel's structural validator. The repo's own doctrine overruled my campaign-cost reasoning, correctly. The campaign wants the validate ENUMERATION collapsed (#618), not all scopes forbidden; the registry it collapses to is where the new scope was added.

DECISION 14: preserve the #618 golden default order as a pristine snapshot. Rationale: it is EVIDENCE that the collapse dropped nothing. Appending a new scope to it would erase the boundary between what the collapse had to reproduce and what came later — the snapshot would silently stop being a snapshot. Added `_POST_SNAPSHOT_DEFAULT_ADDITIONS`; the assertion now proves the golden is a PREFIX of live order, so the migration proof holds while declared growth is admitted.

DECISION 15: re-derive three string-pinned tests rather than bump their literals. Rationale: `test_security_sensitivity_rule.py` pinned rule-version 0.4.0 while its REQ-0.0.22-06-01 still said 0.1.0 and the rule sat at 0.5.0 — three-way drift. The REQ's semantic is "carries a marker plus an agreeing block quote plus rationale"; the literal was the value at authoring time. A pinned literal fails every legitimate bump and PASSES if marker and quote drift apart at the pinned value. This is branch (b) of the adr-audit.md rule fixed earlier the same session.

DECISION 16: GHI #691 filed, NOT direct-fixed. Rationale: the intent test splits the class fix in two. `rule-version` marker enforcement was DECLARED binding by skill-surface-sync #2 with no mechanism, so it is a correction and routed to direct fix. `last_reviewed` for rules is a DELIBERATE prior exclusion ("skills only", clause #6) plus a `RuleFrontmatter` schema change, so it is new capability needing an operator route ruling.

## Immediate Next Steps

A handoff ADVISES; it does not authorize. Present these and obtain explicit operator authorization before executing any of them.

1. **Rule on GHI #691** (rules have no aging mechanism). The blocker comment carries three options: author a pool ADR and close `superseded`; fold into an existing ADR that owns the rule-surface contract; or `wontfix` on the grounds that `--rule-version-markers` plus the Pass A/B/C/D chore sweep is sufficient aging pressure. Agent preference recorded as option 1 with honest backfill dates and advisory-first enforcement. Not urgent — this closes the drift *rate*, not a live break.
2. **Decide whether to re-verify Pass A rows 1-8.** They were carried forward from the 2026-05-11 run WITHOUT re-verification and are authored under the same prose-not-code methodology that produced three defects in rows 9, 10 and 11. Treat as UNVERIFIED until each mechanical-winner cell is re-checked against a `file:line`. This is the highest-value unfinished work from this session.
3. **Consider re-running Pass B and Pass C.** Both last ran 2026-07-07 and were not re-run this session. Pass A's re-run found its own prior output partly false; the same methodology produced B and C.
4. **Work the campaign's topmost item** — the Foundation Sunset (`ADR-0.34.0`), whose Class-2 closeouts sequence before the capstone. Nothing in this session touched it; the campaign governs what is pulled next.

## Pending Work / Open Loops

- **GHI #691 — OPEN, awaiting operator route ruling.** New capability (`last_reviewed` for rules) against a deliberate exclusion plus a `RuleFrontmatter` schema change. Blocker comment posted.
- **GHI #682 — OPEN, and now load-bearing.** Two briefs currently fail the sensitivity floor. `security-sensitivity.md` 0.5.0 explicitly states that `sensitivity` must NOT be promoted into `GATE5_INVARIANTS` until #682 is discharged, because doing so would lock the MX hangar against the briefs an operator enters it to repair. Discharging #682 unblocks that decision.
- **Pass A rows 1-8: carried forward unverified.** See Immediate Next Steps #2.
- **Pass A row 11 (pythonic/threshold authority) — named, not resolved.** Three authorities disagree and the canonical table has no class-size metric. Resolution needs a corpus distillation pass (`gz-complexity-distill`), so it was routed rather than guessed. `docs/governance/advisory-rules-audit.md:70` separately miscodes rule 19 as "Mechanical | xenon complexity" — xenon measures cyclomatic rank, never line count; that Mechanical claim is unbacked and was not fixed.
- **Pass A row 12's code half.** `chores.md` prose was corrected, but `_repair_damaged_doctor_slug` (`src/gzkit/commands/chores.py`) still copies package to `.gzkit/`, the opposite direction from `sync_pkg_surfaces`. The prose no longer misleads; the two mechanisms still oppose each other.
- **Known permission-surface gaps (accepted, documented).** A commit message containing the literal `--no-verify` is refused (glob substring matching cannot distinguish mention from use); `git -C <path> commit -n` is not caught; `Bash(git *)` still permits `git checkout -b`.
- **`gz validate --rule-version-markers` exits 1, not 3** on violation. That is the generic registry-scope path; dedicated-runner scopes like `--unscoped-rules` return 3. Consistent with its registry siblings; noted, not chased.
- **This handoff's own gate is shallow.** `gz handoff create` accepts only `--summary` and `--decisions`; the other five required sections were written as empty headings and passed validation, because the gate checks section PRESENCE, not population. These sections were filled by hand afterward. That is the same defect class this whole session catalogued.

## Verification Checklist

```bash
# State at handoff time — all verified green before writing this document
git status -sb                      # clean, main level with origin/main
uv run gz check                     # exit 0 (41 checks)
uv run -m unittest -q               # exit 0 (7080+ tests)

# The class fix — fails closed on both violation types
uv run gz validate --rule-version-markers   # exit 0; 25/25 canonical rules
# NOTE: read the real exit code. Do NOT pipe through tail/head/grep —
# the shell reports the filter's exit, always 0 (tests.md, GHI #589).

# Pass A and Pass D chore state
uv run python src/gzkit/chores/control-surface-rule-conflicts/check_evidence.py --offline
# expect: "matrix valid: 25 row(s), all evidence resolves"
uv run gz chores advise control-surface-permission-consent-drift   # 5/5 criteria

# The claim that must NOT be re-derived (Pass A row 10 is REFUTED)
grep -A 14 'def _requires_human_obpi_attestation' src/gzkit/commands/adr_audit.py
# expect: `return True`, unconditional. There is no Lane x Kind x Sensitivity matrix.

# Open GHIs from this session
gh issue view 691 --json number,state,title     # OPEN — awaiting operator ruling
gh issue view 690 --json number,state,title     # CLOSED — fixed by 28449b3e
```

## Evidence / Artifacts

Rule surface (canonical; mirrors regenerated by `gz agent sync control-surfaces`):

- `.gzkit/rules/governance-core.md` (0.5.0)
- `.gzkit/rules/gate5-runbook-code-covenant.md` (0.2.0)
- `.gzkit/rules/gh-cli.md` (0.3.0)
- `.gzkit/rules/adr-audit.md` (0.2.0)
- `.gzkit/rules/cli.md` (0.2.0)
- `.gzkit/rules/task-discovery.md` (0.4.0)
- `.gzkit/rules/security-sensitivity.md` (0.5.0)
- `.gzkit/rules/pythonic.md` (0.2.0)
- `.gzkit/rules/brief-heading-conventions.md` (0.1.0)
- `.gzkit/rules/skill-surface-sync.md` (stale module path corrected)

Class fix:

- `src/gzkit/validators/rule_version_markers.py`
- `tests/validators/test_rule_version_markers.py`
- `docs/user/manpages/validate.md` (per-flag doc, GHI #350)

Chore output (the audit's evidence, and the reason for every rule bump above):

- `.gzkit/chores/control-surface-rule-conflicts/proofs/conflict-matrix.md` (25 rows)
- `.gzkit/chores/control-surface-rule-conflicts/proofs/summary.md`
- `.gzkit/chores/control-surface-rule-conflicts/proofs/rule-inventory.md`
- `.gzkit/chores/control-surface-permission-consent-drift/CHORE.md`
- `.gzkit/chores/control-surface-permission-consent-drift/proofs/unwitnessable.md`
- `.gzkit/chores/control-surface-permission-consent-drift/proofs/summary.md`
- `.gzkit/chores/control-surface-permission-consent-drift/proofs/consent-drift.md`

Permission surface:

- `.claude/settings.json` (6 deny rules, committed)
- `.gzkit/insights/agent-insights.jsonl` (course-correction record, Behavior Rule 11)

Re-derived tests and the checker:

- `tests/governance/test_security_sensitivity_rule.py`
- `tests/governance/test_chore_control_surface_rule_conflicts_evidence.py`
- `tests/cli/test_validate_registry_parity.py`
- `src/gzkit/chores/control-surface-rule-conflicts/check_evidence.py`
