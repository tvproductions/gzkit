---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-08T14:29:00Z'
agent: claude-code
---

## Current State Summary

This session audited what gzkit loads into an agent's context and placed the work in the open drydock as a change order on RP-7, the context cut. Everything is committed and pushed: origin/main is at `753e1b1b6`.

- Six-source audit of per-session load (root `AGENTS.md`, path-scoped rules, auto memory, hooks, session orientation, skill listing), recommendation in the `instructions-files-diet` chore's proofs.
- Band C (auto memory) done: 43 files archived outside the repository, `MEMORY.md` 7,798 to 428 B, and five ungoverned rules re-homed in canon (`git-sync` skill, trust-doctrine T4, `pipeline-orchestrator` persona, substrate § Prompt markup, `gz-plan-audit` Step 3a).
- A rule-retirement policy (`skill-surface-sync.md` 0.14.0, scorecard row 33d).
- A validity review of all 27 rules (455 clauses): KEEP 2, KEEP-PARTIAL 21, RETIRE 4; about 39 clauses stale, about half redundant.
- Stale clauses corrected in 18 rules (four commits); scorecard rows 28, 37, 38 and 39 re-scored Promotable, their mechanical-witness grandfather rows drained (65 to 61).
- The RP-7 change order of 2026-11-08 committed (`753e1b1b6`): placement as gate, chore or rule.

Phase: the change order is recorded; none of its five items is worked yet. Last action: push of eight commits, pre-push `gz lint` and `gz check` passed.

## Important Context

- The change order lives in `docs/governance/harbor-ro7-placement.md`; the contract carries § Rulings of 2026-11-08, RP-7's row note, nine list-of-discrepancies lines and a passage-log row; RP-7's specification has § Change order of 2026-11-08.
- The contract's work scope is frozen: a new finding is graded, never a new order. Grades in the record still read "(proposed)" as drafted; the operator's "Commit as drafted" (chore log, commit `753e1b1b6`) is what makes them stand.
- The change order supersedes RP-7 stage 1's "no binding clause is removed or reworded" for rules. The 18-rule stale fixes landed before it, a disclosed departure.
- `gz-obpi-pipeline` stage files are rendered from the attested `data/obpi_pipeline_control_inventory.json` (ADR-0.35.0, live briefs OBPI-0.35.0-17 and -20): never hand-edit them.
- `gz validate --bullet-retention` needs every pinned scorecard row's Rule cell verbatim in a per-turn surface (`.claude/rules` counts, a doc does not). A rule with scored rows cannot simply be deleted; a stub keeps the bullets unless the operator rules rows out.
- `prefer-lsp` falsely blocks text searches of command output; repeating the identical command passes.
- Another session (RP-12, mx-session lock holder `claude-code-f1ade346`) works in the same checkout and once swept this session's files into its commit `aca557bbf`. Its staged bookmark `.gzkit/handoffs/20261108T104501Z-session-exit-bookmark.md` was deliberately kept out of every commit here.
- Shift turnover (MX open): this session hung no tag-out tags and commenced no work package; no finding awaits buy-back. Read for this: `gz obpi lock list` (only the `mx-session` lock, held by the MX session) and the contract § List of discrepancies (RP-7 lines added this session, all `open`).

## Decisions Made

- [operator-ruled] Audit every source that loads into context (verbatim: "All six sources").
- [operator-ruled] Archive the auto-memory duplicates and stale files (verbatim: "Yes, archive all 27", "Yes, archive all 16").
- [operator-ruled] Personas lacking a version marker is a defect (verbatim: "they should, that is a shortcoming"), filed as GHI #1314.
- [operator-ruled] Rules get a retirement policy before any retirement (verbatim: "Yes, policy first").
- [operator-ruled] A rule with scored rows becomes a narrowed stub rather than vanishing (verbatim: "A: stub, core glob").
- [operator-ruled] Review every rule for validity before trimming (verbatim: "we just want to review all of these rules, how many are still useful and valid?").
- [operator-ruled] Restore hexagonal-architecture so it can be reviewed (verbatim: "yes, restore it so it can be reviewed").
- [operator-ruled] Fix stale clauses and review outcomes per batch (verbatim: "review each "batch" - the keeps, the keeps in part, the retires. fix what is stale. review the outcomes with me").
- [operator-ruled] Placement triage (verbatim: "we need to triage these rules and either: 1) gate, 2) keep as rule, 3) go to (or enhance existing) chore. Then, we need something that governs this decision in the future. Perhaps even a chore that evaluates all of the above and decides if they are placed correctly.").
- [operator-ruled] The placement principle (verbatim: "chores and gates are strong, rules and memory files are weak").
- [operator-ruled] Place the work in the open drydock (verbatim: "place the entire endeavor into the existing and ongoing drydock"), recorded as a change order on RP-7.
- [operator-ruled] Commit the capture with its proposed grades (verbatim: "Commit as drafted").
- [agent-chose] Hexagonal-architecture versioned 0.4.1 after the restore, so versions only rise past the reverted 0.4.0 stub.
- [agent-chose] Stale fixes landed one commit per batch, because each batch's rules share scorecard and history hunks.

