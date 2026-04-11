# Research Plan: ai governance

## Questions
1. What does “AI governance” encompass across the main layers: technical governance, organizational governance, national regulation, and international standards?
2. What governance frameworks, taxonomies, and control models are most cited in the academic and policy literature since roughly 2018?
3. What are the major current regulatory and standards regimes shaping practice (for example EU AI Act, NIST AI RMF, OECD principles, ISO/IEC work, White House / U.S. agency guidance, frontier-model lab commitments)?
4. What concrete governance mechanisms are organizations actually using or proposing for high-risk and frontier AI systems (model evaluations, incident reporting, access controls, deployment gating, documentation, red-teaming, monitoring, auditability, board oversight)?
5. Where do sources materially disagree — for example on voluntary vs mandatory controls, model-level vs application-level regulation, open-source treatment, frontier-capability thresholds, and the feasibility of external audits?
6. What evidence exists on governance effectiveness, implementation gaps, and known failure modes?
7. What unresolved questions matter most for a decision-maker trying to design or assess an AI governance program in 2026?

## Strategy
- Scope: produce a broad survey rather than a narrow legal memo or a purely academic literature review.
- Evidence mix required:
  - Papers and policy research for conceptual frameworks and historical development
  - Official government / standards documents for current requirements and guidance
  - Frontier-lab policies, safety frameworks, and transparency artifacts for current practice
  - Credible secondary synthesis only when primary sources are unavailable or to triangulate disagreements
- Time periods:
  - 2016–2020 for foundational principles and early governance framing
  - 2021–2024 for institutionalization and regulatory drafting
  - 2025–2026 for current legal status, standards updates, and frontier-model governance practices
- Researcher allocations and dimensions:
  - T1: academic and policy literature landscape
  - T2: current regulation and standards landscape
  - T3: organizational and frontier-lab governance mechanisms in practice
  - T4: critiques, gaps, enforcement problems, and evidence on effectiveness
- Expected rounds:
  - Round 1: broad evidence gathering across four disjoint dimensions
  - Round 2: targeted follow-up only if critical claims remain single-sourced or contradictory
- Sufficient-answer standard:
  - Key descriptive claims should be backed by at least two independent sources unless the claim is inherently about a single authoritative document
  - Current regulatory status must be tied to official or near-official sources
  - Major disagreements must be explicit, not smoothed over

## Acceptance Criteria
- [ ] All key questions answered with ≥2 independent sources where appropriate
- [ ] Contradictions identified and addressed
- [ ] No single-source claims on critical findings except authoritative-document status claims
- [ ] Current-state claims anchored to official 2025–2026 sources where available
- [ ] Final brief separates observations from inference and flags evidence gaps

## Task Ledger
| ID | Owner | Task | Status | Output |
|---|---|---|---|---|
| T1 | lead / researcher | Map the academic and policy literature on AI governance frameworks, taxonomies, and major schools of thought. | completed | outputs/ai-governance-research-literature.md |
| T2 | lead / researcher | Map current regulation, standards, and official guidance relevant to AI governance in 2025–2026. | completed | outputs/ai-governance-research-regulation.md |
| T3 | lead / researcher | Gather evidence on organizational and frontier-lab governance mechanisms actually proposed or used in practice. | completed | outputs/ai-governance-research-practice.md |
| T4 | lead / researcher | Gather critiques, implementation gaps, enforcement issues, and empirical evidence about governance effectiveness or failure modes. | completed | outputs/ai-governance-research-gaps.md |
| T5 | lead | Synthesize evidence into a research brief with explicit disagreements, open questions, and practical implications. | completed | outputs/.drafts/ai-governance-draft.md |
| T6 | verifier | Add inline citations, verify URLs, and produce the cited brief. | completed | outputs/ai-governance-brief.md |
| T7 | reviewer | Run verification pass for support quality, contradictions, and confidence calibration. | completed | outputs/ai-governance-verification.md |
| T8 | lead | Publish final artifact and provenance record. | in_progress | outputs/ai-governance.md + outputs/ai-governance.provenance.md |

## Verification Log
| Item | Method | Status | Evidence |
|---|---|---|---|
| Definition and scope of “AI governance” | cross-read literature + policy docs | completed | outputs/ai-governance-research-literature.md |
| Current regulatory status claims | direct fetch of official laws / official guidance | completed | outputs/ai-governance-research-regulation.md |
| Claims about frontier-lab governance mechanisms | direct read of lab policy docs / transparency materials | completed | outputs/ai-governance-research-practice.md |
| Claims about effectiveness and failure modes | cross-read papers, policy audits, and oversight reports | completed | outputs/ai-governance-research-gaps.md |
| Final critical-claim sweep | source-to-claim mapping against cited draft | completed | outputs/ai-governance-brief.md |

## Decision Log
- 2026-04-11: Created initial plan for a broad, multi-source survey of AI governance.
- 2026-04-11: No local CHANGELOG.md was present, so there were no prior session entries to incorporate.
- 2026-04-11: Planned for 4 parallel researcher tracks because “AI governance” is a broad, multi-faceted topic spanning literature, regulation, practice, and critique.
- 2026-04-11: Completed round 1 with four disjoint research tracks covering literature, regulation, practice, and governance gaps.
- 2026-04-11: Round-1 evidence appears sufficient for synthesis; no major unanswered core question remains, but treaty-status and implementation-status claims will be phrased conservatively where sources indicate ongoing rollout or ratification dependence.
- 2026-04-11: Wrote lead draft and generated a small quantitative chart from already-reported values to visualize governance observability limits.
- 2026-04-11: Verifier pass added inline citations and URL-checked sources; reviewer pass surfaced major calibration issues around single-study generalization and an ISO citation gap.
- 2026-04-11: Fixed calibration issues by narrowing claims, adding ISO/IEC 23894 and 42005 citations, correcting the Sara Hooker attribution, and reran verification; follow-up review found no FATAL or MAJOR issues.
