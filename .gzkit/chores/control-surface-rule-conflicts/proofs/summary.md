# Conflict Matrix Summary — Pass A

> Chore: `control-surface-rule-conflicts` (Lite lane, audit-only)
> Date: 2026-07-16 (prior run: 2026-05-11, refreshed 2026-07-07)
> Inputs: `rule-inventory.md`, `conflict-matrix.md`

Full re-walk: **28 files, 214 section headings, 378 unordered pairs**, fanned across four independent readers each covering the whole surface from a disjoint focus set.

## Counts

| Severity | Definition | 2026-05-11 | 2026-07-16 |
|----------|-----------|------|------|
| `blocking` | Agent hits this monthly or more often; live mid-work surface | 1 | **12** |
| `episodic` | Hit during a specific ADR or change-shape class | 5 | 8 |
| `theoretical` | Pair could disagree on a misread; canonical reading reconciles | 5 | 4 |
| `refuted` | Prior row's claim verified false | — | 1 |
| **Total** | | **11** | **25** |

Pairs surveyed: 231 (22 files) → **378 (28 files)**. Files touched by ≥1 row: 11 → **19 of 28**.

## The prior run's stability commitment fired — surfacing it as required

The prior summary § Stability commitments states, verbatim:

> *"The matrix has 11 rows. A future agent re-running this audit should expect the row count to fluctuate by <=±2 absent a doctrinal shift; **any larger swing is itself a finding worth surfacing**."*

The swing is **+14 (11 → 25)**, seven times the tolerance. Per the prior run's own terms this is a finding. Its causes, in order of contribution:

1. **The prior walk was not exhaustive.** The surface grew 22 → 28 files (+27%), but rows grew +127%. Growth alone does not explain it. Nine of the fourteen new rows involve files that were *in scope* on 2026-05-11 and produced no row (`gh-cli.md`, `governance-core.md`, `adr-audit.md`, `task-discovery.md`, `mx-mode.md`, `security-sensitivity.md`).
2. **Three prior rows were wrong** (below), so the prior count was not merely low — it was partly false.
3. **The doctrinal shift the commitment excepts did occur**: ADR-0.0.36 collapsed attestation branching, and the rule surface was never reconciled to it (rows 15, 16 — and row 10's refutation).

**Recommendation: retire the ±2 stability commitment.** It presumes the matrix is a measurement of a stable population. It is not — it is a measurement of *reader thoroughness against a moving surface*, and a tight expected-variance band creates pressure to under-report on a re-run rather than to look harder.

## The prior run's rows were not merely incomplete — three were wrong

This is the headline, ahead of any new row.

| Row | Prior claim | Verified truth |
|---|---|---|
| **10** | *"The Lane × Kind × Sensitivity matrix permits self-close for `feature × lite × absent`"*, citing `_requires_human_obpi_attestation` as that matrix | `src/gzkit/commands/adr_audit.py:393-406` is `return True`, unconditional. Docstring: *"human attestation is UNIVERSAL … The foundation/lane/security branching logic has been collapsed."* **No such matrix exists.** |
| **9** | winner: `model-selection.md`; theoretical | winner: `CLAUDE.md`, by loading posture — model-selection's `paths:` exclude general sessions, so it never loads when subagents are dispatched. **Blocking.** |
| **11** | winner: `complexity-thresholds.md`, on the strength of its own *"one canonical table"* invariant | winner: `pythonic.md` — `--class-size` hardcodes `limit = 300` citing it, while the table's length bands have **no consumer** (`complexity_advise.py: METRIC_KEY = "radon_cc"`). **Blocking.** |

**Row 10 is the serious one.** Its remediation was not hypothetical — it sat as item #3 in the prior § Prioritized follow-up list, marked `direct-fix`, ready to apply:

> *"| 3 | direct-fix | `AGENTS.md` § Behavior Rules § Never #1 | Reword to "when the Lane × Kind × Sensitivity matrix requires it" | Row 10 | existing `_requires_human_obpi_attestation` predicate is unchanged |"*

Applying it would have weakened the agent contract to match deleted code, contradicting ADR-0.0.36 and operator canon (*"human attestation is sacrosanct and gold … WHEN I SAY ATTEST COMPLETED IT IS MOTHERFUCKING COMPLETE"*). Its stated acceptance check — *"the predicate is unchanged"* — is true and irrelevant: the predicate returns `True` for every input. **An audit actioned without re-verification would have injected doctrine drift into AGENTS.md via the audit itself.**

**Common defect in all three:** the winner was determined by reading *what a rule claims about enforcement* rather than *the enforcement*. That is precisely the failure this matrix exists to catch, occurring inside the matrix. **Binding on future runs: the mechanical-winner cell MUST cite a `file:line`.**

## Top blocking rows

1. **Row 14 — `governance-core.md` § Non-negotiable rules vs `AGENTS.md` Always #13 + #11.** Highest leverage in the matrix: `governance-core.md` is the **only** rule with `paths: "**/*"`, so it contradicts AGENTS.md in *every session, on every edit*. One bullet violates two rules — it hands agents `gh issue create --label defect` (Always #13 forbids) and names the raw `agent-insights.jsonl` path (Always #11 forbids).
2. **Row 12 — `chores.md` vs `skill-surface-sync.md`, canonical surface.** The row the prior run missed; hit live 2026-07-16. Not merely disagreeing prose — **two live code mechanisms run in opposite directions** (`sync_pkg_surfaces` `.gzkit → src/`; `_repair_damaged_doctor_slug` `package → .gzkit`), so whichever surface the agent edits, the other rule's prescribed command silently destroys it. Both validators exit 0; the drift is invisible.
3. **Rows 15 + 16 — stale lane-conditional attestation, in two grammars.** GHI #487 already caught this residue in a **template** and fixed it; the **rules** were never reconciled. `governance-core.md` contradicts *itself* two bullets apart.
4. **Row 13 — `gh-cli.md` § Allowed commands vs Always #13.** The topically-correct rule affirmatively sanctions the forbidden invocation, and ships in the wheel.
5. **Rows 11 + 17 — authority without enforcement.** `pythonic.md`'s size limits vs the threshold table (with a *third* ceiling in the xenon hook nobody's rules name); `cli.md`'s *"New Flag (Additive = Lite Lane)"* vs AGENTS.md's heavy-lane rule — where `cli.md` contradicts its own *"Heavy Lane Trigger: … flags"* header four sections above.

