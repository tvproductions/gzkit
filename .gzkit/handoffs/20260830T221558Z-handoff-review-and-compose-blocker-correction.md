---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-30T22:15:58Z'
agent: claude-code
session_id: 4ff2acbb-f6a7-4597-b04b-82098030be4f
continues_from: .gzkit/handoffs/20260830T101523Z-rules-diet-version-chain-discharge.md
---

## Current State Summary

Short review-and-discharge session with no ADR parent. Resumed `.gzkit/handoffs/20260830T101523Z-rules-diet-version-chain-discharge.md` (Fresh), verified its claims against Layer-2, and found its advised step 1 ALREADY DISCHARGED by its own session: run b landed at `9edd59fd fix(rules): lift the remaining three version chains (GHI #921)` and was pushed. The predecessor's Verification Checklist is stale in exactly the way it predicted it might be, and it told the reader to check `git log` first.

Booked the operator's ruling on that handoff (`handoff_resume_decided`, decision `proceed`, operator verbatim "commit the bookmarks"), with advised steps 3 and 4 recorded as set aside.

Committed the session-exit residue at `d98eb3c2 chore(handoffs): book two session-exit bookmarks and the resume ruling` (3 files, +80) and pushed it: `ed00f950..d98eb3c2 main -> main`, pre-push `gz check` gate passed. At authoring time `origin/main` and `HEAD` are both `d98eb3c2`.

THE SESSION'S REAL PRODUCT IS A CORRECTION, not the commit. The predecessor's open loop "surface_content_types still declares only AGENTS.md, so gz content compose fails closed on every rule surface" was measured and is WRONG ON BOTH HALVES. An insight is filed at scope `content.compose`. The insight line and this document are the only uncommitted work.

## Important Context

THE MEASURED CORRECTION, in full, because a third reader must not inherit it. Running the command the predecessor never ran:

`uv run gz content compose .gzkit/rules/chores.md --consumer claude --candidate <f>` exits 1 with `Error: No corpus store for '.gzkit/rules/chores.md' at .gzkit/corpus/.gzkit/rules/chores.md.jsonl. Run 'gz content remember' to seed the corpus first.`

The cause is an ABSENT CORPUS, not the surface map. And the single-entry map is DELIBERATE, ruled and attested in terminal `OBPI-0.35.0-09-codex-playback-wiring` (2026-08-21): "An unmapped surface still falls back to the union, deliberately and in the docstring." `src/gzkit/content/vendors.py:140` `content_type_for_surface` returns `None` for an unmapped surface and its docstring says `None` "is a real answer, not an error". So it falls back; it does not fail closed. `Rule` is ALREADY a declared content type routed to `claude` in `content_type_routes` — the type exists, the corpus rows do not.

WHY THIS IS THE INTERESTING FAILURE. It is the exact trap AGENTS.md § Defect-fix routing Precondition names: "Surface the DISPOSITION, never the bare match: a brief enumerating both sides of a pair matches either side, so a presence check can report agreement where the ruling in fact INVERTED it." A grep found `surface_content_types` in an ADR-0.35.0 brief and the shape was reported as a blocker; reading the brief showed the terminal ruling had settled it the other way. The generalized lesson is in the insight's next-action: a handoff open-loop that asserts a CAUSE must cite the command that witnessed it.

THE OWNERSHIP INCONSISTENCY IS UNRESOLVED AND IS FOR THE OPERATOR. The predecessor asserts the corpus half of GHI #921 "remains operator-initiated under ADR-0.35.0-canon-entry-corpus-landing per the IRON LAW." All eight non-terminal ADR-0.35.0 briefs were checked and NONE owns seeding `.gzkit/rules/**` into the corpus — every hit is an incidental citation of `.gzkit/rules/tests.md` as a proof-channel reference, and `OBPI-0.35.0-05-corpus-candidate-generator` is the compose/lineage machinery (`composer.py`, `rendition.py`, `lineage.py`) rather than rule capture. Against that, operator canon reads "GHIs are AUTHORIZED for direct repair, always" and "Never spin up an ADR or OBPI merely to discharge a GHI", and GHI #921 is open. Two live readings, so Behavior Rules — Always #9 applies: the disagreement IS the signal and was surfaced, not resolved.

