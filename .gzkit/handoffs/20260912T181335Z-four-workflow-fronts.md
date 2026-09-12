---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-09-12T18:13:35Z'
agent: codex
continues_from: .gzkit/handoffs/20260912T092705Z-obpi-0.35.0-06-completion.md
---

## Current State Summary

Four-front context is implemented in the active campaign, gz status text/table/JSON, session orientation, corpus-backed root AGENTS.md, and status/router/handoff skills. Verified 167 focused unittest tests, scoped ruff/format/ty, strict docs build, CLI audit 147/147, and selected surface/corpus/distribution/orientation/ledger validators. Changes are uncommitted alongside the earlier health audit. The report and its evidence were staged so this handoff can reference clone-durable paths.

## Important Context

The Workflow fronts section of the campaign selected by data/active_campaign.json is the standing work map. Its four fronts are handoff system, ghi triage, adr/obpi campaign, and new R&D. The map carries declared context; current progress requires live evidence. Campaign sequencing, ascending feature ADR order and operator-only OBPI initiation still govern execution. The prior handoff is lineage provenance; its completion claims are not re-certified here.

## Decisions Made

- [operator-ruled] Four fronts: handoff system; ghi triage; adr/obpi campaign; new R&D. Verbatim direction: get that into our known workflow zeitgeist so that something like `gz status` and any corresponding skill, or my simple inquiry about status all consider these frontiers
- [agent-chose] Make status and the stdlib-only session digest read the same campaign section; retain ledger-derived progress unchanged.
- [agent-chose] Preserve the previous root rendition and add one invariant entry through the corpus workflow. No compression or OBPI work was initiated.

## Immediate Next Steps

1. On an ordinary status inquiry, use gz-status and report each front with evidence, freshness or unknowns, and next action.
2. Verify live work-order ownership and campaign sequence before recommending execution; only the operator initiates OBPI work.
3. When repository synchronization is requested, review the accumulated audit and workflow changes and use git-sync with its required gates.

## Pending Work / Open Loops

- Handoff system: the reported chain-consumption finding was seated as a front; this change does not implement or independently verify its repair.
- GHI triage: the queue was not re-ranked in this context change; earlier observations and routes are in the health audit.
- ADR/OBPI campaign: consult live ledger state. The campaign already homes the disclosed airlock calibration residual in ADR-0.37.0; the audit routing note was corrected accordingly.
- New R&D: carry questions and experiments from the capability-control review; no new ADR or experiment was initiated.
- Existing rendition lineage remains UNGRADED for 12 declared sections; freshness/floor success is not lineage coverage. Compose invalidated the prior candidate lineage sidecar when replacing the candidate.
- Skill audit retains two age warnings. The delivery witness could not observe the Codex prompt payload; no delivery-completeness claim is made.

## Verification Checklist

- uv run -m unittest tests.commands.test_status tests.scripts.test_session_orientation tests.governance.test_active_campaign_registry tests.knowledge.test_active_campaign_resolution
- uv run gz status --json
- uv run gz cli audit
- uv run gz validate --surfaces --distribution --cli-alignment --skill-alignment --invariant-coherence --rendition-freshness --rendition-floor-coherence --orientation-freshness --ledger
- uv run gz skill audit
- git diff --check

## Evidence / Artifacts

- `docs/governance/build-to-1.0-campaign-2026-08-16.md`
- `AGENTS.md`
- `src/gzkit/commands/status.py`
- `scripts/session_orientation.py`
- `tests/commands/test_status.py`
- `tests/scripts/test_session_orientation.py`
- `docs/user/manpages/status.md`
- `docs/governance/health-audit-2026-09-12.md`
- `docs/governance/capability-control-review-2026-09-12.md`

## Settled Rulings

801 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
