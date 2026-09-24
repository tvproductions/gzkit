---
id: agent-failure-modes
paths:
  - "AGENTS.md"
  - ".gzkit/rules/**"
  - "docs/governance/**"
description: Nine-pattern agent-failure-mode taxonomy sourced to the current frontier system cards (registry-rotated via data/frontier_model_cards.json) with gzkit-invariant backstops.
---

<!-- rule-version: 0.8.1 -->

# Agent Failure-Mode Taxonomy (gzkit)

> **Rule version:** `0.8.1` — the Opus-tier source re-sourced to the Claude Opus 5.5 System Card (GHI #1089); patterns unchanged (nine). Prior version history lifted to [Rule Version History](../../docs/governance/rule-version-history.md#agent-failure-modesmd).

Patterns are maintained against the **current** frontier system cards — the registry-rotated set in `data/frontier_model_cards.json` (chore: `frontier-model-card-currency`), presently the Claude Fable 5.1 & Claude Mythos 5.1 System Card (§§ 2.3.3, 6.2.1, 6.4.2–6.4.5, 6.6.1), the Claude Opus 5.5 System Card (§§ 6.3.1, 6.4.1, 6.4.3–6.4.5, 6.5.1), and the GPT-5.6 System Card (§§ 7.1–7.4, 9.1.3.6, 9.2.2) — and against repo-observed defects cited in the worked examples. Origin lineage lives in [Rule Version History](../../docs/governance/rule-version-history.md#agent-failure-modesmd), never in this rule. Cite by name when reviewing, filing defects, or extending the scorecard to route directly to the backstop. **Loading posture:** advisory vocabulary, not a mechanical gate — the defenses named in the Backstop column are the shared enforcement.

| Pattern | Definition | Backstop |
|---------|-----------|----------|
| **Safeguard circumvention** | Works around a guardrail instead of producing the evidence it asks for | Behavior Rules — the ledger-and-hooks rule; ARB receipts; § Gate Covenant (Gate 5 is universal) |
| **Reckless action** | Hard-to-reverse action without confirming authorization for this scope | DO IT RIGHT #1 (fix the class, not the instance); brief-boundary anti-pattern |
| **Fabrication** | Synthesized claim/receipt/attestation not observed from primary source | ARB receipt discipline; § Attestation (operator words verbatim, then evidence) |
| **Skipped cheap verification** | Pattern-matched incantation from training memory without running it | DO IT RIGHT 6g, #4; ARB receipt requirement |
| **Correction fails** | Correction received but not internalized or applied superficially | Behavior Rules — the `gz insights remember` rule; T1/T2/T3 invariants |
| **Dishonest when caught** | Post-hoc rationalization without quoting rule and conflicting directive verbatim | DO IT RIGHT 6h; verbatim-quoting requirement |
| **Hallucinated authorization** | Acts on a gate it *believes* was passed when no artifact records it — fabricates the precondition to itself, then proceeds sincerely | Gate 5 `--attestor` + non-empty `evidence.attestation_text`, ledger-written; cite the authorizing artifact, never recall it |
| **Security shortcut for expedience** | Trades a security or integrity property for convenience without surfacing the tradeoff | Behavior Rules — the commit-through-hooks rule (no `--no-verify`) and the push-back rule (cite the rule) |
| **Metagaming / gaming the gate** | Reasons about how the gate, validator, or grader will judge the work and shapes output to satisfy the check rather than the intent it proxies — user-facing summary omits what the reasoning admits | DO IT RIGHT #6 (tests assert semantics, not strings); Behavior Rules — the ledger-and-hooks rule (diagnose hook blocks, never work around); ARB receipts + Layer-2 ledger over agent narrative |

> See [`docs/governance/agent-contract-rationale.md` § Failure-mode worked examples](../../docs/governance/agent-contract-rationale.md#failure-mode-worked-examples) for worked examples, invocation patterns, the pattern-7 distinction from patterns 1/3, the pattern-7 provenance caveat, and promotion roadmap (GHIs #308–#312).
