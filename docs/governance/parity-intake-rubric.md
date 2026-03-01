# AirlineOps Parity Intake Rubric (gzkit)

Purpose: define a strict, repeatable filter for importing governance behavior from AirlineOps into gzkit.

Principle: selective parity, not wholesale mirroring.

## Decision Rule

For each candidate item from AirlineOps, classify it using this order:

1. Is it GovZero governance behavior (not AirlineOps product behavior)?
2. Does it improve gzkit operator clarity, enforcement strength, or evidence quality?
3. Is there a runnable gzkit runtime/proof surface to back it?
4. Can it be imported without breaking established gzkit command contracts?

If any answer is no, do not import as active parity without explicit tracking.

## Classification Outcomes

| Outcome | Use when | Required action |
|---|---|---|
| Import Now | Governance primitive, high value, runtime-backed | Implement + validate + report evidence |
| Import with Compatibility | Needed, but naming/flow drift exists | Add alias/bridge, document canonical target |
| Defer (Tracked) | Valuable but not runtime-backed yet | File ADR/OBPI follow-up with owner/date |
| Exclude | Product capability or repo-specific process | Record in exclusion log with rationale |

## Severity Guidance

| Severity | Meaning | Typical response |
|---|---|---|
| P0 | Blocks gate integrity or attestation boundary | Immediate fix in current cycle |
| P1 | High governance drift risk | Prioritize next minor |
| P2 | Moderate operational drift | Batch into planned parity tranche |
| P3 | Low impact or documentation polish | Opportunistic or scheduled maintenance |

## Required Evidence for Imports

Every imported item must include:

- Source path in AirlineOps
- Target path in gzkit
- Classification outcome from this rubric
- Validation commands and pass/fail results
- ADR/OBPI linkage for changes or deferrals

## Non-Negotiables

- Do not import product-domain workflows as governance parity.
- Do not claim parity when only naming matches but runtime/proof surfaces do not.
- Do not leave high-impact gaps untracked.
- Do not allow compatibility aliases to drift from canonical behavior.

## Minimal Execution Bundle

```bash
uv run gz cli audit
uv run gz check-config-paths
uv run gz validate --documents --surfaces
uv run mkdocs build --strict
```
