---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-23T20:40:05Z'
agent: claude-code
continues_from: 20260823T162759Z-session-exit-bookmark.md
---

## Current State Summary

Session opened as a routine `/git-sync` and found the local clone had no common ancestor with `origin/main` — `gz git-sync` reported ahead=2992 behind=3198. Diagnosis: this clone missed a whole-history `filter-repo` author rewrite (the `g0` authorship directive; root trees byte-identical, only author identity differs) that was force-pushed to origin. Local `main` was the orphaned pre-rewrite line stranded at 2026-08-16 while origin carried work through 2026-08-23.

Reconciled by adopting `origin/main` after proving all ten recent local commits were patch-id-identical to commits already upstream. Eight genuinely unique local files were preserved and committed as `a50937481`. Tags were force-resynced (all 35 named rewritten-away commits, which was failing `test_real_tree_documented_releases_are_clean`).

Then re-based the 2026-08-23 session-handoff tech-debt dossier, which had been authored inside that stranded clone and was therefore blind to seven days of repair. All twelve findings re-verified against current main; report, findings, scope note and a new verification probe committed as `38bb66e01`. Branch `main` is clean and synced at 0/0.

## Important Context

The rewrite is benign and already ratified: `AGENTS.md` records the operator directive that repo-bound authorship is `g0`, and the root trees compare byte-identical. Only commit identity changed, which is why every SHA moved and `git merge-base` returned nothing. A clone that misses such a rewrite looks exactly like catastrophic divergence and must not be resolved by force-push in either direction.

`git fetch --prune` does NOT update tags that already exist locally. That is why the version-release audit failed after the reset with 35 tags naming commits `origin/main` no longer contained; `git fetch --tags --force --prune-tags` is the cure.

The dossier re-base surfaced a rule that governs routing and is easy to miss. `AGENTS.md` Operator Doctrine says a shortfall against declared intent is a correction routed under the owning ADR, never a fresh pool ADR — but `ADR-0.0.65-handoff-system-consolidation` is status Validated, and a settled ruling in the carried corpus says residual scope from a Validated ADR is re-homed to a feature ADR, never appended to the closed one, because appending would drag it back to Pending and falsify an honest attestation. Both rules bind together: the work is corrective, and its home is a new feature ADR. Foundation is sealed by ADR-0.34.0, and the next free feature slot is 0.38.0.

The handoff surface has five open GHIs the dossier never accounted for, because four postdate the stranded clone. GHI #870 was filed the same day as the audit and already owns the lineage-traversal arm.

## Decisions Made

- [operator-ruled] Reconcile the stranded clone by adopting `origin/main` rather than force-pushing local over it or re-cloning (operator selected "Adopt origin/main" from three presented routes). Force-pushing local would have destroyed seven days of upstream work.
- [operator-ruled] Re-base the dossier against current repo state (verbatim: "update based on the current status of the repo (the evaluation was performed today, but yes, this local was significantly (1 week) behind)").
- [operator-ruled] Re-verify the dossier RECOMMENDATIONS, not only its evidence (verbatim: "okay, have we updated the dossier recommendations to be consistent with the current state of the repo?"). That correction found two wrong routes.
- [agent-chose] Proved local commits redundant by `git patch-id` comparison before any destructive step, rather than trusting commit-subject matching. All ten most recent local commits matched byte-for-byte upstream.
- [agent-chose] Pinned the pre-rewrite tip at branch `pre-rewrite-main-20260823` and copied the eight unique files to scratchpad before repointing `main`. Both remain in place and are disposable.
- [agent-chose] Force-resynced tags rather than deleting the failing assertion, since the audit was correctly reporting real tag breakage.
- [agent-chose] Raised the secret-screening finding from Medium to High on blast radius rather than on coverage breadth, because handoffs are committed to the repository and `CLAUDE.md` records a 2026-04-19 leak whose recovery cost a history rewrite plus force-push.
- [agent-chose] Recorded both wrong routing attempts in the dossier rather than silently overwriting them, because the second error is the instructive one.