THE PRE-PUSH GATE REFUSES A TRANSCRIBED ADR COUNT IN A HANDOFF, inherited and held. `gz validate --transcribed-adr-counts` blocked the predecessor's first push for carrying ADR-0.35.0's landed count as a live figure. This document deliberately cites `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` instead of any figure.

COMMIT-TRAILER FLOOR, inherited. Any commit touching `src/**` or `tests/**` needs a `Task:` trailer. Neither the pending insight line nor this handoff touches those paths, so a plain `chore(handoffs)` commit is correct here.

## Decisions Made

- [operator-ruled] Commit the session-exit bookmarks (verbatim: "commit the bookmarks"). Booked to Layer-2 via `gz handoff decide` against the predecessor handoff, with advised steps 3 and 4 set aside.
- [operator-ruled] Push the commit (verbatim: "push"), authorized separately from the commit as every step has been on this arm.
- [operator-ruled] File the insight on the mis-stated blocker (verbatim: "ok, file it").
- [operator-ruled] Write this handoff (verbatim: "write the handoff").
- [agent-chose] Measured `gz content compose` against a real rule surface rather than relaying the predecessor's causal claim. The claim was wrong; relaying it would have been the third pass of the same misdirection.
- [agent-chose] Read terminal `OBPI-0.35.0-09`'s disposition rather than reporting the bare grep match, per the § Defect-fix routing Precondition.
- [agent-chose] Did NOT resolve the A-versus-B ownership question for the rules-corpus seeding. Two live readings of operator canon conflict; Always #9 says surface and wait.
- [agent-chose] Filed the insight as `defect` at scope `content.compose` rather than `discovery`, because a handoff open loop asserting a false cause is a defect in the record, not a finding about the world.
- [agent-chose] Set aside advised steps 3 and 4 when booking the ruling, rather than leaving them silently unworked — the amendment record is what makes a narrow ruling legible later.

## Immediate Next Steps

1. COMMIT THE TWO UNCOMMITTED FILES. `.gzkit/insights/agent-insights.jsonl` (one appended line) and this handoff. Shape: `chore(handoffs)`, no `Task:` trailer needed because neither path is under `src/**` or `tests/**`. Push is a separate authorization on this arm.
2. RULE ON OWNERSHIP OF THE RULES-CORPUS SEEDING (see Important Context). Reading A: GHI #921 is the work order and seeding via `gz content remember` is direct repair, agent-workable now. Reading B: it belongs to `ADR-0.35.0-canon-entry-corpus-landing` and initiation is the operator's under the IRON LAW. No agent may pick; the predecessor asserted B and a brief-by-brief check does not support it.
3. Hold the two operator-held discussions. Both remain ruled open and neither is agent work: the design spike, whose premise is uncorrected by anything an agent may assert; and whether a delivery-cap breach on must-survive canon stays advisory.
4. Any further instructions-files-diet run on the rules arm must rank NEW material. The version-chain family is discharged across all 25 canonical rules; the remaining large blocks are binding sub-invariants, tables and proof-channel definitions, not narrative.

## Pending Work / Open Loops

STRUCK THIS SESSION — DO NOT RE-INVESTIGATE, AND DO NOT CARRY THE ORIGINAL WORDING FORWARD. The predecessor's entry "OPEN, blocking the corpus arm: surface_content_types in data/vendor-manifest.json still declares only AGENTS.md, so gz content compose fails closed on every rule surface" is FALSE as to cause and as to consequence. Measured: compose exits 1 on `No corpus store`, and the single-entry map is the deliberate, attested design of terminal `OBPI-0.35.0-09` with documented union fallback for unmapped surfaces. What the entry was pointing AT is real and is simply GHI #921's own subject: `.gzkit/rules/**` is uncorpused. Struck rather than deleted, following the predecessor's own treatment of its struck items.

