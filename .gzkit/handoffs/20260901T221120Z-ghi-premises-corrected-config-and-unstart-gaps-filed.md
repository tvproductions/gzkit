---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-01T22:11:20Z'
agent: claude-code
session_id: 1f88784f-0a5b-47f8-9791-367c7a2bd466
continues_from: .gzkit/handoffs/20260901T140713Z-cms-corpora-topmost-fold-amended-ghi-queue-ranked.md
---

## Current State Summary

Resumed `.gzkit/handoffs/20260901T140713Z-cms-corpora-topmost-fold-amended-ghi-queue-ranked.md`, booked the operator's ruling to Layer 2, and worked its advised step 4 plus four items the operator ruled during discussion. One commit landed this session: `f9bea3e0`. HEAD is `f9bea3e0`, tree clean, `git rev-list --left-right --count origin/main...HEAD` returns `0 0`. No locks, no pipeline marker, no OBPI scope claimed, no TASK opened.

Two GHIs were authored (`#929`, `#930`); the open queue moved from 32 to 34. Two open GHIs (`#533`, `#815`) received premise corrections on the issue. One OBPI brief was annotated under an explicit operator ruling.

THE HEADLINE IS THAT A CORE CLAIM ON AN OPEN GHI WAS FALSIFIED BY MEASUREMENT, NOT BY ARGUMENT. `#815` has argued since 2026-08-17 that the truncation breach is a render-ORDER problem — verbatim, *"The rule is not too big to deliver. It is merely rendered in the wrong place."* Measured live this session, must-survive content totals 34,771 B against the 32,768 B codex cap. It is now both. Reorder alone can no longer deliver the survival declaration, which changes that issue's remedy class and is the single most consequential finding here.

## Important Context

THE CAP AND THE RANKS ARE CONFIG, NOT CONSTANTS. An agent presented the 32,768 B cap and `must_survive_through_rank: 11` to the operator as fixed constraints and was corrected: *"remember, this is configurable."* The cap lives in `data/vendor-manifest.json` under `content_type_delivery_caps`; the ranks and threshold live in `data/agents_md_survival_declaration.json`. The precise reading matters: the cap value is gzkit's BELIEF about a vendor's physical truncation, so changing it changes what gets measured, never what codex delivers — the witness says so in its own prose, *"raising the budget cannot relieve a vendor cap."* The rank threshold, by contrast, is genuinely operator-ratified policy and is a real lever.

THE MUST-SURVIVE MEASUREMENT REPRODUCES THE WITNESS EXACTLY, WHICH IS WHY IT CAN BE TRUSTED. Section spans were computed with `gzkit.content.parse.section_id` over rendered `## ` headings; the resulting spans for `operator-doctrine-verbatim-canon` (30020-43941) and `architectural-boundaries` (starting 46281) match the surface-delivery witness's own reported figures byte-for-byte. A different method agreeing with the instrument is what makes the 34,771 B total a measurement rather than an estimate.

THE ONE SECTION THAT CANNOT SHRINK IS THE ONE THAT GROWS. `operator-doctrine-verbatim-canon` is 13,921 B — 40 percent of the entire must-survive budget — and is `tier: invariant`, verbatim-binding, protected by `--rendition-floor-coherence`. Every `gz content remember` of an operator ruling adds to it. A one-off shrink pass is therefore a stopgap by construction, and the durable levers are re-ranking or ADR-0.35.0's section-ownership work reducing unowned bytes.

GHI `#898` WAS RULED WON'T-FIX FOUR DAYS BEFORE `#929` WAS FILED. Operator verbatim 2026-08-28: *"close #897 and #898 as won't-fix, they're not real defects."* `#898` asked where one binding clause should live inside one file's `_doc` string. `#929` asks whether the config surface has an owner, a loader, and a coherence gate — a question `#898` never reached. The distinction is recorded inside `#929`'s body under its own heading so no reader mistakes it for an end-run around that ruling.

THE UN-START GAP IS MECHANICAL, NOT NARRATIVE. `OBPI_TRANSITIONS` in `src/gzkit/core/lifecycle.py` carries exactly four rules, and `get_allowed_transitions('OBPI','Active')` returns `['Completed', 'Abandoned']`. There is no `Active` to `Draft` edge and no CLI verb supplies one. That is why a wrongly-started OBPI cannot be put back, and it is the whole of `#930`.

THE COMMIT-TRAILER PREMISE WAS WRONG FOR FOUR SESSIONS. Prior handoffs carried it as *"the repo uses `Task:` and recent commits carry no session trailer."* Measured: 149 of 705 commits in the last 30 days DO carry `Claude-Session:`, all between 2026-08-20 and 2026-08-30. The question is not whether to adopt a trailer — it is that the repo is 21 percent consistent, and `gz git-sync` composes messages without one. Each session samples different commits and reaches a different answer, which is why it keeps recurring.

