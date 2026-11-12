---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-12T08:11:05Z'
agent: claude-code
session_id: 28be5a76-7522-4bcb-89d2-5979ba71b97e
continues_from: .gzkit/handoffs/20261112T022806Z-hex-spec-funded.md
---

## Current State Summary

The funded hexagonal-specification run's disposition rows were worked on 2026-11-12, each on its row-level go. Row 2: GHIs #1318 to #1324 filed through ghi-author, cross-links posted on #752, #1267, #810, #1230 and #6. Row 4: every item landed. The canon page docs/governance/hexagonal-architecture.md is now gzkit's hexagonal specification, with a Present state table. hexagonal-architecture.md is at 0.6.0 (rule 5 retired, rules 7 and 8 and the cascade restated, rule 10 configuration read once). tests.md 0.28.0 has a Hexagon tests section and behave narrowed to outward-facing contracts. pythonic.md 0.6.0 has values inside the walls and GzkitError outside. models.md 0.3.0 has the closed-set widening rule and loads on src/gzkit/schemas. gz-rnd 0.9.0 labels row 1 with the requirements model's records. The drydock contract carries change orders on RP-15 (tranche 6: kernel, package map, widened dependency rules) and RP-7 (hexagon test gates), with RP-7's H15 ruled. Row 3: the waiver-ratchet-drawdown chore was admitted and run once. Row 5 is routed. Main is level with origin, the tree is clean, and no code under src/gzkit changed except generated mirrors.

## Important Context

Safe mode is active; every act is one commit with the Task: TASK-ro6-classic-adr trailer. Editing the drydock contract makes the commit hook book mx_contract_amended into .gzkit/ledger.jsonl after the commit, leaving it unstaged; commit it separately each time. The MX lease was renewed 2026-11-12 and is active for 24 hours from about 06:00Z. Under MX, gz validate demotes violations to [MX advisory] lines: read the whole log, never only the tail (insight recorded after the scorecard Summary miss of c409637da). The scorecard Summary roll-up is hand-kept and checked by gz validate --advisory-scorecard; it now counts 218 scored rows (Mechanical 68, Promotable 66, Judgment 84). RP-7 owns the placement of every rule, and its H1 on hexagonal rule 1's scope is still unruled, with a dated note that the specification's dependency table takes the universal reading. The canon page's legacy port and adapter to ADR-kind section is kept as is, its contradiction left to the house-style run's row 4(c). gz lint refuses any new ruff finding; chore scripts need a shebang to clear INP001.

## Decisions Made

- [operator-ruled] Renew the expired MX lease on 2026-11-12 (verbatim: "Renew lease").
- [operator-ruled] File the hexagonal run's row 2 defects as GHIs (verbatim: "Row 2: file GHIs").
- [operator-ruled] Work the hexagonal run's row 4 (verbatim: "Yes, row 4").
- [operator-ruled] Rewrite the hexagonal canon page as the specification and change the rule only where the run overturned it, leaving rules 1 to 4 and 6, H1 and placement to RP-7 (verbatim: "A: page, plus overturned").
- [operator-ruled] Land the hexagon test discipline in tests.md (verbatim: "tests.md").
- [operator-ruled] Split pythonic.md error handling inside from outside the walls (verbatim: "pythonic error rule").
- [operator-ruled] Land the closed-set widening rule (verbatim: "closed-set rule").
- [operator-ruled] Land the configuration rule (verbatim: "configuration rule").
- [operator-ruled] Relabel gz-rnd's disposition row 1 to the requirements model's records (verbatim: "gz-rnd label").
- [operator-ruled] Place the hexagon's code on the drydock contract as change orders (verbatim: "Yes, change orders").
- [operator-ruled] The hexagon's structures go to RP-15 tranche 6 and its test gates to RP-7's placement (verbatim: "A: RP-15 plus RP-7").
- [operator-ruled] RP-7 H15: the variant gate is due by the first hexagon REQ admitted (verbatim: "Yes, regrade").
- [operator-ruled] Work the hexagonal run's row 3 (verbatim: "Yes, row 3").
- [operator-ruled] Admit the registry-wide waiver-ratchet drawdown chore (verbatim: "Admit it").
- [agent-chose] Put the closed-set rule in models.md and the configuration rule in the hexagonal rule rather than new rule files, since a new rule file is RP-7's placement question.
- [agent-chose] Narrowed gz-rnd's admission question to classic decision records, on the hexagonal run's commissioned row 1 ("The admission question applies to (f) alone"), not a separate ruling.
- [agent-chose] Widened GHI #1322 from the Harness-Purity name to every non-principle use of purity, as the class of failure.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under the new session's own id.
2. Ask which work moves next. The hexagonal run's open rows are row 1 (diamond 2, after REQs are admitted) and row 7 (two follow-on runs: knowledge and memory, and a decorator opportunity review). The drydock fronts include RP-15 tranche 6 (its owner unruled) and RP-7's held rulings H1 to H14.
3. On a go for RP-15 tranche 6, read the RP-15 specification's change order and docs/governance/hexagonal-architecture.md first; build each check on a shrink-only baseline registered in data/waiver_ratchet_registry.json.
4. Renew the MX lease if a session runs past it, only on the operator's word.

## Pending Work / Open Loops

GHIs #1318 to #1324 are open and unrouted. RP-15 tranche 6 and the RP-7 hexagon test gates are unbuilt and graded blocks return to service. The package map's approval as a classic decision record waits on RP-6's identity crossover. The variant gate is due by the first hexagon REQ admitted. RP-7 H1 to H14 are held. House-style row 4(e) (an owner and target per shrink-ratchet) is unlanded; the drawdown chore reads it when it lands. Row 7's follow-on runs are unopened. families.json still carries one-letter codes (RP-11 tranche 1).

## Verification Checklist

git status -sb shows main level with origin; uv run gz validate --documents --surfaces --advisory-scorecard --bullet-retention --cli-alignment --distribution passes with no MX advisory lines; uv run gz chores advise waiver-ratchet-drawdown passes both criteria; uv run gz obpi lock list shows the mx-session lease state.

## Evidence / Artifacts

`docs/rnd/hexagonal-specification.md`, `docs/governance/hexagonal-architecture.md`, `.gzkit/rules/hexagonal-architecture.md`, `.gzkit/rules/tests.md`, `.gzkit/rules/pythonic.md`, `.gzkit/rules/models.md`, `.gzkit/skills/gz-rnd/SKILL.md`, `docs/governance/rnd-discipline.md`, `docs/governance/harbor-ro15-project-structure.md`, `docs/governance/harbor-ro7-placement.md`, `docs/governance/harbor-pilotage-candidate-2026-10-15.md`, `.gzkit/chores/waiver-ratchet-drawdown/CHORE.md`, `docs/governance/advisory-rules-audit.md`

## Settled Rulings

2177 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
