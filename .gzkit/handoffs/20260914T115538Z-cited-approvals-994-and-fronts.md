---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-14T11:55:38Z'
agent: claude-code
session_id: 9e443c0b-4680-4f25-9e1d-a706ada4dcd6
continues_from: .gzkit/handoffs/20260914T102141Z-presence-shape-session-close.md
---

## Current State Summary

Session 9e443c0b resumed `20260914T102141Z-presence-shape-session-close.md` (ruling booked: proceed) and fixed GHI #994 in `3392c420d`, closed with evidence.

- The `gzkit.acceptance.review.v1` envelope now carries `grounds` (proof_id, repo-relative path or null for the proof's recorded evidence, verbatim excerpt). `record_review` checks every citation on new imports and refuses an uncited approval from a reviewer that cannot execute. That covers a persona with no shell in its frontmatter, and an unresolvable grant: no persona, two personas, a non-plain name, or a tool-override flag. Cross-vendor reviews are exempt. Replay never reinterprets history.
- An independent spec-reviewer pass returned PASS. Three of its non-blocking notes were members of the same mechanism (argv tool overrides, ambiguous or escaping `--agent`, body `tools:` line) and were fixed in the same commit.
- Mid-session the operator asked whether the chores and R&D fronts are still being worked. Answer from the rulings store: no. Both were set aside across four consecutive resume rulings while each resume recommended the next family-A member. Improvement insight recorded.

At authoring: HEAD `3392c420d`, fix committed but not yet pushed (git-sync follows this handoff), no OBPI locks, 42 open GHIs (search total_count).

## Important Context

### Campaign workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts, active per `data/active_campaign.json`)
- **handoff system:** no change. Insight recorded: resume recommendations have kept offering only the prior thread and set aside standing fronts.
- **ghi triage:** presence shape. #994 closed (`3392c420d`). #983 open, touched by PENDING ADR-0.35.0 briefs: OBPI-0.35.0-07 and -13 read `ownership.py` read-only; OBPI-0.35.0-10's REQs 01/02/04 consume corpus-owned status, so a loaded-ownership check would change what they read. The disposition of the 10 uncovered sections is operator-ruled. #894 open, awaiting its 2026-09-07 ruling (OBPI-0.35.0-08 IN PROGRESS). #1008 open, unselected. Queue 42.
- **adr/obpi campaign:** no OBPI work, no locks. ADR-0.35.0 TOPMOST unchanged. The Stage-2 review contract changed under #994: reviewers must now emit `grounds` for approvals, so the next operator-initiated OBPI pipeline run will exercise it for the first time.
- **new R&D:** not worked since `20260912T235557Z-rnd-alignment-chores-rnd-reconstructed.md`. Its step 4 (R&D skill design) and the promised campaign R&D-front amendment text are still undone.

### Chores front state (verified this session)
Revamp steps 5 and 6 landed by `20260913T150226Z`. Step 2 (`gz chores status` plus the orientation overdue announcement, GHI #936, OPEN) has been set aside in four resume rulings. Also open: #997, #808. `test-isolation-compliance` fails on two slow tests. Overdue chores: permission-consent-drift, rule-conflicts, skill-rule-reachability.

### Gotchas carried
- `.claude/agents/*.md` bodies are hand-maintained. `gz agent sync control-surfaces` renders only `.codex/agents/*.toml` from `.gzkit/agents/`; edit all three, and `tests/test_codex_roles.py` checks coherence.
- `run_mutation_sweep` needs `-v` on the unittest argv, or the baseline reads not-green. A should-import test must turn a refusal into an assertion failure (`self.fail`), or the mutant reads inconclusive.
- The verifier-pipe gate refuses `ruff` followed by another statement; read the exit status immediately after the verifier.
- Proof evidence reaches reviewers JSON-escaped; a reviewer copying escaped text verbatim is refused (fails closed, a usability cost only).

## Decisions Made

- [operator-ruled] Resume ruling on `20260914T102141Z`: "Fix #994 (Recommended)". #983 routing facts and the @enforces class declaration set aside.
- [operator-ruled] GHI #994 remedy: "Cited approvals (Recommended)" — structured `grounds` verified at import, must-cite for reviewers that cannot execute (grant read from `--agent`; unresolvable counts as cannot), cross-vendor exempt, forward-only. Stage-2-only and prompt-wording-only set aside.
- [operator-ruled] Session direction after asking whether the chores and R&D fronts were still being worked: "Finish #994 first". Chores step 2 and R&D skill design offered and deferred behind it, not declined.
- [agent-chose] Expanded #994 in the same commit to three members of the same mechanism that independent review surfaced: tool-override argv, ambiguous or escaping `--agent`, and the frontmatter-only grant read in `reviewer_capability`. Each is fail-safe and has a test.

## Immediate Next Steps

1. Put the next move to the operator with the standing fronts as live options, not only the presence thread: (a) chores-revamp step 2, `gz chores status` plus the orientation announcement (GHI #936); (b) R&D skill design per `20260912T235557Z` step 4, plus drafting the campaign R&D-front amendment for ratification; (c) the next presence or family-A member.
2. If (a): read `scripts/check_proof_freshness.py` and `docs/governance/chore-class-system.md` § Implementation order step 2 first; a new verb carries the seven obligations in `.gzkit/rules/cli.md` § New Subcommand.
3. If (b): read `docs/governance/mpas-appropriation-analysis.md`, `docs/governance/chore-class-system.md` and Thread 3 of `20260912T235557Z`; confirm or overturn the orchestrator-over-disciplines resolution; rule on `.out-of-scope/`.
4. If (c): #983 needs an operator ruling first (OBPI-0.35.0-10 overlap, disposition of the 10 uncovered sections); #894 stays awaiting its ruling; #1008 (verifier-pipe-gate grouping) is the unowned direct-fix candidate.

## Pending Work / Open Loops

- GHI #936, #997, #808 (chores); #983, #894 (presence, ruling-gated); #969 open by ruling; #968 open (reviewer read-only description vs grant); #1008 open, unselected.
- R&D: skill design session, campaign R&D-front amendment text, `.out-of-scope/` ratification.
- Insight still open: `src/gzkit/commands/obpi_stages.py` BASELINE_VERIFICATION prescribes `uv run -m unittest -q` rather than the canonical unittest step.
- Three live justify-binding violations await genuine walkthroughs (opt-in scope).
- 83 enforcement claims population-undeclared; 55 exemption-undeclared.
- #994 [settled] residual, disclosed in its close comment and not a defect: a citation proves the bytes exist, not that they support the approval; no dedicated symlink fixture (containment check covered by the escape mutant).

## Verification Checklist

```bash
git status -sb
gh issue view 994 --json state
uv run gz obpi lock list
uv run -m unittest tests.test_acceptance_grounds tests.test_review_capability tests.test_acceptance_store
uv run gz handoff rulings --search "Cited approvals"
```
Expected: branch level with origin/main after the sync that follows this handoff; #994 CLOSED; no active locks; tests green; the remedy ruling present in the store. Re-run rather than trust.

## Evidence / Artifacts

- `.gzkit/handoffs/20260914T102141Z-presence-shape-session-close.md` (predecessor).
- `src/gzkit/acceptance_grounds.py`, `src/gzkit/acceptance.py`, `src/gzkit/acceptance_store.py`, `src/gzkit/acceptance_context.py`, `src/gzkit/pipeline_dispatch.py`.
- `tests/test_acceptance_grounds.py`, `tests/test_acceptance_store.py`, `tests/test_review_capability.py`.
- `docs/user/manpages/obpi-acceptance.md`, `.gzkit/agents/spec-reviewer.md`, `.gzkit/agents/quality-reviewer.md`, `.claude/agents/spec-reviewer.md`, `.claude/agents/quality-reviewer.md`, `.gzkit/skills/gz-obpi-pipeline/SKILL.md`.
- `artifacts/receipts/arb-step-unittest-ff609549477540898f13d4c2b8ed5bd9.json`, `artifacts/receipts/arb-ruff-b61f8ddb57f840de8633246aa8625f47.json`.
- Commit `3392c420d`; GHI #994 close comment.

## Settled Rulings

860 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
