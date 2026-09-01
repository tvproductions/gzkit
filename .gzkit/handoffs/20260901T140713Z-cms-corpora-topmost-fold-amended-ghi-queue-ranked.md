---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-01T14:07:13Z'
agent: claude-code
session_id: d000028c-ebc1-4746-ab5e-140b398338d3
continues_from: .gzkit/handoffs/20260901T081455Z-ghi-924-925-closed-untested-guard-found.md
---

## Current State Summary

The campaign's TOPMOST position was moved to the CMS / corpora / rendering work by operator ruling, four commits landed, and one GHI closed. `c7f85a45` is unpushed at authoring time; everything before it is on origin. No locks, no pipeline marker, no OBPI scope, no open TASK.

The session began as a handoff review and became four distinct pieces of work, each operator-initiated in turn: file the untested-guard GHI (#927), correct GHI #873's ownership paragraph, extend ADR-0.35.0 and amend its binding fold algebra, and reseat the campaign queue. Two GHIs were authored (#927, #928) and one closed (#873, `fixed`).

THE HEADLINE IS A PREMISE FAILURE AT SCALE, NOT A DEFECT. Two open GHIs — #533 and #815 — have been queued behind a design that was CANCELLED on 2026-06-03. Both name the "registry-projection migration" as their blocker. Those are precisely ADR-0.0.37's twelve Abandoned briefs, retired by OBPI-0.0.37-27 (Completed, attested) in favour of corpus -> compress -> rendition -> playback. `.gzkit/invariants/` still holds four entries. Nothing on either issue said so, and nothing downstream would ever have forced the question.

## Important Context

THE FOLD ALGEBRA WAS AMENDED, AND THE IMPLEMENTATION WAS NEVER WRONG. `corpus.py` was faithful to ADR-0.35.0's pinned nine clauses; OBPI-0.35.0-01 REQ-3 forbade choosing the outcome at implementation time and the implementer correctly refused the intuitive answer. GHI #873 was the ruling that refusal had been waiting for since 2026-08-24. Read the amendment as a correction to CANON, never as a defect report against the code — a future reader who inverts that will look for a bug that is not there.

THE OPERATOR RULED THE SEMANTICS, NOT THE AGENT. Two coherent designs were presented: split the two roles, or forbid a `supersedes` chain at load time. The ruling was SPLIT — a `supersedes` row retires its target permanently; neither superseding nor retiring that replacement revives what it replaced. Un-retirement narrows to pure `retires` tombstones. The rejected alternative is recorded in the ADR, the commit, and the close comment, because "why not the other one" is the question that returns.

ONE ARM WAS DELIBERATELY LEFT UNDONE. OBPI-0.35.0-01's brief still restates the pre-amendment algebra in its REQ-3 pinning. Under `governance-core.md` the surface should be repaired in place with the amendment recorded where it lives — but editing an OBPI brief is an IRON LAW arm reserved to the operator. It is recorded on the closed #873 rather than done quietly. This is the one place where a closed GHI knowingly leaves a surface asserting retired doctrine.

MEASURE `L2done` FROM THE LEDGER, NEVER FROM BRIEF FRONTMATTER. A first pass at the #928 measurement used frontmatter status and produced a FALSE finding — ADR-0.9.0 appeared to have a checklist box ticked ahead of its brief, because OBPI-0.9.0-02 reads `status: in_progress` on disk while carrying a completion receipt from 2026-03-09. Re-measured against Layer 2, that ADR agrees exactly and the over-tick count across all sixty ADRs is ZERO. AGENTS.md § Never #7 is load-bearing for that measurement, not decorative.

READ THE FIELD, NOT THE LINE, IN THE CORPUS. `grep -c "supersedes" .gzkit/corpus/AGENTS.md.jsonl` returns 3 and all three are the word inside a row's `text` (the three-system canon quote). The non-null field count is 0. A grep-shaped check reports a producer that does not exist.

THE TRIAGE SCRIPT HAS A CITATION FALSE POSITIVE. It flagged settled citations `#9` and `#7` on two issues; both are ordinal DOCUMENT references (`§ Never #7`), not tracker links. The skill documents that exclusion for the `rule #6` form, but the section-symbol form slips through. Do not let it manufacture a gate.

INHERITED CAUTIONS THAT STILL BIND. `uv run gz validate --transcribed-adr-counts` refuses a live ADR count transcribed into a handoff; cite `uv run gz adr status` instead — the campaign amendment follows the same rule by that file's own convention. Any commit touching source or tests needs a `Task:` trailer. A verifier piped into another process is refused by the verifier-pipe-gate hook; capture to a file and echo the real exit.

COMMIT TRAILER CONVENTION, STILL UNRULED after four sessions. The harness asks for a `Claude-Session:` trailer; the repo uses `Task:` in slug form and recent commits carry no session trailer. This session followed repo convention, as its three predecessors did.

## Decisions Made

- [operator-ruled] Execute the resumed handoff's step 3 only — file the untested-guard GHI (verbatim: "file the untested-guard GHI"). Booked to Layer 2 via `gz handoff decide` with the other five advised steps recorded individually as `--set-aside`.
- [operator-ruled] File the checklist GHI (verbatim: "file the checklist GHI") after it surfaced while grounding a recommendation.
- [operator-ruled] Fold algebra: SPLIT THE TWO ROLES. Presented as a bounded choice against the rejected alternative (forbid the chain at load time); the operator chose the split. This is the ruling GHI #873 had been open for.
- [operator-ruled] Extend ADR-0.35.0 rather than route the stranded findings elsewhere (verbatim: "I am very open to extending 0.35.0", then "proceed as recommended").
- [operator-ruled] The CMS / corpora / rendering work is TOPMOST in the campaign (verbatim: "i want this cms/corpora/rendering issue to move to the top of the campaign queue now").
- [operator-corrected] The agent proposed routing the stranded GHIs through ADR-0.35.0 ceremony and was corrected: "why do you want an adr? the cms system is already in place." Canon is explicit — GHI-tracked defect repair routes direct, and "never spin up an ADR or OBPI merely to discharge a GHI". The framing had been inherited from the predecessor handoff's advised step 4 and carried without testing it against canon. An `improvement` insight was recorded per Behavior Rule Always #11.
- [operator-corrected] The agent offered an incidental finding instead of a recommendation and was told "that isn't your recommended next step". Recommendations are agent labour; offering a menu where a recommendation was owed is the § Operator Economy failure.
- [agent-chose] Reduced the proposal from three new OBPIs to two, after reading OBPI-0.35.0-07. It is Draft and unstarted and owns `content land`, so cap-awareness folds into its scope rather than earning an eleventh checklist item. Scoping an unwritten brief is not correcting a shipped one.
- [agent-chose] Added a fourth test AFTER the first commit landed. GHI #873 states the class as "two or MORE `supersedes` rows"; `6072792b` drove exactly two. Two links is not a proxy here — the original defect was an algebra whose behaviour changed as the lineage lengthened, so a fix special-casing one edge would have passed the two-link assertion.
- [agent-chose] Split the work into two commits rather than one, because the algebra amendment (#873) and the checklist extension (#921/#922) are different work orders that should be separately revertible.
- [agent-chose] Did NOT edit OBPI-0.35.0-01's brief to record the amendment, though `governance-core.md` prescribes repairing the surface. Editing an OBPI brief is an IRON LAW arm. Recorded on the closed issue instead.
- [agent-chose] Left #921 and #922 OPEN after routing them to checklist items. A checklist item is a home to initiate from, not a landing site; closing them `superseded` would have been the dead-letter shape `ghi-close` forbids.

## Immediate Next Steps

1. THE CAMPAIGN NOW SAYS ADR-0.35.0 IS TOPMOST, AND ONLY THE OPERATOR CAN DRAW IT. Under the IRON LAW every arm — lock, marker, TASK, implementer dispatch, brief edit — is operator-initiated via the `gz-obpi-pipeline` skill. The lowest unlanded item is OBPI-0.35.0-03 (`Active`); OBPI-0.35.0-08 is also `Active`, and two briefs sitting Active at once is worth the operator's eye before either is drawn.
2. RE-DERIVE ANY GHI PREMISE BEFORE WORKING IT. Now measured seven times across three sessions, twice more this session. A premise can be stale, understated, or — as #533 and #815 now prove — waiting on a design that was cancelled. The triage script flags stale blockers mechanically, but the flag is a citation and not a verdict: it cannot tell a precondition from provenance, and it has a false positive on `§ Never #7`-shaped references.
3. WORK #927 EARLY, OUT OF PROPORTION TO ITS OWN DAMAGE. Thirty of the thirty-two open GHIs route direct-fix, which is the one route with no falsifiability witness on it. Working the queue before closing that reproduces the untested-guard defect roughly thirty times, each one green. This is a sequencing claim, not a severity claim.
4. CORRECT #533 AND #815 ON THE ISSUE before either is planned around, the way #873 [settled]'s ownership paragraph was corrected. Both currently point a reader at the cancelled registry-projection design. #815 is the one item that has actively DEGRADED — 385 bytes over the codex cap when filed, 14,108 bytes over as re-measured, with a second must-survive section now affected.
5. DECIDE WHETHER OBPI-0.35.0-01's BRIEF GETS ITS AMENDMENT ANNOTATION. It still restates the pre-amendment algebra. IRON-LAW-blocked for the agent; nothing downstream will force it.
6. RULE #928's DISPOSITION when it comes up: the checklist tick is either authored state needing a witness plus a fifty-one-document remediation, or a Layer-3 derived view to regenerate or remove on the `gz register-adrs` precedent. The second touches Layer-1 canon bodies, which is why it is the operator's call.
7. RULE THE COMMIT-TRAILER QUESTION OR RETIRE IT. Four sessions have now carried it unchanged.

## Pending Work / Open Loops

ONE COMMIT UNPUSHED at authoring time: `c7f85a45` (campaign amendment). Everything else is on origin, tree otherwise clean, no locks. Push it or confirm a successor did.

THIRTY-TWO GHIs OPEN, all routed direct-fix, ranked this session via `/ghi-triage`. The rank input is preserved at `.gzkit/cache/triage/rank.json` so the ordering can be re-rendered rather than re-derived. Three carry `blocking` severity; three carry `latent`; the rest `degrading`.

OPEN and now HOMED, deliberately not closed: #921 and #922. Each has a routing comment naming its ADR-0.35.0 checklist item. They stay open because a checklist item is a home to initiate from, not a landing site — closing them `superseded` against an unauthored brief is the dead-letter shape.

OPEN and PREMISE-DEAD: #533 and #815. Both blocked on the cancelled registry-projection design. Neither issue records that. This is the single highest-value correction available on the GHI surface and it needs no code.

OPEN and WIDENING: #815, re-measured this session at 46,876 bytes rendered against the 32,768-byte codex cap. Two must-survive sections affected — `operator-doctrine-verbatim-canon` straddles the cap and `architectural-boundaries` starts entirely past it. `uv run gz validate --instructions-files-budget` exits 0 with three advisory warnings; those figures are the live measurement, never a number transcribed here.

OPEN, filed this session, both with blocker comments naming the next concrete operator action: #927 (falsifiability witness absent on the direct-fix route) and #928 (checklist tick parsed away and read by nothing). Neither could be routed to a destination in-session because both remedies are design choices rather than fixes.

UNSTARTED: ADR-0.35.0 checklist items 11 and 12 have no briefs. That is correct and deliberate — the items give the work a home to be drawn from; authoring the briefs is operator-initiated.

PRE-EXISTING and untouched: the quality gate reports 697 unlinked specs as advisory drift, and 274 tautological operations stand outstanding behind #808's green criteria.

UNRULED and carried forward for the fourth session: whether commits should carry the harness-requested session trailer alongside the repo's task trailer.

## Verification Checklist

Run these before trusting any claim above.

`git rev-list --left-right --count origin/main...HEAD` expected `0 1` at authoring time — one unpushed commit, `c7f85a45`. Anything else means a successor pushed it or work landed after this document.

`git log --oneline -4` expects `c7f85a45`, `d4caa874`, `d3ff4ae9`, `6072792b`.

`uv run gz obpi lock list` expects `No active locks.`

`uv run gz check` expects exit 0, with 697 unlinked specs reported as advisory drift and three surface-delivery-witness warnings. Capture to a file and echo the exit; the verifier-pipe-gate hook refuses a bare pipe.

`uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer` expects 9133 tests OK — 9130 at session start.

`uv run python -m unittest tests.content.test_corpus_model` expects OK, 71 tests. This is the covering module for the amended fold.

To re-demonstrate the fold RED rather than trust it: restore `src/gzkit/content/models/corpus.py` from `6072792b^` and run `tests.content.test_corpus_model.TestEffectiveCorpusSupersedes`. The three amended-semantics tests must fail and `test_pure_tombstone_un_retirement_still_restores_its_target` must PASS — that last one is the regression fence and passing on both trees is what makes it a fence. Restore and confirm `git diff --stat src/gzkit/content/models/corpus.py` is empty.

`uv run gz validate --documents --taxonomy --brief-reconcile` expects exit 0. This is what witnesses the ADR-0.35.0 scorecard against its extended checklist; a mismatch fails at `src/gzkit/validate_pkg/document.py:233`.

`uv run python -m unittest tests.governance.test_active_campaign_registry` expects OK, 7 tests. This is what fails closed if the campaign edition and `data/active_campaign.json` disagree.

`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the lifecycle and landed count. Do NOT trust a count transcribed into any document, this one included — `uv run gz validate --transcribed-adr-counts` exists for that reason.

`python3 -c "import json; rows=[json.loads(l) for l in open('.gzkit/corpus/AGENTS.md.jsonl') if l.strip()]; print(len(rows), sum(1 for r in rows if r.get('supersedes')))"` expects a non-null `supersedes` count of 0. Do NOT substitute `grep -c "supersedes"`, which returns 3 — all three are the word inside a row's `text`.

`gh issue list --state open --limit 60` re-derives the queue rather than trusting the count above.

`uv run gz handoff rulings --search "corpus"` checks the settled corpus before re-arguing any fold or corpus question.

## Evidence / Artifacts

Commits landed this session:

- `24c725c7` chore: update .gzkit (gz git-sync) — two ledger rows, the predecessor's exit bookmark and this session's `handoff_resume_decided`
- `6072792b` fix(corpus): scope un-retirement to pure tombstones (GHI #873) — ADR-0.35.0 § Decision algebra amendment plus its implementation
- `d3ff4ae9` docs(adr-0.35.0): extend the checklist to the corpus shape witness and rules family (GHI #921, GHI #922) — items 11 and 12, scorecard baseline 7 -> 9, final target 10 -> 12
- `d4caa874` test(corpus): drive a three-link supersedes chain, not just two (GHI #873)
- `c7f85a45` docs(campaign): seat the CMS/corpora/rendering work as TOPMOST (operator-ratified) — UNPUSHED at authoring time

Surfaces changed:

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` — the `### Tombstone fold algebra (binding)` block gains an inline AMENDED note and two amended clauses; checklist items 11 and 12; Decomposition Scorecard
- `src/gzkit/content/models/corpus.py` — new `_Edge` NamedTuple; `_tombstones_by_target` carries the role; `_liveness` recurrence gains the `is_replacement(t)` disjunct
- `tests/content/test_corpus_model.py` — `TestEffectiveCorpusSupersedes` gains three cases and one inverted case
- `docs/governance/build-to-1.0-campaign-2026-08-16.md` — § Topmost line, both Movement headers, the edition carry-forward note annotated, and a new § Amendments entry dated 2026-09-01

Surfaces read and verified, not changed:

- `src/gzkit/governance/trust_audits/red_parity.py` — `_brief_is_in_scope` (line 112), the heavy-lane + terminal-brief narrowing that puts the direct-fix route outside the falsifiability witness
- `src/gzkit/core/scoring.py` — `parse_checklist_items` (244) and `active_checklist_items` (286); the regex at 252 is what discards the tick
- `src/gzkit/validate_pkg/document.py` — `_validate_adr_decomposition`, the checklist/scorecard comparison at 233
- `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` — `_TEMPLATE_REL_PATH` (99), the retired bootstrap template the shape witness audits
- `src/gzkit/sync_surfaces.py` — `sync_agents_md` (364), which confirms the monolith render path is retired
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-27-*.md` — the capstone whose Objective records the 2026-06-03 cancellation

ARB receipts emitted this session, `exit_status` read from disk rather than presence counted:

- `arb-ruff-863e70a63bbb4d4eb1685d84a86433a3` — exit_status 0
- `arb-step-typecheck-0f81c096a1424e8c98f9bf19e1ccdffb` — exit_status 0
- `arb-step-unittest-221de4b0954b49b3b8660596b8aa8f52` — exit_status 0, 9132 tests
- `arb-step-unittest-173f3c777dc84eaea92fcab960eeaa57` — exit_status 0, 9133 tests

GHIs authored this session, each with a blocker comment naming the next operator action:

- GHI #927 — red-witness: direct-fix guards are outside every falsifiability gate; cross-linked with #849 at authoring time
- GHI #928 — adr-checklist: the tick mark is parsed away and read by nothing; cross-linked with #927

GHI closed this session:

- GHI #873 — `fixed`, resolved by `6072792b` and `d4caa874`, with a five-row cause-to-test table and the ownership-paragraph correction recorded separately as a comment

Layer-2 records:

- `.gzkit/ledger.jsonl` — one `handoff_resume_decided` row booking the session's opening ruling with five set-aside steps
- `.gzkit/insights/agent-insights.jsonl` — one `improvement` record for the GHI-routing course-correction, appended via `gz insights remember`
- `.gzkit/cache/triage/rank.json` — the triage rank input, preserved so the ordering re-renders rather than re-derives

## Settled Rulings

641 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
