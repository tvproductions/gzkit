---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-26T08:29:17Z'
agent: claude-code
session_id: e54ebf70-4684-461a-9020-9751be91f430
continues_from: .gzkit/handoffs/20261126T074244Z-prompt-audit-m12-m14.md
---

## Current State Summary

Session e54ebf70 resumed from 20261126T074244Z-prompt-audit-m12-m14.md (ruling booked: "M15 now") and walked prompt-audit M15 (finding S29), filed as #1381. All work is on main and pushed.

#1381 is closed, CONFIRMED by an independent reviewer subagent after two rounds:
- 7223523d4: git-sync § Related Skills names gz-check, not the retired lint, test and format, in canon and in the packaged template src/gzkit/templates/skills/git-sync/SKILL.md. The witness is tests/policy/test_related_skills_resolve.py.
- eb211149f: ADR-pool.skill-behavioral-hardening re-targets its RED-GREEN-REFACTOR enrichment from the retired test skill to gz-check, with an amendments entry.
- 1c1116fd3: round-1 review found the witness read only backticked spans under an exact-case heading. It now reads bare, bold and table first-cell entries under any-case headings. The dead format waiver is removed, and the frontmatter waiver no longer credits the archived gz-adr-recon.
- 642311d66: a Related Skills line the witness cannot parse now fails it.

Filed: #1382 (CORE_SKILLS names retired gz-gates, nothing reads it, and its guard test skips deleted slugs). Evidence posted on #1110 (15 of 26 _NO_SKILL_VERBS waivers name wielded verbs) instead of filing a duplicate. Insights: bd5e3cc06, superseded by 585596e99.

The mx-session lease is ACTIVE at 187 of 1440 minutes. CI on 642311d66 was in progress at authoring; earlier runs were cancelled by later pushes.

## Important Context

Safe mode is still open (docs/governance/harbor-pilotage-candidate-2026-10-15.md). Every act is one commit with a Task: trailer.

Shift turnover, reviewed 2026-11-26:
- gz wp tag show --all: "No tag has been issued."
- gz wp runs: "No work package is in flight."
- gz obpi lock list: mx-session ACTIVE.
- The buy-back record is not built.

Mechanics learned:
- gz arb red grades a string literal in a dict as a guard and reports it undriven. A prose reason has no behaviour a test can drive; pinning its text is the string test tests.md forbids. ghi-close step 7c and tests.md conflict here; the operator ruled to disclose and route.
- scaffold_core_skills delivers every canonical slug and never reads CORE_SKILLS, so the dict is a dead public export bound by attested REQ-0.0.32-01-03 (ADR-0.0.32 is Validated, terminal).
- _collect_skill_verb_refs counts references/ files as wielding, so roles, task and covers read as wielded only from references.
- Related Skills sections vary in heading case and entry shape (backticked, bare, bold, tables), so a backtick-only reader misses real entries.
- A heredoc feeding one command and a fallback reading /dev/stdin hangs the fallback; write the body to a file and pass it with --comment "$(cat file)".

## Decisions Made

- [operator-ruled] M15 now (verbatim: "M15 now").
- [operator-ruled] The pool ADR's test-skill target moves to gz-check (verbatim: "Re-target gz-check").
- [operator-ruled] #1381 closes with its two undriven reason-string hunks disclosed and the dead-waiver check routed separately (verbatim: "Close, disclose, file (Rec.)").
- [operator-ruled] File the CORE_SKILLS finding, then a fresh handoff and git sync (verbatim: "yes, then frsh handoff + git sync").
- [agent-chose] The dead-waiver check went to #1110 as new evidence, not a new GHI: #1110 already holds that finding and closure contract.
- [agent-chose] The witness reads only the name opening each list item and a table's first cell, not descriptions, because later cells name non-skills (gz-tech-debt-review's pythonic class).
- [agent-chose] docs/design/briefs/SPEC-agent-capability-uplift.md:278 and the pool ADR's 2026-04-19 amendment prose stay as written, as dated records.

## Immediate Next Steps

1. Confirm CI on 642311d66 or its git-sync follow-up: check (ubuntu-latest) and check (windows-latest) should pass. full-strength-report stays red on the demoted hangar debt (#1262).
2. M16 in map order, per the Revised mechanism map in docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md: gz-arb revived 2026-04-14, findings S16 and S17 (gz-check:18-19 and 77-86).
3. RP-7's blocks-return-to-service line: the compression routine (gz-context-diet, the instructions-files-diet chore, gz content compose) must name and repair or record every consumer of a fact it moves or drops, with a witness, before RP-7 closes. Put its design to the operator before building.
4. Continue M17 onward in map order, stopping after each.

## Pending Work / Open Loops

- #1382 filed, not worked: CORE_SKILLS and its guard test; REQ-0.0.32-01-03 binds the export.
- #1110 holds the dead-waiver check; this session's re-measure is posted there.
- #1377, #1378 and #1380 are filed and open, not worked.
- #1370: the form of the prose fences; test_related_skills_resolve's root-exists check is one more instance.
- #1371: package copies are never byte-checked against canon.
- #1372: gz init's template stays on language: system.
- Insight 2026-11-26: skill links do not resolve from the package copy src/gzkit/skills/<name>/, and how a delivered skill should point at docs it does not ship is unruled.
- A broken link in a dated record, .gzkit/chores/control-surface-rule-conflicts/proofs/archive/2026-09-19/conflict-matrix.md:28, is left as written.
- docs/governance/advisory-rules-audit.md:616 (row 88) quotes the GHI ruling as AGENTS.md § Operator Doctrine inside a dated row; #1378 leaves the call to its executing agent.
- Carried: OBPI-0.35.0-20, pending, must name S5-016, S4-170, S4-045 and T-006 in its completing attestation; the active campaign plan's line 297 repeats the precedent claim inside a dated measurement; src/gzkit/sync_surfaces.py:155-160 writes the retired 50/600 thresholds; the reachability chore's below-the-bar findings are never routed; #1361, #1363 and #1365 filed, not worked; whether #1346 absorbs M25, M28 and M40; M32 needs the operator's attestation words; after the audit, the conceptual-model R&D frontier, the DDD-discipline R&D run, two stale worktrees under .claude/worktrees, and the frontier-model-card-currency chore.

## Verification Checklist

- gh issue view 1381 --json state: CLOSED; 1382: OPEN.
- uv run -m unittest tests.policy.test_related_skills_resolve: 9 tests OK.
- uv run gz validate --skill-alignment --surfaces: all passed.
- uv run gz obpi lock list: mx-session ACTIVE.
- gh run list --limit 4: CI on the newest main commit.
- git rev-list --left-right --count origin/main...HEAD: 0 0.

## Evidence / Artifacts

- `tests/policy/test_related_skills_resolve.py`
- `.gzkit/skills/git-sync/SKILL.md`
- `src/gzkit/templates/skills/git-sync/SKILL.md`
- `src/gzkit/governance/trust_audits/cli.py`
- `docs/design/adr/pool/ADR-pool.skill-behavioral-hardening.md`
- `src/gzkit/skills/__init__.py`
- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md`
- `artifacts/receipts/arb-red-commit-7223523d4dde-27787df6baab41c7b2f0ce27bfc21252.json`
- `artifacts/receipts/arb-red-commit-1c1116fd3df9-04838795ded449d3b841618edd2928a7.json`

## Settled Rulings

2584 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