## The pattern under nearly every row

**Prose describing code that no longer exists.** `gate5-runbook` describes lane-branching deleted at ADR-0.0.36. `chores.md` describes a sync direction the code inverts. `pythonic.md` asserts limits nothing enforces. `adr-audit.md` prescribes a Gate-5 sequence that fail-closes at exit 3 on the ADRs it is written for. `task-discovery.md` presents an optional trailer anchor as mandatory, driving agents into a GHI-filing moratorium violation.

The rules are not wrong about *intent*. They are stale against *implementation*, and **nothing re-reads them when the code moves**. Three of the drifted files carry no `<!-- rule-version -->` marker at all (`adr-audit.md`, `pythonic.md`, `cli.md`), so `skill-surface-sync.md` § Non-negotiable rules #2 has no purchase on them.

## Prioritized follow-up (ready for ghi-author / direct-fix)

Operator canon: a GHI-tracked repair routes to direct fix; never spin up an ADR/OBPI to discharge one.

| # | Route | Target | Edit summary | Rows | Size |
|---|---|---|---|---|---|
| 1 | direct-fix | `governance-core.md` § Non-negotiable rules | Retarget tracking bullet to `/ghi-author` + `gz insights remember`; drop the Gate-5 lane conditional | 14, 16 | ≤10 lines, 1 file |
| 2 | direct-fix | `chores.md` + `src/gzkit/chores/README.md` + `chores.py` | Delete § Two-Surface Layout / § Authoring surface tables → pointer to `skill-surface-sync.md`; fix or rename `_repair_damaged_doctor_slug` | 12 | ~100 lines, 3 files |
| 3 | direct-fix | `gate5-runbook-code-covenant.md` | § Do Not → attestation universal; § Validation bundle → ARB-wrapped canonical invocations | 15, 19 | ≤20 lines, 1 file |
| 4 | direct-fix + mech-promotion | `gh-cli.md` | Annotate `gh issue create` skill-internal-only; promote a PreToolUse hook | 13 | ≤10 lines + hook |
| 5 | direct-fix | `adr-audit.md` | Add SUPPORT/STRUCTURAL-FENCE branch (c); ARB-wrap § Audit sequence; add rule-version marker | 18, 19 | ≤30 lines, 1 file |
| 6 | direct-fix | `cli.md` | Resolve the flags self-contradiction; retarget step 5 to `gz-patch-release`; add rule-version marker | 17, 25 | ≤20 lines, 1 file |
| 7 | direct-fix | `task-discovery.md` | Trailer anchor OPTIONAL; add ceremony form; cumulative-with-a-floor; bump 0.4.0 | 20, 21 | ≤15 lines, 1 file |
| 8 | escalate | `pythonic.md` / `complexity-thresholds.md` / xenon hook | One authority; repoint `audit_class_size`; derive xenon ceiling from the table | 11 | larger — surface routing facts to operator |
| 9 | direct-fix | `mx-mode.md` / `security-sensitivity.md` | Add `sensitivity` to `GATE5_INVARIANTS` or name the demotion explicitly | 22 | ≤10 lines |
| 10 | direct-fix | `security-sensitivity.md` § Registry contract | Name the direct-fix declaration channel | 23 | ≤10 lines |

Carried from the prior run, unchanged: rows 1–8's follow-ups (PD 4 qualifier, Lane Rules Gate 3 trigger, `complexity-thresholds` scope sentence, Output Contract enum, etc.).

**Struck from the prior follow-up list:** item #3 (reword Never #1). Row 10 is refuted; **do not apply**.

## What this audit does not produce

Per CHORE.md § Overview, Pass A is **audit-only**. No rule body, skill, or source file was modified by this run. The follow-up table is operator-fueled work routed individually through `ghi-author` or direct-fix.

## Coverage limits of this run

- **Prior rows 1–8 were carried forward without re-verification.** Their winner cells were authored under the same prose-not-code methodology that produced the three defects in 9/10/11. Treat as **unverified** until re-checked against a `file:line`.
- **Absence of a row is not evidence a pair is clean.** Two readers reported explicit control cases (`cross-platform.md`, `guardrail-feedback-prose.md` — checked, no conflict). Every other silent pair is unreported, not cleared.
- **Confidence tracks convergence.** Rows found independently by 2+ readers (9, 11, 12, 13/14) are strongest; single-reader rows carry correspondingly less. Row 12 was found by all three readers whose focus sets touched it.

## Audit posture

- **Lane:** Lite — no file outside `.gzkit/chores/control-surface-rule-conflicts/proofs/` was edited.
- **Scope discipline:** only pair-rows with a concrete worked example were admitted. One reader explicitly declined a row it judged speculative and offered it for overrule; a second reader found the same conflict independently with code evidence, and it was admitted as row 19. That disagreement-then-corroboration is the fan-out working as intended.
- **Evidence resolution:** each row carries a GHI number, a SHA, or a `file:line`. The chore acceptance gate (`check_evidence.py --offline`) is the mechanical witness.
