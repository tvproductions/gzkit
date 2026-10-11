---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-11T17:58:54Z'
agent: claude-code
session_id: 3cc04308-6113-4284-a47e-54137ca91740
continues_from: .gzkit/handoffs/20261011T172749Z-gz-check-rebalanced-light-gate-full-sweep.md
---

## Current State Summary

Read `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` first. It is the one-page map the operator works from, and this session brought it up to date twice.

This session resumed the handoff of 2026-10-11T17:27Z and did three things on the operator's word.

- The map now carries the afternoon's `gz check` rebalance and a new section, "Loose ends of the run `renewing-vows`", which lists what sits beneath or after the ratified doctrine and names the door canon gives each item.
- GHI #1187 is closed as fixed. Root `AGENTS.md` names the command doctrine as the constitution again, as the last line of its section Governance doctrine surfaces. The fix is commit 6948212bb and corpus landing landing-20261011T174657Z-a30185b7. The operator has ruled that the line stands.
- The operator corrected one report as sloppy; the correction and what it uncovered are in Important Context.

main was even with origin at 10b1ed40b when this was written. This handoff, its ruling rows and two insight records are uncommitted. Nothing is in flight: no active pipeline, no active OBPI, no open TASK, no locks, no Gate 5 awaiting attestation.

## Important Context

