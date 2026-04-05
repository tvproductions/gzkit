---
id: ADR-pool.graduated-oversight-model
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: anthropic-agentic-coding-trends-2026
---

# ADR-pool.graduated-oversight-model: Graduated Oversight Model

## Status

Pool

## Date

2026-03-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Replace the binary Normal/Exception execution mode with a graduated three-tier
oversight model so that human review effort scales proportionally to work risk.
Currently, gzkit (via AirlineOps AGENTS.md) offers two modes: Normal (human
attests every OBPI) and Exception (self-close with ADR-level review). This
binary choice forces a tradeoff between thoroughness and velocity — there is
no middle tier for work that is low-risk but touches enough surface area to
warrant spot-checking rather than full attestation or pure self-close.

---

## Target Scope

- Define three oversight tiers:
  - **Full Oversight**: Human attests every OBPI (current Normal mode). For Heavy lane, external-facing changes, or novel patterns.
  - **Standard Oversight**: Human spot-checks a configurable percentage of OBPIs (e.g., 30-50%); remaining OBPIs self-close with full evidence. For Lite lane internal changes with moderate scope.
  - **Light Oversight**: Self-close all OBPIs with ADR-level review (current Exception mode). For small, well-patterned, all-Lite ADRs.
- Add risk scoring heuristics: file count, subsystem boundary crossings, test coverage delta, novelty (first touch of a module).
- `gz oversight <adr-id>` CLI command to recommend an oversight tier based on risk scoring.
- Tier assignment is still a human decision — the CLI recommends, human approves.
- Integrate tier metadata into the OBPI acceptance protocol and closeout ceremony.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No automatic tier assignment — human always decides.
- No changes to the Lite/Heavy lane model (lanes determine work requirements; oversight determines review intensity).

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.controlled-agency-recovery (oversight tiers complement recovery policies), ADR-pool.agent-role-specialization (role boundaries inform risk scoring)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Three-tier model is accepted (tier definitions, boundary conditions).
3. Risk scoring heuristics are agreed upon (which signals, what weights).
4. Spot-check sampling strategy for Standard tier is decided.

---

## Inspired By

[Anthropic 2026 Agentic Coding Trends Report](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) — Trend 4: Intelligent Oversight.
The report identifies that leading organizations are moving from binary
approval/rejection to graduated oversight where review depth matches risk
level. The parallel to GovZero: Normal mode is thorough but slow; Exception
mode is fast but coarse. A middle tier captures the common case where work is
routine but not trivial enough for full self-close.

---

## Notes

- AirlineOps experience: most ADRs are all-Lite with 5-15 OBPIs. Normal mode creates attestation fatigue; Exception mode feels too permissive for 15-OBPI ADRs.
- The Standard tier addresses the sweet spot: human reviews 3-5 representative OBPIs from a 12-OBPI ADR rather than all 12 or none.
- Risk scoring should be deterministic and reproducible — no LLM-based assessment.
- Consider: should the spot-check set be random or heuristic-selected (e.g., highest file-count OBPIs)?
- Consider: does Standard tier require all OBPIs to pass self-close evidence requirements, with the spot-check being an additional human layer?

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Complements CAP-08** (graduated deviation rules). Spec proposes a 4-tier agent autonomy model that aligns with this ADR's oversight tiers.
