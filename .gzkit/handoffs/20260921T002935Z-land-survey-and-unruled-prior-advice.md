---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-21T00:29:35Z'
agent: claude-code
session_id: 9e53da08-1413-4e36-851a-3dd81f307c4a
continues_from: .gzkit/handoffs/20260920T202207Z-config-surface-adr-and-windows-defect-sweep.md
---

## Current State Summary

A survey-and-sync session that changed no source, no canon and no governance artifact. Two operator directives were worked. FIRST, the guarded git-sync ritual: dry-run reported ahead=0 behind=0 diverged=False dirty=True, and `uv run gz git-sync --apply` landed commit f878e1ea5 carrying three mechanically-generated files, two CHECKPOINT session-exit bookmarks and one ledger row. No force push and no `--no-verify`. SECOND, a lay-of-the-land survey verified against Layer 2 rather than relayed from the predecessor handoff. Observed: `git rev-list --left-right --count origin/main...HEAD` returns `0 0`; `uv run gz obpi lock list` reports no active locks; `uv run gz check` exits 0; the open GHI queue stands at 56. ADR-0.39.0 is Pending / pre_closeout at 0 of 7 with every brief pending and draft, so no OBPI work has begun on it. ADR-0.35.0, which remains TOPMOST, is Pending / pre_closeout at 7 of 13 with closeout BLOCKED on six briefs missing ledger proof of completion. One survey finding is new this session: the settled-citation annotator resolves a cross-repository issue reference against the local repository, so the predecessor advised step naming the gz-skills discovery-contract issue was annotated as settled from a closed gzkit issue of the same number while the real one is open.

## Important Context

THE PREDECESSOR ADVICE IS STILL UNRULED, AND THIS SESSION DID NOT EXECUTE ANY OF IT. No `handoff_resume_decided` row names `.gzkit/handoffs/20260920T202207Z-config-surface-adr-and-windows-defect-sweep.md`; the newest booked decision is a `proceed` on `20260920T160721Z-config-surface-and-magna-carta-edition.md` at 2026-09-20T18:11:26Z. The five advised steps carry forward untouched.

THE WORKFLOW FRONTS MAP is declared in `docs/governance/build-to-1.0-campaign-2026-09-20.md` under `## Workflow fronts`, read through `data/active_campaign.json`, and names four fronts: handoff system, ghi triage, adr/obpi campaign, and new R&D. This session's delta per front. HANDOFF SYSTEM: one new defect observed in the settled-citation annotator, recorded as an insight and unrouted. GHI TRIAGE: queue read at 56 open, against the campaign's dated observation of 57; no triage pass was run and no issue was opened or closed. ADR/OBPI CAMPAIGN: read only, ADR-0.35.0 and ADR-0.39.0 lifecycle observed, nothing initiated. NEW R&D: untouched this session.

THE ANNOTATOR DEFECT MATTERS FOR HOW THIS DOCUMENT IS READ. `gz handoff create` resolves every issue reference in a prospective section against live state and marks a closed one settled in place. It has no repository qualifier, so a reference to another repository resolves against gzkit. That is why the gz-skills discovery-contract issue is named in prose below rather than in the usual number form: writing the number would have stamped a settled mark onto an issue that `gh issue view 1 --repo tvproductions/gz-skills` reports OPEN, falsifying this record at authoring time. The annotation annotates and never refuses, so it is advisory, but a false settled mark on a prospective step is exactly the decay the annotation exists to catch.

TWO CHECKPOINT BOOKMARKS SIT BETWEEN THIS DOCUMENT AND ITS PREDECESSOR. They were written mechanically at session-exit beats at 2026-09-21T00:10:01Z and 00:11:32Z and carry no session model. This handoff chains from the last authored document deliberately; the bookmarks are evidence, not lineage.

THE `gz check` RUN EXITED 0 BUT WAS NOT RECORDED AS VERIFIED. The insights append landed while the gate was running, so the tree was not fully staged and the run reports `not recorded as verified`. The exit code is the verifier truth; the pre-push gate will rerun the suite.

A SIBLING CLONE IS DIRTY. `C:/Users/Jeff/source/repos/agents/gz-skills` is level with its remote at 6633ce3 but carries uncommitted drift: `.opencode/plugins/gz-skills.js` and `docs/roadmap.md` modified, `docs/proposals/repository-baseline-bootstrap.md` untracked. The predecessor claim that both repositories are clean and synced is STALE for that clone.

## Decisions Made

- [agent-chose] Ran the ritual as `uv run gz git-sync --apply` without `--lint --test`, per the git-sync skill Steps item 3: the pre-commit hook is the mandatory gate and the explicit flags are redundant re-runs.
- [agent-chose] Chained this handoff from the last AUTHORED predecessor rather than from the newest file under `.gzkit/handoffs/`, because the two newer files are mechanical CHECKPOINT bookmarks that carry no session model and would add a link without adding lineage.
- [agent-chose] Left the parent ADR unset. No ADR work was done this session, and binding this document to ADR-0.39.0 would suggest work on an ADR whose completion is gated and uninitiated.
- [agent-chose] Recorded the settled-citation annotator defect with `gz insights remember` rather than filing an issue, because filing was outside the requested scope and the routing is the operator ruling to make.
- [agent-chose] Named the gz-skills discovery-contract issue in prose rather than by number in the prospective sections, to keep the annotator from stamping a false settled mark on an open issue.
- [agent-chose] Executed none of the predecessor advised steps. A handoff advises and does not authorize, and no ruling was booked on that document.

