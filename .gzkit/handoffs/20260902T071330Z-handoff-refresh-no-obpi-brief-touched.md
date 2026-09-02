---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-02T07:13:30Z'
agent: claude-code
session_id: 8c68e6b2-c3be-43aa-9bab-f503f7c3e0f1
continues_from: .gzkit/handoffs/20260902T065424Z-frontier-card-scan-and-currency-gate.md
---

## Current State Summary

Supersedes `20260902T065424Z-frontier-card-scan-and-currency-gate.md`, chaining from it. Nothing in the repository changed between the two: HEAD is still `361d6e0e`, the tree is clean, and `origin/main` is level with `main`. This document exists because the operator asked for the handoff to be refreshed after a further exchange, not because work landed.

The session's substantive work is unchanged from the predecessor. The `frontier-model-card-currency` chore was run end-to-end through `gz-chore-runner`, producing three GHIs: #934 (open) carries the Fable 5.1 / Mythos 5.1 card drift, #935 (closed, commit `60bb1374`) added the currency gate the chore lacked, #936 (open) carries the class-level finding that nothing outside a chore run ever reads those gates.

The delta this document adds is a vocabulary ruling and a non-event: asked to "update brief", the agent could not determine which artifact was meant, declined to guess, and touched no OBPI brief. The operator then clarified that "brief" meant this handoff document. No OBPI was initiated, no lock claimed, no pipeline marker set, and no brief file was edited at any point in the session.

## Important Context

"BRIEF" MEANS THE HANDOFF DOCUMENT IN THIS OPERATOR'S USAGE. This is the delta worth carrying forward. Asked to "update brief, git-sync", the agent read "brief" as an OBPI brief, found two Active candidates under ADR-0.35.0 with no way to choose between them, and stopped. The operator clarified with "handoff brief". A future session receiving "update brief" from this operator should read it as the handoff and reach for `gz handoff create`, not for an OBPI brief.

This is a fourth collision on top of the three the transit / exchange / handoff fence already names. That fence separates the three systems that collide on the word "handoff"; it says nothing about "brief", which is load-bearing vocabulary for OBPI briefs and was here used colloquially for the handoff document. The fence's own warning applies unchanged: never infer system membership from a shared name.

There is no `gz handoff update` verb. The verb surface is list, resume, rulings, create, decide, authorize, archive. Updating a handoff means authoring a new one with `--continues-from` pointing at the old; editing a written handoff in place bypasses the fail-closed gate and the settled-citation annotation.

The rest of the context carries forward unchanged from the predecessor. The chore is scan-and-route by design, its lane being read-only, which is why the scan wrote no registry entry and no doctrine edit. The Fable 5.1 / Mythos 5.1 PDF (244pp, 16MB) was verified but deliberately not committed, and must be re-downloaded from the URL in GHI #934. Nine doctrine surfaces are sole-sourced to the superseded 2026-06-09 card; read that list from the registry entry, never from a prose copy. `_SCAN_INTERVALS` in `scripts/check_proof_freshness.py` holds the 30-day value with its derivation; `CHORE.md` § Cadence points at the constant and deliberately does not restate it.

`ledger-vocabulary-inertness` reports a STALE proof (2026-08-15 against a surface that moved 2026-08-28). Pre-existing, not caused by this session, and an instance of #936.

## Decisions Made

- [operator-ruled] "Brief" in "update brief" means this handoff document, not an OBPI brief (verbatim: "handoff brief"). Booked so the next session does not re-derive it.
- [operator-ruled] Supply the Fable 5.1 / Mythos 5.1 card URL and run the currency scan (verbatim: "include this:" with the card URL, followed by "run the scan"). The card was consumed as primary source rather than from secondary reporting.
- [operator-ruled] Land the 30-day criterion under a GHI and file the orientation-surfacing gap separately (verbatim: "yes: Want me to land the 30-day criterion now under a GHI, and file the orientation-surfacing gap separately?"). This ratified 30 days as the interval and the two-GHI split.
- [agent-chose] Stopped rather than guessing which OBPI brief was meant. Two briefs are Active under ADR-0.35.0, `gz validate --brief-reconcile` reports no drift, and nothing this session produced decomposes into either. Editing an OBPI brief is named in the IRON LAW as operator-initiated work, so guessing would have been a violation dressed as helpfulness.
- [agent-chose] Derived 30 days from measured Anthropic tracked-tier publication intervals (n=4, min 12d, median 40.5d, mean 34.5d). Rejected 45d (permits two outstanding releases against the mean) and 14d (fires roughly 2.7x per release interval).
- [agent-chose] Extended the existing `check_proof_freshness.py` with a second arm instead of building a parallel mechanism, and made the run-witness the timestamped block `gz chores run` appends rather than any dated heading.
- [agent-chose] Read `OBPI-0.37.0-05-session-entry-door` (status Draft) as NOT owning the #936 work: `scripts/session_orientation.py` is absent from its allowlist and appears once as a verification command. Recorded the adjacency in #936 so the operator can overrule. Still the judgment call in this session most worth a second look.
- [agent-chose] Discarded two earlier drafts of the predecessor handoff rather than editing them in place — one carried a stale inherited GHI claim, the other a malformed verification command.

## Immediate Next Steps