- The operator's state, carried from the handoff of 2026-10-11T09:21Z and unchanged: write plainly, lead with the answer, put at most one decision at a time, and open no maintenance thread unasked.
- How ratified doctrine that is not yet connected enters, as put to the operator this session. Canon names four doors and each waits on the operator's word; none has a trigger. Doctrine text enters by the operator's ratification on the record, as Part 0 did. What agents load enters by a content landing with the operator's attestation. Anything that needs mechanism enters through the campaign, then promotion of a pool ADR, then OBPIs the operator initiates. What binds gzkit's own construction enters by release (statement of command, line 7), and the pin that would enforce that is unbuilt.
- The operator's correction (verbatim: "this sounds sloppy"). I had reported that the GHI #1187 landing removed the retention sidecar of the previous landing and called that how the verb behaves, from one dry-run line. Read afterwards: `docs/user/manpages/content.md`, section commit, states that the next promotion overwrites the sidecar, that history lives in git beside the rendition, and that a promotion with no removed block removes a stale sidecar. So the removal is documented design. What the file was: the map behind the operator's attestation "I attest dropping C2 and C4" for landing-20261011T144517Z-1a7a9970. Where it is now: `git show 701d01506:.gzkit/renditions/AGENTS.md/root.retention.json`, whose sha256 matches the `rendition_landed` event of that landing in the ledger. The handoff of 2026-10-11T17:27Z cites that path under Evidence and the path no longer resolves in the working tree.
- The hazard under that design: git carries the history only when a commit falls between two landings. On 2026-10-10 a map was overwritten by the next landing before any commit carried it and had to be preserved by hand under the diet chore's proofs. Recorded as an insight under scope "gz content land/retention sidecar lifetime"; no issue, no ruling.
- Content landing mechanics that cost time. `gz content remember` has no dry run and leaves `gz check` red until the entry is landed; `gz content land --dry-run` shows the plan and writes nothing. A corpus-owned section fails closed on an entry left at the capture default classification, so pass `--classification`. `gz git-sync --apply` commits whatever is staged as a chore commit, so a fix commit carrying the issue trailer is made by hand before the sync.
- `.gzkit/rules/agents-md-map-doctrine.md`, section Shape enforcement, gives the trim of an over-budget surface to the `instructions-files-diet` chore: an ordinary session adds to the corpus and does not resize the surface. The body of GHI #1187 said the entry must displace or compress, and I repeated that to the operator before reading the rule. The entry was added; `AGENTS.md` went from 24060 to 24279 bytes against an advisory budget it already exceeded.
- A verifier such as `gz check` or `gz validate` must not be piped or followed by another statement. Redirect it to a log and read the exit status in the same statement.
- Workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-09-20.md`, section Workflow fronts). Session delta, observed 2026-10-11:
  - handoff system: the handoff of 17:27Z was resumed, its claims were checked against live state and all held, and the operator's words "update the page, then git sync" were booked on it with `gz handoff decide` as proceed. The lineage walk stopped at its depth bound of 19 ancestors. I read that handoff, the ones of 10:19Z and 09:21Z, and the one of 2026-10-10T05:15Z, and no older ancestor.
  - ghi triage: GHI #1187 closed. The open count is 73 by the search total. The queue was not triaged.
  - adr/obpi campaign: unchanged. `uv run gz adr status ADR-0.35.0` shows 10/20, closeout BLOCKED; item 15 is next and only the operator initiates it.
  - new R&D: no run opened. The loose ends of `renewing-vows` are listed on the map. Of the run record I read the disposition map, the Close and the decisions from row 4 part 7 onward; its first 4300 lines and `docs/rnd/renewing-vows/review.md` are unread by this session.
  - The three-pillars thread stays held under the campaign's amendment of 2026-09-19; nothing here touched it.

## Decisions Made

- [operator-ruled] The one-page map is brought up to date with the afternoon's work (verbatim: "update the page, then git sync").
- [operator-ruled] The loose ends of the run `renewing-vows` are added to the map as a section (verbatim: "yes, add it, then git sync").
- [operator-ruled] GHI #1187 is repaired directly, ahead of item 15 of `ADR-0.35.0` (verbatim: "direct fix 1187, then git sync").
- [operator-ruled] The constitution line in root `AGENTS.md` stands as landed (verbatim: "the line stands, write a handoff").
- [agent-chose] Captured the entry as its own line at invariant tier, classification Judgment, in section governance-doctrine-surfaces. Rejected: folding it into the existing read-before line, which would have rewritten an entry the operator witnessed and needed a retention map.
- [agent-chose] Added the entry and reported the growth instead of displacing other text, following the map doctrine rule over the issue body; the amendment is recorded on the issue before the fix.
- [agent-chose] Built no check for a retirement that claims recapture and has none, which is the cause that lost the pointer on 2026-09-17. One instance does not meet the promotion freeze; it is recorded as an insight under scope "agents-md/constitution-pointer".
- [agent-chose] Booked "update the page, then git sync" as a proceed ruling on the resumed handoff. It recorded the sync the operator ordered and started no OBPI work.
- [agent-chose] Wrote the outcome of GHI #1187 to the map and not to the run record `docs/rnd/renewing-vows.md`, which the operator opens through its own skill.
- [agent-chose] Left this handoff uncommitted, because the operator asked for a handoff and did not order a sync.

## Immediate Next Steps

1. Present this handoff to the operator and take their ruling on what to draw next. Execute nothing before it.
2. If the operator returns to feature work: `ADR-0.35.0` item 15, `OBPI-0.35.0-15-pipeline-run-position`, which the operator initiates through gz-obpi-pipeline. Confirm the landed count with `uv run gz adr status ADR-0.35.0` first.
3. If this handoff and the two insight records are still uncommitted, ask the operator before syncing them.
4. Put an item from the map's open rulings or loose ends to the operator only when asked, and one at a time.

## Pending Work / Open Loops

- The map is the list of what is open: its sections "Open, and none of it blocks `ADR-0.35.0`" and "Loose ends of the run `renewing-vows`" stand as written, with the GHI #1187 [settled] item marked done.
- The four unanswered policy statements and the eight policies with no witness have the thinnest tracking: they live in the run record, in `docs/rnd/renewing-vows/doctrine-merge.md` and on the map, and in no issue or pool ADR.
- Whether a landing should refuse, or archive the prior sidecar, when the retention sidecar it would remove or overwrite is not yet committed. Insight only; the surface belongs to `ADR-0.35.0` Decision item 10.
- The handoff of 2026-10-11T17:27Z cites a retention sidecar path that the GHI #1187 [settled] landing removed. The file is at commit 701d01506; the older handoff is a dated record and was not edited.
- A retirement that claims recapture and has none is unwitnessed. Insight only.
- `AGENTS.md` is 24279 bytes against its advisory budget; the trim is open ruling (10) on the map.
- The close comment on GHI #1187 [settled] marks two open issues as open, which `.gzkit/rules/gh-cli.md` says not to do. Left as posted, since editing a posted comment changes a dated record.
- Open and untouched: GHI #1185, GHI #1186, GHI #1188, GHI #1189, GHI #1190, GHI #969, GHI #1154, GHI #1171, GHI #1144, GHI #1138, GHI #1034.

## Verification Checklist

- `git status -sb` and `git log --oneline -5`: main at or ahead of 10b1ed40b; 6948212bb is the fix commit.
- `gh issue view 1187 --json state`: CLOSED.
- `grep -n command-doctrine AGENTS.md`: one line, the last of section Governance doctrine surfaces.
- `uv run gz validate --invariant-coherence --rendition-freshness --rendition-floor-coherence` with its output redirected to a log: exit 0.
- `git show 701d01506:.gzkit/renditions/AGENTS.md/root.retention.json` piped to `shasum -a 256`: the digest begins cc27d1340ef1, as the ledger's `rendition_landed` event for landing-20261011T144517Z-1a7a9970 records.
- `uv run gz handoff rulings --search "line stands"`: this handoff's ruling is in the store.
- `uv run gz obpi lock list`: no active locks.
- `uv run gz adr status ADR-0.35.0`: 10/20.

## Evidence / Artifacts

- `docs/rnd/renewing-vows/where-things-stand-2026-10-11.md` (the one-page map)
- `AGENTS.md`
- `.gzkit/corpus/AGENTS.md.jsonl`
- `.gzkit/renditions/AGENTS.md/root.md`
- `.gzkit/renditions/AGENTS.md/root.corpus.json`
- `.gzkit/renditions/AGENTS.md/root.lineage.json`
- `docs/governance/GovZero/command-doctrine.md`
- `docs/rnd/renewing-vows/doctrine-merge.md`
- `docs/rnd/renewing-vows.md`
- `docs/evals/compression-sweep-2026-09-24.md`
- `docs/user/manpages/content.md`
- `.gzkit/rules/agents-md-map-doctrine.md`
- `.gzkit/insights/agent-insights.jsonl`
- Commits 6948212bb (the fix) and 3fb7f6974, d5fd333bf, 7e289f2f0, 10b1ed40b (syncs).
- Corpus landing landing-20261011T174657Z-a30185b7; corpus entry corpus-governance-doctrine-surfaces-2026-10-11T17:46:43.217551+00:00.
- GHI #1187: the closure contract comment (issuecomment-6111872871) and the close comment.

## Settled Rulings

1469 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
