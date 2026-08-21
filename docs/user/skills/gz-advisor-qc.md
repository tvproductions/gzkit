# /gz-advisor-qc

Judge the information-retained-per-byte of a candidate rendition and record the verdict via `gz content advise-rendition` — advisory, never gating. Use after composing a candidate (`gz content compose`) and before operator attestation, to produce the advisor-QC receipt the operator cites at Gate 5.

---

## Purpose

`gz-advisor-qc` is the **advisor-QC stage** of the ADR-0.0.37 corpus pipeline
(`corpus → compress → advisor-QC → operator attest → committed rendition → playback`).
An agent wielding this skill reads a staged candidate rendition against its source
corpus, judges how much **information is retained per byte** of the compressed result,
and records that judgment via `gz content advise-rendition`.

The stage is governed by ADR-0.0.39 LLM-as-judge doctrine:

- **Advisory, never gating.** A low retention score is evidence for the operator, not a
  fail-closed gate — the tool exits 0 for any score.
- **Explanation before verdict.** Reasoning is recorded before the score; an empty
  explanation is the only fail-closed condition (malformed receipt shape, never the value).
- **The judgment is the agent's; the tool is deterministic.** `gz content advise-rendition`
  makes no LLM or network call — it validates shape, writes the ARB receipt, and emits a
  ledger event.

## Invocation

```bash
gz content advise-rendition <surface> [--consumer <vendor>] \
  --score <0.0-1.0> --explanation "<reasoning>"
```

- `<surface>` is the control surface scored (e.g. `AGENTS.md`).
- `--consumer` is the target vendor (e.g. `codex`); omit for surface-wide scoring.
- `--score` is the information-retained-per-byte verdict value — advisory, never gates.
- `--explanation` is the advisor's reasoning, recorded **before** the verdict. An empty
  explanation fails closed (non-zero exit, no receipt).

## Validation

- An ARB receipt named `arb-step-judge-<32hex>.json` is written under the receipts root
  (`artifacts/receipts/` by default), with `exit_status: 0` and the explanation serialized
  before the verdict block.
- A `rendition_advisor_verdict` ledger event carries `surface`, `consumer`, `receipt_id`,
  and `score`.
- A verdict with an empty explanation writes no receipt and emits no event.

## Example

```bash
gz content advise-rendition AGENTS.md --consumer root --score 0.94 \
  --explanation "All Mechanical bullets retained; two Promotable bullets combined without information loss."
```

## Related

- [`gz content`](../manpages/content.md) — the command group; see § advise-rendition
- [`gz-content-compose`](gz-content-compose.md) — the compress stage that precedes advisor-QC
- ADR-0.0.37 — Constitutional Invariant Composition (corpus pipeline)
- ADR-0.0.39 — LLM-as-judge doctrine (advisory, never gating; explanation-before-verdict)
