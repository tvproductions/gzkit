ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.29 — Complexity Advisor
Evaluator: main-session (manual review supersedes CLI pre-screen)
Date: 2026-05-06

--- CLI Pre-Screen (for traceability) ---

CLI Verdict: GO
CLI Weighted Total: 3.75/4.0
CLI Flagged:
  - Dimension 1 (Problem Clarity): score=3, finding="No after/target-state language in Intent"
  - Dimension 8 (Architectural Alignment): score=3, finding="No anti-pattern guidance"

Both CLI flags reviewed and identified as **heuristic false negatives** — see manual rationale below.

--- ADR-Level Scores (manual, authoritative) ---

| # | Dimension | Weight | CLI | Manual | Weighted | Rationale |
|---|-----------|--------|-----|--------|----------|-----------|
| 1 | Problem Clarity        | 15% | 3 | 4 | 0.60 | CLI heuristic looks for "before/after" markers in Intent; ADR distributes the framing as prose. Concrete before-state ("developer gets `CC=14` and no doctrinal frame for action") and concrete after-state ("(authority, refactor archetype, proof range, recommended move)") are both present. All five Dimension-1 checklist items pass with evidence. CLI false negative; override 3 → 4. |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | Eight numbered rationale items each carry an explicit "because"; 12 alternatives in Alternatives Considered with named rejection reasons; cites ADR-0.0.27, ADR-0.0.28, OBPI-0.0.27-07 link-integrity-validator pattern, AGENTS.md § Attestation receipt-ID discipline, OEE doctrine. |
| 3 | Feature Checklist      | 15% | 4 | 4 | 0.60 | 9 items, each independently necessary (schema / engine / CLI / skill / auto-chain / ad-hoc / attestation / proof-binding / timeout); each maps to a single OBPI; ordered per the explicit sequencing diagram (`01 → 02 → 08 → 03 → 04 → 05 → 09 → 06 → 07`). |
| 4 | OBPI Decomposition     | 15% | 4 | 4 | 0.60 | Each OBPI codifies one distinct invariant; clean Allowed/Denied path boundaries between briefs; sequencing acyclic; numbering 01-09 with no gaps; explicit parallelization at the surface layer (CLI/skill/hooks). |
| 5 | Lane Assignment        | 10% | 4 | 4 | 0.40 | All 9 OBPIs heavy; ADR justifies with four heavy-lane triggers (new CLI subcommand + new skill + new pre-commit hook + new ledger event family + new schema). Foundation-kind brief-level Gate 5 stacks per ADR-0.0.18. |
| 6 | Scope Discipline       | 10% | 4 | 4 | 0.40 | Six explicit non-goals (corpus methodology, threshold values, authoring guidance, xenon-as-gate behavior, archetype empirical validation, xenon vendoring); each non-goal cites the ADR that owns it. Cluster-coherence guardrail explicit. |
| 7 | Evidence Requirements  | 10% | 4 | 4 | 0.40 | Every OBPI has a Verification block with concrete `uv run gz` and `uv run -m behave` commands; ARB step incantations cited; REQ-coverage decorators (`@covers(REQ-0.0.29-NN-MM)`) specified per requirement. |
| 8 | Architectural Alignment| 10% | 3 | 4 | 0.40 | CLI heuristic looks for an "anti-pattern" section header; ADR distributes anti-pattern guidance across 12 named-and-rejected alternatives in Alternatives Considered (each with a "REJECTED because [named failure mode]" rationale). References exemplar files (`.claude/rules/cli.md`, `.gzkit/rules/tool-skill-runbook-alignment.md`, ADR-0.0.18, ADR-0.0.27, ADR-0.0.28, AGENTS.md § Attestation, OBPI-0.0.27-07) and module paths (`src/gzkit/complexity/advisor/**`, `src/gzkit/commands/complexity_advise.py`, `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/schemas/advisor_diagnosis.json`). CLI false negative; override 3 → 4. |

WEIGHTED TOTAL: 4.00/4.0
THRESHOLD: ≥3.0 (GO), 2.5-3.0 (CONDITIONAL GO), <2.5 (NO GO)

--- OBPI-Level Scores ---

CLI scoring sample-verified by reading OBPI-07, OBPI-08, OBPI-09 (the three OBPIs the CLI flagged on Size). One adjustment to OBPI-08 Size based on the brief content (single new validator scope at `trust_audits.py`, comparable in shape to existing `validate_complexity_doctrine_links`).

| OBPI | Independence | Testability | Value | Size | Clarity | Avg | Notes |
|------|-------------|-------------|-------|------|---------|-----|-------|
| 01-advisor-diagnosis-schema       | 4 | 4 | 4 | 4 | 4 | 4.0 | — |
| 02-diagnosis-engine               | 4 | 4 | 4 | 4 | 4 | 4.0 | — |
| 03-complexity-advise-cli          | 4 | 4 | 4 | 4 | 4 | 4.0 | — |
| 04-complexity-advisor-skill       | 4 | 4 | 4 | 4 | 4 | 4.0 | — |
| 05-auto-chain-hook                | 4 | 4 | 4 | 4 | 4 | 4.0 | — |
| 06-ad-hoc-path                    | 4 | 4 | 4 | 4 | 4 | 4.0 | — |
| 07-intrinsic-complexity-attestation | 4 | 4 | 4 | 2 | 4 | 3.6 | Genuine size pressure: new decorator API + new ledger event family + schema extension + TTY+ATTEST gate + 13 REQs. CLI's Size=2 is fair (could push to 4-5 days). |
| 08-verdict-proof-binding          | 4 | 4 | 4 | 3 | 4 | 3.8 | CLI Size=2 → manual 3. Brief is bounded to one new validator scope at `trust_audits.py` (parallel to existing validators) + flag wiring + tests/BDD/docs. Reasonable 2-3 day work unit; might push to 4 days. |
| 09-advisor-timeout-fallback       | 4 | 4 | 4 | 3 | 4 | 3.8 | Single timeout primitive + JSONL log schema + cross-platform handling. Bounded scope. |

OBPI THRESHOLD: average ≥3.0 per OBPI; any dimension scoring 1 must be revised. **All OBPIs ≥3.6, no dimension scores 1, threshold satisfied.**

--- Red-Team Challenges ---

Not run for this evaluation (`--red-team` not specified). Optional follow-up if operator requests adversarial pass; recommended pre-promotion given the cluster's structural weight (third foundation in a four-ADR doctrine-cluster).

--- Overall Verdict ---

[x] GO — Ready for proposal/defense review
[ ] CONDITIONAL GO
[ ] NO GO

Manual weighted total 4.00/4.0 (CLI 3.75/4.0). Both CLI flags resolved as heuristic false negatives — Problem Clarity and Architectural Alignment carry the substance the heuristics looked for, distributed across prose and the Alternatives section instead of using the structural markers the heuristics scan.

ACTION ITEMS:

1. None blocking. ADR is structurally exemplary across all 8 dimensions with 9 well-decomposed OBPIs.
2. Optional pre-promotion: run the 10-challenge red-team protocol (`/gz-adr-evaluate ADR-0.0.29 --red-team`) — the cluster's structural weight (third of four foundation ADRs, nine OBPIs, foundation-kind brief-level Gate 5 across all of them) is the right shape for an adversarial pass.
3. Optional pre-implementation: run `gz-justify` for OBPI-07 and OBPI-08 since they are the highest-complexity briefs (CLI Size=2; manual Size=2/3). Walkthrough surfaces hidden ambiguity before promotion to active work; not required (both score ≥3.0) but recommended for the size-flagged briefs.
