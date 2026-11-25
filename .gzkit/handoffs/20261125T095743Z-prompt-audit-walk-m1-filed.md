---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-25T09:57:43Z'
agent: claude-code
session_id: 85e9de78-a6bf-450d-9238-7c154aa3d5fa
continues_from: .gzkit/handoffs/20261125T073749Z-conceptual-model-rnd-ghi-discrepancy.md
---

## Current State Summary

This session (85e9de78) resumed from 20261125T073749Z-conceptual-model-rnd-ghi-discrepancy.md. Instead of ruling on that handoff's step 1, the operator called for a prompt audit of the Claude Code configuration, run as /doctor prompt-audit against Opus 5.5 across root CLAUDE.md and AGENTS.md, 23 nested AGENTS.md files, ~/.claude/CLAUDE.md, 27 rules, 74 skills, 5 agents and 1 command, with the codex and astral plugins report-only. The audit returned 47 High and 64 Medium findings. The operator then walked it systematically to effect repairs.

The walk reopened the conceptual-model R&D (docs/rnd/conceptual-model.md) at its next item, family, using the audit as its test case. That R&D is still in diamond 1 and not closed. Decisions recorded this session:
- a discrepancy is one failure mechanism, and family groups discrepancies across GHIs;
- family is a reading, never stored on the GHI;
- a failure mechanism is drawn per source change, and its reach is every consumer of the changed fact repo-wide;
- last_reviewed records a review, never an edit.
The *what it is* group is closed: class and found are stored, and the failure mechanism lives in the body.

Applied to the audit, these rulings give 51 failure mechanisms, one GHI each, M1 to M51. They are in the landed report docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md (Revised mechanism map, plus three added sections), with the proposed diff beside it. The wording and narrative findings went to RP-7 as comments on GHIs #1246, #1250 and #1251.

Execution is one mechanism at a time: file through ghi-author, repair, independent review, close. Only M1 is done. It was filed as GHI #1357, listing 11 ungated validate scopes canon names as binding beyond F2's five. RP-7 placement finding F2 is extended to cite it, and #1357 stays open until RP-7 wires the scopes onto a gate.

8 commits since the predecessor's anchor 51bcb34c5, from 323d0f8ff to 0a8d3b60c, all on main.

## Important Context

Safe mode is still open under docs/governance/harbor-pilotage-candidate-2026-10-15.md:
- Every act is one commit. A GHI fix commit is `fix(<scope>): … (GHI #N)` with a `Task: TASK-fix-<slug>-#N` trailer; drydock precedent, e.g. TASK-fix-provider-citations-#1338.
- Slow alarms are off, so no pre-push gz check runs; lint runs on every commit and push.
- The ledger is written only through gz verbs. Operator PII stays protected.

Repair mechanics:
- Edits go to canonical sources, never to the generated mirrors:
  - .gzkit/skills/<name>/ (mirrored byte-identical to .claude/skills and .agents/skills);
  - .gzkit/rules/<rule>.md (generates .claude/rules and every nested AGENTS.md);
  - root AGENTS.md changes go through the corpus with gz content remember / land, and need the operator's attestation words.
- After an edit, run uv run gz agent sync control-surfaces.
- Under the last_reviewed ruling, a skill repair bumps skill-version only and never last_reviewed. A rule repair bumps its rule-version marker and banner.
- Each mechanism's reach is every consumer of the changed fact: search the repo at repair time, not just the audited line.
- The pipeline's references/stage-*.md files are rendered from data/obpi_pipeline_control_inventory.json, so they change through a rewording row, not by hand.
- Close a GHI only after a reviewer that did not do the fix confirms it on the issue (AGENTS.md § Defect-fix routing).

ghi-author still carries the secondary labels (runtime and the others). The R&D retirement of those labels is diamond 2 and not in force, so #1357 was filed with defect and runtime.

Shift turnover, reviewed 2026-11-25:
- gz wp tag show --all reads "No tag has been issued.";
- gz wp runs reads "No work package is in flight.";
- gz obpi lock list shows mx-session as the only lock, 549 of 1440 minutes elapsed (lease renewed 2026-11-25 00:48);
- the buy-back record is not built, so no finding awaits buy-back by record.

The operator took the recommended option on most questions. Asked whether the questions were the right ones, the operator answered "questions are fine".

## Decisions Made

