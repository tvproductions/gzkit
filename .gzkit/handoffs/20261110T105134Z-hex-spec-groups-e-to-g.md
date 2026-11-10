---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-10T10:51:34Z'
agent: claude-code
session_id: c8c6c76a-a22e-4222-80e9-12c833a64470
continues_from: .gzkit/handoffs/20261109T235408Z-hex-spec-lease-renewed.md
---

## Current State Summary

The hexagonal specification R&D run (gz-rnd, docs/rnd/hexagonal-specification.md) resumed on the operator's word and ruled groups E, F and G. All seven disposition rows now carry a decision: rows 1 to 5 commissioned (each executes only on the operator's go on that row), row 6 not pursued, row 7 commissioned earlier. The run cannot close: its frontier holds only items that wait on Khononov's passages. Commits this session: c84426195 (group E), 4024ec1d4 (group F), 9a492caa8 (group G and the dispositions), all on main; no code changed.

## Important Context

- One question at a time, recommendation first, rated against the constellation; favour Montenegro, but do not over-follow him where his answer is Java Spring's (operator's caution, recorded).
- Read the held source text before citing it. Montenegro's MEAP V01 and V02 extracted text sits outside the repository in a prior session's scratchpad (the 30cc6a21 session: mont/clean.txt, v2txt/v2_171_352.txt); the operator corrected a citation from notes ('why? you have the text'). Licensed text never lands in the repo; never copy the watermark name or email.
- The work model is the requirements catalog, feature package (epic), work package (the mADR's successor), work order (the OBPI's successor) and Release Package. Nothing moves out of an mADR: legacy ADRs keep their decisions and are reconciled through the drydock contract's exit item 9. A classic ADR records one consequential choice, is authored only after the RP-6 crossover and is Current only by separate approval of its edition. Read docs/governance/ieee/requirements-model.md § 12 and the classic ADR change order before drafting any work.
- The gz-rnd skill's disposition row 1 label 'ADR / OBPI' is stale; row 4 carries its relabel.
- Commissioning a row is not the go to execute it; each row waits for its own go.
- Ask before each commit and each push unless the operator says both.

## Decisions Made

