---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-29T09:57:29Z'
agent: claude-code
session_id: fe40d249-a9b4-4f1c-aabd-1b207be9e01a
continues_from: .gzkit/handoffs/20261029T073942Z-step-back-assess-drydock-and-campaign.md
---

## Current State Summary

A step-back session with the operator, held as conversation rather than R&D. It produced five contract rulings, all committed and pushed (a12ace549, 2cbe943ad, 24945f814, 6b5cde09d, synced at f0ba406c4), in docs/governance/harbor-pilotage-candidate-2026-10-15.md § Repair orders, § Exit item 11 and § Rulings of 2026-10-29. The general-arrangement redraw (exit item 11) has started: a read-only inventory of every standing ruling on the ADR/OBPI replacement was compiled and spot-checked, and the first intake question was put to the operator and is UNANSWERED. No code changed. No tag is hung, no work package is commenced (WP-01 closed), and no finding awaits buy-back; the mx-session lock is held by this session.

## Important Context

How the operator wants to work in this phase: talk first, one question at a time (now a user-level memory and an insight; AGENTS.md's 'one decision per question' covers only bounded choices and should be widened). The operator wants a strategic, operational and tactical brief at every major state change (handoffs, ceremony modes, R&D, work packages, maintenance, design, chores); those state changes are the handoff's bookends, and the redraw names them at each process's edges. Claude artifacts are welcome as derived products of in-repo sources (operator ruling, insight 2026-10-29T08:08Z).

Order count: RO-0 to RO-13 is fourteen orders; the agent misstated 13 earlier and corrected it. RO-11 and RO-13 are both unspecified (no harbor-ro11 or ro13 file).

The inventory's findings, verified in part (gz --help has no catalog/outcome/REQ verb; outcomes.json holds 0 outcomes; _check_closed in src/gzkit/work_package_ledger.py does not check the 100% rule). Landed: the catalog store under data/catalog/ (11 families, empty outcomes and reqs), gz validate --catalog, all gz wp verbs. Not landed: intake; any verb authoring outcomes or REQs (RO-3 and RO-5 each assign it to the other; outcomes.json _doc claims RO-5's verbs, which do not exist); production writers of outcome_transitioned and req_proof_recorded; a delivery close moving its outcome; task cards for work packages; reopen/supplement verbs; anything of RO-4 (no releases.json; gz closeout still takes an ADR). Conflicts to resolve in the redraw: Gate 5 per work package (R2, 2026-10-17) vs per outcome (requirements model, 2026-10-18; RO-5 ruling 5 does both); release members as outcomes (model § 7, FR-017) vs work packages and their issues (RO-4 ruling 6); 0.35.0 Release Package membership (RO-4 ruling 6 vs RO-8 ruling 1, flagged for the operator's careful review); the 'contract' field the rails and RM § 6 rely on exists in no schema; pool entries as decision records (RM:304) vs intentions (C:252, newer); gz-obpi-pipeline § Work selection still binds ascending ADR order which RO-8 ruling 2 retires and RO-11 cites; gz-rnd disposition row 1 routes to ADR/OBPI with no catalog row; repair order 'held as a GitHub issue' (C:76, SMD:29, SVG) vs a repair work package naming issues (RO-5 ruling 1). Terms drift: feature area vs family vs outcome; H1 as family (RM:29) vs one-letter family codes in the store; REQ state vs proof; closeout still ADR-keyed. The current table (C:88-93), its prose (C:103-116, including the stale 'target until RO-2 lands') and the SVG are wrong in about ten places; mandate 3 and exit item 3 still say 'feature-area registry' and claim release schemas landed.

## Decisions Made

- [operator-ruled] The step-back opens with discussion and questions, not A/B/C decisions (verbatim: "I'm not ready to make like A, B, or C decisions yet. I think this handoff has to start with some discussion."); booked through gz handoff decide with the sort set aside.
- [operator-ruled] All fourteen repair orders belong to this drydock; using newly built tools during it is accepted, checked by flight tests and sea trials (verbatim: "We know that the 13 repair orders are all part of this dry dock session"; "that's what some of flight testing and sea trials are for. So I accept that."). The campaign update likely waits until after exit (verbatim: "that might have to wait till dry dock session is over").
- [operator-ruled] Ask one question at a time, in every harness (verbatim: "You gotta give the human thinker an opportunity to reflect one at a time.").
- [operator-ruled] The picture is a tactical, operational and strategic brief known at every major state change (verbatim: "I think the picture needs to be known at every major state change").
- [operator-ruled] Derived artifacts are welcome when derived from in-repo sources and may be kept (verbatim: "Just make sure they're derived from in repo things, and I'm happy.").
- [operator-ruled] Work scope frozen at induction (RO-0 to RO-13); every later finding graded by the return-to-service test, the operator ruling on each (verbatim: "record it now as a ruling").
- [operator-ruled] Every unspecified order is specified now, RO-11 and RO-13 (verbatim: "any unspecified repair orders need to be fixed immediately").
- [operator-ruled] Requirements intake blocks return to service; RO-11 widened by change order to every way a requirement enters the catalog (verbatim: "Yeah, the intake system does, but the entire replacement for the ADR or OBPI is critical.").
- [operator-ruled] Exit waits for the general arrangement redrawn as the one clear description of the replacement, exit item 11 (verbatim: "we have no business leaving dry dock without that being clear").
- [operator-ruled] Start with the general arrangement redraw, before RO-11 and RO-13 (verbatim: "start with the general arrangement redraw").
- [agent-chose] Placed the redraw under RO-0, whose row already lands the contract and its drawing, rather than a new order; the operator may move it.

## Immediate Next Steps

1. Put the open intake question to the operator, alone: should every source (pool entry, R&D disposition, deferred finding, the operator's word) land first as an intention in the pool and become a queued outcome only when pulled, or should some go straight into the catalog? Record the answer in the contract's § Rulings of 2026-10-29 (or a new dated section) with gz insights remember, one commit with its Task trailer.
2. Continue the general-arrangement redraw process by process, one question at a time: the catalog and its organization; catalog to work package (resolve Gate 5 per package vs per outcome and the package-to-outcome state mapping); release and the Release Package (members as outcomes vs work packages); the ADR's and the PRD's roles; legacy migration; then the further components. Name the state changes at each process's edges as the handoff's bookends.
3. Once the redraw shows the state changes, ask the operator to grade the three-level-brief finding under the induction freeze.
4. Then specify RO-11 to its widened scope and RO-13, each with the operator.
5. Land the major-states diagram's Mermaid source in the repo and regenerate the artifact from it.

## Pending Work / Open Loops

- The inventory's 15 gaps and its conflicts (Important Context) are input to the redraw, not yet dispositioned.
- Stale surfaces found, to be fixed under their owning orders: docs/governance/harbor-contractor-brief.md line 16 (RO-11 'not worked'); gz-rnd disposition row 1; gz-obpi-pipeline § Work selection against RO-8 ruling 2; the outcomes.json _doc claim; mandate 3 and exit item 3 wording.
- Widen the AGENTS.md 'one decision per question' clause through the content skills (insight 2026-10-29T07:54Z).
- Carried from the predecessor: RO-5's own Gate 5; the supply-chain canary reviews (supply-chain-audit, supply-chain-audit-ignored); tracing the 2026-10-27 gz check --full failures; GHIs #1298 and #1299 open; no macOS CI job; the rendition-lineage advisory; 31 overdue chores (their trigger, ADR completion, no longer exists; a documentation-coherence chore was raised); MX advisory debt near 290h.
- CI for f0ba406c4 not watched.

## Verification Checklist

- git log --oneline -6 shows a12ace549, 2cbe943ad, 24945f814, 6b5cde09d and f0ba406c4, with origin even.
- grep -n "Rulings of 2026-10-29" docs/governance/harbor-pilotage-candidate-2026-10-15.md finds the section; exit item 11 reads in § Exit.
- uv run gz handoff rulings --search "induction" returns the freeze ruling.
- gh run list --branch main --limit 2 for CI on the pushed commits.
- uv run gz obpi lock list shows mx-session.

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/ieee/requirements-model.md`
- `.gzkit/insights/agent-insights.jsonl`
- `src/gzkit/work_package_ledger.py`
- `data/catalog/outcomes.json`
- `.gzkit/handoffs/20261029T073942Z-step-back-assess-drydock-and-campaign.md`
- Major-states draft artifact: https://claude.ai/artifact/2q5TTJVjaT13vuV2V68L4p (source not yet in the repo)

## Settled Rulings

1828 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
