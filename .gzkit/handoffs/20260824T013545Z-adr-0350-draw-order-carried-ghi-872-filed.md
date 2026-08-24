---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-08-24T01:35:45Z'
agent: claude-code
session_id: 7607d926-546f-4d24-abf5-1bfc7d7f8155
continues_from: 20260823T234634Z-adr-0350-obpi-draw-order.md
---

## Current State Summary

**READ THIS SECTION FIRST — the ADR-0.35.0 draw order is the reason this document exists.**

`ADR-0.35.0-canon-entry-corpus-landing` stands at **1/10 OBPIs landed, closeout BLOCKED** (verified this session, `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing`). `OBPI-0.35.0-09-codex-playback-wiring` is `attested_completed`; `OBPI-0.35.0-08-remember-post-append-advisory` is `in_progress`; the other eight are `pending` with `draft` briefs. Unchanged from the predecessor handoff.

### The draw order, carried forward

`01 -> 02 -> 03`, then `04`, then `10`, then `05`, then `06` and `07`, then finish `08`.

`04` has no prerequisite inside ADR-0.35.0 and may be pulled forward to run alongside `01-03` if two threads are wanted.

This is transcribed from the predecessor, which read it out of the ten briefs' own `Dependency order` lines and `DESIGN_FORCING_FUNCTIONS.md` § 7 Scope Minimization at line 247. **Cite the briefs, never this handoff.** The order is declared in canon; it is not a judgment either session made.

### Why this document exists rather than the predecessor alone

The predecessor cementing that order was authored at `20260823T234634Z` and pushed to `origin`. This session booted on a clone **8 commits behind**, so the resume advisement named a handoff from `20260823T151017Z` — roughly eight hours older — and the draw-order document was not on disk to be selected. Asked for the OBPI order, this session **re-derived one from the ADR body and got it materially wrong**: it placed `10` last by numbering (the declared order draws it fifth), missed that `04` is unblocked and parallelizable, and missed the binding "04 and 06 are cut together, never separately" pairing rule.

The operator caught it. The mechanism is now tracked at **GHI #872**, filed this session.

### What this session did

No OBPI machinery moved. `uv run gz obpi lock list` returns "No active locks". No pipeline marker launched, no TASK started or completed, no brief edited, no implementer or reviewer dispatched. The session ran `gz git-sync --apply` (commit `83bf43a0`, rebased over 8 remote commits), recorded one `improvement` insight, filed GHI #872 with a cross-link comment on sibling GHI #870, and authored this handoff. HEAD is `83bf43a0`, level with `origin/main`.

## Important Context

### The declared dependency graph

Each bullet is transcribed from the cited brief's own `Dependency order` line, carried from the predecessor handoff. Cite the brief.

- **01 -> 02 -> 03** is the head chain and the smallest version that delivers value. It alone discharges GHI #635 and removes the live double-render (brief 01:57, brief 02:69, brief 03:88).
- **04** has no prerequisite inside ADR-0.35.0 and may land in parallel with 01-03 (brief 04:63).
- **05** depends on 01 and 04, and brief 03 names itself "a PREREQUISITE for 05, not a parallel workstream". Shipping 05 first "ships a REGRESSION BY CONSTRUCTION": the seven byte-identical duplicate groups are invisible today only because `src/gzkit/governance/trust_audits/rendition_floor_coherence.py:72` is a substring test, and they become literal double-emissions the instant a generator materializes (brief 05:53; ADR § Alternatives H).
- **06** depends on 04 and 05. **04 and 06 are cut together, never separately** — cutting 06 alone leaves ownership as a claim with no enforcement, which § 7 calls the "worst possible combination" (brief 06:49, brief 04:63).
- **07** depends on 05 and is **not cuttable**: without the generator and `land`, OBPIs 01-03 are schema with no consumer (brief 07:66).
- **10** depends on 04 and MUST land after it. Its own Prerequisites read "If it has not, STOP: this brief cannot land first" (brief 10:56, 10:144).
- **08** and **09** are declared independent of both chains and may land at any point (brief 08:70, brief 09:125). 09 has landed. 08's declared independence does not survive its own REQ set — see Pending Work.

The predecessor recorded one reading rather than canon: placing **10 immediately after 04 and before 06**. Brief 10 pins only "MUST land after 04"; the before-06 placement comes from reading ADR Checklist item 10's phrase "the 36 `Ambiguous` capture-defaults reconciled before ownership binds" as binding at 06's fail-closed gate. If the operator reads "binds" as 04, then 10 may float anywhere after 04.

