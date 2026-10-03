---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-03T04:39:15Z'
agent: claude-code
session_id: 56a95300-b879-488f-9d07-2f5273115442
continues_from: .gzkit/handoffs/20261002T100215Z-canaries-all-reviewed-1161-filed.md
---

## Current State Summary

Since the predecessor: filed and fixed GHI #1162 and GHI #1161 (both ruled direct), measured why repair displaced feature work, drafted a campaign amendment, and ran a Codex sanity pass on it. GHI #1162: the handoff citation resolver and gz obpi status disagreed on short OBPI ids whose siblings are parked or withdrawn phantoms; both now share gzkit.artifact_prefix.active_prefix_matches; unknown citations fell from 87 of 90 to 3 (OBPI-0.29.0-01..03, genuinely ambiguous). Closed with 4b881d97f and c1257ebb6. GHI #1161: the canary review is now witnessed by a guard_canary_reviewed ledger event via the new human-act verb gz canary review; 20 existing reviews backfilled through it; the Edit(data/guard_canaries.json) allow rule removed; closed with 121f99576 and 75f33a003 after the red witness's eight survivors were dispositioned. The amendment draft r2 and its measurement scripts are committed as a dated evidence directory (d4e370d10); the operator has not ruled on it. All pushed except this handoff, which the git-sync after it carries.

## Important Context

The measurement re-cut matters more than the first framing: completions split foundation/feature are Apr 72/35, May 117/17, Jun 65/6, Jul 6/22, Aug 0/3, Sep 0/6, so the headline collapse is mostly the Foundation Sunset ending; all nine Aug-Sep completions are ADR-0.35.0 under the standing one-feature-at-a-time ruling; comparable retry signals (re-claimed locks, relaunched pipelines) rose from median 0/0 in July to 1/3 in Aug-Sep; fix commits doubled (Jul 178, Aug 289, Sep 302). The Codex pass (read-only, via the codex plugin) found that r1 mixed populations, read dead helpers as a missing gate, gave P1 a witness that cannot enforce it, defaulted P2 to retire against canon, and built P5 on standing obligations; r2 fixes each and records them. gz canary review is classified human-act under the GHI #1036 ruling, so --attestor is never defaulted. The red witness on a large commit takes over 30 minutes: run it with run_in_background and a 2-hour timeout or the harness kills it. Do not reuse .git/COMMIT_EDITMSG after a hook-refused commit: it held a stale git-sync message once this session (amended before push). The ledger-vocabulary hook reads the staged ledger, so a commit that introduces an event type must stage the rows that fire it. Evidence scripts under docs/ are linted by ruff.

## Decisions Made

- [operator-ruled] File a GHI for the handoff citation resolver (verbatim: "file the GHI for the resolver").
- [operator-ruled] Route GHI #1161 and GHI #1162 as direct repairs (verbatim: "#1161 and #1162 go direct.").
- [operator-ruled] Rethink why repair expanded while feature completions fell (verbatim: "yes, I think we really need to rethink why the last 4 months has greatly expanded fixes with far fewer features being completed").
- [operator-ruled] Measure the cost of one OBPI completion before drafting, and consider a periodic Codex sanity pass (verbatim: "measure #3 first, then draft the amendment (maybe we invite codex in occassionally to take a 'sanity pass' to ensure that gaps and blindspots are identified?)").
- [operator-ruled] Start GHI #1162 while Codex reviews (verbatim: "start #1162 while codex reviews").
- [operator-ruled] Revise the draft against the Codex review, then do GHI #1161 (verbatim: "1, then 2").
- [operator-ruled] Write the handoff and git-sync (verbatim: "write handoff, git-sync").
- [agent-chose] The phantom signal for short ids is parked OR withdrawn in the ledger graph; it matched the brief-on-disk rule on all 90 ambiguous ids.
- [agent-chose] gz canary review is a new noun group, classified human-act by the GHI #1036 criterion; a skill-alignment waiver with rationale was used instead of a new skill.
- [agent-chose] Session orientation calls guard_canary.unreviewed instead of keeping its own predicate.
- [agent-chose] The canary binding not covering the mutation text was recorded on GHI #1154 as a design question, not fixed under #1161.
- [agent-chose] The amendment draft r2 is persisted as a dated evidence directory marked DRAFT, NOT RATIFIED, on the f1-family-share precedent.