ANY CONFIG FEATURE ADR COLLIDES WITH ASCENDING SEMVER. A config ADR would sit above `ADR-0.35.0`, and `AGENTS.md` § Operator Doctrine forbids working or recommending a higher-semver feature ADR ahead of the lowest one holding unlanded OBPIs. The routes that carry no collision are the existing `hardcoded-root-eradication` chore and direct repair under the GHI. This is surfaced on `#929`, never resolved by the agent.

INHERITED CAUTIONS THAT STILL BIND. `uv run gz validate --transcribed-adr-counts` refuses a live ADR count transcribed into a handoff; cite `uv run gz adr status` instead. A verifier piped into another process is refused by the verifier-pipe-gate hook — capture to a file and echo the real exit. Read the corpus FIELD, not the line: `grep -c "supersedes"` returns 3 and all three are the word inside a row's `text`.

## Decisions Made

- [operator-ruled] Work the resumed handoff's advised step 4 as recommended (verbatim: "proceed as recommended"). Booked to Layer 2 via `gz handoff decide` with five advised steps recorded individually as `--set-aside`.
- [operator-ruled] OBPI-0.35.0-01's brief gets its amendment annotation (verbatim: "yes", answering whether the brief should be annotated). This is an IRON LAW arm and was operator-initiated; the agent did the narrow task by the direct path without lock, marker, TASK, or dispatch.
- [operator-ruled] OBPI-0.35.0-03 is the brief actually in flight; 08 is residue (verbatim: "03 (08 was a misbehaved agent)"). The ledger corroborates: 08 carries `obpi_lock_claimed`, four `red_receipt_emitted`, and repeated `brief_reconcile_drift_detected` rows all dated 2026-08-23, the date canon records the IRON LAW violation.
- [operator-ruled] The central config strategy is a priority (verbatim: "priority"), which routed to GHI `#929`.
- [operator-ruled] File the un-start gap (verbatim: "file the un-start gap - it was a rogue agent who decided to run the OBPI without my consent"), which routed to GHI `#930`.
- [operator-ruled] Sync the session's governance rows (verbatim: "yes"), landed as `f9bea3e0`.
- [operator-corrected] The agent presented the codex cap and rank threshold as fixed constraints; the operator corrected it (verbatim: "remember, this is configurable"). The correction is right and the agent's framing had made a config question look like a physics question. An `improvement` insight was NOT recorded because the correction resolved into GHI `#929` in the same exchange, which is the durable home.
- [agent-chose] Filed `#929` rather than reopening `#898`. `#898` is four days closed as won't-fix on a narrower question; reopening it would have re-litigated a ruling the operator made explicitly. The relationship is recorded inside `#929` under its own heading.
- [agent-chose] Filed `#930` rather than adding the finding to `#611`. Every cut `#611` lists reverses a TERMINAL transition and fails by incomplete restoration; this one reverses a START and fails by a missing edge in the transition table. Cross-linked both ways, and `#611` was given the argument it lacked — that the missing primitive is what makes an IRON LAW violation unrepairable.
- [agent-chose] Recommended leaving `OBPI-0.35.0-08` in its stuck state until the un-start verb exists, rather than clearing it. The stuck state is the only live reproduction of `#930`, and every available route is wrong on its own terms. Recorded as a recommendation on `#930`'s blocker comment for the operator to accept or reject.
- [agent-chose] Did NOT close `#533` despite recommending it. The recommendation is recorded here and in the session, but closing an issue the operator has not ruled on would substitute the agent's judgment for theirs.
- [agent-chose] Corrected an earlier claim to the operator rather than letting it stand: the assertion that recent commits carry no session trailer was false, and the measurement (149 of 705) changed the shape of the open question rather than merely refining it.

## Immediate Next Steps

