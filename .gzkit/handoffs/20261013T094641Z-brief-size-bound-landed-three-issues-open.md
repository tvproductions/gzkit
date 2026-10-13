---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-10-13T09:46:41Z'
agent: claude-code
session_id: 1c9a4ac3-6f57-4b4f-94f5-39bd08920161
continues_from: .gzkit/handoffs/20261013T090121Z-obpi-0.35.0-15-all-findings-filed-and-linked.md
---

## Current State Summary

This session did no OBPI work. It diagnosed why the ADR-0.35.0 briefs are oversized, filed four issues, and landed one structural fix.

- GHI #1196 is fixed and closed in 94ee376e4: `gz validate --brief-size` runs in `gz check` as the Brief size step and fails closed, exit 3, on a live brief past a bound on REQs, numbered requirements, allowed paths, contract bytes or total bytes. Bounds are in `src/gzkit/brief_size_bounds.json`; nine cutover ceilings are in `data/brief_size_grandfather.json`. The full gate passed on the landed tree (11798 unit tests, behave, docs build, canary sweep).
- GHI #1197 (the adr evaluate OBPI Size score cannot fail an oversized brief), GHI #1200 (the Stage 2 fix-cycle cap has no production caller and unblocks have no bound) and GHI #1210 (editing a completed brief writes an agent-attested receipt) are filed, open and unselected.
- An edit this session made to the completed brief OBPI-0.35.0-15 was backed out before any commit, with the two ledger rows it produced. That brief is as it was sealed.
- Nothing is in flight: no lock is held, no pipeline marker exists, the tree is clean and level with origin/main.

## Important Context

- THE OPERATOR'S JUDGMENT, verbatim: "the size of the adrs, opbis, and reqs is insanely high, these are not well decomposed"; "this runaway behavior is very unacceptable"; "we are not decomposing and modularizing enough - we are skipping 1970s-era best principles let alone today's". Treat these as the standing constraint on how the next brief is cut.
- A CONCLUDED BRIEF IS NOT CHANGED. Operator, verbatim: "the hook doesn't want the brief to be changed after the work is concluded". Editing a brief whose status is Completed through the Edit tool makes the post-edit hook append a completion receipt with an agent attestor, and the Receipt shape step then fails. Do not edit a terminal brief, and do not pick an edit path because a hook does not run on it. GHI #1210 carries the corrected contract in its first comment.
- The size bounds are the 95th percentile of the 523 terminal briefs measured at f588f570b. They are a dated record. Do not re-derive them from the current corpus: when OBPI-0.35.0-15 was sealed the contract-bytes percentile moved from 21804 to 22012, so every oversized brief that completes pushes a re-derived bound up.
- The ceilings hold OBPI-0.35.0-16 to -20, OBPI-0.35.0-09, OBPI-0.35.0-12, OBPI-0.34.0-02 and OBPI-0.36.0-09 at their size at landing. They do not force a split. Removing an entry is what forces it. A brief under a ceiling that grows by one byte on a ceilinged dimension fails `gz check`.
- Size does not detect a compound REQ. REQ-0.35.0-15-02 was 269 characters and was refuted nine times; it would pass the size check.
- An in-flight OBPI's acceptance digest hashes the whole source, tests, features, data, scripts, rules, schemas, workflows and config, and the parent ADR's normative body (`src/gzkit/acceptance_execution.py`, `_file_roster` and `_brief_contract`), independent of the brief's Allowed Paths. Any landing anywhere voids its proofs until `gz obpi complete`. GHI #1196 waited for OBPI-0.35.0-15 for that reason. Recorded as an insight; not filed.
- Negative-control decoys are inert under the claim runner, which passes any truthy result carrying the expected text. The brief-size refuse control filters in its entrypoint for that reason. Recorded as an insight; other decoy-bearing controls were not read.
- Workflow fronts (source: the active campaign plan, section Workflow fronts). ghi triage: four issues filed here, one fixed; the queue was not read as a whole. adr/obpi campaign: not worked; ADR-0.35.0 item 16 is next by the campaign order and its brief is over three bounds and under a ceiling. handoff system: used, not changed. new R&D: not touched.

## Decisions Made