## Immediate Next Steps

1. Decision for you: rule on the campaign amendment draft r2 (docs/governance/completion-cost-2026-10-02-evidence/amendment-draft-r2.md), proposal by proposal: P1 completion-path additions come to you (advisory), P2 review post-June checks against the scorecard bar, P3 batch-initiate OBPIs and draw blocking GHIs only, P4 Introduced-by on GHIs, P5 bounded backlog check at 1.0 closeout, P6 periodic Codex sanity pass.
2. Decision for you: route the dead Step-4b verdict helpers and the five --adversary-* flags (obsolete code, not a missing gate; enforcement moved to the acceptance reducer in GHI #985 [settled]), correct gz-obpi-pipeline SKILL.md line 75, and amend OBPI-0.36.0-07's premise.
3. Decision for you on GHI #1154: whether every BEHAVIOR REQ designates one discriminator test, how canaries scale, and whether the mutation text joins the canary binding.
4. Decision for you: whether to start re-completion pipelines for OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02 and OBPI-0.35.0-09.
5. GHI #1155 remaining: measure the mechanism at the nine fix parents, and decide whether a mechanism should detect a claimed gate no production path calls.

## Pending Work / Open Loops

Open: GHI #1154 (now also carrying the mutation-not-hashed finding) and GHI #1155. The amendment draft r2 awaits ruling. The typecheck control runs uv run ty check . while the gz check step runs ty check . --exclude features. A QC rendition-lineage advisory (NCSurface.md/root owned-section) prints on every gz check; not investigated this session. A drafted Claude Code feedback item about the auto-mode classifier refusing an operator-ruled review is queued locally for the operator's /feedback. Carried: the tautological-test debt ceiling steps down monthly; the chore_decommission_processed emitter gap; the unfiled patch-release diff_only listing; trackers #611, #921, #978, #1028 and #799.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after git-sync; uv run python -c 'from pathlib import Path; from gzkit import guard_canary as gc; print(gc.unreviewed(Path(".")))': expect []; uv run gz handoff resume: OBPI-0.34.0-02, OBPI-0.35.0-09 and OBPI-0.36.0-07 render live, not unknown; uv run python -m unittest tests.commands.test_reference_checker tests.governance.test_guard_canaries tests.commands.test_canary_review: expect OK; uv run gz cli audit: expect 151/151 fully covered; gh issue view 1161 1162: expect CLOSED; jq .permissions .claude/settings.json: expect no allow key.

## Evidence / Artifacts

Commits 4b881d97f, c1257ebb6 (GHI #1162), 121f99576, 75f33a003 (GHI #1161), d4e370d10 (evidence). Files: `src/gzkit/artifact_prefix.py`, `src/gzkit/commands/reference_checker.py`, `src/gzkit/commands/common.py`, `src/gzkit/guard_canary.py`, `src/gzkit/commands/canary.py`, `scripts/session_orientation.py`, `docs/user/manpages/canary-review.md`, `features/canary_review.feature`, `tests/commands/test_reference_checker.py`, `tests/governance/test_guard_canaries.py`, `tests/commands/test_canary_review.py`, `docs/governance/completion-cost-2026-10-02-evidence/amendment-draft-r2.md`, `docs/governance/completion-cost-2026-10-02-evidence/README.md`. Receipts: arb-red-commit-4b881d97f000-f2dd58dd19f24eca897a54a87623dd72, arb-red-commit-121f99576884-315b27501cdc4e2fbf6ed7553923c04c. Predecessor: `.gzkit/handoffs/20261002T100215Z-canaries-all-reviewed-1161-filed.md`.

## Settled Rulings

1274 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