1. RULE ON GHI #934 — the Fable 5.1 / Mythos 5.1 refresh, the substantive outstanding work. Evaluate the 244pp card against the nine `doctrine_surfaces`, re-source or retire every Fable/Mythos 5 citation, move lineage to `docs/governance/rule-version-history.md`, then update the registry entry and rotate the 2026-06-09 PDF out in the same commit as the re-source. The blocker comment on #934 carries the sequence. Known non-empty deltas to check first: the cyber-classifier fallback claim, and the alignment risk move from "very low" to "low".
2. RULE ON GHI #936 — an open design question, not an implementation task. Four candidate homes are enumerated in its blocker comment with an agent recommendation (an orientation line restricted to breaching chores only). The session-entry budget call belongs to the operator.
3. ANSWER THE TWO SCAN QUESTIONS PARKED IN THE CHORE-LOG. Whether the OpenAI August updates entry (2026-08-06) is a registry-notes refresh or a new entry, and whether the Sonnet tier belongs in this registry at all.
4. NAME THE OBPI BRIEF IF ONE IS TO BE WORKED. `ADR-0.35.0-canon-entry-corpus-landing` is TOPMOST and untouched. `OBPI-0.35.0-03` and `OBPI-0.35.0-08` are both Active; `OBPI-0.35.0-13` is Draft and carries an open operator question on attestation disposition. Only the operator initiates OBPI work, and this session deliberately initiated none.
5. VERIFY BEFORE INHERITING ANY UNRULED-GHI LIST. GHI #927 is confirmed open and still answered-but-unruled; #928 [settled], #931 [settled] and #932 [settled] all closed on 2026-09-02 and must not be carried forward as pending. #933 and #930 are open and were not touched.

## Pending Work / Open Loops

- GHI #934 is OPEN with a blocker comment. Needs operator initiation; the card PDF must be re-downloaded from the URL in the GHI body.
- GHI #936 is OPEN with a blocker comment naming four candidate remedies and one recommendation. Unrouted pending an operator ruling.
- GHI #927 remains open and answered-but-unruled, now across seven sessions.
- No OBPI brief was updated this session. The instruction that prompted this handoff was ambiguous and resolved to the handoff document instead; if an OBPI brief genuinely needs an amendment, it has not been made.
- 34 of 41 chores have no currency arm at all. #936 covers the reading problem; whether the rest should be gated is a separate, unfiled question.
- `ledger-vocabulary-inertness` has a STALE proof (2026-08-15 vs. surface moved 2026-08-28). Pre-existing, unfixed, an instance of #936.
- The chores registry entry still reads version 1.0.0 while `CHORE.md` now declares 1.1.0 and gained a Cadence section. Not reconciled.
- Advisory warnings from `gz check` are unchanged and pre-existing: AGENTS.md must-survive sections straddling the Codex cap, and 701 unlinked-spec drift findings.

## Verification Checklist

```bash
# Layer-2 state for the three GHIs this session produced
gh issue view 934 --json number,state,title
gh issue view 935 --json number,state,title
gh issue view 936 --json number,state,title

# The currency gate: passes today, and can be shown to fail
uv run python scripts/check_proof_freshness.py frontier-model-card-currency
uv run -m unittest tests.governance.test_scan_interval_gate
uv run -m unittest tests.governance.test_proof_freshness_date_format

# The chore now runs that gate as criterion 1
uv run gz chores advise frontier-model-card-currency

# Registry state — read it, never trust a transcription
python3 -c "import json; d=json.load(open('data/frontier_model_cards.json')); [print(c['vendor'], c['model_family'], c['card_date'], c['status']) for c in d['cards']]"

# Confirm the claim that NO OBPI brief was touched this session
git diff --stat 27c18ca4..HEAD -- 'docs/design/adr/**/obpis/*.md'
uv run gz validate --brief-reconcile
uv run gz obpi lock list

# Branch and tree
git status --short
git rev-list --left-right --count origin/main...HEAD
```

## Evidence / Artifacts

- `.gzkit/handoffs/20260902T065424Z-frontier-card-scan-and-currency-gate.md` — the predecessor this document supersedes
- `scripts/check_proof_freshness.py` — gained the wall-clock arm (`_SCAN_INTERVALS`, `_newest_scan_timestamp`, `_check_scan_interval`)
- `tests/governance/test_scan_interval_gate.py` — 9 tests, new this session
- `.gzkit/chores/frontier-model-card-currency/CHORE.md` — gained § Cadence
- `.gzkit/chores/frontier-model-card-currency/acceptance.json` — currency gate wired as criterion 1
- `src/gzkit/chores/frontier-model-card-currency/acceptance.json` — wheel-shipped copy, byte-identical
- `.gzkit/chores/frontier-model-card-currency/proofs/CHORE-LOG.md` — 2026-09-02 findings plus the mechanical run block
- `data/frontier_model_cards.json` — unchanged; the Mythos-class entry is still the superseded 2026-06-09 card
- `data/system_cards` — unchanged; the 5.1 PDF was deliberately not landed
- `.gzkit/insights/agent-insights.jsonl` — discovery insight on the missing cadence
- Commits: `27c18ca4` (opening sync), `283278bd` (scan findings), `60bb1374` (the currency gate), `361d6e0e` (predecessor handoff)

## Settled Rulings

660 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