1. RULE THE SIX DISCUSSION ITEMS THAT ARE NOW ANSWERED BUT UNRULED. The operator asked for discussion on the commit-trailer question, `#533`'s disposition, `#815`'s remedy class, the parked-reorder question, `#927`, and `#928`; the discussion was delivered in-session and no ruling followed. Every one is a decision only the operator can make, and each is recorded in Pending below with the agent's recommendation attached.
2. `#815` IS THE ONE WITH A CHANGED REMEDY, AND IT SHOULD BE RULED BEFORE THE ISSUE IS PLANNED AROUND. Reorder is now necessary but not sufficient; a shrink of at least 2,003 B inside must-survive, or a re-ratification of `must_survive_through_rank`, has to accompany it. The shrink cannot come from rank 1.
3. THE PARKED REORDER IS PROBABLY LOWER-CEREMONY THAN IT LOOKS. `ADR-pool.render-order-truncation-survival` was parked 2026-07-25 with a stated trigger — it pays off *"only once the cap binds"* — and the cap now binds. That reframes unparking from an Architectural Boundary 1 exception into a park whose declared condition was met. Worth ruling explicitly either way, because the two framings carry very different precedent.
4. DECIDE WHETHER `#930` IS DESIGNED STANDALONE OR FOLDED INTO `#611`. A narrow un-start verb would be the fifth point-solution in a family whose stated defect is that it is made of point-solutions. Both issues carry the cross-link.
5. DECIDE WHETHER `OBPI-0.35.0-08` STAYS PUT. The agent recommends it does, and recorded why on `#930`. Clearing it is an IRON LAW arm and cannot be agent-initiated.
6. `#929` NEEDS A ROUTE RULING BEFORE ANY FIX IS AUTHORED. Three routes, two of which can move immediately (the `hardcoded-root-eradication` chore, or direct repair under the GHI) and one of which collides with ascending semver (a config feature ADR).
7. THE CAMPAIGN STILL NAMES `ADR-0.35.0` TOPMOST AND ONLY THE OPERATOR CAN DRAW IT. `OBPI-0.35.0-03` is the item in flight per this session's ruling.

## Pending Work / Open Loops

NOTHING UNPUSHED. `0 0` against origin, tree clean, no locks, HEAD `f9bea3e0`. This session leaves no in-flight code work.

SIX OPERATOR QUESTIONS ANSWERED IN DISCUSSION BUT NOT RULED. Each carries the agent's recommendation:

- COMMIT TRAILER, now five sessions unruled. The premise changed this session: it is not absent, it is 21 percent consistent (149 of 705 commits in 30 days). Any of three rulings ends it — always, never, or don't care. If "always", `gz git-sync` must compose it or 79 percent of commits will keep missing it.
- `#533` DISPOSITION. Agent recommends CLOSING it. Three of four premises are dead, and the document that originated its 5,000-char target has been deleted from the tree. The mechanism question is owned by ADR-0.35.0 § Decision 3. If the number itself wants tracking, it deserves a fresh two-paragraph issue phrased against the ratchet.
- `#815` REMEDY CLASS. Reorder plus shrink, with the rank threshold as the release valve. Note the collision: rank 11 (`architectural-boundaries`, 596 B) is the cheapest demotion candidate, but `#818` already says those boundaries rest on a memo rather than an ADR.
- THE PARKED REORDER and whether the met trigger unparks it.
- `#927`. Agent recommends binding the falsifiability witness ON THE COMMIT rather than the brief — a `fix(...) (GHI #N)` commit cites an ARB receipt proving RED then GREEN. Reuses existing ARB infrastructure; needs no new concept. Widening `red_parity`'s brief-scoped query tries to make a brief-shaped witness cover work that has no brief.
- `#928`. Agent leans toward REMOVING the tick entirely rather than regenerating it. Over-tick count measured ZERO against Layer 2, so ticks agree with the ledger by discipline alone — a derived view maintained by hand. Removal touches canon once instead of forever.

OPEN and PREMISE-CORRECTED this session: `#533` and `#815`. Both now carry a correction naming the withdrawn artifacts precisely — `OBPI-0.0.37-09` (withdrawn 2026-06-04, operator-directed, never built) and `OBPI-0.0.37-02`/`-03` (permanently withdrawn 2026-07-17). `GHI #623 [settled]`, which tracked the residue, closed 2026-07-19 with an explicit warning that a reader treating its body as current state will burn a session re-deciding a settled question.

OPEN and FILED THIS SESSION, both with blocker comments naming the next concrete operator action: `#929` (config surface has no owner, loader, or coherence gate) and `#930` (no governed reversal for a wrongly-started OBPI).

OPEN and WIDENING: `#815`. Re-measured live at 46,876 B rendered against the 32,768 B codex cap, with must-survive cumulative at 34,771 B. Both figures are live measurements; do not transcribe them forward without re-running the validator.

STUCK BY CONSTRUCTION: `OBPI-0.35.0-08` reads `status: Active` and `gz adr status` reports `in_progress`. It cannot be cleared by any governed route, which is the subject of `#930`.