### Where the ordering doctrine lives

The briefs all cite `ADR-0.35.0 § Scope Minimization`. **That section is not in the ADR body** — it is `## 7. Scope Minimization` in `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md:247`. An agent grepping the ADR body for it finds nothing and may conclude the ordering doctrine is unwritten. That is a live finding, still unrouted.

### IRON LAW applies to every arm

Only the operator initiates OBPI work — claiming or releasing a lock, launching or clearing a pipeline marker, starting or completing a TASK, dispatching an implementer or reviewer, editing a brief. This handoff **records an order; it starts nothing and licenses nothing.** A resuming agent presents it and waits. When the operator initiates, it runs through the `gz-obpi-pipeline` skill, and Stage 2 is dispatched, never run inline.

### The orientation caveat exists and was not delivered

`scripts/session_orientation.py:1072` renders a behind-origin CAVEAT on its handoff selection when the clone is behind. `src/gzkit/session_start.py:149` renders the SessionStart advisement with `Path` and `Freshness` and no behind-awareness at all. The defended rendering goes to stdout, which was 19.3 KB this session and was truncated to a 2 KB preview that clipped the caveat. The undefended rendering is injected as additional context and arrives whole. **A resuming agent should not assume the advisement's candidate set is current — check `git rev-list --left-right --count origin/main...HEAD` and re-read `.gzkit/handoffs/` newest-first before trusting it.**

## Decisions Made

- [operator-ruled] File a GHI for the stale-resume mechanism (verbatim: "file the GHI for the stale resume"). Filed as GHI #872, labels `defect` + `runtime` + `tech-debt`, with the Step-0 mandated cross-link comment on sibling GHI #870.
- [operator-ruled] Carry the execution order into a fresh handoff so the next session starts right (verbatim: "if you can't see execution order from previous handoffs, then ensure to advocate for one now. We'll need a fresh handoff to be able to start the session right"). The draw order is placed in Current State Summary rather than buried in Important Context, so it survives truncation of the tail.
- [agent-chose] Framed GHI #872 as a caveat-omission differential between two renderings, NOT as "orientation does not fetch". The first diagnosis this session gave the operator was wrong and was corrected: `collect_remote_state` does fetch, does compute `behind`, and does warn. The real defect is that one of its two consumers never received the lesson.
- [agent-chose] Left GHI #872 open with a routing comment rather than working the fix. The destination is known (direct fix under operator canon, never an ADR or OBPI), but the operator directed this session to filing and the handoff.
- [agent-chose] Did not book a `gz handoff decide` ruling against any resumed handoff. The operator issued no decision on the advised steps of either the stale document that was resumed or the draw-order document read later, and authoring `--operator-text` for words the operator did not say is fabrication.
- [agent-chose] Recorded the miss as an `improvement` insight before completing the corrected work, per Behavior Rule 11, rather than only narrating it in conversation.

## Immediate Next Steps

1. **Present the draw order above and wait.** The IRON LAW forbids an agent starting any arm of OBPI work. When the operator rules, book their verbatim words with `uv run gz handoff decide --handoff <this file> --session-id <id> --decision proceed --operator-text "<exact words>"`, adding `--set-aside` for any advised step declined.
2. **If the operator initiates OBPI work, the head of the chain is `OBPI-0.35.0-01-corpus-tombstone-schema-and-fold`**, run through the `gz-obpi-pipeline` skill with Stage 2 dispatched rather than run inline. `OBPI-0.35.0-04-section-ownership-and-ratchet` is the only other brief whose prerequisites are satisfied; everything else is blocked behind 01 or 04.
3. **Rule the OBPI-08 conflict.** Brief 08 declares itself independent and free to land at any point, but its REQ-0.35.0-08-04 requires the advisory to carry a runnable `gz content land` invocation — a verb OBPI-07 introduces. 08 therefore cannot complete before 07. Decide whether 08 stays `in_progress` until 07 lands, or its REQ set is amended.
4. **Rule the two REQ residuals brief 08 routes to the operator**, recorded at brief 08:88 as "an operator call": REQ-0.35.0-08-06 is unprovable through this harness because `tests/commands/common.py:69` merges stdout and stderr into one buffer, and REQ-0.35.0-08-05's first disjunct is structurally unreachable. The choice named in the brief is to re-word each REQ to match what is provable, or change the runner.
5. **Decide whether GHI #872 is drawn now or queued.** It is a direct-fix defect under operator canon — never an ADR or OBPI. The class-closing part is extending `tests/governance/test_handoff_selection.py` from "every reader selects the same document" to "every reader renders the same staleness qualifiers"; without that, the next qualifier added to orientation is missed by this same surface a third time.

