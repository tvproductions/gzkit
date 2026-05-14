---
id: agent-failure-modes
paths:
  - "AGENTS.md"
  - ".gzkit/rules/**"
  - "docs/governance/**"
description: Six-pattern agent-failure-mode taxonomy (Opus 4.7 § 2.3.6 / GPT-5.5 § 9.2) with gzkit-invariant backstops.
---

<!-- rule-version: 0.4.0 -->

# Agent Failure-Mode Taxonomy (gzkit)

> **Rule version:** `0.4.0` — repointed the Safeguard-circumvention and Fabrication backstops off the removed TTY `ATTEST` authenticity gate onto AGENTS.md § Never #1 (operator-verbatim attestation + audit), per the canon-owner attestation declaration.

Six patterns from the Opus 4.7 System Card (§ 2.3.6) and GPT-5.5 System Card (§ 9.2). Cite by name when reviewing, filing defects, or extending the scorecard to route directly to the backstop.

| Pattern | Definition | Backstop |
|---------|-----------|----------|
| **Safeguard circumvention** | Works around a guardrail instead of producing the evidence it asks for | Behavior Rules — Never #6; ARB receipts; AGENTS.md § Never #1 |
| **Reckless action** | Hard-to-reverse action without confirming authorization for this scope | DO IT RIGHT 6a; brief-boundary anti-pattern |
| **Fabrication** | Synthesized claim/receipt/attestation not observed from primary source | ARB receipt discipline; AGENTS.md § Never #1 (operator-verbatim attestation + audit) |
| **Skipped cheap verification** | Pattern-matched incantation from training memory without running it | DO IT RIGHT 6g, #4; ARB receipt requirement |
| **Correction fails** | Correction received but not internalized or applied superficially | Behavior Rules — Always #11; T1/T2/T3 invariants |
| **Dishonest when caught** | Post-hoc rationalization without quoting rule and conflicting directive verbatim | DO IT RIGHT 6h; verbatim-quoting requirement |

**Loading posture:** Advisory vocabulary, not a mechanical gate. The defenses (AGENTS.md § Never #1, ARB receipts, hook fail-closed, `gz validate --commit-trailers`, T1/T2/T3) are the shared backstops.

> See [`docs/governance/agent-contract-rationale.md` § Failure-mode worked examples](docs/governance/agent-contract-rationale.md#failure-mode-worked-examples) for worked examples, invocation patterns, and promotion roadmap (GHIs #308–#312).
