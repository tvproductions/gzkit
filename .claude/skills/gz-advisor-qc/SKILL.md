---
name: gz-advisor-qc
description: Judge the information-retained-per-byte of a candidate rendition and record the verdict via gz content advise-rendition — advisory, never gating. Use after composing a candidate (gz content compose) and before operator attestation, to produce the advisor-QC receipt the operator cites at Gate 5.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-08-21
metadata:
  skill-version: "0.2.0"
model: sonnet
gz_command: gz content advise-rendition
---

# gz content advise-rendition (advisor-QC)

## Overview

You are the **advisor panel** in the ADR-0.0.37 corpus pipeline
(`corpus → compress → advisor-QC → operator attest → committed rendition → playback`).
After `gz content compose` stages a candidate rendition, you read the candidate against
its source corpus and judge how much **information is retained per byte** of the
compressed result. You then record that judgment as a verdict via
`gz content advise-rendition`.

This is an **LLM-as-judge** surface governed by ADR-0.0.39 doctrine:

- **Advisory, never gating.** A low retention score is *evidence for the operator*, not a
  fail-closed gate. The tool exits 0 for any score. You never block compose or commit on
  the verdict value.
- **Explanation before verdict.** Your reasoning is recorded *before* the score — state
  *why* first, then the number. The tool fails closed only on a structurally malformed
  verdict (an empty explanation), never on the value.
- **The judgment is yours; the tool is deterministic.** The `gz content advise-rendition`
  tool makes no LLM or network call. It validates receipt shape, writes the ARB receipt,
  and emits a ledger event. The information-retention read is *your* work, not the tool's.

## Workflow

1. Identify the **surface** (e.g. `AGENTS.md`) and the **consumer** (e.g. `root`) whose
   candidate rendition you are judging. The candidate is staged at
   `.gzkit/renditions/<surface>/<consumer>.candidate.md`; the source corpus is at
   `.gzkit/corpus/<surface>.jsonl`.
2. Read both. For each compressible-tier corpus entry, ask: did the candidate **retain the
   information** (possibly compressed) or **lose it**? Invariant-tier entries must appear
   verbatim — their loss is not a low score, it is a compose-stage defect to surface.
3. Form a **retention judgment** as a ratio in `[0.0, 1.0]` — information retained per byte
   of the compressed rendition. High = dense retention; low = measurable loss per byte saved.
4. Write a concise **explanation** naming what was retained, what was combined, and what (if
   anything) was lost. This is the reasoning the operator reads at Gate 5.
5. Record the verdict:

   ```bash
   gz content advise-rendition <surface> [--consumer <vendor>] \
     --score <0.0-1.0> --explanation "<your reasoning>"
   ```

6. The verdict is written as an ARB receipt (`arb-step-judge-<hash>`) and witnessed by a
   `rendition_advisor_verdict` ledger event. Cite the receipt id in the operator's Gate-5
   attestation.

## Validation

- An ARB receipt is written under the configured receipts root (`artifacts/receipts/` by
  default) named `arb-step-judge-<32hex>.json`, with `exit_status: 0` and the explanation
  serialized before the verdict block.
- A `rendition_advisor_verdict` ledger event is emitted carrying `surface`, `consumer`,
  `receipt_id`, and `score`.
- A verdict with an empty/whitespace explanation fails closed: non-zero exit, no receipt,
  no ledger event.

## Example

```bash
# After composing a candidate for AGENTS.md → root, judge and record the verdict.
gz content advise-rendition AGENTS.md --consumer root --score 0.94 \
  --explanation "All Mechanical bullets retained verbatim; two Promotable bullets combined without information loss; no Judgment content dropped."

# A low score is still recorded (advisory) — it is evidence for the operator, not a block.
gz content advise-rendition CLAUDE.md --consumer claude --score 0.55 \
  --explanation "One Judgment-tier rationale paragraph compressed past the point of recoverability; flagging measurable loss for operator review."
```