## Pending Work / Open Loops

### Filed this session

- **GHI #872** — `session-start: resume advisement omits the behind-origin caveat`. Open, destination known (direct fix), not worked. Cross-linked to GHI #870.

### Findings raised by the predecessor, still unrouted

- **OBPI-08's declared independence contradicts its own REQ set.** Brief 08:70 says it "may land at any point"; brief 08:260 REQ-0.35.0-08-04 requires a runnable `gz content land` invocation, and brief 08:87 marks that REQ **OPEN**, blocked on the unlanded verb. The dependency line and the REQ disagree about the same brief.
- **Brief 01:57 asserts "Nothing else in ADR-0.35.0 may land first" and that is already false.** OBPI-09 completed 2026-08-21/22 while 01 sits `pending`, and brief 09:125 asserts 09 is independent. The sentence's justification is only about the generator, so it reads as stale over-broad brief text rather than a live constraint — but it is a contradiction inside a live brief.
- **All ten briefs cite `ADR-0.35.0 § Scope Minimization` at a location the ADR body does not contain.** The section is `## 7. Scope Minimization` in the package's `DESIGN_FORCING_FUNCTIONS.md:247`.

### Carried forward, older

- Two dossier GHIs remain unfiled: the CREATE destination collision in `src/gzkit/handoff_api.py`, where `path.write_text` is preceded only by `mkdir` with no existence guard, and the empty `branch` and `agent` identity on CREATE.
- The bearing-projection design question is unruled; it is the one carried item that is not repair-shaped.
- Whether the CHANGELOG should accumulate during the cycle rather than being authored at release time is undecided; nothing enforces the Unreleased block and it was empty at v0.34.5.

## Verification Checklist

Every claim here was verified against Layer 2 this session. Each can go stale; re-verify before relaying.

**Do this one FIRST — it is the failure this handoff records:**

```bash
git rev-list --left-right --count origin/main...HEAD
ls -1t .gzkit/handoffs/*.md | head -5
```

A non-zero left number means the clone is behind and the SessionStart advisement's candidate set is stale. Pull before trusting which handoff is newest.

Then the state claims:

```bash
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing
uv run gz obpi status OBPI-0.35.0-08-remember-post-append-advisory
uv run gz obpi lock list
gh issue view 872 --json state,title
```

Expected at authoring: ADR at 1/10 with closeout BLOCKED; OBPI-08 `in_progress`; no active locks; GHI #872 OPEN; ahead 0 and behind 0 against `origin/main` at `83bf43a0`.

Then re-read the ordering source rather than trusting this transcription:

```bash
sed -n 247,275p docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md
grep -n "Dependency order" docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/*.md
```

If `gz adr status` reports a landed count other than 1/10, the graph is unchanged but its starting point has moved: re-read the dependency lines and take the lowest-numbered brief whose prerequisites are satisfied.

## Evidence / Artifacts

Read the ADR package first, the briefs second, this document last.

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/DESIGN_FORCING_FUNCTIONS.md` — § 7 Scope Minimization at line 247 is the authoritative cut-line and pairing-rule source every brief cites.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` — parent ADR: § Checklist, § Alternatives H (the rejected generator-first ordering).
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-01-corpus-tombstone-schema-and-fold.md` — head of the chain.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md` — the second unblocked brief.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md` — currently in progress; carries the two REQ residuals routed to the operator.
- `.gzkit/handoffs/20260823T234634Z-adr-0350-obpi-draw-order.md` — predecessor; the document this session failed to see.
- `src/gzkit/session_start.py` — line 149 renders the advisement with no behind-awareness (GHI #872).
- `scripts/session_orientation.py` — line 1072 renders the behind-origin CAVEAT the advisement lacks.
- `src/gzkit/handoff_selection.py` — the differential-fence doctrine GHI #872 shows is scoped to selection but not to qualifiers.
- `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` — the substring test at line 72 that makes 03-before-05 load-bearing.
- `tests/commands/common.py` — line 69 merges stdout and stderr, which makes REQ-0.35.0-08-06 unprovable here.
- `.gzkit/insights/agent-insights.jsonl` — carries this session's `improvement` record.

## Settled Rulings

507 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