UNSURVEYED, deliberately: the sibling transition tables (`ADR_TRANSITIONS`, `PRD_TRANSITIONS`, `RULE_TRANSITIONS`, `SKILL_TRANSITIONS`, `CONSTITUTION_TRANSITIONS`) were not checked for the same forward-only shape. `#930` makes no claim about them. Likewise the other 43 registries in `data/` were not swept for the two-registries-one-concept shape that `#929` names.

PRE-EXISTING and untouched: the quality gate reports unlinked specs as advisory drift, and tautological operations stand outstanding behind `#808`'s green criteria.

## Verification Checklist

Run these before trusting any claim above.

`git rev-list --left-right --count origin/main...HEAD` expects `0 0`. Anything else means work landed after this document was written.

`git log --oneline -2` expects `f9bea3e0` then `8804f379`.

`uv run gz obpi lock list` expects `No active locks.`

`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the lifecycle and landed count. Do NOT trust a count transcribed into any document, this one included — `uv run gz validate --transcribed-adr-counts` exists for that reason. Expect `03` and `08` both `in_progress`; that is the `#930` condition, not a new defect.

`uv run gz validate --documents --brief-reconcile` expects exit 0. This is what witnesses the annotated OBPI-0.35.0-01 brief against its parent ADR.

`uv run gz validate --instructions-files-budget` expects exit 0 with three advisory warnings. The byte figures it prints are the live measurement; the ones quoted in this document are a snapshot.

To re-derive the must-survive total rather than trust it, compute section spans with `gzkit.content.parse.section_id` over the rendered `## ` headings of `AGENTS.md`, sum the eleven ids ranked at or below `must_survive_through_rank` in `data/agents_md_survival_declaration.json`, and compare against the codex cap in `data/vendor-manifest.json`. The method is validated by its spans matching the surface-delivery witness byte-for-byte.

`uv run python -c "from gzkit.core.lifecycle import get_allowed_transitions; print(get_allowed_transitions('OBPI','Active'))"` expects `['Completed', 'Abandoned']`. That absence of a return path is the whole of `#930`.

`gh issue list --state open --limit 60` re-derives the queue rather than trusting a count. Expect 34 unless the operator has ruled since.

`gh issue view 898 --json stateReason` expects `NOT_PLANNED` — the won't-fix ruling `#929` is careful not to re-litigate.

`uv run gz handoff rulings --search "config"` checks the settled corpus before re-arguing any config question.

`git log --since='30 days ago' --grep="Claude-Session" --oneline | wc -l` re-derives the trailer measurement.

## Evidence / Artifacts

Commit landed this session:

- `f9bea3e0` chore: update .gzkit, docs/design/adr (gz git-sync) — the OBPI-0.35.0-01 brief annotation plus two governance ledger rows

Surfaces changed:

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-01-corpus-tombstone-schema-and-fold.md` — an AMENDED note above the pinned algebra recording the GHI #873 split, and clauses 8 and 9 repaired in place so neither asserts retired doctrine. No REQ was invalidated: REQ-0.35.0-01-04's fixture is a pure-tombstone chain and remains true verbatim under the amended algebra.

Surfaces read and verified, not changed:

- `src/gzkit/core/lifecycle.py` — `OBPI_TRANSITIONS`, four rules, no `Active` to `Draft` edge
- `src/gzkit/config.py` — 285 lines, Pydantic, governs none of the 44 registries in `data/`
- `src/gzkit/chores/hardcoded-root-eradication/CHORE.md` — the config-first doctrine's current home
- `data/vendor-manifest.json` — `content_type_delivery_caps` holds the codex cap
- `data/agents_md_survival_declaration.json` — ranks 1 to 11 and `must_survive_through_rank`
- `data/instructions_files_budget.json` — the decoupled ceiling and its dated ruling history
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — the withdrawal dispositions for items 02, 03, 09 and 11 through 17
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` — § Decision 3 is section ownership plus a decrease-only ratchet, NOT registry projection

GHIs authored this session, each with a blocker comment naming the next operator action:

- GHI `#929` — config: 44 registries, 93 readers, no owner, loader, or coherence gate; cross-linked with `#818` at authoring time
- GHI `#930` — obpi lifecycle: no governed reversal for a wrongly-started OBPI; cross-linked with `#611` at authoring time

Corrections posted to open GHIs:

- GHI `#533` — premise correction naming the three withdrawn artifacts, the deleted source document, and the live successor mechanism
- GHI `#815` — the falsification, the 37-fold measurement drift, and the ADR-0.35.0 § Decision 3 mischaracterization

Layer-2 records:

- `.gzkit/ledger.jsonl` — one `handoff_resume_decided` row booking the opening ruling with five set-aside steps, plus the session exit bookmark

## Settled Rulings

646 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