ALSO STRUCK, inherited from the predecessor and unchanged: `.gzkit/renditions/AGENTS.md/codex.md` is a deliberately retained off-route sealed record and nothing reads it; `gz validate --brief-reconcile` exiting 0 on a Draft brief is correct by design at `brief_reconcile.py:301`.

OPEN, operator-held: the design spike (fully open by ruling) and the delivery-cap advisory posture. Root AGENTS.md renders far past the codex cap with operator-doctrine-verbatim-canon straddling the boundary; tracked at GHI #815, and no attestation discloses the current figure.

OPEN, and the live question of this session: ownership of the rules-corpus seeding, A versus B as set out in Immediate Next Steps step 2. GHI #921 is open and its corrected title names the subject directly.

OPEN, unrouted spike residual, inherited: nested projection is unmeasured. `agents-md-map-doctrine.md` declares paths of AGENTS.md, CLAUDE.md and `.claude/rules/*.md` while `agents_md_map_conformance.py` line 100 pins the rendered path to AGENTS.md alone, so the nested AGENTS.md corpus is governed by no shape doctrine.

PRE-EXISTING and untouched: the `gz check` advisory reports unlinked specs.

## Verification Checklist

Run these before trusting any claim above.

git log --oneline -3
  Expect d98eb3c2, ed00f950, 9edd59fd at authoring time. If HEAD has moved, next-step 1 was already taken.

git rev-list --left-right --count origin/main...HEAD
  Expect 0 0 at authoring time, before this handoff is committed.

git status --short
  Expect the modified insights jsonl plus this untracked handoff, and nothing else.

uv run gz content compose .gzkit/rules/chores.md --consumer claude --candidate <any-file>
  Expect exit 1 with "No corpus store". This is THE command that corrects the struck open loop; re-run it before doubting the strike.

uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
  Read its lifecycle and landed count here rather than trusting any figure transcribed in prose.

uv run gz obpi lock list
  Expect no active locks.

gh issue view 921 --json state,title
  Expect OPEN, titled "instruction surfaces: .gzkit/rules/** is uncorpused, and fans out to all 26 generated AGENTS.md".

uv run gz handoff rulings --search "corpus"
  Check the settled corpus before re-arguing the ownership question.

## Evidence / Artifacts

Commits landed this session:
- `d98eb3c2` chore(handoffs): book two session-exit bookmarks and the resume ruling — 3 files, +80, pushed ed00f950 to d98eb3c2

Predecessor and the bookmarks it brackets:
- `.gzkit/handoffs/20260830T101523Z-rules-diet-version-chain-discharge.md`
- `.gzkit/handoffs/20260830T102509Z-session-exit-bookmark.md`
- `.gzkit/handoffs/20260830T103623Z-session-exit-bookmark.md`

Layer-2 records written:
- `.gzkit/ledger.jsonl` — the `handoff_resume_decided` row for this session's proceed ruling, and the `session_exit_bookmark_skipped` row that rode with it
- `.gzkit/insights/agent-insights.jsonl` — one defect record at scope content.compose, four evidence lines, uncommitted at authoring time

Surfaces read for the correction:
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-09-codex-playback-wiring.md` — the terminal ruling and its attestation
- `src/gzkit/content/vendors.py` — `content_type_for_surface` and the union fallback
- `data/vendor-manifest.json` — `surface_content_types` and `content_type_routes`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-05-corpus-candidate-generator.md` — checked and does not own rule capture

Prior-session proof carried in the tree:
- `.gzkit/chores/instructions-files-diet/proofs/post-trim-2026-08-30b.txt`

## Settled Rulings

618 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
