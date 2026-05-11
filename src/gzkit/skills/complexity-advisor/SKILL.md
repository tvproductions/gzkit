---
name: complexity-advisor
description: Preview complexity advisor diagnosis, understand auto-chain context, or check intrinsic complexity attestation guidance. Use when the operator says "preview complexity advisor", "complexity diagnosis", "advisor recommendation", "what does the advisor say", or "intrinsic complexity attestation".
category: code-quality
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-05-06
metadata:
  skill-version: "0.1.0"
  govzero-framework-version: "v6"
  govzero_layer: "Layer 3 - File Sync"
gz_command: complexity advise
model: opus
---

# complexity-advisor

Operator-runnable skill wrapping the `gz complexity advise` CLI verb
(ADR-0.0.29, OBPI-0.0.29-03). The advisor is the trigger-time doctrinal-frame
surface for the four-ADR complexity-doctrine cluster (ADR-0.0.27 corpus /
0.0.28 thresholds / 0.0.29 advisor / 0.0.30 authoring-guidance). Every
diagnosis cites the active distilled-characteristics document and the canonical
`ThresholdTable`, carries a `proof` field linking to responsible AST nodes /
line ranges, and respects the two-path intrinsic-complexity attestation.

## When to Use

Three operator moments trigger this skill — any one fires the advisor:

1. **Ad-hoc preview-before-fail** — the operator wants to preview advisor
   diagnosis on a file before xenon-as-gate would fail it at commit time.
2. **Auto-chain context** — the operator wants to understand what happened
   when xenon-as-gate failed and the advisor auto-fired.
3. **Intrinsic-complexity attestation guidance** — the operator wants to know
   when to use `@intrinsic_complexity` (decorator) vs `--attest-intrinsic`
   (commit-time flag) for irreducibly complex functions.

## Operator Moments

### Ad-hoc preview-before-fail

The operator invokes the advisor directly to preview diagnosis before commit.
This is the OEE-aligned preview-before-fail moment: the developer sees the
full diagnosis (archetype, authority, proof range, recommended move) without
waiting for xenon-as-gate to trip.

```bash
gz complexity advise src/gzkit/commands/validate.py
gz complexity advise src/gzkit/ --json
```

Default output is structured prose with a per-diagnosis block. The `--json`
flag emits the canonical `AdvisorDiagnosis` Pydantic serialization for
machine consumption.

### Auto-chain context

When xenon-as-gate exits non-zero at pre-commit time, the auto-chain hook
(OBPI-0.0.29-05) fires `gz complexity advise --auto-chain` automatically.
The `--auto-chain` flag signals that the invocation is trigger-fired (not
operator-initiated), producing a condensed presentation default suited to
the commit-time moment rather than the verbose preview the ad-hoc path emits.

The auto-chain pathway preserves the existing SKIP-bypass guard wiring from
the `complexity-reduction-xenon` chore — modules previously marked with a
SKIP annotation continue to bypass both xenon-as-gate and the advisor.

### Intrinsic-complexity attestation

For functions whose complexity is irreducibly algorithmic (e.g. CC=24 in a
query optimizer's join-cost calculator), two attestation paths exist:

- **`@intrinsic_complexity(reason=..., attestor=...)`** — decorator applied
  to the function definition. The advisor honors this at diagnosis time and
  skips the function. Use for known-irreducible functions whose complexity
  will not change.

- **`--attest-intrinsic`** — commit-time flag passed to
  `gz complexity advise`. Records the attestation to
  `.gzkit/ledger.jsonl` via canonical event emission with Gate 5
  follow-up persistence. Use for newly-discovered irreducible complexity
  where amending the source with a decorator is premature.

Both paths land at brief-level Gate 5; neither produces a silent escape hatch.
The decorator path pre-attests (skips at diagnosis time); the commit-time path
post-attests (records and schedules review).

## Timeout and Failure Handling

The advisor's pre-commit hook (OBPI-0.0.29-09) wraps the invocation in a
configurable timeout (default 30s). On timeout the hook fails open: the commit
proceeds and a warning is logged to `.gzkit/insights/advisor-failures.jsonl`
for later operator review. The fail-open is deliberate — blocking commits
on advisor failure is worse than letting them through with a logged warning.

## Output Contract

**Declared form:** structured prose (default human-readable).

Each diagnosis block in the default output contains:

- **Metric** — the measured value and the metric name (e.g. `radon_cc=14`)
- **Crossing band** — which threshold band was crossed (`warn` or `block`)
- **Archetype** — the canonical refactor archetype (e.g. Long Parameter List,
  Arrowhead, Switch-on-Type)
- **Doctrinal frame** — the authority citation (Fowler / Martin / Page-Jones /
  Constantine) with chapter/page anchor
- **Proof range** — file path + line range + AST node descriptor linking to
  the responsible code
- **Recommended move** — the refactoring operation the authority prescribes

**Machine-readable mode:** `--json` emits the canonical `AdvisorDiagnosis`
Pydantic serialization as a JSON array. Each element is a frozen Pydantic
model with fields: `metric`, `value`, `band`, `archetype`, `doctrinal_frame`,
`proof`, `recommended_move`.

## Commands

```bash
# Ad-hoc preview (verbose structured prose)
gz complexity advise <path>

# Machine-readable output
gz complexity advise <path> --json

# Auto-chain mode (condensed, trigger-fired)
gz complexity advise <path> --auto-chain

# Intrinsic attestation at commit time
gz complexity advise <path> --attest-intrinsic
```

## Related

- Manpage: `docs/user/manpages/gz-complexity-advise.md`
- Runbook: `docs/user/runbook.md` § Complexity doctrine surfaces
- Parent ADR: `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/`
- Threshold table: `.gzkit/rules/complexity-thresholds.json` (ADR-0.0.28)
- Distilled characteristics: `data/exemplar_corpus.json` + distillation output
  (ADR-0.0.27 OBPI-04)
- Complexity distill skill: `.gzkit/skills/gz-complexity-distill/SKILL.md`