- [operator-ruled] Resume the hexagonal specification run (verbatim: "Yes, resume").
- [operator-ruled] Configuration is read once by the configurator through one config adapter, merged and validated into frozen settings and passed as values (verbatim: "Yes").
- [operator-ruled] Outside readers get a small set of versioned integration events, never ledger rows; the ledger stays internal (verbatim: "Yes").
- [operator-ruled] gz init scaffolds the hexagon for new projects; existing projects get the package map and the checker (verbatim: "Yes").
- [operator-ruled] --no-skeleton skips the folders, never the checker test (verbatim: "Yes, never the check").
- [operator-ruled] Ports and handlers are identified by Protocol and name, not marker decorators; wrapper decorators stay governed by the decorator map (verbatim: "yes: "Shall I record A with that clarification: identity comes from the Protocol and the name, and wrapper decorators stay governed by the decorator map?"").
- [operator-ruled] gzkit stays one distribution; uv_build and workspaces enforce nothing, the checker test is the fence (verbatim: "Keep one distribution").
- [operator-ruled] Fakes only inside the hexagon, enforced by banning the unittest.mock import there, mocks allowed only at an adapter's outer edge (verbatim: "yes ==> "Shall I record the strict rule: fakes only inside the hexagon, enforced by banning the unittest.mock import there, with mocks allowed only at an adapter's outer edge?"").
- [operator-ruled] The Behave-in-the-hexagon ruling is reversed: hexagon tests stay unittest under the four instruments (verbatim: "Yes, reverse it").
- [operator-ruled] Behave proves outward-facing system behaviour, the CLI and the published integration events (verbatim: "Yes, those too"; the rule's wording: "the rules for using BDD in gzkit seem clear: if we are dealing with the contract of outward/consumer-facing, then Behave and BDD are warranted.").
- [operator-ruled] Hexagon tests follow Montenegro's Table 8.3 outcome rows, one test per outcome (verbatim: "yes to the use of table 8.3").
- [operator-ruled] Hexagon unit tests carry given, when, then labels, checked by a tokenize-based checker (verbatim: "Yes, checked").
- [operator-ruled] Every hexagon unit test names the REQ it proves with @covers, fake-adapter tests exempt by declaration (verbatim: "yes").
- [operator-ruled] gzkit migrates one use case at a time, old and new paths compared, no big bang (verbatim: "Yes").
- [operator-ruled] The hexagon's structures land in this drydock as change orders; use-case migration follows return to service; the ruling stands after Montenegro's stabilize-first passage was put (verbatim: "Yes", then "Ruling stands").
- [operator-ruled] Disposition rows 1 to 5 commissioned and row 6 not pursued (verbatim: "Commission row 1", "Commission row 2", "Commission row 3", "Commission row 4", "Commission row 5", "Record row 6"); row 5 against the agent's not-pursued recommendation.
- [agent-chose] Withdrew the published-language recommendation after reading Montenegro Ch. 10 in full, and corrected the earlier "ledger is already the outbox" reasoning.
- [agent-chose] Recorded groups E, F and G as closed, each derived from the rulings, not a new ruling.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide, using this session's own id.
2. On the operator's go, resume under gz-rnd: append a decision entry quoting the resume words, check the record against git, and recompute the frontier.
3. When the operator pastes Khononov's passages (ch. 3, ch. 4, aggregates and event sourcing), take aggregates and bounded contexts, the ontology's DDD role, 'one team per context', and each of the 78 ledger event types' owning entity and drydock name, read against Montenegro's 'an event with no consumer is pure cost' (§9.2.4).
4. Revisit disposition rows 1 and 5 once those are ruled, then restate the challenge on purpose, write docs/rnd/hexagonal-specification/review.md, and put sign-off: kill or fund.

## Pending Work / Open Loops

- The resume ruling was booked with gz handoff decide under session id 30cc6a21-bf21-4119-a79a-d865d35e5e73, the previous session's id, not this session's (c8c6c76a-a22e-4222-80e9-12c833a64470); the record of what the operator said is correct, its session attribution is not.
- Rows 2 and 4 wait for the operator's go before any GHI is filed or any canon drafted; row 3's chores wait for the operator's direction; row 1's outcomes are admitted only on the operator's word, their REQ text in the operator's hand.
- Held for the disposition map: which use case is the tracer; the kernel's and configuration's catalog families; whether the hexagon's cross-cutting rules are Q outcomes (decision 8.1); whether migration phases are work orders.
- Shift turnover: this session hung no tag, commenced no package and changed no code. Reviewed gz obpi lock list (the mx-session lock ACTIVE, 657 of 1440 minutes, agent id claude-code-30cc6a21, read as stale after a /clear per the skill). The contract's list of discrepancies was not read this session.
- The MX session's advisory debt keeps aging; gz mx exit through gz-mx is the full-strength gate.
- Carried from earlier sessions and unchanged: rule 7 and the canon page rewrite, the formatter port, the airlock split, GzkitError leaving core, Harness-Purity renamed, and the other house-style rows and drydock change orders awaiting the operator's go.

## Verification Checklist

- git log --oneline -4 shows 9a492caa8, 4024ec1d4 and c84426195 on main, level with origin.
- grep -c '^## decision' docs/rnd/hexagonal-specification.md counts the decision entries; the newest group G entries close the group.
- grep -n '^| [1-7] |' docs/rnd/hexagonal-specification.md shows all seven disposition rows with a state.
- uv run gz handoff rulings --search 'unittest.mock' returns this session's booked rulings.

## Evidence / Artifacts

- `docs/rnd/hexagonal-specification.md`
- `docs/rnd/hexagonal-specification/sources/uv-boundary-enforcement-2026-11-09.md`
- `docs/rnd/hexagonal-specification/sources/cosmic-python-reading-2026-11-08.md`
- `docs/governance/ieee/requirements-model.md`
- `docs/governance/harbor-classic-adr-change-order.md`
- `docs/rnd/four-records.md`
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

2151 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
