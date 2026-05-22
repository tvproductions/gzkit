# /gz-complexity-advisor

Preview complexity advisor diagnosis, understand auto-chain context, or check intrinsic complexity attestation guidance.

---

## Purpose

`/gz-complexity-advisor` wraps the `gz complexity advise` CLI verb from the
four-ADR complexity-doctrine cluster (ADR-0.0.27 through ADR-0.0.30). It
gives operators a single entry point for previewing per-function complexity
diagnosis before commit, understanding what the auto-chain hook produced when
xenon-as-gate tripped, and choosing the right intrinsic-complexity attestation
path for irreducibly complex functions.

## When to Use

Three operator moments trigger this skill:

1. **Ad-hoc preview-before-fail** -- preview advisor diagnosis on a file
   before xenon-as-gate would fail it at commit time.
2. **Auto-chain context** -- understand what happened when xenon-as-gate
   failed and the advisor auto-fired via `--auto-chain`.
3. **Intrinsic-complexity attestation guidance** -- decide between the
   `@intrinsic_complexity` decorator (pre-attest, skips at diagnosis time)
   and the `--attest-intrinsic` commit-time flag (post-attest, records and
   schedules review).

See [Runbook: Complexity doctrine surfaces](../runbook.md) for the full
workflow context.

## What to Expect

- **Output:** Structured prose with a per-diagnosis block (metric, crossing
  band, archetype, doctrinal frame, proof range, recommended move). Pass
  `--json` for machine-readable `AdvisorDiagnosis` Pydantic serialization.
- **Duration:** Seconds for a single file; may take longer on large directory
  trees.
- **Side effects:** None in default mode. `--attest-intrinsic` records an
  attestation event to `.gzkit/ledger.jsonl`.
- **Success:** Exit 0 (no block-band crossings) or exit 0 with warn-band
  output.
- **Failure:** Exit 3 on block-band crossings; exit 1 on user/config error;
  exit 2 on system/IO error.

## Invocation

```text
/gz-complexity-advisor
/gz-complexity-advisor src/gzkit/commands/validate.py
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `path` | yes | File or directory to analyze |
| `--json` | no | Emit machine-readable JSON array |
| `--auto-chain` | no | Condensed output for trigger-fired context |
| `--attest-intrinsic` | no | Record intrinsic-complexity attestation |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-complexity-advisor/SKILL.md` | Agent execution instructions | Read |
| `.gzkit/rules/complexity-thresholds.json` | Canonical threshold table (ADR-0.0.28) | Read |
| `data/exemplar_corpus.json` | Exemplar corpus for distillation | Read |
| `docs/user/manpages/gz-complexity-advise.md` | CLI verb manpage | Read |
| `.gzkit/ledger.jsonl` | Attestation events (with `--attest-intrinsic`) | Write |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-complexity-distill`](gz-complexity-distill.md) | Companion skill for refreshing distilled-characteristics doctrine |
| [`gz complexity advise`](../manpages/gz-complexity-advise.md) | Underlying CLI verb this skill wraps |
