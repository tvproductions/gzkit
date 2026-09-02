---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-02T06:54:24Z'
agent: claude-code
session_id: 8c68e6b2-c3be-43aa-9bab-f503f7c3e0f1
continues_from: .gzkit/handoffs/20260902T063544Z-session-exit-bookmark.md
---

## Current State Summary

Ran the `frontier-model-card-currency` chore end-to-end through `gz-chore-runner` (show, plan, advise, execute, audit), then closed the gap the run exposed in the chore itself. Three GHIs came out of it: #934 (open) carries the actual card drift, #935 (closed, commit `60bb1374`) added the missing currency gate, #936 (open) carries the class-level finding that nothing reads any of these gates.

Session began with a `git-sync` request; that synced cleanly (commit `27c18ca4` plus two campaign doc commits already ahead). Work then ran GHI-tracked direct repair throughout — no OBPI was initiated, no lock claimed, no pipeline marker set. Tree is clean and `origin/main` is level with `main`.

No campaign work was drawn. `ADR-0.35.0-canon-entry-corpus-landing` remains TOPMOST and untouched; the NEXT-IN-PRIORITY doctrine-declared-without-mechanism box was advanced incidentally, in that #935 converted one declared-but-unwitnessed cadence into a mechanical one.

## Important Context

The chore is scan-and-route by design and its lane note is explicit: "Lite — the scan is read-only; refresh work routes to its own GHI-tracked commits." That is why the scan stopped at routing and wrote no registry entry, no doctrine edit, and did not commit the new card PDF. A resuming agent should not read the open #934 as work half-done; it is work correctly not started.

The Fable 5.1 / Mythos 5.1 PDF (244pp, 16MB) was downloaded and verified but deliberately NOT committed. Anti-pattern in `CHORE.md`: the re-source lands first or in the same commit, then the rotation. It exists only in this session scratchpad and will need re-downloading from the URL recorded in GHI #934.

Nine doctrine surfaces are sole-sourced to the superseded 2026-06-09 card; the registry entry lists them under `doctrine_surfaces`. Read that list from the registry, not from any prose copy.

`_SCAN_INTERVALS` in `scripts/check_proof_freshness.py` now holds the 30-day value with its derivation in the comment. `CHORE.md` § Cadence points at the constant and deliberately does not restate the number — `governance-core.md` binds that a value in a Markdown doc is illustrative, never authoritative. Do not "helpfully" copy the number into the prose.

The gate reads only the timestamped blocks `gz chores run` appends to `CHORE-LOG.md`, never the hand-authored findings headings beside them. This is load-bearing: if prose headings counted, appending a findings section would mark the chore fresh with no scan having run. Pinned by `test_narrative_heading_cannot_rescue_an_overdue_scan`.

`ledger-vocabulary-inertness` currently reports a STALE proof (2026-08-15 against a surface that last moved 2026-08-28). That is pre-existing, was not caused by this session, and is an instance of #936 rather than something to fix in passing.

A first draft of this handoff asserted that GHI #927, #928, #931 and #932 were all still answered-but-unruled, carried forward from the resumed predecessor. The authoring-time settled-citation annotation flagged three of them, and `gh issue view` confirmed #928, #931 and #932 all closed on 2026-09-02. The draft was discarded rather than shipped with a stale claim. Treat any inherited unruled-GHI list as unverified until checked.

## Decisions Made

- [operator-ruled] Supply the Fable 5.1 / Mythos 5.1 card URL and run the currency scan (verbatim: "include this:" with the card URL, followed by "run the scan"). The card was consumed as primary source rather than from secondary reporting.
- [operator-ruled] Land the 30-day criterion under a GHI and file the orientation-surfacing gap separately (verbatim: "yes: Want me to land the 30-day criterion now under a GHI, and file the orientation-surfacing gap separately?"). This ratified 30 days as the interval and the two-GHI split.
- [agent-chose] Derived 30 days from measured Anthropic tracked-tier publication intervals (n=4, min 12d, median 40.5d, mean 34.5d) rather than picking a round number. Rejected 45d (permits two outstanding releases against the mean) and 14d (fires roughly 2.7x per release interval, and the refresh it triggers cannot absorb that rate).
- [agent-chose] Extended the existing `check_proof_freshness.py` with a second arm instead of building a parallel mechanism. Six sibling chores already gate on that script; only the comparison needed extending, because no repo file commit date moves when a vendor publishes.
- [agent-chose] Made the run-witness the timestamped block `gz chores run` appends, never a hand-authored heading. Rejected matching any dated heading, which would have rebuilt the presence-check gate `AGENTS.md` forbids.
- [agent-chose] Did not bundle the OpenAI August-addendum question, the Sonnet-5 tier-scope question, or the cadence gap into GHI #934. One GHI, one class per `ghi-author` § Constraints; the first two went to the CHORE-LOG and the third became #935.
- [agent-chose] Read `OBPI-0.37.0-05-session-entry-door` (status Draft) as NOT owning the #936 work: `scripts/session_orientation.py` is absent from its allowlist, appears once as a verification command at line 183, and the brief subject is the handoff acknowledge-and-decide door. Recorded the adjacency in #936 so the operator can overrule. This is the judgment call in this session most worth a second look.
- [agent-chose] Discarded two drafts of this handoff rather than editing them in place — the first for a stale inherited GHI claim, the second for a malformed verification command. Hand-editing a written handoff bypasses the fail-closed authoring gate.

