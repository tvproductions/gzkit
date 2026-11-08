---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-08T21:31:20Z'
agent: claude-code
continues_from: .gzkit/handoffs/20261108T142900Z-rp7-placement-change-order.md
---

## Current State Summary

This session did two things, each committed and pushed (66 commits since d77eab6fb). First, the classic ADR proposal from cob_projects (pinned at 74f61ba6, summarized, not copied, because that repo is private) entered the drydock as change orders on RP-6, RP-14 and RP-8, with its six held rulings H1 to H6 all ruled the same day. Second, a governed R&D run, house-style, defined gzkit's house style: one register of preferences, each admitted by operator ruling against a stated test, each held at the moment that can enforce it; hexagonal architecture is its foundation, as the whole system's map. 108 candidates were inventoried and ruled family by family, and the run was signed off as funded ("Read it: fund"). Diamond 1 is closed. No disposition row is executed.

## Important Context

Safe mode is open: the drydock contract docs/governance/harbor-pilotage-candidate-2026-10-15.md governs, its scope frozen, so every finding is graded onto an owning order or a change order, never added as a new order. The house-style record is docs/rnd/house-style.md; its review account is docs/rnd/house-style/review.md; its two research reports are landed verbatim under docs/rnd/house-style/sources/. The hexagonal specification run is disposition row 7(c) of that record: its subject is everything the F1, F8, F11 and borderline rulings sent to it (domain-typed ports, Protocol and composition, the second-adapter rule, parameter injection and config loaded once at the boundary, separation of concerns, implicit globals beyond the global statement, folder layout where the operator now disagrees with canon rule 7, what subsumption into one typed model means, the DDD and ontology relation, and layered state with an append-only event log), briefed by the operator's "strengthen" and strong adoption by every adopter. Rows 1 and 4(b) of the house-style map depend on what it settles. The airlock's parent_invariants channel is empty in production and its reach is the ontology graph, not imports (row 7(b)). The prefer-lsp hook falsely blocks text searches of strings and filenames (RP-7 finding F6); repeating the command passes.

## Decisions Made

- [operator-ruled] The classic ADR proposal enters the drydock as change orders on the owning orders (by selection: "Change orders on anchors (Recommended)").
- [operator-ruled] Held rulings H1 to H6 of the classic ADR change orders, each by selection: the handback inventory amended into Exit item 9; the identity crossover on RP-6 with CO-1; the grades as proposed; the crossover at the RP-6 landing commit; ids ADR-[0-9]{4,} with the seam's slug; the general arrangement's ADR row and the independent-evolution invariant stated.
- [operator-ruled] Two defects recorded on the drydock ("Yes, record both"): F22, the import-boundary gate missing from the per-change gz check; the hexagonal canon page's semver-kind ADR mapping, on CO-1.
- [operator-ruled] House style: ruled preferences in the RP-9 shape plus an audit for judgment; admission only by operator ruling against a stated test; one data register with a generated page; four enforcement moments (write, work entry, review, sweep); MAXX Astral for gzkit and every adopter ("MAXX Astral in gzkit and all of its adopters.").
- [operator-ruled] Hexagonal is the whole system, mapped up front as a classic ADR, the signal computed at intake and enforced at the work package freeze; code-design facts in pyproject.toml [tool.py-gzkit], governance settings in .gzkit.json.
- [operator-ruled] The house-style run signed off as funded ("Read it: fund").
- [agent-chose] Summarized the private cob_projects proposal into the public repo instead of copying it, pinning it by commit and sha256.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide.
2. On the operator's go on row 7(c), open the hexagonal specification R&D run with the gz-rnd skill: create docs/rnd/<slug>.md from the template before the first question, quote the operator's F1 words verbatim as the challenge, and enter the house-style record's rulings as source entries, never as decisions.
3. Read the hexagonal sources in full before any question: .gzkit/rules/hexagonal-architecture.md, docs/governance/hexagonal-architecture.md, the gz-skills audit at tvproductions/gz-skills skills/gzs-hexagonal-architecture-audit, src/gzkit/cli/formatters.py, the airlock model and its call sites, and the ontology model.
4. Compute the frontier from the run's subject and put the core model first: what the whole-system map's regions are; ask one question at a time, with real alternatives that never nest.
5. Leave every other house-style row and both drydock change orders waiting for the operator's go on that row.

## Pending Work / Open Loops

House-style rows 1 to 5 and 7(b), 7(d) are commissioned and await the operator's go per row; the scaffold corrections in row 2 (Ruff ALL, the app default, the cognitive ceiling on, forbid-pytest delivered) are corrections of RP-9 tranche 7, closed, with no owner and no tracking item yet. The classic ADR change orders' CO-1 and CO-2 on RP-6 block return to service and are unstarted; CO-6, the approval producer, is due before the first classic ADR is made Current. RP-7's held rulings H2 to H14 and its change order items 1 to 3 remain from the prior handoff; H1's direction was settled by the house-style run (the whole package on a shrink-only baseline) but is not yet booked in RP-7's record. The inventory's 13 canon contradictions are booked as a defect insight and assigned to row 4(i). Shift turnover: this session hung no tags and commenced no work packages; the RP-7 and RP-6 discrepancy lines added today are open in the contract's List of discrepancies. The mx-session lock is held by the MX session, not this harness session.

## Verification Checklist

uv run gz handoff resume
git rev-list --left-right --count origin/main...HEAD
uv run gz obpi lock list
uv run mkdocs build --strict
grep -n '^## decision' docs/rnd/house-style.md

## Evidence / Artifacts

- `docs/rnd/house-style.md`
- `docs/rnd/house-style/review.md`
- `docs/rnd/house-style/sources/candidate-inventory-2026-11-08.md`
- `docs/rnd/house-style/sources/pyproject-tool-table-2026-11-08.md`
- `docs/governance/harbor-classic-adr-change-order.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/harbor-ro7-placement.md`
- `docs/rnd/renewing-vows/identifier-migration-program.md`

## Settled Rulings

2113 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
