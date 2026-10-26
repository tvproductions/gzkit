---
id: ADR-pool.review-receipt-taxonomy
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.review-receipt-taxonomy: Review Receipt Taxonomy

## Status

Pool

## Intent

Define a structured taxonomy for review receipts so spec review, code quality
review, security review, overbuild review, performance review, and integration
review become machine-readable evidence rather than narrative checkpoints.

Competitor workflows often win adoption by making review phases obvious and
repeatable. gzkit's advantage should be stronger: each review phase emits a
typed receipt with scope, reviewer role, findings, disposition, and downstream
blocking semantics.

**Target promotion kind:** foundation or feature candidate depending on scope.
If promoted as doctrine-only receipt semantics, foundation. If promoted as CLI
commands and pipeline integration first, feature.

**Comparator signals:** Superpowers two-stage review, BMAD persona/workflow
packaging, Compound Engineering review-to-learning loops, GSD task review.

## Decision

When promoted, define a canonical review receipt family. Candidate receipt
types:

- `review_spec_compliance`
- `review_code_quality`
- `review_security`
- `review_performance`
- `review_overbuild`
- `review_integration_decision`
- `review_operator_value`

Each receipt should carry:

- `scope`: ADR/OBPI/GHI/file paths reviewed
- `reviewer_role`: persona or command surface that produced the review
- `criteria`: validator/rule/checklist identifiers used
- `findings`: structured severity, evidence path, disposition
- `decision`: pass, pass-with-findings, fail, blocked, waived-with-reason
- `downstream_binding`: whether completion, promotion, or closeout is blocked
- `compounding_destination`: insight, pattern corpus, GHI, chore, ADR amendment,
  or explicit no-action rationale

The taxonomy should plug into ARB receipts and OBPI pipeline dispatch without
requiring every review to be human. The human boundary remains explicit when
lane/kind/sensitivity requires it.

## Amendment 2026-10-26: Reviewer provenance and non-response semantics

Routed from the October 2026 competitor radar (MOVE-101), on the operator's
grill ruling *"Approve, pool ADR (Recommended)"*.

A review receipt records the reviewer's vendor and model, the round number and
the round budget. A timeout, an error or an exhausted budget is recorded as a
**non-response, which never satisfies a review gate**. A receipt also carries an
independent verdict tier, `confirmed`, `needs_validation` or `rejected`, from a
reviewer that tries to disprove each finding.

October sources (in `artifacts/reports/competitor-radar/scans/2026-10.json`, checked at source):

- tstack's `sol-loop` (github.com/t3dotgg/tstack) runs a reviewer on another
  vendor's model in a bounded loop, keeps a findings ledger with stable ids and
  severities, and treats a timeout or exhausted budget as not approval.
- Cloudflare's `security-audit-skill` writes schema-validated findings and has a
  fresh agent try to disprove each one, ending as confirmed, needs_validation or
  rejected.
- Superpowers, Compound Engineering and BMAD each now record a verdict with
  evidence for every review finding.

Rejected from the same sources: model-assigned scores out of 10 as evidence, and
merging on the agent's own confidence (Gate 5 stays human).

Witness at promotion: a typed receipt field set checked by a validator, and a
test that a non-response receipt cannot satisfy a review gate.

## Alternatives Considered

- **Keep review output as prose comments.** Rejected. Prose can explain the
  finding, but completion gates need typed evidence and dispositions.
- **Use one generic review receipt.** Rejected. Spec compliance, quality,
  security, and integration decisions block different downstream actions.
- **Attach review receipts only to PRs.** Rejected. gzkit evidence must work
  before PRs and across local/offline workflows.
- **Make all review findings GHIs.** Rejected. GHIs are for routed observations;
  many review findings are fixed inline or feed compounding surfaces.

## Promotion Triggers

- OBPI pipeline dispatch starts using multiple reviewer personas/agents.
- Security or judge-enforcement work needs typed review evidence.
- Comparator intake finds review workflows that should be absorbed without
  lowering completion rigor.

## Related Destinations

- `ADR-pool.obpi-pipeline-dispatch-attestation`
- `ADR-pool.skill-feedback-loop`
- `ADR-pool.solved-problem-pattern-corpus`
- `ADR-pool.agent-role-specialization`
- `ADR-0.27.0-arb-receipt-system-absorption`
- `ADR-0.41.0-tdd-emission-and-graph-rot-remediation`

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