## Immediate Next Steps

1. Rule on the five advised steps carried from `.gzkit/handoffs/20260920T202207Z-config-surface-adr-and-windows-defect-sweep.md`, which are still unruled at Layer 2, and book the ruling with `uv run gz handoff decide` naming that path, this session id, a decision of proceed, pause, hold or revert, and the operator exact words.
2. Route the settled-citation annotator defect: the annotator resolves a cross-repository issue reference against the local repository. It is recorded in `.gzkit/insights/agent-insights.jsonl` under scope `gzkit.handoff.settled-citation-annotation` and is otherwise unrouted. The repair shape is to carry the owning repository through reference extraction, or to refuse to annotate a reference naming another repository.
3. Rule on GHI #1069, carried unruled from the predecessor and verified OPEN this session. The line-endings audit names the write_text hazard in its own error message and its scope cannot reach it.
4. Decide what to do with the uncommitted drift in the gz-skills clone at `C:/Users/Jeff/source/repos/agents/gz-skills`: two modified files and one untracked proposal, all sitting on top of the released v0.4.0 commit.
5. If campaign work is wanted instead of this residue, the front is adr/obpi campaign and the item is ADR-0.35.0-canon-entry-corpus-landing, which remains TOPMOST. Read its OBPI table first: brief 08 has been in_progress since 2026-08-23 with no lock held and its tasks recorded blocked.

## Pending Work / Open Loops

UNRULED AND CARRIED. The five predecessor advised steps, none booked. GHI #1069, verified OPEN. The gz-skills discovery-contract issue, verified OPEN in its own repository despite the settled annotation the predecessor document carries.

OBSERVED THIS SESSION, UNROUTED. The settled-citation annotator defect, recorded as an insight only. A dangling OBPI state on the TOPMOST ADR: OBPI-0.35.0-08-remember-post-append-advisory reports Runtime State IN PROGRESS with proof missing, while `gz obpi lock list` reports no active locks; its last task events are four `task_blocked` rows at 2026-08-23T14:27:40Z and its last touch is a `brief_reconciled` at 2026-09-06T01:12:46Z. Whether that is abandoned work, a state that outlived its lock, or a brief awaiting operator initiation is unresolved.

MEASURED, NOT ROUTED. GHI #1063 counts 51 validator scopes never invoked; whether the remaining scopes are inert or merely unrouted is still unmeasured. The queue itself stands at 56 open against the campaign dated observation of 57.

ADVISORY SIGNALS FROM THE GREEN RUN. `gz check` reports 713 unlinked specs as spec-test-code drift, and one flag approaching its deadline within 14 days, `ops.product_proof`. Neither affects the exit code; neither has an owner named here.

HELD BY OPERATOR RULING. GHI #1028 remains open under the explicit hold recorded in the campaign Amendments for 2026-09-19. It is not a next action until the operator resumes it.

UNREPAIRABLE RESIDUE, CARRIED. Commit 84ea8e435 touches src and tests and carries no Task trailer. It is published, so repair needs a force-push that repository policy forbids. The gate that would now catch it is wired into `gz check`.

## Verification Checklist

Run `uv run gz check` and expect exit 0. If you pipe it, use `set -o pipefail` first: the verifier-pipe-gate hook refuses a bare pipe because the shell would report the filter exit status, not the gate one.

Run `git rev-list --left-right --count origin/main...HEAD` and expect zero and zero.

Run `uv run gz obpi lock list` and expect no active locks.

Run `uv run gz adr status ADR-0.39.0-gzkit-internal-config-surface` and read the OBPI table as the authority. Expect lifecycle Pending and every brief pending with a draft brief. Any other state means OBPI work began without operator initiation and must be investigated before anything else proceeds.

Run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` and expect 7 of 13 with closeout BLOCKED, and brief 08 showing in_progress.

Run `gh issue view 1069 --json state` in gzkit and expect OPEN. Run `gh issue view 1 --repo tvproductions/gz-skills --json state` and expect OPEN, which is what the predecessor settled annotation contradicts.

Run `grep handoff_resume_decided .gzkit/ledger.jsonl` and confirm no row names the 20260920T202207Z document.

In `C:/Users/Jeff/source/repos/agents/gz-skills` run `git status --short` and expect the three drifted paths named in Important Context.

## Evidence / Artifacts

`.gzkit/handoffs/20260920T202207Z-config-surface-adr-and-windows-defect-sweep.md`
`.gzkit/handoffs/20260921T001001Z-session-exit-bookmark.md`
`.gzkit/handoffs/20260921T001132Z-session-exit-bookmark.md`
`.gzkit/insights/agent-insights.jsonl`
`.gzkit/ledger.jsonl`
`docs/governance/build-to-1.0-campaign-2026-09-20.md`
`docs/design/adr/pre-release/ADR-0.39.0-gzkit-internal-config-surface/ADR-0.39.0-gzkit-internal-config-surface.md`
`data/active_campaign.json`

## Settled Rulings

1009 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
