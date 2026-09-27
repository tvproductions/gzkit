---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-09-27T19:45:32Z'
agent: claude-code
session_id: cd5536cb-c5e8-452f-9c8d-24b97fc4c5ed
continues_from: .gzkit/handoffs/20260927T165044Z-parallel-agents-chunking-discussion.md
---

## Current State Summary

Resumed the chunking checkpoint; operator ruled proceed (booked with gz handoff decide). Chunking closed: ordinary parallel research subagents are already ruled by AGENTS.md Behavior Rules, no policy needed; parallel WRITERS remain unproposed. Skills packaging settled by operator: gzkit's shipped tooling is gzkit's, adopters may not modify it, upgrades overwrite edits; no local overrides, no extension design for 1.0. That conflicts with attested REQ-0.0.32-05-03, so the operator opened an R&D run to formalize amendment of a prior design. The run is IN FLIGHT at docs/rnd/design-amendment.md with Q1-Q8 decided and recorded verbatim; Q9 (amendment REQ ID form) awaits one clarification. The run surfaced a DDD lapse; the operator ruled a separate pre-1.0 DDD-discipline R&D run and it was appended to the Magna Carta as the 2026-09-27 amendment.

## Important Context

Tooling vs aircraft (operator's framing): in an adopter repo, gzkit's tooling (skills, rules, chores, personas, templates, harness skill copies, generated hooks) is gzkit's and upgrades replace it; the adopter's records under .gzkit/ (ledger and what accrues beside it) are theirs and upgrades never touch them. In the gzkit repo, .gzkit/ stays editable because gzkit builds itself. Files gz init writes once outside .gzkit/ (AGENTS.md, design/, settings.json which mixes gzkit hooks with adopter settings) are unclassified. The campaign's Movement C 'The Firewall' box (wheel-borne / authored-into-battlefield / lab-only-jig, operator 2026-06-14) is the same distinction and should be read beside the run. The amendment capability ships to adopters for their own ADRs; gzkit's first use is ADR-0.0.32, whose adopter-edit protection spans at least six REQs across OBPIs 02, 04, 05, 10, 12, 14. gz-rnd is operator-invoked only; the agent cannot open the DDD run.

## Decisions Made

- [operator-ruled] Skills packaging: gzkit's shipped skills and every other shipped surface belong to gzkit; adopters are not to modify them and upgrades overwrite edits (verbatim: 'an adopter is not encouraged to modify anything about gzkit, it is not a good idea. That keeps it simple.').
- [operator-ruled] R&D is gzkit's grill-me; the Magna Carta, roadmap and backlog are explicit row-4 destinations of an R&D run (verbatim: 'rnd is our grill-me and I think acknowledging magna carta, roadmap, and backlog as valid additional docs changes strengthens gzkit's guidance to an agent.'). Not yet applied to gz-rnd or rnd-discipline.md.
- [operator-ruled] Design-amendment R&D run Q1-Q8, each recorded verbatim in docs/rnd/design-amendment.md: separate amendment record riding with the original ADR, GHI-routed; old REQ marked superseded by a ledger event, never erased, old tests adjusted or sunsetted; full Gate 5 attestation and a lighter mini pipeline; Gates 3 and 4 set by what the amendment changes; Steps 4a and 4b on every amendment, adversary sized to the change; one amendment per ADR, ADR-level naming; the noun is amendment (gz-adr-amend / gz adr amend); DDD language arm gets its own R&D run.
- [operator-ruled] The DDD-discipline R&D run is pre-1.0 and is carried in the Magna Carta and in handoffs (verbatim: 'you keep the need for a DDD run in both a h/o AND in the magna carta. I am NOT waiting for post 1.0 for that.').
- [agent-chose] Did not create root GLOSSARY.md despite an earlier go, because the go rested on the agent's false claim that no glossary existed; PRD section 2.1 already is one.

## Immediate Next Steps

1. Resolve Q9 with the operator: they chose option A (REQ-0.0.32-A01-01 form) but also said the amend marker is best as the LAST suffix; confirm which form they mean before recording.
2. Continue the design-amendment run frontier: ledger event names, the patch-release qualifier, the defect-fix routing exception and who opens an amendment, then fill the six-row disposition map and restate the challenge for sign-off.
3. When the operator invokes gz-rnd for DDD discipline, seed it from the Q8 decision and the 2026-09-27 Magna Carta amendment, including Pocock's CONTEXT.md naming convention.
4. On the operator's go, apply the R&D destinations ruling to .gzkit/skills/gz-rnd/SKILL.md and docs/governance/rnd-discipline.md through a GHI.

## Pending Work / Open Loops

Uncommitted: docs/rnd/design-amendment.md (new, staged), the 2026-09-27 amendment in docs/governance/build-to-1.0-campaign-2026-09-20.md, two insight records, the ledger change present at session start. Defect to track: docs/governance/agent-contract-rationale.md:349 claims the DDD cascade is pinned by gz validate scopes; it is not. Glossary term 'amendment' waits for the DDD run to name the glossary home. Option A for vendor mirrors (stop committing .claude/skills and .agents/skills) is held behind the amendment design. GHI #1138 is ordinary GHI repair now that skills are gzkit-owned; routing still awaits the operator. Everything carried in the predecessor handoffs stays open, including the #1119-#1137 queue and ADR-0.35.0 at 8/14.

## Verification Checklist

Read docs/rnd/design-amendment.md end to end; every decision entry quotes the operator. uv run gz adr status ADR-0.0.32 shows Validated 15/15. grep -rn 'preserves operator edits' docs/design/adr/foundation/ADR-0.0.32-canonical-surface-packaging/obpis lists the REQs the amendment must supersede. gh issue view 611 shows gz ledger correct shipped and the issue open on one clause. The Magna Carta amendment sits at the top of the Amendments section of docs/governance/build-to-1.0-campaign-2026-09-20.md.

## Evidence / Artifacts

- `docs/rnd/design-amendment.md`
- `docs/governance/build-to-1.0-campaign-2026-09-20.md`
- `docs/design/prd/PRD-GZKIT-1.0.0.md`
- `docs/design/adr/pool/ADR-pool.ddd-domain-cascade.md`
- `docs/governance/attested-req-subject-retirement.md`
- `.gzkit/rules/hexagonal-architecture.md`
- `docs/governance/mpas-appropriation-analysis.md`
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

1126 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