- [operator-ruled] Prompt-audit repair routing: High findings repaired now as defect fixes, Medium wording and narrative findings handed to RP-7 as stage input (verbatim: "Split (Recommended)").
- [operator-ruled] Family 1, ungated scopes canon calls gates: extend RP-7 placement finding F2 with one GHI listing the additional scopes, the text left until the wiring lands (verbatim: "Extend F2 (Recommended)").
- [operator-ruled] Family 2, Gate 5 described as lane- or mode-dependent: one new GHI citing #1188 and RP-7 F8 as siblings, fixed now (verbatim: "New GHI, fix now (Recommended)").
- [operator-ruled] The Split's 'one GHI per family' conflicted with the R&D's 'one discrepancy is one GHI'; the family axis is ruled first with the audit as test case (verbatim: "Rule family first (Recommended)").
- [operator-ruled] R&D: inside a GHI its failure mechanism, across GHIs family; 'class of failure' retired as a name (verbatim: "Two concepts (Recommended)").
- [operator-ruled] R&D: the questions put this session are the right ones (verbatim: "questions are fine").
- [operator-ruled] R&D: family is a reading with a locus, never stored on the GHI (verbatim: "Not stored (Recommended)").
- [operator-ruled] The 26-row mechanism map is revised before filing (verbatim: "Revise first").
- [operator-ruled] R&D: a failure mechanism is drawn per source change, its reach every consumer repo-wide (verbatim: "Per source change (Recommended)").
- [operator-ruled] Medium findings that state stale facts or conflicts are treated as High and repaired now (verbatim: "Treat as High (Recommended)").
- [operator-ruled] gz-adr-create's 'never propose a default' yields to AGENTS.md Operator Economy; folded into M36 (verbatim: "Economy rule (Recommended)").
- [operator-ruled] cli.md's help-path rule and pythonic.md's no-lazy-imports are reconciled by a third carve-out witnessed by tests/cli/test_help_path_imports.py; M46 (verbatim: "Third carve-out (Recommended)").
- [operator-ruled] The codex plugin's rescue agent defaulting to --write is left; read-only is named per dispatch (verbatim: "No action").
- [operator-ruled] R&D: last_reviewed moves only on a gz-skill-review pass that checked every claim, an edit moves skill-version alone, skill-surface-sync rule 6 rewritten; M47 (verbatim: "Review-only date (Recommended)").
- [operator-ruled] The mechanisms are executed one at a time: file, repair, independent review, close (verbatim: "One at a time").
- [operator-ruled] Write a fresh handoff and git sync (verbatim: "write fresh handoff so we can resume from here, git sync").
- [agent-chose] Routed flags canon already settles without putting them: ghi-author/ghi-close OBPI destination to M29; OBPIs as frozen history to RP-14; gz-mx PRIME DIRECTIVE text to M45 under the 2026-10-25 contract ruling; nested-AGENTS.md generator links to RP-7 F11; git-sync-repo agent to M21; CLAUDE.md Fable 5.1 lines to the frontier-model-card-currency chore; astral ruff's narrow-fix line to no action under the PRIME DIRECTIVE.
- [agent-chose] Added M49 to M51 (R18, R20, A4) under the Treat-as-High ruling after the operator's list of nine missed them.
- [agent-chose] Landed the audit report and diff under docs/rnd/conceptual-model/sources/, the R&D source convention excluded from the strict docs build.
- [agent-chose] Excluded --changelog from GHI #1357: its rule already states it runs outside gz check by operator choice.

## Immediate Next Steps

1. Put the cadence question still open: after each mechanism, report and continue, or stop for the operator's word.
2. M2 (Gate 5 lane- or mode-dependent): file through ghi-author citing #1188 and RP-7 F8 as siblings, then repair four surfaces: gz-obpi-pipeline SKILL.md:113 with the five references/stage-*.md through a rewording row in data/obpi_pipeline_control_inventory.json; gz-adr-create references/govzero-compliance-rules.md:35,39; .claude/agents/narrator.md:39; .gzkit/templates/obpi.md:130,245. Then an independent reviewer subagent, then close.
3. Continue M3 to M51 in map order from the landed report's Revised mechanism map and its three added sections, one full cycle each; check open GHI #1346 (gz-adr-closeout-ceremony paths) before filing M25, M28 and M40, since Step 0 may absorb them. M32 (AGENTS.md receipts fail closed on foundation kind) lands through gz content land and needs the operator's attestation words.
4. After the audit, resume the conceptual-model R&D frontier: the construction question, T37 and the sub-ids, the review of W44 to W50, then the disposition map, docs/rnd/conceptual-model/review.md and sign-off.
5. Carried asks: whether to open the DDD-discipline R&D run; whether to remove the two stale subagent worktrees under .claude/worktrees; whether to run the frontier-model-card-currency chore now, since the Fable 5.2 card is unconsumed.

## Pending Work / Open Loops

Open GHIs from this session:
- #1357 stays open until RP-7 wires F2's sixteen scopes onto a gate.
- M2 to M51 are not filed.

RP-7 holds the hand-off lists, posted as comments on #1246, #1250 and #1251.

Defects found outside the audit surface, each routed:
- the pipeline runbook's Exception mode → #1188;
- .gzkit/templates/obpi.md Gate 5 → M2;
- rnd-discipline.md:199 → M11;
- the content help text calling a receipt Gate 5 → M48;
- .gitattributes:14 § Never #2 → M11.

R&D diamond-2 consequences recorded and executed by nothing:
- ghi-author's Class of failure heading and ghi-close 7b meet the two-concept family ruling;
- the secondary labels retire.

Carried from the predecessor:
- the taxonomy walk is paused at W51;
- T31 to T36 and T39 are unruled;
- TestGhIssueCreatedAt hexagon-test findings;
- OBPI-0.39.0-01 and -02 briefs omit sensitivity;
- the bare PLC0415 suppressions, which M46 meets for the 16 parser sites.

## Verification Checklist

- uv run gz handoff resume, then read docs/rnd/conceptual-model.md from "decision · the run resumes at family" to its end.
- Read docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md: the Revised mechanism map and the three sections after it are the work list.
- gh issue view 1357, and grep -n '^| F2 |' docs/governance/harbor-ro7-placement.md shows the extension citing it.
- git rev-list --left-right --count origin/main...HEAD reads 0 0 after the sync.
- uv run gz obpi lock list shows mx-session as the only lock inside its 1440-minute lease.
- uv run gz wp tag show --all and uv run gz wp runs for the shift-turnover review.

## Evidence / Artifacts

- `docs/rnd/conceptual-model.md` (R&D record; the family, mechanism and last_reviewed decisions)
- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md` (audit report and mechanism maps)
- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25-proposed.diff` (proposed hunks)
- `docs/governance/harbor-ro7-placement.md` (F2 extended, citing GHI #1357)
- `.gzkit/insights/agent-insights.jsonl` (the operator rulings as insight records)
- Commits 323d0f8ff to 0a8d3b60c on main; GHI #1357; comments on #1246, #1250, #1251.

## Settled Rulings

2549 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