- [operator-ruled] File the two size defects and record the insight (verbatim: "file both and record the insight - this is insanity"). Done as GHI #1196 and GHI #1197.
- [operator-ruled] File the missing fix-cycle ceiling as its own defect (verbatim: "yes"). Done as GHI #1200.
- [operator-ruled] Direct repair through issues is the route, and the fixes wanted are structural (verbatim: "direct fixes, via ghis, are fine, I need structural fixes that discipline gzkit's reliable behaviors").
- [operator-ruled] The five brief-size bounds and the cutover ceilings are ratified and the fix lands (verbatim: "ratify the bounds and ceilings, land it"). Recorded in both JSON files and in 94ee376e4.
- [operator-ruled] Back out the edit to the completed brief and the two uncommitted ledger rows it produced (verbatim: "1", the back-out option of three put to the operator).
- [operator-ruled] File the hook defect (verbatim: "file the hook defect"). Done as GHI #1210.
- [operator-ruled] A brief is not changed after its work is concluded (verbatim: "the hook doesn't want the brief to be changed after the work is concluded").
- [agent-chose] Built GHI #1196 in a detached worktree outside the repo while OBPI-0.35.0-15 was in flight, and landed it only after that OBPI completed. The worktree is removed.
- [agent-chose] Read "update brief" as adding GHI #1196, #1197 and #1200 to OBPI-0.35.0-15's Tracked Defects. That reading was wrong and the edit is backed out.
- [agent-chose] Offered to make the same edit by shell so the hook would not run. That would have worked around the control and is withdrawn.
- [agent-chose] Kept the bounds as measured before OBPI-0.35.0-15 was sealed and did not re-derive them at landing.
- [agent-chose] GHI #1210 was first framed as a producer writing a forbidden row; the framing is corrected in a comment after the operator's ruling.

## Immediate Next Steps

1. Present this handoff to the operator and take their ruling before executing anything. Confirm with git status --short, git rev-list --left-right --count origin/main...HEAD, uv run gz obpi lock list and uv run gz validate --brief-size.
2. Tell the operator that the two guard canaries for the claims brief-size and brief-size-grandfathered are bound in data/guard_canaries.json and unreviewed. Only the operator's words through gz canary review mark them reviewed.
3. Before OBPI-0.35.0-16 is initiated, put to the operator how briefs OBPI-0.35.0-16 to -20 are re-cut. Each is over a size bound and held by a ceiling, and the operator has said they are not well decomposed. Re-cutting edits the ADR-0.35.0 checklist and is the operator's to initiate.
4. Take the operator's rulings that the open issues wait on: for GHI #1200, what a run may do when it reaches the fix-cycle bound; for GHI #1210, whether any section of a concluded brief stays writable and whether the repair is ruled into OBPI-0.9.0-02 or worked alone.
5. If the operator selects GHI #1197, it is a direct repair that should read the bounds in src/gzkit/brief_size_bounds.json and not declare a second set.

## Pending Work / Open Loops

- GHI #1197, GHI #1200 and GHI #1210 are open and unselected.
- The two brief-size guard canaries are unreviewed.
- OBPI-0.35.0-15's Tracked Defects does not list GHI #1196 [settled], #1197 or #1200. Under the operator's ruling the brief is not edited; the links live on the issues.
- The whole-tree acceptance digest and the inert negative-control decoys are recorded as insights and have no issue. Whether either becomes one is the operator's call.
- Compound requirements have no mechanical witness. The cut of a brief along one module and its interface was discussed and nothing was built.
- The ceiling values are held against HEAD by a unit test, as the skill-body ceilings are; a raise committed with the unit tier skipped would not be caught.
- Registered worktrees named gzkit-red under the system temp directory and several under the Codex worktrees directory were seen in git worktree list. They are not this session's and were left alone.
- The first insight this session recorded says each fix-cycle escalation offered never a split; that rests on brief Open Design Questions 12 and 22 only, and a later insight corrects it.

## Verification Checklist

- git status --short prints nothing and git rev-list --left-right --count origin/main...HEAD prints 0 0.
- uv run gz validate --brief-size exits 0 and prints Validated: brief_size.
- uv run gz validate --receipt-shape exits 0.
- uv run gz obpi lock list prints No active locks.
- gh issue view 1196 --json state reads CLOSED; 1197, 1200 and 1210 read OPEN.
- git log --oneline --grep "GHI #1196" shows 94ee376e4.
- uv run -m unittest tests.governance.test_brief_size runs 26 tests and passes.

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/brief_size.py`
- `src/gzkit/brief_size_bounds.json`
- `data/brief_size_grandfather.json`
- `tests/governance/test_brief_size.py`
- `data/guard_canaries.json`
- `docs/user/manpages/validate.md`
- `docs/governance/GovZero/obpi-decomposition-matrix.md`
- `src/gzkit/hooks/core.py`
- `src/gzkit/acceptance_execution.py`
- `.gzkit/insights/agent-insights.jsonl`
- Commit 94ee376e4. Receipts: arb-ruff-f6d6505960834ab88b91c6e378730ed3, arb-step-typecheck-c7e4c7bfcb794c74a6a4d02b1101e8ed, arb-step-unittest-f5720067b6e04c55830d5d4ea245fd3f, arb-step-mkdocs-068098674495428d9d407f9906704096, arb-red-commit-94ee376e483b-bc348dd8af524b169954c11027b4de28 (verdict inconclusive: 24 killed, 0 survived, 17 not graded).
- Issues: GHI #1196 (closed), GHI #1197, GHI #1200, GHI #1210.

## Settled Rulings

1522 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