## Immediate Next Steps

1. Triage the five open handoff GHIs before opening any new work: #870, #813, #767, #766, #851. Two dossier findings resolve into that queue, and #766 and #767 name handoff defects the audit never found.
2. Run the `skill-command-doc-parity` chore over the handoff CLI help, manpages, runbook, and `docs/governance/GovZero/session-handoff-schema.md:189`. The highest-value single fix is `src/gzkit/cli/parser_handoff.py`, which contradicts itself 51 lines apart — line 35 says the resume gate was retired, line 86 tells operators only proceed lifts it, and line 86 is published CLI contract.
3. Run the `skill-authoring-quality` chore for the three-way skill identity disagreement in `.gzkit/skills/gz-session-handoff/SKILL.md` and the secret-screening promise.
4. File the CREATE-collision GHI. Step 0 prior-art was run this session across all issue states and is clear; the nearest neighbour #859 [settled] is a different defect that already landed.
5. Decide whether to spend a new feature ADR-0.38.0 on the two contract gaps that need an ADR home, or defer. The active campaign is Magna Carta with Movement B topmost, and handoff work is not campaign work.

## Pending Work / Open Loops

- Five open GHIs on the session-handoff surface remain untriaged: #870, #813, #767, #766, #851.
- Two dossier findings need GHIs filed and are not yet filed: CREATE destination collision, and empty branch and agent identity on CREATE. Neither was filed this session because the dossier is diagnosis and filing was not authorized.
- The bearing projection finding needs an operator ruling on where advisory ends before it enters design. A four-verdict projection sits close to the resume gate retired 2026-08-15 on the operator ruling that a handoff should advise rather than gate.
- The archive retention question is unresolved by design: whether archive means isolated-entry retention or atomic closed-chain compaction. Re-measured unchanged at 11 movable, 87 lock-protected, 111 chain-protected.
- Branch `pre-rewrite-main-20260823` and the scratchpad file backups are still present and are now disposable.
- Whether `gz init --update` should re-seed the ledger merge driver on existing adopter clones is carried unresolved from the predecessor chain.

## Verification Checklist

```bash
git rev-list --left-right --count HEAD...origin/main   # expect 0 0
git status --short                                     # expect clean
uv run gz lint
uv run gz handoff rulings --search "Validated ADR"     # the re-homing ruling that governs routing
gh issue list --state open --limit 100                 # confirm the five open handoff GHIs
```

Focused handoff suite, re-measured at 246 passing:

```bash
uv run -m unittest -q tests.governance.test_handoff_api tests.governance.test_handoff_validation \
  tests.test_handoff_cli tests.governance.test_session_start tests.governance.test_handoff_selection \
  tests.governance.test_handoff_archive tests.governance.test_session_exit
```

Re-confirm the two Critical findings still stand before scheduling: `validate_handoff_document` should still resolve to exactly one call site inside `create_handoff`, and the write in `create_handoff` should still have no destination guard.

## Evidence / Artifacts

Re-based dossier, committed as `38bb66e01`:

- `.gzkit/audits/tech-debt/2026-08-23/report.md`
- `.gzkit/audits/tech-debt/2026-08-23/findings.json`
- `.gzkit/audits/tech-debt/2026-08-23/probes/rebase-verification.txt`
- `.gzkit/audits/tech-debt/2026-08-23/scope.txt`

Surfaces carrying confirmed findings:

- `src/gzkit/cli/parser_handoff.py`
- `src/gzkit/handoff_api.py`
- `src/gzkit/handoff_validation.py`
- `docs/governance/GovZero/session-handoff-schema.md`
- `.gzkit/skills/gz-session-handoff/SKILL.md`

Files rescued from the stranded clone, committed as `a50937481`:

- `.gzkit/handoffs/20260817T011903Z-session-exit-bookmark.md`
- `.gzkit/handoffs/20260823T162759Z-session-exit-bookmark.md`

Course-correction recorded in `.gzkit/insights/agent-insights.jsonl`.

## Settled Rulings

498 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