## Immediate Next Steps

1. RULE ON GHI #934 — the Fable 5.1 / Mythos 5.1 refresh. This is the substantive outstanding work: evaluate the 244pp card against the nine `doctrine_surfaces`, re-source or retire every Fable/Mythos 5 citation, move lineage to `docs/governance/rule-version-history.md`, then update the registry entry and rotate the 2026-06-09 PDF out in the same commit as the re-source. The blocker comment on #934 carries the five-step sequence. Known non-empty deltas to check first: the cyber-classifier fallback claim, and the alignment risk move from "very low" to "low".
2. RULE ON GHI #936 — an open design question, not an implementation task. Four candidate homes are enumerated in its blocker comment with an agent recommendation (an orientation line restricted to breaching chores only). The session-entry budget call belongs to the operator.
3. ANSWER THE TWO SCAN QUESTIONS PARKED IN THE CHORE-LOG. Whether the OpenAI August updates entry (2026-08-06) is a registry-notes refresh or a new entry, and whether the Sonnet tier belongs in this registry at all. Both are scope rulings the chore text does not settle.
4. RESUME CAMPAIGN WORK IF NO GHI IS DRAWN. `ADR-0.35.0-canon-entry-corpus-landing` is TOPMOST and untouched by this session. Run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for its live lifecycle rather than trusting any figure transcribed here. Only the operator initiates OBPI work.
5. VERIFY BEFORE INHERITING ANY UNRULED-GHI LIST. GHI #927 is confirmed open and still answered-but-unruled; #928 [settled], #931 [settled] and #932 [settled] all closed on 2026-09-02 and must not be carried forward as pending. #933 and #930 are open and were not touched this session. The ADR-0.35.0 checklist items 11 and 12 remain undecomposed against the 1:1 Synchronization Mandate.

## Pending Work / Open Loops

- GHI #934 is OPEN with a blocker comment. The refresh needs operator initiation; the card PDF must be re-downloaded from the URL in the GHI body, since it was deliberately not committed.
- GHI #936 is OPEN with a blocker comment naming four candidate remedies and one recommendation. Unrouted pending an operator ruling on the session-entry budget.
- GHI #927 remains open and answered-but-unruled, now across seven sessions.
- 34 of 41 chores have no currency arm at all. #936 covers the reading problem; whether the other 34 should be gated is a separate, unfiled question.
- `ledger-vocabulary-inertness` has a STALE proof (2026-08-15 vs. surface moved 2026-08-28), surfaced incidentally while testing the new arm. Pre-existing, unfixed, and an instance of #936.
- The chores registry entry still reads version 1.0.0 while `CHORE.md` now declares 1.1.0 and gained a Cadence section. Not reconciled; noticed late and left rather than widening the commit.
- Advisory warnings from `gz check` are unchanged and pre-existing: AGENTS.md must-survive sections straddling the Codex cap, and 701 unlinked-spec drift findings.

## Verification Checklist

```bash
# Layer-2 state for the three GHIs this session produced
gh issue view 934 --json number,state,title
gh issue view 935 --json number,state,title
gh issue view 936 --json number,state,title

# The new currency gate: passes today, and can be shown to fail
uv run python scripts/check_proof_freshness.py frontier-model-card-currency
uv run -m unittest tests.governance.test_scan_interval_gate
uv run -m unittest tests.governance.test_proof_freshness_date_format

# The chore now runs that gate as criterion 1
uv run gz chores advise frontier-model-card-currency
uv run gz chores show frontier-model-card-currency

# Registry state — read it, never trust a transcription
python3 -c "import json; d=json.load(open('data/frontier_model_cards.json')); [print(c['vendor'], c['model_family'], c['card_date'], c['status']) for c in d['cards']]"

# Branch, tree, and lock state
git status --short
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
```

## Evidence / Artifacts

- `scripts/check_proof_freshness.py` — gained the wall-clock arm (`_SCAN_INTERVALS`, `_newest_scan_timestamp`, `_check_scan_interval`)
- `tests/governance/test_scan_interval_gate.py` — 9 tests, new this session
- `.gzkit/chores/frontier-model-card-currency/CHORE.md` — gained § Cadence
- `.gzkit/chores/frontier-model-card-currency/acceptance.json` — currency gate wired as criterion 1
- `src/gzkit/chores/frontier-model-card-currency/acceptance.json` — wheel-shipped copy, byte-identical
- `.gzkit/chores/frontier-model-card-currency/proofs/CHORE-LOG.md` — 2026-09-02 findings plus the mechanical run block
- `data/frontier_model_cards.json` — unchanged; the Mythos-class entry is still the superseded 2026-06-09 card
- `data/system_cards` — unchanged; the 5.1 PDF was deliberately not landed
- `.gzkit/insights/agent-insights.jsonl` — discovery insight on the missing cadence
- Commits: `27c18ca4` (opening sync), `283278bd` (scan findings), `60bb1374` (the currency gate)

## Settled Rulings

658 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