## Immediate Next Steps

1. Present this handoff to the operator and book the ruling with `uv run gz handoff decide`.
2. Put held ruling H1 to the operator (hexagonal rule 1: narrow to the core, refactor deps behind ports, or grandfather), then H2 to H14 one at a time, recording each verbatim in the chore log and the change-order record.
3. Run change order item 1, the placement triage: for every TRUE and NEEDED clause in the four validity tables, propose gate, chore or rule with the named check or chore, and put the list to the operator by batch.
4. Draft change order item 2, the placement doctrine, for capture in canon beside the scorecard's Mechanical, Promotable and Judgment classes, and put its home to the operator.
5. Draft change order item 3, the placement-audit chore, as new or as an enhancement of `control-surface-rule-vs-check-drift` or `control-surface-validator-reachability`, for the operator's choice.

## Pending Work / Open Loops

- The 14 held rulings H1 to H14 and the 21 graded findings F1 to F21 in `docs/governance/harbor-ro7-placement.md`; F2, F3 and F4 are graded as blocking return to service.
- Change order item 4: root `AGENTS.md` (Band A, operator-only, blocked by finding F1, the compose invariant-floor failure), hooks and orientation, and the skill listing, placed by the same test.
- RP-7 stage 2 (nested `AGENTS.md` no longer generated) is ruled but not landed (F11).
- The "(proposed)" markers on the grades remain in the record; removing them is the operator's call.
- GHIs filed this session and still open: #1313, #1314, #1315, #1316, #1317.
- The RP-12 session's own handoff and its staged bookmark belong to that session.

## Verification Checklist

- `git rev-list --count origin/main..HEAD` and `git rev-list --count HEAD..origin/main` both read `0` at `753e1b1b6` or later.
- `uv run gz validate --advisory-scorecard --bullet-retention --documents` passes.
- `uv run gz check` passes (one advisory names the QC-binding fixture `NCSurface.md/root`, unrelated to this work).
- `git worktree list` shows no entry under `.claude/worktrees/`.
- `uv run mkdocs build --strict` exits 0.

## Evidence / Artifacts

- `docs/governance/harbor-ro7-placement.md` (the change-order record)
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (§ Rulings of 2026-11-08, RP-7 row, list of discrepancies, passage log)
- `docs/governance/harbor-ro7-context-cut.md` (§ Change order of 2026-11-08)
- `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md` (every ruling, verbatim)
- `.gzkit/chores/instructions-files-diet/proofs/recommendation-2026-11-08.md`
- `.gzkit/chores/instructions-files-diet/proofs/rules-reaudit-2026-11-08.md`
- `.gzkit/chores/instructions-files-diet/proofs/rules-validity-A-2026-11-08.md`
- `.gzkit/chores/instructions-files-diet/proofs/rules-validity-B-2026-11-08.md`
- `.gzkit/chores/instructions-files-diet/proofs/rules-validity-C-2026-11-08.md`
- `.gzkit/chores/instructions-files-diet/proofs/rules-validity-D-2026-11-08.md`
- `.gzkit/rules/skill-surface-sync.md` (§ Retirement policy for rules)
- `docs/governance/advisory-rules-audit.md` (rows 33d, 28, 37, 38, 39; Coverage Ledger)
- Commits: `df08d2a00`, `02745c673`, `b7b788144`, `77c3fed6e`, `c6f350e6a`, `6e6d35134`, `532a071b9`, `31372200c`, `f3469d334`, `a45dcb505`, `200c7dc02`, `e4fa52776`, `753e1b1b6`.
